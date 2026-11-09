"""
Problem generator for the SystemDesign agent.

Compares scraped trending problems with existing repo problems using fuzzy matching,
generates tailored README files based on problem keywords, and updates the main README.
Features:
- Levenshtein distance fuzzy matching to avoid near-duplicates
- Problem-specific content generation based on name keywords
- Proper README.md line insertion (not just appending)
- Run history integration to skip previously added problems
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import settings
from models import Category, ExistingProblem, GeneratedFile, TrendingProblem

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

# Default sub-category for new problems within each category
CATEGORY_DEFAULT_SUBPATH = {
    Category.HLD: "hld/problems",
    Category.LLD: "lld/problems/medium",
    Category.DISTRIBUTED_SYSTEMS: "distributed-systems/problems/data-management",
    Category.TRADEOFFS: "tradeoffs",
    Category.JAVA: "java/concurrency/problems",
}

# Problem-specific content templates keyed by keywords
PROBLEM_TEMPLATES = {
    # HLD templates
    "rag": {
        "concepts": ["Vector embeddings", "Semantic search", "Retrieval-augmented generation", "LLM integration"],
        "architecture": "Client → API Gateway → RAG Service\n"
                        "                        → Embedding Model (GPU)\n"
                        "                        → Vector DB (Milvus/Pinecone)\n"
                        "                        → LLM Service\n"
                        "                        → Document Store",
    },
    "llm": {
        "concepts": ["Model serving", "GPU batching", "Speculative decoding", "Continuous batching"],
        "architecture": "Client → API Gateway → LLM Router\n"
                        "                        → Model Server (vLLM/TGI)\n"
                        "                        → GPU Pool\n"
                        "                        → Token Counter\n"
                        "                        → Cache (Redis)",
    },
    "fraud": {
        "concepts": ["Real-time scoring", "ML model serving", "Rule engine", "Stream processing"],
        "architecture": "Transaction → Kafka → Fraud Detector\n"
                        "                        → Rule Engine\n"
                        "                        → ML Model Server\n"
                        "                        → Alert System\n"
                        "                        → Blocklist DB",
    },
    "flash sale": {
        "concepts": ["Thundering herd", "Queue-based throttling", "Inventory reservation", "Fairness"],
        "architecture": "Client → CDN → API Gateway → Queue\n"
                        "                        → Worker Pool\n"
                        "                        → Inventory Service\n"
                        "                        → Payment Service",
    },
    "streaming": {
        "concepts": ["Ingest", "Transcoding", "Adaptive bitrate", "CDN distribution"],
        "architecture": "Streamer → Ingest Server → Transcoder Farm\n"
                        "                        → Origin Storage\n"
                        "                        → Multi-CDN\n"
                        "                        → Client (HLS/DASH)",
    },
    "ad": {
        "concepts": ["Real-time bidding", "Auction engine", "Budget pacing", "Impression tracking"],
        "architecture": "Publisher → Ad Server → Auction Engine\n"
                        "                        → Bidder Pool\n"
                        "                        → Creative Store\n"
                        "                        → Analytics Pipeline",
    },
    "wallet": {
        "concepts": ["Double-entry bookkeeping", "Idempotency", "Fraud detection", "Multi-currency"],
        "architecture": "Client → API Gateway → Wallet Service\n"
                        "                        → Ledger DB\n"
                        "                        → Fraud Check\n"
                        "                        → Notification Service",
    },
    "workflow": {
        "concepts": ["DAG execution", "Fault tolerance", "Retry policies", "State management"],
        "architecture": "Client → API Gateway → Workflow Engine\n"
                        "                        → Task Queue\n"
                        "                        → Worker Pool\n"
                        "                        → State Store\n"
                        "                        → Event Log",
    },
    # LLD templates
    "text editor": {
        "concepts": ["Gap buffer", "Command pattern", "Undo/redo", "OT/CRDT"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│   Document   │────►│    Buffer    │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - history    │     │ - gapStart   │\n"
                         "│ - cursor     │     │ - gapLength  │\n"
                         "└──────────────┘     └──────────────┘\n"
                         "          │\n"
                         "   ┌──────┴──────┐\n"
                         "   │  Command    │\n"
                         "   ├─────────────┤\n"
                         "   │ - undo/redo │\n"
                         "   └─────────────┘",
    },
    "snake": {
        "concepts": ["State machine", "Deque", "Collision detection", "Grid management"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│     Game     │────►│     Grid     │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - snake      │     │ - cells      │\n"
                         "│ - food       │     │ - obstacles  │\n"
                         "└──────────────┘     └──────────────┘",
    },
    "splitwise": {
        "concepts": ["Expense splitting", "Debt simplification", "Graph algorithms", "Balances"],
        "class_diagram": "┌──────────────┐     ┌──────────────┐\n"
                         "│   Group      │────►│   Expense    │\n"
                         "├──────────────┤     ├──────────────┤\n"
                         "│ - members    │     │ - amount     │\n"
                         "│ - balances   │     │ - splitType  │\n"
                         "└──────────────┘     └──────────────┘",
    },
    # Distributed systems templates
    "vector": {
        "concepts": ["HNSW/IVF-PQ", "ANN search", "Sharding", "Metadata filtering"],
        "architecture": "Client → API Gateway → Vector Service\n"
                        "                        → Index Shards\n"
                        "                        → Metadata Store\n"
                        "                        → Embedding Pipeline",
    },
    "feature store": {
        "concepts": ["Online/offline storage", "Point-in-time correctness", "Training-serving skew"],
        "architecture": "ML Pipeline → Feature Writer → Online Store (Redis)\n"
                        "                        → Offline Store (Parquet)\n"
                        "                        → Feature Registry",
    },
    "secret": {
        "concepts": ["AES-256-GCM", "Shamir sharing", "Dynamic secrets", "RBAC"],
        "architecture": "Client → API Gateway → Vault Service\n"
                        "                        → Encryption Engine\n"
                        "                        → Secret Backend\n"
                        "                        → Audit Log",
    },
}


# ------------------------------------------------------------------ #
#  Fuzzy matching utilities
# ------------------------------------------------------------------ #

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """Return similarity ratio between 0 and 1."""
    if not s1 or not s2:
        return 0.0
    distance = levenshtein_distance(s1.lower(), s2.lower())
    max_len = max(len(s1), len(s2))
    return 1.0 - (distance / max_len) if max_len > 0 else 0.0


def normalize_name(name: str) -> str:
    """Normalize a problem name for comparison."""
    name = name.lower().strip()
    # Remove common prefixes/suffixes
    for prefix in ["design ", "build ", "implement "]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    # Replace separators
    name = re.sub(r"[-_\s]+", "-", name.strip())
    # Remove trailing/leading dashes
    name = name.strip("-")
    return name


# ------------------------------------------------------------------ #
#  Templates
# ------------------------------------------------------------------ #

HLD_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Architecture Overview

```
{architecture}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

LLD_TEMPLATE = """# {name}

