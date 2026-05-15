# P15 PR Code Review：模型下載 Smoke Harness（繁體中文）

## 範圍

本次 review 檢查 P15 feature branch：在同一台 RTX 4090 可能有其他專案使用 GPU 的前提下，加入安全的模型下載/整合 smoke harness。

## 發現與處理

| 發現 | 嚴重度 | 結論 | 證據 |
|---|---|---|---|
| CLI 預設可能誤下載或誤用 GPU | Blocker | 已處理：安全預設 | `model-smoke --json` 顯示 `download_enabled=false`、`gpu_enabled=false`、所有 `command_executed=false` |
| GPU-sensitive route 可能搶其他專案 VRAM | Blocker | 已處理：opt-in + VRAM guard | Demucs / torchcrepe / local LLM 需要 `--allow-gpu` 或 `GPU_TESTS_ENABLED=1`；VRAM 不足會 `skipped` |
| Docker GPU profile 預設不應跑重工作 | Major | 已處理 | `ai-gpu` 預設命令是安全的 `model-smoke --json`；下載仍需 `MODEL_SMOKE_DOWNLOAD=1` |
| 給使用者看的文件需要繁中版 | Major | 已處理 | 新增 `docs/model-smoke.zh-TW.md`，並更新 `docs/docker.zh-TW.md` |
| 本機狀態與 secret 不可追蹤 | Major | merge 前需驗證 | `.env.example` 只放 placeholder；最後 hygiene gate 需確認 `.omx` 未追蹤 |

## 已執行驗證

```bash
uv run pytest -q tests/unit/test_model_smoke.py tests/test_model_smoke_cli.py tests/test_docker_compose_contract.py
uv run guitar-tab-generation model-smoke --json
nvidia-smi --query-gpu=name,memory.free,memory.used,memory.total --format=csv,noheader,nounits
```

review 當下只用 `nvidia-smi` 觀察 RTX 4090 記憶體狀態，沒有下載模型，也沒有啟動 GPU workload。

## Review 結論

可進入 full regression 與 feature→dev→main branch-flow 驗證。
