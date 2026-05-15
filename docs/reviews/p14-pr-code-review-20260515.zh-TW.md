# P14 PR 程式碼審查 — Docker Compose 本機 AI Runtime

## 審查範圍

- `docker-compose.yml`
- `docker/Dockerfile.dev`
- `docker/Dockerfile.gpu`
- `.dockerignore`
- `.env.example`
- `.gitignore`
- `docs/docker.md`
- `docs/docker.zh-TW.md`
- `tests/test_docker_compose_contract.py`
- planning 文件

## 結論

**通過，可合併** — 沒有 blocking issue。

## 發現

### Critical

- 無。

### High

- 無。

### Medium

- 無。

### Low / 觀察項目

- GPU image 支援 `INSTALL_HEAVY_AI=true`，但真實模型 smoke tests 必須維持 opt-in，因為 RTX 4090 可能同時被其他專案使用。
- Compose config 已用所有 profiles 驗證。CI 不應預設 build heavy GPU image。

## 驗證證據

- Red tests：
  - `uv run pytest -q tests/test_docker_compose_contract.py`
  - 實作前結果：4 failed，因為 compose artifacts 尚未存在。
- 目標測試：
  - `uv run pytest -q tests/test_docker_compose_contract.py`
  - 結果：4 passed。
- Compose 驗證：
  - `docker compose --profile dev --profile gpu-ai --profile llm --profile cloud-backup config`
  - 結果：valid config。
- 完整回歸：
  - `uv run pytest -q`
  - 結果：115 passed。
- Dev image build：
  - `docker compose --profile dev build app`
  - 結果：build completed successfully。

## 合併建議

完成最後 CLI 與 hygiene checks 後可合併。GPU 模型下載與 smoke tests 留到下一個 opt-in 階段。
