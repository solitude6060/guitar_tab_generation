# P35 Evaluation Dataset + Metrics Test Spec

日期：2026-05-18
狀態：Planned

## 1. Unit Tests

- `test_build_eval_report_passes_with_fixture_artifacts`
  - 使用臨時 manifest + artifact outputs。
  - 驗證 summary、fixture metrics、thresholds。
- `test_build_eval_report_fails_missing_rubric_record`
  - 缺 rubric record 時記錄 failure。
- `test_build_eval_report_fails_missing_artifacts`
  - 缺 arrangement / quality report 時記錄 failure。
- `test_write_eval_report_defaults_to_artifact_root`
  - 寫入 `<artifact_root>/eval_report.json`。

## 2. CLI / E2E Tests

- `eval-report --help` 顯示 artifact_root、--manifest、--out。
- 先用 fixture backend 產出三個 artifact outputs，再跑 `eval-report`。
- 驗證 `eval_report.json` summary passed，且包含 note/chord/section/playability metrics。

## 3. Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation eval-report --help
```
