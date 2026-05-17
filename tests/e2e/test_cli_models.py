from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


def test_cli_models_help_lists_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["models", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    for command in ["list", "doctor", "prune"]:
        assert command in output


def test_cli_models_list_outputs_manifest_cache_state(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "models" / "basic-pitch").mkdir(parents=True)
    (tmp_path / "models" / "basic-pitch" / "weights.bin").write_bytes(b"abc")

    assert cli.main(["models", "list", "--cache-root", str(tmp_path), "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["cache_root"] == str(tmp_path)
    assert any(model["id"] == "basic-pitch" and model["exists"] for model in payload["models"])


def test_cli_models_doctor_outputs_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["models", "doctor", "--cache-root", str(tmp_path), "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["cache_root"] == str(tmp_path)
    assert payload["status"] in {"passed", "warning"}


def test_cli_models_prune_dry_run_outputs_candidates_without_delete(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    orphan = tmp_path / "old-model"
    orphan.mkdir()

    assert cli.main(["models", "prune", "--cache-root", str(tmp_path), "--dry-run", "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["dry_run"] is True
    assert payload["candidates"][0]["path"].endswith("old-model")
    assert orphan.exists()
