# Loretex

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](#installation)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/loretex)](https://github.com/esther-poniatowski/loretex/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Markdown-to-LaTeX converter that assembles structured documents from modular notes.

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

Markdown is commonly used to draft and organize content for its simplicity, while LaTeX remains
the standard for precise typesetting. Existing converters lack support for complex document
structures, hierarchical ordering, and custom styles, forcing manual adjustments in the final
output.

### Advantages

Loretex converts Markdown notes to LaTeX through a configurable pipeline:

- **Content–typesetting separation**: Authors write in Markdown; LaTeX templates handle
  formatting and compiling.
- **Declarative builds**: An external configuration file specifies document structure and
  conversion rules, eliminating manual editing.
- **Scalable to large projects**: Supports partial builds, hierarchical ordering, and adding
  chapters incrementally.
- **Customizable formatting**: Converts extended Markdown syntax to LaTeX with fine control over
  rendering behavior.

---

## Features

- [x] **Modular document structure**: Generate standalone `.tex` files from individual or aggregated
  Markdown notes, producing composable fragments that integrate into a `main.tex` master file.

- [x] **Declarative configurations**: Specify document structure, input and output paths, and
  optional conversion parameters in a static configuration file.

- [x] **Precise hierarchy mapping**: Map Markdown headings (`#`, `##`, etc) into LaTeX sections
  (`\section{}`, `\subsection{}`, etc) using flexible anchoring logic specific to each note.

- **Formatting transforms**: Convert Markdown formatting into LaTeX equivalents, including:

  - [x] Emphasis (bold, italics)
  - [x] Code blocks and inline verbatim
  - [x] Custom inline markers (e.g., `==TODO: ...==`)
  - [x] Horizontal rules
  - [x] Lists and tables
  - [x] Mathematical expressions (`$...$`, `$$...$$`)
  - [x] Citations (`[@authorYYYY]`)

- **Link and media resolution**:

  - [x] Markdown internal links to LaTeX cross-references (`\ref{}`)
  - [x] Markdown external links into LaTeX URLs (`\url{}`)
  - [x] Embedded images to graphical elements (`\includegraphics{}`)

- [x] **Customizable admonitions and environments**: Translate Markdown callouts (e.g., > [!NOTE], > [!WARNING], etc.) into LaTeX environments with configurable styling.

- [x] **Selective exclusions**: Omit specific Markdown content (e.g., YAML front matter) from the conversion output.

- [x] **Batch or partial builds**: Process full documents or selected subsets of notes to compile and debug specific targets.

---

## Installation

### Using pip

Install from the GitHub repository:

```bash
pip install git+https://github.com/esther-poniatowski/loretex.git
```

### Using conda

Install from the eresthanaconda channel:

```bash
conda install loretex -c eresthanaconda
```

### From Source (Editable)

1. Clone the repository:

      ```bash
      git clone https://github.com/esther-poniatowski/loretex.git
      ```

2. Create a dedicated virtual environment:

      ```bash
      cd loretex
      conda env create -f environment.yml
      ```

3. Activate the environment:

      ```bash
      conda activate loretex
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
Custom placeholders are also supported via `template_vars` in the spec.

### Programmatic Usage

To use the package programmatically in Python:

```python
from loretex import convert_string

latex = convert_string(\"# Title\\n\\nSome **bold** text.\")
```

---

## Configuration

### Configuration File

Configuration options are specified in YAML files located in the `config/` directory or via the
`conversion` section in a spec file.

The canonical configuration schema is provided in [`config/default.yaml`](config/default.yaml).

Example (selected options):

```yaml
conversion:
  parsing:
    strip_yaml_front_matter: true
  math:
    block_style: brackets
  inline:
    inline_math_template: "${content}$"
    custom_markers:
      "==": "\\textbf{{{text}}}"
  horizontal_rule: "\\hrule"
  headings:
    anchor_level: 1
  callouts:
    environment_map:
      note: notebox
```

#### Template Fonts and Callouts

The spec supports font settings at the document level and for callouts:

```yaml
document_font: "\\renewcommand{\\familydefault}{\\sfdefault}"
callout_title_font: "\\sffamily\\bfseries"
callout_body_font: "\\sffamily"
```

These placeholders are expected in the template (see `config/template.tex`).

Loretex ships a default callouts style file and icons under `loretex/latex/`.
Ensure `loretex-callouts.sty` and the `icons/` folder are available to LaTeX at
compile time (for example, by placing them alongside `main.tex` or adding their
location to your LaTeX search path).

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

- [User Guide](docs/usage-examples.md) (coming soon for hosted docs)
- [API Documentation](docs/architecture.md) (coming soon for hosted docs)
- [Usage Examples](docs/usage-examples.md)
- [Architecture](docs/architecture.md)
- [Development Notes](docs/development.md)
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
- Rules driven by `config/default.yaml`.

## Support

**Issues**: [GitHub Issues](https://github.com/esther-poniatowski/loretex/issues)

**Email**: `esther.poniatowski@ens.psl.eu`

---

## Contributing

Please refer to the [contribution guidelines](CONTRIBUTING.md).

---

## Acknowledgments

### Authors & Contributors

**Author**: @esther-poniatowski

**Contact**: `esther.poniatowski@ens.psl.eu`

For academic use, please cite using the GitHub "Cite this repository" feature to
generate a citation in various formats.

Alternatively, refer to the [citation metadata](CITATION.cff).

### Third-Party Dependencies

- **[PyYAML](https://pyyaml.org/)** - YAML configuration parsing.
- **[attrs](https://www.attrs.org/)** - Lightweight data classes and validation helpers.
- **[Typer](https://typer.tiangolo.com/)** - CLI framework.
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting for CLI output.

---

## License

This project is licensed under the terms of the [GNU General Public License v3.0](LICENSE).
