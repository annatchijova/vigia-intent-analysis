"""
B-116 — SignalQualityGate en MODO SOMBRA (WARN informativo).

Decisión doctrinal (Anna, 2026-07-22, sesión B-116 condición 4): los checks
de diversidad/uniformidad del gate NO actúan como cap de veredicto — el
scorer ya aplica su propio Daubert Corroboration Gate, y el check de
uniformidad del gate contradice la doctrina B-171 (STATISTICAL_UNIFORMITY
como señal de fabricación). El gate se cablea como WARN: evalúa, deja
constancia en el resultado del scorer, y NUNCA toca veredicto, score ni
confidence. Ver docs/B116_CONDITION4_DESIGN.md §4.

Este módulo NO participa del path de decisión. Sus floats son material de
narrativa/observabilidad, no de scoring (invariante 4 del CLAUDE.md intacto).

Proveniencia de la línea base (claim-provenance):
    Dataset : data/signal_calibration_dataset_20260709.json (Tanda C)
    SHA-256 : 60023fd5aef6bf41… (primeros 16 hex del archivo completo)
    Población benigna: ground_truth ∈ {NOISE, BENIGN}, n=106 señales
    Método  : mediana y MAD por evidence_type con n≥5; piso MAD=0.05;
              z = (raw − mediana) / (1.4826·MAD). Extraído 2026-07-22 por
              scripts/dryrun_b116_mode_c.py::build_baseline (reproducible).
    Falsador: si el dataset de calibración se regenera con más población
              benigna, estas constantes deben re-extraerse y este bloque
              re-sellarse con el nuevo SHA.
"""
from __future__ import annotations

from typing import Any, Dict, List

_BASELINE_DATASET = "signal_calibration_dataset_20260709.json"
_BASELINE_SHA256_16 = "60023fd5aef6bf41"
_MAD_TO_SIGMA = 1.4826

# (mediana_benigna, MAD_benigna_con_piso) — congeladas, ver docstring.
_BASELINE: Dict[str, tuple] = {
    "memory_process": (0.05, 0.05),
    "log_entry":      (0.70, 0.12),
    "file_hash":      (0.02, 0.05),
    "document":       (0.00, 0.05),
    "file_metadata":  (0.05, 0.05),
}
_POOLED = (0.05, 0.05)


def _z(raw: float, evidence_type: str) -> float:
    med, mad = _BASELINE.get(evidence_type, _POOLED)
    return (raw - med) / (_MAD_TO_SIGMA * mad)


def shadow_signal_quality(artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evalúa SignalQualityGate en modo sombra sobre los artefactos del caso.

    Contrato:
      - NUNCA lanza: cualquier fallo retorna {"error": ...} y el scorer
        sigue intacto.
      - NUNCA muta `artifacts` ni influye en el veredicto.
      - Artefactos sin raw_score numérico se cuentan como no-medibles
        (honest-degradation: no se imputa 0.0).
    """
    try:
        from vigia.core.signal_quality_gate import SignalQualityGate

        signals = []
        unmeasured = 0
        for art in artifacts:
            if not isinstance(art, dict):
                unmeasured += 1
                continue
            raw = art.get("raw_score")
            if not isinstance(raw, (int, float)):
                unmeasured += 1
                continue
            etype = str(art.get("evidence_type", "default"))
            signals.append({
                "tool_name": art.get("tool_name"),
                "source_tool": art.get("source_tool"),
                "evidence_type": etype,
                "type": art.get("type"),
                "z_score": _z(float(raw), etype),
            })

        result = SignalQualityGate().evaluate(signals)
        return {
            "mode": "shadow_warn",
            "doctrine": "WARN informativo — no cap (decisión 2026-07-22)",
            "passed": bool(result.passed),
            "reason_code": str(result.reason_code),
            "reason_detail": str(result.reason_detail),
            "n_signals_evaluated": len(signals),
            "n_signals_unmeasured": unmeasured,
            "baseline_provenance": {
                "dataset": _BASELINE_DATASET,
                "sha256_16": _BASELINE_SHA256_16,
            },
        }
    except Exception as exc:  # el modo sombra jamás voltea el scoring
        return {"mode": "shadow_warn", "error": f"{type(exc).__name__}: {exc}"}
