# DAW Bundle Export (GarageBand / Logic Import)

## What it does

The current `export` command now supports:

- `musicxml` (single file)
- `midi` (single file)
- `daw` (bundle directory)

`--format daw` is optimized for GarageBand / Logic Pro workflows, especially when
full-song input uses chunked processing.

## Usage

```bash
uv run guitar-tab-generation export <artifact_dir> --format daw
```

Default output is `<artifact_dir>/daw_bundle`.

You can set a custom output folder:

```bash
uv run guitar-tab-generation export <artifact_dir> --format daw --out ./my-daw-bundle
```

## Output structure

- `track-01.mid` / `track-01.musicxml` (and track-02... for chunks)
- `daw_manifest.json` (track map, source windows)
- `DAW_IMPORT_README.md` (import steps)

## Clip vs full-song

- Clip (`duration_class=clip`) → one track.
- Full-song chunked plan (`duration_class=full_song`) → one track per processing chunk.

## Import checklist

1. Open GarageBand / Logic Pro.
2. Import each `.mid` as a new track.
3. Use `daw_manifest.json` as reference:
   - `strategy`
   - track index and names
   - source window (if chunked)
4. Set tempo to the source BPM from `arrangement.json` (`timebase.tempo_bpm`).

## Interface guidance

If you have already generated an artifact folder, open `interface.html` and use its **DAW Import** section directly:

1. Open `interface.html` in your browser.
2. Find the DAW section to see:
   - Whether `daw_bundle` exists.
   - The export strategy (`single_track` / `chunked_full_song`).
   - The link list for each `track-*.mid` and `track-*.musicxml`.
3. Click the track file links and import them into GarageBand / Logic Pro according to the same order.

This avoids reading commands again when you only need to continue from an existing artifact.
