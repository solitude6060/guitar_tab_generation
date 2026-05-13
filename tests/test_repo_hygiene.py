"""Repository hygiene checks for the uv-first development flow."""
from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        stderr=subprocess.STDOUT,
    )


def test_omx_state_is_not_tracked() -> None:
    assert _git("ls-files", ".omx").strip() == ""


def test_generated_python_artifacts_are_not_tracked() -> None:
    tracked = _git("ls-files").splitlines()
    forbidden = [
        path
        for path in tracked
        if "__pycache__/" in path
        or ".pytest_cache/" in path
        or path.endswith(".pyc")
        or path.endswith(".pyo")
        or path.endswith(".egg-info")
        or ".egg-info/" in path
    ]
    assert forbidden == []


def test_omx_coauthor_trailer_is_absent_from_branch_history() -> None:
    history = _git("log", "--format=%B", "HEAD")
    assert "Co-authored-by: OmX" not in history


def test_ci_workflow_runs_uv_test_and_cli_gates() -> None:
    assert CI_WORKFLOW.exists()
    workflow = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "uv sync --locked --group dev" in workflow
    assert "uv run pytest -q" in workflow
    assert "uv run guitar-tab-generation --help" in workflow
    assert "git ls-files .omx" in workflow
