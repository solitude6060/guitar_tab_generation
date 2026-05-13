from __future__ import annotations

import pytest

from guitar_tab_generation.backends import BackendExecutionError, resolve_backend
from guitar_tab_generation.pipeline import transcribe_to_tab


def test_default_pipeline_uses_fixture_backend(tmp_path) -> None:
    arrangement, quality_report = transcribe_to_tab(
        "fixtures/simple_chords_30_90s.wav",
        tmp_path,
    )
    assert quality_report["status"] == "passed"
    assert arrangement["timebase"]["provenance"]["backend"] == "fixture"
    assert arrangement["note_events"][0]["provenance"]["backend"] == "fixture"
    assert arrangement["chord_spans"][0]["provenance"]["backend"] == "fixture"
    assert arrangement["section_spans"][0]["provenance"]["backend"] == "fixture"


def test_unknown_backend_fails_with_clear_message() -> None:
    with pytest.raises(BackendExecutionError) as exc:
        resolve_backend("missing-backend")
    assert "Unknown analysis backend" in str(exc.value)
    assert "fixture" in str(exc.value)


def test_optional_real_backend_placeholder_is_import_guarded() -> None:
    with pytest.raises(BackendExecutionError) as exc:
        resolve_backend("real")
    assert "Optional backend 'real' is not installed" in str(exc.value)
