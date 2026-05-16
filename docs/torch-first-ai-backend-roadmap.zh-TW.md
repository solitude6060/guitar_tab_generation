# Torch-first AI Backend Roadmap

## 原則

P19 的目標不是馬上把 Basic Pitch 換掉，而是先把 PyTorch 生態的 backend 邊界定清楚：

- `fixture` 仍是 deterministic default。
- `basic-pitch` 仍是明確指定的第一個真實 note transcription backend。
- Torch-first route 先做 registry、readiness、資源 gate 與 smoke plan。
- 不自動安裝 PyTorch / Demucs / torchcrepe / transformers。
- 只有後續 phase 的 production code 直接呼叫時，才把該依賴加入 `uv` dependency group。

## 候選路線

| Route | 角色 | GPU/CPU 策略 | 狀態 |
|---|---|---|---|
| `torchcrepe-f0` | solo/riff monophonic F0 calibration | CPU 可跑；GPU 可加速；建議至少 4GB free VRAM | P20 candidate |
| `demucs-htdemucs` | guitar/bass/drums/vocals stem separation | GPU-sensitive；共享 4090 上需 sequential；建議至少 12GB free VRAM | P20/P21 candidate |
| `mt3-transcription` | multi-instrument transcription 研究路線 | GPU-sensitive；建議至少 16GB free VRAM | 研究候選，不立即安裝 |

## CLI

查看 Torch-first route readiness：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends
```

輸出 JSON：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-backends --json
```

查看 smoke gate plan：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0
```

GPU route 需要明確 opt-in：

```bash
GPU_TESTS_ENABLED=1 GPU_MIN_FREE_MB=12000 UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route demucs-htdemucs --allow-gpu
```

## 資源策略

- 預設不碰 GPU。
- GPU-sensitive route 必須通過 VRAM gate。
- VRAM 不足時 skip，不把共享機器拖垮。
- 3～8 分鐘歌曲後續應先用 chunk/full-song pipeline 分段，再逐段跑 stem / pitch route。

## 下一階段建議

P20 建議先選一個 Torch route 做真正 production code 接入：

1. 若目標是提升 solo / riff 音高可信度：先做 `torchcrepe-f0`。
2. 若目標是完整歌曲多軌前處理：先做 `demucs-htdemucs`，但要加 queue / resource lock。
3. 若目標是取代 Basic Pitch 的 polyphonic transcription：先做 MT3/YourMT3 research spike，不應直接進 production。
