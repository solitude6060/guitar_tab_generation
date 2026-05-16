from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation.artifact_viewer import load_artifact_bundle, summarize_f0_calibration


def _write_base_artifact(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    arrangement = {
        "source": {"input_uri": "fixture.wav"},
        "timebase": {"tempo_bpm": 120},
        "confidence": {"overall": 0.8, "notes": 0.8, "chords": 0.7, "fingering": 0.7},
        "section_spans": [],
        "chord_spans": [],
        "note_events": [{"id": "n1", "start": 0.0, "end": 0.5, "pitch_name": "C4"}],
        "warnings": [],
    }
    quality = {"status": "passed", "warnings": []}
    (root / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (root / "quality_report.json").write_text(json.dumps(quality), encoding="utf-8")
    (root / "tab.md").write_text("# TAB\n", encoding="utf-8")


def _write_f0_calibration(root: Path) -> None:
    payload = {
        "backend": "torchcrepe-f0",
        "device": "cpu",
        "note_calibrations": [
            {
                "note_id": "n1",
                "expected_midi": 60,
                "observed_midi": 61.1,
                "delta_semitones": 1.1,
                "periodicity_confidence": 0.42,
                "frame_count": 4,
                "status": "calibrated",
            },
            {
                "note_id": "n2",
                "expected_midi": 64,
                "observed_midi": 64.05,
                "delta_semitones": 0.05,
                "periodicity_confidence": 0.91,
                "frame_count": 4,
                "status": "calibrated",
            },
        ],
    }
    (root / "f0_calibration.json").write_text(json.dumps(payload), encoding="utf-8")


def test_load_artifact_bundle_reads_optional_f0_calibration(tmp_path: Path) -> None:
    _write_base_artifact(tmp_path)
    _write_f0_calibration(tmp_path)

    bundle = load_artifact_bundle(tmp_path)

    assert bundle.f0_calibration is not None
    assert bundle.f0_calibration["backend"] == "torchcrepe-f0"


def test_summarize_f0_calibration_flags_pitch_risk() -> None:
    summary = summarize_f0_calibration(
        {
            "note_calibrations": [
                {"note_id": "n1", "delta_semitones": 0.7, "periodicity_confidence": 0.8, "status": "calibrated"},
                {"note_id": "n2", "delta_semitones": 0.1, "periodicity_confidence": 0.4, "status": "calibrated"},
                {"note_id": "n3", "delta_semitones": 0.1, "periodicity_confidence": 0.9, "status": "calibrated"},
            ]
        }
    )

    assert summary["available"] is True
    assert summary["total_notes"] == 3
    assert summary["risk_count"] == 2
    assert [item["note_id"] for item in summary["risk_notes"]] == ["n1", "n2"]


def test_summarize_f0_calibration_missing_is_empty() -> None:
    summary = summarize_f0_calibration(None)

    assert summary["available"] is False
    assert summary["risk_count"] == 0
    assert summary["risk_notes"] == []
