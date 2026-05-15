# P15 PR Code Review：Model Download Smoke Harness

## Scope

Reviewed the P15 feature branch for safe model download/integration smoke
planning on a shared RTX 4090 workstation.

## Findings

| Finding | Severity | Decision | Evidence |
|---|---|---|---|
| Default CLI might download or touch GPU accidentally | Blocker | Addressed by safe defaults | `model-smoke --json` reports `download_enabled=false`, `gpu_enabled=false`, all `command_executed=false` |
| GPU-sensitive routes can steal VRAM from another project | Blocker | Addressed by opt-in + VRAM guard | Demucs/torchcrepe/local-LLM require `--allow-gpu` or `GPU_TESTS_ENABLED=1`; low VRAM returns `skipped` |
| Docker GPU profile should not run heavy work by default | Major | Addressed | `ai-gpu` command is safe `model-smoke --json`; downloads require `MODEL_SMOKE_DOWNLOAD=1` |
| User-facing docs need Traditional Chinese | Major | Addressed | Added `docs/model-smoke.zh-TW.md` and updated `docs/docker.zh-TW.md` |
| Local state/secrets must not be tracked | Major | Verification required before merge | `.env.example` uses placeholders; final hygiene gate must check `.omx` untracked |

## Verification performed

```bash
uv run pytest -q tests/unit/test_model_smoke.py tests/test_model_smoke_cli.py tests/test_docker_compose_contract.py
uv run guitar-tab-generation model-smoke --json
nvidia-smi --query-gpu=name,memory.free,memory.used,memory.total --format=csv,noheader,nounits
```

Current GPU observation at review time: RTX 4090 free VRAM was observed via
`nvidia-smi`; no model download or GPU workload was run.

## Review result

Approved for full regression and branch-flow verification.
