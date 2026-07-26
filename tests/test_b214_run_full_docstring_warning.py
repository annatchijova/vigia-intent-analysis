"""
B-214: VigiaPipeline.run_full() does not run the normalization-integrity
gate that vigia_agent.py (Mode 1) applies before sealing -- confirmed with
two real cases (OWL-NEXUS5, VIGIA-OWL-2019-COMPLETE) where run_full sealed
REJECT/posterior=1.0 while vigia_agent.py on the same JSON sealed ABSTAIN
with reason NORMALIZATION_INTEGRITY_LOSS.

The bug's own text proposed two fixes: (a) run_full runs the same gate and
degrades to ABSTAIN on metadata coercion -- changes sealed verdicts for any
case with normalization_failures, needs an architecture decision + corpus
dry-run before touching; or (b) document run_full explicitly as "raw score,
no gates" so callers don't mistake it for the authoritative sealing path.

This applies (b): a docstring warning naming the exact gap, the two real
repro cases, and pointing callers who need Daubert-honest degradation at
vigia_agent.py instead. Zero behavioral change -- run_full's scoring logic
is untouched, only its documentation. This test locks in that the warning
survives future edits to the docstring (it's easy to trim a long docstring
during an unrelated refactor without noticing a warning goes with it).

Also fixes a stale formula in the same docstring: the [Gobernanza] step
described r = (1-P)*(...), the pre-B-117 inverted formula that produced
backwards verdicts (P0, fixed 2026-07-14). The live implementation
(risk_bounded_layer.py's compute_risk) has used r = P*(...) since that fix;
the docstring just never caught up.
"""

from __future__ import annotations

from vigia.pipeline.pipeline import VigiaPipeline


class TestRunFullDocstringWarnsAboutTheNormalizationGateGap:
    def test_docstring_names_b214_and_the_gap(self):
        doc = VigiaPipeline.run_full.__doc__
        assert doc is not None
        assert "B-214" in doc
        assert "gate de integridad de normalización" in doc
        assert "vigia_agent.py" in doc

    def test_docstring_points_callers_at_the_agent_for_sealing(self):
        doc = VigiaPipeline.run_full.__doc__
        assert "no llames a" in doc.lower() or "no llames" in doc

    def test_docstring_formula_is_not_the_pre_b117_inverted_form(self):
        doc = VigiaPipeline.run_full.__doc__
        assert "(1-P)·(1+λD)" not in doc
        assert "r = P·(1+λD)" in doc
