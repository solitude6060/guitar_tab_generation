"""Demucs runtime planning and install gates.

P24 deliberately stops at runtime/cache/GPU planning. It does not run source
separation, download weights, or write stem artifacts.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any, Callable, Mapping


CommandExists = Callable[[str], bool]
ImportExists = Callable[[str], bool]
CommandRunner = Callable[[list[str]], tuple[int, str, str]]
TRUE_VALUES = {"1", "true", "yes", "on"}
DEFAULT_MODEL_NAME = "htdemucs"
DEFAULT_MIN_FREE_VRAM_MB = 12_000


def _default_command_exists(command: str) -> bool:
    return shutil.which(command) is not None


def _default_import_exists(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def _default_runner(command: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=120)
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in TRUE_VALUES


def _default_cache_root(env: Mapping[str, str]) -> Path:
    configured = env.get("MODEL_CACHE_DIR") or env.get("AI_MODEL_CACHE")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".cache" / "guitar-tab-generation" / "torch-models"


def _query_free_vram_mb(run_command: CommandRunner) -> tuple[int | None, int | None, str | None]:
    code, stdout, stderr = run_command([
        "nvidia-smi",
        "--query-gpu=memory.free,memory.total",
        "--format=csv,noheader,nounits",
    ])
    if code != 0:
        return None, None, stderr or "nvidia-smi unavailable"
    first = stdout.splitlines()[0] if stdout.splitlines() else ""
    parts = [part.strip() for part in first.split(",")]
    if len(parts) < 2:
        return None, None, "unable to parse nvidia-smi memory output"
    try:
        return int(parts[0]), int(parts[1]), None
    except ValueError:
        return None, None, "unable to parse nvidia-smi memory values"


def build_demucs_runtime_gate(
    *,
    env: Mapping[str, str] | None = None,
    check_runtime: bool | None = None,
    allow_gpu: bool | None = None,
    min_free_vram_mb: int | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
    command_exists: CommandExists = _default_command_exists,
    import_exists: ImportExists = _default_import_exists,
    run_command: CommandRunner = _default_runner,
) -> dict[str, Any]:
    """Build and optionally check the Demucs runtime install gate."""

    env_map = dict(os.environ if env is None else env)
    runtime_check_enabled = bool(check_runtime) or _truthy(env_map.get("DEMUCS_GATE_CHECK_RUNTIME"))
    gpu_enabled = bool(allow_gpu) or _truthy(env_map.get("GPU_TESTS_ENABLED"))
    raw_threshold = env_map.get("GPU_MIN_FREE_MB")
    threshold = (
        int(min_free_vram_mb)
        if min_free_vram_mb is not None
        else int(raw_threshold)
        if raw_threshold and raw_threshold.isdigit()
        else DEFAULT_MIN_FREE_VRAM_MB
    )
    cache_root = _default_cache_root(env_map)
    cache_dir = cache_root / "demucs-htdemucs"
    model_cache_dir = cache_dir / "models" / model_name

    free_vram_mb: int | None = None
    total_vram_mb: int | None = None
    gpu_probe_error: str | None = None
    if gpu_enabled:
        free_vram_mb, total_vram_mb, gpu_probe_error = _query_free_vram_mb(run_command)

    command = ["demucs", "--help"]
    step: dict[str, Any] = {
        "id": "demucs-htdemucs",
        "label": "Demucs / HTDemucs Stem Separation",
        "stage": "stem_separation",
        "dependency_group": "torch-ai",
        "install_hint": "uv sync --group torch-ai",
        "model_name": model_name,
        "cache_dir": str(cache_dir),
        "model_cache_dir": str(model_cache_dir),
        "download_enabled": False,
        "runtime_check_enabled": runtime_check_enabled,
        "gpu_sensitive": True,
        "gpu_enabled": gpu_enabled,
        "min_free_vram_mb": threshold,
        "free_vram_mb": free_vram_mb,
        "total_vram_mb": total_vram_mb,
        "command": command,
        "command_executed": False,
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "fallback_backend": None,
        "fallback_used": False,
        "reason": "",
    }

    command_available = command_exists("demucs")
    import_available = import_exists("demucs")
    step["command_available"] = command_available
    step["import_available"] = {"demucs": import_available}

    if runtime_check_enabled and (not command_available or not import_available):
        missing = []
        if not command_available:
            missing.append("demucs command")
        if not import_available:
            missing.append("demucs Python package")
        step.update({
            "status": "failed",
            "reason": (
                "Demucs optional runtime is not installed "
                f"({', '.join(missing)} missing). Install with `uv sync --group torch-ai`. "
                "No fallback stem will be generated."
            ),
        })
    elif gpu_enabled and gpu_probe_error:
        step.update({"status": "skipped", "reason": f"GPU probe unavailable: {gpu_probe_error}."})
    elif gpu_enabled and (free_vram_mb is None or free_vram_mb < threshold):
        step.update({"status": "skipped", "reason": f"Free VRAM is {free_vram_mb or 'unknown'} MB; requires at least {threshold} MB."})
    elif not runtime_check_enabled:
        step.update({"status": "planned", "reason": "預設只規劃 Demucs gate；pass --check-runtime to verify optional runtime."})
    else:
        code, stdout, stderr = run_command(command)
        step.update({
            "command_executed": True,
            "returncode": code,
            "stdout": stdout,
            "stderr": stderr,
            "status": "ready" if code == 0 else "failed",
            "reason": (
                "Demucs runtime is available; P24 does not run stem separation."
                if code == 0
                else "Demucs runtime command failed. No fallback stem will be generated."
            ),
        })

    steps = [step]
    summary = {status: sum(1 for item in steps if item["status"] == status) for status in ["planned", "ready", "skipped", "failed"]}
    return {
        "resource_profile": "local-rtx-4090-first",
        "runtime_check_enabled": runtime_check_enabled,
        "download_enabled": False,
        "gpu_enabled": gpu_enabled,
        "min_free_vram_mb": threshold,
        "cache_root": str(cache_root),
        "model_name": model_name,
        "fallback_policy": "no_silent_fallback",
        "transcribe_policy": "fixture remains default; Demucs is not used by transcribe in P24",
        "steps": steps,
        "summary": summary,
    }


def format_demucs_runtime_gate_markdown(gate: dict[str, Any]) -> str:
    """Format Demucs gate output as Traditional Chinese Markdown."""

    lines = [
        "# Demucs Runtime Gate",
        "",
        "- 安全預設：不下載、不使用 GPU、不執行 stem separation。",
        f"- Runtime check enabled: {gate['runtime_check_enabled']}",
        f"- GPU enabled: {gate['gpu_enabled']}",
        f"- VRAM guard: {gate['min_free_vram_mb']} MB",
        f"- Cache root: `{gate['cache_root']}`",
        f"- Model: `{gate['model_name']}`",
        f"- Fallback policy: `{gate['fallback_policy']}`",
        f"- Transcribe policy: {gate['transcribe_policy']}",
        "",
        "| Route | 狀態 | Runtime | Cache | Reason |",
        "|---|---|---|---|---|",
    ]
    for step in gate["steps"]:
        runtime = "yes" if step["command_available"] and step["import_available"]["demucs"] else "no"
        lines.append(
            f"| {step['label']} | {step['status']} | {runtime} | `{step['model_cache_dir']}` | {step['reason']} |"
        )
    lines.extend([
        "",
        "## Opt-in commands",
        "",
        "```bash",
        "uv sync --group torch-ai",
        "guitar-tab-generation demucs-gate --check-runtime --json",
        "GPU_TESTS_ENABLED=1 guitar-tab-generation demucs-gate --allow-gpu --min-free-vram-mb 12000 --json",
        "```",
        "",
    ])
    return "\n".join(lines)
