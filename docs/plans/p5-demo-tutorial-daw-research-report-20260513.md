# P5 Research Report：Demo / Tutorial / DAW Export

日期：2026-05-13  
狀態：Research completed for next planning pass

## 1. 決策摘要

P5 不直接開大型功能。建議後續拆成三個獨立 phase：

1. **P6 Artifact Viewer Demo**：先做 Streamlit/Notebook 或簡易 static viewer，讀取現有 artifact，不改核心 pipeline。
2. **P7 Practice Tutorial Generator**：從 `arrangement.json` 產生練習步驟、段落循環與慢速練習建議。
3. **P8 Export Research / MIDI-MusicXML-first**：先做 MIDI/MusicXML export，再研究 GarageBand/Logic Pro 匯入；不要一開始承諾完整 DAW session。

## 2. Demo 方向

### 建議方案：artifact viewer first

- 輸入：既有 output dir（含 `arrangement.json`、`tab.md`、`quality_report.json`）。
- 顯示：metadata、sections、chords、TAB、warnings、quality status。
- 優點：不碰音訊處理，不增加上傳/權限/儲存問題。
- 驗收：三個 golden fixture output dir 都能被 viewer 讀取。

### 延後方案：upload UI

- 會涉及檔案上傳、長任務、暫存、錯誤回報與環境差異。
- 等 P2/P3/P6 穩定後再做。

## 3. Tutorial 方向

### 建議 MVP

從 `arrangement.json` 與 `tab.md` 產生 Markdown 教學：

- 先看 warnings / confidence。
- 分段練習：每個 section 一段。
- chord progression 練習。
- riff/lead 慢速練習建議。
- 建議節拍器 BPM：原速 50% / 75% / 100%。

### 非目標

- 不做完整影片課程。
- 不宣稱原演奏者技巧。
- 不生成未驗證音樂理論內容。

## 4. Export / DAW 方向

### 建議順序

1. MIDI export（最小、可測、可被 DAW 匯入）。
2. MusicXML export（譜面交換，比 DAW session 更通用）。
3. GarageBand / Logic Pro：研究匯入 MIDI/MusicXML 的使用流程，而不是產生專有 session。
4. 若未來需要多軌，先定義 track schema，再做 export。

### 風險

- GarageBand/Logic Pro 專案格式不是最適合 MVP 直接生成的格式。
- 多樂器音軌需要 source separation / arrangement quality 先成熟。
- Export 不應掩蓋 transcription confidence；所有低信心都要進 metadata 或 companion report。

## 5. 建議後續 PRD

### P6 Artifact Viewer Demo

- Branch：`feature/artifact-viewer-demo`
- PRD：`docs/plans/p6-artifact-viewer-demo-prd-YYYYMMDD.md`
- Test spec：讀取三個 fixture output snapshots。

### P7 Practice Tutorial Generator

- Branch：`feature/practice-tutorial-generator`
- PRD：`docs/plans/p7-practice-tutorial-generator-prd-YYYYMMDD.md`
- Test spec：fixture arrangement → tutorial markdown contract。

### P8 MIDI/MusicXML Export

- Branch：`feature/midi-musicxml-export`
- ADR：是否引入 `music21` 或採用自製最小 MIDI writer。
- Test spec：export artifact parse/exists + confidence metadata preserved。

## 6. Hard constraints

- 不新增重依賴前先寫 ADR。
- 不讓 UI 重新實作 pipeline；UI 只能呼叫 CLI/pipeline 或讀 artifact。
- 不承諾完整 DAW session export 直到 MIDI/MusicXML path 已驗證。
