"""
Module: `loretex.cli`

Defines the command-line interface for the loretex package.

This module declares command-line commands and associated logic using the `typer` library. The main
entry point is the `convert` subcommand, which transforms Markdown notes into LaTeX files according
to a YAML specification.

Functions
---------
convert(spec_path: Path) -> None
    Convert Markdown notes to LaTeX files based on the provided YAML specification.

See Also
--------
typer. https://typer.tiangolo.com/
    Library for building command-line interfaces with Python.

Notes
-----
In the `Typer` constructor, `add_completion=False` disables automatic installation of shell
completion support (e.g., Bash, Zsh) to keep the CLI interface minimal.
"""

from pathlib import Path

import typer

from loretex.utils.io import load_yaml_spec, ensure_output_dir
from loretex.parsers.markdown_converter import convert_markdown_to_latex
from loretex.config.params import SpecParams

app = typer.Typer(add_completion=False)

@app.command()
def convert(
    spec_path: Path = typer.Option(..., "--spec", "-s", help="Path to the YAML specification file.")
) -> None:
    """
    Convert Markdown notes to LaTeX files according to the specification and write LaTeX files to
    the specified output directory.

    Arguments
    ---------
    spec_path : Path
        Path to the YAML specification file defining global conversion parameters and chapter
        definitions.

    See Also
    --------
    loretex.params.SpecParams
        Class representing the global parameters and chapter definitions extracted from the spec.
    loretex.utils.io.load_yaml_spec
        Function to load and parse the YAML specification file.
    loretex.utils.io.ensure_output_dir
        Function to ensure the output directory exists before writing files.
    loretex.parsers.markdown_converter.convert_markdown_to_latex
        Function to convert Markdown text to LaTeX format based on specified options.
    """

    spec = load_yaml_spec(spec_path)
    params = SpecParams.from_spec(spec)
    ensure_output_dir(params.output_dir)

    for chapter in params.chapters:
        with open(chapter.md_path, "r", encoding="utf-8") as f:
            markdown_text = f.read()

        latex_text = convert_markdown_to_latex(
            markdown_text,
            anchor_level=chapter.local_anchor,
            options=chapter.options
        )

        with open(chapter.tex_output, "w", encoding="utf-8") as f:
            f.write(latex_text)

        typer.echo(f"[SUCCESS] Converted {chapter.md_path} to {chapter.tex_output}")
