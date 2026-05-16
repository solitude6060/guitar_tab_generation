# P23 Test Spec：Real torchcrepe Runtime Smoke

日期：2026-05-16

## 1. Red tests

更新/新增測試：

- `tests/unit/test_torch_backends.py`
  - `run_torchcrepe_f0_runtime_smoke()` 使用 fake runtime 時會建立短 fixture artifact 與 `f0_calibration.json`。
  - `build_torch_backend_smoke_gate(... route=torchcrepe-f0, run_smoke=True ...)` 使用 injected runtime 時不走 subprocess，會輸出 calibration path。
  - `torch_device="cuda"` 但沒有 GPU opt-in 時 skip，不執行 runtime。
- `tests/e2e/test_cli_torch_backends.py`
  - `torch-smoke --help` 顯示 `--device {cpu,cuda}`。
  - `torch-smoke --route torchcrepe-f0 --run --device cuda --json` 在沒有 GPU opt-in 時安全 skip。

## 2. Green implementation

- `src/guitar_tab_generation/torch_backends.py`
  - 新增 tiny C4 WAV fixture 產生器。
  - 新增 `run_torchcrepe_f0_runtime_smoke()`，重用 P20 `write_f0_calibration()`。
  - `build_torch_backend_smoke_gate()` 對 `torchcrepe-f0` route 執行 real runtime smoke，其他 route 保持既有 command runner。
  - 保持 lazy import：未 `--run` 時不 import torch/torchcrepe。
- `src/guitar_tab_generation/cli.py`
  - `torch-smoke` 新增 `--device {cpu,cuda}`。

## 3. Verification gates

必要 gate：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py tests/unit/test_torchcrepe_f0.py
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cuda --json
```

Manual opt-in gate（不納入 default CI）：

```bash
uv sync --group torch-ai
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cpu --json
```

Optional GPU gate（只在共享 GPU 資源允許時）：

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cuda --allow-gpu --min-free-vram-mb 4000 --json
```

## 4. 不驗證項目

- 不在 default CI 執行 real torchcrepe inference。
- 不驗證 CUDA wheel compatibility。
- 不驗證 pitch accuracy，只驗證 artifact sidecar contract 與 runtime path。


## P23 實跑補充

CPU real smoke 實跑時，torchcrepe audio loader 在目前 PyTorch runtime 需要 `torchcodec`。因此 P23 將 `torchcodec>=0.12,<0.13` 加入 `torch-ai` optional group；default dev/CI 仍不安裝。
