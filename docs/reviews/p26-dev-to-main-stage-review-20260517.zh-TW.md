# P26 Dev-to-Main Stage Review

日期：2026-05-17
範圍：PR #9 merge commit `4d64d36778e73931a581341647fab0165ec94a78`
狀態：準備推進 `main`

## Dev stage 驗證

- `uv sync --group dev`：passed
- `uv run pytest -q`：200 passed
- `uv run guitar-tab-generation --help`：passed，列出 `transcribe-stem`
- `uv run guitar-tab-generation transcribe-stem --help`：passed，列出 `artifact_dir`、`--backend`、`--stem`
- `uv run guitar-tab-generation transcribe --help`：passed，未新增 `--stem`
- GitHub CI：`25995613108` success，branch `dev`，SHA `4d64d36778e73931a581341647fab0165ec94a78`

## 風險檢查

- P26 沒有把 stem notes 合併回 `arrangement.json`。
- P26 沒有改 `transcribe` default。
- P26 沒有執行真實 Demucs。
- P26 default tests 使用 fake Basic Pitch runtime，不要求 optional `ai` dependency。
- 已補 unsafe stem name regression，避免 artifact metadata 導致 sidecar path traversal。

## 結論

`dev` 上的 P26 符合 stage gate，可以 merge into `main` 後再跑 main validation。
