# P27 PRD：Artifact Quality Scoring v2

日期：2026-05-18
狀態：Planned
範圍：把 mix notes、P25 stems、P26 stem notes、F0 calibration 與 warnings 收斂成可給 viewer/interface 消費的 `quality_report.json` v2。

## 1. 背景

P21–P26 已讓產品具備多個 artifact sidecar：`f0_calibration.json`、`stem_manifest.json`、`stem_notes/<stem>.notes.json`。目前 `quality_report.json` 仍主要只反映初始 `arrangement.json` 的 hard-fail gate，無法回答使用者最需要的問題：有哪些 stem 可用、stem note 結果可信度如何、pitch risk 有多高、不同 backend 的 confidence 狀態如何。

## 2. 目標

1. 新增 artifact-first quality refresh 路徑。
2. 產生 `quality_report.json` v2 schema。
3. 合併以下訊號：
   - `arrangement.json` mix notes / warnings / confidence
   - `stem_manifest.json` stem availability
   - `stem_notes/*.notes.json` stem note count、平均 confidence、warnings
   - `f0_calibration.json` pitch risk count
   - backend/stem confidence summary
4. viewer / interface 顯示 P27 quality summary。

## 3. CLI contract

```bash
guitar-tab-generation quality-report <artifact_dir>
```

輸出：

- 預設寫入 `<artifact_dir>/quality_report.json`。
- 可選 `--out <path>` 寫到指定 JSON。

## 4. 功能需求

- 缺少 optional sidecars 不應 hard fail；需明確標記 unavailable。
- 低 confidence / pitch risk 只能作為風險摘要，不得宣稱 stem notes 比 mix 更正確。
- 不改 P26 `stem_notes` 輸出契約。
- 不自動執行 Demucs、Basic Pitch、torchcrepe 或 GPU 工作。
- `transcribe` default 不變。

## 5. 驗收標準

- `quality-report --help` 顯示 artifact_dir 與 `--out`。
- 含 stems、stem_notes、f0_calibration 的 artifact 會產生 v2 `quality_report.json`。
- v2 report 包含：
  - `schema_version: 2`
  - `artifact_summary.stem_availability`
  - `artifact_summary.stem_notes`
  - `artifact_summary.pitch_risk`
  - `artifact_summary.backend_confidence`
- viewer / interface 顯示 stem availability、pitch risk、backend confidence summary。
- `transcribe --help` 不新增 quality/stem 自動路徑。
- `uv run pytest -q` 通過。
