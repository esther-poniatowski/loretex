"""Tests for template assembly pipeline."""

from pathlib import Path

from loretex.api import convert_spec


def test_convert_spec_with_template(tmp_path: Path) -> None:
    template = tmp_path / "main.tex"
    template.write_text(
        "\\documentclass{article}\n\\begin{document}\n{{content}}\n\\end{document}",
        encoding="utf-8",
    )
    chapter_md = tmp_path / "chapter.md"
    chapter_md.write_text("# Title\n\nBody", encoding="utf-8")

    spec = tmp_path / "spec.yml"
    output_dir = tmp_path / "tex"
    main_output = output_dir / "main.tex"
    spec.write_text(
        "\n".join(
            [
                f"output_dir: {output_dir}",
                f"template: {template}",
                f"main_output: {main_output}",
                "chapters:",
                f"  - file: {chapter_md}",
            ]
        ),
        encoding="utf-8",
    )

    outputs = convert_spec(spec)

    assert (output_dir / "chapter.tex").exists()
    assert main_output.exists()
    main_text = main_output.read_text(encoding="utf-8")
    assert "\\input{chapter.tex}" in main_text
    assert outputs == [output_dir / "chapter.tex"]
