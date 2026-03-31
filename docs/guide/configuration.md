# Configuration

## Configuration File

Loretex reads conversion rules from YAML spec files and from the canonical schema in
`config/default.yaml`. Rules specified in the spec override the defaults.

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

## Heading Mapping

Markdown headings map to LaTeX sections according to the `anchor_level` parameter.
A heading at `anchor_level` becomes `\section{}`, headings below become subsections.

```yaml
conversion:
  headings:
    anchor_level: 1
```

## Labels and Internal Links

Automatic heading labels and internal references:

```yaml
conversion:
  labels:
    auto_label_headings: true
    label_prefix: sec
  links:
    internal_ref_template: "\\ref{{{label}}}"
```

A Markdown link target like `[see](#some-section)` becomes `\ref{some-section}`.

## Citations

Standard and locator-aware citation formats:

```yaml
conversion:
  citations:
    cite_template: "\\cite{{{keys}}}"
    cite_with_locator_template: "\\cite[{locator}]{{{keys}}}"
```

```markdown
See [@doe2020, p. 12; @smith2021].
```

## Callouts and Fonts

Map Markdown callout types to LaTeX environments and configure fonts:

```yaml
document_font: "\\renewcommand{\\familydefault}{\\sfdefault}"
callout_title_font: "\\sffamily\\bfseries"
callout_body_font: "\\sffamily"
conversion:
  callouts:
    environment_map:
      note: notebox
      warning: warningbox
```

Loretex ships a default callouts style file and icons under `loretex/latex/`.
The `loretex-callouts.sty` file and the `icons/` folder must be available to LaTeX
at compile time (e.g., alongside `main.tex` or on the LaTeX search path).

## Code Blocks

```yaml
conversion:
  code_blocks:
    environment: lstlisting
```

## Images

```yaml
conversion:
  images:
    validate_paths: true
    base_dir: .
```

Missing images emit a warning at conversion time.

## Table Extensions

Column and row spans through inline markers:

```markdown
| A | B | C |
|---|---|---|
| Span{col=2} | X |
```

## Footnotes and Wiki Links

Footnotes and Obsidian-style wiki links are both supported:

```markdown
Text with footnote.[^1]
[^1]: Footnote text.

See [[My Note]] or [[My Note|alias]].
```

Both are configurable via `conversion.footnotes` and `conversion.wiki_links`.
