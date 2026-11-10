# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

### Changed
- `loretex convert-file` names its output file `--output` (short form `-o`), the name that the
  workspace command-line conventions reserve for one output file.

### Deprecated
- `loretex convert-file --out` remains accepted for one release as a hidden alias of `--output`,
  and prints a warning naming `--output`. The following release removes it.

## [0.1.0] - 2026-02-03

### Added
- Full Markdown → LaTeX conversion engine with AST, inline rules, and generator.
- Configurable rules for headings, callouts, lists, tables, images, links, citations, footnotes, wiki links, and math.
- YAML spec pipeline for batch conversion.
- Template-based `main.tex` assembly with placeholders.
- Transform registry/pipeline for extensibility.
- Docs with usage examples and architecture overview.
- Spec validation with friendly errors.

