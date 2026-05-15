# P14 PRD：Docker Compose Local AI Runtime

## Context

The project now has local audio ingest, full-song duration support, and a local
AI backend registry. The next step is to make the development and AI runtime
reproducible with Docker Compose while keeping heavy AI dependencies optional.

## Goal

Create a Docker Compose setup that supports:

1. Fast dev/test CLI execution with `uv`, ffmpeg, and ffprobe.
2. Optional GPU AI runtime profile for CUDA/PyTorch and future Basic Pitch /
   Demucs / torchcrepe work.
3. Optional local LLM runtime profile.
4. Safe secret handling for MiniMax as a backup provider only.

## Non-goals

- Do not install Basic Pitch, Demucs, torchcrepe, Essentia, or large models in
  the default dev image.
- Do not copy `.omx`, `.venv`, caches, local outputs, or secrets into images.
- Do not store MiniMax tokens in repo files.
- Do not enable arbitrary URL / YouTube download.

## Functional requirements

1. Add `docker-compose.yml` with profiles:
   - `dev`
   - `gpu-ai`
   - `llm`
   - `cloud-backup`
2. Add Dockerfiles:
   - `docker/Dockerfile.dev`
   - `docker/Dockerfile.gpu`
3. Add `.dockerignore` to exclude local state and secrets.
4. Add `.env.example` with safe placeholders only.
5. Add user-facing Docker documentation:
   - `docs/docker.md`
   - `docs/docker.zh-TW.md`
6. Compose config must be valid.
7. The dev profile must support `uv run pytest -q` and CLI commands.
8. GPU profile must declare NVIDIA GPU reservation without requiring CI to have
   a GPU.

## Acceptance criteria

- Tests verify compose/profile structure and secret hygiene.
- `docker compose config` passes locally.
- `uv run pytest -q` passes.
- CLI help gates pass.
- `.omx/` remains untracked.
- Recent commits contain no `Co-authored-by: OmX`.
