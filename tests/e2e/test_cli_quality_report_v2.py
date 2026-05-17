from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


def _write_artifact(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    arrangement = {
        "source": {"input_uri": "fixtures/simple_chords_30_90s.wav"},
        "timebase": {"tempo_bpm": 92.0},
        "warnings": [],
        "confidence": {"overall": 0.8, "notes": 0.7, "chords": 0.8, "fingering": 0.75},
        "note_events": [{"id": "n1", "confidence": 0.7, "provenance": {"backend": "fixture", "stem": "mix"}}],
        "chord_spans": [{"label": "G", "start": 0.0, "end": 1.0, "confidence": 0.8, "provenance": {"backend": "fixture"}}],
        "section_spans": [{"label": "A", "start": 0.0, "end": 1.0, "confidence": 0.8, "provenance": {"backend": "fixture"}}],
    }
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps({"status": "passed", "warnings": []}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")
    (path / "stem_manifest.json").write_text(json.dumps({"stems": [{"name": "guitar", "path": "stems/guitar.wav"}]}), encoding="utf-8")
    stem_notes = path / "stem_notes"
    stem_notes.mkdir()
    (stem_notes / "guitar.notes.json").write_text(
        json.dumps(
            {
                "stem": "guitar",
                "backend": "basic-pitch",
                "notes": [{"id": "sg1", "confidence": 0.9, "provenance": {"backend": "basic-pitch", "stem": "guitar"}}],
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    (path / "f0_calibration.json").write_text(
        json.dumps({"note_calibrations": [{"note_id": "n1", "delta_semitones": 0.8, "periodicity_confidence": 0.8, "status": "calibrated"}]}),
        encoding="utf-8",
    )


def test_cli_quality_report_help_lists_artifact_dir_and_out(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["quality-report", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "artifact_dir" in output
    assert "--out" in output


def test_cli_quality_report_writes_v2_and_viewer_interface_show_summary(tmp_path: Path) -> None:
    _write_artifact(tmp_path)

    assert cli.main(["quality-report", str(tmp_path)]) == 0
    payload = json.loads((tmp_path / "quality_report.json").read_text(encoding="utf-8"))

    assert payload["schema_version"] == 2
    assert payload["artifact_summary"]["stem_availability"]["stems"] == ["guitar"]
    assert payload["artifact_summary"]["pitch_risk"]["risk_count"] == 1

    assert cli.main(["view", str(tmp_path)]) == 0
    viewer = (tmp_path / "viewer.md").read_text(encoding="utf-8")
    assert "## Quality Summary" in viewer
    assert "Available stems: guitar" in viewer
    assert "Pitch-risk notes: 1 / 1" in viewer
    assert "basic-pitch / guitar" in viewer

    assert cli.main(["interface", str(tmp_path)]) == 0
    html = (tmp_path / "interface.html").read_text(encoding="utf-8")
    assert "Quality Summary" in html
    assert "Available stems: guitar" in html
    assert "basic-pitch / guitar" in html


def test_cli_transcribe_help_does_not_gain_quality_or_stem_auto_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["transcribe", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "--stem" not in output
    assert "--quality-report" not in output
