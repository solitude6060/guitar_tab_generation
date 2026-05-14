# P10 PRD：Local 4090 AI Runtime + MiniMax Backup Resources

日期：2026-05-14
狀態：Implemented
Branch：`feature/local-ai-runtime-resources`

## 1. 背景

使用者希望後續 AI 資源規劃以「本機 RTX 4090 可以完整負擔」為核心，同時把 MiniMax token plan 當作非本機備援。P10 先建立 runtime 檢查與資源規劃，避免直接下載重模型或硬接 API token。

## 2. 目標

新增 CLI：

```bash
guitar-tab-generation doctor-ai
guitar-tab-generation ai-resources
```

輸出本機 AI runtime 狀態、4090 資源 profile、模型路線與 MiniMax 備援政策。

## 3. 功能需求

1. `doctor-ai` 檢查：Python、平台、`nvidia-smi`、`ffmpeg`、PyTorch/CUDA 是否可用。
2. `doctor-ai --json` 輸出 machine-readable JSON。
3. `ai-resources` 輸出繁中 Markdown，包含：
   - 4090 24GB VRAM 假設
   - Local-first 模型表
   - Basic Pitch、Demucs、Essentia/librosa、CREPE/torchcrepe、本機 LLM
   - MiniMax Text / Music 2.6 / Lyrics / Cover 作為備援，不作為預設 source of truth
   - token/secret 不寫入 repo，只讀環境變數
4. 不新增重依賴。
5. 不呼叫 MiniMax API，不消耗 token。

## 4. 非目標

- 不下載模型。
- 不安裝 CUDA / PyTorch。
- 不實作 Basic Pitch / Demucs 真實推論。
- 不把 MiniMax token 寫入檔案或 git。

## 5. Definition of Done

實作狀態：已完成。CLI `doctor-ai` / `ai-resources`、unit/CLI tests、uv regression、runtime evidence 已通過。

- PRD + test spec 存在。
- 先新增 failing tests，再實作。
- `doctor-ai --json` 與 `ai-resources` 有測試。
- `uv run pytest -q` 通過。
- `uv run guitar-tab-generation doctor-ai --help` 與 `ai-resources --help` 通過。
- Feature 經 code review 後 merge `dev`，驗證，再 merge `main`。
