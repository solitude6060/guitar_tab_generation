# Docker Compose Runtime

Traditional Chinese version: [`docs/docker.zh-TW.md`](docker.zh-TW.md)

This project uses Docker Compose profiles so development, GPU AI work, local
LLM work, and cloud-backup credentials stay separated.

## Profiles

| Profile | Service | Purpose |
|---|---|---|
| `dev` | `app` | Fast uv / pytest / CLI / ffmpeg / ffprobe development |
| `gpu-ai` | `ai-gpu` | CUDA-ready runtime for future Basic Pitch, Demucs, torchcrepe work |
| `llm` | `ollama` | Local LLM server for tutorial text over artifacts |
| `cloud-backup` | `cloud-backup` | MiniMax backup policy inspection using environment variables only |

## Commands

```bash
docker compose --profile dev run --rm app uv run pytest -q
docker compose --profile dev run --rm app uv run guitar-tab-generation --help
docker compose --profile gpu-ai run --rm ai-gpu uv run guitar-tab-generation model-smoke --json
docker compose --profile llm up ollama
docker compose --profile cloud-backup run --rm cloud-backup
```

By default, the GPU image keeps heavy optional packages disabled. To build the
larger AI image on the RTX 4090 host:

```bash
INSTALL_HEAVY_AI=true docker compose --profile gpu-ai build ai-gpu
```

This installs PyTorch CUDA plus Basic Pitch, Demucs, torchcrepe, librosa, and
Essentia into the container virtualenv.

## Resource guards

The compose file defaults to conservative limits because the RTX 4090 may be
shared with other projects:

- `GPU_MEM_LIMIT=20g`
- `GPU_SHM_SIZE=2g`
- `GPU_CPUS=8`
- `CUDA_VISIBLE_DEVICES=0`
- `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512`
- `GPU_TESTS_ENABLED=0`

Keep `GPU_TESTS_ENABLED=0` for normal test runs. Set it to `1` only when the GPU
is idle and you intentionally want model smoke tests to run. Model downloads also require `MODEL_SMOKE_DOWNLOAD=1` or `--download`; see [`docs/model-smoke.md`](model-smoke.md).

## GPU requirements

The `gpu-ai` profile expects the host to have:

- NVIDIA driver
- `nvidia-smi`
- NVIDIA Container Toolkit

The GPU image can install heavy AI packages with `INSTALL_HEAVY_AI=true`, but
the default remains lightweight until the corresponding backend phase is ready.

## Secret policy

Copy `.env.example` to `.env` locally when MiniMax backup credentials are needed.
Never commit `.env`, API keys, model cache directories, media files, `.omx`, or
generated outputs.
