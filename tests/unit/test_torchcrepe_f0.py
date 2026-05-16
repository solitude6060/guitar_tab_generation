from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.backends import BackendExecutionError
from guitar_tab_generation.torchcrepe_f0 import TorchcrepeF0Calibrator, write_f0_calibration


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
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def load_audio(self, audio_path: str):
        self.calls.append({"audio_path": audio_path})
        return object(), 16000

    def predict(self, audio, sample_rate, hop_length, fmin, fmax, model, *, batch_size, device, return_periodicity):
        self.calls.append(
            {
                "sample_rate": sample_rate,
                "hop_length": hop_length,
                "fmin": fmin,
                "fmax": fmax,
                "model": model,
                "batch_size": batch_size,
                "device": device,
                "return_periodicity": return_periodicity,
            }
        )
        return FakeTensor([261.63, 261.63, 329.63, 329.63]), FakeTensor([0.91, 0.89, 0.82, 0.8])


def test_torchcrepe_calibrator_requires_runtime(tmp_path: Path) -> None:
    calibrator = TorchcrepeF0Calibrator(runtime_loader=lambda: (_ for _ in ()).throw(ImportError("missing")))

    with pytest.raises(BackendExecutionError, match="torchcrepe optional runtime is not installed"):
        calibrator.calibrate(tmp_path / "audio.wav", [])


def test_torchcrepe_calibrator_maps_pitch_frames_to_notes(tmp_path: Path) -> None:
    runtime = FakeRuntime()
    calibrator = TorchcrepeF0Calibrator(runtime_loader=lambda: runtime)
    notes = [
        {"id": "n1", "start": 0.0, "end": 0.01, "pitch_midi": 60},
        {"id": "n2", "start": 0.01, "end": 0.02, "pitch_midi": 64},
    ]

    result = calibrator.calibrate(tmp_path / "audio.wav", notes, hop_ms=5.0)

    assert result["backend"] == "torchcrepe-f0"
    assert result["device"] == "cpu"
    assert result["sample_rate"] == 16000
    assert result["hop_length"] == 80
    assert len(result["note_calibrations"]) == 2
    first = result["note_calibrations"][0]
    assert first["note_id"] == "n1"
    assert first["expected_midi"] == 60
    assert abs(first["observed_midi"] - 60) < 0.05
    assert first["periodicity_confidence"] == pytest.approx(0.9)
    assert runtime.calls[1]["device"] == "cpu"
    assert runtime.calls[1]["return_periodicity"] is True


def test_torchcrepe_calibrator_uses_cpu_by_default(tmp_path: Path) -> None:
    runtime = FakeRuntime()
    calibrator = TorchcrepeF0Calibrator(runtime_loader=lambda: runtime)

    calibrator.calibrate(tmp_path / "audio.wav", [{"id": "n1", "start": 0.0, "end": 0.01, "pitch_midi": 60}])

    assert runtime.calls[1]["device"] == "cpu"


def test_write_f0_calibration_requires_artifact_files(tmp_path: Path) -> None:
    with pytest.raises(BackendExecutionError, match="audio_normalized.wav"):
        write_f0_calibration(tmp_path, runtime_loader=lambda: FakeRuntime())

    (tmp_path / "audio_normalized.wav").write_bytes(b"fake")
    with pytest.raises(BackendExecutionError, match="notes.json"):
        write_f0_calibration(tmp_path, runtime_loader=lambda: FakeRuntime())


def test_write_f0_calibration_writes_json(tmp_path: Path) -> None:
    (tmp_path / "audio_normalized.wav").write_bytes(b"fake")
    (tmp_path / "notes.json").write_text(json.dumps([{"id": "n1", "start": 0.0, "end": 0.01, "pitch_midi": 60}]), encoding="utf-8")

    written = write_f0_calibration(tmp_path, runtime_loader=lambda: FakeRuntime())

    payload = json.loads(written.read_text(encoding="utf-8"))
    assert written.name == "f0_calibration.json"
    assert payload["backend"] == "torchcrepe-f0"
    assert payload["note_calibrations"][0]["note_id"] == "n1"
