"""Tests for internal link and label handling."""

from loretex.conversion import MarkdownToLaTeXConverter


def test_internal_link_to_ref() -> None:
    """Convert [text](#label) to \\ref{label}."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [section](#intro)."
    latex = converter.convert_string(markdown)
    assert r"\ref{intro}" in latex


def test_auto_label_headings() -> None:
    """Add labels to headings when enabled."""
    converter = MarkdownToLaTeXConverter()
    markdown = "# Intro Section"
    latex = converter.convert_string(
        markdown,
        overrides={"labels": {"auto_label_headings": True}},
    )
    assert r"\label{intro-section}" in latex
