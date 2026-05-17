# Post-P25 Execution Plan：P26–P31

日期：2026-05-17
狀態：Planned
前提：P25 `separate-stems` 已完成實作、PR #8 已合併進 `dev`，並已透過 stage review 推進到 `main`。

## 1. 目前可用基線

- `transcribe` 保持 fixture default，可 explicit `--backend basic-pitch`。
- `f0-calibrate` 以 artifact sidecar 產生 `f0_calibration.json`。
- `separate-stems` 以 artifact sidecar 產生 `stems/` 與 `stem_manifest.json`。
- P24 gate 保留 no-download、no-GPU default 與 no-silent-fallback policy。

## 2. 下一階段排序

### P26：Stem-aware Basic Pitch Pipeline

目的：讓 Basic Pitch 可明確讀取 stem artifact，先輸出 `stem_notes/<stem>.notes.json`，不直接覆寫主 artifact。

建議分支：`feature/stem-aware-basic-pitch`

停止條件：

- `transcribe-stem <artifact_dir> --backend basic-pitch --stem <name>` contract 完成。
- provenance 正確標記 stem。
- stem 不存在時不 fallback 到 mix。
- `transcribe --help` 仍無 `--stem`。

### P27：Artifact Quality Scoring v2

目的：把 mix notes、stem notes、F0 calibration、stem availability 與 warnings 合併成品質摘要。

建議分支：`feature/artifact-quality-v2`

停止條件：

- `quality_report.json` v2 schema。
- 顯示 stem availability、pitch risk、backend confidence summary。
- viewer/interface 可讀 quality v2，但不把 low confidence 包裝成確定答案。

### P28：Chord Recognition Backend

目的：新增 chord sidecar，先走 deterministic 或 local feature baseline，再評估 heavy model。

建議分支：`feature/chord-recognition-backend`

停止條件：

- `chord-detect <artifact_dir>` sidecar。
- `chords.json` provenance 升級。
- low-confidence chord warning 不可被吞掉。

### P29：Section Detection Backend

目的：把 verse/chorus/solo/bridge 從 fixture/safe baseline 推向可測 sidecar。

建議分支：`feature/section-detection-backend`

停止條件：

- `section-detect <artifact_dir>` sidecar。
- section confidence 與 boundary provenance。
- interface 顯示 section confidence。

### P30：Fingering + Playability v2

目的：改善 solo/riff 指法與可彈性，消化 P26/P27 產生的新 confidence 訊號。

建議分支：`feature/fingering-playability-v2`

停止條件：

- 低 confidence stem/pitch notes 影響 playability 建議。
- regression snapshots 防止 tab layout 退化。

### P31：Local LLM Tutorial v2

目的：本機 LLM 只基於 artifacts 產生教學，不作 truth source。

建議分支：`feature/local-llm-tutorial-v2`

停止條件：

- LLM 輸出引用 artifact provenance。
- 低信心、stem bleed、pitch risk 以 warning 呈現。
- 無 LLM runtime 時清楚 skip/error，不 fallback 到假教學。

## 3. 推薦下一條 Ralph 指令

```text
$ralph 使用 Ralph 完成 P26：依照 docs/plans/p26-stem-aware-basic-pitch-prd-20260517.md 與 docs/plans/p26-stem-aware-basic-pitch-test-spec-20260517.md，新增 artifact-first `guitar-tab-generation transcribe-stem <artifact_dir> --backend basic-pitch --stem <name>`；讀取 P25 `stem_manifest.json`，對指定 stem 使用 fake Basic Pitch runtime 產生 `stem_notes/<stem>.notes.json`，provenance 標記 stem，不改 transcribe default，不 silent fallback 到 mix，不執行真實 Demucs；嚴格 SDD/TDD/git flow，用 uv；非必要不要找使用者。
```

## 4. 風險與前置處理

- P25 commit hook 衝突已處理；後續 commit 仍需維持 Lore commit 格式，且不可加入 OmX coauthor trailer。
- P26 不應把 stem notes 直接合併回主 `notes.json`；合併策略留給 P27。
- P27 前不要宣稱 stem notes 比 mix notes 更準；只能呈現 provenance 與 quality evidence。
- P28/P29 若引入新模型或 heavy dependency，必須先補 ADR 與 optional runtime gate。