## Problem Statement (Staff-Level)

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Class Diagram

```
{class_diagram}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

DS_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Requirements

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## Key Design Decisions
{key_decisions}

## Architecture Overview

```
{architecture}
```

## Staff-Level Design Considerations

{staff_considerations}
"""

TRADEOFF_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## When to Use {option_a}
{when_a}

## When to Use {option_b}
{when_b}

## Decision Framework
{decision_framework}

## Staff-Level Insights
{staff_insights}
"""

JAVA_TEMPLATE = """# {name}

## Problem Statement

{description}

**Reference**: {sources}

## Key Concepts
{key_concepts}

## Implementation
{implementation}

## Staff-Level Design Considerations

{staff_considerations}
"""


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
        """Return trending problems that are not already in the repo.

        Uses fuzzy matching (Levenshtein distance) to catch near-duplicates.
        Also checks run history to avoid re-adding problems from previous agent runs.
        """
        existing_normalized = {normalize_prob.slug: normalize_prob for normalize_prob in existing}
        existing_names_lower = {prob.name.lower() for prob in existing}
        existing_normalized_names = {normalize_name(prob.name): prob for prob in existing}

        # Add run history slugs to exclude set
        history_slugs = run_history_slugs or set()

        missing: list = []
        skipped_exact = 0
        skipped_fuzzy = 0
        skipped_history = 0

        for prob in trending:
            norm = normalize_name(prob.name)

            # Skip if already in run history
            if prob.slug in history_slugs or norm in history_slugs:
                skipped_history += 1
                continue

            # Exact slug match
            if prob.slug in existing_normalized:
                skipped_exact += 1
                continue

            # Exact name match
            if prob.name.lower() in existing_names_lower:
                skipped_exact += 1
                continue

            # Normalized name match
            if norm in existing_normalized_names:
                skipped_exact += 1
                continue

            # Fuzzy match against all existing names
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

        # Limit problems per run
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
    #  Content generators (with problem-specific templates)
    # ------------------------------------------------------------------ #
    def _get_template_override(self, prob: TrendingProblem) -> dict:
        """Check if there's a problem-specific template override."""
        name_lower = prob.name.lower()
        for keyword, template in PROBLEM_TEMPLATES.items():
            if keyword in name_lower:
                return template
        return {}

    def _generate_hld(self, prob: TrendingProblem) -> str:
        """Generate HLD problem README with problem-specific content."""
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or [
            "Scalability", "Reliability", "Performance"
        ]
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
        """Generate LLD problem README with problem-specific content."""
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or [
            "Design patterns", "OOP", "SOLID principles"
        ]
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
        """Generate Distributed Systems problem README."""
        override = self._get_template_override(prob)
        concepts = override.get("concepts") or prob.key_concepts or [
            "Consistency", "Partition tolerance", "Distributed consensus"
        ]
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
        """Generate Trade-off problem README."""
        parts = prob.name.split(" vs ")
        option_a = parts[0].strip() if len(parts) > 1 else "Option A"
        option_b = parts[1].strip() if len(parts) > 1 else "Option B"

        return TRADEOFF_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Understand the trade-offs between {option_a} and {option_b} in system design decisions.",
            sources=prob.source,
            option_a=option_a,
            option_b=option_b,
            when_a=f"- **Predictable performance**: {option_a} provides consistent behavior\n- **Simplicity**: Easier to reason about and debug\n- **Tooling**: Mature ecosystem and tooling support",
            when_b=f"- **Flexibility**: {option_b} adapts to varying workloads\n- **Scalability**: Better horizontal scaling characteristics\n- **Cost**: Potentially lower operational costs at scale",
            decision_framework=f"""| Factor | {option_a} | {option_b} |
|--------|-----------|-----------|
| Performance | Predictable | Variable |
| Scalability | Vertical | Horizontal |
| Complexity | Low | Medium |
| Cost | Higher at scale | Lower at scale |
| Learning Curve | Steep | Gradual |""",
            staff_insights=f"""- **Context matters**: The right choice depends on your specific workload, team size, and growth trajectory.
- **Staff insight**: Start with {option_a} for simplicity; migrate to {option_b} when you hit scaling limits. The cost of premature optimization often exceeds the cost of migration.
- **Hybrid approach**: Many production systems use both, applying each where it excels. Evaluate at component granularity, not just system level.""",
        )

    def _generate_java(self, prob: TrendingProblem) -> str:
        """Generate Java problem README."""
        concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Java concurrency, JVM internals"

        return JAVA_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Implement and understand {prob.name.lower()} in Java, covering concurrency patterns, performance considerations, and production best practices.",
            sources=prob.source,
            key_concepts=f"""- **Core concept**: {concepts}
- **Thread safety**: Proper synchronization and atomic operations
- **Performance**: Benchmarking with JMH, profiling with JFR
- **Best practices**: Java 17+ features, modern concurrency patterns""",
            implementation=f"""```java
