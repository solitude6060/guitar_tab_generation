"""Baseline chord analysis using fixture metadata or safe defaults."""
from __future__ import annotations

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_CHORD_CONFIDENCE


def analyze_chords(duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
    warnings: list[dict] = []
    if fixture_metadata and fixture_metadata.get("chord_spans"):
        spans = fixture_metadata["chord_spans"]
    else:
        spans = [
            {"start": 0.0, "end": duration_seconds / 2, "label": "G", "confidence": 0.68},
            {"start": duration_seconds / 2, "end": duration_seconds, "label": "C", "confidence": 0.68},
        ]
    normalized: list[dict] = []
    for span in spans:
        item = {
            "start": float(span["start"]),
            "end": float(span["end"]),
            "label": str(span["label"]),
            "confidence": float(span.get("confidence", 0.65)),
            "provenance": {"stage": "tonal_chord_analysis", "stem": "mix"},
        }
        normalized.append(item)
        if item["confidence"] < CONFIDENCE_THRESHOLDS["chords"]:
            warnings.append({
                "code": WARNING_LOW_CHORD_CONFIDENCE,
                "severity": "warning",
                "message": f"Chord {item['label']} is below confidence threshold.",
                "time_range": [item["start"], item["end"]],
            })
    return normalized, warnings
