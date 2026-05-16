# Torch-first AI Backend Roadmap

## Principles

P19 does not replace Basic Pitch. It establishes the PyTorch-oriented backend boundary first:

- `fixture` remains the deterministic default.
- `basic-pitch` remains the explicit first real note transcription backend.
- Torch-first routes start as registry/readiness/resource-gate/smoke-plan artifacts.
- PyTorch, Demucs, torchcrepe, and transformers are not auto-installed in P19.
- A heavy dependency should enter a uv dependency group only when production code directly calls it.

## Candidate routes

| Route | Role | GPU/CPU strategy | Status |
|---|---|---|---|
| `torchcrepe-f0` | Solo/riff monophonic F0 calibration | CPU allowed; GPU optional; at least 4GB free VRAM recommended | P20 candidate |
| `demucs-htdemucs` | Guitar/bass/drums/vocals stem separation | GPU-sensitive; sequential on shared RTX 4090; at least 12GB free VRAM recommended | P20/P21 candidate |
| `mt3-transcription` | Multi-instrument transcription research route | GPU-sensitive; at least 16GB free VRAM recommended | Research candidate |

## CLI

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends --json
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0
GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --allow-gpu
```

## Resource strategy

- Do not touch GPU by default.
- GPU-sensitive routes must pass the VRAM gate.
- Insufficient VRAM skips the route instead of failing hard.
- For 3–8 minute songs, future full-song/chunk orchestration should run stem/pitch routes in bounded chunks.

## Recommended next phase

P20 should choose exactly one route for production integration:

1. `torchcrepe-f0` if the goal is solo/riff pitch confidence calibration.
2. `demucs-htdemucs` if the goal is full-song multitrack preprocessing, with queue/resource locking.
3. MT3/YourMT3 only as a research spike before production use.
