"""
Specification validation helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from loretex.config.exceptions import SpecValidationError
from loretex.config.params import SpecParams


def validate_spec(spec: dict[str, Any], *, base_dir: Path | None = None) -> None:
    """Validate a spec by materializing the canonical typed model."""
    SpecParams.from_spec(spec, base_dir=base_dir)
