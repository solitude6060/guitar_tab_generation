# P14 Test Spec：Docker Compose Local AI Runtime

## Scope

Validate repo-native Docker Compose artifacts without requiring CI to build
large GPU images.

## Red tests first

1. `tests/test_docker_compose_contract.py`
   - `test_compose_declares_required_profiles_and_services`
   - `test_dockerignore_excludes_local_state_and_secrets`
   - `test_env_example_uses_placeholders_only`
   - `test_docker_docs_have_traditional_chinese_version`

## Expected behavior

- `docker-compose.yml` contains services:
  - `app`
  - `ai-gpu`
  - `ollama`
  - `cloud-backup`
- Profiles include:
  - `dev`
  - `gpu-ai`
  - `llm`
  - `cloud-backup`
- Dockerfiles exist under `docker/`.
- `.dockerignore` excludes `.omx`, `.venv`, `.env`, caches, and generated
  outputs.
- `.env.example` contains placeholder-only MiniMax environment names.
- Docs exist in English and Traditional Chinese.

## Verification commands

```bash
uv run pytest -q tests/test_docker_compose_contract.py
docker compose config
uv run pytest -q
uv run guitar-tab-generation --help
git ls-files .omx
git log -5 --format=%B
```
