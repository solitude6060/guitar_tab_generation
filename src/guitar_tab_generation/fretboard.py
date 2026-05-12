"""Standard-tuning guitar fretboard mapping."""
from __future__ import annotations

OPEN_STRING_MIDI_BY_STRING = {
    1: 64,  # E4 high string
    2: 59,  # B3
    3: 55,  # G3
    4: 50,  # D3
    5: 45,  # A2
    6: 40,  # E2 low string
}


def playable_positions(pitch_midi: int, *, max_fret: int = 20) -> list[dict]:
    positions: list[dict] = []
    for string, open_midi in OPEN_STRING_MIDI_BY_STRING.items():
        fret = pitch_midi - open_midi
        if 0 <= fret <= max_fret:
            positions.append({"string": string, "fret": fret})
    return sorted(positions, key=lambda p: (p["fret"], p["string"]))
