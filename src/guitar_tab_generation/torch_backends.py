"""Torch-first backend roadmap and safe smoke gates.

This module deliberately does not import torch or any model package at module
import time. P19 establishes the boundary and verification gates only; concrete
Torch model dependencies must be added in the phase that calls them directly.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave
from typing import Any, Callable, Mapping, Sequence


CommandExists = Callable[[str], bool]
ImportExists = Callable[[str], bool]
CommandRunner = Callable[[list[str]], tuple[int, str, str]]
RuntimeLoader = Callable[[], Any]
TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class TorchBackendRoute:
    id: str
    label: str
    stage: str
    role: str
    framework: str
    python_imports: tuple[str, ...]
    command: str | None
    min_free_vram_mb: int
    cpu_allowed: bool
    gpu_sensitive: bool
    integration_phase: str
    dependency_group: str | None
    install_hint: str
    smoke_command_template: tuple[str, ...]
    notes: str
    local_first: bool = True
    auto_install: bool = False


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


def _write_smoke_wav(path: Path, *, sample_rate: int = 16_000, duration_seconds: float = 0.25) -> None:
    """Write a tiny C4 sine fixture using only the Python standard library."""

    frame_count = int(sample_rate * duration_seconds)
    frequency_hz = 261.63
    amplitude = 0.2
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for index in range(frame_count):
            value = int(amplitude * 32767 * math.sin(2 * math.pi * frequency_hz * index / sample_rate))
            wav_file.writeframes(struct.pack("<h", value))


def _prepare_torchcrepe_smoke_artifact(artifact_dir: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_smoke_wav(artifact_dir / "audio_normalized.wav")
    notes = [{"id": "smoke-c4", "start": 0.0, "end": 0.25, "pitch_midi": 60}]
    (artifact_dir / "notes.json").write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_torchcrepe_f0_runtime_smoke(
    cache_dir: Path,
    *,
    device: str = "cpu",
    runtime_loader: RuntimeLoader | None = None,
) -> dict[str, Any]:
    """Run the real torchcrepe F0 path on a tiny local fixture.

    The optional torchcrepe runtime is imported only through
    `write_f0_calibration()`, so default dev/CI can import this module without
    installing PyTorch or torchcrepe.
    """

    from .torchcrepe_f0 import load_torchcrepe_runtime, write_f0_calibration

    artifact_dir = cache_dir / "torchcrepe-f0-runtime-smoke"
    _prepare_torchcrepe_smoke_artifact(artifact_dir)
    output_path = write_f0_calibration(
        artifact_dir,
        device=device,
        model="tiny",
        runtime_loader=runtime_loader or load_torchcrepe_runtime,
    )
    return {
        "status": "ready",
        "device": device,
        "artifact_dir": str(artifact_dir),
        "f0_calibration_path": str(output_path),
    }


def selected_torch_backend_routes() -> list[dict[str, Any]]:
    """Return selected Torch-first candidate routes without probing runtime."""

    routes = [
        TorchBackendRoute(
            id="torchcrepe-f0",
            label="torchcrepe F0 Calibration",
            stage="pitch_calibration",
            role="Validate monophonic lead/riff pitch confidence after note extraction.",
            framework="pytorch",
            python_imports=("torch", "torchcrepe"),
            command=None,
            min_free_vram_mb=4_000,
            cpu_allowed=True,
            gpu_sensitive=True,
            integration_phase="P20 candidate",
            dependency_group="torch-ai",
            install_hint="uv sync --group torch-ai",
            smoke_command_template=(sys.executable, "-c", "import torch, torchcrepe; print('torchcrepe-ok')"),
            notes="Useful as a calibration lane, not a replacement for polyphonic note transcription.",
        ),
        TorchBackendRoute(
            id="demucs-htdemucs",
            label="Demucs / HTDemucs Stem Separation",
            stage="stem_separation",
            role="Separate guitar/bass/drums/vocals before downstream transcription.",
            framework="pytorch",
            python_imports=("torch", "demucs"),
            command="demucs",
            min_free_vram_mb=12_000,
            cpu_allowed=False,
            gpu_sensitive=True,
            integration_phase="P20/P21 candidate",
            dependency_group="torch-ai",
            install_hint="uv sync --group torch-ai",
            smoke_command_template=("demucs", "--help"),
            notes="GPU-sensitive; run sequentially on shared RTX 4090 hosts.",
        ),
        TorchBackendRoute(
            id="mt3-transcription",
            label="MT3 / YourMT3-style Transcription",
            stage="multi_instrument_transcription",
            role="Longer-term Torch-first route for multi-instrument note transcription research.",
            framework="pytorch",
            python_imports=("torch", "transformers"),
            command=None,
            min_free_vram_mb=16_000,
            cpu_allowed=False,
            gpu_sensitive=True,
            integration_phase="Research candidate after P20 smoke evidence",
            dependency_group=None,
            install_hint="not packaged yet; select a concrete checkpoint before adding dependencies",
            smoke_command_template=(sys.executable, "-c", "import torch, transformers; print('mt3-route-ok')"),
            notes="Roadmap candidate only; do not install until a concrete model checkpoint and adapter are selected.",
        ),
    ]
    return [asdict(route) for route in routes]


def collect_torch_backend_status(
    *,
    command_exists: CommandExists = _default_command_exists,
    import_exists: ImportExists = _default_import_exists,
) -> dict[str, Any]:
    """Collect Torch route readiness without importing heavy model packages."""

    route_statuses: list[dict[str, Any]] = []
    for route in selected_torch_backend_routes():
        import_status = {module: import_exists(module) for module in route["python_imports"]}
        command = route["command"]
        command_available = command_exists(command) if command else None
        runtime_available = bool(command_available) if command else all(import_status.values())
        route_statuses.append(
            {
                **route,
                "import_available": import_status,
                "command_available": command_available,
                "runtime_available": runtime_available,
                "status": "available" if runtime_available else "planned",
                "next_action": (
                    "eligible for future implementation phase; do not auto-install"
                    if runtime_available
                    else "keep as roadmap item until its phase directly calls the dependency"
                ),
            }
        )

    return {
        "resource_profile": "local-rtx-4090-first",
        "default_backend_policy": "fixture remains default; basic-pitch remains explicit",
        "basic_pitch_policy": "do not replace Basic Pitch in P19",
        "install_policy": "do not auto-install Torch packages until production code directly calls them",
        "routes": route_statuses,
    }


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


def build_torch_backend_smoke_gate(
    *,
    env: Mapping[str, str] | None = None,
    route_ids: Sequence[str] | None = None,
    run_smoke: bool | None = None,
    allow_gpu: bool | None = None,
    min_free_vram_mb: int | None = None,
    torch_device: str = "cpu",
    run_command: CommandRunner = _default_runner,
    torchcrepe_runtime_loader: RuntimeLoader | None = None,
) -> dict[str, Any]:
    """Build and optionally execute safe Torch route smoke gates."""

    env_map = dict(os.environ if env is None else env)
    routes = selected_torch_backend_routes()
    selected = set(route_ids or [route["id"] for route in routes])
    known = {route["id"] for route in routes}
    unknown = selected - known
    if unknown:
        raise ValueError(f"unknown torch backend route(s): {', '.join(sorted(unknown))}")

    smoke_enabled = bool(run_smoke) or _truthy(env_map.get("TORCH_SMOKE_RUN"))
    gpu_enabled = bool(allow_gpu) or _truthy(env_map.get("GPU_TESTS_ENABLED"))
    threshold_override = min_free_vram_mb
    if threshold_override is None:
        raw_threshold = env_map.get("GPU_MIN_FREE_MB")
        threshold_override = int(raw_threshold) if raw_threshold and raw_threshold.isdigit() else None
    cache_root = _default_cache_root(env_map)

    gpu_needed = any(
        route["gpu_sensitive"]
        and route["id"] in selected
        and not (route["id"] == "torchcrepe-f0" and torch_device == "cpu")
        for route in routes
    )
    free_vram_mb: int | None = None
    total_vram_mb: int | None = None
    gpu_probe_error: str | None = None
    if gpu_enabled and gpu_needed:
        free_vram_mb, total_vram_mb, gpu_probe_error = _query_free_vram_mb(run_command)

    steps: list[dict[str, Any]] = []
    for route in routes:
        if route["id"] not in selected:
            continue
        route_requires_gpu = route["gpu_sensitive"] and not (route["id"] == "torchcrepe-f0" and torch_device == "cpu")
        route_threshold = (
            int(threshold_override)
            if threshold_override is not None and route_requires_gpu
            else int(route["min_free_vram_mb"])
            if route_requires_gpu
            else 0
        )
        step: dict[str, Any] = {
            **route,
            "cache_dir": str(cache_root / route["id"]),
            "device": torch_device if route["id"] == "torchcrepe-f0" else None,
            "smoke_enabled": smoke_enabled,
            "gpu_enabled": gpu_enabled,
            "min_free_vram_mb": route_threshold,
            "free_vram_mb": free_vram_mb if route_requires_gpu else None,
            "total_vram_mb": total_vram_mb if route_requires_gpu else None,
            "command": (
                ["internal", "run_torchcrepe_f0_runtime_smoke", "--device", torch_device]
                if route["id"] == "torchcrepe-f0"
                else list(route["smoke_command_template"])
            ),
            "command_executed": False,
            "returncode": None,
            "stdout": "",
            "stderr": "",
            "reason": "",
        }
        if route["id"] == "torchcrepe-f0" and torch_device == "cuda" and not gpu_enabled:
            step.update({"status": "skipped", "reason": "torchcrepe CUDA smoke requires --allow-gpu or GPU_TESTS_ENABLED=1."})
        elif route_requires_gpu and not gpu_enabled and not route["cpu_allowed"]:
            step.update({"status": "skipped", "reason": "GPU-sensitive Torch smoke requires --allow-gpu or GPU_TESTS_ENABLED=1."})
        elif route_requires_gpu and gpu_enabled and gpu_probe_error:
            step.update({"status": "skipped", "reason": f"GPU probe unavailable: {gpu_probe_error}."})
        elif route_requires_gpu and gpu_enabled and (free_vram_mb is None or free_vram_mb < route_threshold):
            step.update({"status": "skipped", "reason": f"Free VRAM is {free_vram_mb or 'unknown'} MB; requires at least {route_threshold} MB."})
        elif not smoke_enabled:
            step.update({"status": "planned", "reason": "預設不執行 Torch smoke；pass --run or TORCH_SMOKE_RUN=1."})
        elif route["id"] == "torchcrepe-f0":
            try:
                result = run_torchcrepe_f0_runtime_smoke(
                    Path(step["cache_dir"]),
                    device=torch_device,
                    runtime_loader=torchcrepe_runtime_loader,
                )
            except Exception as exc:  # pragma: no cover - real runtime failures are environment dependent
                step.update({
                    "command_executed": True,
                    "returncode": 1,
                    "stderr": str(exc),
                    "status": "failed",
                    "reason": "torchcrepe runtime smoke failed",
                })
            else:
                step.update({
                    "command_executed": True,
                    "returncode": 0,
                    "stdout": json.dumps(result, ensure_ascii=False),
                    "status": "ready",
                    "reason": "torchcrepe runtime smoke wrote f0_calibration.json",
                    "artifact_dir": result["artifact_dir"],
                    "f0_calibration_path": result["f0_calibration_path"],
                })
        else:
            Path(step["cache_dir"]).mkdir(parents=True, exist_ok=True)
            code, stdout, stderr = run_command(step["command"])
            step.update({
                "command_executed": True,
                "returncode": code,
                "stdout": stdout,
                "stderr": stderr,
                "status": "ready" if code == 0 else "failed",
                "reason": "torch smoke command completed" if code == 0 else "torch smoke command failed",
            })
        steps.append(step)

    summary = {status: sum(1 for step in steps if step["status"] == status) for status in ["planned", "ready", "skipped", "failed"]}
    return {
        "resource_profile": "local-rtx-4090-first",
        "smoke_enabled": smoke_enabled,
        "gpu_enabled": gpu_enabled,
        "min_free_vram_mb": threshold_override if threshold_override is not None else "route-specific",
        "cache_root": str(cache_root),
        "default_backend_policy": "fixture remains default; basic-pitch remains explicit",
        "install_policy": "no Torch package is installed by this planner unless a later phase directly calls it",
        "steps": steps,
        "summary": summary,
    }


def format_torch_backend_status_markdown(status: dict[str, Any]) -> str:
    """Format Torch-first route status as Traditional Chinese Markdown."""

    lines = [
        "# Torch-first AI Backend Roadmap",
        "",
        "- 本機優先：Torch route 都以本機 RTX 4090 / CPU gate 為前提。",
        "- 不取代 Basic Pitch：P19 只建立 Torch-first 抽象與 gate，不改 `basic-pitch` 行為。",
        "- 不自動安裝：只有後續 phase 的 production code 直接呼叫時，才新增對應 dependency。",
        f"- Default backend policy: {status['default_backend_policy']}",
        "",
        "| Route | Stage | Runtime | Dependency group | 狀態 | GPU 門檻 | 下一步 |",
        "|---|---|---|---|---|---:|---|",
    ]
    for route in status["routes"]:
        imports = ", ".join(route["python_imports"])
        gpu = f"{route['min_free_vram_mb']} MB" if route["gpu_sensitive"] else "CPU"
        state = "可用" if route["runtime_available"] else "規劃中"
        dependency_group = route["dependency_group"] or "未封裝"
        lines.append(
            f"| {route['label']} | {route['stage']} | {imports} | {dependency_group} | {state} | {gpu} | {route['next_action']} |"
        )
    lines.append("")
    return "\n".join(lines)


def format_torch_smoke_gate_markdown(gate: dict[str, Any]) -> str:
    """Format Torch smoke gate as Traditional Chinese Markdown."""

    lines = [
        "# Torch Smoke Gate",
        "",
        "- 安全預設：不下載、不執行 GPU-sensitive smoke。",
        f"- Smoke enabled: {gate['smoke_enabled']}",
        f"- GPU enabled: {gate['gpu_enabled']}",
        f"- VRAM guard: {gate['min_free_vram_mb']} MB",
        f"- Cache root: `{gate['cache_root']}`",
        "",
        "| Route | 狀態 | GPU-sensitive | Reason |",
        "|---|---|---:|---|",
    ]
    for step in gate["steps"]:
        gpu = "yes" if step["gpu_sensitive"] else "no"
        lines.append(f"| {step['label']} | {step['status']} | {gpu} | {step['reason']} |")
    lines.append("")
    return "\n".join(lines)
