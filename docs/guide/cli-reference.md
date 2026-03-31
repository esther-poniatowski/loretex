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
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--out PATH` | Write output to a file instead of stdout. | stdout |

### `loretex convert --spec <path>`

Convert multiple chapters from a YAML spec. The spec defines document structure,
conversion rules, and optional template assembly.

```sh
loretex convert --spec spec.yml
```

| Option | Description | Default |
| ------ | ----------- | ------- |
| `--spec PATH` | Path to the YAML spec file. | Required |

### `loretex info`

Display version and platform diagnostics.

```sh
loretex info
```
