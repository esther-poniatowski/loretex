"""Contract tests for configurable Markdown ports."""

from __future__ import annotations

from pathlib import Path
import stat

import pytest
import yaml
from typer.testing import CliRunner

from loretex.api import convert_spec
from loretex.cli import app
from loretex.config.exceptions import SpecValidationError
from loretex.conversion import (
    ConversionConfig,
    ConversionError,
    InvalidMathBlockError,
)


def _write_spec(path: Path, data: dict) -> Path:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_configurable_port_renders_every_declared_output_deterministically(
    tmp_path: Path,
) -> None:
    source = tmp_path / "abstract.md"
    source.write_text(
        """---
role: section
---
# A **structured** title

## Abstract

See @eq:fixed, @fig:all, @sec:method and @tab:cases [@Smith2020; @Jones2021].

$$
x = 1
$$ {#eq:fixed}

```latex
\\input{figure/_figure}
```

## Method

Body.
""",
        encoding="utf-8",
    )
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {
            "output_dir": "out",
            "conversion": {
                "parsing": {"strip_yaml_front_matter": True},
                "headings": {
                    "emit_first": False,
                    "environments": {"Abstract": "abstract"},
                },
                "code_blocks": {"passthrough_languages": ["latex"]},
                "cross_references": {
                    "prefixes": ["eq", "fig", "sec", "tab"],
                    "template": "\\ref{{{label}}}",
                },
                "citations": {"cite_template": "\\citep{{{keys}}}"},
            },
            "chapters": [
                {
                    "file": "abstract.md",
                    "output": "abstract.tex",
                    "title": {
                        "output": "title.tex",
                        "template": "\\title{{{title}}}\n",
                    },
                }
            ],
        },
    )

    first = convert_spec(spec)
    body_path = tmp_path / "out" / "abstract.tex"
    title_path = tmp_path / "out" / "title.tex"
    first_body = body_path.read_bytes()
    first_title = title_path.read_bytes()
    second = convert_spec(spec)

    body = first_body.decode()
    assert first.chapter_outputs == [body_path]
    assert first.auxiliary_outputs == [title_path]
    assert second == first
    assert body_path.read_bytes() == first_body
    assert title_path.read_bytes() == first_title
    assert title_path.read_text(encoding="utf-8") == (
        "\\title{A \\textbf{structured} title}\n"
    )
    assert "\\section{A" not in body
    assert "\\begin{abstract}" in body
    assert "\\end{abstract}\n\n\\input{figure/_figure}" in body
    assert "\\begin{equation}\\label{eq:fixed}" in body
    for label in ("eq:fixed", "fig:all", "sec:method", "tab:cases"):
        assert f"\\ref{{{label}}}" in body
    assert "\\citep{Smith2020,Jones2021}" in body


def test_later_conversion_failure_preserves_previous_outputs(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_text("# Good\n\nAccepted.\n", encoding="utf-8")
    bad.write_text("# Bad\n\n$$\nunclosed\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    good_output = output_dir / "good.tex"
    bad_output = output_dir / "bad.tex"
    good_output.write_text("accepted good", encoding="utf-8")
    bad_output.write_text("accepted bad", encoding="utf-8")
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {
            "output_dir": "out",
            "chapters": [
                {"file": "good.md", "output": "good.tex"},
                {"file": "bad.md", "output": "bad.tex"},
            ],
        },
    )

    with pytest.raises(InvalidMathBlockError):
        convert_spec(spec)

    assert good_output.read_text(encoding="utf-8") == "accepted good"
    assert bad_output.read_text(encoding="utf-8") == "accepted bad"


def test_title_rendering_failure_preserves_previous_outputs(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Title\n\nBody.\n", encoding="utf-8")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    body_output = output_dir / "body.tex"
    title_output = output_dir / "title.tex"
    body_output.write_text("accepted body", encoding="utf-8")
    title_output.write_text("accepted title", encoding="utf-8")
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {
            "output_dir": "out",
            "chapters": [
                {
                    "file": "source.md",
                    "output": "body.tex",
                    "title": {
                        "output": "title.tex",
                        "template": "{title} {",
                    },
                }
            ],
        },
    )

    with pytest.raises(ConversionError, match="invalid title template"):
        convert_spec(spec)

    assert body_output.read_text(encoding="utf-8") == "accepted body"
    assert title_output.read_text(encoding="utf-8") == "accepted title"


def test_duplicate_declared_outputs_fail_before_writing(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Title\n\nBody.\n", encoding="utf-8")
    target = tmp_path / "out" / "same.tex"
    target.parent.mkdir()
    target.write_text("accepted", encoding="utf-8")
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {
            "output_dir": "out",
            "chapters": [
                {
                    "file": "source.md",
                    "output": "same.tex",
                    "title": {
                        "output": "same.tex",
                        "template": "\\title{{{title}}}\n",
                    },
                }
            ],
        },
    )

    with pytest.raises(ConversionError, match="duplicate output path"):
        convert_spec(spec)

    assert target.read_text(encoding="utf-8") == "accepted"


def test_cli_resolves_paths_from_the_specification_directory(tmp_path: Path) -> None:
    source = tmp_path / "chapter.md"
    source.write_text("# Relative\n\nBody.\n", encoding="utf-8")
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {"output_dir": "out", "chapters": [{"file": "chapter.md"}]},
    )

    result = CliRunner().invoke(app, ["convert", "--spec", str(spec)])

    assert result.exit_code == 0
    assert (tmp_path / "out" / "chapter.tex").exists()


def test_unknown_title_field_is_rejected(tmp_path: Path) -> None:
    spec = {
        "chapters": [
            {
                "file": "chapter.md",
                "title": {
                    "output": "title.tex",
                    "template": "{title}",
                    "mystery": True,
                },
            }
        ]
    }

    with pytest.raises(SpecValidationError, match="Unknown chapter title key"):
        convert_spec(spec)


@pytest.mark.parametrize(
    "conversion",
    [
        {"headings": {"mystery": True}},
        {"cross_references": {"mystery": True}},
        {"code_blocks": {"mystery": True}},
        {"math": {"mystery": True}},
    ],
)
def test_unknown_fields_in_extended_conversion_sections_are_rejected(
    conversion: dict,
) -> None:
    with pytest.raises(ValueError, match="Unknown .* key"):
        ConversionConfig.from_dict(conversion)


def test_replacement_preserves_existing_output_permissions(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text("# Title\n", encoding="utf-8")
    target = tmp_path / "out" / "source.tex"
    target.parent.mkdir()
    target.write_text("accepted", encoding="utf-8")
    target.chmod(0o640)
    spec = _write_spec(
        tmp_path / "loretex.yml",
        {
            "output_dir": "out",
            "chapters": [{"file": "source.md", "output": "source.tex"}],
        },
    )

    convert_spec(spec)

    assert stat.S_IMODE(target.stat().st_mode) == 0o640
