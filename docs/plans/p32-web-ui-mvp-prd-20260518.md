# P32 Web UI MVP PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P32 建立 artifact-first Web UI MVP。此階段不引入前端框架或服務端 job runner，先提供可開啟的本機 HTML artifact browser。

交付：

- 新增 CLI：`guitar-tab-generation web-ui <workspace_dir>`。
- 掃描 workspace 下含 `arrangement.json` 的 artifact 目錄。
- 輸出 `web-ui.html`，顯示 artifact list、quality status、source、links。
- UI 只讀 artifacts，不重寫 pipeline，不做 URL 下載。

## 2. 非目標

- 不建立長駐 server。
- 不新增 JavaScript build tool。
- 不在 UI 中直接執行 heavy runtime。

## 3. 驗收標準

- `web-ui --help` 可用。
- workspace 有多個 artifact dir 時，HTML 會列出每個 artifact。
- 缺 artifacts 時仍產生空狀態頁。
- HTML 連到 `tab.md`、`viewer.md`、`tutorial.md`、`interface.html`。
