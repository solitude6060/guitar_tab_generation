# P30 Fingering + Playability v2 Test Spec

日期：2026-05-18
狀態：Planned

## Unit Tests

- `test_arranger_assigns_fingers_and_hand_position`
- `test_arranger_warns_on_large_position_shift`
- `test_arranger_warns_on_max_stretch_window`
- 既有 high density / unplayable / nearby position tests 維持通過。

## Regression Gate

```bash
uv sync --group dev
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
```
