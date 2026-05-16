from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.backends import BackendExecutionError, resolve_backend
from guitar_tab_generation.pipeline import transcribe_to_tab


def test_default_pipeline_uses_fixture_backend(tmp_path) -> None:
    arrangement, quality_report = transcribe_to_tab(
        "fixtures/simple_chords_30_90s.wav",
        tmp_path,
    )
    assert quality_report["status"] == "passed"
    assert arrangement["timebase"]["provenance"]["backend"] == "fixture"
    assert arrangement["note_events"][0]["provenance"]["backend"] == "fixture"
    assert arrangement["chord_spans"][0]["provenance"]["backend"] == "fixture"
    assert arrangement["section_spans"][0]["provenance"]["backend"] == "fixture"


def test_unknown_backend_fails_with_clear_message() -> None:
    with pytest.raises(BackendExecutionError) as exc:
        resolve_backend("missing-backend")
    assert "Unknown analysis backend" in str(exc.value)
    assert "fixture" in str(exc.value)


def test_optional_real_backend_placeholder_is_import_guarded() -> None:
    with pytest.raises(BackendExecutionError) as exc:
        resolve_backend("real")
    assert "Optional backend 'real' is not installed" in str(exc.value)


def test_basic_pitch_backend_can_be_resolved_when_audio_path_is_provided(tmp_path: Path) -> None:
    backend = resolve_backend("basic-pitch", audio_path=tmp_path / "normalized.wav")

    assert backend.name == "basic-pitch"


def test_pipeline_passes_normalized_audio_path_to_basic_pitch_backend(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, str] = {}

    class StubBackend:
        name = "basic-pitch"

        def safe_analyze_rhythm(self, duration_seconds: float, fixture_metadata: dict | None = None) -> dict:
            return {"tempo_bpm": 96.0, "confidence": 0.8, "provenance": {"stage": "rhythm_analysis", "backend": "basic-pitch"}}

        def safe_analyze_chords(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
            return ([{"start": 0.0, "end": duration_seconds, "label": "C", "confidence": 0.8, "provenance": {"stage": "tonal_chord_analysis", "backend": "basic-pitch"}}], [])

        def safe_transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
            return ([{"id": "n1", "start": 0.0, "end": 0.5, "pitch_midi": 60, "pitch_name": "C4", "velocity": 0.8, "confidence": 0.8, "provenance": {"stage": "pitch_transcription", "backend": "basic-pitch", "stem": "mix", "model": "basic_pitch_icassp_2022"}}], [])

        def safe_detect_sections(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
            return ([{"start": 0.0, "end": duration_seconds, "label": "Sketch A", "confidence": 0.8, "provenance": {"stage": "section_detector", "backend": "basic-pitch"}}], [])

    def _resolve_backend(name: str | None = None, *, audio_path: Path | None = None):
        assert name == "basic-pitch"
        assert audio_path is not None
        captured["audio_path"] = str(audio_path)
        return StubBackend()

    monkeypatch.setattr("guitar_tab_generation.pipeline.resolve_backend", _resolve_backend)

    out_dir = tmp_path / "out"
    arrangement, _quality_report = transcribe_to_tab(
        "fixtures/simple_chords_30_90s.wav",
        out_dir,
        backend="basic-pitch",
    )

    assert captured["audio_path"].endswith("audio_normalized.wav")
    written_notes = json.loads((out_dir / "notes.json").read_text(encoding="utf-8"))
    assert written_notes[0]["provenance"]["backend"] == "basic-pitch"
    assert arrangement["note_events"][0]["provenance"]["backend"] == "basic-pitch"
