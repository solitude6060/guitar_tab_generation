# P34 Legal URL / YouTube Path PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P34 回應 URL / YouTube 來源需求，但 v1.0 不開任意下載。此階段只建立可測 policy gate 與 source policy artifact。

交付：

- 新增 CLI：`guitar-tab-generation ingest-url <url> --out <artifact_dir>`。
- 沒有 `--i-own-rights` 一律 blocked。
- 任意 YouTube / unsupported URL 一律 blocked。
- 測試用 owned sample URL 只走 stub，不做網路下載。
- 所有結果寫入 `source_policy.json` 或 `policy_gate.txt`。

## 2. 非目標

- 不下載 YouTube。
- 不呼叫 yt-dlp / browser / network。
- 不把 URL ingestion 接進 `transcribe` default。

## 3. 驗收標準

- `ingest-url --help` 可用。
- no-rights URL 回傳 blocked 並寫 `policy_gate.txt`。
- unsupported URL 即使宣告權利也 blocked。
- fixture owned sample URL 產生 `source_policy.json`，provenance 標示 `stub_only`。
