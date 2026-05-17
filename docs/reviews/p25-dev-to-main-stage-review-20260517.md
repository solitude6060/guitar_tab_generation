# P25 Dev-to-Main Stage Review — Demucs Stem Separation Sidecar

Date: 2026-05-17
Source branch: `dev`
Target branch: `main`
Scope:

- PR #8 merge commit on `dev`: `03e4b1b77e0094a9e46840524b22b9695f5097b9`
- P25 `separate-stems` sidecar implementation
- P26/P26-P31 follow-up planning docs
- P25 review artifacts

## Verdict

APPROVE for merge to `main`.

## Stage checks

- PR #8 is merged into `dev`.
- Local `dev` is synchronized with `origin/dev`.
- `main..dev` contains the P25 merge and no unrelated work.
- `.omx` is not tracked.
- The exact forbidden OmX coauthor phrase is absent from branch history.

## Verification evidence on `dev`

- `UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 188 passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems --help` → passed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed.
- `git diff --check HEAD` → passed.

## Residual risks

- Real Demucs source separation remains an opt-in runtime path and was not executed in default gates.
- P26 must keep stem-aware Basic Pitch as a separate sidecar until P27 defines quality reconciliation.

