from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.contracts import WARNING_LOW_SECTION_CONFIDENCE
from guitar_tab_generation.section_sidecar import (
    SectionDetectionError,
    build_section_sidecar,
    write_section_sidecar,
)


def _arrangement_with_sections() -> dict:
    return {
        "section_spans": [
            {"label": "Verse", "start": 0.0, "end": 8.0, "confidence": 0.81},
            {"label": "Chorus", "start": 8.0, "end": 16.0, "confidence": 0.79},
        ],
        "chord_spans": [],
        "note_events": [],
    }


def test_build_section_sidecar_from_arrangement_section_spans() -> None:
    sidecar = build_section_sidecar(_arrangement_with_sections())

    assert sidecar["schema"] == "guitar-tab-generation.sections.v1"
    assert sidecar["backend"] == "deterministic-arrangement"
    assert sidecar["summary"] == {
        "section_count": 2,
        "average_confidence": pytest.approx(0.8),
        "low_confidence_count": 0,
    }
    assert [section["label"] for section in sidecar["sections"]] == ["Verse", "Chorus"]
    assert sidecar["sections"][0]["provenance"] == {
        "stage": "section_detection",
        "source": "arrangement.section_spans",
        "backend": "deterministic-arrangement",
    }
    assert sidecar["warnings"] == []


def test_build_section_sidecar_warns_on_low_confidence() -> None:
    arrangement = _arrangement_with_sections()
    arrangement["section_spans"][1]["confidence"] = 0.41

    sidecar = build_section_sidecar(arrangement)

    assert sidecar["summary"]["low_confidence_count"] == 1
    assert sidecar["warnings"][0]["code"] == WARNING_LOW_SECTION_CONFIDENCE
    assert "Chorus" in sidecar["warnings"][0]["message"]


def test_build_section_sidecar_falls_back_to_chord_window() -> None:
    sidecar = build_section_sidecar(
        {
            "section_spans": [],
            "chord_spans": [
                {"label": "G", "start": 0.0, "end": 4.0, "confidence": 0.8},
                {"label": "D", "start": 4.0, "end": 8.0, "confidence": 0.7},
            ],
            "note_events": [],
        }
    )

    assert sidecar["sections"][0]["label"] == "Chord progression"
    assert sidecar["sections"][0]["start"] == 0.0
    assert sidecar["sections"][0]["end"] == 8.0
    assert sidecar["sections"][0]["provenance"]["source"] == "arrangement.chord_spans"


def test_build_section_sidecar_falls_back_to_note_window() -> None:
    sidecar = build_section_sidecar(
        {
            "section_spans": [],
            "chord_spans": [],
            "note_events": [
                {"id": "n1", "start": 1.0, "end": 1.5, "confidence": 0.8},
                {"id": "n2", "start": 2.0, "end": 3.0, "confidence": 0.6},
            ],
        }
    )

    assert sidecar["sections"][0]["label"] == "Note sketch"
    assert sidecar["sections"][0]["start"] == 1.0
    assert sidecar["sections"][0]["end"] == 3.0
    assert sidecar["sections"][0]["provenance"]["source"] == "arrangement.note_events"


def test_build_section_sidecar_rejects_missing_inputs() -> None:
    with pytest.raises(SectionDetectionError, match="No section, chord, or note events"):
        build_section_sidecar({"section_spans": [], "chord_spans": [], "note_events": []})


def test_write_section_sidecar_defaults_to_artifact_dir(tmp_path: Path) -> None:
    (tmp_path / "arrangement.json").write_text(json.dumps(_arrangement_with_sections()), encoding="utf-8")

    written = write_section_sidecar(tmp_path)

    assert written == tmp_path / "sections.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["summary"]["section_count"] == 2
