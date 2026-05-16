from __future__ import annotations

import json

import pytest

from guitar_tab_generation.cli import main


def test_cli_torch_backends_outputs_traditional_chinese(capsys) -> None:
    assert main(["torch-backends"]) == 0

    output = capsys.readouterr().out
    assert "# Torch-first AI Backend Roadmap" in output
    assert "不取代 Basic Pitch" in output
    assert "不自動安裝" in output


def test_cli_torch_backends_json(capsys) -> None:
    assert main(["torch-backends", "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    ids = {route["id"] for route in payload["routes"]}
    assert "torchcrepe-f0" in ids
    assert payload["default_backend_policy"] == "fixture remains default; basic-pitch remains explicit"


def test_cli_torch_smoke_defaults_to_safe_plan(capsys) -> None:
    assert main(["torch-smoke", "--route", "torchcrepe-f0"]) == 0

    output = capsys.readouterr().out
    assert "# Torch Smoke Gate" in output
    assert "Smoke enabled: False" in output
    assert "GPU enabled: False" in output


def test_cli_torch_smoke_exposes_device_option_for_real_torchcrepe_gate(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["torch-smoke", "--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "--device" in output
    assert "cpu" in output
    assert "cuda" in output


def test_cli_torch_smoke_rejects_unknown_route(capsys) -> None:
    assert main(["torch-smoke", "--route", "missing-route"]) == 1

    err = capsys.readouterr().err
    assert "Torch smoke error" in err


def test_cli_torch_smoke_cuda_device_skips_without_gpu_opt_in(capsys) -> None:
    assert main(["torch-smoke", "--route", "torchcrepe-f0", "--run", "--device", "cuda", "--json"]) == 0

    payload = json.loads(capsys.readouterr().out)
    step = payload["steps"][0]
    assert step["status"] == "skipped"
    assert step["command_executed"] is False
    assert "--allow-gpu" in step["reason"]
