# P14 PR Code Review — Docker Compose Local AI Runtime

## Review scope

- `docker-compose.yml`
- `docker/Dockerfile.dev`
- `docker/Dockerfile.gpu`
- `.dockerignore`
- `.env.example`
- `.gitignore`
- `docs/docker.md`
- `docs/docker.zh-TW.md`
- `tests/test_docker_compose_contract.py`
- planning docs

## Verdict

**APPROVE** — no blocking issues found.

## Findings

### Critical

- None.

### High

- None.

### Medium

- None.

### Low / watchlist

- The GPU image supports `INSTALL_HEAVY_AI=true`, but actual model smoke tests
  should stay opt-in because the RTX 4090 may be shared with other projects.
- Compose config is validated with all profiles enabled. CI should not build the
  heavy GPU image by default.

## Evidence

- Red tests:
  - `uv run pytest -q tests/test_docker_compose_contract.py`
  - Initial result: 4 failed because compose artifacts did not exist.
- Target tests:
  - `uv run pytest -q tests/test_docker_compose_contract.py`
  - Result: 4 passed.
- Compose validation:
  - `docker compose --profile dev --profile gpu-ai --profile llm --profile cloud-backup config`
  - Result: valid config.
- Full regression:
  - `uv run pytest -q`
  - Result: 115 passed.
- Dev image build:
  - `docker compose --profile dev build app`
  - Result: build completed successfully.

## Merge recommendation

Merge after final CLI and hygiene checks. Keep GPU model downloads in a
separate opt-in phase.
