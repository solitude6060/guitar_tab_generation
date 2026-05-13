from __future__ import annotations

from guitar_tab_generation.guitar_arranger import arrange_notes


def note(note_id: str, midi: int, start: float) -> dict:
    return {
        "id": note_id,
        "pitch_midi": midi,
        "start": start,
        "end": start + 0.25,
        "confidence": 0.8,
    }


def test_arranger_prefers_nearby_hand_position_over_lowest_fret_default() -> None:
    positions, warnings, _ = arrange_notes([
        note("n1", 71, 0.0),  # B4: best initial option is string 1 fret 7.
        note("n2", 64, 0.5),  # E4 can be open string 1, but fret 5 is closer to fret 7.
    ])

    assert warnings == []
    assert positions[0]["string"] == 1
    assert positions[0]["fret"] == 7
    assert positions[1]["string"] == 2
    assert positions[1]["fret"] == 5


def test_arranger_degrades_high_density_note_dump_to_sketch() -> None:
    notes = [note(f"n{i}", 64 + (i % 5), i * 0.05) for i in range(48)]

    positions, warnings, _ = arrange_notes(notes)

    assert len(positions) < len(notes)
    assert len(positions) <= 32
    assert any(warning["code"] == "DENSE_NOTE_SKETCH_DEGRADED" for warning in warnings)


def test_arranger_unplayable_note_adds_error_warning_without_position() -> None:
    positions, warnings, confidence = arrange_notes([note("too_low", 20, 0.0)])

    assert positions == []
    assert confidence == 0.0
    assert warnings[0]["code"] == "UNPLAYABLE_NOTE"
