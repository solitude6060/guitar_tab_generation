# v1.0 MVP Completion Plan

日期：2026-05-18
狀態：Planned
基線：`main` / `dev` 已在 P27 `quality-report` v2 後同步。

## 1. 完成定義

本計畫把 v1.0 MVP 定義為「非技術使用者可用的本機、合法音訊、artifact-first 吉他 TAB 產生器」，而不是只完成 CLI demo。

v1.0 MVP 完成必須同時滿足：

- Signal：和弦、段落、指法、品質摘要都能從 artifact 產出，低信心以 warning 表示。
- Product shell：有本機 Web UI / job queue / artifact browser，可跑本機工作流並讀 artifacts。
- Safety：GPU / heavy runtime / URL / model cache 都有明確 opt-in gate，不 silent fallback。
- Evidence：evaluation metrics、release report、review docs、CI、本地驗證都可追溯。
- Distribution：setup / package / docs 足以讓使用者在本機 dry-run 或啟動。

## 2. 外部審查輸入

- Gemini CLI 已完成 scope review，artifact：`.omx/artifacts/gemini-v1-mvp-scope-review-20260517T162138Z.md`。
- `claude-mm` / `codex-mm` binary 不存在；改用已安裝的 `claude` CLI 作為 fallback，artifact：`.omx/artifacts/claude-mm-v1-mvp-scope-review-20260517T162138Z.md`。

採納 Gemini 建議：

- P28/P29/P30/P32/P33 是 v1.0 必備。
- P35 evaluation metrics 提前，作為 signal work 的量化 gate。
- P31/P34 仍納入 v1.0，但只能用 gated/fake-runtime/default-safe 路徑，不讓 LLM 或 URL 成為 truth/source bypass。

Claude fallback 提出相反建議：把 v1.0 縮成 P35-lite + P39-lite + P40，並把 P28-P34、P36-P38 移到 v1.1。此建議有助於控制 release 風險，但本輪使用者明確要求「v1.0 MVP 所有功能完成」，且 repo 既有 P28-P40 roadmap 已把這些列為產品化路徑。因此本計畫將 Claude 建議記為 scope-risk challenge，不採用 scope reduction；若未來使用者明確改成 v1.0-lite，才改走該路線。

## 3. 實作順序

### Lane A：Signal Foundation

1. **P28 Chord Detection Sidecar**
   - `chord-detect <artifact_dir>`
   - 讀 `notes.json` / `stem_notes` / `arrangement.json`
   - 寫 `chords.json`
   - viewer/interface 顯示 chord sidecar confidence

2. **P29 Section Detection Sidecar**
   - `section-detect <artifact_dir>`
   - deterministic baseline：依 duration / existing sections / chord changes 產生 sections
   - 寫 `sections.json`

3. **P35 Evaluation Dataset + Metrics**
   - 提前到 P30 前或與 P30 並行
   - 建立 fixture/eval manifest、note/chord/section/playability metrics、regression report

4. **P30 Fingering + Playability v2**
   - greedy/cost-model first，不先做複雜 DP
   - position shift、max stretch、string preference warnings

5. **P31 Local LLM Tutorial v2**
   - fake LLM default tests
   - LLM 只讀 artifacts，不作 truth source

### Lane B：Product Shell

6. **P32 Web UI MVP**
   - artifact-first 本機 UI
   - 不重寫 pipeline，只呼叫 CLI/service boundary 或讀 artifacts
   - 初版優先 stdlib/static server，除非另有依賴 ADR

7. **P33 Job Queue + GPU Resource Guard**
   - one-GPU-task-at-a-time lock
   - fake GPU probe tests
   - job logs / cancel / resume evidence

8. **P37 Model Cache Manager**
   - `models list`
   - `models doctor`
   - `models prune --dry-run`

9. **P38 Project Workspace**
   - workspace index
   - multi-song metadata/history
   - 不破壞單 `artifact_dir` flow

### Lane C：Compliance / Distribution / Release

10. **P34 Legal URL / YouTube Path**
    - `ingest-url` policy gate
    - 不做真實下載
    - 權利聲明 / unsupported URL / source policy record

11. **P36 DAW Export Quality v2**
    - tempo map、markers/sections、track naming、manifest versioning

12. **P39 Packaged Local App**
    - setup wizard dry-run
    - Docker Compose stable profiles
    - dependency doctor

13. **P40 v1.0 Release Hardening**
    - release checklist
    - security/legal review
    - clean clone setup smoke
    - v1.0 release report

## 4. 每階段固定交付

每個 P 階段都必須：

- 從 `main` 建立獨立 feature branch。
- 先建立 PRD / test spec；若新增 dependency、URL、runtime、schema 破壞性變更，先建立 ADR。
- TDD：先 red test，再最小實作，再 refactor/deslop。
- 用 fake/deterministic runtime 覆蓋 default CI；真實 heavy runtime 只做 manual/optional smoke。
- PR into `dev`，code review，修 blocker。
- merge `dev` 後跑 stage validation。
- merge `main` 後跑 main validation，確認 CI。
- 寫 review / stage docs。

## 5. v1.0 完成驗證

v1.0 MVP 只有在 P40 完成後才能宣稱完成。最終 gate：

```bash
uv sync --group dev
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe --help
uv run guitar-tab-generation chord-detect --help
uv run guitar-tab-generation section-detect --help
uv run guitar-tab-generation quality-report --help
uv run guitar-tab-generation interface --help
uv run guitar-tab-generation export --help
uv run guitar-tab-generation models --help
uv run guitar-tab-generation workspace --help
uv run guitar-tab-generation setup --help
```

Manual/demo gate：

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation chord-detect /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation section-detect /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation quality-report /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation view /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation interface /tmp/guitar-tab-v1-demo
uv run guitar-tab-generation export /tmp/guitar-tab-v1-demo --format daw
```

Completion audit 必須包含：

- P28-P40 prompt-to-artifact checklist。
- 所有 PR / merge commit / CI run IDs。
- full regression output。
- advisor artifacts。
- security/legal/release review docs。
