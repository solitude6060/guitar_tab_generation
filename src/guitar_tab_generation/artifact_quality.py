"""Artifact-level quality report v2 aggregation."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
from typing import Any

from .artifact_viewer import summarize_f0_calibration
from .backends import BackendExecutionError
from .quality_reporter import build_quality_report


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BackendExecutionError(f"{path.name} is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise BackendExecutionError(f"{path.name} must be a JSON object.")
    return payload


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 3)


def _stem_availability(stem_manifest: dict[str, Any] | None) -> dict[str, Any]:
    if not stem_manifest:
        return {"available": False, "count": 0, "stems": []}
    stems = [
        str(stem.get("name"))
        for stem in stem_manifest.get("stems", [])
        if isinstance(stem, dict) and stem.get("name")
    ]
    return {"available": bool(stems), "count": len(stems), "stems": stems}


def _stem_note_summaries(artifact_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    stem_notes_dir = artifact_dir / "stem_notes"
    if not stem_notes_dir.exists():
        return {"available": False, "count": 0, "stems": []}, []

    summaries: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for path in sorted(stem_notes_dir.glob("*.notes.json")):
        payload = _read_json(path) or {}
        stem = str(payload.get("stem") or path.name.removesuffix(".notes.json"))
        notes = [note for note in payload.get("notes", []) if isinstance(note, dict)]
        confidences = [
            float(note["confidence"])
            for note in notes
            if isinstance(note.get("confidence"), (int, float)) and not isinstance(note.get("confidence"), bool)
        ]
        warnings = [warning for warning in payload.get("warnings", []) if isinstance(warning, dict)]
        summaries.append(
            {
                "stem": stem,
                "backend": str(payload.get("backend", "unknown")),
                "note_count": len(notes),
                "average_confidence": _average(confidences),
                "warning_count": len(warnings),
            }
        )
        events.extend(notes)

    return {"available": bool(summaries), "count": len(summaries), "stems": summaries}, events


def _backend_confidence(arrangement: dict[str, Any], stem_note_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[float]] = defaultdict(list)
    for collection in ("note_events", "chord_spans", "section_spans"):
        for item in arrangement.get(collection, []):
            if not isinstance(item, dict):
                continue
            provenance = item.get("provenance", {})
            backend = str(provenance.get("backend", "unknown")) if isinstance(provenance, dict) else "unknown"
            stem = str(provenance.get("stem", "mix")) if isinstance(provenance, dict) else "mix"
            confidence = item.get("confidence")
            if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
                groups[(backend, stem)].append(float(confidence))

    for note in stem_note_events:
        provenance = note.get("provenance", {})
        backend = str(provenance.get("backend", "unknown")) if isinstance(provenance, dict) else "unknown"
        stem = str(provenance.get("stem", "unknown")) if isinstance(provenance, dict) else "unknown"
        confidence = note.get("confidence")
        if isinstance(confidence, (int, float)) and not isinstance(confidence, bool):
            groups[(backend, stem)].append(float(confidence))

    return [
        {
            "backend": backend,
            "stem": stem,
            "event_count": len(values),
            "average_confidence": _average(values),
        }
        for (backend, stem), values in sorted(groups.items())
    ]


def build_artifact_quality_report_v2(artifact_dir: Path) -> dict[str, Any]:
    """Build a v2 quality report from core artifacts and optional sidecars."""

    arrangement = _read_json(artifact_dir / "arrangement.json")
    if arrangement is None:
        raise BackendExecutionError("quality-report requires arrangement.json in the artifact directory.")
    existing = _read_json(artifact_dir / "quality_report.json") or build_quality_report(arrangement)
    stem_manifest = _read_json(artifact_dir / "stem_manifest.json")
    f0_calibration = _read_json(artifact_dir / "f0_calibration.json")
    stem_notes, stem_note_events = _stem_note_summaries(artifact_dir)
    pitch_risk = summarize_f0_calibration(f0_calibration)

    report = dict(existing)
    report["schema_version"] = 2
    report["artifact_summary"] = {
        "stem_availability": _stem_availability(stem_manifest),
        "stem_notes": stem_notes,
        "pitch_risk": {
            "available": bool(pitch_risk.get("available")),
            "total_notes": pitch_risk.get("total_notes", 0),
            "risk_count": pitch_risk.get("risk_count", 0),
            "risk_note_ids": [str(note.get("note_id", "unknown")) for note in pitch_risk.get("risk_notes", [])],
        },
        "backend_confidence": _backend_confidence(arrangement, stem_note_events),
    }
    report["summary"] = {
        **dict(report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}),
        "quality_version": 2,
    }
    return report


def write_artifact_quality_report_v2(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write a v2 quality report and return the destination path."""

    report = build_artifact_quality_report_v2(artifact_dir)
    destination = out_path or artifact_dir / "quality_report.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination
