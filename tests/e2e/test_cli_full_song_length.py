from __future__ import annotations

import json
from pathlib import Path
import wave

from guitar_tab_generation.cli import main
from tests.support.contract_validators import assert_arrangement_contract, assert_quality_report_contract


def _write_silent_wav(path: Path, duration_seconds: float, *, sample_rate: int = 800) -> None:
    frames = int(duration_seconds * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\0" * frames)


def test_cli_transcribe_accepts_three_minute_full_song(tmp_path: Path) -> None:
    audio_path = tmp_path / "legal_full_song_180s.wav"
    artifact_dir = tmp_path / "artifact"
    _write_silent_wav(audio_path, 180.0)

    exit_code = main([
        "transcribe",
        str(audio_path),
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ])

    assert exit_code == 0
    arrangement = json.loads((artifact_dir / "arrangement.json").read_text(encoding="utf-8"))
    quality_report = json.loads((artifact_dir / "quality_report.json").read_text(encoding="utf-8"))

    assert_arrangement_contract(arrangement)
    assert_quality_report_contract(quality_report, arrangement)
    assert arrangement["source"]["duration_class"] == "full_song"
    assert arrangement["source"]["source_duration_seconds"] == 180.0
    assert arrangement["source"]["processing_plan"]["mode"] == "chunked_full_song"
    assert arrangement["source"]["processing_plan"]["chunks"][-1]["end"] == 180.0
    tab = (artifact_dir / "tab.md").read_text(encoding="utf-8")
    assert "Duration class: full_song" in tab
    assert "Processing mode: chunked_full_song" in tab
    assert not (artifact_dir / "policy_gate.txt").exists()
