"""
Registry for conversion transforms.
"""

from __future__ import annotations

from typing import Iterable

from .transforms import Transform

_TRANSFORMS: dict[str, Transform] = {}


def register_transform(name: str, transform: Transform, *, overwrite: bool = False) -> None:
    """Register a transform by name."""
    if name in _TRANSFORMS and not overwrite:
        raise KeyError(f"Transform '{name}' is already registered.")
    _TRANSFORMS[name] = transform


def get_transform(name: str) -> Transform:
    """Retrieve a transform by name."""
    try:
        return _TRANSFORMS[name]
    except KeyError as exc:
        raise KeyError(f"Unknown transform '{name}'.") from exc


def list_transforms() -> list[str]:
    """List registered transform names."""
    return sorted(_TRANSFORMS.keys())


def resolve_transforms(names: Iterable[str]) -> list[Transform]:
    """Resolve names into transform callables."""
    return [get_transform(name) for name in names]
