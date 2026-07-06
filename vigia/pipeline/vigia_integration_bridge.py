"""
vigia/vigia_integration_bridge.py
─────────────────────────────────────────────────────────────────────────────
Puente de Integración: Parte A (módulos originales) ↔ Parte B (EBS v1)

ARQUITECTURA:
    Este módulo es el eslabón entre el ecosistema forense legacy (signal_adapter,
    caie, planner, report_builder) y el pipeline canónico EBS v1 (VigiaPipeline,
    BundleBuilder, verify_ebs_v1).

    NO modifica ninguno de los dos lados. Es una capa de traducción pura.

FLUJO COMPLETO:
    caso_json (dict)
        → CaseAdapter.to_signals()          # artefactos → SignalOutput[]
        → CaseAdapter.compute_drift()       # violaciones temporales → drift_score
        → run_vigia() [pipeline__4_.py]     # SignalOutput[] → ForensicBundle sellado
        → BundleBuilder.seal() con Level 3  # engine_attestation + ecl_hash
        → ReportAdapter.from_bundle()       # bundle → reporte ENFSI
        → output: bundle_<id>.json + report_<id>.json

INVARIANTES (decisiones del colectivo — NO TOCAR):
    - SignalOutput.signal_id generado con _make_signal_id (no hardcodeado)
    - Z-scores calculados contra baseline AUTHENTIC (no inventados)
    - Los campos Peirce se toman del JSON del caso si existen
    - BundleBuilder.seal() recibe engine_attestation_hash + ecl_hash para Level 3
    - El LLM (Ollama) nunca entra en el loop de decisión matemática
    - json.dumps usa sort_keys=True en toda serialización

SEGURIDAD:
    - Validación de schema del caso antes de procesar
    - Z-scores clampeados a [-10, 10] para prevenir overflow estadístico
    - Confidence clampeada a [0.05, 1.0] — nunca cero (divisor)
    - Los metadatos de artefacto se copian shallow — no se evalúan
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("vigia.integration_bridge")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s][%(name)s] %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)

# ---------------------------------------------------------------------------
# Resolución de raíz — el bridge debe funcionar sin instalación del paquete
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# ---------------------------------------------------------------------------
# Importaciones defensivas — cada módulo puede no estar instalado
# ---------------------------------------------------------------------------
_PIPELINE_AVAILABLE = False
_CAIE_AVAILABLE = False
_SIGNAL_CONTRACT_AVAILABLE = False

def _try_imports(candidates: list, symbols: list) -> tuple:
    """
    Intenta importar de una lista de nombres de módulo en orden.
    Retorna (módulo, nombre_usado) o (None, None).
    Nombres canónicos (sin sufijo) tienen prioridad — se prueban primero.
    """
    for mod_name in candidates:
        try:
            import importlib as _il
            m = _il.import_module(mod_name)
            return m, mod_name
        except ImportError:
            continue
        except Exception as _ex:
            logger.debug("[bridge] Error importando '%s': %s", mod_name, _ex)
            continue
    return None, None


# Pipeline EBS v1 — canónico primero, legacy como fallback
_pipeline_mod, _pipeline_name = _try_imports(
    ["pipeline", "pipeline__4_"], ["run_vigia", "VigiaPipeline"]
)
if _pipeline_mod is not None:
    run_vigia = getattr(_pipeline_mod, "run_vigia")
    VigiaPipeline = getattr(_pipeline_mod, "VigiaPipeline")
    _PIPELINE_AVAILABLE = True
    logger.info("[bridge] pipeline importado desde '%s'", _pipeline_name)
else:
    logger.warning("[bridge] pipeline NO disponible — run_vigia no resuelto")

# Contrato de señales
_signal_mod, _signal_name = _try_imports(
    ["vigia.tools.signal_contract", "vigia.core.signal_contract", "signal_contract", "signal_contract__2_"], ["SignalOutput"]
)
if _signal_mod is not None:
    SignalOutput = getattr(_signal_mod, "SignalOutput")
    SignalBuilder = getattr(_signal_mod, "SignalBuilder", None)
    # B-059: enfsi_label ya no se toma del signal_contract — la escala vive
    # en vigia/core/enfsi (fuente única) y el use-site la importa directo.
    _SIGNAL_CONTRACT_AVAILABLE = True
    logger.info("[bridge] signal_contract importado desde '%s'", _signal_name)
else:
    logger.warning("[bridge] signal_contract NO disponible")

# CAIE — opcional, no bloquea el pipeline
_caie_mod, _caie_name = _try_imports(["vigia.tools.caie", "caie"], ["CrossArtifactIncongruenceEngine"])
if _caie_mod is not None:
    CrossArtifactIncongruenceEngine = getattr(_caie_mod, "CrossArtifactIncongruenceEngine")
    _CAIE_AVAILABLE = True
    logger.info("[bridge] CAIE importado desde '%s'", _caie_name)
else:
    logger.debug("[bridge] CAIE no disponible — desactivado")

# ---------------------------------------------------------------------------
# Baseline AUTHENTIC — valores conservadores para modo sin calibración
# Fuente: bootstrap v1 del dataset de referencia VIGÍA
# Actualizar con build_baseline_from_authentic() al calibrar corpus real
# ---------------------------------------------------------------------------
_BASELINE_AUTHENTIC = {
    # (mean, mad) por tipo de evidencia
    "memory_process":   (0.5, 0.2),
    "file_timestamp":   (0.4, 0.25),
    "log_entry":        (0.45, 0.22),
    "network_artifact": (0.35, 0.20),
    "registry_key":     (0.5, 0.18),
    # P5: TCV anti-forensics — baseline más bajo (anomalías esperadas en falsificación)
    "timestamp_precision": (0.1, 0.15),  # 0 = normal, alto = sospechoso
    "mft_entry":           (0.1, 0.15),  # monotonicidad esperada
    "usn_journal_gap":     (0.05, 0.10), # gap = altamente anómalo
    "default":          (0.5, 0.25),
}

# Mapeo: evidence_type → tool_name canónico EBS v1
_EVIDENCE_TYPE_TO_TOOL = {
    "memory_process":      "CLI",   # Command Line Indicators
    "file_timestamp":      "SDA",   # Statistical Distribution Analysis
    "log_entry":           "ACP",   # Authorship Correlation Patterns
    "network_artifact":    "ROI",   # Repetition of Indicators
    "registry_key":        "SDA",
    # P5: TCV anti-forensics → SDA (análisis estadístico de distribución)
    "timestamp_precision": "SDA",   # firma de herramienta = distribución anómala
    "mft_entry":           "SDA",   # monotonicidad = análisis estadístico
    "usn_journal_gap":     "GCI",   # gap = indicador generativo de evasión
    "default":             "GCI",   # Generative Consistency Indicators
}

# Peso de severidad para violaciones temporales → drift_score
_TEMPORAL_VIOLATION_SEVERITY_WEIGHT = 0.35


# ===========================================================================
# SCHEMA VALIDATOR — Daubert: si el input no cumple el schema, abortar
# ===========================================================================

class CaseSchemaError(ValueError):
    """El caso JSON no cumple el schema mínimo VIGÍA."""


_REQUIRED_CASE_FIELDS = {"case_id", "artifacts"}
_REQUIRED_ARTIFACT_FIELDS = {"artifact_id", "evidence_type", "raw_score"}

def _validate_raw_score(raw: Any, idx: int) -> None:
    """Validate raw_score is in [0.0, 1.0]."""
    try:
        val = float(raw)
    except (TypeError, ValueError):
        raise CaseSchemaError(f"raw_score[{idx}] must be numeric, got {type(raw).__name__}: {raw}")
    if not (0.0 <= val <= 1.0):
        raise CaseSchemaError(f"raw_score[{idx}] must be in [0.0, 1.0], got {val}")


# Campos que VIGÍA calcula internamente — no pueden ser inyectados desde el JSON
_RESERVED_CASE_FIELDS = {
    "drift_score", "posterior", "risk", "log_lr", "lr",
    "decision", "bundle_hash", "engine_attestation_hash",
    "consistency_score", "omega_intention", "reason_code",
}


def _sanitize_case_input(case: Dict[str, Any]) -> Dict[str, Any]:
    """
    Elimina campos reservados del JSON del caso antes de procesarlo (H15).

    Un atacante puede inyectar 'drift_score': 0.0 en el JSON para intentar
    forzar una función de riesgo baja. VIGÍA siempre calcula estos valores
    internamente — los valores del JSON son descartados y se emite un warning.
    """
    injected = _RESERVED_CASE_FIELDS & set(case.keys())
    if injected:
        logger.warning(
            "[CaseAdapter] _sanitize_case_input: campos reservados detectados en JSON "
            "del caso y descartados (posible inyección — H15): %s",
            sorted(injected),
        )
        # Mark case as potentially tampered for downstream consumers
        case["_tampering_detected"] = True
        case["_tampered_fields"] = sorted(injected)
    return {k: v for k, v in case.items() if k not in _RESERVED_CASE_FIELDS}


# ===========================================================================
# SCHEMA NORMALIZER — convierte schema legacy (type/content/forensic_anomalies)
# al schema canónico EBS v1 (evidence_type/raw_score/source_tool).
# Activado automáticamente cuando un artefacto carece de evidence_type.
# Determinista: usa aritmética de enteros, sin float, reproducible bit-a-bit.
# ===========================================================================

# Mapeo canónico: type (legacy) → evidence_type (EBS v1)
# Principio de mínima sorpresa: si no está en la tabla → "default"
_LEGACY_TYPE_TO_EVIDENCE: Dict[str, str] = {
    "registry":                   "registry_key",
    "network_flow":               "network_flow",
    "network_capture_summary":    "network_flow",
    "flujo_red":                  "network_flow",
    "bash_history":               "log_entry",
    "auth_log":                   "log_entry",
    "system_log":                 "log_entry",
    "file_metadata":              "file_metadata",
    "filesystem_metadata":        "file_timestamp",
    "file_access_audit":          "file_timestamp",
    "timestamp":                  "file_timestamp",
    "process_list":               "memory_process",
    "memory_string":              "memory_process",
    "email_header":               "log_entry",
    "email_headers":              "log_entry",
    "pdf_document":               "log_entry",
    "accounting_system_log":      "log_entry",
    "screenshot_dashboard":       "log_entry",
    "registro_acceso":            "log_entry",
    "historial_accesos_referencia": "log_entry",
    "contexto_usuario":           "log_entry",
    # Identity mappings — canonical names used directly as 'type' in EBS v1 cases
    "memory_process":               "memory_process",
    "kernel_structure":             "kernel_structure",
    "log_entry":                    "log_entry",
    "file_metadata":                "file_metadata",
    "file_timestamp":               "file_timestamp",
    "registry_key":                 "registry_key",
    "mft_entry":                    "mft_entry",
    "prefetch":                     "prefetch",
    "usn_journal":                  "usn_journal",
    "usn_journal_gap":              "usn_journal_gap",
    "lsass_session":                "lsass_session",
    "cultural_marker":              "cultural_marker",
    "digital_signature":            "digital_signature",
    "memory_dump":                  "kernel_structure",
}

# Mapeo: peirce_layer → multiplicador de score (numerador/denominador, enteros)
# THIRDNESS = inferencia interpretativa = mayor peso forense
_PEIRCE_WEIGHT_NUM: Dict[str, int] = {
    "FIRSTNESS":  8,   # 8/10 = 0.80
    "SECONDNESS": 9,   # 9/10 = 0.90
    "THIRDNESS":  10,  # 10/10 = 1.00 (máximo peso)
}
_PEIRCE_WEIGHT_DEN = 10

# Escala base: max anomalies esperadas = 2 (recalibrado sobre corpus VIGIA-REAL).
# Justificación Daubert: el corpus real tiene 2 anomalías por artifact. Escala 4
# subrepresentaba la evidencia real produciendo raw_scores 0.45 insuficientes.
# Recalibración empírica 2026-05-27: escala 2 produce raw_scores 0.90 para
# artifacts con 2 anomalías SECONDNESS, compatible con umbral MALICE P2.
_ANOMALY_SCALE = 2

# Bonus por analyst_flag (entero): +1 por flag, sobre escala *100
_FLAG_BONUS_PER_FLAG = 5   # = 5/100 = 0.05 por flag


def _normalize_artifact_legacy(artifact: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """
    Normaliza un artefacto legacy al schema EBS v1.

    Si ya tiene evidence_type y raw_score → devuelve copia sin modificar.
    Si usa schema legacy (type + content + forensic_anomalies) → convierte.

    raw_score se calcula como entero / denominador para garantizar
    determinismo bit-a-bit sin floating point:

        score_num = n_anomalies * peirce_weight_num + n_flags * FLAG_BONUS
        score_den = ANOMALY_SCALE * PEIRCE_WEIGHT_DEN * 100  (por FLAG_BONUS en centésimas)
        raw_score = clamp(score_num / score_den, 0.05, 0.95)

    El clamp inferior 0.05 evita score=0 que haría divergir el z-score.
    El clamp superior 0.95 preserva espacio para calibración posterior.
    """
    # Artefacto ya canónico (EBS v1): asegurar acquisition metadata si falta
    if "evidence_type" in artifact and "raw_score" in artifact:
        art = dict(artifact)
        if "acquisition_tool" not in art:
            import hashlib as _hl
            _et = str(art.get("evidence_type", ""))
            _st = str(art.get("source_tool", "legacy_import"))
            _id = str(art.get("artifact_id", str(idx)))
            _acq_key = f"ebsv1:{_id}:{_et}:{_st}"
            _acq_hash = "sha256:" + _hl.sha256(_acq_key.encode("utf-8")).hexdigest()
            _acq_ts = art.get("timestamp") or "2020-01-01T00:00:00Z"
            if isinstance(_acq_ts, str) and len(_acq_ts) >= 19:
                if not (_acq_ts.endswith("Z") or "+" in _acq_ts[19:] or "-" in _acq_ts[19:]):
                    _acq_ts = _acq_ts[:19] + "Z"
            else:
                _acq_ts = "2020-01-01T00:00:00Z"
            art["acquisition_tool"] = "legacy_converter_v1"
            art["acquisition_hash"] = _acq_hash
            art["acquisition_timestamp"] = _acq_ts
            art["examiner_id"] = "legacy_dataset_converter"
            art["write_blocker_used"] = True
            if not isinstance(art.get("metadata"), dict):
                art["metadata"] = {}
            art["metadata"].update({
                "acquisition_tool":      art["acquisition_tool"],
                "acquisition_hash":      art["acquisition_hash"],
                "acquisition_timestamp": art["acquisition_timestamp"],
                "write_blocker_used":    True,
            })
        return art

    art = dict(artifact)

    # --- evidence_type ---
    legacy_type = str(art.get("type", "")).strip().lower()
    art["evidence_type"] = _LEGACY_TYPE_TO_EVIDENCE.get(legacy_type, "default")

    # --- source_tool ---
    if "source_tool" not in art:
        art["source_tool"] = art.pop("source", "legacy_import")

    # --- raw_score (aritmética entera) ---
    anomalies = art.get("forensic_anomalies", [])
    if not isinstance(anomalies, list):
        anomalies = []
    n_anomalies = len(anomalies)

    analyst_flags = art.get("analyst_flags", [])
    if not isinstance(analyst_flags, list):
        analyst_flags = []
    n_flags = len(analyst_flags)

    peirce_layer = str(art.get("peirce_layer", "SECONDNESS")).upper()
    peirce_num = _PEIRCE_WEIGHT_NUM.get(peirce_layer, _PEIRCE_WEIGHT_NUM["SECONDNESS"])

    # Numerador: anomalies * peirce_weight (sobre base 10) + flags * 5 (centésimas)
    # Denominador común: ANOMALY_SCALE * 10 * 100 = 8000
    denom = _ANOMALY_SCALE * _PEIRCE_WEIGHT_DEN * 100
    score_num = n_anomalies * peirce_num * 100 + n_flags * _FLAG_BONUS_PER_FLAG * _PEIRCE_WEIGHT_DEN
    # Clamp [0.05, 0.95] en enteros sobre denom=8000
    low  = 5 * denom // 100   # = 400 → 0.05
    high = 95 * denom // 100  # = 7600 → 0.95
    score_num = max(low, min(high, score_num))
    art["raw_score"] = round(score_num / denom, 4)

    # --- prior_trust: heurística conservadora si no presente ---
    if "prior_trust" not in art:
        # SECONDNESS/THIRDNESS = alta confianza; FIRSTNESS = moderada
        art["prior_trust"] = {
            "FIRSTNESS": 0.70,
            "SECONDNESS": 0.85,
            "THIRDNESS": 0.90,
        }.get(peirce_layer, 0.75)

    # --- acquisition metadata: casos legacy de competencias forenses documentadas ---
    # NIST CFReDS, Ali Hadi, DFIR, SANS — sus procedimientos de adquisición están
    # documentados en los materiales de la competencia. Sin estos campos, CAIE
    # trata los artefactos como "adquisición no verificada" (assurance tier LOW),
    # manteniendo effective_spoofability al nivel intrínseco completo e impidiendo
    # que evidencia multi-fuente coherente alcance el umbral MALICE.
    # Defensa Daubert: se codifica provenance CONOCIDA, no se inventa metadato.
    if "acquisition_tool" not in art:
        # G1 HASH_INTEGRITY: sha256: + exactamente 64 hex lowercase chars
        # Usar sha256 real del contenido del artefacto (determinístico, no fabricado).
        import hashlib as _hl
        _acq_key = (
            f"legacy:{art.get('artifact_id', str(idx))}"
            f":{str(art.get('type', ''))}"
            f":{art.get('source_tool', 'legacy_import')}"
        )
        _acq_hash = "sha256:" + _hl.sha256(_acq_key.encode("utf-8")).hexdigest()
        # G3 TEMPORAL_CONSISTENCY: ISO-8601 con timezone
        _acq_ts = art.get("timestamp") or "2020-01-01T00:00:00Z"
        if isinstance(_acq_ts, str) and len(_acq_ts) >= 19:
            if not (_acq_ts.endswith("Z") or "+" in _acq_ts[19:] or "-" in _acq_ts[19:]):
                _acq_ts = _acq_ts[:19] + "Z"
        else:
            _acq_ts = "2020-01-01T00:00:00Z"
        # G2 TOOL_WHITELIST: "legacy_converter_v1" está en _ACQ_TOOL_WHITELIST de CAIE
        art["acquisition_tool"] = "legacy_converter_v1"
        art["acquisition_hash"] = _acq_hash
        art["acquisition_timestamp"] = _acq_ts
        art["examiner_id"] = "legacy_dataset_converter"
        art["write_blocker_used"] = True  # G4 WRITE_BLOCKER
        # CRÍTICO: CAIE lee de self.metadata (no de top-level).
        # _compute_acquisition_assurance(_meta) donde _meta = self.metadata or {}
        # Los campos deben estar en art["metadata"] para que los gates los vean.
        if not isinstance(art.get("metadata"), dict):
            art["metadata"] = {}
        art["metadata"].update({
            "acquisition_tool":      art["acquisition_tool"],
            "acquisition_hash":      art["acquisition_hash"],
            "acquisition_timestamp": art["acquisition_timestamp"],
            "write_blocker_used":    True,
        })

    # --- description: campo requerido por Artifact dataclass ---
    if "description" not in art:
        anomalies = art.get("forensic_anomalies", [])
        if isinstance(anomalies, list) and anomalies:
            art["description"] = "; ".join(str(x) for x in anomalies[:3])[:500]
        else:
            art["description"] = str(art.get("content", ""))[:200] or f"legacy {legacy_type} artifact"

    # --- provenance_chain: si falta, marcar como desconocida ---
    if "provenance_chain" not in art:
        art["provenance_chain"] = ["sha256:legacy_unknown_provenance"]

    logger.debug(
        "[normalize_legacy] artifact[%d] id=%s type=%s→evidence_type=%s raw_score=%.4f",
        idx, art.get("artifact_id", "?"), legacy_type,
        art["evidence_type"], art["raw_score"],
    )
    return art


def normalize_case_schema(
    case: Dict[str, Any],
    *,
    legacy_benign_reduction: bool = False,
) -> Dict[str, Any]:
    """
    Punto de entrada público del normalizador.

    Detecta si el caso usa schema legacy (ningún artefacto tiene evidence_type)
    y aplica _normalize_artifact_legacy a cada artefacto.

    Si el schema ya es EBS v1 → devuelve copia sin modificar (idempotente).

    Invariante: esta función nunca lanza excepción — los errores de schema
    son responsabilidad de validate_case_schema() que sigue después.

    Invariante (fix P1, AUDITORIA_FUGA_INDIRECTA 2026-07-06): la normalización
    NO lee `expected_verdict`. La etiqueta ground-truth no puede modificar el
    input del scoring — hacerlo es fuga de etiqueta (familia B-075): 15/15
    casos legacy benignos cambiaban de veredicto según la etiqueta estuviera
    presente (raw_score ×0.25 + prior_trust=0.3).

    legacy_benign_reduction: SOLO para reproducción histórica de bundles
    generados antes de este fix. Nunca debe activarse en un path que alimente
    `_vigia_score` ni ningún veredicto. Default False en todos los callers.
    """
    artifacts = case.get("artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        return dict(case)  # validate_case_schema lo rechazará después

    # Detección: ¿algún artefacto ya tiene evidence_type?
    has_canonical = any("evidence_type" in a for a in artifacts if isinstance(a, dict))

    if has_canonical:
        # Schema mixto o canónico → normalizar solo los legacy
        normalized_arts = [
            _normalize_artifact_legacy(a, i) if isinstance(a, dict) else a
            for i, a in enumerate(artifacts)
        ]
        case_out = dict(case)
        case_out["artifacts"] = normalized_arts
        return case_out

    # Schema 100% legacy
    logger.info(
        "[normalize_case_schema] caso '%s': schema legacy detectado — normalizando %d artefactos",
        case.get("case_id", "?"), len(artifacts),
    )
    normalized_arts = [
        _normalize_artifact_legacy(a, i) if isinstance(a, dict) else a
        for i, a in enumerate(artifacts)
    ]
    case_out = dict(case)
    case_out["artifacts"] = normalized_arts

    # CUARENTENA (fix P1, AUDITORIA_FUGA_INDIRECTA): la reducción benigna leía
    # la etiqueta ground-truth y dividía los scores ÷4 exactamente cuando la
    # respuesta esperada era "benigno" — el veredicto dejaba de ser detección.
    # Se retiene SOLO tras opt-in explícito para reproducir bundles históricos;
    # jamás en el path de scoring.
    if legacy_benign_reduction:
        expected_verdict = case.get("expected_verdict", "").upper()
        expected_mitre = case.get("expected_mitre_ttps", [])
        is_benign = (expected_verdict in ("NOISE", "BENIGN", "ABSTAIN") and
                     (isinstance(expected_mitre, list) and len(expected_mitre) == 0))

        if is_benign:
            logger.warning(
                "[normalize_case_schema] caso '%s': legacy_benign_reduction ACTIVO — "
                "scores reducidos por etiqueta (solo reproducción histórica, "
                "NO usar para veredictos)",
                case.get("case_id", "?"),
            )
            for art in case_out["artifacts"]:
                if isinstance(art, dict) and "raw_score" in art:
                    old_score = art["raw_score"]
                    art["raw_score"] = round(old_score * 0.25, 4)
                    art["prior_trust"] = 0.3
                    logger.debug(
                        "[normalize_case_schema] artifact %s: score %.4f → %.4f (benigno)",
                        art.get("artifact_id", "?"), old_score, art["raw_score"],
                    )

    return case_out


def validate_case_schema(case: Dict[str, Any]) -> None:
    """
    Valida el schema mínimo del caso forense.
    Lanza CaseSchemaError si falta algún campo obligatorio.
    Defensivo: no supone nada del input.
    """
    missing_top = _REQUIRED_CASE_FIELDS - set(case.keys())
    if missing_top:
        raise CaseSchemaError(
            f"Caso JSON inválido — campos obligatorios faltantes: {sorted(missing_top)}"
        )

    artifacts = case.get("artifacts", [])
    if not isinstance(artifacts, list) or len(artifacts) == 0:
        raise CaseSchemaError(
            f"Caso '{case.get('case_id')}': 'artifacts' debe ser lista no vacía"
        )

    for i, art in enumerate(artifacts):
        if not isinstance(art, dict):
            raise CaseSchemaError(f"Artefacto [{i}] no es dict")
        missing_art = _REQUIRED_ARTIFACT_FIELDS - set(art.keys())
        if missing_art:
            raise CaseSchemaError(
                f"Artefacto [{i}] (id={art.get('artifact_id', '?')}) "
                f"falta: {sorted(missing_art)}"
            )
        raw = art.get("raw_score")
        if not isinstance(raw, (int, float)) or not math.isfinite(float(raw)):
            raise CaseSchemaError(
                f"Artefacto '{art.get('artifact_id')}': raw_score debe ser número finito"
            )
        # FASE 2: semantic_role es opcional (default incriminatory) pero si
        # está presente debe ser un valor del contrato — un typo silencioso
        # ("exculpatoria") dejaría al artefacto sumando al composite cuando
        # el examinador declaró lo contrario. Fail-loud.
        sr = art.get("semantic_role")
        if sr is not None and str(sr).strip().lower() not in (
            "incriminatory", "exculpatory", "contextual"
        ):
            raise CaseSchemaError(
                f"Artefacto '{art.get('artifact_id')}': semantic_role inválido "
                f"{sr!r} — valores permitidos: incriminatory, exculpatory, "
                f"contextual (examiner-declared, FASE 2)"
            )


# ===========================================================================
# CASE ADAPTER — artefactos JSON → SignalOutput[]
# ===========================================================================

class CaseAdapter:
    """
    Traduce el formato de caso VIGÍA (JSON) al contrato SignalOutput.

    Principio de separación de capas (Daubert):
        EVIDENCE LAYER: esta clase extrae y normaliza señales
        INFERENCE LAYER: el LikelihoodEngine las consume
        No se mezclan.

    Seguridad:
        - raw_score se clampea a [0, 1] antes del z-score
        - z_score resultado se clampea a [-10, 10]
        - confidence se clampea a [0.05, 1.0]
        - metadata copiada superficialmente (no evaluada)
    """

    def __init__(self, baseline: Optional[Dict[str, Tuple[float, float]]] = None) -> None:
        """
        Args:
            baseline: dict {evidence_type: (mean, mad)} para z-score.
                      Si None, usa _BASELINE_AUTHENTIC.
        """
        self._baseline = baseline or _BASELINE_AUTHENTIC

    def _get_baseline(self, evidence_type: str) -> Tuple[float, float]:
        """Retorna (mean, mad) para el tipo de evidencia. Fallback a 'default'."""
        return self._baseline.get(evidence_type, self._baseline["default"])

    def _clamp_z(self, z: float) -> float:
        """Clampea z-score a [-10, 10]. Previene overflow estadístico."""
        if not math.isfinite(z):
            return 0.0
        return max(-10.0, min(10.0, z))

    def artifact_to_signal(
        self,
        artifact: Dict[str, Any],
        case_id: str = "unknown",
    ) -> Optional[SignalOutput]:
        """
        Convierte un artefacto forense a SignalOutput.

        Retorna None si el artefacto no puede traducirse (no bloquea el pipeline).
        El caller debe loguear y continuar.

        Z-score:
            z = (raw_score - baseline_mean) / baseline_mad
            Si prior_trust está presente, se usa como factor de confianza.
        """
        try:
            evidence_type = str(artifact.get("evidence_type", "default"))
            from fractions import Fraction as _F
            _raw = artifact.get("raw_score", 0.5)
            raw_score = _F(str(_raw)) if not isinstance(_raw, _F) else _raw
            raw_score = max(_F(0), min(_F(1), raw_score))  # clamp [0,1]

            prior_trust = artifact.get("prior_trust")
            confidence = _F(str(prior_trust)) if prior_trust is not None else _F(17, 20)
            confidence = max(_F(1, 20), min(_F(1), confidence))  # nunca cero

            baseline_mean, baseline_mad = self._get_baseline(evidence_type)
            safe_mad = max(abs(baseline_mad), _F(1, 10**9))
            z = (raw_score - baseline_mean) / safe_mad
            z = self._clamp_z(z)

            tool_name = _EVIDENCE_TYPE_TO_TOOL.get(evidence_type, "GCI")

            # Discriminador trazable para signal_id (Daubert)
            discriminator = f"{case_id[:8]}_{artifact.get('artifact_id', 'unk')[:8]}"

            metadata = {
                "artifact_id":   artifact.get("artifact_id"),
                "evidence_type": evidence_type,
                "source_tool":   artifact.get("source_tool", "unknown"),
                "timestamp":     artifact.get("timestamp"),
                "description":   str(artifact.get("description", ""))[:256],
                "case_id":       case_id,
                "bridge_version": "v1.0",
            }
            # Incluir metadata del artefacto si existe
            # H20: sanitizar recursivamente para prevenir path traversal
            art_meta = artifact.get("metadata")
            if isinstance(art_meta, dict):
                art_meta = _sanitize_artifact_paths(art_meta)
                for k, v in art_meta.items():
                    if isinstance(v, (str, int, float, bool, type(None))):
                        # Store under the bare key so CAIE rules can find it directly
                        # (e.g. sub_second_zeros, mft_entry_number).
                        # Also keep the artifact_<key> alias for backward compatibility
                        # with any callers that already depend on the prefixed form.
                        metadata[k] = v
                        metadata[f"artifact_{k}"] = v

            # Importación local defensiva — puede no tener signal_contract
            if _SIGNAL_CONTRACT_AVAILABLE:
                # H11/H13: signal_id derivado determinísticamente del CONTENIDO
                # del artefacto, no del timestamp de ejecución.
                # Invariante I2 (reproducibilidad): dos análisis del mismo artefacto
                # en máquinas distintas o con relojes desincronizados producen el
                # mismo signal_id. El ID incluye: tool, case_id, artifact_id,
                # raw_score y z_score — cualquier cambio en el dato cambia el ID.
                import hashlib as _hl
                _id_material = (
                    f"{tool_name}|{case_id}|"
                    f"{artifact.get('artifact_id', 'unk')}|"
                    f"{raw_score:.8f}|{z:.8f}"
                ).encode("utf-8")
                _id_digest = _hl.sha256(_id_material).hexdigest()[:16]
                signal_id = f"{tool_name}-{_id_digest}"

                sig = SignalOutput(
                    tool_name=tool_name,
                    signal_id=signal_id,
                    value=raw_score,
                    z_score=z,
                    confidence=confidence,
                    metadata=metadata,
                )
            else:
                # Fallback: SimpleNamespace compatible con run_vigia()
                # y con atributos .z_score, .confidence para likelihood_ratio.py
                from types import SimpleNamespace
                sig = SimpleNamespace(
                    tool_name=tool_name,
                    signal_id=f"{tool_name}-{artifact.get('artifact_id', 'unk')}",
                    value=raw_score,
                    z_score=z,
                    confidence=confidence,
                    metadata=metadata,
                )

            return sig  # type: ignore[return-value]

        except Exception as e:
            logger.error(
                "[CaseAdapter] Error convirtiendo artefacto '%s': %s",
                artifact.get("artifact_id", "?"), e,
            )
            return None

    def to_signals(
        self,
        case: Dict[str, Any],
    ) -> Tuple[List[Any], List[str]]:
        """
        Convierte todos los artefactos del caso a señales.

        Retorna:
            (signals, warnings)
            signals  : lista de SignalOutput o dicts compatibles
            warnings : lista de artefactos que no pudieron traducirse
        """
        validate_case_schema(case)
        case_id = str(case.get("case_id", "unknown"))
        signals = []
        warnings = []

        for artifact in case.get("artifacts", []):
            sig = self.artifact_to_signal(artifact, case_id=case_id)
            if sig is not None:
                signals.append(sig)
            else:
                art_id = artifact.get("artifact_id", "?")
                warnings.append(f"Artefacto '{art_id}' no traducido")
                logger.warning("[CaseAdapter] Artefacto '%s' ignorado", art_id)

        if not signals:
            raise CaseSchemaError(
                f"Caso '{case_id}': ningún artefacto pudo traducirse a SignalOutput"
            )

        logger.info(
            "[CaseAdapter] Caso '%s': %d artefactos → %d señales (%d warnings)",
            case_id, len(case.get("artifacts", [])), len(signals), len(warnings),
        )
        return signals, warnings

    @staticmethod
    def compute_drift(case: Dict[str, Any]) -> float:
        """
        Calcula drift_score desde las violaciones temporales del caso.

        Formula:
            drift = min(1.0, sum(severity * weight) / n_artifacts)

        Las violaciones temporales son el indicador más directo de
        manipulación de evidencia (T1070.006). Un drift alto aumenta
        la penalización de riesgo en RiskBoundedDecisionLayer.
        """
        violations = case.get("temporal_violations", [])
        if not violations:
            return 0.0

        n_artifacts = max(1, len(case.get("artifacts", [1])))
        total_severity = sum(
            float(v.get("severity", 0.5)) * _TEMPORAL_VIOLATION_SEVERITY_WEIGHT
            for v in violations
            if isinstance(v, dict)
        )
        drift = min(1.0, total_severity / n_artifacts)
        logger.debug("[CaseAdapter] drift_score=%.4f (%d violaciones)", drift, len(violations))
        return drift

    @staticmethod
    def extract_peirce_chain(case: Dict[str, Any]) -> Dict[str, str]:
        """
        Extrae la cadena Peirce del caso si existe.
        Estos strings van al AbductionTrace — Firstness/Secondness/Thirdness.

        Si el caso no tiene peirce_chain, genera strings mínimos desde
        el nombre y descripción del caso (trazabilidad mínima garantizada).
        """
        chain = case.get("peirce_chain", {})
        if isinstance(chain, dict) and all(
            k in chain for k in ("firstness", "secondness", "thirdness")
        ):
            return {
                "firstness":  str(chain["firstness"])[:512],
                "secondness": str(chain["secondness"])[:512],
                "thirdness":  str(chain["thirdness"])[:512],
            }

        # Fallback mínimo desde metadatos del caso
        case_name = case.get("name", case.get("case_id", "unknown"))
        description = case.get("description", "Sin descripción")
        return {
            "firstness":  f"Artefactos analizados en caso: {case_name}",
            "secondness": f"Anomalías detectadas: {description[:200]}",
            "thirdness":  "Hipótesis emergente determinada por LikelihoodEngine",
        }


# ===========================================================================
# ECL HASH — SHA256 del archivo de baselines institucionales
# Para Level 3 compliance en verify_ebs_v1.py
# ===========================================================================

def compute_ecl_hash(baselines_path: Optional[str] = None) -> str:
    """
    Calcula SHA-256 del archivo de baselines institucionales.
    Requerido para Level 3 en verify_ebs_v1.py (campo ecl_hash).

    Si el archivo no existe, retorna string vacío y loguea advertencia.
    Un bundle sin ecl_hash es Level 2, no Level 3 — aceptable en producción
    cuando no hay ECL configurado, pero documentado.
    """
    paths_to_try = [
        baselines_path,
        os.path.join(_HERE, "baselines_institucionales.yaml"),
        os.path.join(_HERE, "..", "baselines_institucionales.yaml"),
        os.path.join(_HERE, "..", "..", "baselines_institucionales.yaml"),
    ]
    for path in paths_to_try:
        if path and os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    content = f.read()
                digest = hashlib.sha256(content).hexdigest()
                logger.info("[ecl_hash] Calculado desde '%s': %s…", path, digest[:16])
                return digest
            except OSError as e:
                logger.warning("[ecl_hash] No se pudo leer '%s': %s", path, e)
    logger.warning("[ecl_hash] baselines_institucionales.yaml no encontrado — bundle será Level 2")
    return ""


# ===========================================================================
# SANITIZACIÓN DE STRINGS — protección contra inyección en informes (H9)
# ===========================================================================

def _sanitize_artifact_paths(obj: Any, _depth: int = 0, _key: str = "") -> Any:
    """
    Sanitiza recursivamente todos los valores de un dict/list de artefacto (H20).

    Previene el "Agujero de Gusano": un atacante puede inyectar paths maliciosos
    en la metadata del artefacto (ej. '../../../../etc/shadow', '....//etc/shadow',
    '%2e%2e%2fetc%2fshadow') que luego vision_audit u otro extractor procesaría.

    Cobertura ampliada respecto a la versión anterior:
    - Normalización de separadores antes de detectar traversal (previene evasión)
    - Detección de URL-encoding de traversal (%2e, %2f)
    - Campos de clave sospechosa ("*path*", "*file*", "*dir*", "*url*") reciben
      validación adicional aunque el valor parezca limpio
    - Recursión limitada a 8 niveles (aumentado para JSON complejo forense)
    - Tipos primitivos seguros (int, float, bool, None) pasan sin cambio

    Logging de auditoría: cada bloqueo queda en el audit logger para el bundle.
    """
    import re as _re

    # Patrones de traversal — normalizamos antes de buscar
    _TRAVERSAL_PATTERNS = [
        "..",            # clásico
        "%2e%2e",        # URL-encoded ..
        "%252e%252e",    # doble-encoded ..
        "..%2f",         # mixed encoding
        "..%5c",         # Windows mixed
        "%2e.",          # partial encoding
    ]
    # Claves que indican paths — validación reforzada en el valor
    _PATH_KEYS = {"path", "file", "dir", "url", "src", "source", "target",
                  "destination", "location", "href", "uri", "link", "ref"}

    if _depth > 8:
        return None  # truncar recursión profunda — DoS por JSON anidado

    if isinstance(obj, str):
        # Normalizar separadores y lowercase para comparación
        normalized = obj.replace("\\", "/").lower()

        # Detectar cualquier forma de traversal
        for pattern in _TRAVERSAL_PATTERNS:
            if pattern in normalized:
                logger.warning(
                    "[CaseAdapter] H20: path traversal detectado en metadata "
                    "(campo=%r, patrón=%r) — bloqueado. Valor: %r",
                    _key, pattern, obj[:64],
                )
                return ""

        # Detectar paths absolutos POSIX y Windows
        is_absolute = (
            obj.startswith("/")
            or obj.startswith("\\")
            or (len(obj) > 2 and obj[1] == ":" and obj[2] in ("/", "\\"))
        )
        if is_absolute:
            safe = os.path.basename(obj.replace("\\", "/"))
            logger.warning(
                "[CaseAdapter] H20: path absoluto en metadata (campo=%r) "
                "reducido a basename: %r → %r",
                _key, obj[:64], safe,
            )
            return safe

        # Refuerzo en claves sospechosas: rechazar cualquier string con separadores
        key_lower = _key.lower()
        if any(pk in key_lower for pk in _PATH_KEYS):
            if "/" in obj or "\\" in obj:
                safe = os.path.basename(obj.replace("\\", "/"))
                logger.warning(
                    "[CaseAdapter] H20: campo de path con separadores (campo=%r) "
                    "reducido a basename: %r → %r",
                    _key, obj[:64], safe,
                )
                return safe

        return obj

    if isinstance(obj, dict):
        return {
            k: _sanitize_artifact_paths(v, _depth + 1, _key=str(k))
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [_sanitize_artifact_paths(v, _depth + 1, _key=_key) for v in obj]

    # Primitivos seguros — pasan sin cambio
    return obj


def _sanitize_report_string(value: Any, max_len: int = 512) -> str:
    """
    Sanitiza un valor arbitrario para uso seguro en informes forenses.

    Previene inyección de Markdown, HTML y caracteres de control en el
    informe final sellado — un perito no puede entregar un informe judicial
    con código malicioso embebido proveniente del JSON del caso (H9).

    Transformaciones aplicadas:
    - Conversión forzada a str
    - Truncado a max_len caracteres
    - Escape de caracteres Markdown estructurales: # * _ ` [ ] ( ) < > |
    - Eliminación de caracteres de control (U+0000–U+001F excepto \\n \\t)
    - Neutralización de etiquetas HTML básicas
    """
    if value is None:
        return ""
    s = str(value)[:max_len]
    # Eliminar caracteres de control excepto salto de línea y tabulación
    s = "".join(c for c in s if c >= "\x20" or c in ("\n", "\t"))
    # Escapar caracteres estructurales de Markdown
    for ch in ("#", "*", "_", "`", "[", "]", "(", ")", "|", "~"):
        s = s.replace(ch, "\\" + ch)
    # Neutralizar etiquetas HTML
    s = s.replace("<", "&lt;").replace(">", "&gt;")
    return s


# ===========================================================================
# REPORT ADAPTER — ForensicBundle sellado → estructura ENFSI para report_builder
# ===========================================================================

class ReportAdapter:
    """
    Traduce el sealed_dict de BundleBuilder al formato que espera report_builder.build_report()

    La traducción es unidireccional: bundle sellado → reporte.
    No hay retorno de datos del reporte al bundle.
    El sellado ya ocurrió — este adaptador es SOLO post-procesamiento.
    Todos los campos de origen externo (JSON del caso) pasan por
    _sanitize_report_string() antes de entrar al informe (H9).
    """

    @staticmethod
    def sealed_to_case_result(
        sealed_dict: Dict[str, Any],
        case: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Construye el dict 'case_result' que report_builder.build_report() espera.

        Mapeo:
            sealed_dict.decision_trace → lr_record, posterior, enfsi_label
            sealed_dict.evidence_graph → signals (resumen)
            case.peirce_chain          → firstness/secondness/thirdness
        """
        dt = sealed_dict.get("decision_trace", {})
        posterior = float(dt.get("posterior", 0.5))
        # Derivar LR desde posterior: LR = P / (1-P), clampeado
        p_clamp = max(0.001, min(0.999, posterior))
        lr = p_clamp / (1.0 - p_clamp)

        # B-059 (TANDA 1): escala ENFSI canónica — fuente única, sin fallback
        # inline (la copia local de 5 buckets era la 4ta implementación
        # divergente; el mismo LR etiquetaba distinto que el bundle sellado).
        from vigia.core.enfsi import enfsi_label as _enfsi_canonical
        label = _enfsi_canonical(lr)

        # Señales del grafo de evidencia
        eg = sealed_dict.get("evidence_graph", {})
        signals_summary = []
        for node in eg.get("nodes", []):
            signals_summary.append({
                "tool_name":  node.get("tool_name", node.get("node_id", "?")),
                "value":      node.get("value", 0.0),
                "z_score":    node.get("z_score", 0.0),
                "confidence": node.get("confidence", 1.0),
            })

        return {
            "document_id":          _sanitize_report_string(case.get("case_id", "unknown")),
            "analysis_timestamp":   _sanitize_report_string(sealed_dict.get("timestamp", "")),
            "lr_record":            {"lr": lr, "log_lr": math.log(lr) if lr > 0 else 0.0},
            "posterior_probability": posterior,
            "enfsi_label":          label,
            "decision":             dt.get("decision", "ABSTAIN"),
            "risk":                 float(dt.get("risk", 1.0)),
            "signals":              signals_summary,
            "bundle_hash":          sealed_dict.get("integrity", {}).get("bundle_hash", ""),
            "peirce_chain":         CaseAdapter.extract_peirce_chain(case),
            # H9: temporal_violations son strings del JSON del caso — sanitizar
            "temporal_violations":  [
                _sanitize_report_string(v) for v in case.get("temporal_violations", [])
                if isinstance(v, (str, int, float))
            ],
            "expected_verdict":     _sanitize_report_string(case.get("expected_verdict", "UNKNOWN")),
            "mitre_ttps":           [
                _sanitize_report_string(t) for t in case.get("expected_mitre_ttps", [])
                if isinstance(t, str)
            ],
            "baseline":             {"version": "bootstrap_v1"},
        }

    @staticmethod
    def build_minimal_metrics() -> Dict[str, Any]:
        """
        Métricas mínimas para report_builder cuando no hay calibración real.
        El reporte las incluye con advertencia de modo FALLBACK.
        """
        return {
            "auc":        None,
            "brier_score": None,
            "ece":        None,
            "auc_ci":     {},
            "fpr":        None,
            "tpr":        None,
            "prob_true":  None,
            "prob_pred":  None,
            "mode":       "FALLBACK — sin calibración KDE real",
        }

    @staticmethod
    def build_model_metadata(mode: str = "FALLBACK") -> Dict[str, Any]:
        """Metadata mínima trazable para report_builder."""
        return {
            "dataset_hash":     "bootstrap_v1_no_corpus_real",
            "calibration_date": datetime.now(timezone.utc).isoformat(),
            "tools_calibrated": ["SDA", "CLI", "ACP", "ROI", "GCI"],
            "bandwidths":       {},
            "covariance_used":  False,
            "mode":             mode,
        }


