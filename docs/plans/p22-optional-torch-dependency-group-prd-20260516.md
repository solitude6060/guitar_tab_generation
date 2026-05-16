# P22 PRD：Optional Torch Dependency Group

日期：2026-05-16  
狀態：Implemented in P22 branch  
範圍：建立可重現但不強迫安裝的 Torch AI 依賴入口。

## 1. 背景

P19 建立 Torch-first backend registry 與 smoke gate，P20 實作 `f0-calibrate` 的 torchcrepe sidecar，但刻意沒有把 PyTorch / torchcrepe / Demucs 安裝進預設開發環境。P22 的目標是補上明確的 opt-in 安裝路徑，讓 P23/P25 可以在可重現環境中做真實 runtime smoke，同時不拖慢 default dev / CI。

## 2. 目標

- 在 `pyproject.toml` 新增 `torch-ai` dependency group。
- `torch-ai` 只包含 P23/P25 已確定會被程式路徑直接呼叫的 packages。
- `dev` 預設同步不安裝 Torch heavy dependencies。
- 文件清楚區分：
  - default dev：一般開發、CI、fixture backend。
  - `ai`：Basic Pitch backend。
  - `torch-ai`：torchcrepe F0 與 Demucs stem separation route。
- `torch-smoke` 保持安全預設：不主動跑 heavy runtime、不偷用 GPU。

## 3. 非目標

- 不在 P22 下載或執行真實模型。
- 不實作 Demucs stem separation；那是 P25。
- 不把 Torch route 加進 default backend。
- 不硬編 CUDA wheel index；CUDA/CPU wheel 選擇以文件 gate 說明。

## 4. 依賴策略

`torch-ai` 包含：

- `torch`：torchcrepe 與 Demucs 的共同 runtime。
- `torchaudio`：Demucs audio runtime 常用依賴。
- `torchcrepe`：P20/P23 F0 calibration route。
- `demucs`：P25 stem separation route。

版本策略：

- PyPI metadata 於 2026-05-16 查核：`torchcrepe 0.0.24`、`demucs 4.0.1`、`torch 2.12.0`、`torchaudio 2.11.0`。
- P22 採 `torch>=2.11,<2.12` 與 `torchaudio>=2.11,<2.12`，原因是 `torchaudio` wheel 通常需要與 `torch` minor version 對齊；目前 PyPI `torchaudio` 尚未對齊 `torch 2.12`。P23 real smoke 顯示 torchcrepe audio loading 也需要 `torchcodec`，因此將其納入 `torch-ai` optional group。
- CUDA wheel selection 不寫死在 `pyproject.toml`，避免跨平台不可重現；需要 CUDA 時由使用者明確選擇 PyTorch index 或本機環境。

## 5. 驗收標準

- `pyproject.toml` 有 `torch-ai` group。
- `[tool.uv].default-groups = ["dev"]`，避免預設安裝 heavy group。
- 有英文與繁中安裝文件。
- Unit tests 驗證 dependency group contract 與 docs contract。
- `uv sync --locked --group dev` / `uv run pytest -q` 不需要安裝 Torch group。
