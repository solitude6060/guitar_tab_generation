# P32 Web UI MVP Test Spec

日期：2026-05-18
狀態：Planned

## Tests

- unit：掃描 workspace artifact dirs。
- unit：HTML escape 與 artifact links。
- e2e：`web-ui --help`。
- e2e：fixture artifact workspace → `web-ui.html` 含 artifact browser。

## Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation web-ui --help
```
