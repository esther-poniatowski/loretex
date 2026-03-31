# Usage

Loretex converts Markdown notes into LaTeX through two modes: single-file conversion
and spec-based multi-chapter builds. Both modes are accessible from the CLI and
the Python API.

For the exhaustive list of commands and options, refer to
[CLI Reference](cli-reference.md). For conversion rules and formatting options, refer
to [Configuration](configuration.md).

## Single-File Conversion

Convert one Markdown file to LaTeX (output to stdout by default):

```sh
loretex convert-file notes.md
```

Write the result to a file:

```sh
loretex convert-file notes.md --out notes.tex
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

## Template Assembly

Adding `template` and `main_output` fields to the spec generates a `main.tex` file
with `\input{...}` statements for each chapter:

```yaml
output_dir: ./tex
template: ./templates/main.tex
main_output: ./tex/main.tex
chapters:
  - file: notes/intro.md
```

The template must contain a `{{content}}` placeholder where inputs are inserted.
Additional placeholders — `{{title}}`, `{{author}}`, `{{date}}`, `{{bibliography}}` —
and custom variables via `template_vars` are also supported.

An example template is available at `config/template.tex`.

## Per-Chapter Overrides

Conversion rules can be specified globally and overridden per chapter:

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

User-defined transforms register through the plugin API and apply during
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

## Python API

The same functionality is accessible programmatically:

```python
from loretex import convert_string, convert_file, convert_spec

latex = convert_string("# Title\n\nSome **bold** text.")
```

## Next Steps

- [CLI Reference](cli-reference.md) — Full command registry and options.
- [Configuration](configuration.md) — Conversion rules, callouts, labels, citations.
