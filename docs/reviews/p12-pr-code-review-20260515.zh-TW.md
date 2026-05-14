# P12 PR 程式碼審查 — FFmpeg 本機音訊 Ingest

## 審查範圍

- `src/guitar_tab_generation/input_adapter.py`
- `src/guitar_tab_generation/audio_preprocess.py`
- `src/guitar_tab_generation/cli.py`
- `src/guitar_tab_generation/ai_runtime.py`
- `tests/test_input_policy.py`
- `tests/unit/test_audio_preprocess_ffmpeg.py`
- `tests/e2e/test_cli_non_wav_ingest.py`
- README / 使用規範 / planning 文件

## 結論

**通過，可合併** — 沒有 blocking issue。

## 發現

### Critical

- 無。

### High

- 無。

### Medium

- 無。

### Low / 觀察項目

- 非 WAV ingest 需要本機系統工具 `ffmpeg` / `ffprobe`。這可接受，因為專案已有 local runtime doctor，且 P12 會回報可行動的本機工具錯誤，不新增 Python media dependency。
- WAV fixture normalization 仍保留 Python `wave` deterministic path。這是刻意設計，讓 CI 與 golden fixtures 保持快速且不強制依賴 ffmpeg。

## 驗證證據

- Red test evidence：
  - `uv run pytest -q tests/test_input_policy.py tests/unit/test_audio_preprocess_ffmpeg.py tests/e2e/test_cli_non_wav_ingest.py`
  - 實作前結果：缺少 `AudioPreprocessError` 的 collection error。
- 目標測試：
  - `uv run pytest -q tests/test_input_policy.py tests/unit/test_audio_preprocess_ffmpeg.py tests/e2e/test_cli_non_wav_ingest.py`
  - 結果：10 passed。
- 完整回歸：
  - `uv run pytest -q`
  - 結果：105 passed。
- 本機真實工具 smoke：
  - 產生 `/tmp/guitar-tab-p12-source.flac`。
  - `uv run guitar-tab-generation transcribe /tmp/guitar-tab-p12-source.flac --backend fixture --out /tmp/guitar-tab-p12-flac`
  - 已驗證：`full_song 180.0 chunked_full_song`；`audio_normalized.wav` 存在。

## 合併建議

完成最後 CLI 與 hygiene checks 後，將 `feature/ffmpeg-local-audio-ingest` 合併到 `dev`。
