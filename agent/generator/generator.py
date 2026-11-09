"""Problem generator — generates README files and updates repo.

Compares scraped trending problems with existing repo problems using fuzzy matching,
generates tailored README files based on problem keywords, and updates the main README.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from agent.core.config import settings
from agent.core.models import Category, ExistingProblem, GeneratedFile, TrendingProblem
from agent.generator.fuzzy import normalize_name, similarity_ratio
from agent.generator.templates import (
    PROBLEM_TEMPLATES, HLD_TEMPLATE, LLD_TEMPLATE, DS_TEMPLATE,
    TRADEOFF_TEMPLATE, JAVA_TEMPLATE,
)

logger = logging.getLogger("agent.generator")

# ------------------------------------------------------------------ #
#  Category path mapping
# ------------------------------------------------------------------ #

CATEGORY_PATHS = {
    Category.HLD: ["hld/problems"],
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
    Category.JAVA: [
        "java/concurrency/problems",
        "java/collections/problems",
        "java/jvm/problems",
        "java/performance/problems",
        "java/streams/problems",
    ],
}

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

    # ------------------------------------------------------------------ #
    #  List existing problems
    # ------------------------------------------------------------------ #
    def list_existing_problems(self) -> list:
        """Scan the repo and return all existing problems."""
        problems: list = []

        for category, relative_paths in CATEGORY_PATHS.items():
            for relative_path in relative_paths:
                base = self.repo_path / relative_path
                if not base.exists():
                    continue

                for item in base.iterdir():
                    if item.is_dir() and (item / "README.md").exists():
                        name = item.name.replace("-", " ").title()
                        problems.append(ExistingProblem(
                            name=name,
                            category=category,
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
            for ex_name, ex_prob in existing_normalized_names.items():
                if ex_prob.category == prob.category:
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

    def _generate_one(self, prob: TrendingProblem) -> Optional[GeneratedFile]:
        """Generate a single problem README."""
        paths = CATEGORY_PATHS.get(prob.category)
        if not paths:
            logger.warning("Unknown category: %s", prob.category)
            return None

        relative = CATEGORY_DEFAULT_SUBPATH.get(prob.category, paths[0])
        dir_path = self.repo_path / relative / prob.slug
        dir_path.mkdir(parents=True, exist_ok=True)

        # Generate content based on category
        if prob.category == Category.HLD:
            content = self._generate_hld(prob)
        elif prob.category == Category.LLD:
            content = self._generate_lld(prob)
        elif prob.category == Category.TRADEOFFS:
            content = self._generate_tradeoff(prob)
        elif prob.category == Category.JAVA:
            content = self._generate_java(prob)
        elif prob.category == Category.DISTRIBUTED_SYSTEMS:
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

        for prob in problems:
            if prob.name.lower() in content.lower():
                logger.debug("README already contains %s, skipping", prob.name)
                continue

            concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Trending topic"
            entry = f"| [{prob.name}]({prob.category.value}/problems/{prob.slug}/) | {concepts} |"

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
        last_table_row = None

        for i, line in enumerate(lines):
            in_section = any(pattern in line for pattern in patterns)
            if in_section:
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("|"):
                        last_table_row = j
                    elif last_table_row is not None and lines[j].strip() and not lines[j].startswith("|"):
                        return last_table_row + 1

        if last_table_row is not None:
            return last_table_row + 1

        return None
