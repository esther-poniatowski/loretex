"""Tests for Markdown link conversion."""

from loretex.conversion import ConversionConfig, MarkdownToLaTeXConverter


def test_markdown_link_converts_to_href() -> None:
    """Convert [text](url) to \\href."""
    converter = MarkdownToLaTeXConverter()
    markdown = "See [Docs](https://example.com)."
    latex = converter.convert_string(markdown)
    assert r"\href{https://example.com}{Docs}" in latex


def test_markdown_link_same_text_uses_url_template() -> None:
    """If link text equals URL, use url_only_template."""
    config = ConversionConfig.from_dict(
        {
            "links": {
                "url_only_template": r"\\url{url}",
                "external_link_template": r"\\href{url}{text}",
            }
        }
    )
    converter = MarkdownToLaTeXConverter(config=config)
    markdown = "[https://example.com](https://example.com)"
    latex = converter.convert_string(markdown)
    assert r"\url{https://example.com}" in latex


def test_autolink_converts_to_url() -> None:
    """Convert <https://...> to \\url."""
    converter = MarkdownToLaTeXConverter()
    markdown = "Visit <https://example.com>."
    latex = converter.convert_string(markdown)
    assert r"\url{https://example.com}" in latex
