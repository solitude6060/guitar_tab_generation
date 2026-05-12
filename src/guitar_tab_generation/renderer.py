"""Render MVP arrangement artifacts into human-readable TAB markdown."""
from __future__ import annotations

STRING_LABELS = {
    1: "e",
    2: "B",
    3: "G",
    4: "D",
    5: "A",
    6: "E",
}


def render_markdown_tab(arrangement: dict, quality_report: dict) -> str:
    """Render a compact sketch TAB with metadata, sections, chords, warnings."""
    source = arrangement["source"]
    timebase = arrangement["timebase"]
    lines = [
        "# Guitar Sketch TAB",
        "",
        "## Metadata",
        f"- Source: `{source['input_uri']}`",
        f"- Input type: {source['input_type']}",
        f"- Rights attestation: {source['rights_attestation']}",
        f"- Tempo: {timebase['tempo_bpm']:.1f} BPM",
        f"- Time signature: {timebase['time_signature']}",
        f"- Schema: {arrangement['schema_version']}",
        "",
        "## Sections",
    ]
    for section in arrangement.get("section_spans", []):
        lines.append(
            f"- {section['label']}: {section['start']:.2f}s–{section['end']:.2f}s "
            f"(confidence {section['confidence']:.2f})"
        )

    lines.extend(["", "## Chords"])
    for chord in arrangement.get("chord_spans", []):
        lines.append(
            f"- {chord['start']:.2f}s–{chord['end']:.2f}s: {chord['label']} "
            f"(confidence {chord['confidence']:.2f})"
        )

    lines.extend(["", "## TAB Sketch", "", *_render_tab_lines(arrangement), "", "## Warnings"])
    if arrangement.get("warnings"):
        for warning in arrangement["warnings"]:
            time_range = warning.get("time_range")
            suffix = f" [{time_range[0]:.2f}s–{time_range[1]:.2f}s]" if time_range else ""
            lines.append(f"- {warning['severity'].upper()} {warning['code']}: {warning['message']}{suffix}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Quality Summary",
            f"- Status: {quality_report['status']}",
            f"- Hard failures: {len(quality_report.get('hard_failures', []))}",
            f"- Warnings: {len(quality_report.get('warnings', []))}",
            "",
            "> Fingering is an AI-estimated playable sketch, not a claim of original performer fingering.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_tab_lines(arrangement: dict) -> list[str]:
    positions = {p["note_id"]: p for p in arrangement.get("positions", []) if p.get("playability") != "unplayable"}
    notes = [n for n in arrangement.get("note_events", []) if n.get("id") in positions]
    if not notes:
        return ["_No playable note TAB generated; see warnings/quality report._"]

    # Sketch renderer: one token per note, aligned across strings. This is not a
    # dense MIDI dump; it exposes the playable contour for practice.
    cells_by_string = {string: [] for string in range(1, 7)}
    for note in notes:
        position = positions[note["id"]]
        for string in range(1, 7):
            if string == position["string"]:
                cells_by_string[string].append(str(position["fret"]).rjust(2, "-"))
            else:
                cells_by_string[string].append("--")
    return [f"{STRING_LABELS[string]}|" + "-".join(cells_by_string[string]) + "-|" for string in range(1, 7)]
