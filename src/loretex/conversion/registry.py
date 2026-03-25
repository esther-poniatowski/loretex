"""
Registry for conversion transforms.

The module-level ``_TRANSFORMS`` dict acts as the default global registry.
Use :func:`clear_transforms` (or :func:`snapshot_transforms` /
:func:`restore_transforms`) for test isolation and lifecycle control.
"""

from __future__ import annotations

from typing import Iterable

from .transforms import Transform


class TransformRegistry:
    """Explicit registry for named AST transforms."""

    def __init__(self, transforms: dict[str, Transform] | None = None) -> None:
        self._transforms = dict(transforms or {})

    def register(self, name: str, transform: Transform, *, overwrite: bool = False) -> None:
        if name in self._transforms and not overwrite:
            raise KeyError(f"Transform '{name}' is already registered.")
        self._transforms[name] = transform

    def get(self, name: str) -> Transform:
        try:
            return self._transforms[name]
        except KeyError as exc:
            raise KeyError(f"Unknown transform '{name}'.") from exc

    def list(self) -> list[str]:
        return sorted(self._transforms.keys())

    def resolve(self, names: Iterable[str]) -> list[Transform]:
        return [self.get(name) for name in names]

    def clear(self) -> None:
        self._transforms.clear()

    def snapshot(self) -> dict[str, Transform]:
        return dict(self._transforms)

    def restore(self, snapshot: dict[str, Transform]) -> None:
        self._transforms.clear()
        self._transforms.update(snapshot)


_DEFAULT_REGISTRY = TransformRegistry()


def register_transform(name: str, transform: Transform, *, overwrite: bool = False) -> None:
    """Register a transform by name."""
    _DEFAULT_REGISTRY.register(name, transform, overwrite=overwrite)


def get_transform(name: str) -> Transform:
    """Retrieve a transform by name."""
    return _DEFAULT_REGISTRY.get(name)


def list_transforms() -> list[str]:
    """List registered transform names."""
    return _DEFAULT_REGISTRY.list()


def resolve_transforms(names: Iterable[str]) -> list[Transform]:
    """Resolve names into transform callables."""
    return _DEFAULT_REGISTRY.resolve(names)


# ---------------------------------------------------------------------------
# Lifecycle control (Fix 5)
# ---------------------------------------------------------------------------


def clear_transforms() -> None:
    """Remove all registered transforms.

    Useful in test teardown to prevent cross-test pollution.
    """
    _DEFAULT_REGISTRY.clear()


def snapshot_transforms() -> dict[str, Transform]:
    """Return a shallow copy of the current registry.

    Pair with :func:`restore_transforms` for save/restore semantics in tests.
    """
    return _DEFAULT_REGISTRY.snapshot()


def restore_transforms(snapshot: dict[str, Transform]) -> None:
    """Replace the global registry with a previous snapshot."""
    _DEFAULT_REGISTRY.restore(snapshot)


def get_default_registry() -> TransformRegistry:
    """Return the process-local default transform registry."""
    return _DEFAULT_REGISTRY
