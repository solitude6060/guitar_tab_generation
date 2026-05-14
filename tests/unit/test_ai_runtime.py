from __future__ import annotations

from guitar_tab_generation.ai_runtime import build_resource_plan, collect_ai_runtime_status


def test_build_resource_plan_is_local_first_with_minimax_backup() -> None:
    markdown = build_resource_plan()

    assert "RTX 4090" in markdown
    assert "24GB VRAM" in markdown
    assert "Basic Pitch" in markdown
    assert "Demucs" in markdown
    assert "MiniMax" in markdown
    assert "備援" in markdown
    assert "不要把 token 寫入 repo" in markdown


def test_collect_ai_runtime_status_handles_missing_tools() -> None:
    def missing_runner(command: list[str]) -> tuple[int, str, str]:
        return 127, "", "missing"

    status = collect_ai_runtime_status(run_command=missing_runner)

    assert status["gpu"]["available"] is False
    assert status["ffmpeg"]["available"] is False
    assert status["python"]["executable"]


def test_collect_ai_runtime_status_parses_nvidia_smi() -> None:
    def runner(command: list[str]) -> tuple[int, str, str]:
        if command[0] == "nvidia-smi":
            return 0, "NVIDIA GeForce RTX 4090, 24564", ""
        if command[0] == "ffmpeg":
            return 0, "ffmpeg version 6.1", ""
        return 127, "", "missing"

    status = collect_ai_runtime_status(run_command=runner)

    assert status["gpu"]["available"] is True
    assert status["gpu"]["name"] == "NVIDIA GeForce RTX 4090"
    assert status["gpu"]["memory_mb"] == 24564
    assert status["ffmpeg"]["available"] is True
