"""CLI entry point for local-audio-first guitar TAB generation."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .ai_backends import collect_ai_backend_status, format_ai_backend_status_markdown
from .ai_runtime import build_resource_plan, collect_ai_runtime_status, format_runtime_status_markdown
from .audio_preprocess import AudioPreprocessError
from .artifact_viewer import ArtifactViewerError, write_artifact_viewer
from .artifact_interface import write_artifact_interface
from .backends import BackendExecutionError
from .exporters import write_export
from .input_adapter import InputError, PolicyGateError
from .model_smoke import available_backend_ids, build_model_smoke_plan, format_model_smoke_markdown
from .pipeline import transcribe_to_tab
from .practice_tutorial import write_practice_tutorial
from .torch_backends import (
    build_torch_backend_smoke_gate,
    collect_torch_backend_status,
    format_torch_backend_status_markdown,
    format_torch_smoke_gate_markdown,
)
from . import torchcrepe_f0


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
    interface = subparsers.add_parser("interface", help="Render an offline HTML interface from an artifact directory")
    interface.add_argument("artifact_dir", type=Path)
    interface.add_argument(
        "--out", type=Path, default=None, help="Output HTML path; defaults to <artifact_dir>/interface.html"
    )
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
            written = write_practice_tutorial(args.artifact_dir, args.out)
        except ArtifactViewerError as exc:
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
    parser.error("unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
