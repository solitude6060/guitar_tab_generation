from __future__ import annotations

import json
from pathlib import Path

import pytest

from guitar_tab_generation.job_queue import JobQueueError, cancel_job, resume_job, run_next_job, submit_job


def _queue_payload(workspace: Path) -> dict:
    return json.loads((workspace / ".gtg_jobs" / "queue.json").read_text(encoding="utf-8"))


def test_submit_job_writes_queue_record_and_log(tmp_path: Path) -> None:
    job = submit_job(tmp_path, job_id="demo", command=["transcribe", "song.wav"])

    assert job["job_id"] == "demo"
    assert job["status"] == "queued"
    assert _queue_payload(tmp_path)["jobs"][0]["command"] == ["transcribe", "song.wav"]
    assert "submitted" in (tmp_path / ".gtg_jobs" / "logs" / "demo.log").read_text(encoding="utf-8")


def test_run_next_job_uses_queue_order(tmp_path: Path) -> None:
    submit_job(tmp_path, job_id="first", command=["view", "a"])
    submit_job(tmp_path, job_id="second", command=["view", "b"])

    result = run_next_job(tmp_path)

    jobs = _queue_payload(tmp_path)["jobs"]
    assert result["job_id"] == "first"
    assert jobs[0]["status"] == "completed"
    assert jobs[1]["status"] == "queued"


def test_gpu_submit_requires_explicit_opt_in(tmp_path: Path) -> None:
    with pytest.raises(JobQueueError, match="requires --allow-gpu"):
        submit_job(tmp_path, job_id="gpu", command=["separate-stems"], gpu_sensitive=True, allow_gpu=False)


def test_run_next_defers_gpu_job_when_lock_exists(tmp_path: Path) -> None:
    submit_job(tmp_path, job_id="gpu", command=["separate-stems"], gpu_sensitive=True, allow_gpu=True)
    (tmp_path / ".gtg_jobs" / "gpu.lock").write_text("other-job\n", encoding="utf-8")

    result = run_next_job(tmp_path, allow_gpu=True, gpu_probe=lambda: (24000, 24564, None))

    assert result["status"] == "deferred"
    assert "already running" in result["reason"]
    assert "already running" in (tmp_path / ".gtg_jobs" / "logs" / "gpu.log").read_text(encoding="utf-8")


def test_run_next_defers_gpu_job_when_vram_is_too_low(tmp_path: Path) -> None:
    submit_job(tmp_path, job_id="gpu", command=["separate-stems"], gpu_sensitive=True, allow_gpu=True)

    result = run_next_job(tmp_path, allow_gpu=True, min_free_vram_mb=12000, gpu_probe=lambda: (8000, 24564, None))

    assert result["status"] == "deferred"
    assert "free VRAM" in result["reason"]


def test_cancel_and_resume_job_update_state_and_logs(tmp_path: Path) -> None:
    submit_job(tmp_path, job_id="demo", command=["tutorial", "song"])

    canceled = cancel_job(tmp_path, "demo")
    resumed = resume_job(tmp_path, "demo")

    assert canceled["status"] == "canceled"
    assert resumed["status"] == "queued"
    log = (tmp_path / ".gtg_jobs" / "logs" / "demo.log").read_text(encoding="utf-8")
    assert "canceled" in log
    assert "resumed" in log
