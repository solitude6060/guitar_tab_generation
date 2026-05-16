from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation import cli


class FakeTensor:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self

    def reshape(self, *_shape):
        return self

    def tolist(self) -> list[float]:
        return self.values


class FakeRuntime:
    def load_audio(self, audio_path: str):
        return object(), 16000

    def predict(self, audio, sample_rate, hop_length, fmin, fmax, model, *, batch_size, device, return_periodicity):
        return FakeTensor([261.63, 261.63]), FakeTensor([0.91, 0.89])


def _write_artifact(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "audio_normalized.wav").write_bytes(b"fake")
    (root / "notes.json").write_text(
        json.dumps([{"id": "n1", "start": 0.0, "end": 0.01, "pitch_midi": 60}]),
        encoding="utf-8",
    )


def test_cli_f0_calibrate_writes_artifact_with_stub_runtime(monkeypatch, tmp_path: Path, capsys) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    monkeypatch.setattr("guitar_tab_generation.torchcrepe_f0.load_torchcrepe_runtime", lambda: FakeRuntime())

    assert cli.main(["f0-calibrate", str(artifact_dir)]) == 0

    output = capsys.readouterr().out
    assert "f0_calibration.json" in output
    payload = json.loads((artifact_dir / "f0_calibration.json").read_text(encoding="utf-8"))
    assert payload["backend"] == "torchcrepe-f0"


def test_cli_f0_calibrate_returns_error_when_runtime_missing(monkeypatch, tmp_path: Path, capsys) -> None:
    artifact_dir = tmp_path / "artifact"
    _write_artifact(artifact_dir)

    def _missing_runtime():
        raise ImportError("missing")

    monkeypatch.setattr("guitar_tab_generation.torchcrepe_f0.load_torchcrepe_runtime", _missing_runtime)

    assert cli.main(["f0-calibrate", str(artifact_dir)]) == 1
    assert "torchcrepe optional runtime is not installed" in capsys.readouterr().err
