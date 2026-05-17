from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation import cli


def _write_stem_artifact(artifact_dir: Path) -> None:
    stems_dir = artifact_dir / "stems"
    stems_dir.mkdir(parents=True)
    (stems_dir / "guitar.wav").write_bytes(b"fake guitar wav")
    (artifact_dir / "stem_manifest.json").write_text(
        json.dumps(
            {
                "backend": "demucs-htdemucs",
                "model_name": "htdemucs",
                "stems": [{"name": "guitar", "path": "stems/guitar.wav"}],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_cli_transcribe_stem_help_lists_backend_and_stem(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["transcribe-stem", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "--backend" in output
    assert "--stem" in output


def test_cli_transcribe_stem_writes_stem_note_sidecar(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_stem_artifact(artifact_dir)

    def _predict(audio_path: str, *_args, **_kwargs):
        assert audio_path.endswith("stems/guitar.wav")
        return ({"raw": True}, object(), [(0.0, 0.5, 67, 0.9, [])])

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", lambda: _predict)

    assert cli.main(["transcribe-stem", str(artifact_dir), "--backend", "basic-pitch", "--stem", "guitar"]) == 0

    notes_path = artifact_dir / "stem_notes" / "guitar.notes.json"
    metadata_path = artifact_dir / "stem_notes" / "guitar.metadata.json"
    payload = json.loads(notes_path.read_text(encoding="utf-8"))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert payload["stem"] == "guitar"
    assert payload["notes"][0]["provenance"]["backend"] == "basic-pitch"
    assert payload["notes"][0]["provenance"]["stem"] == "guitar"
    assert metadata["source"]["stem_manifest"] == "stem_manifest.json"
    assert metadata["source"]["stem_path"] == "stems/guitar.wav"


def test_cli_transcribe_stem_missing_manifest_fails_without_mix_fallback(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_dir = tmp_path / "artifact"
    artifact_dir.mkdir()

    assert cli.main(["transcribe-stem", str(artifact_dir), "--backend", "basic-pitch", "--stem", "guitar"]) == 1

    assert "Run separate-stems first" in capsys.readouterr().err
    assert not (artifact_dir / "stem_notes").exists()


def test_cli_transcribe_help_still_has_no_stem_option(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["transcribe", "--help"])

    assert excinfo.value.code == 0
    output = capsys.readouterr().out
    assert "--stem" not in output


def test_cli_transcribe_stem_rejects_unsafe_name_before_runtime(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    artifact_dir = tmp_path / "artifact"
    stems_dir = artifact_dir / "stems"
    stems_dir.mkdir(parents=True)
    (stems_dir / "guitar.wav").write_bytes(b"fake guitar wav")
    (artifact_dir / "stem_manifest.json").write_text(
        json.dumps({"stems": [{"name": "../leak", "path": "stems/guitar.wav"}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    def _load_runtime():
        raise AssertionError("Basic Pitch runtime must not load for unsafe stem names")

    monkeypatch.setattr("guitar_tab_generation.basic_pitch_backend.load_basic_pitch_predict", _load_runtime)

    assert cli.main(["transcribe-stem", str(artifact_dir), "--backend", "basic-pitch", "--stem", "../leak"]) == 1

    assert "unsafe stem name" in capsys.readouterr().err
    assert not (artifact_dir / "leak.notes.json").exists()
    assert not (artifact_dir / "stem_notes").exists()
