# P15 Test Spec：Model Download Smoke Harness

## Scope

Validate a safe, opt-in model download/integration smoke harness without
requiring network, GPU, or heavyweight AI dependencies in CI.

## Red tests first

1. `tests/unit/test_model_smoke.py`
   - `test_default_plan_does_not_download_or_use_gpu`
   - `test_download_requires_explicit_opt_in`
   - `test_gpu_backend_skips_when_gpu_disabled`
   - `test_gpu_backend_skips_when_free_vram_below_threshold`
   - `test_backend_filter_limits_plan`
2. `tests/test_model_smoke_cli.py`
   - `test_model_smoke_json_safe_defaults`
   - `test_model_smoke_backend_filter_json`
   - `test_model_smoke_plan_markdown_mentions_vram_guard`

## Expected behavior

- `model-smoke --json` returns success with safe `planned`/`skipped` statuses.
- No command runner is called for downloads unless `--download` or
  `MODEL_SMOKE_DOWNLOAD=1` is set.
- GPU-sensitive backends skip unless `--allow-gpu` or `GPU_TESTS_ENABLED=1` is
  set.
- Low free VRAM produces `skipped`, not process failure.
- The CLI can filter one backend without listing unrelated backend smoke steps.

## Verification commands

```bash
uv run pytest -q tests/unit/test_model_smoke.py tests/test_model_smoke_cli.py
uv run pytest -q
uv run guitar-tab-generation model-smoke --help
uv run guitar-tab-generation model-smoke --json
GPU_TESTS_ENABLED=0 uv run guitar-tab-generation model-smoke --backend demucs --json
docker compose --profile dev --profile gpu-ai --profile llm --profile cloud-backup config
git ls-files .omx
```
