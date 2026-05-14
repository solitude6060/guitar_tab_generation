from __future__ import annotations

from pathlib import Path
import wave

import pytest

from guitar_tab_generation.input_adapter import InputPolicyError, PolicyGateError, resolve_local_audio


def _write_silent_wav(path: Path, duration_seconds: float, *, sample_rate: int = 800) -> None:
    frames = int(duration_seconds * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\0" * frames)


def test_url_input_is_blocked_without_download() -> None:
    with pytest.raises(PolicyGateError) as exc:
        resolve_local_audio("https://youtube.com/watch?v=dummy")
    assert "local-audio-first" in str(exc.value)
    assert "disabled" in str(exc.value)


def test_url_policy_message_mentions_full_song_local_path() -> None:
    with pytest.raises(PolicyGateError) as exc:
        resolve_local_audio("https://youtube.com/watch?v=dummy")
    assert "30-90" in str(exc.value)
    assert "3-8 minute" in str(exc.value)


@pytest.mark.parametrize("duration_seconds", [180.0, 480.0])
def test_full_song_boundaries_are_accepted_with_chunk_plan(tmp_path: Path, duration_seconds: float) -> None:
    audio_path = tmp_path / f"full_song_{int(duration_seconds)}s.wav"
    _write_silent_wav(audio_path, duration_seconds)

    audio = resolve_local_audio(audio_path)

    assert audio.duration_seconds == duration_seconds
    assert audio.source_duration_seconds == duration_seconds
    assert audio.duration_class == "full_song"
    assert audio.processing_plan["mode"] == "chunked_full_song"
    assert audio.processing_plan["chunk_seconds"] == 60.0
    assert audio.processing_plan["overlap_seconds"] == 2.0
    assert audio.processing_plan["chunks"][0]["start"] == 0.0
    assert audio.processing_plan["chunks"][-1]["end"] == duration_seconds


def test_middle_length_audio_requires_supported_clip_or_full_song_window(tmp_path: Path) -> None:
    audio_path = tmp_path / "middle_length_120s.wav"
    _write_silent_wav(audio_path, 120.0)

    with pytest.raises(InputPolicyError) as exc:
        resolve_local_audio(audio_path)

    assert "30-90" in str(exc.value)
    assert "3-8 minute" in str(exc.value)
