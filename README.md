# Guitar Tab Generation MVP

繁體中文文件：[`README.zh-TW.md`](README.zh-TW.md)；使用規範：[`docs/usage-guardrails.zh-TW.md`](docs/usage-guardrails.zh-TW.md)。

Local-audio-first MVP for generating practice-usable guitar sketch TAB from legally provided 30–90 second audio clips.

## MVP scope

This project follows the approved planning artifacts:

- `.omx/plans/prd-guitar-tab-generation-mvp-20260512.md`
- `.omx/plans/test-spec-guitar-tab-generation-mvp-20260512.md`

The MVP is intentionally narrow:

- **Input:** local audio files that the user owns, is authorized to use, or created.
- **Duration:** 30–90 second clips, or an explicit trim range that produces a 30–90 second clip.
- **Output:** `tab.md`, `arrangement.json`, and `quality_report.json`.
- **Guitar scope:** standard tuning EADGBE, string 1–6, fret 0–20.
- **Non-goals:** arbitrary YouTube downloads, alternate tunings, required PDF export, DAW export, full teaching lessons, complete songs, and note-perfect/original-fingering guarantees.

## Input policy guardrail

The MVP must not download or parse arbitrary URLs. YouTube/URL input is a disabled policy-gated stub until a later legal flow is designed.

Expected URL behavior:

1. Detect `http://` and `https://` inputs before any media work.
2. Return an explicit refusal such as `URL_INPUT_DISABLED` or `URL_POLICY_GATE_DISABLED`.
3. Tell the user to provide a legal local audio file instead.
4. Do not create downloaded audio, temporary media files, or derived transcription artifacts from the URL.

## CLI usage

The core CLI is expected to expose a local `transcribe` flow. Use either the installed console script or the module form, depending on the environment:

```bash
guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --out out/simple_chords
python3 -m guitar_tab_generation.cli transcribe fixtures/simple_chords_30_90s.wav --out out/simple_chords
```

For a longer legal source file, pass an explicit trim that yields 30–90 seconds:

```bash
guitar-tab-generation transcribe path/to/legal_audio.wav --trim-start 30 --trim-end 90 --out out/clip
```

URL inputs should be used only to verify the policy gate:

```bash
guitar-tab-generation transcribe 'https://www.youtube.com/watch?v=example' --out out/url_stub
# Expected: blocked by URL policy gate; no download or parsed media artifact.
```

## Required output directory

A successful local-audio run should create:

```text
out/<clip>/
├── audio_normalized.wav
├── arrangement.json
├── quality_report.json
└── tab.md
```

Optional future outputs such as MusicXML, MIDI, or PDF may be added, but they are not MVP completion blockers.

## Verification

Run the available checks from the repository root:

```bash
python3 -m pytest
python3 -m compileall src tests
```

When fixture audio and CLI scaffold are present, also run the three golden flows:

```bash
guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --out out/simple_chords
guitar-tab-generation transcribe fixtures/single_note_riff_30_90s.wav --out out/riff
guitar-tab-generation transcribe fixtures/single_note_lead_30_90s.wav --out out/lead
```

See `docs/usage-guardrails.md` for the full usage and acceptance checklist.
