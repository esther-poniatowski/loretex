"""
Module: `loretex.cli`

Defines the command-line interface for the loretex package.

This module declares command-line commands and associated logic using the `typer` library. The main
entry point is the `convert` subcommand, which transforms Markdown notes into LaTeX files according
to a YAML specification.

Functions
---------
convert(spec_path: Path, force: bool) -> None
    Convert Markdown notes to LaTeX files based on the provided YAML specification.
convert_file(input_path: Path, output_path: Path | None, config_path: Path | None) -> None
    Convert a single Markdown file to LaTeX.

Every path given on the command line is read from the current folder. The spec of ``convert`` is a
job file, not a configuration file: the paths written in it are relative to its own folder, so that
a document keeps its spec beside its Markdown. Loretex searches for no configuration file, hence has
no root: the conversion rules of ``convert-file`` come from ``--config`` only. An output never
overwrites an input of the conversion without ``--force``. The exit status is 2 on a usage or spec
error, and 1 when the conversion of the Markdown fails.

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
import yaml

from loretex import info as pkg_info, __version__
from loretex.api import convert_file as api_convert_file
from loretex.api import convert_spec as api_convert_spec
from loretex.api import check_overwrites
from loretex.conversion import ConversionConfig, LoretexError
from loretex.conversion.config import has_anchor_override
from loretex.utils.io import load_yaml_spec

app = typer.Typer(add_completion=False, no_args_is_help=True)

USAGE_ERROR = 2
"""Exit status of a usage or spec error."""

FORCE_HELP = "Overwrite an input of the conversion, such as the Markdown source, if an output names it."


def _fail(error: Exception, code: int) -> typer.Exit:
    """Print an error on the standard error and return the exit to raise."""
    typer.echo(f"loretex: error: {error}", err=True)
    return typer.Exit(code=code)


@app.callback()
def main_callback(
    version: bool = typer.Option(
        False, "--version", "-v", help="Show the package version and exit."
    )
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()

@app.command("info")
def cli_info() -> None:
    """Display package version and platform information."""
    typer.echo(pkg_info())


@app.command()
def convert(
    spec_path: Path = typer.Option(
        ...,
        "--spec",
        "-s",
        exists=True,
        dir_okay=False,
        help="Path to the YAML specification file, whose own paths are relative to its folder.",
    ),
    force: bool = typer.Option(False, "--force", help=FORCE_HELP),
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

    try:
        result = api_convert_spec(spec_path, force=force)
    except (ValueError, yaml.YAMLError, FileNotFoundError) as error:   # a spec or config error
        raise _fail(error, USAGE_ERROR) from error
    except LoretexError as error:
        raise _fail(error, error.exit_code) from error
    for output in result.chapter_outputs:
        typer.echo(f"[SUCCESS] Generated {output}")
    for output in result.auxiliary_outputs:
        typer.echo(f"[SUCCESS] Generated {output}")
    if result.main_output is not None:
        typer.echo(f"[SUCCESS] Generated {result.main_output.name}")


@app.command("convert-file")
def convert_file(
    input_path: Path = typer.Argument(
        ..., exists=True, dir_okay=False, help="Markdown file to convert."
    ),
    output_path: Path | None = typer.Option(
        None, "--output", "-o", help="Optional output .tex path. Defaults to stdout."
    ),
    config_path: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        exists=True,
        dir_okay=False,
        help="Optional YAML conversion config, with the schema of the conversion block of a spec.",
    ),
    anchor_level: int = typer.Option(
        1, "--anchor", "-a", help="Markdown heading mapped to \\section{}."
    ),
    force: bool = typer.Option(False, "--force", help=FORCE_HELP),
) -> None:
    """
    Convert a single Markdown file to LaTeX and write to stdout or a file.
    """
    try:
        if output_path is not None and config_path is not None:
            check_overwrites([output_path], [config_path], force)
        config_data = load_yaml_spec(config_path) if config_path else {}
        if config_data is None:
            config_data = {}
        config = ConversionConfig.from_dict(config_data)
        if not has_anchor_override(config_data):
            config = config.with_overrides({"headings": {"anchor_level": anchor_level}})
        latex_text = api_convert_file(input_path, output_path, config=config, force=force)
    except (ValueError, yaml.YAMLError) as error:                     # a config error
        raise _fail(error, USAGE_ERROR) from error
    except LoretexError as error:
        raise _fail(error, error.exit_code) from error

    if output_path is None:
        typer.echo(latex_text)
        return

    typer.echo(f"[SUCCESS] Converted {input_path} to {output_path}")
