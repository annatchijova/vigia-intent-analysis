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

# M2-2 (Red-Team Round 2, docs/REDTEAM_ROUND2_MONOTONICITY.md): umbral mínimo
# de VALOR EVIDENCIAL para que un artefacto cuente como SEÑAL estructural —
# es decir, para que incremente n_artifacts/support_score, unique_types/
# diversity_bonus y la corroboración del gate B-068. Sin este umbral, el gate
# contaba cardinalidad sin consultar la señal y un documento vacío
# (README.txt, una foto, un manual.pdf) de tipo nuevo volteaba SUSPICION →
# MALICE (invariante No-Dilution).
#
# El umbral se mide sobre adjusted_score = raw × (1−spoofability) × weight ×
# trust — la métrica de valor evidencial propia del scorer (fórmula Kimi) —
# y NO sobre raw_score crudo: un raw 0.08 en memory_process (clase pesada,
# difícil de fabricar, cadena confiable) porta más valor probatorio que el
# mismo 0.08 en un log_entry spoofeable con trust degradado. raw_score=0 ⇒
# adjusted=0 ⇒ nunca corrobora (pedido mínimo M2-2); un artefacto con señal
# pero trust efectivo 0 tampoco (más estricto que raw>0 — y más defendible:
# evidencia sin cadena de custodia no puede ser "fuente independiente").
# Comparación ESTRICTA (adjusted > umbral).
#
# Valor 0.0 (estricto >): CUALQUIER valor evidencial positivo corrobora,
# como en el esquema legacy. NOTA DE CALIBRACIÓN (medido, 2026-07-07): no
# existe umbral > 0 compatible con el corpus de 199 casos — los casos MALICE
# canónicos corroboran con artefactos de adjusted 0.0017–0.002, mientras que
# excluir el diluyente de VIGIA-CAN-029 exigiría > 0.013. Intervalo vacío;
# ver docs/REDTEAM_ROUND2_MONOTONICITY.md §Round 2.1.
_M2_MIN_SIGNAL_ADJ: float = 0.0

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
    # P2-D (Tanda B): el scorer ahora emite ABSTAIN de primera clase
    # (provenance colapsada). Mapea directo — el clasificador lo resuelve
    # como ABSTAIN_DEGRADED vía la razón de abajo.
    "ABSTAIN":   "ABSTAIN",
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
    "ABSTAIN": (
        "Provenance chain collapsed — evidence trust insufficient to "
        "assert benignity; re-acquisition required (P2-D)."
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


def _frac_sev(raw, default: "Fraction" = Fraction(1, 2)) -> "Fraction":
    """
    Coerce an examiner-supplied severity to an exact Fraction, shielding the
    decision path against malformed values. A string ("high") or None in a
    temporal_violations severity previously reached Fraction(str(raw)) and
    raised ValueError, crashing the whole scorer. Non-parseable -> default
    (0.5, matching the missing-key `.get(..., 0.5)` convention). Valid numeric
    values are passed through UNCHANGED (no clamp) so corpus scoring stays
    bit-identical. Ref: docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-E.
    """
    try:
        return Fraction(str(raw))
    except (ValueError, ZeroDivisionError, TypeError):
        return default


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
    ws = [_frac_sev(v.get("severity", 0.5)) * weights.get(v.get("type", ""), Fraction(1, 2))
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

    if verdict not in _VERDICT_TO_RAW:
        raise ValueError(
            f"VIGÍA scorer: veredicto desconocido {verdict!r} — "
            f"valores válidos: {list(_VERDICT_TO_RAW.keys())}. "
            f"Fallo ruidoso en lugar de colapso silencioso a ABSTAIN (Daubert)."
        )
    raw_verdict    = _VERDICT_TO_RAW[verdict]
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
    # Round 4 (boundary): un `case` que no es dict (None, str, lista, número)
    # rompía en `case.get(...)` con AttributeError. Fail-loud LIMPIO: ERROR, no
    # excepción — el scorer nunca debe crashear por un input degenerado.
    if not isinstance(case, dict):
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": [],
                "error": f"case must be a dict, got {type(case).__name__} — "
                         f"cannot evaluate"}

    case          = _normalize_case(case)
    if not isinstance(case, dict):
        # _normalize_case (bridge) podría degradar a no-dict — misma guarda.
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": [],
                "error": "normalized case is not a dict — cannot evaluate"}
    artifacts_all = case.get("artifacts", [])
    violations    = case.get("temporal_violations", [])
    provenance    = case.get("provenance_analysis", {})

    if not artifacts_all:
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": [], "error": "No artifacts provided — cannot evaluate intentionality without evidence"}

    # -----------------------------------------------------------------------
    # B-070: rol epistémico (device / contextual / narrative). Fuente única en
    # vigia.tools.caie.evidence_role. Las clases NARRATIVE (motivo/persona/
    # desenlace) se apartan ANTES de todo el scoring: no alimentan CAIE, ni el
    # composite de malicia, ni el gate de corroboración — informan solo la
    # narrativa del reporte. Cierra el canal composite del FP NGDC-003
    # (AUDITORIA_ABDUCTIVA_NGDC003_FP §canal composite): un artefacto que
    # documenta la intención como indecidible no puede subir el score de
    # malicia. Fallback mínimo si el paquete no está disponible (standalone).
    # -----------------------------------------------------------------------
    try:
        from vigia.tools.caie import (
            evidence_role as _evidence_role,
            EVIDENCE_ROLE_NARRATIVE as _ROLE_NARR,
            EVIDENCE_ROLE_DEVICE as _ROLE_DEVICE,
        )
    except Exception:
        _ROLE_NARR, _ROLE_DEVICE = "narrative", "device"
        _FALLBACK_NARR = frozenset({"behavioral_context", "behavioral_profile", "outcome_signal"})
        def _evidence_role(_t):  # mirror mínimo — fuente de verdad es caie
            return _ROLE_NARR if _t in _FALLBACK_NARR else _ROLE_DEVICE

    _narrative_artifacts = [
        a for a in artifacts_all
        if _evidence_role(str(a.get("evidence_type", ""))) == _ROLE_NARR
    ]
    artifacts = [
        a for a in artifacts_all
        if _evidence_role(str(a.get("evidence_type", ""))) != _ROLE_NARR
    ]

    if not artifacts:
        # Todo el evidence es narrativa de escenario: no hay evidencia de
        # dispositivo sobre la cual afirmar intención. ABSTAIN, no NOISE.
        return {
            "verdict": "ABSTAIN", "score": 0.0, "confidence": 0.0, "fractures": [],
            "narrative_context": [a.get("evidence_type") for a in _narrative_artifacts],
            "reason": ("Only narrative/scenario context present (motive, persona, "
                       "outcome) — no device evidence to evaluate intent (B-070)"),
        }

    # -----------------------------------------------------------------------
    # FASE 2 — semantic_role: dirección de la inferencia (ortogonal a B-070).
    # `evidence_role` clasifica la CLASE del artefacto; `semantic_role`
    # clasifica QUÉ ARGUMENTA su contenido:
    #   incriminatory (default) — suma al composite y corrobora el gate.
    #   exculpatory   — refutación documental (HR record, memo de
    #                   autorización, runbook auditado): se APARTA del
    #                   composite Y del gate B-068 (semántica V1 medida en
    #                   docs/FASE2_EVIDENCIA_EXCULPATORIA.md §3 — un HR
    #                   record es DEVICE por clase, así que sin este campo
    #                   no solo sumaba el score más alto: corroboraba
    #                   MALICE). Retenido en refutation_context del reporte.
    #   contextual    — permanece en el composite pero NO corrobora el gate
    #                   (mismo trato que el rol contextual de B-070).
    #
    # EXAMINER-DECLARED ÚNICAMENTE. Jamás derivado del contenido: el corpus
    # adversarial contiene el ataque exacto (cebo_falso_layman,
    # incompetencia_armamentizada, denunciante_humo — tickets lastimeros que
    # SON la firma Carnegie) y el auto-clasificador medido degrada 9 casos
    # maliciosos (§3, escenario S1).
    #
    # D1 (decisión de doctrina, Anna 2026-07-06): barra de corroboración
    # mínima — cada exculpatorio pasa por el filtro Eco (mismo criterio que
    # detect_eco_overinterpretation, fuente única en vigia.core.eco_check)
    # ANTES de ser apartado. Una "refutación" cuyo texto contiene vocabulario
    # de cebo obvio (onion, c&c, mimikatz…) NO se aparta: documentación
    # demasiado perfecta / mal etiquetada = señal, no refutación. El evento
    # queda sellado en refutation_context.eco_retained.
    # -----------------------------------------------------------------------
    # Capa 1 — fail-CLOSED (Q2, 2026-07-06). Antes el fallback de import devolvía
    # [] (fail-OPEN): sin el módulo Eco, D1 no podía correr y el exculpatorio se
    # apartaba IGUAL — un adversario que rompiera el import de eco_check
    # neutralizaba TODA la evidencia exculpatoria sin filtro. Ahora se aplica el
    # mismo patrón fail-loud/fail-closed que B-023/B-026: si D1 no puede
    # evaluarse, el artefacto NO se aparta automáticamente — se RETIENE en el
    # scoring y el evento queda sellado en refutation_context.eco_retained. La
    # neutralización requiere un filtro Eco OPERATIVO que la avale.
    _ECO_AVAILABLE = True
    try:
        from vigia.core.eco_check import text_obvious_bait_hits as _eco_bait_hits
    except Exception:
        _ECO_AVAILABLE = False

        def _eco_bait_hits(_t):
            return []

    def _semantic_role(a) -> str:
        role = str(a.get("semantic_role", "incriminatory")).strip().lower()
        return role if role in ("incriminatory", "exculpatory", "contextual") else "incriminatory"

    def _artifact_text(a) -> str:
        md = a.get("metadata", {})
        preview = str(md.get("content_preview", "")) if isinstance(md, dict) else ""
        return f"{a.get('description', '')} {preview}"

    _exculpatory_set_aside = []
    _exculpatory_eco_retained = []
    _scored_artifacts = []
    for a in artifacts:
        if _semantic_role(a) == "exculpatory":
            if not _ECO_AVAILABLE:
                # fail-closed: D1 indisponible → RETENER (no apartar). El
                # examinador declaró exculpatorio, pero sin filtro Eco operativo
                # no hay aval para removerlo del scoring.
                _exculpatory_eco_retained.append({
                    "artifact_id": a.get("artifact_id"),
                    "evidence_type": a.get("evidence_type"),
                    "eco_bait_terms": [],
                    "note": ("examiner-declared exculpatory RETAINED in scoring: "
                             "Eco module unavailable — fail-closed, refutation "
                             "cannot be validated (D1, patrón B-023)"),
                })
                _scored_artifacts.append(a)
                continue
            _hits = _eco_bait_hits(_artifact_text(a))
            if _hits:
                # D1: el filtro Eco disparó — la "refutación" grita ataque.
                # Permanece en el scoring como cualquier artefacto.
                _exculpatory_eco_retained.append({
                    "artifact_id": a.get("artifact_id"),
                    "evidence_type": a.get("evidence_type"),
                    "eco_bait_terms": _hits,
                    "note": ("examiner-declared exculpatory RETAINED in scoring: "
                             "Eco filter fired — too-perfect/staged refutation "
                             "is a signal, not a refutation (D1)"),
                })
                _scored_artifacts.append(a)
            else:
                _exculpatory_set_aside.append({
                    "artifact_id": a.get("artifact_id"),
                    "evidence_type": a.get("evidence_type"),
                    "raw_score": a.get("raw_score"),
                })
        else:
            _scored_artifacts.append(a)
    artifacts = _scored_artifacts

    if not artifacts:
        # Toda la evidencia de dispositivo fue declarada exculpatoria por el
        # examinador y superó el filtro Eco: refutación documental completa.
        # NOISE explícito (no ABSTAIN: acá SÍ hay evidencia, y refuta).
        return {
            "verdict": "NOISE", "score": 0.0, "confidence": 0.9, "fractures": [],
            "refutation_context": {
                "set_aside": _exculpatory_set_aside,
                "eco_retained": _exculpatory_eco_retained,
            },
            "narrative_context": [a.get("evidence_type") for a in _narrative_artifacts],
            "reason": ("All device evidence is examiner-declared exculpatory and "
                       "passed the Eco filter — documented refutation of malice "
                       "(FASE 2 semantic_role)"),
        }

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
            except Exception as _caie_skip_exc:
                logging.warning(
                    "CAIE: artifact %s skipped — schema validation failed: %s",
                    art.get("artifact_id", "unknown"), _caie_skip_exc
                )
                continue
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

        # B-026 FIX: prior_trust validado con el mismo Finite Math Shield que
        # raw_score (arriba). Sin este clamp, un prior_trust negativo/NaN/inf
        # entraba directo a effective = prov_trust × epc × temporal y producía
        # un trust efectivo imposible (negativo o NaN propagado al veredicto).
        prov_trust = a.get("prior_trust", 1.0)
        if not isinstance(prov_trust, (int, float)) or isinstance(prov_trust, bool) \
                or not math.isfinite(prov_trust):
            prov_trust = 1.0
        prov_trust = max(0.0, min(1.0, prov_trust))
        chain      = a.get("provenance_chain", [])
        if not isinstance(chain, list):
            chain = []  # B-031: provenance_chain mal tipado — string/dict produce len() incorrecto
        if provenance.get("chain_status") == "BROKEN" or not chain:
            epc_factor = Fraction(1, 10)  # P0: consistencia con _EPC_FACTOR_TABLE
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
            # B-067: tipo desconocido → peso de la peor clase conocida (0.15),
            # no 0.20 — coherente con Artifact.profile. Un tipo inventado no
            # puede pesar más que log_entry.
            weight  = profile.base_weight if profile else 0.15
            _filtered = {
                k: v for k, v in a.items()
                if k in {"source_tool", "evidence_type", "raw_score",
                         "description", "metadata", "provenance_chain",
                         "base_trust", "timestamp"}
            }
            _filtered.setdefault("description", str(a.get("content", ""))[:200] or "legacy_artifact")
            _caie_art    = _CaieArtifact(**_filtered)
            spoofability = _caie_art.effective_spoofability
        except Exception as _spoof_exc:
            logging.warning(
                "CAIE spoofability failed for artifact %s, using conservative fallback 0.50: %s",
                a.get("artifact_id", "unknown"), _spoof_exc
            )
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
    # M2-2: bandera de señal por artefacto (valor evidencial > umbral).
    # effective_trusts es paralelo a artifacts (mismo orden, una entrada por
    # artefacto); adjusted_score ya pasó el Finite Math Shield y el redondeo
    # determinista.
    _signal_flags = [et["adjusted_score"] > _M2_MIN_SIGNAL_ADJ for et in effective_trusts]
    _n_signal     = sum(_signal_flags)

    # M2-2: diversity_bonus cuenta solo tipos CON señal — un artefacto con
    # raw_score=0 no aporta información y no puede comprar el bono de
    # diversidad (cruzaba bordes de banda: NOISE→UNKNOWN con un doc vacío).
    unique_types    = len({
        et["evidence_type"] for et, _sig in zip(effective_trusts, _signal_flags) if _sig
    })
    diversity_bonus = _dround(
        min(0.2, max(0, unique_types - 1) * 0.05), _DETERMINISTIC_INTERNAL_PREC
    )

    # -----------------------------------------------------------------------
    # R4-3: saturación por DOMINIO DE RECOLECCIÓN — arquitectura de DOS etapas
    # con la etapa 1 BIT-EXACTA al esquema legacy M2-1:
    #
    #   Etapa 1 (SIN CAMBIOS — abajo): mejor-prefijo por TIPO (M2-1). Todos
    #   los casos existentes del corpus con <=4 artefactos por sub-banda
    #   producen exactamente el mismo composite que antes de R4-3 — las
    #   corridas comparativas 3-4 probaron que la cabeza NO puede desviarse:
    #   el par CAN-018 (MALICE) / CAN-032 (SUSPICION) tiene FORMA idéntica
    #   (3× memory_process + 1 ip_geolocation) y solo el score calibrado de
    #   contenido los separa; y CAN-029 (MALICE) depende de que lsass_session
    #   NO se agrupe con los memory_process del mismo dominio en la cabeza.
    #
    #   Etapa 2 (R4-3): decay DE COLA por sub-banda de recolección
    #   (docs/TAXA_DOMINIOS_RECOLECCION.md, taxonomía v2). Dentro de cada
    #   sub-banda se rankea por score post-etapa-1; las posiciones 1-4 NO se
    #   tocan (dos-fuentes + margen legacy) y de la 5ta en adelante el peso
    #   decae geométrico r^(pos-4). Acá muere el drowning medido en
    #   docs/BASELINE_TRIPLE_CASTIGO.md: legacy crecía N/2 sin límite
    #   (+0.0016/log constante — 95 logs irrelevantes movían BREAK-014 de
    #   SUSPICION 0.2324 a MALICE 0.3867 y 50 logs de raw 0.05 SOLOS
    #   fabricaban SUSPICION), la cola geométrica converge.
    #
    #   EXENTOS de la etapa 2: D5-media/hard (costo por-artefacto: 10
    #   binarios SON 10 actos de fabricación independientes — FLAREON) y los
    #   artefactos sin evidence_type (schema narrativo SRL: saturarlos
    #   aplastaba 14 casos MALICE en la corrida 3; su redundancia la maneja
    #   la vía semiótica).
    #
    #   Monotonicidad (invariante M2-1): la etapa 1 conserva su propia
    #   garantía; la etapa 2 usa pesos fijos decrecientes por posición sobre
    #   un ranking ordenado — verificada sobre la grilla de los pins M2 y los
    #   tests R4-3 (agregar evidencia incriminatoria nunca baja el score).
    # -----------------------------------------------------------------------
    # M2-1 (Red-Team Round 2): redundancy decay evaluado en el MEJOR PREFIJO
    # por tipo, no sobre el conjunto completo a ciegas. El esquema legacy
    # penalizaba a TODOS los artefactos de un tipo con (count-1)·0.15:
    # agregar un artefacto incriminatorio débil del mismo tipo SUBÍA
    # retroactivamente la penalización de los incumbentes fuertes y BAJABA el
    # score (violación de monotonicidad positiva — 29/30 celdas de la matriz
    # z_score×prior_trust, Δ hasta -0.093).
    #
    # Ahora, por tipo: se ordenan los artefactos por adjusted_score
    # descendente (empates: orden de inserción, sort estable — determinista)
    # y se evalúa la MISMA fórmula legacy sobre cada prefijo top-k
    # (penalty(k) = min(0.5, (k-1)·0.15) aplicada a los k del prefijo). Se
    # queda el prefijo cuya contribución Noisy-OR del grupo es máxima. Un
    # duplicado que solo resta información no puede debilitar la evidencia
    # que duplica — queda fuera del prefijo elegido y contribuye 0.
    #
    # Propiedades: (a) monotonicidad — agregar un artefacto solo agranda el
    # conjunto de prefijos candidatos, así que la contribución del grupo (y
    # el composite) nunca baja; (b) compatibilidad — cuando el conjunto
    # completo ya era el óptimo (todos los casos regulares del corpus), el
    # prefijo elegido es el conjunto completo y el resultado es bit a bit
    # idéntico al legacy.
    _by_type: dict[str, list[int]] = {}
    for _idx, et in enumerate(effective_trusts):
        _by_type.setdefault(et["evidence_type"], []).append(_idx)

    # Round 4 (boundary/perf): el loop legacy evaluaba TODOS los prefijos k=1..n
    # -> O(n^2) por tipo (un flood de un solo tipo tardaba segundos). Los
    # prefijos candidatos se reducen a {1,2,3,4,n} SIN cambiar el resultado (bit
    # a bit idéntico, verificado sobre 20k casos aleatorios):
    #   penalty(k) = min(0.5, (k-1)*0.15) es CONSTANTE (=0.5) para k>=5, así que
    #   entre los prefijos de k>=5 el factor Noisy-OR es no-creciente en k
    #   (cada artefacto extra multiplica por (1 - adj) <= 1) -> el mínimo en ese
    #   régimen está SIEMPRE en k=n. Solo k=1,2,3,4 (donde penalty varía) y k=n
    #   pueden ganar. Se evalúan en orden ascendente con `<=` para conservar el
    #   desempate legacy (prefijo más grande gana). Costo: O(n) por tipo.
    def _prefix_factor(_ranked, _k):
        _pen = min(0.5, (_k - 1) * 0.15)
        _adjs = [
            _dround(effective_trusts[_i]["adjusted_score"] * (1 - _pen),
                    _DETERMINISTIC_OUTPUT_PREC)
            for _i in _ranked[:_k]
        ]
        return math.prod(max(0.0, 1.0 - _s) for _s in _adjs), _adjs

    adj_scores = [0.0] * len(effective_trusts)
    for _idxs in _by_type.values():
        _ranked = sorted(_idxs, key=lambda i: -effective_trusts[i]["adjusted_score"])
        _n = len(_ranked)
        _candidates = list(range(1, _n + 1)) if _n <= 4 else [1, 2, 3, 4, _n]
        _best_factor = 1.0   # factor Noisy-OR del grupo: menor = más señal
        _best_k      = 0
        _best_adjs: list[float] = []
        for _k in _candidates:
            _factor, _adjs = _prefix_factor(_ranked, _k)
            # <= : ante empate se prefiere el prefijo MÁS GRANDE (máxima
            # atribución de evidencia) — determinista.
            if _factor <= _best_factor:
                _best_factor, _best_k, _best_adjs = _factor, _k, _adjs
        for _pos, _i in enumerate(_ranked):
            adj_scores[_i] = _best_adjs[_pos] if _pos < _best_k else 0.0


    try:
        from vigia.tools.caie import (
            classify_domain as _classify_domain,
            classify_domain_subband as _classify_subband,
        )
    except Exception:
        def _classify_domain(_t):  # mirror mínimo — fuente de verdad es caie
            return f"UNKNOWN:{_t}"
        def _classify_subband(_t):
            return (f"UNKNOWN:{_t}", "UNKNOWN")

    # r de cola por sub-banda: replicabilidad del canal (CR-002/CR-004).
    _R43_TAIL_START = 4          # posiciones 1-4 intactas (cabeza legacy)
    _R43_SUBBAND_DECAY = {
        "D1a": 0.5, "D1b": 0.7, "D2": 0.7, "D3": 0.7, "D4": 0.7,
        "D5-soft": 0.5, "D0": 0.5,
    }
    _R43_EXEMPT_BANDS = frozenset({"D5-media", "D5-hard"})

    _by_domain: dict[str, list[int]] = {}
    _by_subband: dict[tuple, list[int]] = {}
    for _idx, et in enumerate(effective_trusts):
        _et_str = str(et["evidence_type"])
        _by_domain.setdefault(_classify_domain(_et_str), []).append(_idx)
        _by_subband.setdefault(_classify_subband(_et_str), []).append(_idx)

    r43_scores = list(adj_scores)
    for (_dom, _band), _sb_idxs in _by_subband.items():
        if _band in _R43_EXEMPT_BANDS or _band == "UNKNOWN" \
                or _dom.startswith("UNKNOWN:"):
            continue
        if len(_sb_idxs) <= _R43_TAIL_START:
            continue  # sin cola: bit-exacto legacy
        _r = _R43_SUBBAND_DECAY.get(_band, 0.7)
        _dranked = sorted(_sb_idxs, key=lambda i: -adj_scores[i])
        for _pos, _i in enumerate(_dranked):
            if _pos < _R43_TAIL_START:
                continue
            r43_scores[_i] = _dround(
                adj_scores[_i] * (_r ** (_pos - _R43_TAIL_START + 1)),
                _DETERMINISTIC_OUTPUT_PREC,
            )

    # Score por dominio (Noisy-OR intra-dominio sobre los pesos saturados) —
    # trazabilidad Daubert y entrada del gate B-068 por dominios.
    r43_domain_scores = {
        _dom: _dround(
            1.0 - math.prod(max(0.0, 1.0 - r43_scores[_i]) for _i in _idxs),
            _DETERMINISTIC_OUTPUT_PREC,
        )
        for _dom, _idxs in sorted(_by_domain.items())
    }

    if not r43_scores:
        composite = 0.0
    else:
        raw_composite = _dround(
            1.0 - math.prod([max(0.0, 1.0 - s) for s in r43_scores]),
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
        # M3 (docs/FOSSIL_HUNT_20260711_PASS2.md §2): scorer<->CAIE realignment.
        # These three are generated by CAIE v2.0 but weighed ZERO here, so the
        # Daubert-correct paths were score-inert while FALSE_FLAG_PATTERN (the
        # fossil path) carried the weight — an inverted incentive:
        #   FALSE_FLAG_ATTRIBUTION_MISMATCH — confirmed false flag (H-02 Case C
        #     and Rule 1b): real attack + planted attribution markers.
        #   LOG_VS_MEMORY — logs assert network activity, memory shows none;
        #     already _STRUCTURAL_MALICE in CAIE's own evaluate(): the two
        #     modes disagreed on the same fracture.
        #   TIMESTAMP_PRECISION_ANOMALY — anti-forensic tool signature
        #     (sub-second truncation), spoofability 0.05.
        "FALSE_FLAG_ATTRIBUTION_MISMATCH",
        "LOG_VS_MEMORY",
        "TIMESTAMP_PRECISION_ANOMALY",
        # Canonical TTP detectors (2026-07-12, docs/CASE_RECOVERY_20260712.md):
        # structured-metadata detectors for masquerade / defense-evasion /
        # injection IoIs that previously produced no fracture, leaving real
        # multi-domain MALICE cases stalled at composite ~0.30. Each maps to a
        # named MITRE TTP; all verified FP-safe corpus-wide (fire only on
        # genuine targets, break zero currently-correct verdicts).
        "PROCESS_MASQUERADE",
        "DEFENSE_EVASION_ARTIFACT",
        "PROCESS_INJECTION_ANTIFORENSIC",
        # Fabricated-corroboration detector (2026-07-12): a subject's claimed
        # corroboration refuted by the executed record check. DOCUMENT_FORGERY
        # (already present above) also gained a mass date-regex-substitution
        # trigger — same type, no new entry needed.
        "CLAIM_VS_RECORD_FABRICATION",
        # M2 (docs/M2_DISCRIMINATORS_DESIGN_20260711.md): class-correct
        # replacements for the pre-M2 FALSE_FLAG_PATTERN catch-all, at weight
        # parity (severity 0.8) so genuine linguistic-attribution and social-
        # engineering signal keeps its score while the sealed theory becomes
        # the one the case actually supports.
        "LINGUISTIC_ATTRIBUTION_SIGNAL",
        "SOCIAL_ENGINEERING_PATTERN",
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
        # M3: ATTRIBUTION_INCONSISTENCY removed — phantom type, never generated
        # by CAIE v2.0 (same family as the P4 phantom cleanup this block
        # documents). Parity is now enforced by
        # tests/test_m3_scorer_caie_parity.py against the live CAIE catalogue.
    }

    def _sev_float(raw, default: float = 0.5) -> float:
        """
        B-057 FIX: las fracturas del CAIE VIVO llevan severity como
        decimal.Decimal (aritmética interna de caie.py); las del fallback
        JSON llevan float. `Decimal * float` crudo → TypeError — crasheaba
        _vigia_score entero en cuanto CAIE vivo emitía una fractura
        maliciosa (reproducido con VIGIA-BREAK-016). Misma familia de
        frontera de tipos que B-024/B-026: coerción + Finite Math Shield
        en el boundary, nunca aritmética mixta.
        """
        try:
            v = float(raw)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(v):
            return default
        return max(0.0, min(1.0, v))

    # Invariant-4 hardening (docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-E):
    # the boost/penalty accumulators were plain float `+=`, which makes the
    # accumulated value depend on fracture EMISSION ORDER. A constructed
    # reproduction through the real engine flips the sealed verdict
    # (UNKNOWN<->SUSPICION at a 5e-5 rounding cliff) from emission order
    # alone, so any CAIE refactor that reorders rule evaluation could change
    # sealed verdicts. Fix: each term keeps the SAME float value as before
    # (a single multiplication has no ordering), but terms are lifted exactly
    # into Fraction and summed exactly — exact addition is associative and
    # commutative, so the sum no longer depends on emission order. The result
    # converts back to float once, at the cap. For 0-2 terms (the entire
    # corpus today) this is bit-identical to the old accumulation; the
    # acceptance gate (scripts/experiments/fraction_gate.py) verifies
    # bit-identity corpus-wide on every change to this block.
    _boost_terms   = []
    _penalty_terms = []
    for f in fractures:
        sev = _sev_float(f.get("severity", 0.5))
        ft  = f.get("fracture_type", "")
        if ft in MALICIOUS_FRACTURE_TYPES:
            _boost_terms.append(Fraction(sev * 0.45))
        elif ft in CREDIBILITY_REDUCING_TYPES:
            _penalty_terms.append(Fraction(sev * 0.25))

    fracture_malice_boost        = float(min(Fraction(1, 2),  sum(_boost_terms,   Fraction(0))))
    fracture_credibility_penalty = float(min(Fraction(7, 20), sum(_penalty_terms, Fraction(0))))

    # STATISTICAL_UNIFORMITY from the temporal engine (not CAIE) — valid signal.
    # Same exact-summation treatment; note the pre-existing semantics are
    # preserved: the CAIE-fracture sum is capped FIRST, then SU terms add on
    # top of the capped value, then the cap applies again.
    _su_terms = [
        Fraction(_sev_float(v.get("severity", 0), 0.0) * 0.35)
        for v in violations
        if v.get("type") == "STATISTICAL_UNIFORMITY"
    ]
    fracture_malice_boost = float(
        min(Fraction(1, 2), Fraction(fracture_malice_boost) + sum(_su_terms, Fraction(0)))
    )

    # Hard gate: physical law violation — unconditional MALICE override.
    # Severity is read through _sev_float (the same coercion shield every other
    # severity consumer uses): this is the highest-authority branch in the
    # scorer (unconditional MALICE), yet it read raw examiner JSON directly, so
    # a string/None severity ("high", null) raised TypeError on the `>= 0.9`
    # comparison and crashed the whole scorer. Non-numeric -> 0.0 (default),
    # which does NOT fire the gate — a malformed severity must not fabricate an
    # unconditional MALICE. Ref: docs/SCORER_ARCHITECTURE_DOSSIER_20260712.md D-E.
    hard_temporal = any(
        v.get("type") == "EFFECT_BEFORE_CAUSE"
        and _sev_float(v.get("severity", 0), 0.0) >= 0.9
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
    #   SUSPICION : > 0.10 (structural signal without certainty threshold)
    #   UNKNOWN   : > 0.08 (weak anomaly — requires human analysis)
    #   NOISE     : <= 0.08 (no relevant forensic signal)
    #
    # B-076 (Fase 2, 2026-07-05): SUSPICION 0.18 → 0.10, calibrado con el
    # dataset de ground truth de 198 casos (data/calibration_ladder_dataset_
    # 20260705.json). Los 10 casos etiquetados SUSPICION que caían en la
    # banda [0.101, 0.148] emitían UNKNOWN; el único caso correcto en la
    # banda [0.10, 0.18) era exp=UNKNOWN (score 0.167 — sigue correcto como
    # SUSPICION bajo el comparador, que acepta cualquier veredicto para
    # expected=UNKNOWN). Gate comparativo: +10 aciertos, 0 regresiones
    # (docs/FASE2_DATASET_CALIBRACION.md, experimento E1).
    # -----------------------------------------------------------------------
    raw_intent_score = _dround(
        max(0.0, min(0.99, composite + fracture_malice_boost - fracture_credibility_penalty)),
        _DETERMINISTIC_OUTPUT_PREC,
    )

    # M2-2: el soporte estructural cuenta artefactos CON señal, no la
    # cardinalidad de la lista — un README vacío no "corrobora". n=0 → la
    # propia fórmula log(1+n)/log(5) da 0.
    n_artifacts   = _n_signal
    support_score = (
        _SUPPORT_SCORE_TABLE.get(n_artifacts, Fraction(1, 1))  # P0: Fraction lookup, no math.log()
        if n_artifacts > 0 else Fraction(0, 1)
    )
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
        # P2-D FIX (Tanda B, PR-B2): antes esta rama emitía NOISE con
        # confidence = 1 - mean_effective (~0.99) — un veredicto "analizado y
        # limpio" con 99% de confianza DERIVADA DE LA AUSENCIA de confianza.
        # Una cadena de custodia colapsada significa "no puedo confiar en
        # nada de esta evidencia": eso es ABSTAIN ("no puedo determinar"),
        # nunca benignidad confiada. Misma familia de falso-negativo que
        # P0-A. El propio reason lo decía: "inadmissible under Daubert" — un
        # veredicto inadmisible no puede presentarse como NOISE confiado.
        verdict    = "ABSTAIN"
        confidence = 0.0
        reason     = ("PROVENANCE COLLAPSED: effective trust < 0.01 sin "
                      "fracturas — cadena de custodia insuficiente para "
                      "afirmar benignidad. Inadmisible bajo Daubert; requiere "
                      "re-adquisición de la evidencia.")
    elif mean_effective < 0.15 and fractures:
        verdict    = "SUSPICION"
        confidence = _dround(min(0.75, fracture_malice_boost + 0.3), 2)
        reason     = f"Broken chain of custody + {len(fractures)} active fracture(s) — deliberate manipulation"
    elif final_score > Fraction(33, 100):
        # Corroboration gate: MALICE requires convergence of heterogeneous evidence.
        # Daubert principle: a single class of technical evidence, regardless of
        # its raw_score, does not justify an inference of malicious intent.
        # Requirement: n_artifacts >= 4 OR n_unique_types >= 3.
        #
        # B-068 (FP VIGIA-NGDC-003), refactor B-070: el gate cuenta solo
        # evidencia DEVICE. Las clases NARRATIVE ya se apartaron arriba (no
        # están en `artifacts`); acá se excluyen además las CONTEXTUAL (OSINT,
        # metadata de adquisición): device-adyacentes, pueden portar señal en
        # el composite pero NO son fuentes independientes de dispositivo, así
        # que no corroboran ("two independent sources" = clases DEVICE). El rol
        # se lee del registro único (vigia.tools.caie.evidence_role), no de una
        # lista local. NGDC-003 (intención disputada) cruzaba el gate contando
        # documentación de escenario como corroboración.
        _tech_arts = [
            a for a, _sig in zip(artifacts, _signal_flags)
            # M2-2: sin señal (adjusted_score <= _M2_MIN_SIGNAL_ADJ) no hay
            # corroboración — el gate contaba cardinalidad sin consultar
            # la señal y un manual.pdf vacío de tipo nuevo lo abría
            # (SUSPICION → MALICE con raw_score=0).
            if _sig
            and _evidence_role(str(a.get("evidence_type", ""))) == _ROLE_DEVICE
            # FASE 2: semantic_role=contextual no corrobora MALICE (mismo
            # trato que el rol contextual de B-070); los exculpatory ya no
            # están en `artifacts` (apartados arriba, semántica V1).
            and _semantic_role(a) != "contextual"
        ]
        # R4-3: el gate cuenta DOMINIOS DE RECOLECCIÓN activos, no tipos ni
        # artefactos. "Two independent sources" (Daubert) hecho literal: dos
        # canales cuya fabricación exige actos independientes del atacante.
        # El esquema previo (n_artifacts >= 4 OR n_types >= 3) era comprable
        # con volumen de UN solo canal: 4 logs, o 3 tipos de metadata del
        # mismo filesystem. assurance_context (D0) no corrobora (no es
        # evidencia de dispositivo); los UNKNOWN:<tipo> cuentan cada uno como
        # su propio dominio (conservador con evidencia genuinamente nueva).
        # R4-3 gate v2 — tres ramas, cada una con doctrina propia (la corrida
        # comparativa 1 mostró que "n_domains>=2" a secas es a la vez más
        # estricto Y más laxo que el gate viejo: bloqueaba MALICE legítimos
        # de un canal duro y abría FPs de dos canales con poca masa):
        #   (1) CROSS-DOMAIN CON MASA: >=2 dominios Y la masa mínima del gate
        #       legado (n_arts>=4 o n_types>=3) — dos canales independientes
        #       no eximen de tener evidencia suficiente (REAL-005/case_002
        #       eran FPs de 2 dominios con 2-3 artefactos).
        #   (2) MASA DURA: >=3 tipos duros O >=4 artefactos duros
        #       (spoofability <=0.30) — fabricar objetos de memoria/MFT exige
        #       compromiso live/Ring-0 real por pieza; nadie "loopea" EPROCESS
        #       falsos dentro de un dump genuino (VIGIA-CAN-029: 3
        #       memory_process + 1 lsass_session = 4 duros de un canal).
        #   (3) COSTO POR-ARTEFACTO: >=4 artefactos D5-hard/media — cada
        #       binario/documento es un acto de fabricación independiente
        #       (FLAREON); el volumen ahí SÍ es corroboración.
        # Un solo canal blando (N logs, N marcadores) no abre ninguna rama.
        try:
            from vigia.tools.caie import EVIDENCE_PROFILES as _EPROF
            def _spoof(_t):
                _p = _EPROF.get(_t)
                return _p.spoofability if _p is not None else 1.0
        except Exception:
            _HARD_TYPES = frozenset({
                "memory_process", "lsass_session", "kernel_structure",
                "usn_journal", "usn_journal_gap", "mft_entry", "prefetch",
                "timestamp_precision", "cryptographic_hash", "hmac_audit_log",
                "digital_signature", "hardware_serial", "TPM_attestation",
            })
            def _spoof(_t):
                return 0.1 if _t in _HARD_TYPES else 1.0

        _gate_types = set()
        _hard_types = set()
        _n_hard_arts = 0
        _n_percost = 0
        _n_gate_arts = 0
        _dom_arts: dict = {}     # dominio -> n artefactos elegibles
        _dom_min_spoof: dict = {}  # dominio -> spoofability mínima vista
        for a, _sig in zip(artifacts, _signal_flags):
            if not _sig:
                continue
            _et_str = str(a.get("evidence_type", ""))
            if _evidence_role(_et_str) != _ROLE_DEVICE:
                continue
            if _semantic_role(a) == "contextual":
                continue
            _dom, _band = _classify_subband(_et_str)
            if _dom == "assurance_context":
                continue
            _n_gate_arts += 1
            _dom_arts[_dom] = _dom_arts.get(_dom, 0) + 1
            _sp = _spoof(_et_str)
            if _sp < _dom_min_spoof.get(_dom, 2.0):
                _dom_min_spoof[_dom] = _sp
            _gate_types.add(_et_str)
            if _sp <= 0.30:
                _hard_types.add(_et_str)
                _n_hard_arts += 1
            if _band in ("D5-hard", "D5-media"):
                _n_percost += 1

        _gate_domains = set(_dom_arts)
        _n_domains = len(_gate_domains)
        _branch = None
        if _n_domains >= 2 and (_n_gate_arts >= 4 or len(_gate_types) >= 3):
            _branch = f"cross-domain ({_n_domains} domains, {_n_gate_arts} artifacts)"
        elif len(_hard_types) >= 3 or _n_hard_arts >= 4:
            _branch = (f"hard-mass ({len(_hard_types)} hard type(s), "
                       f"{_n_hard_arts} hard artifact(s) w/ spoofability<=0.30)")
        elif _n_percost >= 4:
            _branch = f"per-artifact-cost ({_n_percost} D5-hard/media artifacts)"

        if _branch:
            verdict = "MALICE"
            reason  = (
                f"Intent score {final_score:.4f} exceeds MALICE threshold — "
                f"corroboration branch: {_branch} (B-068 gate, R4-3 v2)"
            )
        else:
            verdict = "SUSPICION"
            reason  = (
                f"Intent score {final_score:.4f} exceeds MALICE threshold but "
                f"no corroboration branch opens ({_n_domains} domain(s), "
                f"{len(_hard_types)}/{_n_hard_arts} hard class(es)/artifact(s), "
                f"{_n_percost} per-cost "
                f"artifact(s)) — volume within a single soft collection "
                f"domain does not corroborate MALICE (B-068 gate, R4-3 v2)"
            )
        confidence = _dround(min(0.95, final_score * 2.0), 2)
    elif final_score > Fraction(10, 100):  # B-076: 18/100 → 10/100 (ground truth)
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
        # R4-3: trazabilidad de la saturación por dominio (Daubert).
        "r43_domain_scores":            r43_domain_scores,
        "r43_active_domains":           sorted(
            _dom for _dom, _s in r43_domain_scores.items()
            if _s > _M2_MIN_SIGNAL_ADJ and _dom != "assurance_context"
        ),
        "fracture_malice_boost":        _dround(fracture_malice_boost, _DETERMINISTIC_OUTPUT_PREC),
        "fracture_credibility_penalty": _dround(fracture_credibility_penalty, _DETERMINISTIC_OUTPUT_PREC),
        "diversity_bonus":              _dround(diversity_bonus, _DETERMINISTIC_OUTPUT_PREC),
        "hard_temporal_gate":           hard_temporal,
        "effective_trusts":             effective_trusts,
        "temporal_violations":          len(violations),
        "caie_fractures":               len(fractures),
        # B-094: detalles de fractura (tipo/severidad/interpretación) para que
        # el path motor pueda SURFACEARLAS en el bundle/narrativa. La fractura
        # ya movió el veredicto (fracture_malice_boost); exponerla es requisito
        # Daubert — un veredicto no-NOISE por fractura no puede quedar sin
        # explicación en la narrativa sellada.
        "caie_fracture_details":        list(fractures),
        "caie_fractures_source":        _caie_source,
        "peirce_chain":                 case.get("peirce_chain", {}),
        "expected_verdict":             case.get("expected_verdict", "UNKNOWN"),
        # FASE 2: artefactos exculpatorios apartados (semántica V1) + los
        # retenidos por el filtro Eco (D1) — trazabilidad Daubert de qué
        # refutaciones se aceptaron y cuáles se rechazaron y por qué.
        "refutation_context": {
            "set_aside": _exculpatory_set_aside,
            "eco_retained": _exculpatory_eco_retained,
        },
        # B-070: artefactos NARRATIVE apartados del scoring — retenidos para la
        # narrativa del reporte, no contribuyen al veredicto ni a la confianza.
        "narrative_context":            [
            {"evidence_type": a.get("evidence_type"),
             "artifact_id": a.get("artifact_id"),
             "raw_score": a.get("raw_score")}
            for a in _narrative_artifacts
        ],
    }

    # -----------------------------------------------------------------------
    # Intake-abstain gate (2026-07-12, docs/CASE_RECOVERY_20260712.md)
    #
    # A NOISE verdict claims "analyzed and found clean". That claim is
    # unsupportable when the evidence itself declares that analysis did not
    # occur: an intake-only record whose content was never extracted, or a
    # device image from which no user evidence was recovered. Certifying such
    # a record NOISE is a false clean bill of health; the honest verdict is
    # ABSTAIN ("insufficient analysis to assert benignity" — VIGÍA doctrine:
    # ABSTAIN documents the gap rather than guessing).
    #
    # Keys ONLY on examiner-declared acquisition/analysis-state metadata
    # (status/analysis_status extraction markers, user_data/content/partition
    # == False), never on annotation fields (expected_verdict,
    # confidence_expected, abstention_risk). Fires only when the verdict is
    # already NOISE, so it can never soften a SUSPICION/MALICE finding.
    # Verified FP-safe corpus-wide: fires on exactly the intake/firmware-only
    # records, breaks zero currently-correct verdicts (benign source-code and
    # analyzed phone dumps carry none of these markers).
    # -----------------------------------------------------------------------
    if base_result["verdict"] == "NOISE":
        _analysis_incomplete = any(
            str((a.get("metadata") or {}).get("status", "")).upper().startswith("INTAKE_ONLY")
            or "EXTRACTION PENDING" in str((a.get("metadata") or {}).get("status", "")).upper()
            or str((a.get("metadata") or {}).get("analysis_status", "")).upper().startswith("PENDING")
            or (a.get("metadata") or {}).get("user_data_found") is False
            or (a.get("metadata") or {}).get("user_content_found") is False
            or (a.get("metadata") or {}).get("user_partition") is False
            for a in artifacts
        )
        if _analysis_incomplete:
            verdict = "ABSTAIN"
            confidence = 0.0
            base_result["verdict"] = "ABSTAIN"
            base_result["confidence"] = 0.0
            base_result["reason"] = (
                "INTAKE / INCOMPLETE ANALYSIS: evidence acquired but its content "
                "was not extracted/analyzed, or no user evidence was recovered — "
                "insufficient analysis to assert benignity. NOISE would overclaim "
                "a clean finding; ABSTAIN documents the gap (re-acquisition / full "
                "extraction required before a benignity verdict)."
            )

    base_result["quadripartite_state"] = _apply_quadripartite(
        verdict=verdict,
        confidence=confidence,
        stability=mean_effective,
        fractures=fractures,
    )

    return base_result
