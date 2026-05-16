# Optional Torch Dependencies（可選 Torch 依賴）

P22 新增一個可重現、但必須明確 opt-in 才會安裝的 Torch 環境，供已經規劃或已經接入的 route 使用。

## Groups

| Group | 安裝指令 | 用途 | 預設安裝？ |
|---|---|---|---|
| `dev` | `uv sync --group dev` | 測試、CLI、fixture backend、預設 CI | 是 |
| `ai` | `uv sync --group ai` | Basic Pitch transcription backend | 否 |
| `torch-ai` | `uv sync --group torch-ai` | torchcrepe F0 calibration 與 Demucs stem separation route 準備 | 否 |

專案設定 `tool.uv.default-groups = ["dev"]`；一般開發不會安裝 Torch、torchcrepe、torchaudio 或 Demucs。

## `torch-ai` 包含什麼

- `torch` 與 `torchaudio`：共用 PyTorch runtime packages。
- `torchcrepe`：明確安裝後可供 `guitar-tab-generation f0-calibrate` 使用。
- `Demucs`：P25 預計使用的 stem separation runtime。

## 安全驗證 gate

安裝 heavy group 前，先看安全 smoke plan：

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json
uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --json
```

`torch-smoke` 預設是安全的：除非提供 `--run` 或 `TORCH_SMOKE_RUN=1`，否則不執行 heavy runtime；GPU-sensitive 檢查也需要 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`。

## 只在需要時安裝

```bash
uv sync --group torch-ai
```

如果需要 CUDA-specific PyTorch wheels，請依本機 driver/CUDA stack 明確選擇 PyTorch index，不要把單一 CUDA wheel source 硬寫進 repo。這樣 Linux CPU、Linux CUDA 與非 Linux 安裝路徑才保持可審查。

## 安裝後驗證

CPU-safe route smoke：

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run
```

共享 RTX 4090 主機上的 GPU-sensitive 檢查必須明確 opt-in 並受 VRAM gate 保護：

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --run --allow-gpu --min-free-vram-mb 12000
```