// TODO: Implement {prob.name}
// Key considerations:
// - Thread safety with proper synchronization
// - Performance optimization
// - Edge case handling
```""",
            staff_considerations=f"""### Performance Considerations
- **Benchmarking**: Use JMH for accurate micro-benchmarks; warm-up phases are critical.
- **Profiling**: Use JFR (Java Flight Recorder) for low-overhead production profiling.
- **Staff insight**: Always measure before optimizing. Use async-profiler for CPU and allocation profiling in production.

### Concurrency Best Practices
- **Prefer high-level constructs**: Use `CompletableFuture`, `ExecutorService`, and concurrent collections over raw threads.
- **Avoid shared mutable state**: Use immutable objects and thread-local storage where possible.
- **Staff insight**: The best synchronization is no synchronization. Design for immutability first, then add concurrency where absolutely necessary.""",
        )

    def _generate_generic(self, prob: TrendingProblem) -> str:
        """Generate a generic problem README."""
        return f"""# {prob.name}

## Problem Statement

{prob.description or f"Design and implement {prob.name.lower()}."}

**Reference**: {prob.source}

## Requirements

### Functional Requirements
- Core functionality for {prob.name.lower()}
- Scalability and performance considerations
- Error handling and edge cases

### Non-Functional Requirements
- **Scale**: Handle production-level load
- **Latency**: Sub-second response times
- **Availability**: 99.9% uptime

## Key Design Decisions
- Choose appropriate design patterns and data structures
- Consider thread safety and concurrency
- Plan for horizontal scaling

## Staff-Level Design Considerations

### Architecture
- **Modularity**: Design for extensibility and maintainability
- **Testing**: Comprehensive unit and integration tests
- **Staff insight**: Focus on the core abstractions first; details can be refined iteratively.
"""

    # ------------------------------------------------------------------ #
    #  Helper methods
    # ------------------------------------------------------------------ #
    def _describe_problem(self, prob: TrendingProblem, type_: str) -> str:
        """Generate a problem description based on type."""
        descriptions = {
            "hld": f"Design a {prob.name.lower()} that handles large-scale production workloads with high availability, low latency, and horizontal scalability.",
            "lld": f"Design and implement a {prob.name.lower()} with proper object-oriented design principles, design patterns, and thread-safe operations.",
            "ds": f"Design a distributed {prob.name.lower()} that provides consistency, fault tolerance, and horizontal scalability across multiple nodes.",
        }
        return descriptions.get(type_, f"Design and implement {prob.name.lower()}.")

    def _generate_functional_reqs(self, prob: TrendingProblem, concepts: list = None) -> str:
        """Generate functional requirements bullet points."""
        if concepts is None:
            concepts = prob.key_concepts or ["core functionality", "data management", "API design"]
        lines = []
        for concept in concepts[:5]:
            lines.append(f"- **{concept.title()}**: Support {concept.lower()} with proper error handling and validation.")
        return "\n".join(lines)

    def _generate_non_functional_reqs(self, prob: TrendingProblem) -> str:
        """Generate non-functional requirements."""
        return """- **Scale**: Handle 1M+ users and 100K+ requests per second.
- **Latency**: P99 response time < 200ms for read operations.
- **Availability**: 99.9% uptime with graceful degradation.
- **Consistency**: Eventual consistency with configurable strong consistency for critical paths."""

    def _generate_key_decisions(self, prob: TrendingProblem, concepts: str) -> str:
        """Generate key design decisions."""
        return f"""- **Architecture**: Microservices with API gateway for {prob.name.lower()}.
- **Data storage**: Choose between SQL and NoSQL based on access patterns.
- **Caching**: Multi-tier caching strategy (CDN + Redis + application cache).
- **Key concepts**: {concepts}."""

    def _generate_architecture(self, prob: TrendingProblem) -> str:
        """Generate architecture diagram text."""
        return f"""Client → Load Balancer → API Gateway
                                → {prob.name} Service
                                → Database (Primary + Replica)
                                → Cache (Redis Cluster)
                                → Message Queue (Kafka)"""

    def _generate_class_diagram(self, prob: TrendingProblem) -> str:
        """Generate class diagram text."""
        first_word = prob.name.split()[0] if prob.name.split() else "Entity"
        return f"""┌──────────────┐     ┌──────────────┐
│   {first_word:<10}│────►│   Manager    │
├──────────────┤     ├──────────────┤
│ - properties │     │ - items      │
│ - state      │     │ - config     │
└──────────────┘     └──────────────┘
          │
          │ has
   ┌──────┴──────┐
   │   Handler   │
   ├─────────────┤
   │ - actions   │
   └─────────────┘"""

    def _generate_staff_considerations(
        self, prob: TrendingProblem, concepts: str
    ) -> str:
        """Generate staff-level design considerations."""
        return f"""### Scalability Strategy
- **Horizontal scaling**: Add more instances behind the load balancer.
- **Database sharding**: Partition data by user ID or tenant for write scaling.
- **Staff insight**: Start with a single database; shard only when you hit limits. Premature sharding adds operational complexity without benefit.

### Caching Strategy
- **Multi-tier**: CDN for static assets, Redis for hot data, application cache for computed results.
- **Cache invalidation**: Use TTL-based expiration with event-driven invalidation for critical data.
- **Staff insight**: Cache stampede is the #1 production issue. Use random TTL jitter and stampede protection (single-flight) to prevent thundering herd.

### Error Handling
- **Circuit breaker**: Prevent cascading failures when downstream services are slow.
- **Retry with backoff**: Exponential backoff with jitter for transient failures.
- **Staff insight**: Design for failure. Every external call can fail; every dependency can be slow. Build resilience at every layer.

### Key Concepts: {concepts}
- **Staff insight**: Focus on the trade-offs between consistency, availability, and partition tolerance. No system is perfect; choose the right consistency model for each component."""

    # ------------------------------------------------------------------ #
    #  README updates (proper line insertion)
    # ------------------------------------------------------------------ #
    def update_readme(self, problems: list) -> int:
        """Update the main README.md with new problems.

        Finds the appropriate section for each category and inserts
        the new problem entry in the correct table.
        Returns the number of changes made.
        """
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

            # Build the table row
            concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Trending topic"
            entry = f"| [{prob.name}]({prob.category.value}/problems/{prob.slug}/) | {concepts} |"

            # Find the insertion point based on category
            insert_idx = self._find_readme_insertion_point(lines, prob.category)
            if insert_idx is not None:
                lines.insert(insert_idx, entry)
                changes += 1
                logger.info("Added %s to README at line %d", prob.name, insert_idx + 1)
            else:
                logger.warning("Could not find insertion point in README for %s", prob.name)

        if changes > 0:
            readme_path.write_text("\n".join(lines))
            logger.info("Updated README.md with %d new entries", changes)

        return changes

    def _find_readme_insertion_point(self, lines: list, category: Category) -> Optional[int]:
        """Find the line number to insert a new problem entry in the README.

        Looks for the last table row in the appropriate category section.
        """
        # Map category to section header patterns
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
            # Check if we're entering the right section
            in_section = any(pattern in line for pattern in patterns)
            if in_section:
                # Find the next table row after this header
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("|"):
                        last_table_row = j
                    elif last_table_row is not None and lines[j].strip() and not lines[j].startswith("|"):
                        # End of table
                        return last_table_row + 1

        # If we found any table row, insert after it
        if last_table_row is not None:
            return last_table_row + 1

        return None
