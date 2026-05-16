# P22 Test Spec：Optional Torch Dependency Group

日期：2026-05-16

## 1. Red tests

新增 `tests/test_torch_dependency_group_contract.py`：

- 驗證 `pyproject.toml` 含 `torch-ai` dependency group。
- 驗證 `torch-ai` 含 `torch`、`torchaudio`、`torchcrepe`、`demucs`。
- 驗證 default uv groups 只有 `dev`。
- 驗證英文與繁中安裝文件都提到 `uv sync --group torch-ai` 與 `torch-smoke`。

更新 `tests/unit/test_torch_backends.py`：

- `torchcrepe-f0` 與 `demucs-htdemucs` route 需標示 `dependency_group=torch-ai` 與安裝提示。

## 2. Green implementation

- 更新 `pyproject.toml` dependency groups。
- 更新 `torch_backends.py` route metadata。
- 新增 `docs/torch-optional-dependencies.md` 與 `docs/torch-optional-dependencies.zh-TW.md`。
- 更新 `uv.lock`，但驗證 default sync 不安裝 Torch heavy group。

## 3. Verification gates

必要 gate：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/test_torch_dependency_group_contract.py tests/unit/test_torch_backends.py tests/e2e/test_cli_torch_backends.py
UV_CACHE_DIR=/tmp/uv-cache uv sync --locked --group dev
UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --help
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation torch-smoke --route torchcrepe-f0 --json
```

Optional Torch group validation（不作 default CI gate）：

```bash
UV_CACHE_DIR=/tmp/uv-cache uv lock --check
# 使用者明確 opt-in 才跑：
UV_CACHE_DIR=/tmp/uv-cache uv sync --group torch-ai
```

## 4. 不驗證項目

- P22 不跑真實 torchcrepe inference。
- P22 不跑 Demucs separation。
- P22 不驗證 CUDA wheel 安裝，避免在共享 RTX 4090 主機上造成資源風險。
