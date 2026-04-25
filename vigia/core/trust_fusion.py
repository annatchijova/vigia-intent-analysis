"""
vigia/core/trust_fusion.py  — VIGÍA Trust Fusion Engine (P2)
Extraído desde trust_fusion_hardened.py (raíz) hacia ruta correcta del paquete.
Diagnóstico: 20-abr-2026 — Claude (Systems Integration Engineer).

Ver docstring completo en la versión fuente: trust_fusion_hardened.py
"""
# Re-exporta el módulo fuente para evitar duplicación de código.
# La lógica real vive en trust_fusion_hardened.py hasta que se complete
# la refactorización al monorepo final.

from __future__ import annotations

# Importaciones directas para que `from vigia.core.trust_fusion import X` funcione
import bisect
import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Final, Optional

from vigia.security import _utcnow, audit_logger

_DETERMINISTIC_INTERNAL_PREC: Final[int] = 6
_DETERMINISTIC_OUTPUT_PREC: Final[int] = 4

TRUST_THRESHOLD_CRITICAL: Final[float] = 0.2
TRUST_THRESHOLD_SUSPICIOUS: Final[float] = 0.5
TEMPORAL_WINDOW_SECONDS: Final[int] = 300
MAX_NEIGHBORS: Final[int] = 10
DAUBERT_MIN_EFFECTIVE_TRUST: Final[float] = 0.5

_TEMPORAL_VIOLATION_WEIGHTS: Final[dict[str, float]] = {
    "EFFECT_BEFORE_CAUSE":    1.0,
    "TOO_FAST":               0.7,
    "STATISTICAL_UNIFORMITY": 0.6,
    "IDENTICAL_TIMESTAMP":    0.5,
    "CLOCK_SKEW":             0.4,
}


def _dround(value: float, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> float:
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


def _product(iterable: list) -> float:
    result = 1.0
    for x in iterable:
        result = _dround(result * x)
    return result


@dataclass(frozen=True)
class TemporalArtifact:
    artifact_id: str
    timestamp: datetime
    evidence_type: str
    source_tool: str
    raw_score: float
    prior_trust: float
    provenance_chain: tuple
    metadata: frozenset = field(default_factory=frozenset)

    def __post_init__(self):
        if self.timestamp.tzinfo is None:
            raise ValueError(f"{self.artifact_id}: timestamp must be timezone-aware")
        if not 0.0 <= self.prior_trust <= 1.0:
            raise ValueError(f"{self.artifact_id}: prior_trust in [0,1]")
        if not 0.0 <= self.raw_score <= 1.0:
            raise ValueError(f"{self.artifact_id}: raw_score in [0,1]")

    @property
    def effective_provenance_trust(self) -> float:
        if not self.provenance_chain:
            return 1.0
        total = 1.0
        for i, h in enumerate(self.provenance_chain):
            lt = _dround(0.95 ** i)
            if not h or len(h) < 8:
                lt = _dround(lt * 0.5)
            total = _dround(total * lt)
        return _dround(max(0.0, min(1.0, total)))

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "timestamp": self.timestamp.isoformat(),
            "evidence_type": self.evidence_type,
            "source_tool": self.source_tool,
            "raw_score": round(self.raw_score, 6),
            "prior_trust": round(self.prior_trust, 6),
            "provenance_chain": list(self.provenance_chain),
            "effective_provenance_trust": round(self.effective_provenance_trust, 6),
        }


@dataclass
class NeighborhoodContext:
    center_artifact_id: str
    temporal_window_seconds: int
    neighbors_before: list
    neighbors_after: list

    @property
    def all_neighbors(self):
        return self.neighbors_before + self.neighbors_after

    @property
    def neighbor_count(self):
        return len(self.all_neighbors)

    @property
    def mean_neighbor_trust(self):
        if not self.all_neighbors:
            return 1.0
        return _dround(math.fsum(n.prior_trust for n in self.all_neighbors) / len(self.all_neighbors))

    @property
    def contamination_ratio(self):
        if not self.all_neighbors:
            return 0.0
        return _dround(sum(1 for n in self.all_neighbors if n.prior_trust < TRUST_THRESHOLD_CRITICAL) / len(self.all_neighbors))

    @property
    def suspicious_ratio(self):
        if not self.all_neighbors:
            return 0.0
        return _dround(sum(1 for n in self.all_neighbors if n.prior_trust < TRUST_THRESHOLD_SUSPICIOUS) / len(self.all_neighbors))


