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


# P0-001 census §5.3: umbrales de clasificación en Fraction — el invariante
# Fraction-pura del path de veredicto pide que las comparaciones no dependan
# de literales float. Semántica idéntica a los literales previos (2.0, 1.5,
# 3.0, 0.5 son exactamente representables); mismo patrón que el override
# L-036 en vigia_agent.py (_to_frac + Fraction thresholds).
_Z_TECHNIQUE = Fraction(2, 1)   # antes: > 2.0
_Z_ACTIVE = Fraction(3, 2)      # antes: > 1.5
_Z_CRITICAL = Fraction(3, 1)    # antes: > 3.0
_Z_CONTRADICT = Fraction(1, 2)  # antes: <= 0.5


def _z_frac(signal: SignalOutput) -> Fraction:
    """z_score del DTO (float) → Fraction vía str(), NaN/inf → 0."""
    z = signal.z_score
    if isinstance(z, Fraction):
        return z
    try:
        if z != z or z in (float("inf"), float("-inf")):
            return Fraction(0, 1)
        return Fraction(str(z))
    except (ValueError, TypeError, ZeroDivisionError):
        return Fraction(0, 1)


def _is_primary_signal(signal: SignalOutput) -> bool:
    """
    F5 (AUDITORIA_PIPELINE_ROBUSTEZ): una señal es PRIMARIA si proviene de un
    artefacto de evidencia. Las señales DERIVADAS (motores engine: resonance,
    patterns, timeline, adversarial robustness) y los marcadores `unanalyzed`
    no son evidencia — no deben contar para el gate de corroboración ≥3 ni
    alimentar el CCS. Señales sin metadata se tratan como primarias
    (compatibilidad con adaptadores que no etiquetan).
    """
    meta = signal.metadata if isinstance(signal.metadata, dict) else {}
    if meta.get("signal_class") == "derived":
        return False
    if meta.get("unanalyzed"):
        return False
    return True


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
        # F5: el gate de corroboración cuenta SOLO señales primarias — las
        # derivadas (engine/timeline/adv_robust) inflaban el conteo y un solo
        # artefacto real "pasaba" el gate disfrazado de 5 señales (N4).
        primary = [s for s in signals if _is_primary_signal(s)]
        if len(primary) < 3:
            return AbductionTrace(
                peirce_narrative=(
                    f"[FIRSTNESS] Señales primarias insuficientes: {len(primary)} "
                    f"primaria(s) de {len(signals)} totales.\n"
                    f"[SECONDNESS] El gate de corroboración Daubert (≥3 fuentes "
                    f"primarias) no se satisface — las señales derivadas de motores "
                    f"engine no cuentan como corroboración.\n"
                    f"[THIRDNESS] Sin base para inferencia abductiva. Veredicto: "
                    f"UNDETERMINED (→ ABSTAIN en el agente)."
                ),
            )

        # F2 (AUDITORIA_PIPELINE_ROBUSTEZ, N1): TODO el camino v2 va dentro del
        # try — antes solo run_pipeline estaba protegido y _build_hypotheses
        # crasheaba con AssertionError (INVARIANTE 4) que escapaba hasta el
        # orquestador, produciendo el genérico "[FIRSTNESS] Pipeline error."
        try:
            # FIX (AUDITORIA_PIPELINE_ROBUSTEZ, N17): instancia v2 FRESCA por
            # llamada. AbductiveReasonerV2 acumula estado (selected_hypothesis,
            # phase_log) entre run_pipeline() — reutilizarla contamina la
            # corrida siguiente (p.ej. un empate heredaba la hipótesis
            # seleccionada de la llamada anterior).
            self._v2 = AbductiveReasonerV2()

            # ── 1. Convertir signals a ArtifactRecords ──
            artifacts = self._signals_to_artifacts(primary)

            # ── 2. Construir hipótesis candidatas ──
            hypotheses = self._build_hypotheses(primary)

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
            result = self._v2.run_pipeline(
                artifacts=artifacts,
                candidate_hypotheses=hypotheses,
                baseline_expectations=baseline,
                memory_has_active_thread=any(
                    s.tool_name == "MEMORY_FORENSICS" and _z_frac(s) > _Z_TECHNIQUE
                    for s in primary
                ),
                si_fn_delta_seconds=None,  # No disponible en esta capa
                c2_ip_known=False,  # Simplificado
                registry_service_match=False,
                inversion=inversion,
            )

            # ── 6. Convertir resultado v2 → AbductionTrace v1 ──
            return self._v2_result_to_trace(result, primary)
        except Exception as e:  # pylint: disable=broad-except
            # F2: el error nunca más genérico ni solo-en-logs. best_hypothesis
            # REASONER_ERROR mapea a ABSTAIN en el agente (nunca benigno), y la
            # narrativa conserva el tipo y mensaje de la excepción.
            return AbductionTrace(
                best_hypothesis="REASONER_ERROR",
                peirce_narrative=(
                    f"[FIRSTNESS] {len(signals)} señales recibidas "
                    f"({len(primary)} primarias) — extracción completada.\n"
                    f"[SECONDNESS] Error en pipeline v2: {type(e).__name__}: {e}.\n"
                    f"[THIRDNESS] Sin inferencia abductiva — el veredicto se "
                    f"resuelve por override determinista de señales (L-036) o "
                    f"ABSTAIN. El fallo del razonador NO es evidencia de "
                    f"benignidad ni de malicia."
                ),
            )

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
            ont_level = OntologicalLevel.TECHNIQUE if _z_frac(s) > _Z_TECHNIQUE else OntologicalLevel.TACTIC
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
        """
        Construye hipótesis básicas a partir de señales activas.

        FIX (AUDITORIA_PIPELINE_ROBUSTEZ, N1+N2):
        - INVARIANTE 4: ninguna DecisionTrace puede tener supporting_artifacts
          ni applied_rules vacíos. La hipótesis benigna se apoya en las señales
          bajo umbral (su evidencia real) o en la expectativa de baseline; la
          maliciosa, en las señales activas o en un marcador explícito.
        - CCS por hipótesis: los CausalLink de H2 son la NEGACIÓN de los de H1.
          Antes ambas compartían el MISMO objeto ccs → empate garantizado en
          phase_thirdness, resuelto por orden lexicográfico a favor de
          H2-BENIGN (sesgo benigno estructural).
        """
        active_tools = sorted({s.tool_name for s in signals if _z_frac(s) > _Z_ACTIVE})
        inactive_tools = sorted({s.tool_name for s in signals if _z_frac(s) <= _Z_ACTIVE})

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
            supporting_artifacts=active_tools or ["NO_ACTIVE_SIGNALS"],
            applied_rules=["T1055", "T1070", "T1547"],
            intermediate_scores=[Fraction(8, 10)],
            final_score=Fraction(7, 10),
            timestamp_utc="2026-05-06T00:00:00Z",
        )

        # CCS por hipótesis: consistencia de cada señal con CADA hipótesis.
        # H1 (maliciosa): consistente si la señal está activa (z>1.5).
        # H2 (benigna):   consistente si la señal está bajo umbral (z<=1.5).
        mal_links = []
        ben_links = []
        for i, s in enumerate(signals):
            is_active = _z_frac(s) > _Z_ACTIVE
            mal_links.append(CausalLink(
                link_id=f"H1-{i:03d}-{s.tool_name}",
                description=s.tool_name,
                weight=Fraction(1, 1),
                evidence_present=True,
                consistent_with_hypothesis=is_active,
                is_broken=False,
            ))
            ben_links.append(CausalLink(
                link_id=f"H2-{i:03d}-{s.tool_name}",
                description=s.tool_name,
                weight=Fraction(1, 1),
                evidence_present=True,
                consistent_with_hypothesis=not is_active,
                is_broken=False,
            ))
        ccs_mal = CausalClosureEngine.compute(mal_links)
        ccs_ben = CausalClosureEngine.compute(ben_links)

        h_mal = AbductiveHypothesis(
            hypothesis_id="H1-MALICIOUS",
            description="Compromiso confirmado por evidencia forense cruzada",
            objective_level="DATA_EXFILTRATION_OR_PERSISTENCE",
            tactic_level="TA0005_DEFENSE_EVASION",
            technique_level="T1055_PROCESS_INJECTION",
            ccs=ccs_mal,
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
            # La evidencia de la hipótesis nula son las señales bajo umbral;
            # si todas están activas, el soporte es la expectativa de baseline.
            supporting_artifacts=inactive_tools or ["BASELINE_EXPECTATION"],
            applied_rules=["NULL_HYPOTHESIS_BASELINE"],
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
            ccs=ccs_ben,
            scores=ben_scores,
            trace=ben_trace,
        )

        return [h_mal, h_ben]

    @staticmethod
    def _v2_result_to_trace(result: Dict[str, Any], signals: List[SignalOutput]) -> AbductionTrace:
        """
        Convierte dict de salida v2 a AbductionTrace v1.

        FIX (AUDITORIA_PIPELINE_ROBUSTEZ, N3 + F4):
        - Veredicto v2 ABSTAIN → best_hypothesis "ABSTAIN_V2" (mapea a ABSTAIN
          en el agente). Antes se exponía el nombre de la hipótesis ganadora
          ("H2-BENIGN") y el agente lo clasificaba NOISE — un ABSTAIN
          deliberado se convertía en veredicto benigno.
        - La hipótesis seleccionada se traduce al vocabulario del agente con
          gate Daubert: MALICIOUS solo con ≥2 tipos de artefacto con z>3.
        - La narrativa usa las notas Peircean reales de phases[] del motor v2
          en vez de descartarlas.
        """
        verdict = result.get("verdict", "ABSTAIN")
        selected = result.get("selected_hypothesis")
        reason_code = result.get("reason_code", "")
        ccs_dict = result.get("ccs", {}) or {}

        # Extraer posterior del CCS si está disponible
        posterior = Fraction(0, 1)
        try:
            posterior = Fraction(ccs_dict.get("value", "0"))
        except Exception:
            pass

        # Tipos de artefacto con señal crítica (z>3) — gate Daubert de dos
        # fuentes independientes para poder afirmar MALICIOUS.
        critical_types = sorted({
            (s.metadata or {}).get("artifact_type", s.tool_name)
            for s in signals if _z_frac(s) > _Z_CRITICAL
        })

        if verdict == "ABSTAIN" or not selected:
            best_hypothesis = "ABSTAIN_V2"
            is_conclusive = False
        elif selected == "H1-MALICIOUS":
            if len(critical_types) >= 2:
                best_hypothesis = "MALICIOUS_INTENT_DETECTED"
            else:
                best_hypothesis = "INTENT_DETECTED"
            is_conclusive = verdict == "REJECT" and posterior > CCS_THRESHOLD_ADMISSIBLE
        elif critical_types:
            # Guard anti-swallow: la hipótesis benigna ganó por mayoría de
            # señales quietas, pero existe al menos una señal primaria crítica
            # (z>3). Una anomalía estructural de esa magnitud no puede
            # sellarse como NOISE conclusivo por dilución — se degrada a
            # SUSPICION (anomalía presente, sin evidencia de coordinación).
            best_hypothesis = "SUSPICION_DETECTED"
            is_conclusive = False
        else:  # H2-BENIGN sin señales críticas
            best_hypothesis = "NO_ANOMALY_DETECTED"
            is_conclusive = verdict == "REJECT" and posterior > CCS_THRESHOLD_ADMISSIBLE

        # Narrativa: capa Peircean real del motor v2 (phases[].notes), con
        # fallback determinista si una fase no reportó notas. Las notas del
        # motor empiezan con "FASE: " — se remueve para no duplicar el tag.
        phase_notes = {}
        for p in result.get("phases", []) or []:
            note = p.get("notes", "") or ""
            phase_name = p.get("phase", "")
            if note.startswith(f"{phase_name}: "):
                note = note[len(phase_name) + 2:]
            phase_notes[phase_name] = note
        first = phase_notes.get("FIRSTNESS") or (
            f"{len(signals)} señales primarias procesadas por motor v2."
        )
        second = phase_notes.get("SECONDNESS") or (
            "Contraste contra baseline no reportado por el motor v2."
        )
        second += (
            f" Veredicto v2: {verdict}"
            + (f" (motivo: {reason_code})" if verdict == "ABSTAIN" and reason_code else "")
            + f". CCS: {ccs_dict.get('value', 'N/A')}."
        )
        third = phase_notes.get("THIRDNESS") or (
            f"Hipótesis seleccionada: {selected or 'ninguna'}."
        )
        third += f" Mapeo VIGÍA: {best_hypothesis}."
        if verdict == "ABSTAIN" and result.get("detail"):
            third += f" Detalle: {result['detail']}"
        narrative = (
            f"[FIRSTNESS] {first}\n"
            f"[SECONDNESS] {second}\n"
            f"[THIRDNESS] {third}"
        )

        # Hipótesis rankeadas
        ranked = []
        if selected:
            ranked.append({
                "name": selected,
                "posterior": str(posterior),
                "level": "TECHNIQUE",
            })

        return AbductionTrace(
            best_hypothesis=best_hypothesis,
            best_posterior=posterior,
            confidence=posterior if is_conclusive else posterior * Fraction(8, 10),
            peirce_narrative=narrative,
            is_conclusive=is_conclusive,
            ontological_level="TECHNIQUE",
            ranked_hypotheses=ranked,
            key_supporting=[s.tool_name for s in signals if _z_frac(s) > _Z_ACTIVE],
            key_contradicting=[s.tool_name for s in signals if _z_frac(s) <= _Z_CONTRADICT],
            pruned=[],
            contradiction_type=None,
        )
