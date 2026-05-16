# P18 PRD：Basic Pitch Local Backend MVP

日期：2026-05-16
狀態：Implemented
Branch：`feature/basic-pitch-backend`

## 1. 背景

目前 pipeline 已有完整 artifact / tutorial / interface / export / DAW bundle 流程，但真實音訊辨識仍停留在 `fixture` backend。
使用者明確要求直接下載模型並設定好 AI backend 接入，因此下一階段先接入第一個可運行的本機 note transcription backend。

## 2. 目標

新增可運行的 `basic-pitch` backend：

1. `guitar-tab-generation transcribe <audio> --backend basic-pitch --out <dir>` 可執行。
2. `basic-pitch` 直接對合法本機音訊產生 note events。
3. `fixture` 仍維持 deterministic default。
4. 當 `basic-pitch` 未安裝或執行失敗時，錯誤需清楚，不得 silently fallback 成 fixture。

## 3. 功能需求

### 3.1 Backend resolution

- `resolve_backend("basic-pitch")` 應回傳可執行的 backend 實例。
- backend 必須能取得 normalized local audio path。

### 3.2 Note transcription

- 透過 Basic Pitch 的 Python API 對 audio path 執行 prediction。
- 將預測結果轉成現有 `note_events` contract：
  - `id`
  - `start`
  - `end`
  - `pitch_midi`
  - `pitch_name`
  - `velocity`
  - `confidence`
  - `provenance`

### 3.3 Provenance

- provenance 至少包含：
  - `stage: pitch_transcription`
  - `backend: basic-pitch`
  - `stem: mix`
  - `model: basic_pitch_icassp_2022`

### 3.4 Packaging / environment

- 專案需提供可重現的安裝方式。
- 允許將 `basic-pitch` 放入新的 `ai` dependency group，而不是強迫所有 dev/CI 環境都安裝。

## 4. 非目標

- 不整合 Demucs / torchcrepe / Essentia。
- 不在本階段改寫 chord/section/rhythm 的演算法。
- 不保證 production-grade transcription accuracy。

## 5. 驗收標準

1. `transcribe --backend basic-pitch` 能成功輸出 artifact。
2. 測試證明：
   - backend 可被 resolve；
   - pipeline 會把 normalized audio path 傳給 backend；
   - backend 產出的 note events 符合既有 contract/provenance。
3. `fixture` backend 既有測試不回歸。
4. 文件新增 basic-pitch 安裝與使用說明（含繁中）。
5. `uv run pytest -q` 維持綠燈。

## 6. 實作驗證紀錄

- AI dependency 安裝範圍限制在 repo `uv` `.venv` 的 optional `ai` group。
- `ai` group 只加入 `basic-pitch` 與 Basic Pitch runtime 相容所需的 `setuptools>=68,<81`。
- 未安裝 Demucs、torchcrepe、Essentia 或其他尚未接入的模型套件。
- 已用 `CUDA_VISIBLE_DEVICES=''` 跑過 fixture 音訊 smoke test，避免佔用共享 GPU。
