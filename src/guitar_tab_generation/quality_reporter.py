"""Quality checks and hard-fail classification for MVP artifacts."""
from __future__ import annotations

from .contracts import (
    CONFIDENCE_THRESHOLDS,
    HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
    HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
    HARD_FAIL_UNPLAYABLE_TAB,
    WARNING_LOW_CHORD_CONFIDENCE,
    WARNING_LOW_FINGERING_CONFIDENCE,
    WARNING_LOW_NOTE_CONFIDENCE,
    WARNING_LOW_SECTION_CONFIDENCE,
    WARNING_UNPLAYABLE_NOTE,
)
from .schema import validate_arrangement

WARNING_FOR_KIND = {
    "notes": WARNING_LOW_NOTE_CONFIDENCE,
    "chords": WARNING_LOW_CHORD_CONFIDENCE,
    "sections": WARNING_LOW_SECTION_CONFIDENCE,
    "fingering": WARNING_LOW_FINGERING_CONFIDENCE,
}


def _has_warning(arrangement: dict, code: str) -> bool:
    return any(warning.get("code") == code for warning in arrangement.get("warnings", []))


def build_quality_report(arrangement: dict, *, fixture_metadata: dict | None = None) -> dict:
    hard_failures: list[dict] = []
    warnings = list(arrangement.get("warnings", []))

    for error in validate_arrangement(arrangement):
        hard_failures.append({"code": HARD_FAIL_UNPLAYABLE_TAB, "message": error})

    if _has_warning(arrangement, WARNING_UNPLAYABLE_NOTE):
        hard_failures.append({
            "code": HARD_FAIL_UNPLAYABLE_TAB,
            "message": "At least one note could not be mapped to playable TAB.",
        })

    confidence = arrangement.get("confidence", {})
    for kind, threshold in CONFIDENCE_THRESHOLDS.items():
        value = float(confidence.get(kind, 0.0))
        if value < threshold and not _has_warning(arrangement, WARNING_FOR_KIND[kind]):
            hard_failures.append({
                "code": HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                "message": f"{kind} confidence {value:.2f} is below {threshold:.2f} without warning.",
            })

    if fixture_metadata is not None:
        if not fixture_metadata.get("rights") or not fixture_metadata.get("rubric_record"):
            hard_failures.append({
                "code": HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
                "message": "Golden fixture is missing rights metadata or manual rubric record.",
            })

    return {
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "summary": {
            "warning_count": len(warnings),
            "hard_failure_count": len(hard_failures),
        },
    }
