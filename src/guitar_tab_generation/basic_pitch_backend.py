"""Optional Basic Pitch backend integration."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .backends import BackendExecutionError, FixtureAnalysisBackend
from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_NOTE_CONFIDENCE
from .pitch_transcription import pitch_name

BasicPitchPredict = Callable[..., tuple[Any, Any, list[tuple[float, float, int, float, list[int] | None]]]]


def load_basic_pitch_predict() -> BasicPitchPredict:
    """Return the lazy-loaded Basic Pitch predict function bound to the default model path."""

    try:
        from basic_pitch import ICASSP_2022_MODEL_PATH
        from basic_pitch.inference import predict
    except ImportError as exc:  # pragma: no cover - covered by monkeypatched unit tests
        raise ImportError("basic_pitch package is not installed") from exc

    def _predict(audio_path: str, *args: Any, **kwargs: Any) -> tuple[Any, Any, list[tuple[float, float, int, float, list[int]]]]:
        return predict(audio_path, ICASSP_2022_MODEL_PATH, *args, **kwargs)

    return _predict


class BasicPitchAnalysisBackend(FixtureAnalysisBackend):
    """Real note-transcription backend powered by Spotify Basic Pitch."""

    name = "basic-pitch"

    def __init__(self, *, audio_path: Path | None, stem_name: str = "mix") -> None:
        self.audio_path = audio_path
        self.stem_name = stem_name

    def transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        if self.audio_path is None:
            raise BackendExecutionError("basic-pitch backend requires a normalized local audio path.")

        try:
            predict = load_basic_pitch_predict()
        except ImportError as exc:
            raise BackendExecutionError(
                "basic-pitch backend requires the optional Python package 'basic-pitch'. "
                "Install the ai dependency group before using this backend."
            ) from exc

        try:
            _model_output, _midi_data, raw_note_events = predict(str(self.audio_path))
        except Exception as exc:  # pragma: no cover - real runtime errors depend on local install/runtime
            raise BackendExecutionError(f"basic-pitch note backend failed: {exc}") from exc

        events: list[dict] = []
        warnings: list[dict] = []
        for index, raw in enumerate(raw_note_events, start=1):
            start_time, end_time, midi_number, amplitude = raw[:4]
            event = {
                "id": f"n{index}",
                "start": float(start_time),
                "end": float(end_time),
                "pitch_midi": int(midi_number),
                "pitch_name": pitch_name(int(midi_number)),
                "velocity": float(amplitude),
                "confidence": float(amplitude),
                "provenance": {
                    "stage": "pitch_transcription",
                    "backend": self.name,
                    "stem": self.stem_name,
                    "model": "basic_pitch_icassp_2022",
                    "runtime": "basic_pitch_python_api",
                },
            }
            events.append(event)
            if event["confidence"] < CONFIDENCE_THRESHOLDS["notes"]:
                warnings.append(
                    {
                        "code": WARNING_LOW_NOTE_CONFIDENCE,
                        "severity": "warning",
                        "message": f"Note {event['id']} is below confidence threshold.",
                        "time_range": [event["start"], event["end"]],
                    }
                )

        return events, warnings
