# P20 PR Code Review：torchcrepe F0 Calibration Adapter

日期：2026-05-16
分支：`feature/torchcrepe-f0-calibration`
範圍：artifact-first `f0-calibrate` CLI、optional torchcrepe runtime boundary、文件、測試。

## Review checklist

- 規格對齊：通過。實作符合 `docs/plans/p20-torchcrepe-f0-calibration-prd-20260516.md` 與 test spec。
- Basic Pitch 相容性：通過。P20 沒有替換或改變 `basic-pitch` backend 行為。
- Default backend 安全性：通過。`fixture` 仍是 default；`f0-calibrate` 是獨立 artifact command。
- 依賴衛生：通過。本階段沒有把 PyTorch / torchcrepe 加進 default 或 optional dependency group。
- Runtime boundary：通過。只有執行 `f0-calibrate` 時才 lazy import `torchcrepe`。
- GPU 安全：通過。CLI 預設 device 是 `cpu`；GPU 必須明確指定 `--device cuda:0` 或等價值。
- 失敗模式：通過。未安裝 torchcrepe 時回傳清楚 `BackendExecutionError`，不 silent fallback 或輸出假資料。
- 文件：通過。已新增英文與繁中文件。
- 本機衛生：通過。`.omx` 沒有被追蹤。

## Findings

沒有 blocking finding。

## 驗證證據

- `PYTHONPATH=src python3 -m pytest -q tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py` → red/green cycle 後 7 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/unit/test_torchcrepe_f0.py tests/e2e/test_cli_f0_calibrate.py tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py` → 17 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` → 155 passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -m compileall -q src tests` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help` → passed。
- `UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate --help` → passed。
- Missing runtime manual gate：artifact 有 `audio_normalized.wav` 與 `notes.json` 時，未安裝 torchcrepe 會 exit 1 並顯示清楚 optional runtime 訊息。
- `git diff --check` → passed。
- `git ls-files .omx` → 無追蹤檔案。

## 已知限制

- P20 刻意不安裝 torchcrepe，也不跑真實 torchcrepe inference。
- F0 calibration 較適合 solo/riff passages，不是 polyphonic transcription。
- 目前輸出是 sidecar artifact，尚未被 renderer/tutorial scoring 消費。
