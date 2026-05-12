from __future__ import annotations

import pytest

from tests.support.contract_validators import ContractError, assert_arrangement_contract


def test_minimal_arrangement_fixture_matches_shared_schema(fixtures_dir, load_json):
    arrangement = load_json(fixtures_dir / "arrangements" / "minimal_valid_arrangement.json")

    assert_arrangement_contract(arrangement)


def test_low_confidence_note_without_warning_is_hard_fail(fixtures_dir, load_json):
    arrangement = load_json(fixtures_dir / "arrangements" / "low_confidence_missing_warning.json")

    with pytest.raises(ContractError, match="LOW_NOTE_CONFIDENCE"):
        assert_arrangement_contract(arrangement)


def test_unplayable_position_outside_supported_fret_range_is_hard_fail(fixtures_dir, load_json):
    arrangement = load_json(fixtures_dir / "arrangements" / "unplayable_position.json")

    with pytest.raises(ContractError, match="fret must be 0-20"):
        assert_arrangement_contract(arrangement)
