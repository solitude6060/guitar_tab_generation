"""Read generated artifacts and render a lightweight Markdown demo view."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = ("arrangement.json", "quality_report.json", "tab.md")


class ArtifactViewerError(ValueError):
    """Raised when an artifact directory cannot be rendered safely."""


@dataclass(frozen=True)
class ArtifactBundle:
    artifact_dir: Path
    arrangement: dict[str, Any]
    quality_report: dict[str, Any]
    tab_markdown: str
    f0_calibration: dict[str, Any] | None = None
    chord_detection: dict[str, Any] | None = None
    section_detection: dict[str, Any] | None = None


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactViewerError(f"Invalid JSON artifact: {path.name}") from exc
    if not isinstance(data, dict):
        raise ArtifactViewerError(f"JSON artifact must be an object: {path.name}")
    return data


def _read_optional_json_object(path: Path) -> dict[str, Any] | None:
    """Read optional sidecar JSON; legacy non-object sidecars are ignored."""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactViewerError(f"Invalid JSON artifact: {path.name}") from exc
    if isinstance(data, dict):
        return data
    return None


def load_artifact_bundle(artifact_dir: Path) -> ArtifactBundle:
    """Load the artifacts required by the Markdown viewer."""

    if not artifact_dir.exists():
        raise ArtifactViewerError(f"Artifact directory does not exist: {artifact_dir}")
    if not artifact_dir.is_dir():
        raise ArtifactViewerError(f"Artifact path is not a directory: {artifact_dir}")

    missing = [name for name in REQUIRED_ARTIFACTS if not (artifact_dir / name).exists()]
    if missing:
        raise ArtifactViewerError(f"Missing required artifact(s): {', '.join(missing)}")

    return ArtifactBundle(
        artifact_dir=artifact_dir,
        arrangement=_read_json(artifact_dir / "arrangement.json"),
        quality_report=_read_json(artifact_dir / "quality_report.json"),
        tab_markdown=(artifact_dir / "tab.md").read_text(encoding="utf-8"),
        f0_calibration=_read_json(artifact_dir / "f0_calibration.json")
        if (artifact_dir / "f0_calibration.json").exists()
        else None,
        chord_detection=_read_optional_json_object(artifact_dir / "chords.json")
        if (artifact_dir / "chords.json").exists()
        else None,
        section_detection=_read_optional_json_object(artifact_dir / "sections.json")
        if (artifact_dir / "sections.json").exists()
        else None,
    )


def _format_confidence(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "unknown"


def _format_seconds(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}s"
    return "unknown"


def _duration_seconds(arrangement: dict[str, Any]) -> object:
    explicit = arrangement.get("duration_seconds")
    if isinstance(explicit, (int, float)):
        return explicit
    ends: list[float] = []
    for key in ("section_spans", "chord_spans", "note_events"):
        for event in arrangement.get(key, []):
            end = event.get("end")
            if isinstance(end, (int, float)):
                ends.append(float(end))
    return max(ends) if ends else None


def _chord_progression(chords: list[dict[str, Any]]) -> str:
    labels: list[str] = []
    for chord in chords:
        label = str(chord.get("label", "")).strip()
        if label and (not labels or labels[-1] != label):
            labels.append(label)
    return " → ".join(labels) if labels else "No chord spans found"


def _label_progression(items: list[dict[str, Any]], *, empty: str) -> str:
    labels: list[str] = []
    for item in items:
        label = str(item.get("label", "")).strip()
        if label and (not labels or labels[-1] != label):
            labels.append(label)
    return " → ".join(labels) if labels else empty


def _practice_readiness(arrangement: dict[str, Any], quality_report: dict[str, Any]) -> str:
    status = quality_report.get("status", "unknown")
    warning_count = len(arrangement.get("warnings", []))
    overall = arrangement.get("confidence", {}).get("overall")
    if status == "passed" and isinstance(overall, (int, float)) and overall >= 0.75 and warning_count == 0:
        return "Ready for first-pass practice. Open `tab.md` and start at 50% tempo."
    if status == "passed":
        return "Usable for guided practice, but review warnings first. Open `tab.md` before rehearsing."
    return "Not practice-ready yet. Fix quality failures before treating the TAB as playable."


def _format_signed(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):+.2f}"
    return "unknown"


def summarize_f0_calibration(f0_calibration: dict[str, Any] | None) -> dict[str, Any]:
    """Summarize optional F0 calibration into user-facing pitch-risk notes."""

    if not f0_calibration:
        return {"available": False, "total_notes": 0, "risk_count": 0, "risk_notes": []}

    raw_notes = f0_calibration.get("note_calibrations", [])
    note_calibrations = raw_notes if isinstance(raw_notes, list) else []
    risk_notes: list[dict[str, Any]] = []
    for note in note_calibrations:
        if not isinstance(note, dict):
            continue
        delta = note.get("delta_semitones")
        confidence = note.get("periodicity_confidence")
        status = str(note.get("status", "unknown"))
        is_delta_risk = isinstance(delta, (int, float)) and abs(float(delta)) >= 0.5
        is_confidence_risk = isinstance(confidence, (int, float)) and float(confidence) < 0.5
        is_status_risk = status != "calibrated"
        if is_delta_risk or is_confidence_risk or is_status_risk:
            risk_notes.append(note)

    return {
        "available": True,
        "backend": f0_calibration.get("backend", "unknown"),
        "device": f0_calibration.get("device", "unknown"),
        "total_notes": len(note_calibrations),
        "risk_count": len(risk_notes),
        "risk_notes": risk_notes,
    }


def format_f0_calibration_markdown(f0_calibration: dict[str, Any] | None) -> list[str]:
    """Return Markdown lines for optional F0 calibration summary."""

    summary = summarize_f0_calibration(f0_calibration)
    if not summary["available"]:
        return []

    lines = [
        "",
        "## F0 Calibration",
        f"- Backend: {summary.get('backend', 'unknown')}",
        f"- Device: {summary.get('device', 'unknown')}",
        f"- Pitch-risk notes: {summary['risk_count']} / {summary['total_notes']}",
    ]
    if summary["risk_notes"]:
        lines.append("- Risk details:")
        for note in summary["risk_notes"][:8]:
            note_id = note.get("note_id", "unknown")
            delta = _format_signed(note.get("delta_semitones"))
            confidence = _format_confidence(note.get("periodicity_confidence"))
            lines.append(f"  - {note_id}: delta {delta} semitones, periodicity {confidence}")
    else:
        lines.append("- No pitch-risk notes detected.")
    return lines


def format_quality_summary_markdown(quality_report: dict[str, Any]) -> list[str]:
    """Return Markdown lines for optional quality report v2 summary."""

    summary = quality_report.get("artifact_summary")
    if not isinstance(summary, dict):
        return []

    stem_availability = summary.get("stem_availability", {})
    pitch_risk = summary.get("pitch_risk", {})
    backend_confidence = summary.get("backend_confidence", [])
    stems = stem_availability.get("stems", []) if isinstance(stem_availability, dict) else []
    pitch_risk_summary = pitch_risk if isinstance(pitch_risk, dict) else {}
    stem_text = ", ".join(str(stem) for stem in stems) if stems else "none"
    lines = [
        "",
        "## Quality Summary",
        f"- Available stems: {stem_text}",
        f"- Pitch-risk notes: {pitch_risk_summary.get('risk_count', 0)} / {pitch_risk_summary.get('total_notes', 0)}",
    ]
    if isinstance(backend_confidence, list) and backend_confidence:
        lines.append("- Backend confidence:")
        for item in backend_confidence[:8]:
            if not isinstance(item, dict):
                continue
            backend = item.get("backend", "unknown")
            stem = item.get("stem", "unknown")
            confidence = _format_confidence(item.get("average_confidence"))
            count = item.get("event_count", 0)
            lines.append(f"  - {backend} / {stem}: {confidence} across {count} events")
    else:
        lines.append("- Backend confidence: unavailable")
    return lines


def summarize_chord_detection(chord_detection: dict[str, Any] | None) -> dict[str, Any]:
    """Summarize optional chord detection sidecar for viewer surfaces."""

    if not chord_detection:
        return {"available": False, "chords": [], "warnings": []}
    chords = chord_detection.get("chords", [])
    warnings = chord_detection.get("warnings", [])
    summary = chord_detection.get("summary", {})
    return {
        "available": True,
        "backend": chord_detection.get("backend", "unknown"),
        "chords": chords if isinstance(chords, list) else [],
        "warnings": warnings if isinstance(warnings, list) else [],
        "average_confidence": summary.get("average_confidence") if isinstance(summary, dict) else None,
        "low_confidence_count": summary.get("low_confidence_count", 0) if isinstance(summary, dict) else 0,
    }


def format_chord_detection_markdown(chord_detection: dict[str, Any] | None) -> list[str]:
    """Return Markdown lines for optional chord detection sidecar summary."""

    summary = summarize_chord_detection(chord_detection)
    if not summary["available"]:
        return []

    lines = [
        "",
        "## Chord Detection Sidecar",
        f"- Backend: {summary.get('backend', 'unknown')}",
        f"- Chord progression: {_chord_progression(summary['chords'])}",
        f"- Average confidence: {_format_confidence(summary.get('average_confidence'))}",
        f"- Low-confidence chords: {summary.get('low_confidence_count', 0)}",
    ]
    if summary["warnings"]:
        lines.append("- Warnings:")
        for warning in summary["warnings"][:8]:
            if not isinstance(warning, dict):
                continue
            lines.append(f"  - {warning.get('code', 'UNKNOWN')}: {warning.get('message', '')}")
    else:
        lines.append("- Warnings: none")
    return lines


def summarize_section_detection(section_detection: dict[str, Any] | None) -> dict[str, Any]:
    """Summarize optional section detection sidecar for viewer surfaces."""

    if not section_detection:
        return {"available": False, "sections": [], "warnings": []}
    sections = section_detection.get("sections", [])
    warnings = section_detection.get("warnings", [])
    summary = section_detection.get("summary", {})
    return {
        "available": True,
        "backend": section_detection.get("backend", "unknown"),
        "sections": sections if isinstance(sections, list) else [],
        "warnings": warnings if isinstance(warnings, list) else [],
        "average_confidence": summary.get("average_confidence") if isinstance(summary, dict) else None,
        "low_confidence_count": summary.get("low_confidence_count", 0) if isinstance(summary, dict) else 0,
        "section_count": summary.get("section_count", 0) if isinstance(summary, dict) else 0,
    }


def format_section_detection_markdown(section_detection: dict[str, Any] | None) -> list[str]:
    """Return Markdown lines for optional section detection sidecar summary."""

    summary = summarize_section_detection(section_detection)
    if not summary["available"]:
        return []

    lines = [
        "",
        "## Section Detection Sidecar",
        f"- Backend: {summary.get('backend', 'unknown')}",
        f"- Sections: {_label_progression(summary['sections'], empty='No sections found')}",
        f"- Section count: {summary.get('section_count', 0)}",
        f"- Average confidence: {_format_confidence(summary.get('average_confidence'))}",
        f"- Low-confidence sections: {summary.get('low_confidence_count', 0)}",
    ]
    if summary["warnings"]:
        lines.append("- Warnings:")
        for warning in summary["warnings"][:8]:
            if not isinstance(warning, dict):
                continue
            lines.append(f"  - {warning.get('code', 'UNKNOWN')}: {warning.get('message', '')}")
    else:
        lines.append("- Warnings: none")
    return lines


def render_artifact_viewer_markdown(bundle: ArtifactBundle) -> str:
    """Render a stable Markdown summary for demos and practice review."""

    arrangement = bundle.arrangement
    quality_report = bundle.quality_report
    timebase = arrangement.get("timebase", {})
    confidence = arrangement.get("confidence", {})
    sections = arrangement.get("section_spans", [])
    chords = arrangement.get("chord_spans", [])
    warnings = arrangement.get("warnings", [])

    lines = [
        "# Artifact Viewer",
        "",
        "## Summary",
        f"- Source: {arrangement.get('source', {}).get('input_uri', 'unknown')}",
        f"- Tempo: {timebase.get('tempo_bpm', 'unknown')} BPM",
        f"- Duration: {_format_seconds(_duration_seconds(arrangement))}",
        f"- Overall confidence: {_format_confidence(confidence.get('overall'))}",
        f"- Notes/chords/fingering confidence: {_format_confidence(confidence.get('notes'))} / {_format_confidence(confidence.get('chords'))} / {_format_confidence(confidence.get('fingering'))}",
        f"- Quality status: {quality_report.get('status', 'unknown')}",
        "",
        "## Sections",
    ]
    if sections:
        for section in sections:
            lines.append(
                f"- {section.get('label', 'unknown')}: "
                f"{float(section.get('start', 0.0)):.2f}s–{float(section.get('end', 0.0)):.2f}s "
                f"(confidence {_format_confidence(section.get('confidence'))})"
            )
    else:
        lines.append("- No sections found")

    lines.extend(["", "## Chord progression", f"- {_chord_progression(chords)}", "", "## Warnings"])
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning.get('code', 'UNKNOWN')}: {warning.get('message', '')}")
    else:
        lines.append("- None")

    lines.extend(format_f0_calibration_markdown(bundle.f0_calibration))
    lines.extend(format_chord_detection_markdown(bundle.chord_detection))
    lines.extend(format_section_detection_markdown(bundle.section_detection))
    lines.extend(format_quality_summary_markdown(quality_report))

    lines.extend([
        "",
        "## Practice readiness",
        f"- {_practice_readiness(arrangement, quality_report)}",
        "- Original TAB: Open `tab.md` in this artifact directory.",
        "",
    ])
    return "\n".join(lines)


def write_artifact_viewer(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write a Markdown artifact viewer and return the path written."""

    bundle = load_artifact_bundle(artifact_dir)
    destination = out_path or artifact_dir / "viewer.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_artifact_viewer_markdown(bundle), encoding="utf-8")
    return destination
