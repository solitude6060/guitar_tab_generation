from __future__ import annotations

from pathlib import Path

import pytest

from guitar_tab_generation import cli


def test_cli_web_ui_help_lists_workspace_and_out(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["web-ui", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "workspace_dir" in output
    assert "--out" in output


def test_cli_web_ui_writes_artifact_browser(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "song"
    assert cli.main(["transcribe", "fixtures/simple_chords_30_90s.wav", "--backend", "fixture", "--out", str(artifact_dir)]) == 0

    assert cli.main(["web-ui", str(tmp_path)]) == 0

    html = (tmp_path / "web-ui.html").read_text(encoding="utf-8")
    assert "Guitar Tab Workspace" in html
    assert "song" in html
    assert "tab.md" in html
