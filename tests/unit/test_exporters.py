from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from guitar_tab_generation.artifact_viewer import ArtifactViewerError, load_artifact_bundle
from guitar_tab_generation.exporters import render_midi, render_musicxml, write_export


def _write_bundle(path: Path) -> None:
    arrangement = {
        "source": {"input_uri": "fixtures/single_note_riff_30_90s.wav"},
        "timebase": {"tempo_bpm": 100.0},
        "confidence": {"overall": 0.77},
        "note_events": [
            {"id": "n1", "start": 0.0, "end": 0.5, "pitch_name": "E3", "confidence": 0.8},
            {"id": "n2", "start": 0.5, "end": 1.0, "pitch_name": "G3", "confidence": 0.7},
        ],
        "warnings": [{"code": "LOW_CONF", "message": "Review notes."}],
    }
    path.mkdir(parents=True, exist_ok=True)
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")


def test_render_musicxml_is_parseable_and_preserves_metadata(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    xml = render_musicxml(load_artifact_bundle(tmp_path))
    root = ET.fromstring(xml)

    assert root.tag == "score-partwise"
    assert root.find(".//step").text == "E"
    assert "LOW_CONF" in xml
    assert "overall confidence 0.77" in xml


def test_render_midi_writes_standard_header(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    midi = render_midi(load_artifact_bundle(tmp_path))

    assert midi.startswith(b"MThd")
    assert b"MTrk" in midi
    assert len(midi) > 32


@pytest.mark.parametrize("fmt, expected", [("musicxml", "score.musicxml"), ("midi", "score.mid")])
def test_write_export_uses_default_filename(tmp_path: Path, fmt: str, expected: str) -> None:
    _write_bundle(tmp_path)

    written = write_export(tmp_path, fmt)

    assert written == tmp_path / expected
    assert written.exists()


def test_write_export_rejects_unknown_format(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    with pytest.raises(ValueError, match="Unsupported export format"):
        write_export(tmp_path, "pdf")


def test_write_export_uses_artifact_contract_errors(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)

    with pytest.raises(ArtifactViewerError, match="arrangement.json"):
        write_export(tmp_path, "musicxml")
