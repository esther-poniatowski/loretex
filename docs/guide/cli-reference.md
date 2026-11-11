# CLI Reference

## Global Options

```
loretex [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
| ------ | ----------- |
| `--version`, `-v` | Display the version and exit. |
| `--help` | Display the help message and exit. |

A path given on the command line is relative to the current folder. Loretex searches for no
configuration file, hence has no root: the conversion rules come from `--config` or from the spec.
An output never overwrites an input of the conversion, such as the Markdown source, the spec, the
template or the `--config` file, unless `--force` is given; a generated `.tex` file is overwritten
freely. The exit status is 2 on a usage, spec or configuration error, such as an absent `--spec` or
`--config` file, and 1 when the conversion of the Markdown fails.

## Commands

### `loretex convert-file <path>`

Convert a single Markdown file to LaTeX.

```sh
loretex convert-file notes.md
loretex convert-file notes.md --output notes.tex
loretex convert-file notes.md --config rules.yaml --anchor 2
```

| Option | Short | Description | Default |
| ------ | ----- | ----------- | ------- |
| `--output PATH` | `-o` | Write output to a file instead of stdout. | stdout |
| `--config PATH` | `-c` | YAML file with conversion rules (same schema as the `conversion` block in a spec). | none |
| `--anchor INT` | `-a` | Markdown heading level mapped to `\section{}`. Ignored when the config file already sets `headings.anchor_level`. | `1` |
| `--force` | | Overwrite an input of the conversion if `--output` names it. | off |

### `loretex convert`

Convert multiple chapters from a YAML spec. The spec defines document structure,
conversion rules, and optional template assembly. The spec is a job file for one document, not a
configuration file: the paths written in it are relative to the folder of the spec, so that a
document keeps its spec beside its Markdown.

```sh
loretex convert --spec spec.yml
loretex convert -s spec.yml
```

| Option | Short | Description | Default |
| ------ | ----- | ----------- | ------- |
| `--spec PATH` | `-s` | Path to the YAML spec file. | Required |
| `--force` | | Overwrite an input of the run, such as a chapter source, if an output of the spec names it. | off |

### `loretex info`

Display version and platform diagnostics.

```sh
loretex info
```
