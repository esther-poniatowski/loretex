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


def test_cli_convert_file_rejects_the_retired_out_option(tmp_path):
    """
    Test that the retired `--out` name of `--output` is rejected as an unknown option.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file), "--out", str(tmp_path / "o.tex")])
    assert result.exit_code == 2
    assert "No such option" in result.output
    assert not (tmp_path / "o.tex").exists()


def test_cli_convert_file_help_lists_output_only():
    """
    Test that the help lists `--output` and not the retired `--out`.
    """
    result = runner.invoke(app, ["convert-file", "--help"])
    assert result.exit_code == 0
    assert "--output" in result.stdout
    assert "--out " not in result.stdout


def test_cli_convert_file_refuses_to_overwrite_its_input(tmp_path):
    """
    Test that an output naming the input Markdown is refused without `--force`, naming the file.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file), "--output", str(input_file)])
    assert result.exit_code == 2
    assert str(input_file) in result.stderr
    assert input_file.read_text(encoding="utf-8") == "# Hello"

    result = runner.invoke(
        app, ["convert-file", str(input_file), "--output", str(input_file), "--force"]
    )
    assert result.exit_code == 0
    assert input_file.read_text(encoding="utf-8").startswith(r"\section{Hello}")


def test_cli_convert_file_refuses_to_overwrite_its_config(tmp_path):
    """
    Test that an output naming the conversion config is refused without `--force`.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    config = tmp_path / "rules.yml"
    config.write_text("{}\n", encoding="utf-8")
    result = runner.invoke(
        app, ["convert-file", str(input_file), "--config", str(config), "--output", str(config)]
    )
    assert result.exit_code == 2
    assert config.read_text(encoding="utf-8") == "{}\n"


def test_cli_convert_file_overwrites_a_derived_output(tmp_path):
    """
    Test that an existing `.tex` output, which loretex derives, is overwritten without `--force`.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    output_file = tmp_path / "input.tex"
    output_file.write_text("stale", encoding="utf-8")
    result = runner.invoke(app, ["convert-file", str(input_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.read_text(encoding="utf-8").startswith(r"\section{Hello}")


def test_cli_absent_config_or_spec_is_a_usage_error(tmp_path):
    """
    Test that a file named by `--config` or `--spec` and absent stops with status 2.
    """
    input_file = tmp_path / "input.md"
    input_file.write_text("# Hello", encoding="utf-8")
    result = runner.invoke(
        app, ["convert-file", str(input_file), "--config", str(tmp_path / "absent.yml")]
    )
    assert result.exit_code == 2
    result = runner.invoke(app, ["convert", "--spec", str(tmp_path / "absent.yml")])
    assert result.exit_code == 2


def test_cli_spec_paths_are_relative_to_the_spec_folder(tmp_path, monkeypatch):
    """
    Test that the paths written in a spec resolve from its folder, whatever the current folder.
    """
    md = tmp_path / "doc" / "md"
    md.mkdir(parents=True)
    (md / "intro.md").write_text("# Intro", encoding="utf-8")
    spec = md / "loretex.yml"
    spec.write_text("output_dir: ../tex\nchapters:\n  - file: intro.md\n", encoding="utf-8")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    result = runner.invoke(app, ["convert", "--spec", str(spec)])
    assert result.exit_code == 0
    assert (tmp_path / "doc" / "tex" / "intro.tex").is_file()


def test_cli_convert_refuses_an_output_on_a_chapter_source(tmp_path):
    """
    Test that a spec whose output names a chapter source is refused, and writes nothing.
    """
    (tmp_path / "intro.md").write_text("# Intro", encoding="utf-8")
    (tmp_path / "other.md").write_text("# Other", encoding="utf-8")
    spec = tmp_path / "loretex.yml"
    spec.write_text(
        "output_dir: .\nchapters:\n  - file: other.md\n  - file: intro.md\n    output: other.md\n",
        encoding="utf-8",
    )
    result = runner.invoke(app, ["convert", "--spec", str(spec)])
    assert result.exit_code == 2
    assert str(tmp_path / "other.md") in result.stderr
    assert (tmp_path / "other.md").read_text(encoding="utf-8") == "# Other"
    assert not (tmp_path / "intro.tex").exists()


def test_cli_invalid_spec_is_a_usage_error(tmp_path):
    """
    Test that a spec failing validation stops with status 2 and a message, not a traceback.
    """
    spec = tmp_path / "loretex.yml"
    spec.write_text("chapters: [{nofile: x}]\n", encoding="utf-8")
    result = runner.invoke(app, ["convert", "--spec", str(spec)])
    assert result.exit_code == 2
    assert "loretex: error:" in result.stderr
