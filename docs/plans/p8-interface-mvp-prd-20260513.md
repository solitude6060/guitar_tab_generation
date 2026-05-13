# P8 PRD：Interface MVP

日期：2026-05-13
狀態：Implemented
Branch：`feature/interface-mvp`

## 1. 背景

使用者希望產品「好用」時有介面。P6 已有 `viewer.md`，P7 已有 `tutorial.md`。P8 要提供一個可離線開啟的 HTML artifact workspace，讓使用者不用在多個 Markdown 檔案之間切換。

## 2. 目標

新增 CLI：

```bash
guitar-tab-generation interface <artifact_dir> --out interface.html
```

它只讀既有 artifacts，產生 `interface.html`。

## 3. 功能需求

1. `interface` command 接受 artifact directory。
2. 預設輸出 `<artifact_dir>/interface.html`，`--out` 可覆寫。
3. HTML 必須包含：
   - title / source / tempo / confidence / quality status
   - warnings 區塊，且放在首頁明顯位置
   - sections、chord progression、practice links
   - `tab.md`、`viewer.md`、`tutorial.md` 連結或缺檔提示
4. HTML 必須 escape artifact content，避免 artifact 文字破壞頁面。
5. 不重新執行 transcription pipeline。
6. 不下載 URL。

## 4. 非目標

- 不做上傳 UI、登入、雲端儲存。
- 不引入前端框架或重依賴。
- 不做即時音訊處理。
- 不做 MIDI/MusicXML 或 DAW export。

## 5. Definition of Done

實作狀態：已完成。CLI `interface`、unit/e2e tests、uv regression、manual demo gate 已通過。

- PRD + test spec 存在。
- 先新增 failing tests，再實作。
- 三個 golden fixtures 可跑 `transcribe → view → tutorial → interface`。
- `uv run pytest -q` 通過。
- `uv run guitar-tab-generation interface --help` 通過。
- Feature 經 code review 後 merge `dev`，驗證，再 merge `main`。
