"""
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
        Heading level to be mapped to `\section{}` in LaTeX.
    options : dict
        Additional options passed from the specification file.

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
        return cls(
            md_path=md,
            tex_output=output_dir / f"{md.stem}.tex",
            local_anchor=chapter_dict.get("anchor_level", default_anchor),
            options=chapter_dict
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

    Methods
    -------
    from_spec(spec)
        Construct a SpecParams object from a parsed YAML dictionary.
    """

    output_dir: Path
    anchor_level: int
    chapters: List[Chapter]

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
        chapters = [
            Chapter.from_dict(ch, output_dir, anchor_level)
            for ch in spec.get("chapters", [])
        ]
        return cls(output_dir=output_dir, anchor_level=anchor_level, chapters=chapters)
