from __future__ import annotations

from guitar_tab_generation.renderer import render_markdown_tab
from guitar_tab_generation.schema import base_arrangement


def arrangement() -> dict:
    arr = base_arrangement(
        sample_rate=44100,
        tempo_bpm=120.0,
        duration_seconds=30.0,
        source={
            "input_type": "local_audio",
            "input_uri": "fixtures/simple_chords_30_90s.wav",
            "rights_attestation": "user_provided",
            "trim": {"start": 0.0, "end": 30.0},
            "stems": [
                {
                    "name": "mix",
                    "path": "audio_normalized.wav",
                    "model": None,
                    "confidence": 1.0,
                    "provenance": {"stage": "audio_preprocess", "input": "local_audio"},
                }
            ],
        },
    )
    arr["confidence"].update({"overall": 0.81, "notes": 0.8, "chords": 0.8, "sections": 0.8, "fingering": 0.8})
    arr["section_spans"] = [{"start": 0.0, "end": 30.0, "label": "Riff A", "confidence": 0.8, "provenance": {"stage": "section_detector", "backend": "fixture"}}]
    arr["chord_spans"] = [{"start": 0.0, "end": 30.0, "label": "Em", "confidence": 0.8, "provenance": {"stage": "tonal_chord_analysis", "stem": "mix", "backend": "fixture"}}]
    arr["note_events"] = [{"id": "n1", "start": 1.0, "end": 1.25, "pitch_midi": 64, "pitch_name": "E4", "confidence": 0.8, "provenance": {"stage": "pitch_transcription", "stem": "mix", "backend": "fixture"}}]
    arr["positions"] = [{"note_id": "n1", "string": 1, "fret": 0, "confidence": 0.8, "playability": "playable"}]
    return arr


def test_renderer_includes_practice_metadata_sections_chords_tab_and_warnings() -> None:
    tab = render_markdown_tab(arrangement(), {"status": "passed", "hard_failures": []})

    assert "## Metadata" in tab
    assert "Overall confidence: 0.81" in tab
    assert "## Sections" in tab and "Riff A" in tab
    assert "## Chords" in tab and "Em" in tab
    assert "## TAB" in tab and "string 1 fret 0" in tab
    assert "## Warnings" in tab and "- None" in tab


def test_renderer_does_not_render_unplayable_position_as_normal_tab() -> None:
    arr = arrangement()
    arr["positions"][0].update({"playability": "unplayable", "fret": 20})
    arr["warnings"] = [{"code": "UNPLAYABLE_NOTE", "severity": "error", "message": "No playable mapping"}]

    tab = render_markdown_tab(arr, {"status": "failed", "hard_failures": []})

    assert "string 1 fret 20" not in tab
    assert "UNPLAYABLE omitted" in tab
    assert "UNPLAYABLE_NOTE" in tab
