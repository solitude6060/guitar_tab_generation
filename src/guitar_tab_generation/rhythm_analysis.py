from __future__ import annotations


def analyze_rhythm(audio_metadata: dict) -> dict:
    duration = float(audio_metadata["duration_seconds"])
    tempo = 120.0
    beat_interval = 60.0 / tempo
    beats = [{"time": round(i * beat_interval, 3), "beat": (i % 4) + 1} for i in range(int(duration / beat_interval) + 1)]
    bars = []
    for idx in range(0, len(beats), 4):
        start = beats[idx]["time"]
        end = min(start + 4 * beat_interval, duration)
        bars.append({"index": len(bars) + 1, "start": round(start, 3), "end": round(end, 3)})
    return {
        "sample_rate": audio_metadata["sample_rate"],
        "tempo_bpm": tempo,
        "beats": beats,
        "bars": bars,
        "time_signature": "4/4",
    }
