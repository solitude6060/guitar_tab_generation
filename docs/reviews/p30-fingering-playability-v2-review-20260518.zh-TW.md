# P30 Fingering + Playability v2 Review

日期：2026-05-18
狀態：本地審查通過

## 範圍

- `docs/plans/p30-fingering-playability-v2-prd-20260518.md`
- `docs/plans/p30-fingering-playability-v2-test-spec-20260518.md`
- `src/guitar_tab_generation/guitar_arranger.py`
- `src/guitar_tab_generation/contracts.py`
- `tests/unit/test_guitar_arranger_playability.py`

## 審查結論

P30 保持 deterministic arranger，不新增依賴、不改 `transcribe` default，並補上可檢查的可彈性 metadata：

- `hand_position`
- `finger`
- `position_shift`
- `LARGE_POSITION_SHIFT`
- `MAX_STRETCH_EXCEEDED`

## 驗證證據

```bash
uv run pytest tests/unit/test_guitar_arranger_playability.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --backend fixture --out /tmp/guitar-tab-p30-demo-20260517T1713
```

結果：

- targeted tests：6 passed
- full regression：234 passed
- compileall：通過
- diff check：通過
- manual demo：`arrangement.json` positions 含 `finger`、`hand_position`、`position_shift`

## 剩餘風險

- 仍是 greedy heuristic，不是完整動態規劃。
- stretch 檢查以近同時 note window 為 MVP baseline，未解決所有 chord voicing 場景。
