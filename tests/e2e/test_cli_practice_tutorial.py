from __future__ import annotations

from pathlib import Path

import pytest

from guitar_tab_generation.cli import main


FIXTURES = [
    ("simple_chords_30_90s", "Chord progression", ["G", "D", "Em", "C"]),
    ("single_note_riff_30_90s", "Riff A", ["Em"]),
    ("single_note_lead_30_90s", "Lead sketch", ["Am"]),
]


@pytest.mark.parametrize("fixture_id, expected_section, expected_chords", FIXTURES)
def test_cli_tutorial_generates_practice_markdown_for_golden_fixture(
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

    assert main(["tutorial", str(artifact_dir)]) == 0

    tutorial = (artifact_dir / "tutorial.md").read_text(encoding="utf-8")
    assert "# Practice Tutorial" in tutorial
    assert fixture_id in tutorial
    assert "## Readiness check" in tutorial
    assert "## Tempo ladder" in tutorial
    assert "50%" in tutorial and "75%" in tutorial and "100%" in tutorial
    assert expected_section in tutorial
    for chord in expected_chords:
        assert chord in tutorial
    assert "## Section loop plan" in tutorial
    assert "## Chord practice plan" in tutorial
    assert "## Lead/riff practice plan" in tutorial
    assert "## Safety note" in tutorial
    assert "Open `tab.md`" in tutorial


def test_cli_tutorial_supports_custom_output_path(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "riff"
    custom_out = tmp_path / "custom-tutorial.md"
    assert main([
        "transcribe",
        "fixtures/single_note_riff_30_90s.wav",
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ]) == 0

    assert main(["tutorial", str(artifact_dir), "--out", str(custom_out)]) == 0

    assert custom_out.exists()
    assert not (artifact_dir / "tutorial.md").exists()
    assert "single_note_riff_30_90s" in custom_out.read_text(encoding="utf-8")


def test_cli_tutorial_fake_llm_backend_adds_cited_coaching_notes(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "riff"
    assert main([
        "transcribe",
        "fixtures/single_note_riff_30_90s.wav",
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ]) == 0

    assert main(["tutorial", str(artifact_dir), "--llm-backend", "fake"]) == 0

    tutorial = (artifact_dir / "tutorial.md").read_text(encoding="utf-8")
    assert "## LLM Coaching Notes" in tutorial
    assert "`arrangement.json`" in tutorial
    assert "`quality_report.json`" in tutorial


def test_cli_tutorial_local_llm_backend_fails_without_fallback(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "riff"
    assert main([
        "transcribe",
        "fixtures/single_note_riff_30_90s.wav",
        "--backend",
        "fixture",
        "--out",
        str(artifact_dir),
    ]) == 0

    assert main(["tutorial", str(artifact_dir), "--llm-backend", "local"]) == 1
    assert not (artifact_dir / "tutorial.md").exists()


def test_cli_tutorial_fails_cleanly_when_artifact_is_missing(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "broken"
    artifact_dir.mkdir()
    (artifact_dir / "tab.md").write_text("# Guitar TAB Sketch\n", encoding="utf-8")

    assert main(["tutorial", str(artifact_dir)]) == 1
    assert not (artifact_dir / "tutorial.md").exists()
