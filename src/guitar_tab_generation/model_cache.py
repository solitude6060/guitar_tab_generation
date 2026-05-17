"""Read-only model cache discovery and dry-run prune planning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelCacheError(RuntimeError):
    """Raised when a model cache operation is unsafe or invalid."""


def default_cache_root() -> Path:
    """Return the default base cache root for user-managed model artifacts."""

    return Path.home() / ".cache" / "guitar-tab-generation"


def model_manifest() -> list[dict[str, Any]]:
    """Return the static v1 model cache manifest."""

    return [
        {
            "id": "basic-pitch",
            "label": "Basic Pitch",
            "runtime": "basic-pitch",
            "cache_subdir": "models/basic-pitch",
            "optional": True,
        },
        {
            "id": "demucs-htdemucs",
            "label": "Demucs htdemucs",
            "runtime": "demucs",
            "cache_subdir": "torch-models/demucs-htdemucs",
            "optional": True,
        },
        {
            "id": "torchcrepe",
            "label": "torchcrepe F0",
            "runtime": "torchcrepe",
            "cache_subdir": "torch-models/torchcrepe",
            "optional": True,
        },
        {
            "id": "essentia",
            "label": "Essentia",
            "runtime": "essentia",
            "cache_subdir": "models/essentia",
            "optional": True,
        },
        {
            "id": "ollama-local-llm",
            "label": "Ollama local LLM",
            "runtime": "ollama",
            "cache_subdir": "models/ollama",
            "optional": True,
        },
    ]


def _directory_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def _read_smoke_evidence(path: Path) -> dict[str, Any] | None:
    evidence_path = path / "smoke.json"
    if not evidence_path.exists():
        return None
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"status": "invalid", "error": str(exc)}
    return payload if isinstance(payload, dict) else {"status": "invalid", "error": "smoke.json must be an object"}


def discover_model_caches(cache_root: Path | None = None) -> dict[str, Any]:
    """Discover known model cache directories without downloading anything."""

    root = cache_root or default_cache_root()
    models = []
    for entry in model_manifest():
        cache_dir = root / entry["cache_subdir"]
        models.append(
            {
                **entry,
                "cache_dir": str(cache_dir),
                "exists": cache_dir.exists(),
                "size_bytes": _directory_size_bytes(cache_dir),
                "smoke_evidence": _read_smoke_evidence(cache_dir),
            }
        )
    return {
        "cache_root": str(root),
        "manifest_version": 1,
        "models": models,
        "total_size_bytes": sum(model["size_bytes"] for model in models),
    }


def build_cache_doctor(cache_root: Path | None = None, *, repo_root: Path | None = None) -> dict[str, Any]:
    """Build a cache health report."""

    root = cache_root or default_cache_root()
    resolved_root = root.resolve()
    warnings: list[str] = []
    if repo_root is not None:
        try:
            resolved_root.relative_to(repo_root.resolve())
        except ValueError:
            pass
        else:
            warnings.append("Cache root is inside the repository; prefer an external user cache directory.")
    discovery = discover_model_caches(root)
    missing = [model["id"] for model in discovery["models"] if not model["exists"]]
    return {
        "status": "warning" if warnings else "passed",
        "cache_root": str(root),
        "manifest_version": discovery["manifest_version"],
        "model_count": len(discovery["models"]),
        "missing_model_ids": missing,
        "warnings": warnings,
    }


def build_prune_plan(cache_root: Path | None = None, *, dry_run: bool) -> dict[str, Any]:
    """Return unmanaged cache directories that would be pruned."""

    if not dry_run:
        raise ModelCacheError("models prune is dry-run only in P37; pass --dry-run.")
    root = cache_root or default_cache_root()
    known_subdirs = {entry["cache_subdir"] for entry in model_manifest()}
    known_top_dirs = {Path(subdir).parts[0] for subdir in known_subdirs}
    candidates = []
    if root.exists():
        for child in sorted(root.iterdir(), key=lambda item: item.name):
            if child.is_dir() and child.name in known_top_dirs:
                continue
            if child.is_dir() and child.name not in known_subdirs:
                candidates.append(
                    {
                        "path": str(child),
                        "reason": "unmanaged cache directory",
                        "size_bytes": _directory_size_bytes(child),
                    }
                )
            elif child.is_dir() and _directory_size_bytes(child) == 0:
                candidates.append(
                    {
                        "path": str(child),
                        "reason": "empty known cache directory",
                        "size_bytes": 0,
                    }
                )
    return {
        "dry_run": True,
        "cache_root": str(root),
        "candidates": candidates,
        "total_reclaimable_bytes": sum(candidate["size_bytes"] for candidate in candidates),
    }
