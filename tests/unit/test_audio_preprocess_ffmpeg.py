from __future__ import annotations

from pathlib import Path
import wave

import pytest

from guitar_tab_generation.audio_preprocess import AudioPreprocessError, normalize_audio
from guitar_tab_generation.input_adapter import AudioInput, build_processing_plan


def _write_wav(path: Path, duration_seconds: float = 1.0, *, sample_rate: int = 44100) -> None:
    frames = int(duration_seconds * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\0\0" * frames)


def _audio_input(path: Path) -> AudioInput:
    return AudioInput(
        input_type="local_audio",
        input_uri=str(path),
        rights_attestation="user_provided",
        duration_seconds=180.0,
        source_duration_seconds=180.0,
        duration_class="full_song",
        processing_plan=build_processing_plan(180.0, "full_song"),
        trim={"start": 0.0, "end": 180.0},
    )


def test_non_wav_normalization_uses_ffmpeg_to_write_wav(tmp_path: Path) -> None:
    source = tmp_path / "song.mp3"
    source.write_bytes(b"fake local mp3 bytes")
    commands: list[list[str]] = []

    def fake_run(command: list[str]) -> tuple[int, str, str]:
        commands.append(command)
        _write_wav(Path(command[-1]))
        return 0, "", ""

    result = normalize_audio(_audio_input(source), tmp_path / "out", run_command=fake_run)

    assert commands
    assert commands[0][0] == "ffmpeg"
    assert "-ss" in commands[0]
    assert "-to" in commands[0]
    assert commands[0][-1].endswith("audio_normalized.wav")
    assert result["sample_rate"] == 44100
    assert result["channels"] == 1
    assert Path(result["path"]).suffix == ".wav"


def test_non_wav_normalization_failure_is_actionable(tmp_path: Path) -> None:
    source = tmp_path / "song.flac"
    source.write_bytes(b"fake local flac bytes")

    def fake_run(command: list[str]) -> tuple[int, str, str]:
        return 1, "", "ffmpeg decode failed"

    with pytest.raises(AudioPreprocessError) as exc:
        normalize_audio(_audio_input(source), tmp_path / "out", run_command=fake_run)

    assert "ffmpeg" in str(exc.value)
    assert "decode failed" in str(exc.value)
