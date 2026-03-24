"""
Module: `loretex.parsers.markdown_converter`

Markdown-to-LaTeX transformation logic.

This module provides the legacy ``convert_markdown_to_latex`` helper. It delegates to the
canonical ``api.convert_string`` entry point so that all conversion paths share a single
implementation.

Functions
---------
convert_markdown_to_latex(markdown_text: str, anchor_level: int = 1, options: dict = None) -> str
    Convert a Markdown string to LaTeX format with specified heading levels and options.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Dict

from loretex.conversion.config import has_anchor_override


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
    from loretex.api import convert_string  # deferred to avoid circular import

    conversion_data = _extract_conversion_options(options)
    overrides: dict | None = None
    if anchor_level is not None and not has_anchor_override(conversion_data):
        overrides = {"headings": {"anchor_level": anchor_level}}
    return convert_string(markdown_text, config=conversion_data, overrides=overrides)


def _extract_conversion_options(options: Dict | None) -> Mapping[str, object]:
    if isinstance(options, Mapping):
        if "conversion" in options:
            return options.get("conversion") or {}
        if "rules" in options:
            return options.get("rules") or {}
    return options or {}
