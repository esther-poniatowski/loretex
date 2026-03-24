"""
Public API helpers for the loretex package.

This module exposes simple, stable entry points for common conversion workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from loretex.config.params import (
    DEFAULT_CALLOUT_BODY_FONT,
    DEFAULT_CALLOUT_TITLE_FONT,
    DEFAULT_DOCUMENT_FONT,
    SpecParams,
)
from loretex.config.validate import validate_spec
from loretex.conversion import ConversionConfig, MarkdownToLaTeXConverter
from loretex.conversion.config import has_anchor_override
from loretex.pipeline import AssemblyPlan, assemble
from loretex.utils.io import ensure_output_dir, load_yaml_spec


# ---------------------------------------------------------------------------
# String / file conversion (Fix 1: single authoritative path)
# ---------------------------------------------------------------------------


def convert_string(
    source: str,
    config: ConversionConfig | Mapping[str, object] | None = None,
    overrides: Mapping[str, object] | None = None,
    transforms: list | None = None,
) -> str:
    """
    Convert a Markdown string to LaTeX.

    This is the canonical public entry point. All other helpers ultimately
    delegate to :meth:`MarkdownToLaTeXConverter.convert_string`.
    """
    conversion_config = _coerce_config(config)
    converter = MarkdownToLaTeXConverter(config=conversion_config, transforms=transforms)
    return converter.convert_string(source, overrides)


def convert_file(
    input_path: Path,
    output_path: Path | None = None,
    config: ConversionConfig | Mapping[str, object] | None = None,
    overrides: Mapping[str, object] | None = None,
    transforms: list | None = None,
) -> str:
    """
    Convert a Markdown file to LaTeX. Returns the LaTeX string.
    """
    markdown_text = input_path.read_text(encoding="utf-8")
    latex_text = convert_string(
        markdown_text,
        config=config,
        overrides=overrides,
        transforms=transforms,
    )

    if output_path is not None:
        output_path.write_text(latex_text, encoding="utf-8")

    return latex_text


# ---------------------------------------------------------------------------
# Spec-based batch conversion (Fix 2: decomposed into three layers)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SpecResult:
    """Result of a spec-based batch conversion."""

    chapter_outputs: list[Path]
    main_output: Path | None


def convert_spec(spec_input: Path | dict) -> SpecResult:
    """
    Convert chapters from a YAML specification file (or pre-loaded dict).

    Parameters
    ----------
    spec_input : Path | dict
        Either the path to a YAML spec file, or an already-loaded spec dict.

    Returns
    -------
    SpecResult
        Paths of generated chapter files and, optionally, the assembled main file.
    """
    if isinstance(spec_input, dict):
        spec = spec_input
    else:
        spec = load_yaml_spec(spec_input) or {}
    validate_spec(spec)
    params = SpecParams.from_spec(spec)

    # Layer 1 — pure orchestration (no I/O)
    converted = _convert_chapters(params)

    # Layer 3 — I/O: write results to disk
    chapter_outputs = _write_chapters(params, converted)

    # Optional assembly
    main_output = _maybe_assemble_main(params, chapter_outputs)

    return SpecResult(chapter_outputs=chapter_outputs, main_output=main_output)


def _convert_chapters(params: SpecParams) -> list[tuple[Path, str]]:
    """Layer 1: pure orchestration — convert every chapter and return pairs.

    Returns a list of ``(output_path, latex_text)`` without performing any I/O.
    """
    base_config = ConversionConfig.from_dict(params.conversion)
    if not has_anchor_override(params.conversion):
        base_config = base_config.with_overrides(
            {"headings": {"anchor_level": params.anchor_level}}
        )
    converter = MarkdownToLaTeXConverter(config=base_config)

    results: list[tuple[Path, str]] = []
    for chapter in params.chapters:
        markdown_text = chapter.md_path.read_text(encoding="utf-8")
        overrides = chapter.options or {}
        if chapter.local_anchor is not None and not has_anchor_override(overrides):
            overrides = _apply_anchor_override(overrides, chapter.local_anchor)
        latex_text = converter.convert_string(markdown_text, overrides)
        results.append((chapter.tex_output, latex_text))
    return results


def _write_chapters(
    params: SpecParams, converted: list[tuple[Path, str]]
) -> list[Path]:
    """Layer 3: I/O — write converted chapters to disk."""
    ensure_output_dir(params.output_dir)
    outputs: list[Path] = []
    for tex_path, latex_text in converted:
        tex_path.write_text(latex_text, encoding="utf-8")
        outputs.append(tex_path)
    return outputs


def _build_template_vars(params: SpecParams) -> dict[str, str]:
    """Layer 2: build template variables from spec params (pure).

    Font defaults are drawn from ``SpecParams`` field defaults rather than
    being hardcoded here (Fix 6).
    """
    document_font = params.document_font or DEFAULT_DOCUMENT_FONT
    callout_title_font = params.callout_title_font or DEFAULT_CALLOUT_TITLE_FONT
    callout_body_font = params.callout_body_font or DEFAULT_CALLOUT_BODY_FONT
    template_vars: dict[str, str] = {
        "document_font": document_font,
        "title": f"{{{params.title}}}" if params.title else "",
        "author": f"{{{params.author}}}" if params.author else "",
        "date": f"{{{params.date}}}" if params.date else "",
        "bibliography": params.bibliography or "",
        "callout_title_font": (
            f"\\renewcommand{{\\loretexcallouttitlefont}}{{{callout_title_font}}}"
        ),
        "callout_body_font": (
            f"\\renewcommand{{\\loretexcalloutbodyfont}}{{{callout_body_font}}}"
        ),
    }
    template_vars.update(
        {str(key): str(value) for key, value in params.template_vars.items()}
    )
    return template_vars


def _maybe_assemble_main(params: SpecParams, outputs: list[Path]) -> Path | None:
    if params.template_path is None:
        return None
    main_output = params.main_output or (params.output_dir / "main.tex")
    template_vars = _build_template_vars(params)
    plan = AssemblyPlan(
        output_dir=params.output_dir,
        chapter_outputs=outputs,
        template_path=params.template_path,
        main_output=main_output,
        template_vars=template_vars,
    )
    return assemble(plan)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _coerce_config(
    config: ConversionConfig | Mapping[str, object] | None,
) -> ConversionConfig:
    if config is None:
        return ConversionConfig()
    if isinstance(config, ConversionConfig):
        return config
    return ConversionConfig.from_dict(config)


def _apply_anchor_override(overrides: Mapping[str, object], anchor_level: int) -> dict:
    updated = dict(overrides)
    headings = updated.get("headings")
    if isinstance(headings, Mapping):
        headings = dict(headings)
    else:
        headings = {}
    headings.setdefault("anchor_level", anchor_level)
    updated["headings"] = headings
    return updated
