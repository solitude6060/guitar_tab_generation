"""Practice tutorial generation from existing transcription artifacts."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_viewer import ArtifactBundle, load_artifact_bundle, summarize_f0_calibration


def _format_confidence(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return "unknown"


def _tempo_ladder(tempo: object) -> list[tuple[str, str]]:
    if not isinstance(tempo, (int, float)):
        return [("50%", "unknown BPM"), ("75%", "unknown BPM"), ("100%", "unknown BPM")]
    base = float(tempo)
    return [
        ("50%", f"{round(base * 0.50):.0f} BPM"),
        ("75%", f"{round(base * 0.75):.0f} BPM"),
        ("100%", f"{round(base):.0f} BPM"),
    ]


def _unique_labels(items: list[dict[str, Any]]) -> list[str]:
    labels: list[str] = []
    for item in items:
        label = str(item.get("label", "")).strip()
        if label and (not labels or labels[-1] != label):
            labels.append(label)
    return labels


def _pitch_sketch(notes: list[dict[str, Any]], limit: int = 8) -> str:
    pitches: list[str] = []
    for note in notes[:limit]:
        pitch = str(note.get("pitch_name", "")).strip()
        if pitch:
            pitches.append(pitch)
    return " → ".join(pitches) if pitches else "No note sketch available"


def _readiness(arrangement: dict[str, Any], quality_report: dict[str, Any]) -> str:
    status = quality_report.get("status", "unknown")
    warnings = arrangement.get("warnings", [])
    overall = arrangement.get("confidence", {}).get("overall")
    if status == "passed" and isinstance(overall, (int, float)) and overall >= 0.8 and not warnings:
        return "Ready for structured practice."
    if status == "passed":
        return "Practice-usable, but review confidence and warnings before increasing speed."
    return "Not practice-ready. Fix hard quality failures before using this as a lesson."


def _format_signed(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):+.2f}"
    return "unknown"


def _f0_practice_lines(f0_calibration: dict[str, Any] | None) -> list[str]:
    summary = summarize_f0_calibration(f0_calibration)
    if not summary["available"]:
        return []

    lines = [
        "",
        "## Pitch calibration practice",
        f"- Pitch-risk notes: {summary['risk_count']} / {summary['total_notes']}",
    ]
    if summary["risk_notes"]:
        lines.append("- Slow down and isolate these notes before full-tempo practice:")
        for note in summary["risk_notes"][:8]:
            note_id = note.get("note_id", "unknown")
            delta = _format_signed(note.get("delta_semitones"))
            confidence = _format_confidence(note.get("periodicity_confidence"))
            lines.append(f"  - {note_id}: delta {delta} semitones, periodicity {confidence}. Sing or hum the target pitch, then replay at 50% tempo.")
    else:
        lines.append("- No pitch-risk notes detected; keep normal tempo ladder practice.")
    return lines


def render_practice_tutorial_markdown(bundle: ArtifactBundle) -> str:
    """Render a stable Markdown practice tutorial from a loaded artifact bundle."""

    arrangement = bundle.arrangement
    quality_report = bundle.quality_report
    confidence = arrangement.get("confidence", {})
    warnings = arrangement.get("warnings", [])
    sections = arrangement.get("section_spans", [])
    chords = arrangement.get("chord_spans", [])
    notes = arrangement.get("note_events", [])
    tempo = arrangement.get("timebase", {}).get("tempo_bpm")
    chord_labels = _unique_labels(chords)

    lines = [
        "# Practice Tutorial",
        "",
        "## Readiness check",
        f"- Source: {arrangement.get('source', {}).get('input_uri', 'unknown')}",
        f"- Quality status: {quality_report.get('status', 'unknown')}",
        f"- Overall confidence: {_format_confidence(confidence.get('overall'))}",
        f"- Notes/chords/fingering confidence: {_format_confidence(confidence.get('notes'))} / {_format_confidence(confidence.get('chords'))} / {_format_confidence(confidence.get('fingering'))}",
        f"- Recommendation: {_readiness(arrangement, quality_report)}",
        "",
        "### Warnings to check first",
    ]
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning.get('code', 'UNKNOWN')}: {warning.get('message', '')}")
    else:
        lines.append("- None")

    lines.extend(["", "## Tempo ladder"])
    for percentage, bpm in _tempo_ladder(tempo):
        lines.append(f"- {percentage}: {bpm} — loop cleanly twice before moving faster.")

    lines.extend(["", "## Section loop plan"])
    if sections:
        for index, section in enumerate(sections, start=1):
            lines.append(
                f"{index}. {section.get('label', 'Section')}: "
                f"{float(section.get('start', 0.0)):.2f}s–{float(section.get('end', 0.0)):.2f}s. "
                "Loop at 50%, then 75%, then original tempo."
            )
    else:
        lines.append("1. No section labels found; practice the full TAB in short 4-bar loops.")

    lines.extend(["", "## Chord practice plan"])
    if chord_labels:
        lines.append(f"- Progression: {' → '.join(chord_labels)}")
        lines.append("- Strum each chord for one bar, then connect pairs before playing the full progression.")
    else:
        lines.append("- No chord progression found; focus on the TAB rhythm and note sketch.")

    lines.extend([
        "",
        "## Lead/riff practice plan",
        f"- Note sketch: {_pitch_sketch(notes)}",
        "- Clap or count the rhythm first, then play only the first two notes until timing is stable.",
        "- Add one note at a time; do not speed up while any position feels uncertain.",
    ])

    lines.extend(_f0_practice_lines(bundle.f0_calibration))

    lines.extend([
        "",
        "## Safety note",
        "- This tutorial is generated from confidence-scored artifacts. Manually confirm low-confidence notes, chords, sections, and fingerings before treating them as final.",
        "- Original TAB: Open `tab.md` in this artifact directory.",
        "",
    ])
    return "\n".join(lines)


def write_practice_tutorial(artifact_dir: Path, out_path: Path | None = None) -> Path:
    """Write a Markdown practice tutorial and return the path written."""

    bundle = load_artifact_bundle(artifact_dir)
    destination = out_path or artifact_dir / "tutorial.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_practice_tutorial_markdown(bundle), encoding="utf-8")
    return destination
