from __future__ import annotations

from guitar_tab_generation.quality_gate import (
    validate_arrangement,
    validate_golden_fixture_manifest,
)


def valid_arrangement() -> dict:
    return {
        "schema_version": "0.1.0",
        "timebase": {
            "sample_rate": 44100,
            "tempo_bpm": 96.0,
            "beats": [{"time": 0.0, "beat": 1}],
            "bars": [{"index": 1, "start": 0.0, "end": 2.5}],
            "time_signature": "4/4",
        },
        "source": {
            "input_type": "local_audio",
            "input_uri": "fixtures/simple_chords_30_90s.wav",
            "rights_attestation": "user_provided",
            "trim": {"start": 0.0, "end": 60.0},
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
        "confidence": {
            "overall": 0.72,
            "rhythm": 0.8,
            "chords": 0.7,
            "notes": 0.65,
            "fingering": 0.75,
            "thresholds": {"notes": 0.55, "chords": 0.60, "sections": 0.50, "fingering": 0.65},
        },
        "warnings": [],
        "note_events": [
            {
                "id": "n1",
                "start": 1.25,
                "end": 1.55,
                "pitch_midi": 64,
                "confidence": 0.82,
                "provenance": {"stage": "pitch_transcription", "stem": "mix"},
            }
        ],
        "chord_spans": [
            {"start": 0.0, "end": 2.5, "label": "G", "confidence": 0.78, "provenance": {"stage": "tonal_chord_analysis"}}
        ],
        "section_spans": [{"start": 0.0, "end": 16.0, "label": "Verse/Riff A", "confidence": 0.66}],
        "fretboard": {
            "tuning": ["E2", "A2", "D3", "G3", "B3", "E4"],
            "supported_fret_range": {"min": 0, "max": 20},
            "capo": 0,
        },
        "positions": [
            {"note_id": "n1", "string": 1, "fret": 0, "confidence": 0.78, "playability": "playable"}
        ],
        "render_hints": {
            "tab_density": "sketch",
            "show_rhythm_slashes": True,
            "show_warnings_inline": True,
            "preferred_output": "markdown",
        },
    }


def test_valid_arrangement_passes_quality_gate():
    result = validate_arrangement(valid_arrangement())
    assert result.passed, result.issues


def test_unplayable_tab_hard_fails():
    arrangement = valid_arrangement()
    arrangement["positions"][0]["fret"] = 24
    result = validate_arrangement(arrangement)
    assert not result.passed
    assert any(issue.code == "UNPLAYABLE_TAB" for issue in result.issues)


def test_low_confidence_without_warning_hard_fails():
    arrangement = valid_arrangement()
    arrangement["confidence"]["notes"] = 0.2
    result = validate_arrangement(arrangement)
    assert not result.passed
    assert any(issue.code == "LOW_CONFIDENCE_WITHOUT_WARNING" for issue in result.issues)


def test_low_confidence_with_warning_passes():
    arrangement = valid_arrangement()
    arrangement["confidence"]["notes"] = 0.2
    arrangement["warnings"] = [
        {"code": "LOW_NOTE_CONFIDENCE", "severity": "warning", "message": "Lead line is approximate"}
    ]
    result = validate_arrangement(arrangement)
    assert result.passed, result.issues


def test_url_policy_bypass_hard_fails():
    arrangement = valid_arrangement()
    arrangement["source"]["input_type"] = "youtube_url"
    arrangement["source"]["rights_attestation"] = "unknown"
    result = validate_arrangement(arrangement)
    assert not result.passed
    assert any(issue.code == "URL_POLICY_BYPASS" for issue in result.issues)


def test_golden_manifest_requires_all_three_fixtures_and_manual_rubrics():
    manifest = {
        "fixtures": [
            {
                "id": "simple_chords_30_90s",
                "duration_seconds": 60,
                "rights": "self-made synthetic fixture",
                "manual_rubric": {
                    "reviewer": "author",
                    "recognizability": 3,
                    "chord_usability": 3,
                    "tab_playability": 3,
                    "rhythm_readability": 3,
                    "honesty": 4,
                },
            }
        ]
    }
    result = validate_golden_fixture_manifest(manifest)
    assert not result.passed
    assert any(issue.code == "MISSING_GOLDEN_FIXTURES" for issue in result.issues)


def test_complete_golden_manifest_passes():
    def fixture(fixture_id: str) -> dict:
        return {
            "id": fixture_id,
            "duration_seconds": 45,
            "rights": "self-made synthetic fixture",
            "manual_rubric": {
                "reviewer": "author",
                "recognizability": 3,
                "chord_usability": 3,
                "tab_playability": 3,
                "rhythm_readability": 3,
                "honesty": 4,
            },
        }

    manifest = {
        "fixtures": [
            fixture("simple_chords_30_90s"),
            fixture("single_note_riff_30_90s"),
            fixture("single_note_lead_30_90s"),
        ]
    }
    result = validate_golden_fixture_manifest(manifest)
    assert result.passed, result.issues

from guitar_tab_generation.contracts import (
    HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING,
    HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD,
    HARD_FAIL_UNPLAYABLE_TAB,
    WARNING_UNPLAYABLE_NOTE,
)
from guitar_tab_generation.quality_reporter import build_quality_report


def test_quality_reporter_hard_fails_unplayable_warning():
    arrangement = valid_arrangement()
    arrangement["warnings"] = [
        {"code": WARNING_UNPLAYABLE_NOTE, "severity": "error", "message": "No playable mapping"}
    ]
    report = build_quality_report(arrangement)
    assert report["status"] == "failed"
    assert any(failure["code"] == HARD_FAIL_UNPLAYABLE_TAB for failure in report["hard_failures"])


def test_quality_reporter_checks_item_level_low_confidence():
    arrangement = valid_arrangement()
    arrangement["note_events"][0]["confidence"] = 0.1
    report = build_quality_report(arrangement)
    assert report["status"] == "failed"
    assert any(
        failure["code"] == HARD_FAIL_LOW_CONFIDENCE_WITHOUT_WARNING
        and failure.get("path") == "$.note_events[0].confidence"
        for failure in report["hard_failures"]
    )


def test_quality_reporter_requires_fixture_rights_and_rubric_record():
    report = build_quality_report(valid_arrangement(), fixture_metadata={})
    assert report["status"] == "failed"
    assert sum(
        1 for failure in report["hard_failures"] if failure["code"] == HARD_FAIL_MISSING_GOLDEN_FIXTURE_RECORD
    ) == 2
