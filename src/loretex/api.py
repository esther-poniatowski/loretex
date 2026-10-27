"""
Public API helpers for the loretex package.

This module exposes simple, stable entry points for common conversion workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import stat
import tempfile
from typing import Mapping

from loretex.config.params import (
    DEFAULT_CALLOUT_BODY_FONT,
    DEFAULT_CALLOUT_TITLE_FONT,
    DEFAULT_DOCUMENT_FONT,
    SpecParams,
)
from loretex.conversion import ConversionConfig, ConversionError, MarkdownToLaTeXConverter
from loretex.conversion.config import has_anchor_override
from loretex.pipeline import AssemblyPlan, render_assembly
from loretex.utils.io import load_yaml_spec


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
    auxiliary_outputs: list[Path]
    main_output: Path | None


@dataclass(frozen=True)
class PlannedOutput:
    """One fully rendered file awaiting its filesystem write."""

    path: Path
    text: str


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
        base_dir = None
    else:
        spec = load_yaml_spec(spec_input) or {}
        base_dir = Path(spec_input).resolve().parent
    params = SpecParams.from_spec(spec, base_dir=base_dir)

    planned, chapter_outputs, auxiliary_outputs = _convert_chapters(params)
    main_output = _plan_main(params, chapter_outputs, planned)
    _validate_unique_outputs(planned)
    _write_outputs(planned)

    return SpecResult(
        chapter_outputs=chapter_outputs,
        auxiliary_outputs=auxiliary_outputs,
        main_output=main_output,
    )


def _convert_chapters(
    params: SpecParams,
) -> tuple[list[PlannedOutput], list[Path], list[Path]]:
    """Render every chapter and title fragment without changing output files."""
    base_config = ConversionConfig.from_dict(params.conversion)
    if not has_anchor_override(params.conversion):
        base_config = base_config.with_overrides(
            {"headings": {"anchor_level": params.anchor_level}}
        )
    converter = MarkdownToLaTeXConverter(config=base_config)

    planned: list[PlannedOutput] = []
    chapter_outputs: list[Path] = []
    auxiliary_outputs: list[Path] = []
    for chapter in params.chapters:
        markdown_text = chapter.md_path.read_text(encoding="utf-8")
        overrides = chapter.options or {}
        if chapter.local_anchor is not None and not has_anchor_override(overrides):
            overrides = _apply_anchor_override(overrides, chapter.local_anchor)
        result = converter.convert_result(markdown_text, overrides)
        planned.append(PlannedOutput(chapter.tex_output, result.latex))
        chapter_outputs.append(chapter.tex_output)
        if chapter.title is not None:
            if result.first_heading is None:
                raise ConversionError(
                    f"{chapter.md_path}: a declared title output requires a heading"
                )
            try:
                title_text = chapter.title.template.format(title=result.first_heading)
            except (KeyError, ValueError) as error:
                raise ConversionError(
                    f"{chapter.md_path}: invalid title template: {error}"
                ) from error
            planned.append(PlannedOutput(chapter.title.output, title_text))
            auxiliary_outputs.append(chapter.title.output)
    return planned, chapter_outputs, auxiliary_outputs


def _write_outputs(planned: list[PlannedOutput]) -> None:
    """Stage every output beside its target, then replace the declared files."""
    staged: list[tuple[Path, Path]] = []
    try:
        for output in planned:
            output.path.parent.mkdir(parents=True, exist_ok=True)
            output_mode = (
                stat.S_IMODE(output.path.stat().st_mode)
                if output.path.exists()
                else 0o644
            )
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=output.path.parent,
                prefix=f".{output.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(output.text)
                os.chmod(handle.name, output_mode)
                staged.append((Path(handle.name), output.path))
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _target in staged:
            temporary.unlink(missing_ok=True)


def _validate_unique_outputs(planned: list[PlannedOutput]) -> None:
    """Reject output plans whose declared targets overlap."""
    seen: set[Path] = set()
    for output in planned:
        target = output.path.resolve()
        if target in seen:
            raise ConversionError(f"duplicate output path: {output.path}")
        seen.add(target)


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


def _plan_main(
    params: SpecParams,
    chapter_outputs: list[Path],
    planned: list[PlannedOutput],
) -> Path | None:
    if params.template_path is None:
        return None
    main_output = params.main_output or (params.output_dir / "main.tex")
    template_vars = _build_template_vars(params)
    plan = AssemblyPlan(
        output_dir=params.output_dir,
        chapter_outputs=chapter_outputs,
        template_path=params.template_path,
        main_output=main_output,
        template_vars=template_vars,
    )
    planned.append(PlannedOutput(main_output, render_assembly(plan)))
    return main_output


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
