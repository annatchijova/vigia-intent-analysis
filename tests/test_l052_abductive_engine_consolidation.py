"""Regression test for L-052 — AbductiveIntentEngine consolidation.

Four DIVERGENT full copies of the engine existed (distinct md5: different
hypothesis IDs, Daubert annotations, import styles), none invoked in
production except vigia/inference's via pipeline.py's defensive import.
Because several modules insert <repo>/vigia into sys.path, a bare
`import abductive_intent_engine` resolved to a DIFFERENT copy than the one
the pipeline imports — for a Daubert-grade deterministic engine, which copy
loads must not depend on import spelling.

The three non-canonical copies are now re-export shims; every spelling must
resolve to the same class object.
"""

import sys

import pytest

from vigia.inference.abductive_intent_engine import AbductiveIntentEngine as CANONICAL


@pytest.mark.parametrize("module_path", [
    "vigia.core.abductive_intent_engine",
    "vigia.abductive_intent_engine",
    "vigia.tools.abductive_intent_engine",
])
def test_all_spellings_resolve_to_canonical(module_path):
    import importlib

    mod = importlib.import_module(module_path)
    assert mod.AbductiveIntentEngine is CANONICAL, (
        f"{module_path} resolved to a different class object — a divergent "
        "copy is back (L-052 regression)"
    )
    # The full public surface must come from the canonical module too.
    for symbol in ("AbductiveHypothesis", "AbductiveResult",
                   "Artifact", "HYPOTHESIS_TEMPLATES"):
        assert hasattr(mod, symbol), f"{module_path} lost re-export {symbol}"


def test_bare_flat_import_resolves_to_canonical():
    # The <repo>/vigia sys.path insertions make the bare name importable;
    # before consolidation it silently loaded a divergent copy.
    import importlib

    import vigia.pipeline.pipeline  # noqa: F401 — establishes the sys.path state
    try:
        mod = importlib.import_module("abductive_intent_engine")
    except ImportError:
        pytest.skip("bare flat import not resolvable in this sys.path layout")
    assert mod.AbductiveIntentEngine is CANONICAL


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
