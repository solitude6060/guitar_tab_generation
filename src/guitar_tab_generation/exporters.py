"""MusicXML and MIDI export from existing transcription artifacts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import struct
from typing import Any

from .artifact_viewer import ArtifactBundle, load_artifact_bundle


PITCH_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
DEFAULT_DAW_TRACK_NAME = "guitar"


def _coerce_float(value: object, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_pitch(pitch_name: str) -> tuple[str, int, int]:
    step = pitch_name[0].upper() if pitch_name else "C"
    octave_text = "".join(ch for ch in pitch_name if ch.isdigit())
    octave = int(octave_text) if octave_text else 4
    alter = 1 if "#" in pitch_name else -1 if "b" in pitch_name else 0
    return step if step in PITCH_CLASSES else "C", alter, octave


def _midi_note_number(pitch_name: str) -> int:
    step, alter, octave = _parse_pitch(pitch_name)
    return (octave + 1) * 12 + PITCH_CLASSES[step] + alter


def _varlen(value: int) -> bytes:
    buffer = value & 0x7F
    value >>= 7
    while value:
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)
        value >>= 7
    output = bytearray()
    while True:
        output.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
        else:
            break
    return bytes(output)


def _render_note_rows(notes: list[dict[str, Any]]) -> list[str]:
    note_xml: list[str] = []
    for note in notes:
        step, alter, octave = _parse_pitch(str(note.get("pitch_name", "C4")))
        duration = max(1, round((_coerce_float(note.get("end", 0.0)) - _coerce_float(note.get("start", 0.0))) * 4))
        alter_xml = f"<alter>{alter}</alter>" if alter else ""
        note_xml.append(
            f"<note><pitch><step>{escape(step)}</step>{alter_xml}<octave>{octave}</octave></pitch>"
            f"<duration>{duration}</duration><type>quarter</type>"
            f"<lyric><text>confidence {note.get('confidence', 'unknown')}</text></lyric></note>"
        )
    if not note_xml:
        note_xml.append("<note><rest/><duration>4</duration><type>whole</type></note>")
    return note_xml


def _iter_notes_for_window(note_events: list[dict[str, Any]], *, start: float, end: float) -> list[dict[str, Any]]:
    selected = []
    for note in note_events:
        note_start = _coerce_float(note.get("start"), default=-1.0)
        note_end = _coerce_float(note.get("end"), default=note_start)
        if note_end <= start or note_start >= end:
            continue
        clip_start = max(note_start, start)
        clip_end = min(note_end, end)
        if clip_end <= clip_start:
            continue
        normalized = dict(note)
        normalized["start"] = clip_start
        normalized["end"] = clip_end
        selected.append(normalized)
    return sorted(selected, key=lambda item: _coerce_float(item.get("start", 0.0)))


def _track_plan(arrangement: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    source = arrangement.get("source", {})
    processing_plan = source.get("processing_plan", {}) if isinstance(source, dict) else {}
    mode = str(processing_plan.get("mode", "single_track"))

    note_events = arrangement.get("note_events", []) if isinstance(arrangement.get("note_events"), list) else []
    chunks = processing_plan.get("chunks") if isinstance(processing_plan, dict) else None
    if mode == "chunked_full_song" and isinstance(chunks, list) and chunks:
        tracks: list[dict[str, Any]] = []
        for index, chunk in enumerate(chunks, start=1):
            chunk_start = _coerce_float(chunk.get("start"), default=0.0)
            chunk_end = _coerce_float(chunk.get("end"), default=chunk_start)
            if chunk_end <= chunk_start:
                continue
            tracks.append({
                "strategy": "chunk",
                "name": f"chunk_{index}",
                "index": int(chunk.get("index", index)),
                "window": {
                    "start": chunk_start,
                    "end": chunk_end,
                },
                "notes": _iter_notes_for_window(note_events, start=chunk_start, end=chunk_end),
            })
        if tracks:
            return "chunked_full_song", tracks

    return "single_track", [
        {
            "strategy": "single",
            "name": DEFAULT_DAW_TRACK_NAME,
            "index": 1,
            "window": None,
            "notes": [
                note
                for note in note_events
                if isinstance(note, dict)
            ],
        },
    ]


def render_musicxml(bundle: ArtifactBundle, *, note_events: list[dict[str, Any]] | None = None, track_name: str = "Guitar") -> str:
    """Render a minimal parseable MusicXML score."""

    arrangement = bundle.arrangement
    notes = note_events if note_events is not None else arrangement.get("note_events", [])
    warnings = arrangement.get("warnings", [])
    confidence = arrangement.get("confidence", {}).get("overall", "unknown")
    source = arrangement.get("source", {}).get("input_uri", "unknown")
    note_xml = _render_note_rows(sorted(notes, key=lambda item: _coerce_float(item.get("start", 0.0))))

    warning_text = "; ".join(f"{w.get('code', 'UNKNOWN')}: {w.get('message', '')}" for w in warnings) or "None"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <work><work-title>Guitar TAB Export</work-title></work>
  <identification>
    <miscellaneous>
      <miscellaneous-field name="source">{escape(str(source))}</miscellaneous-field>
      <miscellaneous-field name="confidence">overall confidence {escape(str(confidence))}</miscellaneous-field>
      <miscellaneous-field name="warnings">{escape(warning_text)}</miscellaneous-field>
      <miscellaneous-field name="export_strategy">{escape(_track_plan(arrangement)[0])}</miscellaneous-field>
    </miscellaneous>
  </identification>
  <part-list><score-part id="P1"><part-name>{escape(track_name)}</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>4</divisions><key><fifths>0</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
      {''.join(note_xml)}
    </measure>
  </part>
</score-partwise>
"""


