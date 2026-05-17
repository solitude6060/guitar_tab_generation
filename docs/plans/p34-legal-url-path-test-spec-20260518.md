# P34 Legal URL / YouTube Path Test Spec

日期：2026-05-18
狀態：Planned

## Tests

- unit：no-rights URL blocked。
- unit：YouTube URL blocked。
- unit：owned sample URL stub writes `source_policy.json`。
- e2e：`ingest-url --help`。
- e2e：CLI no-rights writes `policy_gate.txt`。
- e2e：CLI owned stub writes source policy。

## Regression Gate

```bash
uv sync --group dev
uv run pytest tests/unit/test_url_ingest.py tests/e2e/test_cli_ingest_url.py -q
uv run pytest -q
uv run python -m compileall -q src tests
git diff --check HEAD
uv run guitar-tab-generation ingest-url --help
```
