"""
vigia/pipeline.py
─────────────────────────────────────────────────────────────────────────────
Pipeline de Integración VIGÍA Forensic Suite EBS v1

ARQUITECTURA COMPLETA — CAPAS ESTANCAS (Zero-Trust):

    CAPA 0: models/ebs_v1.py         — Contratos de datos (inmutable)
    CAPA 1: (señales externas)       — Herramientas forenses SDA/CLI/GCI/etc.
    CAPA 2: engine/                  — Inferencia multivariada (sin LLM)
        └─ likelihood_engine.py      — KDE + Ledoit-Wolf
        └─ graph_stability.py        — Bootstrap stability selection
    CAPA 3: governance/              — Gobernanza y riesgo
        └─ risk_bounded_layer.py     — r=(1-P)·(1+λD)·(1+γ(1-S))
    CAPA 4: audit/ + action/         — Auditoría y acción controlada
        └─ audit_action.py           — Diff / Optimizer / PolicyEngine / Executor
    CAPA 5: forensics/               — Verificación independiente
        └─ verify_ebs_v1.py          — Sin dependencias del runtime

REGLA DE ORO:
    El LLM (PeircePlanner) queda fuera del loop de decisión matemática.
    Su única función: traducir el ForensicBundle sellado a narrativa humana.

COMPATIBILIDAD:
    Claude Code  — integración via MCP bridge
    Ollama       — backend LLM para narrativa (PeircePlanner)
    SIFT         — consumo del ForensicBundle como JSON sellado

FLUJO:
    signals → LikelihoodEngine → EvidenceGraph → RiskLayer
    → DecisionTrace → ForensicBundle.seal() → SIFT

─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import importlib
import json
import logging
import os
import subprocess
import sys
import asyncio
import tempfile
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Imports internos con paths relativos robustos
# ---------------------------------------------------------------------------

# Patron de raiz dinamica (DeepSeek) — blindado
_ROOT_PIPELINE = os.path.dirname(os.path.abspath(__file__))
if _ROOT_PIPELINE not in sys.path:
    sys.path.insert(0, _ROOT_PIPELINE)

from vigia.core.ebs_v1 import (
    SignalOutput, EvidenceGraph, EvidenceEdge,
    DecisionTrace, ForensicBundle, PolicySpec, SystemState,
    ActionRecord, AbductionTrace, make_default_policy,
)
from vigia.core.likelihood_engine import LikelihoodEngine
from vigia.core.graph_stability import GraphStabilityEngine
from vigia.core.risk_bounded_layer import (
    RiskBoundedDecisionLayer, SelfAdaptiveRiskPolicy, PolicyStabilityController,
)
from vigia.core.audit_action import (
    EvidenceGraphDiff, InterventionOptimizer,
    FormalPolicyEngine, SafeActionExecutor,
)
from vigia.core.bundle_builder import BundleBuilder

# ---------------------------------------------------------------------------
# Imports defensivos — integración soberana (Segundidad + Terceridad)
# Cada módulo es opcional: si no está disponible, el pipeline corre en modo
# degradado documentado. Nunca se lanza excepción por import fallido.
# ---------------------------------------------------------------------------
try:
    from vigia.tools.visible_variables import VisibleVariablesEngine
    _VISIBLE_VARS_AVAILABLE = True
except ImportError:
    VisibleVariablesEngine = None  # type: ignore
    _VISIBLE_VARS_AVAILABLE = False
    logger.warning("[Pipeline] VisibleVariablesEngine no disponible — lazy abstraction desactivada")

try:
    from vigia.inference.abductive_intent_engine import AbductiveIntentEngine
    _ABDUCTIVE_AVAILABLE = True
except ImportError:
    AbductiveIntentEngine = None  # type: ignore
    _ABDUCTIVE_AVAILABLE = False
    logger.warning("[Pipeline] AbductiveIntentEngine no disponible — Terceridad desactivada")

try:
    from vigia.forensics.vision_audit import vision_intent_audit
    _VISION_AVAILABLE = True
except ImportError:
    vision_intent_audit = None  # type: ignore
    _VISION_AVAILABLE = False
    logger.warning("[Pipeline] vision_intent_audit no disponible — visión forense desactivada")

try:
    from vigia.core.lr_calibration import LRCalibrator
    _LR_CALIBRATOR_AVAILABLE = True
except ImportError:
    LRCalibrator = None  # type: ignore
    _LR_CALIBRATOR_AVAILABLE = False
    logger.warning("[Pipeline] LRCalibrator no disponible — LR sin calibración logística")

try:
    from vigia.core.execution_logger import VigiaExecutionLogger
    _EXEC_LOGGER_AVAILABLE = True
except ImportError:
    VigiaExecutionLogger = None  # type: ignore
    _EXEC_LOGGER_AVAILABLE = False
    logger.warning("[Pipeline] VigiaExecutionLogger no disponible — Agent Execution Logs desactivados")


# ---------------------------------------------------------------------------
# VigiaPipeline — orquestador principal
# ---------------------------------------------------------------------------

class VigiaPipeline:
    """
    Orquestador del pipeline forense VIGÍA EBS v1.

    Encapsula todas las capas estancas y expone una API simple:
        bundle = pipeline.run(signals)

    O con control detallado:
        result = pipeline.run_full(signals, evidence_graph=graph)

    El ForensicBundle producido es el artefacto de entrega final a SIFT.
    """

    def __init__(
        self,
        calibration_path: Optional[str] = None,
        covariance_path: Optional[str] = None,
        policy: Optional[PolicySpec] = None,
        graph_bootstrap_rounds: int = 500,
        graph_stability_threshold: float = 0.85,
        lambda_init: float = 2.0,
        gamma_init: float = 2.0,
        epsilon_init: float = 0.05,
        adaptive_policy: bool = True,
        engine_attestation_hash: str = "",
        ecl_hash: str = "",
        ollama_model: Optional[str] = None,  # ej: "llama3.2" para PeircePlanner
    ) -> None:
        # Política formal
        self._policy_spec = policy or make_default_policy(
            epsilon=epsilon_init,
            lambda_drift=lambda_init,
            gamma_stability=gamma_init,
        )

        # Capa 2: motores de inferencia
        # hint_threshold derivados de PolicySpec — no hardcodeados en el motor
        _eps = self._policy_spec.epsilon_accept
        self._likelihood_engine = LikelihoodEngine(
            calibration_path=calibration_path,
            covariance_path=covariance_path,
            hint_threshold_reject=1.0 - _eps,
            hint_threshold_accept=_eps,
        )
        self._graph_engine = GraphStabilityEngine(
            n_bootstrap=graph_bootstrap_rounds,
            stability_threshold=graph_stability_threshold,
        )

        # Capa 3: gobernanza
        # BLOQUE 4: epsilon_accept/reject leidos de PolicySpec — sin hardcoding
        stability_ctrl = PolicyStabilityController()
        if adaptive_policy:
            self._adaptive_policy = SelfAdaptiveRiskPolicy(
                lambda_init=self._policy_spec.lambda_drift_init,
                gamma_init=self._policy_spec.gamma_stability_init,
                epsilon_init=self._policy_spec.epsilon_accept,
                stability_controller=stability_ctrl,
            )
        else:
            self._adaptive_policy = None

        # Usar from_policy_spec — todo viene del PolicySpec sellado en el bundle
        self._risk_layer = RiskBoundedDecisionLayer.from_policy_spec(self._policy_spec)
        if self._adaptive_policy is not None:
            self._risk_layer._policy = self._adaptive_policy

        # Capa 4: auditoría y acción
        self._policy_engine = FormalPolicyEngine(self._policy_spec)
        self._optimizer = InterventionOptimizer(self._risk_layer)
        self._executor = SafeActionExecutor(
            self._risk_layer, self._policy_engine, self._optimizer
        )
        self._graph_differ = EvidenceGraphDiff()

        # Metadatos de sellado
        self._engine_attestation_hash = engine_attestation_hash or self._compute_attestation()
        self._ecl_hash = ecl_hash

        # Backend LLM (solo para narrativa — nunca para decisión)
        self._ollama_model = ollama_model

        # H28: LRCalibrator — calibración logística del LR antes de la gobernanza
        # Carga desde calibration_path con sufijo _isotonic.json.
        # Si no existe, pipeline corre sin calibrar (documentado en bundle).
        self._lr_calibrator = None
        if _LR_CALIBRATOR_AVAILABLE and LRCalibrator is not None and calibration_path:
            _iso_path = calibration_path.replace(".json", "_isotonic.json")
            try:
                self._lr_calibrator = LRCalibrator.load(_iso_path)
                logger.info("[VigiaPipeline] H28: LRCalibrator cargado desde %s", _iso_path)
            except Exception:
                logger.info(
                    "[VigiaPipeline] H28: %s no encontrado — LR sin calibración logística.",
                    _iso_path,
                )

        # Estado del pipeline
        self._last_bundle: Optional[ForensicBundle] = None
        self._calibration_dataset: List[Dict] = []

        logger.info(
            "[VigiaPipeline] Inicializado | mode=%s | adaptive=%s | ollama=%s | calibrator=%s",
            self._likelihood_engine._mode,
            adaptive_policy,
            ollama_model or "disabled",
            "loaded" if self._lr_calibrator else "uncalibrated",
        )

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def run(
        self,
        signals: List[SignalOutput],
        drift_score: float = 0.0,
        evidence_graph: Optional[EvidenceGraph] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ForensicBundle:
        """
        Ejecuta el pipeline completo y retorna el ForensicBundle sellado.

        Args:
            signals       : lista de SignalOutput de herramientas forenses
            drift_score   : D ∈ [0,1] — PSI de distribución actual vs referencia
            evidence_graph: grafo pre-computado (si None, se omite condicionamiento)
            metadata      : metadatos adicionales para el bundle

        Returns:
            ForensicBundle sellado y listo para SIFT
        """
        result = self.run_full(signals, drift_score, evidence_graph, metadata)
        return result["bundle"]  # bundle con .integrity asignado por BundleBuilder

    def run_full(
        self,
        signals: List[SignalOutput],
        drift_score: float = 0.0,
        evidence_graph: Optional[EvidenceGraph] = None,
        metadata: Optional[Dict[str, Any]] = None,
        image_paths: Optional[List[str]] = None,
        detected_phase: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Pipeline soberano — Integración Segundidad + Terceridad.

        FLUJO (Doctrina China/Israel):
            [Pre-filtro]  VisibleVariablesEngine filtra señales por fase detectada
                          → Lazy Abstraction: solo variables visibles para la fase
                          → Elimina ruido y alucinaciones estadísticas

            [Primeridad]  vision_intent_audit sobre imágenes del bundle
                          → Fracturas visuales inyectadas como artefactos de Primeridad
                          → digital_perfection, metadata_stripping → señales adicionales

            [Segundidad]  LikelihoodEngine(señales filtradas + señales de visión)
                          → Posterior estadístico P(fabricación | evidencia)

            [Terceridad]  AbductiveIntentEngine(posterior)
                          → Hipótesis de intención consistente con el posterior
                          → consistency_score I ∈ [0,1]

            [Disonancia]  Si posterior indica FABRICADO pero AbductiveIntent
                          no encuentra hipótesis consistente (I < 0.5):
                          → ABSTAIN por Disonancia Semántica (reason_code=ABSTAIN_INTENTION)

            [Gobernanza]  RiskBoundedDecisionLayer con factor ω(1-I)
                          → r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))

            [Sellado]     ForensicBundle con AbductiveResult + LikelihoodResult
                          bajo el mismo bundle_hash — admisibilidad Daubert

        Returns:
            {
                "bundle"         : ForensicBundle sellado
                "sealed_dict"    : dict sellado completo
                "inference"      : resultado LikelihoodEngine
                "abductive"      : resultado AbductiveIntentEngine | None
                "decision"       : DecisionTrace con reason_code y omega
                "vision_signals" : señales de Primeridad inyectadas | []
                "graph_used"     : EvidenceGraph | None
                "intervention"   : recomendación si no ACCEPT | None
                "verify_quick"   : (bool, str)
                "lazy_filtered"  : int — señales descartadas por lazy abstraction
            }
        """
        logger.info(
            "[Pipeline] Inicio soberano — %d señales, drift=%.4f, fase=%s",
            len(signals), drift_score, detected_phase or "UNKNOWN",
        )

        # ── Agent Execution Logger — SANS Find Evil! entregable obligatorio ──
        # Genera data/logs/{case_id}_execution.jsonl con cada paso del razonamiento
        _case_id = (metadata or {}).get("case_id", "unknown")
        _exec_log = None
        if _EXEC_LOGGER_AVAILABLE and VigiaExecutionLogger is not None:
            try:
                _exec_log = VigiaExecutionLogger(_case_id)
            except Exception as _el_exc:
                logger.warning("[Pipeline] ExecutionLogger no pudo iniciar: %s", _el_exc)

        # ── H27: Recalcular drift internamente — no confiar en el parámetro externo ──
        # Si el caller (CLI o script externo) pasa drift_score=0.0 para anular
        # la Risk Bounded Layer, el pipeline lo detecta y lo sobreescribe con el
        # drift calculado desde las propias señales.
        # El drift_score externo solo se usa si no hay señales suficientes para calcular.
        _internal_drift = drift_score  # fallback si no hay suficientes señales
        try:
            z_vals = []
            for s in signals:
                z = s.z_score if hasattr(s, "z_score") else s.get("z_score", 0.0)
                if isinstance(z, (int, float)) and z == z:  # no NaN
                    z_vals.append(float(z))
            if len(z_vals) >= 4:
                from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer as _RBL
                # Usar la mitad de las señales como "referencia" y la otra como "actual"
                # — aproximación válida para Daubert: deriva el drift de los datos del caso
                half = len(z_vals) // 2
                _internal_drift = _RBL.psi_to_drift_score(
                    _RBL.compute_psi(z_vals[:half], z_vals[half:])
                )
                if abs(_internal_drift - drift_score) > 0.1:
                    logger.warning(
                        "[Pipeline] H27: drift recalculado internamente (%.4f) difiere "
                        "del drift externo (%.4f) en más de 0.1. "
                        "Usando drift interno — el externo podría estar manipulado.",
                        _internal_drift, drift_score,
                    )
                drift_score = _internal_drift
        except Exception as _drift_exc:
            logger.warning("[Pipeline] H27: recálculo de drift falló (%s) — usando drift externo", _drift_exc)

        # ── PRE-FILTRO: Lazy Abstraction (VisibleVariablesEngine) ──────────
        # Solo las variables "visibles" para la fase detectada entran al motor
        # de inferencia. Elimina ruido estadístico y señales de fases anteriores.
        filtered_signals = signals
        lazy_filtered_count = 0
        if _VISIBLE_VARS_AVAILABLE and detected_phase and VisibleVariablesEngine is not None:
            try:
                vve = VisibleVariablesEngine()
                visible_tools = vve.get_visible_tools(detected_phase)
                if visible_tools:
                    original_count = len(signals)
                    filtered_signals = [
                        s for s in signals
                        if (s.tool_name if hasattr(s, "tool_name") else s.get("tool_name"))
                        in visible_tools
                    ]
                    lazy_filtered_count = original_count - len(filtered_signals)
                    if lazy_filtered_count > 0:
                        logger.info(
                            "[Pipeline] Lazy abstraction: %d señales filtradas "
                            "(fase=%s, visibles=%s)",
                            lazy_filtered_count, detected_phase, list(visible_tools),
                        )
                    # Si el filtro dejó vacío, usar todas (fail-safe)
                    if not filtered_signals:
                        logger.warning(
                            "[Pipeline] Lazy abstraction vacío para fase=%s — "
                            "usando todas las señales (fail-safe)",
                            detected_phase,
                        )
                        filtered_signals = signals
                        lazy_filtered_count = 0
            except Exception as _vve_exc:
                logger.warning("[Pipeline] VisibleVariablesEngine falló: %s — usando todas", _vve_exc)
                filtered_signals = signals

        # ── PRIMERIDAD: visión forense como artefacto de Primeridad ────────
        # Las "fracturas visuales" detectadas por CLIP/ELA se inyectan como
        # señales adicionales antes de que entren al LikelihoodEngine.
        vision_signals: List[SignalOutput] = []
        vision_metadata: Dict[str, Any] = {}
        if _exec_log:
            _exec_log.log_event(
                phase=detected_phase or "UNKNOWN",
                peirce_layer="FIRSTNESS",
                artifact="vision_input",
                finding=f"{len(image_paths or [])} imagen(es) para análisis visual",
                tool_called="vision_intent_audit",
            )
        if _VISION_AVAILABLE and image_paths and vision_intent_audit is not None:
            import asyncio as _asyncio
            for img_path in image_paths:
                try:
                    try:
                        loop = _asyncio.get_event_loop()
                        if loop.is_running():
                            import concurrent.futures as _cf
                            with _cf.ThreadPoolExecutor(max_workers=1) as ex:
                                vision_result = ex.submit(
                                    _asyncio.run, vision_intent_audit(img_path)
                                ).result(timeout=30)
                        else:
                            vision_result = loop.run_until_complete(vision_intent_audit(img_path))
                    except RuntimeError:
                        vision_result = _asyncio.run(vision_intent_audit(img_path))

                    if vision_result.get("status") == "OK":
                        vms = float(vision_result.get("visual_malice_score", 0.0))
                        # Inyectar como SignalOutput de Primeridad
                        import hashlib as _hl
                        _vid = _hl.sha256(img_path.encode()).hexdigest()[:12]
                        vsig = SignalOutput(
                            tool_name="VISION_AUDIT",
                            signal_id=f"VISION-{_vid}",
                            value=vms,
                            z_score=max(-6.0, min(6.0, (vms - 0.3) / 0.15)),
                            confidence=float(vision_result.get("clip_confidence", 0.7)),
                            metadata={
                                "source": "vision_intent_audit",
                                "peirce_layer": "FIRSTNESS",
                                "top_signals": vision_result.get("top_signals", []),
                                "image_path_hash": _vid,
                            },
                        )
                        vision_signals.append(vsig)
                        vision_metadata[_vid] = vision_result.get("peirce_chain", {})
                        logger.info(
                            "[Pipeline] Primeridad visual: img=%s vms=%.4f z=%.4f",
                            img_path[-32:], vms, vsig.z_score,
                        )
                except Exception as _vis_exc:
                    logger.warning("[Pipeline] vision_audit falló para %s: %s", img_path, _vis_exc)

        # Combinar señales filtradas + señales de visión
        all_signals = filtered_signals + vision_signals

        # ── SEGUNDIDAD: LikelihoodEngine ────────────────────────────────────
        inference_result = self._likelihood_engine.infer(
            signals=all_signals,
            evidence_graph=evidence_graph,
        )
        posterior = inference_result["posterior"]
        graph_stability = (
            evidence_graph.global_stability() if evidence_graph else 1.0
        )

        # ── H28: Calibración logística del posterior (LRCalibrator) ────────
        # El LikelihoodEngine escupe un posterior crudo. El LRCalibrator aplica
        # regresión logística para producir probabilidades calibradas (ECE válido).
        # Sin calibración, el "posterior" es una estimación — no una probabilidad.
        # El método de calibración se registra en inference_result para Daubert.
        lr_calibration_method = "uncalibrated"
        if self._lr_calibrator is not None:
            try:
                # Usamos el log_lr del inference_result como entrada al calibrador
                raw_log_lr = inference_result.get("log_lr", 0.0)
                # Aproximar z_score desde log_lr para la API del calibrador
                _z_approx = max(-6.0, min(6.0, raw_log_lr))
                calibrated_posterior = self._lr_calibrator.calibrated_posterior(_z_approx)
                if 0.0 < calibrated_posterior < 1.0:
                    logger.info(
                        "[Pipeline] H28: posterior calibrado logísticamente %.4f → %.4f",
                        posterior, calibrated_posterior,
                    )
                    posterior = calibrated_posterior
                    inference_result = dict(inference_result)
                    inference_result["posterior"] = posterior
                    lr_calibration_method = "logistic_regression"
            except Exception as _cal_exc:
                logger.warning("[Pipeline] H28: calibración logística falló: %s", _cal_exc)

        inference_result["lr_calibration_method"] = lr_calibration_method

        logger.info(
            "[Pipeline] Segundidad: posterior=%.4f LR=%.4f mode=%s signals_totales=%d calibration=%s",
            posterior, inference_result["lr"], inference_result["mode"],
            len(all_signals), lr_calibration_method,
        )
        if _exec_log:
            _exec_log.log_event(
                phase=detected_phase or "UNKNOWN",
                peirce_layer="SECONDNESS",
                artifact=f"{len(all_signals)} señales",
                finding=(
                    f"posterior={posterior:.4f} LR={inference_result['lr']:.4f} "
                    f"mode={inference_result['mode']} calibration={lr_calibration_method}"
                ),
                tool_called="likelihood_engine",
                confidence=posterior,
            )

        # ── TERCERIDAD: AbductiveIntentEngine ───────────────────────────────
        abductive_result: Optional[Dict[str, Any]] = None
        consistency_score: float = 1.0

        if _ABDUCTIVE_AVAILABLE and AbductiveIntentEngine is not None:
            # STUB — L-027: Integración semántica Terceridad requiere capa de
            # traducción SignalOutput.tool_name → HYPOTHESIS_TEMPLATES.required_artifacts.
            # Hasta entonces: Terceridad no aplica desde VigiaPipeline.
            # Ver KNOWN_LIMITATIONS.md L-027 para detalle.
            # Estado anterior conocido: consistency_score=1.0 (regla de
            # disonancia semántica inactiva, documentado desde 2026-05-06).
            from vigia.core.darvo_detector import adjust_consistency_score
            consistency_score = adjust_consistency_score(1.0, signals)
            abductive_result = None

        # ── GOBERNANZA: RiskBoundedDecisionLayer con factor ω ──────────────
        decision_trace = self._risk_layer.decide(
            posterior=posterior,
            drift_score=drift_score,
            graph_stability=graph_stability,
            inference_result=inference_result,
            consistency_score=consistency_score,
        )

        logger.info(
            "[Pipeline] Gobernanza: %s [%s] risk=%.6f ω=%.4f I=%.4f",
            decision_trace.decision, decision_trace.reason_code,
            decision_trace.risk, decision_trace.omega_intention, consistency_score,
        )
        if _exec_log:
            if decision_trace.decision == "ABSTAIN":
                _exec_log.log_abstain(
                    reason_code=decision_trace.reason_code,
                    explanation=decision_trace.abstain_reason or "Zona de incertidumbre honesta",
                )
            else:
                _exec_log.log_event(
                    phase=detected_phase or "UNKNOWN",
                    peirce_layer="THIRDNESS",
                    artifact="risk_bounded_layer",
                    finding=(
                        f"risk={decision_trace.risk:.6f} "
                        f"reason={decision_trace.reason_code}"
                    ),
                    verdict_partial=decision_trace.decision,
                    confidence=float(decision_trace.posterior),
                )

        # ── INTERVENCIÓN (si no es ACCEPT) ──────────────────────────────────
        intervention = None
        if decision_trace.decision != "ACCEPT":
            current_state = {
                "posterior": posterior,
                "drift_score": drift_score,
                "graph_stability": graph_stability,
                "consistency_score": consistency_score,
            }
            intervention = self._optimizer.recommend(current_state)
            logger.info("[Pipeline] Intervención: %s", intervention.get("message", "N/A"))

        # ── CAIE: Cross-Artifact Incongruence Engine ─────────────────────────
        # Detecta fracturas entre artefactos antes del sellado.
        self._last_caie_result = None
        try:
            from vigia.core.forensic_adapter import ForensicAdapter
            from vigia.tools.caie import cross_artifact_analysis
            context = ForensicAdapter.build_context(filtered_signals, raw_results={})
            if context.caie_artifacts:
                caie_input = [
                    {
                        "source_tool": a.source_tool,
                        "evidence_type": a.evidence_type,
                        "raw_score": a.raw_score,
                        "description": a.description,
                        "metadata": a.metadata,
                        "base_trust": getattr(a, 'base_trust', 1.0),
                    }
                    for a in context.caie_artifacts
                ]
                caie_result = asyncio.run(cross_artifact_analysis(caie_input))
                self._last_caie_result = caie_result
                logger.info(
                    "[Pipeline] CAIE: verdict=%s composite=%.4f fractures=%d",
                    caie_result.get('verdict'),
                    caie_result.get('composite_score', 0.0),
                    caie_result.get('fractures_detected', 0),
                )
            else:
                logger.info("[Pipeline] CAIE: no artifacts to analyze")
        except Exception as _caie_exc:
            logger.warning("[Pipeline] CAIE failed (non-blocking): %s", _caie_exc)

        # ── SELLADO CONJUNTO — Daubert: AbductiveResult + LikelihoodResult ──
        system_state = SystemState(
            lambda_drift=(
                self._adaptive_policy.lambda_t
                if self._adaptive_policy else self._risk_layer._lambda
            ),
            gamma_stability=(
                self._adaptive_policy.gamma_t
                if self._adaptive_policy else self._risk_layer._gamma
            ),
            epsilon_accept=decision_trace.epsilon_used,
            epsilon_reject=decision_trace.epsilon_used,
            drift_score=drift_score,
            graph_stability_global=graph_stability,
            engine_version="vigia-ebs-v1.0",
        )

        graph_for_bundle = evidence_graph or EvidenceGraph(nodes=[], edges=[])

        # AbductionTrace enriquecida con resultado del motor de abducción
        abduction = self._build_abduction_trace(
            all_signals, inference_result, decision_trace,
            abductive_result=abductive_result,
        )

        bundle = ForensicBundle(
            evidence_graph=graph_for_bundle,
            decision_trace=decision_trace,
            policy_spec=self._policy_spec,
            actions=self._executor.get_action_history(),
            system_state=system_state,
            abduction_trace=abduction,
        )

        # Preparar CAIE analysis si está disponible
        caie_analysis = None
        if hasattr(self, '_last_caie_result') and self._last_caie_result:
            caie_analysis = {
                "verdict": self._last_caie_result.get("verdict"),
                "structural_verdict": self._last_caie_result.get("structural_verdict"),
                "composite_score": self._last_caie_result.get("composite_score"),
                "fractures_detected": self._last_caie_result.get("fractures_detected", 0),
                "golden_rules_triggered": self._last_caie_result.get("golden_rules_triggered", 0),
                "fractures": self._last_caie_result.get("fractures", []),
                "key_fractures": [
                    {
                        "type": f.get("type"),
                        "severity": f.get("severity"),
                        "artifact_a": f.get("artifact_a", "")[:100],
                        "artifact_b": f.get("artifact_b", "")[:100],
                    }
                    for f in self._last_caie_result.get("fractures", [])[:5]
                ],
            }

            # R7 — deterministic devil_advocate. pattern_signal_metadata is
            # always None here: CasePatternLibrary never runs inside
            # pipeline.py (confirmed by direct audit, 2026-06-19 — no
            # reference to CasePatternLibrary/case_pattern_library/
            # sift_orchestrator anywhere in this file). It only runs inside
            # sift_orchestrator.py, a separate, currently unconnected path.
            # See KNOWN_LIMITATIONS.md. The composer falls back to an
            # explicit scope-limitation narrative instead of a generic
            # template.
            if caie_analysis.get("verdict") in ("MALICE", "INTENT"):
                from vigia.core.devil_advocate_gen import compose_devil_advocate_struct
                caie_analysis["devil_advocate"] = compose_devil_advocate_struct(
                    pattern_signal_metadata=None,
                    raw_verdict=caie_analysis.get("verdict", "UNKNOWN"),
                    mapped_verdict=decision_trace.decision,
                    score=caie_analysis.get("composite_score", 0.0),
                    confidence=decision_trace.posterior,
                    scope_note="standalone scorer mode (vigia/pipeline/pipeline.py)",
                )

        # ── CAIE structural hard gate (runs BEFORE sealing so the override is
        # covered by bundle_hash — caie_analysis is part of bundle_payload) ──
        # Rationale: causal impossibilities and tool-signature fractures are a
        # different epistemic category from probabilistic evidence — they are
        # not subject to Bayesian updating.
        _STRUCTURAL_VETO_TYPES = frozenset({
            # Golden Rules — causal impossibilities (always override)
            "TEMPORAL_CAUSALITY_VIOLATION",
            "CRYPTOGRAPHIC_INCONSISTENCY",        # only when trust_chain_validated=True
            # Structural fractures that force MALICE
            "LOG_VS_MEMORY",
            "DOCUMENT_FORGERY",
            "NETWORK_VS_HOST",
            "MFT_ENTRY_ANOMALY",
            "NARRATIVE_POISONING_DETECTED",
            "TIMESTAMP_PRECISION_ANOMALY",
            "USN_JOURNAL_GAP",
            # EXCLUDED: CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED (severity=0.6, verdict=SUSPICION)
        })
        if caie_analysis is not None:
            _golden_triggered = caie_analysis.get("golden_rules_triggered", 0)
            _all_fractures = caie_analysis.get("fractures", [])
            _veto_fractures = [f for f in _all_fractures if f.get("type") in _STRUCTURAL_VETO_TYPES]
            if _golden_triggered > 0 or len(_veto_fractures) > 0:
                _pre_verdict = caie_analysis.get("verdict")
                _veto_type = _veto_fractures[0]["type"] if _veto_fractures else "golden_rule"
                caie_analysis["gate_verdict"] = "MALICE"
                caie_analysis["gate_override_reason"] = (
                    f"CAIE structural veto: {_veto_type} detected. Pre-override: {_pre_verdict}."
                )
                logger.warning(
                    "[Pipeline] CAIE structural hard gate triggered: verdict overridden "
                    "%s → MALICE (%s)",
                    _pre_verdict, caie_analysis["gate_override_reason"],
                )

        sealed_dict = BundleBuilder.seal(
            bundle,
            engine_attestation_hash=self._engine_attestation_hash,
            ecl_hash=self._ecl_hash,
            caie_analysis=caie_analysis,
        )

        verify_ok, verify_msg = BundleBuilder.quick_verify(sealed_dict)
        if not verify_ok:
            logger.error("[Pipeline] ALERTA: bundle inválido post-sellado: %s", verify_msg)

        # H21: inyectar redundancy_alerts en el bloque INTEGRITY del bundle sellado
        # El bundle ya está sellado (hash calculado sobre el payload).
        # La alerta va DENTRO del bloque integrity — que está EXCLUIDO del hash.
        # Esto permite que el perito vea la alerta SIN invalidar el bundle_hash.
        # === FIX APLICADO ===
        _redundancy = inference_result.get("redundancy_alerts", {})
        if _redundancy.get("twin_pairs_detected", 0) > 0:
            # Agregar al bloque integrity, NO al payload hasheado
            integrity_block = sealed_dict.setdefault("integrity", {})
            integrity_block.setdefault("forensic_alerts", []).append({
                "type": "REDUNDANCY_LOCAL",
                "severity": "WARNING",
                "twin_pairs": _redundancy["twin_pairs_detected"],
                "message": _redundancy.get("alert", ""),
                "action_taken": "LR penalizado por factor n_efectivo/n",
                "daubert_note": (
                    "El motor detectó y neutralizó señales redundantes. "
                    "El LR reportado ya incluye la corrección. "
                    "Ver campo 'contributions' para detalle por señal."
                ),
            })
            logger.warning(
                "[Pipeline] H21: %d par(es) gemelo(s) — alerta de redundancia "
                "inyectada en integrity block (NO invalida bundle_hash).",
                _redundancy["twin_pairs_detected"],
            )

        self._last_bundle = bundle
        self._last_sealed_dict = sealed_dict

        logger.info(
            "[Pipeline] Bundle sellado: %s | %s | decision=%s [%s]",
            bundle.bundle_id[:12], verify_msg,
            decision_trace.decision, decision_trace.reason_code,
        )

        # Registrar veredicto final en el execution log
        if _exec_log:
            _bundle_hash = sealed_dict.get("integrity", {}).get("bundle_hash", "")
            _exec_log.log_verdict(
                verdict=decision_trace.decision,
                confidence=float(decision_trace.posterior * 100),
                reason_code=decision_trace.reason_code,
                bundle_hash=_bundle_hash[:16] + "…" if _bundle_hash else "",
                carnegie_pattern=getattr(abductive_result, "carnegie_pattern", None)
                    if abductive_result else None,
            )
            logger.info("[Pipeline] Agent Execution Log guardado: %s", _exec_log.log_file)

        return {
            "bundle":          bundle,
            "sealed_dict":     sealed_dict,
            "inference":       inference_result,
            "abductive":       abductive_result,
            "decision":        decision_trace,
            "vision_signals":  vision_signals,
            "graph_used":      evidence_graph,
            "intervention":    intervention,
            "verify_quick":    (verify_ok, verify_msg),
            "lazy_filtered":   lazy_filtered_count,
        }



    # ------------------------------------------------------------------
    # Construccion de AbductionTrace
    # ------------------------------------------------------------------

    def _build_abduction_trace(
        self,
        signals: list,
        inference_result: dict,
        decision_trace,
        abductive_result: Optional[Dict[str, Any]] = None,
    ) -> "AbductionTrace":
        """
        Construye la traza abductiva que documenta el razonamiento del sistema.

        Responde a la pregunta del perito:
            "Por que se priorizo esta senal?"
            "Por que se aborto CLIP?"
            "Que patron de atacante emerge de estas anomalias?"

        Semiosis de Peirce aplicada a DFIR:
            Firstness  — senales crudas disponibles y observadas
            Secondness — anomalias detectadas respecto al baseline
            Thirdness  — hipotesis del atacante que emerge de la correlacion
        """
        try:
            contribs = inference_result.get("contributions", [])

            # Firstness: que habia disponible y que se proceso
            tools_available = [s.tool_name for s in signals]
            tools_executed = [c["tool_name"] for c in contribs if c.get("log_lr", 0) != 0]
            tools_skipped = [t for t in tools_available if t not in tools_executed]

            # Señal dominante (mayor contribucion absoluta al log-LR)
            dominant = None
            dominant_z = 0.0
            dominant_cluster = None
            if contribs:
                top = max(contribs, key=lambda c: abs(c.get("log_lr", 0)))
                dominant = top.get("tool_name")
                dominant_z = top.get("z_score", 0.0)
                dominant_cluster = top.get("cluster")

            # Anomalias: senales con z_score > umbral
            ANOMALY_THRESHOLD = 2.0
            anomalies = [
                {
                    "tool": c["tool_name"],
                    "z_score": c["z_score"],
                    "log_lr": c.get("log_lr", 0),
                    "cluster": c.get("cluster"),
                }
                for c in contribs
                if abs(c.get("z_score", 0)) >= ANOMALY_THRESHOLD
            ]

            # Secondness: construir descripcion de anomalia
            if anomalies:
                top_anom = max(anomalies, key=lambda a: abs(a["z_score"]))
                secondness = (
                    f"{top_anom['tool']} z={top_anom['z_score']:.2f} "
                    f"anomalo respecto al baseline AUTHENTIC "
                    f"(cluster: {top_anom['cluster'] or 'sin asignar'})"
                )
            else:
                secondness = "Sin anomalias significativas (z < 2.0)"

            # Firstness: descripcion de lo observado
            mode = inference_result.get("mode", "FALLBACK")
            n_components = inference_result.get("components_used", 0)
            firstness = (
                f"{len(tools_executed)} senal(es) procesadas via {mode}. "
                f"{n_components} cluster(s) de inferencia. "
                f"Señal dominante: {dominant or 'ninguna'} "
                f"(z={dominant_z:.2f})"
            )

            # Thirdness: hipotesis del atacante
            posterior = inference_result.get("posterior", 0.5)
            decision = getattr(decision_trace, "decision", "ABSTAIN")
            risk = getattr(decision_trace, "risk", 0.0)

            if posterior > 0.80 and anomalies:
                thirdness = (
                    f"Patron consistente con fabricacion deliberada. "
                    f"P(fabricacion)={posterior:.3f}. "
                    f"Multiples senales anomalas ({len(anomalies)}) con correlacion "
                    f"estadistica robusta. Decision: {decision} (risk={risk:.3f})."
                )
            elif posterior > 0.50:
                thirdness = (
                    f"Patron ambiguo — posible fabricacion parcial. "
                    f"P(fabricacion)={posterior:.3f}. "
                    f"Evidencia insuficiente para certeza. Decision: {decision}."
                )
            else:
                thirdness = (
                    f"Sin patron de fabricacion detectado. "
                    f"P(fabricacion)={posterior:.3f}. "
                    f"Señales consistentes con contenido AUTHENTIC. Decision: {decision}."
                )

            # Enriquecer Thirdness con resultado del AbductiveIntentEngine si está disponible
            if abductive_result:
                best_hyp = abductive_result.get("best_hypothesis", "")
                hyp_cost = abductive_result.get("hypothesis_cost", 0.0)
                consistency = abductive_result.get("consistency_score", 1.0)
                if best_hyp:
                    thirdness = (
                        f"{thirdness} | AbductiveIntent: hipótesis='{best_hyp}' "
                        f"costo={hyp_cost:.3f} consistencia={consistency:.3f}"
                    )

            # Plan de ejecucion del ResourceOptimizer (si esta disponible)
            plan_rationale = []
            if hasattr(self, "_last_execution_plan"):
                plan_rationale = [
                    {
                        "tool": t.name,
                        "priority": round(t.priority, 4),
                        "cost": t.cost,
                        "executed": t.executed,
                        "skipped": t.skipped,
                    }
                    for t in self._last_execution_plan
                ]

            return AbductionTrace(
                tools_available=tools_available,
                tools_executed=tools_executed,
                tools_skipped=tools_skipped,
                dominant_signal=dominant,
                dominant_z_score=dominant_z,
                cluster_name=dominant_cluster,
                anomalies_found=anomalies,
                peirce_firstness=firstness,
                peirce_secondness=secondness,
                peirce_thirdness=thirdness,
                execution_plan_rationale=plan_rationale,
                abort_triggered=False,
                inference_mode=mode,
                clustering_method=inference_result.get("clustering_method", "heuristic_default"),
                correlation_penalties_applied=any(
                    "corr_penalty" in c.get("method", "") for c in contribs
                ),
            )

        except Exception as e:
            logger.warning("[Pipeline] AbductionTrace no construida: %s — usando traza vacia", e)
            return AbductionTrace(
                peirce_firstness="Error al construir traza abductiva.",
                peirce_secondness="Ver logs del sistema.",
                peirce_thirdness="Traza no disponible.",
            )

    # ------------------------------------------------------------------
    # Entrenamiento del grafo de estabilidad
    # ------------------------------------------------------------------

    def fit_evidence_graph(
        self,
        calibration_dataset: List[Dict[str, Any]],
        nodes: Optional[List[str]] = None,
    ) -> EvidenceGraph:
        """
        Ajusta el EvidenceGraph sobre el dataset de calibración.

        Delega al GraphStabilityEngine (bootstrap B=500).
        El grafo resultante puede pasarse a pipeline.run() como evidence_graph.

        Args:
            calibration_dataset: lista de dicts {tool: z_score} o SignalOutput
            nodes              : nodos explícitos (se infieren si no se proveen)

        Returns:
            EvidenceGraph sellado con π ≥ stability_threshold
        """
        logger.info(
            "[Pipeline] Ajustando EvidenceGraph sobre %d samples",
            len(calibration_dataset),
        )
        graph = self._graph_engine.fit(calibration_dataset, nodes=nodes)
        logger.info(
            "[Pipeline] Grafo: %d nodos, %d aristas estables (τ=%.2f)",
            len(graph.nodes), len(graph.edges), graph.stability_threshold,
        )
        return graph

    # ------------------------------------------------------------------
    # Narrativa LLM (PeircePlanner) — FUERA del loop de decisión
    # ------------------------------------------------------------------

    def generate_narrative(
        self,
        bundle: Optional[ForensicBundle] = None,
        model: Optional[str] = None,
    ) -> Optional[str]:
        """
        Genera narrativa humana a partir del ForensicBundle sellado.

        REGLA DE ORO: El LLM no participa en la decisión matemática.
        Esta función se llama DESPUÉS de .seal() — el bundle ya está cerrado.

        Soporta:
            - Ollama (local): si self._ollama_model está configurado
            - Claude Code: si se usa desde MCP bridge

        Returns:
            Narrativa en texto, o None si no hay backend disponible.
        """
        b = bundle or self._last_bundle
        if b is None:
            logger.warning("[Pipeline] No hay bundle para generar narrativa")
            return None

        if b.integrity is None:
            logger.error("[Pipeline] Bundle no atestado (integrity=None) — narrativa rechazada")
            return None

        backend = model or self._ollama_model
        if backend is None:
            logger.info("[Pipeline] Sin backend LLM configurado — narrativa omitida")
            return None

        try:
            if backend == "gemini":
                return self._call_gemini(b)
            elif backend == "claude":
                return self._call_claude(b)
            else:
                return self._call_ollama(b, backend)
        except Exception as e:
            logger.warning("[Pipeline] Error al llamar %s: %s", backend, e)
            return None

    def _call_ollama(self, bundle: ForensicBundle, model: str) -> str:
        """
        Llama a Ollama (local) para generar narrativa ENFSI-style.

        El prompt incluye el bundle comprimido (no el JSON completo —
        demasiado largo para contexto de LLM).
        """
        summary = self._build_narrative_summary(bundle)
        prompt = self._build_enfsi_prompt(summary)

        # Llamada a Ollama via subprocess (no requiere SDK)
        cmd = [
            "ollama", "run", model,
            "--nowordwrap",
        ]

        proc = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Ollama error: {proc.stderr[:200]}")

        return proc.stdout.strip()

    def _build_narrative_summary(self, bundle: "ForensicBundle") -> dict:
        """Compressed bundle summary for LLM narrative — never the full bundle."""
        dt = bundle.decision_trace
        graph = bundle.evidence_graph
        return {
            "decision": dt.decision,
            "posterior": round(dt.posterior, 4),
            "risk": round(dt.risk, 4),
            "drift": round(dt.drift_score, 4),
            "graph_stability": round(dt.graph_stability, 4),
            "n_stable_edges": len(graph.edges),
            "lambda": round(dt.lambda_drift, 3),
            "gamma": round(dt.gamma_stability, 3),
            "contributions": dt.signal_contributions or [],
        }

    def _build_enfsi_prompt(self, summary: dict) -> str:
        """ENFSI-style forensic narrative prompt shared by all LLM backends."""
        return (
            "Sos un experto en análisis forense digital. "
            "Tu tarea es generar un reporte técnico conciso en español rioplatense "
            "basado en el siguiente resultado de análisis forense. "
            "El análisis fue realizado por VIGÍA, un sistema determinístico. "
            "NO modifiques los números. Usá el vocabulario de ENFSI. "
            "Formato: párrafos cortos, sin emojis, tono pericial.\n\n"
            f"RESULTADO:\n{json.dumps(summary, sort_keys=True, ensure_ascii=False, indent=2)}\n\n"
            "Generá el reporte:"
        )

    def _call_gemini(self, bundle: "ForensicBundle") -> str:
        """Narrative via Gemini API. Requires GEMINI_API_KEY env var."""
        import os
        import httpx
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY not set — export GEMINI_API_KEY=<key>"
            )
        summary = self._build_narrative_summary(bundle)
        prompt = self._build_enfsi_prompt(summary)
        resp = httpx.post(
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    def _call_claude(self, bundle: "ForensicBundle") -> str:
        """Narrative via Anthropic API. Requires ANTHROPIC_API_KEY env var."""
        import os
        try:
            import anthropic
        except ImportError:
            raise RuntimeError(
                "anthropic SDK not installed — pip install anthropic"
            )
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set — export ANTHROPIC_API_KEY=<key>"
            )
        client = anthropic.Anthropic(api_key=api_key)
        summary = self._build_narrative_summary(bundle)
        prompt = self._build_enfsi_prompt(summary)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text.strip()

    # ------------------------------------------------------------------
    # Verificación externa (delega a verify_ebs_v1.py)
    # ------------------------------------------------------------------

    def verify_bundle_external(
        self,
        bundle_path: str,
        strict: bool = False,
    ) -> Dict[str, Any]:
        """
        Verifica un bundle usando el verificador independiente (subprocess).
        Emula cómo SIFT consumiría el bundle.
        """
        verify_script = os.path.join(
            os.path.dirname(__file__), "forensics", "verify_ebs_v1.py"
        )

        if not os.path.exists(verify_script):
            # Fallback: verificación interna
            with open(bundle_path) as f:
                bundle_dict = json.load(f)
            from forensics.verify_ebs_v1 import verify_bundle
            result = verify_bundle(bundle_dict, strict=strict)
            return result.to_dict()

        cmd = [sys.executable, verify_script, bundle_path, "--json"]
        if strict:
            cmd.append("--strict")

        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError:
            return {"error": proc.stdout or proc.stderr, "passed": False}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _compute_attestation(self) -> str:
        """
        Calcula engine_attestation_hash basado en el código fuente disponible.
        En producción debería incluir hash del repo + deps + build.
        """
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            sources = []
            for root, _, files in os.walk(here):
                for fname in sorted(files):
                    if fname.endswith(".py"):
                        fpath = os.path.join(root, fname)
                        try:
                            with open(fpath, "rb") as f:
                                sources.append(f.read())
                        except OSError:
                            pass
            combined = b"".join(sources)
            return hashlib.sha256(combined).hexdigest()
        except Exception:
            return ""

    def save_bundle(self, bundle: ForensicBundle, path: str) -> str:
        """Guarda bundle y retorna file hash para verificación de transporte."""
        return bundle.save(path)

    def load_and_verify(self, bundle_path: str) -> Dict[str, Any]:
        """Carga un bundle desde disco y lo verifica."""
        with open(bundle_path, "r", encoding="utf-8") as f:
            bundle_dict = json.load(f)

        try:
            from forensics.verify_ebs_v1 import verify_bundle
        except ImportError:
            # Fallback si el path no está configurado
            sys.path.insert(0, os.path.dirname(__file__))
            from forensics.verify_ebs_v1 import verify_bundle

        result = verify_bundle(bundle_dict)
        return result.to_dict()

    @property
    def mode(self) -> str:
        return self._likelihood_engine._mode

    @property
    def last_bundle(self) -> Optional[ForensicBundle]:
        return self._last_bundle


