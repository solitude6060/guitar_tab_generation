from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation.cli import main


def _write_artifact(root: Path, *, with_f0: bool = True) -> None:
    root.mkdir(parents=True, exist_ok=True)
    arrangement = {
        "source": {"input_uri": "fixture.wav"},
        "timebase": {"tempo_bpm": 120},
        "confidence": {"overall": 0.8, "notes": 0.8, "chords": 0.7, "fingering": 0.7},
        "section_spans": [{"label": "Riff", "start": 0, "end": 1, "confidence": 0.8}],
        "chord_spans": [{"label": "C", "start": 0, "end": 1, "confidence": 0.8}],
        "note_events": [{"id": "n1", "start": 0.0, "end": 0.5, "pitch_name": "C4"}],
        "warnings": [],
    }
    (root / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (root / "quality_report.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (root / "tab.md").write_text("# TAB\n", encoding="utf-8")
    if with_f0:
        (root / "f0_calibration.json").write_text(
            json.dumps(
                {
                    "backend": "torchcrepe-f0",
                    "device": "cpu",
                    "note_calibrations": [
                        {
                            "note_id": "n1",
                            "expected_midi": 60,
                            "observed_midi": 61.0,
                            "delta_semitones": 1.0,
                            "periodicity_confidence": 0.41,
                            "frame_count": 4,
                            "status": "calibrated",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )


def test_view_interface_and_tutorial_include_f0_pitch_risk(tmp_path: Path) -> None:
    _write_artifact(tmp_path, with_f0=True)

    assert main(["view", str(tmp_path)]) == 0
    assert main(["interface", str(tmp_path)]) == 0
    assert main(["tutorial", str(tmp_path)]) == 0

    viewer = (tmp_path / "viewer.md").read_text(encoding="utf-8")
    interface = (tmp_path / "interface.html").read_text(encoding="utf-8")
    tutorial = (tmp_path / "tutorial.md").read_text(encoding="utf-8")

    assert "F0 Calibration" in viewer
    assert "Pitch-risk notes: 1 / 1" in viewer
    assert "n1" in viewer
    assert "delta +1.00" in viewer
    assert "F0 Calibration" in interface
    assert "Pitch-risk notes" in interface
    assert "delta +1.00" in interface
    assert "Pitch calibration practice" in tutorial
    assert "n1" in tutorial


def test_missing_f0_calibration_keeps_existing_outputs(tmp_path: Path) -> None:
    _write_artifact(tmp_path, with_f0=False)

    assert main(["view", str(tmp_path)]) == 0
    assert main(["interface", str(tmp_path)]) == 0
    assert main(["tutorial", str(tmp_path)]) == 0

    assert "F0 Calibration" not in (tmp_path / "viewer.md").read_text(encoding="utf-8")
    assert "F0 Calibration" not in (tmp_path / "interface.html").read_text(encoding="utf-8")
    assert "Pitch calibration practice" not in (tmp_path / "tutorial.md").read_text(encoding="utf-8")
