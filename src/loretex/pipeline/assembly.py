"""
Document assembly utilities for generating a main LaTeX file.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from loretex.pipeline.templates import TemplateContext, load_template, render_template


@dataclass(frozen=True)
class AssemblyPlan:
    """Plan describing how to assemble a main LaTeX document."""

    output_dir: Path
    chapter_outputs: list[Path]
    template_path: Path
    main_output: Path
    template_vars: dict[str, str]


def build_inputs(chapter_outputs: list[Path], *, main_output: Path) -> str:
    """
    Build a sequence of \\input{...} lines for chapter outputs.
    """
    lines = []
    base_dir = main_output.parent
    for chapter in chapter_outputs:
        relative = os.path.relpath(Path(chapter).resolve(), base_dir.resolve())
        lines.append(f"\\input{{{Path(relative).as_posix()}}}")
    return "\n".join(lines)


def assemble(plan: AssemblyPlan) -> Path:
    """
    Assemble a main.tex file using the template and chapter outputs.
    """
    template_text = load_template(plan.template_path)
    inputs = build_inputs(plan.chapter_outputs, main_output=plan.main_output)
    context = TemplateContext(content=inputs, values=plan.template_vars)
    rendered = render_template(template_text, context)
    plan.main_output.parent.mkdir(parents=True, exist_ok=True)
    plan.main_output.write_text(rendered, encoding="utf-8")
    return plan.main_output
