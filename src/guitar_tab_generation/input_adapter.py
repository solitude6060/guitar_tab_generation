from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable
from urllib.parse import urlparse
import wave

from .contracts import (
    FULL_SONG_CHUNK_OVERLAP_SECONDS,
    FULL_SONG_CHUNK_SECONDS,
    MAX_CLIP_DURATION_SECONDS,
    MAX_FULL_SONG_DURATION_SECONDS,
    MIN_CLIP_DURATION_SECONDS,
    MIN_FULL_SONG_DURATION_SECONDS,
    SUPPORTED_AUDIO_EXTENSIONS,
)

SUPPORTED_DURATION_MESSAGE = (
    "Supported legal local audio duration is either a 30-90 second practice clip "
    "or a 3-8 minute full song (180-480 seconds)."
)

CommandRunner = Callable[[list[str]], tuple[int, str, str]]


class InputPolicyError(ValueError):
    """Raised when an input violates MVP input policy."""


class InputError(ValueError):
    """Raised when local audio input cannot be resolved."""


class PolicyGateError(InputPolicyError):
    """Raised when URL input hits the MVP policy gate."""


@dataclass(frozen=True)
class AudioInput:
    input_type: str
    input_uri: str
    rights_attestation: str
    duration_seconds: float | None
    source_duration_seconds: float | None
    duration_class: str
    processing_plan: dict
    trim: dict[str, float]

    @property
    def path(self) -> Path:
        return Path(self.input_uri)

    @property
    def trim_start(self) -> float:
        return float(self.trim["start"])

    @property
    def trim_end(self) -> float:
        return float(self.trim["end"])


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
            "Provide a legal local 30-90 second audio clip or 3-8 minute full song instead."
        ),
    }


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        frames = handle.getnframes()
        rate = handle.getframerate()
    return frames / float(rate)


def _run_command(command: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=30)
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    except subprocess.SubprocessError as exc:
        return 1, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def ffprobe_duration(path: Path, run_command: CommandRunner | None = None) -> float:
    """Read local non-WAV media duration with ffprobe."""

    runner = run_command or _run_command
    code, stdout, stderr = runner([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ])
    if code != 0:
        detail = stderr or stdout or "unknown ffprobe error"
        raise InputPolicyError(f"local ffprobe could not read audio duration: {detail}")
    try:
        duration = float(stdout.strip().splitlines()[0])
    except (IndexError, ValueError) as exc:
        raise InputPolicyError("local ffprobe returned an invalid audio duration.") from exc
    if duration <= 0:
        raise InputPolicyError("local ffprobe returned a non-positive audio duration.")
    return duration


def classify_duration(duration_seconds: float) -> str:
    """Return the supported duration class or raise a policy error."""

    if MIN_CLIP_DURATION_SECONDS <= duration_seconds <= MAX_CLIP_DURATION_SECONDS:
        return "clip"
    if MIN_FULL_SONG_DURATION_SECONDS <= duration_seconds <= MAX_FULL_SONG_DURATION_SECONDS:
        return "full_song"
    raise InputPolicyError(SUPPORTED_DURATION_MESSAGE)


def build_processing_plan(duration_seconds: float, duration_class: str) -> dict:
    """Build local-first processing metadata for later AI stages."""

    if duration_class == "clip":
        return {
            "mode": "single_pass_clip",
            "target_length_seconds": float(duration_seconds),
            "chunk_seconds": float(duration_seconds),
            "overlap_seconds": 0.0,
            "chunks": [{"index": 1, "start": 0.0, "end": round(float(duration_seconds), 3)}],
        }

    chunks: list[dict[str, float | int]] = []
    cursor = 0.0
    index = 1
    while cursor < duration_seconds:
        end = min(duration_seconds, cursor + FULL_SONG_CHUNK_SECONDS)
        chunks.append({"index": index, "start": round(cursor, 3), "end": round(end, 3)})
        if end >= duration_seconds:
            break
        cursor = max(0.0, end - FULL_SONG_CHUNK_OVERLAP_SECONDS)
        index += 1

    return {
        "mode": "chunked_full_song",
        "target_length_seconds": round(float(duration_seconds), 3),
        "chunk_seconds": FULL_SONG_CHUNK_SECONDS,
        "overlap_seconds": FULL_SONG_CHUNK_OVERLAP_SECONDS,
        "chunks": chunks,
    }


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

    duration = wav_duration(path) if path.suffix.lower() == ".wav" else ffprobe_duration(path)
    start = 0.0 if trim_start is None else float(trim_start)
    end = duration if trim_end is None else float(trim_end)
    if start < 0 or end <= start:
        raise InputPolicyError("Trim range must have non-negative start and end greater than start.")
    clip_duration = end - start
    duration_class = classify_duration(clip_duration)

    return AudioInput(
        input_type="local_audio",
        input_uri=str(path),
        rights_attestation=rights_attestation,
        duration_seconds=round(float(clip_duration), 3),
        source_duration_seconds=round(float(duration), 3) if duration is not None else None,
        duration_class=duration_class,
        processing_plan=build_processing_plan(clip_duration, duration_class),
        trim={"start": start, "end": end},
    )


def policy_gate_message(url: str) -> str:
    """Return the user-facing URL policy gate message without downloading anything."""
    return policy_gate_for_url(url)["message"]


def resolve_local_audio(
    input_uri: str | Path,
    *,
    trim_start: float | None = None,
    trim_end: float | None = None,
    rights_attestation: str = "user_provided",
) -> AudioInput:
    """Resolve a legal local audio input; URL inputs are blocked by policy."""
    if is_url(str(input_uri)):
        raise PolicyGateError(policy_gate_message(str(input_uri)))
    try:
        return validate_local_audio(
            input_uri,
            trim_start=trim_start,
            trim_end=trim_end,
            rights_attestation=rights_attestation,
        )
    except FileNotFoundError as exc:
        raise InputError(str(exc)) from exc
    except InputPolicyError:
        raise


def load_fixture_metadata(audio_path: Path) -> dict | None:
    """Load optional fixture metadata for deterministic MVP tests.

    Lookup order keeps ad-hoc sidecars supported while allowing the repository's
    golden fixtures to keep metadata/rubric records in ``fixtures/metadata``.
    Missing metadata remains allowed for non-golden local audio.
    """
    import json

    candidates = [audio_path.with_suffix(audio_path.suffix + ".fixture.json")]
    if audio_path.parent.name == "fixtures":
        candidates.append(audio_path.parent / "metadata" / f"{audio_path.stem}.json")

    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return None
