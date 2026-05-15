# P13 Test Spec：Local AI Backend Registry

## Scope

Add deterministic registry tests without installing or importing heavy AI
libraries.

## Red tests first

1. `tests/unit/test_ai_backends.py`
   - `test_backend_registry_lists_selected_local_models`
   - `test_backend_status_uses_injected_command_and_import_checks`
   - `test_backend_markdown_is_traditional_chinese_and_local_first`
2. `tests/test_ai_backends_cli.py`
   - `test_ai_backends_json_cli_outputs_registry`
   - `test_ai_backends_markdown_cli_outputs_registry`
   - `test_doctor_ai_json_includes_ai_backends`

## Expected behavior

- Registry contains `basic-pitch`, `demucs`, `torchcrepe`, `essentia`, and
  `local-llm`.
- All registry rows are local-first.
- Availability is computed from injected command/import checks in tests.
- Markdown output includes Traditional Chinese section titles.
- JSON output includes `resource_profile == "local-rtx-4090-first"` and a
  `backends` list.

## Verification commands

```bash
uv run pytest -q tests/unit/test_ai_backends.py tests/test_ai_backends_cli.py
uv run pytest -q
uv run guitar-tab-generation ai-backends --help
uv run guitar-tab-generation ai-backends --json
uv run guitar-tab-generation doctor-ai --json
git ls-files .omx
git log -5 --format=%B
```
