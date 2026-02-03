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
    def from_dict(cls, chapter_dict: dict, output_dir: Path, default_anchor: int):
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
        md = Path(chapter_dict["file"])
        options = chapter_dict.get("conversion")
        if options is None:
            options = chapter_dict.get("options")
        if options is None:
            options = chapter_dict.get("rules")
        if options is None:
            options = {}
        if not isinstance(options, dict):
            raise TypeError("Chapter conversion options must be a dictionary.")
        return cls(
            md_path=md,
            tex_output=output_dir / f"{md.stem}.tex",
            local_anchor=chapter_dict.get("anchor_level", default_anchor),
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

    @classmethod
    def from_spec(cls, spec: dict):
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
        output_dir = Path(spec.get("output_dir", "./tex"))
        anchor_level = spec.get("anchor_level", 1)
        conversion = spec.get("conversion")
        if conversion is None:
            conversion = spec.get("rules")
        if conversion is None:
            conversion = {}
        if not isinstance(conversion, dict):
            raise TypeError("Spec conversion rules must be a dictionary.")
        template_path = spec.get("template")
        if template_path is not None:
            template_path = Path(template_path)
        main_output = spec.get("main_output")
        if main_output is not None:
            main_output = Path(main_output)
        template_vars = spec.get("template_vars") or {}
        if not isinstance(template_vars, dict):
            raise TypeError("template_vars must be a dictionary.")
        bibliography = spec.get("bibliography")
        if isinstance(bibliography, list):
            bibliography = "\n".join(str(item) for item in bibliography)
        if bibliography is not None and not isinstance(bibliography, str):
            raise TypeError("bibliography must be a string or list of strings.")
        title = spec.get("title")
        author = spec.get("author")
        date = spec.get("date")
        chapters = [
            Chapter.from_dict(ch, output_dir, anchor_level)
            for ch in spec.get("chapters", [])
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
        )
