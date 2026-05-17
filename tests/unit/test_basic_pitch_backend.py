from __future__ import annotations

from pathlib import Path

import pytest

from guitar_tab_generation.backends import BackendExecutionError
from guitar_tab_generation.basic_pitch_backend import BasicPitchAnalysisBackend


def test_basic_pitch_backend_requires_installed_package(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    backend = BasicPitchAnalysisBackend(audio_path=tmp_path / "audio.wav")

    def _missing_import():
        raise ImportError("No module named 'basic_pitch'")

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", _missing_import)

    with pytest.raises(BackendExecutionError, match="basic-pitch backend requires the optional Python package"):
        backend.transcribe_notes(30.0)


def test_basic_pitch_backend_requires_audio_path(monkeypatch: pytest.MonkeyPatch) -> None:
    backend = BasicPitchAnalysisBackend(audio_path=None)

    monkeypatch.setattr(
        "guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict",
        lambda: (lambda *_args, **_kwargs: ({}, object(), [])),
    )

    with pytest.raises(BackendExecutionError, match="requires a normalized local audio path"):
        backend.transcribe_notes(30.0)


def test_basic_pitch_backend_translates_prediction_to_note_events(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = BasicPitchAnalysisBackend(audio_path=tmp_path / "audio.wav")

    def _predict(audio_path: str, *_args, **_kwargs):
        assert audio_path == str(tmp_path / "audio.wav")
        return (
            {"note": "raw"},
            object(),
            [
                (0.0, 0.5, 60, 0.81, []),
                (0.75, 1.25, 64, 0.49, []),
            ],
        )

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", lambda: _predict)

    notes, warnings = backend.transcribe_notes(30.0)

    assert [note["pitch_midi"] for note in notes] == [60, 64]
    assert notes[0]["pitch_name"] == "C4"
    assert notes[0]["provenance"]["backend"] == "basic-pitch"
    assert notes[0]["provenance"]["model"] == "basic_pitch_icassp_2022"
    assert notes[0]["velocity"] == pytest.approx(0.81)
    assert any(warning["code"] == "LOW_NOTE_CONFIDENCE" for warning in warnings)


def test_basic_pitch_backend_marks_explicit_stem_in_provenance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    backend = BasicPitchAnalysisBackend(audio_path=tmp_path / "guitar.wav", stem_name="guitar")

    def _predict(audio_path: str, *_args, **_kwargs):
        assert audio_path == str(tmp_path / "guitar.wav")
        return ({"note": "raw"}, object(), [(0.0, 0.5, 67, 0.88, [])])

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", lambda: _predict)

    notes, _warnings = backend.transcribe_notes(30.0)

    assert notes[0]["provenance"]["backend"] == "basic-pitch"
    assert notes[0]["provenance"]["stem"] == "guitar"
