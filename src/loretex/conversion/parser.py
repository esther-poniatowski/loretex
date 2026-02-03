"""Markdown parser producing an AST for conversion."""

from __future__ import annotations

import re

from .constants import TAB_WIDTH
from .exceptions import (
    InvalidCalloutError,
    InvalidCodeFenceError,
    InvalidHeadingError,
    InvalidImageError,
    InvalidListError,
)
from .nodes import (
    Callout,
    CodeBlock,
    Document,
    HorizontalRule,
    Image,
    List,
    ListItem,
    MathBlock,
    Node,
    Paragraph,
    Section,
    Table,
)


class MarkdownParser:
    """Parse Markdown text into an AST."""

    _code_fence_pattern = re.compile(
        r"^(?P<indent>[ \t]*)```(?P<lang>[A-Za-z0-9_-]+)?\s*$"
    )
    _code_fence_end_pattern = re.compile(r"^[ \t]*```\s*$")
    _callout_header_pattern = re.compile(
        r"^(?P<indent>[ \t]*)> \[!(?P<type>[A-Za-z]+)\](?:\s+(?P<title>.*))?$"
    )
    _heading_pattern = re.compile(r"^(?P<marks>#{1,6})[ \t]+(?P<title>.+)$")
    _list_item_pattern = re.compile(
        r"^(?P<indent>[ \t]*)(?P<marker>(?:[-*+])|(?:\d+\.))\s+(?P<content>.*)$"
    )
    _image_line_pattern = re.compile(
        r"^<img src=\"(?P<path>[^\"]+)\.svg\" width=\"(?P<width>\d+)\"[^>]*>$"
    )
    _table_row_pattern = re.compile(r"^\|(.+)\|$")
    _table_separator_pattern = re.compile(r"^\|[\s:|-]+\|$")
    _horizontal_rule_pattern = re.compile(r"^[ \t]*([-*_])(?:[ \t]*\1){2,}[ \t]*$")

    def parse(self, source: str) -> Document:
        """Parse Markdown source into AST.

        Parameters
        ----------
        source : str
            Raw Markdown source.

        Returns
        -------
        Document
            Parsed document node.
        """
        lines = source.splitlines()
        children = self._parse_lines(lines)
        return Document(children=children)

    def _parse_lines(self, lines: list[str]) -> list[Node]:
        """Parse a list of lines into AST nodes."""
        nodes: list[Node] = []
        i = 0

        while i < len(lines):
            raw_line = lines[i]
            normalized_line = self._normalized_line(raw_line)

            if self._is_blank(normalized_line):
                i += 1
                continue

            if self._is_callout_header(raw_line):
                callout, consumed = self._parse_callout(lines, i)
                nodes.append(callout)
                i += consumed
                continue

            if self._is_code_fence_start(normalized_line):
                code_block, consumed = self._parse_code_block(lines, i)
                nodes.append(code_block)
                i += consumed
                continue

            if self._is_math_block_start(normalized_line):
                math_block, consumed = self._parse_math_block(lines, i)
                nodes.append(math_block)
                i += consumed
                continue

            if self._is_heading(normalized_line):
                nodes.append(self._parse_heading(normalized_line, i))
                i += 1
                continue

            if self._is_list_item(normalized_line):
                list_node, consumed = self._parse_list(lines, i)
                nodes.append(list_node)
                i += consumed
                continue

            if self._is_image_line(normalized_line):
                nodes.append(self._parse_image_line(normalized_line, i))
                i += 1
                continue

            if self._is_table_start(lines, i):
                table, consumed = self._parse_table(lines, i)
                nodes.append(table)
                i += consumed
                continue

            if self._is_horizontal_rule(normalized_line):
                nodes.append(HorizontalRule())
                i += 1
                continue

            paragraph_lines = [normalized_line]
            i += 1
            while i < len(lines):
                raw_line = lines[i]
                normalized_line = self._normalized_line(raw_line)
                if self._is_blank(normalized_line):
                    break
                if self._is_callout_header(raw_line):
                    break
                if self._is_code_fence_start(normalized_line):
                    break
                if self._is_math_block_start(normalized_line):
                    break
                if self._is_heading(normalized_line):
                    break
                if self._is_list_item(normalized_line):
                    break
                if self._is_image_line(normalized_line):
                    break
                if self._is_table_start(lines, i):
                    break
                if self._is_horizontal_rule(normalized_line):
                    break
                paragraph_lines.append(normalized_line)
                i += 1

            nodes.append(Paragraph(content="\n".join(paragraph_lines)))

        return nodes

    def _parse_code_block(self, lines: list[str], start_idx: int) -> tuple[CodeBlock, int]:
        """Parse fenced code block."""
        normalized_start = self._normalized_line(lines[start_idx])
        match = self._code_fence_pattern.match(normalized_start)
        if not match:
            raise InvalidCodeFenceError(start_idx + 1, lines[start_idx])
        indent = match.group("indent") or ""
        language = match.group("lang")

        content_lines: list[str] = []
        i = start_idx + 1
        while i < len(lines):
            normalized_line = self._normalized_line(lines[i])
            if self._code_fence_end_pattern.match(normalized_line):
                i += 1
                break
            if indent and normalized_line.startswith(indent):
                content_lines.append(normalized_line[len(indent):])
            else:
                content_lines.append(normalized_line)
            i += 1

        return CodeBlock(language=language, content="\n".join(content_lines)), i - start_idx

    def _parse_math_block(self, lines: list[str], start_idx: int) -> tuple[MathBlock, int]:
        """Parse block math delimited by $$ or \\[."""
        start_line = self._normalized_line(lines[start_idx]).strip()
        if start_line in {"$$", "\\["}:
            end_delimiter = "$$" if start_line == "$$" else "\\]"
            content_lines: list[str] = []
            i = start_idx + 1
            while i < len(lines):
                line = self._normalized_line(lines[i]).strip()
                if line == end_delimiter:
                    i += 1
                    break
                content_lines.append(self._normalized_line(lines[i]))
                i += 1
            return MathBlock(content="\n".join(content_lines)), i - start_idx

        if start_line.startswith("$$") and start_line.endswith("$$") and len(start_line) > 4:
            content = start_line[2:-2].strip()
            return MathBlock(content=content), 1

        if start_line.startswith("\\[") and start_line.endswith("\\]") and len(start_line) > 4:
            content = start_line[2:-2].strip()
            return MathBlock(content=content), 1

        return MathBlock(content=start_line), 1

    def _parse_callout(self, lines: list[str], start_idx: int) -> tuple[Callout, int]:
        """Parse callout block."""
        header_line = lines[start_idx]
        match = self._callout_header_pattern.match(header_line)
        if not match:
            raise InvalidCalloutError(start_idx + 1, header_line)
        callout_type = match.group("type")
        title = match.group("title") if match.group("title") else None

        content_lines: list[str] = []
        i = start_idx + 1
        while i < len(lines):
            line = lines[i]
            if self._is_callout_header(line):
                break
            if not self._is_blockquote_line(line):
                break
            content_lines.append(self._strip_callout_prefix(line))
            i += 1

        children = self._parse_lines(content_lines)
        return Callout(callout_type=callout_type, title=title, children=children), i - start_idx

    def _parse_heading(self, line: str, line_idx: int) -> Section:
        """Parse Markdown heading line."""
        match = self._heading_pattern.match(line)
        if not match:
            raise InvalidHeadingError(line_idx + 1, line)
        level = len(match.group("marks"))
        title = match.group("title").strip()
        return Section(level=level, title=title)

    def _parse_list(self, lines: list[str], start_idx: int) -> tuple[List, int]:
        """Parse list starting at start_idx."""
        start_line = self._normalized_line(lines[start_idx])
        match = self._list_item_pattern.match(start_line)
        if not match:
            raise InvalidListError(start_idx + 1, start_line)

        base_indent = self._indent_width(match.group("indent"))
        ordered = self._is_ordered_marker(match.group("marker"))
        list_node = List(ordered=ordered)

        i = start_idx
        while i < len(lines):
            normalized_line = self._normalized_line(lines[i])
            if self._is_blank(normalized_line):
                i += 1
                continue
            item_match = self._list_item_pattern.match(normalized_line)
            if not item_match:
                break
            indent = self._indent_width(item_match.group("indent"))
            if indent != base_indent:
                break
            if self._is_ordered_marker(item_match.group("marker")) != ordered:
                break
            item, consumed = self._parse_list_item(lines, i, item_match)
            list_node.items.append(item)
            i += consumed

        return list_node, i - start_idx

    def _parse_list_item(
        self, lines: list[str], start_idx: int, match: re.Match[str]
    ) -> tuple[ListItem, int]:
        """Parse a list item and its continuation lines."""
        base_indent = self._indent_width(match.group("indent"))
        content_indent = match.start("content")
        item_lines: list[str] = []
        first_content = match.group("content").strip()
        if first_content:
            item_lines.append(first_content)

        i = start_idx + 1
        while i < len(lines):
            normalized_line = self._normalized_line(lines[i])
            if self._is_blank(normalized_line):
                item_lines.append("")
                i += 1
                continue
            next_match = self._list_item_pattern.match(normalized_line)
            if next_match:
                next_indent = self._indent_width(next_match.group("indent"))
                if next_indent <= base_indent:
                    break
            current_indent = self._indent_width(normalized_line)
            if current_indent <= base_indent:
                break
            item_lines.append(self._dedent_line(normalized_line, content_indent))
            i += 1

        children = self._parse_lines(item_lines) if item_lines else []
        return ListItem(content=children), i - start_idx

    def _parse_image_line(self, line: str, line_idx: int) -> Image:
        """Parse HTML image tag line."""
        match = self._image_line_pattern.match(line.strip())
        if not match:
            raise InvalidImageError(line_idx + 1, line)
        return Image(
            source_path=match.group("path"),
            width_px=int(match.group("width")),
        )

    def _is_table_start(self, lines: list[str], idx: int) -> bool:
        """Check if a table starts at the given index."""
        if idx + 1 >= len(lines):
            return False
        header_line = self._normalized_line(lines[idx]).strip()
        separator_line = self._normalized_line(lines[idx + 1]).strip()
        return (
            self._table_row_pattern.match(header_line) is not None
            and self._table_separator_pattern.match(separator_line) is not None
        )

    def _parse_table(self, lines: list[str], start_idx: int) -> tuple[Table, int]:
        """Parse a Markdown table starting at start_idx."""
        header_line = self._normalized_line(lines[start_idx]).strip()
        separator_line = self._normalized_line(lines[start_idx + 1]).strip()

        header = self._parse_table_row(header_line)
        alignments = self._parse_alignments(separator_line)

        rows: list[list[str]] = []
        i = start_idx + 2
        while i < len(lines):
            normalized_line = self._normalized_line(lines[i]).strip()
            if not self._table_row_pattern.match(normalized_line):
                break
            rows.append(self._parse_table_row(normalized_line))
            i += 1

        return Table(alignments=alignments, header=header, rows=rows), i - start_idx

    def _parse_table_row(self, line: str) -> list[str]:
        """Parse a table row into cell contents."""
        content = line.strip("|")
        return [cell.strip() for cell in content.split("|")]

    def _parse_alignments(self, separator_line: str) -> list[str]:
        """Parse alignment indicators from separator row."""
        content = separator_line.strip("|")
        cells = [cell.strip() for cell in content.split("|")]
        alignments: list[str] = []
        for cell in cells:
            if cell.startswith(":") and cell.endswith(":"):
                alignments.append("c")
            elif cell.endswith(":"):
                alignments.append("r")
            else:
                alignments.append("l")
        return alignments

    def _normalized_line(self, line: str) -> str:
        """Apply blockquote stripping when applicable."""
        if self._is_callout_header(line):
            return line
        return self._strip_leading_chevron(line)

    def _strip_leading_chevron(self, line: str) -> str:
        """Strip leading blockquote chevron while preserving indentation."""
        match = re.match(r"^(?P<indent>[ \t]*)> ?(?P<rest>.*)$", line)
        if match:
            return f"{match.group('indent')}{match.group('rest')}"
        return line

    def _strip_callout_prefix(self, line: str) -> str:
        """Strip callout prefix and leading chevrons."""
        match = re.match(r"^[ \t]*> ?(.*)$", line)
        return match.group(1) if match else line

    def _is_blank(self, line: str) -> bool:
        """Check if line is blank."""
        return line.strip() == ""

    def _is_code_fence_start(self, line: str) -> bool:
        """Check if line starts a fenced code block."""
        return self._code_fence_pattern.match(line) is not None

    def _is_callout_header(self, line: str) -> bool:
        """Check if line is a callout header."""
        return self._callout_header_pattern.match(line) is not None

    def _is_blockquote_line(self, line: str) -> bool:
        """Check if line starts with a blockquote chevron."""
        return re.match(r"^[ \t]*>", line) is not None

    def _is_heading(self, line: str) -> bool:
        """Check if line is a heading."""
        return self._heading_pattern.match(line) is not None

    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item."""
        return self._list_item_pattern.match(line) is not None

    def _is_image_line(self, line: str) -> bool:
        """Check if line is an image tag on its own line."""
        return self._image_line_pattern.match(line.strip()) is not None

    def _is_math_block_start(self, line: str) -> bool:
        """Check if line starts a block math section."""
        stripped = line.strip()
        if stripped in {"$$", "\\["}:
            return True
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            return True
        if stripped.startswith("\\[") and stripped.endswith("\\]") and len(stripped) > 4:
            return True
        return False

    def _is_horizontal_rule(self, line: str) -> bool:
        """Check if line is a horizontal rule."""
        return self._horizontal_rule_pattern.match(line) is not None

    def _is_ordered_marker(self, marker: str) -> bool:
        """Check if list marker is ordered."""
        return marker.endswith(".")

    def _indent_width(self, line: str) -> int:
        """Compute leading indentation width accounting for tabs."""
        width = 0
        for char in line:
            if char == " ":
                width += 1
            elif char == "\t":
                width += TAB_WIDTH
            else:
                break
        return width

    def _dedent_line(self, line: str, indent: int) -> str:
        """Remove leading indentation from a line."""
        if len(line) <= indent:
            return line.lstrip()
        return line[indent:]
