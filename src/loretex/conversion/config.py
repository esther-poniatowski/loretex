"""Configuration models for Markdown-to-LaTeX conversion."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping
import warnings

from .constants import (
    DEFAULT_CALLOUT_ENV_TEMPLATE,
    DEFAULT_CHARACTER_NORMALIZATION,
    DEFAULT_FIGURES_PDF_PATH,
    DEFAULT_IMAGE_BLOCK_TEMPLATE,
    DEFAULT_SECTION_COMMANDS,
    DEFAULT_TEXTTT_ESCAPE_MAP,
)


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively merge override into base."""
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_link_template(template: str) -> str:
    if "{url}" in template and "{{{url}}}" not in template:
        template = template.replace("{url}", "{{{url}}}")
    if "{text}" in template and "{{{text}}}" not in template:
        template = template.replace("{text}", "{{{text}}}")
    if "{label}" in template and "{{{label}}}" not in template:
        template = template.replace("{label}", "{{{label}}}")
    if "{keys}" in template and "{{{keys}}}" not in template:
        template = template.replace("{keys}", "{{{keys}}}")
    return template


@dataclass(frozen=True)
class HeadingConfig:
    """Heading conversion rules."""

    anchor_level: int = 1
    commands: Mapping[int, str] = field(default_factory=lambda: dict(DEFAULT_SECTION_COMMANDS))
    fallback_command: str = "paragraph"

    def resolve_command(self, markdown_level: int) -> str:
        """Resolve Markdown heading level to a LaTeX command."""
        relative_level = markdown_level - self.anchor_level + 1
        if relative_level < 1:
            relative_level = 1
        return self.commands.get(relative_level, self.fallback_command)


@dataclass(frozen=True)
class InlineConfig:
    """Inline formatting rules."""

    bold_command: str = "textbf"
    italic_command: str = "textit"
    code_command: str = "texttt"
    line_break_command: str = "newline"
    texttt_escape_map: Mapping[str, str] = field(
        default_factory=lambda: dict(DEFAULT_TEXTTT_ESCAPE_MAP)
    )
    character_normalization: tuple[tuple[str, str], ...] = DEFAULT_CHARACTER_NORMALIZATION


@dataclass(frozen=True)
class LinkConfig:
    """Markdown link conversion rules."""

    external_link_template: str = r"\href{{{url}}}{{{text}}}"
    url_only_template: str = r"\url{{{url}}}"
    autolink_template: str = r"\url{{{url}}}"
    internal_ref_template: str = r"\ref{{{label}}}"

    def format_external(self, url: str, text: str) -> str:
        template = _normalize_link_template(self.external_link_template)
        return template.format(url=url, text=text)

    def format_url_only(self, url: str) -> str:
        template = _normalize_link_template(self.url_only_template)
        return template.format(url=url)

    def format_autolink(self, url: str) -> str:
        template = _normalize_link_template(self.autolink_template)
        return template.format(url=url)

    def format_internal(self, label: str) -> str:
        template = _normalize_link_template(self.internal_ref_template)
        return template.format(label=label)


@dataclass(frozen=True)
class CitationConfig:
    """Markdown citation conversion rules."""

    cite_template: str = r"\cite{{{keys}}}"
    cite_with_locator_template: str = r"\cite[{locator}]{{{keys}}}"
    separator: str = ","
    multi_cite_separator: str = " "

    def format_citation(self, keys: list[str]) -> str:
        template = _normalize_link_template(self.cite_template)
        joined = self.separator.join(keys)
        return template.format(keys=joined)

    def format_citation_with_locator(self, keys: list[str], locator: str) -> str:
        template = _normalize_link_template(self.cite_with_locator_template)
        joined = self.separator.join(keys)
        return template.format(keys=joined, locator=locator)


@dataclass(frozen=True)
class FootnoteConfig:
    """Markdown footnote conversion rules."""

    footnote_template: str = r"\footnote{{{text}}}"

    def format_footnote(self, text: str) -> str:
        template = _normalize_link_template(self.footnote_template)
        return template.format(text=text)


