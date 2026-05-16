"""Pluggable analysis backend contracts for the MVP pipeline.

The default backend remains deterministic and fixture-driven. Future heavy
analysis backends should implement the same contract behind optional imports so
CI and golden fixtures stay reproducible.
"""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from .rhythm_analysis import analyze_rhythm
from .section_detector import detect_sections
from .tonal_chord_analysis import analyze_chords
from .pitch_transcription import transcribe_notes


class BackendExecutionError(RuntimeError):
    """Raised when backend selection or execution violates the pipeline contract."""


@runtime_checkable
class AnalysisBackend(Protocol):
    """Protocol shared by deterministic and future real audio analysis backends."""

    name: str

    def analyze_rhythm(self, duration_seconds: float, fixture_metadata: dict | None = None) -> dict:
        """Return rhythm/timebase metadata with confidence and provenance."""

    def analyze_chords(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        """Return chord spans and warnings."""

    def transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        """Return note events and warnings."""

    def detect_sections(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        """Return section spans and warnings."""


def _ensure_backend_provenance(item: dict, *, backend: str, stage: str | None = None) -> dict:
    provenance = item.setdefault("provenance", {})
    if not isinstance(provenance, dict):
        raise BackendExecutionError("Backend item provenance must be an object.")
    provenance.setdefault("backend", backend)
    if stage is not None:
        provenance.setdefault("stage", stage)
    return item


def validate_backend_items(collection_name: str, items: list[dict]) -> None:
    """Validate backend event/span provenance before quality/report rendering."""
    for index, item in enumerate(items):
        confidence = item.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            raise BackendExecutionError(f"{collection_name}[{index}].confidence must be numeric.")
        provenance = item.get("provenance")
        if not isinstance(provenance, dict):
            raise BackendExecutionError(f"{collection_name}[{index}].provenance must be an object.")
        if not provenance.get("stage"):
            raise BackendExecutionError(f"{collection_name}[{index}].provenance.stage is required.")
        if not provenance.get("backend"):
            raise BackendExecutionError(f"{collection_name}[{index}].provenance.backend is required.")


class FixtureAnalysisBackend:
    """Deterministic fixture/default backend used for tests and MVP scaffolding."""

    name = "fixture"

    def analyze_rhythm(self, duration_seconds: float, fixture_metadata: dict | None = None) -> dict:
        rhythm = analyze_rhythm(duration_seconds, fixture_metadata)
        rhythm["provenance"] = {"stage": "rhythm_analysis", "backend": self.name, "stem": "mix"}
        return rhythm

    def analyze_chords(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        chords, warnings = analyze_chords(duration_seconds, fixture_metadata)
        for chord in chords:
            _ensure_backend_provenance(chord, backend=self.name, stage="tonal_chord_analysis")
        validate_backend_items("chord_spans", chords)
        return chords, warnings

    def transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        notes, warnings = transcribe_notes(duration_seconds, fixture_metadata)
        for note in notes:
            _ensure_backend_provenance(note, backend=self.name, stage="pitch_transcription")
        validate_backend_items("note_events", notes)
        return notes, warnings

    def detect_sections(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        sections, warnings = detect_sections(duration_seconds, fixture_metadata)
        for section in sections:
            _ensure_backend_provenance(section, backend=self.name, stage="section_detector")
        validate_backend_items("section_spans", sections)
        return sections, warnings

    def safe_analyze_rhythm(self, duration_seconds: float, fixture_metadata: dict | None = None) -> dict:
        try:
            return self.analyze_rhythm(duration_seconds, fixture_metadata)
        except BackendExecutionError:
            raise
        except Exception as exc:  # pragma: no cover - exercised by subclass tests
            raise BackendExecutionError(f"{self.name} rhythm backend failed: {exc}") from exc

    def safe_analyze_chords(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        try:
            return self.analyze_chords(duration_seconds, fixture_metadata)
        except BackendExecutionError:
            raise
        except Exception as exc:  # pragma: no cover - exercised by subclass tests
            raise BackendExecutionError(f"{self.name} chord backend failed: {exc}") from exc

    def safe_transcribe_notes(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        try:
            return self.transcribe_notes(duration_seconds, fixture_metadata)
        except BackendExecutionError:
            raise
        except Exception as exc:
            raise BackendExecutionError(f"{self.name} note backend failed: {exc}") from exc

    def safe_detect_sections(self, duration_seconds: float, fixture_metadata: dict | None = None) -> tuple[list[dict], list[dict]]:
        try:
            return self.detect_sections(duration_seconds, fixture_metadata)
        except BackendExecutionError:
            raise
        except Exception as exc:  # pragma: no cover - exercised by integration if subclassed
            raise BackendExecutionError(f"{self.name} section backend failed: {exc}") from exc


def resolve_backend(
    name: str | AnalysisBackend | None = None,
    *,
    audio_path: Path | None = None,
) -> AnalysisBackend:
    """Resolve an analysis backend by name without importing heavy optional deps."""
    if name is None or name == "fixture":
        return FixtureAnalysisBackend()
    if not isinstance(name, str):
        return name
    if name == "basic-pitch":
        from .basic_pitch_backend import BasicPitchAnalysisBackend

        return BasicPitchAnalysisBackend(audio_path=audio_path)
    if name in {"real", "librosa"}:
        raise BackendExecutionError(
            f"Optional backend {name!r} is not installed or enabled in the MVP. "
            "Use backend 'fixture' or add an ADR before introducing heavy dependencies."
        )
    raise BackendExecutionError(f"Unknown analysis backend {name!r}. Available backends: fixture, basic-pitch.")
