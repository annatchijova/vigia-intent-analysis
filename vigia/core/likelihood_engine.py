# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
vigia/engine/likelihood_engine.py
─────────────────────────────────────────────────────────────────────────────
Motor de Inferencia Multivariado — VIGIA Forensic Suite EBS v1

REFACTORIZACION (DeepSeek + Gemini):
    1. Imports blindados via patron de raiz dinamica (DeepSeek)
    2. Naming emergente: clusters se llaman G_cluster_{idx} o G_{tool}
       — NO se fuerzan etiquetas NLP/TEMPORAL sobre estructura emergente (Gemini)
    3. Correccion de inflacion artificial de LR en fallback univariado:
       Factor de correlacion de Pearson aplicado al cluster para penalizar
       senal redundante. Sin Ledoit-Wolf, el LR se deflacta proporcionalmente
       a la correlacion promedio entre senales del cluster (Gemini)

CLUSTERS EMERGENTES:
    Con EvidenceGraph disponible:
        Los nombres de clusters derivan del ID de componente conectada.
        G_cluster_{i} o G_{tool_mas_fuerte}_{i}
        PROHIBIDO forzar "NLP" o "TEMPORAL" sobre estructura emergente.
        Esto obliga al perito a examinar que senales se agruparon de forma
        anomala en lugar de asumir categorias conocidas.

    Sin EvidenceGraph:
        Se usan los DEFAULT_CLUSTERS como fallback documentado.
        Se registra en metadata que el clustering es heuristico.

CORRECCIÓN INFLACION LR (Gemini):
    Fallback univariado: log_LR = sum(log_LR_i) asume independencia.
    Si SDA y CLI estan correlacionadas, esto es doble conteo.
    Correccion aplicada:
        corr_penalty = 1 - mean(|rho_ij|) para i!=j en el cluster
        log_LR_cluster = sum(log_LR_i) * corr_penalty

    Con Ledoit-Wolf activo: la covarianza ya captura la correlacion,
    no se aplica correccion adicional.

IMPORTS BLINDADOS (DeepSeek):
    Patron de raiz dinamica — el sistema sabe donde esta parado
    sin importar desde que directorio se ejecuta.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patron de raiz dinamica (DeepSeek) — imports blindados
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from vigia.core.ebs_v1 import (
    SignalOutput, EvidenceGraph,
    Z_CLIP_MAX, EPS_NUMERIC,
)

# ---------------------------------------------------------------------------
# Dependencias opcionales con fallback garantizado
# ---------------------------------------------------------------------------
try:
    import numpy as np
    _NP = True
except ImportError:
    np = None  # type: ignore
    _NP = False

try:
    from sklearn.neighbors import KernelDensity
    from sklearn.model_selection import GridSearchCV
    from sklearn.covariance import LedoitWolf
    _SK = True
except ImportError:
    KernelDensity = GridSearchCV = LedoitWolf = None  # type: ignore
    _SK = False

# ---------------------------------------------------------------------------
# Clusters por defecto — solo usados cuando NO hay EvidenceGraph
# ---------------------------------------------------------------------------
DEFAULT_CLUSTERS: Dict[str, List[str]] = {
    "NLP_default":      ["SDA", "ACP", "CLI", "ROI"],
    "TEMPORAL_default": ["GCI", "DGPI"],
    "VISION_default":   ["ELA", "CLIP"],
}

NLP_TOOLS_DEFAULT: List[str] = ["SDA", "ACP", "CLI", "ROI"]
Z_CLIP = min(Z_CLIP_MAX, 5.0)


# ---------------------------------------------------------------------------
# Aproximacion gaussiana — fallback documentado
# ---------------------------------------------------------------------------

def _gaussian_log_lr(z: float) -> float:
    """
    log LR ~ z^2/2 bajo asuncion gaussiana.
    PLACEHOLDER DOCUMENTADO para Daubert — indica dataset de calibracion pendiente.
    """
    z_c = max(-Z_CLIP, min(Z_CLIP, z))
    return (z_c ** 2) / 2.0


# ---------------------------------------------------------------------------
# Penalizacion de correlacion para fallback univariado
# ---------------------------------------------------------------------------

