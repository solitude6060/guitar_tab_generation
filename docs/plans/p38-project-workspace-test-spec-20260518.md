# P38 Project Workspace Test Spec

日期：2026-05-18
狀態：Planned

## Tests

- unit：`init_workspace` 建立 schema v1 project metadata。
- unit：`update_workspace_index` 掃描多個 artifact dirs。
- unit：`add_artifact_to_workspace` 保留 artifact history。
- unit：Web UI 讀 `workspace.json` 並顯示 project name。
- e2e：`workspace --help`。
- e2e：`workspace init/index/add-artifact --json`。
- regression：既有單 artifact dir CLI 不變。

## Regression Gate

```bash
uv sync --group dev
uv run pytest tests/unit/test_project_workspace.py tests/e2e/test_cli_workspace.py tests/unit/test_web_ui.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation workspace --help
uv run guitar-tab-generation workspace init --help
uv run guitar-tab-generation workspace index --help
uv run guitar-tab-generation workspace add-artifact --help
```
