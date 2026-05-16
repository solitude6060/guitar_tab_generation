# torchcrepe F0 Calibration

## Purpose

`f0-calibrate` is the P20 Torch-first minimal integration. It does not produce note events and does not replace Basic Pitch. It reads existing artifact note events and maps torchcrepe F0 frames onto solo/riff note confidence calibration.

## Safe defaults

- Default device is `cpu`.
- GPU is never used unless explicitly requested.
- The command does not auto-download models or install PyTorch / torchcrepe.
- Missing torchcrepe fails clearly; it never falls back to fake data.

## Usage

Create an artifact first:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation transcribe fixtures/simple_chords_30_90s.wav --backend basic-pitch --out /tmp/guitar-tab-basic-pitch
```

Run F0 calibration:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate /tmp/guitar-tab-basic-pitch
```

Output:

```text
/tmp/guitar-tab-basic-pitch/f0_calibration.json
```

GPU must be explicit:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run guitar-tab-generation f0-calibrate /tmp/guitar-tab-basic-pitch --device cuda:0
```

## Output contract

`f0_calibration.json` includes:

- `backend: torchcrepe-f0`
- `device`
- `sample_rate`
- `hop_length`
- `model`
- `note_calibrations[]`

Each note calibration includes:

- `note_id`
- `expected_midi`
- `observed_midi`
- `delta_semitones`
- `periodicity_confidence`
- `frame_count`
- `status`

## Dependency policy

P20 establishes the optional runtime boundary only. Because `torchcrepe` brings PyTorch heavy dependencies, this phase does not auto-install it into the default dev flow.
