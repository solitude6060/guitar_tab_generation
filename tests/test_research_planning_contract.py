from __future__ import annotations

from pathlib import Path


def test_p5_research_report_defines_demo_tutorial_export_sequence() -> None:
    report = Path("docs/plans/p5-demo-tutorial-daw-research-report-20260513.md")

    assert report.exists()
    text = report.read_text(encoding="utf-8")
    for required in [
        "P6 Artifact Viewer Demo",
        "P7 Practice Tutorial Generator",
        "P8 MIDI/MusicXML Export",
        "不直接開大型功能",
        "不要一開始承諾完整 DAW session",
    ]:
        assert required in text


def test_demo_tutorial_daw_sequence_adr_exists() -> None:
    adr = Path("docs/adr/20260513-demo-tutorial-daw-sequencing.md")

    assert adr.exists()
    text = adr.read_text(encoding="utf-8")
    for required in ["Artifact viewer", "Practice tutorial", "MIDI/MusicXML", "GarageBand/Logic Pro"]:
        assert required in text
