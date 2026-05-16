# P19 PR Code Review：Torch-first AI Backend Roadmap

日期：2026-05-16
分支：`feature/torch-first-backend-roadmap`
範圍：Torch-first route registry、readiness CLI、安全 smoke gate CLI、roadmap 文件、測試。

## Review checklist

- 規格對齊：通過。實作符合 `docs/plans/p19-torch-first-ai-backend-roadmap-prd-20260516.md` 與 test spec。
- Basic Pitch 相容性：通過。P19 沒有替換或改變 `basic-pitch` backend 行為。
- 依賴衛生：通過。沒有加入 PyTorch、Demucs、torchcrepe、transformers 或 checkpoint dependency。
- 資源 gate：通過。GPU-sensitive routes 有 gate，且保留 route-specific VRAM default。
- CLI 邊界：通過。`torch-backends` 只做 readiness 檢查；`torch-smoke` 只在明確 `--run` 時執行 smoke command。
- 文件：通過。已新增英文與繁中文件。
- 本機衛生：通過。`.omx` 沒有被追蹤。

## Architect review

第一次 architect review 要求修正：

1. `torchcrepe-f0` 文件與 registry 宣告 4GB VRAM，但 smoke gate 實際套用全域 12GB。
2. Torch smoke 內部/API 命名仍混用 download 語意。

已修正：

- Smoke gate 預設使用每條 route 自己的 VRAM 門檻；只有明確傳 `--min-free-vram-mb` / `GPU_MIN_FREE_MB` 時才 override。
- Torch smoke 改成 `run_smoke` / `smoke_enabled` 與 CLI `--run`，不再對 Torch smoke 暴露 `download_enabled`。

最終 architect verdict：APPROVE。

## 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py tests/unit/test_ai_backends.py tests/unit/test_model_smoke.py` → 19 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 148 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed，且列出 `torch-backends` / `torch-smoke`。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → `min_free_vram_mb=4000`，`smoke_enabled=false`。
- `git diff --check` → passed。
- `git ls-files .omx` → 無追蹤檔案。

## 已知限制

- P19 刻意不執行真實 Torch inference。
- P19 刻意不安裝 Torch heavy dependencies。
- MT3/YourMT3 仍是研究路線，需等具體 checkpoint 與 adapter 選定後才進 production。
