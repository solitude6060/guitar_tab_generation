# ADR: P37 Model Cache Safety

日期：2026-05-18
狀態：Accepted

## Context

v1.0 需要管理 optional AI model cache，但 default CI 與一般 CLI 不能下載 heavy models、安裝 optional runtimes 或刪除使用者資料。

## Decision

P37 model cache manager 使用只讀 discovery：

- 預設 base cache root：`~/.cache/guitar-tab-generation`。
- Manifest 可指向 `models/<backend>` 與 `torch-models/<backend>`，對齊既有 model-smoke / Demucs / torch runtime gate。
- CLI 支援 `--cache-root` 以便測試與手動檢查。
- Model manifest 由 repo 程式碼定義，描述 model id、label、cache subdir、runtime 與 optional status。
- `models prune` 必須顯式 `--dry-run`，否則回傳錯誤；本階段不提供 destructive prune。
- Smoke evidence 只讀取 cache dir 內的 `smoke.json`，不執行 smoke。

## Rejected

- 自動下載缺少的模型：會違反 default-safe / no-heavy-runtime policy。
- 真實刪除 cache：需要更嚴格的保護與使用者確認，不屬於 P37。
- 讀取第三方 package cache 內部格式：不同 backend 版本差異大，P37 先用 repo manifest 管理路徑與證據。

## Consequences

- 使用者可以看到 cache 健康狀態與可清理候選，但不能透過 P37 直接刪除。
- 後續若要實作 destructive prune，必須新增 explicit opt-in、path allowlist、測試與 review。
