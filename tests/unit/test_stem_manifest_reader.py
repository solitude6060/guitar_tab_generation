from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.backends import BackendExecutionError
from guitar_tab_generation.stem_notes import resolve_stem_audio


def _write_manifest(artifact_dir: Path, stems: list[dict]) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / "stem_manifest.json").write_text(
        json.dumps({"backend": "demucs-htdemucs", "stems": stems}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_resolve_stem_audio_reads_manifest_stem_path(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    stem_path = artifact_dir / "stems" / "guitar.wav"
    stem_path.parent.mkdir(parents=True)
    stem_path.write_bytes(b"fake guitar")
    _write_manifest(artifact_dir, [{"name": "guitar", "path": "stems/guitar.wav"}])

    resolved = resolve_stem_audio(artifact_dir, "guitar")

    assert resolved.name == "guitar"
    assert resolved.audio_path == stem_path.resolve()
    assert resolved.manifest_path == artifact_dir / "stem_manifest.json"
    assert resolved.available_stems == ["guitar"]


def test_resolve_stem_audio_rejects_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(BackendExecutionError, match="Run separate-stems first"):
        resolve_stem_audio(tmp_path, "guitar")


def test_resolve_stem_audio_rejects_unknown_stem_with_available_names(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    stem_path = artifact_dir / "stems" / "bass.wav"
    stem_path.parent.mkdir(parents=True)
    stem_path.write_bytes(b"fake bass")
    _write_manifest(artifact_dir, [{"name": "bass", "path": "stems/bass.wav"}])

    with pytest.raises(BackendExecutionError, match="Available stems: bass"):
        resolve_stem_audio(artifact_dir, "guitar")


def test_resolve_stem_audio_rejects_missing_stem_file(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_manifest(artifact_dir, [{"name": "guitar", "path": "stems/guitar.wav"}])

    with pytest.raises(BackendExecutionError, match="does not exist"):
        resolve_stem_audio(artifact_dir, "guitar")


def test_resolve_stem_audio_rejects_path_outside_artifact_dir(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"outside")
    _write_manifest(artifact_dir, [{"name": "guitar", "path": "../outside.wav"}])

    with pytest.raises(BackendExecutionError, match="inside the artifact directory"):
        resolve_stem_audio(artifact_dir, "guitar")


def test_resolve_stem_audio_rejects_unsafe_stem_name(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifact"
    stem_path = artifact_dir / "stems" / "guitar.wav"
    stem_path.parent.mkdir(parents=True)
    stem_path.write_bytes(b"fake guitar")
    _write_manifest(artifact_dir, [{"name": "../leak", "path": "stems/guitar.wav"}])

    with pytest.raises(BackendExecutionError, match="unsafe stem name"):
        resolve_stem_audio(artifact_dir, "../leak")
