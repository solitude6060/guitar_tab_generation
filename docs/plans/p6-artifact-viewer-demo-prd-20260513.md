# P6 PRD：Artifact Viewer Demo

日期：2026-05-13
狀態：Implemented
Branch：`feature/artifact-viewer-demo`

## 1. 背景

P5 research 建議先做 artifact viewer，讓使用者可在不重新跑音訊分析、不新增重 UI 依賴的情況下，檢視 `transcribe` 已產出的 `arrangement.json`、`quality_report.json`、`tab.md` 等 artifacts。

## 2. 目標

新增一個最小、可測、repo-native 的 viewer：

```bash
guitar-tab-generation view <artifact_dir> --out viewer.md
```

它會讀取既有 artifact directory，產生可分享的 Markdown demo summary。

## 3. 使用者價值

- 快速檢查轉譜結果是否可練。
- 顯示 tempo、confidence、sections、chords、warnings、quality status。
- 對三個 golden fixtures 可重現展示結果。
- 保持 URL/legal policy 不變，不觸碰下載或權利繞過。

## 4. 功能需求

1. `view` command 接受 artifact directory。
2. 必須讀取：
   - `arrangement.json`
   - `quality_report.json`
   - `tab.md`
3. 輸出 Markdown 必須包含：
   - `# Artifact Viewer`
   - Source / tempo / duration / confidence
   - Quality status
   - Sections
   - Chord progression
   - Warnings
   - Practice readiness summary
   - Link/reference to original `tab.md`
4. 缺必要 artifact 時要回傳非 0 exit code，並提供清楚錯誤訊息。
5. 預設輸出為 `<artifact_dir>/viewer.md`；`--out` 可覆寫。

## 5. 非目標

- 不新增 Streamlit/Notebook/前端框架依賴。
- 不重新執行 transcription pipeline。
- 不讀取或下載任意 URL。
- 不承諾完整 DAW export 或互動式教學 UI。

## 6. Definition of Done

實作狀態：已完成。CLI `view`、unit/e2e tests、uv regression、manual demo gate 已通過。

- PRD + test spec 存在於 `docs/plans/`。
- 先新增 failing tests，再實作。
- 三個 golden fixtures 透過 CLI `transcribe` 後可再透過 CLI `view` 產生 viewer。
- `uv run pytest -q` 通過。
- `uv run guitar-tab-generation --help` 與 `view --help` 通過。
- `.omx/` 未被追蹤，commit 無 OmX co-author trailer。
