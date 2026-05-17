"""Evaluation fixture metrics and regression report generation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import CONFIDENCE_THRESHOLDS

EVAL_REPORT_SCHEMA = "guitar-tab-generation.eval-report.v1"


class EvaluationReportError(ValueError):
    """Raised when evaluation inputs cannot be read."""


def _read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise EvaluationReportError(f"Missing JSON file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EvaluationReportError(f"Invalid JSON file: {path}") from exc
    if not isinstance(payload, dict):
        raise EvaluationReportError(f"JSON file must contain an object: {path}")
    return payload


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def _confidence_values(items: list[Any]) -> list[float]:
    values: list[float] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        confidence = item.get("confidence")
        if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            values.append(float(confidence))
    return values


def _confidence_metrics(items: list[Any], threshold: float) -> dict[str, Any]:
    values = _confidence_values(items)
    return {
        "count": len([item for item in items if isinstance(item, dict)]),
        "average_confidence": _average(values),
        "low_confidence_count": sum(1 for value in values if value < threshold),
    }


def _playability_metrics(arrangement: dict[str, Any]) -> dict[str, Any]:
    positions = [position for position in arrangement.get("positions", []) if isinstance(position, dict)]
    playable = [position for position in positions if str(position.get("playability", "")).lower() == "playable"]
    warnings = [warning for warning in arrangement.get("warnings", []) if isinstance(warning, dict)]
    return {
        "position_count": len(positions),
        "playable_count": len(playable),
        "playable_rate": round(len(playable) / len(positions), 3) if positions else None,
        "warning_count": len(warnings),
    }


def _rubric_summary(manifest_dir: Path, fixture: dict[str, Any], failures: list[dict[str, Any]]) -> dict[str, Any]:
    fixture_id = str(fixture.get("id", "unknown"))
    rubric_path = fixture.get("rubric_record")
    if not isinstance(rubric_path, str) or not rubric_path:
        failures.append({"fixture_id": fixture_id, "code": "MISSING_RUBRIC_RECORD", "message": "Fixture has no rubric_record."})
        return {"available": False, "average_score": None}
    resolved = manifest_dir / rubric_path
    if not resolved.exists():
        failures.append({"fixture_id": fixture_id, "code": "MISSING_RUBRIC_RECORD", "message": f"Rubric record missing: {rubric_path}"})
        return {"available": False, "average_score": None}
    rubric = _read_json_object(resolved)
    average = rubric.get("average_score")
    if isinstance(average, (int, float)) and not isinstance(average, bool):
        average_score = float(average)
    else:
        scores = rubric.get("scores", {})
        score_values = [
            float(value)
            for value in (scores.values() if isinstance(scores, dict) else [])
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        average_score = _average(score_values)
    hard_failures = rubric.get("hard_failures", [])
    if isinstance(hard_failures, list) and hard_failures:
        failures.append({"fixture_id": fixture_id, "code": "RUBRIC_HARD_FAILURE", "message": "Rubric contains hard failures."})
    return {
        "available": True,
        "reviewer": rubric.get("reviewer", "unknown"),
        "average_score": average_score,
        "hard_failure_count": len(hard_failures) if isinstance(hard_failures, list) else 0,
    }


def _rights_summary(fixture: dict[str, Any], failures: list[dict[str, Any]]) -> dict[str, Any]:
    fixture_id = str(fixture.get("id", "unknown"))
    source_statement = fixture.get("source_statement")
    rights_attestation = fixture.get("rights_attestation")
    ok = bool(source_statement) and bool(rights_attestation)
    if not ok:
        failures.append({"fixture_id": fixture_id, "code": "MISSING_RIGHTS_EVIDENCE", "message": "Fixture lacks rights evidence."})
    return {
        "available": ok,
        "source_statement": source_statement or "",
        "rights_attestation": rights_attestation or "",
    }


def _artifact_metrics(artifact_root: Path, fixture: dict[str, Any], failures: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture_id = str(fixture.get("id", "unknown"))
    expected = fixture.get("expected_outputs", {})
    if not isinstance(expected, dict):
        failures.append({"fixture_id": fixture_id, "code": "MISSING_ARTIFACT", "message": "Fixture has no expected_outputs object."})
        return {"available": False}, {}

    arrangement_rel = expected.get("arrangement_json")
    quality_rel = expected.get("quality_report_json")
    missing = []
    if not isinstance(arrangement_rel, str) or not (artifact_root / arrangement_rel).exists():
        missing.append("arrangement_json")
    if not isinstance(quality_rel, str) or not (artifact_root / quality_rel).exists():
        missing.append("quality_report_json")
    if missing:
        failures.append({"fixture_id": fixture_id, "code": "MISSING_ARTIFACT", "message": f"Missing artifact(s): {', '.join(missing)}"})
        return {"available": False, "missing": missing}, {}

    arrangement = _read_json_object(artifact_root / str(arrangement_rel))
    quality_report = _read_json_object(artifact_root / str(quality_rel))
    status = str(quality_report.get("status", "unknown"))
    if status != "passed":
        failures.append({"fixture_id": fixture_id, "code": "QUALITY_REPORT_FAILED", "message": f"quality_report status is {status}."})

    notes = arrangement.get("note_events", [])
    chords = arrangement.get("chord_spans", [])
    sections = arrangement.get("section_spans", [])
    metrics = {
        "notes": _confidence_metrics(notes if isinstance(notes, list) else [], float(CONFIDENCE_THRESHOLDS["notes"])),
        "chords": _confidence_metrics(chords if isinstance(chords, list) else [], float(CONFIDENCE_THRESHOLDS["chords"])),
        "sections": _confidence_metrics(sections if isinstance(sections, list) else [], float(CONFIDENCE_THRESHOLDS["sections"])),
        "playability": _playability_metrics(arrangement),
    }
    for metric_name in ("notes", "chords", "sections"):
        metric = metrics[metric_name]
        if metric["low_confidence_count"]:
            failures.append(
                {
                    "fixture_id": fixture_id,
                    "code": "LOW_METRIC_CONFIDENCE",
                    "message": f"{metric_name} has {metric['low_confidence_count']} event(s) below threshold.",
                }
            )
    playable_rate = metrics["playability"]["playable_rate"]
    if isinstance(playable_rate, (int, float)) and playable_rate < 1.0:
        failures.append(
            {
                "fixture_id": fixture_id,
                "code": "LOW_PLAYABILITY_RATE",
                "message": f"Playable rate is {playable_rate:.3f}.",
            }
        )
    return {"available": True, "quality_status": status}, metrics


def build_eval_report(artifact_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Build an evaluation report from fixture metadata and generated artifacts."""

    manifest = _read_json_object(manifest_path)
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list):
        raise EvaluationReportError("Evaluation manifest must contain a fixtures list.")

    failures: list[dict[str, Any]] = []
    fixture_reports: list[dict[str, Any]] = []
    rubric_scores: list[float] = []
    confidence_values: list[float] = []
    artifact_count = 0
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            continue
        fixture_id = str(fixture.get("id", "unknown"))
        rights = _rights_summary(fixture, failures)
        rubric = _rubric_summary(manifest_path.parent, fixture, failures)
        if isinstance(rubric.get("average_score"), (int, float)):
            rubric_scores.append(float(rubric["average_score"]))
        artifact, metrics = _artifact_metrics(artifact_root, fixture, failures)
        if artifact.get("available"):
            artifact_count += 1
            for metric in (metrics.get("notes", {}), metrics.get("chords", {}), metrics.get("sections", {})):
                confidence = metric.get("average_confidence") if isinstance(metric, dict) else None
                if isinstance(confidence, (int, float)):
                    confidence_values.append(float(confidence))
        fixture_reports.append(
            {
                "id": fixture_id,
                "rights": rights,
                "rubric": rubric,
                "artifact": artifact,
                "metrics": metrics,
            }
        )

    status = "passed" if not failures else "failed"
    return {
        "schema": EVAL_REPORT_SCHEMA,
        "thresholds": {
            "notes": CONFIDENCE_THRESHOLDS["notes"],
            "chords": CONFIDENCE_THRESHOLDS["chords"],
            "sections": CONFIDENCE_THRESHOLDS["sections"],
            "fingering": CONFIDENCE_THRESHOLDS["fingering"],
        },
        "summary": {
            "status": status,
            "fixture_count": len(fixture_reports),
            "artifact_count": artifact_count,
            "failure_count": len(failures),
            "average_confidence": _average(confidence_values),
            "average_rubric_score": _average(rubric_scores),
        },
        "fixtures": fixture_reports,
        "failures": failures,
    }


def write_eval_report(artifact_root: Path, manifest_path: Path, out_path: Path | None = None) -> Path:
    """Write eval_report.json for a generated artifact root."""

    report = build_eval_report(artifact_root, manifest_path)
    destination = out_path or artifact_root / "eval_report.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination
