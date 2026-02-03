# Release Checklist

## Required

- [ ] Update version in `pyproject.toml`.
- [ ] Update `CHANGELOG.md` with a dated release section.
- [ ] Run `ruff check .`.
- [ ] Run `mypy src`.
- [ ] Run `pytest`.
- [ ] Verify `LICENSE` matches `pyproject.toml`.
- [ ] Ensure docs are up to date (`docs/usage-examples.md`, `docs/architecture.md`).

## Recommended

- [ ] Verify README badges and URLs.
- [ ] Build package: `python -m build`.
- [ ] Smoke test install: `pip install dist/*.whl`.
- [ ] Create Git tag and release notes.
