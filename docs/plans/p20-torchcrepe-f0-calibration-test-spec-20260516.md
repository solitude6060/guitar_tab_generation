# P20 Test Spec：torchcrepe F0 Calibration Adapter

## Scope

驗證 P20 是否建立 artifact-first 的 torchcrepe F0 calibration adapter / CLI，並維持 Basic Pitch 與 fixture 行為不變。

## Red tests first

### Unit

`tests/unit/test_torchcrepe_f0.py`

- `test_torchcrepe_calibrator_requires_runtime`
- `test_torchcrepe_calibrator_maps_pitch_frames_to_notes`
- `test_torchcrepe_calibrator_uses_cpu_by_default`
- `test_write_f0_calibration_requires_artifact_files`

### CLI / E2E

`tests/e2e/test_cli_f0_calibrate.py`

- `test_cli_f0_calibrate_writes_artifact_with_stub_runtime`
- `test_cli_f0_calibrate_returns_error_when_runtime_missing`

## Verification commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate --help
```

## Expected behavior

- `f0-calibrate` 預設 device 為 `cpu`。
- fake runtime 測試不需要安裝 torchcrepe。
- 未安裝 torchcrepe 時命令失敗且錯誤清楚。
- `transcribe --backend basic-pitch` 與 `fixture` 不受影響。
