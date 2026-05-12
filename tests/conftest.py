from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def load_json():
    def _load(path: Path):
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    return _load
