# P31 Local LLM Tutorial v2 Test Spec

日期：2026-05-18
狀態：Planned

## Unit Tests

- fake LLM prompt builder 只讀 artifact summary。
- fake LLM output 包含 citations。
- local backend missing 時拋出可讀錯誤。

## CLI / E2E Tests

- default `tutorial` 不含 LLM coaching notes。
- `tutorial --llm-backend fake` 寫入 LLM coaching notes。
- `tutorial --llm-backend local` 失敗且不 silent fallback。

## Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation tutorial --help
```
