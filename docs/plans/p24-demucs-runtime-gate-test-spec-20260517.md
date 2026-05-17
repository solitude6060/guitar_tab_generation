# P24 Test Spec：Demucs Runtime Planning + Install Gate

日期：2026-05-17

## 1. Red tests

新增測試：

- `tests/unit/test_demucs_runtime_gate.py`
  - `build_demucs_runtime_gate()` 預設為 planned，不執行 command、不啟用 GPU、不下載模型。
  - missing Demucs runtime 在 `check_runtime=True` 時回傳 failed，reason 包含 `Demucs optional runtime is not installed` 與 `uv sync --group torch-ai`。
  - GPU opt-in 但 free VRAM 低於 12000 MB 時 skip，且不執行 Demucs command。
  - runtime command 回傳非 0 時 failed，且 `fallback_policy` 為 `no_silent_fallback`。
  - gate payload 固定包含 `model_name=htdemucs`、`cache_dir`、`model_cache_dir`。
- `tests/e2e/test_cli_demucs_gate.py`
  - `demucs-gate --help` 顯示 `--check-runtime`、`--allow-gpu`、`--min-free-vram-mb`。
  - `demucs-gate --json` 預設安全 planned。
  - `transcribe --help` 仍顯示 fixture default，沒有 Demucs/stem 預設。

## 2. Green implementation

- 新增 `src/guitar_tab_generation/demucs_runtime.py`。
- 新增 `guitar-tab-generation demucs-gate` CLI。
- Demucs runtime gate 只做 install/runtime readiness 與 GPU/cache planning：
  - 不呼叫 stem separation。
  - 不下載 model。
  - 不寫 stems artifact。
  - 不改 pipeline/transcribe。

## 3. Verification gates

必要 gate：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_demucs_runtime_gate.py tests/e2e/test_cli_demucs_gate.py tests/unit/test_torch_backends.py
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation demucs-gate --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation demucs-gate --json
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe --help
```

## 4. 不驗證項目

- 不執行真實 Demucs separation。
- 不下載 Demucs model weights。
- 不驗證 stem quality。
- 不驗證 CUDA wheel compatibility。
