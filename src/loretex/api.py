"""
Public API helpers for the loretex package.

This module exposes simple, stable entry points for common conversion workflows.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

from loretex.config.params import SpecParams
from loretex.config.validate import validate_spec
from loretex.conversion import ConversionConfig, MarkdownToLaTeXConverter
from loretex.pipeline import AssemblyPlan, assemble
from loretex.utils.io import ensure_output_dir, load_yaml_spec


def convert_string(
    source: str,
    config: ConversionConfig | Mapping[str, object] | None = None,
    overrides: Mapping[str, object] | None = None,
    transforms: list | None = None,
) -> str:
    """
    Convert a Markdown string to LaTeX.
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


def convert_spec(spec_path: Path) -> list[Path]:
    """
    Convert chapters from a YAML specification file.

    Returns a list of generated output paths.
    """
    spec = load_yaml_spec(spec_path) or {}
    validate_spec(spec)
    params = SpecParams.from_spec(spec)
    ensure_output_dir(params.output_dir)

    base_config = ConversionConfig.from_dict(params.conversion)
    if not _has_anchor_override(params.conversion):
        base_config = base_config.with_overrides(
            {"headings": {"anchor_level": params.anchor_level}}
        )
    converter = MarkdownToLaTeXConverter(config=base_config)

    outputs: list[Path] = []
    for chapter in params.chapters:
        markdown_text = chapter.md_path.read_text(encoding="utf-8")
        overrides = chapter.options or {}
        if chapter.local_anchor is not None and not _has_anchor_override(overrides):
            overrides = _apply_anchor_override(overrides, chapter.local_anchor)
        latex_text = converter.convert_string(markdown_text, overrides)
        chapter.tex_output.write_text(latex_text, encoding="utf-8")
        outputs.append(chapter.tex_output)

    _maybe_assemble_main(params, outputs)
    return outputs


def _coerce_config(
    config: ConversionConfig | Mapping[str, object] | None,
) -> ConversionConfig:
    if config is None:
        return ConversionConfig()
    if isinstance(config, ConversionConfig):
        return config
    return ConversionConfig.from_dict(config)


def _has_anchor_override(data: Mapping[str, object]) -> bool:
    headings = data.get("headings")
    return isinstance(headings, Mapping) and "anchor_level" in headings


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


def _maybe_assemble_main(params: SpecParams, outputs: list[Path]) -> Path | None:
    if params.template_path is None:
        return None
    main_output = params.main_output or (params.output_dir / "main.tex")
    document_font = (
        params.document_font or r"\renewcommand{\familydefault}{\sfdefault}"
    )
    callout_title_font = params.callout_title_font or r"\sffamily\bfseries"
    callout_body_font = params.callout_body_font or r"\sffamily"
    template_vars = {
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
    plan = AssemblyPlan(
        output_dir=params.output_dir,
        chapter_outputs=outputs,
        template_path=params.template_path,
        main_output=main_output,
        template_vars=template_vars,
    )
    return assemble(plan)
