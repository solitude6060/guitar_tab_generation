# P1 PRD：Audio Backend Adapter 架構

日期：2026-05-12  
狀態：Planned  
建議分支：`feature/audio-backend-adapters`

## 1. 背景

目前 pipeline 已能以 fixture metadata 產生 deterministic outputs。這對 MVP contract 很重要，但未來要加入 librosa、Basic Pitch、Essentia 或 Demucs 時，不能把第三方套件邏輯直接塞進 pipeline，否則會讓測試不穩且難以替換模型。

## 2. 目標

建立可插拔 backend interface，讓 fixture backend 與 future real backend 共用同一份 pipeline contract。

## 3. 非目標

- 不要求 P1 真的完成 Basic Pitch / Essentia / Demucs 整合。
- 不新增沉重 dependency 到必裝路徑。
- 不改變 MVP 的 local-audio-first 與 URL disabled gate。

## 4. 功能需求

### R1：Backend protocols

定義至少以下 protocol / interface：

- Rhythm backend：輸出 tempo、beats、bars、confidence、provenance。
- Chord backend：輸出 chord spans、confidence、warnings、provenance。
- Note backend：輸出 note events、confidence、warnings、provenance。
- Section backend：輸出 section spans、confidence、provenance。

### R2：Fixture backend default

目前 fixture-driven 行為必須保留為 default backend，確保測試 deterministic。

### R3：Optional real backend placeholder

可建立 placeholder 或 import-guarded backend：

- dependency 不存在時，回傳明確錯誤。
- 不影響 fixture backend。
- 不自動下載模型或音訊。

### R4：Provenance contract

所有 events/spans 必須包含 backend/stage provenance。空 provenance 屬 hard fail。

## 5. Acceptance Criteria

1. Pipeline 可選 backend，預設 fixture backend。
2. 現有 20+ 測試維持通過。
3. 新增 backend failure fallback tests。
4. arrangement output 中 note/chord/section provenance 都能指出 backend/stage。
5. 缺 optional dependency 時錯誤清楚，不是 ImportError stack dump。

## 6. 風險與緩解

- 風險：過早抽象造成複雜度。  
  緩解：只抽目前 pipeline 已有的 rhythm/chord/note/section 邊界。
- 風險：真實 backend 非 deterministic。  
  緩解：fixture backend 永遠保留為測試主路徑。
- 風險：新增 dependency 破壞安裝。  
  緩解：所有 heavy backend 都 optional/import guarded，新增 dependency 需 ADR。
