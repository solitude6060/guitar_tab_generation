# P29 Section Detection Sidecar Test Spec

日期：2026-05-18
狀態：Planned

## 1. 測試策略

P29 只使用 deterministic artifact input，不下載模型、不跑 GPU、不呼叫網路。

## 2. Unit Tests

- `test_build_section_sidecar_from_arrangement_section_spans`
  - 驗證 schema、backend、summary、sections、provenance。
- `test_build_section_sidecar_warns_on_low_confidence`
  - 驗證 `LOW_SECTION_CONFIDENCE` warning。
- `test_build_section_sidecar_falls_back_to_chord_window`
  - 缺少 sections 時，用 chord/chords sidecar window 產生 fallback section。
- `test_build_section_sidecar_rejects_missing_inputs`
  - 缺少 sections/chords/notes 時拋出可讀錯誤。
- `test_write_section_sidecar_defaults_to_artifact_dir`
  - 寫入 `<artifact_dir>/sections.json`。

## 3. CLI / E2E Tests

- `section-detect --help` 顯示 artifact_dir / --out。
- `section-detect <artifact_dir>` 輸出 object 版 `sections.json`。
- 缺少 `arrangement.json` 時 exit code 1 且 stderr 包含 section detection error。

## 4. Viewer / Interface Tests

- `load_artifact_bundle` optional 載入 object 版 `sections.json`。
- 舊 list 版 `sections.json` 被視為 legacy pipeline artifact，不顯示 sidecar 區塊。
- `viewer.md` 包含 `## Section Detection Sidecar`、backend、section count、average confidence。
- `interface.html` 包含 sidecar 區塊與 warning summary。

## 5. Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation --help
uv run guitar-tab-generation section-detect --help
```
