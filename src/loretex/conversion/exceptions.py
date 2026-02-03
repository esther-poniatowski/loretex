"""Custom exception hierarchy for loretex conversion errors."""

from __future__ import annotations

from typing import Any


class LoretexError(Exception):
    """Base exception for loretex errors.

    Parameters
    ----------
    message : str
        Human-readable error description.
    **context : Any
        Additional context about the error (line number, content, etc.).

    Attributes
    ----------
    context : dict[str, Any]
        Additional context passed to the exception.
    """

    exit_code: int = 1

    def __init__(self, message: str, **context: Any) -> None:
        self.context = context
        super().__init__(message)


class ConversionError(LoretexError):
    """Raised when conversion fails."""


class ParsingError(ConversionError):
    """Raised when parsing encounters invalid Markdown syntax.

    Parameters
    ----------
    message : str
        Description of the parsing failure.
    line : int, optional
        Line number where the error occurred.
    content : str, optional
        The problematic content.
    """

    exit_code = 2


class InvalidCodeFenceError(ParsingError):
    """Raised when a code fence is malformed."""

    def __init__(self, line: int, content: str) -> None:
        super().__init__(
            f"Invalid code fence at line {line}: {content!r}",
            line=line,
            content=content,
        )


class InvalidCalloutError(ParsingError):
    """Raised when a callout header is malformed."""

    def __init__(self, line: int, content: str) -> None:
        super().__init__(
            f"Invalid callout header at line {line}: {content!r}",
            line=line,
            content=content,
        )


class InvalidHeadingError(ParsingError):
    """Raised when a heading line is malformed."""

    def __init__(self, line: int, content: str) -> None:
        super().__init__(
            f"Invalid heading at line {line}: {content!r}",
            line=line,
            content=content,
        )


class InvalidListError(ParsingError):
    """Raised when a list structure is malformed."""

    def __init__(self, line: int, content: str) -> None:
        super().__init__(
            f"Invalid list item at line {line}: {content!r}",
            line=line,
            content=content,
        )


class InvalidImageError(ParsingError):
    """Raised when an image tag is malformed."""

    def __init__(self, line: int, content: str) -> None:
        super().__init__(
            f"Invalid image tag at line {line}: {content!r}",
            line=line,
            content=content,
        )
