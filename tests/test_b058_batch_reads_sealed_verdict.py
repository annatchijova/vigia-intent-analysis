"""
B-058 (Grupo B / B10) — the batch comparator must read the SEALED
`agent_verdict`, not re-derive the verdict from `best_hypothesis`.

AUDITORIA_INVARIANTES_ASIMETRIAS_20260703 §B-058 documented the fix for
`ABSTAIN_DETECTED` classifying NOISE, and left one recommendation unapplied:

  > el comparador de run_all_agent.py debería leer agent_verdict sellado, no
  > re-derivar el veredicto de best_hypothesis — así el batch nunca podría
  > enmascarar una divergencia del clasificador.

`vigia_agent.py::_seal_bundle` writes a top-level `agent_verdict` computed by
`classify_agent_verdict` — the SAME single path that decides the process exit
code. That is the authoritative verdict. The old
`extract_verdict_from_bundle` instead re-derived from
`pipeline_results.abduction.best_hypothesis`, which can DIVERGE from what was
sealed (e.g. `SUSPICION_DETECTED` -> best_hypothesis path says "SUSPICION"
while the sealed 4-value verdict is "INTENT", since the agent scale has no
SUSPICION rung).

Fix:
  1. `extract_verdict_from_bundle` reads the sealed `agent_verdict` first,
     falling back to the legacy best_hypothesis derivation only for older
     bundles that predate the field.
  2. The comparison doctrine (`verdict_matches`) treats the agent's INTENT
     tier as covering an expected SUSPICION label — the agent's 4-value scale
     {MALICE, INTENT, ABSTAIN, NOISE} has no SUSPICION rung, and its INTENT
     tier represents "INTENT/SUSPICION" (documented in B-073, Fase 2 §4).

Red-first: `verdict_matches` did not exist before this change (the doctrine
lived inline in `main()`), so the import failed.

Measured over the 198 sealed corpus bundles: 0 regressions, +3 cases
recovered (INTENT-labeled cases the agent sealed as INTENT but the old path
under-reported as SUSPICION -> FAIL).
"""
from __future__ import annotations

import json

import run_all_agent as R


def _write_bundle(tmp_path, name, *, agent_verdict=None, best_hypothesis=None):
    d = {
        "case_id": name,
        "pipeline_results": {"abduction": {}},
    }
    if agent_verdict is not None:
        d["agent_verdict"] = agent_verdict
    if best_hypothesis is not None:
        d["pipeline_results"]["abduction"]["best_hypothesis"] = best_hypothesis
    p = tmp_path / f"{name}_agent_bundle.json"
    p.write_text(json.dumps(d))
    return p


# ── extract_verdict_from_bundle: sealed verdict wins ────────────────────────

def test_prefers_sealed_agent_verdict_over_best_hypothesis(tmp_path):
    """The bug: best_hypothesis=SUSPICION_DETECTED re-derives to SUSPICION,
    but the sealed (and exit-deciding) verdict is INTENT. Read the sealed one."""
    b = _write_bundle(
        tmp_path, "DIVERGE",
        agent_verdict="INTENT",
        best_hypothesis="SUSPICION_DETECTED",
    )
    assert R.extract_verdict_from_bundle(b) == "INTENT"


def test_sealed_noise_is_not_masked(tmp_path):
    """A bundle sealed NOISE must report NOISE even if best_hypothesis text
    would have re-derived to something softer/different — no masking."""
    b = _write_bundle(
        tmp_path, "SEALED_NOISE",
        agent_verdict="NOISE",
        best_hypothesis="SUSPICION_DETECTED",
    )
    assert R.extract_verdict_from_bundle(b) == "NOISE"


def test_falls_back_to_best_hypothesis_without_sealed_field(tmp_path):
    """Older bundles predating the agent_verdict field keep the legacy path."""
    b = _write_bundle(
        tmp_path, "LEGACY",
        agent_verdict=None,
        best_hypothesis="MALICIOUS_INTENT_DETECTED",
    )
    assert R.extract_verdict_from_bundle(b) == "MALICE"


def test_empty_bundle_is_error(tmp_path):
    p = tmp_path / "BROKEN_agent_bundle.json"
    p.write_text("{ not json")
    assert R.extract_verdict_from_bundle(p) == "ERROR"


# ── verdict_matches: comparison doctrine ────────────────────────────────────

def test_exact_match():
    assert R.verdict_matches("MALICE", "MALICE")
    assert R.verdict_matches("NOISE", "NOISE")
    assert R.verdict_matches("ABSTAIN", "ABSTAIN")


def test_benign_aliases_to_noise():
    assert R.verdict_matches("BENIGN", "NOISE")
    assert R.verdict_matches("NOISE", "BENIGN")


def test_unknown_expected_always_passes():
    assert R.verdict_matches("UNKNOWN", "MALICE")
    assert R.verdict_matches("UNKNOWN", "ABSTAIN")


def test_over_severity_intent_label_accepts_malice():
    # MALICE ⊃ INTENT + concealment; over-severity, not a direction error.
    assert R.verdict_matches("INTENT", "MALICE")


def test_suspicion_label_accepts_sealed_intent():
    # The agent scale has no SUSPICION rung; its INTENT tier ⊇ SUSPICION.
    assert R.verdict_matches("SUSPICION", "INTENT")


def test_sub_severity_still_fails():
    # INTENT label, agent only reached (something softer) -> FAIL by design.
    assert not R.verdict_matches("INTENT", "SUSPICION")
    assert not R.verdict_matches("MALICE", "INTENT")
    assert not R.verdict_matches("MALICE", "NOISE")


def test_noise_label_rejects_intent():
    assert not R.verdict_matches("NOISE", "INTENT")
