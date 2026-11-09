"""Problem generator — generates README files and updates repo.

Compares scraped trending problems with existing repo problems using fuzzy matching,
generates tailored README files based on problem keywords, and updates the main README.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent.core.config import settings
from agent.core.models import Category, ExistingProblem, GeneratedFile, TrendingProblem
from agent.ml_classifier import ProblemClassifier
from agent.generator.fuzzy import normalize_name, route_subfolder, similarity_ratio
from agent.generator.templates import (
    PROBLEM_TEMPLATES, HLD_TEMPLATE, LLD_TEMPLATE, DS_TEMPLATE,
    TRADEOFF_TEMPLATE, JAVA_TEMPLATE,
)

logger = logging.getLogger("agent.generator")

# ------------------------------------------------------------------ #
#  Category path mapping
# ------------------------------------------------------------------ #

CATEGORY_PATHS = {
    Category.HLD: ["hld/problems", "hld/case-studies"],
    Category.LLD: ["lld/problems/easy", "lld/problems/medium", "lld/problems/hard", "lld/problems/concurrency"],
    Category.DISTRIBUTED_SYSTEMS: [
        "distributed-systems/problems/coordination",
        "distributed-systems/problems/data-management",
        "distributed-systems/problems/messaging-events",
        "distributed-systems/problems/resilience",
        "distributed-systems/problems/observability",
        "distributed-systems/problems/infrastructure",
        "distributed-systems/problems/scheduling",
    ],
    Category.TRADEOFFS: ["tradeoffs"],
    Category.JAVA: ["java/problems"],
}

# Dedup also considers problems found in adjacent repo locations, regardless of
# the category the source site tagged them with.
DEDUP_EXTRA_PATHS = [
    "db-design/problems",
    "api-modeling/problems",
    "hld/fundamentals",
    "lld/fundamentals",
    "distributed-systems/topics",
]

CATEGORY_DEFAULT_SUBPATH = {
    Category.HLD: "hld/problems",
    Category.LLD: "lld/problems/medium",
    Category.DISTRIBUTED_SYSTEMS: "distributed-systems/problems/data-management",
    Category.TRADEOFFS: "tradeoffs",
    Category.JAVA: "java/concurrency/problems",
}


class ProblemGenerator:
    """Generate new problem README files and update repo."""

    def __init__(self) -> None:
        self.repo_path = Path(settings.REPO_PATH)
        self.similarity_threshold = settings.AGENT_SIMILARITY_THRESHOLD
        # ML classifier (TF-IDF + LogReg) for names not covered by the
        # hardcoded keyword database; trained lazily on first use.
        self._classifier = None

    # ------------------------------------------------------------------ #
    #  List existing problems
    # ------------------------------------------------------------------ #
    def list_existing_problems(self) -> list:
        """Scan the repo and return all existing problems."""
        problems: list = []

        all_paths = []
        for category, relative_paths in CATEGORY_PATHS.items():
            for relative_path in relative_paths:
                all_paths.append((category, relative_path))
        # Extra locations scanned only for dedup (any problem with the same name
        # anywhere means it already exists — category mismatches are common).
        for relative_path in DEDUP_EXTRA_PATHS:
            all_paths.append((None, relative_path))

        for category, relative_path in all_paths:
            base = self.repo_path / relative_path
            if not base.exists():
                continue

            for item in base.iterdir():
                if item.is_dir() and (item / "README.md").exists():
                    name = item.name.replace("-", " ").title()
                    problems.append(ExistingProblem(
                        name=name,
                        category=category or Category.HLD,  # extra paths: category unknown; treated as HLD for routing but dedup uses name only
                        path=str(item),
                        slug=item.name,
                    ))

        logger.info("Found %d existing problems in repo", len(problems))
        return problems

    # ------------------------------------------------------------------ #
    #  Filter missing problems (with fuzzy matching)
    # ------------------------------------------------------------------ #
    def filter_missing(
        self, trending: list, existing: list, run_history_slugs: set = None
    ) -> list:
        """Return trending problems that are not already in the repo."""
        existing_normalized = {prob.slug: prob for prob in existing}
        existing_names_lower = {prob.name.lower() for prob in existing}
        existing_normalized_names = {normalize_name(prob.name): prob for prob in existing}

        history_slugs = run_history_slugs or set()

        missing: list = []
        skipped_exact = 0
        skipped_fuzzy = 0
        skipped_history = 0

        for prob in trending:
            if not prob.is_valid_name():
                logger.debug("Dropping invalid problem name: %r", prob.name)
                continue

            norm = normalize_name(prob.name)

            if prob.slug in history_slugs or norm in history_slugs:
                skipped_history += 1
                continue

            if prob.slug in existing_normalized:
                skipped_exact += 1
                continue

            if prob.name.lower() in existing_names_lower:
                skipped_exact += 1
                continue

            if norm in existing_normalized_names:
                skipped_exact += 1
                continue

            is_duplicate = False
            # Category-agnostic fuzzy match: sources often tag the same problem
            # under different categories (e.g. Ride Sharing as HLD vs LLD).
            for ex_name, ex_prob in existing_normalized_names.items():
                ratio = similarity_ratio(norm, ex_name)
                if ratio >= self.similarity_threshold:
                    logger.debug(
                        "Fuzzy match: '%s' ≈ '%s' (%.2f) — skipping",
                        prob.name, ex_prob.name, ratio,
                    )
                    skipped_fuzzy += 1
                    is_duplicate = True
                    break

            if not is_duplicate:
                missing.append(prob)

        logger.info(
            "Missing: %d (skipped: %d exact, %d fuzzy, %d history) out of %d trending",
            len(missing), skipped_exact, skipped_fuzzy, skipped_history, len(trending),
        )
        return missing

    # ------------------------------------------------------------------ #
    #  Generate all files
    # ------------------------------------------------------------------ #
    def generate_all(self, problems: list) -> list:
        """Generate README files for all missing problems."""
        generated: list = []
        max_problems = settings.AGENT_MAX_PROBLEMS_PER_RUN
        if len(problems) > max_problems:
            logger.info(
                "Limiting to top %d problems (by source count) out of %d",
                max_problems, len(problems),
            )
            problems = problems[:max_problems]

        for prob in problems:
            try:
                file_gen = self._generate_one(prob)
                if file_gen:
                    generated.append(file_gen)
            except Exception as exc:
                logger.error("Failed to generate %s: %s", prob.name, exc, exc_info=True)

        return generated

    def _ml_category(self, prob: TrendingProblem) -> Optional[Category]:
        """Ask the ML classifier for a category when keywords can't decide."""
        if self._classifier is None:
            self._classifier = ProblemClassifier()
            self._classifier.fit()
        ml_cat = self._classifier.predict_category(prob.name)
        if ml_cat:
            logger.info("ML classified %r as %s (keyword db had no match)", prob.name, ml_cat.value)
        return ml_cat

    def _generate_one(self, prob: TrendingProblem) -> Optional[GeneratedFile]:
        """Generate a single problem README."""
        category = prob.category
        paths = CATEGORY_PATHS.get(category)
        if not paths:
            # Unknown category from the source — let the ML model decide
            ml_cat = self._ml_category(prob)
            if ml_cat and CATEGORY_PATHS.get(ml_cat):
                category = ml_cat
                prob.category = ml_cat
                paths = CATEGORY_PATHS[ml_cat]
            else:
                logger.warning("Unknown category for %r: %s (ML fallback failed)", prob.name, prob.category)
                return None

        default = CATEGORY_DEFAULT_SUBPATH.get(category, paths[0])
        # Route to the subfolder matching the repo's existing organization
        relative = route_subfolder(category.value, prob.name.lower(), default)
        dir_path = self.repo_path / relative / prob.slug
        dir_path.mkdir(parents=True, exist_ok=True)

        # Normalize display name once for both content and README metadata
        prob.name = self.display_name(prob.name)

        # Generate content based on (possibly ML-corrected) category
        if category == Category.HLD:
            content = self._generate_hld(prob)
        elif category == Category.LLD:
            content = self._generate_lld(prob)
        elif category == Category.TRADEOFFS:
            content = self._generate_tradeoff(prob)
        elif category == Category.JAVA:
            content = self._generate_java(prob)
        elif category == Category.DISTRIBUTED_SYSTEMS:
            content = self._generate_ds(prob)
        else:
            content = self._generate_generic(prob)

        file_path = dir_path / "README.md"
        file_path.write_text(content)

        logger.info("Generated %s (%d bytes)", file_path.relative_to(self.repo_path), len(content))
        return GeneratedFile(
            path=str(file_path.relative_to(self.repo_path)),
            content=content,
            category=prob.category,
            problem_name=prob.name,
        )

    # ------------------------------------------------------------------ #
    #  Content generators
    # ------------------------------------------------------------------ #
    _SMALL_WORDS = {
        "a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on",
        "or", "the", "to", "vs", "via", "with", "from", "into", "over",
    }

    def display_name(self, name: str) -> str:
        """Normalize a problem name for display: consistent Title Case with
        small words lowercased (except at the start), acronym/known-term
        preservation, and cleanup of stray punctuation."""
        name = re.sub(r"\s+", " ", str(name)).strip(" -–—\t")
        words = name.split()
        out = []
        for i, word in enumerate(words):
            lower = word.lower()
            # Preserve known acronyms / tech terms
            special = {
                "llm": "LLM", "rag": "RAG", "api": "API", "sql": "SQL",
                "nosql": "NoSQL", "aws": "AWS", "gcp": "GCP", "rpc": "RPC",
                "grpc": "gRPC", "graphql": "GraphQL", "io": "I/O",
                "ui": "UI", "cdn": "CDN", "dns": "DNS", "mqtt": "MQTT",
                "ci/cd": "CI/CD", "crud": "CRUD", "db": "DB", "url": "URL",
                "uri": "URI", "http": "HTTP", "tcp": "TCP", "udp": "UDP",
                "oauth": "OAuth", "jwt": "JWT", "kafka": "Kafka",
                "tiktok": "TikTok", "youtube": "YouTube", "whatsapp": "WhatsApp",
                "instagram": "Instagram", "linkedin": "LinkedIn",
                "lru": "LRU", "lfu": "LFU", "hld": "HLD", "lld": "LLD",
                "ssr": "SSR", "sla": "SLA", "cpu": "CPU", "gpu": "GPU",
                "ram": "RAM", "sdk": "SDK", "qa": "QA", "otp": "OTP",
            }
            if lower in special:
                out.append(special[lower])
            elif lower in self._SMALL_WORDS and i > 0:
                out.append(lower)
            elif "-" in word:
                # Title-case each hyphen-separated part, preserving specials
                parts = []
                for p in word.split("-"):
                    pl = p.lower()
                    if pl in special:
                        parts.append(special[pl])
                    elif pl in self._SMALL_WORDS and i > 0:
                        parts.append(pl)
                    else:
                        parts.append(p.capitalize())
                out.append("-".join(parts))
            else:
                out.append(word.capitalize())
        return " ".join(out)

    def _get_template_override(self, prob: TrendingProblem) -> dict:
        """Check if there's a problem-specific template override."""
        name_lower = prob.name.lower()
        for keyword, template in PROBLEM_TEMPLATES.items():
            if keyword in name_lower:
                return template
        return {}

    def _generate_hld(self, prob: TrendingProblem) -> str:
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or ["Scalability", "Reliability", "Performance"]
        concepts_str = ", ".join(concepts)
        return HLD_TEMPLATE.format(
            name=prob.name,
            description=prob.description or self._describe_problem(prob, "hld"),
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob, concepts),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts_str),
            architecture=override.get("architecture") or self._generate_architecture(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts_str),
        )

    def _generate_lld(self, prob: TrendingProblem) -> str:
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or ["Design patterns", "OOP", "SOLID principles"]
        concepts_str = ", ".join(concepts)
        return LLD_TEMPLATE.format(
            name=prob.name,
            description=prob.description or self._describe_problem(prob, "lld"),
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob, concepts),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts_str),
            class_diagram=override.get("class_diagram") or self._generate_class_diagram(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts_str),
        )

    def _generate_ds(self, prob: TrendingProblem) -> str:
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or ["Consistency", "Partition tolerance", "Distributed consensus"]
        concepts_str = ", ".join(concepts)
        return DS_TEMPLATE.format(
            name=prob.name,
            description=prob.description or self._describe_problem(prob, "ds"),
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob, concepts),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts_str),
            architecture=override.get("architecture") or self._generate_architecture(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts_str),
        )

    def _generate_tradeoff(self, prob: TrendingProblem) -> str:
        parts = prob.name.split(" vs ")
        option_a = parts[0].strip() if len(parts) > 1 else "Option A"
        option_b = parts[1].strip() if len(parts) > 1 else "Option B"
        return TRADEOFF_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Understand the trade-offs between {option_a} and {option_b}.",
            sources=prob.source,
            option_a=option_a,
            option_b=option_b,
            when_a=f"- **Predictable performance**: {option_a} provides consistent behavior\n- **Simplicity**: Easier to reason about\n- **Tooling**: Mature ecosystem",
            when_b=f"- **Flexibility**: {option_b} adapts to varying workloads\n- **Scalability**: Better horizontal scaling\n- **Cost**: Potentially lower at scale",
            decision_framework=f"| Factor | {option_a} | {option_b} |\n|--------|-----------|-----------|\n| Performance | Predictable | Variable |\n| Scalability | Vertical | Horizontal |\n| Complexity | Low | Medium |",
            staff_insights=f"- **Context matters**: Start with {option_a}; migrate to {option_b} when needed.\n- **Hybrid approach**: Many systems use both, applying each where it excels.",
        )

    def _generate_java(self, prob: TrendingProblem) -> str:
        concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Java concurrency, JVM internals"
        return JAVA_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Implement and understand {prob.name.lower()} in Java.",
            sources=prob.source,
            key_concepts=f"- **Core concept**: {concepts}\n- **Thread safety**: Proper synchronization\n- **Performance**: Benchmarking with JMH",
            implementation=f"```java\n// TODO: Implement {prob.name}\n```",
            staff_considerations="### Performance\n- Use JMH for benchmarks\n- Use JFR for profiling\n\n### Concurrency\n- Prefer high-level constructs\n- Avoid shared mutable state",
        )

    def _generate_generic(self, prob: TrendingProblem) -> str:
        return f"""# {prob.name}

## Problem Statement

{prob.description or f"Design and implement {prob.name.lower()}."}

**Reference**: {prob.source}

## Requirements

### Functional Requirements
- Core functionality for {prob.name.lower()}
- Scalability and performance considerations

### Non-Functional Requirements
- **Scale**: Handle production-level load
- **Latency**: Sub-second response times
- **Availability**: 99.9% uptime

## Staff-Level Design Considerations

- **Modularity**: Design for extensibility
- **Testing**: Comprehensive tests
"""

    # ------------------------------------------------------------------ #
    #  Helper methods
    # ------------------------------------------------------------------ #
    def _describe_problem(self, prob: TrendingProblem, type_: str) -> str:
        descriptions = {
            "hld": f"Design a {prob.name.lower()} that handles large-scale production workloads.",
            "lld": f"Design and implement a {prob.name.lower()} with proper OOP principles.",
            "ds": f"Design a distributed {prob.name.lower()} with consistency and fault tolerance.",
        }
        return descriptions.get(type_, f"Design and implement {prob.name.lower()}.")

    def _generate_functional_reqs(self, prob: TrendingProblem, concepts: list = None) -> str:
        if concepts is None:
            concepts = prob.key_concepts or ["core functionality", "data management", "API design"]
        lines = []
        for concept in concepts[:5]:
            lines.append(f"- **{concept.title()}**: Support {concept.lower()} with proper error handling.")
        return "\n".join(lines)

    def _generate_non_functional_reqs(self, prob: TrendingProblem) -> str:
        return "- **Scale**: Handle 1M+ users\n- **Latency**: P99 < 200ms\n- **Availability**: 99.9% uptime\n- **Consistency**: Eventual with configurable strong consistency"

    def _generate_key_decisions(self, prob: TrendingProblem, concepts: str) -> str:
        return f"- **Architecture**: Microservices with API gateway\n- **Data storage**: SQL vs NoSQL based on access patterns\n- **Caching**: Multi-tier strategy\n- **Key concepts**: {concepts}"

    def _generate_architecture(self, prob: TrendingProblem) -> str:
        return f"Client → Load Balancer → API Gateway\n                                → {prob.name} Service\n                                → Database (Primary + Replica)\n                                → Cache (Redis Cluster)\n                                → Message Queue (Kafka)"

    def _generate_class_diagram(self, prob: TrendingProblem) -> str:
        first_word = prob.name.split()[0] if prob.name.split() else "Entity"
        return f"┌──────────────┐     ┌──────────────┐\n│   {first_word:<10}│────►│   Manager    │\n├──────────────┤     ├──────────────┤\n│ - properties │     │ - items      │\n└──────────────┘     └──────────────┘"

    def _generate_staff_considerations(self, prob: TrendingProblem, concepts: str) -> str:
        return f"### Scalability\n- **Horizontal scaling**: Add instances behind load balancer\n- **Staff insight**: Start simple; shard only when needed.\n\n### Caching\n- **Multi-tier**: CDN + Redis + app cache\n- **Staff insight**: Use TTL jitter and single-flight to prevent stampede.\n\n### Error Handling\n- **Circuit breaker**: Prevent cascading failures\n- **Staff insight**: Design for failure at every layer.\n\n### Key Concepts: {concepts}"

    # ------------------------------------------------------------------ #
    #  README updates
    # ------------------------------------------------------------------ #
    def update_readme(self, problems: list) -> int:
        """Update the main README.md with new problems."""
        readme_path = self.repo_path / "README.md"
        if not readme_path.exists():
            logger.warning("README.md not found at %s", readme_path)
            return 0

        content = readme_path.read_text()
        lines = content.split("\n")
        changes = 0

        existing_dirs = {prob.slug: prob.path for prob in self.list_existing_problems()}
        for prob in problems:
            if prob.name.lower() in content.lower():
                logger.debug("README already contains %s, skipping", prob.name)
                continue

            # Link to wherever the problem actually lives (falls back to the
            # default subpath for problems that were just generated)
            prob_path = existing_dirs.get(prob.slug)
            if prob_path:
                link = str(Path(prob_path).relative_to(self.repo_path)).replace("\\", "/")
            else:
                # Problem was just generated — link to its default subpath
                link = CATEGORY_DEFAULT_SUBPATH.get(prob.category, "").rstrip("/")
                link = f"{link}/{prob.slug}" if link else prob.slug

            concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Trending topic"
            entry = f"| [{prob.name}]({link}/) | {concepts} |"

            insert_idx = self._find_readme_insertion_point(lines, prob.category)
            if insert_idx is not None:
                lines.insert(insert_idx, entry)
                changes += 1
                logger.info("Added %s to README at line %d", prob.name, insert_idx + 1)

        if changes > 0:
            readme_path.write_text("\n".join(lines))
            logger.info("Updated README.md with %d new entries", changes)

        return changes

    def _find_readme_insertion_point(self, lines: list, category: Category) -> Optional[int]:
        """Find the line number to insert a new problem entry in the README."""
        section_patterns = {
            Category.HLD: ["#### HLD Problems", "### Practice Problems (HLD)", "## HLD"],
            Category.LLD: ["#### Medium", "#### Hard", "### Practice Problems (LLD)"],
            Category.DISTRIBUTED_SYSTEMS: ["#### Data Management", "### Problems by Category"],
            Category.TRADEOFFS: ["## Trade-offs", "| **Data Storage**"],
            Category.JAVA: ["### Concurrency Problems", "### Collections Problems"],
        }

        patterns = section_patterns.get(category, [])

        def _is_table_row(line: str) -> bool:
            return line.lstrip().startswith("|")

        def _is_separator_row(line: str) -> bool:
            # Markdown table separator like |----|-----|
            stripped = line.strip()
            return stripped.startswith("|") and set(stripped.replace("|", "")).issubset({"-", ":", " "})

        for i, line in enumerate(lines):
            if not any(pattern in line for pattern in patterns):
                continue
            # Find the table header row that directly follows the section heading,
            # then append entries after the LAST contiguous table row.
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines) or not _is_table_row(lines[j]):
                continue
            if j + 1 >= len(lines) or not _is_separator_row(lines[j + 1]):
                continue  # not a well-formed table — safer to skip than corrupt
            end = j + 1
            k = end + 1
            while k < len(lines) and _is_table_row(lines[k]):
                end = k
                k += 1
            return end + 1

        return None
