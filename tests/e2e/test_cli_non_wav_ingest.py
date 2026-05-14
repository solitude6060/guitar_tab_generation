from __future__ import annotations

import json
from pathlib import Path
import wave

from guitar_tab_generation.cli import main


def _write_wav(path: Path, duration_seconds: float = 1.0, *, sample_rate: int = 44100) -> None:
    frames = int(duration_seconds * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\0\0" * frames)


def test_cli_transcribe_accepts_mocked_mp3_full_song(tmp_path: Path, monkeypatch) -> None:
    audio_path = tmp_path / "legal_full_song.mp3"
    artifact_dir = tmp_path / "artifact"
    audio_path.write_bytes(b"fake local mp3 bytes")

    def fake_probe(command: list[str]) -> tuple[int, str, str]:
        return 0, "180.0", ""

    def fake_ffmpeg(command: list[str]) -> tuple[int, str, str]:
        _write_wav(Path(command[-1]))
        return 0, "", ""

    import guitar_tab_generation.input_adapter as input_adapter
    import guitar_tab_generation.audio_preprocess as audio_preprocess

    monkeypatch.setattr(input_adapter, "_run_command", fake_probe)
    monkeypatch.setattr(audio_preprocess, "_run_command", fake_ffmpeg)

    assert main(["transcribe", str(audio_path), "--backend", "fixture", "--out", str(artifact_dir)]) == 0

    arrangement = json.loads((artifact_dir / "arrangement.json").read_text(encoding="utf-8"))
    assert arrangement["source"]["duration_class"] == "full_song"
    assert arrangement["source"]["source_duration_seconds"] == 180.0
    assert arrangement["source"]["processing_plan"]["mode"] == "chunked_full_song"
    assert (artifact_dir / "audio_normalized.wav").exists()
