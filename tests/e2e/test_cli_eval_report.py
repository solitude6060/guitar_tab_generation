from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


FIXTURES = [
    ("simple_chords_30_90s", "out/simple_chords"),
    ("single_note_riff_30_90s", "out/riff"),
    ("single_note_lead_30_90s", "out/lead"),
]


def test_cli_eval_report_help_lists_manifest_and_out(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["eval-report", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "artifact_root" in output
    assert "--manifest" in output
    assert "--out" in output


def test_cli_eval_report_scores_golden_fixture_outputs(tmp_path: Path) -> None:
    for fixture_id, relative_out in FIXTURES:
        assert (
            cli.main(
                [
                    "transcribe",
                    f"fixtures/{fixture_id}.wav",
                    "--backend",
                    "fixture",
                    "--out",
                    str(tmp_path / relative_out),
                ]
            )
            == 0
        )

    manifest = Path("tests/fixtures/golden_manifest.json")
    assert cli.main(["eval-report", str(tmp_path), "--manifest", str(manifest)]) == 0
    payload = json.loads((tmp_path / "eval_report.json").read_text(encoding="utf-8"))

    assert payload["summary"]["status"] == "passed"
    assert payload["summary"]["fixture_count"] == 3
    assert payload["summary"]["artifact_count"] == 3
    assert payload["summary"]["average_rubric_score"] >= 3.0
    assert all("notes" in fixture["metrics"] for fixture in payload["fixtures"])
    assert all("chords" in fixture["metrics"] for fixture in payload["fixtures"])
    assert all("sections" in fixture["metrics"] for fixture in payload["fixtures"])
    assert all("playability" in fixture["metrics"] for fixture in payload["fixtures"])
