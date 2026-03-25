from pathlib import Path

import pytest

from loretex.api import convert_spec
from loretex.config.exceptions import SpecValidationError
from loretex.conversion import ConversionConfig, InvalidCodeFenceError, MarkdownParser, TransformRegistry


def test_conversion_config_rejects_unknown_keys() -> None:
    with pytest.raises(ValueError, match="Unknown conversion key"):
        ConversionConfig.from_dict({"unknown_section": {"value": 1}})


def test_markdown_parser_rejects_unterminated_code_fence() -> None:
    parser = MarkdownParser()
    with pytest.raises(InvalidCodeFenceError):
        parser.parse("```python\nprint('hello')\n")


def test_convert_spec_preserves_relative_chapter_layout(tmp_path: Path) -> None:
    template = tmp_path / "main.tex"
    template.write_text("{{content}}", encoding="utf-8")
    chapters_dir = tmp_path / "chapters"
    nested_dir = chapters_dir / "part1"
    nested_dir.mkdir(parents=True)
    chapter_md = nested_dir / "intro.md"
    chapter_md.write_text("# Intro", encoding="utf-8")

    spec = tmp_path / "spec.yml"
    spec.write_text(
        "\n".join(
            [
                "output_dir: ./tex",
                "template: ./main.tex",
                "main_output: main.tex",
                "chapters:",
                "  - file: chapters/part1/intro.md",
            ]
        ),
        encoding="utf-8",
    )

    result = convert_spec(spec)

    expected_output = tmp_path / "tex" / "chapters" / "part1" / "intro.tex"
    assert expected_output.exists()
    assert result.chapter_outputs == [expected_output]
    main_text = (tmp_path / "tex" / "main.tex").read_text(encoding="utf-8")
    assert "\\input{chapters/part1/intro.tex}" in main_text


def test_spec_validation_rejects_unknown_chapter_keys(tmp_path: Path) -> None:
    spec = {"chapters": [{"file": "chapter.md", "mystery": True}]}
    with pytest.raises(SpecValidationError, match="Unknown chapter key"):
        convert_spec(spec)


def test_converter_uses_explicit_transform_registry() -> None:
    registry = TransformRegistry()

    def add_notice(doc):
        from loretex.conversion import Document, Paragraph

        return Document(children=[Paragraph("NOTICE")] + doc.children)

    registry.register("notice", add_notice)
    converter = MarkdownToLaTeXConverter(transform_names=["notice"], transform_registry=registry)
    latex = converter.convert_string("# Title")
    assert "NOTICE" in latex
