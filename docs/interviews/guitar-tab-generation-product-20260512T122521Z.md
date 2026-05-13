# Deep Interview Transcript Summary: AI Guitar Tab Generation Product

Metadata:
- Profile: standard
- Context type: greenfield
- Final ambiguity: 0.18
- Threshold: 0.20
- Context snapshot: .omx/context/guitar-tab-generation-product-20260512T121227Z.md

## Transcript

0. User seed: Wants an AI project using recognition + AI generation. Input music/YouTube URL, generate guitar tabs/chords/solo, later possibly DAW tracks for GarageBand/Logic Pro and teaching.
1. Core intent: selected `transcribe-tabs` — prioritize automatic transcription/tab generation.
2. First output target: selected `complete-guitar-score` — chords, rhythm/strumming, riffs, solo, fingering, section structure.
3. Boundary pressure / non-goals: selected `defer-daw-export`, `defer-full-tutorial`, `allow-inferred-fingering`.
4. Success criterion: selected `practice-usable` — useful for practicing and close enough to the song, not necessarily note-perfect.
5. Decision boundaries: selected `agent-chooses-models`, `agent-chooses-platform`.
6. Input/output boundary: selected `yt-or-audio-readable-tab` — YouTube URL or audio file input; human-readable score/TAB output.

## Pressure Pass Finding
The high-ambition “complete guitar score” target was challenged. The MVP was narrowed by deferring DAW export and full tutorial generation, and by accepting AI-inferred playable fingering rather than original-performance fingering.
