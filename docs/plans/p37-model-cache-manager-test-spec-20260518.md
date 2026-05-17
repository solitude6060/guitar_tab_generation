# P37 Model Cache Manager Test Spec

日期：2026-05-18
狀態：Planned

## Tests

- unit：model manifest 包含 required ids 與 cache subdirs。
- unit：cache discovery 計算 exists、size bytes、smoke evidence path。
- unit：doctor 偵測 cache root 在 repo 內時給 warning。
- unit：prune dry-run 列出 unmanaged cache dirs 且不刪檔。
- unit：prune without dry-run raises error。
- e2e：`models --help` 顯示 list/doctor/prune。
- e2e：`models list --json --cache-root <fixture>`。
- e2e：`models doctor --json --cache-root <fixture>`。
- e2e：`models prune --dry-run --json --cache-root <fixture>`。

## Regression Gate

```bash
uv sync --group dev
uv run pytest tests/unit/test_model_cache.py tests/e2e/test_cli_models.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation models --help
uv run guitar-tab-generation models list --help
uv run guitar-tab-generation models doctor --help
uv run guitar-tab-generation models prune --help
```
