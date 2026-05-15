from __future__ import annotations

import json

from guitar_tab_generation.cli import main


def test_ai_backends_json_cli_outputs_registry(capsys) -> None:
    assert main(["ai-backends", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["resource_profile"] == "local-rtx-4090-first"
    assert {backend["id"] for backend in payload["backends"]} >= {"basic-pitch", "demucs", "torchcrepe"}
    assert all(backend["local_first"] is True for backend in payload["backends"])


def test_ai_backends_markdown_cli_outputs_registry(capsys) -> None:
    assert main(["ai-backends"]) == 0
    output = capsys.readouterr().out

    assert "# 本機 AI Backend 狀態" in output
    assert "Basic Pitch" in output
    assert "Demucs" in output


def test_doctor_ai_json_includes_ai_backends(capsys) -> None:
    assert main(["doctor-ai", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert "ai_backends" in payload
    assert payload["ai_backends"]["resource_profile"] == "local-rtx-4090-first"
    assert isinstance(payload["ai_backends"]["backends"], list)
