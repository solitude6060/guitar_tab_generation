"""Local AI runtime inspection and resource planning."""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
from typing import Callable, Any


CommandRunner = Callable[[list[str]], tuple[int, str, str]]


def _default_runner(command: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def _probe_torch() -> dict[str, Any]:
    try:
        import torch  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - depends on optional local install
        return {"available": False, "cuda_available": False, "error": str(exc)}
    return {
        "available": True,
        "version": getattr(torch, "__version__", "unknown"),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
    }


def collect_ai_runtime_status(run_command: CommandRunner = _default_runner) -> dict[str, Any]:
    """Collect local runtime status without requiring heavy AI dependencies."""

    nvidia_code, nvidia_out, nvidia_err = run_command([
        "nvidia-smi",
        "--query-gpu=name,memory.total",
        "--format=csv,noheader,nounits",
    ])
    gpu: dict[str, Any] = {"available": False, "name": None, "memory_mb": None, "error": nvidia_err or None}
    if nvidia_code == 0 and nvidia_out:
        first = nvidia_out.splitlines()[0]
        parts = [part.strip() for part in first.split(",", maxsplit=1)]
        gpu.update({"available": True, "name": parts[0], "error": None})
        if len(parts) > 1 and parts[1].isdigit():
            gpu["memory_mb"] = int(parts[1])

    ffmpeg_path = shutil.which("ffmpeg")
    ffmpeg_code, ffmpeg_out, ffmpeg_err = run_command(["ffmpeg", "-version"])
    ffmpeg_first_line = (ffmpeg_out or ffmpeg_err).splitlines()[0] if (ffmpeg_out or ffmpeg_err) else ""

    return {
        "python": {
            "executable": sys.executable,
            "version": platform.python_version(),
            "platform": platform.platform(),
        },
        "gpu": gpu,
        "ffmpeg": {
            "available": ffmpeg_code == 0,
            "path": ffmpeg_path,
            "version": ffmpeg_first_line,
        },
        "torch": _probe_torch(),
        "resource_profile": "local-rtx-4090-first",
        "secrets_policy": "Read provider tokens from environment variables only; never write tokens to repo.",
    }


def format_runtime_status_markdown(status: dict[str, Any]) -> str:
    """Format runtime status as Traditional Chinese Markdown."""

    gpu = status["gpu"]
    ffmpeg = status["ffmpeg"]
    torch = status["torch"]
    return "\n".join([
        "# AI Runtime Doctor",
        "",
        f"- Python: {status['python']['version']}",
        f"- Platform: {status['python']['platform']}",
        f"- GPU: {gpu['name'] or 'not detected'}",
        f"- VRAM: {gpu['memory_mb'] or 'unknown'} MB",
        f"- ffmpeg: {'available' if ffmpeg['available'] else 'missing'}",
        f"- PyTorch: {'available' if torch['available'] else 'missing'}",
        f"- CUDA: {'available' if torch.get('cuda_available') else 'missing'}",
        "",
    ])


def build_resource_plan() -> str:
    """Return the local-first AI resource plan with MiniMax as backup."""

    return """# 本機 4090 AI 資源規劃

## 原則

- 本機優先：RTX 4090 24GB VRAM 是主要推論環境。
- 離線優先：轉譜、分軌、和弦、教學、匯出都應先嘗試本機完成。
- 完整歌曲必備：3–8 分鐘（180–480 秒）音訊走 chunked local processing。
- MiniMax 是備援：只在本機模型不足、需要音樂生成/cover/lyrics 輔助時使用。
- 不要把 token 寫入 repo；MiniMax token 只允許從環境變數讀取。

## 本機模型路線

| 功能 | 首選資源 | 4090 負擔 |
|---|---|---|
| 音高轉譜 | Basic Pitch | 輕量，可本機跑 |
| 分軌 | Demucs / HTDemucs | 4090 可負擔，建議單獨跑 |
| 單音校準 | CREPE / torchcrepe | 4090 可負擔 |
| 節奏 / 特徵 | Essentia + librosa | CPU/GPU 都可 |
| 本機音訊 ingest | ffprobe + ffmpeg | CPU 為主，先轉成 normalized WAV |
| 教學文字 | 本機量化 LLM | 14B 穩，32B 視量化策略 |
| 匯出 | MusicXML / MIDI | 幾乎不吃 GPU |

## MiniMax 備援策略

| MiniMax 資源 | 用途 | 使用限制 |
|---|---|---|
| Text Generation | 教學文字、摘要、介面說明備援 | 不能改寫音符 source of truth |
| Music Generation v2.6 | 生成練習伴奏、示範 backing track | 不用於辨識原曲音符 |
| Lyrics Generation | 歌詞草稿或教學素材 | 不用於 copyrighted lyrics 擷取 |
| Music Cover | 風格 cover 實驗 | 必須確認權利與授權 |
| Image Understanding / Web Search | 文件或介面輔助 | 不得繞過本機 URL policy |

## 排程建議

1. 非 WAV 先用 ffprobe 讀長度，再用 ffmpeg 轉成 `audio_normalized.wav`。
2. 3–8 分鐘完整歌曲先切成 60 秒 chunk、2 秒 overlap，逐段分軌/轉譜。
3. Demucs 分軌單獨跑，避免和 32B LLM 搶 VRAM。
4. Basic Pitch / CREPE 跑完後釋放 GPU。
5. 本機 LLM 只讀 artifacts：`arrangement.json`、`quality_report.json`、`tab.md`。
6. MiniMax 只做備援與創作輔助，不當 transcription 真相來源。
"""


def runtime_status_json() -> str:
    return json.dumps(collect_ai_runtime_status(), ensure_ascii=False, indent=2) + "\n"
