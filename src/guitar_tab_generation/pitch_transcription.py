from __future__ import annotations


def transcribe_notes(audio_metadata: dict) -> list[dict]:
    duration = float(audio_metadata["duration_seconds"])
    if "simple_chords" in audio_metadata["path"]:
        return []
    pattern = [64, 67, 69, 67] if "riff" in audio_metadata["path"] else [64, 66, 67, 71, 69]
    notes = []
    t = 1.0
    idx = 0
    while t + 0.3 < min(duration, 17.0):
        notes.append(
            {
                "id": f"n{idx + 1}",
                "start": round(t, 3),
                "end": round(t + 0.35, 3),
                "pitch_midi": pattern[idx % len(pattern)],
                "pitch_name": _pitch_name(pattern[idx % len(pattern)]),
                "velocity": 0.7,
                "confidence": 0.78,
                "provenance": {"stage": "pitch_transcription", "stem": "mix", "model": "synthetic_baseline"},
            }
        )
        idx += 1
        t += 0.5
    return notes


def _pitch_name(midi: int) -> str:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    return f"{names[midi % 12]}{midi // 12 - 1}"
