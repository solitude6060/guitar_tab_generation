# P29 Section Detection Sidecar Review

日期：2026-05-18
狀態：本地審查通過，外部 advisor 受阻延後

## 範圍

本次審查涵蓋：

- `docs/plans/p29-section-detection-sidecar-prd-20260518.md`
- `docs/plans/p29-section-detection-sidecar-test-spec-20260518.md`
- `src/guitar_tab_generation/section_sidecar.py`
- `src/guitar_tab_generation/cli.py`
- `src/guitar_tab_generation/artifact_viewer.py`
- `src/guitar_tab_generation/artifact_interface.py`
- `tests/unit/test_section_detection_sidecar.py`
- `tests/e2e/test_cli_section_detection.py`
- `tests/unit/test_artifact_viewer.py`

## 審查結論

P29 符合 artifact-first 與 default-safe 原則：

- 新增 `section-detect <artifact_dir>`，不改 `transcribe` default。
- `sections.json` object sidecar 保留 schema、backend、source、summary、provenance、warnings。
- 低信心 section 使用 `LOW_SECTION_CONFIDENCE` warning。
- 沒有新增模型、GPU、網路或外部依賴。
- viewer / interface 只在 `sections.json` 為 object sidecar 時顯示 P29 summary。
- 既有 `transcribe` 產生的 list 版 `sections.json` 保持相容，不破壞既有 viewer/export/tutorial 流程。

## 已驗證的風險點

- 既有 pipeline 早已輸出 list 版 `sections.json`；P29 loader 明確忽略 legacy list，不把它誤判為 sidecar object。
- 缺少 `section_spans` 時，fallback 會依序使用 `chords.json` object sidecar、`arrangement.chord_spans`、`arrangement.note_events`，且 provenance 指明來源。
- section sidecar 只覆寫使用者明確執行 `section-detect` 的輸出，不會在 `transcribe` 中自動執行。

## 外部 advisor 狀態

P28 同輪已嘗試 `gemini` 與 `claude`：

- `gemini` 停在瀏覽器登入提示。
- `claude-mm` binary 不存在。
- `claude` 回傳 API connection refused。

因此 P29 未重複卡住的外部 review；P40 release hardening 時需重新嘗試外部 reviewer。

## 驗證證據

```bash
uv run pytest tests/unit/test_section_detection_sidecar.py tests/e2e/test_cli_section_detection.py tests/unit/test_artifact_viewer.py tests/unit/test_artifact_interface.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation section-detect --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p29-demo-20260517T1658
uv run guitar-tab-generation section-detect /tmp/guitar-tab-p29-demo-20260517T1658
uv run guitar-tab-generation view /tmp/guitar-tab-p29-demo-20260517T1658
uv run guitar-tab-generation interface /tmp/guitar-tab-p29-demo-20260517T1658
```

結果：

- targeted tests：21 passed
- full regression：225 passed
- compileall：通過
- diff check：通過
- manual demo：產生 object 版 `sections.json`，viewer/interface 均顯示 sidecar summary

## 剩餘風險

- deterministic fallback 只提供 MVP 結構化 sidecar，不代表真實音樂段落辨識品質。
- P35 evaluation 前尚未量化 section boundary 準確度。
