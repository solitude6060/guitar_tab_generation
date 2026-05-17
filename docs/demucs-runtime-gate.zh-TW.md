# Demucs Runtime Gate

P24 只建立 Demucs runtime planning 與 install gate，不做真實 stem separation。

## 安全預設

```bash
uv run guitar-tab-generation demucs-gate --json
```

預設輸出 plan：

- 不下載 model。
- 不使用 GPU。
- 不執行 Demucs command。
- 不產生 `stems/` 或 `stem_manifest.json`。
- 不改 `transcribe` 預設 backend。

## Optional runtime 安裝

Demucs 在 `torch-ai` optional group：

```bash
uv sync --group torch-ai
```

檢查 runtime：

```bash
uv run guitar-tab-generation demucs-gate --check-runtime --json
```

若 Demucs 不存在，gate 會回報清楚錯誤，不會 fallback 到 mix 或 fixture stem。

## Cache 與 model path

預設 cache root：

```text
~/.cache/guitar-tab-generation/torch-models
```

可用 `MODEL_CACHE_DIR` 或 `AI_MODEL_CACHE` 覆蓋。Demucs route 使用：

```text
<cache-root>/demucs-htdemucs
<cache-root>/demucs-htdemucs/models/htdemucs
```

P24 不下載 model weights；P25 之後若要跑 separation，仍必須保留明確 opt-in。

## GPU gate

Demucs 預設視為 GPU-sensitive，門檻為 12000 MB free VRAM：

```bash
GPU_TESTS_ENABLED=1 uv run guitar-tab-generation demucs-gate --allow-gpu --min-free-vram-mb 12000 --json
```

VRAM 不足時狀態為 `skipped`，不執行 runtime command。
