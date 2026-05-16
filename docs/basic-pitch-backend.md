# Basic Pitch Backend

## What it does

This project now supports a first real local AI note backend:

```bash
guitar-tab-generation transcribe <audio> --backend basic-pitch --out <artifact_dir>
```

`basic-pitch` is used only for note transcription in this phase. Rhythm, chord, and section analysis still follow the existing safe local path.

## Install

Sync the optional AI dependency group:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev --group ai
```

This installs the `basic-pitch` Python package and its local inference runtime dependencies.
It installs into this repository's `.venv` through `uv`; it does not install packages into system Python and does not build or modify Docker images.

The `ai` group intentionally includes only packages used by this backend:

- `basic-pitch`
- `setuptools>=68,<81` because Basic Pitch's `resampy` path still imports `pkg_resources`

## Usage

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

To avoid touching a busy GPU host, run inference with GPU hidden:

```bash
CUDA_VISIBLE_DEVICES='' UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

## Current scope

- Real local note transcription via Basic Pitch
- Existing artifact pipeline remains unchanged
- Provenance marks note events with `backend=basic-pitch`

## Current non-goals

- No Demucs integration yet
- No torchcrepe integration yet
- No real chord recognition backend yet
- No real section detection backend yet
