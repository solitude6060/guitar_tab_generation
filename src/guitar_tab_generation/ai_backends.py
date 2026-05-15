"""Local-first AI backend registry.

This module is intentionally inspection-only: it reports whether selected local
model/tool routes appear available without importing heavy dependencies or
running inference.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import importlib.util
import shutil
from typing import Callable, Any


CommandExists = Callable[[str], bool]
ImportExists = Callable[[str], bool]


@dataclass(frozen=True)
class AIBackendSpec:
    id: str
    label: str
    category: str
    product_role: str
    selected_runtime: str
    command: str | None
    python_import: str | None
    gpu_profile: str
    local_first: bool = True


def selected_backend_specs() -> list[dict[str, Any]]:
    """Return the selected local model/tool route without probing the machine."""

    specs = [
        AIBackendSpec(
            id="basic-pitch",
            label="Basic Pitch",
            category="pitch_transcription",
            product_role="polyphonic note sketch extraction from normalized audio",
            selected_runtime="basic_pitch optional package or basic-pitch CLI",
            command="basic-pitch",
            python_import="basic_pitch",
            gpu_profile="lightweight_cpu_or_gpu",
        ),
        AIBackendSpec(
            id="demucs",
            label="Demucs / HTDemucs",
            category="stem_separation",
            product_role="guitar/vocal/drums/bass source separation before transcription",
            selected_runtime="demucs CLI with htdemucs-family model",
            command="demucs",
            python_import="demucs",
            gpu_profile="single_gpu_sequential_on_4090",
        ),
        AIBackendSpec(
            id="torchcrepe",
            label="CREPE / torchcrepe",
            category="pitch_calibration",
            product_role="monophonic pitch confidence calibration for solo/riff passages",
            selected_runtime="torchcrepe optional Python package",
            command=None,
            python_import="torchcrepe",
            gpu_profile="gpu_optional",
        ),
        AIBackendSpec(
            id="essentia",
            label="Essentia / librosa-style features",
            category="rhythm_features",
            product_role="tempo, beat, onset, and audio feature extraction",
            selected_runtime="essentia optional Python package",
            command=None,
            python_import="essentia",
            gpu_profile="cpu_first",
        ),
        AIBackendSpec(
            id="local-llm",
            label="Local LLM",
            category="teaching_generation",
            product_role="practice tutorial text over artifacts only",
            selected_runtime="local runtime such as ollama; never source of truth for notes",
            command="ollama",
            python_import=None,
            gpu_profile="quantized_model_after_audio_jobs",
        ),
    ]
    return [asdict(spec) for spec in specs]


def _default_command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _default_import_exists(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def collect_ai_backend_status(
    *,
    command_exists: CommandExists = _default_command_exists,
    import_exists: ImportExists = _default_import_exists,
) -> dict[str, Any]:
    """Collect local AI backend availability without importing heavy packages."""

    backends: list[dict[str, Any]] = []
    for spec in selected_backend_specs():
        command = spec["command"]
        python_import = spec["python_import"]
        command_available = command_exists(command) if command else None
        import_available = import_exists(python_import) if python_import else None
        available = bool(command_available) or bool(import_available)
        status = "available" if available else "missing"
        backend = {
            **spec,
            "command_available": command_available,
            "import_available": import_available,
            "available": available,
            "status": status,
            "next_action": (
                "ready for optional backend integration"
                if available
                else "install locally only when this backend phase starts; do not add secrets or cloud fallback"
            ),
        }
        backends.append(backend)

    return {
        "resource_profile": "local-rtx-4090-first",
        "local_first": True,
        "cloud_policy": "MiniMax is backup for creative assistance only; it is not a transcription source of truth.",
        "backends": backends,
    }


def format_ai_backend_status_markdown(status: dict[str, Any]) -> str:
    """Format AI backend status as Traditional Chinese Markdown."""

    lines = [
        "# 本機 AI Backend 狀態",
        "",
        f"- Resource profile: {status['resource_profile']}",
        "- 本機優先：所有音訊辨識 backend 都應先在本機執行。",
        "- MiniMax：只作創作/教學備援，不作音符辨識 truth source。",
        "",
        "| Backend | 角色 | Runtime | 狀態 | 下一步 |",
        "|---|---|---|---|---|",
    ]
    for backend in status["backends"]:
        state = "可用" if backend["available"] else "未安裝"
        lines.append(
            "| {label} | {role} | {runtime} | {state} | {next_action} |".format(
                label=backend["label"],
                role=backend["product_role"],
                runtime=backend["selected_runtime"],
                state=state,
                next_action=backend["next_action"],
            )
        )
    lines.append("")
    return "\n".join(lines)