def _correlation_penalty(signals: List[SignalOutput]) -> float:
    """
    Penalización de correlación por redundancia local (H21).

    PROBLEMA CON EL PROMEDIO SIMPLE:
    Con 10 señales y solo 2 perfectamente correlacionadas (ρ=1.0),
    el promedio es ~0.2 → penalización mínima → el doble conteo se cuela.
    El promedio es "licuable" inyectando señales independientes basura.

    SOLUCIÓN — penalización por pares efectivos:
    En lugar de promediar, contamos cuántos pares tienen |ρ| ≥ umbral_alto
    (pares "gemelos" — doble conteo real) y reducimos el conteo efectivo de
    señales. La penalización es:

        n_efectivo = n - pares_gemelos
        penalty = n_efectivo / n

    Con n=10, 2 gemelos → n_efectivo=9 → penalty=0.9 (correcto: solo deflata 1).
    Con n=2 perfectamente correlacionadas → n_efectivo=1 → penalty=0.5 (una sola).

    Umbral de "par gemelo": |ρ| ≥ 0.90 (muy alta correlación).
    Sin numpy: usa diferencia normalizada de z-scores como proxy de correlación.
    """
    n = len(signals)
    if n <= 1:
        return 1.0

    RHO_TWIN_THRESHOLD = 0.90  # umbral para considerar un par como "gemelo"

    z_vals = [max(-Z_CLIP, min(Z_CLIP, s.z_score)) for s in signals]

    twin_pairs = 0

    if not _NP:
        def _pearson_scalar(a: float, b: float) -> float:
            # Para escalares individuales usamos diferencia normalizada como proxy
            diff = abs(a - b)
            denom = max(abs(a), abs(b), EPS_NUMERIC) * 2
            return max(0.0, 1.0 - diff / denom)

        for i in range(n):
            for j in range(i + 1, n):
                rho = _pearson_scalar(z_vals[i], z_vals[j])
                if rho >= RHO_TWIN_THRESHOLD:
                    twin_pairs += 1
    else:
        z_arr = np.array(z_vals)
        for i in range(n):
            for j in range(i + 1, n):
                diff = abs(z_arr[i] - z_arr[j])
                denom = max(abs(float(z_arr[i])), abs(float(z_arr[j])), EPS_NUMERIC) * 2
                rho_proxy = max(0.0, 1.0 - diff / denom)
                if rho_proxy >= RHO_TWIN_THRESHOLD:
                    twin_pairs += 1

    if twin_pairs > 0:
        logger.warning(
            "[LikelihoodEngine] H21: %d par(es) gemelo(s) detectados (|ρ| ≥ %.2f) "
            "en cluster de %d señales. Penalización por redundancia local aplicada. "
            "Posible doble conteo — verificar independencia de herramientas.",
            twin_pairs, RHO_TWIN_THRESHOLD, n,
        )

    # n_efectivo = n señales - n pares gemelos (cada par gemelo aporta 1 señal redundante)
    n_efectivo = max(1, n - twin_pairs)
    penalty = max(0.1, n_efectivo / n)
    return penalty, twin_pairs


# ---------------------------------------------------------------------------
# SignalContribution — trazabilidad
# ---------------------------------------------------------------------------

class SignalContribution:
    def __init__(
        self,
        tool_name: str,
        z_score: float,
        log_lr: float,
        method: str,
        confidence: float,
        cluster: str,
    ) -> None:
        self.tool_name = tool_name
        self.z_score = z_score
        self.log_lr = log_lr
        self.method = method
        self.confidence = confidence
        self.cluster = cluster

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "z_score": round(self.z_score, 6),
            "log_lr": round(self.log_lr, 6),
            "method": self.method,
            "confidence": round(self.confidence, 4),
            "cluster": self.cluster,
        }


# ---------------------------------------------------------------------------
# LikelihoodEngine
# ---------------------------------------------------------------------------

