"""Fuzzy matching utilities for problem name comparison and subfolder routing."""

import re

# Keyword hints for routing LLD problems into the correct difficulty/concurrency
# subfolder, matching the repo's existing organization (see lld/problems/*).
LLD_CONCURRENCY_HINTS = [
    "thread", "concurrent", "concurren", "lock", "semaphore", "barrier",
    "latch", "phaser", "executor", "queue", "pool", "deadlock", "race",
    "atomic", "synchroniz", "producer", "consumer", "countdown", "mutex",
    "blocking", "cyclic", "read-write", "cache with ttl", "rate limit",
]

LLD_EASY_HINTS = [
    "tic-tac-toe", "tic tac toe", "snake", "lru", "lfu", "parking lot",
    "vending machine", "insert delete", "shuffle", "min stack", "unix",
]

LLD_MEDIUM_HINTS = [
    "atm", "elevator", "hotel", "library", "restaurant", "coffee", "traffic",
    "taxi", "movie", "concert", "car rental", "task", "logging", "logger",
    "notification", "wallet", "expense", "split", "airline", "inventory",
    "stack overflow", "pubsub", "pub-sub", "social", "editor", "calendar",
    "vending", "cache", "strategy", "board game", "auction", "linkedin",
]

# Distributed systems subfolder routing (mirrors distributed-systems/problems/*)
DS_SUBFOLDER_HINTS = [
    ("coordination", ["lock", "leader", "election", "consensus", "hashing", "raft", "paxos", "zookeeper"]),
    ("data-management", ["cache", "config", "session", "vector", "feature", "store", "database", "kv", "storage"]),
    ("messaging-events", ["event", "cqrs", "sourcing", "message", "stream", "kafka", "queue", "outbox", "inbox"]),
    ("resilience", ["breaker", "rate limit", "ratelimit", "throttle", "retry", "bulkhead", "timeout", "fallback"]),
    ("observability", ["tracing", "metric", "monitor", "log aggregation", "alert", "telemetry"]),
    ("infrastructure", ["id generat", "uuid", "snowflake", "search", "file", "blob", "secret", "vault", "dns"]),
    ("scheduling", ["scheduler", "cron", "workflow", "dag", "job", "task queue", "batch"]),
]


def route_lld_subfolder(name_lower: str) -> str:
    """Pick the LLD subfolder matching the repo's difficulty organization."""
    if any(h in name_lower for h in LLD_CONCURRENCY_HINTS):
        return "lld/problems/concurrency"
    if any(h in name_lower for h in LLD_EASY_HINTS):
        return "lld/problems/easy"
    if any(h in name_lower for h in LLD_MEDIUM_HINTS):
        return "lld/problems/medium"
    return "lld/problems/hard"


def route_ds_subfolder(name_lower: str) -> str:
    """Pick the distributed-systems subfolder matching the repo's categories."""
    for subfolder, hints in DS_SUBFOLDER_HINTS:
        if any(h in name_lower for h in hints):
            return f"distributed-systems/problems/{subfolder}"
    return "distributed-systems/problems/data-management"


def route_subfolder(category_value: str, name_lower: str, default: str) -> str:
    """Route a problem to the right subfolder based on category and name."""
    if category_value == "lld":
        return route_lld_subfolder(name_lower)
    if category_value == "distributed-systems":
        return route_ds_subfolder(name_lower)
    return default


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
