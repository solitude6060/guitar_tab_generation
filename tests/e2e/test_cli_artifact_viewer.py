from __future__ import annotations

from pathlib import Path

import pytest

from guitar_tab_generation.cli import main


FIXTURES = [
    ("simple_chords_30_90s", "Chord progression", ["Em", "G"]),
    ("single_note_riff_30_90s", "Riff A", ["Em"]),
    ("single_note_lead_30_90s", "Lead sketch", ["Am"]),
]


@pytest.mark.parametrize("fixture_id, expected_section, expected_chords", FIXTURES)
def test_cli_view_generates_markdown_summary_for_golden_fixture(
    tmp_path: Path, fixture_id: str, expected_section: str, expected_chords: list[str]
) -> None:
    artifact_dir = tmp_path / fixture_id
    assert main([
        "transcribe",
        f"fixtures/{fixture_id}.wav",
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ]) == 0

    assert main(["view", str(artifact_dir)]) == 0

    viewer = (artifact_dir / "viewer.md").read_text(encoding="utf-8")
    assert "# Artifact Viewer" in viewer
    assert fixture_id in viewer
    assert "Quality status: passed" in viewer
    assert "Duration: unknown" not in viewer
    assert expected_section in viewer
    for chord in expected_chords:
        assert chord in viewer
    assert "## Practice readiness" in viewer
    assert "Open `tab.md`" in viewer


def test_cli_view_supports_custom_output_path(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "simple"
    custom_out = tmp_path / "custom-view.md"
    assert main([
        "transcribe",
        "fixtures/simple_chords_30_90s.wav",
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ]) == 0

    assert main(["view", str(artifact_dir), "--out", str(custom_out)]) == 0

    assert custom_out.exists()
    assert not (artifact_dir / "viewer.md").exists()
    assert "fixtures/simple_chords_30_90s.wav" in custom_out.read_text(encoding="utf-8")


def test_cli_view_fails_cleanly_when_artifact_is_missing(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()
    (artifact_dir / "tab.md").write_text("# Guitar TAB Sketch\n", encoding="utf-8")

    assert main(["view", str(artifact_dir)]) == 1
    assert not (artifact_dir / "viewer.md").exists()