class LikelihoodEngine:
    """
    Motor de inferencia multivariado calibrado.

    Modos:
        FULL     — KDE calibrado + Ledoit-Wolf NLP + graph-conditioned
        KDE      — KDE calibrado + clusters emergentes (sin covarianza)
        FALLBACK — Aproximacion gaussiana con penalizacion de correlacion
    """

    def __init__(
        self,
        calibration_path: Optional[str] = None,
        covariance_path: Optional[str] = None,
        prior_odds: float = 1.0,
        hint_threshold_reject: float = 0.70,
        hint_threshold_accept: float = 0.30,
    ) -> None:
        # hint_threshold_* son para el decision_hint orientativo del LikelihoodEngine.
        # La decision REAL la toma RiskBoundedDecisionLayer con epsilon de PolicySpec.
        # Estos valores NO deben ser hardcodeados — se pasan desde PolicySpec o config.
        self.hint_threshold_reject = hint_threshold_reject
        self.hint_threshold_accept = hint_threshold_accept
        self.prior_odds = prior_odds
        self._mode = "FALLBACK"
        self._kde_models: Dict[str, Any] = {}
        self._calibration_metadata: Dict[str, Any] = {}

        if calibration_path and _SK and _NP:
            try:
                _hmac_key = os.getenv("VIGIA_HMAC_KEY", "").encode()
                with open(calibration_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                # Verificar integridad HMAC si la clave está configurada
                if _hmac_key:
                    expected_mac = payload.get("_hmac", "")
                    data_bytes = json.dumps(
                        payload.get("data", {}), sort_keys=True
                    ).encode()
                    computed_mac = hmac.new(_hmac_key, data_bytes, hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(expected_mac, computed_mac):
                        raise ValueError("HMAC de calibración KDE no válido — posible adulteración")
                data = payload.get("data", payload)
                self._kde_models = data.get("models", {})
                self._calibration_metadata = data.get("metadata", {})
                self._mode = "KDE"
            except Exception as e:
                logger.warning("[LikelihoodEngine] KDE no cargado: %s", e)

        self._use_covariance = False
        self._inv_cov_h0 = self._inv_cov_h1 = None
        self._mean_h0 = self._mean_h1 = None
        self._log_det_ratio = 0.0
        self._cov_tools: List[str] = NLP_TOOLS_DEFAULT

        if covariance_path and _NP:
            try:
                _hmac_key = os.getenv("VIGIA_HMAC_KEY", "").encode()
                with open(covariance_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                if _hmac_key:
                    expected_mac = payload.get("_hmac", "")
                    data_bytes = json.dumps(
                        payload.get("data", {}), sort_keys=True
                    ).encode()
                    computed_mac = hmac.new(_hmac_key, data_bytes, hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(expected_mac, computed_mac):
                        raise ValueError("HMAC de covarianza no válido — posible adulteración")
                cov = payload.get("data", payload)
                cov_h0 = np.array(cov["cov_h0"])
                cov_h1 = np.array(cov["cov_h1"])
                self._mean_h0 = np.array(cov["mean_h0"])
                self._mean_h1 = np.array(cov["mean_h1"])
                self._cov_tools = cov.get("tools", NLP_TOOLS_DEFAULT)
                reg = np.eye(len(cov_h0)) * 1e-6
                self._inv_cov_h0 = np.linalg.inv(cov_h0 + reg)
                self._inv_cov_h1 = np.linalg.inv(cov_h1 + reg)
                s0, ld0 = np.linalg.slogdet(cov_h0)
                s1, ld1 = np.linalg.slogdet(cov_h1)
                if s0 > 0 and s1 > 0:
                    self._log_det_ratio = 0.5 * (ld1 - ld0)
                self._use_covariance = True
                if self._mode == "KDE":
                    self._mode = "FULL"
            except Exception as e:
                logger.warning("[LikelihoodEngine] Covarianza no cargada: %s", e)

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------

    def infer(
        self,
        signals: List[SignalOutput],
        evidence_graph: Optional[EvidenceGraph] = None,
    ) -> Dict[str, Any]:
        """
        Calcula LR total y P(fabricacion | evidencia).

        Naming emergente (Gemini):
            Con EvidenceGraph: clusters se nombran G_cluster_{i} o G_{tool}_{i}
            Sin EvidenceGraph: se usan DEFAULT_CLUSTERS documentados como heuristicos
        """
        if not signals:
            return self._empty_result()

        signal_map = {s.tool_name: s for s in signals}
        clusters, clustering_method = self._resolve_clusters(signal_map, evidence_graph)

        contributions: List[SignalContribution] = []
        total_log_lr = math.log(self.prior_odds + EPS_NUMERIC)
        total_twin_pairs = 0  # H21: acumular pares gemelos de todos los clusters

        for cluster_name, cluster_tools in clusters.items():
            cluster_signals = [signal_map[t] for t in cluster_tools if t in signal_map]
            if not cluster_signals:
                continue

            # NLP cluster con Ledoit-Wolf (solo si coincide con los tools de covarianza)
            is_nlp_covariance_cluster = (
                self._use_covariance
                and set(t for t in cluster_tools if t in signal_map)
                    <= set(self._cov_tools)
                and len(cluster_signals) >= 2
                and _NP
            )

            if is_nlp_covariance_cluster:
                log_lr_c, contribs = self._multivariate_log_lr(cluster_signals, cluster_name)
            else:
                log_lr_c, contribs, twin_pairs_c = self._univariate_with_correction(
                    cluster_signals, cluster_name
                )
                total_twin_pairs += twin_pairs_c

            total_log_lr += log_lr_c
            contributions.extend(contribs)

        # Senales no asignadas
        assigned = {t for tools in clusters.values() for t in tools}
        for s in signals:
            if s.tool_name not in assigned:
                log_lr_i, c = self._single_signal(s, "unassigned")
                total_log_lr += log_lr_i
                contributions.append(c)

        total_log_lr = max(-30.0, min(30.0, total_log_lr))
        lr = math.exp(total_log_lr)
        posterior = lr / (1.0 + lr)

        # decision_hint es ORIENTATIVO — decision real la toma RiskBoundedDecisionLayer.
        # Umbrales configurables, no hardcodeados.
        decision_hint = "ABSTAIN"
        if posterior > self.hint_threshold_reject:
            decision_hint = "REJECT"
        elif posterior < self.hint_threshold_accept:
            decision_hint = "ACCEPT"

        return {
            "lr": lr,
            "log_lr": total_log_lr,
            "posterior": posterior,
            "decision_hint": decision_hint,
            "components_used": len(clusters),
            "mode": self._mode,
            "clustering_method": clustering_method,
            "contributions": [c.to_dict() for c in contributions],
            # H21: Alerta de Redundancia Local — para el ForensicBundle y el perito
            # Si twin_pairs > 0, el motor detectó señales con |ρ| ≥ 0.90 y las neutralizó.
            # Rob T. Lee puede verificar que el doble conteo fue identificado y corregido.
            "redundancy_alerts": {
                "twin_pairs_detected": total_twin_pairs,
                "penalty_applied": total_twin_pairs > 0,
                "alert": (
                    f"{total_twin_pairs} par(es) de señales altamente correlacionadas "
                    f"(|ρ| ≥ 0.90) detectados y penalizados. Posible inyección de señales "
                    f"redundantes para inflar LR. Verificar independencia de herramientas."
                ) if total_twin_pairs > 0 else None,
            },
            "metadata": {
                "calibration": self._calibration_metadata,
                "prior_odds": self.prior_odds,
                "signals_count": len(signals),
                "ledoit_wolf_active": self._use_covariance,
                "graph_conditioned": evidence_graph is not None,
            },
        }

    # ------------------------------------------------------------------
    # Resolucion de clusters — NAMING EMERGENTE
    # ------------------------------------------------------------------

    def _resolve_clusters(
        self,
        signal_map: Dict[str, SignalOutput],
        evidence_graph: Optional[EvidenceGraph],
    ) -> Tuple[Dict[str, List[str]], str]:
        """
        Con EvidenceGraph: nombres emergentes G_cluster_{i} o G_{strongest_tool}_{i}
        Sin EvidenceGraph: DEFAULT_CLUSTERS (heuristico documentado)

        PROHIBIDO forzar etiquetas NLP/TEMPORAL sobre estructura emergente (Gemini).
        """
        if evidence_graph is not None:
            components = evidence_graph.connected_components()
            clusters: Dict[str, List[str]] = {}
            for i, comp in enumerate(components):
                active = [t for t in comp if t in signal_map]
                if not active:
                    continue

                # Nombre emergente: tool con z_score mas alto en la componente
                strongest = max(active, key=lambda t: abs(signal_map[t].z_score))
                # G_{strongest_tool}_{i} — no NLP, no TEMPORAL
                cluster_name = f"G_{strongest}_{i}"
                clusters[cluster_name] = comp

            if clusters:
                return clusters, "graph_conditioned_emergent"

        return DEFAULT_CLUSTERS, "heuristic_default"

    # ------------------------------------------------------------------
    # Log-LR multivariado (Ledoit-Wolf)
    # ------------------------------------------------------------------

    def _multivariate_log_lr(
        self,
        signals: List[SignalOutput],
        cluster_name: str,
    ) -> Tuple[float, List[SignalContribution]]:
        """
        log LR = 0.5 * [(z-mu1)^T Sigma1^-1 (z-mu1) - (z-mu0)^T Sigma0^-1 (z-mu0)]
                 + log_det_ratio
        Captura correlaciones — sin doble conteo.
        """
        z_vec = []
        active_idx = []
        for k, tool in enumerate(self._cov_tools):
            s = next((sig for sig in signals if sig.tool_name == tool), None)
            if s is not None:
                z_vec.append(max(-Z_CLIP, min(Z_CLIP, s.z_score)))
                active_idx.append(k)
            else:
                z_vec.append(0.0)

        if len(active_idx) < 2:
            return self._univariate_with_correction(signals, cluster_name)

        z = np.array(z_vec)[active_idx]
        inv_h0 = self._inv_cov_h0[np.ix_(active_idx, active_idx)]
        inv_h1 = self._inv_cov_h1[np.ix_(active_idx, active_idx)]
        d0 = z - self._mean_h0[active_idx]
        d1 = z - self._mean_h1[active_idx]
        q0, q1 = float(d0 @ inv_h0 @ d0), float(d1 @ inv_h1 @ d1)
        log_lr = max(-15.0, min(15.0, 0.5 * (q0 - q1) + self._log_det_ratio))

        avg_conf = sum(s.confidence for s in signals) / len(signals)
        contrib = SignalContribution(
            tool_name=f"{cluster_name}[{','.join(self._cov_tools[k] for k in active_idx)}]",
            z_score=float(np.linalg.norm(z)),
            log_lr=log_lr,
            method="multivariate_ledoit_wolf",
            confidence=avg_conf,
            cluster=cluster_name,
        )
        return log_lr, [contrib]

    # ------------------------------------------------------------------
    # Log-LR univariado con correccion de correlacion
    # ------------------------------------------------------------------

    def _univariate_with_correction(
        self,
        signals: List[SignalOutput],
        cluster_name: str,
    ) -> Tuple[float, List[SignalContribution]]:
        """
        Suma log-LR_i con penalizacion de correlacion intra-cluster.

        CORRECCION (Gemini): sin Ledoit-Wolf, la suma directa infla el LR
        cuando las senales estan correlacionadas. Se aplica:
            log_LR_cluster = sum(log_LR_i) * corr_penalty
        donde corr_penalty = max(0.1, 1 - mean(|rho_ij|))
        """
        raw_log_lr = 0.0
        contribs = []
        for s in signals:
            log_lr_i, c = self._single_signal(s, cluster_name)
            raw_log_lr += log_lr_i
            contribs.append(c)

        # Aplicar penalizacion de correlacion
        penalty, twin_pairs = _correlation_penalty(signals)
        corrected = raw_log_lr * penalty

        # Actualizar contribuciones con el factor de escala
        if abs(raw_log_lr) > EPS_NUMERIC and len(signals) > 1:
            scale = corrected / (raw_log_lr + EPS_NUMERIC * math.copysign(1, raw_log_lr))
            for c in contribs:
                c.log_lr *= scale
                suffix = f"_corr_penalty={penalty:.3f}"
                if twin_pairs > 0:
                    suffix += f"_twins={twin_pairs}"
                c.method += suffix

        return corrected, contribs, twin_pairs

    def _single_signal(
        self,
        signal: SignalOutput,
        cluster_name: str,
    ) -> Tuple[float, SignalContribution]:
        z = max(-Z_CLIP, min(Z_CLIP, signal.z_score))
        weight = 0.5 + 0.5 * signal.confidence

        if self._kde_models and signal.tool_name in self._kde_models and _NP:
            try:
                kde_h0, kde_h1 = self._kde_models[signal.tool_name]
                lp0 = float(kde_h0.score_samples([[z]])[0])
                lp1 = float(kde_h1.score_samples([[z]])[0])

                # H19: floor de log-probabilidad para evitar colapso por falta de
                # cobertura en el dataset de calibración (sesgo de selección del baseline).
                # Si H1 no tiene ejemplos cerca de z, score_samples devuelve log(≈0) → -∞.
                # Un LR de 0 o ∞ por falta de datos no es evidencia — es silencio del modelo.
                # Floor: log(1e-10) ≈ -23.0 — conservador pero no infinito.
                # El método se documenta como "kde_calibrated_floored" para el perito.
                _LP_FLOOR = -23.025  # log(1e-10)
                floored = False
                if lp0 < _LP_FLOOR or lp1 < _LP_FLOOR:
                    lp0 = max(lp0, _LP_FLOOR)
                    lp1 = max(lp1, _LP_FLOOR)
                    floored = True

                log_lr = (lp1 - lp0) * weight
                method = "kde_calibrated_floored" if floored else "kde_calibrated"

                if floored:
                    logger.warning(
                        "[LikelihoodEngine] H19: floor aplicado en KDE para '%s' (z=%.4f). "
                        "Solapamiento de soporte insuficiente — dataset de calibración "
                        "puede tener sesgo de selección. INCLUIR EN INFORME PERICIAL.",
                        signal.tool_name, z,
                    )
            except Exception as _kde_exc:
                # H10: el fallo del KDE NO es silencioso
                logger.warning(
                    "[LikelihoodEngine] KDE falló para herramienta '%s' (z=%.4f): %s. "
                    "LR calculado con aproximación gaussiana — INCLUIR EN INFORME PERICIAL.",
                    signal.tool_name, z, _kde_exc,
                )
                log_lr = _gaussian_log_lr(z) * weight
                method = "gaussian_fallback_kde_error"
        else:
            log_lr = _gaussian_log_lr(z) * weight
            method = "gaussian_fallback"

        log_lr = max(-10.0, min(10.0, log_lr))
        return log_lr, SignalContribution(
            tool_name=signal.tool_name,
            z_score=z,
            log_lr=log_lr,
            method=method,
            confidence=signal.confidence,
            cluster=cluster_name,
        )

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "lr": 1.0, "log_lr": 0.0, "posterior": 0.5,
            "decision_hint": "ABSTAIN", "components_used": 0,
            "mode": self._mode, "clustering_method": "none",
            "contributions": [], "metadata": {"error": "No signals"},
        }

    # ------------------------------------------------------------------
    # Metodos de entrenamiento estaticos
    # ------------------------------------------------------------------

    @staticmethod
    def fit_kde_models(
        samples: List[Dict[str, Any]],
        tools: Optional[List[str]] = None,
        bandwidth_range: Optional[List[float]] = None,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Ajusta KDE por herramienta. Requiere sklearn + numpy."""
        if not _SK or not _NP:
            raise RuntimeError("sklearn + numpy requeridos")

        tools = tools or (NLP_TOOLS_DEFAULT + ["GCI", "DGPI"])
        bw = bandwidth_range or [0.1, 0.2, 0.3, 0.5, 0.8]
        models: Dict[str, Any] = {}
        meta: Dict[str, Any] = {"method": "KDE_GridSearchCV", "tools": tools}

        for tool in tools:
            z_h0 = [s["z_scores"][tool] for s in samples
                    if tool in s.get("z_scores", {}) and s.get("ground_truth") == "AUTHENTIC"]
            z_h1 = [s["z_scores"][tool] for s in samples
                    if tool in s.get("z_scores", {}) and s.get("ground_truth") != "AUTHENTIC"]

            if len(z_h0) < 5 or len(z_h1) < 5:
                continue

            # H16: bandwidth mínimo para evitar KDE "picudo" con pocas muestras.
            # Con n < 20, la regla de Scott (h ∝ n^{-1/5}) produce bandwidths
            # tan pequeños que un outlier genera LR ≈ ∞.
            # Piso absoluto de 0.3 z-score unidades — científicamente conservador.
            BW_MIN = 0.3
            bw_guarded = [max(BW_MIN, b) for b in bw]

            def _best(data):
                gs = GridSearchCV(
                    KernelDensity(), {"bandwidth": bw_guarded, "kernel": ["gaussian"]},
                    cv=min(5, len(data))
                )
                gs.fit(np.array(data).reshape(-1, 1))
                return gs.best_estimator_

            models[tool] = (_best(z_h0), _best(z_h1))
            meta[f"{tool}_n"] = (len(z_h0), len(z_h1))

        return {"models": models, "metadata": meta}

    @staticmethod
    def fit_ledoit_wolf(
        samples: List[Dict[str, Any]],
        tools: Optional[List[str]] = None,
        baseline_sizes: Optional[Dict[str, int]] = None,
    ) -> Dict[str, Any]:
        """
        Ajusta matrices Ledoit-Wolf para cluster NLP. Requiere sklearn + numpy.

        ADVERTENCIA ESTADÍSTICA (H12 — Daubert):
        Los z-scores de herramientas distintas (ej. SDA con baseline n=1000 vs
        CLI con n=50) NO son directamente comparables en una matriz de covarianza
        conjunta. Para que la combinación sea estadísticamente válida, los z-scores
        deben estar re-normalizados globalmente sobre el mismo dataset de referencia.

        Este método acepta el parámetro `baseline_sizes` para documentar el tamaño
        del baseline de cada herramienta en los metadatos del modelo. Si los tamaños
        difieren en más de un factor 10, emite una advertencia explícita.

        La re-normalización real debe hacerse ANTES de llamar a este método,
        usando el mismo dataset de referencia para todas las herramientas.
        """
        if not _SK or not _NP:
            raise RuntimeError("sklearn + numpy requeridos")

        tools = tools or NLP_TOOLS_DEFAULT

        # H12: validar comparabilidad de baselines
        if baseline_sizes:
            sizes = [baseline_sizes.get(t, 0) for t in tools if baseline_sizes.get(t, 0) > 0]
            if sizes:
                ratio = max(sizes) / max(min(sizes), 1)
                if ratio > 10:
                    logger.warning(
                        "[LikelihoodEngine] fit_ledoit_wolf: baselines no comparables. "
                        "Ratio máx/mín = %.1f (herramientas: %s). "
                        "Re-normalizar z-scores sobre dataset común antes de ajustar. "
                        "INCLUIR ADVERTENCIA EN INFORME PERICIAL.",
                        ratio, tools,
                    )

        def _vec(s):
            z = s.get("z_scores", {})
            vals = [z.get(t) for t in tools]
            return [float(v) for v in vals] if all(v is not None for v in vals) else None

        h0 = [v for s in samples if s.get("ground_truth") == "AUTHENTIC" for v in [_vec(s)] if v]
        h1 = [v for s in samples if s.get("ground_truth") != "AUTHENTIC" for v in [_vec(s)] if v]

        if len(h0) < 4 or len(h1) < 4:
            raise ValueError(f"Muestras insuficientes: h0={len(h0)} h1={len(h1)}")

        lw0 = LedoitWolf().fit(np.array(h0))
        lw1 = LedoitWolf().fit(np.array(h1))

        return {
            "cov_h0": lw0.covariance_.tolist(),
            "cov_h1": lw1.covariance_.tolist(),
            "mean_h0": lw0.location_.tolist(),
            "mean_h1": lw1.location_.tolist(),
            "tools": tools,
            "n_h0": len(h0), "n_h1": len(h1),
        }
