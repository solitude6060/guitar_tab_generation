"""Artifact-first static Web UI generation."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def discover_artifacts(workspace_dir: Path) -> list[dict[str, Any]]:
    """Discover artifact directories under a workspace."""

    candidates = [workspace_dir] + [path for path in workspace_dir.rglob("*") if path.is_dir()]
    artifacts: list[dict[str, Any]] = []
    for directory in candidates:
        arrangement_path = directory / "arrangement.json"
        if not arrangement_path.exists():
            continue
        arrangement = _read_json(arrangement_path)
        quality = _read_json(directory / "quality_report.json")
        artifacts.append(
            {
                "name": directory.name,
                "relative_path": directory.relative_to(workspace_dir).as_posix() if directory != workspace_dir else ".",
                "source": arrangement.get("source", {}).get("input_uri", "unknown"),
                "quality_status": quality.get("status", "unknown"),
                "overall_confidence": arrangement.get("confidence", {}).get("overall", "unknown"),
                "links": [name for name in ("tab.md", "viewer.md", "tutorial.md", "interface.html") if (directory / name).exists()],
            }
        )
    return sorted(artifacts, key=lambda item: str(item["relative_path"]))


def render_web_ui_html(workspace_dir: Path) -> str:
    """Render a static artifact browser."""

    artifacts = discover_artifacts(workspace_dir)
    if artifacts:
        rows = []
        for artifact in artifacts:
            base = "" if artifact["relative_path"] == "." else f"{artifact['relative_path']}/"
            links = " ".join(
                f'<a href="{escape(base + link)}">{escape(link)}</a>' for link in artifact["links"]
            ) or "No rendered links"
            rows.append(
                "<tr>"
                f"<td>{escape(str(artifact['relative_path']))}</td>"
                f"<td>{escape(str(artifact['source']))}</td>"
                f"<td>{escape(str(artifact['quality_status']))}</td>"
                f"<td>{escape(str(artifact['overall_confidence']))}</td>"
                f"<td>{links}</td>"
                "</tr>"
            )
        body = (
            "<table><thead><tr><th>Artifact</th><th>Source</th><th>Quality</th>"
            "<th>Confidence</th><th>Links</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>"
        )
    else:
        body = "<p>No artifact directories found.</p>"
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Guitar Tab Workspace</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; line-height: 1.5; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Guitar Tab Workspace</h1>
  {body}
</body>
</html>
"""


def write_web_ui(workspace_dir: Path, out_path: Path | None = None) -> Path:
    """Write web-ui.html and return the path."""

    workspace_dir.mkdir(parents=True, exist_ok=True)
    destination = out_path or workspace_dir / "web-ui.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_web_ui_html(workspace_dir), encoding="utf-8")
    return destination
