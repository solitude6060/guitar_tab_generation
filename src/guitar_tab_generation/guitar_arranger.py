from __future__ import annotations

STANDARD_TUNING = [40, 45, 50, 55, 59, 64]  # strings 6..1: E2 A2 D3 G3 B3 E4
FRET_MIN = 0
FRET_MAX = 20


class ArrangementError(ValueError):
    pass


def arrange(timebase: dict, source: dict, chord_spans: list[dict], note_events: list[dict]) -> dict:
    warnings = []
    positions = []
    for note in note_events:
        position = map_note_to_position(note["pitch_midi"])
        if position is None:
            warnings.append(
                {
                    "code": "UNPLAYABLE_NOTE",
                    "severity": "error",
                    "message": f"No standard-tuning fretboard position for note {note['id']} within frets 0-20.",
                    "time_range": [note["start"], note["end"]],
                }
            )
            continue
        positions.append(
            {
                "note_id": note["id"],
                **position,
                "finger": None,
                "confidence": min(0.8, note.get("confidence", 0.0)),
                "playability": "playable",
            }
        )

    section_end = timebase["bars"][min(7, len(timebase["bars"]) - 1)]["end"] if timebase["bars"] else 0.0
    return {
        "schema_version": "0.1.0",
        "timebase": timebase,
        "source": source,
        "confidence": {
            "overall": 0.72,
            "rhythm": 0.8,
            "chords": 0.72 if chord_spans else 0.0,
            "notes": 0.78 if note_events else 0.0,
            "fingering": 0.75 if positions else 0.0,
            "thresholds": {"notes": 0.55, "chords": 0.60, "sections": 0.50, "fingering": 0.65},
        },
        "warnings": warnings,
        "note_events": note_events,
        "chord_spans": chord_spans,
        "section_spans": [{"start": 0.0, "end": section_end, "label": "Sketch A", "confidence": 0.66}],
        "fretboard": {
            "tuning": ["E2", "A2", "D3", "G3", "B3", "E4"],
            "capo": 0,
            "supported_fret_range": {"min": FRET_MIN, "max": FRET_MAX},
        },
        "positions": positions,
        "render_hints": {
            "tab_density": "sketch",
            "show_rhythm_slashes": True,
            "show_warnings_inline": True,
            "preferred_output": "markdown",
        },
    }


def map_note_to_position(pitch_midi: int) -> dict | None:
    candidates = []
    for idx, open_midi in enumerate(STANDARD_TUNING):
        fret = pitch_midi - open_midi
        if FRET_MIN <= fret <= FRET_MAX:
            string = 6 - idx
            candidates.append({"string": string, "fret": fret})
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item["fret"], item["string"]))
