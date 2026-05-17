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
        "confidence": {"overall": 0.82, "notes": 0.75, "chords": 0.8, "fingering": 0.7},
        "note_events": [],
        "chord_spans": [{"label": "Em", "start": 0.0, "end": 8.0, "confidence": 0.86}],
        "section_spans": [
            {"label": "A", "start": 0.0, "end": 4.0, "confidence": 0.8},
            {"label": "B", "start": 4.0, "end": 8.0, "confidence": 0.45},
        ],
    }
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps({"status": "passed", "warnings": []}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")


def test_cli_section_detect_help_lists_artifact_dir_and_out(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["section-detect", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "artifact_dir" in output
    assert "--out" in output


def test_cli_section_detect_writes_sidecar_and_viewer_interface_show_summary(tmp_path: Path) -> None:
    _write_artifact(tmp_path)

    assert cli.main(["section-detect", str(tmp_path)]) == 0
    payload = json.loads((tmp_path / "sections.json").read_text(encoding="utf-8"))

    assert payload["schema"] == "guitar-tab-generation.sections.v1"
    assert payload["summary"]["section_count"] == 2
    assert payload["summary"]["low_confidence_count"] == 1

    assert cli.main(["view", str(tmp_path)]) == 0
    viewer = (tmp_path / "viewer.md").read_text(encoding="utf-8")
    assert "## Section Detection Sidecar" in viewer
    assert "Backend: deterministic-arrangement" in viewer
    assert "A → B" in viewer

    assert cli.main(["interface", str(tmp_path)]) == 0
    html = (tmp_path / "interface.html").read_text(encoding="utf-8")
    assert "Section Detection Sidecar" in html
    assert "LOW_SECTION_CONFIDENCE" in html


def test_cli_section_detect_reports_missing_arrangement(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["section-detect", str(tmp_path)]) == 1
    assert "Section detection error" in capsys.readouterr().err
