---
title: Complex Document
tags:
  - test
  - loretex
---

# Introduction

This is a ==complex== test document. It includes inline math $a_b + c$ and a citation [@doe2020].
See [Background](#background) for more details.

> [!NOTE] Motivation
> This is a note callout with **bold** and *italic* text.
> It also includes a footnote reference.[^1]

[^1]: Footnote content for the introduction.

---

## Code Example

```python
def hello(name: str) -> None:
    print(f"Hello {name}")
```

## Image

<img src="figs/diagram.svg" width="300">

## Table

| Column A | Column B | Column C |
|:--|:--:|--:|
| A1 | B1 | C1 |
| Span{col=2} |  | C2 |

## Wiki Link

See [[Background]] for context.
