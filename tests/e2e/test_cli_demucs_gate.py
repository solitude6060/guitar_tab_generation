from __future__ import annotations

import json

import pytest

from guitar_tab_generation.cli import main


def test_cli_demucs_gate_help_exposes_runtime_and_gpu_options(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["demucs-gate", "--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--check-runtime" in output
    assert "--allow-gpu" in output
    assert "--min-free-vram-mb" in output


def test_cli_demucs_gate_defaults_to_safe_json_plan(capsys) -> None:
    assert main(["demucs-gate", "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    step = payload["steps"][0]
    assert payload["runtime_check_enabled"] is False
    assert payload["gpu_enabled"] is False
    assert payload["download_enabled"] is False
    assert payload["fallback_policy"] == "no_silent_fallback"
    assert step["status"] == "planned"
    assert step["command_executed"] is False


def test_cli_transcribe_default_remains_fixture_and_has_no_demucs_stem_default(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["transcribe", "--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "Default is fixture" in output
    assert "--stem" not in output
    assert "demucs" not in output.lower()
