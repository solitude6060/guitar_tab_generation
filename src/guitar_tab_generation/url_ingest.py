"""Legal URL ingestion policy gate."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlparse


OWNED_SAMPLE_URL = "https://example.com/guitar-tab-generation/owned-sample.wav"


class UrlIngestError(RuntimeError):
    """Raised when URL ingestion is blocked by policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_youtube_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"youtube.com", "www.youtube.com", "youtu.be", "music.youtube.com"}


def ingest_url(url: str, artifact_dir: Path, *, i_own_rights: bool = False) -> Path:
    """Apply URL policy and write source_policy.json for the owned sample stub."""

    artifact_dir.mkdir(parents=True, exist_ok=True)
    if not i_own_rights:
        raise UrlIngestError("URL ingestion requires --i-own-rights; arbitrary URL download is disabled.")
    if _is_youtube_url(url):
        raise UrlIngestError("YouTube URL ingestion is blocked in v1.0; provide a legal local audio file instead.")
    if url != OWNED_SAMPLE_URL:
        raise UrlIngestError("Unsupported URL for v1.0 stub ingestion; arbitrary URL download is disabled.")

    policy = {
        "schema_version": 1,
        "status": "allowed",
        "mode": "stub_only",
        "url": url,
        "i_own_rights": True,
        "download_performed": False,
        "created_at": _now(),
        "warnings": ["No network download was performed; this is a policy stub for tests."],
    }
    path = artifact_dir / "source_policy.json"
    path.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
