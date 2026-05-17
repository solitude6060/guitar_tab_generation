# P35 Evaluation Dataset + Metrics Review

日期：2026-05-18
狀態：本地審查通過，外部 advisor 受阻延後

## 範圍

本次審查涵蓋：

- `docs/plans/p35-evaluation-dataset-metrics-prd-20260518.md`
- `docs/plans/p35-evaluation-dataset-metrics-test-spec-20260518.md`
- `src/guitar_tab_generation/evaluation_metrics.py`
- `src/guitar_tab_generation/cli.py`
- `tests/unit/test_evaluation_metrics.py`
- `tests/e2e/test_cli_eval_report.py`

## 審查結論

P35 已建立 v1.0 MVP 的 baseline evaluation gate：

- `eval-report <artifact_root> --manifest <manifest>` 會讀取 fixture manifest、rights/rubric record、artifact outputs。
- report 包含 note/chord/section/playability metrics。
- 缺少 rights、rubric、artifact、quality failure、低於 threshold 的 metrics 都會進入 machine-readable failures。
- 沒有新增外部資料、模型下載、GPU 或網路依賴。

## 已驗證的風險點

- rubric scores parser 可處理缺少 `scores` object 的資料，不會因非 dict 崩潰。
- low confidence note/chord/section 會讓 eval gate failed，而不是只留在 summary。
- placeholder rubric 只作 regression baseline；文件明確標註不代表最終人工音樂驗收。

## 外部 advisor 狀態

本 Ralph run 已在 P28 嘗試外部 advisor：

- `gemini` 停在瀏覽器登入提示。
- `claude-mm` binary 不存在。
- `claude` 回傳 API connection refused。

P35 未重複已知會卡住的外部 review；P40 release hardening 時需重新嘗試。

## 驗證證據

```bash
uv run pytest tests/unit/test_evaluation_metrics.py tests/e2e/test_cli_eval_report.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation eval-report --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p35-demo-20260517T1705/out/simple_chords
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-p35-demo-20260517T1705/out/riff
uv run guitar-tab-generation transcribe fixtures/single_note_lead_30_90s.wav --backend fixture --out /tmp/guitar-tab-p35-demo-20260517T1705/out/lead
uv run guitar-tab-generation eval-report /tmp/guitar-tab-p35-demo-20260517T1705 --manifest tests/fixtures/golden_manifest.json
```

結果：

- targeted tests：6 passed
- full regression：231 passed
- compileall：通過
- diff check：通過
- manual demo：`eval_report.json` status passed，fixture_count 3，artifact_count 3，failure_count 0

## 剩餘風險

- 目前資料集仍是 synthetic placeholder fixtures，不代表真實歌曲泛化品質。
- 第二位吉他手交叉驗收仍是 post-MVP 建議，不是本階段 blocker。
