# P1 Test Spec：Audio Backend Adapter 架構

日期：2026-05-12  
對應 PRD：`docs/plans/p1-audio-backend-adapters-prd-20260512.md`

## 1. 測試目標

證明 pipeline 能透過 backend interface 取得 rhythm/chord/note/section，而不是硬綁 fixture metadata 或未來第三方套件。

## 2. Red Tests

先新增以下失敗測試：

1. `tests/unit/test_backend_contracts.py`
   - fake backend 回傳空 provenance 時 quality gate fail。
   - backend exception 會被包成清楚 domain error。
2. `tests/integration/test_pipeline_backend_selection.py`
   - default backend 為 fixture backend。
   - 指定不存在 backend 時 fail with clear message。
   - fixture backend output 與現有 schema 相容。

## 3. Contract Tests

每個 backend output 必須符合：

- 有 `confidence`。
- 有 `provenance.stage`。
- 有 `provenance.backend` 或等價 backend identifier。
- 低於 threshold 時 warning 不可缺漏。

## 4. Regression Tests

```bash
uv run pytest -q
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --out /tmp/guitar-tab-simple
```

預期：

- 既有 output files 仍存在。
- schema validator 仍通過。
- quality report 仍通過或有明確 warning。

## 5. Hard Fail

1. Fixture backend 不再 deterministic。
2. Pipeline 直接 import heavy dependency 作為必要條件。
3. Provenance 缺 backend/stage。
4. Optional backend 缺 dependency 時出現未處理 stack trace。
5. URL policy gate 行為被改變。

## 6. Executable Coverage（2026-05-13）

已新增並通過：

- `tests/unit/test_backend_contracts.py`
  - provenance 必須包含 `stage` 與 `backend`。
  - fixture backend 輸出 backend provenance。
  - backend 例外會包成 `BackendExecutionError`。
- `tests/integration/test_pipeline_backend_selection.py`
  - default pipeline 使用 fixture backend。
  - unknown backend 清楚失敗。
  - optional real backend placeholder 清楚拒絕。

驗證指令：

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --out /tmp/guitar-tab-p1-simple
```
