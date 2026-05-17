# P28 Chord Recognition Backend Test Spec

日期：2026-05-18
狀態：Planned

## 1. 測試策略

P28 只測 deterministic/fake artifact path。測試不得下載模型、不得執行 GPU、不得呼叫網路。

## 2. Unit Tests

- `test_build_chord_sidecar_from_arrangement_chord_spans`
  - 輸入包含 `chord_spans` 的 arrangement。
  - 驗證 schema、backend、summary、chords、provenance。
- `test_build_chord_sidecar_warns_on_low_confidence`
  - chord confidence 低於 `CONFIDENCE_THRESHOLDS["chords"]`。
  - 驗證 `LOW_CHORD_CONFIDENCE` warning。
- `test_build_chord_sidecar_rejects_missing_inputs`
  - 缺少 `chord_spans` 與可推論 notes 時拋出可讀錯誤。
- `test_write_chord_sidecar_defaults_to_artifact_dir`
  - 寫入 `<artifact_dir>/chords.json`。

## 3. CLI / E2E Tests

- `chord-detect --help` 顯示 artifact-first 子命令。
- `chord-detect <artifact_dir>` 輸出 `chords.json` 並列印 path。
- 缺少 `arrangement.json` 時 exit code 1 且 stderr 包含 chord detection error。

## 4. Viewer / Interface Tests

- `load_artifact_bundle` optional 載入 `chords.json`。
- `viewer.md` 包含 `## Chord Detection Sidecar`、backend、average confidence、chord progression。
- `interface.html` 包含 sidecar 區塊與 warning summary。

## 5. Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation --help
uv run guitar-tab-generation chord-detect --help
```
