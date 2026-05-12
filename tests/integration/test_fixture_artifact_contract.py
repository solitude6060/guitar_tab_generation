from __future__ import annotations

from tests.support.contract_validators import assert_arrangement_contract, assert_quality_report_contract


def test_arrangement_and_quality_report_warning_contract_stays_in_sync(fixtures_dir, load_json):
    arrangement = load_json(fixtures_dir / "arrangements" / "minimal_valid_arrangement.json")
    quality_report = load_json(fixtures_dir / "quality_reports" / "minimal_valid_quality_report.json")

    assert_arrangement_contract(arrangement)
    assert_quality_report_contract(quality_report, arrangement)
