"""Test-only contract validators for the guitar TAB MVP artifacts.

These helpers intentionally live under tests/ so they can pin the approved PRD/test-spec
contracts without owning production implementation modules that other workers may create.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

CONFIDENCE_THRESHOLDS = {
    "notes": 0.55,
    "chords": 0.60,
    "sections": 0.50,
    "fingering": 0.65,
}
REQUIRED_WARNING_KEYS = {"code", "severity", "message"}
SUPPORTED_AUDIO_SUFFIXES = {".mp3", ".wav", ".flac", ".m4a"}
URL_POLICY_CODES = {"URL_POLICY_GATE", "URL_INPUT_DISABLED"}


class ContractError(AssertionError):
    """Raised when a fixture violates the approved MVP contract."""


def require_keys(mapping: dict[str, Any], keys: Iterable[str], context: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise ContractError(f"{context} missing required keys: {', '.join(missing)}")


def _warning_codes(artifact: dict[str, Any]) -> set[str]:
    return {warning.get("code", "") for warning in artifact.get("warnings", [])}


def assert_warning_shape(artifact: dict[str, Any]) -> None:
    for index, warning in enumerate(artifact.get("warnings", [])):
        require_keys(warning, REQUIRED_WARNING_KEYS, f"warnings[{index}]")
        if warning["severity"] not in {"info", "warning", "error"}:
            raise ContractError(f"warnings[{index}] severity must be info/warning/error")
        if "time_range" in warning:
            time_range = warning["time_range"]
            if not (
                isinstance(time_range, list)
                and len(time_range) == 2
                and time_range[0] <= time_range[1]
            ):
                raise ContractError(f"warnings[{index}] time_range must be [start, end]")


def assert_arrangement_contract(artifact: dict[str, Any]) -> None:
    require_keys(
        artifact,
        [
            "schema_version",
            "timebase",
            "source",
            "confidence",
            "warnings",
            "note_events",
            "chord_spans",
            "section_spans",
            "fretboard",
            "positions",
            "render_hints",
        ],
        "arrangement.json",
    )
    assert_warning_shape(artifact)
    _assert_timebase(artifact["timebase"])
    _assert_source(artifact["source"])
    _assert_confidence(artifact["confidence"])
    _assert_fretboard(artifact["fretboard"])
    _assert_note_events(artifact)
    _assert_chord_spans(artifact)
    _assert_section_spans(artifact)
    _assert_positions(artifact)
    _assert_render_hints(artifact["render_hints"])
    _assert_low_confidence_has_warnings(artifact)


def _assert_timebase(timebase: dict[str, Any]) -> None:
    require_keys(timebase, ["sample_rate", "tempo_bpm", "beats", "bars", "time_signature"], "timebase")
    if timebase["sample_rate"] <= 0 or timebase["tempo_bpm"] <= 0:
        raise ContractError("timebase sample_rate and tempo_bpm must be positive")
    for index, beat in enumerate(timebase["beats"]):
        require_keys(beat, ["time", "beat"], f"timebase.beats[{index}]")
        if beat["time"] < 0:
            raise ContractError(f"timebase.beats[{index}] time must be non-negative seconds")
    for index, bar in enumerate(timebase["bars"]):
        require_keys(bar, ["index", "start", "end"], f"timebase.bars[{index}]")
        if bar["start"] < 0 or bar["end"] <= bar["start"]:
            raise ContractError(f"timebase.bars[{index}] must have increasing second offsets")


def _assert_source(source: dict[str, Any]) -> None:
    require_keys(source, ["input_type", "input_uri", "rights_attestation", "trim", "stems"], "source")
    if source["input_type"] != "local_audio":
        raise ContractError("MVP arrangement source must be local_audio")
    require_keys(source["trim"], ["start", "end"], "source.trim")
    duration = source["trim"]["end"] - source["trim"]["start"]
    if not 30 <= duration <= 90:
        raise ContractError("MVP golden fixture duration must be 30-90 seconds")
    if not source["stems"]:
        raise ContractError("source.stems must include at least the normalized mix stem")
    for index, stem in enumerate(source["stems"]):
        require_keys(stem, ["name", "path", "model", "confidence", "provenance"], f"source.stems[{index}]")
        require_keys(stem["provenance"], ["stage", "input"], f"source.stems[{index}].provenance")


def _assert_confidence(confidence: dict[str, Any]) -> None:
    require_keys(confidence, ["overall", "rhythm", "chords", "notes", "fingering"], "confidence")
    thresholds = confidence.get("thresholds", CONFIDENCE_THRESHOLDS)
    for key, minimum in CONFIDENCE_THRESHOLDS.items():
        if thresholds.get(key) != minimum:
            raise ContractError(f"confidence.thresholds.{key} must be {minimum}")
    for key in ["overall", "rhythm", "chords", "notes", "fingering"]:
        if not 0 <= confidence[key] <= 1:
            raise ContractError(f"confidence.{key} must be between 0 and 1")


def _assert_fretboard(fretboard: dict[str, Any]) -> None:
    require_keys(fretboard, ["tuning", "capo", "supported_fret_range"], "fretboard")
    if fretboard["tuning"] != ["E2", "A2", "D3", "G3", "B3", "E4"]:
        raise ContractError("MVP supports standard EADGBE tuning only")
    if fretboard["capo"] != 0:
        raise ContractError("MVP fixtures must not require capo/alternate tuning")
    if fretboard["supported_fret_range"] != {"min": 0, "max": 20}:
        raise ContractError("supported_fret_range must be min=0 max=20")


def _assert_note_events(artifact: dict[str, Any]) -> None:
    for index, note in enumerate(artifact["note_events"]):
        require_keys(note, ["id", "start", "end", "pitch_midi", "confidence", "provenance"], f"note_events[{index}]")
        if note["end"] <= note["start"] or note["start"] < 0:
            raise ContractError(f"note_events[{index}] must have increasing second offsets")
        if not 0 <= note["confidence"] <= 1:
            raise ContractError(f"note_events[{index}].confidence must be between 0 and 1")
        require_keys(note["provenance"], ["stage", "stem", "backend"], f"note_events[{index}].provenance")


def _assert_chord_spans(artifact: dict[str, Any]) -> None:
    for index, chord in enumerate(artifact["chord_spans"]):
        require_keys(chord, ["start", "end", "label", "confidence", "provenance"], f"chord_spans[{index}]")
        if chord["end"] <= chord["start"] or chord["start"] < 0:
            raise ContractError(f"chord_spans[{index}] must have increasing second offsets")
        require_keys(chord["provenance"], ["stage", "stem", "backend"], f"chord_spans[{index}].provenance")


def _assert_section_spans(artifact: dict[str, Any]) -> None:
    for index, section in enumerate(artifact["section_spans"]):
        require_keys(section, ["start", "end", "label", "confidence", "provenance"], f"section_spans[{index}]")
        if section["end"] <= section["start"] or section["start"] < 0:
            raise ContractError(f"section_spans[{index}] must have increasing second offsets")
        require_keys(section["provenance"], ["stage", "backend"], f"section_spans[{index}].provenance")


def _assert_positions(artifact: dict[str, Any]) -> None:
    note_ids = {note["id"] for note in artifact["note_events"]}
    for index, position in enumerate(artifact["positions"]):
        require_keys(position, ["note_id", "string", "fret", "confidence", "playability"], f"positions[{index}]")
        if position["note_id"] not in note_ids:
            raise ContractError(f"positions[{index}] references missing note_id")
        if not 1 <= position["string"] <= 6:
            raise ContractError(f"positions[{index}].string must be 1-6")
        if not 0 <= position["fret"] <= 20:
            raise ContractError(f"positions[{index}].fret must be 0-20")
        if position["playability"] not in {"playable", "degraded", "unplayable"}:
            raise ContractError(f"positions[{index}].playability has invalid value")


def _assert_render_hints(render_hints: dict[str, Any]) -> None:
    require_keys(
        render_hints,
        ["tab_density", "show_rhythm_slashes", "show_warnings_inline", "preferred_output"],
        "render_hints",
    )
    if render_hints["preferred_output"] != "markdown":
        raise ContractError("MVP preferred_output must be markdown")


def _assert_low_confidence_has_warnings(artifact: dict[str, Any]) -> None:
    codes = _warning_codes(artifact)
    for note in artifact["note_events"]:
        if note["confidence"] < CONFIDENCE_THRESHOLDS["notes"] and "LOW_NOTE_CONFIDENCE" not in codes:
            raise ContractError("low-confidence notes must produce LOW_NOTE_CONFIDENCE warning")
    for chord in artifact["chord_spans"]:
        if chord["confidence"] < CONFIDENCE_THRESHOLDS["chords"] and "LOW_CHORD_CONFIDENCE" not in codes:
            raise ContractError("low-confidence chords must produce LOW_CHORD_CONFIDENCE warning")
    for section in artifact["section_spans"]:
        if section["confidence"] < CONFIDENCE_THRESHOLDS["sections"] and "LOW_SECTION_CONFIDENCE" not in codes:
            raise ContractError("low-confidence sections must produce LOW_SECTION_CONFIDENCE warning")
    for position in artifact["positions"]:
        if position["confidence"] < CONFIDENCE_THRESHOLDS["fingering"] and "LOW_FINGERING_CONFIDENCE" not in codes:
            raise ContractError("low-confidence fingering must produce LOW_FINGERING_CONFIDENCE warning")


def assert_quality_report_contract(report: dict[str, Any], arrangement: dict[str, Any] | None = None) -> None:
    require_keys(report, ["status", "warnings", "hard_failures", "checks"], "quality_report.json")
    if report["status"] not in {"pass", "warning", "failed"}:
        raise ContractError("quality_report.status must be pass/warning/failed")
    assert_warning_shape(report)
    if report["status"] == "failed" and not report["hard_failures"]:
        raise ContractError("failed quality report must include hard_failures")
    if arrangement is not None:
        arrangement_codes = _warning_codes(arrangement)
        report_codes = _warning_codes(report)
        missing = arrangement_codes - report_codes
        if missing:
            raise ContractError(f"quality_report missing arrangement warning codes: {sorted(missing)}")


def assert_golden_manifest_contract(manifest: dict[str, Any], base_path: Path) -> None:
    require_keys(manifest, ["fixtures"], "golden manifest")
    expected_ids = {"simple_chords_30_90s", "single_note_riff_30_90s", "single_note_lead_30_90s"}
    fixtures = {fixture.get("id"): fixture for fixture in manifest["fixtures"]}
    if set(fixtures) != expected_ids:
        raise ContractError(f"golden manifest fixtures must be exactly {sorted(expected_ids)}")
    for fixture_id, fixture in fixtures.items():
        require_keys(
            fixture,
            [
                "id",
                "kind",
                "audio_path",
                "source_statement",
                "rights_attestation",
                "duration_seconds",
                "trim",
                "rubric_record",
                "expected_outputs",
            ],
            f"fixtures[{fixture_id}]",
        )
        if Path(fixture["audio_path"]).suffix not in SUPPORTED_AUDIO_SUFFIXES:
            raise ContractError(f"{fixture_id} audio_path must use supported local audio suffix")
        if fixture["rights_attestation"] not in {"self_created", "licensed", "public_domain"}:
            raise ContractError(f"{fixture_id} rights_attestation must be legally usable")
        if not 30 <= fixture["duration_seconds"] <= 90:
            raise ContractError(f"{fixture_id} duration must be 30-90 seconds")
        if fixture["trim"] != {"start": 0.0, "end": fixture["duration_seconds"]}:
            raise ContractError(f"{fixture_id} trim must match fixture duration for Phase 0 baseline")
        rubric_path = base_path / fixture["rubric_record"]
        if not rubric_path.exists():
            raise ContractError(f"{fixture_id} rubric record missing: {rubric_path}")
        require_keys(
            fixture["expected_outputs"],
            ["tab_md", "arrangement_json", "quality_report_json"],
            f"fixtures[{fixture_id}].expected_outputs",
        )


def assert_no_url_download_contract(policy_result: dict[str, Any]) -> None:
    require_keys(policy_result, ["input_type", "status", "warning", "download_attempted", "message"], "URL policy result")
    if policy_result["input_type"] != "url":
        raise ContractError("URL policy fixture must declare input_type=url")
    if policy_result["status"] != "blocked":
        raise ContractError("MVP URL inputs must be blocked by policy gate")
    if policy_result["download_attempted"] is not False:
        raise ContractError("URL policy gate must not attempt download or remote parsing")
    if policy_result["warning"].get("code") not in URL_POLICY_CODES:
        raise ContractError("URL policy warning code must document disabled/stub gate")
    message = policy_result["message"].lower()
    if "local" not in message or "rights" not in message:
        raise ContractError("URL policy message must direct users to legal local-audio alternatives")
