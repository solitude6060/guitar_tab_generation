# ADR: P34 Legal URL Policy

日期：2026-05-18
狀態：Accepted

## Context

使用者會自然提供 YouTube 或網路音訊 URL，但 v1.0 MVP 必須維持 local-audio-first 與 rights-first，不可任意下載第三方內容。

## Decision

P34 新增 `ingest-url` policy gate：

- 沒有 `--i-own-rights` 就 block。
- YouTube 與一般 URL 在 v1.0 仍 block。
- 只有測試 fixture URL `https://example.com/guitar-tab-generation/owned-sample.wav` 可走 stub，且不下載網路內容。
- 成功或失敗都留下 policy artifact。

## Rejected

- 直接整合 yt-dlp：法律與產品風險過高。
- 只靠 CLI help 警告：不可驗證，且容易被誤用。

## Consequences

- v1.0 可展示 URL path 的合法邊界，但不承諾真實下載。
- 後續若要支援真實下載，必須新增本機工具檢查、權利聲明、來源記錄與法律 review。
