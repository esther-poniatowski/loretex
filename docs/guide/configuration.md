# Configuration

## Overview

Loretex reads conversion rules from the `conversion` block of a YAML spec file.
Defaults are defined in the Python dataclass `ConversionConfig`
(`src/loretex/conversion/config.py`). Spec-level values override those defaults.

The `conversion` block contains 15 sub-sections, each controlling one aspect of the
Markdown-to-LaTeX pipeline. All sub-sections and keys are optional; omitted keys
fall back to built-in defaults.

```yaml
conversion:
  headings:
    anchor_level: 1
  parsing:
    strip_yaml_front_matter: true
  math:
    block_style: brackets
```

---

## `headings`

Controls how Markdown heading levels map to LaTeX section commands.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `anchor_level` | `int` | `1` | Markdown heading level mapped to `\section{}`. |
| `commands` | `map[int, str]` | `{1: section, 2: subsection, 3: subsubsection, 4: paragraph}` | Mapping from *relative* heading level to LaTeX command name. |
| `fallback_command` | `str` | `"paragraph"` | LaTeX command for heading levels beyond the `commands` map. |

A heading at `anchor_level` receives relative level 1 and maps to `commands[1]`
(default `\section{}`). Each deeper level increments the relative level.

```yaml
conversion:
  headings:
    anchor_level: 2
    commands:
      1: chapter
      2: section
      3: subsection
    fallback_command: subsubsection
```

---

## `inline`

Controls inline formatting: bold, italic, code, line breaks, math, custom markers,
and character handling.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `bold_command` | `str` | `"textbf"` | LaTeX command for bold text. |
| `italic_command` | `str` | `"textit"` | LaTeX command for italic text. |
| `code_command` | `str` | `"texttt"` | LaTeX command for inline code. |
| `line_break_command` | `str` | `"newline"` | LaTeX command for hard line breaks. |
| `inline_math_template` | `str` | `"${content}$"` | Template wrapping inline math. |
| `custom_markers` | `map[str, str]` | `{"==": "\\textbf{{{text}}}"}` | Map from Markdown marker to LaTeX template. `{text}` is replaced with the marked content. |
| `texttt_escape_map` | `map[str, str]` | *(see below)* | Character escape sequences inside `\texttt{}`. |
| `character_normalization` | `list[list[str, str]]` | *(see below)* | Pairs `[source_char, replacement]` applied globally to output text. |

Default `texttt_escape_map` entries:

| Character | Replacement |
| --------- | ----------- |
| `\` | `\textbackslash{}` |
| `{` | `\{` |
| `}` | `\}` |
| `#` | `\#` |
| `$` | `\$` |
| `%` | `\%` |
| `&` | `\&` |
| `_` | `\_` |
| `~` | `\textasciitilde{}` |
| `^` | `\textasciicircum{}` |

Default `character_normalization` entries normalize typographic Unicode characters
(right single quotation mark, en-dash, ligatures) into LaTeX-safe equivalents.

```yaml
conversion:
  inline:
    bold_command: textbf
    custom_markers:
      "==": "\\textbf{{{text}}}"
    inline_math_template: "${content}$"
```

---

## `links`

Controls how Markdown links map to LaTeX commands.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `external_link_template` | `str` | `"\\href{url}{text}"` | Template for `[text](url)` links. |
| `url_only_template` | `str` | `"\\url{url}"` | Template for bare-URL links `[url](url)`. |
| `autolink_template` | `str` | `"\\url{url}"` | Template for autolinks `<url>`. |
| `internal_ref_template` | `str` | `"\\ref{{{label}}}"` | Template for `[text](#anchor)` links. |

All templates use `{url}`, `{text}`, or `{label}` as placeholders.

```yaml
conversion:
  links:
    external_link_template: "\\href{url}{text}"
    internal_ref_template: "\\ref{{{label}}}"
```

---

## `citations`

Controls BibTeX citation rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `cite_template` | `str` | `"\\cite{{{keys}}}"` | Template for `[@key]` citations. `{keys}` expands to comma-separated cite keys. |
| `cite_with_locator_template` | `str` | `"\\cite[{locator}]{{{keys}}}"` | Template for `[@key, p. 12]` citations. `{locator}` expands to the page/locator string. |
| `separator` | `str` | `","` | Delimiter joining multiple keys inside one `\cite`. |
| `multi_cite_separator` | `str` | `" "` | Separator between independently grouped citations. |

```yaml
conversion:
  citations:
    cite_template: "\\cite{{{keys}}}"
    cite_with_locator_template: "\\cite[{locator}]{{{keys}}}"
```

---

## `footnotes`

Controls footnote rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `footnote_template` | `str` | `"\\footnote{{{text}}}"` | Template for `[^id]` footnotes. `{text}` expands to the footnote body. |

Footnote definitions follow standard Markdown syntax:

```markdown
Text with footnote.[^1]
[^1]: Footnote body text.
```

---

## `images`

