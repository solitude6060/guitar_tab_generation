# P9 Test Spec：MIDI / MusicXML Export MVP

日期：2026-05-13
狀態：Implemented

## 1. Unit tests

新增 `tests/unit/test_exporters.py`：

- `render_musicxml` 產生可用 `xml.etree.ElementTree` parse 的 XML。
- MusicXML 包含 note pitch、confidence metadata、warning metadata。
- `render_midi` 產生以 `MThd` 開頭且包含 `MTrk` 的 bytes。
- `write_export` 根據 format 寫出正確副檔名或自訂路徑。

## 2. E2E tests

新增 `tests/e2e/test_cli_export.py`：

- 三個 golden fixtures 跑 `transcribe` 後可 `export --format musicxml`。
- 三個 golden fixtures 跑 `transcribe` 後可 `export --format midi`。
- 缺 artifact 時 CLI 回傳 1 且不產生輸出。

## 3. Regression gates

```bash
uv run pytest -q
uv run guitar-tab-generation --help
uv run guitar-tab-generation export --help
```
