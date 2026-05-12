from __future__ import annotations

from tests.support.contract_validators import assert_no_url_download_contract


def test_url_policy_stub_blocks_download_and_points_to_legal_local_audio(fixtures_dir, load_json):
    policy_result = load_json(fixtures_dir / "url_policy_stub_result.json")

    assert_no_url_download_contract(policy_result)
