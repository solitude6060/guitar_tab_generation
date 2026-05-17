# P33 Job Queue + GPU Resource Guard Review

日期：2026-05-18
範圍：`feature/job-queue-gpu-guard`

## 結論

未發現 blocker。P33 交付本機 artifact-first job queue 與 GPU guard evidence：queue 狀態、job logs、GPU opt-in、VRAM defer、one-GPU-task lock 都以 stdlib JSON / file lock 完成，default CI 不 probe GPU、不執行 heavy runtime。

## 檢查項

- CLI：新增 `guitar-tab-generation jobs submit/status/run-next/cancel/resume`。
- Queue：workspace-local `.gtg_jobs/queue.json`，每個 job 有 `status`、`command`、`gpu_sensitive`、`gpu_opt_in`、`reason`、`log_path`。
- Logs：`.gtg_jobs/logs/<job_id>.log` 記錄 submit/run/defer/cancel/resume。
- GPU guard：GPU job submit-time 需要 `--allow-gpu`；run-time 也需要 `--allow-gpu` 才會 probe / lock。
- VRAM：`run-next --fake-free-vram-mb` 支援測試，不觸碰真 GPU。
- Lock：`.gtg_jobs/gpu.lock` 存在時 GPU job deferred 並寫入 reason/log。

## 驗證證據

- `uv run pytest tests/unit/test_job_queue.py tests/e2e/test_cli_jobs.py -q`：9 passed。
- `uv sync --group dev`：通過。
- `uv run pytest -q`：253 passed。
- `uv run python -m compileall -q src tests`：通過。
- `git diff --check HEAD`：通過。
- `uv run guitar-tab-generation jobs --help`：列出 submit/status/run-next/cancel/resume。
- `uv run guitar-tab-generation jobs submit --help`：列出 `--command`、`--gpu`、`--allow-gpu`。
- `uv run guitar-tab-generation jobs run-next --help`：列出 `--allow-gpu`、`--min-free-vram-mb`、`--fake-free-vram-mb`。
- 手動 demo：`/tmp/guitar-tab-p33-demo-20260517T173430Z`，CPU job completed；GPU job 因 8000 MB < 12000 MB deferred，queue/log 均保留 reason。

## 外部審查工具狀態

- `gemini --help` 可執行；本 session 非互動 review 嘗試卡在 browser authentication prompt，未產生可用審查結果。
- `claude-mm`：本機 `command -v claude-mm` 無結果，未安裝或不在 `PATH`。

## 剩餘風險

- P33 不提供 background daemon；`run-next` 是同步 lifecycle simulation。
- JSON queue 是單機最佳努力，不保證跨程序 transaction；P39 packaged app 若導入 worker daemon 需要重新評估 crash recovery。
- P33 不執行 command tokens；真 pipeline execution boundary 留給後續 workspace/app 階段。
