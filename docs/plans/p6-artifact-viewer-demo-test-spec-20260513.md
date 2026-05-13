# P6 Test Spec：Artifact Viewer Demo

日期：2026-05-13
狀態：Implemented

## 1. Unit tests

新增 `tests/unit/test_artifact_viewer.py`：

- `load_artifact_bundle` 讀取必要 artifacts 並回傳 bundle。
- 缺 `arrangement.json` / `quality_report.json` / `tab.md` 時丟出清楚的 `ArtifactViewerError`。
- `render_artifact_viewer_markdown` 產生固定章節：metadata、quality、sections、chords、warnings、practice readiness。

## 2. E2E tests

新增 `tests/e2e/test_cli_artifact_viewer.py`：

- 對三個 golden fixture：
  1. `guitar_tab_generation.cli.main(["transcribe", ...])` 產出 artifacts。
  2. `main(["view", artifact_dir])` 產生 `viewer.md`。
  3. 驗證 Markdown 內含 fixture source、quality status、section/chord 摘要、practice readiness。
- 覆寫輸出：`--out custom-view.md`。
- 缺必要 artifact 時 CLI `view` 回傳 1 且不產生誤導性成功檔案。

## 3. Regression gates

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation view --help
```

## 4. 手動展示 gate

實作狀態：已通過。

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p6-simple
uv run guitar-tab-generation view /tmp/guitar-tab-p6-simple
sed -n '1,120p' /tmp/guitar-tab-p6-simple/viewer.md
```
