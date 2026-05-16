# P23 PRD：Real torchcrepe Runtime Smoke

日期：2026-05-16  
狀態：Implemented in P23 branch  
範圍：在 P22 `torch-ai` optional group 基礎上，建立明確 opt-in 的真實 torchcrepe runtime smoke。

## 1. 背景

P20 已經提供 `f0-calibrate` sidecar，但 default dev/CI 沒有安裝 torchcrepe。P22 新增 `torch-ai` optional group，讓 PyTorch / torchcrepe / Demucs 有可重現的安裝入口。P23 的任務是把 `torch-smoke --route torchcrepe-f0 --run` 從「只做 import smoke」提升為「實際跑過 F0 calibration path，並輸出 `f0_calibration.json`」。

## 2. 目標

- `torch-smoke --route torchcrepe-f0 --run` 在已安裝 `torch-ai` 的 opt-in 環境中建立短音訊 fixture，並輸出 `f0_calibration.json`。
- CPU smoke 是預設 real runtime route，避免無意佔用 GPU。
- GPU smoke 必須同時符合：
  - 使用者明確要求 `--device cuda`。
  - 使用者明確允許 `--allow-gpu` 或設定 `GPU_TESTS_ENABLED=1`。
  - VRAM gate 通過。
- default dev/CI 不安裝、不執行 torch/torchcrepe heavy runtime。
- smoke artifact 寫入 model cache，不污染使用者 artifact directory。

## 3. 非目標

- 不在 CI 安裝 `torch-ai`。
- 不承諾 CUDA wheel 在所有平台可用。
- 不做品質評估或 benchmark；P23 只驗證 runtime path 可跑通。
- 不改 `f0-calibrate` artifact sidecar contract。

## 4. 使用者流程

安全預設（不執行 heavy runtime）：

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json
```

安裝 optional Torch group：

```bash
uv sync --group torch-ai
```

CPU real smoke：

```bash
uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cpu --json
```

GPU real smoke（明確 opt-in + VRAM gate）：

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --run --device cuda --allow-gpu --min-free-vram-mb 4000 --json
```

## 5. 驗收標準

- 有 P23 PRD 與 test spec。
- `torch-smoke --help` 顯示 `--device {cpu,cuda}`。
- `torch-smoke --route torchcrepe-f0 --run` 會呼叫 real calibration path；測試可用 fake runtime 鎖定 artifact contract。
- `--device cuda` 沒有 GPU opt-in 時要 skip，不得嘗試 import torchcrepe 或執行 runtime。
- default `uv sync --locked --group dev` 與 `uv run pytest -q` 不需要 Torch heavy dependency。


## P23 實跑補充

CPU real smoke 實跑時，torchcrepe audio loader 在目前 PyTorch runtime 需要 `torchcodec`。因此 P23 將 `torchcodec>=0.12,<0.13` 加入 `torch-ai` optional group；default dev/CI 仍不安裝。
