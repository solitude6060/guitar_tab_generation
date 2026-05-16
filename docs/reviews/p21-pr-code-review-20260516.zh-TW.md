# P21 PR Code Review：F0 Calibration Consumption

日期：2026-05-16
分支：`feature/f0-calibration-consumption`
範圍：viewer/interface/tutorial 消費 optional `f0_calibration.json`。

## Review checklist

- 規格對齊：通過。實作符合 P21 PRD / test spec。
- P20 相容性：通過。直接消費既有 `f0_calibration.json` schema；沒有改變 `f0-calibrate` sidecar 行為。
- 依賴衛生：通過。沒有 dependency 變更，也沒有新增 Torch heavy dependency。
- Missing artifact 行為：通過。沒有 `f0_calibration.json` 時，viewer/interface/tutorial 維持既有輸出。
- 使用者可見性：通過。使用者輸出會顯示 pitch-risk count、note id、delta semitones、periodicity confidence。
- 風險門檻：通過。`abs(delta_semitones) >= 0.5`、`periodicity_confidence < 0.5` 或 status 不是 `calibrated` 時會標記為 pitch risk。
- 本機衛生：通過。`.omx` 沒有被追蹤。

## Findings

沒有 blocking finding。

## 驗證證據

- `PYTHONPATH=src python3 -m pytest -q tests/unit/test_f0_calibration_consumption.py tests/e2e/test_cli_f0_calibration_consumption.py` → red/green cycle 後 5 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_f0_calibration_consumption.py tests/e2e/test_cli_f0_calibration_consumption.py tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py` → 12 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 160 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation view --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation interface --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation tutorial --help` → passed。
- `git diff --check` → passed。
- `git ls-files .omx` → 無追蹤檔案。

## 已知限制

- P21 只顯示 calibration risk，不重新計算 F0，也不修改 note events。
- 風險門檻目前是固定預設，後續階段可再做成設定。
