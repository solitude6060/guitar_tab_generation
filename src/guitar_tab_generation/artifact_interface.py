"""Static HTML interface generation from existing transcription artifacts."""
from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from .artifact_viewer import ArtifactBundle, load_artifact_bundle


def _confidence(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "unknown"


def _artifact_link(bundle: ArtifactBundle, filename: str) -> str:
    path = bundle.artifact_dir / filename
    if path.exists():
        return f'<a href="{escape(filename)}">{escape(filename)}</a>'
    return f"{escape(filename)} missing"


def _unique_chords(chords: list[dict[str, Any]]) -> str:
    labels: list[str] = []
    for chord in chords:
        label = str(chord.get("label", "")).strip()
        if label and (not labels or labels[-1] != label):
            labels.append(label)
    return " → ".join(escape(label) for label in labels) if labels else "No chord progression found"


def render_artifact_interface_html(bundle: ArtifactBundle) -> str:
    """Render an offline HTML workspace for a generated artifact directory."""

    arrangement = bundle.arrangement
    quality_report = bundle.quality_report
    confidence = arrangement.get("confidence", {})
    warnings = arrangement.get("warnings", [])
    sections = arrangement.get("section_spans", [])
    chords = arrangement.get("chord_spans", [])
    source = escape(str(arrangement.get("source", {}).get("input_uri", "unknown")))
    tempo = escape(str(arrangement.get("timebase", {}).get("tempo_bpm", "unknown")))
    quality_status = escape(str(quality_report.get("status", "unknown")))

    warning_items = "\n".join(
        f"<li><strong>{escape(str(warning.get('code', 'UNKNOWN')))}</strong>: "
        f"{escape(str(warning.get('message', '')))}</li>"
        for warning in warnings
    ) or "<li>None</li>"
    section_items = "\n".join(
        f"<li>{escape(str(section.get('label', 'Section')))}: "
        f"{float(section.get('start', 0.0)):.2f}s–{float(section.get('end', 0.0)):.2f}s "
        f"(confidence {_confidence(section.get('confidence'))})</li>"
        for section in sections
    ) or "<li>No sections found</li>"

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Artifact Interface</title>
  <style>
    body {{ font-family: system-ui, sans-serif; line-height: 1.5; margin: 2rem; max-width: 960px; }}
    header, section {{ border: 1px solid #ddd; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; }}
    .warning {{ border-color: #f59e0b; background: #fffbeb; }}
    code {{ background: #f3f4f6; padding: 0.1rem 0.25rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Artifact Interface</h1>
    <p><strong>Source:</strong> {source}</p>
    <p><strong>Tempo:</strong> {tempo} BPM</p>
    <p><strong>Quality status: {quality_status}</strong></p>
  </header>

  <section class="warning">
    <h2>Warnings</h2>
    <ul>{warning_items}</ul>
  </section>

  <section>
    <h2>Confidence</h2>
    <ul>
      <li>Overall confidence: {_confidence(confidence.get('overall'))}</li>
      <li>Notes: {_confidence(confidence.get('notes'))}</li>
      <li>Chords: {_confidence(confidence.get('chords'))}</li>
      <li>Fingering: {_confidence(confidence.get('fingering'))}</li>
    </ul>
  </section>

  <section>
    <h2>Sections</h2>
    <ul>{section_items}</ul>
  </section>

  <section>
    <h2>Chord progression</h2>
    <p>{_unique_chords(chords)}</p>
  </section>

  <section>
    <h2>Practice links</h2>
    <ul>
      <li>{_artifact_link(bundle, 'tab.md')}</li>
      <li>{_artifact_link(bundle, 'viewer.md')}</li>
      <li>{_artifact_link(bundle, 'tutorial.md')}</li>
    </ul>
  </section>
</body>
</html>
"""


def write_artifact_interface(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write an offline HTML interface and return the path written."""

    bundle = load_artifact_bundle(artifact_dir)
    destination = out_path or artifact_dir / "interface.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_artifact_interface_html(bundle), encoding="utf-8")
    return destination