# ---------------------------------------------------------------------------
# Función de entrada rápida para Claude Code / MCP
# ---------------------------------------------------------------------------

def run_vigia(
    signals_data: List[Dict[str, Any]],
    drift_score: float = 0.0,
    calibration_path: Optional[str] = None,
    covariance_path: Optional[str] = None,
    ollama_model: Optional[str] = None,
    llm_backend: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Punto de entrada simplificado para uso desde Claude Code / MCP.

    Args:
        signals_data: lista de dicts compatibles con SignalOutput
            [{"tool_name": "SDA", "value": 0.8, "z_score": 2.3, "confidence": 0.9}, ...]
        drift_score : PSI drift score ∈ [0, 1]
        calibration_path: path a modelos KDE calibrados (.pkl)
        covariance_path : path a covarianza Ledoit-Wolf (.pkl)
        ollama_model    : nombre del modelo Ollama para narrativa (legacy)
        llm_backend     : backend LLM para narrativa — "gemini", "claude",
                          o nombre de modelo Ollama. Tiene precedencia sobre
                          ollama_model si ambos están definidos.
        output_path     : si se provee, guarda el bundle en disco

    Returns:
        {
            "decision"    : str — ACCEPT / REJECT / ABSTAIN
            "posterior"   : float
            "risk"        : float
            "bundle_hash" : str
            "bundle_json" : str — bundle completo serializado
            "narrative"   : str | None
            "verify"      : dict
        }
    """
    # Construir SignalOutput desde dicts
    signals = []
    for d in signals_data:
        try:
            s = SignalOutput(
                tool_name=d["tool_name"],
                value=float(d.get("value", 0.0)),
                z_score=float(d.get("z_score", 0.0)),
                confidence=float(d.get("confidence", 1.0)),
                description=d.get("description"),
                metadata=d.get("metadata"),
            )
            signals.append(s)
        except Exception as e:
            logger.warning("[run_vigia] Señal inválida ignorada: %s — %s", d, e)

    # H27: recalcular drift internamente — no confiar en el parámetro externo.
    # Un atacante que controle el script que llama a VIGÍA puede pasar drift=0.0
    # para anular la Risk Bounded Layer. El drift se recalcula desde los z-scores
    # reales de las señales usando PSI. El parámetro externo se usa solo como
    # fallback documentado cuando no hay suficientes señales para PSI.
    internal_drift = drift_score  # fallback documentado
    # P1-21: umbral bajado de 4 a 2 — atacante no puede evadir con 3 señales
    if len(signals) >= 2:
        try:
            from vigia.core.risk_bounded_layer import RiskBoundedDecisionLayer
            z_scores = [s.z_score for s in signals if hasattr(s, "z_score")]
            # Referencia: distribución gaussiana estándar en [-3, 3]
            import random as _rand
            _rng = _rand.Random(42)
            reference = [_rng.gauss(0, 1) for _ in range(max(len(z_scores) * 3, 30))]
            reference = [max(-3.0, min(3.0, v)) for v in reference]
            psi = RiskBoundedDecisionLayer.compute_psi(reference, z_scores)
            internal_drift = RiskBoundedDecisionLayer.psi_to_drift_score(psi)
            if abs(internal_drift - drift_score) > 0.15:
                logger.warning(
                    "[run_vigia] H27: drift externo=%.4f difiere del recalculado=%.4f "
                    "(PSI=%.4f). Usando drift recalculado internamente.",
                    drift_score, internal_drift, psi,
                )
        except Exception as _drift_exc:
            logger.warning(
                "[run_vigia] H27: no se pudo recalcular drift (%s) — "
                "usando parámetro externo %.4f como fallback.",
                _drift_exc, drift_score,
            )

    # Inicializar pipeline
    pipeline = VigiaPipeline(
        calibration_path=calibration_path,
        covariance_path=covariance_path,
    )

    # H28: aplicar LRCalibrator si está disponible — calibración logística
    # El LR crudo del KDE no tiene curva de confianza respaldada hasta que
    # pasa por la regresión logística. Sin esto el "Posterior" es una suposición.
    calibrated_signals = signals
    if _LR_CALIBRATOR_AVAILABLE and LRCalibrator is not None:
        try:
            _cal = LRCalibrator()
            # Intentar cargar calibrador persistido si existe
            _cal_path = (calibration_path or "").replace(".json", "_isotonic.json")
            if _cal_path and __import__("os").path.isfile(_cal_path):
                _cal = LRCalibrator.load(_cal_path)
                if _cal._fitted:
                    # Ajustar z_score de cada señal con el LR calibrado
                    _adjusted = []
                    for sig in signals:
                        try:
                            _log_lr_cal = _cal.calibrated_log_lr(sig.z_score)
                            # Reconstruir señal con z_score equivalente al LR calibrado
                            # z_cal = clip(log_lr_calibrado, -Z_CLIP, Z_CLIP)
                            _z_cal = max(-6.0, min(6.0, _log_lr_cal))
                            import dataclasses as _dc
                            if _dc.is_dataclass(sig):
                                sig_cal = _dc.replace(sig, z_score=_z_cal)
                            else:
                                sig_cal = sig  # fallback si no es dataclass
                            _adjusted.append(sig_cal)
                        except Exception:
                            _adjusted.append(sig)
                    calibrated_signals = _adjusted
                    logger.info("[run_vigia] H28: LR calibrado logísticamente (%d señales)", len(calibrated_signals))
        except Exception as _cal_exc:
            logger.warning("[run_vigia] H28: LRCalibrator falló (%s) — usando señales sin calibrar", _cal_exc)

    # Ejecutar pipeline soberano
    result = pipeline.run_full(calibrated_signals, drift_score=internal_drift)
    bundle = result["bundle"]
    sealed_dict = result["sealed_dict"]

    # Guardar bundle sellado si se pide
    if output_path:
        BundleBuilder.save(sealed_dict, output_path)

    # Generar narrativa DESPUÉS del sellado — post-procesador externo
    # El LLM recibe el bundle ya cerrado, no modifica nada
    narrative = None
    _active_backend = llm_backend or ollama_model
    if _active_backend:
        try:
            narrative = pipeline.generate_narrative(bundle, model=_active_backend)
        except Exception as e:
            logger.warning("[run_vigia] Narrativa no generada: %s", e)

    # Verificación usando BundleBuilder (no bundle.quick_verify)
    verify_ok, verify_msg = BundleBuilder.quick_verify(sealed_dict)

    import json as _json
    return {
        "decision": sealed_dict["decision_trace"]["decision"],
        "posterior": sealed_dict["decision_trace"]["posterior"],
        "risk": sealed_dict["decision_trace"]["risk"],
        "bundle_hash": sealed_dict["integrity"]["bundle_hash"],
        "bundle_json": _json.dumps(sealed_dict, sort_keys=True, indent=2, default=str),
        "narrative": narrative,
        "verify": {"passed": verify_ok, "message": verify_msg},
        "mode": pipeline.mode,
    }


# ---------------------------------------------------------------------------
# Entry point CLI (vigia = pipeline:main en pyproject.toml)
# ---------------------------------------------------------------------------

def main() -> int:
    """
    CLI mínimo del pipeline VIGÍA.

    Uso:
        vigia --signals signals.json [--drift 0.05] [--output bundle.json]

    signals.json: lista de dicts compatibles con SignalOutput
        [{"tool_name": "SDA", "value": 0.8, "z_score": 2.3, "confidence": 0.9}, ...]
    """
    import argparse
    import json as _json_cli
    import sys as _sys_cli

    parser = argparse.ArgumentParser(
        description="VIGÍA Forensic Suite — Pipeline EBS v1",
        epilog="Salida: JSON con decision, posterior, risk, bundle_hash",
    )
    parser.add_argument(
        "--signals", required=True,
        help="JSON con lista de SignalOutput [{tool_name, value, z_score, confidence}]",
    )
    parser.add_argument(
        "--drift", type=float, default=0.0,
        help=(
            "Drift score externo [0.0, 1.0] (default: 0.0). "
            "ADVERTENCIA: el pipeline recalcula el drift internamente desde las señales "
            "(H27). Si el valor interno difiere en más de 0.1, este argumento es ignorado "
            "y se emite una advertencia en el log."
        ),
    )
    parser.add_argument(
        "--output", default=None,
        help="Guardar bundle sellado en este path (opcional)",
    )
    parser.add_argument(
        "--calibration", default=None,
        help="Path a modelos KDE calibrados (.pkl)",
    )
    parser.add_argument(
        "--covariance", default=None,
        help="Path a covarianza Ledoit-Wolf (.pkl)",
    )
    parser.add_argument(
        "--ollama", default=None,
        help="Modelo Ollama para narrativa (ej: llama3.2) — legacy, prefer --llm",
    )
    parser.add_argument(
        "--llm", default=None,
        help=(
            "Backend LLM para narrativa ENFSI post-veredicto. "
            "Valores: 'gemini' (requiere GEMINI_API_KEY), "
            "'claude' (requiere ANTHROPIC_API_KEY), "
            "o nombre de modelo Ollama local (ej: gemma3:27b)."
        ),
    )

    args = parser.parse_args()

    # Cargar señales
    try:
        with open(args.signals) as f:
            signals_data = _json_cli.load(f)
    except (FileNotFoundError, _json_cli.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=_sys_cli.stderr)
        return 1

    result = run_vigia(
        signals_data=signals_data,
        drift_score=args.drift,
        calibration_path=args.calibration,
        covariance_path=args.covariance,
        ollama_model=args.ollama,
        llm_backend=args.llm,
        output_path=args.output,
    )

    # Salida compacta para integración con SIFT
    output = {
        "decision":   result["decision"],
        "posterior":  result["posterior"],
        "risk":       result["risk"],
        "bundle_hash": result["bundle_hash"],
        "verify":     result["verify"],
        "mode":       result["mode"],
    }
    if result.get("narrative"):
        output["narrative"] = result["narrative"]

    print(_json_cli.dumps(output, indent=2, sort_keys=True))
    return 0 if result["verify"]["passed"] else 1


if __name__ == "__main__":
    import sys as _sys_main
    _sys_main.exit(main())
