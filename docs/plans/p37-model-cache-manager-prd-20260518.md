# P37 Model Cache Manager PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P37 建立本機模型 cache manager，讓 v1.0 使用者能看見模型 cache 位置、版本/用途、磁碟使用與 smoke evidence，且 prune 預設只 dry-run。

交付：

- 新增 CLI：`guitar-tab-generation models list`。
- 新增 CLI：`guitar-tab-generation models doctor`。
- 新增 CLI：`guitar-tab-generation models prune --dry-run`。
- 建立 model manifest：Basic Pitch、Demucs、torchcrepe、Essentia、Ollama local LLM。
- 支援 `--cache-root` 測試 fixture，不讀寫 repo-tracked cache。
- `prune` 預設不刪除；若未來要真刪除需另開 opt-in scope。

## 2. 非目標

- 不下載模型。
- 不安裝 optional AI dependencies。
- 不執行 smoke tests。
- 不做 destructive prune。

## 3. 驗收標準

- `models --help`、`models list --help`、`models doctor --help`、`models prune --help` 可用。
- `models list --json --cache-root <fixture>` 回報每個 manifest model 的 cache path、exists、size bytes、smoke evidence。
- `models doctor --json` 回報 cache root 是否在 git repo 外、manifest 是否可解析。
- `models prune --dry-run --json` 只列出 unmanaged cache dirs / zero-size dirs，不刪檔。
- 沒有 `--dry-run` 時 prune 仍拒絕執行 destructive 行為。
