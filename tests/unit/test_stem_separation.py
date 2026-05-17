from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.backends import BackendExecutionError
from guitar_tab_generation.demucs_runtime import build_demucs_runtime_gate
from guitar_tab_generation.stem_separation import write_stem_separation


class FakeDemucsRuntime:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict]:
        self.calls.append({
            "audio_path": audio_path,
            "stems_dir": stems_dir,
            "model_name": model_name,
            "device": device,
        })
        stems_dir.mkdir(parents=True, exist_ok=True)
        stems = []
        for name in ("drums", "bass", "other", "vocals"):
            path = stems_dir / f"{name}.wav"
            path.write_bytes(f"fake {name}".encode("utf-8"))
            stems.append({"name": name, "path": path})
        return stems


def _ready_gate(*, gpu_enabled: bool = False) -> dict:
    return {
        "runtime_check_enabled": True,
        "download_enabled": False,
        "gpu_enabled": gpu_enabled,
        "min_free_vram_mb": 12_000,
        "cache_root": "/tmp/cache",
        "model_name": "htdemucs",
        "fallback_policy": "no_silent_fallback",
        "steps": [{"id": "demucs-htdemucs", "status": "ready", "fallback_used": False}],
        "summary": {"planned": 0, "ready": 1, "skipped": 0, "failed": 0},
    }


def _write_artifact(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "audio_normalized.wav").write_bytes(b"fake wav")


def test_write_stem_separation_writes_manifest_and_stems(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)
    runtime = FakeDemucsRuntime()

    written = write_stem_separation(
        artifact_dir,
        runtime_loader=lambda: runtime,
        gate_builder=lambda **_kwargs: _ready_gate(),
    )

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert written.name == "stem_manifest.json"
    assert (artifact_dir / "stems").is_dir()
    assert payload["backend"] == "demucs-htdemucs"
    assert payload["model_name"] == "htdemucs"
    assert payload["device"] == "cpu"
    assert payload["source_audio"] == "audio_normalized.wav"
    assert payload["stems_dir"] == "stems"
    assert payload["fallback_used"] is False
    assert [stem["name"] for stem in payload["stems"]] == ["drums", "bass", "other", "vocals"]
    assert payload["stems"][1]["path"] == "stems/bass.wav"
    assert payload["stems"][1]["provenance"]["stage"] == "stem_separation"
    assert payload["gate"]["gpu_enabled"] is False
    assert runtime.calls[0]["device"] == "cpu"


def test_write_stem_separation_requires_audio_artifact(tmp_path: Path) -> None:
    with pytest.raises(BackendExecutionError, match="audio_normalized.wav"):
        write_stem_separation(tmp_path, runtime_loader=lambda: FakeDemucsRuntime())


def test_write_stem_separation_rejects_cuda_without_gpu_opt_in(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    with pytest.raises(BackendExecutionError, match="requires --allow-gpu"):
        write_stem_separation(
            artifact_dir,
            device="cuda",
            allow_gpu=False,
            runtime_loader=lambda: FakeDemucsRuntime(),
        )


def test_write_stem_separation_stops_when_gate_is_not_ready(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    def failed_gate(**_kwargs) -> dict:
        gate = _ready_gate()
        gate["summary"] = {"planned": 0, "ready": 0, "skipped": 0, "failed": 1}
        gate["steps"][0]["status"] = "failed"
        gate["steps"][0]["reason"] = "Demucs optional runtime is not installed"
        return gate

    with pytest.raises(BackendExecutionError, match="Demucs optional runtime is not installed"):
        write_stem_separation(
            artifact_dir,
            runtime_loader=lambda: FakeDemucsRuntime(),
            gate_builder=failed_gate,
        )


def test_write_stem_separation_cpu_device_does_not_pass_gpu_to_gate_from_env(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)
    captured_gate_args: dict = {}

    def gate(**kwargs) -> dict:
        captured_gate_args.update(kwargs)
        return _ready_gate(gpu_enabled=kwargs["allow_gpu"])

    write_stem_separation(
        artifact_dir,
        env={"GPU_TESTS_ENABLED": "1"},
        runtime_loader=lambda: FakeDemucsRuntime(),
        gate_builder=gate,
    )

    assert captured_gate_args["allow_gpu"] is False


def test_write_stem_separation_cpu_device_suppresses_gpu_env_for_real_gate(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)
    commands: list[list[str]] = []

    def command_exists(command: str) -> bool:
        return command == "demucs"

    def import_exists(module: str) -> bool:
        return module == "demucs"

    def run_command(command: list[str]) -> tuple[int, str, str]:
        commands.append(command)
        if command[:1] == ["demucs"]:
            return 0, "demucs help", ""
        return 1, "", "gpu probe should not run"

    def gate(**kwargs) -> dict:
        return build_demucs_runtime_gate(
            command_exists=command_exists,
            import_exists=import_exists,
            run_command=run_command,
            **kwargs,
        )

    write_stem_separation(
        artifact_dir,
        env={"GPU_TESTS_ENABLED": "1"},
        runtime_loader=lambda: FakeDemucsRuntime(),
        gate_builder=gate,
    )

    assert commands == [["demucs", "--help"]]


def test_write_stem_separation_rejects_runtime_stem_outside_stems_dir(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    class BadRuntime:
        def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict]:
            outside = artifact_dir / "outside.wav"
            outside.write_bytes(b"outside")
            return [{"name": "outside", "path": outside}]

    with pytest.raises(BackendExecutionError, match="inside stems/"):
        write_stem_separation(
            artifact_dir,
            runtime_loader=lambda: BadRuntime(),
            gate_builder=lambda **_kwargs: _ready_gate(),
        )


def test_write_stem_separation_rejects_missing_runtime_stem_file(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    class MissingRuntime:
        def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict]:
            return [{"name": "missing", "path": stems_dir / "missing.wav"}]

    with pytest.raises(BackendExecutionError, match="did not create stem file"):
        write_stem_separation(
            artifact_dir,
            runtime_loader=lambda: MissingRuntime(),
            gate_builder=lambda **_kwargs: _ready_gate(),
        )
