"""Static HTML interface generation from existing transcription artifacts."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any

from .artifact_viewer import (
    ArtifactBundle,
    load_artifact_bundle,
    summarize_chord_detection,
    summarize_f0_calibration,
)


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


def _render_daw_track_item(bundle: ArtifactBundle, track: dict[str, Any]) -> str:
    midi = str(track.get("midi", "")).strip()
    musicxml = str(track.get("musicxml", "")).strip()
    name = escape(str(track.get("name", "Track")))

    if not midi or not musicxml:
        return "<li>Invalid DAW track entry</li>"

    return (
        f"<li>{name}: "
        f"{_artifact_link(bundle, f'daw_bundle/{midi}')} "
        f"/ {_artifact_link(bundle, f'daw_bundle/{musicxml}')}</li>"
    )


def _format_daw_bundle_section(bundle: ArtifactBundle) -> str:
    daw_dir = bundle.artifact_dir / "daw_bundle"
    if not daw_dir.exists():
        return (
            "<p>尚未建立 DAW 匯出包。</p>"
            "<p>可執行：<code>guitar-tab-generation export . --format daw</code></p>"
        )

    manifest_path = daw_dir / "daw_manifest.json"
    tracks: list[dict[str, Any]] = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            tracks = list(manifest.get("tracks", []))
            strategy = manifest.get("strategy", "chunked_full_song")
        except json.JSONDecodeError:
            tracks = []
            strategy = "unknown"
    else:
        strategy = "unknown"

    if not tracks:
        tracks = []
        for midi_file in sorted(daw_dir.glob("track-*.mid")):
            stem = midi_file.stem
            musicxml_file = daw_dir / f"{stem}.musicxml"
            tracks.append({"name": stem, "midi": midi_file.name, "musicxml": musicxml_file.name})

    track_items = "".join(_render_daw_track_item(bundle, track) for track in tracks) or "<li>No tracks found in DAW bundle.</li>"

    return (
        f"<p><strong>DAW 匯出策略：</strong>{escape(str(strategy))}</p>"
        f"<ul>{track_items}</ul>"
        "<p>建議匯入步驟：</p>"
        "<ol>"
        "<li>開啟 GarageBand / Logic 專案</li>"
        "<li>匯入 bundle 中對應的 <code>.mid</code> 或 <code>.musicxml</code> 檔案</li>"
        "</ol>"
    )


def _format_signed(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):+.2f}"
    return "unknown"


def _format_f0_calibration_section(bundle: ArtifactBundle) -> str:
    summary = summarize_f0_calibration(bundle.f0_calibration)
    if not summary["available"]:
        return ""

    rows = []
    for note in summary["risk_notes"][:12]:
        rows.append(
            "<tr>"
            f"<td>{escape(str(note.get('note_id', 'unknown')))}</td>"
            f"<td>delta {_format_signed(note.get('delta_semitones'))}</td>"
            f"<td>{_confidence(note.get('periodicity_confidence'))}</td>"
            f"<td>{escape(str(note.get('status', 'unknown')))}</td>"
            "</tr>"
        )
    table_rows = "".join(rows) or '<tr><td colspan="4">No pitch-risk notes detected.</td></tr>'
    table = (
        "<table><thead><tr><th>Note</th><th>Pitch delta</th><th>Periodicity</th><th>Status</th></tr></thead>"
        f"<tbody>{table_rows}</tbody></table>"
    )
    return (
        "<section>"
        "<h2>F0 Calibration</h2>"
        f"<p><strong>Pitch-risk notes:</strong> {summary['risk_count']} / {summary['total_notes']}</p>"
        f"{table}"
        "</section>"
    )


def _format_quality_summary_section(bundle: ArtifactBundle) -> str:
    summary = bundle.quality_report.get("artifact_summary")
    if not isinstance(summary, dict):
        return ""

    stem_availability = summary.get("stem_availability", {})
    pitch_risk = summary.get("pitch_risk", {})
    backend_confidence = summary.get("backend_confidence", [])
    stems = stem_availability.get("stems", []) if isinstance(stem_availability, dict) else []
    pitch_risk_summary = pitch_risk if isinstance(pitch_risk, dict) else {}
    stem_text = ", ".join(escape(str(stem)) for stem in stems) if stems else "none"
    items = []
    if isinstance(backend_confidence, list):
        for item in backend_confidence[:8]:
            if not isinstance(item, dict):
                continue
            label = f"{item.get('backend', 'unknown')} / {item.get('stem', 'unknown')}"
            items.append(
                f"<li>{escape(label)}: {_confidence(item.get('average_confidence'))} "
                f"across {escape(str(item.get('event_count', 0)))} events</li>"
            )
    confidence_items = "".join(items) or "<li>unavailable</li>"
    return (
        "<section>"
        "<h2>Quality Summary</h2>"
        f"<p>Available stems: {stem_text}</p>"
        f"<p>Pitch-risk notes: {escape(str(pitch_risk_summary.get('risk_count', 0)))} / "
        f"{escape(str(pitch_risk_summary.get('total_notes', 0)))}</p>"
        f"<ul>{confidence_items}</ul>"
        "</section>"
    )


def _format_chord_detection_section(bundle: ArtifactBundle) -> str:
    summary = summarize_chord_detection(bundle.chord_detection)
    if not summary["available"]:
        return ""

    warning_items = []
    for warning in summary["warnings"][:8]:
        if not isinstance(warning, dict):
            continue
        warning_items.append(
            f"<li><strong>{escape(str(warning.get('code', 'UNKNOWN')))}</strong>: "
            f"{escape(str(warning.get('message', '')))}</li>"
        )
    warnings = "".join(warning_items) or "<li>none</li>"
    return (
        "<section>"
        "<h2>Chord Detection Sidecar</h2>"
        f"<p><strong>Backend:</strong> {escape(str(summary.get('backend', 'unknown')))}</p>"
        f"<p><strong>Progression:</strong> {_unique_chords(summary['chords'])}</p>"
        f"<p><strong>Average confidence:</strong> {_confidence(summary.get('average_confidence'))}</p>"
        f"<p><strong>Low-confidence chords:</strong> {escape(str(summary.get('low_confidence_count', 0)))}</p>"
        f"<ul>{warnings}</ul>"
        "</section>"
    )


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

  {_format_f0_calibration_section(bundle)}

  {_format_chord_detection_section(bundle)}

  {_format_quality_summary_section(bundle)}

  <section>
    <h2>Practice links</h2>
    <ul>
      <li>{_artifact_link(bundle, 'tab.md')}</li>
      <li>{_artifact_link(bundle, 'viewer.md')}</li>
      <li>{_artifact_link(bundle, 'tutorial.md')}</li>
    </ul>
  </section>

  <section>
    <h2>DAW 匯入</h2>
    {_format_daw_bundle_section(bundle)}
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
