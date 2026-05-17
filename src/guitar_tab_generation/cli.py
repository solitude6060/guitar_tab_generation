"""CLI entry point for local-audio-first guitar TAB generation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import artifact_quality, chord_detection, evaluation_metrics, section_sidecar, stem_notes, stem_separation, torchcrepe_f0
from .ai_backends import collect_ai_backend_status, format_ai_backend_status_markdown
from .ai_runtime import build_resource_plan, collect_ai_runtime_status, format_runtime_status_markdown
from .audio_preprocess import AudioPreprocessError
from .artifact_viewer import ArtifactViewerError, write_artifact_viewer
from .artifact_interface import write_artifact_interface
from .backends import BackendExecutionError
from .demucs_runtime import build_demucs_runtime_gate, format_demucs_runtime_gate_markdown
from .exporters import write_export
from .input_adapter import InputError, PolicyGateError
from .job_queue import JobQueueError, cancel_job, read_queue, resume_job, run_next_job, submit_job
from .model_cache import ModelCacheError, build_cache_doctor, build_prune_plan, discover_model_caches
from .model_smoke import available_backend_ids, build_model_smoke_plan, format_model_smoke_markdown
from .pipeline import transcribe_to_tab
from .practice_tutorial import LocalLLMTutorialError, write_practice_tutorial
from .project_workspace import WorkspaceError, add_artifact_to_workspace, init_workspace, update_workspace_index
from .torch_backends import (
    build_torch_backend_smoke_gate,
    collect_torch_backend_status,
    format_torch_backend_status_markdown,
    format_torch_smoke_gate_markdown,
)
from .web_ui import write_web_ui


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guitar-tab-generation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    transcribe = subparsers.add_parser("transcribe", help="Generate sketch guitar TAB from legal local audio")
    transcribe.add_argument("input_uri")
    transcribe.add_argument("--out", required=True, type=Path)
    transcribe.add_argument("--trim-start", type=float, default=None)
    transcribe.add_argument("--trim-end", type=float, default=None)
    transcribe.add_argument(
        "--backend",
        default="fixture",
        help="Analysis backend to use; available: fixture, basic-pitch. Default is fixture.",
    )
    transcribe.add_argument(
        "--i-own-rights",
        action="store_true",
        help="Reserved for future gated URL support; arbitrary URL download remains disabled in MVP.",
    )
    view = subparsers.add_parser("view", help="Render a Markdown summary from an existing artifact directory")
    view.add_argument("artifact_dir", type=Path)
    view.add_argument("--out", type=Path, default=None, help="Output Markdown path; defaults to <artifact_dir>/viewer.md")
    tutorial = subparsers.add_parser("tutorial", help="Render a practice tutorial from an existing artifact directory")
    tutorial.add_argument("artifact_dir", type=Path)
    tutorial.add_argument(
        "--out", type=Path, default=None, help="Output Markdown path; defaults to <artifact_dir>/tutorial.md"
    )
    tutorial.add_argument(
        "--llm-backend",
        choices=["none", "fake", "local"],
        default="none",
        help="Optional LLM coaching backend; default is none. fake is deterministic for tests.",
    )
    interface = subparsers.add_parser("interface", help="Render an offline HTML interface from an artifact directory")
    interface.add_argument("artifact_dir", type=Path)
    interface.add_argument(
        "--out", type=Path, default=None, help="Output HTML path; defaults to <artifact_dir>/interface.html"
    )
    web_ui = subparsers.add_parser("web-ui", help="Render a static artifact browser for a workspace")
    web_ui.add_argument("workspace_dir", type=Path)
    web_ui.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output HTML path; defaults to <workspace_dir>/web-ui.html",
    )
    jobs = subparsers.add_parser("jobs", help="Manage local workspace jobs")
    job_subparsers = jobs.add_subparsers(dest="jobs_command", required=True)
    jobs_submit = job_subparsers.add_parser("submit", help="Submit a local job spec without executing it")
    jobs_submit.add_argument("workspace_dir", type=Path)
    jobs_submit.add_argument("--job-id", default=None)
    jobs_submit.add_argument(
        "--command",
        dest="job_command",
        action="append",
        required=True,
        help="Command token; repeat for each token",
    )
    jobs_submit.add_argument("--gpu", action="store_true", help="Mark the job as GPU-sensitive")
    jobs_submit.add_argument("--allow-gpu", action="store_true", help="Explicitly allow submitting a GPU-sensitive job")
    jobs_submit.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    jobs_status = job_subparsers.add_parser("status", help="Show workspace job queue status")
    jobs_status.add_argument("workspace_dir", type=Path)
    jobs_status.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    jobs_run_next = job_subparsers.add_parser("run-next", help="Run the next queued job through the local scheduler")
    jobs_run_next.add_argument("workspace_dir", type=Path)
    jobs_run_next.add_argument("--allow-gpu", action="store_true", help="Allow GPU probe and lock acquisition")
    jobs_run_next.add_argument("--min-free-vram-mb", type=int, default=12000)
    jobs_run_next.add_argument(
        "--fake-free-vram-mb",
        type=int,
        default=None,
        help="Test-only fake GPU free VRAM value; avoids probing real GPU",
    )
    jobs_run_next.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    jobs_cancel = job_subparsers.add_parser("cancel", help="Cancel a queued, deferred, or running job")
    jobs_cancel.add_argument("workspace_dir", type=Path)
    jobs_cancel.add_argument("job_id")
    jobs_cancel.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    jobs_resume = job_subparsers.add_parser("resume", help="Resume a canceled or deferred job")
    jobs_resume.add_argument("workspace_dir", type=Path)
    jobs_resume.add_argument("job_id")
    jobs_resume.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    models = subparsers.add_parser("models", help="Inspect local model caches")
    model_subparsers = models.add_subparsers(dest="models_command", required=True)
    models_list = model_subparsers.add_parser("list", help="List known model cache entries")
    models_list.add_argument("--cache-root", type=Path, default=None)
    models_list.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    models_doctor = model_subparsers.add_parser("doctor", help="Check model cache health")
    models_doctor.add_argument("--cache-root", type=Path, default=None)
    models_doctor.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    models_prune = model_subparsers.add_parser("prune", help="Plan safe model cache pruning")
    models_prune.add_argument("--cache-root", type=Path, default=None)
    models_prune.add_argument("--dry-run", action="store_true", help="Required; P37 does not delete cache files")
    models_prune.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    workspace = subparsers.add_parser("workspace", help="Manage project workspaces")
    workspace_subparsers = workspace.add_subparsers(dest="workspace_command", required=True)
    workspace_init = workspace_subparsers.add_parser("init", help="Initialize workspace.json")
    workspace_init.add_argument("workspace_dir", type=Path)
    workspace_init.add_argument("--name", default=None)
    workspace_init.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    workspace_index = workspace_subparsers.add_parser("index", help="Scan artifact directories into workspace.json")
    workspace_index.add_argument("workspace_dir", type=Path)
    workspace_index.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    workspace_add = workspace_subparsers.add_parser("add-artifact", help="Add one artifact directory to workspace.json")
    workspace_add.add_argument("workspace_dir", type=Path)
    workspace_add.add_argument("artifact_dir", type=Path)
    workspace_add.add_argument("--song-id", default=None)
    workspace_add.add_argument("--title", default=None)
    workspace_add.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    export = subparsers.add_parser("export", help="Export MusicXML / MIDI or DAW bundle from an artifact directory")
    export.add_argument("artifact_dir", type=Path)
    export.add_argument("--format", choices=["musicxml", "midi", "daw"], required=True)
    export.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path; defaults to score.musicxml, score.mid, or daw_bundle",
    )
    f0_calibrate = subparsers.add_parser(
        "f0-calibrate",
        help="Calibrate existing note events against torchcrepe F0 frames",
    )
    f0_calibrate.add_argument("artifact_dir", type=Path)
    f0_calibrate.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path; defaults to <artifact_dir>/f0_calibration.json",
    )
    f0_calibrate.add_argument("--device", default="cpu", help="torchcrepe device; default is cpu")
    f0_calibrate.add_argument("--model", choices=["tiny", "full"], default="tiny", help="torchcrepe model capacity")
    f0_calibrate.add_argument("--hop-ms", type=float, default=5.0, help="Frame hop in milliseconds")
    doctor_ai = subparsers.add_parser("doctor-ai", help="Inspect local AI runtime readiness")
    doctor_ai.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    subparsers.add_parser("ai-resources", help="Print the local 4090 AI resource plan with MiniMax backup policy")
    ai_backends = subparsers.add_parser("ai-backends", help="Inspect selected local AI backend/model availability")
    ai_backends.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    torch_backends = subparsers.add_parser("torch-backends", help="Inspect Torch-first backend roadmap and readiness")
    torch_backends.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    torch_smoke = subparsers.add_parser("torch-smoke", help="Plan or run safe Torch-first backend smoke gates")
    torch_smoke.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    torch_smoke.add_argument("--route", action="append", help="Torch route id to include; repeat to include multiple")
    torch_smoke.add_argument("--run", dest="run_smoke", action="store_true", help="Actually run smoke commands; default only plans")
    torch_smoke.add_argument("--allow-gpu", action="store_true", help="Allow GPU-sensitive smoke checks when VRAM guard passes")
    torch_smoke.add_argument("--min-free-vram-mb", type=int, default=None, help="Minimum free VRAM required for GPU-sensitive checks")
    torch_smoke.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cpu",
        help="torchcrepe runtime smoke device; cuda requires --allow-gpu or GPU_TESTS_ENABLED=1",
    )
    model_smoke = subparsers.add_parser("model-smoke", help="Plan or run safe opt-in local model download smoke checks")
    model_smoke.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    model_smoke.add_argument("--backend", action="append", choices=available_backend_ids(), help="Backend to include; repeat to include multiple")
    model_smoke.add_argument("--download", action="store_true", help="Actually run download commands; default only plans")
    model_smoke.add_argument("--allow-gpu", action="store_true", help="Allow GPU-sensitive smoke checks when VRAM guard passes")
    model_smoke.add_argument("--min-free-vram-mb", type=int, default=None, help="Minimum free VRAM required for GPU-sensitive checks")
    demucs_gate = subparsers.add_parser("demucs-gate", help="Plan and check Demucs optional runtime install gates")
    demucs_gate.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    demucs_gate.add_argument("--check-runtime", action="store_true", help="Verify optional Demucs runtime without running separation")
    demucs_gate.add_argument("--allow-gpu", action="store_true", help="Allow GPU gate probe when VRAM guard passes")
    demucs_gate.add_argument("--min-free-vram-mb", type=int, default=None, help="Minimum free VRAM required for Demucs GPU work")
    demucs_gate.add_argument("--model", default="htdemucs", help="Demucs model name for cache planning; default is htdemucs")
    separate_stems = subparsers.add_parser(
        "separate-stems",
        help="Run optional Demucs stem separation for an existing artifact directory",
    )
    separate_stems.add_argument("artifact_dir", type=Path)
    separate_stems.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output manifest path; defaults to <artifact_dir>/stem_manifest.json",
    )
    separate_stems.add_argument("--device", choices=["cpu", "cuda"], default="cpu", help="Demucs device; default is cpu")
    separate_stems.add_argument("--model", default="htdemucs", help="Demucs model name; default is htdemucs")
    separate_stems.add_argument("--allow-gpu", action="store_true", help="Allow GPU separation when VRAM guard passes")
    separate_stems.add_argument("--min-free-vram-mb", type=int, default=None, help="Minimum free VRAM required for GPU work")
    transcribe_stem = subparsers.add_parser(
        "transcribe-stem",
        help="Run Basic Pitch note transcription for a named stem sidecar",
    )
    transcribe_stem.add_argument("artifact_dir", type=Path)
    transcribe_stem.add_argument(
        "--backend",
        default="basic-pitch",
        choices=["basic-pitch"],
        help="Stem transcription backend; default is basic-pitch",
    )
    transcribe_stem.add_argument("--stem", required=True, help="Stem name from stem_manifest.json, e.g. guitar")
    quality_report = subparsers.add_parser(
        "quality-report",
        help="Refresh artifact-level quality_report.json from existing sidecars",
    )
    quality_report.add_argument("artifact_dir", type=Path)
    quality_report.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path; defaults to <artifact_dir>/quality_report.json",
    )
    chord_detect = subparsers.add_parser(
        "chord-detect",
        help="Generate a deterministic chords.json sidecar from an artifact directory",
    )
    chord_detect.add_argument("artifact_dir", type=Path)
    chord_detect.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path; defaults to <artifact_dir>/chords.json",
    )
    section_detect = subparsers.add_parser(
        "section-detect",
        help="Generate a deterministic sections.json sidecar from an artifact directory",
    )
    section_detect.add_argument("artifact_dir", type=Path)
    section_detect.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path; defaults to <artifact_dir>/sections.json",
    )
    eval_report = subparsers.add_parser(
        "eval-report",
        help="Generate evaluation metrics from fixture manifest and artifact outputs",
    )
    eval_report.add_argument("artifact_root", type=Path)
    eval_report.add_argument("--manifest", required=True, type=Path, help="Evaluation fixture manifest JSON")
    eval_report.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output JSON path; defaults to <artifact_root>/eval_report.json",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "transcribe":
        try:
            arrangement, quality_report = transcribe_to_tab(
                args.input_uri,
                args.out,
                trim_start=args.trim_start,
                trim_end=args.trim_end,
                backend=args.backend,
            )
        except PolicyGateError as exc:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "policy_gate.txt").write_text(str(exc) + "\n", encoding="utf-8")
            print(str(exc), file=sys.stderr)
            return 2
        except InputError as exc:
            print(f"Input error: {exc}", file=sys.stderr)
            return 1
        except AudioPreprocessError as exc:
            print(f"Audio preprocess error: {exc}", file=sys.stderr)
            return 1
        except BackendExecutionError as exc:
            print(f"Backend error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {args.out / 'tab.md'}")
        return 0 if quality_report["status"] == "passed" else 3
    if args.command == "view":
        try:
            written = write_artifact_viewer(args.artifact_dir, args.out)
        except ArtifactViewerError as exc:
            print(f"Artifact viewer error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "tutorial":
        try:
            written = write_practice_tutorial(args.artifact_dir, args.out, llm_backend=args.llm_backend)
        except (ArtifactViewerError, LocalLLMTutorialError) as exc:
            print(f"Practice tutorial error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "interface":
        try:
            written = write_artifact_interface(args.artifact_dir, args.out)
        except ArtifactViewerError as exc:
            print(f"Artifact interface error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "web-ui":
        written = write_web_ui(args.workspace_dir, args.out)
        print(f"Wrote {written}")
        return 0
    if args.command == "jobs":
        return _handle_jobs_command(args)
    if args.command == "models":
        return _handle_models_command(args)
    if args.command == "workspace":
        return _handle_workspace_command(args)
    if args.command == "export":
        try:
            written = write_export(args.artifact_dir, args.format, args.out)
        except (ArtifactViewerError, ValueError) as exc:
            print(f"Export error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "f0-calibrate":
        try:
            written = torchcrepe_f0.write_f0_calibration(
                args.artifact_dir,
                out=args.out,
                device=args.device,
                model=args.model,
                hop_ms=args.hop_ms,
            )
        except BackendExecutionError as exc:
            print(f"F0 calibration error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "doctor-ai":
        status = collect_ai_runtime_status()
        if args.json:
            import json

            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(format_runtime_status_markdown(status))
        return 0
    if args.command == "ai-resources":
        print(build_resource_plan())
        return 0
    if args.command == "ai-backends":
        status = collect_ai_backend_status()
        if args.json:
            import json

            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(format_ai_backend_status_markdown(status))
        return 0
    if args.command == "torch-backends":
        status = collect_torch_backend_status()
        if args.json:
            import json

            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(format_torch_backend_status_markdown(status))
        return 0
    if args.command == "torch-smoke":
        try:
            gate = build_torch_backend_smoke_gate(
                route_ids=args.route,
                run_smoke=args.run_smoke,
                allow_gpu=args.allow_gpu,
                min_free_vram_mb=args.min_free_vram_mb,
                torch_device=args.device,
            )
        except ValueError as exc:
            print(f"Torch smoke error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            import json

            print(json.dumps(gate, ensure_ascii=False, indent=2))
        else:
            print(format_torch_smoke_gate_markdown(gate))
        return 1 if gate["summary"]["failed"] else 0
    if args.command == "model-smoke":
        try:
            plan = build_model_smoke_plan(
                backends=args.backend,
                download=args.download,
                allow_gpu=args.allow_gpu,
                min_free_vram_mb=args.min_free_vram_mb,
            )
        except ValueError as exc:
            print(f"Model smoke error: {exc}", file=sys.stderr)
            return 1
        if args.json:
            import json

            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print(format_model_smoke_markdown(plan))
        return 1 if plan["summary"]["failed"] else 0
    if args.command == "demucs-gate":
        gate = build_demucs_runtime_gate(
            check_runtime=args.check_runtime,
            allow_gpu=args.allow_gpu,
            min_free_vram_mb=args.min_free_vram_mb,
            model_name=args.model,
        )
        if args.json:
            import json

            print(json.dumps(gate, ensure_ascii=False, indent=2))
        else:
            print(format_demucs_runtime_gate_markdown(gate))
        return 1 if gate["summary"]["failed"] else 0
    if args.command == "separate-stems":
        try:
            written = stem_separation.write_stem_separation(
                args.artifact_dir,
                out=args.out,
                device=args.device,
                model_name=args.model,
                allow_gpu=args.allow_gpu,
                min_free_vram_mb=args.min_free_vram_mb,
            )
        except BackendExecutionError as exc:
            print(f"Stem separation error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "transcribe-stem":
        try:
            written = stem_notes.write_basic_pitch_stem_notes(
                args.artifact_dir,
                stem_name=args.stem,
                backend=args.backend,
            )
        except BackendExecutionError as exc:
            print(f"Stem transcription error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "quality-report":
        try:
            written = artifact_quality.write_artifact_quality_report_v2(args.artifact_dir, out_path=args.out)
        except BackendExecutionError as exc:
            print(f"Quality report error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "chord-detect":
        try:
            written = chord_detection.write_chord_sidecar(args.artifact_dir, out_path=args.out)
        except chord_detection.ChordDetectionError as exc:
            print(f"Chord detection error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "section-detect":
        try:
            written = section_sidecar.write_section_sidecar(args.artifact_dir, out_path=args.out)
        except section_sidecar.SectionDetectionError as exc:
            print(f"Section detection error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0
    if args.command == "eval-report":
        try:
            written = evaluation_metrics.write_eval_report(args.artifact_root, args.manifest, out_path=args.out)
            report = evaluation_metrics.build_eval_report(args.artifact_root, args.manifest)
        except evaluation_metrics.EvaluationReportError as exc:
            print(f"Evaluation error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {written}")
        return 0 if report["summary"]["status"] == "passed" else 3
    parser.error("unknown command")
    return 1


def _print_json_or_summary(payload: dict, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False))


def _handle_jobs_command(args: argparse.Namespace) -> int:
    fake_probe = None
    if getattr(args, "fake_free_vram_mb", None) is not None:
        fake_probe = lambda: (args.fake_free_vram_mb, 24564, None)
    try:
        if args.jobs_command == "submit":
            payload = submit_job(
                args.workspace_dir,
                command=args.job_command,
                job_id=args.job_id,
                gpu_sensitive=args.gpu,
                allow_gpu=args.allow_gpu,
            )
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.jobs_command == "status":
            payload = read_queue(args.workspace_dir)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.jobs_command == "run-next":
            payload = run_next_job(
                args.workspace_dir,
                allow_gpu=args.allow_gpu,
                min_free_vram_mb=args.min_free_vram_mb,
                gpu_probe=fake_probe,
            ) or {"status": "empty", "reason": "No queued jobs."}
            _print_json_or_summary(payload, as_json=args.json)
            return 3 if payload.get("status") == "deferred" else 0
        if args.jobs_command == "cancel":
            payload = cancel_job(args.workspace_dir, args.job_id)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.jobs_command == "resume":
            payload = resume_job(args.workspace_dir, args.job_id)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
    except JobQueueError as exc:
        print(f"Job queue error: {exc}", file=sys.stderr)
        return 1
    raise JobQueueError(f"Unknown jobs command: {args.jobs_command}")


def _handle_models_command(args: argparse.Namespace) -> int:
    try:
        if args.models_command == "list":
            payload = discover_model_caches(args.cache_root)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.models_command == "doctor":
            payload = build_cache_doctor(args.cache_root, repo_root=Path.cwd())
            _print_json_or_summary(payload, as_json=args.json)
            return 0 if payload["status"] == "passed" else 3
        if args.models_command == "prune":
            payload = build_prune_plan(args.cache_root, dry_run=args.dry_run)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
    except ModelCacheError as exc:
        print(f"Model cache error: {exc}", file=sys.stderr)
        return 1
    raise ModelCacheError(f"Unknown models command: {args.models_command}")


def _handle_workspace_command(args: argparse.Namespace) -> int:
    try:
        if args.workspace_command == "init":
            payload = init_workspace(args.workspace_dir, name=args.name)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.workspace_command == "index":
            payload = update_workspace_index(args.workspace_dir)
            _print_json_or_summary(payload, as_json=args.json)
            return 0
        if args.workspace_command == "add-artifact":
            payload = add_artifact_to_workspace(
                args.workspace_dir,
                args.artifact_dir,
                song_id=args.song_id,
                title=args.title,
            )
            _print_json_or_summary(payload, as_json=args.json)
            return 0
    except WorkspaceError as exc:
        print(f"Workspace error: {exc}", file=sys.stderr)
        return 1
    raise WorkspaceError(f"Unknown workspace command: {args.workspace_command}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
