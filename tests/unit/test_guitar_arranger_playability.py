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


def test_arranger_assigns_fingers_and_hand_position() -> None:
    positions, warnings, _ = arrange_notes([
        note("n1", 64, 0.0),
        note("n2", 65, 0.5),
    ])

    assert warnings == []
    assert positions[0]["hand_position"] >= 1
    assert positions[1]["finger"] in {1, 2, 3, 4}
    assert "position_shift" in positions[1]


def test_arranger_warns_on_large_position_shift() -> None:
    positions, warnings, _ = arrange_notes([
        note("n1", 40, 0.0),
        note("n2", 84, 0.5),
    ])

    assert positions
    assert any(warning["code"] == "LARGE_POSITION_SHIFT" for warning in warnings)


def test_arranger_warns_on_max_stretch_window() -> None:
    simultaneous = [
        note("n1", 64, 0.0),
        note("n2", 72, 0.0),
        note("n3", 79, 0.0),
    ]

    _, warnings, _ = arrange_notes(simultaneous)

    assert any(warning["code"] == "MAX_STRETCH_EXCEEDED" for warning in warnings)
