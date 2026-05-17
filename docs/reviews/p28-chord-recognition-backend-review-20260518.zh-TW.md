# P28 Chord Recognition Backend Review

日期：2026-05-18
狀態：本地審查通過，外部 advisor 部分受阻

## 範圍

本次審查涵蓋：

- `docs/plans/p28-chord-recognition-backend-prd-20260518.md`
- `docs/plans/p28-chord-recognition-backend-test-spec-20260518.md`
- `src/guitar_tab_generation/chord_detection.py`
- `src/guitar_tab_generation/cli.py`
- `src/guitar_tab_generation/artifact_viewer.py`
- `src/guitar_tab_generation/artifact_interface.py`
- `tests/unit/test_chord_detection.py`
- `tests/e2e/test_cli_chord_detection.py`

## 審查結論

P28 的實作符合 artifact-first 與 default-safe 原則：

- `transcribe` default 沒有新增 GPU、模型下載或自動 sidecar 執行。
- `chord-detect` 從既有 artifact 讀取資料並寫入 `chords.json`。
- `viewer` / `interface` 只在 `chords.json` 為 object sidecar 時顯示 P28 區塊。
- 舊 `transcribe` 產生的 list 版 `chords.json` 保持相容，不會破壞既有 viewer/export/tutorial 流程。
- 低信心和弦會以 `LOW_CHORD_CONFIDENCE` warning 呈現。

## 已修正問題

### 舊格式 `chords.json` 相容性

全量測試最初失敗，原因是 P28 viewer loader 把既有 `transcribe` 輸出的 list 版 `chords.json` 視為新 sidecar object。

修正：

- `artifact_viewer` 新增 optional JSON object loader。
- list 版 `chords.json` 代表 legacy chord spans，P28 sidecar 顯示層會忽略它。
- object 版 `chords.json` 由 `chord-detect` 覆寫產生，才顯示 sidecar summary。

## 外部 advisor 狀態

- `gemini` binary 存在，但本輪執行 review 時停在瀏覽器登入提示，未產生可用審查內容。
- `claude-mm` binary 不存在。
- `claude` binary 存在，但本輪 review 回傳 API connection refused，未產生可用審查內容。

因此本階段以本地測試、手動 demo gate、相容性回歸與本文件作為 merge 前證據。P40 release hardening 時需再次嘗試外部 reviewer。

## 驗證證據

```bash
uv sync --group dev
uv run pytest tests/unit/test_chord_detection.py tests/e2e/test_cli_chord_detection.py tests/unit/test_artifact_viewer.py tests/unit/test_artifact_interface.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe --help
uv run guitar-tab-generation chord-detect --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p28-demo-20260517T1638
uv run guitar-tab-generation chord-detect /tmp/guitar-tab-p28-demo-20260517T1638
uv run guitar-tab-generation view /tmp/guitar-tab-p28-demo-20260517T1638
uv run guitar-tab-generation interface /tmp/guitar-tab-p28-demo-20260517T1638
```

結果：

- targeted tests：18 passed
- full regression：214 passed
- compileall：通過
- diff check：通過
- manual demo：產生 `chords.json`、`viewer.md`、`interface.html`

## 剩餘風險

- P28 的 note-derived chord inference 只是一個 deterministic baseline，不應視為真實音樂學辨識品質。
- P28 沒有把 `chords.json` 納入 `quality_report` 彙總；此整合可在 P35 evaluation 或 P40 hardening 補強。
- 外部 advisor review 本輪受工具登入 / binary 可用性阻塞。
