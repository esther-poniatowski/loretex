"""Fixture-based tests for md2latex converter."""

from __future__ import annotations

from pathlib import Path

import pytest

from loretex.conversion import MarkdownToLaTeXConverter

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"

FIXTURE_EXPECTATIONS: list[tuple[str, list[str]]] = [
    (
        "inline-formatting.md",
        [
            r"\textbf{bold}",
            r"\textit{italic}",
            r"\texttt{a\_b\%\#\textbackslash{}",
            r"\texttt{**not bold**}",
            r"\includegraphics",
        ],
    ),
    (
        "code-blocks.md",
        [
            r"\begin{lstlisting}",
            "def add(a, b):",
            "**bold**",
            r"\end{lstlisting}",
        ],
    ),
    (
        "callouts.md",
        [
            r"\begin{notebox}[Title line]",
            r"\begin{warningbox}",
            r"\item item one",
            r"\includegraphics",
        ],
    ),
    (
        "images.md",
        [
            r"\includegraphics[width=220\htmlpx]{../figures-pdfs/figs/figure-one.pdf}",
            r"\includegraphics[width=150\htmlpx]{../figures-pdfs/figs/figure-two.pdf}",
        ],
    ),
    (
        "lists.md",
        [
            r"\begin{itemize}",
            r"\begin{enumerate}",
            r"\item Item one",
            r"\item Ordered one",
        ],
    ),
    (
        "blockquotes.md",
        [
            "This is a quoted line.",
            r"\textbf{bold}",
        ],
    ),
    (
        "mixed-structure.md",
        [
            r"\section{Mixed Document}",
            r"\subsection{Section A}",
            r"\subsubsection{Subsection A1}",
            r"\paragraph{Minor Heading}",
            r"\begin{importantbox}[Reminder]",
            r"\begin{lstlisting}",
        ],
    ),
    (
        "edge-cases.md",
        [
            "pre*fix",
            "pre_fix",
            "asterisk*stuck",
            "x_1",
        ],
    ),
    (
        "tables.md",
        [
            r"\begin{tabular}{lcr}",
            r"\hline",
            "Name & Age & City",
            "Alice & 30 & Paris",
            r"\end{tabular}",
            r"\textbf{Bold}",
            r"\newline",
        ],
    ),
]


@pytest.mark.parametrize("fixture_name, expected_snippets", FIXTURE_EXPECTATIONS)
def test_fixture_conversion_contains_expected_snippets(
    fixture_name: str,
    expected_snippets: list[str],
) -> None:
    """Verify fixture conversion includes expected LaTeX markers."""
    # Arrange
    converter = MarkdownToLaTeXConverter()
    markdown = (FIXTURE_DIR / fixture_name).read_text(encoding="utf-8")

    # Act
    latex = converter.convert_string(markdown)

    # Assert
    for snippet in expected_snippets:
        assert snippet in latex
