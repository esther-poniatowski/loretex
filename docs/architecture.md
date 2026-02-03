# Architecture

This document describes the Loretex architecture, responsibilities, and interactions.

## Overview

Loretex is organized into a small set of modules, each with a single responsibility:

- `loretex.conversion`: Markdown → LaTeX engine (parser, AST, inline rules, generator).
- `loretex.pipeline`: Template rendering and `main.tex` assembly.
- `loretex.api`: Public API (simple entry points).
- `loretex.config`: Spec parsing and validation.
- `loretex.cli`: Command-line interface.
- `loretex.latex`: Packaged LaTeX assets (callouts style and icons).

The system is designed for:

- **Ease of use**: simple API + CLI.
- **Separation of concerns**: parsing, transformation, generation, assembly isolated.
- **Modularity and extensibility**: transform registry and config-driven rules.
- **Robustness**: validation and warnings for missing assets.

## Component Roles

### 1. Conversion Engine (`loretex.conversion`)

**Modules:**

- `parser.py`:
  - Parses Markdown to an AST (`nodes.py`).
  - Handles headings, lists, code blocks, tables, callouts, images, etc.

- `nodes.py`:
  - AST node definitions + visitor interface.

- `inline.py`:
  - Inline transformations (bold, italics, links, citations, footnotes, wiki links).

- `generator.py`:
  - Visitor implementation that turns AST into LaTeX.
  - Adds heading labels, formats tables, emits callout environments, etc.

- `engine.py`:
  - Orchestrates parsing → transforms → generation.
  - Applies optional preprocessing (front matter stripping, math normalization).

- `config.py`:
  - Conversion configuration models and defaults.
  - Configurable via YAML spec.

- `registry.py` / `transforms.py`:
  - Optional AST transform registry and pipeline.

### 2. Pipeline (`loretex.pipeline`)

- `templates.py`:
  - Simple placeholder replacement (`{{content}}`, `{{title}}`, etc.).

- `assembly.py`:
  - Generates `main.tex` from a template and `\input{...}` lines for chapter files.
  - Template placeholders include `{{content}}`, `{{title}}`, `{{author}}`, `{{date}}`,
    `{{bibliography}}`, plus `{{document_font}}`, `{{callout_title_font}}`,
    and `{{callout_body_font}}`.

### 3. Public API (`loretex.api`)

- `convert_string`, `convert_file`, `convert_spec` provide stable high-level entry points.
- Also responsible for spec validation and triggering optional assembly.

### 4. Config and Validation (`loretex.config`)

- `params.py`: structured representation of spec configuration.
- `validate.py`: schema validation with friendly errors.

### 5. CLI (`loretex.cli`)

- Thin wrapper around API for user-facing commands.

## Data Flow

1. **Input Markdown**
   - From file or in-memory string.

2. **Preprocessing** (optional)
   - YAML front matter stripping.
   - Footnote extraction.

3. **Parsing**
   - Markdown → AST (`nodes.py`).

4. **Transform Pipeline** (optional)
   - User-registered transforms apply to AST.

5. **Generation**
   - AST → LaTeX (`generator.py` + `inline.py`).

6. **Output**
   - Write `*.tex` chapter files.
   - Optionally assemble `main.tex` using a template.

## Extensibility Points

- **Transforms**:
  - Register custom AST transforms via `register_transform` and `transform_names`.

- **Config Rules**:
  - Customize conversion behavior in YAML (`config/default.yaml`).

- **Templates**:
  - Customize layout of `main.tex` with placeholders.

- **LaTeX Assets**:
  - Packaged callout style file and icons under `loretex/latex/`.

## Design Principles Applied

- **Single Responsibility**: each module has a dedicated task.
- **Modularity**: conversion engine and pipeline are independent.
- **Flexibility**: config-driven rules, template variables, transform registry.
- **Robustness**: spec validation and optional missing-asset warnings.
- **Ease of use**: minimal API surface + CLI.
