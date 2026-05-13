# Open Questions

- [x] 是否需要在 MVP 明確支援 alternate tunings，或僅支援標準調弦 EADGBE？（Task 3 review 決議：MVP 僅支援標準調弦 EADGBE；alternate tunings 延後，避免擴 scope）
- [x] 初版輸出是否需要 PDF 作為必備，或 Markdown/TXT + JSON 即可？（Task 3 review 決議：Markdown/TXT + `arrangement.json` + `quality_report.json` 必備；PDF/MusicXML/MIDI 可選）
- [x] 人工音樂驗收者是否可由專案作者擔任，或需第二位吉他手交叉驗收？（Architect ITERATE 後決議：作者 + golden fixture rubric 可作 MVP 驗收；第二位吉他手建議但非 blocker）
- [x] `arrangement.json` confidence 門檻初值如何設定？決議：MVP 預設 notes 0.55、chords 0.60、sections 0.50、fingering 0.65；可由設定檔調整，低於門檻必產生 warning。
- [x] MVP 支援 fret 範圍要固定到 20、22 或 24 fret？決議：MVP 固定支援 0–20 fret，以保守覆蓋多數練習情境並讓不可彈 TAB hard fail 可測。
- [x] 合法 URL 後續路徑的 allowlist 來源要如何定義？（Task 3 review 決議：MVP 不定義 allowlist 實作；URL 僅 disabled/stub/policy gate，合法 allowlist path 留到 post-MVP ADR）
