"""MusicXML and MIDI export from existing transcription artifacts."""
from __future__ import annotations

from html import escape
from pathlib import Path
import struct
from typing import Any

from .artifact_viewer import ArtifactBundle, load_artifact_bundle


PITCH_CLASSES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


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


def render_musicxml(bundle: ArtifactBundle) -> str:
    """Render a minimal parseable MusicXML score."""

    arrangement = bundle.arrangement
    notes = arrangement.get("note_events", [])
    warnings = arrangement.get("warnings", [])
    confidence = arrangement.get("confidence", {}).get("overall", "unknown")
    source = arrangement.get("source", {}).get("input_uri", "unknown")
    note_xml: list[str] = []
    for note in notes:
        step, alter, octave = _parse_pitch(str(note.get("pitch_name", "C4")))
        duration = max(1, round((float(note.get("end", 0.0)) - float(note.get("start", 0.0))) * 4))
        alter_xml = f"<alter>{alter}</alter>" if alter else ""
        note_xml.append(
            f"<note><pitch><step>{escape(step)}</step>{alter_xml}<octave>{octave}</octave></pitch>"
            f"<duration>{duration}</duration><type>quarter</type>"
            f"<lyric><text>confidence {note.get('confidence', 'unknown')}</text></lyric></note>"
        )
    if not note_xml:
        note_xml.append("<note><rest/><duration>4</duration><type>whole</type></note>")

    warning_text = "; ".join(f"{w.get('code', 'UNKNOWN')}: {w.get('message', '')}" for w in warnings) or "None"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <work><work-title>Guitar TAB Export</work-title></work>
  <identification>
    <miscellaneous>
      <miscellaneous-field name="source">{escape(str(source))}</miscellaneous-field>
      <miscellaneous-field name="confidence">overall confidence {escape(str(confidence))}</miscellaneous-field>
      <miscellaneous-field name="warnings">{escape(warning_text)}</miscellaneous-field>
    </miscellaneous>
  </identification>
  <part-list><score-part id="P1"><part-name>Guitar</part-name></score-part></part-list>
  <part id="P1">
    <measure number="1">
      <attributes><divisions>4</divisions><key><fifths>0</fifths></key><time><beats>4</beats><beat-type>4</beat-type></time><clef><sign>G</sign><line>2</line></clef></attributes>
      {''.join(note_xml)}
    </measure>
  </part>
</score-partwise>
"""


def render_midi(bundle: ArtifactBundle) -> bytes:
    """Render a minimal standard MIDI file with one track."""

    notes = sorted(bundle.arrangement.get("note_events", []), key=lambda item: float(item.get("start", 0.0)))
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
        events.extend(_varlen(start_tick - last_tick) + bytes([0x90, pitch, 80]))
        events.extend(_varlen(end_tick - start_tick) + bytes([0x80, pitch, 0]))
        last_tick = end_tick
    events.extend(b"\x00\xff\x2f\x00")
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter)
    track = b"MTrk" + struct.pack(">I", len(events)) + bytes(events)
    return header + track


def write_export(artifact_dir: Path, export_format: str, out_path: Path | None = None) -> Path:
    """Write an export artifact and return the path written."""

    normalized = export_format.lower()
    if normalized not in {"musicxml", "midi"}:
        raise ValueError(f"Unsupported export format: {export_format}")
    bundle = load_artifact_bundle(artifact_dir)
    destination = out_path or artifact_dir / ("score.musicxml" if normalized == "musicxml" else "score.mid")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if normalized == "musicxml":
        destination.write_text(render_musicxml(bundle), encoding="utf-8")
    else:
        destination.write_bytes(render_midi(bundle))
    return destination
