"""Unit tests for LaTeX generator."""

from __future__ import annotations

from loretex.conversion import ConversionConfig, InlineTransformer, LaTeXGenerator
from loretex.conversion import (
    Callout,
    CodeBlock,
    Document,
    Image,
    List,
    ListItem,
    Paragraph,
    Section,
    Table,
)


class TestInlineTransformer:
    """Tests for InlineTransformer class."""

    def test_bold_conversion(self) -> None:
        """Convert **bold** to \\textbf."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("This is **bold** text")

        # Assert
        assert r"\textbf{bold}" in result

    def test_italic_star_conversion(self) -> None:
        """Convert *italic* to \\textit."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("This is *italic* text")

        # Assert
        assert r"\textit{italic}" in result

    def test_italic_underscore_conversion(self) -> None:
        """Convert _italic_ to \\textit."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("This is _italic_ text")

        # Assert
        assert r"\textit{italic}" in result

    def test_inline_code_conversion(self) -> None:
        """Convert `code` to \\texttt."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("Use `print()` function")

        # Assert
        assert r"\texttt{print()}" in result

    def test_inline_code_escapes_backslash(self) -> None:
        """Escape backslash in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert(r"`\n`")

        # Assert
        assert r"\texttt{\textbackslash{}n}" in result

    def test_inline_code_escapes_braces(self) -> None:
        """Escape braces in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`{}`")

        # Assert
        assert r"\texttt{\{\}}" in result

    def test_inline_code_escapes_percent(self) -> None:
        """Escape percent in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`100%`")

        # Assert
        assert r"\texttt{100\%}" in result

    def test_inline_code_escapes_hash(self) -> None:
        """Escape hash in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`#comment`")

        # Assert
        assert r"\texttt{\#comment}" in result

    def test_inline_code_escapes_dollar(self) -> None:
        """Escape dollar in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`$var`")

        # Assert
        assert r"\texttt{\$var}" in result

    def test_inline_code_escapes_ampersand(self) -> None:
        """Escape ampersand in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`a & b`")

        # Assert
        assert r"\texttt{a \& b}" in result

    def test_inline_code_escapes_underscore(self) -> None:
        """Escape underscore in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`var_name`")

        # Assert
        assert r"\texttt{var\_name}" in result

    def test_inline_code_escapes_tilde(self) -> None:
        """Escape tilde in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`~home`")

        # Assert
        assert r"\texttt{\textasciitilde{}home}" in result

    def test_inline_code_escapes_caret(self) -> None:
        """Escape caret in inline code."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`a^b`")

        # Assert
        assert r"\texttt{a\textasciicircum{}b}" in result

    def test_formatting_preserved_in_inline_code(self) -> None:
        """Bold markers inside inline code are not converted."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("`**not bold**`")

        # Assert
        assert r"\texttt{**not bold**}" in result
        assert r"\textbf" not in result

    def test_character_normalization_curly_quote(self) -> None:
        """Normalize curly quote to straight apostrophe."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("it\u2019s fine")

        # Assert
        assert "it's fine" in result

    def test_character_normalization_leq(self) -> None:
        """Normalize ≤ to \\leq."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("x ≤ 5")

        # Assert
        assert r"x \leq 5" in result

    def test_character_normalization_geq(self) -> None:
        """Normalize ≥ to \\geq."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("x ≥ 5")

        # Assert
        assert r"x \geq 5" in result

    def test_character_normalization_oe(self) -> None:
        """Normalize œ to oe."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("cœur")

        # Assert
        assert "coeur" in result

    def test_character_normalization_endash(self) -> None:
        """Normalize en-dash to hyphen."""
        # Arrange
        transformer = InlineTransformer(ConversionConfig())

        # Act
        result = transformer.convert("2020–2021")

        # Assert
        assert "2020-2021" in result


