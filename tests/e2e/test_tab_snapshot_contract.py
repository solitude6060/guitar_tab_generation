from __future__ import annotations

from pathlib import Path

import pytest

from guitar_tab_generation.cli import main


CASES = {
    "simple_chords_30_90s": ["Chord progression", "G", "D", "Em", "C"],
    "single_note_riff_30_90s": ["Riff A", "Em", "## TAB", "confidence"],
    "single_note_lead_30_90s": ["Lead sketch", "Am", "## TAB", "confidence"],
}


@pytest.mark.parametrize("fixture_id, expected_terms", CASES.items())
def test_fixture_tab_contains_practice_contract_sections(tmp_path: Path, fixture_id: str, expected_terms: list[str]) -> None:
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
    tab = (out_dir / "tab.md").read_text(encoding="utf-8")
    for heading in ["## Metadata", "## Sections", "## Chords", "## TAB", "## Warnings", "## Quality"]:
        assert heading in tab
    for term in expected_terms:
        assert term in tab
    assert "Overall confidence" in tab
    assert "[UNPLAYABLE omitted]" not in tab
