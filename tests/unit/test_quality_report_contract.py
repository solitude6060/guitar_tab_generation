from __future__ import annotations

from tests.support.contract_validators import assert_quality_report_contract


def test_quality_report_warning_codes_match_arrangement(fixtures_dir, load_json):
    arrangement = load_json(fixtures_dir / "arrangements" / "minimal_valid_arrangement.json")
    quality_report = load_json(fixtures_dir / "quality_reports" / "minimal_valid_quality_report.json")

    assert_quality_report_contract(quality_report, arrangement)
