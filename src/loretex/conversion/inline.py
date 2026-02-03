"""Inline Markdown-to-LaTeX transformations."""

from __future__ import annotations

import re

from .config import ConversionConfig
from .labels import slugify


class InlineTransformer:
    """Apply inline Markdown transformations to LaTeX."""

    _inline_code_pattern = re.compile(r"`([^`\n]+)`")
    _inline_math_dollar_pattern = re.compile(r"(?<!\\)\$(?!\$)([^$\n]+?)\$(?!\$)")
    _inline_math_paren_pattern = re.compile(r"\\\((.+?)\\\)")
    _footnote_ref_pattern = re.compile(r"\[\^([^\]]+)\]")
    _wiki_link_pattern = re.compile(r"\[\[([^\]]+)\]\]")
    _citation_pattern = re.compile(r"\[@([^\]]+)\]")
    _link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    _autolink_pattern = re.compile(r"<(https?://[^>]+)>")
    _bold_pattern = re.compile(r"\*\*([^*\n]+)\*\*")
    _italic_star_pattern = re.compile(
        r"(?<![A-Za-z0-9*])\*([^*\n]+)\*(?![A-Za-z0-9*])"
    )
    _italic_underscore_pattern = re.compile(
        r"(?<![A-Za-z0-9_])_([^_\n]+)_(?![A-Za-z0-9_])"
    )
    _image_pattern = re.compile(r"<img src=\"([^\"]+)\.svg\" width=\"(\d+)\"[^>]*>")

    def __init__(
        self,
        config: ConversionConfig | None = None,
        footnotes_map: dict[str, str] | None = None,
    ) -> None:
        self._config = config or ConversionConfig()
        self._footnotes_map = footnotes_map or {}

    def convert(self, text: str) -> str:
        """Convert inline Markdown syntax to LaTeX.

        Parameters
        ----------
        text : str
            Raw text containing inline Markdown.

        Returns
        -------
        str
            Text with inline Markdown converted to LaTeX.
        """
        fragments: list[str] = []
        last_idx = 0
        for match in self._inline_code_pattern.finditer(text):
            fragments.append(self._convert_non_code(text[last_idx:match.start()]))
            fragments.append(self._format_inline_code(match.group(1)))
            last_idx = match.end()
        fragments.append(self._convert_non_code(text[last_idx:]))
        return "".join(fragments)

    def _convert_non_code(self, text: str) -> str:
        """Convert inline formatting for non-code segments."""
        text, math_spans = self._extract_inline_math(text)
        line_break = self._ensure_command(self._config.inline.line_break_command)
        text = re.sub(r"<br\s*/?>", lambda _match: f"{line_break} ", text)
        text = self._apply_custom_markers(text)
        text = self._image_pattern.sub(
            lambda match: self._config.images.format_block(
                match.group(1), int(match.group(2))
            ),
            text,
        )
        text = self._citation_pattern.sub(
            lambda match: self._format_citation(match.group(1)),
            text,
        )
        text = self._footnote_ref_pattern.sub(
            lambda match: self._format_footnote_ref(match.group(1)),
            text,
        )
        text = self._wiki_link_pattern.sub(
            lambda match: self._format_wiki_link(match.group(1)),
            text,
        )
        text = self._link_pattern.sub(
            lambda match: self._format_link(match.group(1), match.group(2)),
            text,
        )
        text = self._autolink_pattern.sub(
            lambda match: self._format_autolink(match.group(1)),
            text,
        )
        bold_command = self._ensure_command(self._config.inline.bold_command)
        italic_command = self._ensure_command(self._config.inline.italic_command)
        text = self._bold_pattern.sub(
            lambda match: f"{bold_command}{{{match.group(1)}}}",
            text,
        )
        text = self._italic_star_pattern.sub(
            lambda match: f"{italic_command}{{{match.group(1)}}}",
            text,
        )
        text = self._italic_underscore_pattern.sub(
            lambda match: f"{italic_command}{{{match.group(1)}}}",
            text,
        )
        text = self._normalize_characters(text)
        return self._restore_inline_math(text, math_spans)

    def _format_inline_code(self, code: str) -> str:
        """Format inline code as LaTeX texttt with escaping."""
        command = self._ensure_command(self._config.inline.code_command)
        escaped = self._escape_texttt(code)
        return f"{command}{{{escaped}}}"

    def _escape_texttt(self, code: str) -> str:
        """Escape LaTeX-sensitive characters inside inline code."""
        return "".join(self._config.inline.texttt_escape_map.get(char, char) for char in code)

    def _normalize_characters(self, text: str) -> str:
        """Normalize typographic characters for LaTeX."""
        normalized = text
        for source, target in self._config.inline.character_normalization:
            normalized = normalized.replace(source, target)
        return normalized

    def _extract_inline_math(self, text: str) -> tuple[str, dict[str, str]]:
        placeholders: dict[str, str] = {}
        counter = 0

        def _replace(pattern: re.Pattern[str], source: str) -> str:
            nonlocal counter

            def repl(match: re.Match[str]) -> str:
                nonlocal counter
                content = match.group(1)
                token = f"__LORETEX_MATH_{counter}__"
                placeholders[token] = self._format_inline_math(content)
                counter += 1
                return token

            return pattern.sub(repl, source)

        text = _replace(self._inline_math_paren_pattern, text)
        text = _replace(self._inline_math_dollar_pattern, text)
        return text, placeholders

    def _restore_inline_math(self, text: str, placeholders: dict[str, str]) -> str:
        if not placeholders:
            return text
        restored = text
        for token, value in placeholders.items():
            restored = restored.replace(token, value)
        return restored

    def _format_inline_math(self, content: str) -> str:
        template = self._config.inline.inline_math_template
        if "{content}" in template:
            return template.format(content=content)
        if "{text}" in template:
            return template.format(text=content)
        return f"{template}{content}"

    def _apply_custom_markers(self, text: str) -> str:
        if not self._config.inline.custom_markers:
            return text
        markers = sorted(
            self._config.inline.custom_markers.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )
        rendered = text
        for marker, template in markers:
            if not marker:
                continue
            pattern = re.compile(rf"{re.escape(marker)}([^\n]+?){re.escape(marker)}")
            rendered = pattern.sub(
                lambda match: self._format_custom_marker(template, match.group(1)),
                rendered,
            )
        return rendered

    def _format_custom_marker(self, template: str, text: str) -> str:
        if "{text}" in template or "{content}" in template:
            return template.format(text=text, content=text)
        command = self._ensure_command(template)
        return f"{command}{{{text}}}"

    def _format_link(self, text: str, url: str) -> str:
        if url.startswith("#"):
            label = slugify(url.lstrip("#"), self._config.labels.label_separator)
            prefix = self._config.labels.label_prefix
            if prefix:
                label = f"{prefix}{self._config.labels.label_separator}{label}"
            return self._config.links.format_internal(label)
        link_text = self._convert_link_text(text)
        if text.strip() == url.strip():
            return self._config.links.format_url_only(url)
        return self._config.links.format_external(url, link_text)

    def _format_autolink(self, url: str) -> str:
        return self._config.links.format_autolink(url)

    def _convert_link_text(self, text: str) -> str:
        bold_command = self._ensure_command(self._config.inline.bold_command)
        italic_command = self._ensure_command(self._config.inline.italic_command)
        text = self._bold_pattern.sub(
            lambda match: f"{bold_command}{{{match.group(1)}}}",
            text,
        )
        text = self._italic_star_pattern.sub(
            lambda match: f"{italic_command}{{{match.group(1)}}}",
            text,
        )
        text = self._italic_underscore_pattern.sub(
            lambda match: f"{italic_command}{{{match.group(1)}}}",
            text,
        )
        return self._normalize_characters(text)

    def _format_citation(self, raw: str) -> str:
        entries: list[tuple[str, str | None]] = []
        for part in raw.split(";"):
            part = part.strip()
            if not part:
                continue
            if "," in part:
                key_part, locator = part.split(",", 1)
                key = key_part.strip().lstrip("@")
                entries.append((key, locator.strip()))
            else:
                key = part.strip().lstrip("@")
                entries.append((key, None))

        if not entries:
            return raw

        if all(locator is None for _key, locator in entries):
            keys = [key for key, _ in entries]
            return self._config.citations.format_citation(keys)

        rendered = []
        for key, locator_value in entries:
            if locator_value:
                rendered.append(
                    self._config.citations.format_citation_with_locator(
                        [key], locator_value
                    )
                )
            else:
                rendered.append(self._config.citations.format_citation([key]))
        return self._config.citations.multi_cite_separator.join(rendered)

    def _format_footnote_ref(self, key: str) -> str:
        footnote = self._footnotes_map.get(key)
        if footnote is None:
            return f"[^{key}]"
        return self._config.footnotes.format_footnote(footnote)

    def _format_wiki_link(self, raw: str) -> str:
        if "|" in raw:
            target, alias = [part.strip() for part in raw.split("|", 1)]
            label = self._make_wiki_label(target)
            return self._config.wiki_links.format_alias(label, alias)
        label = self._make_wiki_label(raw.strip())
        return self._config.wiki_links.format_link(label)

    def _make_wiki_label(self, text: str) -> str:
        return slugify(text, self._config.wiki_links.label_separator)

    @staticmethod
    def _ensure_command(command: str) -> str:
        command = command.strip()
        if command.startswith("\\"):
            return command
        return f"\\{command}"
