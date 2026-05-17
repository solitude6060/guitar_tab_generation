# P26 PRD：Stem-aware Basic Pitch Pipeline

日期：2026-05-17
狀態：Planned
範圍：讓 Basic Pitch 可明確選擇 P25 產生的 stem artifact 作為 note transcription 輸入，同時保留 `transcribe` 的安全預設。

## 1. 背景

P25 已新增 `separate-stems <artifact_dir>` sidecar，輸出 `stems/` 與 `stem_manifest.json`。P26 的目標不是重跑 Demucs，也不是讓 `transcribe` 預設自動分軌；而是讓使用者在已具備 stem artifact 後，可以明確要求 Basic Pitch 對特定 stem 執行，並把 provenance 寫清楚。

## 2. 目標

1. 新增明確 stem-aware transcription 路徑。
2. Basic Pitch 可讀取 `stem_manifest.json` 中指定 stem 的音訊檔。
3. note events provenance 標記：
   - `backend: basic-pitch`
   - `stem: <stem-name>`
   - `stem_manifest: stem_manifest.json`
4. 若指定 stem 不存在，清楚提示先跑 `separate-stems` 或改用可用 stem。
5. 不把 Demucs 接進 `transcribe` default，不 silent fallback 到 mix。

## 3. 建議 CLI contract

優先採用 artifact-first sidecar，避免 `transcribe` 同時負責 ingest、分軌與重新產物寫入：

```bash
guitar-tab-generation transcribe-stem <artifact_dir> --backend basic-pitch --stem guitar
```

輸出：

- 預設輸出 `stem_notes/<stem>.notes.json`。
- 新增 `stem_notes/<stem>.metadata.json`，記錄 source stem、backend、model、runtime 與 manifest provenance。

## 4. 功能需求

### 4.1 Stem manifest reader

- 讀取 `<artifact_dir>/stem_manifest.json`。
- 驗證指定 stem 的 `path` 存在且位於 artifact directory 內。
- 回傳 stem audio path 與 manifest provenance。

### 4.2 Basic Pitch adapter extension

- 允許 `BasicPitchAnalysisBackend` 接收 `stem_name` 或在事件轉換階段覆寫 provenance stem。
- 若 backend 仍收到 mix audio path，provenance 必須保持 `stem: mix`。

### 4.3 Output policy

- 不自動改 `arrangement.json`、`tab.md`、`quality_report.json`，避免 P26 直接改變既有 artifact rendering。
- 若後續要合併 notes 回主 artifact，應留到 P27 quality scoring 或另一個明確 merge phase。

## 5. 非目標

- 不執行 Demucs。
- 不新增 `transcribe --stem` default path。
- 不改 fixture backend。
- 不把 stem notes 自動視為比 mix notes 更正確。
- 不做 chord/section/fingering 重新推導。

## 6. 驗收標準

- `transcribe-stem --help` 顯示 artifact_dir、`--backend basic-pitch`、`--stem`。
- 缺少 `stem_manifest.json` 時清楚失敗。
- 指定不存在 stem 時清楚失敗，列出可用 stems。
- fake Basic Pitch runtime 可對 fake stem path 產生 `stem_notes/<stem>.notes.json`。
- note provenance 包含指定 stem，不 fallback 到 mix。
- `transcribe --help` 仍不含 `--stem`。
- `uv run pytest -q` 通過。