def render_midi(bundle: ArtifactBundle, *, note_events: list[dict[str, Any]] | None = None) -> bytes:
    """Render a minimal standard MIDI file with one track."""

    notes = note_events if note_events is not None else bundle.arrangement.get("note_events", [])
    notes = sorted(notes, key=lambda item: float(item.get("start", 0.0)))
    tempo_bpm = float(bundle.arrangement.get("timebase", {}).get("tempo_bpm", 120.0))
    ticks_per_quarter = 480
    tempo_microseconds = int(60_000_000 / tempo_bpm)
    events = bytearray()
    events.extend(b"\x00\xff\x51\x03" + tempo_microseconds.to_bytes(3, "big"))
    last_tick = 0
    for note in notes:
        start_tick = max(0, round(float(note.get("start", 0.0)) * ticks_per_quarter))
        end_tick = max(start_tick + 1, round(float(note.get("end", 0.0)) * ticks_per_quarter))
        pitch = max(0, min(127, _midi_note_number(str(note.get("pitch_name", "C4")))))
        events.extend(_varlen(max(0, start_tick - last_tick)) + bytes([0x90, pitch, 80]))
        events.extend(_varlen(end_tick - start_tick) + bytes([0x80, pitch, 0]))
        last_tick = end_tick
    events.extend(b"\x00\xff\x2f\x00")
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter)
    track = b"MTrk" + struct.pack(">I", len(events)) + bytes(events)
    return header + track


def write_daw_bundle(bundle: ArtifactBundle, out_path: Path) -> Path:
    """Write a multi-track DAW-ready export bundle."""

    arrangement = bundle.arrangement
    strategy, tracks = _track_plan(arrangement)
    out_path.mkdir(parents=True, exist_ok=True)

    track_manifest: list[dict[str, Any]] = []
    for track in tracks:
        track_index = int(track.get("index", 1))
        track_id = f"track-{track_index:02d}"
        notes = track.get("notes", []) if isinstance(track.get("notes"), list) else []
        midi_name = f"{track_id}.mid"
        musicxml_name = f"{track_id}.musicxml"
        midi_path = out_path / midi_name
        musicxml_path = out_path / musicxml_name

        midi_path.write_bytes(render_midi(bundle, note_events=notes))
        musicxml_path.write_text(
            render_musicxml(
                bundle,
                note_events=notes,
                track_name=f"{str(track.get('name', DEFAULT_DAW_TRACK_NAME)).replace('_', ' ').title()}",
            ),
            encoding="utf-8",
        )
        track_manifest.append({
            "index": track_index,
            "name": str(track.get("name", DEFAULT_DAW_TRACK_NAME)),
            "strategy": str(track.get("strategy", "single")),
            "window": track.get("window"),
            "midi": midi_name,
            "musicxml": musicxml_name,
            "note_count": len(notes),
        })

    manifest = {
        "export_version": "1.0",
        "exported_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_input_uri": arrangement.get("source", {}).get("input_uri", "unknown"),
        "strategy": strategy,
        "track_count": len(track_manifest),
        "tracks": track_manifest,
    }
    (out_path / "daw_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    readme = """# DAW Import Bundle\n\n"""
    readme += "This bundle contains per-chunk Guitar tracks for import into GarageBand or Logic Pro.\n\n"
    readme += "## Files\n\n"
    readme += "- `daw_manifest.json`: track plan and source windows.\n"
    for track_entry in track_manifest:
        readme += f"- `{track_entry['midi']}` / `{track_entry['musicxml']}`: {track_entry['name']} ({track_entry['strategy']}).\n"
    readme += ("\nImport steps:\n"
               "1. Open one track in GarageBand/Logic as a new region.\n"
               "2. Set tempo to match source BPM in `arrangement.json`.\n"
               "3. Import all `.mid` files as separate tracks, or use `.musicxml` for part-level review.\n")
    (out_path / "DAW_IMPORT_README.md").write_text(readme, encoding="utf-8")
    return out_path


def write_export(artifact_dir: Path, export_format: str, out_path: Path | None = None) -> Path:
    """Write an export artifact and return the path written."""

    normalized = export_format.lower()
    if normalized not in {"musicxml", "midi", "daw"}:
        raise ValueError(f"Unsupported export format: {export_format}")
    bundle = load_artifact_bundle(artifact_dir)
    if normalized == "daw":
        destination = out_path or artifact_dir / "daw_bundle"
    else:
        destination = out_path or artifact_dir / ("score.musicxml" if normalized == "musicxml" else "score.mid")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if normalized == "musicxml":
        destination.write_text(render_musicxml(bundle), encoding="utf-8")
    elif normalized == "midi":
        destination.write_bytes(render_midi(bundle))
    else:
        destination = write_daw_bundle(bundle, destination)
    return destination
