# P21 Test Spec：F0 Calibration Consumption

## Scope

讓 P20 `f0_calibration.json` 被 viewer / interface / tutorial 消費。

## Tests

### Unit

- parse calibration summary。
- classify pitch risk by `delta_semitones` 與 `periodicity_confidence`。
- missing calibration returns empty optional state。

### E2E

- `view` includes F0 summary when file exists。
- `interface` includes pitch-risk notes table。
- `tutorial` includes pitch-specific practice guidance。
- missing file keeps previous behavior。

## Verification commands

```bash
uv run pytest -q tests/unit/test_f0_calibration_consumption.py tests/e2e/test_cli_f0_calibration_consumption.py
uv run pytest -q
uv run guitar-tab-generation view --help
uv run guitar-tab-generation interface --help
uv run guitar-tab-generation tutorial --help
```
