# ADR 20260517：Demucs Runtime Install Gate 先於 Stem Separation

狀態：Accepted
日期：2026-05-17

## 背景

Demucs 會引入 PyTorch runtime、模型 cache、GPU VRAM 壓力與可能的 model weight 下載。若直接在 P25 實作 `separate-stems`，容易讓 default dev/CI、共享 RTX 4090 主機或使用者 artifact contract 同時承受太多風險。

## 決策

先在 P24 實作 `demucs-gate`，只負責 Demucs optional runtime planning 與 install gate：

- default 不下載、不用 GPU、不分軌。
- runtime check 必須明確 opt-in：`--check-runtime`。
- GPU gate 必須明確 opt-in：`--allow-gpu` 或 `GPU_TESTS_ENABLED=1`。
- free VRAM 未達門檻時回報 `skipped`，不執行 Demucs command。
- missing runtime 回報清楚錯誤與 `uv sync --group torch-ai`。
- fallback policy 固定為 `no_silent_fallback`。

## 後果

- P25 可以重用相同 gate，再接上 `separate-stems` artifact contract。
- `transcribe` 在 P24 完全不變，fixture 仍是預設 backend，Basic Pitch 仍需 explicit opt-in。
- 使用者可以先驗證安裝與 GPU 資源，不需要真的跑 separation。

## 被拒絕方案

- 在 P24 直接新增 `separate-stems`：會跨入 P25 範圍，且需要 stem artifact contract 與 fake Demucs runtime 測試。
- 在 `transcribe` 自動使用 Demucs：違反 artifact-first sidecar 邊界，且會改變預設行為。
- missing Demucs 時 fallback 到 mix：會產生看似成功但 provenance 錯誤的結果。
