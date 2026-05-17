"""Deterministic chord sidecar generation from existing artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_CHORD_CONFIDENCE

CHORD_SIDECAR_SCHEMA = "guitar-tab-generation.chords.v1"
CHORD_BACKEND = "deterministic-arrangement"
PITCH_CLASS_NAMES = ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")
MAJOR_TRIAD = {0, 4, 7}
MINOR_TRIAD = {0, 3, 7}


class ChordDetectionError(ValueError):
    """Raised when a chord sidecar cannot be produced from local artifacts."""


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ChordDetectionError(f"Missing required artifact: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ChordDetectionError(f"Invalid JSON artifact: {path.name}") from exc
    if not isinstance(payload, dict):
        raise ChordDetectionError(f"JSON artifact must be an object: {path.name}")
    return payload


def _number(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _confidence(value: object) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return 0.5


def _warning_for_chord(label: str, confidence: float, threshold: float) -> dict[str, Any] | None:
    if confidence >= threshold:
        return None
    return {
        "code": WARNING_LOW_CHORD_CONFIDENCE,
        "severity": "warning",
        "message": f"Chord {label} confidence {confidence:.2f} is below threshold {threshold:.2f}.",
    }


def _chords_from_spans(spans: list[Any], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    chords: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        label = str(span.get("label", "")).strip()
        if not label:
            continue
        confidence = _confidence(span.get("confidence"))
        chord = {
            "start": _number(span.get("start")),
            "end": _number(span.get("end")),
            "label": label,
            "confidence": confidence,
            "provenance": {
                "stage": "chord_detection",
                "source": "arrangement.chord_spans",
                "backend": CHORD_BACKEND,
            },
        }
        chords.append(chord)
        warning = _warning_for_chord(label, confidence, threshold)
        if warning:
            warnings.append(warning)
    return chords, warnings


def _infer_label_from_pitch_classes(pitch_classes: set[int]) -> str:
    if not pitch_classes:
        return "Unknown"
    for root in range(12):
        normalized = {(pitch_class - root) % 12 for pitch_class in pitch_classes}
        if MAJOR_TRIAD.issubset(normalized):
            return PITCH_CLASS_NAMES[root]
        if MINOR_TRIAD.issubset(normalized):
            return f"{PITCH_CLASS_NAMES[root]}m"
    root = min(pitch_classes)
    return PITCH_CLASS_NAMES[root]


def _chord_from_notes(notes: list[Any], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_notes = [note for note in notes if isinstance(note, dict) and isinstance(note.get("pitch_midi"), (int, float))]
    if not valid_notes:
        return [], []

    pitch_classes = {int(note["pitch_midi"]) % 12 for note in valid_notes}
    confidence_values = [_confidence(note.get("confidence")) for note in valid_notes]
    confidence = sum(confidence_values) / len(confidence_values)
    label = _infer_label_from_pitch_classes(pitch_classes)
    start = min(_number(note.get("start")) for note in valid_notes)
    end = max(_number(note.get("end"), start) for note in valid_notes)
    chord = {
        "start": start,
        "end": end,
        "label": label,
        "confidence": confidence,
        "provenance": {
            "stage": "chord_detection",
            "source": "arrangement.note_events",
            "backend": CHORD_BACKEND,
        },
    }
    warning = _warning_for_chord(label, confidence, threshold)
    return [chord], [warning] if warning else []


def build_chord_sidecar(arrangement: dict[str, Any], *, artifact_dir: Path | None = None) -> dict[str, Any]:
    """Build a deterministic chord sidecar from existing arrangement evidence."""

    threshold = float(CONFIDENCE_THRESHOLDS["chords"])
    raw_spans = arrangement.get("chord_spans", [])
    spans = raw_spans if isinstance(raw_spans, list) else []
    chords, warnings = _chords_from_spans(spans, threshold)
    source_name = "arrangement.chord_spans"
    if not chords:
        raw_notes = arrangement.get("note_events", [])
        notes = raw_notes if isinstance(raw_notes, list) else []
        chords, warnings = _chord_from_notes(notes, threshold)
        source_name = "arrangement.note_events"
    if not chords:
        raise ChordDetectionError("No chord or note events are available for chord detection.")

    confidence_values = [float(chord["confidence"]) for chord in chords]
    low_confidence_count = sum(1 for value in confidence_values if value < threshold)
    return {
        "schema": CHORD_SIDECAR_SCHEMA,
        "backend": CHORD_BACKEND,
        "source": {
            "artifact_dir": str(artifact_dir) if artifact_dir is not None else ".",
            "arrangement": "arrangement.json",
            "stem_notes": [],
            "primary": source_name,
        },
        "summary": {
            "chord_count": len(chords),
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 3),
            "low_confidence_count": low_confidence_count,
        },
        "chords": chords,
        "warnings": warnings,
    }


def write_chord_sidecar(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write chords.json for an artifact directory."""

    arrangement = _load_json_object(artifact_dir / "arrangement.json")
    sidecar = build_chord_sidecar(arrangement, artifact_dir=artifact_dir)
    destination = out_path or artifact_dir / "chords.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination
