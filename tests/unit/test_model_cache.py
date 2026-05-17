from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.model_cache import (
    ModelCacheError,
    build_cache_doctor,
    build_prune_plan,
    discover_model_caches,
    model_manifest,
)


def test_model_manifest_contains_required_runtime_ids() -> None:
    ids = {entry["id"] for entry in model_manifest()}

    assert {"basic-pitch", "demucs-htdemucs", "torchcrepe", "essentia", "ollama-local-llm"} <= ids


def test_discover_model_caches_reports_size_and_smoke_evidence(tmp_path: Path) -> None:
    cache_dir = tmp_path / "models" / "basic-pitch"
    cache_dir.mkdir(parents=True)
    (cache_dir / "weights.bin").write_bytes(b"abc")
    (cache_dir / "smoke.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")

    payload = discover_model_caches(tmp_path)
    basic_pitch = next(item for item in payload["models"] if item["id"] == "basic-pitch")

    assert basic_pitch["exists"] is True
    assert basic_pitch["size_bytes"] >= 3
    assert basic_pitch["smoke_evidence"]["status"] == "passed"


def test_cache_doctor_warns_when_cache_root_is_inside_repo(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    cache_root = repo_root / ".cache" / "models"

    payload = build_cache_doctor(cache_root, repo_root=repo_root)

    assert payload["status"] == "warning"
    assert any("inside the repository" in warning for warning in payload["warnings"])


def test_prune_dry_run_lists_unmanaged_cache_dirs_without_deleting(tmp_path: Path) -> None:
    known_parent = tmp_path / "models" / "basic-pitch"
    known_parent.mkdir(parents=True)
    (known_parent / "weights.bin").write_bytes(b"abc")
    orphan = tmp_path / "old-model"
    orphan.mkdir()
    (orphan / "weights.bin").write_bytes(b"abc")

    payload = build_prune_plan(tmp_path, dry_run=True)

    assert payload["dry_run"] is True
    assert [candidate["path"] for candidate in payload["candidates"]] == [str(orphan)]
    assert orphan.exists()


def test_prune_without_dry_run_raises(tmp_path: Path) -> None:
    with pytest.raises(ModelCacheError, match="--dry-run"):
        build_prune_plan(tmp_path, dry_run=False)
