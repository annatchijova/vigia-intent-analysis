"""B-197 — ``run_vigia`` must not silently discard malformed input signals."""

from __future__ import annotations

import pytest

from vigia.pipeline.pipeline import _signals_from_dicts, run_vigia


_VALID_SIGNAL = {
    "tool_name": "SDA",
    "value": 0.1,
    "z_score": 0.2,
    "confidence": 0.9,
    "metadata": {},
}
_MALFORMED_SIGNAL = {
    "z_score": 9.0,
    "confidence": 1.0,
    "metadata": {"source": "unparsed"},
}


def test_signal_boundary_rejects_mixed_valid_and_malformed_input():
    """A malformed artefact cannot vanish while a partial result is sealed."""
    with pytest.raises(ValueError, match=r"signals_data\[1\].*tool_name"):
        _signals_from_dicts([_VALID_SIGNAL, _MALFORMED_SIGNAL])


def test_run_vigia_does_not_decide_after_a_signal_was_rejected():
    with pytest.raises(ValueError, match=r"signals_data\[1\].*tool_name"):
        run_vigia([_VALID_SIGNAL, _MALFORMED_SIGNAL])
