# P18 PR Code Review: Basic Pitch Local Backend MVP

Date: 2026-05-16
Branch: `feature/basic-pitch-backend`
Scope: Basic Pitch note transcription backend, optional uv `ai` dependency group, docs, tests.

## Review checklist

- Spec alignment: Pass. Implementation follows `docs/plans/p18-basic-pitch-local-backend-prd-20260516.md` and test spec.
- Dependency scope: Pass. Only `basic-pitch` and the compatibility pin `setuptools>=68,<81` were added to the optional `ai` group.
- Backend behavior: Pass. `fixture` remains the default deterministic backend; `basic-pitch` must be explicitly selected.
- Failure mode: Pass. Missing Basic Pitch raises a clear `BackendExecutionError`; there is no silent fallback to fixture.
- Provenance: Pass. Produced note events include `backend=basic-pitch`, model, runtime, stage, and stem metadata.
- GPU safety: Pass. Real smoke verification was run with `CUDA_VISIBLE_DEVICES=''`.
- Local hygiene: Pass. `.omx` is not tracked.

## Findings

No blocking findings.

## Verification evidence

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_basic_pitch_backend.py tests/integration/test_pipeline_backend_selection.py tests/e2e/test_cli_basic_pitch_backend.py tests/unit/test_ai_backends.py tests/unit/test_model_smoke.py` → 18 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 138 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed.
- `CUDA_VISIBLE_DEVICES='' UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-p18-basic-pitch-final` → wrote artifacts, 60 notes, `quality_status=passed`.
- `git diff --check` → passed.
- `git ls-files .omx` → no tracked files.

## Known limitations

- Basic Pitch is currently used only for note transcription; rhythm, chords, and sections remain on the existing safe local path.
- Basic Pitch uses TensorFlow runtime through its official Python package.
- `ruff` is not installed in the current project environment, so no new lint dependency was added during this phase.
