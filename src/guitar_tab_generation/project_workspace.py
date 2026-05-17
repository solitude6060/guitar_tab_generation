"""Project workspace index for multi-song artifact collections."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class WorkspaceError(RuntimeError):
    """Raised when a workspace operation cannot be completed."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def workspace_path(workspace_dir: Path) -> Path:
    return workspace_dir / "workspace.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_workspace(workspace_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    workspace_path(workspace_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def init_workspace(workspace_dir: Path, *, name: str | None = None) -> dict[str, Any]:
    """Create or refresh a workspace index file."""

    existing = _read_json(workspace_path(workspace_dir))
    now = _now()
    payload = {
        "schema_version": 1,
        "project": {
            "name": name or existing.get("project", {}).get("name") or workspace_dir.name,
            "created_at": existing.get("project", {}).get("created_at") or now,
            "updated_at": now,
        },
        "songs": existing.get("songs", []) if isinstance(existing.get("songs"), list) else [],
    }
    return _write_workspace(workspace_dir, payload)


def read_workspace(workspace_dir: Path) -> dict[str, Any]:
    """Read workspace.json, creating a default workspace if needed."""

    payload = _read_json(workspace_path(workspace_dir))
    if not payload:
        return init_workspace(workspace_dir)
    if payload.get("schema_version") != 1 or not isinstance(payload.get("songs"), list):
        raise WorkspaceError("Invalid workspace.json schema; expected schema_version 1 with songs list.")
    return payload


def _artifact_metadata(workspace_dir: Path, artifact_dir: Path, *, song_id: str | None = None, title: str | None = None) -> dict[str, Any]:
    arrangement = _read_json(artifact_dir / "arrangement.json")
    quality = _read_json(artifact_dir / "quality_report.json")
    relative_artifact_dir = (
        artifact_dir.relative_to(workspace_dir).as_posix() if artifact_dir.is_relative_to(workspace_dir) else str(artifact_dir)
    )
    resolved_song_id = song_id or (relative_artifact_dir if relative_artifact_dir != "." else artifact_dir.name)
    now = _now()
    return {
        "song_id": resolved_song_id,
        "title": title or resolved_song_id,
        "artifact_dir": relative_artifact_dir,
        "source": arrangement.get("source", {}).get("input_uri", "unknown"),
        "quality_status": quality.get("status", "unknown"),
        "overall_confidence": arrangement.get("confidence", {}).get("overall", "unknown"),
        "updated_at": now,
        "history": [{"artifact_dir": relative_artifact_dir, "recorded_at": now}],
    }


def _merge_song(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    if existing is None:
        return incoming
    history = list(existing.get("history", []))
    history.extend(incoming["history"])
    return {**existing, **incoming, "history": history}


def add_artifact_to_workspace(
    workspace_dir: Path,
    artifact_dir: Path,
    *,
    song_id: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Add or update one artifact in workspace.json."""

    if not (artifact_dir / "arrangement.json").exists():
        raise WorkspaceError(f"Artifact directory is missing arrangement.json: {artifact_dir}")
    payload = read_workspace(workspace_dir)
    incoming = _artifact_metadata(workspace_dir, artifact_dir, song_id=song_id, title=title)
    songs_by_id = {song["song_id"]: song for song in payload["songs"] if isinstance(song, dict) and "song_id" in song}
    songs_by_id[incoming["song_id"]] = _merge_song(songs_by_id.get(incoming["song_id"]), incoming)
    payload["songs"] = [songs_by_id[key] for key in sorted(songs_by_id)]
    payload["project"]["updated_at"] = _now()
    return _write_workspace(workspace_dir, payload)


def update_workspace_index(workspace_dir: Path) -> dict[str, Any]:
    """Scan artifact dirs under a workspace and update workspace.json."""

    payload = read_workspace(workspace_dir)
    songs_by_id = {song["song_id"]: song for song in payload["songs"] if isinstance(song, dict) and "song_id" in song}
    candidates = [workspace_dir] + [path for path in workspace_dir.rglob("*") if path.is_dir()]
    for artifact_dir in candidates:
        if artifact_dir == workspace_dir and workspace_path(workspace_dir).exists():
            continue
        if not (artifact_dir / "arrangement.json").exists():
            continue
        incoming = _artifact_metadata(workspace_dir, artifact_dir)
        songs_by_id[incoming["song_id"]] = _merge_song(songs_by_id.get(incoming["song_id"]), incoming)
    payload["songs"] = [songs_by_id[key] for key in sorted(songs_by_id)]
    payload["project"]["updated_at"] = _now()
    return _write_workspace(workspace_dir, payload)
