"""
Module= `loretex.config.params`

Structured representations of specification parameters for the loretex package.

This module defines immutable data classes for storing and validating the parameters used in the
Markdown-to-LaTeX conversion pipeline.

Classes
-------
SpecParams
    Encapsulates global parameters extracted from the YAML specification file.
Chapter
    Represents a single Markdown document to be converted.

Notes
-----
All classes are implemented using the `attrs` library for conciseness, immutability, and built-in
type validation. Construction from raw dictionaries is supported via class methods.

See Also
--------
attrs. https://www.attrs.org/en/stable/
    Library for creating classes with automatic attribute management and validation.
"""
from pathlib import Path
from typing import List

import attr
from loretex.config.exceptions import SpecValidationError

# Presentation defaults for template assembly (Fix 6: centralised here, not in api.py)
DEFAULT_DOCUMENT_FONT: str = r"\renewcommand{\familydefault}{\sfdefault}"
DEFAULT_CALLOUT_TITLE_FONT: str = r"\sffamily\bfseries"
DEFAULT_CALLOUT_BODY_FONT: str = r"\sffamily"


@attr.s(auto_attribs=True, frozen=True)
class Chapter:
    """
    Structured representation of a single Markdown-to-LaTeX conversion unit.

    Parameters
    ----------
    md_path : Path
        Path to the source Markdown file.
    tex_output : Path
        Path to the output LaTeX file to be written.
    local_anchor : int
        Heading level to be mapped to `\\section{}` in LaTeX.
    options : dict
        Conversion rule overrides for this chapter.

    Methods
    -------
    from_dict(chapter_dict, output_dir, default_anchor)
        Construct a Chapter from a YAML specification entry.
    """

    md_path: Path
    tex_output: Path
    local_anchor: int
    options: dict

    @classmethod
    def from_dict(
        cls,
        chapter_dict: dict,
        output_dir: Path,
        default_anchor: int,
        *,
        base_dir: Path | None = None,
    ):
        """
        Create a Chapter object from a chapter dictionary.

        Parameters
        ----------
        chapter_dict : dict
            Dictionary describing the chapter entry in the specification.
        output_dir : Path
            Output directory for generated LaTeX files.
        default_anchor : int
            Default anchor level to use if not specified in the entry.

        Returns
        -------
        Chapter
            Fully initialized Chapter instance.
        """
        if not isinstance(chapter_dict, dict):
            raise SpecValidationError("Chapter entries must be dictionaries.")
        if "file" not in chapter_dict or not isinstance(chapter_dict["file"], str):
            raise SpecValidationError("Each chapter requires a string 'file' path.")
        allowed_keys = {"file", "anchor_level", "conversion", "options", "rules", "output"}
        unknown = sorted(key for key in chapter_dict if key not in allowed_keys)
        if unknown:
            raise SpecValidationError(f"Unknown chapter key(s): {', '.join(unknown)}")

        source_ref = Path(chapter_dict["file"])
        md = _resolve_spec_path(source_ref, base_dir)
        options = chapter_dict.get("conversion")
        if options is None:
            options = chapter_dict.get("options")
        if options is None:
            options = chapter_dict.get("rules")
        if options is None:
            options = {}
        if not isinstance(options, dict):
            raise SpecValidationError("Chapter conversion options must be a dictionary.")
        local_anchor = chapter_dict.get("anchor_level", default_anchor)
        if not isinstance(local_anchor, int):
            raise SpecValidationError("Chapter anchor_level must be an integer.")
        output_ref = chapter_dict.get("output")
        if output_ref is not None and not isinstance(output_ref, str):
            raise SpecValidationError("Chapter output must be a string path.")
        tex_output = (
            _resolve_output_path(Path(output_ref), output_dir)
            if output_ref is not None
            else output_dir / _default_output_relpath(source_ref)
        )
        return cls(
            md_path=md,
            tex_output=tex_output,
            local_anchor=local_anchor,
            options=options
        )


