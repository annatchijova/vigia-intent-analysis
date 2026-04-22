"""
vigia/engine/graph_stability.py
─────────────────────────────────────────────────────────────────────────────
Graph Stability Engine — VIGÍA Forensic Suite EBS v1

ARQUITECTURA: Capa 2 — Motor de Inferencia
REGLA DE AISLAMIENTO: Lee de models/. No lee de governance/ ni audit/.

DISEÑO:
    Implementa Stability Selection vía Bootstrap (B=500).
    El grafo de evidencia EMERGE DEL DATO — no está hardcodeado.

    Cada arista (i,j) existe si y solo si:
        π_ij = freq(arista i,j en bootstrap) ≥ τ

    Esto es estadísticamente defendible ante Daubert:
        "Esta dependencia aparece en X% de los mundos estadísticos
         posibles del dataset de calibración."

PROCESO:
    1. BootstrapSampler: remuestrea el dataset B=500 veces
    2. StructureLearner: construye grafo por muestra (Spearman ρ + MI)
    3. StabilityAggregator: acumula frecuencia de aristas
    4. Thresholding: aristas con π ≥ τ son "estables"
    5. Export: EvidenceGraph listo para LikelihoodEngine y ForensicBundle

CRITERIOS DE DEPENDENCIA (sin ML opaco):
    - Spearman ρ ≥ threshold_rho (robusto ante no-normalidad)
    - Mutual Information ≥ threshold_mi (captura no-linealidad)
    - Una arista requiere AMBOS criterios para ser "candidata" por muestra
    - Solo se mantiene si es candidata en π ≥ τ muestras

UMBRALES (selección forense):
    τ = 0.85 → forense fuerte (por defecto)
    τ = 0.75 → conservador
    τ = 0.60 → exploratorio

COMPATIBILIDAD:
    scipy.stats disponible → Spearman + MI estimado
    Solo numpy → Pearson + correlación manual
    Ninguno → correlación básica Python stdlib

SIFT INTEGRATION:
    Salida: EvidenceGraph con hash criptográfico sellado.
    Compatible con ForensicBundle.evidence_graph.
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import logging
import math
import hashlib
import json
from collections import defaultdict
from itertools import combinations
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

try:
    import numpy as np
    _NP_AVAILABLE = True
except ImportError:
    np = None  # type: ignore
    _NP_AVAILABLE = False

try:
    from scipy.stats import spearmanr
    _SCIPY_AVAILABLE = True
except ImportError:
    spearmanr = None  # type: ignore
    _SCIPY_AVAILABLE = False

import os as _os_gs, sys as _sys_gs
_ROOT_GS = _os_gs.path.dirname(_os_gs.path.dirname(_os_gs.path.abspath(__file__)))
if _ROOT_GS not in _sys_gs.path:
    _sys_gs.path.insert(0, _ROOT_GS)

from models.ebs_v1 import (
    EvidenceEdge, EvidenceGraph,
    STABILITY_THRESHOLD_FORENSIC, STABILITY_THRESHOLD_EXPLORATORY,
)


# ---------------------------------------------------------------------------
# Fallback: correlación de Pearson con stdlib
# ---------------------------------------------------------------------------

def _pearson_stdlib(x: List[float], y: List[float]) -> float:
    """Correlación de Pearson sin numpy — fallback completo."""
    n = len(x)
    if n < 3:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
    if dx < 1e-9 or dy < 1e-9:
        return 0.0
    return num / (dx * dy)


def _spearman_stdlib(x: List[float], y: List[float]) -> float:
    """
    Correlación de Spearman sin scipy.
    Rankea los valores y aplica Pearson sobre rangos.
    """
    def rank(lst: List[float]) -> List[float]:
        indexed = sorted(enumerate(lst), key=lambda t: t[1])
        ranks = [0.0] * len(lst)
        for i, (orig_idx, _) in enumerate(indexed):
            ranks[orig_idx] = float(i + 1)
        return ranks

    return _pearson_stdlib(rank(x), rank(y))


def _mutual_information_approx(
    x: List[float],
    y: List[float],
    bins: int = 5,
) -> float:
    """
    Estimación discreta de Mutual Information via histograma 2D.
    Aproximación — suficiente para decidir candidatura de arista.
    """
    n = len(x)
    if n < 5:
        return 0.0

    # Discretizar en bins iguales
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)

    if x_max == x_min or y_max == y_min:
        return 0.0

    def digitize(vals: List[float], vmin: float, vmax: float) -> List[int]:
        rng = vmax - vmin + 1e-9
        return [min(bins - 1, int((v - vmin) / rng * bins)) for v in vals]

    bx = digitize(x, x_min, x_max)
    by = digitize(y, y_min, y_max)

    # Frecuencias conjuntas y marginales
    joint: Dict[Tuple[int, int], int] = defaultdict(int)
    px: Dict[int, int] = defaultdict(int)
    py: Dict[int, int] = defaultdict(int)

    for xi, yi in zip(bx, by):
        joint[(xi, yi)] += 1
        px[xi] += 1
        py[yi] += 1

    eps = 1e-9
    mi = 0.0
    for (xi, yi), cnt in joint.items():
        p_xy = cnt / n
        p_x = px[xi] / n
        p_y = py[yi] / n
        if p_xy > eps and p_x > eps and p_y > eps:
            mi += p_xy * math.log(p_xy / (p_x * p_y + eps))

    return max(0.0, mi)


# ---------------------------------------------------------------------------
# BootstrapSampler
# ---------------------------------------------------------------------------

class BootstrapSampler:
    """
    Remuestreador bootstrap determinístico.
    Mismo seed → misma secuencia de muestras → mismo grafo.
    """

    def __init__(self, n_bootstrap: int = 500, seed: int = 42) -> None:
        self.n_bootstrap = n_bootstrap
        self.seed = seed

    def samples(self, data: List[Any]):
        """Generator: produce n_bootstrap muestras bootstrap del dataset."""
        n = len(data)
        if n == 0:
            return

        if _NP_AVAILABLE:
            rng = np.random.default_rng(self.seed)
            for _ in range(self.n_bootstrap):
                idx = rng.integers(0, n, n)
                yield [data[int(i)] for i in idx]
        else:
            import random
            rng = random.Random(self.seed)
            for _ in range(self.n_bootstrap):
                yield [data[rng.randint(0, n - 1)] for _ in range(n)]


# ---------------------------------------------------------------------------
# StructureLearner
# ---------------------------------------------------------------------------

class StructureLearner:
    """
    Aprende la estructura del grafo para una muestra dada.

    Criterio de arista (candidata en este bootstrap):
        Spearman |ρ| ≥ threshold_rho  AND  MI ≥ threshold_mi

    Sin ML opaco: estadística clásica explícita.
    """

    def __init__(
        self,
        threshold_rho: float = 0.25,
        threshold_mi: float = 0.05,
    ) -> None:
        self.threshold_rho = threshold_rho
        self.threshold_mi = threshold_mi

    def build_graph(
        self,
        samples: List[Dict[str, float]],
    ) -> Set[Tuple[str, str]]:
        """
        Construye conjunto de aristas (candidatas) para esta muestra bootstrap.

        samples: lista de dicts {tool_name: z_score}
        """
        if not samples:
            return set()

        tools = sorted(samples[0].keys())
        edges: Set[Tuple[str, str]] = set()

        for tool_i, tool_j in combinations(tools, 2):
            x = [s.get(tool_i, 0.0) for s in samples if tool_i in s and tool_j in s]
            y = [s.get(tool_j, 0.0) for s in samples if tool_i in s and tool_j in s]

            if len(x) < 4:
                continue

            # Spearman ρ
            if _SCIPY_AVAILABLE and _NP_AVAILABLE:
                rho_val, _ = spearmanr(x, y)
                rho = float(rho_val) if not math.isnan(rho_val) else 0.0
            else:
                rho = _spearman_stdlib(x, y)

            if abs(rho) < self.threshold_rho:
                continue

            # Mutual Information
            mi = _mutual_information_approx(x, y)
            if mi < self.threshold_mi:
                continue

            # Orden canónico (i < j) para consistencia
            edge = (min(tool_i, tool_j), max(tool_i, tool_j))
            edges.add(edge)

        return edges


# ---------------------------------------------------------------------------
# StabilityAggregator
# ---------------------------------------------------------------------------

class StabilityAggregator:
    """
    Acumula frecuencias de aristas a través de rondas bootstrap.
    π_ij = freq(arista ij en B muestras).
    """

    def __init__(self) -> None:
        self._edge_counts: Dict[Tuple[str, str], int] = defaultdict(int)
        self._edge_rho_sum: Dict[Tuple[str, str], float] = defaultdict(float)
        self._edge_rho_sq: Dict[Tuple[str, str], float] = defaultdict(float)
        self._total: int = 0

    def update(
        self,
        edges: Set[Tuple[str, str]],
        rho_map: Optional[Dict[Tuple[str, str], float]] = None,
    ) -> None:
        self._total += 1
        for edge in edges:
            self._edge_counts[edge] += 1
            if rho_map and edge in rho_map:
                self._edge_rho_sum[edge] += rho_map[edge]
                self._edge_rho_sq[edge] += rho_map[edge] ** 2

    def stability_map(self) -> Dict[Tuple[str, str], float]:
        """π_ij para cada arista observada."""
        if self._total == 0:
            return {}
        return {
            edge: count / self._total
            for edge, count in self._edge_counts.items()
        }

    def weight_map(self) -> Dict[Tuple[str, str], float]:
        """Media de |ρ| sobre las muestras donde la arista apareció."""
        result = {}
        for edge, count in self._edge_counts.items():
            if count > 0:
                result[edge] = self._edge_rho_sum[edge] / count
        return result

    def confidence_interval_map(
        self,
        z_alpha: float = 1.96,
    ) -> Dict[Tuple[str, str], Tuple[float, float]]:
        """IC asintótico de Wilson para π_ij."""
        ci_map = {}
        n = self._total
        for edge, count in self._edge_counts.items():
            p = count / n
            margin = z_alpha * math.sqrt(p * (1 - p) / max(n, 1))
            ci_map[edge] = (max(0.0, p - margin), min(1.0, p + margin))
        return ci_map


# ---------------------------------------------------------------------------
# GraphStabilityEngine — motor completo
# ---------------------------------------------------------------------------

class GraphStabilityEngine:
    """
    Motor de estabilidad de grafos via bootstrap stability selection.

    Uso:
        engine = GraphStabilityEngine(n_bootstrap=500, stability_threshold=0.85)
        graph = engine.fit(dataset)   # retorna EvidenceGraph sellado

    dataset: lista de dicts {"tool_name_1": z_score, "tool_name_2": z_score, ...}
             o lista de SignalOutput
    """

    def __init__(
        self,
        n_bootstrap: int = 500,
        stability_threshold: float = STABILITY_THRESHOLD_FORENSIC,
        threshold_rho: float = 0.25,
        threshold_mi: float = 0.05,
        seed: int = 42,
        robustness_weight: float = 0.5,  # R_ij = π_ij * |ρ_mean| — penaliza aristas estables pero débiles
    ) -> None:
        self.n_bootstrap = n_bootstrap
        self.stability_threshold = stability_threshold
        self.threshold_rho = threshold_rho
        self.threshold_mi = threshold_mi
        self.seed = seed
        self.robustness_weight = robustness_weight

        self._sampler = BootstrapSampler(n_bootstrap=n_bootstrap, seed=seed)
        self._learner = StructureLearner(
            threshold_rho=threshold_rho,
            threshold_mi=threshold_mi,
        )
        self._aggregator = StabilityAggregator()

    def fit(
        self,
        dataset: List[Any],
        nodes: Optional[List[str]] = None,
    ) -> EvidenceGraph:
        """
        Ajusta el grafo de estabilidad sobre el dataset.

        Args:
            dataset: lista de dicts {tool: z_score} o lista de SignalOutput
            nodes  : lista explícita de nodos (opcional, se infiere si no)

        Returns:
            EvidenceGraph sellado con π ≥ stability_threshold
        """
        # Normalizar dataset a list of dicts
        normalized = self._normalize_dataset(dataset)

        if not normalized:
            logger.warning("[GraphStabilityEngine] Dataset vacío — retornando grafo vacío")
            return EvidenceGraph(nodes=nodes or [], edges=[])

        # Inferir nodos si no se proveen
        if nodes is None:
            nodes = sorted(set(k for sample in normalized for k in sample.keys()))

        logger.info(
            "[GraphStabilityEngine] Iniciando bootstrap B=%d sobre %d samples, %d nodos",
            self.n_bootstrap, len(normalized), len(nodes)
        )

        # Bootstrap loop
        self._aggregator = StabilityAggregator()
        for round_idx, bootstrap_sample in enumerate(self._sampler.samples(normalized)):
            edges = self._learner.build_graph(bootstrap_sample)
            self._aggregator.update(edges)

            if (round_idx + 1) % 100 == 0:
                logger.debug("[Bootstrap] Ronda %d/%d", round_idx + 1, self.n_bootstrap)

        # Construir grafo estable
        stability_map = self._aggregator.stability_map()
        weight_map = self._aggregator.weight_map()
        ci_map = self._aggregator.confidence_interval_map()

        evidence_edges: List[EvidenceEdge] = []

        for (source, target), pi in stability_map.items():
            if pi < self.stability_threshold:
                continue

            w_mean = weight_map.get((source, target), 0.0)

            # Robustness score: R_ij = π_ij * |ρ_mean|
            # Penaliza aristas "estables pero débiles"
            robustness = pi * abs(w_mean)
            if robustness < self.robustness_weight * self.stability_threshold:
                logger.debug(
                    "[GraphStability] Arista (%s,%s) descartada por robustez baja: R=%.3f",
                    source, target, robustness
                )
                continue

            ci = ci_map.get((source, target), (0.0, 1.0))

            edge = EvidenceEdge(
                source=source,
                target=target,
                stability=pi,
                weight_mean=w_mean,
                confidence_interval=ci,
                dependency_type="spearman_mi_bootstrap",
            )
            evidence_edges.append(edge)

        # Garantizar que todos los nodos estén representados
        # (nodos sin aristas son válidos — señales independientes)
        graph = EvidenceGraph(
            nodes=nodes,
            edges=evidence_edges,
            bootstrap_rounds=self.n_bootstrap,
            stability_threshold=self.stability_threshold,
        )

        # Sellar hash del grafo
        graph.graph_hash = graph.compute_graph_hash()

        n_edges = len(evidence_edges)
        n_possible = len(nodes) * (len(nodes) - 1) // 2
        logger.info(
            "[GraphStabilityEngine] Grafo construido: %d/%d aristas estables (τ=%.2f)",
            n_edges, n_possible, self.stability_threshold
        )

        return graph

    # ------------------------------------------------------------------
    # Drift detection entre dos grafos
    # ------------------------------------------------------------------

    def compute_graph_drift(
        self,
        old_graph: EvidenceGraph,
        new_graph: EvidenceGraph,
        drift_threshold: float = 0.20,
    ) -> Dict[str, Any]:
        """
        Detecta drift estructural entre dos grafos.

        Retorna:
            {
                "global_drift": float — PSI-like score
                "edges_gained": list  — aristas nuevas
                "edges_lost":   list  — aristas perdidas
                "stability_delta": dict — Δπ por arista
                "above_threshold": bool
            }
        """
        old_map = {(e.source, e.target): e.stability for e in old_graph.edges}
        new_map = {(e.source, e.target): e.stability for e in new_graph.edges}

        all_edges = set(old_map.keys()) | set(new_map.keys())

        delta_map: Dict[str, float] = {}
        edges_gained: List[str] = []
        edges_lost: List[str] = []

        for edge in all_edges:
            old_pi = old_map.get(edge, 0.0)
            new_pi = new_map.get(edge, 0.0)
            delta = abs(old_pi - new_pi)
            delta_map[f"{edge[0]}->{edge[1]}"] = delta

            if old_pi == 0.0 and new_pi > 0.0:
                edges_gained.append(f"{edge[0]}->{edge[1]}")
            elif old_pi > 0.0 and new_pi == 0.0:
                edges_lost.append(f"{edge[0]}->{edge[1]}")

        global_drift = (
            sum(delta_map.values()) / len(delta_map) if delta_map else 0.0
        )

        return {
            "global_drift": global_drift,
            "edges_gained": edges_gained,
            "edges_lost": edges_lost,
            "stability_delta": delta_map,
            "above_threshold": global_drift > drift_threshold,
            "n_edges_old": len(old_graph.edges),
            "n_edges_new": len(new_graph.edges),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_dataset(dataset: List[Any]) -> List[Dict[str, float]]:
        """
        Acepta:
            - list of dicts {tool: z_score}
            - list of SignalOutput
            - list of dicts {"z_scores": {tool: z_score}}
        """
        if not dataset:
            return []

        first = dataset[0]

        # Caso: ya es dict {tool: z_score}
        if isinstance(first, dict) and not ("z_scores" in first or "tool_name" in first):
            return [
                {k: float(v) for k, v in d.items() if isinstance(v, (int, float))}
                for d in dataset
            ]

        # Caso: dict con "z_scores" anidado
        if isinstance(first, dict) and "z_scores" in first:
            return [
                {k: float(v) for k, v in d["z_scores"].items()}
                for d in dataset
                if isinstance(d.get("z_scores"), dict)
            ]

        # Caso: lista de SignalOutput (duck typing)
        if hasattr(first, "tool_name") and hasattr(first, "z_score"):
            # Agrupar por... no podemos agrupar señales sin saber qué pertenece
            # a qué "sample". Tratar cada SignalOutput como muestra individual
            # con un solo punto (útil para testing, no para bootstrap real).
            return [{s.tool_name: s.z_score} for s in dataset]

        # Caso: lista de listas de SignalOutput (agrupadas por caso)
        if isinstance(first, list) and hasattr(first[0], "tool_name"):
            return [
                {s.tool_name: s.z_score for s in group}
                for group in dataset
            ]

        logger.warning("[GraphStabilityEngine] Formato de dataset no reconocido")
        return []

    def export_sift(
        self,
        graph: EvidenceGraph,
    ) -> Dict[str, Any]:
        """
        Exporta el grafo en formato SIFT Evidence Graph v1.0.
        Compatible con ingestión directa en SIFT.
        """
        edges_export = []
        for e in graph.edges:
            edges_export.append({
                "from": e.source,
                "to": e.target,
                "stability": round(e.stability, 4),
                "weight": round(e.weight_mean, 4),
                "confidence_interval": [
                    round(e.confidence_interval[0], 4),
                    round(e.confidence_interval[1], 4),
                ],
                "type": e.dependency_type,
                "forensically_stable": e.is_forensically_stable(),
            })

        sift_graph = {
            "version": "SIFT-EVG-1.0",
            "threshold": graph.stability_threshold,
            "bootstrap_rounds": graph.bootstrap_rounds,
            "nodes": graph.nodes,
            "edges": edges_export,
            "global_stability": round(graph.global_stability(), 4),
        }

        raw = json.dumps(sift_graph, sort_keys=True).encode()
        sift_graph["hash"] = hashlib.sha256(raw).hexdigest()

        return sift_graph
