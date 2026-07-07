#!/usr/bin/env python3
"""
Red-Team Round 2 — Monotonicity Invariants (property-based)
===========================================================
Method: Abductive Engineering (A-D-I) + Red-Team Auditing (epistemic ladder).
Scope : vigia_scorer._vigia_score — deterministic core. READ-ONLY audit,
        no source code touched.

Two invariants under test:

  INV-1  Positive monotonicity: adding an INCRIMINATING artifact must never
         LOWER final_score.  Matrix: raw_score(z) x prior_trust.
  INV-2  No dilution: adding FORENSICALLY IRRELEVANT evidence (raw_score~=0:
         README.txt / photo / manual.pdf) must never CHANGE the verdict.
         Special watch: gate B-068 counts n_artifacts / n_unique_types.

Run:
    cd <repo root>
    PYTHONPATH=$(pwd) python3 scratchpad/redteam_round2_monotonicity.py

Prints, for every experiment, the PREDICTION (stated before the result) and
the observed before/after so a reviewer can reproduce and check the claim.
"""
from __future__ import annotations

import itertools
import sys

from vigia_scorer import _vigia_score


# ---------------------------------------------------------------------------
# Helpers — build artifacts on the canonical schema the scorer consumes.
# provenance_chain has len 1  -> epc_k = max(0, 1-3) = 0 -> epc_factor = 1.0
# chain_status not BROKEN, chain non-empty  -> no provenance collapse.
# effective_trust = prior_trust * 1.0 * 1.0  (no temporal violations).
# ---------------------------------------------------------------------------
def art(i, etype, raw=0.85, prior=0.85, semantic="incriminatory"):
    return {
        "artifact_id": f"A{i}",
        "evidence_type": etype,
        "raw_score": raw,
        "prior_trust": prior,
        "semantic_role": semantic,
        "source_tool": f"tool_{i}",
        "description": f"artifact {i} ({etype})",
        "timestamp": f"2026-01-{(i % 27) + 1:02d}T10:00:00Z",
        "provenance_chain": ["acquire"],
        "metadata": {},
    }


def score(arts):
    r = _vigia_score({"case_id": "RT2", "artifacts": arts})
    return r


def line(s=""):
    print(s)


def hr(title):
    line()
    line("=" * 78)
    line(title)
    line("=" * 78)


# ===========================================================================
# INVARIANT 1 — POSITIVE MONOTONICITY
# ===========================================================================
def inv1_matrix_newtype():
    """
    Experiment 1A (discriminates H1 vs H2/H3).
    Baseline: 1 strong device artifact. Add ONE incriminating artifact of a
    DIFFERENT evidence_type, sweeping the z_score(raw) x prior_trust matrix.

    PREDICTION (H1, null): score never decreases -> 0 violations.
    A new type triggers no source_penalty; only diversity/composite gains.
    """
    hr("INV-1  Exp 1A  —  add NEW-type incriminating artifact  (matrix)")
    line("PREDICTION: 0 violations (new type => no correlation penalty).")
    base_arts = [art(0, "file_hash", raw=0.6, prior=0.85)]
    base = score(base_arts)["score"]
    z_grid = [0, 1, 2, 3, 4, 5]          # z-score bucket -> raw = z/5
    trust_grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    violations = 0
    worst = None
    for z, pt in itertools.product(z_grid, trust_grid):
        raw = min(1.0, z / 5.0)
        arts = base_arts + [art(1, "memory_process", raw=raw, prior=pt)]
        s = score(arts)["score"]
        if s < base - 1e-9:
            violations += 1
            d = s - base
            if worst is None or d < worst[0]:
                worst = (d, z, pt, base, s)
    line(f"baseline score (1 file_hash raw=0.6): {base}")
    line(f"violations across {len(z_grid)*len(trust_grid)} cells: {violations}")
    if worst:
        line(f"worst: z={worst[1]} prior={worst[2]}  {worst[3]} -> {worst[4]}  (d={worst[0]:.4f})")
    line("RESULT: " + ("HOLDS (as predicted)" if violations == 0 else "VIOLATED"))
    return violations


