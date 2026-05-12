"""Schema validation and hard-fail quality gates for MVP arrangements.

This module intentionally avoids third-party dependencies so it can run early in
this greenfield project and in worker integration branches before the audio
pipeline exists. It validates the shared ``arrangement.json`` contract and the
MVP hard-fail rules from the approved PRD/test spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SUPPORTED_FRET_MIN = 0
SUPPORTED_FRET_MAX = 20
SUPPORTED_STRINGS = set(range(1, 7))
DEFAULT_THRESHOLDS = {
    "notes": 0.55,
    "chords": 0.60,
    "sections": 0.50,
    "fingering": 0.65,
}
LOW_CONFIDENCE_WARNING_CODES = {
    "notes": "LOW_NOTE_CONFIDENCE",
    "chords": "LOW_CHORD_CONFIDENCE",
    "sections": "LOW_SECTION_CONFIDENCE",
    "fingering": "LOW_FINGERING_CONFIDENCE",
}
URL_INPUT_TYPES = {"url", "youtube", "youtube_url", "remote_url"}


@dataclass(frozen=True)
class GateIssue:
    """A quality gate finding."""

    code: str
    message: str
    path: str = "$"
    severity: str = "error"


@dataclass
class GateResult:
    """Validation result for an arrangement or fixture manifest."""

    issues: list[GateIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(self, code: str, message: str, path: str = "$", severity: str = "error") -> None:
        self.issues.append(GateIssue(code=code, message=message, path=path, severity=severity))

    def extend(self, issues: Iterable[GateIssue]) -> None:
        self.issues.extend(issues)

    def to_quality_report(self) -> dict[str, Any]:
        return {
            "status": "pass" if self.passed else "fail",
            "hard_fail": not self.passed,
            "issues": [issue.__dict__ for issue in self.issues],
        }


def load_json(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_arrangement(arrangement: Mapping[str, Any]) -> GateResult:
    """Validate MVP schema and hard-fail rules for an arrangement."""

    result = GateResult()
    _validate_required_schema(arrangement, result)
    _validate_url_policy_gate(arrangement, result)
    _validate_playable_positions(arrangement, result)
    _validate_low_confidence_warnings(arrangement, result)
    _validate_not_raw_dump(arrangement, result)
    return result


def validate_arrangement_file(path: str | Path) -> GateResult:
    data = load_json(path)
    if not isinstance(data, Mapping):
        result = GateResult()
        result.add("INVALID_JSON_TYPE", "arrangement.json must contain a JSON object")
        return result
    return validate_arrangement(data)


def validate_golden_fixture_manifest(manifest: Mapping[str, Any]) -> GateResult:
    """Validate Phase 0 legal golden fixture/manual rubric requirements."""

    result = GateResult()
    fixtures = manifest.get("fixtures")
    required_ids = {
        "simple_chords_30_90s",
        "single_note_riff_30_90s",
        "single_note_lead_30_90s",
    }
    if not isinstance(fixtures, Sequence) or isinstance(fixtures, (str, bytes)):
        result.add("MISSING_GOLDEN_FIXTURES", "manifest.fixtures must list the three MVP golden fixtures", "$.fixtures")
        return result

    seen: set[str] = set()
    for index, fixture in enumerate(fixtures):
        path = f"$.fixtures[{index}]"
        if not isinstance(fixture, Mapping):
            result.add("INVALID_FIXTURE", "fixture entry must be an object", path)
            continue
        fixture_id = fixture.get("id")
        if isinstance(fixture_id, str):
            seen.add(fixture_id)
        duration = fixture.get("duration_seconds")
        if not _is_number(duration) or not 30 <= float(duration) <= 90:
            result.add("INVALID_FIXTURE_DURATION", "golden fixture duration must be 30-90 seconds", f"{path}.duration_seconds")
        if not fixture.get("rights"):
            result.add("MISSING_RIGHTS_RECORD", "golden fixture must include source/license or self-made rights record", f"{path}.rights")
        rubric = fixture.get("manual_rubric")
        if not isinstance(rubric, Mapping):
            result.add("MISSING_MANUAL_RUBRIC", "golden fixture must include manual rubric baseline/record", f"{path}.manual_rubric")
        else:
            for key in ("recognizability", "chord_usability", "tab_playability", "rhythm_readability", "honesty"):
                score = rubric.get(key)
                if not _is_number(score) or not 1 <= float(score) <= 5:
                    result.add("INVALID_RUBRIC_SCORE", f"manual rubric score {key!r} must be 1-5", f"{path}.manual_rubric.{key}")
            if not rubric.get("reviewer"):
                result.add("MISSING_RUBRIC_REVIEWER", "manual rubric must record reviewer", f"{path}.manual_rubric.reviewer")

    missing = sorted(required_ids - seen)
    if missing:
        result.add("MISSING_GOLDEN_FIXTURES", "missing required golden fixture(s): " + ", ".join(missing), "$.fixtures")
    return result


def validate_golden_fixture_manifest_file(path: str | Path) -> GateResult:
    data = load_json(path)
    if not isinstance(data, Mapping):
        result = GateResult()
        result.add("INVALID_JSON_TYPE", "golden fixture manifest must contain a JSON object")
        return result
    return validate_golden_fixture_manifest(data)


def _validate_required_schema(arrangement: Mapping[str, Any], result: GateResult) -> None:
    required = {
        "schema_version": str,
        "timebase": Mapping,
        "source": Mapping,
        "confidence": Mapping,
        "warnings": Sequence,
        "note_events": Sequence,
        "chord_spans": Sequence,
        "section_spans": Sequence,
        "fretboard": Mapping,
        "positions": Sequence,
        "render_hints": Mapping,
    }
    for key, expected_type in required.items():
        value = arrangement.get(key)
        if value is None:
            result.add("MISSING_SCHEMA_FIELD", f"missing required field {key!r}", f"$.{key}")
            continue
        if expected_type is Sequence and isinstance(value, (str, bytes)):
            result.add("INVALID_SCHEMA_FIELD", f"field {key!r} must be an array", f"$.{key}")
        elif not isinstance(value, expected_type):
            result.add("INVALID_SCHEMA_FIELD", f"field {key!r} has invalid type", f"$.{key}")

    timebase = arrangement.get("timebase")
    if isinstance(timebase, Mapping):
        for key in ("sample_rate", "tempo_bpm", "beats", "bars", "time_signature"):
            if key not in timebase:
                result.add("MISSING_SCHEMA_FIELD", f"missing timebase field {key!r}", f"$.timebase.{key}")

    source = arrangement.get("source")
    if isinstance(source, Mapping):
        for key in ("input_type", "input_uri", "rights_attestation", "trim", "stems"):
            if key not in source:
                result.add("MISSING_SCHEMA_FIELD", f"missing source field {key!r}", f"$.source.{key}")

    fretboard = arrangement.get("fretboard")
    if isinstance(fretboard, Mapping):
        fret_range = fretboard.get("supported_fret_range")
        if not isinstance(fret_range, Mapping):
            result.add("MISSING_SCHEMA_FIELD", "fretboard.supported_fret_range is required", "$.fretboard.supported_fret_range")
        else:
            if fret_range.get("min") != SUPPORTED_FRET_MIN or fret_range.get("max") != SUPPORTED_FRET_MAX:
                result.add("UNSUPPORTED_FRET_RANGE", "MVP supported fret range must be min=0, max=20", "$.fretboard.supported_fret_range")
        for key in ("tuning", "capo"):
            if key not in fretboard:
                result.add("MISSING_SCHEMA_FIELD", f"missing fretboard field {key!r}", f"$.fretboard.{key}")


def _validate_url_policy_gate(arrangement: Mapping[str, Any], result: GateResult) -> None:
    source = arrangement.get("source")
    if not isinstance(source, Mapping):
        return
    input_type = str(source.get("input_type", "")).lower()
    if input_type in URL_INPUT_TYPES:
        rights = str(source.get("rights_attestation", "")).lower()
        policy = source.get("policy_gate")
        if rights not in {"i_own_rights", "allowlisted", "user_provided"} or policy != "passed":
            result.add(
                "URL_POLICY_BYPASS",
                "URL/YouTube input must remain stubbed or pass explicit rights/allowlist policy gate before processing",
                "$.source",
            )


def _validate_playable_positions(arrangement: Mapping[str, Any], result: GateResult) -> None:
    positions = arrangement.get("positions")
    if not isinstance(positions, Sequence) or isinstance(positions, (str, bytes)):
        return
    for index, position in enumerate(positions):
        path = f"$.positions[{index}]"
        if not isinstance(position, Mapping):
            result.add("INVALID_POSITION", "position must be an object", path)
            continue
        string = position.get("string")
        fret = position.get("fret")
        playability = str(position.get("playability", "playable")).lower()
        degraded = playability in {"degraded", "unmapped", "chord_only"}
        if string not in SUPPORTED_STRINGS:
            if not degraded:
                result.add("UNPLAYABLE_TAB", "TAB position string must be 1-6 or explicitly degraded", f"{path}.string")
        if not isinstance(fret, int) or not SUPPORTED_FRET_MIN <= fret <= SUPPORTED_FRET_MAX:
            if not degraded:
                result.add("UNPLAYABLE_TAB", "TAB position fret must be 0-20 or explicitly degraded", f"{path}.fret")
        if playability in {"unplayable", "impossible"}:
            result.add("UNPLAYABLE_TAB", "unplayable TAB must hard fail instead of being silently rendered", f"{path}.playability")


def _validate_low_confidence_warnings(arrangement: Mapping[str, Any], result: GateResult) -> None:
    confidence = arrangement.get("confidence")
    thresholds = DEFAULT_THRESHOLDS.copy()
    if isinstance(confidence, Mapping) and isinstance(confidence.get("thresholds"), Mapping):
        for key in thresholds:
            value = confidence["thresholds"].get(key)
            if _is_number(value):
                thresholds[key] = float(value)

    warning_codes = _warning_codes(arrangement.get("warnings"))
    if isinstance(confidence, Mapping):
        for key in ("notes", "chords", "sections", "fingering"):
            value = confidence.get(key)
            if _is_number(value) and float(value) < thresholds[key]:
                expected = LOW_CONFIDENCE_WARNING_CODES[key]
                if expected not in warning_codes:
                    result.add("LOW_CONFIDENCE_WITHOUT_WARNING", f"{key} confidence below threshold requires {expected}", f"$.confidence.{key}")

    collections = {
        "notes": ("note_events", "LOW_NOTE_CONFIDENCE"),
        "chords": ("chord_spans", "LOW_CHORD_CONFIDENCE"),
        "sections": ("section_spans", "LOW_SECTION_CONFIDENCE"),
        "fingering": ("positions", "LOW_FINGERING_CONFIDENCE"),
    }
    for key, (collection_name, warning_code) in collections.items():
        values = arrangement.get(collection_name)
        if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
            continue
        for index, item in enumerate(values):
            if isinstance(item, Mapping) and _is_number(item.get("confidence")) and float(item["confidence"]) < thresholds[key]:
                if warning_code not in warning_codes:
                    result.add(
                        "LOW_CONFIDENCE_WITHOUT_WARNING",
                        f"low-confidence {collection_name} entry requires {warning_code}",
                        f"$.{collection_name}[{index}].confidence",
                    )


def _validate_not_raw_dump(arrangement: Mapping[str, Any], result: GateResult) -> None:
    if not arrangement.get("section_spans"):
        result.add("RAW_MIDI_DUMP", "arrangement must include section spans, not only raw notes", "$.section_spans")
    if not arrangement.get("chord_spans") and not arrangement.get("positions"):
        result.add("RAW_MIDI_DUMP", "arrangement must include chords or playable TAB positions", "$")
    render_hints = arrangement.get("render_hints")
    if isinstance(render_hints, Mapping) and not render_hints.get("show_warnings_inline", False):
        result.add("WARNINGS_NOT_RENDERED", "render hints must request inline warning display", "$.render_hints.show_warnings_inline")


def _warning_codes(warnings: Any) -> set[str]:
    if not isinstance(warnings, Sequence) or isinstance(warnings, (str, bytes)):
        return set()
    codes = set()
    for warning in warnings:
        if isinstance(warning, Mapping) and isinstance(warning.get("code"), str):
            codes.add(warning["code"])
    return codes


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate arrangement.json and MVP hard-fail quality gates.")
    parser.add_argument("path", help="Path to arrangement.json or golden fixture manifest")
    parser.add_argument("--golden-manifest", action="store_true", help="Validate Phase 0 golden fixture manifest instead of arrangement.json")
    parser.add_argument("--report", help="Optional path to write quality_report.json")
    args = parser.parse_args(argv)

    result = validate_golden_fixture_manifest_file(args.path) if args.golden_manifest else validate_arrangement_file(args.path)
    report = result.to_quality_report()
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.report:
        Path(args.report).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
