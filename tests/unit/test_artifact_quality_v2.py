from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.artifact_quality import build_artifact_quality_report_v2, write_artifact_quality_report_v2


def _write_core_artifact(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    arrangement = {
        "warnings": [{"code": "LOW_NOTE_CONFIDENCE", "message": "Check note n1."}],
        "confidence": {"overall": 0.72, "notes": 0.65, "chords": 0.7, "fingering": 0.75},
        "note_events": [
            {
                "id": "n1",
                "start": 0.0,
                "end": 0.5,
                "pitch_midi": 64,
                "confidence": 0.6,
                "provenance": {"backend": "fixture", "stem": "mix"},
            }
        ],
        "chord_spans": [{"label": "Em", "start": 0.0, "end": 1.0, "confidence": 0.7, "provenance": {"backend": "fixture"}}],
        "section_spans": [{"label": "A", "start": 0.0, "end": 1.0, "confidence": 0.8, "provenance": {"backend": "fixture"}}],
    }
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps({"status": "passed", "warnings": arrangement["warnings"]}), encoding="utf-8")


def test_quality_v2_marks_missing_optional_sidecars_unavailable(tmp_path: Path) -> None:
    _write_core_artifact(tmp_path)

    report = build_artifact_quality_report_v2(tmp_path)

    assert report["schema_version"] == 2
    assert report["artifact_summary"]["stem_availability"]["available"] is False
    assert report["artifact_summary"]["stem_notes"]["available"] is False
    assert report["artifact_summary"]["pitch_risk"]["available"] is False
    assert report["artifact_summary"]["backend_confidence"][0]["backend"] == "fixture"


def test_quality_v2_summarizes_stems_stem_notes_and_pitch_risk(tmp_path: Path) -> None:
    _write_core_artifact(tmp_path)
    (tmp_path / "stem_manifest.json").write_text(
        json.dumps({"stems": [{"name": "guitar", "path": "stems/guitar.wav"}, {"name": "bass", "path": "stems/bass.wav"}]}),
        encoding="utf-8",
    )
    stem_notes = tmp_path / "stem_notes"
    stem_notes.mkdir()
    (stem_notes / "guitar.notes.json").write_text(
        json.dumps(
            {
                "stem": "guitar",
                "backend": "basic-pitch",
                "notes": [
                    {"id": "sg1", "confidence": 0.9, "provenance": {"backend": "basic-pitch", "stem": "guitar"}},
                    {"id": "sg2", "confidence": 0.5, "provenance": {"backend": "basic-pitch", "stem": "guitar"}},
                ],
                "warnings": [{"code": "LOW_NOTE_CONFIDENCE"}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "f0_calibration.json").write_text(
        json.dumps(
            {
                "note_calibrations": [
                    {"note_id": "n1", "delta_semitones": 0.7, "periodicity_confidence": 0.8, "status": "calibrated"},
                    {"note_id": "n2", "delta_semitones": 0.1, "periodicity_confidence": 0.9, "status": "calibrated"},
                ]
            }
        ),
        encoding="utf-8",
    )

    report = build_artifact_quality_report_v2(tmp_path)

    summary = report["artifact_summary"]
    assert summary["stem_availability"] == {"available": True, "count": 2, "stems": ["guitar", "bass"]}
    assert summary["stem_notes"]["stems"][0]["stem"] == "guitar"
    assert summary["stem_notes"]["stems"][0]["note_count"] == 2
    assert summary["stem_notes"]["stems"][0]["average_confidence"] == pytest.approx(0.7)
    assert summary["stem_notes"]["stems"][0]["warning_count"] == 1
    assert summary["pitch_risk"]["risk_count"] == 1
    assert any(item["backend"] == "basic-pitch" and item["stem"] == "guitar" for item in summary["backend_confidence"])


def test_write_artifact_quality_report_v2_writes_default_quality_report(tmp_path: Path) -> None:
    _write_core_artifact(tmp_path)

    written = write_artifact_quality_report_v2(tmp_path)

    assert written == tmp_path / "quality_report.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 2
