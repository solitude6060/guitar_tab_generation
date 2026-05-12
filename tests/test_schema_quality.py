from __future__ import annotations

from guitar_tab_generation.quality_reporter import build_quality_report
from guitar_tab_generation.schema import base_arrangement, validate_arrangement


def _arrangement() -> dict:
    arr = base_arrangement(
        sample_rate=44100,
        tempo_bpm=120.0,
        duration_seconds=30.0,
        source={
            "input_type": "local_audio",
            "input_uri": "fixtures/simple.wav",
            "rights_attestation": "self_created",
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
    arr["note_events"] = [
        {
            "id": "n1",
            "start": 0.0,
            "end": 0.5,
            "pitch_midi": 64,
            "pitch_name": "E4",
            "confidence": 0.82,
            "provenance": {"stage": "pitch_transcription", "stem": "mix"},
        }
    ]
    arr["chord_spans"] = [
        {"start": 0.0, "end": 30.0, "label": "E", "confidence": 0.8, "provenance": {"stage": "tonal_chord_analysis", "stem": "mix"}}
    ]
    arr["section_spans"] = [{"start": 0.0, "end": 30.0, "label": "Main", "confidence": 0.8}]
    arr["positions"] = [{"note_id": "n1", "string": 1, "fret": 0, "confidence": 0.8, "playability": "playable"}]
    arr["confidence"].update({"overall": 0.8, "notes": 0.8, "chords": 0.8, "sections": 0.8, "fingering": 0.8})
    return arr


def test_valid_arrangement_passes_schema_and_quality() -> None:
    arr = _arrangement()
    assert validate_arrangement(arr) == []
    report = build_quality_report(arr)
    assert report["status"] == "passed"


def test_out_of_range_fret_hard_fails() -> None:
    arr = _arrangement()
    arr["positions"][0]["fret"] = 21
    report = build_quality_report(arr)
    assert report["status"] == "failed"
    assert any(f["code"] in {"UNPLAYABLE_TAB", "SCHEMA_ERROR"} for f in report["hard_failures"])
