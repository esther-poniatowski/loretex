"""
Transformation pipeline for AST manipulation.
"""

from __future__ import annotations

from typing import Iterable, Protocol

from .nodes import Document


class Transform(Protocol):
    """Callable transform that returns a new Document."""

    def __call__(self, document: Document) -> Document:
        ...


def apply_transforms(document: Document, transforms: Iterable[Transform]) -> Document:
    """Apply transforms sequentially to the document."""
    current = document
    for transform in transforms:
        current = transform(current)
    return current
