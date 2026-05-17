# P31 Local LLM Tutorial v2 Review

日期：2026-05-18
狀態：本地審查通過

## 範圍

- `docs/plans/p31-local-llm-tutorial-v2-prd-20260518.md`
- `docs/plans/p31-local-llm-tutorial-v2-test-spec-20260518.md`
- `src/guitar_tab_generation/practice_tutorial.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_practice_tutorial.py`
- `tests/e2e/test_cli_practice_tutorial.py`

## 審查結論

P31 保持 default-safe：

- `tutorial` 預設不跑 LLM。
- `--llm-backend fake` 產生 deterministic coaching notes。
- `--llm-backend local` 在 runtime 未設定時明確失敗，不 silent fallback。
- fake LLM notes 引用 `arrangement.json`、`quality_report.json`、`tab.md`，且聲明不修改 notes/chords/sections/fingerings。

## 驗證證據

```bash
uv run pytest tests/unit/test_practice_tutorial.py tests/e2e/test_cli_practice_tutorial.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation tutorial --help
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-p31-demo-20260517T1720
uv run guitar-tab-generation tutorial /tmp/guitar-tab-p31-demo-20260517T1720 --llm-backend fake
```

結果：

- targeted tests：14 passed
- full regression：239 passed
- compileall：通過
- diff check：通過
- manual demo：`tutorial.md` 含 `## LLM Coaching Notes` 與 artifact citations

## 剩餘風險

- 本階段只提供 fake backend 與 failure gate；真實 local LLM runtime 仍需後續明確設定。