def inv1_matrix_sametype():
    """
    Experiment 1B (discriminates H2: correlation-decay source_penalty).
    Baseline: 3 STRONG same-type device artifacts. Add ONE incriminating
    artifact of the SAME evidence_type, sweeping raw(z) x prior_trust.

    Mechanism under test (vigia_scorer.py L714-727): source_penalty =
    min(0.5,(count-1)*0.15) is applied to EVERY artifact of that type. Raising
    count from 3->4 lifts the penalty 0.30->0.45 on the incumbents. If the
    added artifact is weaker than the incumbents, the penalty hike on the
    strong evidence can outweigh the new contribution -> score DROPS.

    PREDICTION (H2): violations appear, concentrated at LOW z / LOW prior
    (weak additions), disappearing as the added artifact gets as strong as the
    incumbents.
    """
    hr("INV-1  Exp 1B  —  add SAME-type incriminating artifact  (matrix)")
    line("PREDICTION (H2): score DROPS for weak same-type additions "
         "(low z / low prior).")
    ETYPE = "cryptographic_hash"   # high weight (0.45), low spoof (0.05): max adj
    base_arts = [art(i, ETYPE, raw=1.0, prior=1.0) for i in range(3)]
    base = score(base_arts)["score"]
    z_grid = [0, 1, 2, 3, 4, 5]
    trust_grid = [0.0, 0.25, 0.5, 0.75, 1.0]
    violations = 0
    worst = None
    grid = []
    for z in z_grid:
        row = []
        for pt in trust_grid:
            raw = min(1.0, z / 5.0)
            arts = base_arts + [art(99, ETYPE, raw=raw, prior=pt)]
            s = score(arts)["score"]
            drop = s < base - 1e-9
            row.append("DOWN" if drop else " up ")
            if drop:
                violations += 1
                d = s - base
                if worst is None or d < worst[0]:
                    worst = (d, z, pt, base, s)
        grid.append((z, row))
    line(f"baseline score (3x {ETYPE} raw=1.0 prior=1.0): {base}")
    line("matrix cell = sign of (after - before);  rows=z_score, cols=prior_trust")
    line("        prior=" + " ".join(f"{t:>4}" for t in trust_grid))
    for z, row in grid:
        line(f"  z={z}   " + "  ".join(row))
    line(f"violations: {violations} / {len(z_grid)*len(trust_grid)}")
    if worst:
        line(f"worst: z={worst[1]} prior={worst[2]}  score {worst[3]} -> {worst[4]}  (delta={worst[0]:.4f})")
    line("RESULT: " + ("HOLDS" if violations == 0 else "VIOLATED (H2 corroborated)"))
    return violations, worst


def inv1_crisp():
    """
    Experiment 1C — crispest single counterexample for INV-1.
    3 strong cryptographic_hash artifacts, then add ONE more incriminating
    (non-zero raw) artifact of the SAME type but WEAKER. Full before/after.
    """
    hr("INV-1  Exp 1C  —  crisp counterexample (before/after)")
    ETYPE = "cryptographic_hash"
    before = [art(i, ETYPE, raw=1.0, prior=1.0) for i in range(3)]
    rb = score(before)
    added = art(3, ETYPE, raw=0.05, prior=0.85)   # incriminating but weak
    after = before + [added]
    ra = score(after)
    line("BEFORE: 3x cryptographic_hash, raw=1.0, prior=1.0")
    line(f"   verdict={rb['verdict']:9} score={rb['score']}  composite={rb['composite_base']}")
    line("ADD   : 1x cryptographic_hash, raw=0.05, prior=0.85  (incriminating, weak)")
    line(f"AFTER : verdict={ra['verdict']:9} score={ra['score']}  composite={ra['composite_base']}")
    d = ra["score"] - rb["score"]
    line(f"delta score = {d:.4f}   -> {'VIOLATION' if d < -1e-9 else 'no drop'}")
    return d


