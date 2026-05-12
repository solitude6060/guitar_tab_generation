# Execution-Ready Spec: AI Guitar Tab Generation Product

## Metadata
- Source workflow: deep-interview
- Profile: standard
- Context type: greenfield
- Final ambiguity: 0.18
- Threshold: 0.20
- Context snapshot: `.omx/context/guitar-tab-generation-product-20260512T121227Z.md`
- Transcript summary: see `.omx/interviews/`

## Clarity Breakdown
| Dimension | Score | Notes |
|---|---:|---|
| Intent | 0.90 | Primary job is automatic guitar transcription/tab generation. |
| Outcome | 0.85 | MVP output is complete, practice-usable guitar score/TAB. |
| Scope | 0.82 | DAW export and full tutorial are deferred; readable score is first. |
| Constraints | 0.75 | Approved MVP is local-audio-first; URL/YouTube remains future gated input; human-readable output; agent may choose models/platform. |
| Success | 0.80 | Practice usability beats note-perfect transcription. |

Weighted ambiguity: `0.18`.

## Intent
Build an AI-based project that combines audio recognition/transcription and AI generation to automatically create useful guitar tabs/scores from legally provided local audio, with YouTube/URL input reserved for a later gated legal flow.

## Desired Outcome
This interview artifact captured the product vision before the later PRD/test-spec
scope cut. The approved MVP scope is **local-audio-first**:

- MVP accepts uploaded/local audio files that the user legally owns, is
  authorized to use, or created.
- YouTube/URL input is a future product path only; in the MVP it must be a
  disabled/stub/policy-gated path that does not download or parse arbitrary
  videos.

and outputs a human-readable complete guitar score/TAB suitable for practice, including as many of these as feasible:
- chords / chord progression
- rhythm or strumming guidance
- riffs
- solo or lead melody when present
- AI-generated playable fingering
- section structure such as intro/verse/chorus/solo

## In Scope for MVP
- AI-assisted music/audio analysis.
- Guitar-focused transcription.
- Human-readable TAB/chord/section output.
- Practice-usable approximation of the song.
- Agent-selected model/package stack after research.
- Agent-selected MVP platform, such as CLI, notebook, local demo, or simple web UI, depending on fastest reliable validation path.

## Out of Scope / Non-goals for MVP
- GarageBand / Logic Pro multi-track export.
- Full multi-instrument DAW session generation.
- Complete interactive teaching course.
- Guaranteeing original guitarist’s exact fingering.
- Note-perfect transcription as the primary success criterion.

## Decision Boundaries
Agent may decide without further confirmation:
- which AI/audio/transcription/source-separation/chord-recognition/generation models or packages to evaluate/use;
- the MVP platform form factor.

Agent should not assume without explicit confirmation:
- paid cloud APIs, paid GPU usage, or significant recurring cost;
- expansion from readable score/TAB into DAW export;
- expansion into full teaching product;
- broad non-guitar instrument accuracy as an MVP requirement.

## Constraints
- Optimize for practice usability over exact reconstruction.
- Fingering may be AI-inferred as a playable arrangement.
- Input for the approved MVP is local audio. URL/YouTube handling is limited to
  an explicit policy gate/stub until a later legal flow is designed.
- First output should be readable by a guitarist, even if later versions add MusicXML/MIDI/Guitar Pro/DAW export.

## Testable Acceptance Criteria
1. Given a supported local audio file, the system produces a readable guitar-focused output.
2. Output includes chord/section information and at least one TAB-like playable guitar part when the source supports it.
3. Output explicitly marks uncertainty or approximation where exact transcription is unreliable.
4. A guitarist can use the result to practice a recognizable version of the song/segment.
5. MVP does not require DAW export, full tutorial generation, or arbitrary URL download to be considered complete.

## Assumptions Exposed + Resolutions
- Assumption: “Complete guitar score” must mean exact original performance. Resolution: no; practice-usable approximation is acceptable.
- Assumption: GarageBand/Logic Pro export is required in v1. Resolution: deferred.
- Assumption: Teaching is required in v1. Resolution: full tutorial deferred; lightweight guidance may be optional if cheap.
- Assumption: Fingering must match the original guitarist. Resolution: AI-inferred playable fingering is acceptable.

## Pressure-Pass Findings
The ambitious full-score goal was pressure-tested. MVP narrowed to a readable, practice-usable guitar transcription product with DAW export and full tutorial explicitly deferred.

## Recommended Next Step
Run `$ralplan` using this spec as the source of truth to validate architecture, feasibility, model/tool choices, legal/platform constraints, and test strategy before implementation.

Suggested invocation:
`$plan --consensus --direct .omx/specs/deep-interview-guitar-tab-generation-product.md`
