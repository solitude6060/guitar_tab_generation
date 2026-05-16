from __future__ import annotations

from pathlib import Path

import wave

import pytest

from guitar_tab_generation.cli import main


FIXTURES = ["simple_chords_30_90s", "single_note_riff_30_90s", "single_note_lead_30_90s"]


def _write_silent_wav(path: Path, duration_seconds: float, *, sample_rate: int = 800) -> None:
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(1)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\0" * int(duration_seconds * sample_rate))


@pytest.mark.parametrize("fixture_id", FIXTURES)
def test_cli_interface_generates_html_workspace_for_golden_fixture(tmp_path: Path, fixture_id: str) -> None:
    artifact_dir = tmp_path / fixture_id
    assert main(["transcribe", f"fixtures/{fixture_id}.wav", "--backend", "fixture", "--out", str(artifact_dir)]) == 0
    assert main(["view", str(artifact_dir)]) == 0
    assert main(["tutorial", str(artifact_dir)]) == 0

    assert main(["interface", str(artifact_dir)]) == 0

    html = (artifact_dir / "interface.html").read_text(encoding="utf-8")
    assert "<!doctype html>" in html
    assert fixture_id in html
    assert "Quality status: passed" in html
    assert "Warnings" in html
    assert "Confidence" in html
    assert "tab.md" in html
    assert "viewer.md" in html
    assert "tutorial.md" in html


def test_cli_interface_supports_custom_output_path(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "simple"
    custom_out = tmp_path / "custom-interface.html"
    assert main(["transcribe", "fixtures/simple_chords_30_90s.wav", "--backend", "fixture", "--out", str(artifact_dir)]) == 0

    assert main(["interface", str(artifact_dir), "--out", str(custom_out)]) == 0

    assert custom_out.exists()
    assert not (artifact_dir / "interface.html").exists()
    assert "simple_chords_30_90s" in custom_out.read_text(encoding="utf-8")


def test_cli_interface_fails_cleanly_when_artifact_is_missing(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()
    (artifact_dir / "tab.md").write_text("# Guitar TAB Sketch\n", encoding="utf-8")

    assert main(["interface", str(artifact_dir)]) == 1
    assert not (artifact_dir / "interface.html").exists()


def test_cli_interface_shows_daw_tracks_after_export(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "full_song"
    audio_path = tmp_path / "full_song_180.wav"
    _write_silent_wav(audio_path, 180.0)

    assert main(["transcribe", str(audio_path), "--backend", "fixture", "--out", str(artifact_dir)]) == 0
    assert main(["export", str(artifact_dir), "--format", "daw"]) == 0
    assert main(["interface", str(artifact_dir)]) == 0

    html = (artifact_dir / "interface.html").read_text(encoding="utf-8")
    assert "DAW 匯出策略" in html
    assert "track-01.mid" in html
    assert "track-01.musicxml" in html
    assert "track-02.mid" in html
    assert "track-02.musicxml" in html
    assert "建議匯入" in html
