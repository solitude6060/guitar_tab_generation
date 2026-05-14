# P11 PR 程式碼審查 — 3–8 分鐘完整歌曲支援

## 審查範圍

- `src/guitar_tab_generation/input_adapter.py`
- `src/guitar_tab_generation/pipeline.py`
- `src/guitar_tab_generation/renderer.py`
- `src/guitar_tab_generation/ai_runtime.py`
- `src/guitar_tab_generation/contracts.py`
- `tests/test_input_policy.py`
- `tests/e2e/test_cli_full_song_length.py`
- `tests/support/contract_validators.py`
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

- 目前 deterministic backend 對完整歌曲仍產生 sketch placeholder notes。這符合 P11 範圍，因為本階段目標是輸入契約與 artifact 排程，不是完整 production transcription accuracy。後續 AI backend phase 必須消費 `source.processing_plan`。

## 驗證證據

- Red tests first：
  - `uv run pytest -q tests/test_input_policy.py tests/e2e/test_cli_full_song_length.py`
  - 實作前結果：5 failed / 1 passed。
- 目標測試：
  - `uv run pytest -q tests/test_input_policy.py tests/e2e/test_cli_full_song_length.py`
  - 結果：6 passed。
- 完整回歸：
  - `uv run pytest -q`
  - 結果：100 passed。
- CLI smoke：
  - `uv run guitar-tab-generation --help`
  - `uv run guitar-tab-generation transcribe --help`
  - `uv run guitar-tab-generation ai-resources | grep -E '3–8|60 秒 chunk|MiniMax'`
- 手動完整歌曲 smoke：
  - 產生 `/tmp/guitar-tab-p11-full-song.wav`，長度 180 秒。
  - `uv run guitar-tab-generation transcribe /tmp/guitar-tab-p11-full-song.wav --backend fixture --out /tmp/guitar-tab-p11-full-song`
  - 已驗證 artifact source metadata：`full_song chunked_full_song 180.0`。
- 空白檢查：
  - `git diff --check`
  - 結果：clean。

## 合併建議

完成 hygiene checks 後，將 `feature/full-song-length-support` 合併到 `dev`：

- `.omx/` 維持未追蹤。
- Commit message 不包含 `Co-authored-by: OmX`。
