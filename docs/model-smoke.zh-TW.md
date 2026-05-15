# 模型 Smoke Harness（繁體中文）

English version: [`docs/model-smoke.md`](model-smoke.md)

`guitar-tab-generation model-smoke` 用來安全準備本機 AI 模型路線。它是針對「同一台 RTX 4090 可能同時有其他專案在用」的情境設計：一般執行只印出計畫，不下載套件、不拉模型、不使用 GPU。

## 安全預設

```bash
uv run guitar-tab-generation model-smoke
uv run guitar-tab-generation model-smoke --json
```

預設行為：

- 不下載；
- 不使用 GPU；
- GPU-sensitive backend 必須明確開啟才會執行；
- MiniMax 不會作為音符/和弦辨識的 truth source；
- cache 預設放在 repo 外，避免被 git 追蹤。

## 指定 backend

```bash
uv run guitar-tab-generation model-smoke --backend basic-pitch
uv run guitar-tab-generation model-smoke --backend essentia --json
```

支援 backend id：

- `basic-pitch`
- `demucs`
- `torchcrepe`
- `essentia`
- `local-llm`

## 明確 opt-in 下載

下載必須加 `--download` 或設定 `MODEL_SMOKE_DOWNLOAD=1`。

```bash
MODEL_SMOKE_DOWNLOAD=1 uv run guitar-tab-generation model-smoke --backend basic-pitch
```

GPU-sensitive route 還需要 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`，並且會先檢查可用 VRAM。

```bash
GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 \
  uv run guitar-tab-generation model-smoke --backend demucs --download --allow-gpu
```

如果可用 VRAM 低於門檻，該 backend 會標記為 `skipped`，不是失敗。這是刻意設計，避免搶走其他專案正在使用的 GPU。

## Docker Compose

`gpu-ai` profile 預設只跑安全 JSON plan：

```bash
docker compose --profile gpu-ai run --rm ai-gpu
```

若要在 GPU container 內允許實際下載，必須加同樣的 opt-in 旗標：

```bash
MODEL_SMOKE_DOWNLOAD=1 GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 \
  docker compose --profile gpu-ai run --rm ai-gpu \
  uv run guitar-tab-generation model-smoke --backend demucs --download --allow-gpu
```

當工作站忙碌時，請維持 `GPU_TESTS_ENABLED=0`。
