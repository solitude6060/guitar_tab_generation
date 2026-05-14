from __future__ import annotations

import json

from guitar_tab_generation.cli import main


def test_cli_doctor_ai_json_outputs_runtime_status(capsys) -> None:
    assert main(["doctor-ai", "--json"]) == 0

    output = capsys.readouterr().out
    data = json.loads(output)
    assert "python" in data
    assert "gpu" in data
    assert "ffmpeg" in data


def test_cli_ai_resources_outputs_traditional_chinese_plan(capsys) -> None:
    assert main(["ai-resources"]) == 0

    output = capsys.readouterr().out
    assert "本機優先" in output
    assert "RTX 4090" in output
    assert "MiniMax" in output
    assert "Basic Pitch" in output
    assert "Demucs" in output
