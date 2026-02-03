"""
Template rendering utilities for LaTeX assembly.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class TemplateContext:
    """Context used for simple placeholder replacement."""

    content: str
    values: Mapping[str, str]

    def as_mapping(self) -> Mapping[str, str]:
        merged = {"content": self.content}
        merged.update(self.values)
        return merged


def render_template(template_text: str, context: TemplateContext) -> str:
    """
    Render template by replacing {{key}} placeholders with values.
    """
    rendered = template_text
    for key, value in context.as_mapping().items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def load_template(path: Path) -> str:
    """
    Load a template file from disk.
    """
    return path.read_text(encoding="utf-8")
