# P8 Test Spec：Interface MVP

日期：2026-05-13
狀態：Implemented

## 1. Unit tests

新增 `tests/unit/test_artifact_interface.py`：

- `render_artifact_interface_html` 產生 HTML document。
- 必須包含 source、tempo、quality status、confidence、warnings、sections、chords。
- artifact 文字必須 HTML escape。
- `write_artifact_interface` 預設輸出 `<artifact_dir>/interface.html`。

## 2. E2E tests

新增 `tests/e2e/test_cli_artifact_interface.py`：

- 對三個 golden fixture：
  1. `transcribe`
  2. `view`
  3. `tutorial`
  4. `interface`
  5. 驗證 `interface.html` 包含 fixture id、quality、warning/confidence、TAB/viewer/tutorial links。
- 驗證 `--out custom-interface.html`。
- 缺必要 artifact 時 CLI 回傳 1 且不產生 `interface.html`。

## 3. Regression gates

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation interface --help
```

## 4. Manual demo gate

實作狀態：已通過。

```bash
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p8-simple
uv run guitar-tab-generation view /tmp/guitar-tab-p8-simple
uv run guitar-tab-generation tutorial /tmp/guitar-tab-p8-simple
uv run guitar-tab-generation interface /tmp/guitar-tab-p8-simple
sed -n '1,120p' /tmp/guitar-tab-p8-simple/interface.html
```
