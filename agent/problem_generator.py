"""
Problem generator for the SystemDesign agent.

Compares scraped trending problems with existing repo problems,
generates new README files, and updates the main README.
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

# ------------------------------------------------------------------ #
#  Problem templates
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

                # Each subdirectory is a problem
                for item in base.iterdir():
                    if item.is_dir() and (item / "README.md").exists():
                        name = item.name.replace("-", " ").title()
                        problems.append(ExistingProblem(
                            name=name,
                            category=category,
                            path=str(item),
                            slug=item.name,
                        ))

        return problems

    # ------------------------------------------------------------------ #
    #  Filter missing problems
    # ------------------------------------------------------------------ #
    def filter_missing(
        self, trending: list, existing: list
    ) -> list:
        """Return trending problems that are not already in the repo."""
        existing_slugs = {prob.slug for prob in existing}
        existing_names_lower = {prob.name.lower() for prob in existing}

        missing: list = []
        for prob in trending:
            # Skip if slug or name already exists
            if prob.slug in existing_slugs:
                continue
            if prob.name.lower() in existing_names_lower:
                continue
            # Fuzzy check: "tic-tac-toe" vs "Tic Tac Toe"
            slug_normalized = prob.slug.replace("-", "")
            if any(slug_normalized in slug.replace("-", "") for slug in existing_slugs):
                continue

            missing.append(prob)

        logger.info(
            "Found %d missing problems out of %d trending", len(missing), len(trending)
        )
        return missing

    # ------------------------------------------------------------------ #
    #  Generate all files
    # ------------------------------------------------------------------ #
    def generate_all(self, problems: list) -> list:
        """Generate README files for all missing problems."""
        generated: list = []

        for prob in problems:
            try:
                file = self._generate_one(prob)
                if file:
                    generated.append(file)
            except Exception as exc:
                logger.error("Failed to generate %s: %s", prob.name, exc)

        return generated

    def _generate_one(self, prob: TrendingProblem) -> Optional[GeneratedFile]:
        """Generate a single problem README."""
        # Determine the directory (use first path for the category)
        paths = CATEGORY_PATHS.get(prob.category)
        if not paths:
            logger.warning("Unknown category: %s", prob.category)
            return None

        relative = paths[0]
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

        logger.info("Generated %s", file_path)
        return GeneratedFile(
            path=str(file_path.relative_to(self.repo_path)),
            content=content,
            category=prob.category,
            problem_name=prob.name,
        )

    # ------------------------------------------------------------------ #
    #  Content generators
    # ------------------------------------------------------------------ #
    def _generate_hld(self, prob: TrendingProblem) -> str:
        """Generate HLD problem README."""
        concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Scalability, reliability, performance"

        return HLD_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Design a {prob.name.lower()} that handles large-scale production workloads with high availability, low latency, and horizontal scalability.",
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts),
            architecture=self._generate_architecture(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts),
        )

    def _generate_lld(self, prob: TrendingProblem) -> str:
        """Generate LLD problem README."""
        concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Design patterns, OOP, SOLID principles"

        return LLD_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Design and implement a {prob.name.lower()} with proper object-oriented design principles, design patterns, and thread-safe operations.",
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts),
            class_diagram=self._generate_class_diagram(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts),
        )

    def _generate_ds(self, prob: TrendingProblem) -> str:
        """Generate Distributed Systems problem README."""
        concepts = ", ".join(prob.key_concepts) if prob.key_concepts else "Consistency, partition tolerance, distributed consensus"

        return HLD_TEMPLATE.format(
            name=prob.name,
            description=prob.description or f"Design a distributed {prob.name.lower()} that provides consistency, fault tolerance, and horizontal scalability across multiple nodes.",
            sources=prob.source,
            functional_reqs=self._generate_functional_reqs(prob),
            non_functional_reqs=self._generate_non_functional_reqs(prob),
            key_decisions=self._generate_key_decisions(prob, concepts),
            architecture=self._generate_architecture(prob),
            staff_considerations=self._generate_staff_considerations(prob, concepts),
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
    def _generate_functional_reqs(self, prob: TrendingProblem) -> str:
        """Generate functional requirements bullet points."""
        concepts = prob.key_concepts if prob.key_concepts else ["core functionality", "data management", "API design"]
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
        return f"""┌──────────────┐     ┌──────────────┐
│   {prob.name.split()[0]}     │────►│   Manager    │
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
    #  README updates
    # ------------------------------------------------------------------ #
    def update_readme(self, problems: list) -> list:
        """Update the main README.md with new problems."""
        readme_path = self.repo_path / "README.md"
        if not readme_path.exists():
            logger.warning("README.md not found at %s", readme_path)
            return []

        content = readme_path.read_text()
        changes = []

        for prob in problems:
            # Add entry to the appropriate section
            entry = f"| [{prob.name}]({prob.category.value}/problems/{prob.slug}/) | {', '.join(prob.key_concepts)} |"

            if prob.category == Category.HLD:
                # Find the HLD problems section and add the entry
                if prob.name.lower() not in content.lower():
                    changes.append(entry)
                    logger.info("Added %s to README HLD section", prob.name)

        return changes
