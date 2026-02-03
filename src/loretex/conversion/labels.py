"""
Label normalization helpers.
"""

from __future__ import annotations


def slugify(text: str, separator: str = "-") -> str:
    normalized = text.strip().lower()
    normalized = "".join(
        char if char.isalnum() else separator for char in normalized
    )
    while separator * 2 in normalized:
        normalized = normalized.replace(separator * 2, separator)
    return normalized.strip(separator)
