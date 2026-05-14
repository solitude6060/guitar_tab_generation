# P12 PR Code Review — FFmpeg Local Audio Ingest

## Review scope

- `src/guitar_tab_generation/input_adapter.py`
- `src/guitar_tab_generation/audio_preprocess.py`
- `src/guitar_tab_generation/cli.py`
- `src/guitar_tab_generation/ai_runtime.py`
- `tests/test_input_policy.py`
- `tests/unit/test_audio_preprocess_ffmpeg.py`
- `tests/e2e/test_cli_non_wav_ingest.py`
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

- `ffmpeg` / `ffprobe` are required local system tools for non-WAV ingest. This
  is acceptable because the project already has a local runtime doctor and P12
  documents actionable failures instead of adding Python media dependencies.
- WAV fixture normalization still uses the deterministic Python `wave` path.
  This intentionally keeps CI fast and avoids requiring ffmpeg for existing
  golden fixtures.

## Evidence

- Red test evidence:
  - `uv run pytest -q tests/test_input_policy.py tests/unit/test_audio_preprocess_ffmpeg.py tests/e2e/test_cli_non_wav_ingest.py`
  - Initial result: collection error for missing `AudioPreprocessError`.
- Target tests:
  - `uv run pytest -q tests/test_input_policy.py tests/unit/test_audio_preprocess_ffmpeg.py tests/e2e/test_cli_non_wav_ingest.py`
  - Result: 10 passed.
- Full regression:
  - `uv run pytest -q`
  - Result: 105 passed.
- Local real-tool smoke:
  - Generated `/tmp/guitar-tab-p12-source.flac`.
  - `uv run guitar-tab-generation transcribe /tmp/guitar-tab-p12-source.flac --backend fixture --out /tmp/guitar-tab-p12-flac`
  - Verified: `full_song 180.0 chunked_full_song`; `audio_normalized.wav` exists.

## Merge recommendation

Merge `feature/ffmpeg-local-audio-ingest` into `dev` after final CLI and hygiene
checks.
