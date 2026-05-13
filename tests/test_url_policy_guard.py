from __future__ import annotations

from pathlib import Path

from guitar_tab_generation.cli import main


def test_i_own_rights_does_not_enable_arbitrary_url_download(tmp_path: Path) -> None:
    out_dir = tmp_path / "url"

    exit_code = main([
        "transcribe",
        "https://www.youtube.com/watch?v=example",
        "--i-own-rights",
        "--out",
        str(out_dir),
    ])

    assert exit_code == 2
    assert (out_dir / "policy_gate.txt").exists()
    assert "local-audio-first" in (out_dir / "policy_gate.txt").read_text(encoding="utf-8")
    assert not any(
        (out_dir / artifact).exists()
        for artifact in [
            "audio_normalized.wav",
            "arrangement.json",
            "quality_report.json",
            "tab.md",
            "notes.json",
            "chords.json",
            "sections.json",
        ]
    )


def test_legal_url_policy_adr_records_future_gate_requirements() -> None:
    adr = Path("docs/adr/20260513-legal-url-input-policy.md")

    assert adr.exists()
    text = adr.read_text(encoding="utf-8")
    for required in [
        "arbitrary URL download remains disabled",
        "allowlist",
        "rights attestation",
        "audit log",
        "user-provided audio",
    ]:
        assert required in text
