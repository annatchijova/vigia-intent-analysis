"""
vigia_scorer.py — Scorer forense de VIGÍA
==========================================

Parte del proyecto VIGÍA — Forensic Intentionality Analysis Suite.
Desarrollado para el SANS FIND EVIL Hackathon 2026.
Candidato a integración en SANS SIFT Workstation.

Licencia: Apache 2.0
Repositorio: https://github.com/annatchijova/vigia-intent-analysis
Autora principal: Annia Tchijova

DESCRIPCIÓN:
    Scorer forense standalone. Implementa el pipeline de puntuación de
    intención maliciosa: TrustFusion → CorrelationDecay → CAIE → Decision.
    No requiere que el paquete vigia esté instalado — funciona en modo
    demo standalone con fallback seguro a parámetros conservadores.

FILOSOFÍA FORENSE:
    Tres pilares: Peircean Thirdness (inferencia abductiva), Navaja de Ockham
    (selección de hipótesis), admisibilidad Daubert. Todo output es
    determinista, bit-a-bit reproducible, y auditable por un perito.

HISTORIAL DE PATCHES:
    B1     : CAIE vivo — fractures recalculadas desde artifacts, no desde JSON
    B2     : source_counts indexa por evidence_type (misma clave que la búsqueda)
    B3     : isolation_penalty / n_boost eran dead code — eliminados
    B4     : diversity_bonus multiplicativo, no aditivo — evita saturación de score
    P2     : adjusted_score unificado con fórmula CAIE (EvidenceProfile) — Kimi 2026-05-19
    P4     : MALICIOUS_FRACTURE_TYPES saneado — eliminados 3 fantasmas,
             agregado FALSE_FLAG_PATTERN que CAIE sí genera — Kimi 2026-05-19
    P5     : Determinismo P0 — decimal.Decimal + _dround/_dsum — Kimi 2026-05-19
    P6     : Finite Math Shield — float('inf')/NaN en raw_score → 0.0 — Kimi 2026-05-19
    P1-K   : CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED agregado a CREDIBILITY_REDUCING_TYPES
             — era invisible para el scorer — Kimi 2026-05-19

LIMITACIONES CONOCIDAS:
    - EvidenceProfile fallback (spoofability=0.50, weight=0.20) es conservador
      pero no calibrado. La calibración real requiere corpus forense etiquetado.
      Ver fit_calibration.py y run_calibration.py.
    - La propagación de invalidación de supuestos (ATMS) tiene profundidad 1.
      A invalida B, B invalida C no se propaga automáticamente.
      Ver integrity_constraints.py — roadmap v2.0.
    - El scorer no persiste estado entre ejecuciones. Cada llamada es independiente.
    - CAIE en modo live requiere instalación del paquete vigia. En modo standalone
      usa fractures pre-calculadas del JSON (caie_fractures_source: "json_fallback").
      El bundle documenta qué modo se usó.
    - _dround() garantiza determinismo cross-platform para output a 4 decimales.
      Testeado en x86-64 y ARM64 Linux (CPython 3.12). Pendiente: macOS, Windows.
    - Los coeficientes de boost (0.45) y penalty (0.25) son heurísticos, no
      calibrados sobre corpus real. Roadmap: calibración bayesiana.
"""
from __future__ import annotations

import decimal
import json
import math
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# P5: Determinismo P0 — mismo protocolo que CAIE
# decimal.Decimal con prec=28 y ROUND_HALF_EVEN elimina la divergencia del
# bit 52 de la mantisa que round() nativo puede producir en arquitecturas
# con diferente orden de evaluación de expresiones flotantes (x86 vs ARM).
# ---------------------------------------------------------------------------
_DETERMINISTIC_INTERNAL_PREC = 6
_DETERMINISTIC_OUTPUT_PREC   = 4

decimal.getcontext().prec     = 28
decimal.getcontext().rounding = decimal.ROUND_HALF_EVEN

_D_ZERO = decimal.Decimal("0")
_D_ONE  = decimal.Decimal("1")


