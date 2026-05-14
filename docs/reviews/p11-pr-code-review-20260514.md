# P11 PR Code Review — Full Song Length Support

## Review scope

- `src/guitar_tab_generation/input_adapter.py`
- `src/guitar_tab_generation/pipeline.py`
- `src/guitar_tab_generation/renderer.py`
- `src/guitar_tab_generation/ai_runtime.py`
- `src/guitar_tab_generation/contracts.py`
- `tests/test_input_policy.py`
- `tests/e2e/test_cli_full_song_length.py`
- `tests/support/contract_validators.py`
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

- The current deterministic backend still produces sketch-level placeholder
  notes for full-song inputs. This is acceptable for P11 because the phase goal
  is input contract + artifact scheduling, not production transcription
  accuracy. Future AI backend phases must consume `source.processing_plan`.

## Evidence

- Red tests first:
  - `uv run pytest -q tests/test_input_policy.py tests/e2e/test_cli_full_song_length.py`
  - Initial result: 5 failed / 1 passed before implementation.
- Target tests after implementation:
  - `uv run pytest -q tests/test_input_policy.py tests/e2e/test_cli_full_song_length.py`
  - Result: 6 passed.
- Full regression:
  - `uv run pytest -q`
  - Result: 100 passed.
- CLI smoke:
  - `uv run guitar-tab-generation --help`
  - `uv run guitar-tab-generation transcribe --help`
  - `uv run guitar-tab-generation ai-resources | grep -E '3–8|60 秒 chunk|MiniMax'`
- Manual full-song smoke:
  - Generated `/tmp/guitar-tab-p11-full-song.wav` at 180s.
  - `uv run guitar-tab-generation transcribe /tmp/guitar-tab-p11-full-song.wav --backend fixture --out /tmp/guitar-tab-p11-full-song`
  - Verified artifact source metadata: `full_song chunked_full_song 180.0`.
- Whitespace:
  - `git diff --check`
  - Result: clean.

## Merge recommendation

Merge `feature/full-song-length-support` into `dev` after hygiene checks:

- `.omx/` remains untracked.
- Commit messages contain no `Co-authored-by: OmX`.