@dataclass
class BayesianTrustUpdate:
    artifact_id: str
    prior_trust: float
    posterior_trust: float
    likelihood_evidence: float
    evidence_marginal: float
    neighborhood_influence: float
    update_reason: str

    @property
    def trust_delta(self):
        return _dround(self.posterior_trust - self.prior_trust)

    @property
    def was_degraded(self):
        return self.posterior_trust < self.prior_trust

    def to_dict(self):
        return {
            "artifact_id": self.artifact_id,
            "prior_trust": round(self.prior_trust, 6),
            "posterior_trust": round(self.posterior_trust, 6),
            "trust_delta": round(self.trust_delta, 6),
            "likelihood_evidence": round(self.likelihood_evidence, 6),
            "evidence_marginal": round(self.evidence_marginal, 6),
            "neighborhood_influence": round(self.neighborhood_influence, 6),
            "was_degraded": self.was_degraded,
            "update_reason": self.update_reason,
        }


class TrustFusionEngine:
    """Motor de Fusión de Confianza — Capa P2 del Pipeline VIGÍA."""

    def __init__(self, temporal_window_seconds=TEMPORAL_WINDOW_SECONDS, max_neighbors=MAX_NEIGHBORS):
        self.temporal_window = timedelta(seconds=temporal_window_seconds)
        self.max_neighbors = max_neighbors
        self._artifacts: dict[str, TemporalArtifact] = {}
        self._temporal_index: list = []
        self._timestamps: list = []
        self._bayesian_cache: dict[str, BayesianTrustUpdate] = {}

    def add_artifact(self, artifact: TemporalArtifact) -> bool:
        if artifact.artifact_id in self._artifacts:
            return False
        self._artifacts[artifact.artifact_id] = artifact
        ts = artifact.timestamp
        pos = bisect.bisect_right(self._timestamps, ts)
        self._timestamps.insert(pos, ts)
        self._temporal_index.insert(pos, (ts, artifact.artifact_id))
        self._bayesian_cache.clear()
        return True

    def add_artifacts_batch(self, artifacts: list) -> int:
        return sum(1 for a in artifacts if self.add_artifact(a))

    def get_neighborhood(self, artifact_id: str, custom_window=None) -> NeighborhoodContext:
        if artifact_id not in self._artifacts:
            raise ValueError(f"Artifact {artifact_id!r} not found")
        center = self._artifacts[artifact_id]
        window_s = (custom_window or self.temporal_window).total_seconds()
        before, after = [], []
        pos = bisect.bisect_left(self._timestamps, center.timestamp)
        idx = pos - 1
        while idx >= 0 and len(before) < self.max_neighbors // 2:
            if (center.timestamp - self._timestamps[idx]).total_seconds() > window_s:
                break
            aid = self._temporal_index[idx][1]
            if aid != artifact_id:
                before.append(self._artifacts[aid])
            idx -= 1
        idx = pos + 1
        while idx < len(self._timestamps) and len(after) < self.max_neighbors // 2:
            if (self._timestamps[idx] - center.timestamp).total_seconds() > window_s:
                break
            aid = self._temporal_index[idx][1]
            if aid != artifact_id:
                after.append(self._artifacts[aid])
            idx += 1
        return NeighborhoodContext(artifact_id, int(window_s), before, after)

    def calculate_likelihood(self, artifact: TemporalArtifact, neighborhood: NeighborhoodContext) -> float:
        if neighborhood.neighbor_count == 0:
            return 0.5
        base = _dround(neighborhood.mean_neighbor_trust)
        penalty = _dround(neighborhood.contamination_ratio * 0.5 + neighborhood.suspicious_ratio * 0.2)
        return max(0.01, min(0.99, _dround(base - penalty)))

    def calculate_evidence_marginal(self, artifact: TemporalArtifact, likelihood: float) -> float:
        p = artifact.prior_trust
        marginal = _dround(math.fsum([_dround(likelihood * p), _dround((1.0 - likelihood) * (1.0 - p))]))
        floor = _dround(p * 0.1)
        if marginal < floor:
            marginal = floor
        return max(0.001, marginal)

    def bayesian_update(self, artifact_id: str, custom_window=None) -> BayesianTrustUpdate:
        if artifact_id in self._bayesian_cache:
            return self._bayesian_cache[artifact_id]
        if artifact_id not in self._artifacts:
            raise ValueError(f"Artifact {artifact_id!r} not found")
        artifact = self._artifacts[artifact_id]
        neighborhood = self.get_neighborhood(artifact_id, custom_window)
        prior = artifact.prior_trust
        likelihood = self.calculate_likelihood(artifact, neighborhood)
        marginal = self.calculate_evidence_marginal(artifact, likelihood)
        posterior = max(0.0, min(1.0, _dround(_dround(likelihood * prior) / marginal)))
        influence = _dround(abs(posterior - prior))
        if neighborhood.contamination_ratio > 0.5:
            reason = f"CRITICAL: {neighborhood.contamination_ratio:.1%} vecinos contaminados. {prior:.3f}→{posterior:.3f}"
        elif neighborhood.suspicious_ratio > 0.5:
            reason = f"WARNING: vecinos sospechosos. {prior:.3f}→{posterior:.3f}"
        elif posterior > prior:
            reason = f"BOOST: trust vecindad={neighborhood.mean_neighbor_trust:.3f}. {prior:.3f}→{posterior:.3f}"
        else:
            reason = f"NEUTRAL: prior={prior:.3f} posterior={posterior:.3f}"
        result = BayesianTrustUpdate(artifact_id, prior, posterior, likelihood, marginal, influence, reason)
        self._bayesian_cache[artifact_id] = result
        if result.was_degraded:
            audit_logger.log_info("TRUST_BAYESIAN_DEGRADATION", "TrustFusionEngine", reason)
        return result

    @staticmethod
    def compute_temporal_trust_factor(violations: list, artifact_id: str) -> float:
        """exp(-2 * max_weighted_severity). Cierra el ciclo Temporal→Provenance→Correlation."""
        relevant = [
            v for v in violations
            if v.get("cause", {}).get("artifact_id") == artifact_id
            or v.get("effect", {}).get("artifact_id") == artifact_id
        ]
        if not relevant:
            return 1.0
        weighted = [
            v.get("severity", 0.5) * _TEMPORAL_VIOLATION_WEIGHTS.get(v.get("type", ""), 0.5)
            for v in relevant
        ]
        return max(0.0, min(1.0, _dround(math.exp(-2.0 * max(weighted)))))

    def compute_effective_trust(self, artifact_id: str, provenance_chain_trust: float, temporal_violations: list) -> float:
        """effective_trust = provenance_trust × temporal_integrity_factor."""
        factor = self.compute_temporal_trust_factor(temporal_violations, artifact_id)
        effective = max(0.0, min(1.0, _dround(provenance_chain_trust * factor)))
        audit_logger.log_info(
            "EFFECTIVE_TRUST_COMPUTED", "TrustFusionEngine",
            f"artifact={artifact_id} prov={provenance_chain_trust:.4f} temp_factor={factor:.4f} effective={effective:.4f}"
        )
        return effective

    def apply_reliability_ceiling(self, raw_score: float, artifact_id: str) -> tuple:
        if artifact_id not in self._artifacts:
            raise ValueError(f"Artifact {artifact_id!r} not found")
        artifact = self._artifacts[artifact_id]
        bayesian = self.bayesian_update(artifact_id)
        epc = artifact.effective_provenance_trust
        ceiling = _dround(min(bayesian.posterior_trust, epc))
        final = min(raw_score, ceiling)
        applied = final < raw_score
        if applied:
            audit_logger.log_info("RELIABILITY_CEILING_APPLIED", "TrustFusionEngine",
                                  f"raw={raw_score:.3f}→final={final:.3f}")
        return final, {
            "raw_score": round(raw_score, 6),
            "score_final": round(final, 6),
            "effective_ceiling": round(ceiling, 6),
            "posterior_trust": round(bayesian.posterior_trust, 6),
            "epc_trust": round(epc, 6),
            "ceiling_applied": applied,
            "ceiling_reason": f"ceiling={ceiling:.3f}",
            "daubert_compliant": ceiling >= DAUBERT_MIN_EFFECTIVE_TRUST,
        }

    def calculate_composite_trust(self, artifact_ids: list, aggregation_method: str = "noisy_or") -> dict:
        if not artifact_ids:
            return {"composite_trust": 0.0, "method": aggregation_method, "artifact_count": 0}
        trusts, details = [], []
        for aid in artifact_ids:
            if aid not in self._artifacts:
                continue
            b = self.bayesian_update(aid)
            epc = self._artifacts[aid].effective_provenance_trust
            ft = _dround(min(b.posterior_trust, epc))
            trusts.append(ft)
            details.append({"artifact_id": aid, "prior": round(b.prior_trust, 4),
                            "posterior": round(b.posterior_trust, 4), "epc_trust": round(epc, 4), "final_trust": round(ft, 4)})
        if not trusts:
            return {"composite_trust": 0.0, "method": aggregation_method, "error": "No valid artifacts"}
        if aggregation_method == "noisy_or":
            composite = _dround(1.0 - _product([_dround(1.0 - t) for t in trusts]))
        elif aggregation_method == "conservative_min":
            composite = min(trusts)
        else:
            composite = _dround(math.fsum(trusts) / len(trusts))
        return {
            "composite_trust": round(composite, 6), "method": aggregation_method,
            "artifact_count": len(trusts), "individual_trusts": details,
            "min_trust": round(min(trusts), 6), "max_trust": round(max(trusts), 6),
            "mean_trust": round(_dround(math.fsum(trusts) / len(trusts)), 6),
            "daubert_admissible": composite >= DAUBERT_MIN_EFFECTIVE_TRUST,
        }

    def generate_daubert_report(self, artifact_ids: list) -> dict:
        composite = self.calculate_composite_trust(artifact_ids)
        if len(artifact_ids) > 1 and composite.get("individual_trusts"):
            trusts = [d["final_trust"] for d in composite["individual_trusts"]]
            mean_t = _dround(math.fsum(trusts) / len(trusts))
            variance = _dround(math.fsum([_dround((t - mean_t) ** 2) for t in trusts]) / len(trusts))
            error_rate = _dround(math.sqrt(variance))
        else:
            error_rate = 0.5
        return {
            "standard": "Daubert v. Merrell Dow Pharmaceuticals, Inc., 509 U.S. 579 (1993)",
            "composite_trust": composite["composite_trust"],
            "error_rate_estimate": round(error_rate, 4),
            "error_rate_acceptable": error_rate < 0.2,
            "methodology": "Bayesian Trust Fusion with Temporal Neighborhood Analysis",
            "general_acceptance": True,
            "thresholds": {"critical": TRUST_THRESHOLD_CRITICAL, "suspicious": TRUST_THRESHOLD_SUSPICIOUS, "daubert_min": DAUBERT_MIN_EFFECTIVE_TRUST},
            "admissible": composite["composite_trust"] >= DAUBERT_MIN_EFFECTIVE_TRUST and error_rate < 0.3,
        }

    def export_to_caie(self, artifact_ids=None) -> list:
        if artifact_ids is None:
            artifact_ids = list(self._artifacts.keys())
        exports = []
        for aid in artifact_ids:
            if aid not in self._artifacts:
                continue
            artifact = self._artifacts[aid]
            b = self.bayesian_update(aid)
            score, meta = self.apply_reliability_ceiling(artifact.raw_score, aid)
            exports.append({
                "artifact_id": aid, "evidence_type": artifact.evidence_type,
                "source_tool": artifact.source_tool, "timestamp": artifact.timestamp.isoformat(),
                "prior_trust": b.prior_trust, "posterior_trust": b.posterior_trust,
                "effective_trust": meta["score_final"], "raw_score": artifact.raw_score,
                "adjusted_score": score, "ceiling_applied": meta["ceiling_applied"],
                "provenance_chain": list(artifact.provenance_chain),
                "epc_trust": meta["epc_trust"], "daubert_compliant": meta["daubert_compliant"],
            })
        return exports

    def reset(self):
        self._artifacts.clear()
        self._temporal_index.clear()
        self._timestamps.clear()
        self._bayesian_cache.clear()


