# P26–P40 Ralph Command Plan

日期：2026-05-17
狀態：Planned
基線：P25 已合併並推進到 `main`。下一步從 `main` 開新 feature branch 做 P26。

## 執行原則

- 每一個 P 階段都用獨立 feature branch。
- 每一階段先補或更新 PRD / test spec；若涉及新依賴、外部工具、URL policy、模型 runtime、schema 破壞性變更，先補 ADR。
- 預設不新增 heavy dependency；需要時走 optional group / runtime gate。
- 所有 artifact 先走 sidecar / manifest，不把不確定輸出直接覆寫主 artifact。
- 每階段完成後跑 code review、PR into `dev`、stage review、再 merge `main`。

## 建議批次

1. MVP+ 收斂：P26–P27。
2. Beta AI sidecars：P28–P31。
3. Product shell：P32–P34。
4. v1.0 hardening：P35–P40。

## Ralph 指令

### P26：Stem-aware Basic Pitch Pipeline

```text
$ralph 使用 Ralph 完成 P26：依照 docs/plans/p26-stem-aware-basic-pitch-prd-20260517.md 與 docs/plans/p26-stem-aware-basic-pitch-test-spec-20260517.md，從 main 建立 feature/stem-aware-basic-pitch；新增 artifact-first `guitar-tab-generation transcribe-stem <artifact_dir> --backend basic-pitch --stem <name>`；讀取 P25 `stem_manifest.json`，對指定 stem 使用 fake Basic Pitch runtime 產生 `stem_notes/<stem>.notes.json` 與 metadata，provenance 標記 stem，不改 transcribe default，不 silent fallback 到 mix，不執行真實 Demucs；嚴格 SDD/TDD/git flow，用 uv；完成後開 PR into dev、跑 review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P27：Artifact Quality Scoring v2

```text
$ralph 使用 Ralph 完成 P27：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P27 範圍，從 main 建立 feature/artifact-quality-v2；先建立 P27 PRD/test-spec，實作 `quality_report.json` v2；合併 mix notes、stem_notes、f0_calibration、stem_manifest 與 warnings 成品質摘要，讓 viewer/interface 顯示 stem availability、pitch risk、backend confidence summary；不得把低信心結果包裝成確定答案，不改 P26 sidecar 輸出契約；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P28：Chord Recognition Backend

```text
$ralph 使用 Ralph 完成 P28：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P28 範圍，從 main 建立 feature/chord-recognition-backend；先建立 P28 PRD/test-spec 與必要 ADR，新增 artifact-first `guitar-tab-generation chord-detect <artifact_dir>` sidecar；產生或更新 `chords.json`，provenance 標記 backend/model/source/stem，低信心 chord 必須保留 warning；先用 deterministic/local feature baseline 或 fake runtime 測試，不新增 heavy dependency；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P29：Section Detection Backend

```text
$ralph 使用 Ralph 完成 P29：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P29 範圍，從 main 建立 feature/section-detection-backend；先建立 P29 PRD/test-spec，新增 artifact-first `guitar-tab-generation section-detect <artifact_dir>` sidecar；產生 `sections.json`，包含 section boundaries、confidence、provenance；viewer/interface 顯示 section confidence；低 confidence 不可 silent pass；使用 deterministic fixture/fake runtime 測試，不新增 heavy dependency；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P30：Fingering + Playability v2

```text
$ralph 使用 Ralph 完成 P30：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P30 範圍，從 main 建立 feature/fingering-playability-v2；先建立 P30 PRD/test-spec，改善 fingering/playability v2；加入指法 cost model / position shift / string preference / max stretch config，並消化 P26/P27 的 stem、pitch risk、confidence 訊號；低信心 note/stem 只影響建議與 warning，不宣稱自動更準；新增 golden riff snapshots 與 impossible stretch warnings；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P31：Local LLM Tutorial v2

```text
$ralph 使用 Ralph 完成 P31：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P31 範圍，從 main 建立 feature/local-llm-tutorial-v2；先建立 P31 PRD/test-spec 與必要 ADR，實作 Local LLM Tutorial v2；LLM 只能基於 artifacts 產生教學，不作 truth source，輸出必須引用 artifact provenance，低信心、stem bleed、pitch risk 以 warning 呈現；無 LLM runtime 時清楚 skip/error，不 fallback 到假教學；使用 fake LLM 測 prompt builder/e2e，不要求 default CI 跑真實 LLM；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P32：Web UI MVP

