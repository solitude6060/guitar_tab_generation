from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


OWNED_SAMPLE_URL = "https://example.com/guitar-tab-generation/owned-sample.wav"


def test_cli_ingest_url_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["ingest-url", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "--i-own-rights" in output
    assert "--out" in output


def test_cli_ingest_url_no_rights_writes_policy_gate(tmp_path: Path) -> None:
    assert cli.main(["ingest-url", OWNED_SAMPLE_URL, "--out", str(tmp_path)]) == 2

    assert "requires --i-own-rights" in (tmp_path / "policy_gate.txt").read_text(encoding="utf-8")


def test_cli_ingest_url_owned_stub_writes_source_policy(tmp_path: Path) -> None:
    assert cli.main(["ingest-url", OWNED_SAMPLE_URL, "--i-own-rights", "--out", str(tmp_path)]) == 0

    payload = json.loads((tmp_path / "source_policy.json").read_text(encoding="utf-8"))
    assert payload["status"] == "allowed"
    assert payload["mode"] == "stub_only"
