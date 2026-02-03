# Loretex

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2025)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/loretex)](https://github.com/esther-poniatowski/loretex/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Convert modular Markdown notes into structured LaTeX documents with declarative templates,
customizable styles, and support for complex formatting.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Documentation](#documentation)
- [Support](#support)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

### Motivation

When redacting a complex document, Markdown is frequently used to draft and organize content due to
its simplicity and readability, while LaTeX remains the preferred system for its precise typesetting
and formatting capabilities.

Existing tools for converting Markdown to LaTeX often lack support for complex document structures,
hierarchical organization, and style customizations. As a result, manual adjustments are frequently
required to ensure consistency and correctness in the final output.

### Advantages

This tool provides a configurable pipeline to generate structured LaTeX documents from modular
Markdown notes.

It provides the following benefits:

- **Separation of content and typesetting**: Enables authors to focus on semantic content authoring
  in Markdown, while delegating formatting and compilation to configurable LaTeX templates.
- **Declarative and reproducible document builds**: Eliminates manual editing by specifying the document structure and conversion rules in an external configuration file.
- **Scalability to large projects**: Supports partial builds, hierarchical ordering, and modular
  inclusion of chapters or sections, enabling progressive iteration on multi-stage writing processes.
- **Advanced and customizable formatting**: Converts extended Markdown syntax into LaTeX with fine
  control over rendering behavior.

---

## Features

- [ ] **Modular document structure**: Generate standalone `.tex` files from individual or aggregated
  Markdown notes, producing composable fragments for integration into a `main.tex` master file.

- [ ] **Declarative configurations**: Specify document structure, input and output paths, and
  optional conversion parameters in a static configuration file.

- [ ] **Fine-grained hierarchy mapping**: Map Markdown headings (`#`, `##`, etc) into LaTeX sections
  (`\section{}`, `\subsection{}`, etc) using flexible, note-specific anchoring logic.

- **Formatting transformation**: Convert Markdown formatting into LaTeX equivalents, including:

  - [ ] Emphasis (bold, italics, underlined, strike-through)
  - [ ] Code blocks and inline verbatim
  - [ ] Custom inline markers (e.g., `==TODO: ...==`)
  - [ ] Horizontal rules
  - [ ] Lists and tables
  - [ ] Mathematical expressions (`$...$`, `$$...$$`)
  - [ ] Citations (`[@authorYYYY]`)

- **Link and media resolution**:

  - [ ] Markdown internal links to LaTeX cross-references (`\ref{}`)
  - [ ] Markdown external links into LaTeX URLs (`\url{}`)
  - [ ] Embedded images to graphical elements (`\includegraphics{}`)

- **Customizable admonitions and environments**: Translate Markdown callouts (e.g., > [!NOTE], > [!WARNING], etc.) into LaTeX environments with configurable styling.

- [ ] **Selective exclusions**: Omit specific Markdown content (e.g., YAML front matter) from the conversion output.

- [ ] **Batch or partial builds**: Process full documents or selected subsets of notes for targeted compilation and debugging.

---

## Installation

To install the package and its dependencies, use one of the following methods:

### Using Pip Installs Packages

Install the package from the GitHub repository URL via `pip`:

```bash
pip install git+https://github.com/esther-poniatowski/loretex.git
```

### Using Conda

Install the package from the private channel eresthanaconda:

```bash
conda install loretex -c eresthanaconda
```

### From Source

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/loretex.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd loretex
      conda env create -f environment.yml
      ```

---

## Usage

### Command Line Interface (CLI)

To display the list of available commands and options:

```sh
loretex --help
```

#### Simple Conversion (Single File)

Convert one Markdown file to LaTeX (output to stdout by default):

```sh
loretex convert-file path/to/input.md
```

Write to a file:

```sh
loretex convert-file path/to/input.md --out path/to/output.tex
```

#### Spec-Based Conversion (Multiple Files)

Use a YAML spec to convert multiple chapters:

```sh
loretex convert --spec path/to/spec.yml
```

#### Template Assembly (Optional)

Add a `template` and `main_output` in the spec to generate a `main.tex` file
with `\\input{...}` statements for each chapter:

```yaml
output_dir: ./tex
template: ./templates/main.tex
main_output: ./tex/main.tex
chapters:
  - file: notes/intro.md
```

Template must include a `{{content}}` placeholder where inputs are inserted.
An example template is available at `config/template.tex`.

Additional placeholders supported: `{{title}}`, `{{author}}`, `{{date}}`, and `{{bibliography}}`.
Title/author/date values are inserted already wrapped in braces for convenience (e.g. `\title{{title}}`).
You can also provide custom placeholders via `template_vars` in the spec.

### Programmatic Usage

To use the package programmatically in Python:

```python
from loretex import convert_markdown_to_latex

latex = convert_markdown_to_latex(\"# Title\\n\\nSome **bold** text.\")
```

---

## Configuration

### Environment Variables

|Variable|Description|Default|Required|
|---|---|---|---|
|`VAR_1`|Description 1|None|Yes|
|`VAR_2`|Description 2|`false`|No|

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

```yaml
var_1: value1
var_2: value2
```

#### Conversion Rules

Conversion rules can be specified in the YAML spec under `conversion` and/or per chapter:

```yaml
output_dir: ./out
anchor_level: 1
    conversion:
      callouts:
        environment_map:
          note: notebox
          warning: warningbox
  code_blocks:
    environment: lstlisting
chapters:
  - file: notes/intro.md
    conversion:
      headings:
        anchor_level: 2
```

##### Internal Links and Labels

Enable automatic labels for headings and internal references:

```yaml
conversion:
  labels:
    auto_label_headings: true
    label_prefix: sec
  links:
    internal_ref_template: "\\ref{{{label}}}"
```

Markdown link targets like `[see](#some-section)` become `\\ref{some-section}`.

##### Footnotes and Wiki Links

Footnotes:

```markdown
Here is a note.[^1]

[^1]: Footnote text.
```

Wiki links:

```markdown
See [[My Note]] or [[My Note|alias]].
```

Both are configurable via `conversion.footnotes` and `conversion.wiki_links`.

##### Citations (With Locators)

```markdown
See [@doe2020, p. 12; @smith2021].
```

The locator will be rendered with `conversion.citations.cite_with_locator_template`.

##### Table Spans (Extension)

You can use `{col=2}` or `{row=2}` at the end of a table cell:

```markdown
| A | B | C |
|---|---|---|
| Span{col=2} | X |
```

##### Custom Transforms

You can register and apply AST transforms programmatically:

```python
from loretex.conversion import MarkdownToLaTeXConverter, register_transform, Document, Paragraph

def add_notice(doc: Document) -> Document:
    return Document(children=[Paragraph("NOTICE")] + doc.children)

register_transform("notice", add_notice)
converter = MarkdownToLaTeXConverter(transform_names=["notice"])
latex = converter.convert_string("# Title")
```

---

## Documentation

- [User Guide](https://esther-poniatowski.github.io/loretex/guide/)
- [API Documentation](https://esther-poniatowski.github.io/loretex/api/)
- [Usage Examples](docs/usage-examples.md)
- [Architecture](docs/architecture.md)
- [Release Checklist](docs/release-checklist.md)

> [!NOTE]
> Documentation can also be browsed locally from the [`docs/`](docs/) directory.

## Architecture & Extension Points

Key modules:

- Conversion engine: `loretex/conversion/` (parser, AST, inline rules, generator).
- Pipeline/assembly: `loretex/pipeline/` (template rendering, main.tex assembly).
- Public API: `loretex/api.py` (simple entry points).
- Spec validation: `loretex/config/validate.py`.

Extension points:

- AST transforms via registry (`register_transform`, `transform_names`).
- Config-driven rules in `config/default.yaml`.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/loretex/issues)

**Email**: `{{ contact@example.com }}`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `{{ contact@example.com }}`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[Library A](link)** - Purpose
- **[Library B](link)** - Purpose

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