```text
$ralph 使用 Ralph 完成 P32：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P32 範圍，從 main 建立 feature/web-ui-mvp；先建立 P32 PRD/test-spec 與 UI/architecture ADR，實作 artifact-first 本機 Web UI MVP：local audio upload、job status、artifact browser、TAB/quality/DAW/tutorial tabs；UI 不重寫 pipeline，只呼叫 CLI/service boundary 或讀 artifacts；使用 Playwright/contract tests 驗證主要流程；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P33：Job Queue + GPU Resource Guard

```text
$ralph 使用 Ralph 完成 P33：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P33 範圍，從 main 建立 feature/job-queue-gpu-guard；先建立 P33 PRD/test-spec 與 resource scheduler ADR，實作 job queue、VRAM guard、one-GPU-task-at-a-time lock、cancel/resume/logs；保護共享 RTX 4090，GPU-sensitive jobs 必須 explicit opt-in，低 VRAM 時 defer/skip 並保留證據；使用 fake GPU probe/queue tests，不要求 default CI 佔用 GPU；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P34：Legal URL / YouTube Path

```text
$ralph 使用 Ralph 完成 P34：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P34 範圍，從 main 建立 feature/legal-url-path；先建立 P34 PRD/test-spec 並更新 legal URL ADR，實作 `ingest-url` policy gate；只允許使用者明確權利聲明且本機工具存在時執行，所有 URL artifacts 必須留下 source policy record；no-rights 與 unsupported URL 必須 blocked，不可任意下載 YouTube/URL；使用 stub fixtures，不做真實下載；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P35：Evaluation Dataset + Metrics

```text
$ralph 使用 Ralph 完成 P35：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P35 範圍，從 main 建立 feature/eval-dataset-metrics；先建立 P35 PRD/test-spec，建立 evaluation fixtures manifest 與 note onset/pitch/chord/section metrics；產生 regression report 與 baseline threshold gate，讓品質可量化而不是只靠 demo 感覺；fixture 必須有 rights/rubric record，不引入未授權資料；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P36：DAW Export Quality v2

```text
$ralph 使用 Ralph 完成 P36：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P36 範圍，從 main 建立 feature/daw-export-quality-v2；先建立 P36 PRD/test-spec，強化 DAW export：tempo map、markers/sections、track naming、manifest versioning、import checklist validation；保持通用 MIDI/MusicXML 優先，不承諾專有 GarageBand/Logic project；新增 DAW manifest schema 與 track/marker tests；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P37：Model Cache Manager

```text
$ralph 使用 Ralph 完成 P37：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P37 範圍，從 main 建立 feature/model-cache-manager；先建立 P37 PRD/test-spec 與 cache safety ADR，實作 `models list`、`models doctor`、`models prune --dry-run` 與 model manifest；預設只 dry-run，不做 destructive prune；管理模型版本、cache size、smoke evidence；使用 cache discovery fixtures，不下載 heavy models；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P38：Project Workspace

```text
$ralph 使用 Ralph 完成 P38：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P38 範圍，從 main 建立 feature/project-workspace；先建立 P38 PRD/test-spec 與 workspace schema ADR，實作多歌曲 workspace、song/project metadata、artifact history、workspace index 與 interface project list；不得破壞現有單 artifact_dir flow；新增 index update 與 multiple artifact dirs tests；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P39：Packaged Local App

```text
$ralph 使用 Ralph 完成 P39：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P39 範圍，從 main 建立 feature/packaged-local-app；先建立 P39 PRD/test-spec，實作 setup wizard、Docker Compose stable profiles、local app command、dependency doctor；所有 installer/setup 動作預設 dry-run 或明確 opt-in，不自動安裝 heavy AI dependencies；驗證 `docker compose config`、setup dry-run、CLI doctor；嚴格 SDD/TDD/git flow，用 uv；完成後 PR into dev、review、merge dev、stage review、merge main；非必要不要找使用者。
```

### P40：v1.0 Release Hardening

```text
$ralph 使用 Ralph 完成 P40：依照 docs/plans/remaining-feature-master-plan-20260516.md 的 P40 範圍，從 main 建立 release/v1.0-hardening；先建立 P40 PRD/test-spec/release checklist，完成 security/legal review、docs 完整化、demo assets、CI matrix、clean clone setup smoke；禁止新增 feature scope，專注 hardening、文件、測試、release readiness；跑 full regression、docs link check、packaged setup dry-run；完成後 PR into dev、review、merge dev、stage review、merge main，並產出 v1.0 release report；非必要不要找使用者。
```
