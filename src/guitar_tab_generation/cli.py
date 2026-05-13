"""CLI entry point for local-audio-first guitar TAB generation."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .backends import BackendExecutionError
from .input_adapter import InputError, PolicyGateError, policy_gate_message
from .pipeline import transcribe_to_tab


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guitar-tab-generation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    transcribe = subparsers.add_parser("transcribe", help="Generate sketch guitar TAB from legal local audio")
    transcribe.add_argument("input_uri")
    transcribe.add_argument("--out", required=True, type=Path)
    transcribe.add_argument("--trim-start", type=float, default=None)
    transcribe.add_argument("--trim-end", type=float, default=None)
    transcribe.add_argument("--backend", default="fixture", help="Analysis backend to use; MVP default is fixture.")
    transcribe.add_argument(
        "--i-own-rights",
        action="store_true",
        help="Reserved for future gated URL support; arbitrary URL download remains disabled in MVP.",
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
        except BackendExecutionError as exc:
            print(f"Backend error: {exc}", file=sys.stderr)
            return 1
        print(f"Wrote {args.out / 'tab.md'}")
        return 0 if quality_report["status"] == "passed" else 3
    parser.error("unknown command")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
