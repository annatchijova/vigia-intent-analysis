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

from models.ebs_v1 import (
    SignalOutput, EvidenceGraph, EvidenceEdge,
    DecisionTrace, ForensicBundle, PolicySpec, SystemState,
    ActionRecord, AbductionTrace, make_default_policy,
)
from engine.likelihood_engine import LikelihoodEngine
from engine.graph_stability import GraphStabilityEngine
from governance.risk_bounded_layer import (
    RiskBoundedDecisionLayer, SelfAdaptiveRiskPolicy, PolicyStabilityController,
)
from audit.audit_action import (
    EvidenceGraphDiff, InterventionOptimizer,
    FormalPolicyEngine, SafeActionExecutor,
)
from forensics.bundle_builder import BundleBuilder


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

        # Estado del pipeline
        self._last_bundle: Optional[ForensicBundle] = None
        self._calibration_dataset: List[Dict] = []

        logger.info(
            "[VigiaPipeline] Inicializado | mode=%s | adaptive=%s | ollama=%s",
            self._likelihood_engine._mode,
            adaptive_policy,
            ollama_model or "disabled",
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
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo con resultado detallado.

        Returns:
            {
                "bundle"        : ForensicBundle sellado
                "inference"     : dict — resultado del LikelihoodEngine
                "decision"      : DecisionTrace
                "graph_used"    : EvidenceGraph | None
                "intervention"  : dict | None — recomendación si no es ACCEPT
                "verify_quick"  : tuple(bool, str) — verificación interna rápida
            }
        """
        logger.info("[Pipeline] Inicio — %d señales, drift=%.4f", len(signals), drift_score)

        # ── CAPA 2A: Inferencia ────────────────────────────────────────
        inference_result = self._likelihood_engine.infer(
            signals=signals,
            evidence_graph=evidence_graph,
        )
        posterior = inference_result["posterior"]
        graph_stability = (
            evidence_graph.global_stability() if evidence_graph else 1.0
        )

        logger.info(
            "[Pipeline] Inferencia: posterior=%.4f LR=%.4f mode=%s",
            posterior, inference_result["lr"], inference_result["mode"],
        )

        # ── CAPA 3: Decisión ───────────────────────────────────────────
        decision_trace = self._risk_layer.decide(
            posterior=posterior,
            drift_score=drift_score,
            graph_stability=graph_stability,
            inference_result=inference_result,
        )

        logger.info(
            "[Pipeline] Decisión: %s (risk=%.4f, ε=%.4f)",
            decision_trace.decision, decision_trace.risk, decision_trace.epsilon_used,
        )

        # ── CAPA 4: Intervención (si no es ACCEPT) ─────────────────────
        intervention = None
        if decision_trace.decision != "ACCEPT":
            current_state = {
                "posterior": posterior,
                "drift_score": drift_score,
                "graph_stability": graph_stability,
            }
            intervention = self._optimizer.recommend(current_state)
            logger.info(
                "[Pipeline] Intervención sugerida: %s",
                intervention.get("message", "N/A"),
            )

        # ── CAPA 0: Construcción del ForensicBundle (datos puros) ──────
        # PURIFICADO: sin ollama_backend ni vars LLM en SystemState
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

        # ── Construir AbductionTrace — trazabilidad del razonamiento ───
        abduction = self._build_abduction_trace(signals, inference_result, decision_trace)

        bundle = ForensicBundle(
            evidence_graph=graph_for_bundle,
            decision_trace=decision_trace,
            policy_spec=self._policy_spec,
            actions=self._executor.get_action_history(),
            system_state=system_state,
            abduction_trace=abduction,
        )

        # ── CAPA 5: Sellado externo via BundleBuilder (no auto-sellado) ─
        sealed_dict = BundleBuilder.seal(
            bundle,
            engine_attestation_hash=self._engine_attestation_hash,
            ecl_hash=self._ecl_hash,
        )

        # Verificación interna rápida post-sellado
        verify_ok, verify_msg = BundleBuilder.quick_verify(sealed_dict)
        if not verify_ok:
            logger.error("[Pipeline] ALERTA: bundle invalido post-sellado: %s", verify_msg)

        # Guardar referencia al bundle (con integrity asignada por BundleBuilder)
        self._last_bundle = bundle
        self._last_sealed_dict = sealed_dict

        logger.info(
            "[Pipeline] Bundle sellado: %s | %s",
            bundle.bundle_id[:12], verify_msg,
        )

        return {
            "bundle": bundle,
            "sealed_dict": sealed_dict,
            "inference": inference_result,
            "decision": decision_trace,
            "graph_used": evidence_graph,
            "intervention": intervention,
            "verify_quick": (verify_ok, verify_msg),
        }


    # ------------------------------------------------------------------
    # Construccion de AbductionTrace
    # ------------------------------------------------------------------

    def _build_abduction_trace(
        self,
        signals: list,
        inference_result: dict,
        decision_trace,
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
            return self._call_ollama(b, backend)
        except Exception as e:
            logger.warning("[Pipeline] Error al llamar Ollama: %s", e)
            return None

    def _call_ollama(self, bundle: ForensicBundle, model: str) -> str:
        """
        Llama a Ollama (local) para generar narrativa ENFSI-style.

        El prompt incluye el bundle comprimido (no el JSON completo —
        demasiado largo para contexto de LLM).
        """
        dt = bundle.decision_trace
        graph = bundle.evidence_graph

        # Resumen comprimido para el LLM — no el bundle completo
        summary = {
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

        prompt = (
            "Sos un experto en análisis forense digital. "
            "Tu tarea es generar un reporte técnico conciso en español rioplatense "
            "basado en el siguiente resultado de análisis forense. "
            "El análisis fue realizado por VIGÍA, un sistema determinístico. "
            "NO modifiques los números. Usá el vocabulario de ENFSI. "
            "Formato: párrafos cortos, sin emojis, tono pericial.\n\n"
            f"RESULTADO:\n{json.dumps(summary, sort_keys=True, ensure_ascii=False, indent=2)}\n\n"
            "Generá el reporte:"
        )

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
        ollama_model    : nombre del modelo Ollama para narrativa
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
                metadata=d.get("metadata"),
            )
            signals.append(s)
        except Exception as e:
            logger.warning("[run_vigia] Señal inválida ignorada: %s — %s", d, e)

    # Inicializar pipeline — sin ollama_model en VigiaPipeline
    # (la narrativa es post-procesador externo, no contaminamos el bundle)
    pipeline = VigiaPipeline(
        calibration_path=calibration_path,
        covariance_path=covariance_path,
    )

    # Ejecutar — BundleBuilder.seal() es llamado internamente
    result = pipeline.run_full(signals, drift_score=drift_score)
    bundle = result["bundle"]
    sealed_dict = result["sealed_dict"]

    # Guardar bundle sellado si se pide
    if output_path:
        BundleBuilder.save(sealed_dict, output_path)

    # Generar narrativa DESPUÉS del sellado — post-procesador externo
    # El LLM recibe el bundle ya cerrado, no modifica nada
    narrative = None
    if ollama_model:
        try:
            narrative = pipeline.generate_narrative(bundle, model=ollama_model)
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
        help="Drift score [0.0, 1.0] (default: 0.0)",
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
        help="Modelo Ollama para narrativa (ej: llama3.2)",
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
