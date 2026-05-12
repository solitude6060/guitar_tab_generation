"""Quality reporting and MVP hard-fail enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import (
    CONFIDENCE_THRESHOLDS,
    HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
    HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
    HARD_FAIL_RAW_MIDI_ONLY,
    HARD_FAIL_UNPLAYABLE_TAB,
    WARNING_LOW_CHORD_CONFIDENCE,
    WARNING_LOW_FINGERING_CONFIDENCE,
    WARNING_LOW_NOTE_CONFIDENCE,
    WARNING_LOW_SECTION_CONFIDENCE,
)
from .schema import validate_arrangement


@dataclass(frozen=True)
class QualityReport:
    """Machine-readable quality gate result."""

    status: str
    hard_failures: list[dict]
    warnings: list[dict]
    schema_errors: list[str]
    summary: str

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "hard_failures": self.hard_failures,
            "warnings": self.warnings,
            "schema_errors": self.schema_errors,
            "summary": self.summary,
        }


def warning(code: str, message: str, *, severity: str = "warning", time_range: list[float] | None = None) -> dict:
    item = {"code": code, "severity": severity, "message": message}
    if time_range is not None:
        item["time_range"] = time_range
    return item


def _warning_codes(warnings: Iterable[dict]) -> set[str]:
    return {str(item.get("code")) for item in warnings}


def _missing_confidence_warnings(arrangement: dict) -> list[dict]:
    warnings = arrangement.get("warnings", [])
    warning_codes = _warning_codes(warnings)
    missing: list[dict] = []

    for note in arrangement.get("note_events", []):
        if float(note.get("confidence", 1.0)) < CONFIDENCE_THRESHOLDS["notes"] and WARNING_LOW_NOTE_CONFIDENCE not in warning_codes:
            missing.append(
                {
                    "code": HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                    "message": f"Low-confidence note {note.get('id')} has no warning.",
                    "event": note.get("id"),
                }
            )

    for chord in arrangement.get("chord_spans", []):
        if float(chord.get("confidence", 1.0)) < CONFIDENCE_THRESHOLDS["chords"] and WARNING_LOW_CHORD_CONFIDENCE not in warning_codes:
            missing.append(
                {
                    "code": HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                    "message": f"Low-confidence chord {chord.get('label')} has no warning.",
                    "event": chord.get("label"),
                }
            )

    for section in arrangement.get("section_spans", []):
        if float(section.get("confidence", 1.0)) < CONFIDENCE_THRESHOLDS["sections"] and WARNING_LOW_SECTION_CONFIDENCE not in warning_codes:
            missing.append(
                {
                    "code": HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                    "message": f"Low-confidence section {section.get('label')} has no warning.",
                    "event": section.get("label"),
                }
            )

    for position in arrangement.get("positions", []):
        if float(position.get("confidence", 1.0)) < CONFIDENCE_THRESHOLDS["fingering"] and WARNING_LOW_FINGERING_CONFIDENCE not in warning_codes:
            missing.append(
                {
                    "code": HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                    "message": f"Low-confidence fingering for {position.get('note_id') or position.get('chord_id')} has no warning.",
                    "event": position.get("note_id") or position.get("chord_id"),
                }
            )

    return missing


def _unplayable_failures(arrangement: dict) -> list[dict]:
    failures: list[dict] = []
    note_ids = {note.get("id") for note in arrangement.get("note_events", [])}
    positions = arrangement.get("positions", [])

    for position in positions:
        string = position.get("string")
        fret = position.get("fret")
        note_id = position.get("note_id")
        playability = position.get("playability", "playable")
        if not isinstance(string, int) or not 1 <= string <= 6 or not isinstance(fret, int) or not 0 <= fret <= 20:
            failures.append({"code": HARD_FAIL_UNPLAYABLE_TAB, "message": f"Illegal string/fret in position {position!r}"})
        if note_id and note_id not in note_ids:
            failures.append({"code": HARD_FAIL_UNPLAYABLE_TAB, "message": f"Position references unknown note_id {note_id!r}."})
        if playability not in {"playable", "degraded", "unmapped"}:
            failures.append({"code": HARD_FAIL_UNPLAYABLE_TAB, "message": f"Unknown playability {playability!r}."})

    if arrangement.get("note_events") and not positions:
        failures.append({"code": HARD_FAIL_UNPLAYABLE_TAB, "message": "Note events exist but no playable TAB positions were produced."})

    return failures


def _fixture_record_failures(metadata: dict | None) -> list[dict]:
    if not metadata or not metadata.get("golden_fixture"):
        return []
    missing = []
    if not metadata.get("rights") and not metadata.get("rights_attestation"):
        missing.append("rights")
    if not metadata.get("manual_rubric_record"):
        missing.append("manual_rubric_record")
    if missing:
        return [
            {
                "code": HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
                "message": "Golden fixture metadata is missing: " + ", ".join(missing),
            }
        ]
    return []


def evaluate_quality(arrangement: dict, *, fixture_metadata: dict | None = None) -> QualityReport:
    schema_errors = validate_arrangement(arrangement)
    failures: list[dict] = []
    failures.extend({"code": "SCHEMA_ERROR", "message": error} for error in schema_errors)
    failures.extend(_unplayable_failures(arrangement))
    failures.extend(_missing_confidence_warnings(arrangement))
    failures.extend(_fixture_record_failures(fixture_metadata))

    if arrangement.get("note_events") and not arrangement.get("chord_spans") and not arrangement.get("section_spans"):
        failures.append({"code": HARD_FAIL_RAW_MIDI_ONLY, "message": "Output contains notes without sections/chords/readable arrangement context."})

    status = "failed" if failures else "passed"
    summary = "MVP quality gate passed." if status == "passed" else "MVP quality gate failed."
    return QualityReport(
        status=status,
        hard_failures=failures,
        warnings=list(arrangement.get("warnings", [])),
        schema_errors=schema_errors,
        summary=summary,
    )


def build_quality_report(arrangement: dict, *, fixture_metadata: dict | None = None) -> dict:
    """Compatibility wrapper returning the machine-readable quality report dict."""
    return evaluate_quality(arrangement, fixture_metadata=fixture_metadata).to_dict()
