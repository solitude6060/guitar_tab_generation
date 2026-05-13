# ADR-20260513：Demo / Tutorial / DAW Export Sequencing

## 狀態

Accepted as product sequencing guidance.

## 背景

原始願景包含教學、GarageBand/Logic Pro 匯入與完整多樂器音軌。但目前 MVP 核心仍在 local audio → guitar TAB artifact。若過早做 UI/DAW，會把工程重心從 transcription quality 與 artifact contract 移走。

## 決策

採用以下順序：

1. Artifact viewer demo：只讀現有 artifact。
2. Practice tutorial generator：從 verified arrangement 產生 Markdown 練習建議。
3. MIDI/MusicXML export：先做通用交換格式。
4. GarageBand/Logic Pro：先文件化匯入流程，不直接產生專有完整 session。

## 替代方案

- 直接做 GarageBand/Logic project export。  
  拒絕原因：專有格式/多軌品質/模型成熟度不足，驗收成本高。
- 先做 upload UI。  
  拒絕原因：檔案處理、長任務與安全問題會分散核心 MVP。
- 先做 artifact viewer。  
  採用原因：低風險、能展示成果、可重用現有 outputs。

## 後果

- 使用者展示會先偏工程/demo，不是完整產品 UI。
- DAW 願景保留，但經由 MIDI/MusicXML 逐步驗證。
- 教學生成會依賴已驗證的 `arrangement.json`，不憑空生成。

## 驗證

- P6/P7/P8 各自有 PRD/test spec。
- UI/demo 不得繞過 `quality_report.json` warnings。
- Export artifact 必須保留 confidence/provenance companion report。
