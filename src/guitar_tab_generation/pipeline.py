"""End-to-end placeholder pipeline for local-audio-first MVP artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .audio_preprocess import normalize_audio
from .guitar_arranger import arrange_notes
from .input_adapter import AudioInput
from .pitch_transcription import transcribe_notes
from .quality_reporter import build_quality_report
from .renderer import render_markdown_tab
from .rhythm_analysis import analyze_rhythm
from .schema import base_arrangement
from .section_detector import detect_sections
from .tonal_chord_analysis import analyze_chords


def load_fixture_metadata(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def run_placeholder_pipeline(
    audio: AudioInput,
    out_dir: str | Path,
    *,
    fixture_metadata: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Run deterministic scaffold stages and write required MVP artifacts."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    normalized = normalize_audio(audio, out)
    duration = audio.trim["end"] - audio.trim["start"]
    rhythm = analyze_rhythm(duration, fixture_metadata)
    chords, chord_warnings = analyze_chords(duration, fixture_metadata)
    notes, note_warnings = transcribe_notes(duration, fixture_metadata)
    sections, section_warnings = detect_sections(duration, fixture_metadata)
    positions, playability_warnings, fingering_confidence = arrange_notes(notes)

    source = {
        "input_type": audio.input_type,
        "input_uri": audio.input_uri,
        "rights_attestation": audio.rights_attestation,
        "trim": audio.trim,
        "stems": [
            {
                "name": "mix",
                "path": normalized["path"],
                "model": None,
                "confidence": 1.0,
                "provenance": normalized["provenance"],
            }
        ],
    }
    arrangement = base_arrangement(
        sample_rate=int(normalized["sample_rate"]),
        tempo_bpm=float(rhythm["tempo_bpm"]),
        duration_seconds=duration,
        source=source,
    )
    arrangement["note_events"] = notes
    arrangement["chord_spans"] = chords
    arrangement["section_spans"] = sections
    arrangement["positions"] = positions
    arrangement["warnings"] = [*chord_warnings, *note_warnings, *section_warnings, *playability_warnings]
    arrangement["confidence"].update(
        {
            "rhythm": float(rhythm.get("confidence", 0.8)),
            "chords": _average_confidence(chords),
            "notes": _average_confidence(notes),
            "fingering": fingering_confidence,
        }
    )
    arrangement["confidence"]["overall"] = _average_values(
        [
            arrangement["confidence"]["rhythm"],
            arrangement["confidence"]["chords"],
            arrangement["confidence"]["notes"],
            arrangement["confidence"]["fingering"],
        ]
    )

    quality_report = build_quality_report(arrangement, fixture_metadata=fixture_metadata)

    arrangement_path = out / "arrangement.json"
    quality_path = out / "quality_report.json"
    tab_path = out / "tab.md"
    arrangement_path.write_text(json.dumps(arrangement, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    quality_path.write_text(json.dumps(quality_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tab_path.write_text(render_markdown_tab(arrangement, quality_report), encoding="utf-8")
    return {"arrangement": arrangement_path, "quality_report": quality_path, "tab": tab_path}


def _average_confidence(items: list[dict]) -> float:
    if not items:
        return 0.0
    return _average_values([float(item.get("confidence", 0.0)) for item in items])


def _average_values(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 3)
