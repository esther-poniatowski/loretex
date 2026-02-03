from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from loretex.api import convert_spec


def _fixture_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "complex"


def _write_temp_spec(
    spec_template: Path,
    output_dir: Path,
    template_path: Path,
    main_output: Path,
    working_dir: Path,
) -> Path:
    spec = yaml.safe_load(spec_template.read_text(encoding="utf-8"))
    spec["output_dir"] = str(output_dir)
    spec["template"] = str(template_path)
    spec["main_output"] = str(main_output)
    chapters = spec.get("chapters") or []
    updated_chapters = []
    for chapter in chapters:
        if not isinstance(chapter, dict):
            continue
        entry = dict(chapter)
        file_value = entry.get("file")
        if isinstance(file_value, str):
            entry["file"] = str(working_dir / file_value)
        updated_chapters.append(entry)
    if updated_chapters:
        spec["chapters"] = updated_chapters
    spec_path = output_dir / "spec.yml"
    spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path


def _ensure_assets(tmp_root: Path, fixture_root: Path) -> bool:
    assets_src = fixture_root / "assets"
    if not assets_src.exists():
        return False
    assets_dst = tmp_root / "assets"
    shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
    expected = assets_dst / "figs" / "diagram.pdf"
    return expected.exists()


def _latexmk_available() -> bool:
    return shutil.which("latexmk") is not None


def _pdflatex_available() -> bool:
    return shutil.which("pdflatex") is not None


def _compile_pdf(output_dir: Path, main_tex: Path) -> Path:
    if _latexmk_available():
        subprocess.run(
            ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
            check=True,
            cwd=output_dir,
        )
    elif _pdflatex_available():
        for _ in range(2):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
                check=True,
                cwd=output_dir,
            )
    else:
        pytest.skip("No LaTeX engine available (latexmk or pdflatex).")
    return output_dir / main_tex.with_suffix(".pdf").name


def test_complex_pipeline_to_pdf(tmp_path: Path) -> None:
    fixture_root = _fixture_dir()
    working_dir = tmp_path / "complex"
    working_dir.mkdir()

    chapters_src = fixture_root / "chapters"
    chapters_dst = working_dir / "chapters"
    shutil.copytree(chapters_src, chapters_dst, dirs_exist_ok=True)

    template_src = fixture_root / "template.tex"
    template_dst = working_dir / "template.tex"
    shutil.copy2(template_src, template_dst)
    callout_src = fixture_root / "loretex-callouts.sty"
    callout_dst = working_dir / "loretex-callouts.sty"
    shutil.copy2(callout_src, callout_dst)
    icons_src = fixture_root / "icons"
    if icons_src.exists():
        shutil.copytree(icons_src, working_dir / "icons", dirs_exist_ok=True)

    assets_ready = _ensure_assets(working_dir, fixture_root)

    output_dir = working_dir / "out"
    output_dir.mkdir()
    main_output = output_dir / "main.tex"

    spec_path = _write_temp_spec(
        fixture_root / "spec.yml",
        output_dir=output_dir,
        template_path=template_dst,
        main_output=main_output,
        working_dir=working_dir,
    )

    outputs = convert_spec(spec_path)
    assert outputs, "Expected chapter outputs to be generated."
    assert main_output.exists()

    if not assets_ready:
        pytest.skip("Missing PDF assets under tests/fixtures/complex/assets.")

    pdf_path = _compile_pdf(output_dir, main_output)
    assert pdf_path.exists()
