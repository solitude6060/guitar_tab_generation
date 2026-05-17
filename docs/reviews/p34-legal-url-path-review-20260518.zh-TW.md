# P34 Legal URL / YouTube Path Review

日期：2026-05-18
範圍：`feature/legal-url-path`

## 結論

未發現 blocker。P34 只建立 legal URL policy gate 與 stub artifact，不做任意 URL / YouTube 下載，也不改 `transcribe` default。

## 檢查項

- CLI：新增 `guitar-tab-generation ingest-url <url> --out <artifact_dir> [--i-own-rights]`。
- No-rights：缺 `--i-own-rights` 會 blocked，寫 `policy_gate.txt`。
- YouTube：即使宣告權利仍 blocked。
- Owned sample stub：只允許 `https://example.com/guitar-tab-generation/owned-sample.wav`，寫 `source_policy.json`。
- Safety：`download_performed=false`，未呼叫 downloader / browser / network。

## 驗證證據

- `uv run pytest tests/unit/test_url_ingest.py tests/e2e/test_cli_ingest_url.py -q`：6 passed。
- `uv sync --group dev`：通過。
- `uv run pytest -q`：274 passed。
- `uv run python -m compileall -q src tests`：通過。
- `git diff --check HEAD`：通過。
- `uv run guitar-tab-generation ingest-url --help`：列出 `--out`、`--i-own-rights`。
- 手動 demo：`/tmp/guitar-tab-p34-demo-20260517T175620Z/no-rights/policy_gate.txt` 寫入 blocked reason；`/tmp/guitar-tab-p34-demo-20260517T175620Z/owned/source_policy.json` 寫入 `mode=stub_only`、`download_performed=false`。

## 外部審查工具狀態

- `gemini --help` 可執行；本 session 非互動 review 嘗試卡在 browser authentication prompt，未產生可用審查結果。
- `claude-mm`：本機 `command -v claude-mm` 無結果，未安裝或不在 `PATH`。

## 剩餘風險

- v1.0 不支援真實 URL 下載；後續若要支援，需另做法律 review、本機工具檢查、明確 opt-in 與來源稽核。
