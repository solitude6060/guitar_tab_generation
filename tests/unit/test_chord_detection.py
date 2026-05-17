from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.chord_detection import (
    ChordDetectionError,
    build_chord_sidecar,
    write_chord_sidecar,
)
from guitar_tab_generation.contracts import WARNING_LOW_CHORD_CONFIDENCE


def _arrangement_with_chords() -> dict:
    return {
        "source": {"input_uri": "fixtures/simple_chords_30_90s.wav"},
        "chord_spans": [
            {"label": "Em", "start": 0.0, "end": 4.0, "confidence": 0.91},
            {"label": "G", "start": 4.0, "end": 8.0, "confidence": 0.89},
        ],
        "note_events": [],
    }


def test_build_chord_sidecar_from_arrangement_chord_spans() -> None:
    sidecar = build_chord_sidecar(_arrangement_with_chords())

    assert sidecar["schema"] == "guitar-tab-generation.chords.v1"
    assert sidecar["backend"] == "deterministic-arrangement"
    assert sidecar["summary"] == {
        "chord_count": 2,
        "average_confidence": pytest.approx(0.9),
        "low_confidence_count": 0,
    }
    assert [chord["label"] for chord in sidecar["chords"]] == ["Em", "G"]
    assert sidecar["chords"][0]["provenance"] == {
        "stage": "chord_detection",
        "source": "arrangement.chord_spans",
        "backend": "deterministic-arrangement",
    }
    assert sidecar["warnings"] == []


def test_build_chord_sidecar_warns_on_low_confidence() -> None:
    arrangement = _arrangement_with_chords()
    arrangement["chord_spans"][1]["confidence"] = 0.41

    sidecar = build_chord_sidecar(arrangement)

    assert sidecar["summary"]["low_confidence_count"] == 1
    assert sidecar["warnings"][0]["code"] == WARNING_LOW_CHORD_CONFIDENCE
    assert "G" in sidecar["warnings"][0]["message"]


def test_build_chord_sidecar_rejects_missing_inputs() -> None:
    with pytest.raises(ChordDetectionError, match="No chord or note events"):
        build_chord_sidecar({"chord_spans": [], "note_events": []})


def test_build_chord_sidecar_can_infer_single_chord_from_notes() -> None:
    sidecar = build_chord_sidecar(
        {
            "chord_spans": [],
            "note_events": [
                {"id": "n1", "start": 0.0, "end": 1.0, "pitch_midi": 60, "confidence": 0.8},
                {"id": "n2", "start": 0.0, "end": 1.0, "pitch_midi": 64, "confidence": 0.7},
                {"id": "n3", "start": 0.0, "end": 1.0, "pitch_midi": 67, "confidence": 0.9},
            ],
        }
    )

    assert sidecar["chords"][0]["label"] == "C"
    assert sidecar["chords"][0]["start"] == 0.0
    assert sidecar["chords"][0]["end"] == 1.0
    assert sidecar["chords"][0]["provenance"]["source"] == "arrangement.note_events"


def test_write_chord_sidecar_defaults_to_artifact_dir(tmp_path: Path) -> None:
    (tmp_path / "arrangement.json").write_text(json.dumps(_arrangement_with_chords()), encoding="utf-8")

    written = write_chord_sidecar(tmp_path)

    assert written == tmp_path / "chords.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["summary"]["chord_count"] == 2
