# P13 PR Code Review — Local AI Backend Registry

## Review scope

- `src/guitar_tab_generation/ai_backends.py`
- `src/guitar_tab_generation/ai_runtime.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_ai_backends.py`
- `tests/test_ai_backends_cli.py`
- README / usage guardrail / planning docs

## Verdict

**APPROVE** — no blocking issues found.

## Findings

### Critical

- None.

### High

- None.

### Medium

- None.

### Low / watchlist

- Registry status is intentionally diagnostic only. Future backend phases must
  still add separate ADRs/tests before installing heavy dependencies or running
  inference.
- Availability is based on command/import presence, not model health. That is
  sufficient for P13 and avoids importing heavy libraries in CI.

## Evidence

- Red test evidence:
  - `uv run pytest -q tests/unit/test_ai_backends.py tests/test_ai_backends_cli.py`
  - Initial result: missing `guitar_tab_generation.ai_backends`.
- Target tests:
  - `uv run pytest -q tests/unit/test_ai_backends.py tests/test_ai_backends_cli.py`
  - Result: 6 passed.

## Merge recommendation

Merge after full regression, CLI help gates, and hygiene checks.
