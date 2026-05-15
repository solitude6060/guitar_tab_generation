# P13 PRD：Local AI Backend Registry

## Context

P10 documented the RTX 4090 local-first resource plan, P11 added full-song
duration support, and P12 added ffprobe/ffmpeg ingest. The next step is to make
the selected local AI model route inspectable before wiring heavy inference
dependencies into the transcription pipeline.

## Goal

Expose a local AI backend registry that reports availability and intended role
for the project's selected local-first model/tool route:

- Basic Pitch for pitch transcription.
- Demucs / HTDemucs for stem separation.
- CREPE / torchcrepe for monophonic pitch calibration.
- Essentia / librosa-style feature extraction for rhythm and audio features.
- Local LLM runtime for tutorial text over artifacts only.

## Non-goals

- Do not install heavy dependencies.
- Do not run model inference yet.
- Do not send media or artifacts to MiniMax or any cloud provider.
- Do not enable URL/YouTube download.

## Functional requirements

1. Add a reusable module that lists selected local AI backends with:
   - backend id
   - category / product role
   - command availability
   - Python import availability
   - selected model or runtime note
   - whether it is local-first
2. Add CLI command:
   - `guitar-tab-generation ai-backends`
   - `guitar-tab-generation ai-backends --json`
3. `doctor-ai --json` includes backend registry status for machine-readable
   diagnostics.
4. `ai-resources` references the registry command.
5. User-facing docs explain that P13 is inspection/planning, not heavy model
   installation or inference.

## Acceptance criteria

- Unit tests cover backend registry output with injected availability checks.
- CLI tests cover Markdown and JSON output.
- Full `uv run pytest -q` passes.
- CLI help gates pass for `doctor-ai`, `ai-resources`, and `ai-backends`.
- `.omx/` remains untracked and recent commits contain no OmX co-author.
