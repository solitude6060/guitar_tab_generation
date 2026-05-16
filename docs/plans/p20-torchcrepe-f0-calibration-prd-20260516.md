# P20 PRD：torchcrepe F0 Calibration Adapter

日期：2026-05-16
狀態：Implemented
Branch：`feature/torchcrepe-f0-calibration`

## 1. 背景

P19 建立 Torch-first route registry 與 smoke gate。下一階段選擇最低風險的 `torchcrepe-f0`：它不負責 polyphonic note transcription，而是用於 solo/riff passages 的 F0 confidence calibration，補強既有 note events 的可信度判讀。

## 2. 目標

1. 新增 artifact-first CLI：`guitar-tab-generation f0-calibrate <artifact_dir>`。
2. 從 `artifact_dir/audio_normalized.wav` 與 `artifact_dir/notes.json` 產生 `f0_calibration.json`。
3. Adapter lazy-import `torchcrepe`，未安裝時清楚失敗，不 silent fallback。
4. 預設使用 CPU，避免佔用共享 GPU。
5. 不取代 Basic Pitch，也不改 `fixture` default。

## 3. 功能需求

### 3.1 Input contract

`f0-calibrate` 需讀取：

- `audio_normalized.wav`
- `notes.json`

若缺任一檔案，需回傳清楚錯誤。

### 3.2 torchcrepe runtime boundary

Adapter 需以 lazy import 方式載入 `torchcrepe`。P20 不在 module import time 載入 Torch heavy dependency。

根據 torchcrepe 官方文件，主要呼叫形狀為：

```python
torchcrepe.predict(audio, sr, hop_length, fmin, fmax, model, batch_size=batch_size, device=device, return_periodicity=True)
```

### 3.3 Output contract

輸出 `f0_calibration.json`，至少包含：

- `backend: torchcrepe-f0`
- `device`
- `sample_rate`
- `hop_length`
- `model`
- `note_calibrations[]`

每個 note calibration 至少包含：

- `note_id`
- `expected_midi`
- `observed_midi`
- `delta_semitones`
- `periodicity_confidence`
- `frame_count`
- `status`

### 3.4 CLI

```bash
guitar-tab-generation f0-calibrate <artifact_dir> [--out <path>] [--device cpu] [--model tiny|full] [--hop-ms 5]
```

### 3.5 安全策略

- 預設 `--device cpu`。
- GPU 使用必須明確 `--device cuda:0`。
- 若 `torchcrepe` 未安裝，回傳錯誤並提示這是 optional Torch route。

## 4. 非目標

- 不把 `torchcrepe` 接進 `transcribe` 主流程。
- 不替換 Basic Pitch。
- 不做 polyphonic transcription。
- 不自動下載或安裝 PyTorch / torchcrepe。
- 不在本階段建立 Docker GPU image。

## 5. 驗收標準

1. Unit tests 覆蓋 fake torchcrepe runtime → F0 calibration output。
2. E2E tests 覆蓋 CLI 讀 artifacts、輸出 `f0_calibration.json`。
3. 未安裝 runtime 時錯誤清楚，不 fallback。
4. `uv run pytest -q` 綠燈。
5. `uv run guitar-tab-generation --help` 顯示 `f0-calibrate`。
