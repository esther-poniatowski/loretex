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
convert_file(input_path: Path, output_path: Path | None, config_path: Path | None) -> None
    Convert a single Markdown file to LaTeX.

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

from loretex.api import convert_file as api_convert_file
from loretex.api import convert_spec as api_convert_spec
from loretex.conversion import ConversionConfig
from loretex.utils.io import load_yaml_spec

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
    loretex.conversion.MarkdownToLaTeXConverter
        Conversion engine used to convert Markdown text to LaTeX format.
    """

    spec_data = load_yaml_spec(spec_path) or {}
    outputs = api_convert_spec(spec_path)
    for output in outputs:
        typer.echo(f"[SUCCESS] Generated {output}")
    if spec_data.get("template"):
        typer.echo("[SUCCESS] Generated main.tex")


@app.command("convert-file")
def convert_file(
    input_path: Path = typer.Argument(..., help="Markdown file to convert."),
    output_path: Path | None = typer.Option(
        None, "--out", "-o", help="Optional output .tex path. Defaults to stdout."
    ),
    config_path: Path | None = typer.Option(
        None, "--config", "-c", help="Optional YAML conversion config."
    ),
    anchor_level: int = typer.Option(
        1, "--anchor", "-a", help="Markdown heading mapped to \\section{}."
    ),
) -> None:
    """
    Convert a single Markdown file to LaTeX and write to stdout or a file.
    """
    config_data = load_yaml_spec(config_path) if config_path else {}
    if config_data is None:
        config_data = {}
    config = ConversionConfig.from_dict(config_data)
    if not _has_anchor_override(config_data):
        config = config.with_overrides({"headings": {"anchor_level": anchor_level}})
    latex_text = api_convert_file(input_path, output_path, config=config)

    if output_path is None:
        typer.echo(latex_text)
        return

    typer.echo(f"[SUCCESS] Converted {input_path} to {output_path}")


def _has_anchor_override(data: dict) -> bool:
    headings = data.get("headings")
    return isinstance(headings, dict) and "anchor_level" in headings