@dataclass(frozen=True)
class ImageConfig:
    """Image conversion rules."""

    path_prefix: str = DEFAULT_FIGURES_PDF_PATH
    path_suffix: str = ".pdf"
    width_unit: str = r"\htmlpx"
    include_command: str = r"\includegraphics"
    block_template: str = DEFAULT_IMAGE_BLOCK_TEMPLATE
    base_dir: str | None = None
    validate_paths: bool = False

    def format_block(self, source_path: str, width_px: int) -> str:
        include_command = self.include_command
        if not include_command.startswith("\\"):
            include_command = f"\\{include_command}"
        if self.validate_paths:
            base = Path(self.base_dir) if self.base_dir else None
            prefix = self.path_prefix.rstrip("/")
            filename = f"{source_path}{self.path_suffix}"
            target = Path(prefix) / filename
            if base:
                target = base / target
            if not target.exists():
                warnings.warn(f"Image not found: {target}", stacklevel=2)
        return self.block_template.format(
            include_command=include_command,
            width=width_px,
            unit=self.width_unit,
            path_prefix=self.path_prefix.rstrip("/"),
            source=source_path,
            path_suffix=self.path_suffix,
        )


@dataclass(frozen=True)
class ListConfig:
    """List environment rules."""

    unordered_environment: str = "itemize"
    ordered_environment: str = "enumerate"


@dataclass(frozen=True)
class CodeBlockConfig:
    """Code block environment rules."""

    environment: str = "lstlisting"
    options_template: str | None = None

    def begin(self, language: str | None) -> str:
        if not self.options_template:
            return f"\\begin{{{self.environment}}}"
        options = self.options_template.format(language=language or "")
        if options.strip() == "":
            return f"\\begin{{{self.environment}}}"
        return f"\\begin{{{self.environment}}}[{options}]"

    def end(self) -> str:
        return f"\\end{{{self.environment}}}"


@dataclass(frozen=True)
class CalloutConfig:
    """Callout conversion rules."""

    environment_map: Mapping[str, str] = field(default_factory=dict)
    default_environment_template: str = DEFAULT_CALLOUT_ENV_TEMPLATE
    title_template: str | None = "[{title}]"
    type_normalization: str = "lower"

    def normalize_type(self, callout_type: str) -> str:
        if self.type_normalization == "lower":
            return callout_type.lower()
        if self.type_normalization == "upper":
            return callout_type.upper()
        return callout_type

    def resolve_environment(self, callout_type: str) -> str:
        normalized = self.normalize_type(callout_type)
        if normalized in self.environment_map:
            return self.environment_map[normalized]
        if callout_type in self.environment_map:
            return self.environment_map[callout_type]
        return self.default_environment_template.format(type=normalized)


@dataclass(frozen=True)
class TableConfig:
    """Table rendering rules."""

    environment: str = "tabular"
    include_hlines: bool = True
    multicolumn_align: str = "c"
    multirow_command: str = "multirow"


@dataclass(frozen=True)
class ParsingConfig:
    """Parsing behavior options."""

    strip_yaml_front_matter: bool = False


@dataclass(frozen=True)
class MathConfig:
    """Math conversion rules."""

    block_style: str = "dollars"  # dollars or brackets

    def format_block(self, content: str) -> str:
        if self.block_style == "brackets":
            return f"\\\\[{content}\\\\]"
        return f"$${content}$$"


@dataclass(frozen=True)
class LabelConfig:
    """Heading label generation rules."""

    auto_label_headings: bool = False
    label_template: str = r"\label{{{label}}}"
    label_prefix: str = ""
    label_separator: str = "-"


@dataclass(frozen=True)
class WikiLinkConfig:
    """Wiki-link conversion rules."""

    link_template: str = r"\ref{{{label}}}"
    alias_template: str = r"\ref{{{label}}}"
    label_separator: str = "-"

    def format_link(self, label: str) -> str:
        template = _normalize_link_template(self.link_template)
        return template.format(label=label)

    def format_alias(self, label: str, _alias: str) -> str:
        template = _normalize_link_template(self.alias_template)
        return template.format(label=label)


