# P27 Test Spec：Artifact Quality Scoring v2

日期：2026-05-18
狀態：Planned

## 1. Unit tests

- `tests/unit/test_artifact_quality_v2.py`
  - 無 optional sidecar 時仍輸出 v2，並標記 stem/F0 unavailable。
  - 讀取 `stem_manifest.json` 後列出可用 stems。
  - 讀取 `stem_notes/<stem>.notes.json` 後產生 note count、平均 confidence、warning count。
  - 讀取 `f0_calibration.json` 後產生 pitch risk summary。
  - backend confidence summary 依 backend/stem 聚合，不宣稱 correctness。

## 2. E2E tests

- `tests/e2e/test_cli_quality_report_v2.py`
  - `quality-report --help` 顯示 `artifact_dir` 與 `--out`。
  - fixture artifact + optional sidecars → 寫出 v2 `quality_report.json`。
  - `view` 輸出包含 stem availability、pitch risk、backend confidence summary。
  - `interface` 輸出包含同等 quality summary。
  - `transcribe --help` 不新增 `--stem` 或自動 quality refresh option。

## 3. Regression gates

```bash
UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation quality-report --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe --help
```

## 4. Red-first expectations

第一個 red test 鎖定 `quality-report --help` 尚不存在。第二個 red test 鎖定 v2 report 不含 stem/F0/backend 摘要。
