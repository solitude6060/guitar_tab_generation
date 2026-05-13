# P0 Test Spec：Dev Flow + CI Gate

日期：2026-05-12  
對應 PRD：`docs/plans/p0-dev-flow-ci-prd-20260512.md`

## 1. 測試目標

證明 repo 具備最小自動化開發護欄：測試可跑、CLI 可啟動、`.omx` 不被追蹤、OmX co-author trailer 不再出現。

## 2. Red Tests / Contract Tests

實作前先新增以下測試或檢查，確認至少一個能在未實作完整護欄前表達缺口：

1. `tests/test_repo_hygiene.py`
   - `git ls-files .omx` 必須為空。
   - `git ls-files` 不得包含 `.pyc`、`__pycache__`、`.pytest_cache`。
   - `git log --format=%B -n <bounded>` 不得包含 `Co-authored-by: OmX`。
2. CI workflow existence check（可用 pytest 或 script）：
   - `.github/workflows/ci.yml` 必須存在。
   - workflow 文字必須包含 pytest 與 CLI help 指令。

## 3. Unit / Static Checks

```bash
uv run pytest -q tests/test_repo_hygiene.py
```

預期：

- 若 `.omx` 被追蹤，fail。
- 若 pycache 被追蹤，fail。
- 若 recent history 含 OmX co-author trailer，fail。

## 4. Integration Checks

```bash
uv run pytest -q
uv run guitar-tab-generation --help
```

預期：

- 所有測試通過。
- CLI help exit code 0。
- pytest warning 已在 uv-first 設定中移除，P0 需保持 pytest 輸出乾淨。

## 5. CI Checks

GitHub Actions workflow 應至少包含：

- checkout（`actions/checkout@v6`，`fetch-depth: 0` 供 history hygiene check）。
- Python 3.11 setup（`actions/setup-python@v6`，讀取 `.python-version`）。
- `uv sync --locked --group dev` 或等價 local package setup。
- `uv run pytest -q`。
- `uv run guitar-tab-generation --help`。

實作時若使用第三方 Action 版本，需在當次實作前查官方文件或沿用當下官方建議版本。

## 6. Hard Fail

以下任一發生，P0 不通過：

1. `.omx` 出現在 `git ls-files`。
2. `Co-authored-by: OmX` 出現在欲推送 commit history。
3. pytest fail。
4. CLI help fail。
5. workflow 不存在或未跑 pytest。
6. README 沒有連到開發流程與 backlog。
