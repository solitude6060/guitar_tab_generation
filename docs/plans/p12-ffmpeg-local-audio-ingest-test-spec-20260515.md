# P12 Test Spec：FFmpeg Local Audio Ingest

## Scope

Add deterministic tests for local ffprobe/ffmpeg ingest without depending on
real copyrighted media or external network access.

## Red tests first

1. `tests/test_input_policy.py`
   - `test_non_wav_full_song_duration_is_read_with_ffprobe`
   - `test_non_wav_without_ffprobe_reports_actionable_error`
2. `tests/unit/test_audio_preprocess_ffmpeg.py`
   - `test_non_wav_normalization_uses_ffmpeg_to_write_wav`
   - `test_non_wav_normalization_failure_is_actionable`
3. `tests/e2e/test_cli_non_wav_ingest.py`
   - `test_cli_transcribe_accepts_mocked_mp3_full_song`

## Expected behavior

- ffprobe command:
  - uses local `ffprobe`
  - reads `format=duration`
  - returns seconds as float
- ffmpeg command:
  - uses local `ffmpeg`
  - applies trim start/end
  - writes mono 44.1 kHz `audio_normalized.wav`
- Error messages mention `ffprobe` or `ffmpeg` and do not suggest URL download.

## Verification commands

```bash
uv run pytest -q tests/test_input_policy.py tests/unit/test_audio_preprocess_ffmpeg.py tests/e2e/test_cli_non_wav_ingest.py
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe --help
git ls-files .omx
git log -5 --format=%B
```