class TestLaTeXGenerator:
    """Tests for LaTeXGenerator class."""

    def test_visit_document_empty(self) -> None:
        """Empty document produces empty output."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        doc = Document(children=[])

        # Act
        result = generator.visit_document(doc)

        # Assert
        assert result == ""

    def test_visit_document_with_children(self) -> None:
        """Document with children joins with double newlines."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        doc = Document(children=[
            Section(level=1, title="Title"),
            Paragraph(content="Hello"),
        ])

        # Act
        result = generator.visit_document(doc)

        # Assert
        assert r"\section{Title}" in result
        assert "Hello" in result
        assert "\n\n" in result

    def test_visit_section_level_1(self) -> None:
        """Level 1 heading produces section command."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        section = Section(level=1, title="Introduction")

        # Act
        result = generator.visit_section(section)

        # Assert
        assert result == r"\section{Introduction}"

    def test_visit_section_level_2(self) -> None:
        """Level 2 heading produces subsection command."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        section = Section(level=2, title="Details")

        # Act
        result = generator.visit_section(section)

        # Assert
        assert result == r"\subsection{Details}"

    def test_visit_section_level_3(self) -> None:
        """Level 3 heading produces subsubsection command."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        section = Section(level=3, title="Minor")

        # Act
        result = generator.visit_section(section)

        # Assert
        assert result == r"\subsubsection{Minor}"

    def test_visit_section_level_4(self) -> None:
        """Level 4 heading produces paragraph command."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        section = Section(level=4, title="Point")

        # Act
        result = generator.visit_section(section)

        # Assert
        assert result == r"\paragraph{Point}"

    def test_visit_section_level_5_fallback(self) -> None:
        """Level 5+ heading falls back to paragraph command."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        section = Section(level=5, title="Deep")

        # Act
        result = generator.visit_section(section)

        # Assert
        assert result == r"\paragraph{Deep}"

    def test_visit_paragraph(self) -> None:
        """Paragraph content is processed for inline formatting."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        para = Paragraph(content="Text with **bold**")

        # Act
        result = generator.visit_paragraph(para)

        # Assert
        assert r"\textbf{bold}" in result

    def test_visit_list_unordered(self) -> None:
        """Unordered list produces itemize environment."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        lst = List(ordered=False, items=[
            ListItem(content=[Paragraph(content="Item 1")]),
            ListItem(content=[Paragraph(content="Item 2")]),
        ])

        # Act
        result = generator.visit_list(lst)

        # Assert
        assert r"\begin{itemize}" in result
        assert r"\item Item 1" in result
        assert r"\item Item 2" in result
        assert r"\end{itemize}" in result

    def test_visit_list_ordered(self) -> None:
        """Ordered list produces enumerate environment."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        lst = List(ordered=True, items=[
            ListItem(content=[Paragraph(content="Step 1")]),
        ])

        # Act
        result = generator.visit_list(lst)

        # Assert
        assert r"\begin{enumerate}" in result
        assert r"\item Step 1" in result
        assert r"\end{enumerate}" in result

    def test_visit_list_item_empty(self) -> None:
        """Empty list item produces just \\item."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        item = ListItem(content=[])

        # Act
        result = generator.visit_list_item(item)

        # Assert
        assert result == r"\item"

    def test_visit_list_item_with_text(self) -> None:
        """List item with text paragraph."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        item = ListItem(content=[Paragraph(content="Content")])

        # Act
        result = generator.visit_list_item(item)

        # Assert
        assert result == r"\item Content"

    def test_visit_list_item_with_nested_list(self) -> None:
        """List item with nested list."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        nested = List(ordered=False, items=[
            ListItem(content=[Paragraph(content="Nested")])
        ])
        item = ListItem(content=[nested])

        # Act
        result = generator.visit_list_item(item)

        # Assert
        assert r"\item" in result
        assert r"\begin{itemize}" in result
        assert r"\item Nested" in result

    def test_visit_code_block(self) -> None:
        """Code block produces lstlisting environment."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        code = CodeBlock(language="python", content="print('hi')")

        # Act
        result = generator.visit_code_block(code)

        # Assert
        assert r"\begin{lstlisting}" in result
        assert "print('hi')" in result
        assert r"\end{lstlisting}" in result

    def test_visit_callout_with_title(self) -> None:
        """Callout with title includes title in environment."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        callout = Callout(
            callout_type="note",
            title="Important",
            children=[Paragraph(content="Content")],
        )

        # Act
        result = generator.visit_callout(callout)

        # Assert
        assert r"\begin{notebox}[Important]" in result
        assert "Content" in result
        assert r"\end{notebox}" in result

    def test_visit_callout_without_title(self) -> None:
        """Callout without title uses plain environment."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        callout = Callout(
            callout_type="warning",
            title=None,
            children=[Paragraph(content="Warning text")],
        )

        # Act
        result = generator.visit_callout(callout)

        # Assert
        assert r"\begin{warningbox}" in result
        assert "Warning text" in result
        assert r"\end{warningbox}" in result

    def test_visit_image(self) -> None:
        """Image produces centered includegraphics."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        image = Image(source_path="figures/test", width_px=300)

        # Act
        result = generator.visit_image(image)

        # Assert
        assert r"\begin{center}" in result
        assert r"\includegraphics[width=300\htmlpx]{../figures-pdfs/figures/test.pdf}" in result
        assert r"\end{center}" in result

    def test_custom_inline_transformer(self) -> None:
        """Generator accepts custom inline transformer."""
        # Arrange
        class CustomTransformer(InlineTransformer):
            def convert(self, text: str) -> str:
                return text.upper()

        generator = LaTeXGenerator(inline_transformer=CustomTransformer())
        para = Paragraph(content="hello")

        # Act
        result = generator.visit_paragraph(para)

        # Assert
        assert result == "HELLO"

    def test_visit_table_basic(self) -> None:
        """Table produces tabular environment with header and rows."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        table = Table(
            alignments=["l", "c", "r"],
            header=["Name", "Age", "City"],
            rows=[["Alice", "30", "Paris"], ["Bob", "25", "Lyon"]],
        )

        # Act
        result = generator.visit_table(table)

        # Assert
        assert r"\begin{tabular}{lcr}" in result
        assert r"\hline" in result
        assert "Name & Age & City" in result
        assert "Alice & 30 & Paris" in result
        assert "Bob & 25 & Lyon" in result
        assert r"\end{tabular}" in result

    def test_visit_table_inline_formatting(self) -> None:
        """Table cells support inline formatting."""
        # Arrange
        generator = LaTeXGenerator(ConversionConfig())
        table = Table(
            alignments=["l"],
            header=["Text"],
            rows=[["**bold**"]],
        )

        # Act
        result = generator.visit_table(table)

        # Assert
        assert r"\textbf{bold}" in result
