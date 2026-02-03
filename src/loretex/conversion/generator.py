"""LaTeX generation from AST."""

from __future__ import annotations

import re

from .config import ConversionConfig
from .inline import InlineTransformer
from .labels import slugify
from .nodes import (
    Callout,
    CodeBlock,
    Document,
    HorizontalRule,
    Image,
    List,
    ListItem,
    MathBlock,
    NodeVisitor,
    Paragraph,
    Section,
    Table,
)


class LaTeXGenerator(NodeVisitor):
    """Generate LaTeX output from AST nodes."""

    def __init__(
        self,
        config: ConversionConfig | None = None,
        inline_transformer: InlineTransformer | None = None,
    ) -> None:
        self._config = config or ConversionConfig()
        self._inline = inline_transformer or InlineTransformer(self._config)

    def visit_document(self, node: Document) -> str:
        """Generate LaTeX for the full document."""
        blocks = [child.accept(self) for child in node.children if child]
        blocks = [block for block in blocks if block.strip() != ""]
        return "\n\n".join(blocks)

    def visit_section(self, node: Section) -> str:
        """Convert heading to LaTeX sectioning command."""
        command = self._config.headings.resolve_command(node.level)
        title = self._inline.convert(node.title)
        section = f"\\{command}{{{title}}}"
        if self._config.labels.auto_label_headings:
            label = self._make_label(node.title)
            label_cmd = self._config.labels.label_template.format(label=label)
            return f"{section}\n{label_cmd}"
        return section

    def visit_paragraph(self, node: Paragraph) -> str:
        """Convert paragraph to LaTeX with inline formatting."""
        return self._inline.convert(node.content)

    def visit_list(self, node: List) -> str:
        """Convert list to itemize or enumerate environment."""
        env = (
            self._config.lists.ordered_environment
            if node.ordered
            else self._config.lists.unordered_environment
        )
        items = [item.accept(self) for item in node.items]
        body = "\n".join(items)
        return f"\\begin{{{env}}}\n{body}\n\\end{{{env}}}"

    def visit_list_item(self, node: ListItem) -> str:
        """Convert list item to LaTeX \\item."""
        segments: list[tuple[str, str]] = []
        text_parts: list[str] = []

        for child in node.content:
            if isinstance(child, Paragraph):
                text_parts.append(self._inline.convert(child.content))
                continue
            if text_parts:
                segments.append(("text", "\n".join(text_parts).strip()))
                text_parts = []
            segments.append(("block", child.accept(self)))

        if text_parts:
            segments.append(("text", "\n".join(text_parts).strip()))

        if not segments:
            return "\\item"

        lines: list[str] = []
        first_kind, first_value = segments[0]
        if first_kind == "text":
            if first_value:
                lines.append(f"\\item {first_value}")
            else:
                lines.append("\\item")
        else:
            lines.append("\\item")
            lines.append(first_value)

        for _kind, value in segments[1:]:
            lines.append(value)

        return "\n".join(lines)

    def visit_code_block(self, node: CodeBlock) -> str:
        """Convert fenced code block to configured environment."""
        begin = self._config.code_blocks.begin(node.language)
        end = self._config.code_blocks.end()
        return f"{begin}\n{node.content}\n{end}"

    def visit_horizontal_rule(self, node: HorizontalRule) -> str:
        """Convert horizontal rule to LaTeX rule."""
        return self._config.horizontal_rule.render()

    def visit_math_block(self, node: MathBlock) -> str:
        """Convert block math to configured LaTeX."""
        return self._config.math.format_block(node.content)

    def visit_callout(self, node: Callout) -> str:
        """Convert callout to custom LaTeX environment."""
        body_blocks = [child.accept(self) for child in node.children]
        body = "\n\n".join(block for block in body_blocks if block.strip() != "")
        environment = self._config.callouts.resolve_environment(node.callout_type)
        title = self._inline.convert(node.title) if node.title else None
        if title and self._config.callouts.title_template is not None:
            title_suffix = self._config.callouts.title_template.format(title=title)
            begin = f"\\begin{{{environment}}}{title_suffix}"
        else:
            begin = f"\\begin{{{environment}}}"
        return f"{begin}\n{body}\n\\end{{{environment}}}"

    def visit_image(self, node: Image) -> str:
        """Convert image node to LaTeX includegraphics."""
        return self._config.images.format_block(node.source_path, node.width_px)

    def visit_table(self, node: Table) -> str:
        """Convert table node to LaTeX tabular environment."""
        col_spec = "".join(node.alignments)
        header_cells = " & ".join(self._inline.convert(c) for c in node.header)
        body_lines = []
        for row in node.rows:
            rendered_cells = []
            idx = 0
            while idx < len(row):
                cell = row[idx]
                content, col_span, row_span = _parse_cell_span(cell)
                latex = self._inline.convert(content)
                if row_span > 1:
                    command = self._config.tables.multirow_command
                    if not command.startswith("\\"):
                        command = f"\\{command}"
                    latex = f"{command}{{{row_span}}}{{*}}{{{latex}}}"
                if col_span > 1:
                    align = self._config.tables.multicolumn_align
                    latex = f"\\multicolumn{{{col_span}}}{{{align}}}{{{latex}}}"
                    idx += col_span
                else:
                    idx += 1
                rendered_cells.append(latex)
            cells = " & ".join(rendered_cells)
            body_lines.append(f"{cells} \\\\")

        if self._config.tables.include_hlines:
            return (
                f"\\begin{{{self._config.tables.environment}}}{{{col_spec}}}\n"
                f"\\hline\n"
                f"{header_cells} \\\\\n"
                f"\\hline\n"
                + "\n".join(body_lines)
                + "\n"
                "\\hline\n"
                f"\\end{{{self._config.tables.environment}}}"
            )

        return (
            f"\\begin{{{self._config.tables.environment}}}{{{col_spec}}}\n"
            f"{header_cells} \\\\\n"
            + "\n".join(body_lines)
            + "\n"
            f"\\end{{{self._config.tables.environment}}}"
        )

    def _make_label(self, title: str) -> str:
        normalized = slugify(title, self._config.labels.label_separator)
        prefix = self._config.labels.label_prefix
        if prefix:
            return f"{prefix}{self._config.labels.label_separator}{normalized}"
        return normalized


def _parse_cell_span(cell: str) -> tuple[str, int, int]:
    match = re.search(r"\{([^{}]+)\}\s*$", cell)
    col_span = 1
    row_span = 1
    if match:
        props = match.group(1)
        for entry in props.split(","):
            entry = entry.strip()
            if "=" not in entry:
                continue
            key, value = [part.strip() for part in entry.split("=", 1)]
            if key == "col":
                col_span = int(value)
            if key == "row":
                row_span = int(value)
        cell = cell[:match.start()].rstrip()
    return cell, col_span, row_span
