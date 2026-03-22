# Development Notes

This document captures developer-facing notes about tests, fixtures, and workflows.

## Integration Test Fixtures

The complex integration test lives under `tests/fixtures/complex/`.

Notes:
- `spec.yml` intentionally omits `output_dir`, `template`, and `main_output`.
  The test fills these dynamically so the fixture remains portable.
- Assets are expected at `tests/fixtures/complex/assets/figs/diagram.pdf`.
- The test writes outputs to a temporary working directory unless you run the
  conversion manually.

## Running the Complex Integration Test

```bash
conda run -n loretex pytest tests/test_loretex/test_integration_complex.py
```

To render a PDF into the fixture folder for visual inspection:

```bash
conda run -n loretex python /tmp/loretex_complex_build.py
cd tests/fixtures/complex/out
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```
