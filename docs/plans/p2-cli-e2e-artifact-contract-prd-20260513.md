# P2 PRD：CLI E2E Artifact Contract

日期：2026-05-13  
狀態：Ready for execution  
建議分支：`feature/cli-e2e-artifact-contract`

## 1. 背景

目前 pipeline 與 schema tests 已能驗證核心 contract，但 golden fixtures 需要被 CLI 端到端跑過，確認實際使用者命令會產生完整 artifact，而不是只驗單元函式或 sample JSON。

## 2. 目標

三個 MVP golden fixtures 都能透過 `uv run guitar-tab-generation transcribe ... --backend fixture` 產出完整、可驗證、可練歌審查的 artifact set。

## 3. 非目標

- 不導入真實 ML backend。
- 不開 URL 下載。
- 不改善 TAB 美觀；美觀放 P3。

## 4. 功能需求

1. CLI 對三個 fixtures 產出：
   - `audio_normalized.wav`
   - `arrangement.json`
   - `quality_report.json`
   - `tab.md`
   - `notes.json`
   - `chords.json`
   - `sections.json`
2. `arrangement.json` 通過 shared contract validator。
3. `quality_report.json` status 應為 passed，或若 warning 存在需與 `arrangement.json`、`tab.md` 一致。
4. URL policy gate 仍不得下載、不得產生假音訊 artifact。
5. Fixture metadata / rubric 必須被 quality gate 使用。

## 5. Acceptance Criteria

- `uv run pytest -q` 通過。
- 新增 integration/e2e tests 覆蓋三個 fixtures。
- 每個 fixture 的 artifact files 都存在且 JSON 可 parse。
- `tab.md` 包含 metadata、sections/chords/TAB、warning section 或明確無 warning。