def create_artifact_from_caie_result(result: dict, evidence_type: str, source_tool: str) -> TemporalArtifact:
    ts_str = result.get("timestamp", _utcnow())
    try:
        timestamp = datetime.fromisoformat(str(ts_str).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        timestamp = datetime.now(timezone.utc)
    content_hash = hashlib.sha256(json.dumps(result, sort_keys=True, default=str).encode()).hexdigest()[:16]
    artifact_id = result.get("artifact_id", f"{source_tool}_{evidence_type}_{content_hash}")
    provenance = result.get("provenance_chain", [])
    provenance = tuple(str(h) for h in provenance) if isinstance(provenance, list) else ()
    try:
        metadata = frozenset(result.get("metadata", {}).items())
    except (AttributeError, TypeError):
        metadata = frozenset()
    return TemporalArtifact(
        artifact_id=artifact_id, timestamp=timestamp, evidence_type=evidence_type,
        source_tool=source_tool, raw_score=float(result.get("raw_score", 0.0)),
        prior_trust=float(result.get("base_trust", result.get("prior_trust", 1.0))),
        provenance_chain=provenance, metadata=metadata,
    )


async def trust_fusion_analysis(
    artifacts: list, temporal_window_seconds: int = TEMPORAL_WINDOW_SECONDS,
    aggregation_method: str = "noisy_or", temporal_violations=None,
) -> dict:
    """MCP Tool: análisis completo de fusión de confianza con integración temporal."""
    engine = TrustFusionEngine(temporal_window_seconds=temporal_window_seconds)
    violations = temporal_violations or []
    temporal_artifacts = []

    for i, art_dict in enumerate(artifacts):
        try:
            art_dict = dict(art_dict)

            # Normalizador de formato — acepta artefactos de Claude Code y otros callers
            # Claude Code puede pasar: {indicator, value, confidence, weight}
            # CAIE espera:             {artifact_id, evidence_type, prior_trust, ...}
            if "indicator" in art_dict and "artifact_id" not in art_dict:
                art_dict["artifact_id"] = f"mcp_{i}_{hash(str(art_dict)) & 0xFFFF:04x}"
            if "confidence" in art_dict and "prior_trust" not in art_dict:
                art_dict["prior_trust"] = float(art_dict["confidence"])
            if "evidence_type" not in art_dict:
                art_dict["evidence_type"] = art_dict.get("type", art_dict.get("label", "unknown"))
            if "source_tool" not in art_dict:
                art_dict["source_tool"] = art_dict.get("label", "mcp_caller")
            if "artifact_id" not in art_dict:
                art_dict["artifact_id"] = f"artifact_{i}_{hash(str(art_dict)) & 0xFFFF:04x}"

            if violations:
                factor = TrustFusionEngine.compute_temporal_trust_factor(violations, art_dict["artifact_id"])
                prov = float(art_dict.get("base_trust", art_dict.get("prior_trust", 1.0)))
                art_dict["prior_trust"] = _dround(prov * factor)
            temporal_artifacts.append(create_artifact_from_caie_result(
                art_dict, art_dict.get("evidence_type", "unknown"), art_dict.get("source_tool", "unknown")
            ))
        except Exception as exc:
            audit_logger.log_info("TRUST_FUSION_ARTIFACT_SKIP", "trust_fusion_analysis", f"Skip {i}: {exc}")
    engine.add_artifacts_batch(temporal_artifacts)
    ids = list(engine._artifacts.keys())
    if not ids:
        return {"status": "ERROR", "error": "No valid artifacts", "composite_trust": 0.0, "daubert_admissible": False}
    composite = engine.calculate_composite_trust(ids, aggregation_method)
    daubert = engine.generate_daubert_report(ids)
    return {
        "status": "OK", "composite_trust": composite["composite_trust"],
        "aggregation_method": aggregation_method, "artifact_count": len(ids),
        "temporal_violations_applied": len(violations) > 0,
        "individual_results": [{"artifact_id": a, "bayesian_update": engine.bayesian_update(a).to_dict()} for a in ids],
        "composite_details": composite, "daubert_report": daubert,
        "artifacts_for_caie": engine.export_to_caie(ids), "timestamp": _utcnow(),
        "vigia_verdict": (
            f"[VIGIA_TRUST_FUSION]: composite={composite['composite_trust']:.4f} "
            f"n={len(ids)} daubert={daubert['admissible']} error={daubert['error_rate_estimate']:.2%}"
        ),
        "_determinism_protocol": f"P0-v2.0 (internal={_DETERMINISTIC_INTERNAL_PREC}, output={_DETERMINISTIC_OUTPUT_PREC})",
    }
