"""Tests for footnote and wiki-link handling."""

from loretex.conversion import MarkdownToLaTeXConverter


def test_footnote_conversion() -> None:
    """Convert footnote references and definitions to \\footnote{}."""
    converter = MarkdownToLaTeXConverter()
    markdown = "Text with footnote.[^1]\n\n[^1]: Footnote text."
    latex = converter.convert_string(markdown)
    assert r"\footnote{Footnote text.}" in latex
    assert "[^1]:" not in latex


def test_footnote_multiline() -> None:
    """Support multi-line footnotes."""
    converter = MarkdownToLaTeXConverter()
    markdown = "Text.[^1]\n\n[^1]: First line.\n    Second line.\n"
    latex = converter.convert_string(markdown)
    assert "First line." in latex
    assert "Second line." in latex


def test_wiki_link_conversion() -> None:
    """Convert wiki links to references."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [[My Note]] and [[My Note|alias]]."
    latex = converter.convert_string(markdown)
    assert r"\ref{my-note}" in latex
