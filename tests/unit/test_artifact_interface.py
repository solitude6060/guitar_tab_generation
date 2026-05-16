from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.artifact_interface import render_artifact_interface_html, write_artifact_interface
from guitar_tab_generation.artifact_viewer import ArtifactViewerError, load_artifact_bundle


def _write_bundle(path: Path) -> None:
    arrangement = {
        "source": {"input_uri": "fixtures/<unsafe>&.wav"},
        "timebase": {"tempo_bpm": 96.0},
        "confidence": {"overall": 0.74, "notes": 0.7, "chords": 0.76, "fingering": 0.7},
        "section_spans": [{"label": "Chord <A>", "start": 0.0, "end": 8.0, "confidence": 0.68}],
        "chord_spans": [{"label": "G", "start": 0.0, "end": 4.0, "confidence": 0.8}],
        "warnings": [{"code": "LOW_CONF", "message": "Check <this> first"}],
    }
    path.mkdir(parents=True, exist_ok=True)
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")
    (path / "viewer.md").write_text("# Viewer\n", encoding="utf-8")
    (path / "tutorial.md").write_text("# Tutorial\n", encoding="utf-8")


def test_render_artifact_interface_html_escapes_and_links_artifacts(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    html = render_artifact_interface_html(load_artifact_bundle(tmp_path))

    assert "<!doctype html>" in html
    assert "Artifact Interface" in html
    assert "fixtures/&lt;unsafe&gt;&amp;.wav" in html
    assert "96.0 BPM" in html
    assert "Quality status: passed" in html
    assert "Overall confidence: 0.74" in html
    assert "LOW_CONF" in html
    assert "Check &lt;this&gt; first" in html
    assert "Chord &lt;A&gt;" in html
    assert "tab.md" in html
    assert "viewer.md" in html
    assert "tutorial.md" in html
    assert "DAW 匯入" in html
    assert "尚未建立 DAW 匯出包" in html
    assert "guitar-tab-generation export . --format daw" in html


def test_render_artifact_interface_html_uses_daw_manifest(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    daw_dir = tmp_path / "daw_bundle"
    daw_dir.mkdir()
    (daw_dir / "daw_manifest.json").write_text(
        json.dumps(
            {
                "strategy": "chunked_full_song",
                "tracks": [
                    {"name": "track-01", "midi": "track-01.mid", "musicxml": "track-01.musicxml"},
                    {"name": "track-02", "midi": "track-02.mid", "musicxml": "track-02.musicxml"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (daw_dir / "track-01.mid").write_text("MThd", encoding="utf-8")
    (daw_dir / "track-01.musicxml").write_text("<score-partwise></score-partwise>", encoding="utf-8")
    (daw_dir / "track-02.mid").write_text("MThd", encoding="utf-8")
    (daw_dir / "track-02.musicxml").write_text("<score-partwise></score-partwise>", encoding="utf-8")

    html = render_artifact_interface_html(load_artifact_bundle(tmp_path))

    assert "DAW 匯出策略" in html
    assert "chunked_full_song" in html
    assert "track-01.mid" in html
    assert "track-02.musicxml" in html
    assert "GarageBand" in html


def test_write_artifact_interface_defaults_to_artifact_dir(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    written = write_artifact_interface(tmp_path)

    assert written == tmp_path / "interface.html"
    assert "Artifact Interface" in written.read_text(encoding="utf-8")


def test_write_artifact_interface_uses_artifact_contract_errors(tmp_path: Path) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "tab.md").write_text("# TAB\n", encoding="utf-8")

    with pytest.raises(ArtifactViewerError, match="arrangement.json"):
        write_artifact_interface(tmp_path)
