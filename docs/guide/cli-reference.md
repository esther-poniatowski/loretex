# CLI Reference

## Global Options

```
loretex [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
| ------ | ----------- |
| `--version`, `-v` | Display the version and exit. |
| `--help` | Display the help message and exit. |

## Commands

### `loretex convert-file <path>`

Convert a single Markdown file to LaTeX.

```sh
loretex convert-file notes.md
loretex convert-file notes.md --out notes.tex
loretex convert-file notes.md --config rules.yaml --anchor 2
```

| Option | Short | Description | Default |
| ------ | ----- | ----------- | ------- |
| `--out PATH` | `-o` | Write output to a file instead of stdout. | stdout |
| `--config PATH` | `-c` | YAML file with conversion rules (same schema as the `conversion` block in a spec). | none |
| `--anchor INT` | `-a` | Markdown heading level mapped to `\section{}`. Ignored when the config file already sets `headings.anchor_level`. | `1` |

### `loretex convert`

Convert multiple chapters from a YAML spec. The spec defines document structure,
conversion rules, and optional template assembly.

```sh
loretex convert --spec spec.yml
loretex convert -s spec.yml
```

| Option | Short | Description | Default |
| ------ | ----- | ----------- | ------- |
| `--spec PATH` | `-s` | Path to the YAML spec file. | Required |

### `loretex info`

Display version and platform diagnostics.

```sh
loretex info
```
