"""Deterministic section sidecar generation from existing artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_SECTION_CONFIDENCE

SECTION_SIDECAR_SCHEMA = "guitar-tab-generation.sections.v1"
SECTION_BACKEND = "deterministic-arrangement"


class SectionDetectionError(ValueError):
    """Raised when a section sidecar cannot be produced from local artifacts."""


def _load_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SectionDetectionError(f"Missing required artifact: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SectionDetectionError(f"Invalid JSON artifact: {path.name}") from exc
    if not isinstance(payload, dict):
        raise SectionDetectionError(f"JSON artifact must be an object: {path.name}")
    return payload


def _load_optional_sidecar(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _number(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _confidence(value: object) -> float:
    if isinstance(value, (int, float)):
        return max(0.0, min(1.0, float(value)))
    return 0.5


def _warning_for_section(label: str, confidence: float, threshold: float) -> dict[str, Any] | None:
    if confidence >= threshold:
        return None
    return {
        "code": WARNING_LOW_SECTION_CONFIDENCE,
        "severity": "warning",
        "message": f"Section {label} confidence {confidence:.2f} is below threshold {threshold:.2f}.",
    }


def _sections_from_spans(spans: list[Any], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sections: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        label = str(span.get("label", "")).strip()
        if not label:
            continue
        confidence = _confidence(span.get("confidence"))
        section = {
            "start": _number(span.get("start")),
            "end": _number(span.get("end")),
            "label": label,
            "confidence": confidence,
            "provenance": {
                "stage": "section_detection",
                "source": "arrangement.section_spans",
                "backend": SECTION_BACKEND,
            },
        }
        sections.append(section)
        warning = _warning_for_section(label, confidence, threshold)
        if warning:
            warnings.append(warning)
    return sections, warnings


def _sections_from_chords(chords: list[Any], threshold: float, *, source_name: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_chords = [chord for chord in chords if isinstance(chord, dict)]
    if not valid_chords:
        return [], []
    confidence_values = [_confidence(chord.get("confidence")) for chord in valid_chords]
    confidence = min(0.75, sum(confidence_values) / len(confidence_values))
    start = min(_number(chord.get("start")) for chord in valid_chords)
    end = max(_number(chord.get("end"), start) for chord in valid_chords)
    section = {
        "start": start,
        "end": end,
        "label": "Chord progression",
        "confidence": confidence,
        "provenance": {
            "stage": "section_detection",
            "source": source_name,
            "backend": SECTION_BACKEND,
        },
    }
    warning = _warning_for_section(section["label"], confidence, threshold)
    return [section], [warning] if warning else []


def _section_from_notes(notes: list[Any], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    valid_notes = [note for note in notes if isinstance(note, dict)]
    if not valid_notes:
        return [], []
    confidence_values = [_confidence(note.get("confidence")) for note in valid_notes]
    confidence = min(0.7, sum(confidence_values) / len(confidence_values))
    start = min(_number(note.get("start")) for note in valid_notes)
    end = max(_number(note.get("end"), start) for note in valid_notes)
    section = {
        "start": start,
        "end": end,
        "label": "Note sketch",
        "confidence": confidence,
        "provenance": {
            "stage": "section_detection",
            "source": "arrangement.note_events",
            "backend": SECTION_BACKEND,
        },
    }
    warning = _warning_for_section(section["label"], confidence, threshold)
    return [section], [warning] if warning else []


def build_section_sidecar(
    arrangement: dict[str, Any],
    *,
    chord_sidecar: dict[str, Any] | None = None,
    artifact_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic section sidecar from arrangement and chord evidence."""

    threshold = float(CONFIDENCE_THRESHOLDS["sections"])
    raw_spans = arrangement.get("section_spans", [])
    spans = raw_spans if isinstance(raw_spans, list) else []
    sections, warnings = _sections_from_spans(spans, threshold)
    source_name = "arrangement.section_spans"
    if not sections and chord_sidecar:
        raw_chords = chord_sidecar.get("chords", [])
        chords = raw_chords if isinstance(raw_chords, list) else []
        sections, warnings = _sections_from_chords(chords, threshold, source_name="chords.json")
        source_name = "chords.json"
    if not sections:
        raw_chords = arrangement.get("chord_spans", [])
        chords = raw_chords if isinstance(raw_chords, list) else []
        sections, warnings = _sections_from_chords(chords, threshold, source_name="arrangement.chord_spans")
        source_name = "arrangement.chord_spans"
    if not sections:
        raw_notes = arrangement.get("note_events", [])
        notes = raw_notes if isinstance(raw_notes, list) else []
        sections, warnings = _section_from_notes(notes, threshold)
        source_name = "arrangement.note_events"
    if not sections:
        raise SectionDetectionError("No section, chord, or note events are available for section detection.")

    confidence_values = [float(section["confidence"]) for section in sections]
    low_confidence_count = sum(1 for value in confidence_values if value < threshold)
    return {
        "schema": SECTION_SIDECAR_SCHEMA,
        "backend": SECTION_BACKEND,
        "source": {
            "artifact_dir": str(artifact_dir) if artifact_dir is not None else ".",
            "arrangement": "arrangement.json",
            "chords": "chords.json",
            "primary": source_name,
        },
        "summary": {
            "section_count": len(sections),
            "average_confidence": round(sum(confidence_values) / len(confidence_values), 3),
            "low_confidence_count": low_confidence_count,
        },
        "sections": sections,
        "warnings": warnings,
    }


def write_section_sidecar(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write sections.json for an artifact directory."""

    arrangement = _load_json_object(artifact_dir / "arrangement.json")
    chord_sidecar = _load_optional_sidecar(artifact_dir / "chords.json")
    sidecar = build_section_sidecar(arrangement, chord_sidecar=chord_sidecar, artifact_dir=artifact_dir)
    destination = out_path or artifact_dir / "sections.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination
