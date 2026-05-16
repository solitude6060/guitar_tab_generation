# P16 PR Code Review：DAW 多軌匯出 Bundle

## 審查範圍

本次審查 P16：`export --format daw` 的輸出流程（bundle、多軌 MIDI/MusicXML、manifest、README）與
既有 `musicxml` / `midi` CLI 相容性。

## 審查結果

| 發現 | 嚴重性 | 決策 | 證據 |
|---|---|---|---|
| Full-song chunk 計畫未能輸出多軌，會影響 DAW 匯入 | Blocker | 已修正 | `write_export(..., "daw")` 依 `duration_class` 與 `processing_plan.mode` 輸出 `track-01...track-N` |
| 重疊音符可能造成 MIDI delta 負值，導致匯出卡死 | Major | 已修正 | `render_midi` 改用 `max(0, start_tick - last_tick)`，避免變長量編碼碰到負值 |
| 缺少 DAW 導入指引文件 | Major | 已補齊 | 新增 `docs/daw-bundle-export.md` 與 `docs/daw-bundle-export.zh-TW.md` |
| 使用者文件需有繁中版本 | Major | 已補齊 | DAW bundle 使用說明同時提供英文與繁中版本 |

## 驗證紀錄

```bash
PYTHONPATH=src python3 -m pytest -q tests/unit/test_exporters.py tests/e2e/test_cli_export.py tests/e2e/test_cli_full_song_length.py
PYTHONPATH=src python3 -m pytest -q
PYTHONPATH=src python3 -m compileall src tests
```

## 審查結論

批准進入後續 Git 流程，建議再補一次 `guitar-tab-generation export --help` 與 `--format daw`
文件一致性檢核，確保 CLI 幫助訊息與規格對齊。

