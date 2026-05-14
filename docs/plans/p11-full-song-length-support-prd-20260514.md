# P11 PRD：Full Song Length Support（3–8 Minutes）

## Context

The product must support one complete song-length audio input, not only short
MVP clips. The mandatory supported full-song window is **3–8 minutes
（180–480 seconds）** while preserving the existing 30–90 second golden fixture
clip workflow for deterministic tests and demos.

## Goal

Accept legal local audio whose effective trim/input duration is either:

1. **Practice clip:** 30–90 seconds.
2. **Full song:** 3–8 minutes / 180–480 seconds.

Full-song inputs must be marked in artifacts so later AI stages can schedule
chunked local processing on the RTX 4090 without pretending that a single pass
has already solved long-song transcription.

## Non-goals

- Do not enable arbitrary YouTube/URL download.
- Do not download or install heavy AI models in this phase.
- Do not remove the existing 30–90 second golden fixture gate.
- Do not claim production-level full-song transcription accuracy yet; P11 is
  the input contract and artifact scheduling foundation.

## Functional requirements

1. `resolve_local_audio()` accepts a 180–480 second local WAV input.
2. `resolve_local_audio()` rejects ambiguous middle-length inputs between 90 and
   180 seconds unless later product work defines a separate mode.
3. URL policy messaging must mention legal local clips and legal local full
   songs.
4. `AudioInput` exposes:
   - `duration_class`: `clip` or `full_song`
   - effective `duration_seconds`
   - original `source_duration_seconds`
   - `processing_plan` describing single-pass clip or chunked full-song mode.
5. `transcribe` artifacts include `source.duration_class`,
   `source.source_duration_seconds`, and `source.processing_plan`.
6. The local AI resource plan mentions 3–8 minute full-song scheduling.

## Acceptance criteria

- Unit tests cover 180s and 480s accepted full-song boundaries.
- Unit tests cover 120s rejected as outside the supported clip/full-song
  windows.
- CLI E2E proves a legal 180s WAV can produce the standard artifact contract
  with full-song metadata.
- Full test suite passes under `uv run pytest -q`.
- `.omx/` remains untracked and commit messages contain no OmX co-author.