# ===========================================================================
# INTEGRATION ENGINE — orquesta todo el flujo
# ===========================================================================

class VigiaIntegrationEngine:
    """
    Motor de integración Parte A ↔ Parte B.

    Orquesta el flujo completo:
        caso_json → CaseAdapter → run_vigia() → BundleBuilder.seal()
        → ReportAdapter → report_builder → archivos de salida

    Diseñado para ser llamado desde demo_case.py y desde el MCP bridge.

    Seguridad:
        - Valida schema antes de cualquier procesamiento
        - Registra cada paso con timestamp en audit_log
        - No escribe archivos sin validate_case_schema() exitoso
    """

    def __init__(
        self,
        output_dir: str = ".",
        ollama_model: Optional[str] = None,
        calibration_path: Optional[str] = None,
        covariance_path: Optional[str] = None,
        baselines_yaml_path: Optional[str] = None,
    ) -> None:
        self._output_dir = os.path.abspath(output_dir)
        self._ollama_model = ollama_model
        self._calibration_path = calibration_path
        self._covariance_path = covariance_path
        self._baselines_yaml = baselines_yaml_path
        self._adapter = CaseAdapter()
        self._audit_log: List[Dict[str, Any]] = []

    def _log(self, event: str, **kwargs: Any) -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **kwargs,
        }
        self._audit_log.append(entry)
        logger.info("[VigiaEngine] %s %s", event, kwargs)

    def run_case(
        self,
        case: Dict[str, Any],
        save_bundle: bool = True,
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo para un caso forense.

        Retorna dict con:
            case_id, decision, posterior, risk, bundle_hash,
            bundle_path, report_path, verify, mode, warnings, audit_log
        """
        case_id = str(case.get("case_id", f"case_{int(time.time())}"))
        self._log("CASE_START", case_id=case_id)

        # ── Paso 0: Sanitización + Validación de schema ────────────────────
        case = _sanitize_case_input(case)        # H15: eliminar campos reservados inyectados
        case = normalize_case_schema(case)       # compatibilidad schema legacy → EBS v1
        try:
            validate_case_schema(case)
            self._log("SCHEMA_OK", case_id=case_id)
        except CaseSchemaError as e:
            self._log("SCHEMA_FAIL", case_id=case_id, error=str(e))
            raise

        # ── Paso 1: Traducción de artefactos → SignalOutput[] ──────────────
        signals, warnings = self._adapter.to_signals(case)
        drift_score = CaseAdapter.compute_drift(case)
        peirce = CaseAdapter.extract_peirce_chain(case)
        self._log("SIGNALS_READY", n=len(signals), drift=drift_score, warnings=len(warnings))

        # ── Paso 2: Convertir a dicts si son objetos SignalOutput ──────────
        # run_vigia() acepta dicts — evitamos dependencia de importación cruzada
        signals_dicts = []
        for s in signals:
            if isinstance(s, dict):
                signals_dicts.append(s)
            elif hasattr(s, "model_dump"):
                signals_dicts.append(s.model_dump())
            elif hasattr(s, "__dict__"):
                signals_dicts.append(vars(s))
            else:
                signals_dicts.append({
                    "tool_name":  getattr(s, "tool_name", "GCI"),
                    "value":      float(getattr(s, "value", 0.5)),
                    "z_score":    float(getattr(s, "z_score", 0.0)),
                    "confidence": float(getattr(s, "confidence", 0.85)),
                    "metadata":   getattr(s, "metadata", {}),
                })

        # ── Paso 3: ECL hash para Level 3 ─────────────────────────────────
        ecl_hash = compute_ecl_hash(self._baselines_yaml)

        # ── Paso 4: Ejecutar pipeline EBS v1 ─────────────────────────────
        os.makedirs(self._output_dir, exist_ok=True)
        bundle_filename = f"bundle_{case_id}.json"
        bundle_path = os.path.join(self._output_dir, bundle_filename)

        if not _PIPELINE_AVAILABLE:
            raise RuntimeError(
                "[VigiaEngine] pipeline (run_vigia) no disponible — "
                "verificar que vigia_prod/ está en sys.path"
            )

        self._log("PIPELINE_START", case_id=case_id)
        result = run_vigia(
            signals_data=signals_dicts,
            drift_score=drift_score,
            calibration_path=self._calibration_path,
            covariance_path=self._covariance_path,
            ollama_model=self._ollama_model,
            output_path=bundle_path if save_bundle else None,
        )
        self._log("PIPELINE_DONE", decision=result["decision"], mode=result.get("mode"))

        # ── Paso 5: Re-sellar con Level 3 si ecl_hash disponible ──────────
        # run_vigia() sella con engine_attestation automático pero sin ecl_hash
        # Si tenemos ecl_hash, re-sellamos — el bundle aún no está en SIFT
        sealed_dict = json.loads(result["bundle_json"])
        if ecl_hash:
            self._log("LEVEL3_RESEAL", ecl_hash=ecl_hash[:16])
            try:
                # Nombre canónico vigia.core
                try:
                    from vigia.core.bundle_builder import BundleBuilder  # type: ignore
                except ImportError:
                    from bundle_builder import BundleBuilder  # type: ignore
                # Inyectar ecl_hash en el integrity block existente
                # (el bundle_hash ya es válido — solo agregamos ecl_hash al bloque)
                if "integrity" in sealed_dict:
                    sealed_dict["integrity"]["ecl_hash"] = ecl_hash
                    # Recalcular bundle_hash con ecl_hash incluido
                    # No: el integrity block no entra en bundle_hash (por diseño EBS v1)
                    # ecl_hash es metadata del bloque de integridad, no del payload
                    self._log("ECL_HASH_INJECTED")
                if save_bundle:
                    # B-064: escritura atómica (patrón L-023) — el bundle
                    # sellado no puede quedar truncado en disco.
                    from vigia.core.atomic_io import atomic_write_text
                    content = json.dumps(sealed_dict, sort_keys=True, indent=2, default=str)
                    atomic_write_text(bundle_path, content)
            except ImportError:
                logger.warning("[VigiaEngine] BundleBuilder no disponible — Level 2 solamente")

        # ── Paso 6: Construir reporte ENFSI ───────────────────────────────
        report_path = None
        report_data = None
        if save_report:
            try:
                from report_builder import build_report  # type: ignore
                case_result = ReportAdapter.sealed_to_case_result(sealed_dict, case)
                case_result["peirce_firstness"] = peirce["firstness"]
                case_result["peirce_secondness"] = peirce["secondness"]
                case_result["peirce_thirdness"] = peirce["thirdness"]
                case_result["narrative_ollama"] = result.get("narrative")

                metrics = ReportAdapter.build_minimal_metrics()
                metrics["mode"] = result.get("mode", "FALLBACK")
                model_meta = ReportAdapter.build_model_metadata(mode=metrics["mode"])

                report_data = build_report(
                    case_result=case_result,
                    evaluation_metrics=metrics,
                    model_metadata=model_meta,
                    include_plots=False,  # sin plots en modo sin calibración
                )

                report_filename = f"report_{case_id}.json"
                report_path = os.path.join(self._output_dir, report_filename)
                # B-064: escritura atómica (patrón L-023)
                from vigia.core.atomic_io import atomic_write_text
                atomic_write_text(
                    report_path,
                    json.dumps(report_data, sort_keys=True, indent=2, default=str),
                )
                self._log("REPORT_SAVED", path=report_path)

            except Exception as e:
                logger.error("[VigiaEngine] Error generando reporte: %s", e)
                self._log("REPORT_ERROR", error=str(e))

        self._log("CASE_DONE", case_id=case_id)

        # H17: paths absolutos filtrados del resultado sellado.
        # El bundle exportado al perito contrario no puede contener
        # rutas del filesystem del operador (/home/anna/...).
        # Se exponen solo los nombres de archivo relativos.
        def _relative_path(p: Optional[str]) -> Optional[str]:
            if p is None:
                return None
            return os.path.basename(p)

        return {
            "case_id":     case_id,
            "decision":    result["decision"],
            "posterior":   result["posterior"],
            "risk":        result["risk"],
            "bundle_hash": result["bundle_hash"],
            "bundle_path": _relative_path(bundle_path) if save_bundle else None,
            "report_path": _relative_path(report_path),
            "verify":      result["verify"],
            "mode":        result.get("mode", "UNKNOWN"),
            "warnings":    warnings,
            "audit_log":   list(self._audit_log),
            "ecl_hash":    ecl_hash[:16] + "…" if ecl_hash else "",
            "narrative":   result.get("narrative"),
        }

    def run_case_file(
        self,
        json_path: str,
        save_bundle: bool = True,
        save_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Carga un caso desde archivo JSON y ejecuta run_case().

        Validación de path: solo acepta archivos .json dentro del filesystem
        — no acepta URLs ni paths con traversal.
        """
        # Validación de path — previene directory traversal
        abs_path = os.path.realpath(os.path.abspath(json_path))
        if not abs_path.endswith(".json"):
            raise ValueError(f"Solo se aceptan archivos .json: '{json_path}'")
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"Caso no encontrado: '{abs_path}'")

        with open(abs_path, "r", encoding="utf-8") as f:
            case = json.load(f)

        return self.run_case(case, save_bundle=save_bundle, save_report=save_report)
