from __future__ import annotations

from guitar_tab_generation.model_smoke import build_model_smoke_plan, format_model_smoke_markdown


def test_default_plan_does_not_download_or_use_gpu() -> None:
    calls: list[list[str]] = []

    plan = build_model_smoke_plan(env={}, run_command=lambda command: calls.append(command) or (0, "", ""))

    assert plan["download_enabled"] is False
    assert plan["gpu_enabled"] is False
    assert calls == []
    assert {step["id"] for step in plan["steps"]} >= {"basic-pitch", "demucs", "torchcrepe", "essentia", "local-llm"}
    assert all(step["command_executed"] is False for step in plan["steps"])
    assert plan["summary"]["failed"] == 0


def test_download_requires_explicit_opt_in() -> None:
    calls: list[list[str]] = []

    disabled = build_model_smoke_plan(
        env={},
        backends=["basic-pitch"],
        run_command=lambda command: calls.append(command) or (0, "downloaded", ""),
    )
    assert disabled["steps"][0]["status"] == "planned"
    assert calls == []

    enabled = build_model_smoke_plan(
        env={},
        backends=["basic-pitch"],
        download=True,
        run_command=lambda command: calls.append(command) or (0, "downloaded", ""),
    )
    assert enabled["steps"][0]["status"] == "ready"
    assert enabled["steps"][0]["command_executed"] is True
    assert calls == [enabled["steps"][0]["download_command"]]


def test_gpu_backend_skips_when_gpu_disabled() -> None:
    plan = build_model_smoke_plan(env={}, backends=["demucs"])

    step = plan["steps"][0]
    assert step["id"] == "demucs"
    assert step["status"] == "skipped"
    assert "GPU_TESTS_ENABLED=1" in step["reason"]
    assert step["command_executed"] is False


def test_gpu_backend_skips_when_free_vram_below_threshold() -> None:
    def runner(command: list[str]) -> tuple[int, str, str]:
        if command[0] == "nvidia-smi":
            return 0, "4096, 24564", ""
        return 0, "downloaded", ""

    plan = build_model_smoke_plan(
        env={"GPU_TESTS_ENABLED": "1"},
        backends=["demucs"],
        download=True,
        min_free_vram_mb=12000,
        run_command=runner,
    )

    step = plan["steps"][0]
    assert step["status"] == "skipped"
    assert step["free_vram_mb"] == 4096
    assert "12000 MB" in step["reason"]
    assert step["command_executed"] is False


def test_backend_filter_limits_plan() -> None:
    plan = build_model_smoke_plan(env={}, backends=["essentia"])

    assert [step["id"] for step in plan["steps"]] == ["essentia"]
    assert plan["steps"][0]["status"] == "planned"


def test_plan_markdown_mentions_vram_guard() -> None:
    markdown = format_model_smoke_markdown(build_model_smoke_plan(env={}, backends=["demucs"]))

    assert "VRAM" in markdown
    assert "GPU_TESTS_ENABLED=1" in markdown
    assert "預設不下載" in markdown
