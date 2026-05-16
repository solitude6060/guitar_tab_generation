# P22 PR Code Review — Optional Torch Dependency Group

Date: 2026-05-16
Branch: `feature/optional-torch-deps`
Scope reviewed:

- `pyproject.toml`
- `uv.lock`
- `src/guitar_tab_generation/torch_backends.py`
- `tests/test_torch_dependency_group_contract.py`
- `tests/unit/test_torch_backends.py`
- `docs/plans/p22-optional-torch-dependency-group-prd-20260516.md`
- `docs/plans/p22-optional-torch-dependency-group-test-spec-20260516.md`
- `docs/torch-optional-dependencies.md`
- `docs/torch-optional-dependencies.zh-TW.md`

## Verdict

APPROVE.

## Findings

### Critical

None.

### High

None.

### Medium

None.

### Low

None.

## Architecture assessment

Status: CLEAR.

The change keeps Torch as an opt-in dependency group and does not alter default backend selection, Basic Pitch behavior, or `torch-smoke` safe defaults. CUDA wheel selection is intentionally documented instead of hard-coded in `pyproject.toml`, which avoids forcing one GPU platform path on all users.

## Verification evidence

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/test_torch_dependency_group_contract.py tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py` → 13 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev` → resolved/audited default dev environment only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 163 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → safe planned smoke, no command execution.
- `UV_CACHE_DIR=/tmp/uv-cache uv pip list | grep -E '^(torch|torchaudio|torchcrepe|demucs)\b' || true` → no Torch heavy packages installed in default dev environment.
- `git diff --check` → passed.

## Residual risks

- The `torch-ai` group is locked but intentionally not installed in CI/default dev. Real torchcrepe runtime smoke remains P23.
- GPU/CUDA wheel compatibility must be validated in the opt-in environment, not in P22.
