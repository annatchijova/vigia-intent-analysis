"""
vigia/core/signal_mapper.py

Mapeador de señales con Gate de Causalidad (CCS - Causal Closure Score).
El CCS actúa como filtro pasabajos: si ccs < 0.5, el signal se fuerza a ABSTAIN.

FIX P0: CausalClosureScore integrado como gate de seguridad anti-deepfake.
FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX


@dataclass(frozen=True)
class CausalClosureScore:
    """
    Score de Cierre Causal.
    Mide qué tan "cerrado" causalmente es un conjunto de señales.

    - ccs = 1.0: Todas las señales tienen explicación causal mutua (coherente)
    - ccs = 0.0: Señales aisladas sin conexión causal (posible deepfake/inyección)

    Fórmula: ccs = (señales_con_causa_explicada / total_señales) * (1 - causal_entropy)
    """
    score: Fraction
    explained_signals: int
    total_signals: int
    causal_entropy: Fraction
    missing_causes: List[str]


class SignalMapper:
    """
    Mapea señales crudas a SignalOutput con validación de causalidad.

    El CCS Gate:
    - Si ccs >= 0.5: Señal pasa normalmente
    - Si ccs < 0.5: Señal se fuerza a ABSTAIN (z_score = 0, confidence = 0)
    """

    CCS_THRESHOLD = Fraction(1, 2)  # 0.5
    CCS_ABSTAIN_Z = Fraction(0, 1)
    CCS_ABSTAIN_CONF = Fraction(0, 1)

    def __init__(self):
        self._history: List[SignalOutput] = []

    def from_ccs(
        self,
        raw_signals: List[Dict[str, Any]],
        causal_links: Optional[Dict[str, List[str]]] = None,
    ) -> List[SignalOutput]:
        """
        Construye SignalOutputs desde señales crudas aplicando CCS Gate.

        Args:
            raw_signals: Lista de dicts con keys: tool_name, value, z_score, confidence, metadata
            causal_links: Dict {signal_id: [causes]} describiendo dependencias causales

        Returns:
            Lista de SignalOutput con CCS aplicado
        """
        if not raw_signals:
            return []

        # Calcular CCS para el conjunto
        ccs = self._calculate_ccs(raw_signals, causal_links or {})

        mapped: List[SignalOutput] = []

        for raw in raw_signals:
            tool_name = raw.get("tool_name", "UNKNOWN")
            value = raw.get("value", 0.0)
            z_score = raw.get("z_score", 0.0)
            confidence = raw.get("confidence", 0.0)
            metadata = raw.get("metadata", {})

            # FIX P0: Asegurar que metadata no contiene floats
            metadata = self._sanitize_metadata(metadata)

            # CCS Gate
            if ccs.score < self.CCS_THRESHOLD:
                # Forzar ABSTAIN
                mapped.append(SignalOutput(
                    tool_name=tool_name,
                    value=0.0,
                    z_score=0.0,
                    confidence=0.0,
                    metadata={
                        **metadata,
                        "ccs_gate": "ABSTAIN",
                        "ccs_score": str(ccs.score),
                        "ccs_reason": "Causal closure insuficiente",
                        "ccs_missing_causes": ccs.missing_causes,
                        "original_z_score": str(Fraction(int(round(z_score * 100)), 100)),
                        "original_confidence": str(Fraction(int(round(confidence * 1000)), 1000)),
                    }
                ))
            else:
                # Pasar normalmente con CCS en metadata
                mapped.append(SignalOutput(
                    tool_name=tool_name,
                    value=float(value),
                    z_score=float(z_score),
                    confidence=float(confidence),
                    metadata={
                        **metadata,
                        "ccs_gate": "PASS",
                        "ccs_score": str(ccs.score),
                        "ccs_explained": ccs.explained_signals,
                        "ccs_total": ccs.total_signals,
                    }
                ))

        self._history.extend(mapped)
        return mapped

    def _calculate_ccs(
        self,
        raw_signals: List[Dict[str, Any]],
        causal_links: Dict[str, List[str]],
    ) -> CausalClosureScore:
        """
        Calcula el Causal Closure Score.

        Una señal está "explicada causalmente" si:
        1. Tiene al menos una causa en causal_links, O
        2. Es una señal "raíz" (no necesita causa, ej: memory forensics)
        """
        total = len(raw_signals)
        if total == 0:
            return CausalClosureScore(
                score=Fraction(1, 1), explained_signals=0,
                total_signals=0, causal_entropy=Fraction(0, 1),
                missing_causes=[],
            )

        explained = 0
        missing = []

        # Señales raíz que no necesitan causa
        root_signals = {"MEMORY_FORENSICS", "DISK_FORENSICS", "MFT_ANALYZER", "REGISTRY_RTR", "NETWORK_FORENSICS", "EVENT_LOG", "PREFETCH_ANALYZER", "USB_DEVICE_TRACKER", "BROWSER_FORENSICS", "SHELLBAG_ANALYZER", "AMCACHE_SHIMCACHE"}

        for raw in raw_signals:
            sid = raw.get("signal_id", raw.get("tool_name", ""))
            causes = causal_links.get(sid, [])

            if sid in root_signals or causes:
                explained += 1
            else:
                missing.append(sid)

        # Entropía causal: cuántas señales comparten las mismas causas
        cause_counts: Dict[str, int] = {}
        for causes in causal_links.values():
            for cause in causes:
                cause_counts[cause] = cause_counts.get(cause, 0) + 1

        if cause_counts:
            from vigia.sift._math_utils import _entropy_shannon
            # FIX P2: Pasar lista de tokens para evitar colisiones
            entropy = _entropy_shannon([f"{k}:{v}" for k, v in sorted(cause_counts.items())])
            # Normalizar entropía a [0, 1]
            max_entropy = Fraction(47, 10)  # ~4.7 bits para charset típico
            normalized_entropy = min(entropy / max_entropy, Fraction(1, 1))
        else:
            normalized_entropy = Fraction(0, 1)

        # FIX P2 (V16/V20): CCS ahora usa ratio de explicación con techo de entropía.
        # La entropía ya no puede forzar ABSTAIN arbitrariamente.
        explained_ratio = Fraction(explained, total)
        # Entropía máxima real basada en número de causas únicas (no valor fijo)
        max_entropy_real = Fraction(len(cause_counts), 1) if cause_counts else Fraction(1, 1)
        if max_entropy_real > 0:
            normalized_entropy = min(entropy / max_entropy_real, Fraction(1, 1))
        else:
            normalized_entropy = Fraction(0, 1)
        # Penalización de entropía acotada: nunca reduce CCS por debajo de explained_ratio * 0.5
        entropy_factor = max(Fraction(1, 1) - normalized_entropy, Fraction(1, 2))
        ccs_score = explained_ratio * entropy_factor

        return CausalClosureScore(
            score=ccs_score,
            explained_signals=explained,
            total_signals=total,
            causal_entropy=normalized_entropy,
            missing_causes=missing,
        )

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        FIX P0: Elimina floats de metadata. Convierte a Fraction/str.
        """
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, float):
                # Convertir float a Fraction string
                clean[key] = str(Fraction(int(round(value * 1000)), 1000))
            elif isinstance(value, dict):
                clean[key] = self._sanitize_metadata(value)
            elif isinstance(value, list):
                clean[key] = [
                    str(Fraction(int(round(v * 1000)), 1000)) if isinstance(v, float) else v
                    for v in value
                ]
            else:
                clean[key] = value
        return clean

    def get_history(self) -> List[SignalOutput]:
        """Retorna historial de señales mapeadas."""
        return list(self._history)
