"""Map notes and chords into playable MVP guitar arrangement positions."""
from __future__ import annotations

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_UNPLAYABLE_NOTE
from .fretboard import playable_positions


def arrange_notes(note_events: list[dict]) -> tuple[list[dict], list[dict], float]:
    positions: list[dict] = []
    warnings: list[dict] = []
    confidences: list[float] = []
    for event in note_events:
        candidates = playable_positions(int(event["pitch_midi"]))
        if not candidates:
            warnings.append({
                "code": WARNING_UNPLAYABLE_NOTE,
                "severity": "error",
                "message": f"Note {event['id']} cannot be mapped to standard tuning fret 0–20.",
                "time_range": [event["start"], event["end"]],
            })
            continue
        chosen = candidates[0]
        confidence = min(float(event.get("confidence", 0.7)), 0.82)
        confidences.append(confidence)
        positions.append({
            "note_id": event["id"],
            "string": chosen["string"],
            "fret": chosen["fret"],
            "finger": None,
            "confidence": confidence,
            "playability": "playable" if confidence >= CONFIDENCE_THRESHOLDS["fingering"] else "low_confidence",
        })
    fingering_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return positions, warnings, fingering_confidence
