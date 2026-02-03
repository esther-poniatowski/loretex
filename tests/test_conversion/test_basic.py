"""Basic tests for conversion pipeline."""

from loretex.conversion import MarkdownToLaTeXConverter


def test_single_heading() -> None:
    """Test conversion of single heading."""
    converter = MarkdownToLaTeXConverter()

    markdown = "# Introduction"
    latex = converter.convert_string(markdown)

    assert r"\section{Introduction}" in latex


def test_nested_headings() -> None:
    """Test conversion of nested headings."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Chapter One
## First Section
### Subsection A
"""

    latex = converter.convert_string(markdown)

    assert r"\section{Chapter One}" in latex
    assert r"\subsection{First Section}" in latex
    assert r"\subsubsection{Subsection A}" in latex


def test_paragraph() -> None:
    """Test conversion of paragraph."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Title

This is a paragraph.
"""

    latex = converter.convert_string(markdown)

    assert r"\section{Title}" in latex
    assert "This is a paragraph." in latex


def test_unordered_list() -> None:
    """Test conversion of unordered list."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Items

- First item
- Second item
- Third item
"""

    latex = converter.convert_string(markdown)

    assert r"\begin{itemize}" in latex
    assert r"\item First item" in latex
    assert r"\item Second item" in latex
    assert r"\item Third item" in latex
    assert r"\end{itemize}" in latex


def test_ordered_list() -> None:
    """Test conversion of ordered list."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Steps

1. First step
2. Second step
3. Third step
"""

    latex = converter.convert_string(markdown)

    assert r"\begin{enumerate}" in latex
    assert r"\item First step" in latex
    assert r"\item Second step" in latex
    assert r"\item Third step" in latex
    assert r"\end{enumerate}" in latex


def test_nested_list() -> None:
    """Test conversion of nested list."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Hierarchy

- Top level item
  - Nested item 1
  - Nested item 2
- Another top level item
"""

    latex = converter.convert_string(markdown)

    assert r"\begin{itemize}" in latex
    assert r"\item Top level item" in latex
    assert r"\item Nested item 1" in latex
    assert r"\item Nested item 2" in latex
    assert r"\item Another top level item" in latex


def test_mixed_content() -> None:
    """Test conversion with mixed content types."""
    converter = MarkdownToLaTeXConverter()

    markdown = """# Document

This is a paragraph before the list.

- Item one
- Item two

This is a paragraph after the list.
"""

    latex = converter.convert_string(markdown)

    assert r"\section{Document}" in latex
    assert "This is a paragraph before the list." in latex
    assert r"\begin{itemize}" in latex
    assert r"\item Item one" in latex
    assert "This is a paragraph after the list." in latex
