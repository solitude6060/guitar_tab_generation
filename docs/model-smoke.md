# Model Smoke Harness

Traditional Chinese version: [`docs/model-smoke.zh-TW.md`](model-smoke.zh-TW.md)

`guitar-tab-generation model-smoke` prepares the local AI model path safely. It
is designed for a shared RTX 4090 workstation: normal runs only print a plan and
will not download packages, pull models, or use the GPU.

## Safe defaults

```bash
uv run guitar-tab-generation model-smoke
uv run guitar-tab-generation model-smoke --json
```

Default behavior:

- no downloads;
- no GPU use;
- GPU-sensitive backends are skipped unless explicitly enabled;
- MiniMax is not used as a transcription source of truth;
- cache paths stay outside tracked source by default.

## Backend filters

```bash
uv run guitar-tab-generation model-smoke --backend basic-pitch
uv run guitar-tab-generation model-smoke --backend essentia --json
```

Supported backend ids:

- `basic-pitch`
- `demucs`
- `torchcrepe`
- `essentia`
- `local-llm`

## Opt-in downloads

Downloads require `--download` or `MODEL_SMOKE_DOWNLOAD=1`.

```bash
MODEL_SMOKE_DOWNLOAD=1 uv run guitar-tab-generation model-smoke --backend basic-pitch
```

GPU-sensitive routes additionally require `--allow-gpu` or
`GPU_TESTS_ENABLED=1`. They also check free VRAM before doing work.

```bash
GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 \
  uv run guitar-tab-generation model-smoke --backend demucs --download --allow-gpu
```

If free VRAM is below the threshold, the backend is marked `skipped` instead of
failing the command. This is intentional so another project can keep using the
GPU safely.

## Docker Compose

The GPU profile runs the safe JSON plan by default:

```bash
docker compose --profile gpu-ai run --rm ai-gpu
```

To allow actual downloads in the GPU container, set the same opt-in flags:

```bash
MODEL_SMOKE_DOWNLOAD=1 GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 \
  docker compose --profile gpu-ai run --rm ai-gpu \
  uv run guitar-tab-generation model-smoke --backend demucs --download --allow-gpu
```

Keep `GPU_TESTS_ENABLED=0` when the workstation is busy.
