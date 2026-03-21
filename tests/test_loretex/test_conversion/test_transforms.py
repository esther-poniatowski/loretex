"""Tests for transform registry and pipeline."""

from loretex.conversion import (
    Document,
    MarkdownToLaTeXConverter,
    Paragraph,
    register_transform,
)


def test_transform_pipeline_applied() -> None:
    """Apply a transform to prepend a notice paragraph."""
    def add_notice(doc: Document) -> Document:
        return Document(children=[Paragraph("NOTICE")] + doc.children)

    converter = MarkdownToLaTeXConverter(transforms=[add_notice])
    latex = converter.convert_string("# Title")
    assert "NOTICE" in latex


def test_transform_registry_by_name() -> None:
    """Resolve registered transforms by name."""
    def add_notice(doc: Document) -> Document:
        return Document(children=[Paragraph("NOTICE")] + doc.children)

    register_transform("notice-test", add_notice, overwrite=True)
    converter = MarkdownToLaTeXConverter(transform_names=["notice-test"])
    latex = converter.convert_string("# Title")
    assert "NOTICE" in latex
