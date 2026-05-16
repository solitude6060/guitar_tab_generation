# P21 PR Code Review: F0 Calibration Consumption

Date: 2026-05-16
Branch: `feature/f0-calibration-consumption`
Scope: viewer/interface/tutorial consumption of optional `f0_calibration.json`.

## Review checklist

- Spec alignment: Pass. Implementation follows P21 PRD/test spec.
- P20 compatibility: Pass. `f0_calibration.json` schema is consumed as-is; `f0-calibrate` sidecar behavior is not changed.
- Dependency hygiene: Pass. No dependency changes; no heavy Torch dependency added.
- Missing artifact behavior: Pass. Viewer/interface/tutorial preserve existing output when `f0_calibration.json` is absent.
- User visibility: Pass. Pitch-risk count, note id, delta semitones, and periodicity confidence are visible in user-facing outputs.
- Risk threshold: Pass. Notes are flagged when `abs(delta_semitones) >= 0.5`, `periodicity_confidence < 0.5`, or calibration status is not `calibrated`.
- Local hygiene: Pass. `.omx` is not tracked.

## Findings

No blocking findings.

## Verification evidence

- `PYTHONPATH=src python3 -m pytest -q tests/unit/test_f0_calibration_consumption.py tests/e2e/test_cli_f0_calibration_consumption.py` → 5 passed during red/green cycle.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_f0_calibration_consumption.py tests/e2e/test_cli_f0_calibration_consumption.py tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py` → 12 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 160 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation view --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation interface --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation tutorial --help` → passed.
- `git diff --check` → passed.
- `git ls-files .omx` → no tracked files.

## Known limitations

- P21 displays calibration risk; it does not recompute F0 or alter note events.
- Risk thresholds are fixed defaults for now and can be made configurable in a later phase.
