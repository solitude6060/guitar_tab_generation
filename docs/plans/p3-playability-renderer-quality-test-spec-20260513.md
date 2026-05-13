# P3 Test Spec：Playability + Renderer Quality

日期：2026-05-13
對應 PRD：`docs/plans/p3-playability-renderer-quality-prd-20260513.md`

## 1. Red tests

新增或擴充：

- `tests/unit/test_guitar_arranger_playability.py`
  - 同音多位置選擇手位較近者。
  - 超出 fret range 時 degraded/hard fail。
  - 過高密度 notes 不產生不可讀 TAB dump。
- `tests/unit/test_renderer_tab_quality.py`
  - tab.md 包含 metadata/sections/chords/TAB/warnings。
  - unplayable 不渲染為正常 fret number。
- `tests/e2e/test_tab_snapshot_contract.py`
  - 三個 fixtures 的 tab output 包含固定關鍵段落。

## 2. Regression commands

```bash
uv run pytest -q
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p3-simple
```

## 3. Hard fail

- Renderer 忽略 warning。
- Unplayable position 出現在正常 TAB。
- TAB 缺 sections/chords。

## 4. Executable Coverage（2026-05-13）

已新增並通過：

- `tests/unit/test_guitar_arranger_playability.py`
  - 手位鄰近選擇。
  - 高密度 notes 降級為 sketch。
  - 不可彈 note 只產生 error warning，不產生 position。
- `tests/unit/test_renderer_tab_quality.py`
  - metadata / sections / chords / TAB / warnings。
  - unplayable 不渲染為正常 TAB。
- `tests/e2e/test_tab_snapshot_contract.py`
  - 三個 fixtures 的 tab output 含固定練習關鍵段落。

驗證證據：

```bash
uv run pytest -q
# 42 passed
uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend fixture --out /tmp/guitar-tab-p3-simple
```
