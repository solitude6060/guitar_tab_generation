# P20 PR Code Review: torchcrepe F0 Calibration Adapter

Date: 2026-05-16
Branch: `feature/torchcrepe-f0-calibration`
Scope: artifact-first `f0-calibrate` CLI, optional torchcrepe runtime boundary, docs, tests.

## Review checklist

- Spec alignment: Pass. Implementation follows `docs/plans/p20-torchcrepe-f0-calibration-prd-20260516.md` and test spec.
- Basic Pitch compatibility: Pass. P20 does not replace or alter `basic-pitch` backend behavior.
- Default backend safety: Pass. `fixture` remains default; `f0-calibrate` is a separate artifact command.
- Dependency hygiene: Pass. No PyTorch / torchcrepe dependency was added to default or optional dependency groups in this phase.
- Runtime boundary: Pass. `torchcrepe` is lazy-imported only when `f0-calibrate` runs.
- GPU safety: Pass. CLI default device is `cpu`; GPU requires explicit `--device cuda:0` or equivalent.
- Failure mode: Pass. Missing torchcrepe returns a clear `BackendExecutionError`; no silent fallback or fake output.
- Documentation: Pass. English and Traditional Chinese usage docs were added.
- Local hygiene: Pass. `.omx` is not tracked.

## Findings

No blocking findings.

## Verification evidence

- `PYTHONPATH=src python3 -m pytest -q tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py` → 7 passed during red/green cycle.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py` → 17 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 155 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate --help` → passed.
- Missing runtime manual gate: artifact with `audio_normalized.wav` and `notes.json` exits 1 with clear torchcrepe optional runtime message.
- `git diff --check` → passed.
- `git ls-files .omx` → no tracked files.

## Known limitations

- P20 intentionally does not install torchcrepe or run real torchcrepe inference.
- F0 calibration is best suited for solo/riff passages; it is not polyphonic transcription.
- Output is a sidecar artifact and is not yet consumed by renderer/tutorial scoring.
