from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.artifact_viewer import (
    ArtifactViewerError,
    load_artifact_bundle,
    render_artifact_viewer_markdown,
    write_artifact_viewer,
)


def _write_bundle(path: Path) -> None:
    arrangement = {
        "schema_version": "0.1.0",
        "source": {"input_uri": "fixtures/simple_chords_30_90s.wav"},
        "timebase": {"tempo_bpm": 92.0},
        "duration_seconds": 45.0,
        "confidence": {"overall": 0.88, "notes": 0.81, "chords": 0.9, "fingering": 0.86},
        "section_spans": [
            {"label": "Chord progression", "start": 0.0, "end": 16.0, "confidence": 0.82},
        ],
        "chord_spans": [
            {"label": "Em", "start": 0.0, "end": 4.0, "confidence": 0.91},
            {"label": "G", "start": 4.0, "end": 8.0, "confidence": 0.89},
        ],
        "warnings": [
            {"code": "LOW_FINGERING_CONFIDENCE", "severity": "warning", "message": "Check fingering."},
        ],
    }
    quality_report = {"status": "passed", "hard_failures": []}
    path.mkdir(parents=True, exist_ok=True)
    (path / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (path / "quality_report.json").write_text(json.dumps(quality_report), encoding="utf-8")
    (path / "tab.md").write_text("# Guitar TAB Sketch\n\n## TAB\n", encoding="utf-8")


def test_load_artifact_bundle_requires_core_artifacts(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    bundle = load_artifact_bundle(tmp_path)

    assert bundle.artifact_dir == tmp_path
    assert bundle.arrangement["source"]["input_uri"] == "fixtures/simple_chords_30_90s.wav"
    assert bundle.quality_report["status"] == "passed"
    assert "Guitar TAB Sketch" in bundle.tab_markdown


@pytest.mark.parametrize("missing", ["arrangement.json", "quality_report.json", "tab.md"])
def test_load_artifact_bundle_reports_missing_artifact(tmp_path: Path, missing: str) -> None:
    _write_bundle(tmp_path)
    (tmp_path / missing).unlink()

    with pytest.raises(ArtifactViewerError, match=missing):
        load_artifact_bundle(tmp_path)


def test_render_artifact_viewer_markdown_contains_demo_sections(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    markdown = render_artifact_viewer_markdown(load_artifact_bundle(tmp_path))

    assert "# Artifact Viewer" in markdown
    assert "fixtures/simple_chords_30_90s.wav" in markdown
    assert "92.0 BPM" in markdown
    assert "Quality status: passed" in markdown
    assert "Chord progression" in markdown
    assert "Em → G" in markdown
    assert "LOW_FINGERING_CONFIDENCE" in markdown
    assert "## Practice readiness" in markdown
    assert "Open `tab.md`" in markdown


def test_load_artifact_bundle_ignores_legacy_chords_list_sidecar(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    (tmp_path / "chords.json").write_text(json.dumps([{"label": "Em"}]), encoding="utf-8")

    bundle = load_artifact_bundle(tmp_path)
    markdown = render_artifact_viewer_markdown(bundle)

    assert bundle.chord_detection is None
    assert "## Chord Detection Sidecar" not in markdown


def test_load_artifact_bundle_ignores_legacy_sections_list_sidecar(tmp_path: Path) -> None:
    _write_bundle(tmp_path)
    (tmp_path / "sections.json").write_text(json.dumps([{"label": "A"}]), encoding="utf-8")

    bundle = load_artifact_bundle(tmp_path)
    markdown = render_artifact_viewer_markdown(bundle)

    assert bundle.section_detection is None
    assert "## Section Detection Sidecar" not in markdown


def test_write_artifact_viewer_defaults_to_artifact_dir(tmp_path: Path) -> None:
    _write_bundle(tmp_path)

    written = write_artifact_viewer(tmp_path)

    assert written == tmp_path / "viewer.md"
    assert "# Artifact Viewer" in written.read_text(encoding="utf-8")
