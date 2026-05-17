"""Map notes and chords into playable MVP guitar arrangement positions."""
from __future__ import annotations

from .contracts import (
    CONFIDENCE_THRESHOLDS,
    WARNING_DENSE_NOTE_SKETCH_DEGRADED,
    WARNING_LARGE_POSITION_SHIFT,
    WARNING_MAX_STRETCH_EXCEEDED,
    WARNING_UNPLAYABLE_NOTE,
)
from .fretboard import playable_positions

MAX_SKETCH_NOTES = 32
LARGE_POSITION_SHIFT_FRETS = 7
MAX_STRETCH_FRETS = 4
SIMULTANEOUS_WINDOW_SECONDS = 0.05


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


def _hand_position(fret: int) -> int:
    return max(1, fret - 1)


def _finger_for_fret(fret: int, hand_position: int) -> int | None:
    if fret == 0:
        return None
    return max(1, min(4, fret - hand_position + 1))


def _append_stretch_warnings(positions: list[dict], warnings: list[dict]) -> None:
    windows: dict[float, list[dict]] = {}
    for position in positions:
        start = float(position.get("start", 0.0))
        bucket = round(start / SIMULTANEOUS_WINDOW_SECONDS) * SIMULTANEOUS_WINDOW_SECONDS
        windows.setdefault(bucket, []).append(position)
    for bucket_positions in windows.values():
        fretted = [int(position["fret"]) for position in bucket_positions if int(position["fret"]) > 0]
        if len(fretted) < 2:
            continue
        stretch = max(fretted) - min(fretted)
        if stretch > MAX_STRETCH_FRETS:
            warnings.append(
                {
                    "code": WARNING_MAX_STRETCH_EXCEEDED,
                    "severity": "warning",
                    "message": f"Fretted note window spans {stretch} frets, above max stretch {MAX_STRETCH_FRETS}.",
                    "time_range": [bucket_positions[0]["start"], bucket_positions[-1]["end"]],
                }
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
        fret = int(chosen["fret"])
        hand_position = _hand_position(fret)
        position_shift = abs(fret - int(previous_position["fret"])) if previous_position is not None else 0
        if position_shift > LARGE_POSITION_SHIFT_FRETS:
            warnings.append(
                {
                    "code": WARNING_LARGE_POSITION_SHIFT,
                    "severity": "warning",
                    "message": f"Position shift of {position_shift} frets may be hard to play cleanly.",
                    "time_range": [event["start"], event["end"]],
                }
            )
        position = {
            "note_id": event["id"],
            "string": chosen["string"],
            "fret": fret,
            "finger": _finger_for_fret(fret, hand_position),
            "hand_position": hand_position,
            "position_shift": position_shift,
            "start": event["start"],
            "end": event["end"],
            "confidence": confidence,
            "playability": "playable" if confidence >= CONFIDENCE_THRESHOLDS["fingering"] else "degraded",
        }
        positions.append(position)
        previous_position = position
    _append_stretch_warnings(positions, warnings)
    fingering_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return positions, warnings, fingering_confidence
