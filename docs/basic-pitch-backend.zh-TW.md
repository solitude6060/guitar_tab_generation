# Basic Pitch Backend

## 功能

本專案現在支援第一個真實本機 AI note backend：

```bash
guitar-tab-generation transcribe <audio> --backend basic-pitch --out <artifact_dir>
```

在這個階段，`basic-pitch` 只負責 note transcription。節奏、和弦、段落仍沿用現有安全本機流程。

## 安裝

同步可選的 AI dependency group：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev --group ai
```

這會安裝 `basic-pitch` Python 套件與其本機推論 runtime 依賴。
安裝位置是本 repo 的 `uv` `.venv`，不會安裝到系統 Python，也不會建立或修改 Docker image。

目前 `ai` dependency group 只包含這個 backend 確定會用到的套件：

- `basic-pitch`
- `setuptools>=68,<81`：因為 Basic Pitch 的 `resampy` 路徑仍會匯入 `pkg_resources`

## 使用方式

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

如果目前機器上 GPU 正被其他專案使用，建議先隱藏 GPU，用 CPU 跑 smoke test：

```bash
CUDA_VISIBLE_DEVICES='' UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

## 目前範圍

- 用 Basic Pitch 做真實本機 note transcription
- 既有 artifact pipeline 不重寫
- note events provenance 會標記 `backend=basic-pitch`

## 目前非目標

- 尚未整合 Demucs
- 尚未整合 torchcrepe
- 尚未整合真實 chord recognition backend
- 尚未整合真實 section detection backend
