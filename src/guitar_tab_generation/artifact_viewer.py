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


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ArtifactViewerError(f"Invalid JSON artifact: {path.name}") from exc
    if not isinstance(data, dict):
        raise ArtifactViewerError(f"JSON artifact must be an object: {path.name}")
    return data


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


def _practice_readiness(arrangement: dict[str, Any], quality_report: dict[str, Any]) -> str:
    status = quality_report.get("status", "unknown")
    warning_count = len(arrangement.get("warnings", []))
    overall = arrangement.get("confidence", {}).get("overall")
    if status == "passed" and isinstance(overall, (int, float)) and overall >= 0.75 and warning_count == 0:
        return "Ready for first-pass practice. Open `tab.md` and start at 50% tempo."
    if status == "passed":
        return "Usable for guided practice, but review warnings first. Open `tab.md` before rehearsing."
    return "Not practice-ready yet. Fix quality failures before treating the TAB as playable."


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
