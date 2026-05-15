"""Safe model download and integration smoke planning.

The harness is intentionally conservative: default CLI usage only reports the
work that would be done. Downloads and GPU-sensitive checks require explicit
opt-in so a shared RTX 4090 is not stolen from another local project.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import os
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence

from .ai_backends import selected_backend_specs


CommandRunner = Callable[[list[str]], tuple[int, str, str]]
DEFAULT_MIN_FREE_VRAM_MB = 12_000
TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ModelSmokeSpec:
    id: str
    label: str
    purpose: str
    cache_subdir: str
    download_command_template: tuple[str, ...]
    gpu_sensitive: bool
    notes: str


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
    return Path.home() / ".cache" / "guitar-tab-generation" / "models"


def _selected_smoke_specs(cache_root: Path) -> list[ModelSmokeSpec]:
    backend_by_id = {backend["id"]: backend for backend in selected_backend_specs()}

    def purpose(backend_id: str) -> str:
        return str(backend_by_id[backend_id]["product_role"])

    return [
        ModelSmokeSpec(
            id="basic-pitch",
            label="Basic Pitch",
            purpose=purpose("basic-pitch"),
            cache_subdir="basic-pitch",
            download_command_template=(
                sys.executable,
                "-m",
                "pip",
                "download",
                "basic-pitch",
                "--dest",
                str(cache_root / "basic-pitch"),
            ),
            gpu_sensitive=False,
            notes="Package download only; inference remains a later opt-in backend phase.",
        ),
        ModelSmokeSpec(
            id="demucs",
            label="Demucs / HTDemucs",
            purpose=purpose("demucs"),
            cache_subdir="demucs",
            download_command_template=(
                sys.executable,
                "-m",
                "pip",
                "download",
                "demucs",
                "--dest",
                str(cache_root / "demucs"),
            ),
            gpu_sensitive=True,
            notes="Treat as GPU-sensitive because the next integration smoke is stem separation.",
        ),
        ModelSmokeSpec(
            id="torchcrepe",
            label="CREPE / torchcrepe",
            purpose=purpose("torchcrepe"),
            cache_subdir="torchcrepe",
            download_command_template=(
                sys.executable,
                "-m",
                "pip",
                "download",
                "torchcrepe",
                "--dest",
                str(cache_root / "torchcrepe"),
            ),
            gpu_sensitive=True,
            notes="Pitch calibration can run on GPU; keep opt-in on shared hosts.",
        ),
        ModelSmokeSpec(
            id="essentia",
            label="Essentia / feature route",
            purpose=purpose("essentia"),
            cache_subdir="essentia",
            download_command_template=(
                sys.executable,
                "-m",
                "pip",
                "download",
                "essentia",
                "--dest",
                str(cache_root / "essentia"),
            ),
            gpu_sensitive=False,
            notes="CPU-first feature extraction route.",
        ),
        ModelSmokeSpec(
            id="local-llm",
            label="Local LLM via Ollama",
            purpose=purpose("local-llm"),
            cache_subdir="ollama",
            download_command_template=("ollama", "pull", "qwen2.5:7b-instruct-q4_K_M"),
            gpu_sensitive=True,
            notes="Tutorial text only; never a source of truth for notes or chords.",
        ),
    ]


def available_backend_ids() -> list[str]:
    """Return valid backend ids for the model smoke CLI."""

    return [spec.id for spec in _selected_smoke_specs(Path("/tmp/guitar-tab-generation-models"))]


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


def build_model_smoke_plan(
    *,
    env: Mapping[str, str] | None = None,
    backends: Sequence[str] | None = None,
    download: bool | None = None,
    allow_gpu: bool | None = None,
    min_free_vram_mb: int | None = None,
    run_command: CommandRunner = _default_runner,
) -> dict[str, Any]:
    """Build and optionally execute safe model preparation smoke steps."""

    env_map = dict(os.environ if env is None else env)
    cache_root = _default_cache_root(env_map)
    specs = _selected_smoke_specs(cache_root)
    selected = set(backends or [spec.id for spec in specs])
    unknown = selected - {spec.id for spec in specs}
    if unknown:
        raise ValueError(f"unknown model smoke backend(s): {', '.join(sorted(unknown))}")

    download_enabled = bool(download) or _truthy(env_map.get("MODEL_SMOKE_DOWNLOAD"))
    gpu_enabled = bool(allow_gpu) or _truthy(env_map.get("GPU_TESTS_ENABLED"))
    threshold = min_free_vram_mb
    if threshold is None:
        raw_threshold = env_map.get("GPU_MIN_FREE_MB")
        threshold = int(raw_threshold) if raw_threshold and raw_threshold.isdigit() else DEFAULT_MIN_FREE_VRAM_MB

    free_vram_mb: int | None = None
    total_vram_mb: int | None = None
    gpu_probe_error: str | None = None
    if gpu_enabled and any(spec.gpu_sensitive and spec.id in selected for spec in specs):
        free_vram_mb, total_vram_mb, gpu_probe_error = _query_free_vram_mb(run_command)

    steps: list[dict[str, Any]] = []
    for spec in specs:
        if spec.id not in selected:
            continue
        command = list(spec.download_command_template)
        step: dict[str, Any] = {
            **asdict(spec),
            "cache_dir": str(cache_root / spec.cache_subdir),
            "download_command": command,
            "download_enabled": download_enabled,
            "gpu_enabled": gpu_enabled,
            "min_free_vram_mb": threshold,
            "free_vram_mb": free_vram_mb if spec.gpu_sensitive else None,
            "total_vram_mb": total_vram_mb if spec.gpu_sensitive else None,
            "command_executed": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason": "",
        }

        if spec.gpu_sensitive and not gpu_enabled:
            step.update({
                "status": "skipped",
                "reason": "GPU-sensitive smoke requires --allow-gpu or GPU_TESTS_ENABLED=1.",
            })
        elif spec.gpu_sensitive and gpu_probe_error:
            step.update({"status": "skipped", "reason": f"GPU probe unavailable: {gpu_probe_error}."})
        elif spec.gpu_sensitive and (free_vram_mb is None or free_vram_mb < threshold):
            step.update({
                "status": "skipped",
                "reason": f"Free VRAM is {free_vram_mb or 'unknown'} MB; requires at least {threshold} MB.",
            })
        elif not download_enabled:
            step.update({"status": "planned", "reason": "預設不下載；pass --download or MODEL_SMOKE_DOWNLOAD=1."})
        else:
            Path(step["cache_dir"]).mkdir(parents=True, exist_ok=True)
            code, stdout, stderr = run_command(command)
            step.update({
                "command_executed": True,
                "returncode": code,
                "stdout": stdout,
                "stderr": stderr,
                "status": "ready" if code == 0 else "failed",
                "reason": "download command completed" if code == 0 else "download command failed",
            })
        steps.append(step)

    summary = {status: sum(1 for step in steps if step["status"] == status) for status in ["planned", "ready", "skipped", "failed"]}
    return {
        "resource_profile": "local-rtx-4090-first",
        "download_enabled": download_enabled,
        "gpu_enabled": gpu_enabled,
        "min_free_vram_mb": threshold,
        "cache_root": str(cache_root),
        "cloud_policy": "MiniMax remains backup only; model smoke never uses it as transcription truth.",
        "steps": steps,
        "summary": summary,
    }


def format_model_smoke_markdown(plan: dict[str, Any]) -> str:
    """Format model smoke plan as Traditional Chinese Markdown."""

    lines = [
        "# Model Smoke Plan",
        "",
        "- 安全預設：預設不下載、不使用 GPU。",
        f"- Download enabled: {plan['download_enabled']}",
        f"- GPU enabled: {plan['gpu_enabled']}（GPU backend 需要 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`）",
        f"- VRAM guard: 至少 {plan['min_free_vram_mb']} MB free VRAM，否則 skip。",
        f"- Cache root: `{plan['cache_root']}`",
        "- MiniMax：仍只作備援/創作輔助，不作 transcription truth source。",
        "",
        "| Backend | 狀態 | GPU | Cache | Reason |",
        "|---|---|---:|---|---|",
    ]
    for step in plan["steps"]:
        gpu = "yes" if step["gpu_sensitive"] else "no"
        lines.append(
            f"| {step['label']} | {step['status']} | {gpu} | `{step['cache_dir']}` | {step['reason']} |"
        )
    lines.extend([
        "",
        "## Opt-in commands",
        "",
        "```bash",
        "MODEL_SMOKE_DOWNLOAD=1 guitar-tab-generation model-smoke --backend basic-pitch",
        "GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 guitar-tab-generation model-smoke --backend demucs --download --allow-gpu",
        "```",
        "",
    ])
    return "\n".join(lines)
