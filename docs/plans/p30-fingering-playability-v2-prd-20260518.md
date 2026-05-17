# P30 Fingering + Playability v2 PRD

日期：2026-05-18
狀態：Planned

## 1. 目標

P30 改善既有 `guitar_arranger` 的指法與可彈性資訊，讓 riff / solo TAB 不只選最近 fret，還能輸出可檢查的 position shift、stretch 與 finger assignment。

交付：

- greedy cost model 保留 deterministic 行為。
- position output 新增 `position_shift`、`hand_position`、`finger`。
- 大位移產生 warning。
- 同時或近同時音符超過 max stretch 產生 warning。
- 不新增模型、不改 `transcribe` default、不改既有 artifact schema 必填欄位。

## 2. 非目標

- 不做完整動態規劃。
- 不做 polyphonic chord voicing solver。
- 不宣稱專業吉他教師級指法。

## 3. 驗收標準

- 既有 arranger 測試維持通過。
- 近距離位置仍優先於最低 fret。
- 大位移會產生 `LARGE_POSITION_SHIFT` warning。
- 同一時間窗 stretch 超過 4 frets 會產生 `MAX_STRETCH_EXCEEDED` warning。
- finger assignment 為 1–4 或 `None`，且低信心時 playability degraded。
