"""Quality reporting and MVP hard-fail enforcement."""
from __future__ import annotations

from typing import Any, Iterable

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
    WARNING_UNPLAYABLE_NOTE,
)
from .schema import validate_arrangement

WARNING_FOR_KIND = {
    "notes": WARNING_LOW_NOTE_CONFIDENCE,
    "chords": WARNING_LOW_CHORD_CONFIDENCE,
    "sections": WARNING_LOW_SECTION_CONFIDENCE,
    "fingering": WARNING_LOW_FINGERING_CONFIDENCE,
}
COLLECTION_FOR_KIND = {
    "notes": "note_events",
    "chords": "chord_spans",
    "sections": "section_spans",
    "fingering": "positions",
}


def warning(code: str, message: str, *, severity: str = "warning", time_range: list[float] | None = None) -> dict:
    item = {"code": code, "severity": severity, "message": message}
    if time_range is not None:
        item["time_range"] = time_range
    return item


def _warning_codes(warnings: Iterable[dict]) -> set[str]:
    return {str(item.get("code")) for item in warnings}




def _has_warning(arrangement: dict, code: str) -> bool:
    return code in _warning_codes(arrangement.get("warnings", []))

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
        if playability not in {"playable", "degraded", "unplayable"}:
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


def _append_hard_failure(hard_failures: list[dict], code: str, message: str, *, path: str | None = None) -> None:
    failure: dict[str, str] = {"code": code, "message": message}
    if path is not None:
        failure["path"] = path
    hard_failures.append(failure)


def _confidence_thresholds(arrangement: dict) -> dict[str, float]:
    thresholds = dict(CONFIDENCE_THRESHOLDS)
    configured = arrangement.get("confidence", {}).get("thresholds", {})
    for kind in thresholds:
        value = configured.get(kind)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            thresholds[kind] = float(value)
    return thresholds


def _hard_fail_low_confidence_without_warning(arrangement: dict, hard_failures: list[dict]) -> None:
    confidence = arrangement.get("confidence", {})
    thresholds = _confidence_thresholds(arrangement)

    for kind, threshold in thresholds.items():
        warning_code = WARNING_FOR_KIND[kind]
        aggregate = confidence.get(kind)
        if isinstance(aggregate, (int, float)) and not isinstance(aggregate, bool):
            if float(aggregate) < threshold and not _has_warning(arrangement, warning_code):
                _append_hard_failure(
                    hard_failures,
                    HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                    f"{kind} confidence {float(aggregate):.2f} is below {threshold:.2f} without {warning_code}.",
                    path=f"$.confidence.{kind}",
                )

        collection_name = COLLECTION_FOR_KIND[kind]
        for index, item in enumerate(arrangement.get(collection_name, [])):
            if not isinstance(item, dict):
                continue
            value = item.get("confidence")
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if float(value) < threshold and not _has_warning(arrangement, warning_code):
                    _append_hard_failure(
                        hard_failures,
                        HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
                        f"{collection_name}[{index}] confidence {float(value):.2f} is below {threshold:.2f} without {warning_code}.",
                        path=f"$.{collection_name}[{index}].confidence",
                    )


def _hard_fail_unplayable_positions(arrangement: dict, hard_failures: list[dict]) -> None:
    for index, position in enumerate(arrangement.get("positions", [])):
        if not isinstance(position, dict):
            _append_hard_failure(hard_failures, HARD_FAIL_UNPLAYABLE_TAB, "TAB position must be an object.", path=f"$.positions[{index}]")
            continue
        playability = str(position.get("playability", "playable")).lower()
        if playability in {"unplayable", "impossible"}:
            _append_hard_failure(
                hard_failures,
                HARD_FAIL_UNPLAYABLE_TAB,
                "Unplayable TAB must fail or be degraded before rendering.",
                path=f"$.positions[{index}].playability",
            )


def validate_golden_fixture_record(fixture_metadata: dict[str, Any]) -> list[dict]:
    """Return hard failures for missing legal fixture/manual rubric evidence."""

    hard_failures: list[dict] = []
    if not fixture_metadata.get("rights") and not fixture_metadata.get("rights_attestation"):
        _append_hard_failure(
            hard_failures,
            HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
            "Golden fixture is missing source/license/self-created rights evidence.",
            path="$.rights_attestation",
        )
    if not fixture_metadata.get("rubric_record") and not fixture_metadata.get("manual_rubric"):
        _append_hard_failure(
            hard_failures,
            HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
            "Golden fixture is missing manual rubric record.",
            path="$.rubric_record",
        )
    return hard_failures


def build_quality_report(arrangement: dict, *, fixture_metadata: dict | None = None) -> dict:
    hard_failures: list[dict] = []
    warnings = list(arrangement.get("warnings", []))

    for error in validate_arrangement(arrangement):
        _append_hard_failure(hard_failures, HARD_FAIL_UNPLAYABLE_TAB, error)

    if _has_warning(arrangement, WARNING_UNPLAYABLE_NOTE):
        _append_hard_failure(
            hard_failures,
            HARD_FAIL_UNPLAYABLE_TAB,
            "At least one note could not be mapped to playable TAB.",
        )

    _hard_fail_unplayable_positions(arrangement, hard_failures)
    _hard_fail_low_confidence_without_warning(arrangement, hard_failures)

    if fixture_metadata is not None:
        hard_failures.extend(validate_golden_fixture_record(fixture_metadata))

    checks = {
        "schema": not any(failure["code"] == HARD_FAIL_UNPLAYABLE_TAB for failure in hard_failures),
        "low_confidence_warnings": not any(
            failure["code"] == HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING for failure in hard_failures
        ),
        "golden_fixture_record": not any(
            failure["code"] == HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD for failure in hard_failures
        ),
    }

    return {
        "status": "failed" if hard_failures else "passed",
        "hard_failures": hard_failures,
        "warnings": warnings,
        "checks": checks,
        "summary": {
            "warning_count": len(warnings),
            "hard_failure_count": len(hard_failures),
        },
    }
