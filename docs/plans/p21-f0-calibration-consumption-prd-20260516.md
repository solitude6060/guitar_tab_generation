# P21 PRD：F0 Calibration Consumption

日期：2026-05-16
狀態：Planned
建議分支：`feature/f0-calibration-consumption`

## 1. 背景

P20 已產生 `f0_calibration.json`，但目前它只是 sidecar artifact。P21 目標是讓使用者在 viewer、interface、tutorial 直接看見 pitch 風險與練習建議。

## 2. 目標

1. `view <artifact_dir>` 顯示 F0 calibration summary。
2. `interface <artifact_dir>` 顯示 pitch-risk notes、delta semitones、periodicity confidence。
3. `tutorial <artifact_dir>` 將 pitch-risk notes 轉成練習重點。
4. 若 `f0_calibration.json` 不存在，既有 viewer/interface/tutorial 行為不回歸。

## 3. 非目標

- 不重新跑 torchcrepe。
- 不修改 `f0-calibrate` output schema。
- 不新增 heavy dependency。
- 不讓 LLM 修改 pitch truth。

## 4. 驗收標準

- Unit：artifact reader 可讀取 optional `f0_calibration.json`。
- E2E：fixture artifact + fake calibration 會讓 viewer/interface/tutorial 顯示 pitch risk。
- Missing calibration path 維持現有輸出。
- `uv run pytest -q` 通過。
