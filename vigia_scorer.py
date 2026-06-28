"""
vigia_scorer.py — VIGÍA Forensic Intent Scorer
===============================================

Part of the VIGÍA project — Forensic Intentionality Analysis Suite.
Developed for the SANS FIND EVIL Hackathon 2026.
Candidate for integration into SANS SIFT Workstation.

License: Apache 2.0
Repository: https://github.com/annatchijova/vigia-intent-analysis
Principal author: Anna Tchijova

DESCRIPTION:
    Standalone forensic scorer. Implements the malicious intent scoring
    pipeline: TrustFusion → CorrelationDecay → CAIE → Decision → Quadripartite.
    Does not require the vigia package to be installed — runs in standalone
    demo mode with safe fallback to conservative parameters.

FORENSIC PHILOSOPHY:
    Three pillars: Peircean Thirdness (abductive inference), Occam's Razor
    (hypothesis selection), Daubert admissibility. All output is deterministic,
    bit-for-bit reproducible, and auditable by an expert witness.

PATCH HISTORY:
    B1     : Live CAIE — fractures recomputed from artifacts, not from JSON
    B2     : source_counts indexed by evidence_type (same key as lookup)
    B3     : isolation_penalty / n_boost were dead code — removed
    B4     : diversity_bonus multiplicative, not additive — avoids score saturation
    P2     : adjusted_score unified with CAIE formula (EvidenceProfile) — Kimi 2026-05-19
    P4     : MALICIOUS_FRACTURE_TYPES sanitised — removed 3 phantom types,
             added FALSE_FLAG_PATTERN which CAIE does generate — Kimi 2026-05-19
    P5     : Determinism P0 — decimal.Decimal + _dround/_dsum — Kimi 2026-05-19
    P6     : Finite Math Shield — float('inf')/NaN in raw_score → 0.0 — Kimi 2026-05-19
    P1-K   : CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED added to CREDIBILITY_REDUCING_TYPES
             — was invisible to the scorer — Kimi 2026-05-19
    Q1     : Quadripartite bridge — connects simple 4-state scorer to the full
             8-state cascade via QuadripartiteClassifier — 2026-05-31

KNOWN LIMITATIONS:
    - EvidenceProfile fallback (spoofability=0.50, weight=0.20) is conservative
      but not calibrated. Real calibration requires a labelled forensic corpus.
      See fit_calibration.py and run_calibration.py.
    - Assumption invalidation propagation (ATMS) has depth 1.
      A invalidates B, B invalidates C does not propagate automatically.
      See integrity_constraints.py — roadmap v2.0.
    - The scorer does not persist state between executions. Each call is independent.
    - Live CAIE requires the vigia package to be installed. In standalone mode
      it uses pre-computed fractures from the JSON (caie_fractures_source: "json_fallback").
      The bundle documents which mode was used.
    - _dround() guarantees cross-platform determinism for output at 4 decimal places.
      Tested on x86-64 and ARM64 Linux (CPython 3.12). Pending: macOS, Windows.
    - Boost (0.45) and penalty (0.25) coefficients are heuristic, not
      calibrated on a real corpus. Roadmap: Bayesian calibration.
    - Quadripartite bridge uses mean_effective_trust as stability proxy.
      The full graph_stability engine is not invoked here to keep the scorer
      self-contained. For production use, wire graph_stability directly.
"""
from __future__ import annotations

import decimal
import json
import logging
import math
import sys
from fractions import Fraction

# ── P0 Lookup Tables — eliminan funciones transcendentales del scoring path ──
# Auditado: Claude + Kimi, 2026-06-14. Reemplaza math.log() y math.exp()
# que son platform-dependent a nivel ULP, violando reproducibilidad Daubert.
# Valores calculados con decimal.Decimal(precision=50) y Fraction.limit_denominator(100000).

# support_score = min(1.0, log(1+n) / log(5)) para n=1..20
# Solo n=1,2,3 son no-triviales; n>=4 satura a 1.
_SUPPORT_SCORE_TABLE: dict[int, Fraction] = {
     1: Fraction(4004, 9297),   # log(2)/log(5) = 0.4306765581
     2: Fraction(4725, 6922),   # log(3)/log(5) = 0.6826061945
     3: Fraction(8008, 9297),   # log(4)/log(5) = 0.8613531161
}
# n>=4: log(1+n)/log(5) >= 1.0 → clamped to Fraction(1,1)

