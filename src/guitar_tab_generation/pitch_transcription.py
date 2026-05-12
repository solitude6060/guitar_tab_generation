"""Baseline pitch transcription adapter."""
from __future__ import annotations

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_NOTE_CONFIDENCE

PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def pitch_name(midi: int) -> str:
    return f"{PITCH_NAMES[midi % 12]}{midi // 12 - 1}"


def transcribe_notes(duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
    warnings: list[dict] = []
    raw_notes = (fixture_metadata or {}).get("note_events")
    if not raw_notes:
        raw_notes = [
            {"start": 1.0, "end": 1.35, "pitch_midi": 64, "velocity": 0.7, "confidence": 0.74},
            {"start": 2.0, "end": 2.35, "pitch_midi": 67, "velocity": 0.7, "confidence": 0.72},
            {"start": 3.0, "end": 3.35, "pitch_midi": 69, "velocity": 0.7, "confidence": 0.70},
        ]
    events: list[dict] = []
    for index, raw in enumerate(raw_notes, start=1):
        event = {
            "id": raw.get("id", f"n{index}"),
            "start": float(raw["start"]),
            "end": float(raw["end"]),
            "pitch_midi": int(raw["pitch_midi"]),
            "pitch_name": pitch_name(int(raw["pitch_midi"])),
            "velocity": float(raw.get("velocity", 0.7)),
            "confidence": float(raw.get("confidence", 0.7)),
            "provenance": {"stage": "pitch_transcription", "stem": "mix", "model": "baseline_fixture"},
        }
        events.append(event)
        if event["confidence"] < CONFIDENCE_THRESHOLDS["notes"]:
            warnings.append({
                "code": WARNING_LOW_NOTE_CONFIDENCE,
                "severity": "warning",
                "message": f"Note {event['id']} is below confidence threshold.",
                "time_range": [event["start"], event["end"]],
            })
    return events, warnings
