# P3 PRD：Playability + Renderer Quality

日期：2026-05-13  
狀態：Planned  
建議分支：`feature/playability-renderer-quality`

## 1. 背景

P1/P2 建立可替換 backend 與 E2E artifact contract 後，下一個核心價值是讓輸出的 TAB 更像吉他手能拿來練的譜，而不是機械化 note list。

## 2. 目標

改善 `guitar_arranger` 與 `renderer`，讓 TAB 輸出具備合理手位、段落、節奏提示、inline warning 與降級標示。

## 3. 非目標

- 不追求原演奏者指法。
- 不做完整教學課程。
- 不做 DAW export。

## 4. 功能需求

1. 同音多位置選擇時，偏好手位移動較小的位置。
2. 過高密度 note events 需降級或簡化為 sketch phrase。
3. `unplayable` 不得渲染成正常 TAB。
4. `tab.md` 應包含：
   - source metadata
   - tempo/key/confidence
   - sections
   - chords
   - TAB block
   - warnings/degraded notes
5. Snapshot/golden text regression 要能避免輸出大幅漂移。

## 5. Acceptance Criteria

- P3 tests 通過。
- 三個 fixtures 的 `tab.md` 人類可讀，且不缺 warning/degraded section。
- 所有 positions 仍符合 string 1–6、fret 0–20。
