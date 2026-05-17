# P35 Evaluation Dataset + Metrics PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P35 建立 v1.0 MVP 的 evaluation dataset 與 metrics gate，讓後續 P30/P31/P32 不只靠 demo 感覺判斷品質。

本階段交付：

- 新增 CLI：`guitar-tab-generation eval-report <artifact_root> --manifest <manifest.json>`。
- 讀取 evaluation fixture manifest 與 rubric records。
- 驗證每個 fixture 有 rights statement、rights attestation、rubric record。
- 讀取每個 fixture 在 `expected_outputs` 指向的 `arrangement.json` / `quality_report.json`。
- 產生 `eval_report.json`，包含 note/chord/section/playability metrics、rubric summary、threshold gate。
- 不引入未授權資料；不下載模型；不跑 GPU。

## 2. 非目標

- 不建立真實音訊標註資料集。
- 不用 LLM 評分音樂品質。
- 不把 placeholder rubric 當作最終人工驗收，只作 v1.0 MVP regression baseline。

## 3. CLI Contract

```bash
guitar-tab-generation eval-report <artifact_root> --manifest tests/fixtures/golden_manifest.json
```

預設輸出：

```text
<artifact_root>/eval_report.json
```

可用 `--out <path>` 覆寫。

## 4. Metrics Contract

`eval_report.json` 必須包含：

- `schema`: `guitar-tab-generation.eval-report.v1`
- `summary`: fixture count、passed、failed、average confidence、average rubric score
- `fixtures[]`: 每個 fixture 的 rights/rubric/artifact/metrics 狀態
- `thresholds`: note/chord/section/fingering threshold
- `failures[]`: machine-readable failures

每個 fixture metrics：

- note：count、average confidence、low confidence count
- chord：count、average confidence、low confidence count
- section：count、average confidence、low confidence count
- playability：position count、playable rate、warning count

## 5. 驗收標準

- `eval-report --help` 可用。
- 缺少 manifest、rights/rubric record、artifact output 時失敗且記錄 failure。
- 三個 golden fixtures 產生 artifacts 後，eval report passed。
- eval report 不需要網路、GPU、heavy runtime。
