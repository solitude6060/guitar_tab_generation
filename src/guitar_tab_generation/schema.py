"""Arrangement JSON construction and validation."""
from __future__ import annotations

from .contracts import CONFIDENCE_THRESHOLDS, SCHEMA_VERSION, STANDARD_TUNING, SUPPORTED_FRET_RANGE

REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "timebase",
    "source",
    "confidence",
    "warnings",
    "note_events",
    "chord_spans",
    "section_spans",
    "fretboard",
    "positions",
    "render_hints",
}


def base_arrangement(*, sample_rate: int, tempo_bpm: float, duration_seconds: float, source: dict) -> dict:
    beat_seconds = 60.0 / tempo_bpm
    beats = [
        {"time": round(i * beat_seconds, 3), "beat": (i % 4) + 1}
        for i in range(max(1, int(duration_seconds / beat_seconds)))
    ]
    bars = []
    for index in range(max(1, len(beats) // 4)):
        start = beats[index * 4]["time"]
        end = min(duration_seconds, start + beat_seconds * 4)
        bars.append({"index": index + 1, "start": round(start, 3), "end": round(end, 3)})
    return {
        "schema_version": SCHEMA_VERSION,
        "timebase": {
            "sample_rate": sample_rate,
            "tempo_bpm": tempo_bpm,
            "beats": beats,
            "bars": bars,
            "time_signature": "4/4",
        },
        "source": source,
        "confidence": {
            "overall": 0.0,
            "rhythm": 0.8,
            "chords": 0.0,
            "notes": 0.0,
            "fingering": 0.0,
            "thresholds": CONFIDENCE_THRESHOLDS,
        },
        "warnings": [],
        "note_events": [],
        "chord_spans": [],
        "section_spans": [],
        "fretboard": {
            "tuning": STANDARD_TUNING,
            "capo": 0,
            "supported_fret_range": SUPPORTED_FRET_RANGE,
        },
        "positions": [],
        "render_hints": {
            "tab_density": "sketch",
            "show_rhythm_slashes": True,
            "show_warnings_inline": True,
            "preferred_output": "markdown",
        },
    }


def validate_arrangement(arrangement: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL_KEYS - arrangement.keys())
    if missing:
        errors.append(f"Missing top-level keys: {', '.join(missing)}")
    fret_range = arrangement.get("fretboard", {}).get("supported_fret_range", {})
    if fret_range.get("min") != 0 or fret_range.get("max") != 20:
        errors.append("MVP fret range must be 0–20.")
    for position in arrangement.get("positions", []):
        string = position.get("string")
        fret = position.get("fret")
        if not isinstance(string, int) or not 1 <= string <= 6:
            errors.append(f"Invalid TAB string for position {position!r}")
        if not isinstance(fret, int) or not 0 <= fret <= 20:
            errors.append(f"Invalid TAB fret for position {position!r}")
    return errors