# ===========================================================================
# INVARIANT 2 — NO DILUTION
# ===========================================================================
def _irrelevant(i, etype):
    # README.txt / photo / manual.pdf equivalents: DEVICE-class, zero signal.
    return art(i, etype, raw=0.0, prior=0.85)


def inv2_gate_ntypes():
    """
    Experiment 2A (discriminates H2: B-068 gate n_unique_types path).
    Baseline sits just inside the MALICE band (final_score>0.33) but is capped
    to SUSPICION by B-068 because it has only 2 device evidence classes
    (n_arts=3, n_types=2). Add ONE irrelevant document of a NEW type with
    raw_score=0.

    Gate (vigia_scorer.py L924-936): counts DEVICE artifacts and unique types
    with NO reference to their raw_score. A zero-signal new-type document
    lifts n_types 2->3 => gate opens => MALICE.

    PREDICTION (H2): verdict flips SUSPICION -> MALICE from adding manual.pdf.
    """
    hr("INV-2  Exp 2A  —  irrelevant NEW-type doc crosses B-068 n_types gate")
    line("PREDICTION (H2): verdict flips SUSPICION -> MALICE (raw_score=0 doc).")
    before = [
        art(0, "malware_infrastructure", raw=0.95),
        art(1, "keylogger_capture", raw=0.95),
        art(2, "keylogger_capture", raw=0.95),
    ]
    rb = score(before)
    # manual.pdf -> evidence_type "document" (LEGACY profile, DEVICE role), raw 0
    after = before + [_irrelevant(3, "document")]
    ra = score(after)
    line("BEFORE: 3 device artifacts / 2 types (malware_infrastructure, keylogger_capture)")
    line(f"   verdict={rb['verdict']:9} score={rb['score']}  reason={rb['reason'][:70]}")
    line("ADD   : manual.pdf  (evidence_type='document', raw_score=0.0)  [IRRELEVANT]")
    line(f"AFTER : verdict={ra['verdict']:9} score={ra['score']}")
    flip = rb["verdict"] != ra["verdict"]
    line(f"verdict changed = {flip}   {rb['verdict']} -> {ra['verdict']}")
    line("RESULT: " + ("VIOLATED (H2 corroborated)" if flip else "HOLDS"))
    return flip, rb, ra


def inv2_gate_narts():
    """
    Experiment 2B (discriminates H2: B-068 gate n_artifacts>=4 path).
    Baseline: 3 device artifacts of a SINGLE type, score>0.33 -> SUSPICION
    (n_arts=3<4, n_types=1<3). Add ONE irrelevant artifact of the SAME type,
    raw_score=0. n_arts 3->4 opens the gate.

    NOTE: same-type addition also triggers source_penalty (Exp 1B), which
    lowers the score. This experiment shows the two effects race: does the
    gate still open, or does the penalty push score below 0.33 first?

    PREDICTION: outcome is data-dependent; report whichever wins.
    """
    hr("INV-2  Exp 2B  —  irrelevant SAME-type artifact vs B-068 n_arts gate")
    line("PREDICTION: n_arts 3->4 opens gate UNLESS source_penalty sinks score<0.33.")
    ETYPE = "malware_infrastructure"
    before = [art(i, ETYPE, raw=0.97) for i in range(3)]
    rb = score(before)
    after = before + [_irrelevant(3, ETYPE)]
    ra = score(after)
    line(f"BEFORE: 3x {ETYPE} raw=0.97 (1 type)")
    line(f"   verdict={rb['verdict']:9} score={rb['score']}")
    line(f"ADD   : 1x {ETYPE} raw_score=0.0  [IRRELEVANT, same type]")
    line(f"AFTER : verdict={ra['verdict']:9} score={ra['score']}")
    flip = rb["verdict"] != ra["verdict"]
    line(f"verdict changed = {flip}   {rb['verdict']} -> {ra['verdict']}")
    line("RESULT: " + ("VIOLATED" if flip else "HOLDS"))
    return flip, rb, ra


