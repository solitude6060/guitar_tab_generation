# P0 PRD：Dev Flow + CI Gate

日期：2026-05-12  
狀態：Ready for execution  
建議分支：`feature/dev-flow-and-ci`

## 1. 背景

專案已建立 MVP 骨架與繁中開發流程文件，但目前尚未有自動化 CI gate 來保證：

- 測試會在遠端執行。
- CLI entrypoint 可啟動。
- `.omx/` 不被追蹤或推送。
- commit message 不含使用者明確不想要的 OmX co-author trailer。
- 規劃文件位置從 `.omx/` 轉移到 `docs/` 後不再漂移。

## 2. 目標

建立最小但嚴格的開發護欄，讓後續功能在 SDD/TDD/git flow 下安全演進。

## 3. 非目標

- 不導入大型 dependency。
- 不在本階段實作音訊 AI backend。
- 不新增 UI、教學或 DAW export。
- 不處理任意 URL 下載。

## 4. 使用者價值

開發者可以放心迭代，因為每個 PR 都會自動檢查基本品質，避免重新把本機 orchestration state 或 unwanted co-author trailer 推上 GitHub。

## 5. 功能需求

### R1：CI workflow

新增 GitHub Actions workflow，至少執行：

```bash
uv run pytest -q
uv run guitar-tab-generation --help
```

### R2：Repo hygiene check

新增自動檢查，確認：

- `git ls-files .omx` 為空。
- tracked files 不包含 `__pycache__`、`.pytest_cache`、`.pyc`。
- commit history 或目前 branch 不包含 `Co-authored-by: OmX`。

### R3：文件入口

`README.md` 與 `README.zh-TW.md` 必須連到：

- `docs/development-flow.zh-TW.md`
- `docs/plans/backlog-20260512.md`

### R4：pytest warning 決策

目前已移除舊 `pythonpath` pytest 設定；P0 必須保持 `uv run pytest -q` 無 pytest config warning。

## 6. Acceptance Criteria

1. CI workflow 存在並可在 push / PR 觸發。
2. 本機執行 pytest 與 CLI help 通過。
3. Hygiene check 會在 `.omx` 被追蹤時失敗。
4. Hygiene check 會在 commit message 含 `Co-authored-by: OmX` 時失敗。
5. README / 繁中 README 有開發流程與 backlog 入口。
6. `.omx/` 留在 `.gitignore` 且不被 git 追蹤。

## 7. 風險與緩解

- 風險：CI 與本機 Python 版本不同。  
  緩解：先鎖 Python 3.11，符合 `pyproject.toml`。
- 風險：history grep 在 shallow clone 不完整。  
  緩解：workflow checkout 使用足夠 history 或將檢查限縮到目前 commit range；實作前在 test-spec 定義。
- 風險：過度自訂腳本增加維護成本。  
  緩解：P0 只做 repo hygiene，不做完整 lint framework。

## 8. 回滾策略

P0 僅新增 CI、docs、輕量檢查。若阻塞開發，可暫時 disable workflow job，但不得移除 `.omx/` ignore 或恢復追蹤 `.omx/`。
