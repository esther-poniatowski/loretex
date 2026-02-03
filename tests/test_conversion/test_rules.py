"""Rule coverage tests for md2latex converter."""

from loretex.conversion import MarkdownToLaTeXConverter


def test_code_block_python_to_lstlisting() -> None:
    """Convert Python fenced code block to lstlisting."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "```python\nprint('hi')\n```"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{lstlisting}" in latex
    assert "print('hi')" in latex
    assert r"\end{lstlisting}" in latex


def test_callout_converts_to_environment() -> None:
    """Convert callout block to custom LaTeX environment."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "> [!note] Titre\n> Ligne 1\n> Ligne 2"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{notebox}[Titre]" in latex
    assert "Ligne 1" in latex
    assert "Ligne 2" in latex
    assert r"\end{notebox}" in latex


def test_blockquote_strip_leading_chevron() -> None:
    """Strip leading chevrons for non-callout blockquotes."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "> Ligne 1\n> Ligne 2"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert "Ligne 1" in latex
    assert "Ligne 2" in latex
    assert "> Ligne" not in latex


def test_headings_convert_to_sections() -> None:
    """Convert heading levels to LaTeX section commands."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "# Titre\n## Sous-titre\n### Sous-sous-titre"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\section{Titre}" in latex
    assert r"\subsection{Sous-titre}" in latex
    assert r"\subsubsection{Sous-sous-titre}" in latex


def test_nested_unordered_lists() -> None:
    """Convert nested unordered lists to itemize environments."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "- Parent\n  - Enfant 1\n  - Enfant 2"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert latex.count(r"\begin{itemize}") == 2
    assert r"\item Parent" in latex
    assert r"\item Enfant 1" in latex
    assert r"\item Enfant 2" in latex


def test_ordered_list_conversion() -> None:
    """Convert ordered list to enumerate environment."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "1. Premier\n2. Second"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{enumerate}" in latex
    assert r"\item Premier" in latex
    assert r"\item Second" in latex
    assert r"\end{enumerate}" in latex


def test_inline_formatting_rules() -> None:
    """Convert inline bold, italic, and code formatting."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "Texte **gras** *italique* _italique_ `code`."

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\textbf{gras}" in latex
    assert r"\textit{italique}" in latex
    assert r"\texttt{code}" in latex


def test_inline_code_escapes_special_characters() -> None:
    """Escape LaTeX special characters inside inline code."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "Code `a_b%#\\`"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\texttt{a\_b\%\#\textbackslash{}}" in latex


def test_image_tag_conversion() -> None:
    """Convert HTML image tag to includegraphics."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = '<img src="figures-svg/figure_1.svg" width="250">'

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{center}" in latex
    assert (
        r"\includegraphics[width=250\htmlpx]{../figures-pdfs/figures-svg/figure_1.pdf}"
        in latex
    )
    assert r"\end{center}" in latex


def test_character_normalization() -> None:
    """Normalize typographic characters to LaTeX equivalents."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "≤ ≥ œ – ’"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\leq" in latex
    assert r"\geq" in latex
    assert "oe" in latex
    assert "-" in latex
    assert "'" in latex


def test_inline_formatting_not_applied_in_code_block() -> None:
    """Avoid inline formatting inside fenced code blocks."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "```python\n**gras**\n```"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert "**gras**" in latex
    assert r"\textbf{gras}" not in latex


def test_inline_formatting_not_applied_in_inline_code() -> None:
    """Avoid inline formatting inside inline code."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "Texte `**x**`"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\texttt{**x**}" in latex
    assert r"\textbf{x}" not in latex


def test_table_converts_to_tabular() -> None:
    """Convert Markdown table to LaTeX tabular environment."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "| A | B |\n|---|---|\n| 1 | 2 |"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{tabular}{ll}" in latex
    assert "A & B" in latex
    assert "1 & 2" in latex
    assert r"\hline" in latex
    assert r"\end{tabular}" in latex


def test_table_alignment_detection() -> None:
    """Detect left, center, and right alignment from separator."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "| L | C | R |\n|:--|:--:|--:|\n| a | b | c |"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\begin{tabular}{lcr}" in latex


def test_table_inline_formatting() -> None:
    """Apply inline formatting inside table cells."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "| Text |\n|------|\n| **bold** |"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\textbf{bold}" in latex


def test_table_br_to_newline() -> None:
    """Convert <br> tags to newline in table cells."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = "| Text |\n|------|\n| Line1<br>Line2 |"

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    assert r"\newline" in latex


def test_strip_yaml_front_matter() -> None:
    """Strip YAML front matter when configured."""
    converter = MarkdownToLaTeXConverter()
    markdown = """---
title: Sample
tags:
  - demo
---

# Heading

Content here.
"""
    latex = converter.convert_string(
        markdown,
        overrides={"parsing": {"strip_yaml_front_matter": True}},
    )
    assert r"\section{Heading}" in latex
    assert "title:" not in latex


def test_citation_single() -> None:
    """Convert [@key] to \\cite{key}."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [@doe2020]."
    latex = converter.convert_string(markdown)
    assert r"\cite{doe2020}" in latex


def test_citation_multiple() -> None:
    """Convert [@a; @b] to \\cite{a,b}."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [@doe2020; @smith2021]."
    latex = converter.convert_string(markdown)
    assert r"\cite{doe2020,smith2021}" in latex


def test_citation_with_locator() -> None:
    """Convert [@key, p. 2] to \\cite[p. 2]{key}."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [@doe2020, p. 2]."
    latex = converter.convert_string(markdown)
    assert r"\cite[p. 2]{doe2020}" in latex


def test_math_block_brackets() -> None:
    """Convert $$...$$ to \\[...\\] when configured."""
    converter = MarkdownToLaTeXConverter()
    markdown = "$$\nE = mc^2\n$$"
    latex = converter.convert_string(
        markdown,
        overrides={"math": {"block_style": "brackets"}},
    )
    assert r"\[" in latex
    assert r"\]" in latex


def test_table_colspan() -> None:
    """Support colspan in table cells."""
    converter = MarkdownToLaTeXConverter()
    markdown = "| A | B | C |\n|---|---|---|\n| Span{col=2} | X |"
    latex = converter.convert_string(markdown)
    assert r"\multicolumn{2}{c}{Span}" in latex
