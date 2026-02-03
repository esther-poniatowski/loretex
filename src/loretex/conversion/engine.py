"""Conversion engine entry points."""

from __future__ import annotations

from typing import Mapping

from .config import ConversionConfig
from .generator import LaTeXGenerator
from .inline import InlineTransformer
from .parser import MarkdownParser
from .registry import resolve_transforms
from .transforms import Transform, apply_transforms


class MarkdownToLaTeXConverter:
    """Main converter orchestrating the transformation."""

    def __init__(
        self,
        parser: MarkdownParser | None = None,
        generator: LaTeXGenerator | None = None,
        config: ConversionConfig | None = None,
        transforms: list[Transform] | None = None,
        transform_names: list[str] | None = None,
    ) -> None:
        self._config = config or ConversionConfig()
        self._parser = parser or MarkdownParser()
        self._generator = generator or LaTeXGenerator(self._config)
        self._transforms = transforms or []
        if transform_names:
            self._transforms = [*self._transforms, *resolve_transforms(transform_names)]

    def convert_string(self, source: str, overrides: Mapping[str, object] | None = None) -> str:
        """Convert Markdown string to LaTeX.

        Parameters
        ----------
        source : str
            Markdown source content.
        overrides : Mapping[str, object], optional
            Partial conversion configuration overrides.

        Returns
        -------
        str
            Converted LaTeX.
        """
        if overrides:
            config = self._config.with_overrides(overrides)
        else:
            config = self._config
        if config.parsing.strip_yaml_front_matter:
            source = _strip_yaml_front_matter(source)
        source, footnotes = _extract_footnotes(source)
        if overrides or footnotes:
            inline_transformer = InlineTransformer(config, footnotes)
            generator = LaTeXGenerator(config, inline_transformer=inline_transformer)
        else:
            generator = self._generator
        ast = self._parser.parse(source)
        if self._transforms:
            ast = apply_transforms(ast, self._transforms)
        return ast.accept(generator)


def convert_string(
    source: str,
    config: ConversionConfig | None = None,
    overrides: Mapping[str, object] | None = None,
) -> str:
    """Convenience helper for converting Markdown to LaTeX."""
    converter = MarkdownToLaTeXConverter(config=config)
    return converter.convert_string(source, overrides)


def _strip_yaml_front_matter(source: str) -> str:
    lines = source.splitlines()
    if not lines:
        return source
    if lines[0].strip() != "---":
        return source
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "\n".join(lines[idx + 1 :]).lstrip("\n")
    return source


def _extract_footnotes(source: str) -> tuple[str, dict[str, str]]:
    lines = source.splitlines()
    if not lines:
        return source, {}
    footnotes: dict[str, str] = {}
    output_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("[^") and "]: " in line:
            key, rest = line.split("]: ", 1)
            key = key[2:]
            content_lines = [rest.rstrip()]
            i += 1
            while i < len(lines):
                next_line = lines[i]
                if next_line.startswith("[^") and "]: " in next_line:
                    break
                if next_line.strip() == "":
                    content_lines.append("")
                    i += 1
                    continue
                if next_line.startswith("    ") or next_line.startswith("\t"):
                    content_lines.append(next_line.strip())
                    i += 1
                    continue
                break
            footnotes[key] = "\n".join(content_lines).strip()
            continue
        output_lines.append(line)
        i += 1
    return "\n".join(output_lines), footnotes
