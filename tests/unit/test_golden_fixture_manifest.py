from __future__ import annotations

from tests.support.contract_validators import assert_golden_manifest_contract


def test_manifest_declares_required_legal_golden_fixture_scaffold(fixtures_dir, load_json):
    manifest = load_json(fixtures_dir / "golden_manifest.json")

    assert_golden_manifest_contract(manifest, fixtures_dir)
