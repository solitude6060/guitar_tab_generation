# P25 PR Code Review — Demucs Stem Separation Sidecar（繁中）

日期：2026-05-17
分支：`feature/demucs-stem-sidecar`
審查範圍：

- `src/guitar_tab_generation/stem_separation.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_stem_separation.py`
- `tests/e2e/test_cli_separate_stems.py`
- `docs/plans/p25-demucs-stem-sidecar-prd-20260517.md`
- `docs/plans/p25-demucs-stem-sidecar-test-spec-20260517.md`
- `docs/plans/p26-stem-aware-basic-pitch-prd-20260517.md`
- `docs/plans/p26-stem-aware-basic-pitch-test-spec-20260517.md`
- `docs/plans/post-p25-execution-plan-20260517.md`
- `docs/plans/remaining-feature-master-plan-20260516.md`

## 結論

APPROVE。

## Findings

### Critical

無。

### High

無。

### Medium

無。

### Low

無。

## 架構評估

狀態：CLEAR。

實作將 Demucs 保持在 artifact-first sidecar，沒有改動 `transcribe` 預設流程。`separate-stems` 要求既有 `audio_normalized.wav`，執行 runtime 前先檢查 P24 Demucs gate，輸出 `stems/` 與 `stem_manifest.json`，並明確記錄 no silent fallback。CPU 是預設路徑；CUDA 必須明確 opt-in。最後一輪 architect review 曾抓到一個 blocker：環境中有 `GPU_TESTS_ENABLED=1` 時，CPU run 仍可能讓 P24 gate probe GPU。已修正為 CPU 模式會清理傳給 gate 的 GPU env，並新增使用真實 P24 gate 與 injected probes 的 regression。

P26 規劃也已和 P25 實作切開：stem-aware Basic Pitch 規劃為 `transcribe-stem <artifact_dir> --backend basic-pitch --stem <name>`，輸出 `stem_notes/<stem>.notes.json`，不自動合併進主 artifact。

## 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 188 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_stem_separation.py tests/e2e/test_cli_separate_stems.py` → 11 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed，並列出 `separate-stems`。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation separate-stems --help` → passed，並顯示 `--device`、`--allow-gpu`、`--min-free-vram-mb`。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe --help` → passed；`fixture` 仍是預設，沒有 stem option。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation demucs-gate --json` → safe planned gate；`gpu_enabled=false`、`command_executed=false`。
- `git log --format=%B HEAD` hygiene check → amend 後沒有精確禁用的 OmX coauthor 片語。
- `git ls-files .omx` hygiene check → 沒有追蹤 `.omx`。

## 剩餘風險

- default gates 刻意不執行真實 Demucs source separation。P25 只以 fake runtime 與 P24 gate reuse 驗證 sidecar contract。
- 真實 Demucs CLI 輸出 layout 仍有環境相依風險；adapter 預期 `<output>/<model>/<audio-stem>/*.wav`。
- P26 在 P27 定義 quality reconciliation 前，不應把 stem notes 直接合併進主 `notes.json`。
