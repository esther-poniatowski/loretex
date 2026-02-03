"""Unit tests for AST nodes."""

from __future__ import annotations

from loretex.conversion import (
    Callout,
    CodeBlock,
    Document,
    Image,
    List,
    ListItem,
    NodeVisitor,
    Paragraph,
    Section,
    Table,
)


class MockVisitor(NodeVisitor):
    """Mock visitor for testing accept method dispatch."""

    def visit_document(self, node: Document) -> str:
        return "document"

    def visit_section(self, node: Section) -> str:
        return f"section:{node.level}:{node.title}"

    def visit_paragraph(self, node: Paragraph) -> str:
        return f"paragraph:{node.content}"

    def visit_list(self, node: List) -> str:
        return f"list:{'ordered' if node.ordered else 'unordered'}"

    def visit_list_item(self, node: ListItem) -> str:
        return "list_item"

    def visit_code_block(self, node: CodeBlock) -> str:
        return f"code:{node.language or 'none'}"

    def visit_callout(self, node: Callout) -> str:
        return f"callout:{node.callout_type}"

    def visit_image(self, node: Image) -> str:
        return f"image:{node.source_path}"

    def visit_table(self, node: Table) -> str:
        return f"table:{len(node.rows)}rows"


class TestDocumentNode:
    """Tests for Document node."""

    def test_document_accepts_visitor(self) -> None:
        """Document node dispatches to visit_document."""
        # Arrange
        doc = Document(children=[])
        visitor = MockVisitor()

        # Act
        result = doc.accept(visitor)

        # Assert
        assert result == "document"

    def test_document_default_children(self) -> None:
        """Document initializes with empty children list."""
        # Act
        doc = Document()

        # Assert
        assert doc.children == []


class TestSectionNode:
    """Tests for Section node."""

    def test_section_accepts_visitor(self) -> None:
        """Section node dispatches to visit_section."""
        # Arrange
        section = Section(level=2, title="Test Title")
        visitor = MockVisitor()

        # Act
        result = section.accept(visitor)

        # Assert
        assert result == "section:2:Test Title"


class TestParagraphNode:
    """Tests for Paragraph node."""

    def test_paragraph_accepts_visitor(self) -> None:
        """Paragraph node dispatches to visit_paragraph."""
        # Arrange
        para = Paragraph(content="Hello world")
        visitor = MockVisitor()

        # Act
        result = para.accept(visitor)

        # Assert
        assert result == "paragraph:Hello world"


class TestListNode:
    """Tests for List node."""

    def test_ordered_list_accepts_visitor(self) -> None:
        """Ordered list dispatches correctly."""
        # Arrange
        lst = List(ordered=True)
        visitor = MockVisitor()

        # Act
        result = lst.accept(visitor)

        # Assert
        assert result == "list:ordered"

    def test_unordered_list_accepts_visitor(self) -> None:
        """Unordered list dispatches correctly."""
        # Arrange
        lst = List(ordered=False)
        visitor = MockVisitor()

        # Act
        result = lst.accept(visitor)

        # Assert
        assert result == "list:unordered"

    def test_list_default_items(self) -> None:
        """List initializes with empty items list."""
        # Act
        lst = List(ordered=True)

        # Assert
        assert lst.items == []


class TestListItemNode:
    """Tests for ListItem node."""

    def test_list_item_accepts_visitor(self) -> None:
        """ListItem node dispatches to visit_list_item."""
        # Arrange
        item = ListItem()
        visitor = MockVisitor()

        # Act
        result = item.accept(visitor)

        # Assert
        assert result == "list_item"

    def test_list_item_default_content(self) -> None:
        """ListItem initializes with empty content list."""
        # Act
        item = ListItem()

        # Assert
        assert item.content == []


class TestCodeBlockNode:
    """Tests for CodeBlock node."""

    def test_code_block_accepts_visitor(self) -> None:
        """CodeBlock node dispatches to visit_code_block."""
        # Arrange
        code = CodeBlock(language="python", content="print('hi')")
        visitor = MockVisitor()

        # Act
        result = code.accept(visitor)

        # Assert
        assert result == "code:python"

    def test_code_block_without_language(self) -> None:
        """CodeBlock with no language returns 'none'."""
        # Arrange
        code = CodeBlock(language=None, content="text")
        visitor = MockVisitor()

        # Act
        result = code.accept(visitor)

        # Assert
        assert result == "code:none"


class TestCalloutNode:
    """Tests for Callout node."""

    def test_callout_accepts_visitor(self) -> None:
        """Callout node dispatches to visit_callout."""
        # Arrange
        callout = Callout(callout_type="note", title="Title")
        visitor = MockVisitor()

        # Act
        result = callout.accept(visitor)

        # Assert
        assert result == "callout:note"

    def test_callout_default_children(self) -> None:
        """Callout initializes with empty children list."""
        # Act
        callout = Callout(callout_type="warning", title=None)

        # Assert
        assert callout.children == []


class TestImageNode:
    """Tests for Image node."""

    def test_image_accepts_visitor(self) -> None:
        """Image node dispatches to visit_image."""
        # Arrange
        image = Image(source_path="figures/test", width_px=200)
        visitor = MockVisitor()

        # Act
        result = image.accept(visitor)

        # Assert
        assert result == "image:figures/test"


class TestTableNode:
    """Tests for Table node."""

    def test_table_accepts_visitor(self) -> None:
        """Table node dispatches to visit_table."""
        # Arrange
        table = Table(
            alignments=["l", "c"],
            header=["A", "B"],
            rows=[["1", "2"], ["3", "4"]],
        )
        visitor = MockVisitor()

        # Act
        result = table.accept(visitor)

        # Assert
        assert result == "table:2rows"
