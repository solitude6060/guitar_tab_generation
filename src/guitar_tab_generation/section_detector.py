"""Baseline section detection for the MVP placeholder pipeline."""
from __future__ import annotations

from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_SECTION_CONFIDENCE


def detect_sections(duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
    """Return section spans from fixture metadata or a safe single-section sketch.

    The MVP scaffold is intentionally conservative: it produces reviewable
    structure with confidence/provenance hooks without pretending to solve full
    section detection yet.
    """
    raw_sections = (fixture_metadata or {}).get("section_spans") or [
        {"start": 0.0, "end": duration_seconds, "label": "Sketch A", "confidence": 0.66}
    ]
    sections: list[dict] = []
    warnings: list[dict] = []
    for raw in raw_sections:
        section = {
            "start": float(raw["start"]),
            "end": float(raw["end"]),
            "label": str(raw.get("label", "Sketch")),
            "confidence": float(raw.get("confidence", 0.66)),
        }
        sections.append(section)
        if section["confidence"] < CONFIDENCE_THRESHOLDS["sections"]:
            warnings.append(
                {
                    "code": WARNING_LOW_SECTION_CONFIDENCE,
                    "severity": "warning",
                    "message": f"Section {section['label']} is below confidence threshold.",
                    "time_range": [section["start"], section["end"]],
                }
            )
    return sections, warnings
