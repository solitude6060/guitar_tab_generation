"""CLI entrypoint for the local-audio-first guitar TAB MVP scaffold."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .input_adapter import InputPolicyError, is_url, policy_gate_for_url, validate_local_audio
from .pipeline import load_fixture_metadata, run_placeholder_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="guitar-tab-generation")
    subcommands = parser.add_subparsers(dest="command", required=True)

    transcribe = subcommands.add_parser(
        "transcribe",
        help="Generate local-audio-first sketch TAB artifacts from a legal 30-90s audio clip.",
    )
    transcribe.add_argument("input", help="Local audio path. URLs are policy-gated and never downloaded.")
    transcribe.add_argument("--out", required=True, help="Output directory for tab.md, arrangement.json, quality_report.json.")
    transcribe.add_argument("--trim-start", type=float, default=None, help="Trim start in seconds.")
    transcribe.add_argument("--trim-end", type=float, default=None, help="Trim end in seconds.")
    transcribe.add_argument(
        "--rights-attestation",
        default="user_provided",
        help="Rights attestation recorded in arrangement.json source metadata.",
    )
    transcribe.add_argument(
        "--fixture-metadata",
        default=None,
        help="Optional JSON metadata with baseline note/chord/section expectations.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "transcribe":
        return _transcribe(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


def _transcribe(args: argparse.Namespace) -> int:
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if is_url(args.input):
        policy = policy_gate_for_url(args.input)
        policy["warning"] = {
            "code": "URL_POLICY_GATE",
            "severity": "error",
            "message": policy["message"],
        }
        policy["download_attempted"] = False
        (out_dir / "url_policy_gate.json").write_text(json.dumps(policy, indent=2) + "\n", encoding="utf-8")
        print(policy["message"], file=sys.stderr)
        return 2

    try:
        audio = validate_local_audio(
            args.input,
            trim_start=args.trim_start,
            trim_end=args.trim_end,
            rights_attestation=args.rights_attestation,
        )
        metadata = load_fixture_metadata(args.fixture_metadata)
        artifacts = run_placeholder_pipeline(audio, out_dir, fixture_metadata=metadata)
    except (InputPolicyError, FileNotFoundError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for name, path in artifacts.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
