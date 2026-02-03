"""AST node definitions for Markdown-to-LaTeX conversion."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

# === AST Node Definitions ======================================


class Node(ABC):
    """Abstract base for all AST nodes.

    All AST nodes must implement the visitor pattern via the accept method.
    """

    @abstractmethod
    def accept(self, visitor: NodeVisitor) -> str:
        """Accept a visitor for transformation.

        Parameters
        ----------
        visitor : NodeVisitor
            Visitor implementing transformation logic.

        Returns
        -------
        str
            Transformed output (typically LaTeX).
        """
        ...


@dataclass
class Document(Node):
    """Root node containing document structure."""

    children: list[Node] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_document(self)


@dataclass
class Section(Node):
    """Section node (h1, h2, h3 → section, subsection, subsubsection)."""

    level: int
    title: str

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_section(self)


@dataclass
class Paragraph(Node):
    """Paragraph containing plain text."""

    content: str

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_paragraph(self)


@dataclass
class List(Node):
    """List node (ordered or unordered)."""

    ordered: bool
    items: list[ListItem] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_list(self)


@dataclass
class ListItem(Node):
    """Individual list item."""

    content: list[Node] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_list_item(self)


@dataclass
class CodeBlock(Node):
    """Fenced code block."""

    language: str | None
    content: str

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_code_block(self)


@dataclass
class HorizontalRule(Node):
    """Horizontal rule block."""

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_horizontal_rule(self)


@dataclass
class MathBlock(Node):
    """Block math expression."""

    content: str

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_math_block(self)


@dataclass
class Callout(Node):
    """Callout block with an optional title."""

    callout_type: str
    title: str | None
    children: list[Node] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_callout(self)


@dataclass
class Image(Node):
    """HTML image tag converted to LaTeX includegraphics."""

    source_path: str
    width_px: int

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_image(self)


@dataclass
class Table(Node):
    """Table with header and body rows."""

    alignments: list[str]
    header: list[str]
    rows: list[list[str]]

    def accept(self, visitor: NodeVisitor) -> str:
        return visitor.visit_table(self)


# ==== Abstract Visitor Definition ==============================


class NodeVisitor(ABC):
    """Abstract visitor for traversing and transforming AST.

    Implementations should provide concrete visit methods for each node type.
    """

    @abstractmethod
    def visit_document(self, node: Document) -> str:
        """Visit document node."""
        ...

    @abstractmethod
    def visit_section(self, node: Section) -> str:
        """Visit section node."""
        ...

    @abstractmethod
    def visit_paragraph(self, node: Paragraph) -> str:
        """Visit paragraph node."""
        ...

    @abstractmethod
    def visit_list(self, node: List) -> str:
        """Visit list node."""
        ...

    @abstractmethod
    def visit_list_item(self, node: ListItem) -> str:
        """Visit list item node."""
        ...

    @abstractmethod
    def visit_code_block(self, node: CodeBlock) -> str:
        """Visit code block node."""
        ...

    @abstractmethod
    def visit_horizontal_rule(self, node: HorizontalRule) -> str:
        """Visit horizontal rule node."""
        ...

    @abstractmethod
    def visit_math_block(self, node: MathBlock) -> str:
        """Visit math block node."""
        ...

    @abstractmethod
    def visit_callout(self, node: Callout) -> str:
        """Visit callout node."""
        ...

    @abstractmethod
    def visit_image(self, node: Image) -> str:
        """Visit image node."""
        ...

    @abstractmethod
    def visit_table(self, node: Table) -> str:
        """Visit table node."""
        ...