Controls image conversion to LaTeX figure environments.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `path_prefix` | `str` | `"../figures-pdfs"` | Directory prefix prepended to image filenames. |
| `path_suffix` | `str` | `".pdf"` | Extension appended to image filenames. |
| `width_unit` | `str` | `"\\htmlpx"` | LaTeX unit for width values. |
| `include_command` | `str` | `"\\includegraphics"` | LaTeX command for including images. |
| `block_template` | `str` | *(center environment)* | Full LaTeX block template. Placeholders: `{include_command}`, `{width}`, `{unit}`, `{path_prefix}`, `{source}`, `{path_suffix}`. |
| `base_dir` | `str \| null` | `null` | Base directory for resolving image paths when `validate_paths` is enabled. |
| `validate_paths` | `bool` | `false` | Emit a warning when referenced image files do not exist on disk. |

```yaml
conversion:
  images:
    path_prefix: ./figures
    path_suffix: .pdf
    validate_paths: true
    base_dir: .
```

---

## `lists`

Controls list environment names.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `unordered_environment` | `str` | `"itemize"` | LaTeX environment for unordered lists. |
| `ordered_environment` | `str` | `"enumerate"` | LaTeX environment for ordered lists. |

Alias: `list` is accepted as an alternative key name for `lists`.

---

## `code_blocks`

Controls fenced code block rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `environment` | `str` | `"lstlisting"` | LaTeX environment wrapping code blocks. |
| `options_template` | `str \| null` | `null` | Optional template for environment options. `{language}` is replaced with the fence language tag. |

Alias: `code-blocks` is accepted as an alternative key name for `code_blocks`.

```yaml
conversion:
  code_blocks:
    environment: lstlisting
    options_template: "language={language}"
```

---

## `horizontal_rule`

Controls thematic-break rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `template` | `str` | `"\\hrule"` | LaTeX command emitted for `---` rules. |

A plain string value (instead of a mapping) is also accepted:

```yaml
conversion:
  horizontal_rule: "\\hrule"
```

---

## `callouts`

Controls conversion of Markdown blockquote callouts (`> [!type]`) to LaTeX
environments.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `environment_map` | `map[str, str]` | `{}` | Explicit mapping from callout type to LaTeX environment name. |
| `default_environment_template` | `str` | `"{type}box"` | Fallback template for unmapped types. `{type}` expands to the normalized callout type. |
| `title_template` | `str \| null` | `"[{title}]"` | Template for the optional argument passed to the environment. Set to `null` to suppress titles. |
| `type_normalization` | `str` | `"lower"` | Case normalization for callout types: `"lower"`, `"upper"`, or `"none"`. |

```yaml
conversion:
  callouts:
    environment_map:
      note: notebox
      warning: warningbox
    default_environment_template: "{type}box"
    title_template: "[{title}]"
```

---

## `tables`

Controls table rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `environment` | `str` | `"tabular"` | LaTeX environment for tables. |
| `include_hlines` | `bool` | `true` | Insert `\hline` between rows. |
| `multicolumn_align` | `str` | `"c"` | Alignment for `\multicolumn{}` cells. |
| `multirow_command` | `str` | `"multirow"` | LaTeX command for row-spanning cells. |

Column and row spans use inline markers:

```markdown
| A | B | C |
|---|---|---|
| Span{col=2} | X |
```

---

## `parsing`

Controls pre-conversion parsing behavior.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `strip_yaml_front_matter` | `bool` | `false` | Remove YAML front matter (`---` delimited) before conversion. |

---

## `math`

Controls math block rendering.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `block_style` | `str` | `"dollars"` | Display-math delimiter style: `"dollars"` (`$$...$$`) or `"brackets"` (`\[...\]`). |

```yaml
conversion:
  math:
    block_style: brackets
```

---

## `labels`

Controls automatic heading labels and cross-reference generation.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `auto_label_headings` | `bool` | `false` | Emit a `\label{}` after each heading. |
| `label_template` | `str` | `"\\label{{{label}}}"` | LaTeX template for labels. |
| `label_prefix` | `str` | `""` | Prefix prepended to generated label strings. |
| `label_separator` | `str` | `"-"` | Separator between words in label strings. |

```yaml
conversion:
  labels:
    auto_label_headings: true
    label_prefix: sec
    label_separator: "-"
```

A Markdown link target like `[see](#some-section)` becomes `\ref{some-section}`.

---

## `wiki_links`

Controls Obsidian-style wiki-link conversion.

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `link_template` | `str` | `"\\ref{{{label}}}"` | LaTeX template for `[[Target]]` links. |
| `alias_template` | `str` | `"\\ref{{{label}}}"` | LaTeX template for `[[Target\|alias]]` links. |
| `label_separator` | `str` | `"-"` | Separator between words when generating labels from note names. |

```markdown
See [[My Note]] or [[My Note|alias]].
```

---

## Spec-Level Font Settings

Three font keys sit at the spec top level (outside `conversion`) and affect
template assembly:

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `document_font` | `str` | `"\\renewcommand{\\familydefault}{\\sfdefault}"` | LaTeX command setting the default document font. |
| `callout_title_font` | `str` | `"\\sffamily\\bfseries"` | LaTeX font command for callout title text. |
| `callout_body_font` | `str` | `"\\sffamily"` | LaTeX font command for callout body text. |

```yaml
document_font: "\\renewcommand{\\familydefault}{\\sfdefault}"
callout_title_font: "\\sffamily\\bfseries"
callout_body_font: "\\sffamily"
```

Loretex ships a default callouts style file and icons under `loretex/latex/`.
The `loretex-callouts.sty` file and the `icons/` folder must be available to LaTeX
at compile time (e.g., alongside `main.tex` or on the LaTeX search path).
