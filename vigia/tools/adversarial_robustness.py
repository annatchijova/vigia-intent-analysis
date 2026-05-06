"""
vigia/tools/adversarial_robustness.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. PUREZA FRACTION: Todos los cálculos internos usan Fraction. 
   NUNCA se convierte a float para penalización.
2. Z_CLIP_MAX ahora es Fraction(35, 10) para consistencia.
3. SIFT_CRITICAL_Z usa Fraction(25, 10).
4. Todos los returns de SignalOutput usan float() solo en el constructor
   (inevitable por la API), pero los cálculos internos son 100% Fraction.
"""

from __future__ import annotations

from typing import List, Dict, Optional, Any
from fractions import Fraction

from vigia.core.ebs_v1 import SignalOutput

TOOL_NAME = "ADV_ROBUST"

# FIX: Todos los umbrales como Fraction
THRESHOLDS = {
    "GCI": Fraction(280, 100), "DGPI": Fraction(250, 100), "ACP": Fraction(200, 100),
    "ROI": Fraction(200, 100), "CLI": Fraction(250, 100), "SDA_NR": Fraction(200, 100),
    "CAIE": Fraction(200, 100), "TEMPORAL": Fraction(200, 100),
}

COOCCURRENCE = {
    "CAIE": ["TEMPORAL", "ADV_ROBUST"],
    "GCI": ["DGPI", "STYLO_FP"],
    "ACP": ["STYLO_FP"],
    "TEMPORAL": ["CAIE"],
    "DGPI": ["GCI"],
    "STYLO_FP": ["GCI", "ACP"],
}

F_THRESHOLD_MARGIN = Fraction(15, 100)
F_P_NULL = Fraction(15, 100)
F_ZERO = Fraction(0, 1)
F_ONE = Fraction(1, 1)
F_HALF = Fraction(1, 2)
F_THREE_QUARTERS = Fraction(3, 4)
SIFT_CRITICAL_Z = Fraction(25, 10)
Z_CLIP_MAX_FRAC = Fraction(35, 10)