# epc_factor = 0.95 ** k, k = max(0, len(chain) - 3)
# 0.95 = 19/20 → potencias son fracciones exactas
_EPC_FACTOR_TABLE: dict[int, Fraction] = {
     0: Fraction(1, 1),
     1: Fraction(19, 20),
     2: Fraction(361, 400),
     3: Fraction(6859, 8000),
     4: Fraction(130321, 160000),
     5: Fraction(2476099, 3200000),
     6: Fraction(47045881, 64000000),
     7: Fraction(893871739, 1280000000),
     8: Fraction(16983563041, 25600000000),
     9: Fraction(322687697779, 512000000000),
    10: Fraction(6131066257801, 10240000000000),
    11: Fraction(116490258898219, 204800000000000),
    12: Fraction(2213314919066161, 4096000000000000),
    13: Fraction(42052983462257059, 81920000000000000),
    14: Fraction(799006685782884121, 1638400000000000000),
    15: Fraction(15181127029874798299, 32768000000000000000),
}

# temporal_factor = exp(-2 * max_ws), max_ws bucketed to nearest 0.05
# key = round(max_ws / 0.05), clamped to [0, 20]
_EXP_NEG2_TABLE: dict[int, Fraction] = {
     0: Fraction(1, 1),
     1: Fraction(57630, 63691),
     2: Fraction(13559, 16561),
     3: Fraction(50286, 67879),
     4: Fraction(26788, 39963),
     5: Fraction(20841, 34361),
     6: Fraction(28148, 51289),
     7: Fraction(46609, 93859),
     8: Fraction(37297, 83006),
     9: Fraction(40263, 99031),
    10: Fraction(18089, 49171),
    11: Fraction(6481, 19470),
    12: Fraction(13342, 44297),
    13: Fraction(4436, 16277),
    14: Fraction(24529, 99470),
    15: Fraction(21053, 94353),
    16: Fraction(9283, 45979),
    17: Fraction(9999, 54734),
    18: Fraction(3404, 20593),
    19: Fraction(4282, 28629),
    20: Fraction(12957, 95740),
}
# ─────────────────────────────────────────────────────────────────────────────
from pathlib import Path

# ---------------------------------------------------------------------------
# P5: Determinism P0 — same protocol as CAIE
# decimal.Decimal with prec=28 and ROUND_HALF_EVEN eliminates bit-52 mantissa
# divergence that native round() can produce on architectures with different
# floating-point evaluation order (x86 vs ARM).
# ---------------------------------------------------------------------------
_DETERMINISTIC_INTERNAL_PREC = 6
_DETERMINISTIC_OUTPUT_PREC   = 4

decimal.getcontext().prec     = 28
decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN

_D_ZERO = decimal.Decimal("0")
_D_ONE  = decimal.Decimal("1")


