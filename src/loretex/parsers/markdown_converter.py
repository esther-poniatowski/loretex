"""
Module: `loretex.parsers.markdown_converter`

Markdown-to-LaTeX transformation logic.

This module implements the core function `convert_markdown_to_latex` for converting Markdown strings
into LaTeX-formatted output. The conversion is modular and structured for extensibility.

Functions
---------
convert_markdown_to_latex(markdown_text: str, anchor_level: int = 1, options: Dict = None) -> str
    Convert a Markdown string to LaTeX format with specified heading levels and options.
"""

from collections.abc import Mapping
from typing import Dict

from loretex.conversion import ConversionConfig, MarkdownToLaTeXConverter


def convert_markdown_to_latex(
    markdown_text: str,
    anchor_level: int = 1,
    options: Dict | None = None,
) -> str:
    """
    Convert a Markdown string to LaTeX.

    Parameters
    ----------
    markdown_text : str
        Raw Markdown source text.
    anchor_level : int
        Heading level in Markdown to be mapped to \\section{}. Lower headings are mapped accordingly.
    options : dict, optional
        Additional conversion options (e.g., callout environments, custom macros).

    Returns
    -------
    str
        LaTeX-formatted output string.
    """
    conversion_data = _extract_conversion_options(options)
    config = ConversionConfig.from_dict(conversion_data)
    if anchor_level is not None and not _has_anchor_override(conversion_data):
        config = config.with_overrides({"headings": {"anchor_level": anchor_level}})
    converter = MarkdownToLaTeXConverter(config=config)
    return converter.convert_string(markdown_text)


def _extract_conversion_options(options: Dict | None) -> Mapping[str, object]:
    if isinstance(options, Mapping):
        if "conversion" in options:
            return options.get("conversion") or {}
        if "rules" in options:
            return options.get("rules") or {}
    return options or {}


def _has_anchor_override(options: Mapping[str, object]) -> bool:
    headings = options.get("headings")
    return isinstance(headings, Mapping) and "anchor_level" in headings
