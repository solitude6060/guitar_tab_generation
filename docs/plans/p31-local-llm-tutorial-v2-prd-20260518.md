# P31 Local LLM Tutorial v2 PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P31 強化 tutorial，但 LLM 只能基於 artifacts 產生 coaching text，不能成為 notes/chords/sections 的 truth source。

交付：

- `tutorial <artifact_dir> --llm-backend fake` 產生 deterministic fake LLM coaching notes。
- 預設 `tutorial` 不跑 LLM。
- `--llm-backend local` 在 runtime 未實作時清楚失敗，不 silent fallback。
- LLM coaching notes 必須引用 artifact source，例如 `arrangement.json`、`quality_report.json`、`tab.md`。

## 2. 非目標

- 不接真實 LLM API。
- 不讓 LLM 修改 notes/chords/sections。
- 不新增 dependency。

## 3. 驗收標準

- `tutorial --help` 顯示 `--llm-backend`。
- default tutorial 不含 LLM coaching section。
- fake backend 產生可重現 coaching section 並含 artifact citations。
- local backend missing 時 exit code 1 且不寫入 tutorial。
