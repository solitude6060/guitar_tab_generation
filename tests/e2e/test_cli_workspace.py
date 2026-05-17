from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


def _write_artifact(path: Path) -> None:
    path.mkdir(parents=True)
    (path / "arrangement.json").write_text(
        json.dumps({"source": {"input_uri": "song.wav"}, "confidence": {"overall": 0.7}}),
        encoding="utf-8",
    )
    (path / "quality_report.json").write_text(json.dumps({"status": "warning"}), encoding="utf-8")


def test_cli_workspace_help_lists_subcommands(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["workspace", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    for command in ["init", "index", "add-artifact"]:
        assert command in output


def test_cli_workspace_init_index_and_add_artifact(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    artifact = tmp_path / "song-a"
    _write_artifact(artifact)

    assert cli.main(["workspace", "init", str(tmp_path), "--name", "Demo", "--json"]) == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["project"]["name"] == "Demo"

    assert cli.main(["workspace", "index", str(tmp_path), "--json"]) == 0
    index_payload = json.loads(capsys.readouterr().out)
    assert index_payload["songs"][0]["song_id"] == "song-a"

    assert (
        cli.main(
            [
                "workspace",
                "add-artifact",
                str(tmp_path),
                str(artifact),
                "--song-id",
                "lead",
                "--title",
                "Lead",
                "--json",
            ]
        )
        == 0
    )
    add_payload = json.loads(capsys.readouterr().out)
    assert any(song["song_id"] == "lead" and song["title"] == "Lead" for song in add_payload["songs"])
