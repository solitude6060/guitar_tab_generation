# torchcrepe F0 Calibration

## 功能定位

`f0-calibrate` 是 P20 的 Torch-first 最小接入點。它不負責產生音符，也不取代 Basic Pitch；它只讀取既有 artifact 的 note events，並用 torchcrepe F0 frames 做 solo/riff pitch confidence calibration。

## 安全預設

- 預設 device 是 `cpu`。
- 不會自動使用 GPU。
- 不會自動下載模型或安裝 PyTorch / torchcrepe。
- 未安裝 torchcrepe 時會清楚失敗，不會 fallback 成假資料。

## 使用方式

先用既有流程產生 artifact：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

再執行 F0 calibration：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate /tmp/guitar-tab-basic-pitch
```

輸出：

```text
/tmp/guitar-tab-basic-pitch/f0_calibration.json
```

若要明確使用 GPU，必須指定 device：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate /tmp/guitar-tab-basic-pitch --device cuda:0
```

## Output contract

`f0_calibration.json` 會包含：

- `backend: torchcrepe-f0`
- `device`
- `sample_rate`
- `hop_length`
- `model`
- `note_calibrations[]`

每個 note calibration 包含：

- `note_id`
- `expected_midi`
- `observed_midi`
- `delta_semitones`
- `periodicity_confidence`
- `frame_count`
- `status`

## 依賴策略

P20 只建立 optional runtime boundary。因為 `torchcrepe` 會帶入 PyTorch heavy dependency，本階段不自動安裝。真正要跑本機 torchcrepe 時，再用專門的 optional Torch 環境安裝，不放進 default dev flow。
