# Usage

Loretex converts Markdown notes into LaTeX through two modes: single-file conversion
and spec-based multi-chapter builds. The CLI and the Python API expose the same
functionality.

For the full list of commands and options, see
[CLI Reference](cli-reference.md). For conversion rules and formatting options, see
[Configuration](configuration.md).

## Single-File Conversion

Convert one Markdown file to LaTeX (output to stdout by default):

```sh
loretex convert-file notes.md
```

Write the result to a file:

```sh
loretex convert-file notes.md --out notes.tex
```

Pass a YAML config and set the anchor level:

```sh
loretex convert-file notes.md --config rules.yaml --anchor 2
```

## Spec-Based Conversion

A YAML spec defines the document structure, input/output paths, and conversion
parameters for multi-chapter builds:

```yaml
output_dir: ./tex
anchor_level: 1
chapters:
  - file: notes/intro.md
  - file: notes/chapter1.md
```

```sh
loretex convert --spec spec.yml
```

### Spec-Level Keys

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `output_dir` | `str` | `"./tex"` | Directory for generated `.tex` files. |
| `anchor_level` | `int` | `1` | Default heading level mapped to `\section{}`. |
| `chapters` | `list` | `[]` | List of chapter entries (see below). |
| `conversion` | `map` | `{}` | Global conversion rules. Alias: `rules`. See [Configuration](configuration.md). |
| `template` | `str` | none | Path to a LaTeX template file containing the `{{content}}` placeholder. |
| `main_output` | `str` | none | Path for the assembled main `.tex` file. Defaults to `<output_dir>/main.tex` when `template` is set. |
| `title` | `str` | none | Document title, available in templates as `{{title}}`. |
| `author` | `str` | none | Document author, available in templates as `{{author}}`. |
| `date` | `str` | none | Document date, available in templates as `{{date}}`. |
| `bibliography` | `str \| list` | none | Bibliography snippet inserted into templates as `{{bibliography}}`. Accepts a string or a list of strings (joined by newlines). |
| `template_vars` | `map` | `{}` | Extra key-value pairs available as `{{key}}` placeholders in templates. |
| `document_font` | `str` | `"\\renewcommand{\\familydefault}{\\sfdefault}"` | LaTeX command setting the default document font. |
| `callout_title_font` | `str` | `"\\sffamily\\bfseries"` | LaTeX font command for callout titles. |
| `callout_body_font` | `str` | `"\\sffamily"` | LaTeX font command for callout body text. |

### Chapter Entry Keys

Each entry in `chapters` accepts:

| Key | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `file` | `str` | Required | Path to the source Markdown file. |
| `anchor_level` | `int` | spec-level `anchor_level` | Heading level mapped to `\section{}` for this chapter. |
| `output` | `str` | derived from `file` | Custom output path relative to `output_dir`. When omitted, the output filename mirrors the source path with a `.tex` extension. |
| `conversion` | `map` | `{}` | Per-chapter conversion rule overrides (same schema as the spec-level `conversion` block). Aliases: `options`, `rules`. |

```yaml
chapters:
  - file: notes/intro.md
    anchor_level: 2
    output: intro.tex
    conversion:
      headings:
        anchor_level: 2
      callouts:
        environment_map:
          note: notebox
```

## Template Assembly

Adding `template` and `main_output` to the spec generates a `main.tex` file
with `\input{...}` statements for each chapter:

```yaml
output_dir: ./tex
template: ./templates/main.tex
main_output: ./tex/main.tex
title: "Lecture Notes"
author: "J. Doe"
date: "2025"
bibliography: "\\bibliography{refs}"
chapters:
  - file: notes/intro.md
```

The template must contain a `{{content}}` placeholder where `\input` statements
are inserted. Additional built-in placeholders: `{{title}}`, `{{author}}`,
`{{date}}`, `{{bibliography}}`, `{{document_font}}`, `{{callout_title_font}}`,
`{{callout_body_font}}`. Custom placeholders defined in `template_vars` are also
replaced.

An example template ships at `config/template.tex`.

## Per-Chapter Overrides

Conversion rules set at the spec level apply globally. Per-chapter `conversion`
blocks override specific keys without replacing the entire configuration:

```yaml
conversion:
  headings:
    anchor_level: 1
  callouts:
    environment_map:
      note: notebox
chapters:
  - file: notes/intro.md
    conversion:
      headings:
        anchor_level: 2
```

## Custom AST Transforms

User-defined transforms register in the transform registry and apply during
conversion:

```python
from loretex.conversion import (
    Document,
    Paragraph,
    register_transform,
    MarkdownToLaTeXConverter,
)

def add_notice(doc: Document) -> Document:
    return Document(children=[Paragraph("NOTICE")] + doc.children)

register_transform("notice", add_notice)
converter = MarkdownToLaTeXConverter(transform_names=["notice"])
latex = converter.convert_string("# Title")
```

A transform is any callable that accepts a `Document` and returns a new `Document`.
The `register_transform` function stores the callable by name in the global
`TransformRegistry`. The converter resolves names to callables at construction time.

## Python API

The same conversion functionality is accessible programmatically:

```python
from loretex import convert_string, convert_file, convert_spec

latex = convert_string("# Title\n\nSome **bold** text.")
```

## Next Steps

- [CLI Reference](cli-reference.md) -- Full command list and options.
- [Configuration](configuration.md) -- Conversion rules, callouts, labels, citations.
