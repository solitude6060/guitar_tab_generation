from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


class FakeDemucsRuntime:
    def separate(self, audio_path: Path, stems_dir: Path, *, model_name: str, device: str) -> list[dict]:
        stems_dir.mkdir(parents=True, exist_ok=True)
        stem_path = stems_dir / "guitar.wav"
        stem_path.write_bytes(b"fake guitar stem")
        return [{"name": "guitar", "path": stem_path}]


def _write_artifact(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "audio_normalized.wav").write_bytes(b"fake wav")


def _ready_gate(**_kwargs) -> dict:
    return {
        "runtime_check_enabled": True,
        "download_enabled": False,
        "gpu_enabled": False,
        "min_free_vram_mb": 12_000,
        "cache_root": "/tmp/cache",
        "model_name": "htdemucs",
        "fallback_policy": "no_silent_fallback",
        "steps": [{"id": "demucs-htdemucs", "status": "ready", "fallback_used": False}],
        "summary": {"planned": 0, "ready": 1, "skipped": 0, "failed": 0},
    }


def test_cli_separate_stems_help_exposes_runtime_and_gpu_options(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["separate-stems", "--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "artifact_dir" in output
    assert "--device" in output
    assert "--allow-gpu" in output
    assert "--min-free-vram-mb" in output


def test_cli_separate_stems_writes_artifacts_with_stub_runtime(monkeypatch, tmp_path: Path, capsys) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)
    monkeypatch.setattr("guitar_tab_generation.stem_separation.load_demucs_runtime", lambda: FakeDemucsRuntime())
    monkeypatch.setattr("guitar_tab_generation.stem_separation.build_demucs_runtime_gate", _ready_gate)

    assert cli.main(["separate-stems", str(artifact_dir)]) == 0

    assert "stem_manifest.json" in capsys.readouterr().out
    payload = json.loads((artifact_dir / "stem_manifest.json").read_text(encoding="utf-8"))
    assert payload["backend"] == "demucs-htdemucs"
    assert payload["stems"][0]["name"] == "guitar"
    assert (artifact_dir / "stems" / "guitar.wav").exists()


def test_cli_transcribe_default_still_has_no_demucs_stem_default(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["transcribe", "--help"])

    assert exc.value.code == 0
    output = capsys.readouterr().out
    assert "Default is fixture" in output
    assert "--stem" not in output
    assert "demucs" not in output.lower()
