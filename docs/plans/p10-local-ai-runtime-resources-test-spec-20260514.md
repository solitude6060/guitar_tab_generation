# P10 Test Spec：Local 4090 AI Runtime + MiniMax Backup Resources

日期：2026-05-14
狀態：Implemented

## 1. Unit tests

新增 `tests/unit/test_ai_runtime.py`：

- `build_resource_plan()` 回傳 4090 local-first 與 MiniMax backup sections。
- `collect_ai_runtime_status()` 可注入 command runner，不依賴真實 GPU。
- 無 `nvidia-smi` / `ffmpeg` 時仍回傳 status，不 crash。

## 2. CLI tests

新增 `tests/test_ai_runtime_cli.py`：

- `doctor-ai --json` 回傳合法 JSON。
- `ai-resources` 輸出繁中 Markdown，包含 4090、MiniMax、Basic Pitch、Demucs。

## 3. Regression gates

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation doctor-ai --help
uv run guitar-tab-generation ai-resources --help
```
