"""Stem-aware note transcription sidecar helpers."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from .backends import BackendExecutionError
from .basic_pitch_backend import BasicPitchAnalysisBackend


@dataclass(frozen=True)
class ResolvedStemAudio:
    name: str
    audio_path: Path
    relative_path: str
    manifest_path: Path
    available_stems: list[str]


SAFE_STEM_NAME = re.compile(r"[A-Za-z0-9._-]+")


def _validate_stem_name(stem_name: str) -> None:
    if stem_name in {".", ".."} or not SAFE_STEM_NAME.fullmatch(stem_name):
        raise BackendExecutionError(
            f"unsafe stem name {stem_name!r}; use only letters, numbers, dots, dashes, or underscores."
        )


def _load_manifest(manifest_path: Path) -> dict[str, Any]:
    if not manifest_path.exists():
        raise BackendExecutionError(
            "stem_manifest.json is missing. Run separate-stems first, then retry transcribe-stem."
        )
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BackendExecutionError(f"stem_manifest.json is not valid JSON: {exc}") from exc


def resolve_stem_audio(artifact_dir: Path, stem_name: str) -> ResolvedStemAudio:
    """Resolve a named stem from P25 stem_manifest.json without falling back to mix."""

    _validate_stem_name(stem_name)
    artifact_root = artifact_dir.resolve()
    manifest_path = artifact_root / "stem_manifest.json"
    manifest = _load_manifest(manifest_path)
    stems = manifest.get("stems")
    if not isinstance(stems, list):
        raise BackendExecutionError("stem_manifest.json must contain a stems list.")

    available = [str(stem.get("name")) for stem in stems if isinstance(stem, dict) and stem.get("name")]
    selected = next((stem for stem in stems if isinstance(stem, dict) and stem.get("name") == stem_name), None)
    if selected is None:
        suffix = f" Available stems: {', '.join(available)}." if available else " No stems are available."
        raise BackendExecutionError(f"Stem {stem_name!r} was not found in stem_manifest.json.{suffix}")

    raw_path = selected.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise BackendExecutionError(f"Stem {stem_name!r} has no usable path in stem_manifest.json.")
    audio_path = (artifact_root / raw_path).resolve()
    try:
        audio_path.relative_to(artifact_root)
    except ValueError as exc:
        raise BackendExecutionError("Stem audio path must stay inside the artifact directory.") from exc
    if not audio_path.exists():
        raise BackendExecutionError(f"Stem audio path does not exist: {raw_path}")

    return ResolvedStemAudio(
        name=stem_name,
        audio_path=audio_path,
        relative_path=raw_path,
        manifest_path=manifest_path,
        available_stems=available,
    )


def write_basic_pitch_stem_notes(artifact_dir: Path, *, stem_name: str, backend: str = "basic-pitch") -> Path:
    """Transcribe one resolved stem with Basic Pitch and write sidecar notes."""

    if backend != "basic-pitch":
        raise BackendExecutionError("transcribe-stem currently supports only --backend basic-pitch.")

    resolved = resolve_stem_audio(artifact_dir, stem_name)
    analysis_backend = BasicPitchAnalysisBackend(audio_path=resolved.audio_path, stem_name=resolved.name)
    notes, warnings = analysis_backend.transcribe_notes(0.0)

    output_dir = artifact_dir / "stem_notes"
    output_dir.mkdir(parents=True, exist_ok=True)
    notes_path = output_dir / f"{resolved.name}.notes.json"
    metadata_path = output_dir / f"{resolved.name}.metadata.json"
    output_root = output_dir.resolve()
    for path in (notes_path.resolve(), metadata_path.resolve()):
        try:
            path.relative_to(output_root)
        except ValueError as exc:
            raise BackendExecutionError("Stem note sidecar paths must stay inside stem_notes/.") from exc
    payload = {
        "schema": "guitar-tab-generation.stem-notes.v1",
        "backend": backend,
        "stem": resolved.name,
        "source": {
            "stem_manifest": resolved.manifest_path.name,
            "stem_path": resolved.relative_path,
        },
        "notes": notes,
        "warnings": warnings,
    }
    metadata = {
        "schema": "guitar-tab-generation.stem-notes-metadata.v1",
        "backend": backend,
        "stem": resolved.name,
        "source": {
            "stem_manifest": resolved.manifest_path.name,
            "stem_path": resolved.relative_path,
        },
        "provenance": {
            "stage": "stem_pitch_transcription",
            "backend": backend,
            "stem": resolved.name,
            "stem_manifest": resolved.manifest_path.name,
            "runtime": "basic_pitch_python_api",
        },
        "warnings": [
            "Stem note events are sidecar evidence and are not automatically merged into arrangement.json."
        ],
    }
    notes_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return notes_path
