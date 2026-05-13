"""Map notes and chords into playable MVP guitar arrangement positions."""
from __future__ import annotations

from .contracts import (
    CONFIDENCE_THRESHOLDS,
    WARNING_DENSE_NOTE_SKETCH_DEGRADED,
    WARNING_UNPLAYABLE_NOTE,
)
from .fretboard import playable_positions

MAX_SKETCH_NOTES = 32


def _select_sketch_notes(note_events: list[dict]) -> tuple[list[dict], list[dict]]:
    if len(note_events) <= MAX_SKETCH_NOTES:
        return note_events, []
    step = len(note_events) / MAX_SKETCH_NOTES
    selected_indexes = {min(len(note_events) - 1, int(round(i * step))) for i in range(MAX_SKETCH_NOTES)}
    selected = [event for index, event in enumerate(note_events) if index in selected_indexes]
    if len(selected) > MAX_SKETCH_NOTES:
        selected = selected[:MAX_SKETCH_NOTES]
    warning = {
        "code": WARNING_DENSE_NOTE_SKETCH_DEGRADED,
        "severity": "warning",
        "message": f"Dense note transcription was reduced from {len(note_events)} events to {len(selected)} sketch TAB notes.",
        "time_range": [float(note_events[0]["start"]), float(note_events[-1]["end"])],
    }
    return selected, [warning]


def _choose_position(candidates: list[dict], previous: dict | None) -> dict:
    if previous is None:
        return candidates[0]
    previous_fret = int(previous["fret"])
    previous_string = int(previous["string"])
    return min(
        candidates,
        key=lambda candidate: (
            abs(int(candidate["fret"]) - previous_fret),
            abs(int(candidate["string"]) - previous_string),
            int(candidate["fret"]),
            int(candidate["string"]),
        ),
    )


def arrange_notes(note_events: list[dict]) -> tuple[list[dict], list[dict], float]:
    positions: list[dict] = []
    selected_events, warnings = _select_sketch_notes(note_events)
    confidences: list[float] = []
    previous_position: dict | None = None

    for event in selected_events:
        candidates = playable_positions(int(event["pitch_midi"]))
        if not candidates:
            warnings.append({
                "code": WARNING_UNPLAYABLE_NOTE,
                "severity": "error",
                "message": f"Note {event['id']} cannot be mapped to standard tuning fret 0–20.",
                "time_range": [event["start"], event["end"]],
            })
            continue
        chosen = _choose_position(candidates, previous_position)
        confidence = min(float(event.get("confidence", 0.7)), 0.82)
        confidences.append(confidence)
        position = {
            "note_id": event["id"],
            "string": chosen["string"],
            "fret": chosen["fret"],
            "finger": None,
            "confidence": confidence,
            "playability": "playable" if confidence >= CONFIDENCE_THRESHOLDS["fingering"] else "degraded",
        }
        positions.append(position)
        previous_position = position
    fingering_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return positions, warnings, fingering_confidence
