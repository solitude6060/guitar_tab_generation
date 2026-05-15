# Docker Compose Runtime（繁體中文）

English version: [`docs/docker.md`](docker.md)

本專案用 Docker Compose profiles 分離開發、GPU AI、本機 LLM、MiniMax 備援，避免把所有重型 AI 依賴和 secret 塞進單一 image。

## Profiles

| Profile | Service | 用途 |
|---|---|---|
| `dev` | `app` | 快速執行 uv / pytest / CLI / ffmpeg / ffprobe |
| `gpu-ai` | `ai-gpu` | 預留 CUDA runtime，後續接 Basic Pitch、Demucs、torchcrepe |
| `llm` | `ollama` | 本機 LLM，只讀 artifacts 產生教學文字 |
| `cloud-backup` | `cloud-backup` | MiniMax 備援政策檢查；token 只從環境變數讀取 |

## 常用指令

```bash
docker compose --profile dev run --rm app uv run pytest -q
docker compose --profile dev run --rm app uv run guitar-tab-generation --help
docker compose --profile gpu-ai run --rm ai-gpu uv run guitar-tab-generation ai-backends
docker compose --profile llm up ollama
docker compose --profile cloud-backup run --rm cloud-backup
```

預設 GPU image 不安裝重型 optional packages。若要在 RTX 4090 主機上建立較大的完整 AI image：

```bash
INSTALL_HEAVY_AI=true docker compose --profile gpu-ai build ai-gpu
```

這會把 PyTorch CUDA、Basic Pitch、Demucs、torchcrepe、librosa、Essentia 安裝到 container 的 virtualenv。

## 資源限制

因為 RTX 4090 可能同時被其他專案使用，compose 預設採保守限制：

- `GPU_MEM_LIMIT=20g`
- `GPU_SHM_SIZE=2g`
- `GPU_CPUS=8`
- `CUDA_VISIBLE_DEVICES=0`
- `PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512`
- `GPU_TESTS_ENABLED=0`

一般測試請維持 `GPU_TESTS_ENABLED=0`。只有在 GPU 空閒、且你明確要跑模型 smoke tests 時，才把它設為 `1`。

## GPU 需求

`gpu-ai` profile 預期主機已安裝：

- NVIDIA driver
- `nvidia-smi`
- NVIDIA Container Toolkit

GPU image 可透過 `INSTALL_HEAVY_AI=true` 安裝 Basic Pitch、Demucs、torchcrepe、Essentia 等重依賴；預設保持輕量，避免一般 dev / CI 被大型套件拖慢。

## MiniMax 與 secret 政策

需要 MiniMax 備援時，請在本機把 `.env.example` 複製成 `.env`，再填入 token。

禁止提交：

- `.env`
- API key / token
- `.omx`
- 模型 cache
- 產生的媒體檔
- `out/` 輸出
