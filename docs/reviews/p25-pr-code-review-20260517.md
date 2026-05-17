# P25 PR Code Review — Demucs Stem Separation Sidecar

Date: 2026-05-17
Branch: `feature/demucs-stem-sidecar`
Scope reviewed:

- `src/guitar_tab_generation/stem_separation.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_stem_separation.py`
- `tests/e2e/test_cli_separate_stems.py`
- `docs/plans/p25-demucs-stem-sidecar-prd-20260517.md`
- `docs/plans/p25-demucs-stem-sidecar-test-spec-20260517.md`
- `docs/plans/p26-stem-aware-basic-pitch-prd-20260517.md`
- `docs/plans/p26-stem-aware-basic-pitch-test-spec-20260517.md`
- `docs/plans/post-p25-execution-plan-20260517.md`
- `docs/plans/remaining-feature-master-plan-20260516.md`

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

The implementation keeps Demucs in an artifact-first sidecar instead of changing `transcribe`. `separate-stems` requires an existing `audio_normalized.wav`, checks the P24 Demucs runtime gate before runtime execution, writes `stems/` plus `stem_manifest.json`, and records no silent fallback. CPU is the default path; CUDA requires explicit opt-in. A final architect review found one blocker where ambient `GPU_TESTS_ENABLED=1` could still make the P24 gate probe GPU during CPU runs. That was fixed by sanitizing the gate environment for CPU mode and adding a regression that uses the real P24 gate with injected probes.

P26 planning is correctly separated from the P25 implementation: stem-aware Basic Pitch is planned as `transcribe-stem <artifact_dir> --backend basic-pitch --stem <name>`, with `stem_notes/<stem>.notes.json` output and no automatic merge into primary artifacts.

## Verification evidence

- `UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 188 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_stem_separation.py tests/e2e/test_cli_separate_stems.py` → 11 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed and lists `separate-stems`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems --help` → passed and exposes `--device`, `--allow-gpu`, and `--min-free-vram-mb`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe --help` → passed; `fixture` remains default and no stem option is present.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation demucs-gate --json` → safe planned gate; `gpu_enabled=false`, `command_executed=false`.
- `git log --format=%B HEAD` hygiene check → exact forbidden OmX coauthor phrase absent after commit-message amend.
- `git ls-files .omx` hygiene check → no tracked `.omx` files.

## Residual risks

- Real Demucs source separation was intentionally not executed in default gates. P25 validates the sidecar contract with fake runtime and P24 gate reuse only.
- The real Demucs CLI output layout remains environment-sensitive; the adapter expects `<output>/<model>/<audio-stem>/*.wav`.
- P26 must not merge stem notes into primary `notes.json` until P27 defines quality reconciliation.
