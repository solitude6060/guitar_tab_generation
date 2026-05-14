from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from guitar_tab_generation.cli import main


FIXTURES = ["simple_chords_30_90s", "single_note_riff_30_90s", "single_note_lead_30_90s"]


@pytest.mark.parametrize("fixture_id", FIXTURES)
def test_cli_export_musicxml_for_golden_fixture(tmp_path: Path, fixture_id: str) -> None:
    artifact_dir = tmp_path / fixture_id
    assert main(["transcribe", f"fixtures/{fixture_id}.wav", "--backend", "fixture", "--out", str(artifact_dir)]) == 0

    assert main(["export", str(artifact_dir), "--format", "musicxml"]) == 0

    out = artifact_dir / "score.musicxml"
    assert out.exists()
    assert ET.parse(out).getroot().tag == "score-partwise"
    assert fixture_id in out.read_text(encoding="utf-8")


@pytest.mark.parametrize("fixture_id", FIXTURES)
def test_cli_export_midi_for_golden_fixture(tmp_path: Path, fixture_id: str) -> None:
    artifact_dir = tmp_path / fixture_id
    assert main(["transcribe", f"fixtures/{fixture_id}.wav", "--backend", "fixture", "--out", str(artifact_dir)]) == 0

    assert main(["export", str(artifact_dir), "--format", "midi"]) == 0

    out = artifact_dir / "score.mid"
    assert out.exists()
    assert out.read_bytes().startswith(b"MThd")


def test_cli_export_fails_cleanly_when_artifact_is_missing(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()

    assert main(["export", str(artifact_dir), "--format", "musicxml"]) == 1
    assert not (artifact_dir / "score.musicxml").exists()
