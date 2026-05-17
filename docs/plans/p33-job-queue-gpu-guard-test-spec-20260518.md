# P33 Job Queue + GPU Resource Guard Test Spec

日期：2026-05-18
狀態：Planned

## Tests

- unit：submit 產生 queue record 與 log。
- unit：queue ordering 依 `created_at` / insertion order。
- unit：GPU submit 需要 explicit `allow_gpu`。
- unit：GPU lock 存在時 `run_next_job` deferred。
- unit：VRAM 低於門檻時 deferred，reason 進 queue/log。
- unit：cancel/resume 更新狀態並保留 logs。
- e2e：`jobs --help` 顯示 submit/status/run-next/cancel/resume。
- e2e：CLI submit/status/run-next 完成本機 CPU fake job。
- e2e：CLI GPU job 使用 `--fake-free-vram-mb` 驗證低 VRAM deferred，不 probe 真 GPU。

## Regression Gate

```bash
uv sync --group dev
uv run pytest tests/unit/test_job_queue.py tests/e2e/test_cli_jobs.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation jobs --help
uv run guitar-tab-generation jobs submit --help
uv run guitar-tab-generation jobs run-next --help
```
