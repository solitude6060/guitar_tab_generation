from __future__ import annotations

import pytest

from guitar_tab_generation.input_adapter import PolicyGateError, resolve_local_audio


def test_url_input_is_blocked_without_download() -> None:
    with pytest.raises(PolicyGateError) as exc:
        resolve_local_audio("https://youtube.com/watch?v=dummy")
    assert "local-audio-first" in str(exc.value)
    assert "disabled" in str(exc.value)
