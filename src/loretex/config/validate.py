"""
Specification validation helpers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class SpecValidationError(ValueError):
    """Raised when a spec file fails validation."""


def validate_spec(spec: dict[str, Any]) -> None:
    errors: list[str] = []
    if not isinstance(spec, dict):
        raise SpecValidationError("Spec must be a dictionary.")

    if "output_dir" in spec and not isinstance(spec["output_dir"], str):
        errors.append("output_dir must be a string.")
    if "anchor_level" in spec and not isinstance(spec["anchor_level"], int):
        errors.append("anchor_level must be an integer.")
    if "template" in spec:
        if not isinstance(spec["template"], str):
            errors.append("template must be a string path.")
        else:
            template_path = Path(spec["template"])
            if not template_path.exists():
                errors.append(f"template not found: {template_path}")
    if "main_output" in spec and not isinstance(spec["main_output"], str):
        errors.append("main_output must be a string path.")
    if "title" in spec and not isinstance(spec["title"], str):
        errors.append("title must be a string.")
    if "author" in spec and not isinstance(spec["author"], str):
        errors.append("author must be a string.")
    if "date" in spec and not isinstance(spec["date"], str):
        errors.append("date must be a string.")
    if "bibliography" in spec and not isinstance(spec["bibliography"], (str, list)):
        errors.append("bibliography must be a string or list of strings.")
    if "callout_title_font" in spec and not isinstance(spec["callout_title_font"], str):
        errors.append("callout_title_font must be a string.")
    if "callout_body_font" in spec and not isinstance(spec["callout_body_font"], str):
        errors.append("callout_body_font must be a string.")
    if "document_font" in spec and not isinstance(spec["document_font"], str):
        errors.append("document_font must be a string.")
    if "template_vars" in spec and not isinstance(spec["template_vars"], dict):
        errors.append("template_vars must be a dictionary.")

    chapters = spec.get("chapters", [])
    if not isinstance(chapters, list):
        errors.append("chapters must be a list.")
    else:
        for idx, chapter in enumerate(chapters):
            if not isinstance(chapter, dict):
                errors.append(f"chapters[{idx}] must be a dictionary.")
                continue
            if "file" not in chapter:
                errors.append(f"chapters[{idx}] missing required 'file'.")
            elif not isinstance(chapter["file"], str):
                errors.append(f"chapters[{idx}].file must be a string.")

    if errors:
        message = "Spec validation failed:\n- " + "\n- ".join(errors)
        raise SpecValidationError(message)
