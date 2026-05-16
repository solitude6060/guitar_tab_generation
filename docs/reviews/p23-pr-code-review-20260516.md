# P23 PR Code Review — Real torchcrepe Runtime Smoke

Date: 2026-05-16
Branch: `feature/real-torchcrepe-smoke`
Scope reviewed:

- `src/guitar_tab_generation/torch_backends.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_torch_backends.py`
- `tests/e2e/test_cli_torch_backends.py`
- `docs/plans/p23-real-torchcrepe-runtime-smoke-prd-20260516.md`
- `docs/plans/p23-real-torchcrepe-runtime-smoke-test-spec-20260516.md`
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

The implementation keeps torchcrepe behind explicit `--run` and the existing optional `torch-ai` dependency group. Default `torch-smoke` remains a planner, CPU is the default runtime device, and CUDA requires explicit GPU opt-in before any runtime work is attempted. The tiny smoke artifact reuses the existing P20 `write_f0_calibration()` sidecar path instead of introducing a parallel calibration contract.

## Verification evidence

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py tests/unit/test_torchcrepe_f0.py` → 21 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev` → default dev sync passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 169 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help` → passed and exposes `--device {cpu,cuda}`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → safe planned smoke.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cuda --json` → skipped safely without GPU opt-in.
- `UV_CACHE_DIR=/tmp/uv-cache uv pip list | grep -E '^(torch|torchaudio|torchcodec|torchcrepe|demucs)\b' || true` → no Torch heavy packages installed in default dev environment.
- `git diff --check` → passed.
- Architect review noted and fixed non-blocker: CPU smoke no longer probes GPU when `GPU_TESTS_ENABLED=1`; covered by targeted unit test.


- CPU real torchcrepe smoke completed successfully and wrote `f0_calibration.json`; `note_id=smoke-c4`, `status=calibrated`.
- P23 adds `torchcodec>=0.12,<0.13` to the optional `torch-ai` group because torchcrepe real audio loading directly requires it; default dev sync was verified to remove heavy packages.

## Residual risks

- Real torchcrepe CPU inference is intentionally an opt-in manual gate requiring `uv sync --group torch-ai`; default CI uses injected fake runtime tests for the artifact contract.
- CUDA wheel and driver compatibility remain environment-specific and are guarded behind explicit GPU opt-in.


