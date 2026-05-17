# P32 Web UI MVP Review

日期：2026-05-18
範圍：`feature/web-ui-mvp`

## 結論

未發現 blocker。P32 交付維持 artifact-first：`web-ui` 只掃描既有 workspace artifacts 並輸出靜態 `web-ui.html`，不新增 server、前端 build stack、URL 下載或 heavy runtime 執行路徑。

## 檢查項

- CLI：新增 `guitar-tab-generation web-ui <workspace_dir> [--out]`。
- Artifact 邊界：只讀含 `arrangement.json` 的 artifact 目錄，讀取 `quality_report.json`、`tab.md`、`viewer.md`、`tutorial.md`、`interface.html`。
- 安全性：HTML 內容與連結文字使用 escaping；無任意 URL 下載或 subprocess 執行。
- Default 行為：不改 `transcribe`、`view`、`tutorial`、`interface`、`export` 既有預設。

## 驗證證據

- `uv sync --group dev`：通過。
- `uv run pytest tests/unit/test_web_ui.py tests/e2e/test_cli_web_ui.py -q`：5 passed。
- `uv run pytest -q`：244 passed。
- `uv run python -m compileall -q src tests`：通過。
- `git diff --check HEAD`：通過。
- `uv run guitar-tab-generation web-ui --help`：列出 `workspace_dir` 與 `--out`。
- 手動 demo：`/tmp/guitar-tab-p32-demo-20260517T172455Z/web-ui.html` 含 `Guitar Tab Workspace`、`song`、`tab.md`、`viewer.md`、`tutorial.md`、`interface.html`。

## 外部審查工具狀態

- `gemini --help` 可執行；非互動 review 嘗試卡在瀏覽器 authentication prompt，未產生可用審查結果。
- `claude-mm`：本機 `command -v claude-mm` 無結果，未安裝或不在 `PATH`。

## 剩餘風險

- P32 是靜態 HTML browser，尚未包含 P33 job queue 或 P38 project workspace 管理。
- 未做瀏覽器截圖 visual QA；本階段驗收以 HTML artifact 內容與連結為主。
