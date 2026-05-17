from __future__ import annotations

import json
from pathlib import Path

from guitar_tab_generation.evaluation_metrics import build_eval_report, write_eval_report


def _write_manifest(root: Path, *, include_rubric: bool = True) -> Path:
    manifest = {
        "fixtures": [
            {
                "id": "fixture-a",
                "source_statement": "Synthetic self-created fixture.",
                "rights_attestation": "self_created",
                "rubric_record": "rubric_records/fixture-a.json" if include_rubric else "rubric_records/missing.json",
                "expected_outputs": {
                    "arrangement_json": "out/fixture-a/arrangement.json",
                    "quality_report_json": "out/fixture-a/quality_report.json",
                },
            }
        ]
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    if include_rubric:
        rubric_dir = root / "rubric_records"
        rubric_dir.mkdir()
        (rubric_dir / "fixture-a.json").write_text(
            json.dumps(
                {
                    "fixture_id": "fixture-a",
                    "reviewer": "author",
                    "scores": {
                        "recognizability": 4,
                        "chord_usability": 4,
                        "tab_playability": 4,
                        "rhythm_readability": 3,
                        "honesty": 5,
                    },
                    "average_score": 4.0,
                    "hard_failures": [],
                }
            ),
            encoding="utf-8",
        )
    return manifest_path


def _write_artifacts(root: Path) -> None:
    artifact_dir = root / "out" / "fixture-a"
    artifact_dir.mkdir(parents=True)
    arrangement = {
        "confidence": {"overall": 0.8, "notes": 0.76, "chords": 0.78, "fingering": 0.82},
        "warnings": [],
        "note_events": [
            {"id": "n1", "confidence": 0.8},
            {"id": "n2", "confidence": 0.7},
        ],
        "chord_spans": [{"label": "G", "confidence": 0.78}],
        "section_spans": [{"label": "A", "confidence": 0.68}],
        "positions": [
            {"note_id": "n1", "playability": "playable"},
            {"note_id": "n2", "playability": "playable"},
        ],
    }
    (artifact_dir / "arrangement.json").write_text(json.dumps(arrangement), encoding="utf-8")
    (artifact_dir / "quality_report.json").write_text(json.dumps({"status": "passed", "hard_failures": []}), encoding="utf-8")


def test_build_eval_report_passes_with_fixture_artifacts(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    _write_artifacts(tmp_path)

    report = build_eval_report(tmp_path, manifest_path)

    assert report["schema"] == "guitar-tab-generation.eval-report.v1"
    assert report["summary"]["status"] == "passed"
    assert report["summary"]["fixture_count"] == 1
    assert report["summary"]["average_rubric_score"] == 4.0
    fixture = report["fixtures"][0]
    assert fixture["metrics"]["notes"]["count"] == 2
    assert fixture["metrics"]["chords"]["average_confidence"] == 0.78
    assert fixture["metrics"]["sections"]["count"] == 1
    assert fixture["metrics"]["playability"]["playable_rate"] == 1.0
    assert report["failures"] == []


def test_build_eval_report_fails_missing_rubric_record(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path, include_rubric=False)
    _write_artifacts(tmp_path)

    report = build_eval_report(tmp_path, manifest_path)

    assert report["summary"]["status"] == "failed"
    assert report["failures"][0]["code"] == "MISSING_RUBRIC_RECORD"


def test_build_eval_report_fails_missing_artifacts(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)

    report = build_eval_report(tmp_path, manifest_path)

    assert report["summary"]["status"] == "failed"
    assert {failure["code"] for failure in report["failures"]} == {"MISSING_ARTIFACT"}


def test_write_eval_report_defaults_to_artifact_root(tmp_path: Path) -> None:
    manifest_path = _write_manifest(tmp_path)
    _write_artifacts(tmp_path)

    written = write_eval_report(tmp_path, manifest_path)

    assert written == tmp_path / "eval_report.json"
    payload = json.loads(written.read_text(encoding="utf-8"))
    assert payload["summary"]["status"] == "passed"
