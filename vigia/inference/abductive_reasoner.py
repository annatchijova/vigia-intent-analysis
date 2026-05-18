"""
vigia/engine/abductive_reasoner.py

BRIDGE P2: Wrapper que expone la API v1 (método reason(signals)) pero usa
AbductiveReasonerV2 internamente para cálculo de CCS, veto y veredicto Daubert.

Mantiene compatibilidad con sift_orchestrator.py sin refactorización mayor.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

# Importar v2 completo
from vigia.inference.abductive_reasoner_v2 import (
    AbductiveReasonerV2,
    ArtifactRecord,
    EvidenceLayer,
    OntologicalLevel,
    CausalClosureEngine,
    CausalLink,
    AbductiveHypothesis,
    HypothesisScores,
    DecisionTrace,
    InferenceStep,
    InversionCausalEngine,
    InversionAnalysis,
    InversionVerdict,
    AbstainConditionsEngine,
    AbstainCheck,
    AbstainReason,
    CCS_THRESHOLD_ADMISSIBLE,
)

from vigia.core.ebs_v1 import SignalOutput


@dataclass
class AbductionTrace:
    """API v1 compatible — campos que espera sift_orchestrator.py"""
    best_hypothesis: str = "UNDETERMINED"
    best_posterior: Fraction = Fraction(0, 1)
    best_ibe_score: Fraction = Fraction(0, 1)
    ranked_hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    key_supporting: List[str] = field(default_factory=list)
    key_contradicting: List[str] = field(default_factory=list)
    peirce_narrative: str = "[FIRSTNESS] No razonamiento ejecutado."
    pruned: List[str] = field(default_factory=list)
    is_conclusive: bool = False
    confidence: Fraction = Fraction(0, 1)
    contradiction_type: Optional[str] = None
    ontological_level: Optional[str] = None


class AbductiveReasoner:
    """
    Wrapper v1-compatible sobre AbductiveReasonerV2.

    Uso:
        reasoner = AbductiveReasoner()
        trace = reasoner.reason(signals)
    """

    def __init__(self) -> None:
        self._v2 = AbductiveReasonerV2()

    def reason(self, signals: List[SignalOutput]) -> AbductionTrace:
        if len(signals) < 3:
            return AbductionTrace(
                peirce_narrative=f"[FIRSTNESS] Señales insuficientes ({len(signals)}).",
            )

        # ── 1. Convertir signals a ArtifactRecords ──
        artifacts = self._signals_to_artifacts(signals)

        # ── 2. Construir hipótesis candidatas ──
        hypotheses = self._build_hypotheses(signals)

        # ── 3. Baseline expectations (simplificado) ──
        baseline = {a.artifact_id: "unknown" for a in artifacts}

        # ── 4. Inversion Analysis (sin contradicción por defecto) ──
        inversion = InversionAnalysis(
            verdict=InversionVerdict.NO_CONTRADICTION,
            dominant_layer=None,
            reasoning="No se detectó contradicción Memory vs Disk en el wrapper.",
            decorative_not_causal=False,
        )

        # ── 5. Ejecutar pipeline v2 ──
        try:
            result = self._v2.run_pipeline(
                artifacts=artifacts,
                candidate_hypotheses=hypotheses,
                baseline_expectations=baseline,
                memory_has_active_thread=any(
                    s.tool_name == "MEMORY_FORENSICS" and s.z_score > 2.0 for s in signals
                ),
                si_fn_delta_seconds=None,  # No disponible en esta capa
                c2_ip_known=False,  # Simplificado
                registry_service_match=False,
                inversion=inversion,
            )
        except Exception as e:
            return AbductionTrace(
                peirce_narrative=f"[FIRSTNESS] Error en pipeline v2: {e}",
            )

        # ── 6. Convertir resultado v2 → AbductionTrace v1 ──
        return self._v2_result_to_trace(result, signals)

    @staticmethod
    def _signals_to_artifacts(signals: List[SignalOutput]) -> List[ArtifactRecord]:
        """Infiere layer y ontología desde tool_name de SignalOutput."""
        layer_map = {
            "MEMORY_FORENSICS": EvidenceLayer.MEMORY,
            "NETWORK_FORENSICS": EvidenceLayer.NETWORK,
            "REGISTRY_RTR": EvidenceLayer.REGISTRY,
            "MFT_ANALYZER": EvidenceLayer.DISK_MFT,
            "EVENT_LOG": EvidenceLayer.REGISTRY,  # Logs son semi-volátiles
            "PREFETCH_ANALYZER": EvidenceLayer.DISK_MFT,
            "USB_DEVICE_TRACKER": EvidenceLayer.REGISTRY,
            "BROWSER_FORENSICS": EvidenceLayer.DISK_MFT,
            "SHELLBAG_ANALYZER": EvidenceLayer.REGISTRY,
            "AMCACHE_SHIMCACHE": EvidenceLayer.DISK_MFT,
        }
        artifacts = []
        for i, s in enumerate(signals):
            layer = layer_map.get(s.tool_name, EvidenceLayer.DISK_MFT)
            ont_level = OntologicalLevel.TECHNIQUE if s.z_score > 2.0 else OntologicalLevel.TACTIC
            artifacts.append(ArtifactRecord(
                artifact_id=f"SIG-{i:03d}-{s.tool_name}",
                source_path=s.tool_name,
                sha256_hash="0" * 64,
                acquisition_timestamp_utc="2026-05-06T00:00:00Z",
                byte_size=0,
                layer=layer,
                ontology_level=ont_level,
                observed=True,
            ))
        return artifacts

    @staticmethod
    def _build_hypotheses(signals: List[SignalOutput]) -> List[AbductiveHypothesis]:
        """Construye hipótesis básicas a partir de señales activas."""
        active_tools = {s.tool_name for s in signals if s.z_score > 1.5}

        # Hipótesis MALICIOSA
        mal_scores = HypothesisScores(
            hypothesis_id="H1-MALICIOUS",
            technique_score=Fraction(8, 10),
            tactic_score=Fraction(6, 10),
            objective_score=Fraction(4, 10),
        )
        mal_trace = DecisionTrace(
            decision_id="H1-trace",
            conclusion="Actividad maliciosa detectada por múltiples motores SIFT",
            supporting_artifacts=list(active_tools),
            applied_rules=["T1055", "T1070", "T1547"],
            intermediate_scores=[Fraction(8, 10)],
            final_score=Fraction(7, 10),
            timestamp_utc="2026-05-06T00:00:00Z",
        )

        # Construir CCS simple: ratio de señales activas / total
        total = len(signals)
        active = len([s for s in signals if s.z_score > 1.5])
        ccs_links = []
        for s in signals:
            is_active = s.z_score > 1.5
            ccs_links.append(CausalLink(
                link_id=s.tool_name,
                description=s.tool_name,
                weight=Fraction(1, 1),
                evidence_present=True,
                consistent_with_hypothesis=is_active,
                is_broken=False,
            ))
        ccs = CausalClosureEngine.compute(ccs_links)

        h_mal = AbductiveHypothesis(
            hypothesis_id="H1-MALICIOUS",
            description="Compromiso confirmado por evidencia forense cruzada",
            objective_level="DATA_EXFILTRATION_OR_PERSISTENCE",
            tactic_level="TA0005_DEFENSE_EVASION",
            technique_level="T1055_PROCESS_INJECTION",
            ccs=ccs,
            scores=mal_scores,
            trace=mal_trace,
        )

        # Hipótesis BENIGNA
        ben_scores = HypothesisScores(
            hypothesis_id="H2-BENIGN",
            technique_score=Fraction(2, 10),
            tactic_score=Fraction(1, 10),
            objective_score=Fraction(1, 10),
        )
        ben_trace = DecisionTrace(
            decision_id="H2-trace",
            conclusion="Sin evidencia concluyente de actividad maliciosa",
            supporting_artifacts=[],
            applied_rules=[],
            intermediate_scores=[Fraction(1, 10)],
            final_score=Fraction(1, 10),
            timestamp_utc="2026-05-06T00:00:00Z",
        )
        h_ben = AbductiveHypothesis(
            hypothesis_id="H2-BENIGN",
            description="Actividad legítima o insuficiente evidencia",
            objective_level="LEGITIMATE_OPERATION",
            tactic_level="NONE",
            technique_level="NONE",
            ccs=ccs,  # mismo ccs, distinta interpretación
            scores=ben_scores,
            trace=ben_trace,
        )

        return [h_mal, h_ben]

    @staticmethod
    def _v2_result_to_trace(result: Dict[str, Any], signals: List[SignalOutput]) -> AbductionTrace:
        """Convierte dict de salida v2 a AbductionTrace v1."""
        verdict = result.get("verdict", "ABSTAIN")
        selected = result.get("selected_hypothesis", "UNDETERMINED")
        ccs_dict = result.get("ccs", {})

        # Extraer posterior del CCS si está disponible
        posterior = Fraction(0, 1)
        try:
            posterior = Fraction(ccs_dict.get("value", "0"))
        except Exception:
            pass

        is_conclusive = verdict == "REJECT" and posterior > CCS_THRESHOLD_ADMISSIBLE

        # Narrativa
        narrative = f"[FIRSTNESS] {len(signals)} señales procesadas por motor v2.\n"
        narrative += f"[SECONDNESS] Veredicto v2: {verdict}. CCS: {ccs_dict.get('value', 'N/A')}.\n"
        narrative += f"[THIRDNESS] Hipótesis seleccionada: {selected}."

        # Hipótesis rankeadas
        ranked = []
        for hyp in result.get("phases", []):
            if hyp.get("phase") == "THIRDNESS":
                ranked.append({
                    "name": selected,
                    "posterior": str(posterior),
                    "level": "TECHNIQUE",
                })

        return AbductionTrace(
            best_hypothesis=selected,
            best_posterior=posterior,
            confidence=posterior if is_conclusive else posterior * Fraction(8, 10),
            peirce_narrative=narrative,
            is_conclusive=is_conclusive,
            ontological_level="TECHNIQUE",
            ranked_hypotheses=ranked,
            key_supporting=[s.tool_name for s in signals if s.z_score > 1.5],
            key_contradicting=[s.tool_name for s in signals if s.z_score <= 0.5],
            pruned=[],
            contradiction_type=None,
        )
