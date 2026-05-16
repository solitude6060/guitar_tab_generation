# P22 PR Code Review — Optional Torch Dependency Group（繁中）

日期：2026-05-16
分支：`feature/optional-torch-deps`
審查範圍：

- `pyproject.toml`
- `uv.lock`
- `src/guitar_tab_generation/torch_backends.py`
- `tests/test_torch_dependency_group_contract.py`
- `tests/unit/test_torch_backends.py`
- `docs/plans/p22-optional-torch-dependency-group-prd-20260516.md`
- `docs/plans/p22-optional-torch-dependency-group-test-spec-20260516.md`
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

本變更將 Torch 保持為 opt-in dependency group，沒有改變 default backend selection、Basic Pitch 行為或 `torch-smoke` 的安全預設。CUDA wheel selection 只文件化、不硬寫進 `pyproject.toml`，避免把單一 GPU 平台路徑強加到所有使用者環境。

## 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/test_torch_dependency_group_contract.py tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py` → 13 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev` → 只同步/稽核 default dev environment。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 163 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → safe planned smoke，未執行 heavy command。
- `UV_CACHE_DIR=/tmp/uv-cache uv pip list | grep -E '^(torch|torchaudio|torchcrepe|demucs)\b' || true` → default dev environment 未安裝 Torch heavy packages。
- `git diff --check` → passed。

## 剩餘風險

- `torch-ai` group 已 lock，但刻意不在 CI/default dev 安裝。真實 torchcrepe runtime smoke 留到 P23。
- GPU/CUDA wheel compatibility 必須在 opt-in environment 驗證，不在 P22 驗證。
