"""
Registry for conversion transforms.

The module-level ``_TRANSFORMS`` dict acts as the default global registry.
Use :func:`clear_transforms` (or :func:`snapshot_transforms` /
:func:`restore_transforms`) for test isolation and lifecycle control.
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


# ---------------------------------------------------------------------------
# Lifecycle control (Fix 5)
# ---------------------------------------------------------------------------


def clear_transforms() -> None:
    """Remove all registered transforms.

    Useful in test teardown to prevent cross-test pollution.
    """
    _TRANSFORMS.clear()


def snapshot_transforms() -> dict[str, Transform]:
    """Return a shallow copy of the current registry.

    Pair with :func:`restore_transforms` for save/restore semantics in tests.
    """
    return dict(_TRANSFORMS)


def restore_transforms(snapshot: dict[str, Transform]) -> None:
    """Replace the global registry with a previous snapshot."""
    _TRANSFORMS.clear()
    _TRANSFORMS.update(snapshot)
