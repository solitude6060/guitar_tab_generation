# P16 PR Code Review：DAW Multi-track Export Bundle

## Scope

審查 P16：`export --format daw` 的輸出流程（bundle、多軌 MIDI/MusicXML、manifest、README）與
既有 `musicxml` / `midi` CLI 相容性。

## Findings

| Finding | Severity | Decision | Evidence |
|---|---|---|---|
| Full-song chunk plan 未輸出為多軌會影響 DAW 導入體驗 | Blocker | 已處理 | `write_export(..., "daw")` 根據 `duration_class` 對應 `processing_plan.mode` 生成 `track-01...track-N` |
| 重疊音符會造成 MIDI delta 時間戳負值 | Major | 已修正 | `render_midi` 使用 `max(0, start_tick - last_tick)`，避免 `0x`/變長量編碼卡死 |
| 缺少 DAW 導入指引文件 | Major | 已補齊 | `docs/daw-bundle-export.md` + `docs/daw-bundle-export.zh-TW.md` |
| 用戶輸出文檔要有繁中版本 | Major | 已補齊 | DAW bundle 使用說明同時提供英文與繁中版本 |

## Verification performed

```bash
PYTHONPATH=src python3 -m pytest -q tests/unit/test_exporters.py tests/e2e/test_cli_export.py tests/e2e/test_cli_full_song_length.py
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m compileall src tests
```

## Review result

批准進入下一個 Git 流程節點，建議一併執行完整 `guitar-tab-generation --help` 與 `export --help` 進行文件一致性復核。

