# P38 Project Workspace Review

日期：2026-05-18
範圍：`feature/project-workspace`

## 結論

未發現 blocker。P38 交付 workspace-local `workspace.json` schema、`workspace init/index/add-artifact` CLI，以及 Web UI project name 顯示。既有單 `artifact_dir` flow 未被 workspace 綁死。

## 檢查項

- CLI：新增 `guitar-tab-generation workspace init/index/add-artifact`。
- Schema：`schema_version: 1`、`project` metadata、`songs`、artifact `history`。
- Index：掃描 workspace 下含 `arrangement.json` 的 artifact dirs，讀取 source / quality / confidence。
- Add artifact：可指定 `song_id` / `title`，重複加入保留 history。
- Web UI：存在 `workspace.json` 時用 project name 作為頁面 title/H1。
- Compatibility：既有 `transcribe`、`web-ui` 單 artifact 掃描行為仍通過既有測試。

## 驗證證據

- `uv run pytest tests/unit/test_project_workspace.py tests/e2e/test_cli_workspace.py tests/unit/test_web_ui.py -q`：9 passed。
- `uv sync --group dev`：通過。
- `uv run pytest -q`：268 passed。
- `uv run python -m compileall -q src tests`：通過。
- `git diff --check HEAD`：通過。
- `uv run guitar-tab-generation workspace --help`：列出 init/index/add-artifact。
- `uv run guitar-tab-generation workspace init --help`：通過。
- `uv run guitar-tab-generation workspace index --help`：通過。
- `uv run guitar-tab-generation workspace add-artifact --help`：通過。
- 手動 demo：`/tmp/guitar-tab-p38-demo-20260517T175042Z`，兩個 fixture artifacts 被 index 到 `workspace.json`；`web-ui.html` 顯示 `DemoProject`、`song-a`、`song-b`、`tab.md`。

## 外部審查工具狀態

- `gemini --help` 可執行；本 session 非互動 review 嘗試卡在 browser authentication prompt，未產生可用審查結果。
- `claude-mm`：本機 `command -v claude-mm` 無結果，未安裝或不在 `PATH`。

## 剩餘風險

- Workspace JSON 是本機 index，不是唯一 truth source；artifact files 仍是主資料。
- 未做跨程序 concurrent write lock；目前符合本機單使用者 MVP。
