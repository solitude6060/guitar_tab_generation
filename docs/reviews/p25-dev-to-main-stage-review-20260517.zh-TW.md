# P25 Dev-to-Main Stage Review — Demucs Stem Separation Sidecar（繁中）

日期：2026-05-17
來源分支：`dev`
目標分支：`main`
範圍：

- PR #8 在 `dev` 的 merge commit：`03e4b1b77e0094a9e46840524b22b9695f5097b9`
- P25 `separate-stems` sidecar 實作
- P26 / P26-P31 後續規劃文件
- P25 review artifacts

## 結論

APPROVE，可合併到 `main`。

## Stage checks

- PR #8 已合併進 `dev`。
- 本機 `dev` 已與 `origin/dev` 同步。
- `main..dev` 只包含 P25 merge 內容，沒有無關工作。
- `.omx` 未被追蹤。
- branch history 不含精確禁用的 OmX coauthor 片語。

## `dev` 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 188 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `git diff --check HEAD` → passed。

## 剩餘風險

- 真實 Demucs source separation 仍是 opt-in runtime path，default gates 沒有執行。
- P26 必須維持 stem-aware Basic Pitch sidecar，直到 P27 定義 quality reconciliation。
