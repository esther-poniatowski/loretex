"""Unit tests for exception classes."""

from __future__ import annotations

from loretex.conversion import (
    InvalidCalloutError,
    InvalidCodeFenceError,
    InvalidHeadingError,
    InvalidImageError,
    InvalidListError,
    LoretexError,
    ParsingError,
)


class TestLoretexError:
    """Tests for base LoretexError."""

    def test_error_stores_message(self) -> None:
        """Error stores the message."""
        # Act
        error = LoretexError("Something went wrong")

        # Assert
        assert str(error) == "Something went wrong"

    def test_error_stores_context(self) -> None:
        """Error stores context kwargs."""
        # Act
        error = LoretexError("Error", line=10, column=5)

        # Assert
        assert error.context == {"line": 10, "column": 5}

    def test_error_has_exit_code(self) -> None:
        """Base error has exit code 1."""
        # Act
        error = LoretexError("Error")

        # Assert
        assert error.exit_code == 1


class TestParsingError:
    """Tests for ParsingError."""

    def test_parsing_error_exit_code(self) -> None:
        """Parsing error has exit code 2."""
        # Act
        error = ParsingError("Parse failed")

        # Assert
        assert error.exit_code == 2

    def test_parsing_error_inherits_from_base(self) -> None:
        """ParsingError inherits from LoretexError."""
        # Act
        error = ParsingError("Error")

        # Assert
        assert isinstance(error, LoretexError)


class TestInvalidCodeFenceError:
    """Tests for InvalidCodeFenceError."""

    def test_message_format(self) -> None:
        """Error message includes line and content."""
        # Act
        error = InvalidCodeFenceError(line=5, content="``invalid")

        # Assert
        assert "line 5" in str(error)
        assert "``invalid" in str(error)

    def test_context_values(self) -> None:
        """Context stores line and content."""
        # Act
        error = InvalidCodeFenceError(line=5, content="``invalid")

        # Assert
        assert error.context["line"] == 5
        assert error.context["content"] == "``invalid"


class TestInvalidCalloutError:
    """Tests for InvalidCalloutError."""

    def test_message_format(self) -> None:
        """Error message includes line and content."""
        # Act
        error = InvalidCalloutError(line=10, content="> [!bad")

        # Assert
        assert "line 10" in str(error)
        assert "> [!bad" in str(error)


class TestInvalidHeadingError:
    """Tests for InvalidHeadingError."""

    def test_message_format(self) -> None:
        """Error message includes line and content."""
        # Act
        error = InvalidHeadingError(line=1, content="##no space")

        # Assert
        assert "line 1" in str(error)
        assert "##no space" in str(error)


class TestInvalidListError:
    """Tests for InvalidListError."""

    def test_message_format(self) -> None:
        """Error message includes line and content."""
        # Act
        error = InvalidListError(line=20, content="- ")

        # Assert
        assert "line 20" in str(error)


class TestInvalidImageError:
    """Tests for InvalidImageError."""

    def test_message_format(self) -> None:
        """Error message includes line and content."""
        # Act
        error = InvalidImageError(line=15, content="<img>")

        # Assert
        assert "line 15" in str(error)
        assert "<img>" in str(error)
