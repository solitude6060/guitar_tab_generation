# ADR: P38 Workspace Schema

日期：2026-05-18
狀態：Accepted

## Context

v1.0 需要一個可讓 UI / job queue / exports 共享的 project boundary，但既有 CLI 已以單一 `artifact_dir` 為核心，不能被 workspace schema 綁死。

## Decision

P38 使用 workspace-local `workspace.json`：

- `schema_version: 1`
- `project`: name、created_at、updated_at
- `songs`: song_id、title、artifact_dir、source、quality_status、overall_confidence、history

Workspace index 可從 `arrangement.json` / `quality_report.json` 掃描 artifact dirs。`add-artifact` 可登錄 workspace 外部 artifact dir，但只記相對路徑或原始 path，不搬移檔案。

## Rejected

- 把所有 artifact 強制搬進 workspace：會破壞現有單 artifact_dir workflow。
- SQLite project DB：P38 的資料量小，JSON 較容易 review 與手動修復。
- UI 直接維護自己的 project state：會讓 artifact-first 邊界分裂。

## Consequences

- `workspace.json` 是可讀寫的本機 index，不是唯一 truth source；artifact files 仍是最終產出。
- 後續 P39 packaged app 可以把此 schema 當作啟動與 project list 的資料來源。
