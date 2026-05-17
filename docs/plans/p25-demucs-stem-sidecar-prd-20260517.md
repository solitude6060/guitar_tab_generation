# P25 PRD：Demucs Stem Separation Sidecar

日期：2026-05-17
狀態：Implemented
範圍：在 P24 Demucs runtime gate 之上，新增 artifact-first stem separation sidecar。

## 背景

P24 已建立 Demucs optional runtime、cache path、GPU gate 與 no-silent-fallback policy。P25 要把這些 gate 連到可測的 artifact contract，但仍不把 Demucs 接進 `transcribe` 預設流程，也不在測試中執行真實 source separation。

## 目標

- 新增 `guitar-tab-generation separate-stems <artifact_dir>`。
- 從 `<artifact_dir>/audio_normalized.wav` 產生：
  - `<artifact_dir>/stems/`
  - `<artifact_dir>/stem_manifest.json`
- 重用 P24 Demucs gate 的 runtime/cache/GPU policy。
- 預設不使用 GPU；只有 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1` 才允許 GPU gate。
- 使用 fake Demucs runtime 做 unit/e2e，避免真實 Demucs、Torch、model download 進入 default test。

## 非目標

- 不執行真實 Demucs stem separation 的 CI/default 測試。
- 不下載 model weights。
- 不新增 heavy dependency。
- 不改 `transcribe` default，不新增 `transcribe --stem`；stem-aware Basic Pitch 是 P26。
- 不保證真實 Demucs CLI 在所有平台的輸出 layout；本階段定義 adapter contract。

## 使用者故事

1. 作為本機使用者，我可以對既有 artifact directory 執行 `separate-stems`，得到可被後續 pipeline 消費的 stem artifacts。
2. 作為開發者，我可以用 fake Demucs runtime 測試 manifest 與檔案 layout，不需要 GPU 或 Demucs 安裝。
3. 作為共享 GPU 主機使用者，我不會因為預設指令而意外佔用 GPU。

## Artifact contract

`stem_manifest.json` 至少包含：

- `backend`: `demucs-htdemucs`
- `model_name`
- `device`: 預設 `cpu`
- `source_audio`: `audio_normalized.wav`
- `stems_dir`: `stems`
- `stems[]`: 每個 stem 的 `name`、`path`、`model`、`confidence`、`provenance`
- `gate`: P24 gate payload summary
- `warnings[]`: 低風險提醒，例如 fake runtime 或非真實 confidence。

預設 stem name 使用 `drums`、`bass`、`other`、`vocals`，並允許 runtime 回報實際輸出清單。

## CLI contract

```bash
guitar-tab-generation separate-stems <artifact_dir>
guitar-tab-generation separate-stems <artifact_dir> --device cpu
guitar-tab-generation separate-stems <artifact_dir> --allow-gpu --device cuda --min-free-vram-mb 12000
```

`--device cuda` 必須搭配 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`，否則失敗並清楚提示。預設 `--device cpu`。

## 驗收標準

- `separate-stems --help` 顯示 artifact dir、device、model、GPU guard options。
- artifact 缺少 `audio_normalized.wav` 時清楚失敗，不產生假成功。
- fake runtime e2e 會寫入 `stems/*.wav` 與 `stem_manifest.json`。
- `transcribe --help` 仍沒有 Demucs/stem default。
- `uv run pytest -q` 通過。
