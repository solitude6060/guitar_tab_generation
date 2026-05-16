from __future__ import annotations

import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_torch_ai_dependency_group_is_optional_and_route_scoped() -> None:
    groups = _pyproject()["dependency-groups"]

    assert "torch-ai" in groups
    torch_ai = groups["torch-ai"]
    assert any(dep.startswith("torch>=") for dep in torch_ai)
    assert any(dep.startswith("torchaudio>=") for dep in torch_ai)
    assert any(dep.startswith("torchcrepe>=") for dep in torch_ai)
    assert any(dep.startswith("demucs>=") for dep in torch_ai)
    assert not set(torch_ai) & set(groups["dev"])
    assert not set(torch_ai) & set(groups["ai"])


def test_default_uv_groups_do_not_include_heavy_torch_ai() -> None:
    pyproject = _pyproject()
    tool_uv = pyproject.get("tool", {}).get("uv", {})

    assert tool_uv["default-groups"] == ["dev"]


def test_torch_install_docs_exist_in_english_and_traditional_chinese() -> None:
    english = (REPO_ROOT / "docs" / "torch-optional-dependencies.md").read_text(encoding="utf-8")
    zh_tw = (REPO_ROOT / "docs" / "torch-optional-dependencies.zh-TW.md").read_text(encoding="utf-8")

    for text in (english, zh_tw):
        assert "uv sync --group torch-ai" in text
        assert "uv run guitar-tab-generation torch-smoke" in text
        assert "torchcrepe" in text
        assert "Demucs" in text
        assert "default" in text or "預設" in text
