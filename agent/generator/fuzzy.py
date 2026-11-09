"""Fuzzy matching utilities for problem name comparison."""

import re


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
