"""Artifact-first Demucs stem separation sidecar.

The default test path injects a fake runtime. The package runtime is loaded only
when `separate-stems` is executed, and GPU use remains opt-in.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any, Callable, Mapping, Protocol

from .backends import BackendExecutionError
from .demucs_runtime import DEFAULT_MODEL_NAME, build_demucs_runtime_gate


TRUE_VALUES = {"1", "true", "yes", "on"}


class DemucsRuntime(Protocol):
    def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict[str, Any]]:
        """Run separation and return stem descriptors with names and paths."""


RuntimeLoader = Callable[[], DemucsRuntime]
GateBuilder = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class DemucsCliRuntime:
    """Small adapter around the optional Demucs CLI."""

    command: str = "demucs"

    def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict[str, Any]]:
        with tempfile.TemporaryDirectory(prefix="guitar-tab-demucs-") as tmp:
            output_root = Path(tmp)
            command = [
                self.command,
                "-n",
                model_name,
                "-o",
                str(output_root),
                "-d",
                device,
                str(audio_path),
            ]
            try:
                completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=60 * 60)
            except (FileNotFoundError, subprocess.SubprocessError) as exc:
                raise BackendExecutionError(f"Demucs stem separation failed: {exc}") from exc
            if completed.returncode != 0:
                stderr = completed.stderr.strip() or completed.stdout.strip()
                raise BackendExecutionError(f"Demucs stem separation failed: {stderr}")

            demucs_output_dir = output_root / model_name / audio_path.stem
            if not demucs_output_dir.exists():
                raise BackendExecutionError(
                    f"Demucs completed but did not create expected output directory: {demucs_output_dir}"
                )

            stems_dir.mkdir(parents=True, exist_ok=True)
            stems: list[dict[str, Any]] = []
            for stem_path in sorted(demucs_output_dir.glob("*.wav")):
                target = stems_dir / stem_path.name
                shutil.copy2(stem_path, target)
                stems.append({"name": target.stem, "path": target})
            if not stems:
                raise BackendExecutionError("Demucs completed but produced no WAV stems.")
            return stems


def load_demucs_runtime() -> DemucsRuntime:
    """Load the optional runtime adapter without importing heavy packages."""

    return DemucsCliRuntime()


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in TRUE_VALUES


def _relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _first_blocking_reason(gate: dict[str, Any]) -> str:
    for step in gate.get("steps", []):
        if step.get("status") != "ready":
            return str(step.get("reason") or f"Demucs gate status is {step.get('status')}.")
    return "Demucs runtime gate did not report a ready route."


def _gate_is_ready(gate: dict[str, Any]) -> bool:
    return bool(gate.get("summary", {}).get("ready"))


def write_stem_separation(
    artifact_dir: Path,
    *,
    out: Path | None = None,
    device: str = "cpu",
    model_name: str = DEFAULT_MODEL_NAME,
    allow_gpu: bool = False,
    min_free_vram_mb: int | None = None,
    runtime_loader: RuntimeLoader | None = None,
    gate_builder: GateBuilder | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    """Write `stem_manifest.json` and `stems/` for an artifact directory."""

    env_map = dict(os.environ if env is None else env)
    artifact_dir = artifact_dir.resolve()
    audio_path = artifact_dir / "audio_normalized.wav"
    if not audio_path.exists():
        raise BackendExecutionError("separate-stems requires audio_normalized.wav in the artifact directory.")

    gpu_opted_in = allow_gpu or _truthy(env_map.get("GPU_TESTS_ENABLED"))
    gpu_allowed = device == "cuda" and gpu_opted_in
    if device == "cuda" and not gpu_opted_in:
        raise BackendExecutionError("separate-stems --device cuda requires --allow-gpu or GPU_TESTS_ENABLED=1.")
    gate_env = dict(env_map)
    if not gpu_allowed:
        gate_env["GPU_TESTS_ENABLED"] = "0"

    build_gate = gate_builder or build_demucs_runtime_gate
    gate = build_gate(
        env=gate_env,
        check_runtime=True,
        allow_gpu=gpu_allowed,
        min_free_vram_mb=min_free_vram_mb,
        model_name=model_name,
    )
    if not _gate_is_ready(gate):
        raise BackendExecutionError(_first_blocking_reason(gate))

    stems_dir = artifact_dir / "stems"
    runtime = (runtime_loader or load_demucs_runtime)()
    try:
        runtime_stems = runtime.separate(audio_path, stems_dir, model_name=model_name, device=device)
    except BackendExecutionError:
        raise
    except Exception as exc:  # pragma: no cover - runtime-specific failures are environment dependent
        raise BackendExecutionError(f"Demucs stem separation failed: {exc}") from exc

    stems: list[dict[str, Any]] = []
    for item in runtime_stems:
        stem_path = Path(item["path"]).resolve()
        if not stem_path.exists():
            raise BackendExecutionError(f"Demucs runtime did not create stem file: {stem_path}")
        try:
            stem_path.relative_to(stems_dir.resolve())
        except ValueError as exc:
            raise BackendExecutionError(f"Demucs runtime must return stem files inside stems/: {stem_path}") from exc
        stems.append({
            "name": str(item["name"]),
            "path": _relative_posix(stem_path, artifact_dir),
            "model": model_name,
            "confidence": item.get("confidence"),
            "provenance": {
                "stage": "stem_separation",
                "backend": "demucs-htdemucs",
                "model": model_name,
                "device": device,
                "source": "audio_normalized.wav",
            },
        })

    manifest = {
        "backend": "demucs-htdemucs",
        "model_name": model_name,
        "device": device,
        "source_audio": "audio_normalized.wav",
        "stems_dir": "stems",
        "fallback_used": False,
        "gate": gate,
        "stems": stems,
        "warnings": [
            "Demucs stem confidence is not calibrated; downstream stages must treat stems as sidecar evidence."
        ],
    }
    output_path = out or artifact_dir / "stem_manifest.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output_path
