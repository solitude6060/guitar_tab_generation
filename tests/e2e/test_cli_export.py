from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET
import wave

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


def test_cli_export_daw_bundle_for_fullsong_golden_window(tmp_path: Path) -> None:
    audio_path = tmp_path / "full_song_for_daw_bundle.wav"
    # 180s at 48k mono with 1 byte/sample.
    artifact_dir = tmp_path / "full_song_artifact"
    with wave.open(str(audio_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(48_000)
        handle.writeframes(b"\0" * 8_640_000)

    assert main([
        "transcribe",
        str(audio_path),
        "--backend",
        "fixture",
        "--trim-end",
        "180",
        "--out",
        str(artifact_dir),
    ]) == 0
    assert main(["export", str(artifact_dir), "--format", "daw"]) == 0

    bundle_dir = artifact_dir / "daw_bundle"
    assert bundle_dir.is_dir()
    manifest = json.loads((bundle_dir / "daw_manifest.json").read_text(encoding="utf-8"))
    assert manifest["track_count"] >= 1
    assert manifest["strategy"] == "chunked_full_song"
    assert (bundle_dir / "DAW_IMPORT_README.md").exists()
    for track in manifest["tracks"]:
        assert (bundle_dir / track["midi"]).exists()
        assert (bundle_dir / track["musicxml"]).exists()


def test_cli_export_fails_cleanly_when_artifact_is_missing(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()

    assert main(["export", str(artifact_dir), "--format", "musicxml"]) == 1
    assert not (artifact_dir / "score.musicxml").exists()
