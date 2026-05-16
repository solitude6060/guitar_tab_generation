# P19 PRD：Torch-first AI Backend Roadmap 與 Smoke Gate

日期：2026-05-16
狀態：Implemented
Branch：`feature/torch-first-backend-roadmap`

## 1. 背景

P18 已接入 `basic-pitch` 作為第一個真實本機 note transcription backend。使用者確認 Basic Pitch 目前可接受，但長期方向偏好 Torch-first 生態。P19 不替換 Basic Pitch，而是先建立 PyTorch backend 抽象、模型選型文件、GPU/CPU 資源門檻與 smoke gate，避免後續每次接模型都臨時改 pipeline。

## 2. 目標

1. 建立 Torch-first route registry，描述候選 backend、角色、依賴、GPU/CPU 門檻與 integration phase。
2. 新增 CLI 可檢查 Torch-first roadmap / readiness。
3. 新增 CLI 可產生安全 smoke gate plan，預設不下載、不使用 GPU。
4. 文件化模型選型與 4090 資源策略，含繁中版本。
5. 不新增 PyTorch / Demucs / torchcrepe / transformers 等 heavy dependency，除非本階段 production code 直接呼叫。

## 3. 功能需求

### 3.1 Torch route registry

需列出至少三條 Torch-first candidate route：

- `torchcrepe-f0`：solo/riff F0 calibration。
- `demucs-htdemucs`：stem separation。
- `mt3-transcription`：長期 multi-instrument transcription 研究路線。

每條 route 必須有：

- `id`
- `label`
- `stage`
- `role`
- `framework=pytorch`
- `python_imports`
- `command`
- `min_free_vram_mb`
- `cpu_allowed`
- `gpu_sensitive`
- `integration_phase`
- `auto_install=false`

### 3.2 Readiness CLI

新增：

```bash
guitar-tab-generation torch-backends
```

輸出繁中 Markdown，說明：

- 本機優先。
- P19 不取代 Basic Pitch。
- P19 不自動安裝 Torch packages。

也需支援：

```bash
guitar-tab-generation torch-backends --json
```

### 3.3 Smoke gate CLI

新增：

```bash
guitar-tab-generation torch-smoke --route torchcrepe-f0
```

安全預設：

- 不下載。
- 不執行 GPU-sensitive smoke。
- GPU route 需要 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`。
- VRAM 不足時 skip，不失敗。

### 3.4 文件

新增：

- `docs/torch-first-ai-backend-roadmap.md`
- `docs/torch-first-ai-backend-roadmap.zh-TW.md`

內容需包含模型選型、GPU/CPU 資源門檻、下一階段建議。

## 4. 非目標

- 不替換 `basic-pitch`。
- 不新增實際 Torch heavy dependency。
- 不下載模型 checkpoint。
- 不承諾 MT3/YourMT3 已可 production 使用。
- 不改變 `fixture` default backend。

## 5. 驗收標準

1. `torch-backends` 與 `torch-smoke` CLI 可用。
2. 測試覆蓋 route registry、readiness probing、VRAM gate、CLI Markdown/JSON。
3. `uv run pytest -q` 綠燈。
4. `uv run guitar-tab-generation --help` 顯示新命令。
5. `.omx` 不追蹤。
