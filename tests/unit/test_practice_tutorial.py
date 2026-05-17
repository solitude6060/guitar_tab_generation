from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.practice_tutorial import (
    LocalLLMTutorialError,
    build_fake_llm_coaching_notes,
    render_practice_tutorial_markdown,
    write_practice_tutorial,
)
from guitar_tab_generation.artifact_viewer import ArtifactViewerError, load_artifact_bundle


def _write_bundle(path: Path, *, warnings: bool = True, overall: float = 0.68) -> None:
    arrangement = {
        "schema_version": "0.1.0",
        "source": {"input_uri": "fixtures/single_note_riff_30_90s.wav"},
        "timebase": {"tempo_bpm": 120.0},
        "confidence": {"overall": overall, "notes": 0.62, "chords": 0.8, "fingering": 0.64},
        "section_spans": [
            {"label": "Riff A", "start": 0.0, "end": 8.0, "confidence": 0.72},
            {"label": "Riff B", "start": 8.0, "end": 16.0, "confidence": 0.7},
        ],
        "chord_spans": [
            {"label": "Em", "start": 0.0, "end": 4.0, "confidence": 0.82},
            {"label": "C", "start": 4.0, "end": 8.0, "confidence": 0.78},
        ],
        "note_events": [
            {"id": "n1", "start": 0.0, "end": 0.5, "pitch_name": "E4", "confidence": 0.66},
            {"id": "n2", "start": 0.5, "end": 1.0, "pitch_name": "G4", "confidence": 0.67},
        ],
        "warnings": [
            {"code": "LOW_FINGERING_CONFIDENCE", "severity": "warning", "message": "Check fingering."},
        ] if warnings else [],
    }
    quality_report = {"status": "passed", "hard_failures": []}
    path.mkdir(parents=True, exist_ok=True)
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps(quality_report), encoding="utf-8")
    (path / "tab.md").write_text("# Guitar TAB Sketch\n\n## TAB\n", encoding="utf-8")


def test_render_practice_tutorial_contains_practice_sections_and_tempo_ladder(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    markdown = render_practice_tutorial_markdown(load_artifact_bundle(tmp_path))

    assert "# Practice Tutorial" in markdown
    assert "fixtures/single_note_riff_30_90s.wav" in markdown
    assert "## Readiness check" in markdown
    assert "LOW_FINGERING_CONFIDENCE" in markdown
    assert "60 BPM" in markdown
    assert "90 BPM" in markdown
    assert "120 BPM" in markdown
    assert "## Section loop plan" in markdown
    assert "Riff A" in markdown
    assert "Riff B" in markdown
    assert "## Chord practice plan" in markdown
    assert "Em → C" in markdown
    assert "## Lead/riff practice plan" in markdown
    assert "E4 → G4" in markdown
    assert "## Safety note" in markdown
    assert "Open `tab.md`" in markdown


def test_render_practice_tutorial_marks_ready_when_confident_and_warning_free(tmp_path: Path) -> None:
    _write_bundle(tmp_path, warnings=False, overall=0.86)

    markdown = render_practice_tutorial_markdown(load_artifact_bundle(tmp_path))

    assert "Ready for structured practice" in markdown
    assert "- None" in markdown


def test_write_practice_tutorial_defaults_to_artifact_dir(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    written = write_practice_tutorial(tmp_path)

    assert written == tmp_path / "tutorial.md"
    assert "# Practice Tutorial" in written.read_text(encoding="utf-8")


def test_fake_llm_coaching_notes_include_artifact_citations(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    bundle = load_artifact_bundle(tmp_path)

    notes = build_fake_llm_coaching_notes(bundle)

    assert "## LLM Coaching Notes" in notes
    assert "`arrangement.json`" in notes
    assert "`quality_report.json`" in notes
    assert "`tab.md`" in notes


def test_write_practice_tutorial_fake_llm_backend_is_opt_in(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    default_written = write_practice_tutorial(tmp_path)
    assert "## LLM Coaching Notes" not in default_written.read_text(encoding="utf-8")

    fake_written = write_practice_tutorial(tmp_path, llm_backend="fake")
    assert "## LLM Coaching Notes" in fake_written.read_text(encoding="utf-8")


def test_write_practice_tutorial_local_llm_backend_fails_without_runtime(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    with pytest.raises(LocalLLMTutorialError, match="Local LLM tutorial backend is not configured"):
        write_practice_tutorial(tmp_path, llm_backend="local")

    assert not (tmp_path / "tutorial.md").exists()


def test_write_practice_tutorial_uses_artifact_contract_errors(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "tab.md").write_text("# TAB\n", encoding="utf-8")

    with pytest.raises(ArtifactViewerError, match="arrangement.json"):
        write_practice_tutorial(tmp_path)
