from __future__ import annotations

from pathlib import Path

from guitar_tab_generation.demucs_runtime import build_demucs_runtime_gate


def test_demucs_gate_defaults_to_safe_plan_without_running_commands(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    gate = build_demucs_runtime_gate(
        env={"MODEL_CACHE_DIR": str(tmp_path)},
        run_command=lambda command: calls.append(command) or (0, "ok", ""),
    )

    step = gate["steps"][0]
    assert gate["runtime_check_enabled"] is False
    assert gate["gpu_enabled"] is False
    assert gate["download_enabled"] is False
    assert gate["fallback_policy"] == "no_silent_fallback"
    assert step["status"] == "planned"
    assert step["command_executed"] is False
    assert step["model_name"] == "htdemucs"
    assert step["cache_dir"] == str(tmp_path / "demucs-htdemucs")
    assert step["model_cache_dir"] == str(tmp_path / "demucs-htdemucs" / "models" / "htdemucs")
    assert calls == []


def test_demucs_gate_reports_clear_error_when_runtime_missing(tmp_path: Path) -> None:
    gate = build_demucs_runtime_gate(
        env={"MODEL_CACHE_DIR": str(tmp_path)},
        check_runtime=True,
        command_exists=lambda command: False,
        import_exists=lambda module: False,
    )

    step = gate["steps"][0]
    assert step["status"] == "failed"
    assert step["command_executed"] is False
    assert "Demucs optional runtime is not installed" in step["reason"]
    assert "uv sync --group torch-ai" in step["reason"]
    assert gate["summary"]["failed"] == 1


def test_demucs_gate_skips_when_gpu_vram_is_insufficient(tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command: list[str]) -> tuple[int, str, str]:
        calls.append(command)
        if command[0] == "nvidia-smi":
            return 0, "8192, 24564", ""
        return 0, "demucs help", ""

    gate = build_demucs_runtime_gate(
        env={"MODEL_CACHE_DIR": str(tmp_path), "GPU_TESTS_ENABLED": "1"},
        check_runtime=True,
        allow_gpu=True,
        min_free_vram_mb=12000,
        command_exists=lambda command: True,
        import_exists=lambda module: True,
        run_command=runner,
    )

    step = gate["steps"][0]
    assert step["status"] == "skipped"
    assert step["free_vram_mb"] == 8192
    assert "requires at least 12000 MB" in step["reason"]
    assert step["command_executed"] is False
    assert calls == [["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"]]


def test_demucs_gpu_gate_can_skip_without_runtime_check(tmp_path: Path) -> None:
    gate = build_demucs_runtime_gate(
        env={"MODEL_CACHE_DIR": str(tmp_path), "GPU_TESTS_ENABLED": "1"},
        allow_gpu=True,
        min_free_vram_mb=12000,
        run_command=lambda command: (0, "8192, 24564", ""),
    )

    step = gate["steps"][0]
    assert step["status"] == "skipped"
    assert step["command_executed"] is False
    assert step["free_vram_mb"] == 8192
    assert "requires at least 12000 MB" in step["reason"]


def test_demucs_gate_failed_command_does_not_fallback(tmp_path: Path) -> None:
    gate = build_demucs_runtime_gate(
        env={"MODEL_CACHE_DIR": str(tmp_path), "GPU_TESTS_ENABLED": "1"},
        check_runtime=True,
        allow_gpu=True,
        command_exists=lambda command: True,
        import_exists=lambda module: True,
        run_command=lambda command: (0, "24564, 24564", "") if command[0] == "nvidia-smi" else (2, "", "boom"),
    )

    step = gate["steps"][0]
    assert step["status"] == "failed"
    assert step["command_executed"] is True
    assert step["returncode"] == 2
    assert step["stderr"] == "boom"
    assert gate["fallback_policy"] == "no_silent_fallback"
    assert "No fallback stem will be generated" in step["reason"]
