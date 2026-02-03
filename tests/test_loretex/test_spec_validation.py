"""Tests for spec validation."""

import pytest

from loretex.api import convert_spec
from loretex.config.validate import SpecValidationError


def test_spec_validation_requires_chapter_file(tmp_path):
    spec = tmp_path / "spec.yml"
    spec.write_text("chapters:\n  - {}", encoding="utf-8")
    with pytest.raises(SpecValidationError):
        convert_spec(spec)
