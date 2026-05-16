# DAW 匯出 Bundle（GarageBand / Logic 匯入）

## 功能說明

目前 `export` 指令新增：

- `musicxml`（單一檔）
- `midi`（單一檔）
- `daw`（資料夾 bundle）

`--format daw` 專為 GarageBand / Logic Pro 工作流程設計，特別適合 full-song 的 chunked 轉譯結果。

## 使用方式

```bash
uv run guitar-tab-generation export <artifact_dir> --format daw
```

預設輸出資料夾為 `<artifact_dir>/daw_bundle`。

可指定輸出資料夾：

```bash
uv run guitar-tab-generation export <artifact_dir> --format daw --out ./my-daw-bundle
```

## 輸出內容

- `track-01.mid` / `track-01.musicxml`（full-song 時會有 track-02...）
- `daw_manifest.json`（track 對應表、chunk window）
- `DAW_IMPORT_README.md`（匯入步驟）

## Clip 與 full-song 行為差異

- Clip（`duration_class=clip`）：輸出單一 track。
- Full-song chunked（`duration_class=full_song`）：每個 chunk 輸出一條 track。

## 匯入步驟（建議）

1. 開啟 GarageBand / Logic Pro。
2. 每條 `.mid` 匯入成一條新 track。
3. 參考 `daw_manifest.json`：
   - `strategy`
   - track index / 名稱
   - chunk 窗口（若為 chunked）
4. 依 `arrangement.json` 的 `timebase.tempo_bpm` 設定 BPM。

## 介面導引

若已經有 `interface.html`，可直接在「DAW 匯入」區塊閱讀下一步導覽，免重看 CLI 指令：

1. 用瀏覽器開啟 `interface.html`。
2. 在 DAW 匯入區塊檢查：
   - 是否已建立 `daw_bundle`
   - 匯出策略（`single_track` / `chunked_full_song`）
   - 每條 `track-*.mid` 與 `track-*.musicxml` 連結
3. 依清單順序點擊或匯入檔案到 GarageBand / Logic Pro。

如此可直接接續既有 artifact 工作流程，不需再次查閱指令才知道接下來該匯入哪個檔案。
