# P16 PRD：DAW Multi-track Export Bundle（GarageBand / Logic 匯入）

日期：2026-05-16
狀態：Implemented
Branch：`feature/daw-multitrack-export`

## 1. 背景

P9 已完成通用 `MusicXML` 與 `MIDI` 匯出，但在 3–8 分鐘 full-song 流程中，需要能對應到後續 DAW 分軌編輯。  
基於 P11 的 `chunked_full_song` `processing_plan`，P16 將把現有 export 擴充為「一鍵產生 DAW 匯入 bundle」。

## 2. 目標

新增 `export --format daw`：

1. 保留既有 `musicxml` / `midi` 行為不變。
2. 對於 clip（`duration_class=clip`）：
   - 預設輸出單一 track 檔案（`track-01.mid`、`track-01.musicxml`）。
3. 對於 full-song（`duration_class=full_song` 且 `processing_plan.mode=chunked_full_song`）：
   - 依照 chunk 計畫輸出多條 track（`track-01`、`track-02`…）。
   - 每條 track 同時輸出 `.mid` 與 `.musicxml`。
4. 產出 `daw_manifest.json`（track map + source window）與 `DAW_IMPORT_README.md`。

## 3. 功能需求

### 3.1 CLI

- `guitar-tab-generation export <artifact_dir> --format daw --out <bundle_dir>`
- 缺少 artifacts 時回傳失敗，不產生誤導性輸出。
- `--out` 未指定時預設為 `<artifact_dir>/daw_bundle`。

### 3.2 DAW bundle 結構

輸出目錄至少包含：

- `track-01.mid` / `track-01.musicxml`（clip or 第 1 track）
- `track-02.mid` / `track-02.musicxml` …（full-song chunk 後每段）
- `daw_manifest.json`
- `DAW_IMPORT_README.md`

### 3.3 manifest 欄位

`daw_manifest.json` 必須至少包含：

- `export_version`
- `exported_at`
- `strategy`（`single_track` / `chunked_full_song`）
- `track_count`
- `tracks[]`（含 `index`, `name`, `strategy`, `window`, `midi`, `musicxml`, `note_count`）

### 3.4 P8 usability integration

- 在 `export`/`usage` 說明加入 `daw` 格式可直接匯入 GarageBand / Logic 的使用提示。

## 4. 非目標

- 不生成 GarageBand `.band` 或 Logic Project 專有檔。
- 不保證 chunk boundary 對齊節拍；目前為轉檔用窗口切分。
- 不加入 stem 分離或實體 source track 導出（例如鼓/貝斯/人聲）。

## 5. Acceptance Criteria

1. 單元測試與 e2e 測試涵蓋：
   - 單 track clip 的 `--format daw` 輸出。
   - `--format daw` 於 chunked full-song 會輸出對應數量 track。
   - 缺 artifact 時錯誤不會產生 bundle。
2. `uv run guitar-tab-generation export --help` 顯示 `daw` 可選。
3. `uv run pytest -q` 維持綠燈。
4. 文件新增：
   - `docs/daw-bundle-export.md`
   - `docs/daw-bundle-export.zh-TW.md`
5. 遵守 no `.omx` / no co-author / uv flow 的既有規則。
