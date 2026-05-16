from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.cli import main


def test_cli_transcribe_with_basic_pitch_backend_uses_ai_note_provenance(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def _predict(audio_path: str, *_args, **_kwargs):
        assert audio_path.endswith("audio_normalized.wav")
        return (
            {"raw": True},
            object(),
            [
                (0.0, 0.5, 60, 0.82, []),
                (1.0, 1.4, 64, 0.79, []),
            ],
        )

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", lambda: _predict)

    artifact_dir = tmp_path / "basic_pitch"
    assert main(["transcribe", "fixtures/simple_chords_30_90s.wav", "--backend", "basic-pitch", "--out", str(artifact_dir)]) == 0

    arrangement = json.loads((artifact_dir / "arrangement.json").read_text(encoding="utf-8"))
    assert arrangement["note_events"]
    assert arrangement["note_events"][0]["provenance"]["backend"] == "basic-pitch"
    assert arrangement["note_events"][0]["provenance"]["model"] == "basic_pitch_icassp_2022"
