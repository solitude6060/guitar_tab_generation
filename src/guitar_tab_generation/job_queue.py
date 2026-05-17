"""Local artifact-first job queue with GPU guard evidence."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Any


class JobQueueError(RuntimeError):
    """Raised when a queue operation cannot be completed."""


GpuProbe = Callable[[], tuple[int | None, int | None, str | None]]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _queue_dir(workspace_dir: Path) -> Path:
    return workspace_dir / ".gtg_jobs"


def _queue_path(workspace_dir: Path) -> Path:
    return _queue_dir(workspace_dir) / "queue.json"


def _logs_dir(workspace_dir: Path) -> Path:
    return _queue_dir(workspace_dir) / "logs"


def _lock_path(workspace_dir: Path) -> Path:
    return _queue_dir(workspace_dir) / "gpu.lock"


def _ensure_queue(workspace_dir: Path) -> None:
    _logs_dir(workspace_dir).mkdir(parents=True, exist_ok=True)
    path = _queue_path(workspace_dir)
    if not path.exists():
        path.write_text(json.dumps({"version": 1, "jobs": []}, indent=2) + "\n", encoding="utf-8")


def _load_queue(workspace_dir: Path) -> dict[str, Any]:
    _ensure_queue(workspace_dir)
    try:
        payload = json.loads(_queue_path(workspace_dir).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JobQueueError(f"Invalid queue file: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise JobQueueError("Invalid queue file: expected object with jobs list.")
    return payload


def _save_queue(workspace_dir: Path, payload: dict[str, Any]) -> None:
    _ensure_queue(workspace_dir)
    _queue_path(workspace_dir).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _append_log(workspace_dir: Path, job_id: str, message: str) -> None:
    _ensure_queue(workspace_dir)
    log_path = _logs_dir(workspace_dir) / f"{job_id}.log"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_now()} {message}\n")


def _find_job(payload: dict[str, Any], job_id: str) -> dict[str, Any]:
    for job in payload["jobs"]:
        if isinstance(job, dict) and job.get("job_id") == job_id:
            return job
    raise JobQueueError(f"Unknown job: {job_id}")


def _default_gpu_probe() -> tuple[int | None, int | None, str | None]:
    command = ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"]
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        return None, None, (result.stderr or "nvidia-smi failed").strip()
    line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 2:
        return None, None, "nvidia-smi returned an unexpected payload"
    try:
        return int(parts[0]), int(parts[1]), None
    except ValueError as exc:
        return None, None, f"nvidia-smi returned non-numeric VRAM: {exc}"


def read_queue(workspace_dir: Path) -> dict[str, Any]:
    """Return the current queue payload."""

    return _load_queue(workspace_dir)


def submit_job(
    workspace_dir: Path,
    *,
    command: Sequence[str],
    job_id: str | None = None,
    gpu_sensitive: bool = False,
    allow_gpu: bool = False,
) -> dict[str, Any]:
    """Submit a local job spec without executing the command."""

    if not command:
        raise JobQueueError("Job command must not be empty.")
    if gpu_sensitive and not allow_gpu:
        raise JobQueueError("GPU-sensitive job requires --allow-gpu at submit time.")
    payload = _load_queue(workspace_dir)
    resolved_job_id = job_id or f"job-{len(payload['jobs']) + 1:04d}"
    if any(job.get("job_id") == resolved_job_id for job in payload["jobs"] if isinstance(job, dict)):
        raise JobQueueError(f"Duplicate job id: {resolved_job_id}")
    now = _now()
    job = {
        "job_id": resolved_job_id,
        "status": "queued",
        "command": list(command),
        "gpu_sensitive": gpu_sensitive,
        "gpu_opt_in": allow_gpu,
        "created_at": now,
        "updated_at": now,
        "reason": None,
        "log_path": f".gtg_jobs/logs/{resolved_job_id}.log",
    }
    payload["jobs"].append(job)
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, resolved_job_id, f"submitted command={list(command)!r}")
    return job


def run_next_job(
    workspace_dir: Path,
    *,
    allow_gpu: bool = False,
    min_free_vram_mb: int = 12000,
    gpu_probe: GpuProbe | None = None,
) -> dict[str, Any] | None:
    """Run the next queued/deferred job through a simulated lifecycle."""

    payload = _load_queue(workspace_dir)
    job = next(
        (candidate for candidate in payload["jobs"] if candidate.get("status") in {"queued", "deferred"}),
        None,
    )
    if job is None:
        return None

    if job.get("gpu_sensitive"):
        if not allow_gpu:
            reason = "GPU-sensitive job requires --allow-gpu at run time."
            _defer_job(workspace_dir, payload, job, reason)
            return job
        lock_path = _lock_path(workspace_dir)
        if lock_path.exists():
            owner = lock_path.read_text(encoding="utf-8").strip() or "unknown"
            reason = f"GPU job already running: {owner}."
            _defer_job(workspace_dir, payload, job, reason)
            return job
        free_vram_mb, total_vram_mb, probe_error = (gpu_probe or _default_gpu_probe)()
        job["free_vram_mb"] = free_vram_mb
        job["total_vram_mb"] = total_vram_mb
        if probe_error:
            _defer_job(workspace_dir, payload, job, f"GPU probe unavailable: {probe_error}.")
            return job
        if free_vram_mb is None or free_vram_mb < min_free_vram_mb:
            _defer_job(
                workspace_dir,
                payload,
                job,
                f"Insufficient free VRAM: {free_vram_mb} MB available, {min_free_vram_mb} MB required.",
            )
            return job
        lock_path.write_text(f"{job['job_id']}\n", encoding="utf-8")

    job["status"] = "running"
    job["reason"] = None
    job["updated_at"] = _now()
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, job["job_id"], "running")

    job["status"] = "completed"
    job["updated_at"] = _now()
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, job["job_id"], "completed")
    if job.get("gpu_sensitive"):
        _lock_path(workspace_dir).unlink(missing_ok=True)
    return job


def _defer_job(workspace_dir: Path, payload: dict[str, Any], job: dict[str, Any], reason: str) -> None:
    job["status"] = "deferred"
    job["reason"] = reason
    job["updated_at"] = _now()
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, job["job_id"], f"deferred: {reason}")


def cancel_job(workspace_dir: Path, job_id: str) -> dict[str, Any]:
    """Cancel an existing job."""

    payload = _load_queue(workspace_dir)
    job = _find_job(payload, job_id)
    job["status"] = "canceled"
    job["reason"] = "Canceled by user."
    job["updated_at"] = _now()
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, job_id, "canceled")
    if _lock_path(workspace_dir).exists() and _lock_path(workspace_dir).read_text(encoding="utf-8").strip() == job_id:
        _lock_path(workspace_dir).unlink(missing_ok=True)
    return job


def resume_job(workspace_dir: Path, job_id: str) -> dict[str, Any]:
    """Resume a canceled or deferred job back to queued."""

    payload = _load_queue(workspace_dir)
    job = _find_job(payload, job_id)
    if job.get("status") not in {"canceled", "deferred"}:
        raise JobQueueError(f"Only canceled or deferred jobs can be resumed; current status is {job.get('status')}.")
    job["status"] = "queued"
    job["reason"] = None
    job["updated_at"] = _now()
    _save_queue(workspace_dir, payload)
    _append_log(workspace_dir, job_id, "resumed")
    return job
