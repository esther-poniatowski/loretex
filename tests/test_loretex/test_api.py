"""Tests for public API helpers."""

from pathlib import Path

from loretex import convert_file, convert_string


def test_api_convert_string() -> None:
    """convert_string returns LaTeX output."""
    latex = convert_string("# Title")
    assert r"\section{Title}" in latex


def test_api_convert_file(tmp_path: Path) -> None:
    """convert_file writes output when output_path is provided."""
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.tex"
    input_file.write_text("# Title\n\nText", encoding="utf-8")
    latex = convert_file(input_file, output_file)
    assert r"\section{Title}" in latex
    assert output_file.read_text(encoding="utf-8").startswith(r"\section{Title}")