def _dround(value, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> float:
    """
    Deterministic rounding — P0.
    Finite Math Shield integrated: returns 0.0 for inf, -inf, NaN.
    Guarantees identical result on x86-64 and ARM64 for precision <= 15.
    """
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


def _dsum(values) -> float:
    """
    Sum with decimal.Decimal accumulator to avoid floating-point drift.
    Accepts any iterable of int/float. Non-finite values are discarded.
    """
    acc = _D_ZERO
    for v in values:
        if isinstance(v, (int, float)) and math.isfinite(v):
            acc += decimal.Decimal(str(v))
    return _dround(float(acc), _DETERMINISTIC_INTERNAL_PREC)


# ---------------------------------------------------------------------------
# ANSI constants — defined inline, not imported from external module.
# Allows this file to be standalone without vigia package dependencies.
# ---------------------------------------------------------------------------
RED = "\033[91m"
YEL = "\033[93m"
GRN = "\033[92m"
BLU = "\033[94m"
PUR = "\033[95m"
BLD = "\033[1m"
RST = "\033[0m"

# ---------------------------------------------------------------------------
# Q1: Quadripartite bridge — optional import, degrades gracefully.
# Connects the simple 4-state scorer to the full 8-state cascade.
# ---------------------------------------------------------------------------
try:
    from vigia.verdict.quadripartite import QuadripartiteClassifier as _QuadClassifier
    _QUAD_AVAILABLE = True
except ImportError:
    try:
        import sys as _sys_q, os as _os_q
        _sys_q.path.insert(0, _os_q.path.join(_os_q.path.dirname(_os_q.path.abspath(__file__)), "vigia", "verdict"))
        from quadripartite import QuadripartiteClassifier as _QuadClassifier
        _QUAD_AVAILABLE = True
    except ImportError:
        _QUAD_AVAILABLE = False

# Vocabulary mapping: scorer 4-state → quadripartite raw_verdict.
# SUSPICION maps to ABSTAIN because the signal exists but does not reach
# the forensic action threshold. QuadripartiteClassifier will resolve it
# as ABSTAIN_INSUFFICIENT, which is semantically correct.
_VERDICT_TO_RAW: dict[str, str] = {
    "MALICE":    "MALICE",
    "SUSPICION": "ABSTAIN",
    "NOISE":     "BENIGN",
    "UNKNOWN":   "ABSTAIN",
}

_ABSTAIN_REASONS: dict[str, str] = {
    "SUSPICION": (
        "Significant signal below MALICE threshold — "
        "corroboration required before forensic action."
    ),
    "UNKNOWN": (
        "Insufficient structural support — "
        "more evidence required."
    ),
}


def _normalize_case(c):
    """
    Normalises a case to the canonical VIGÍA schema.
    Transparent fallback if the bridge is not available (standalone mode).
    """
    try:
        from vigia.pipeline.vigia_integration_bridge import normalize_case_schema
        return normalize_case_schema(c)
    except Exception:
        return c


def _verdict_color(verdict) -> str:
    """
    Returns ANSI code for the verdict.
    Accepts str or Enum (compatibility with CollapseDecisionLayer).
    """
    v_str = verdict.value if hasattr(verdict, "value") else str(verdict)
    return {
        "MALICE":       RED + BLD,
        "SUSPICION":    YEL + BLD,
        "INCONCLUSIVE": PUR + BLD,
        "NOISE":        GRN,
    }.get(v_str.upper(), BLU)


def _compute_temporal_factor(violations: list[dict], artifact_id: str) -> Fraction:
    """
    Temporal penalty factor per artifact. Returns Fraction (P0: no math.exp()).

    Inline — does not depend on the vigia package. Allows standalone demo execution.

    Weights by violation type (forensic severity):
      EFFECT_BEFORE_CAUSE    : physical law violation — maximum weight (1.0)
      TOO_FAST               : physically impossible speed — high weight (0.7)
      STATISTICAL_UNIFORMITY : artificial distribution — medium weight (0.6)
      IDENTICAL_TIMESTAMP    : timestamp collision — medium-low weight (0.5)
      CLOCK_SKEW             : synchronisation noise — low weight (0.4)

    P0 patch 2026-06-14 (Claude+Kimi): replaced math.exp(-2*x) with
    _EXP_NEG2_TABLE keyed on round(max_ws/0.05). max_ws bucketed to 0.05
    precision — max error 0.025 in argument, negligible vs _dround(prec=4).
    """
    weights = {
        "EFFECT_BEFORE_CAUSE":    Fraction(1, 1),
        "TOO_FAST":               Fraction(7, 10),
        "STATISTICAL_UNIFORMITY": Fraction(3, 5),
        "IDENTICAL_TIMESTAMP":    Fraction(1, 2),
        "CLOCK_SKEW":             Fraction(2, 5),
    }
    relevant = [
        v for v in violations
        if v.get("cause",  {}).get("artifact_id") == artifact_id
        or v.get("effect", {}).get("artifact_id") == artifact_id
    ]
    if not relevant:
        return Fraction(1, 1)
    ws = [Fraction(str(v.get("severity", 0.5))) * weights.get(v.get("type", ""), Fraction(1, 2))
          for v in relevant]
    max_ws = max(ws)
    max_ws_clamped = min(Fraction(1, 1), max(Fraction(0, 1), max_ws))
    # Bucket to nearest 0.05 for table lookup
    bucket_key = min(20, max(0, round(float(max_ws_clamped) / 0.05)))
    return _EXP_NEG2_TABLE[bucket_key]


def _naive_score(artifacts: list[dict]) -> float:
    """
    Naive baseline: average of raw_scores without trust adjustment or correlation.
    Used as a reference to detect divergence from the full pipeline.

    P5: _dsum/_dround for P0 determinism.
    P6: Finite Math Shield — non-finite raw_score → 0.0.
    """
    if not artifacts:
        return 0.0
    scores = []
    for a in artifacts:
        rs = a.get("raw_score", 0.0)
        if isinstance(rs, (int, float)) and math.isfinite(rs):
            scores.append(max(0.0, min(1.0, rs)))
        else:
            scores.append(0.0)
    return _dround(_dsum(scores) / len(scores), _DETERMINISTIC_OUTPUT_PREC)


def _apply_quadripartite(
    verdict:    str,
    confidence: float,
    stability:  float,
    fractures:  list,
) -> dict:
    """
    Q1: Wraps QuadripartiteClassifier.classify() around the simple scorer output.

    Uses mean_effective_trust as stability proxy — the graph_stability engine
    is not invoked here to keep the scorer self-contained. For production use,
    wire graph_stability directly.

    Returns a dict with the full render_for_report output so the caller never
    has to import quadripartite directly.

    Degrades gracefully if quadripartite is unavailable (returns stub).
    """
    if not _QUAD_AVAILABLE:
        return {
            "verdict_state":   "UNAVAILABLE",
            "action_required": "quadripartite module not found",
            "analyst_summary": "",
            "confidence_pct":  round(confidence * 100),
        }

    raw_verdict    = _VERDICT_TO_RAW.get(verdict, "ABSTAIN")
    abstain_reason = _ABSTAIN_REASONS.get(verdict)

    # Convert floats to Fraction for deterministic arithmetic.
    # Clamp to [0, 1] before converting to avoid Fraction overflow on
    # floating-point noise (e.g. 1.0000000000000002).
    conf_frac = Fraction(min(1, max(0, round(confidence, 4)))).limit_denominator(10000)
    stab_frac = Fraction(min(1, max(0, round(stability,  4)))).limit_denominator(10000)

    # Degraded flag: active fractures AND very low confidence → degraded mode.
    has_active_fractures = isinstance(fractures, list) and len(fractures) > 0
    integrity_level = (
        "DEGRADED_MODE"
        if (has_active_fractures and conf_frac < Fraction(3, 10))
        else "FULL_INTEGRITY"
    )

    try:
        classifier = _QuadClassifier()
        qv = classifier.classify(
            raw_verdict=raw_verdict,
            confidence=conf_frac,
            stability=stab_frac,
            integrity_level=integrity_level,
            dissent_info={},
            abstain_reason=abstain_reason,
            pivot_signals=[],
            investigation_roadmap=[],
            adversarial_penalty=False,
        )
        # render_for_report produces the canonical structured dict.
        return classifier.render_for_report(qv)
    except Exception as exc:
        # Never let the quadripartite crash the main scoring path.
        return {
            "verdict_state":   "QUADRIPARTITE_ERROR",
            "action_required": f"classification failed: {exc}",
            "analyst_summary": "",
            "confidence_pct":  round(confidence * 100),
        }


def _vigia_score(case: dict) -> dict:
    """
    VIGÍA malicious intent scoring pipeline.

    Implements: TrustFusion → CorrelationDecay → CAIE → Decision → Quadripartite.

    Args:
        case: dict with ForensicBundle schema. Expected fields:
            artifacts            : list[dict] — forensic artifacts
            temporal_violations  : list[dict] — temporal violations
            provenance_analysis  : dict       — chain-of-custody analysis
            caie_fractures       : list[dict] — pre-computed fractures (JSON fallback)
            peirce_chain         : dict       — Peircean abductive chain
            expected_verdict     : str        — expected verdict (for evaluation)

    Returns:
        JSON-serialisable dict with verdict, score, confidence, and full
        traceability for expert witness testimony under the Daubert standard.
        caie_fractures_source indicates whether live CAIE ("live_caie") or
        pre-computed JSON fractures ("json_fallback") were used.
    """
    case       = _normalize_case(case)
    artifacts  = case.get("artifacts", [])
    violations = case.get("temporal_violations", [])
    provenance = case.get("provenance_analysis", {})

    if not artifacts:
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": [], "error": "No artifacts provided — cannot evaluate intentionality without evidence"}

    # -----------------------------------------------------------------------
    # B1: Live CAIE — recompute fractures from artifacts
    # The original bug read fractures from the pre-computed JSON, so new CAIE
    # rules were never applied. Case 009 (NARRATIVE_POISONING) failed because
    # the fracture existed in CAIE but not in the stale JSON.
    # Falls back to the JSON if CAIE is not available (standalone mode).
    # -----------------------------------------------------------------------
    fractures    = []
    _caie_source = "json_fallback"
    try:
        from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact as CaieArtifact
        _valid_fields = {
            "source_tool", "evidence_type", "raw_score", "description",
            "metadata", "provenance_chain", "base_trust", "timestamp",
        }
        engine = CrossArtifactIncongruenceEngine()
        for art in artifacts:
            filtered = {k: v for k, v in art.items() if k in _valid_fields}
            try:
                engine.add_artifact(CaieArtifact(**filtered))
            except Exception:
                continue  # artifact with invalid schema — skip, do not break pipeline
        raw_fractures = engine.detect_fractures()
        fractures = [
            {
                "fracture_type":  f.fracture_type,
                "severity":       f.severity,
                "artifact_a":     f.artifact_a,
                "artifact_b":     f.artifact_b,
                "interpretation": f.interpretation,
                "ttp_id":         f.ttp_id,
            }
            for f in raw_fractures
        ]
        _caie_source = "live_caie"
    except Exception as e:
        logging.warning("CAIE failed, using json_fallback: %s", e)
        fractures    = case.get("caie_fractures", [])
        _caie_source = "json_fallback"

    # -----------------------------------------------------------------------
    # Step 1: effective_trust per artifact
    #
    # effective_trust = prior_trust × epc_factor × temporal_factor
    #   prior_trust    : artifact prior confidence
    #   epc_factor     : penalty for broken or long chain of custody
    #   temporal_factor: penalty for temporal violations on this artifact
    #
    # P2: adjusted_score with unified CAIE formula:
    #   adjusted = raw_score × (1 − spoofability) × weight × effective_trust
    #   spoofability and weight are read from EvidenceProfile (CAIE).
    #   Conservative fallback if CAIE is unavailable: spoofability=0.50, weight=0.20.
    #   LIMITATION: fallback is not calibrated. See fit_calibration.py.
    #
    # P6: Finite Math Shield — raw_score=inf/NaN → 0.0, does not contaminate verdict.
    # P5: _dround on all intermediate values.
    # -----------------------------------------------------------------------
    effective_trusts = []
    for a in artifacts:
        # P6: Finite Math Shield
        raw_score = a.get("raw_score", 0.0)
        if not isinstance(raw_score, (int, float)) or not math.isfinite(raw_score):
            raw_score = 0.0
        raw_score = max(0.0, min(1.0, raw_score))

        prov_trust = a.get("prior_trust", 1.0)
        chain      = a.get("provenance_chain", [])
        if provenance.get("chain_status") == "BROKEN" or not chain:
            epc_factor = 0.1
        else:
            _epc_k = min(15, max(0, len(chain) - 3))  # P0: Fraction lookup, no float pow
            epc_factor = _EPC_FACTOR_TABLE[_epc_k]

        temp_factor = _compute_temporal_factor(violations, a.get("artifact_id", ""))
        effective   = _dround(prov_trust * epc_factor * temp_factor, _DETERMINISTIC_OUTPUT_PREC)

        # P2 + acquisition_assurance: CAIE formula with contextual spoofability.
        # Instantiates Artifact to obtain effective_spoofability, which incorporates
        # forensic acquisition gates G1-G4 (collective VIGÍA decision).
        # Conservative fallback if CAIE is not available.
        try:
            from vigia.tools.caie import EVIDENCE_PROFILES, Artifact as _CaieArtifact
            profile = EVIDENCE_PROFILES.get(a.get("evidence_type"))
            weight  = profile.base_weight if profile else 0.20
            _filtered = {
                k: v for k, v in a.items()
                if k in {"source_tool", "evidence_type", "raw_score",
                         "description", "metadata", "provenance_chain",
                         "base_trust", "timestamp"}
            }
            _filtered.setdefault("description", str(a.get("content", ""))[:200] or "legacy_artifact")
            _caie_art    = _CaieArtifact(**_filtered)
            spoofability = _caie_art.effective_spoofability
        except Exception:
            spoofability = 0.50
            weight       = 0.20

        step1    = _dround(raw_score  * (1.0 - spoofability), _DETERMINISTIC_INTERNAL_PREC)
        step2    = _dround(step1      * weight,               _DETERMINISTIC_INTERNAL_PREC)
        adjusted = _dround(step2      * effective,            _DETERMINISTIC_OUTPUT_PREC)

        effective_trusts.append({
            "artifact_id":     a.get("artifact_id"),
            "evidence_type":   a.get("evidence_type"),
            "raw_score":       raw_score,
            "effective_trust": effective,
            "adjusted_score":  adjusted,
            "spoofability":    spoofability,   # traceable in expert testimony
            "weight":          weight,         # traceable in expert testimony
        })

    # -----------------------------------------------------------------------
    # Step 2: Correlation decay
    #
    # Penalises artifacts of the same evidence type (redundancy → less new
    # information). Bonuses diversity of types (multi-source signal).
    #
    # B2: source_counts indexed by evidence_type — same key as the lookup.
    #     Original bug: indexed by acquisition_record, penalty never applied.
    # B4: diversity_bonus multiplicative before clamping.
    #     Original bug: additive, could saturate the score without enough evidence.
    # -----------------------------------------------------------------------
    source_counts: dict[str, int] = {}
    for a in artifacts:
        src = a.get("evidence_type", "?")
        source_counts[src] = source_counts.get(src, 0) + 1

    unique_types    = len(set(a.get("evidence_type") for a in artifacts))
    diversity_bonus = _dround(min(0.2, (unique_types - 1) * 0.05), _DETERMINISTIC_INTERNAL_PREC)

    adj_scores = []
    for et in effective_trusts:
        et_type        = et["evidence_type"]
        count          = source_counts.get(et_type, 1)
        source_penalty = min(0.5, (count - 1) * 0.15)
        adj            = _dround(et["adjusted_score"] * (1 - source_penalty), _DETERMINISTIC_OUTPUT_PREC)
        adj_scores.append(adj)

    if not adj_scores:
        composite = 0.0
    else:
        raw_composite = _dround(
            1.0 - math.prod([max(0.0, 1.0 - s) for s in adj_scores]),
            _DETERMINISTIC_INTERNAL_PREC,
        )
        composite = _dround(raw_composite * (1.0 + diversity_bonus), _DETERMINISTIC_OUTPUT_PREC)
        composite = min(0.99, composite)

    # -----------------------------------------------------------------------
    # Step 3: CAIE fracture analysis
    #
    # CRITICAL DISTINCTION (Daubert):
    #   DELIBERATE PLANTING fractures → raise malicious intent score.
    #     Semantics: "someone acted to deceive" → evidence of a deliberate agent.
    #   INTERNAL INCONSISTENCY fractures → reduce evidence credibility.
    #     Semantics: "evidence is incoherent" → score decreases.
    #
    # P4: MALICIOUS_FRACTURE_TYPES sanitised — only types CAIE v2.0 generates.
    #   Removed (phantoms — do not exist in CAIE v2.0):
    #     STATISTICAL_UNIFORMITY, LIVE_RESPONSE_VS_DISK, CLOUD_VS_ONPREM
    #   Added:
    #     FALSE_FLAG_PATTERN (was the major gap — CAIE generates it, scorer ignored it),
    #     NETWORK_VS_HOST, DOCUMENT_FORGERY, MFT_ENTRY_ANOMALY,
    #     USN_JOURNAL_GAP, NARRATIVE_POISONING_DETECTED
    #
    # NOTE: STATISTICAL_UNIFORMITY from temporal violations (temporal engine, not CAIE)
    #   is processed below — it is a valid deliberate-automation signal.
    #
    # LIMITATION: boost=0.45 and penalty=0.25 coefficients are heuristic.
    #   Roadmap: Bayesian calibration on labelled case dataset.
    # -----------------------------------------------------------------------
    fracture_malice_boost        = 0.0
    fracture_credibility_penalty = 0.0

    MALICIOUS_FRACTURE_TYPES = {
        "FALSE_FLAG_PATTERN",
        "TEMPORAL_CAUSALITY_VIOLATION",
        "CRYPTOGRAPHIC_INCONSISTENCY",
        "NETWORK_VS_HOST",
        "DOCUMENT_FORGERY",
        "MFT_ENTRY_ANOMALY",
        "USN_JOURNAL_GAP",
        "NARRATIVE_POISONING_DETECTED",
    }
    CREDIBILITY_REDUCING_TYPES = {
        "VERDICT_CONFLICT",
        "METADATA_CONCEALMENT",
        # P1-K fix (Kimi 2026-05-19): CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED was
        # invisible to the scorer — passed without penalty or boost. CAIE generates
        # it when there is a hash mismatch but the trust-chain was NOT validated
        # (severity=0.6). Cannot be MALICIOUS (no spoofing confirmation), but does
        # reduce credibility: there is unexplained cryptographic discrepancy.
        # fracture_credibility_penalty += sev * 0.25 captures this correctly.
        "CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED",
        "ATTRIBUTION_INCONSISTENCY",
    }

    for f in fractures:
        sev = f.get("severity", 0.5)
        ft  = f.get("fracture_type", "")
        if ft in MALICIOUS_FRACTURE_TYPES:
            fracture_malice_boost += sev * 0.45
        elif ft in CREDIBILITY_REDUCING_TYPES:
            fracture_credibility_penalty += sev * 0.25

    fracture_malice_boost        = min(0.5,  fracture_malice_boost)
    fracture_credibility_penalty = min(0.35, fracture_credibility_penalty)

    # STATISTICAL_UNIFORMITY from the temporal engine (not CAIE) — valid signal
    for v in violations:
        if v.get("type") == "STATISTICAL_UNIFORMITY":
            fracture_malice_boost += v.get("severity", 0) * 0.35

    fracture_malice_boost = min(0.5, fracture_malice_boost)

    # Hard gate: physical law violation — unconditional MALICE override
    hard_temporal = any(
        v.get("type") == "EFFECT_BEFORE_CAUSE" and v.get("severity", 0) >= 0.9
        for v in violations
    )

    # -----------------------------------------------------------------------
    # Step 4: Decision
    #
    # final_score = raw_intent_score × (0.9 + 0.1 × support_score)
    # support_score penalises cases with very few artifacts (scarce evidence).
    # Explicit gate: a single artifact cannot exceed score 0.65.
    #
    # B3: isolation_penalty and n_boost were dead code — existed but were never
    #     applied to final_score. Removed to avoid confusion.
    # P5: _dround on raw_intent_score and final_score.
    #
    # Recalibrated thresholds for P2 scale (patch 2026-05-19):
    # The P2 formula (raw × (1-spoofability) × weight × trust) produces scores
    # in range [0, ~0.54] without CAIE fractures, vs [0, ~0.99] with the old
    # formula. With original thresholds (0.75/0.55/0.25), MALICE was
    # mathematically impossible without fractures — guaranteed false negative.
    # New thresholds calibrated on real EBS v1 case distribution:
    #   MALICE    : > 0.33 (P2 + acquisition_assurance recalibration)
    #   SUSPICION : > 0.18 (structural signal without certainty threshold)
    #   UNKNOWN   : > 0.08 (weak anomaly — requires human analysis)
    #   NOISE     : <= 0.08 (no relevant forensic signal)
    # -----------------------------------------------------------------------
    raw_intent_score = _dround(
        max(0.0, min(0.99, composite + fracture_malice_boost - fracture_credibility_penalty)),
        _DETERMINISTIC_OUTPUT_PREC,
    )

    n_artifacts   = len(artifacts)
    support_score = _SUPPORT_SCORE_TABLE.get(n_artifacts, Fraction(1, 1))  # P0: Fraction lookup, no math.log()
    final_score   = _dround(raw_intent_score * (0.9 + 0.1 * support_score), _DETERMINISTIC_OUTPUT_PREC)

    mean_effective = _dround(
        _dsum(e["effective_trust"] for e in effective_trusts) / len(effective_trusts),
        _DETERMINISTIC_OUTPUT_PREC,
    )

    # Collapsed provenance without fractures → NOISE (inadmissible under Daubert)
    # Collapsed provenance WITH fractures → possible planting → SUSPICION
    provenance_collapsed = (
        mean_effective < 0.01
        and not fractures
    )

    if n_artifacts < 2 and final_score > 0.65:
        final_score = 0.65

    if hard_temporal:
        verdict    = "MALICE"
        confidence = 0.95
        reason     = "HARD GATE: EFFECT_BEFORE_CAUSE — physical law violation"
    elif provenance_collapsed:
        verdict    = "NOISE"
        confidence = _dround(1.0 - mean_effective, 2)
        reason     = "Provenance chain collapsed, no active fractures — inadmissible under Daubert"
    elif mean_effective < 0.15 and fractures:
        verdict    = "SUSPICION"
        confidence = _dround(min(0.75, fracture_malice_boost + 0.3), 2)
        reason     = f"Broken chain of custody + {len(fractures)} active fracture(s) — deliberate manipulation"
    elif final_score > Fraction(33, 100):
        # Corroboration gate: MALICE requires convergence of heterogeneous evidence.
        # Daubert principle: a single class of technical evidence, regardless of
        # its raw_score, does not justify an inference of malicious intent.
        # Requirement: n_artifacts >= 4 OR n_unique_types >= 3.
        _n_arts  = len(artifacts)
        _n_types = len(set(a.get("evidence_type", "") for a in artifacts))
        if _n_arts >= 4 or _n_types >= 3:
            verdict = "MALICE"
        else:
            verdict = "SUSPICION"
        confidence = _dround(min(0.95, final_score * 2.0), 2)
        reason     = f"Intent score {final_score:.4f} exceeds MALICE threshold (P2+acq_assurance scale, threshold=0.33)"
    elif final_score > Fraction(18, 100):
        verdict    = "SUSPICION"
        confidence = _dround(final_score * 2.0, 2)
        reason     = f"Significant signal with structural support (score={final_score:.4f})"
    elif final_score > Fraction(8, 100):
        verdict    = "UNKNOWN"
        confidence = _dround(final_score * 2.0, 2)
        reason     = f"Anomaly without sufficient structural support (score={final_score:.4f})"
    else:
        verdict    = "NOISE"
        confidence = _dround(1.0 - final_score, 2)
        reason     = f"Insufficient evidence of malicious intent (score={final_score:.4f})"

    # -----------------------------------------------------------------------
    # Step 5: Quadripartite 8-state cascade (Q1)
    # Non-destructive: base verdict field is unchanged.
    # Adds "quadripartite_state" with the full render_for_report output.
    # -----------------------------------------------------------------------
    base_result = {
        "verdict":                      verdict,
        "score":                        final_score,
        "confidence":                   confidence,
        "reason":                       reason,
        "mean_effective_trust":         mean_effective,
        "composite_base":               _dround(composite, _DETERMINISTIC_OUTPUT_PREC),
        "fracture_malice_boost":        _dround(fracture_malice_boost, _DETERMINISTIC_OUTPUT_PREC),
        "fracture_credibility_penalty": _dround(fracture_credibility_penalty, _DETERMINISTIC_OUTPUT_PREC),
        "diversity_bonus":              _dround(diversity_bonus, _DETERMINISTIC_OUTPUT_PREC),
        "hard_temporal_gate":           hard_temporal,
        "effective_trusts":             effective_trusts,
        "temporal_violations":          len(violations),
        "caie_fractures":               len(fractures),
        "caie_fractures_source":        _caie_source,
        "peirce_chain":                 case.get("peirce_chain", {}),
        "expected_verdict":             case.get("expected_verdict", "UNKNOWN"),
    }

    base_result["quadripartite_state"] = _apply_quadripartite(
        verdict=verdict,
        confidence=confidence,
        stability=mean_effective,
        fractures=fractures,
    )

    return base_result
