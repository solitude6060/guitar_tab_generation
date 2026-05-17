from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation.project_workspace import add_artifact_to_workspace, init_workspace, update_workspace_index
from guitar_tab_generation.web_ui import render_web_ui_html


def _write_artifact(path: Path, source: str = "song.wav", confidence: float = 0.8) -> None:
    path.mkdir(parents=True)
    (path / "arrangement.json").write_text(
        json.dumps({"source": {"input_uri": source}, "confidence": {"overall": confidence}}),
        encoding="utf-8",
    )
    (path / "quality_report.json").write_text(json.dumps({"status": "passed"}), encoding="utf-8")
    (path / "tab.md").write_text("# TAB\n", encoding="utf-8")


def test_init_workspace_creates_schema_v1_project_metadata(tmp_path: Path) -> None:
    payload = init_workspace(tmp_path, name="Demo Project")

    assert payload["schema_version"] == 1
    assert payload["project"]["name"] == "Demo Project"
    assert (tmp_path / "workspace.json").exists()


def test_update_workspace_index_discovers_multiple_artifact_dirs(tmp_path: Path) -> None:
    init_workspace(tmp_path, name="Demo")
    _write_artifact(tmp_path / "song-a", source="a.wav")
    _write_artifact(tmp_path / "song-b", source="b.wav")

    payload = update_workspace_index(tmp_path)

    assert [song["song_id"] for song in payload["songs"]] == ["song-a", "song-b"]
    assert payload["songs"][0]["source"] == "a.wav"
    assert payload["songs"][1]["quality_status"] == "passed"


def test_add_artifact_to_workspace_preserves_artifact_history(tmp_path: Path) -> None:
    init_workspace(tmp_path, name="Demo")
    artifact = tmp_path / "take-1"
    _write_artifact(artifact)

    first = add_artifact_to_workspace(tmp_path, artifact, song_id="lead", title="Lead")
    second = add_artifact_to_workspace(tmp_path, artifact, song_id="lead", title="Lead")

    assert first["songs"][0]["history"][0]["artifact_dir"] == "take-1"
    assert len(second["songs"][0]["history"]) == 2


def test_web_ui_uses_workspace_project_name(tmp_path: Path) -> None:
    init_workspace(tmp_path, name="Demo Project")
    _write_artifact(tmp_path / "song-a")
    update_workspace_index(tmp_path)

    html = render_web_ui_html(tmp_path)

    assert "Demo Project" in html
    assert "song-a" in html