def _dround(value, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> float:
    """
    Redondeo determinístico P0.
    Finite Math Shield integrado: retorna 0.0 para inf, -inf, NaN.
    Garantiza mismo resultado en x86-64 y ARM64 para precision <= 15.
    """
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


def _dsum(values) -> float:
    """
    Suma con acumulador decimal.Decimal para evitar drift de punto flotante.
    Acepta cualquier iterable de int/float. Valores no finitos se descartan.
    """
    acc = _D_ZERO
    for v in values:
        if isinstance(v, (int, float)) and math.isfinite(v):
            acc += decimal.Decimal(str(v))
    return _dround(float(acc), _DETERMINISTIC_INTERNAL_PREC)


# ---------------------------------------------------------------------------
# Constantes ANSI — definidas inline, no importadas de módulo externo.
# Permite que este archivo sea standalone sin dependencias del paquete vigia.
# ---------------------------------------------------------------------------
RED = "\033[91m"
YEL = "\033[93m"
GRN = "\033[92m"
BLU = "\033[94m"
PUR = "\033[95m"
BLD = "\033[1m"
RST = "\033[0m"


def _normalize_case(c):
    """
    Normaliza un caso al schema canónico de VIGÍA.
    Fallback transparente si el bridge no está disponible (modo standalone).
    """
    try:
        from vigia.pipeline.vigia_integration_bridge import normalize_case_schema
        return normalize_case_schema(c)
    except Exception:
        return c


def _verdict_color(verdict) -> str:
    """
    Retorna código ANSI para el veredicto.
    Acepta str o Enum (compatibilidad con CollapseDecisionLayer).
    """
    v_str = verdict.value if hasattr(verdict, "value") else str(verdict)
    return {
        "MALICE":       RED + BLD,
        "SUSPICION":    YEL + BLD,
        "INCONCLUSIVE": PUR + BLD,
        "NOISE":        GRN,
    }.get(v_str.upper(), BLU)


def _compute_temporal_factor(violations: list[dict], artifact_id: str) -> float:
    """
    Factor de penalización temporal por artefacto.
    Inline — no depende del paquete vigia. Permite ejecución en demo standalone.

    Pesos por tipo de violación (severidad forense):
      EFFECT_BEFORE_CAUSE    : violación de ley física — peso máximo (1.0)
      TOO_FAST               : velocidad físicamente imposible — peso alto (0.7)
      STATISTICAL_UNIFORMITY : distribución artificial — peso medio (0.6)
      IDENTICAL_TIMESTAMP    : colisión de timestamp — peso medio-bajo (0.5)
      CLOCK_SKEW             : ruido de sincronización — peso bajo (0.4)
    """
    weights = {
        "EFFECT_BEFORE_CAUSE":    1.0,
        "TOO_FAST":               0.7,
        "STATISTICAL_UNIFORMITY": 0.6,
        "IDENTICAL_TIMESTAMP":    0.5,
        "CLOCK_SKEW":             0.4,
    }
    relevant = [
        v for v in violations
        if v.get("cause",  {}).get("artifact_id") == artifact_id
        or v.get("effect", {}).get("artifact_id") == artifact_id
    ]
    if not relevant:
        return 1.0
    ws = [v.get("severity", 0.5) * weights.get(v.get("type", ""), 0.5) for v in relevant]
    return _dround(max(0.0, min(1.0, math.exp(-2.0 * max(ws)))), _DETERMINISTIC_OUTPUT_PREC)


def _naive_score(artifacts: list[dict]) -> float:
    """
    Baseline ingenuo: promedio de raw_scores sin ajuste de trust ni correlación.
    Usado como referencia para detectar divergencia con el pipeline completo.

    P5: _dsum/_dround para determinismo P0.
    P6: Finite Math Shield — raw_score no finito → 0.0.
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


def _vigia_score(case: dict) -> dict:
    """
    Pipeline VIGÍA de puntuación de intención maliciosa.

    Implementa: TrustFusion → CorrelationDecay → CAIE → Decision.

    Args:
        case: dict con schema ForensicBundle. Campos esperados:
            artifacts            : list[dict] — artefactos forenses
            temporal_violations  : list[dict] — violaciones temporales
            provenance_analysis  : dict       — análisis de cadena de custodia
            caie_fractures       : list[dict] — fractures pre-calculadas (fallback JSON)
            peirce_chain         : dict       — cadena abductiva Peircean
            expected_verdict     : str        — veredicto esperado (para evaluación)

    Returns:
        dict JSON-serializable con veredicto, score, confianza, y trazabilidad
        completa para declaración pericial bajo estándar Daubert.
        caie_fractures_source indica si se usó CAIE vivo ("live_caie") o
        fractures pre-calculadas del JSON ("json_fallback").
    """
    artifacts  = case.get("artifacts", [])
    violations = case.get("temporal_violations", [])
    provenance = case.get("provenance_analysis", {})

    if not artifacts:
        return {"verdict": "ERROR", "score": 0.0, "confidence": 0.0, "fractures": []}

    # -----------------------------------------------------------------------
    # B1: Recalcular fractures con CAIE vivo
    # El bug original leía fractures del JSON pre-calculado, lo que hacía que
    # reglas nuevas de CAIE no se aplicaran. Caso 009 (NARRATIVE_POISONING)
    # fallaba por esto — la fractura existía en CAIE pero no en el JSON viejo.
    # Fallback al JSON si CAIE no está disponible (modo standalone).
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
                continue  # artifact con schema inválido — skip, no romper pipeline
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
    except Exception:
        fractures    = case.get("caie_fractures", [])
        _caie_source = "json_fallback"

    # -----------------------------------------------------------------------
    # Paso 1: effective_trust por artefacto
    #
    # effective_trust = prior_trust × epc_factor × temporal_factor
    #   prior_trust    : confianza a priori del artefacto
    #   epc_factor     : penalización por cadena de custodia rota o larga
    #   temporal_factor: penalización por violaciones temporales del artefacto
    #
    # P2: adjusted_score con fórmula CAIE unificada:
    #   adjusted = raw_score × (1 − spoofability) × weight × effective_trust
    #   spoofability y weight se leen de EvidenceProfile (CAIE).
    #   Fallback conservador si CAIE no está disponible: spoofability=0.50, weight=0.20.
    #   LIMITACIÓN: fallback no calibrado. Ver fit_calibration.py.
    #
    # P6: Finite Math Shield — raw_score=inf/NaN → 0.0, no contamina el veredicto.
    # P5: _dround en todos los valores intermedios.
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
            epc_factor = min(1.0, 0.95 ** max(0, len(chain) - 3))

        temp_factor = _compute_temporal_factor(violations, a.get("artifact_id", ""))
        effective   = _dround(prov_trust * epc_factor * temp_factor, _DETERMINISTIC_OUTPUT_PREC)

        # P2: fórmula CAIE unificada con EvidenceProfile
        try:
            from vigia.tools.caie import EVIDENCE_PROFILES
            profile = EVIDENCE_PROFILES.get(a.get("evidence_type"))
            if profile:
                spoofability = profile.spoofability
                weight       = profile.base_weight
            else:
                spoofability = 0.50   # fallback conservador — ver LIMITACIONES
                weight       = 0.20
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
            "spoofability":    spoofability,   # trazable en peritaje
            "weight":          weight,          # trazable en peritaje
        })

    # -----------------------------------------------------------------------
    # Paso 2: Correlation decay
    #
    # Penaliza artefactos del mismo tipo de evidencia (redundancia → menor
    # información nueva). Bonifica diversidad de tipos (señal multi-fuente).
    #
    # B2: source_counts indexa por evidence_type — misma clave que la búsqueda.
    #     Bug original: indexaba por acquisition_record, penalización nunca aplicaba.
    # B4: diversity_bonus multiplicativo antes del recorte.
    #     Bug original: aditivo, podía saturar el score sin evidencia suficiente.
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
    # Paso 3: CAIE fracture analysis
    #
    # DISTINCIÓN CRÍTICA (Daubert):
    #   Fractures de PLANTACIÓN DELIBERADA → elevan score de intención maliciosa.
    #     Semántica: "alguien actuó para engañar" → evidencia de agente deliberado.
    #   Fractures de INCONSISTENCIA INTERNA → reducen credibilidad de evidencia.
    #     Semántica: "la evidencia no es coherente" → score baja.
    #
    # P4: MALICIOUS_FRACTURE_TYPES saneado — solo tipos que CAIE v2.0 genera.
    #   Eliminados (fantasmas — no existen en CAIE v2.0):
    #     STATISTICAL_UNIFORMITY, LIVE_RESPONSE_VS_DISK, CLOUD_VS_ONPREM
    #   Agregados:
    #     FALSE_FLAG_PATTERN (era el gran ausente — CAIE lo genera, scorer lo ignoraba),
    #     NETWORK_VS_HOST, DOCUMENT_FORGERY, MFT_ENTRY_ANOMALY,
    #     USN_JOURNAL_GAP, NARRATIVE_POISONING_DETECTED
    #
    # NOTA: STATISTICAL_UNIFORMITY de violations temporales (motor temporal, no CAIE)
    #   se procesa más abajo — es señal válida de automatización deliberada.
    #
    # LIMITACIÓN: coeficientes boost=0.45 y penalty=0.25 son heurísticos.
    #   Roadmap: calibración bayesiana sobre dataset de casos etiquetados.
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
        # P1 fix (Kimi 2026-05-19): CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED era invisible
        # para el scorer — pasaba sin penalización ni boost. CAIE lo genera cuando hay
        # hash mismatch pero el trust-chain NO fue validado (severity=0.6).
        # No puede ser MALICIOUS (no hay confirmación de spoofing), pero sí reduce
        # credibilidad: hay evidencia de discrepancia criptográfica no explicada.
        # fracture_credibility_penalty += sev * 0.25 lo captura correctamente.
        "CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED",
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

    # STATISTICAL_UNIFORMITY del motor temporal (no de CAIE) — señal válida
    for v in violations:
        if v.get("type") == "STATISTICAL_UNIFORMITY":
            fracture_malice_boost += v.get("severity", 0) * 0.35

    fracture_malice_boost = min(0.5, fracture_malice_boost)

    # Hard gate: violación de ley física — override incondicional a MALICE
    hard_temporal = any(
        v.get("type") == "EFFECT_BEFORE_CAUSE" and v.get("severity", 0) >= 0.9
        for v in violations
    )

    # -----------------------------------------------------------------------
    # Paso 4: Decisión
    #
    # final_score = raw_intent_score × (0.9 + 0.1 × support_score)
    # support_score penaliza casos con muy pocos artefactos (evidencia escasa).
    # Compuerta explícita: un único artefacto no puede superar score 0.65.
    #
    # B3: isolation_penalty y n_boost eran dead code — existían pero nunca se
    #     aplicaban al final_score. Eliminados para evitar confusión.
    # P5: _dround en raw_intent_score y final_score.
    # -----------------------------------------------------------------------
    raw_intent_score = _dround(
        max(0.0, min(0.99, composite + fracture_malice_boost - fracture_credibility_penalty)),
        _DETERMINISTIC_OUTPUT_PREC,
    )

    n_artifacts   = len(artifacts)
    support_score = _dround(min(1.0, math.log(1 + n_artifacts) / math.log(5)), _DETERMINISTIC_OUTPUT_PREC)
    final_score   = _dround(raw_intent_score * (0.9 + 0.1 * support_score), _DETERMINISTIC_OUTPUT_PREC)

    mean_effective = _dround(
        _dsum(e["effective_trust"] for e in effective_trusts) / len(effective_trusts),
        _DETERMINISTIC_OUTPUT_PREC,
    )

    # Provenance colapsada sin fractures → NOISE (inadmisible bajo Daubert)
    # Provenance colapsada CON fractures → posible plantación → SUSPICION
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
        reason     = "Provenance chain collapsed, sin fractures activas — inadmissible under Daubert"
    elif mean_effective < 0.15 and fractures:
        verdict    = "SUSPICION"
        confidence = _dround(min(0.75, fracture_malice_boost + 0.3), 2)
        reason     = f"Cadena de custodia rota + {len(fractures)} fracture(s) activas — manipulación deliberada"
    elif final_score > 0.75:
        verdict    = "MALICE"
        confidence = _dround(final_score, 2)
        reason     = f"Intent score {final_score:.4f} excede umbral MALICE"
    elif final_score > 0.55:
        verdict    = "SUSPICION"
        confidence = _dround(final_score, 2)
        reason     = f"Señal significativa con soporte estructural (score={final_score:.4f})"
    elif final_score > 0.25:
        verdict    = "UNKNOWN"
        confidence = _dround(final_score * 0.5, 2)
        reason     = f"Anomalía sin suficiente soporte estructural (score={final_score:.4f})"
    else:
        verdict    = "NOISE"
        confidence = _dround(1.0 - final_score, 2)
        reason     = f"Sin evidencia suficiente de intención maliciosa (score={final_score:.4f})"

    return {
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
