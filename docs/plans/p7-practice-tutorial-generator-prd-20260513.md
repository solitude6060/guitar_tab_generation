# P7 PRD：Practice Tutorial Generator

日期：2026-05-13
狀態：Implemented
Branch：`feature/practice-tutorial-generator`

## 1. 背景

P6 已能讀取 transcription artifacts 並產生 demo viewer。P7 延續 P5 research，從同一組 artifacts 產生可練習的 Markdown 教學，讓使用者知道先檢查哪些 warning、每段如何循環練習、和弦如何拆練、lead/riff 如何用慢速節拍器逐步練。

## 2. 目標

新增 CLI：

```bash
guitar-tab-generation tutorial <artifact_dir> --out tutorial.md
```

它會讀取既有 `arrangement.json`、`quality_report.json`、`tab.md`，產生 `tutorial.md`。

## 3. 使用者價值

- 把 TAB artifact 轉成「下一步怎麼練」的實用指南。
- 明確提醒 confidence / warning，不把低信心結果包裝成確定教學。
- 針對 sections、chord progression、note sketch 產生練習順序。
- 提供 50% / 75% / 100% 原速的節拍器 BPM 建議。

## 4. 功能需求

1. `tutorial` command 接受 artifact directory。
2. 預設輸出 `<artifact_dir>/tutorial.md`，`--out` 可覆寫。
3. Markdown 必須包含：
   - `# Practice Tutorial`
   - Readiness / confidence / warning 前置檢查
   - Warm-up tempo ladder：50%、75%、100% BPM
   - Section loop plan
   - Chord practice plan
   - Lead/riff practice plan
   - Safety note：所有低信心內容需先人工確認
   - 原始 `tab.md` reference
4. 缺必要 artifact 時回傳非 0，且不產生誤導成功檔案。
5. 不重新執行 transcription pipeline。

## 5. 非目標

- 不產生影片課程。
- 不宣稱原演奏者技巧或未驗證音樂理論分析。
- 不新增 UI/Notebook/Streamlit。
- 不做 MIDI/MusicXML 或 DAW export。

## 6. Definition of Done

實作狀態：已完成。CLI `tutorial`、unit/e2e tests、uv regression、manual demo gate 已通過。

- PRD + test spec 存在於 `docs/plans/`。
- 先新增 failing tests，再實作。
- 三個 golden fixtures 透過 `transcribe` 後可再透過 `tutorial` 產生 `tutorial.md`。
- `uv run pytest -q` 通過。
- `uv run guitar-tab-generation --help` 與 `tutorial --help` 通過。
- `.omx/` 未被追蹤；commit 無 OmX co-author trailer。
