# P19 Test Spec：Torch-first AI Backend Roadmap 與 Smoke Gate

## Scope

驗證 P19 是否建立 Torch-first backend 抽象、模型路線狀態、GPU/CPU gate 與 CLI smoke plan，同時不安裝或執行 heavy Torch dependency。

## Red tests first

### Unit

`tests/unit/test_torch_backends.py`

- `test_torch_backend_routes_are_roadmap_only_and_local_first`
- `test_torch_backend_status_uses_injected_probes_without_importing_torch`
- `test_torch_smoke_gate_defaults_to_planned_and_never_uses_gpu`
- `test_torch_smoke_gate_enforces_vram_before_gpu_sensitive_route`
- `test_torch_backend_markdown_is_traditional_chinese`

### CLI / E2E

`tests/e2e/test_cli_torch_backends.py`

- `test_cli_torch_backends_outputs_traditional_chinese`
- `test_cli_torch_backends_json`
- `test_cli_torch_smoke_defaults_to_safe_plan`
- `test_cli_torch_smoke_rejects_unknown_route`

## Verification commands

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0
```

## Expected behavior

- `torch-backends` 只做 readiness probing，不 import heavy packages。
- `torch-smoke` 預設只輸出 plan，不下載、不跑 GPU。
- GPU-sensitive route 若 GPU 未允許或 VRAM 不足，結果為 `skipped` 而不是硬失敗。
- `fixture` 與 `basic-pitch` 行為不被修改。
