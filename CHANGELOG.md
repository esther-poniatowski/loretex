# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project adheres to Semantic Versioning.

## [Unreleased]

The command line follows the workspace
[command-line conventions](https://github.com/esther-poniatowski/keystone/blob/main/docs/internals/cli-conventions.md).

### Added
- `loretex convert --force` and `loretex convert-file --force` allow an output to overwrite an
  input of the conversion. Without `--force`, an output that names the Markdown source, the spec,
  the template or the `--config` file stops the command with status 2 and an error naming the file,
  before any file is written.

### Changed
- `loretex convert-file` names its output file `--output` (short form `-o`), the name that the
  conventions reserve for one output file. The former name `--out` is no longer accepted.
- An absent `--spec`, `--config` or input file, an invalid spec and an invalid conversion config
  stop the command with status 2 and a message, instead of a traceback.

## [0.1.0] - 2026-02-03

### Added
- Full Markdown → LaTeX conversion engine with AST, inline rules, and generator.
- Configurable rules for headings, callouts, lists, tables, images, links, citations, footnotes, wiki links, and math.
- YAML spec pipeline for batch conversion.
- Template-based `main.tex` assembly with placeholders.
- Transform registry/pipeline for extensibility.
- Docs with usage examples and architecture overview.
- Spec validation with friendly errors.