@attr.s(auto_attribs=True, frozen=True)
class SpecParams:
    """
    Structured representation of a YAML specification file.

    Parameters
    ----------
    output_dir : Path
        Directory to write all LaTeX output files.
    anchor_level : int
        Default anchor level for heading conversion.
    chapters : List[Chapter]
        List of Chapter objects to be processed.
    conversion : dict
        Global conversion rule overrides.
    template_path : Path | None
        Path to a LaTeX template file containing the {{content}} placeholder.
    main_output : Path | None
        Path to the assembled main .tex output file.
    template_vars : dict
        Extra variables available to templates.
    bibliography : str | None
        Bibliography snippet inserted into templates.
    title : str | None
        Document title for templates.
    author : str | None
        Document author for templates.
    date : str | None
        Document date for templates.
    callout_title_font : str | None
        LaTeX font command for callout titles (e.g. "\\sffamily\\bfseries").
    callout_body_font : str | None
        LaTeX font command for callout body text (e.g. "\\sffamily").
    document_font : str | None
        LaTeX command to set the default document font (e.g. "\\renewcommand{\\familydefault}{\\sfdefault}").

    Methods
    -------
    from_spec(spec)
        Construct a SpecParams object from a parsed YAML dictionary.
    """

    output_dir: Path
    anchor_level: int
    chapters: List[Chapter]
    conversion: dict
    template_path: Path | None
    main_output: Path | None
    template_vars: dict
    bibliography: str | None
    title: str | None
    author: str | None
    date: str | None
    callout_title_font: str | None
    callout_body_font: str | None
    document_font: str | None

    @classmethod
    def from_spec(cls, spec: dict, *, base_dir: Path | None = None):
        """
        Create a SpecParams object from a YAML specification.

        Parameters
        ----------
        spec : dict
            Dictionary loaded from the YAML specification file.

        Returns
        -------
        SpecParams
            Fully initialized specification object.
        """
        if not isinstance(spec, dict):
            raise SpecValidationError("Spec must be a dictionary.")

        allowed_keys = {
            "output_dir",
            "anchor_level",
            "chapters",
            "conversion",
            "rules",
            "template",
            "main_output",
            "template_vars",
            "bibliography",
            "title",
            "author",
            "date",
            "callout_title_font",
            "callout_body_font",
            "document_font",
        }
        unknown_keys = sorted(key for key in spec if key not in allowed_keys)
        if unknown_keys:
            raise SpecValidationError(f"Unknown spec key(s): {', '.join(unknown_keys)}")

        output_dir_raw = spec.get("output_dir", "./tex")
        if not isinstance(output_dir_raw, str):
            raise SpecValidationError("output_dir must be a string.")
        output_dir = _resolve_spec_path(Path(output_dir_raw), base_dir)
        anchor_level = spec.get("anchor_level", 1)
        if not isinstance(anchor_level, int):
            raise SpecValidationError("anchor_level must be an integer.")
        conversion = spec.get("conversion")
        if conversion is None:
            conversion = spec.get("rules")
        if conversion is None:
            conversion = {}
        if not isinstance(conversion, dict):
            raise SpecValidationError("Spec conversion rules must be a dictionary.")
        template_path = spec.get("template")
        if template_path is not None:
            if not isinstance(template_path, str):
                raise SpecValidationError("template must be a string path.")
            template_path = _resolve_spec_path(Path(template_path), base_dir)
            if not template_path.exists():
                raise SpecValidationError(f"template not found: {template_path}")
        main_output = spec.get("main_output")
        if main_output is not None:
            if not isinstance(main_output, str):
                raise SpecValidationError("main_output must be a string path.")
            main_output = _resolve_output_path(Path(main_output), output_dir)
        template_vars = spec.get("template_vars") or {}
        if not isinstance(template_vars, dict):
            raise SpecValidationError("template_vars must be a dictionary.")
        bibliography = spec.get("bibliography")
        if isinstance(bibliography, list):
            bibliography = "\n".join(str(item) for item in bibliography)
        if bibliography is not None and not isinstance(bibliography, str):
            raise SpecValidationError("bibliography must be a string or list of strings.")
        title = spec.get("title")
        author = spec.get("author")
        date = spec.get("date")
        callout_title_font = spec.get("callout_title_font")
        callout_body_font = spec.get("callout_body_font")
        document_font = spec.get("document_font")
        for label, value in (
            ("title", title),
            ("author", author),
            ("date", date),
            ("callout_title_font", callout_title_font),
            ("callout_body_font", callout_body_font),
            ("document_font", document_font),
        ):
            if value is not None and not isinstance(value, str):
                raise SpecValidationError(f"{label} must be a string.")
        chapters_raw = spec.get("chapters", [])
        if not isinstance(chapters_raw, list):
            raise SpecValidationError("chapters must be a list.")
        chapters = [
            Chapter.from_dict(ch, output_dir, anchor_level, base_dir=base_dir)
            for ch in chapters_raw
        ]
        return cls(
            output_dir=output_dir,
            anchor_level=anchor_level,
            chapters=chapters,
            conversion=conversion,
            template_path=template_path,
            main_output=main_output,
            template_vars=template_vars,
            bibliography=bibliography,
            title=title,
            author=author,
            date=date,
            callout_title_font=callout_title_font,
            callout_body_font=callout_body_font,
            document_font=document_font,
        )


def _resolve_spec_path(path: Path, base_dir: Path | None) -> Path:
    if path.is_absolute() or base_dir is None:
        return path
    return (base_dir / path).resolve()


def _resolve_output_path(path: Path, output_dir: Path) -> Path:
    if path.is_absolute():
        return path
    return output_dir / path


def _default_output_relpath(source_ref: Path) -> Path:
    if source_ref.is_absolute():
        return Path(source_ref.name).with_suffix(".tex")
    return source_ref.with_suffix(".tex")
