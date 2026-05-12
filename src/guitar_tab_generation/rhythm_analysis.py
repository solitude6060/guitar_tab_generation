"""Deterministic baseline rhythm analysis."""
from __future__ import annotations


def analyze_rhythm(duration_seconds: float, fixture_metadata: dict | None = None) -> dict:
    tempo = float((fixture_metadata or {}).get("tempo_bpm", 96.0))
    return {"tempo_bpm": tempo, "confidence": 0.8, "time_signature": "4/4"}
