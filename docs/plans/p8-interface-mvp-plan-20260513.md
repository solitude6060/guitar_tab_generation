# P8 Plan：Interface MVP（好用介面）

日期：2026-05-13
狀態：Implemented
建議分支：`feature/interface-mvp`

## 1. 背景

使用者明確要求「要好用可能需要介面」。目前 P6/P7 已把 artifacts 轉成 viewer / tutorial Markdown；P8 應該在不重寫 pipeline、不新增重依賴的前提下，提供更接近產品使用的介面。

## 2. 建議方向

### 首選：Static artifact workspace

- CLI 產生 `index.html` 或 `interface.html`，讀同一個 artifact directory。
- 顯示：TAB、viewer summary、tutorial、warnings、confidence、sections、chords。
- 優點：零後端、可離線、可被 GitHub artifact 或本機瀏覽器打開。

### 延後：Web app / upload UI

- 需要處理上傳、長任務、暫存、權限、錯誤狀態。
- 等 artifact workspace 穩定後再做。

## 3. Scope

P8 MVP：

```bash
guitar-tab-generation interface <artifact_dir> --out interface.html
```

需求：

- 只讀 artifacts，不重新跑 transcription。
- 不下載 URL。
- warnings / confidence 必須顯示在首頁可見位置。
- 可連到 `tab.md`、`viewer.md`、`tutorial.md`。
- 三個 golden fixtures 都能產生 interface。

## 4. Test strategy

- Unit：HTML renderer 包含必要 sections 與 escaped content。
- E2E：三個 fixtures `transcribe → view → tutorial → interface`。
- Regression：`uv run pytest -q`、`uv run guitar-tab-generation interface --help`。

## 5. 非目標

- 不做登入、上傳、雲端儲存。
- 不做即時音訊處理。
- 不承諾 GarageBand / Logic Pro 專案檔。


## 6. Execution specs

- PRD：`docs/plans/p8-interface-mvp-prd-20260513.md`
- Test spec：`docs/plans/p8-interface-mvp-test-spec-20260513.md`
