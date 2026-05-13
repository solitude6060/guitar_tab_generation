# P7 Test Spec：Practice Tutorial Generator

日期：2026-05-13
狀態：Implemented

## 1. Unit tests

新增 `tests/unit/test_practice_tutorial.py`：

- `render_practice_tutorial_markdown` 產生固定章節：readiness、tempo ladder、section loop、chord plan、lead/riff plan、safety note。
- tempo ladder 根據 artifact tempo 產生 50% / 75% / 100% BPM。
- warnings 與低 confidence 必須在 tutorial 中可見。
- `write_practice_tutorial` 預設輸出 `<artifact_dir>/tutorial.md`。

## 2. E2E tests

新增 `tests/e2e/test_cli_practice_tutorial.py`：

- 對三個 golden fixture：
  1. `main(["transcribe", ...])` 產生 artifacts。
  2. `main(["tutorial", artifact_dir])` 產生 `tutorial.md`。
  3. 驗證 Markdown 內含 fixture source、tempo ladder、section/chord/lead-riff plan、safety note、`tab.md` reference。
- 驗證 `--out custom-tutorial.md`。
- 缺必要 artifact 時 CLI 回傳 1 且不產生 `tutorial.md`。

## 3. Regression gates

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation tutorial --help
```

## 4. Manual demo gate

實作狀態：已通過。

```bash
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-p7-riff
uv run guitar-tab-generation tutorial /tmp/guitar-tab-p7-riff
sed -n '1,160p' /tmp/guitar-tab-p7-riff/tutorial.md
```
