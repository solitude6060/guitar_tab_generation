from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.cli import main
from tests.support.contract_validators import assert_arrangement_contract, assert_quality_report_contract


FIXTURES = {
    "simple_chords_30_90s": {"section": "Chord progression", "chord": "Em"},
    "single_note_riff_30_90s": {"section": "Riff A", "chord": "Em"},
    "single_note_lead_30_90s": {"section": "Lead sketch", "chord": "Am"},
}
EXPECTED_ARTIFACTS = {
    "audio_normalized.wav",
    "arrangement.json",
    "quality_report.json",
    "tab.md",
    "notes.json",
    "chords.json",
    "sections.json",
}


@pytest.mark.parametrize("fixture_id, expected", FIXTURES.items())
def test_cli_transcribe_fixture_writes_complete_artifact_contract(tmp_path: Path, fixture_id: str, expected: dict[str, str]) -> None:
    out_dir = tmp_path / fixture_id
    exit_code = main([
        "transcribe",
        f"fixtures/{fixture_id}.wav",
        "--backend",
        "fixture",
        "--out",
        str(out_dir),
    ])

    assert exit_code == 0
    assert {path.name for path in out_dir.iterdir()} >= EXPECTED_ARTIFACTS

    arrangement = json.loads((out_dir / "arrangement.json").read_text(encoding="utf-8"))
    quality_report = json.loads((out_dir / "quality_report.json").read_text(encoding="utf-8"))
    notes = json.loads((out_dir / "notes.json").read_text(encoding="utf-8"))
    chords = json.loads((out_dir / "chords.json").read_text(encoding="utf-8"))
    sections = json.loads((out_dir / "sections.json").read_text(encoding="utf-8"))
    tab = (out_dir / "tab.md").read_text(encoding="utf-8")

    assert_arrangement_contract(arrangement)
    assert_quality_report_contract(quality_report, arrangement)
    assert quality_report["status"] == "passed"
    assert expected["section"] in {section["label"] for section in arrangement["section_spans"]}
    assert expected["chord"] in {chord["label"] for chord in arrangement["chord_spans"]}
    assert notes == arrangement["note_events"]
    assert chords == arrangement["chord_spans"]
    assert sections == arrangement["section_spans"]

    assert fixture_id in arrangement["source"]["input_uri"]
    assert "## Metadata" in tab
    assert "## Sections" in tab
    assert "## Chords" in tab
    assert "## TAB" in tab
    assert "## Warnings" in tab
    assert "## Quality" in tab
    assert expected["section"] in tab
    assert expected["chord"] in tab
    assert "- None" in tab or all(warning["code"] in tab for warning in arrangement["warnings"])


def test_cli_url_policy_gate_writes_no_media_artifacts(tmp_path: Path) -> None:
    out_dir = tmp_path / "url"
    exit_code = main([
        "transcribe",
        "https://www.youtube.com/watch?v=example",
        "--out",
        str(out_dir),
    ])

    assert exit_code == 2
    assert (out_dir / "policy_gate.txt").exists()
    assert "local-audio-first" in (out_dir / "policy_gate.txt").read_text(encoding="utf-8")
    assert not any((out_dir / name).exists() for name in EXPECTED_ARTIFACTS)
