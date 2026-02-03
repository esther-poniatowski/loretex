# Usage Examples

This document provides practical examples for all major features.

## 1. Quick Start (Single File)

```bash
loretex convert-file notes.md
```

```bash
loretex convert-file notes.md --out notes.tex
```

```python
from loretex import convert_string

latex = convert_string("# Title\n\nSome **bold** text.")
```

## 2. Spec-Based Conversion (Multiple Files)

```yaml
# spec.yml
output_dir: ./tex
anchor_level: 1
chapters:
  - file: notes/intro.md
  - file: notes/chapter1.md
```

```bash
loretex convert --spec spec.yml
```

## 3. Template Assembly (main.tex)

Template file (`templates/main.tex`):

```tex
\documentclass{article}
\usepackage{hyperref}
\begin{document}
{{content}}
\end{document}
```

Spec file:

```yaml
output_dir: ./tex
template: ./templates/main.tex
main_output: ./tex/main.tex
chapters:
  - file: notes/intro.md
```

Result: `main.tex` contains `\input{intro.tex}`.

## 4. Template Variables

Template:

```tex
\title{{title}}
\author{{author}}
\date{{date}}
\begin{document}
\maketitle
{{bibliography}}
{{content}}
\end{document}
```

Spec:

```yaml
template: ./templates/main.tex
main_output: ./tex/main.tex
output_dir: ./tex

title: My Document
author: Me
date: 2026-02-03
bibliography: "\\bibliography{refs}"

chapters:
  - file: notes/intro.md
```

## 5. Conversion Rules (Global + Per Chapter)

```yaml
output_dir: ./tex
conversion:
  headings:
    anchor_level: 1
  callouts:
    environment_map:
      note: notebox
chapters:
  - file: notes/intro.md
    conversion:
      headings:
        anchor_level: 2
```

## 6. Headings & Labels

```yaml
conversion:
  labels:
    auto_label_headings: true
    label_prefix: sec
```

```markdown
# Introduction
```

Produces:

```tex
\section{Introduction}
\label{sec-introduction}
```

## 7. Internal Links

```markdown
See [Introduction](#introduction).
```

Produces:

```tex
See \ref{introduction}.
```

## 8. External Links

```markdown
Read [the docs](https://example.com).
<https://example.com>
```

Produces:

```tex
\href{https://example.com}{the docs}
\url{https://example.com}
```

## 9. Citations (With Locators)

```markdown
See [@doe2020].
See [@doe2020, p. 12; @smith2021].
```

Produces:

```tex
\cite{doe2020}
\cite[p. 12]{doe2020} \cite{smith2021}
```

Config:

```yaml
conversion:
  citations:
    cite_template: "\\cite{{{keys}}}"
    cite_with_locator_template: "\\cite[{locator}]{{{keys}}}"
```

## 10. Footnotes

```markdown
Text with footnote.[^1]

[^1]: Footnote text.
```

Produces:

```tex
Text with footnote.\footnote{Footnote text.}
```

## 11. Wiki Links (Obsidian)

```markdown
See [[My Note]] and [[My Note|alias]].
```

Produces:

```tex
\ref{my-note}
```

## 12. Math Blocks

```markdown
$$
E = mc^2
$$
```

With config:

```yaml
conversion:
  math:
    block_style: brackets
```

Produces:

```tex
\[E = mc^2\]
```

## 13. Images

```markdown
<img src="figs/diagram.svg" width="300">
```

Produces:

```tex
\begin{center}
\includegraphics[width=300\htmlpx]{../figures-pdfs/figs/diagram.pdf}
\end{center}
```

## 14. Tables with Colspan/Rowspan

```markdown
| A | B | C |
|---|---|---|
| Span{col=2} | X |
```

Produces:

```tex
\multicolumn{2}{c}{Span}
```

## 15. Transforms (Plugin Hook)

```python
from loretex.conversion import Document, Paragraph, register_transform, MarkdownToLaTeXConverter


def add_notice(doc: Document) -> Document:
    return Document(children=[Paragraph("NOTICE")] + doc.children)

register_transform("notice", add_notice)
converter = MarkdownToLaTeXConverter(transform_names=["notice"])
latex = converter.convert_string("# Title")
```

## 16. Image Validation Warnings

```yaml
conversion:
  images:
    validate_paths: true
    base_dir: .
```

If an image is missing, a warning is emitted at conversion time.

## 17. Spec Validation Errors

If required fields are missing, conversion raises a `SpecValidationError` with details.
