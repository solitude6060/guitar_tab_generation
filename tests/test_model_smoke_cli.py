from __future__ import annotations

import json

from guitar_tab_generation.cli import main


def test_model_smoke_json_safe_defaults(capsys) -> None:
    assert main(["model-smoke", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["download_enabled"] is False
    assert payload["gpu_enabled"] is False
    assert payload["summary"]["failed"] == 0
    assert all(step["command_executed"] is False for step in payload["steps"])


def test_model_smoke_backend_filter_json(capsys) -> None:
    assert main(["model-smoke", "--backend", "essentia", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert [step["id"] for step in payload["steps"]] == ["essentia"]
    assert payload["steps"][0]["status"] == "planned"


def test_model_smoke_plan_markdown_mentions_vram_guard(capsys) -> None:
    assert main(["model-smoke", "--backend", "demucs"]) == 0
    output = capsys.readouterr().out

    assert "# Model Smoke Plan" in output
    assert "VRAM" in output
    assert "GPU_TESTS_ENABLED=1" in output
