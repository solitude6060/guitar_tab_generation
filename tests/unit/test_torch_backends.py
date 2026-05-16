from __future__ import annotations

from guitar_tab_generation.torch_backends import (
    build_torch_backend_smoke_gate,
    collect_torch_backend_status,
    format_torch_backend_status_markdown,
    selected_torch_backend_routes,
)


def test_torch_backend_routes_are_roadmap_only_and_local_first() -> None:
    routes = selected_torch_backend_routes()
    ids = {route["id"] for route in routes}

    assert {"torchcrepe-f0", "demucs-htdemucs", "mt3-transcription"} <= ids
    assert all(route["framework"] == "pytorch" for route in routes)
    assert all(route["local_first"] is True for route in routes)
    assert all(route["auto_install"] is False for route in routes)


def test_torch_backend_status_uses_injected_probes_without_importing_torch() -> None:
    status = collect_torch_backend_status(
        command_exists=lambda command: command == "demucs",
        import_exists=lambda module: module in {"torch", "torchcrepe"},
    )
    by_id = {route["id"]: route for route in status["routes"]}

    assert status["default_backend_policy"] == "fixture remains default; basic-pitch remains explicit"
    assert by_id["torchcrepe-f0"]["runtime_available"] is True
    assert by_id["demucs-htdemucs"]["runtime_available"] is True
    assert by_id["mt3-transcription"]["runtime_available"] is False
    assert by_id["torchcrepe-f0"]["next_action"] == "eligible for future implementation phase; do not auto-install"


def test_torch_smoke_gate_defaults_to_planned_and_never_uses_gpu() -> None:
    calls: list[list[str]] = []

    gate = build_torch_backend_smoke_gate(
        env={},
        route_ids=["torchcrepe-f0", "demucs-htdemucs"],
        run_command=lambda command: calls.append(command) or (0, "", ""),
    )

    assert gate["gpu_enabled"] is False
    assert gate["smoke_enabled"] is False
    assert calls == []
    assert {step["status"] for step in gate["steps"]} == {"planned", "skipped"}
    assert gate["summary"]["failed"] == 0


def test_torch_smoke_gate_enforces_vram_before_gpu_sensitive_route() -> None:
    def runner(command: list[str]) -> tuple[int, str, str]:
        if command[0] == "nvidia-smi":
            return 0, "8192, 24564", ""
        return 0, "ok", ""

    gate = build_torch_backend_smoke_gate(
        env={"GPU_TESTS_ENABLED": "1", "TORCH_SMOKE_RUN": "1"},
        route_ids=["demucs-htdemucs"],
        min_free_vram_mb=12000,
        run_command=runner,
    )

    step = gate["steps"][0]
    assert step["status"] == "skipped"
    assert step["free_vram_mb"] == 8192
    assert "requires at least 12000 MB" in step["reason"]
    assert step["command_executed"] is False


def test_torch_smoke_gate_uses_route_specific_vram_by_default() -> None:
    def runner(command: list[str]) -> tuple[int, str, str]:
        if command[0] == "nvidia-smi":
            return 0, "6000, 24564", ""
        return 0, "ok", ""

    gate = build_torch_backend_smoke_gate(
        env={"GPU_TESTS_ENABLED": "1", "TORCH_SMOKE_RUN": "1"},
        route_ids=["torchcrepe-f0"],
        run_command=runner,
    )

    step = gate["steps"][0]
    assert step["min_free_vram_mb"] == 4000
    assert step["status"] == "ready"
    assert step["command_executed"] is True


def test_torch_backend_markdown_is_traditional_chinese() -> None:
    markdown = format_torch_backend_status_markdown(
        collect_torch_backend_status(
            command_exists=lambda command: False,
            import_exists=lambda module: module == "torch",
        )
    )

    assert "# Torch-first AI Backend Roadmap" in markdown
    assert "不取代 Basic Pitch" in markdown
    assert "本機優先" in markdown
    assert "不自動安裝" in markdown
