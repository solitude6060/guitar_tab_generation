# P25 Test Spec：Demucs Stem Separation Sidecar

日期：2026-05-17
狀態：Implemented

## Unit tests

- `tests/unit/test_stem_separation.py`
  - fake runtime 成功時，`write_stem_separation()` 產生 `stems/` 與 `stem_manifest.json`。
  - manifest 包含 `backend=demucs-htdemucs`、`model_name=htdemucs`、`source_audio=audio_normalized.wav`、`fallback_used=false`。
  - 預設 gate 不啟用 GPU、不下載、不執行 runtime check 之外的隱性 fallback。
  - `device=cuda` 但未 opt-in GPU 時回傳清楚錯誤。
  - 缺少 `audio_normalized.wav` 時回傳清楚錯誤。

## E2E tests

- `tests/e2e/test_cli_separate_stems.py`
  - `separate-stems --help` 顯示 `--device`、`--allow-gpu`、`--min-free-vram-mb`。
  - 透過 monkeypatched fake runtime loader 呼叫 CLI，確認產物存在且 JSON contract 可解析。
  - `transcribe --help` 保持 fixture default，沒有 `--stem` 或 Demucs default。

## Manual demo gate

使用 fixture backend 先建立 artifact，再以 fake runtime path 的 unit/e2e 覆蓋 sidecar contract。P25 不執行真實 Demucs manual separation。

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p25
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems /tmp/guitar-tab-p25 --help
```

## Regression gates

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation demucs-gate --json
```
