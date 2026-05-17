# P26 PR Code Review

日期：2026-05-17
PR：#9 `feature/stem-aware-basic-pitch` → `dev`
結論：APPROVED

## 審查範圍

- `src/guitar_tab_generation/basic_pitch_backend.py`
- `src/guitar_tab_generation/stem_notes.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_basic_pitch_backend.py`
- `tests/unit/test_stem_manifest_reader.py`
- `tests/e2e/test_cli_transcribe_stem.py`

## 發現與修正

### Blocker：stem name path traversal

初次審查發現 `stem_manifest.json` / `--stem` 的 stem name 會直接組成 `stem_notes/<stem>.notes.json`，若 manifest stem name 為 `../leak`，可能把 sidecar 寫出 `stem_notes/`。

修正：

- 在 `stem_notes.py` 加入 stem name allowlist，只允許英數、`.`、`_`、`-`，並拒絕 `.` / `..`。
- 寫入前確認 notes 與 metadata path 都留在 `stem_notes/` 內。
- 新增 regression tests，確認 unsafe stem name 會在載入 Basic Pitch runtime 前失敗，且不寫出檔案。

## 驗證

- `uv run pytest tests/unit/test_stem_manifest_reader.py tests/unit/test_basic_pitch_backend.py tests/e2e/test_cli_transcribe_stem.py -q`：15 passed
- `uv run pytest -q`：200 passed
- `uv run python -m compileall -q src tests`：passed
- `git diff --check`：passed
- PR checks：CI passed

## 結論

P26 滿足 PRD/test spec：新增 `transcribe-stem` sidecar、讀取 P25 `stem_manifest.json`、輸出 `stem_notes/<stem>.notes.json` 與 metadata、保留 stem provenance、不改 `transcribe` default、不 silent fallback 到 mix，且 default tests 不執行真實 Demucs 或真實 Basic Pitch runtime。
