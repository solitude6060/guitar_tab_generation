from __future__ import annotations

import pytest

from guitar_tab_generation.backends import BackendExecutionError, FixtureAnalysisBackend, validate_backend_items


def test_backend_contract_requires_backend_and_stage_provenance() -> None:
    with pytest.raises(BackendExecutionError) as exc:
        validate_backend_items(
            "note_events",
            [
                {
                    "id": "n1",
                    "start": 0.0,
                    "end": 0.5,
                    "pitch_midi": 64,
                    "confidence": 0.8,
                    "provenance": {"stage": "pitch_transcription"},
                }
            ],
        )
    assert "provenance.backend" in str(exc.value)


def test_fixture_backend_outputs_backend_provenance() -> None:
    backend = FixtureAnalysisBackend()
    notes, warnings = backend.transcribe_notes(30.0, None)
    assert warnings == []
    assert notes
    assert notes[0]["provenance"]["stage"] == "pitch_transcription"
    assert notes[0]["provenance"]["backend"] == "fixture"


def test_backend_exception_is_wrapped_with_clear_domain_error() -> None:
    class BrokenBackend(FixtureAnalysisBackend):
        name = "broken"

        def transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None):
            raise RuntimeError("third party exploded")

    with pytest.raises(BackendExecutionError) as exc:
        BrokenBackend().safe_transcribe_notes(30.0, None)
    assert "broken note backend failed" in str(exc.value)
    assert "third party exploded" in str(exc.value)
