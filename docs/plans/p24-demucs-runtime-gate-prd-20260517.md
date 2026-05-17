# P24 PRD：Demucs Runtime Planning + Install Gate

日期：2026-05-17
狀態：Planned
範圍：在 P25 真正做 stem separation 前，先把 Demucs optional runtime、cache、GPU gate、錯誤與 skip 策略定成可測契約。

## 1. 背景

P22 已建立 `torch-ai` optional dependency group，P23 已驗證 torchcrepe 的 opt-in runtime smoke。Demucs 仍停在 route 與 dependency 準備階段；P24 的目標是先建立 install/runtime gate，避免 P25 導入 `separate-stems` 時出現隱性下載、偷偷佔用 GPU、missing runtime 時靜默 fallback，或 stem artifact provenance 不清楚。

## 2. 目標

- 新增 Demucs gate，可回報：
  - optional dependency 安裝提示：`uv sync --group torch-ai`。
  - runtime command/import 是否可用。
  - model name：預設 `htdemucs`。
  - cache root 與 Demucs model cache path。
  - GPU gate：必須明確 opt-in，且 free VRAM 達門檻。
- 安全預設：
  - 不下載模型。
  - 不使用 GPU。
  - 不執行 stem separation。
  - 不改 `transcribe` 預設 backend。
- 錯誤策略：
  - missing Demucs runtime 必須是清楚 error，附安裝指令。
  - GPU VRAM 不足必須 skip，不可繼續跑 runtime。
  - Demucs gate 失敗不可 fallback 成 mix 或 fixture stem。

## 3. 非目標

- 不新增 `separate-stems` CLI；那是 P25。
- 不呼叫 Demucs 做任何真實 source separation。
- 不下載 Demucs model weights。
- 不把 Demucs 接進 `transcribe`。
- 不在 default dev/CI 安裝 `torch-ai`。

## 4. 使用者流程

安全規劃：

```bash
uv run guitar-tab-generation demucs-gate --json
```

安裝 optional runtime：

```bash
uv sync --group torch-ai
```

檢查 runtime 是否已安裝，但仍不分軌、不下載模型：

```bash
uv run guitar-tab-generation demucs-gate --check-runtime --json
```

共享 GPU 主機上檢查 GPU gate：

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation demucs-gate --allow-gpu --min-free-vram-mb 12000 --json
```

## 5. 驗收標準

- 有 P24 PRD、test spec、ADR 與 Demucs runtime gate 文件。
- `demucs-gate --json` 預設只輸出 plan，不執行 Demucs、不使用 GPU、不下載。
- `demucs-gate --check-runtime --json` 在 Demucs 缺失時回傳清楚錯誤與 `uv sync --group torch-ai` 提示。
- GPU opt-in 且 free VRAM 不足時狀態為 `skipped`，不執行 runtime command。
- 所有 gate payload 均明確宣告 `fallback_policy=no_silent_fallback`。
- `transcribe --help` 仍顯示 fixture default，沒有 Demucs/stem 預設行為。
