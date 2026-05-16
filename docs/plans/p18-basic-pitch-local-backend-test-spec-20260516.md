# P18 Test Spec：Basic Pitch Local Backend MVP

## Scope

驗證第一個真實本機 AI backend 是否已成功接入 pipeline，並且不破壞既有 `fixture` 路徑。

## Red tests first

### Unit

1. `tests/unit/test_basic_pitch_backend.py`
   - `test_basic_pitch_backend_requires_installed_package`
   - `test_basic_pitch_backend_translates_prediction_to_note_events`
   - `test_basic_pitch_backend_requires_audio_path`

2. `tests/integration/test_pipeline_backend_selection.py`
   - 新增 `test_basic_pitch_backend_can_be_resolved_when_available`
   - 新增 `test_pipeline_passes_normalized_audio_path_to_basic_pitch_backend`

### CLI / E2E

1. `tests/e2e/test_cli_basic_pitch_backend.py`
   - 以 monkeypatch/stub 避免真實重推論，但驗證 CLI 能跑 `--backend basic-pitch`
   - 驗證 `arrangement.json` 的 note provenance 為 `basic-pitch`

## Expected behavior

- `fixture` 預設行為不變。
- `basic-pitch` 在有安裝時可被 resolve。
- `basic-pitch` 未安裝時回傳清楚錯誤，不 silent fallback。
- prediction 結果會被轉成既有 `note_events` contract。

## Verification commands

```bash
uv run pytest -q tests/unit/test_basic_pitch_backend.py tests/integration/test_pipeline_backend_selection.py tests/e2e/test_cli_basic_pitch_backend.py
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-p18-basic-pitch
```
