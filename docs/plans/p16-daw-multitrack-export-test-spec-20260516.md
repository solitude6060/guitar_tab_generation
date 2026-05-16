# P16 Test Spec：DAW Multi-track Export Bundle（GarageBand / Logic 匯入）

## Scope

驗證 `export --format daw` 與 `P11` full-song chunk 計畫整合是否可直接匯入 DAW 工作流程（MIDI + MusicXML bundle）。

## Red-first policy

1. 先新增單元與 E2E 測試，確認目前行為失敗，再實作。
2. 只在通過測試後允許最小實作修正。

## 測試項目

### Unit（`tests/unit/test_exporters.py`）

1. `test_render_daw_bundle_tracks_chunks_and_manifest`
   - 建立 chunked arrangement + 有跨邊界 note events。
   - 驗證：
     - 產生 `daw_bundle` 或指定 `--out` 的資料夾；
     - manifest strategy 為 `chunked_full_song`；
     - track 數量與 chunks 一致；
     - `track-XX.mid` 開頭是 `MThd`。

2. `test_write_export_default_output_path_by_format`
   - 增加 `daw -> daw_bundle` 的預設輸出路徑期望。

3. `test_write_export_rejects_unknown_format`
   - 保持 `pdf` 不支援。

### E2E（`tests/e2e/test_cli_export.py`）

1. `test_cli_export_daw_bundle_for_fullsong_golden_window`
   - 用 180 秒合法 full-song fixture（本地靜音）跑 `transcribe`。
   - 跑 `export --format daw`。
   - 驗證 bundle 目錄、manifest、每條 track 的 `.mid` 與 `.musicxml` 存在。

2. `test_cli_export_fails_cleanly_when_artifact_is_missing`
   - 缺 artifact 的錯誤流程保留。

### 指令驗證

```bash
uv run pytest -q tests/unit/test_exporters.py tests/e2e/test_cli_export.py tests/e2e/test_cli_full_song_length.py
uv run guitar-tab-generation export --help
uv run guitar-tab-generation export <artifact_dir> --format daw
```

## 驗收標準

- `write_export` 在 daW 格式下不寫入 `score.*` 迷惑性檔案。
- full-song chunk 轉檔時每個 track 都有 `.mid` + `.musicxml`，並有 `DAW_IMPORT_README.md`。
- `uv run pytest -q` 仍為全綠。
