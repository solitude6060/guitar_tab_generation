# P11 Test Spec：Full Song Length Support（3–8 Minutes）

## Scope

Validate the new full-song input contract while preserving the deterministic
30–90 second fixture contract.

## Red tests first

1. `tests/test_input_policy.py`
   - `test_full_song_boundaries_are_accepted_with_chunk_plan`
   - `test_middle_length_audio_requires_supported_clip_or_full_song_window`
   - `test_url_policy_message_mentions_full_song_local_path`
2. `tests/e2e/test_cli_full_song_length.py`
   - `test_cli_transcribe_accepts_three_minute_full_song`

## Expected behavior

- 180s WAV → accepted as `duration_class == "full_song"`.
- 480s WAV → accepted as `duration_class == "full_song"`.
- 120s WAV → rejected with a clear message mentioning `30-90` and `3-8 minute`.
- Full-song `processing_plan`:
  - `mode == "chunked_full_song"`
  - chunk size is 60s
  - overlap is 2s
  - first chunk starts at 0.0
  - last chunk ends at the effective duration.
- CLI E2E output still writes:
  - `arrangement.json`
  - `quality_report.json`
  - `tab.md`
  - `notes.json`
  - `chords.json`
  - `sections.json`

## Verification commands

```bash
uv run pytest -q tests/test_input_policy.py tests/e2e/test_cli_full_song_length.py
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe --help
git ls-files .omx
git log -5 --format=%B
```
