# P4 Plan：Legal URL Path ADR

日期：2026-05-13  
狀態：Deferred planning  
建議分支：`plan/legal-url-path-adr`

## 目標

保留貼 URL 的產品願景，但只先完成合規設計與防回歸測試。P4 不實作任意下載。

## 交付

1. `docs/adr/YYYYMMDD-legal-url-input-policy.md`
2. URL policy tests：未授權 URL 必須被拒絕。
3. 文件更新：說明合法替代流程，包括 user-provided audio、allowlist、rights attestation。

## Hard fail

- 任意 URL 下載 code。
- `--i-own-rights` 直接繞過 policy gate。
- 未記錄 audit/provenance。
