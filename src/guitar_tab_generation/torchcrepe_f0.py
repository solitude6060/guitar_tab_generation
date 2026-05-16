"""Artifact-first torchcrepe F0 calibration adapter.

P20 intentionally keeps torchcrepe as an optional runtime. Importing this module
does not import torch or torchcrepe; the dependency is loaded only when the
`f0-calibrate` command is executed.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from statistics import median
from typing import Any, Callable, Protocol

from .backends import BackendExecutionError


class TorchcrepeRuntime(Protocol):
    def load_audio(self, audio_path: str):
        """Load audio and return `(audio, sample_rate)`."""

    def predict(
        self,
        audio: Any,
        sample_rate: int,
        hop_length: int,
        fmin: float,
        fmax: float,
        model: str,
        *,
        batch_size: int,
        device: str,
        return_periodicity: bool,
    ):
        """Return pitch and periodicity tensors/sequences."""


RuntimeLoader = Callable[[], TorchcrepeRuntime]


@dataclass(frozen=True)
class TorchcrepePackageRuntime:
    torchcrepe: Any

    def load_audio(self, audio_path: str):
        return self.torchcrepe.load.audio(audio_path)

    def predict(
        self,
        audio: Any,
        sample_rate: int,
        hop_length: int,
        fmin: float,
        fmax: float,
        model: str,
        *,
        batch_size: int,
        device: str,
        return_periodicity: bool,
    ):
        return self.torchcrepe.predict(
            audio,
            sample_rate,
            hop_length,
            fmin,
            fmax,
            model,
            batch_size=batch_size,
            device=device,
            return_periodicity=return_periodicity,
        )


def load_torchcrepe_runtime() -> TorchcrepeRuntime:
    """Lazy-load the optional torchcrepe runtime."""

    try:
        import torchcrepe
    except ImportError as exc:  # pragma: no cover - covered by monkeypatched tests
        raise ImportError("torchcrepe package is not installed") from exc
    return TorchcrepePackageRuntime(torchcrepe=torchcrepe)


def _as_float_list(values: Any) -> list[float]:
    current = values
    for method in ("detach", "cpu", "numpy"):
        if hasattr(current, method):
            current = getattr(current, method)()
    if hasattr(current, "reshape"):
        current = current.reshape(-1)
    if hasattr(current, "tolist"):
        current = current.tolist()
    if current and isinstance(current[0], list):
        flattened: list[float] = []
        for row in current:
            flattened.extend(float(value) for value in row)
        return flattened
    return [float(value) for value in current]


def _hz_to_midi(frequency_hz: float) -> float | None:
    if frequency_hz <= 0 or math.isnan(frequency_hz):
        return None
    return 69.0 + 12.0 * math.log2(frequency_hz / 440.0)


class TorchcrepeF0Calibrator:
    """Map torchcrepe pitch frames onto existing note events."""

    backend = "torchcrepe-f0"

    def __init__(self, *, runtime_loader: RuntimeLoader = load_torchcrepe_runtime) -> None:
        self.runtime_loader = runtime_loader

    def calibrate(
        self,
        audio_path: Path,
        note_events: list[dict],
        *,
        device: str = "cpu",
        model: str = "tiny",
        hop_ms: float = 5.0,
        fmin: float = 50.0,
        fmax: float = 550.0,
        batch_size: int = 2048,
    ) -> dict[str, Any]:
        try:
            runtime = self.runtime_loader()
        except ImportError as exc:
            raise BackendExecutionError(
                "torchcrepe optional runtime is not installed. "
                "Install the torchcrepe route only when you intend to run f0-calibrate."
            ) from exc

        try:
            audio, sample_rate = runtime.load_audio(str(audio_path))
            hop_length = max(1, int(round(sample_rate * hop_ms / 1000.0)))
            pitch_values, periodicity_values = runtime.predict(
                audio,
                sample_rate,
                hop_length,
                fmin,
                fmax,
                model,
                batch_size=batch_size,
                device=device,
                return_periodicity=True,
            )
        except Exception as exc:  # pragma: no cover - runtime-specific failures are environment dependent
            raise BackendExecutionError(f"torchcrepe f0 calibration failed: {exc}") from exc

        pitches = _as_float_list(pitch_values)
        periodicity = _as_float_list(periodicity_values)
        frame_count = min(len(pitches), len(periodicity))
        frame_seconds = hop_length / float(sample_rate)
        note_calibrations = [
            self._calibrate_note(note, pitches[:frame_count], periodicity[:frame_count], frame_seconds)
            for note in note_events
        ]

        return {
            "backend": self.backend,
            "device": device,
            "sample_rate": sample_rate,
            "hop_length": hop_length,
            "hop_ms": hop_ms,
            "model": model,
            "fmin": fmin,
            "fmax": fmax,
            "note_calibrations": note_calibrations,
        }

    @staticmethod
    def _calibrate_note(note: dict, pitches: list[float], periodicity: list[float], frame_seconds: float) -> dict[str, Any]:
        start = float(note.get("start", 0.0))
        end = float(note.get("end", start))
        selected_indexes = [
            index
            for index in range(len(pitches))
            if start <= index * frame_seconds < end
        ]
        selected_pitches = [pitches[index] for index in selected_indexes if pitches[index] > 0]
        selected_periodicity = [periodicity[index] for index in selected_indexes]
        observed_hz = median(selected_pitches) if selected_pitches else None
        observed_midi = _hz_to_midi(observed_hz) if observed_hz is not None else None
        expected_midi = int(note["pitch_midi"]) if "pitch_midi" in note else None
        delta = observed_midi - expected_midi if observed_midi is not None and expected_midi is not None else None
        confidence = sum(selected_periodicity) / len(selected_periodicity) if selected_periodicity else 0.0
        return {
            "note_id": note.get("id"),
            "start": start,
            "end": end,
            "expected_midi": expected_midi,
            "observed_hz": observed_hz,
            "observed_midi": observed_midi,
            "delta_semitones": delta,
            "periodicity_confidence": confidence,
            "frame_count": len(selected_indexes),
            "status": "calibrated" if observed_midi is not None else "no_f0_frames",
        }


def write_f0_calibration(
    artifact_dir: Path,
    *,
    out: Path | None = None,
    device: str = "cpu",
    model: str = "tiny",
    hop_ms: float = 5.0,
    runtime_loader: RuntimeLoader | None = None,
) -> Path:
    """Write `f0_calibration.json` for an existing artifact directory."""

    audio_path = artifact_dir / "audio_normalized.wav"
    notes_path = artifact_dir / "notes.json"
    if not audio_path.exists():
        raise BackendExecutionError(f"f0-calibrate requires {audio_path.name} in the artifact directory.")
    if not notes_path.exists():
        raise BackendExecutionError(f"f0-calibrate requires {notes_path.name} in the artifact directory.")

    notes = json.loads(notes_path.read_text(encoding="utf-8"))
    if not isinstance(notes, list):
        raise BackendExecutionError("notes.json must contain a list of note events.")
    payload = TorchcrepeF0Calibrator(runtime_loader=runtime_loader or load_torchcrepe_runtime).calibrate(
        audio_path,
        notes,
        device=device,
        model=model,
        hop_ms=hop_ms,
    )
    output_path = out or artifact_dir / "f0_calibration.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
