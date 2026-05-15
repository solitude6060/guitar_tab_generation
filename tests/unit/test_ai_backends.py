from __future__ import annotations

from guitar_tab_generation.ai_backends import (
    collect_ai_backend_status,
    format_ai_backend_status_markdown,
    selected_backend_specs,
)


def test_backend_registry_lists_selected_local_models() -> None:
    specs = selected_backend_specs()
    ids = {spec["id"] for spec in specs}

    assert {"basic-pitch", "demucs", "torchcrepe", "essentia", "local-llm"} <= ids
    assert all(spec["local_first"] is True for spec in specs)
    assert any(spec["category"] == "pitch_transcription" for spec in specs)
    assert any(spec["category"] == "stem_separation" for spec in specs)


def test_backend_status_uses_injected_command_and_import_checks() -> None:
    commands = {"basic-pitch", "demucs", "ollama"}
    imports = {"basic_pitch", "torchcrepe"}

    status = collect_ai_backend_status(
        command_exists=lambda command: command in commands,
        import_exists=lambda module: module in imports,
    )
    by_id = {backend["id"]: backend for backend in status["backends"]}

    assert status["resource_profile"] == "local-rtx-4090-first"
    assert by_id["basic-pitch"]["available"] is True
    assert by_id["demucs"]["available"] is True
    assert by_id["torchcrepe"]["available"] is True
    assert by_id["essentia"]["available"] is False
    assert by_id["local-llm"]["command_available"] is True


def test_backend_markdown_is_traditional_chinese_and_local_first() -> None:
    status = collect_ai_backend_status(
        command_exists=lambda command: command == "demucs",
        import_exists=lambda module: False,
    )

    markdown = format_ai_backend_status_markdown(status)

    assert "# 本機 AI Backend 狀態" in markdown
    assert "Basic Pitch" in markdown
    assert "Demucs" in markdown
    assert "本機優先" in markdown
    assert "MiniMax" in markdown
