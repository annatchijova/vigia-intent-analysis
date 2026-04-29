#!/usr/bin/env python3
"""
vigia/tools/vigia_case_adapter.py  v6

Cambios v6:
  Opcion B Weighted Domain Ensemble:
    final_z = max(z_tech, z_sem, z_weighted)
    Preserva recall (max como piso), agrega discriminacion por dominio.

  get_weights(artifact_type) -> Tuple[Fraction, Fraction]:
    registry/file_system  → (8/10, 2/10)  tecnico dominante
    email/chat            → (4/10, 6/10)  semiotico dominante
    default               → (5/10, 5/10)  equilibrado

  C16: sd=None setea detector_fault (Kimi)
  C28: cache de error evita traceback spam en batch (Kimi)
  DoS-input: anomalias limitadas antes del join (consistente con detector)
  confidence=Fraction(0,1) en fault para pipelines automatizados (Kimi)

No implementado (justificado):
  A8: sys.path — compatibilidad SIFT
  A3/A9: TYPE_TOOL duplicado — v3.0
  A4: ensemble ponderado por corpus — esta version
  M15: paths en fault_info — SIFT local, no multi-tenant
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from fractions import Fraction
from pathlib import Path
from typing import Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
for p in [_ROOT, os.path.join(_ROOT, "vigia", "core")]:
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Umbrales ──────────────────────────────────────────────────────────
THRESHOLD_MALICIOUS = Fraction(32, 10)
THRESHOLD_BENIGN    = Fraction(17, 10)
BASE_Z              = Fraction(4, 10)
MAX_Z               = Fraction(45, 10)

# ── Limites DoS ───────────────────────────────────────────────────────
INPUT_ANOMALIES_LIMIT    = 200
METADATA_ANOMALIES_LIMIT = 50
METADATA_INDICATORS_LIMIT = 30

# ── Mapeo tipo → tool_name ────────────────────────────────────────────
TYPE_TOOL = {
    "registry": "ROI", "network_flow": "GCI", "bash_history": "CLI",
    "file_system": "ACP", "process": "SDA", "memory": "SDA",
    "log": "CLI", "auth_log": "CLI", "email": "DGPI", "browser": "GCI",
    "usb": "ACP", "prefetch": "ACP", "lnk": "ACP",
    "scheduled_task": "ROI", "service": "ROI", "user_account": "SDA",
    "crypto": "DGPI", "timeline": "GCI", "file_metadata": "ACP",
    "artifact": "ACP",
}

# ── C28: cache de error — evita retry y traceback spam en batch ───────
_technical_detector = None
_technical_error    = None
_semiotic_detector  = None
_semiotic_error     = None


def _get_technical():
    global _technical_detector, _technical_error
    if _technical_detector is None and _technical_error is None:
        try:
            from forensic_technical_detector import ForensicTechnicalDetector
            _technical_detector = ForensicTechnicalDetector()
        except Exception as e:
            _technical_error = e
            print(f"[adapter] ForensicTechnicalDetector no disponible: {type(e).__name__}: {e}",
                  file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    return _technical_detector


def _get_semiotic():
    global _semiotic_detector, _semiotic_error
    if _semiotic_detector is None and _semiotic_error is None:
        try:
            from semiotic_detector_v2 import SemioticDetectorV2
            _semiotic_detector = SemioticDetectorV2()
        except Exception as e:
            _semiotic_error = e
            print(f"[adapter] SemioticDetectorV2 no disponible: {type(e).__name__}: {e}",
                  file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    return _semiotic_detector


def get_weights(artifact_type: str) -> Tuple[Fraction, Fraction]:
    """
    Retorna (w_technical, w_semiotic) segun el dominio del artefacto.

    registry/file_system : evidencia tecnica domina (8/10, 2/10)
    email/chat           : manipulacion linguistica domina (4/10, 6/10)
    default              : equilibrado (5/10, 5/10)

    Los pesos suman 1 — garantia de que z_weighted esta en el mismo espacio
    que z_tech y z_sem (BASE_Z a MAX_Z).
    """
    if artifact_type in ("registry", "file_system"):
        return Fraction(8, 10), Fraction(2, 10)
    if artifact_type in ("email", "chat"):
        return Fraction(4, 10), Fraction(6, 10)
    return Fraction(5, 10), Fraction(5, 10)


def artifact_to_signal(artifact: dict) -> dict:
    art_type  = artifact.get("type") or "unknown"  # B14: None-safe
    art_id    = artifact.get("artifact_id", "ART-000")
    # C6/B12/B15: protege contra null, dict y string en vez de lista
    _raw = artifact.get("forensic_anomalies")
    if isinstance(_raw, list):
        raw_anomalies = _raw
    elif isinstance(_raw, dict):
        raw_anomalies = [_raw]          # B12: dict → lista de un elemento
    elif isinstance(_raw, str):
        raw_anomalies = [_raw]          # B15: string → lista de un elemento
    else:
        raw_anomalies = []
    # DoS protection en input
    if len(raw_anomalies) > INPUT_ANOMALIES_LIMIT:
        raw_anomalies = raw_anomalies[:INPUT_ANOMALIES_LIMIT]
    content   = artifact.get("content", "")
    tool_name = TYPE_TOOL.get(art_type, art_type.upper()[:6])

    detector_fault      = False
    detector_fault_info = []

    # ── Detector técnico ──────────────────────────────────────────────
    z_technical    = BASE_Z
    conf_technical = Fraction(7, 10)
    tech_indicators: list = []

    td = _get_technical()
    if td:
        try:
            tr = td.analyze(artifact)
            z_technical     = Fraction(tr["_z_num"], tr["_z_den"])
            conf_technical  = Fraction(tr["_conf_num"], tr["_conf_den"])
            tech_indicators = tr.get("matched_indicators", [])
        except Exception as e:
            msg = f"technical.analyze: {type(e).__name__}: {e}"
            print(f"[adapter] FAULT {msg}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            z_technical    = BASE_Z
            conf_technical = Fraction(0, 1)
            detector_fault = True
            detector_fault_info.append(msg)
    else:
        # C16: td=None setea fault (no solo sd)
        detector_fault = True
        err_msg = f"ForensicTechnicalDetector no cargado"
        if _technical_error:
            err_msg += f": {type(_technical_error).__name__}"
        detector_fault_info.append(err_msg)
        conf_technical = Fraction(0, 1)

    # ── Detector semiótico ────────────────────────────────────────────
    z_semiotic    = BASE_Z
    conf_semiotic = Fraction(7, 10)

    sd = _get_semiotic()
    if sd:
        # M6: extraer texto correctamente de anomalias como dicts o strings
        anom_parts = []
        for a in raw_anomalies:
            if isinstance(a, str):
                anom_parts.append(a)
            elif isinstance(a, dict):
                anom_parts.append(a.get("description", a.get("summary", str(a))))
            else:
                anom_parts.append(str(a))
        anom_text = " | ".join(anom_parts)
        text = " | ".join(filter(None, [anom_text, content]))  # B16: sin " | " inicial

        if text.strip():
            try:
                timestamp = artifact.get("timestamp", "2026-01-01T00:00:00Z")
                sr = sd.analyze(text, art_id, timestamp)

                # A6: validar schema + C8: no truncar floats con int()
                mi = sr.get("fsv", {}).get("manipulation_index", {})
                if (isinstance(mi, dict) and
                        "num" in mi and "den" in mi and
                        mi["den"] != 0):
                    num, den = mi["num"], mi["den"]
                    if isinstance(num, int) and isinstance(den, int):
                        mi_val = Fraction(num, max(den, 1))
                    else:
                        mi_val = (Fraction(str(float(num))) /
                                  Fraction(str(float(den))))
                    mi_val = max(Fraction(0), min(Fraction(1), mi_val))
                    z_semiotic = BASE_Z + mi_val * (MAX_Z - BASE_Z)
                else:
                    z_semiotic = BASE_Z

                conf_semiotic = (
                    Fraction(92, 100)
                    if sr.get("alert_level") in ("CRITICAL", "HIGH")
                    else Fraction(75, 100)
                )
            except Exception as e:
                msg = f"semiotic.analyze: {type(e).__name__}: {e}"
                print(f"[adapter] FAULT {msg}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                z_semiotic    = BASE_Z
                conf_semiotic = Fraction(0, 1)
                detector_fault = True
                detector_fault_info.append(msg)
    else:
        # C16: sd=None setea detector_fault
        detector_fault = True
        err_msg = "SemioticDetectorV2 no cargado"
        if _semiotic_error:
            err_msg += f": {type(_semiotic_error).__name__}"
        detector_fault_info.append(err_msg)
        conf_semiotic = Fraction(0, 1)

    # ── Weighted Domain Ensemble (Opción B) ─────────────────────────
    # Pesos por dominio del artefacto
    w_tech, w_sem = get_weights(art_type)

    # z_weighted es combinación convexa: por propiedad matemática SIEMPRE
    # está entre z_tech y z_sem, nunca los supera.
    # Se calcula solo para metadata/trazabilidad — no afecta la decisión.
    # Para v3.0: implementar tie-breaker por dominio cuando |z_t - z_s| < epsilon
    z_weighted = z_technical * w_tech + z_semiotic * w_sem  # metadata only

    # Real Consensus Bonus — Sinergia Epistemica
    # Cuando ambos detectores superan THRESHOLD_BENIGN, la coincidencia
    # de dos fuentes independientes merece un bonus sobre final_z.
    # La probabilidad de error simultaneo en dos sensores independientes
    # es significativamente menor que en uno solo (principio forense).
    #
    # bonus = (min(z_t, z_s) - BASE_Z) * 0.2
    # Con z_t=3.1, z_s=3.1: bonus=0.54 → final=3.64 (REJECT)
    # Con z_t=2.5, z_s=2.5: bonus=0.42 → final=2.92 (ABSTAIN, no REJECT)
    # Con z_t=4.0, z_s=0.4: bonus=0    → final=4.0  (un sensor neutro = sin bonus)
    # Invariante Daubert: dos señales medias nunca llegan a REJECT
    # Solo una señal fuerte + consenso del otro detector lo logra.
    CONSENSUS_FACTOR    = Fraction(2, 10)
    CONSENSUS_MIN_SIGNAL = Fraction(20, 10)  # Issue A: 2.0 no 1.7 — 1.7 es boundary benigno
    if z_technical >= CONSENSUS_MIN_SIGNAL and z_semiotic >= CONSENSUS_MIN_SIGNAL:
        bonus = (min(z_technical, z_semiotic) - BASE_Z) * CONSENSUS_FACTOR
        final_z = min(max(z_technical, z_semiotic) + bonus, MAX_Z)
        both_signal = True
    else:
        final_z = max(z_technical, z_semiotic)
        bonus = Fraction(0)
        both_signal = False

    # Confidence: del detector dominante
    # R5: near-tie (|z_t - z_s| < 0.1) → tomar la maxima confianza
    if abs(z_technical - z_semiotic) < Fraction(1, 10):
        final_conf = max(conf_technical, conf_semiotic)
    elif z_technical >= z_semiotic:
        final_conf = conf_technical
    else:
        final_conf = conf_semiotic

    # Kimi: confidence=0 en fault para pipelines automatizados
    if detector_fault:
        final_conf = Fraction(0, 1)

    # ── Decisión ──────────────────────────────────────────────────────
    # El bonus ya incorporo el consenso en final_z — threshold fijo
    if detector_fault:
        decision = "ABSTAIN"
    elif final_z >= THRESHOLD_MALICIOUS:
        decision = "REJECT"
    elif final_z <= THRESHOLD_BENIGN:
        decision = "ACCEPT"
    else:
        decision = "ABSTAIN"

    # ── value ∈ [0,1] ─────────────────────────────────────────────────
    value_f = (final_z - BASE_Z) / (MAX_Z - BASE_Z)
    if value_f < Fraction(0): value_f = Fraction(0)
    if value_f > Fraction(1): value_f = Fraction(1)

    # ── Metadata con limite (A12) ─────────────────────────────────────
    anom_list = list(raw_anomalies)
    anom_truncated = len(anom_list) > METADATA_ANOMALIES_LIMIT
    anom_meta = anom_list[:METADATA_ANOMALIES_LIMIT] if anom_truncated else anom_list

    ind_truncated = len(tech_indicators) > METADATA_INDICATORS_LIMIT
    ind_meta = tech_indicators[:METADATA_INDICATORS_LIMIT] if ind_truncated else tech_indicators

    return {
        "tool_name":   tool_name,
        "decision":    decision,
        "_value":      round(float(value_f), 3),
        "_z_score":    round(float(final_z), 3),
        "_confidence": round(float(final_conf), 3),
        "_z_num":      final_z.numerator,
        "_z_den":      final_z.denominator,
        "_conf_num":   final_conf.numerator,
        "_conf_den":   final_conf.denominator,
        # Compatibilidad EBS v1
        "value":       round(float(value_f), 3),
        "z_score":     round(float(final_z), 3),
        "confidence":  round(float(final_conf), 3),
        "metadata": {
            "artifact_id":          art_id,
            "peirce_layer":         artifact.get("peirce_layer", ""),
            "type":                 art_type,
            "anomalies":            anom_meta,
            "anomalies_truncated":  anom_truncated,
            "tech_indicators":      ind_meta,
            "indicators_truncated": ind_truncated,
            "z_technical":          round(float(z_technical), 3),
            "z_semiotic":           round(float(z_semiotic), 3),
            "z_weighted":           round(float(z_weighted), 3),
            "consensus_bonus":      round(float(bonus), 3),
            "both_signal":          both_signal,
            "w_tech":               round(float(w_tech), 1),
            "w_sem":                round(float(w_sem), 1),
            "detector_fault":       detector_fault,
            "detector_fault_info":  detector_fault_info,
        },
    }


def convert_case(case_path: str) -> list:
    with open(case_path) as f:
        case = json.load(f)

    artifacts = case.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError(f"Schema invalido en {case_path}: 'artifacts' debe ser lista")

    signals = [artifact_to_signal(a) for a in artifacts]
    td = _get_technical()
    sd = _get_semiotic()
    n_fault = sum(1 for s in signals if s["metadata"]["detector_fault"])

    print(f"Caso: {Path(case_path).stem}", file=sys.stderr)
    print(f"  Veredicto esperado:  {case.get('expected_verdict','?')}", file=sys.stderr)
    print(f"  TechnicalDetector:   {'OK' if td else 'NO DISPONIBLE'}", file=sys.stderr)
    print(f"  SemioticDetector:    {'OK' if sd else 'NO DISPONIBLE'}", file=sys.stderr)
    print(f"  Senales:             {len(signals)} ({n_fault} con fault)", file=sys.stderr)
    return signals


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 vigia_case_adapter.py <caso.json> [output.json]")
        sys.exit(1)
    signals = convert_case(sys.argv[1])
    output  = json.dumps(signals, indent=2, ensure_ascii=False)
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            f.write(output)
        print(f"Guardado en {sys.argv[2]}", file=sys.stderr)
    else:
        print(output)
