# P17 Test Spec：DAW Workflow Usability（DAW 匯出可用性強化）

## Scope

驗證 DAW 匯出後的介面可用性是否更完整：使用者在 `interface.html` 能直接看到是否已有 DAW bundle、有哪些 track、以及基本匯入流程。

## Test cases

### Unit（`tests/unit/test_artifact_interface.py`）

1. `test_render_artifact_interface_html_uses_daw_manifest`
   - 建立 `daw_bundle/daw_manifest.json`。
   - 驗證 `DAW 匯出策略` 與 `track-XX.mid / track-XX.musicxml` 連結。

2. `test_render_artifact_interface_html_escapes_and_links_artifacts`
   - 保持新增 DAW 區塊文本在未產生 bundle 時顯示。

### E2E（`tests/e2e/test_cli_artifact_interface.py`）

1. `test_cli_interface_generates_html_workspace_for_golden_fixture`
   - 產出 `interface.html`。
   - 驗證其含 `DAW` 文案與 `guitar-tab-generation export --format daw` 提示。

2. `test_cli_interface_shows_daw_tracks_after_export`
   - 對 golden fixture 先 `transcribe` 後 `export --format daw`。
   - 再跑 `interface` 並驗證至少有 `track-01.mid` 連結。

## 驗收指令

```bash
python -m pytest -q tests/unit/test_artifact_interface.py tests/e2e/test_cli_artifact_interface.py
python -m pytest -q
python -m guitar_tab_generation.cli --help
```

## 風險與備援

- 若 `daw_manifest.json` 缺失/毀損：介面應以可用方式退化顯示，並列出可嘗試的檔名。
