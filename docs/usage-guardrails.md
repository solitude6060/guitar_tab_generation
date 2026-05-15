# Usage Guardrails

## Local audio is the only MVP success path

A run is in scope only when the input is a local audio file with a clear rights attestation:

- self-created audio,
- licensed/authorized audio, or
- public-domain audio with a recorded source statement.

Supported MVP suffixes are `.wav`, `.mp3`, `.flac`, and `.m4a`. Accepted effective durations are:

- 30–90 seconds for deterministic practice clips and golden fixtures.
- 3–8 minutes（180–480 seconds）for required full-song support.

Middle-length inputs between 90 and 180 seconds are intentionally rejected until a later product mode defines their UX. Longer source files must be trimmed explicitly into one of the supported windows.

Non-WAV local ingest requires local `ffprobe` for duration probing and local
`ffmpeg` for conversion into `audio_normalized.wav`. The project must fail with
an actionable local-tool error when those tools are missing; it must not fall
back to downloading, uploading, or cloud media parsing.

Use `uv run guitar-tab-generation ai-backends` to inspect selected local AI
backend availability. This command is diagnostic only: it must not install
packages, download models, run inference, or use cloud APIs.

## URL and YouTube policy gate

URL support is a future legal path, not an MVP feature. The MVP behavior is a stub/policy gate:

| Input | Expected behavior |
|---|---|
| `https://...` without a future legal gate | Block before download or parsing |
| YouTube URL | Block before download or parsing |
| Allowlist URL | Not implemented in MVP; defer to post-MVP ADR |
| Local file path | Continue through local-audio validation |

The policy response should include a stable reason code such as `URL_INPUT_DISABLED` or `URL_POLICY_GATE_DISABLED` and a next action: provide a legal local audio clip or legal local 3–8 minute full song.

## Output artifact contract

Every successful local-audio run must produce these artifacts:

- `arrangement.json` — shared machine-readable contract for timebase, source provenance, confidence, warnings, note/chord/section spans, fretboard, positions, and render hints.
- `tab.md` — human-readable sketch TAB with metadata, sections, chords, warnings, and at least one playable TAB part when the fixture requires riff/lead output.
- `quality_report.json` — quality gate summary, warnings, hard failures, and degraded status.

## Hard-fail and degradation rules

The run must fail or explicitly degrade when any of these occur:

1. TAB position has an invalid string/fret (`string` outside 1–6 or `fret` outside 0–20).
2. A low-confidence note/chord/section/fingering has no matching warning or quality-report entry.
3. Required golden fixture metadata or manual rubric record is missing.
4. URL policy gate is bypassed or any downloader/parser is invoked for arbitrary URL input.
5. Output is only raw MIDI/note data without readable sections, chords, TAB, and warnings.
6. `positions[].playability` is `unplayable` but is rendered as normal TAB.

Allowed `positions[].playability` values are:

- `playable` — can be rendered as normal TAB.
- `degraded` — render only with a warning or chord-only/text fallback.
- `unplayable` — hard fail unless removed from normal TAB output and reported clearly.

## Golden-fixture acceptance flow

Phase 0 must establish three legal fixtures before claiming e2e MVP success:

1. `simple_chords_30_90s`
2. `single_note_riff_30_90s`
3. `single_note_lead_30_90s`

Each fixture needs:

- rights/source statement,
- trim start/end or duration metadata,
- expected musical focus,
- manual rubric baseline,
- generated `tab.md`, `arrangement.json`, and `quality_report.json` from the current run.

Manual rubric scores use 1–5 for recognizability, chord usability, TAB playability, rhythm readability, and honesty. MVP pass threshold is average >= 3/5 for each core fixture with no hard failures.

## Contributor checklist

Before marking a change complete:

- [ ] The local-audio-first rule is preserved.
- [ ] URL behavior remains a no-download policy gate.
- [ ] `arrangement.json` fields remain backward-compatible with the PRD/test-spec required schema.
- [ ] Low-confidence values produce warnings.
- [ ] Unplayable TAB cannot be emitted as normal TAB.
- [ ] `tab.md`, `arrangement.json`, and `quality_report.json` warnings agree.
- [ ] `uv run pytest -q` passes, or any collection/runtime limitation is documented.
