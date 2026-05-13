from __future__ import annotations

from pathlib import Path


def test_project_agent_and_skill_contract_exist() -> None:
    agents = Path("AGENTS.md")
    guide = Path("docs/agents/guitar-tab-agent.md")

    assert agents.exists()
    assert guide.exists()

    agents_text = agents.read_text(encoding="utf-8")
    guide_text = guide.read_text(encoding="utf-8")
    for required in ["PR / code review", "merge `dev`", "merge `main`", ".omx/", "Co-authored-by: OmX"]:
        assert required in agents_text
    assert "~/.codex/skills/guitar-tab-product-dev/SKILL.md" in agents_text
    assert "錯誤位置的 `skills/`" in agents_text
    for required in ["P8 Interface MVP", "Feature branch", "code review"]:
        assert required in guide_text


def test_p8_interface_mvp_is_planned_in_roadmap() -> None:
    plan = Path("docs/plans/p8-interface-mvp-plan-20260513.md")
    backlog = Path("docs/plans/backlog-20260512.md")
    execution = Path("docs/plans/development-execution-plan-20260513.md")

    assert plan.exists()
    plan_text = plan.read_text(encoding="utf-8")
    for required in [
        "Interface MVP",
        "artifact directory",
        "不重新跑 transcription",
        "不下載 URL",
        "warnings / confidence",
        "interface.html",
    ]:
        assert required in plan_text
    assert "P8 | Interface MVP" in backlog.read_text(encoding="utf-8")
    assert "P8 Interface MVP" in execution.read_text(encoding="utf-8")


def test_user_facing_review_has_traditional_chinese_version() -> None:
    agents = Path("AGENTS.md")
    review_zh = Path("docs/reviews/p7-pr-code-review-20260513.zh-TW.md")

    assert "所有給使用者看的文件都必須提供繁中版本" in agents.read_text(encoding="utf-8")
    assert review_zh.exists()
    text = review_zh.read_text(encoding="utf-8")
    for required in ["程式碼審查", "結論", "驗證證據", "合併建議"]:
        assert required in text
