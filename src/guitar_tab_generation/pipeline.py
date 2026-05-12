"""End-to-end local-audio MVP orchestration."""
from __future__ import annotations

from pathlib import Path
import json

from .audio_preprocess import normalize_audio
from .contracts import CONFIDENCE_THRESHOLDS, WARNING_LOW_FINGERING_CONFIDENCE, WARNING_LOW_SECTION_CONFIDENCE
from .guitar_arranger import arrange_notes
from .input_adapter import load_fixture_metadata, resolve_local_audio
from .pitch_transcription import transcribe_notes
from .quality_reporter import build_quality_report
from .renderer import write_outputs
from .rhythm_analysis import analyze_rhythm
from .schema import base_arrangement
from .tonal_chord_analysis import analyze_chords


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def transcribe_to_tab(
    input_uri: str,
    out_dir: Path,
    *,
    trim_start: float | None = None,
    trim_end: float | None = None,
) -> tuple[dict, dict]:
    audio_input = resolve_local_audio(input_uri, trim_start=trim_start, trim_end=trim_end)
    fixture_metadata = load_fixture_metadata(audio_input.path)
    normalized = normalize_audio(audio_input, out_dir)
    rhythm = analyze_rhythm(audio_input.duration_seconds, fixture_metadata)

    source = {
        "input_type": audio_input.input_type,
        "input_uri": audio_input.input_uri,
        "rights_attestation": audio_input.rights_attestation,
        "trim": {"start": audio_input.trim_start, "end": audio_input.trim_end},
        "stems": [
            {
                "name": "mix",
                "path": normalized["path"],
                "model": None,
                "confidence": 1.0,
                "provenance": {"stage": "audio_preprocess", "input": "local_audio"},
            }
        ],
    }
    arrangement = base_arrangement(
        sample_rate=int(normalized["sample_rate"]),
        tempo_bpm=float(rhythm["tempo_bpm"]),
        duration_seconds=audio_input.duration_seconds,
        source=source,
    )

    chords, chord_warnings = analyze_chords(audio_input.duration_seconds, fixture_metadata)
    notes, note_warnings = transcribe_notes(audio_input.duration_seconds, fixture_metadata)
    positions, playability_warnings, fingering_confidence = arrange_notes(notes)
    sections = (fixture_metadata or {}).get("section_spans") or [
        {"start": 0.0, "end": audio_input.duration_seconds, "label": "Main sketch", "confidence": 0.66}
    ]
    sections = [
        {
            "start": float(section["start"]),
            "end": float(section["end"]),
            "label": str(section["label"]),
            "confidence": float(section.get("confidence", 0.66)),
        }
        for section in sections
    ]

    arrangement["chord_spans"] = chords
    arrangement["note_events"] = notes
    arrangement["positions"] = positions
    arrangement["section_spans"] = sections
    arrangement["warnings"].extend(chord_warnings + note_warnings + playability_warnings)

    section_confidence = _average([section["confidence"] for section in sections])
    if section_confidence < CONFIDENCE_THRESHOLDS["sections"]:
        arrangement["warnings"].append({
            "code": WARNING_LOW_SECTION_CONFIDENCE,
            "severity": "warning",
            "message": "Section confidence is below threshold.",
        })
    if fingering_confidence < CONFIDENCE_THRESHOLDS["fingering"]:
        arrangement["warnings"].append({
            "code": WARNING_LOW_FINGERING_CONFIDENCE,
            "severity": "warning",
            "message": "Fingering confidence is below threshold.",
        })

    arrangement["confidence"].update({
        "overall": round(_average([
            float(rhythm["confidence"]),
            _average([chord["confidence"] for chord in chords]),
            _average([note["confidence"] for note in notes]),
            fingering_confidence,
        ]), 3),
        "rhythm": float(rhythm["confidence"]),
        "chords": round(_average([chord["confidence"] for chord in chords]), 3),
        "notes": round(_average([note["confidence"] for note in notes]), 3),
        "fingering": round(fingering_confidence, 3),
    })

    (out_dir / "notes.json").write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
    (out_dir / "chords.json").write_text(json.dumps(chords, indent=2) + "\n", encoding="utf-8")
    (out_dir / "sections.json").write_text(json.dumps(sections, indent=2) + "\n", encoding="utf-8")
    quality_report = build_quality_report(arrangement, fixture_metadata=fixture_metadata)
    write_outputs(out_dir, arrangement, quality_report)
    return arrangement, quality_report
