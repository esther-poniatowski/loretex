"""Tests for the ordered substitutions applied to the converted LaTeX."""

from __future__ import annotations

import pytest

from loretex.conversion import ConversionConfig, MarkdownToLaTeXConverter


def _converter(substitutions: list[dict[str, str]]) -> MarkdownToLaTeXConverter:
    config = ConversionConfig.from_dict({"substitutions": substitutions})
    return MarkdownToLaTeXConverter(config=config)


def test_substitutions_rewrite_the_converted_latex_in_order() -> None:
    """Apply each substitution to the output of the previous one, after conversion."""
    # Arrange
    converter = _converter(
        [
            {"pattern": r"(?m)^\\textbf\{(.+?)\.\}\s*", "replacement": r"\\lead{\1} "},
            {"pattern": r"\\lead\{Note\}", "replacement": r"\\lead[draft]{Note}"},
        ]
    )

    # Act
    latex = converter.convert_string("**Note.** Some text with **bold** words.")

    # Assert
    assert latex == r"\lead[draft]{Note} Some text with \textbf{bold} words."


def test_chapter_overrides_replace_the_global_substitutions() -> None:
    """A chapter list of substitutions replaces the global list."""
    # Arrange
    converter = _converter([{"pattern": "alpha", "replacement": "beta"}])

    # Act
    overridden = converter.convert_string(
        "alpha gamma",
        {"substitutions": [{"pattern": "gamma", "replacement": "delta"}]},
    )

    # Assert
    assert converter.convert_string("alpha gamma") == "beta gamma"
    assert overridden == "alpha delta"


def test_substitutions_survive_unrelated_overrides() -> None:
    """An override of another section keeps the global substitutions."""
    # Arrange
    converter = _converter([{"pattern": "alpha", "replacement": "beta"}])

    # Act
    latex = converter.convert_string("alpha", {"headings": {"emit_first": True}})

    # Assert
    assert latex == "beta"


@pytest.mark.parametrize(
    ("substitutions", "message"),
    [
        ({"pattern": "a"}, "must be a list"),
        (["a"], "must be a mapping"),
        ([{"pattern": "a"}], "needs string pattern and replacement"),
        ([{"pattern": "(", "replacement": ""}], "invalid pattern"),
        ([{"pattern": "a", "replacement": "b", "flags": "m"}], "Unknown substitutions entry 1 key"),
    ],
)
def test_malformed_substitutions_are_rejected(substitutions: object, message: str) -> None:
    """Reject a malformed list, entry or pattern when the configuration is read."""
    with pytest.raises(ValueError, match=message):
        ConversionConfig.from_dict({"substitutions": substitutions})
