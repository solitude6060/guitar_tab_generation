"""Markdown and JSON artifact rendering."""
from __future__ import annotations

from pathlib import Path
import json


def render_markdown_tab(arrangement: dict, quality_report: dict) -> str:
    lines = [
        "# Guitar TAB Sketch",
        "",
        "## Metadata",
        f"- Schema: {arrangement['schema_version']}",
        f"- Tempo: {arrangement['timebase']['tempo_bpm']} BPM",
        f"- Time signature: {arrangement['timebase']['time_signature']}",
        f"- Source: {arrangement['source']['input_uri']}",
        "",
        "## Sections",
    ]
    for section in arrangement.get("section_spans", []):
        lines.append(f"- {section['label']}: {section['start']:.2f}s–{section['end']:.2f}s (confidence {section['confidence']:.2f})")
    lines.extend(["", "## Chords"])
    for chord in arrangement.get("chord_spans", []):
        lines.append(f"- {chord['start']:.2f}s–{chord['end']:.2f}s: {chord['label']} ({chord['confidence']:.2f})")
    lines.extend(["", "## TAB", "", "```text"])
    by_note = {event["id"]: event for event in arrangement.get("note_events", [])}
    for position in arrangement.get("positions", []):
        event = by_note.get(position["note_id"], {})
        lines.append(
            f"{event.get('start', 0):6.2f}s  {event.get('pitch_name', '?'):>3}  "
            f"string {position['string']} fret {position['fret']}  "
            f"confidence {position['confidence']:.2f}"
        )
    lines.extend(["```", "", "## Warnings"])
    if arrangement.get("warnings"):
        for warning in arrangement["warnings"]:
            lines.append(f"- {warning['code']}: {warning['message']}")
    else:
        lines.append("- None")
    lines.extend(["", "## Quality", f"- Status: {quality_report['status']}"])
    for failure in quality_report.get("hard_failures", []):
        lines.append(f"- HARD FAIL {failure['code']}: {failure['message']}")
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path, arrangement: dict, quality_report: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "arrangement.json").write_text(
        json.dumps(arrangement, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out_dir / "quality_report.json").write_text(
        json.dumps(quality_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out_dir / "tab.md").write_text(render_markdown_tab(arrangement, quality_report), encoding="utf-8")
