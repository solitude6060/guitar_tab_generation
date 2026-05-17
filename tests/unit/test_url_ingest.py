from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.url_ingest import UrlIngestError, ingest_url


OWNED_SAMPLE_URL = "https://example.com/guitar-tab-generation/owned-sample.wav"


def test_ingest_url_blocks_without_rights(tmp_path: Path) -> None:
    with pytest.raises(UrlIngestError, match="requires --i-own-rights"):
        ingest_url("https://example.com/guitar-tab-generation/owned-sample.wav", tmp_path, i_own_rights=False)


def test_ingest_url_blocks_youtube_even_with_rights(tmp_path: Path) -> None:
    with pytest.raises(UrlIngestError, match="YouTube"):
        ingest_url("https://www.youtube.com/watch?v=abc", tmp_path, i_own_rights=True)


def test_ingest_owned_sample_url_writes_source_policy(tmp_path: Path) -> None:
    policy_path = ingest_url(OWNED_SAMPLE_URL, tmp_path, i_own_rights=True)

    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    assert payload["status"] == "allowed"
    assert payload["mode"] == "stub_only"
    assert payload["url"] == OWNED_SAMPLE_URL
