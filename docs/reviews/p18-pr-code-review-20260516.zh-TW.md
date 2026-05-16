# P18 PR Code Review：Basic Pitch 本機 Backend MVP

日期：2026-05-16
分支：`feature/basic-pitch-backend`
範圍：Basic Pitch 音符辨識 backend、可選 uv `ai` dependency group、文件、測試。

## Review checklist

- 規格對齊：通過。實作符合 `docs/plans/p18-basic-pitch-local-backend-prd-20260516.md` 與 test spec。
- 依賴範圍：通過。只在可選 `ai` group 加入 `basic-pitch` 與相容性所需的 `setuptools>=68,<81`。
- Backend 行為：通過。`fixture` 仍是預設 deterministic backend；`basic-pitch` 必須明確指定。
- 失敗模式：通過。Basic Pitch 未安裝時會丟出清楚的 `BackendExecutionError`，不會 silent fallback 到 fixture。
- Provenance：通過。輸出的 note events 會包含 `backend=basic-pitch`、model、runtime、stage、stem metadata。
- GPU 安全：通過。真實 smoke 驗證使用 `CUDA_VISIBLE_DEVICES=''`，避免佔用共享 GPU。
- 本機衛生：通過。`.omx` 沒有被追蹤。

## Findings

沒有 blocking finding。

## 驗證證據

- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_basic_pitch_backend.py tests/integration/test_pipeline_backend_selection.py tests/e2e/test_cli_basic_pitch_backend.py tests/unit/test_ai_backends.py tests/unit/test_model_smoke.py` → 18 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 138 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed。
- `CUDA_VISIBLE_DEVICES='' UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-p18-basic-pitch-final` → 成功輸出 artifacts，60 個 notes，`quality_status=passed`。
- `git diff --check` → passed。
- `git ls-files .omx` → 無追蹤檔案。

## 已知限制

- Basic Pitch 目前只負責 note transcription；節奏、和弦、段落仍使用既有安全本機路徑。
- Basic Pitch 官方 Python 套件使用 TensorFlow runtime。
- 目前專案環境未安裝 `ruff`，本階段未為了 lint 額外新增依賴。
