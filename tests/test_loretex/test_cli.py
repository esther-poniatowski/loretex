"""
Module: `test_loretex.test_cli`

Test suite for the CLI interface of the loretex package.

See Also
--------
loretex.cli:
    Module under test.
typer.testing.CliRunner:
    Utility for testing command-line interfaces built with Typer.
"""
from typer.testing import CliRunner

from loretex.cli import app

runner = CliRunner()

def test_cli_help():
    """
    Test that the CLI responds correctly to the `--help` command.
    """
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "convert" in result.stdout  # checks if subcommand appears in help


def test_cli_runs_on_spec(tmp_path):
    """
    Test that the CLI can run with a valid specification file.
    This test creates a temporary specification file and invokes the CLI to ensure it can process
    the file without errors.
    """
    spec_file = tmp_path / "spec.yml"
    spec_file.write_text("output_dir: ./out\nanchor_level: 1\nchapters: []")
    result = runner.invoke(app, ["convert", "--spec", str(spec_file)])
    assert result.exit_code == 0


def test_cli_convert_file_stdout(tmp_path):
    """
    Test that the CLI can convert a single file and write to stdout.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello\n\nWorld", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file)])
    assert result.exit_code == 0
    assert r"\section{Hello}" in result.stdout
    assert "World" in result.stdout


def test_cli_convert_file_output(tmp_path):
    """
    Test that the CLI can convert a single file and write to a file.
    """
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.tex"
    input_file.write_text("# Hello\n\nWorld", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.read_text(encoding="utf-8").startswith(r"\section{Hello}")
    assert "deprecated" not in result.stderr


def test_cli_convert_file_deprecated_out_alias(tmp_path):
    """
    Test that the former `--out` name still writes the file and warns on stderr.
    """
    input_file = tmp_path / "input.md"
    output_file = tmp_path / "output.tex"
    input_file.write_text("# Hello\n\nWorld", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file), "--out", str(output_file)])
    assert result.exit_code == 0
    assert output_file.read_text(encoding="utf-8").startswith(r"\section{Hello}")
    assert "--out is deprecated; use --output" in result.stderr


def test_cli_convert_file_rejects_both_output_names(tmp_path):
    """
    Test that giving both `--output` and the deprecated `--out` is a usage error.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    result = runner.invoke(
        app, ["convert-file", str(input_file), "--output", "a.tex", "--out", "b.tex"]
    )
    assert result.exit_code == 2


def test_cli_convert_file_help_hides_out_alias():
    """
    Test that the help lists `--output` and hides the deprecated `--out`.
    """
    result = runner.invoke(app, ["convert-file", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.stdout
    assert "--out " not in result.stdout
