# P15 PRD：Model Download Smoke Harness

## Context

P14 made the Docker Compose AI runtime reproducible, but the project still needs
a safe way to prepare local AI models without unexpectedly consuming the RTX
4090 while another project is using GPU resources.

The next step is a model download/integration smoke harness that is safe by
default, explicit when it downloads, and conservative before any GPU work.

## Goal

Create a CLI-driven harness that can plan and optionally execute model/backend
preparation checks for the selected local AI routes:

1. Basic Pitch for polyphonic pitch sketching.
2. Demucs / HTDemucs for stem separation.
3. torchcrepe for solo/riff pitch confidence calibration.
4. Essentia/librosa-style feature route for rhythm/onset features.
5. Ollama/local LLM for tutorial text over artifacts only.

## Safety requirements

- Default behavior must not download packages/models.
- Default behavior must not use GPU.
- Any download requires either `--download` or `MODEL_SMOKE_DOWNLOAD=1`.
- Any GPU-sensitive backend requires `GPU_TESTS_ENABLED=1`.
- GPU-sensitive execution must check free VRAM before running.
- The default minimum free VRAM is `12000` MB and can be changed by
  `GPU_MIN_FREE_MB` or `--min-free-vram-mb`.
- If VRAM is below the threshold, the harness must skip instead of failing.
- Model/cache paths must be outside git-tracked source by default.
- No credentials or MiniMax tokens may be written to repo files.

## Functional requirements

1. Add `guitar-tab-generation model-smoke` CLI.
2. Support `--json` for machine-readable status.
3. Support `--backend` filters; default is all selected backends.
4. Support `--download` opt-in.
5. Support `--allow-gpu` opt-in, with `GPU_TESTS_ENABLED=1` as an environment
   alternative.
6. Report per-backend status:
   - `planned`
   - `ready`
   - `skipped`
   - `failed`
7. Report download commands and cache locations without executing them unless
   download is enabled.
8. Integrate with Docker Compose docs/profile guidance.

## Non-goals

- Do not run heavy Demucs/Basic Pitch inference in default CI.
- Do not install heavy optional dependencies into the default dev environment.
- Do not choose cloud inference as a transcription source of truth.
- Do not enable YouTube or arbitrary URL download.

## Acceptance criteria

- Unit tests prove safe defaults do not call download commands.
- Unit tests prove GPU checks skip when free VRAM is below threshold.
- CLI tests prove JSON output and backend filtering.
- English and Traditional Chinese docs explain safe model preparation.
- `uv run pytest -q` passes.
- `guitar-tab-generation model-smoke --json` is safe to run on a busy GPU host.
- `.omx/` remains untracked and recent commits have no OmX co-author trailer.
