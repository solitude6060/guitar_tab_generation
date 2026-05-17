from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


def test_cli_jobs_help_lists_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["jobs", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    for command in ["submit", "status", "run-next", "cancel", "resume"]:
        assert command in output


def test_cli_jobs_submit_status_and_run_next_cpu_job(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        cli.main(
            [
                "jobs",
                "submit",
                str(tmp_path),
                "--job-id",
                "demo",
                "--command",
                "view",
                "--command",
                "song",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert cli.main(["jobs", "status", str(tmp_path), "--json"]) == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["jobs"][0]["job_id"] == "demo"

    assert cli.main(["jobs", "run-next", str(tmp_path), "--json"]) == 0
    run_payload = json.loads(capsys.readouterr().out)
    assert run_payload["status"] == "completed"


def test_cli_jobs_gpu_low_vram_defers_with_fake_probe(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert (
        cli.main(
            [
                "jobs",
                "submit",
                str(tmp_path),
                "--job-id",
                "gpu",
                "--gpu",
                "--allow-gpu",
                "--command",
                "separate-stems",
            ]
        )
        == 0
    )
    capsys.readouterr()

    assert (
        cli.main(
            [
                "jobs",
                "run-next",
                str(tmp_path),
                "--allow-gpu",
                "--min-free-vram-mb",
                "12000",
                "--fake-free-vram-mb",
                "8000",
                "--json",
            ]
        )
        == 3
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "deferred"
    assert "free VRAM" in payload["reason"]