@dataclass(frozen=True)
class ConversionConfig:
    """Aggregate configuration for Markdown-to-LaTeX conversion."""

    headings: HeadingConfig = field(default_factory=HeadingConfig)
    inline: InlineConfig = field(default_factory=InlineConfig)
    links: LinkConfig = field(default_factory=LinkConfig)
    citations: CitationConfig = field(default_factory=CitationConfig)
    footnotes: FootnoteConfig = field(default_factory=FootnoteConfig)
    images: ImageConfig = field(default_factory=ImageConfig)
    lists: ListConfig = field(default_factory=ListConfig)
    code_blocks: CodeBlockConfig = field(default_factory=CodeBlockConfig)
    callouts: CalloutConfig = field(default_factory=CalloutConfig)
    tables: TableConfig = field(default_factory=TableConfig)
    parsing: ParsingConfig = field(default_factory=ParsingConfig)
    math: MathConfig = field(default_factory=MathConfig)
    labels: LabelConfig = field(default_factory=LabelConfig)
    wiki_links: WikiLinkConfig = field(default_factory=WikiLinkConfig)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any] | None) -> "ConversionConfig":
        if not data:
            return cls()

        headings_data = data.get("headings", {})
        inline_data = data.get("inline", {})
        links_data = data.get("links", {})
        citations_data = data.get("citations", {})
        footnotes_data = data.get("footnotes", {})
        images_data = data.get("images", {})
        lists_data = data.get("lists", data.get("list", {}))
        code_blocks_data = data.get("code_blocks", data.get("code-blocks", {}))
        callouts_data = data.get("callouts", {})
        tables_data = data.get("tables", {})
        parsing_data = data.get("parsing", {})
        math_data = data.get("math", {})
        labels_data = data.get("labels", {})
        wiki_links_data = data.get("wiki_links", {})

        headings = HeadingConfig(
            anchor_level=int(headings_data.get("anchor_level", 1)),
            commands=_coerce_int_mapping(headings_data.get("commands")),
            fallback_command=str(headings_data.get("fallback_command", "paragraph")),
        )

        inline = InlineConfig(
            bold_command=str(inline_data.get("bold_command", "textbf")),
            italic_command=str(inline_data.get("italic_command", "textit")),
            code_command=str(inline_data.get("code_command", "texttt")),
            line_break_command=str(inline_data.get("line_break_command", "newline")),
            texttt_escape_map=_coerce_str_mapping(
                inline_data.get("texttt_escape_map")
            )
            or dict(DEFAULT_TEXTTT_ESCAPE_MAP),
            character_normalization=tuple(
                tuple(pair)
                for pair in inline_data.get("character_normalization", DEFAULT_CHARACTER_NORMALIZATION)
            ),
        )

        links = LinkConfig(
            external_link_template=str(
                links_data.get("external_link_template", r"\href{url}{text}")
            ),
            url_only_template=str(
                links_data.get("url_only_template", r"\url{url}")
            ),
            autolink_template=str(
                links_data.get("autolink_template", r"\url{url}")
            ),
            internal_ref_template=str(
                links_data.get("internal_ref_template", r"\ref{{{label}}}")
            ),
        )

        citations = CitationConfig(
            cite_template=str(
                citations_data.get("cite_template", r"\cite{{{keys}}}")
            ),
            cite_with_locator_template=str(
                citations_data.get(
                    "cite_with_locator_template",
                    r"\cite[{locator}]{{{keys}}}",
                )
            ),
            separator=str(citations_data.get("separator", ",")),
            multi_cite_separator=str(citations_data.get("multi_cite_separator", " ")),
        )

        footnotes = FootnoteConfig(
            footnote_template=str(
                footnotes_data.get("footnote_template", r"\footnote{{{text}}}")
            ),
        )

        images = ImageConfig(
            path_prefix=str(images_data.get("path_prefix", DEFAULT_FIGURES_PDF_PATH)),
            path_suffix=str(images_data.get("path_suffix", ".pdf")),
            width_unit=str(images_data.get("width_unit", r"\htmlpx")),
            include_command=str(images_data.get("include_command", r"\includegraphics")),
            block_template=str(
                images_data.get(
                    "block_template",
                    DEFAULT_IMAGE_BLOCK_TEMPLATE,
                )
            ),
            base_dir=images_data.get("base_dir"),
            validate_paths=bool(images_data.get("validate_paths", False)),
        )

        lists = ListConfig(
            unordered_environment=str(
                lists_data.get("unordered_environment", "itemize")
            ),
            ordered_environment=str(lists_data.get("ordered_environment", "enumerate")),
        )

        code_blocks = CodeBlockConfig(
            environment=str(code_blocks_data.get("environment", "lstlisting")),
            options_template=code_blocks_data.get("options_template"),
        )

        callouts = CalloutConfig(
            environment_map=_coerce_str_mapping(callouts_data.get("environment_map")),
            default_environment_template=str(
                callouts_data.get("default_environment_template", DEFAULT_CALLOUT_ENV_TEMPLATE)
            ),
            title_template=callouts_data.get("title_template", "[{title}]"),
            type_normalization=str(callouts_data.get("type_normalization", "lower")),
        )

        tables = TableConfig(
            environment=str(tables_data.get("environment", "tabular")),
            include_hlines=bool(tables_data.get("include_hlines", True)),
            multicolumn_align=str(tables_data.get("multicolumn_align", "c")),
            multirow_command=str(tables_data.get("multirow_command", "multirow")),
        )

        return cls(
            headings=headings,
            inline=inline,
            links=links,
            citations=citations,
            footnotes=footnotes,
            images=images,
            lists=lists,
            code_blocks=code_blocks,
            callouts=callouts,
            tables=tables,
            parsing=ParsingConfig(
                strip_yaml_front_matter=bool(
                    parsing_data.get("strip_yaml_front_matter", False)
                )
            ),
            math=MathConfig(
                block_style=str(math_data.get("block_style", "dollars"))
            ),
            labels=LabelConfig(
                auto_label_headings=bool(
                    labels_data.get("auto_label_headings", False)
                ),
                label_template=str(
                    labels_data.get("label_template", r"\label{{{label}}}")
                ),
                label_prefix=str(labels_data.get("label_prefix", "")),
                label_separator=str(labels_data.get("label_separator", "-")),
            ),
            wiki_links=WikiLinkConfig(
                link_template=str(
                    wiki_links_data.get("link_template", r"\ref{{{label}}}")
                ),
                alias_template=str(
                    wiki_links_data.get("alias_template", r"\ref{{{label}}}")
                ),
                label_separator=str(
                    wiki_links_data.get("label_separator", "-")
                ),
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "headings": {
                "anchor_level": self.headings.anchor_level,
                "commands": dict(self.headings.commands),
                "fallback_command": self.headings.fallback_command,
            },
            "inline": {
                "bold_command": self.inline.bold_command,
                "italic_command": self.inline.italic_command,
                "code_command": self.inline.code_command,
                "line_break_command": self.inline.line_break_command,
                "texttt_escape_map": dict(self.inline.texttt_escape_map),
                "character_normalization": list(self.inline.character_normalization),
            },
            "links": {
                "external_link_template": self.links.external_link_template,
                "url_only_template": self.links.url_only_template,
                "autolink_template": self.links.autolink_template,
                "internal_ref_template": self.links.internal_ref_template,
            },
            "citations": {
                "cite_template": self.citations.cite_template,
                "cite_with_locator_template": self.citations.cite_with_locator_template,
                "separator": self.citations.separator,
                "multi_cite_separator": self.citations.multi_cite_separator,
            },
            "footnotes": {
                "footnote_template": self.footnotes.footnote_template,
            },
            "images": {
                "path_prefix": self.images.path_prefix,
                "path_suffix": self.images.path_suffix,
                "width_unit": self.images.width_unit,
                "include_command": self.images.include_command,
                "block_template": self.images.block_template,
                "base_dir": self.images.base_dir,
                "validate_paths": self.images.validate_paths,
            },
            "lists": {
                "unordered_environment": self.lists.unordered_environment,
                "ordered_environment": self.lists.ordered_environment,
            },
            "code_blocks": {
                "environment": self.code_blocks.environment,
                "options_template": self.code_blocks.options_template,
            },
            "callouts": {
                "environment_map": dict(self.callouts.environment_map),
                "default_environment_template": self.callouts.default_environment_template,
                "title_template": self.callouts.title_template,
                "type_normalization": self.callouts.type_normalization,
            },
            "tables": {
                "environment": self.tables.environment,
                "include_hlines": self.tables.include_hlines,
                "multicolumn_align": self.tables.multicolumn_align,
                "multirow_command": self.tables.multirow_command,
            },
            "parsing": {
                "strip_yaml_front_matter": self.parsing.strip_yaml_front_matter,
            },
            "math": {
                "block_style": self.math.block_style,
            },
            "labels": {
                "auto_label_headings": self.labels.auto_label_headings,
                "label_template": self.labels.label_template,
                "label_prefix": self.labels.label_prefix,
                "label_separator": self.labels.label_separator,
            },
            "wiki_links": {
                "link_template": self.wiki_links.link_template,
                "alias_template": self.wiki_links.alias_template,
                "label_separator": self.wiki_links.label_separator,
            },
        }

    def with_overrides(self, overrides: Mapping[str, Any] | None) -> "ConversionConfig":
        if not overrides:
            return self
        merged = _deep_merge(self.to_dict(), overrides)
        return ConversionConfig.from_dict(merged)


def _coerce_int_mapping(value: Any) -> dict[int, str]:
    if not value:
        return dict(DEFAULT_SECTION_COMMANDS)
    if not isinstance(value, Mapping):
        raise TypeError("Expected mapping for headings.commands")
    return {int(key): str(val) for key, val in value.items()}


def _coerce_str_mapping(value: Any) -> dict[str, str]:
    if not value:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("Expected mapping for environment maps")
    return {str(key): str(val) for key, val in value.items()}
