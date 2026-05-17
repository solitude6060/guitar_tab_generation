from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation.web_ui import discover_artifacts, render_web_ui_html, write_web_ui


def _write_artifact(path: Path) -> None:
    path.mkdir(parents=True)
    (path / "arrangement.json").write_text(
        json.dumps({"source": {"input_uri": "fixtures/<riff>.wav"}, "confidence": {"overall": 0.8}}),
        encoding="utf-8",
    )
    (path / "quality_report.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")


def test_discover_artifacts_finds_nested_artifact_dirs(tmp_path: Path) -> None:
    _write_artifact(tmp_path / "song-a")

    artifacts = discover_artifacts(tmp_path)

    assert artifacts[0]["relative_path"] == "song-a"
    assert artifacts[0]["quality_status"] == "passed"


def test_render_web_ui_html_escapes_and_links_artifacts(tmp_path: Path) -> None:
    _write_artifact(tmp_path / "song-a")

    html = render_web_ui_html(tmp_path)

    assert "Guitar Tab Workspace" in html
    assert "fixtures/&lt;riff&gt;.wav" in html
    assert "song-a/tab.md" in html


def test_write_web_ui_defaults_to_workspace(tmp_path: Path) -> None:
    written = write_web_ui(tmp_path)

    assert written == tmp_path / "web-ui.html"
    assert "No artifact directories found" in written.read_text(encoding="utf-8")
