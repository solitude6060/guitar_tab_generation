# P12 PRD：FFmpeg Local Audio Ingest

## Context

P11 added required 3–8 minute full-song support, but only WAV files can be
validated without explicit `--trim-end`. The product advertises `.mp3`,
`.flac`, and `.m4a` as supported local audio suffixes, so real song files need a
local ffprobe/ffmpeg ingest path before heavier AI transcription backends are
introduced.

## Goal

Support legal local `.mp3`, `.flac`, and `.m4a` inputs by:

1. Reading source duration with local `ffprobe`.
2. Applying the same 30–90 second clip and 3–8 minute full-song policy.
3. Converting / trimming the input to `audio_normalized.wav` with local
   `ffmpeg`.
4. Preserving the local-only, no-download, no-cloud policy.

## Non-goals

- Do not enable arbitrary URL / YouTube download.
- Do not add Python package dependencies.
- Do not run Demucs / Basic Pitch / CREPE yet.
- Do not claim transcription accuracy improvements; this is an ingest
  foundation phase.

## Functional requirements

1. `resolve_local_audio("song.mp3")` can accept a valid 180–480 second
   full-song input without explicit `--trim-end` when ffprobe reports duration.
2. `resolve_local_audio()` returns a clear input policy error when ffprobe is
   missing or cannot read duration.
3. `normalize_audio()` uses ffmpeg for non-WAV inputs and writes a real
   `audio_normalized.wav`.
4. The CLI `transcribe` path can process a mocked non-WAV full-song input in
   tests without requiring real media downloads.
5. README and usage guardrails document that non-WAV ingest requires local
   ffprobe/ffmpeg.

## Acceptance criteria

- Red tests fail before implementation.
- Target P12 tests pass after implementation.
- Full `uv run pytest -q` passes.
- CLI help gates pass.
- Manual or mocked smoke proves an `.mp3` full-song path reaches
  `duration_class == "full_song"` and `processing_plan.mode ==
  "chunked_full_song"`.
- `.omx/` remains untracked and recent commits contain no OmX co-author.
