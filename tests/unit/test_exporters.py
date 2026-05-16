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


def test_render_midi_handles_overlapping_notes(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    overlapping_notes = [
        {"start": 0.0, "end": 0.5, "pitch_name": "E3"},
        {"start": 0.2, "end": 0.8, "pitch_name": "G3"},
    ]

    midi = render_midi(load_artifact_bundle(tmp_path), note_events=overlapping_notes)

    assert midi.startswith(b"MThd")
    assert b"\x90" in midi


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


def test_render_daw_bundle_tracks_chunks_and_manifest(tmp_path: Path) -> None:
    arrangement = {
        "source": {
            "input_uri": "fixtures/legal_full_song_180s.wav",
            "processing_plan": {
                "mode": "chunked_full_song",
                "chunks": [
                    {"index": 1, "start": 0.0, "end": 60.0},
                    {"index": 2, "start": 58.0, "end": 118.0},
                ],
            },
        },
        "timebase": {"tempo_bpm": 120.0},
        "confidence": {"overall": 0.77},
        "note_events": [
            {"id": "n1", "start": 0.0, "end": 0.5, "pitch_name": "E3", "confidence": 0.8},
            {"id": "n2", "start": 58.2, "end": 59.0, "pitch_name": "G3", "confidence": 0.7},
            {"id": "n3", "start": 58.8, "end": 60.2, "pitch_name": "C4", "confidence": 0.6},
            {"id": "n4", "start": 118.1, "end": 118.4, "pitch_name": "A2", "confidence": 0.7},
        ],
        "warnings": [{"code": "LOW_CONF", "message": "Review notes."}],
    }
    out = tmp_path / "artifact"
    out.mkdir(parents=True)
    (out / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (out / "quality_report.json").write_text(json.dumps({"status": "passed", "warnings": [], "hard_failures": [], "checks": []}), encoding="utf-8")
    (out / "tab.md").write_text("# TAB\n", encoding="utf-8")

    bundle_dir = write_export(out, "daw")
    manifest_path = bundle_dir / "daw_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert bundle_dir.is_dir()
    assert manifest["strategy"] == "chunked_full_song"
    assert manifest["track_count"] == 2
    for idx in (1, 2):
        track_mid = bundle_dir / f"track-{idx:02d}.mid"
        track_musicxml = bundle_dir / f"track-{idx:02d}.musicxml"
        readme = bundle_dir / "DAW_IMPORT_README.md"
        assert track_mid.exists() and track_musicxml.exists()
        assert readme.exists()
        assert track_mid.read_bytes().startswith(b"MThd")
        assert track_musicxml.exists()
        assert "track-" in track_mid.name
    assert manifest_path.exists()


@pytest.mark.parametrize("fmt, expected", [("musicxml", "score.musicxml"), ("midi", "score.mid"), ("daw", "daw_bundle")])
def test_write_export_default_output_path_by_format(tmp_path: Path, fmt: str, expected: str) -> None:
    _write_bundle(tmp_path)

    written = write_export(tmp_path, fmt)
    assert written == tmp_path / expected
