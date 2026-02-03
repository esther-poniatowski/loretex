"""Tests for template variables and bibliography insertion."""

from pathlib import Path

from loretex.api import convert_spec


def test_template_variables_and_bibliography(tmp_path: Path) -> None:
    template = tmp_path / "main.tex"
    template.write_text(
        "\\title{{title}}\n\\author{{author}}\n{{bibliography}}\n{{content}}",
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
                "title: Doc",
                "author: Me",
                "bibliography: \\\\bibliography{refs}",
                "chapters:",
                f"  - file: {chapter_md}",
            ]
        ),
        encoding="utf-8",
    )

    convert_spec(spec)
    content = main_output.read_text(encoding="utf-8")
    assert "\\title{Doc}" in content
    assert "\\author{Me}" in content
    assert "\\bibliography{refs}" in content
