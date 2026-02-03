"""Default constants for the loretex Markdown-to-LaTeX conversion engine."""

from __future__ import annotations

# Indentation constants
TAB_WIDTH: int = 4
"""Number of spaces equivalent to one tab character."""

# Default LaTeX section mapping (relative levels)
DEFAULT_SECTION_COMMANDS: dict[int, str] = {
    1: "section",
    2: "subsection",
    3: "subsubsection",
    4: "paragraph",
}
"""Mapping from relative heading level to LaTeX section command."""

# Character escaping for \texttt
DEFAULT_TEXTTT_ESCAPE_MAP: dict[str, str] = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}
"""Escape sequences for special characters inside \texttt{}."""

# Character normalization for LaTeX output
DEFAULT_CHARACTER_NORMALIZATION: tuple[tuple[str, str], ...] = (
    ("\u2019", "'"),  # RIGHT SINGLE QUOTATION MARK → apostrophe
    ("≤", r"\leq"),
    ("≥", r"\geq"),
    ("œ", "oe"),
    ("–", "-"),
)
"""Replacement pairs for typographic character normalization."""

# Default output paths
DEFAULT_FIGURES_PDF_PATH: str = "../figures-pdfs"
"""Default path prefix for PDF figure includes."""

# Default callout environment template
DEFAULT_CALLOUT_ENV_TEMPLATE: str = "{type}box"
"""Template used to build LaTeX environments from callout types."""

# Default image block template
DEFAULT_IMAGE_BLOCK_TEMPLATE: str = (
    "\\\\begin{{center}}\\n"
    "{include_command}[width={width}{unit}]"
    "{{{path_prefix}/{source}{path_suffix}}}\\n"
    "\\\\end{{center}}"
)
"""Default LaTeX block template for image includes."""
