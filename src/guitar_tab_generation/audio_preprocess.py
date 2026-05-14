from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Callable
import wave

from .input_adapter import AudioInput

TARGET_SAMPLE_RATE = 44100
TARGET_CHANNELS = 1
CommandRunner = Callable[[list[str]], tuple[int, str, str]]


class AudioPreprocessError(RuntimeError):
    """Raised when local audio normalization fails."""


def _run_command(command: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=120)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.SubprocessError as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def normalize_audio(audio: AudioInput, out_dir: str | Path, *, run_command: CommandRunner | None = None) -> dict:
    """Create normalized audio artifact metadata.

    WAV fixtures are trimmed directly for deterministic tests. Non-WAV local
    files are decoded and trimmed through local ffmpeg so downstream stages
    always receive a WAV artifact.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    source = Path(audio.input_uri)
    target = out / "audio_normalized.wav"

    if source.suffix.lower() == ".wav":
        _copy_wav_trimmed_mono(source, target, audio.trim["start"], audio.trim["end"])
    else:
        _ffmpeg_normalize(source, target, audio.trim["start"], audio.trim["end"], run_command=run_command)

    with wave.open(str(target), "rb") as handle:
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        duration = handle.getnframes() / float(sample_rate)

    return {
        "path": str(target),
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_seconds": duration,
        "trim": audio.trim,
        "provenance": {"stage": "audio_preprocess", "input": audio.input_type},
    }


def _copy_wav_trimmed_mono(source: Path, target: Path, start: float, end: float) -> None:
    with wave.open(str(source), "rb") as src:
        params = src.getparams()
        rate = src.getframerate()
        start_frame = int(start * rate)
        frame_count = int((end - start) * rate)
        src.setpos(start_frame)
        frames = src.readframes(frame_count)
        with wave.open(str(target), "wb") as dst:
            dst.setnchannels(params.nchannels)
            dst.setsampwidth(params.sampwidth)
            dst.setframerate(rate)
            dst.writeframes(frames)


def _ffmpeg_normalize(
    source: Path,
    target: Path,
    start: float,
    end: float,
    *,
    run_command: CommandRunner | None = None,
) -> None:
    runner = run_command or _run_command
    command = [
        "ffmpeg",
        "-v",
        "error",
        "-y",
        "-ss",
        f"{start:.3f}",
        "-to",
        f"{end:.3f}",
        "-i",
        str(source),
        "-ac",
        str(TARGET_CHANNELS),
        "-ar",
        str(TARGET_SAMPLE_RATE),
        str(target),
    ]
    code, stdout, stderr = runner(command)
    if code != 0:
        detail = stderr or stdout or "unknown ffmpeg error"
        raise AudioPreprocessError(f"Local ffmpeg could not normalize audio: {detail}")
