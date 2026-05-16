# P23 PR Code Review — Real torchcrepe Runtime Smoke（繁中）

日期：2026-05-16
分支：`feature/real-torchcrepe-smoke`
審查範圍：

- `src/guitar_tab_generation/torch_backends.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_torch_backends.py`
- `tests/e2e/test_cli_torch_backends.py`
- `docs/plans/p23-real-torchcrepe-runtime-smoke-prd-20260516.md`
- `docs/plans/p23-real-torchcrepe-runtime-smoke-test-spec-20260516.md`
- `docs/torch-optional-dependencies.md`
- `docs/torch-optional-dependencies.zh-TW.md`

## 結論

APPROVE。

## Findings

### Critical

無。

### High

無。

### Medium

無。

### Low

無。

## 架構評估

狀態：CLEAR。

實作將 torchcrepe 保持在明確 `--run` 與既有 optional `torch-ai` dependency group 後面。預設 `torch-smoke` 仍只做 plan，CPU 是預設 runtime device，CUDA 必須明確 GPU opt-in 後才會嘗試 runtime。短 smoke artifact 重用 P20 `write_f0_calibration()` sidecar path，沒有建立第二套 calibration contract。

## 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py tests/unit/test_torchcrepe_f0.py` → 21 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev` → default dev sync passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 169 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help` → passed，並顯示 `--device {cpu,cuda}`。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → safe planned smoke。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cuda --json` → 未 GPU opt-in 時安全 skip。
- `UV_CACHE_DIR=/tmp/uv-cache uv pip list | grep -E '^(torch|torchaudio|torchcodec|torchcrepe|demucs)\b' || true` → default dev environment 未安裝 Torch heavy packages。
- `git diff --check` → passed。
- Architect review 指出的 non-blocker 已修正：`GPU_TESTS_ENABLED=1` 時 CPU smoke 不再 probe GPU，並已用 targeted unit test 覆蓋。


- CPU real torchcrepe smoke 實跑成功，輸出 `f0_calibration.json`；`note_id=smoke-c4`、`status=calibrated`。
- P23 補入 `torchcodec>=0.12,<0.13` 到 `torch-ai` optional group，因 torchcrepe real audio loading 直接需要它；default dev sync 已驗證會移除 heavy packages。

## 剩餘風險

- 真實 torchcrepe CPU inference 是明確 opt-in manual gate，需要 `uv sync --group torch-ai`；default CI 以 injected fake runtime 測 artifact contract。
- CUDA wheel 與 driver compatibility 是環境相依，已放在 explicit GPU opt-in 後面。


