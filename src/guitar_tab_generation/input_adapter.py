from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import wave

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a"}
MIN_DURATION_SECONDS = 30.0
MAX_DURATION_SECONDS = 90.0


class InputPolicyError(ValueError):
    """Raised when an input violates MVP input policy."""


@dataclass(frozen=True)
class AudioInput:
    input_type: str
    input_uri: str
    rights_attestation: str
    duration_seconds: float | None
    trim: dict[str, float]


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def policy_gate_for_url(url: str) -> dict:
    return {
        "status": "blocked",
        "code": "URL_POLICY_GATE_DISABLED",
        "input_type": "url",
        "input_uri": url,
        "message": (
            "MVP is local-audio-first: arbitrary YouTube/URL download or parsing is disabled. "
            "Provide a legal local 30-90 second audio file instead."
        ),
    }


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        frames = handle.getnframes()
        rate = handle.getframerate()
    return frames / float(rate)


def validate_local_audio(
    input_path: str | Path,
    *,
    trim_start: float | None = None,
    trim_end: float | None = None,
    rights_attestation: str = "user_provided",
) -> AudioInput:
    path = Path(input_path)
    if is_url(str(input_path)):
        raise InputPolicyError(policy_gate_for_url(str(input_path))["message"])
    if not path.exists():
        raise FileNotFoundError(f"Audio file does not exist: {path}")
    if path.suffix.lower() not in SUPPORTED_AUDIO_EXTENSIONS:
        raise InputPolicyError(f"Unsupported audio format: {path.suffix}")

    duration = wav_duration(path) if path.suffix.lower() == ".wav" else None
    start = 0.0 if trim_start is None else float(trim_start)
    end = duration if trim_end is None else float(trim_end)
    if end is None:
        raise InputPolicyError("Non-WAV inputs require explicit trim_end until ffprobe support is added.")
    if start < 0 or end <= start:
        raise InputPolicyError("Trim range must have non-negative start and end greater than start.")
    clip_duration = end - start
    if clip_duration < MIN_DURATION_SECONDS or clip_duration > MAX_DURATION_SECONDS:
        raise InputPolicyError("MVP requires an explicit 30-90 second legal local audio clip or trim range.")

    return AudioInput(
        input_type="local_audio",
        input_uri=str(path),
        rights_attestation=rights_attestation,
        duration_seconds=duration,
        trim={"start": start, "end": end},
    )
