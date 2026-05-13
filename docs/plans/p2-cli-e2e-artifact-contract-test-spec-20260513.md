# P2 Test Spec：CLI E2E Artifact Contract

日期：2026-05-13
對應 PRD：`docs/plans/p2-cli-e2e-artifact-contract-prd-20260513.md`

## 1. Red tests

新增 `tests/e2e/test_cli_fixture_artifacts.py`：

1. parameterize 三個 fixtures。
2. 透過 CLI main 或 subprocess 執行 transcribe 到 `tmp_path`。
3. 先 assert 七個 artifact files 必須存在。
4. `arrangement.json` 用 `assert_arrangement_contract`。
5. `quality_report.json` 用 `assert_quality_report_contract` 或 equivalent。
6. `tab.md` 需包含 fixture id / section / chord / warning text。

## 2. Regression commands

```bash
uv run pytest -q tests/e2e/test_cli_fixture_artifacts.py
uv run pytest -q
uv run guitar-tab-generation --help
```

## 3. Hard fail

- CLI 只產生 raw notes/MIDI dump。
- 任一 golden fixture 缺 artifact。
- warning 在 tab/report/arrangement 不一致。
- URL path 產生 media artifact。

## 4. Executable Coverage（2026-05-13）

已新增並通過：

- `tests/e2e/test_cli_fixture_artifacts.py`
  - 三個 golden fixtures 端到端 CLI artifact contract。
  - URL policy gate 無 media artifact。

驗證證據：

```bash
uv run pytest -q
# 34 passed
uv run guitar-tab-generation --help
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p2-simple
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-p2-riff
uv run guitar-tab-generation transcribe fixtures/single_note_lead_30_90s.wav --backend fixture --out /tmp/guitar-tab-p2-lead
```
