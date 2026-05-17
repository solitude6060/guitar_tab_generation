# P29 Section Detection Sidecar PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P29 新增 artifact-first 段落偵測 sidecar，讓既有 artifact 目錄可執行 `section-detect` 產生可追溯的 `sections.json` object sidecar。

本階段交付：

- 新增 CLI：`guitar-tab-generation section-detect <artifact_dir>`。
- 讀取 `arrangement.json` 的 `section_spans`；若缺少 sections，使用 `chords.json` object sidecar 或 `chord_spans` 做 deterministic fallback。
- 輸出 `<artifact_dir>/sections.json`，包含 schema、backend、source、summary、sections、warnings。
- viewer / interface 顯示 optional section sidecar 摘要。
- 不改 `transcribe` default；不執行模型、GPU 或網路下載。

## 2. 非目標

- 不引入外部 segmentation 模型。
- 不把 deterministic baseline 包裝成真實音樂結構辨識。
- 不破壞既有 list 版 `sections.json`，也不改 `arrangement.json` schema。

## 3. Artifact Contract

```json
{
  "schema": "guitar-tab-generation.sections.v1",
  "backend": "deterministic-arrangement",
  "source": {
    "artifact_dir": ".",
    "arrangement": "arrangement.json",
    "chords": "chords.json",
    "primary": "arrangement.section_spans"
  },
  "summary": {
    "section_count": 1,
    "average_confidence": 0.8,
    "low_confidence_count": 0
  },
  "sections": [
    {
      "start": 0.0,
      "end": 16.0,
      "label": "Verse/Riff A",
      "confidence": 0.8,
      "provenance": {
        "stage": "section_detection",
        "source": "arrangement.section_spans",
        "backend": "deterministic-arrangement"
      }
    }
  ],
  "warnings": []
}
```

低信心 warning 使用既有 `LOW_SECTION_CONFIDENCE` code。

## 4. 驗收標準

- `uv run guitar-tab-generation section-detect --help` 可用。
- 有 `section_spans` 的 artifact 會輸出 object 版 `sections.json`。
- 缺少 `section_spans` 但有 chords 時，會用 chord window 產生 single section fallback，並標明 provenance。
- 低於 section confidence threshold 的 section 會產生 warning。
- 既有 list 版 `sections.json` 不會破壞 viewer/interface/export/tutorial。
- `view` 與 `interface` 會讀取 optional object 版 `sections.json` 並顯示 sidecar summary。
