# P19 PR Code Review: Torch-first AI Backend Roadmap

Date: 2026-05-16
Branch: `feature/torch-first-backend-roadmap`
Scope: Torch-first route registry, readiness CLI, safe smoke gate CLI, roadmap docs, tests.

## Review checklist

- Spec alignment: Pass. Implementation follows `docs/plans/p19-torch-first-ai-backend-roadmap-prd-20260516.md` and test spec.
- Basic Pitch compatibility: Pass. P19 does not replace or alter `basic-pitch` backend behavior.
- Dependency hygiene: Pass. No PyTorch, Demucs, torchcrepe, transformers, or checkpoint dependency was added.
- Resource gate: Pass. GPU-sensitive routes are gated; route-specific VRAM defaults are preserved.
- CLI boundary: Pass. `torch-backends` inspects readiness; `torch-smoke` plans or runs smoke commands only when explicitly requested via `--run`.
- Documentation: Pass. English and Traditional Chinese roadmap docs were added.
- Local hygiene: Pass. `.omx` is not tracked.

## Architect review

Initial architect review requested changes for:

1. `torchcrepe-f0` VRAM gate was using a global 12GB minimum despite the route declaring 4GB.
2. Torch smoke internal/API names still used download terminology.

Fixes applied:

- Smoke gate now uses route-specific VRAM by default and only overrides when `--min-free-vram-mb` / `GPU_MIN_FREE_MB` is explicitly set.
- Torch smoke now uses `run_smoke` / `smoke_enabled` and CLI `--run`; no Torch-specific `download_enabled` field remains.

Final architect verdict: APPROVE.

## Verification evidence

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py tests/unit/test_ai_backends.py tests/unit/test_model_smoke.py` → 19 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 148 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed and lists `torch-backends` / `torch-smoke`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json` → `min_free_vram_mb=4000`, `smoke_enabled=false`.
- `git diff --check` → passed.
- `git ls-files .omx` → no tracked files.

## Known limitations

- P19 intentionally does not run real Torch inference.
- P19 intentionally does not install Torch heavy dependencies.
- MT3/YourMT3 remains a research route until a concrete checkpoint and adapter are selected.
