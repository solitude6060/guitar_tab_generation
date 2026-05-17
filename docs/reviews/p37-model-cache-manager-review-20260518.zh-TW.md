# P37 Model Cache Manager Review

日期：2026-05-18
範圍：`feature/model-cache-manager`

## 結論

未發現 blocker。P37 交付只讀 model cache manager：`models list`、`models doctor`、`models prune --dry-run` 均不下載模型、不執行 smoke、不刪除 cache。Manifest 對齊既有 cache family：`models/<backend>` 與 `torch-models/<backend>`。

## 檢查項

- CLI：新增 `guitar-tab-generation models list/doctor/prune`。
- Manifest：包含 Basic Pitch、Demucs htdemucs、torchcrepe、Essentia、Ollama local LLM。
- Discovery：回報 cache path、exists、size bytes、`smoke.json` evidence。
- Doctor：檢查 cache root 是否在 repo 內，避免追蹤 heavy cache。
- Prune：P37 僅允許 `--dry-run`，未提供 destructive delete。
- Safety：不下載 heavy models、不安裝 optional dependencies、不 probe GPU。

## 驗證證據

- `uv run pytest tests/unit/test_model_cache.py tests/e2e/test_cli_models.py -q`：9 passed。
- `uv sync --group dev`：通過。
- `uv run pytest -q`：262 passed。
- `uv run python -m compileall -q src tests`：通過。
- `git diff --check HEAD`：通過。
- `uv run guitar-tab-generation models --help`：列出 list/doctor/prune。
- `uv run guitar-tab-generation models list --help`：列出 `--cache-root`、`--json`。
- `uv run guitar-tab-generation models doctor --help`：列出 `--cache-root`、`--json`。
- `uv run guitar-tab-generation models prune --help`：列出 `--dry-run`。
- 手動 demo：`/tmp/guitar-tab-p37-demo-20260517T174301Z`，`models list` 讀到 `models/basic-pitch` 與 smoke evidence；`models prune --dry-run` 只列出 unmanaged `old-model`，未刪檔。

## 外部審查工具狀態

- `gemini --help` 可執行；本 session 非互動 review 嘗試卡在 browser authentication prompt，未產生可用審查結果。
- `claude-mm`：本機 `command -v claude-mm` 無結果，未安裝或不在 `PATH`。

## 剩餘風險

- P37 不做真實 prune；若未來要刪除 cache，需新增 explicit opt-in、allowlist 與 crash-safe tests。
- Manifest 是 repo 內靜態資料；後續新 backend 需要同步新增 manifest entry。
