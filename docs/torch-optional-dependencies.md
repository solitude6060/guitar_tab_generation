# Optional Torch Dependencies

P22 adds a reproducible but opt-in Torch environment for the routes that are already planned or directly wired by the product.

## Groups

| Group | Install command | Purpose | Default? |
|---|---|---|---|
| `dev` | `uv sync --group dev` | Tests, CLI, fixture backend, default CI | Yes |
| `ai` | `uv sync --group ai` | Basic Pitch transcription backend | No |
| `torch-ai` | `uv sync --group torch-ai` | torchcrepe F0 calibration and Demucs stem-separation route preparation | No |

The project sets `tool.uv.default-groups = ["dev"]`; default development does not install Torch, torchcrepe, torchaudio, or Demucs.

## What `torch-ai` contains

- `torch` and `torchaudio`: shared PyTorch runtime packages.
- `torchcrepe`: used by `guitar-tab-generation f0-calibrate` after explicit installation.
- `Demucs`: planned stem separation runtime for P25.

## Safe verification gate

Before installing the heavy group, inspect the safe smoke plan:

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json
uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --json
```

The smoke gate is safe by default: it does not run the heavy runtime unless `--run` or `TORCH_SMOKE_RUN=1` is provided, and GPU-sensitive checks require `--allow-gpu` or `GPU_TESTS_ENABLED=1`.

## Install only when needed

```bash
uv sync --group torch-ai
```

For CUDA-specific PyTorch wheels, choose the PyTorch index that matches the local driver/CUDA stack explicitly instead of hard-coding one CUDA wheel source in this repository. This keeps Linux CPU, Linux CUDA, and non-Linux installs reviewable.

## After installation

CPU-safe route smoke:

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run
```

GPU-sensitive checks should be explicit and guarded on shared RTX 4090 hosts:

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --run --allow-gpu --min-free-vram-mb 12000
```
