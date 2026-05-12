from __future__ import annotations

from pathlib import Path
import shutil
import wave

from .input_adapter import AudioInput

TARGET_SAMPLE_RATE = 44100
TARGET_CHANNELS = 1


def normalize_audio(audio: AudioInput, out_dir: str | Path) -> dict:
    """Create normalized audio artifact metadata.

    This MVP skeleton handles WAV fixtures directly without inventing an ffmpeg
    dependency. Non-WAV files are copied as a placeholder after input policy
    validation, with provenance preserved for later ffmpeg replacement.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    source = Path(audio.input_uri)
    target = out / "audio_normalized.wav"

    if source.suffix.lower() == ".wav":
        _copy_wav_trimmed_mono(source, target, audio.trim["start"], audio.trim["end"])
    else:
        shutil.copyfile(source, target)

    with wave.open(str(target), "rb") as handle:
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        duration = handle.getnframes() / float(sample_rate)

    return {
        "path": str(target),
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_seconds": duration,
        "trim": audio.trim,
        "provenance": {"stage": "audio_preprocess", "input": audio.input_type},
    }


def _copy_wav_trimmed_mono(source: Path, target: Path, start: float, end: float) -> None:
    with wave.open(str(source), "rb") as src:
        params = src.getparams()
        rate = src.getframerate()
        start_frame = int(start * rate)
        frame_count = int((end - start) * rate)
        src.setpos(start_frame)
        frames = src.readframes(frame_count)
        with wave.open(str(target), "wb") as dst:
            dst.setnchannels(params.nchannels)
            dst.setsampwidth(params.sampwidth)
            dst.setframerate(rate)
            dst.writeframes(frames)