def inv2_threshold_bump():
    """
    Experiment 2C (discriminates H3: diversity_bonus/support raise a band edge).
    Find a baseline whose final_score sits just below a verdict threshold, then
    add an irrelevant NEW-type zero-score artifact and see if diversity_bonus
    (+0.05 per new type) + support_score bump crosses the edge.

    PREDICTION (H3): a verdict change with NO score-lowering, purely additive.
    """
    hr("INV-2  Exp 2C  —  diversity/support bump across a band edge")
    line("PREDICTION (H3): zero-signal new-type doc nudges score across a threshold.")
    # Tune a baseline near SUSPICION(0.10)/UNKNOWN(0.08) or MALICE(0.33) edge.
    # Two device types, modest raw, so final_score lands just under 0.33.
    before = [
        art(0, "malware_infrastructure", raw=0.62),
        art(1, "keylogger_capture", raw=0.62),
        art(2, "keylogger_capture", raw=0.62),
    ]
    rb = score(before)
    after = before + [_irrelevant(3, "document")]   # new type, raw 0
    ra = score(after)
    line(f"BEFORE: score={rb['score']} verdict={rb['verdict']} diversity={rb['diversity_bonus']}")
    line(f"AFTER : score={ra['score']} verdict={ra['verdict']} diversity={ra['diversity_bonus']}")
    line(f"score delta = {ra['score']-rb['score']:+.4f}   verdict changed = {rb['verdict']!=ra['verdict']}")

    # Tuned band-edge flip: two log_entry @ raw=0.49 sit in NOISE (<=0.08);
    # adding a raw=0 'document' lifts diversity_bonus 0.00->0.05 and support,
    # crossing the UNKNOWN edge (0.08) with ZERO new signal.
    b2 = [art(0, "log_entry", raw=0.49), art(1, "log_entry", raw=0.49)]
    rb2 = score(b2)
    ra2 = score(b2 + [_irrelevant(2, "document")])
    line("  band-edge probe: 2x log_entry raw=0.49")
    line(f"    {rb2['score']} ({rb2['verdict']})  ->  {ra2['score']} ({ra2['verdict']})"
         f"   {'FLIP by irrelevant doc' if rb2['verdict']!=ra2['verdict'] else 'no flip'}")
    line("RESULT: " + ("VIOLATED (H3 corroborated)"
                       if rb2["verdict"] != ra2["verdict"] else "HOLDS"))
    return (rb2["verdict"] != ra2["verdict"]), rb, ra


def main():
    print("VIGIA Red-Team Round 2 — Monotonicity Invariants")
    print("scorer =", _vigia_score.__module__)
    v_new = inv1_matrix_newtype()
    v_same, worst = inv1_matrix_sametype()
    d_crisp = inv1_crisp()
    f_types, *_ = inv2_gate_ntypes()
    f_narts, *_ = inv2_gate_narts()
    f_edge, *_ = inv2_threshold_bump()

    hr("SUMMARY")
    line(f"INV-1 new-type additions violations : {v_new}   -> {'HOLDS' if v_new==0 else 'VIOLATED'}")
    line(f"INV-1 same-type additions violations: {v_same}  -> {'VIOLATED' if v_same else 'HOLDS'}")
    line(f"INV-1 crisp delta score             : {d_crisp:.4f}")
    line(f"INV-2 n_types gate flip (H2)        : {f_types}")
    line(f"INV-2 n_arts  gate flip             : {f_narts}")
    line(f"INV-2 band-edge diversity flip (H3) : {f_edge}")


if __name__ == "__main__":
    sys.exit(main())