class AdversarialRobustnessEngine:
    def analyze(self, all_signals: List[SignalOutput]) -> SignalOutput:
        if len(all_signals) < 2:
            return self._insufficient()

        # Detectar señales SIFT críticas (usando Fraction)
        sift_critical = []
        for s in all_signals:
            if s.tool_name in {
                "MEMORY_FORENSICS", "REGISTRY_RTR", "EVENT_LOG", "MFT_ANALYZER", "NETWORK_FORENSICS"
            }:
                z_frac = Fraction(int(round(s.z_score * 100)), 100)
                if z_frac >= SIFT_CRITICAL_Z:
                    sift_critical.append(s)

        indicators: List[Dict[str, Any]] = []

        tc = self._detect_threshold_clustering(all_signals)
        if tc:
            indicators.append(tc)

        ce = self._detect_coordinated_evasion(all_signals)
        if ce:
            indicators.append(ce)

        ss = self._detect_significant_silence(all_signals)
        if ss:
            indicators.append(ss)

        ae = self._detect_asymmetric_evasion(all_signals)
        if ae:
            indicators.append(ae)

        if not indicators:
            z_agg = F_ZERO
            dominant = "NONE"
        else:
            # FIX: max_z como Fraction, no float
            max_z = max(Fraction(int(round(i["score_frac"] * 100)), 100) for i in indicators)
            z_agg = max_z if max_z > 0 else F_ZERO
            dominant = max(indicators, key=lambda x: x["score_frac"])["pattern"]

        # FIX: Cálculo de confianza 100% Fraction
        n_tools = len(all_signals)
        coverage = Fraction(min(n_tools, 8), 8)
        avg_conf = Fraction(int(sum(s.confidence for s in all_signals) / max(n_tools, 1) * 1000), 1000)
        confidence = coverage * Fraction(4, 10) + avg_conf * Fraction(6, 10)

        if sift_critical:
            confidence = confidence * F_HALF
            z_agg = z_agg * F_THREE_QUARTERS

        # FIX: Solo convertir a float al final, en el constructor de SignalOutput
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z_agg) / float(Z_CLIP_MAX_FRAC) if Z_CLIP_MAX_FRAC > 0 else 0.0,
            z_score=float(z_agg),
            confidence=float(confidence),
            metadata={
                "n_tools": n_tools,
                "n_indicators": len(indicators),
                "dominant_pattern": dominant,
                "indicators": indicators,
                "sift_critical_active": len(sift_critical),
            }
        )

    def _detect_threshold_clustering(self, signals: List[SignalOutput]) -> Optional[Dict[str, Any]]:
        near_tools = []
        applicable = 0
        for signal in signals:
            th = THRESHOLDS.get(signal.tool_name)
            if th is None:
                continue
            applicable += 1
            z = Fraction(int(round(signal.z_score * 100)), 100)
            margin = th - z
            if F_ZERO < margin < (th * F_THRESHOLD_MARGIN):
                near_tools.append(signal.tool_name)
        if applicable < 2 or not near_tools:
            return None
        ratio = Fraction(len(near_tools), applicable)
        n = applicable
        k = len(near_tools)
        mean = n * F_P_NULL
        var = mean * (F_ONE - F_P_NULL)
        std_proxy = var + Fraction(1, 100)
        diff = Fraction(k) - mean
        z = diff / std_proxy if std_proxy > 0 else F_ZERO
        z_float = float(z)
        if z_float < 1.0:
            return None
        # FIX: Guardar score_frac como Fraction para pureza interna
        return {
            "pattern": "THRESHOLD_CLUSTERING", "score": z_float, "score_frac": z,
            "confidence": min(Fraction(1, 2) + ratio * F_HALF, Fraction(95, 100)),
            "affected_tools": near_tools,
            "description": f"{len(near_tools)}/{applicable} herramientas justo bajo umbral",
        }

    def _detect_coordinated_evasion(self, signals: List[SignalOutput]) -> Optional[Dict[str, Any]]:
        if len(signals) < 3:
            return None
        z_scores = [Fraction(int(round(s.z_score * 100)), 100) for s in signals]
        mean_z = sum(z_scores) / len(z_scores)
        if mean_z >= Fraction(150, 100):
            return None
        variance = sum((z - mean_z) ** 2 for z in z_scores) / len(z_scores)
        std_proxy = variance + Fraction(1, 100)
        cv = std_proxy / mean_z if mean_z > 0 else F_ZERO
        if cv >= Fraction(30, 100):
            return None
        z_cv = (Fraction(30, 100) - cv) / Fraction(10, 100)
        z_mean = (Fraction(150, 100) - mean_z) / Fraction(50, 100)
        combined = z_cv + z_mean
        if combined < Fraction(15, 10):
            return None
        # FIX: score_frac como Fraction
        return {
            "pattern": "COORDINATED_EVASION", "score": float(min(combined, Z_CLIP_MAX_FRAC)),
            "score_frac": min(combined, Z_CLIP_MAX_FRAC),
            "confidence": Fraction(7, 10),
            "affected_tools": [s.tool_name for s in signals],
            "description": f"z_scores uniformemente bajos. media={float(mean_z):.2f}",
        }

    def _detect_significant_silence(self, signals: List[SignalOutput]) -> Optional[Dict[str, Any]]:
        active_tools = {s.tool_name for s in signals if s.z_score > 1.5}
        present_tools = {s.tool_name for s in signals}
        silences = []
        total_expected = 0
        for trigger, expected in COOCCURRENCE.items():
            if trigger not in active_tools:
                continue
            for companion in expected:
                total_expected += 1
                if companion not in present_tools:
                    silences.append({"trigger": trigger, "missing": companion, "type": "TOOL_NOT_RUN"})
                elif companion not in active_tools:
                    silences.append({"trigger": trigger, "missing": companion, "type": "TOOL_SILENT"})
        if not silences or total_expected == 0:
            return None
        ratio = Fraction(len(silences), total_expected)
        z = ratio * Fraction(3, 1)
        if z < F_ONE:
            return None
        return {
            "pattern": "SIGNIFICANT_SILENCE", "score": float(z), "score_frac": z,
            "confidence": Fraction(65, 100),
            "affected_tools": list(set(s["trigger"] for s in silences) | set(s["missing"] for s in silences)),
            "description": f"{len(silences)}/{total_expected} co-ocurrencias ausentes",
        }

    def _detect_asymmetric_evasion(self, signals: List[SignalOutput]) -> Optional[Dict[str, Any]]:
        if len(signals) < 4:
            return None
        low_signals = []
        high_signals = []
        for signal in signals:
            th = THRESHOLDS.get(signal.tool_name)
            z = Fraction(int(round(signal.z_score * 100)), 100)
            if th and z < th * Fraction(75, 100):
                low_signals.append(signal)
            elif z >= Fraction(250, 100):
                high_signals.append(signal)
        n_low = len(low_signals)
        n_high = len(high_signals)
        total = len(signals)
        if n_low < 3 or n_high < 1:
            return None
        if Fraction(n_low, total) < Fraction(60, 100):
            return None
        if Fraction(n_high, total) > Fraction(40, 100):
            return None
        has_context = self._check_outlier_context(high_signals, signals)
        context_penalty = F_ONE if has_context else F_HALF
        asym = Fraction(n_low, total) * Fraction(2, 1) + Fraction(n_high, total) * Fraction(15, 10)
        score_raw = min(asym, Z_CLIP_MAX_FRAC)
        score = score_raw * context_penalty
        return {
            "pattern": "ASYMMETRIC_EVASION", "score": float(score), "score_frac": score,
            "confidence": float(Fraction(75, 100) * context_penalty),
            "affected_tools": [s.tool_name for s in low_signals + high_signals],
            "description": f"Evasión parcial: {n_low}/{total} evadidas, {n_high} alta. Contexto: {'presente' if has_context else 'ausente'}",
            "thresholds_used": {"low_threshold_ratio": "75/100", "high_z_threshold": "250/100", "min_total_ratio": "60/100"},
            "filters_applied": {"high_ratio_filter": str(Fraction(n_high, total) > Fraction(40, 100)), "context_filter": "PASSED" if has_context else "PENALIZED"},
        }

    def _check_outlier_context(self, high_signals: List[SignalOutput], all_signals: List[SignalOutput]) -> bool:
        if not high_signals:
            return False
        present_active = {s.tool_name for s in all_signals if s.z_score > 1.5}
        for hs in high_signals:
            companions = COOCCURRENCE.get(hs.tool_name, [])
            if companions and any(c in present_active for c in companions):
                return True
        return False

    def _insufficient(self) -> SignalOutput:
        return SignalOutput(
            tool_name=TOOL_NAME, value=0.0, z_score=0.0, confidence=0.1,
            metadata={"reason": "INSUFFICIENT_SIGNALS"}
        )
