# P28 Chord Recognition Backend PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P28 新增 artifact-first 和弦辨識 sidecar，讓既有 artifact 目錄可在不重跑轉錄、不啟動 GPU、不下載模型的情況下產生 `chords.json`。

本階段交付：

- 新增 CLI：`guitar-tab-generation chord-detect <artifact_dir>`。
- 讀取既有 `arrangement.json` 的 `chord_spans` 與 `note_events`；若未來 P26 stem note sidecar 存在，可作為補充輸入，但 P28 不要求真實 stem inference。
- 輸出 `<artifact_dir>/chords.json`，包含 schema、backend、source、provenance、confidence、warnings。
- viewer / interface 顯示 `chords.json` sidecar 摘要，並保留低信心 warning。
- 不改 `transcribe` default；不執行真實 AI 模型、GPU 或網路下載。

## 2. 非目標

- 不引入新的 chord recognition 模型或外部依賴。
- 不把 `chords.json` 視為比原始 transcription 更高權威的 truth source。
- 不在低信心時 silent fallback 成「看似確定」的和弦。
- 不改既有 `arrangement.json` schema。

## 3. 使用者故事

1. 使用者已有一個合法本機音訊產生的 artifact 目錄，可以執行 `chord-detect` 取得可檢查的和弦 sidecar。
2. 使用者開啟 `viewer.md` 或 `interface.html` 時，可以看到和弦 sidecar 的來源、backend、和弦進行、平均信心與 warning。
3. 若 artifact 缺少必要輸入或信心不足，CLI 會失敗或寫入 warning，而不是靜默產出不可追溯結果。

## 4. Artifact Contract

`chords.json` 必須是 JSON object：

```json
{
  "schema": "guitar-tab-generation.chords.v1",
  "backend": "deterministic-arrangement",
  "source": {
    "artifact_dir": ".",
    "arrangement": "arrangement.json",
    "stem_notes": []
  },
  "summary": {
    "chord_count": 2,
    "average_confidence": 0.85,
    "low_confidence_count": 0
  },
  "chords": [
    {
      "start": 0.0,
      "end": 4.0,
      "label": "Em",
      "confidence": 0.91,
      "provenance": {
        "stage": "chord_detection",
        "source": "arrangement.chord_spans",
        "backend": "deterministic-arrangement"
      }
    }
  ],
  "warnings": []
}
```

低信心 warning 使用既有 `LOW_CHORD_CONFIDENCE` code。

## 5. 驗收標準

- `uv run guitar-tab-generation chord-detect --help` 可用。
- 有 `chord_spans` 的 artifact 會輸出 `chords.json`，保留 label/time/confidence/provenance。
- 低於 chord confidence threshold 的 chord 會產生 warning。
- 缺少 `arrangement.json` 或無可用 chord/note input 時，CLI 清楚失敗。
- `view` 與 `interface` 會讀取 optional `chords.json` 並顯示 sidecar summary。
- 全量 `uv run pytest -q` 通過。
