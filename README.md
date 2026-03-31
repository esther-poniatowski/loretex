# Loretex

[![Conda](https://img.shields.io/badge/conda-eresthanaconda--channel-blue)](docs/guide/installation.md)
[![Maintenance](https://img.shields.io/maintenance/yes/2026)]()
[![Last Commit](https://img.shields.io/github/last-commit/esther-poniatowski/loretex)](https://github.com/esther-poniatowski/loretex/commits/main)
[![Python](https://img.shields.io/badge/python-supported-blue)](https://www.python.org/)
[![License: GPL](https://img.shields.io/badge/License-GPL-yellow.svg)](https://opensource.org/licenses/GPL-3.0)

Converts modular Markdown notes into structured LaTeX documents.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## Overview

Loretex converts Markdown notes into LaTeX through a configurable pipeline, bridging
the simplicity of Markdown drafting with the precision of LaTeX typesetting.

### Motivation

Markdown is commonly used to draft and organize content for its simplicity, while LaTeX
remains the standard for precise typesetting. Existing converters lack support for
complex document structures, hierarchical ordering, and custom styles, forcing manual
adjustments in the final output.

### Advantages

- **Content–typesetting separation** — authors write in Markdown; LaTeX templates handle
  formatting and compiling.
- **Declarative builds** — an external YAML spec defines document structure and
  conversion rules, eliminating manual editing.
- **Scalable to large projects** — partial builds, hierarchical ordering, and
  incremental chapter additions are supported natively.
- **Customizable formatting** — extended Markdown syntax converts to LaTeX with fine
  control over rendering behavior.

---

## Features

- [x] **Modular document structure**: Generate standalone `.tex` files from individual
  or aggregated Markdown notes, producing composable fragments that integrate into a
  `main.tex` master file.
- [x] **Declarative configurations**: Define document structure, input/output paths, and
  conversion parameters in a static YAML spec.
- [x] **Precise hierarchy mapping**: Map Markdown headings (`#`, `##`, ...) to LaTeX
  sections (`\section{}`, `\subsection{}`, ...) with flexible anchoring logic.
- [x] **Formatting transforms**: Convert emphasis, code blocks, inline markers
  (`==TODO==`), horizontal rules, lists, tables, math expressions, and citations.
- [x] **Link and media resolution**: Translate internal links to `\ref{}`, external
  links to `\url{}`, and embedded images to `\includegraphics{}`.
- [x] **Customizable admonitions**: Translate Markdown callouts (`> [!NOTE]`,
  `> [!WARNING]`, ...) into configurable LaTeX environments.
- [x] **Selective exclusions**: Omit specific content (e.g., YAML front matter) from
  the conversion output.
- [x] **Batch or partial builds**: Process full documents or selected subsets of notes.
- [x] **Template assembly**: Generate a `main.tex` with `\input{...}` statements from
  a template with configurable placeholders.
- [x] **Custom AST transforms**: Register and apply user-defined transforms via a
  plugin registry.

---

## Quick Start

Convert a single Markdown file:

```sh
loretex convert-file notes.md --out notes.tex
```

Convert multiple chapters from a YAML spec:

```sh
loretex convert --spec spec.yml
```

---

## Documentation

| Guide | Content |
| ----- | ------- |
| [Installation](docs/guide/installation.md) | Prerequisites, pip/conda/source setup |
| [Usage](docs/guide/usage.md) | Workflows, spec files, template assembly |
| [CLI Reference](docs/guide/cli-reference.md) | Full command registry and options |
| [Configuration](docs/guide/configuration.md) | Conversion rules, callouts, labels, citations |
| [Architecture](docs/architecture.md) | Module organization and data flow |
| [Development](docs/guide/development.md) | Developer notes, integration tests |
| [Release Checklist](docs/guide/release-checklist.md) | Pre-release verification steps |

Full API documentation and rendered guides are also available at
[esther-poniatowski.github.io/loretex](https://esther-poniatowski.github.io/loretex/).

---

## Contributing

Contribution guidelines are described in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Acknowledgments

### Authors

**Author**: @esther-poniatowski

For academic use, the GitHub "Cite this repository" feature generates citations in
various formats. The [citation metadata](CITATION.cff) file is also available.

### Third-Party Dependencies

- **[PyYAML](https://pyyaml.org/)** — YAML configuration parsing.
- **[attrs](https://www.attrs.org/)** — Lightweight data classes and validation helpers.
- **[Typer](https://typer.tiangolo.com/)** — CLI framework.
- **[Rich](https://rich.readthedocs.io/)** — Terminal formatting for CLI output.

---

## License

This project is licensed under the terms of the
[GNU General Public License v3.0](LICENSE).
