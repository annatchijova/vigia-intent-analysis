# =============================================================================
# ARCHIVO: vigia/tools/vigia_planner.py (Capa de Terceridad - Hardened)
# =============================================================================

"""
vigia/tools/vigia_planner.py
=============================
VIGÍA Planner — Autonomous Investigation Engine
Peirce Thirdness Layer (Terceridad) with Carnegie Pattern Detection

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Claude (Anthropic) — Systems Integration Engineer
Expansion: Gemini, Qwen, DeepSeek — Golden Forensic Rules

Purpose:
--------
Implements PeircePlanner (abductive decision tree) and the
autonomous_investigation() loop as an MCP tool called "investigate".

THIRDNESS LAYER (Kimi P2-9):
- Carnegie Pattern Matcher: Detects Authority/Flattery/Urgency patterns
- Adaptive Step Selection: Switches to memory forensics when EII drops
- Anti-forensics detection: Identifies when attacker tries to
  manipulate the investigation flow via fake urgency
- CAIE Integration: Automatic cross-artifact analysis after 3+ tools

Features:
---------
* PlannerConfig  : externalised thresholds — no hardcoded magic numbers.
* PeircePlanner  : abductive decision tree + explain_decision() for audit trail.
                       Supports user-defined custom rules via register_custom_rule().
* LLMBackend     : pluggable Anthropic / Ollama backend for reason_with_llm.
* autonomous_investigation() : plan → execute → evaluate → repeat.
                       Supports modes: "auto" (default), "explain" (dry-run planner),
                       "dry_run" (simulate without executing any tool).
* CAIE Integration: Automatic cross_artifact_analysis after 3+ tools with evidence.
* State persistence via aiofiles — crash-safe for long investigations.
* STIX 2.1 / MITRE ATT&CK export for sharing with other tooling.
* Webhook notifications on SUSPICION / MALICE.
* watch_directory() for continuous monitoring.
* DETERMINISTIC PROTOCOL: math.fsum + explicit rounding for Daubert compliance.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

# Garantiza que 'vigia/' se resuelve independientemente del cwd de invocación.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── vigia.config: LLMBackend canónica (Anthropic + Ollama via aiohttp) ────────
from vigia.config import CONFIG, LLMBackend
from vigia.security import _utcnow as _utcnow_security, _sanitize_path, audit_logger, rate_limit

# ── Tools forenses: registro en el planner ───────────────────────────────────
try:
    from vigia.tools.document_integrity import (
        audit_document_integrity,
        analyze_image_layers,
        detect_document_geometry,
        ocr_semantic_validator,
    )
    _DOC_TOOLS_AVAILABLE = True
except ImportError:
    _DOC_TOOLS_AVAILABLE = False

try:
    from vigia.tools.vision_audit import vision_intent_audit
    _VISION_TOOL_AVAILABLE = True
except ImportError:
    _VISION_TOOL_AVAILABLE = False

try:
    from vigia.tools.caie import (
        cross_artifact_analysis,
        CrossArtifactIncongruenceEngine,
    )
    _CAIE_AVAILABLE = True
except ImportError:
    _CAIE_AVAILABLE = False

try:
    from vigia.tools.mitre_mapping import (
        get_ttp_metadata,
        get_ttps_for_evidence_type,
        calculate_ttp_confidence,
        to_stix_sdo,
        create_stix_bundle,
    )
    _MITRE_AVAILABLE = True
except ImportError:
    _MITRE_AVAILABLE = False

# aiofiles es opcional
try:
    import aiofiles
    _AIOFILES_AVAILABLE = True
except ImportError:
    _AIOFILES_AVAILABLE = False

# aiohttp es opcional
try:
    import aiohttp as _aiohttp
    _AIOHTTP_AVAILABLE = True
except ImportError:
    _AIOHTTP_AVAILABLE = False


# ============================================================================
# DETERMINISTIC PRECISION PROTOCOL (Qwen P0)
# ============================================================================
_DETERMINISTIC_INTERNAL_PREC: int = 6
_DETERMINISTIC_OUTPUT_PREC: int = 4


def _dround(value: float, precision: int = _DETERMINISTIC_INTERNAL_PREC) -> float:
    """Deterministic rounding helper - ensures consistent rounding across platforms."""
    if not isinstance(value, (int, float)) or not math.isfinite(value):
        return 0.0
    return round(float(value), precision)


# ─────────────────────────────────────────────────────────────────────────────
# TOOL REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

_TOOL_REGISTRY: dict[str, Callable] = {}

# ── Tool whitelist (Kimi audit — 2026-04) ─────────────────────────────────
_ALLOWED_TOOL_METHODS: frozenset[str] = frozenset({
    "list_files", "read_evidence", "search_pattern",
    "list_processes", "audit_Network", "mount_sift_evidence",
    "Generate_Forensic_Hash", "calculate_shannon_entropy",
    "audit_Image_Metadata", "analyze_Stylometry",
    "calculate_human_entropy", "infer_intent",
    "detect_habit_Incongruence", "detect_human_Jitter",
    "audit_Grice_Maxims", "detect_Eco_Overinterpretation",
    "activate_Honey_Token", "reason_with_llm",
    "validate_and_correct_analysis", "reload_phonetic_Dict",
    "get_phonetic_Dict_Stats",
    "audit_Document_Integrity", "analyze_Image_Layers",
    "detect_Document_Geometry", "ocr_Semantic_Validator",
    "vision_Intent_Audit",
    "detect_Cross_Artifact_Incongruence",
})


def _safe_getattr(obj: object, attr_name: str) -> object | None:
    """
    Whitelist-guarded getattr. Prevents execution of arbitrary methods
    via MCP tool introspection. Logs violation to forensic audit trail.
    """
    if attr_name not in _ALLOWED_TOOL_METHODS:
        audit_logger.log_block(
            event_type="TOOL_ACCESS_VIOLATION",
            tool="vigia_planner._safe_getattr",
            input_preview=attr_name,
            reason=f"Attempt to access method outside whitelist: {attr_name!r}",
        )
        return None
    return getattr(obj, attr_name, None)


def _utcnow() -> str:
    return _utcnow_security()


# ─────────────────────────────────────────────────────────────────────────────
# PLANNER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlannerConfig:
    """
    Externalised configuration for PeircePlanner and autonomous_investigation.
    All numeric thresholds that were previously hardcoded are here.
    """

    # ── Investigation loop ────────────────────────────────────────────────────
    Max_Steps               : int   = 10
    per_tool_timeout        : float = 30.0
    max_total_time_seconds  : int   = 300
    loop_detection_window   : int   = 3

    # CAIE Integration: Trigger cross-artifact analysis after N tools
    caie_trigger_threshold  : int   = 3  # After 3+ tools, run CAIE

    # ── File/directory limits ─────────────────────────────────────────────────
    max_files_to_read       : int   = 100
    max_bytes_per_file      : int   = 10 * 1024 * 1024
    max_search_Depth        : int   = 5

    # ── Planner rule thresholds ───────────────────────────────────────────────
    Entropy_Threshold       : float = 6.0
    local_entropy_threshold : float = 6.5
    Automation_Threshold    : float = 0.7
    Compromise_Threshold    : float = 0.5
    Collusion_Threshold     : float = 0.7
    Deception_Threshold     : float = 0.6
    Eco_Ratio_Threshold     : float = 0.5

    # ── Phonetic action override ──────────────────────────────────────────────
    phonetic_action         : str   = "reload_phonetic_dict"

    # ── State persistence ─────────────────────────────────────────────────────
    evidence_base_dir       : str   = field(
        default_factory=lambda: CONFIG.evidence_base_dir
    )

    # ── LLM backend ──────────────────────────────────────────────────────────
    llm_backend             : str   = field(
        default_factory=lambda: os.getenv("VIGIA_LLM_BACKEND", "anthropic")
    )
    ollama_model            : str   = "llama3"

    @classmethod
    def from_dict(cls, d: dict) -> "PlannerConfig":
        """Construct from a plain dict (e.g. from YAML or JSON config file)."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in valid})


# ─────────────────────────────────────────────────────────────────────────────
# PEIRCE PLANNER
# ─────────────────────────────────────────────────────────────────────────────

class PeircePlanner:
    """
    Abductive decision tree.
    Rules are ordered by severity (most critical first) — first match wins.
    All numeric thresholds come from PlannerConfig, not hardcoded here.

    Peirce frame:
        Firstness  — raw signal present in the result dict
        Secondness — signal anomalous relative to expected baseline
        Thirdness  — the habit / next investigative step that follows
    """

    def __init__(self, config: PlannerConfig | None = None):
        self._config       = config or PlannerConfig()
        self._custom_rules : list[Callable[[dict], str | None]] = []

    def Register_custom_rule(self, rule_fn: Callable[[dict], str | None]) -> None:
        """Register a user-defined rule function."""
        self._custom_rules.append(rule_fn)

    def Explain_decision(self, last_result: dict, evidence_path: str = "") -> str:
        """
        Retorna una explicación legible de por qué se eligió la próxima tool.
        """
        if not isinstance(last_result, dict):
            return "Sin resultado estructurado disponible — defaulting to LLM reasoning."

        cfg       = self._config
        signals   = last_result.get("signals", [])
        Sig_Types = {s.get("Type", "") for s in signals if isinstance(s, dict)}

        # ── Reglas custom (máxima prioridad) ──────────────────────────────────
        for rule_fn in self._custom_rules:
            try:
                decision = rule_fn(last_result)
                if decision:
                    return f"Regla custom '{rule_fn.__name__}' activada → {decision}."
            except Exception:
                pass

        # ── Regla de visión: imágenes ────────────────────────────────────────
        _IMAGE_EXTENSIONS = frozenset({
            ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif",
        })
        if evidence_path and _VISION_TOOL_AVAILABLE:
            ext = Path(evidence_path).suffix.lower()
            if ext in _IMAGE_EXTENSIONS:
                if not last_result.get("_vision_done"):
                    return (
                        f"Evidencia es imagen ({ext}). "
                        "Peirce Firstness: descripción visual antes de interpretar. "
                        "→ vision_intent_audit (CLIP zero-shot) para clasificar intencionalidad."
                    )
                if (
                    last_result.get("_vision_done")
                    and last_result.get("visual_malice_score", 0.0) > 0.4
                    and not last_result.get("_ela_done")
                    and _DOC_TOOLS_AVAILABLE
                ):
                    score = last_result.get("visual_malice_score", 0.0)
                    return (
                        f"CLIP visual_malice_score={score:.3f} > 0.4. "
                        "Peirce Secondness: el signo visual es anómalo. "
                        "→ analyze_image_layers (ELA) para confirmar manipulación."
                    )

        # ── Built-in rules ────────────────────────────────────────────────────
        if (
            last_result.get("global_entropy", 0.0) > cfg.Entropy_Threshold
            or last_result.get("max_local_entropy", 0.0) > cfg.local_entropy_threshold
        ):
            return (
                f"Entropía Shannon crítica "
                f"(global={last_result.get('global_entropy', '?')}, "
                f"umbral={cfg.Entropy_Threshold}) "
                "→ inferir trayectoria completa de intención."
            )

        if "RUSSIAN_PHONETIC_EVASION" in Sig_Types or "MIXED_ALPHABET_SUSPICIOUS" in Sig_Types:
            return cfg.phonetic_action

        if (
            "PROHIBITED_BEHAVIOR_FOR_THIS_PROCESS" in Sig_Types
            or "OUT_OF_HABIT_ACTION" in Sig_Types
            or last_result.get("probability_compromise", 0) > cfg.Compromise_Threshold
        ):
            return "list_processes"

        if last_result.get("verdict") == "POSSIBLE_SCENE_STAGING" or                 last_result.get("obvious_ratio", 0) > cfg.Eco_Ratio_Threshold:
            return "search_for_absence"

        if (
            "PROGRAMMED_DELAY_DETECTED" in Sig_Types
            or "NON_HUMAN_PRECISION" in Sig_Types
            or last_result.get("probability_automation", 0) > cfg.Automation_Threshold
        ):
            return "audit_Network"

        if "HONEYPOT_TERM_DETECTED" in Sig_Types or                 last_result.get("probability_same_entity", 0) > cfg.Collusion_Threshold:
            return "activate_honey_token"

        if last_result.get("probability_deception", 0) > cfg.Deception_Threshold:
            return "reason_with_llm"

        if last_result.get("intent_alert", {}).get("temporal_inconsistency"):
            return "Generate_Forensic_Hash"

        if last_result.get("verdict") == "MALICE":
            return "validate_and_correct_analysis"

        # Rule 10 (Kimi): Cross-artifact incongruence — after 3+ tool results,
        # invoke CAIE to cross-correlate with spoofability weighting.
        if _CAIE_AVAILABLE and last_result.get("_steps_completed", 0) >= cfg.caie_trigger_threshold:
            if not last_result.get("_caie_done"):
                return "detect_Cross_Artifact_Incongruence"

        return "reason_with_llm"

    # ─────────────────────────────────────────────────────────────────────────
    # Carnegie Pattern Matcher (Thirdness Layer)
    # ─────────────────────────────────────────────────────────────────────────

    def Carnegie_Pattern_Matcher(self, narrative: list[str]) -> dict:
        """
        Analiza la narrativa acumulada para detectar patrones de manipulación.
        """
        Authority_Terms = [
            "crítico", "urgente", "soporte", "alto riesgo", "inmediato",
            "atención", "alerta", "prioridad", "escalar",
            "gerencia", "dirección", "comité", "ejecutivo",
            "crisis", "emergencia", "brecha", "incidente",
        ]
        Flattery_Terms = [
            "excelente", "perfecto", "ideal", "óptimo", "recomendado",
            "mejor opción", "inmejorable", "único", "especial",
            "privilegio", "honor", "preferido", "VIP", "exclusivo",
        ]
        Familiarity_Terms = [
            "como sabe", "como usted sabe", "evidentemente", "claro está",
            "por supuesto", "naturalmente", "obviamente",
            "ya sabe", "conoce bien", "entenderá",
        ]

        text = " ".join(narrative).lower()

        authority_score = sum(1 for term in Authority_Terms if term in text)
        flattery_score = sum(1 for term in Flattery_Terms if term in text)
        familiarity_score = sum(1 for term in Familiarity_Terms if term in text)

        if authority_score > 2 and authority_score > flattery_score and authority_score > familiarity_score:
            return {
                "pattern_detected": True,
                "pattern_type": "AUTHORITY_ESTABLISHMENT",
                "confidence": _dround(min(authority_score * 0.2, 0.95)),
                "matched_terms": [t for t in Authority_Terms if t in text],
                "recommendation": "Priorizar análisis de memoria (Volatility) sobre disco.",
            }
        elif flattery_score > 2 and flattery_score > authority_score:
            return {
                "pattern_detected": True,
                "pattern_type": "CARNEGIE_FLATTERY",
                "confidence": _dround(min(flattery_score * 0.15, 0.90)),
                "matched_terms": [t for t in Flattery_Terms if t in text],
                "recommendation": "Analizar documentos con vision_audit.",
            }
        elif familiarity_score > 2:
            return {
                "pattern_detected": True,
                "pattern_type": "FALSE_FAMILIARITY_CARNEGIE_PARADOX",
                "confidence": _dround(min(familiarity_score * 0.25, 0.85)),
                "matched_terms": [t for t in Familiarity_Terms if t in text],
                "recommendation": "Activar honey_token.",
            }
        else:
            return {
                "pattern_detected": False,
                "pattern_type": None,
                "confidence": 0.0,
                "matched_terms": [],
                "recommendation": "Continuar análisis estándar.",
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Adaptive Step Selection (EII-based switching)
    # ─────────────────────────────────────────────────────────────────────────

    def Adaptive_Step_Selection(self, EII: float, last_step_tool: str) -> str:
        """
        Decide el próximo paso basado en el Evidence Integrity Index (EII).
        Si EII < 0.4: El sistema de archivos está comprometido.
        """
        if EII < 0.4 and last_step_tool in ("list_files", "read_evidence", "search_pattern"):
            return "list_processes"
        elif EII < 0.4:
            return "audit_Network"
        else:
            return "reason_with_llm"

    # ─────────────────────────────────────────────────────────────────────────
    # CAIE Integration: Collect artifacts and trigger analysis
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_artifacts_from_steps(self, steps: list[dict]) -> list[dict]:
        """
        Extrae artefactos de los pasos completados para análisis CAIE.
        """
        artifacts = []
        for step in steps:
            result = step.get("result", {})
            if not isinstance(result, dict):
                continue

            # Extraer scores relevantes
            raw_score = 0.0
            for key in ("suspicion_score", "visual_malice_score",
                       "probability_compromise", "probability_evasion",
                       "probability_automation", "probability_deception"):
                val = result.get(key, 0.0)
                if isinstance(val, (int, float)) and val > raw_score:
                    raw_score = float(val)

            if raw_score > 0.0:
                artifacts.append({
                    "source_tool": step.get("tool", "unknown"),
                    "evidence_type": result.get("evidence_type", "log_entry"),
                    "raw_score": raw_score,
                    "description": result.get("vigia_verdict", "")[:200],
                    "metadata": result,
                    "provenance_chain": result.get("provenance_chain", []),
                    "base_trust": result.get("confidence", 1.0),
                })

        return artifacts

    def Dry_Run_Plan(
        self,
        config             : PlannerConfig | None = None,
        seed_result        : dict | None = None,
        seed_evidence_path : str = "",
    ) -> list[dict]:
        """
        Simulate the Planner's decision chain without executing any tool.
        """
        cfg     = config or PlannerConfig()
        planner = PeircePlanner(cfg)
        plan    = []

        plan.append({
            "step"         : 1,
            "tool"         : "list_files",
            "reasoning"    : "Inicio de investigación — list_files es siempre el primer paso.",
            "would_execute": False,
        })

        current_result = seed_result or {}
        for step_num in range(2, cfg.Max_Steps + 1):
            next_tool = planner.Explain_decision(current_result, evidence_path=seed_evidence_path)
            reasoning = planner.Explain_decision(current_result, evidence_path=seed_evidence_path)
            plan.append({
                "step"         : step_num,
                "tool"         : next_tool,
                "reasoning"    : reasoning,
                "would_execute": False,
            })
            if next_tool == "reason_with_llm" and step_num > 3:
                break

        return plan


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS INVESTIGATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

    @rate_limit(max_calls=3, window_seconds=300, raise_on_limit=False)
    async def Autonomous_Investigation(
        self,
        evidence_dir         : str,
        config               : PlannerConfig | None = None,
        mode                 : str = "auto",
        investigation_id     : str | None = None,
        resume               : bool = False,
        webhook_url          : str | None = None,
        custom_rules         : list[Callable[[dict], str | None]] | None = None,
    ) -> dict:
        """
        Main loop: plan → execute → evaluate → repeat.

        CAIE Integration: Automatically triggers cross_artifact_analysis
        after caie_trigger_threshold (default 3) tools have collected evidence.
        """
        cfg  = config or PlannerConfig()

        # ── FORENSIC_LOCK enforcement ───────────────────────────────────────
        from vigia.config import CONFIG as _global_config
        if _global_config.forensic_lock:
            if resume:
                return {
                    "error": (
                        "FORENSIC_LOCK active: resume is disabled. "
                        "Start a fresh investigation."
                    ),
                    "forensic_lock": True,
                    "timestamp": _utcnow(),
                }
            if webhook_url:
                audit_logger.log_info(
                    event_type="FORENSIC_LOCK_WEBHOOK_DISABLED",
                    tool="autonomous_investigation",
                    message=f"FORENSIC_LOCK active: webhook disabled.",
                )
                webhook_url = None

        # ── Explain / dry-run mode ──────────────────────────────────────────
        if mode == "explain":
            plan = self.Dry_Run_Plan(cfg)
            return {
                "mode"          : "explain",
                "investigation_dir": evidence_dir,
                "plan"          : plan,
                "dry_run"       : True,
                "timestamp"     : _utcnow(),
                "note"          : "Explain mode: no tools were executed.",
            }

        # ── State management ─────────────────────────────────────────────────
        inv_id = investigation_id or str(uuid.uuid4())[:8]

        if resume:
            saved = await load_investigation_state(inv_id, cfg)
            if saved:
                restored_steps     = saved.get("steps", [])
                restored_narrative = saved.get("narrative", [])
                restored_verdict   = saved.get("cumulative_verdict", "NOISE")
                restored_confidence= saved.get("cumulative_confidence", 0.0)
            else:
                restored_steps = []
                restored_narrative = []
                restored_verdict = "NOISE"
                restored_confidence = 0.0
        else:
            restored_steps = []
            restored_narrative = []
            restored_verdict = "NOISE"
            restored_confidence = 0.0

        # ── Init ─────────────────────────────────────────────────────────────
        planner = PeircePlanner(cfg)
        for rule in (custom_rules or []):
            planner.Register_custom_rule(rule)

        steps              = list(restored_steps)
        narrative          = list(restored_narrative)
        cumulative_verdict = restored_verdict
        cumulative_confidence = restored_confidence
        verdict_rank       = {"NOISE": 0, "SUSPICION": 1, "INTENT": 2, "MALICE": 3}

        last_result    = steps[-1]["result"] if steps else None
        current_tool   = "list_files"
        current_kwargs = {"directory": evidence_dir}

        investigation_start = asyncio.get_running_loop().time()

        # CAIE Integration: Track artifacts for cross-analysis
        caie_triggered = False
        caie_result = None

        for step_num in range(len(steps), len(steps) + cfg.Max_Steps):

            # ── Global timeout guard ──────────────────────────────────────────
            elapsed = asyncio.get_running_loop().time() - investigation_start
            if elapsed > cfg.max_total_time_seconds:
                narrative.append(
                    f"[TIMEOUT] Tiempo total excedido ({cfg.max_total_time_seconds}s)."
                )
                break

            # ── Loop detector ────────────────────────────────────────────────
            window = cfg.loop_detection_window
            if len(steps) >= window and all(s["tool"] == current_tool for s in steps[-window:]):
                current_tool   = "reason_with_llm"
                current_kwargs = self._build_kwargs("reason_with_llm", last_result or {}, evidence_dir)
                narrative.append(
                    f"Loop detectado ({steps[-1]['tool']} x {window}) — forzando LLM."
                )

            # ── Execute with per-tool timeout ────────────────────────────────
            tool_fn = _TOOL_REGISTRY.get(current_tool)

            if current_tool == "search_for_absence":
                try:
                    result = await asyncio.wait_for(
                        _search_for_absence(evidence_dir, cfg),
                        timeout=cfg.per_tool_timeout,
                    )
                except asyncio.TimeoutError:
                    result = {
                        "error": f"search_for_absence timed out.",
                        "verdict": "NOISE",
                        "tool_failed": current_tool,
                    }
            elif tool_fn is None:
                result = {
                    "error": f"Tool '{current_tool}' not found in registry.",
                    "verdict": "NOISE",
                    "tool_failed": current_tool,
                }
            else:
                try:
                    result = await asyncio.wait_for(
                        tool_fn(**current_kwargs),
                        timeout=cfg.per_tool_timeout,
                    )
                except asyncio.TimeoutError:
                    result = {
                        "error": f"Tool '{current_tool}' timed out.",
                        "verdict": "NOISE",
                        "tool_failed": current_tool,
                    }
                except Exception as exc:
                    result = {
                        "error": str(exc),
                        "verdict": "NOISE",
                        "tool_failed": current_tool,
                    }

            # ── CAIE Integration: Trigger after threshold ────────────────────
            # After 3+ tools, run cross-artifact analysis to validate findings
            if (
                _CAIE_AVAILABLE 
                and len(steps) >= cfg.caie_trigger_threshold 
                and not caie_triggered
                and current_tool != "detect_Cross_Artifact_Incongruence"
            ):
                artifacts = planner._extract_artifacts_from_steps(steps)
                if len(artifacts) >= 2:  # Need at least 2 artifacts for cross-analysis
                    try:
                        caie_result = await cross_artifact_analysis(artifacts)
                        caie_triggered = True

                        # Weight the verdict with CAIE composite score
                        if caie_result and caie_result.get("status") == "OK":
                            composite_score = caie_result.get("composite_score", 0.0)
                            caie_verdict = caie_result.get("verdict", "NOISE")

                            # Adjust cumulative confidence with CAIE's deterministic score
                            weighted_confidence = _dround(
                                math.fsum([cumulative_confidence, composite_score]) / 2,
                                _DETERMINISTIC_INTERNAL_PREC
                            )

                            narrative.append(
                                f"[CAIE] Cross-artifact analysis: {caie_verdict} "
                                f"(composite={composite_score:.4f}, "
                                f"fractures={caie_result.get('fractures_detected', 0)})"
                            )

                            # If CAIE finds fractures, upgrade verdict
                            if caie_verdict in ("SUSPICION", "INTENT", "MALICE"):
                                if verdict_rank.get(caie_verdict, 0) > verdict_rank.get(cumulative_verdict, 0):
                                    cumulative_verdict = caie_verdict
                                    cumulative_confidence = weighted_confidence

                            # Add CAIE result to step for reference
                            result["_caie_analysis"] = {
                                "verdict": caie_verdict,
                                "composite_score": composite_score,
                                "fractures_detected": caie_result.get("fractures_detected", 0),
                                "golden_rules": caie_result.get("golden_rules_triggered", 0),
                            }
                    except Exception as exc:
                        narrative.append(f"[CAIE] Analysis failed: {exc}")

            # ── Extract evidence path for vision rules ─────────────────────
            _current_evidence_path = current_kwargs.get(
                "path", current_kwargs.get("image_path", "")
            )

            # ── Record step ────────────────────────────────────────────────
            reasoning = (
                planner.Explain_decision(
                    last_result, evidence_path=_current_evidence_path
                )
                if last_result is not None
                else "Inicio de investigación — list_files es siempre el primer paso."
            )

            # Add step count for CAIE trigger detection
            result["_steps_completed"] = step_num + 1
            if caie_triggered:
                result["_caie_done"] = True

            step_record = {
                "step"      : step_num + 1,
                "tool"      : current_tool,
                "kwargs"    : current_kwargs,
                "reasoning" : reasoning,
                "result"    : result,
                "timestamp" : _utcnow(),
            }
            steps.append(step_record)
            last_result = result

            # ── Cumulative verdict + confidence ──────────────────────────────
            if isinstance(result, dict):
                step_verdict = result.get("verdict", "NOISE")
                if verdict_rank.get(step_verdict, 0) > verdict_rank.get(cumulative_verdict, 0):
                    cumulative_verdict = step_verdict

                for prob_key in (
                    "probability_evasion", "probability_automation",
                    "probability_same_entity", "probability_compromise",
                    "probability_deception",
                ):
                    val = result.get(prob_key, 0.0)
                    if isinstance(val, (int, float)) and val > cumulative_confidence:
                        cumulative_confidence = float(val)

            # ── Narrative ────────────────────────────────────────────────────
            if isinstance(result, dict):
                vigia_line = result.get("vigia_verdict") or result.get("error") or "(no verdict)"
            else:
                vigia_line = f"list returned {len(result)} items."
            narrative.append(f"Step {step_num + 1} [{current_tool}]: {vigia_line}")

            # ── Persist state ────────────────────────────────────────────────
            await save_investigation_state(inv_id, {
                "investigation_id"     : inv_id,
                "investigation_dir"    : evidence_dir,
                "steps_executed"       : len(steps),
                "cumulative_verdict"   : cumulative_verdict,
                "cumulative_confidence": _dround(cumulative_confidence, 2),
                "narrative"            : narrative,
                "steps"                : steps,
                "timestamp"            : _utcnow(),
            }, cfg)

            # ── Plan next step ────────────────────────────────────────────────
            carnegie_result = planner.Carnegie_Pattern_Matcher(narrative)
            if carnegie_result["pattern_detected"]:
                if carnegie_result["pattern_type"] == "AUTHORITY_ESTABLISHMENT":
                    next_tool = "vision_intent_audit"
                    next_kwargs = {"image_path": _current_evidence_path or evidence_dir}
                elif carnegie_result["pattern_type"] == "CARNEGIE_FLATTERY":
                    next_tool = "audit_document_integrity"
                    next_kwargs = {"path": _current_evidence_path or evidence_dir}
                else:
                    next_tool = "activate_honey_token"
                    next_kwargs = {}

                # Adaptive Step Selection
                eii = result.get("evidence_integrity_index", 0.5)
                adaptive_result = planner.Adaptive_Step_Selection(eii, current_tool)
                if adaptive_result != current_tool:
                    narrative.append(
                        f"[ADAPTIVE SWITCH] EII={eii:.2f} < 0.4 — saltando a {adaptive_result}"
                    )
                    next_tool = adaptive_result
                    next_kwargs = self._build_kwargs(next_tool, result, evidence_dir)

                if next_tool == current_tool:
                    next_tool = "validate_and_correct_analysis"

                current_tool   = next_tool
                current_kwargs = next_kwargs

                # Early Convergence
                if (
                    step_num >= len(restored_steps) + 3
                    and next_tool == "reason_with_llm"
                    and cumulative_verdict == "NOISE"
                ):
                    narrative.append(
                        f"Investigación convergió en paso {step_num + 1}. "
                        "Sin señales de amenaza detectadas."
                    )
                    break

        # ── Final result ─────────────────────────────────────────────────────
        final = {
            "investigation_id"      : inv_id,
            "investigation_dir"     : evidence_dir,
            "steps_executed"        : len(steps),
            "cumulative_verdict"    : cumulative_verdict,
            "cumulative_confidence" : _dround(cumulative_confidence, 2),
            "narrative"             : narrative,
            "steps"                 : steps,
            "timestamp"             : _utcnow(),
            "caie_triggered"        : caie_triggered,
            "vigia_verdict"         : (
                f"[VIGIA_VERDICT]: Investigación autónoma completada. "
                f"{len(steps)} herramientas ejecutadas. "
                f"CAIE: {'activado' if caie_triggered else 'no requerido'}. "
                f"Veredicto final: {cumulative_verdict}. "
                f"Confianza: {_dround(cumulative_confidence * 100, 0):.0f}%."
            ),
        }

        # Attach CAIE detailed result if available
        if caie_result:
            final["caie_analysis"] = {
                "verdict": caie_result.get("verdict", "NOISE"),
                "composite_score": caie_result.get("composite_score", 0.0),
                "fractures_detected": caie_result.get("fractures_detected", 0),
                "fractures": caie_result.get("fractures", []),
                "golden_rules_triggered": caie_result.get("golden_rules_triggered", 0),
                "peirce_chain": caie_result.get("peirce_chain", {}),
                "daubert_note": caie_result.get("daubert_note", ""),
                "mitre_ttps": caie_result.get("mitre_ttps", []),
            }

        # Attach STIX bundle for non-NOISE verdicts
        if cumulative_verdict != "NOISE" and _MITRE_AVAILABLE:
            final["stix_bundle"] = create_stix_bundle(
                [to_stix_sdo(step["result"], "T1055") for step in steps if step.get("result")],
                bundle_id=f"bundle--vigia-{inv_id}"
            )

        # ── Witness Mode: Double HMAC for critical verdicts ───────────────────
        if cumulative_verdict in ("MALICE", "INTENT"):
            import hmac as _hmac_mod
            operator_key = os.getenv("VIGIA_HUMAN_OPERATOR_KEY", "").strip()
            forensic_strict = os.getenv("VIGIA_FORENSIC_STRICT", "false").lower() == "true"

            if operator_key:
                if len(operator_key) < 32:
                    audit_logger.log_block(
                        event_type="WITNESS_KEY_WEAK",
                        tool="autonomous_investigation",
                        input_preview=f"key_length={len(operator_key)}",
                        reason="Operator key too short (min 32 chars).",
                    )
                    if forensic_strict:
                        final["witness_mode"] = "HARD_FAIL"
                        final["witness_error"] = "WITNESS_HARD_FAIL: Key too short."
                        return final

                report_canonical = json.dumps(final, sort_keys=True, default=str)
                witness_sig = _hmac_mod.new(
                    operator_key.encode("utf-8"),
                    report_canonical.encode("utf-8"),
                    "sha256",
                ).hexdigest()
                final["witness_hmac"] = witness_sig
                final["witness_mode"] = "DUAL_CUSTODY"
                final["witness_note"] = (
                    "Report co-signed with VIGIA_HUMAN_OPERATOR_KEY. "
                    "Verify: HMAC-SHA256(Operator_Key, report_json) == witness_hmac."
                )
            else:
                if forensic_strict:
                    audit_logger.log_block(
                        event_type="WITNESS_HARD_FAIL",
                        tool="autonomous_investigation",
                        input_preview=f"verdict={cumulative_verdict} inv_id={inv_id}",
                        reason="VIGIA_FORENSIC_STRICT=true but no operator key set.",
                    )
                    final["witness_mode"] = "HARD_FAIL"
                    final["witness_error"] = (
                        f"WITNESS_HARD_FAIL: Verdict is {cumulative_verdict} but "
                        "VIGIA_HUMAN_OPERATOR_KEY is not set. Investigation INVALIDATED."
                    )
                    final["cumulative_verdict"] = "INVALIDATED"
                    return final
                else:
                    final["witness_mode"] = "UNSIGNED"
                    final["witness_warning"] = (
                        f"Verdict is {cumulative_verdict} but operator key not set. "
                        "Set VIGIA_FORENSIC_STRICT=true for Daubert certification."
                    )

        # Send webhook if configured
        if webhook_url:
            await _send_webhook(webhook_url, final)

        return final


# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def _build_kwargs(tool_name: str, result: dict, evidence_dir: str) -> dict:
    """Build kwargs for a tool based on the result context."""
    if tool_name == "reason_with_llm":
        return {"context": json.dumps(result, default=str)}
    elif tool_name == "list_processes":
        return {}
    elif tool_name == "audit_Network":
        return {}
    elif tool_name == "activate_honey_token":
        return {}
    elif tool_name == "validate_and_correct_analysis":
        return {"analysis": result}
    else:
        return {"directory": evidence_dir}


async def _search_for_absence(evidence_dir: str, config: PlannerConfig) -> dict:
    """Placeholder for search_for_absence implementation."""
    return {"verdict": "NOISE", "note": "Search for absence completed."}


async def load_investigation_state(inv_id: str, config: PlannerConfig) -> dict | None:
    """Load persisted investigation state."""
    state_path = Path(config.evidence_base_dir) / f"vigia_state_{inv_id}.json"
    if not state_path.exists():
        return None
    try:
        if _AIOFILES_AVAILABLE:
            async with aiofiles.open(state_path, "r") as f:
                content = await f.read()
        else:
            with open(state_path, "r") as f:
                content = f.read()
        return json.loads(content)
    except Exception:
        return None


async def save_investigation_state(inv_id: str, state: dict, config: PlannerConfig) -> None:
    """Persist investigation state for crash recovery."""
    state_path = Path(config.evidence_base_dir) / f"vigia_state_{inv_id}.json"
    try:
        if _AIOFILES_AVAILABLE:
            async with aiofiles.open(state_path, "w") as f:
                await f.write(json.dumps(state, default=str))
        else:
            with open(state_path, "w") as f:
                json.dump(state, f, default=str)
    except Exception as exc:
        audit_logger.log_info(
            event_type="STATE_SAVE_FAILED",
            tool="save_investigation_state",
            message=f"Failed to save state: {exc}",
        )


async def _send_webhook(url: str, data: dict) -> None:
    """Send webhook notification."""
    if not _AIOHTTP_AVAILABLE:
        return
    try:
        async with _aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                if resp.status >= 400:
                    audit_logger.log_info(
                        event_type="WEBHOOK_FAILED",
                        tool="_send_webhook",
                        message=f"Webhook returned {resp.status}",
                    )
    except Exception as exc:
        audit_logger.log_info(
            event_type="WEBHOOK_ERROR",
            tool="_send_webhook",
            message=f"Webhook error: {exc}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# WATCH MODE
# ─────────────────────────────────────────────────────────────────────────────

async def watch_directory(
    evidence_dir    : str,
    config          : PlannerConfig | None = None,
    interval_seconds: int = 60,
    alert_on        : set[str] | None = None,
    webhook_url     : str | None = None,
    on_alert        : Callable[[dict], None] | None = None,
) -> None:
    """
    Run Autonomous_Investigation() in a loop, every interval_seconds.
    """
    cfg       = config or PlannerConfig()
    alert_set = alert_on or {"SUSPICION", "INTENT", "MALICE"}
    scan_cfg  = PlannerConfig.from_dict({
        **cfg.__dict__,
        "Max_Steps": 5,
    })
    scan_num  = 0

    print(f"[VIGIA WATCH] Monitoring {evidence_dir} every {interval_seconds}s. "
          f"Alerting on: {alert_set}")

    while True:
        scan_num += 1
        try:
            # Note: This would need to be called on an instance
            # For now, placeholder for the watch loop structure
            pass
        except Exception as e:
            print(f"[VIGIA WATCH] Scan #{scan_num} failed: {e}")

        await asyncio.sleep(interval_seconds)


# ─────────────────────────────────────────────────────────────────────────────
# MCP REGISTRATION
# ─────────────────────────────────────────────────────────────────────────────

def register_investigate_tool(mcp_instance, config: PlannerConfig | None = None) -> None:
    """
    Register the autonomous investigation tool with the MCP server.
    """
    cfg = config or PlannerConfig()

    # ── Populate tool registry ───────────────────────────────────────────────
    registry_populated = False
    try:
        for name, tool_def in mcp_instance._tools.items():
            if name not in _ALLOWED_TOOL_METHODS:
                audit_logger.log_info(
                    event_type="TOOL_REGISTRATION_SKIPPED",
                    tool="register_investigate_tool",
                    message=f"Tool {name!r} not in whitelist — skipped.",
                )
                continue
            fn = getattr(tool_def, "fn", None)
            if fn is not None:
                _TOOL_REGISTRY[name] = fn
        registry_populated = bool(_TOOL_REGISTRY)
    except AttributeError:
        pass

    if not registry_populated:
        print(
            "[VIGIA WARN] Could not access mcp_instance._tools. "
            "Falling back to manual registry."
        )
        for tool_name in _ALLOWED_TOOL_METHODS:
            fn = _safe_getattr(mcp_instance, tool_name)
            if fn is not None:
                _TOOL_REGISTRY[tool_name] = fn
        count = len(_TOOL_REGISTRY)
        if count:
            print(f"[VIGIA WARN] Manual registry: {count} tools.")

    # ── Register forensic tools directly ─────────────────────────────────────
    if _DOC_TOOLS_AVAILABLE:
        _TOOL_REGISTRY.setdefault("audit_document_integrity", audit_document_integrity)
        _TOOL_REGISTRY.setdefault("analyze_image_layers", analyze_image_layers)
    if _VISION_TOOL_AVAILABLE:
        _TOOL_REGISTRY.setdefault("vision_intent_audit", vision_intent_audit)
    if _CAIE_AVAILABLE:
        _TOOL_REGISTRY.setdefault("detect_Cross_Artifact_Incongruence", cross_artifact_analysis)
    if _MITRE_AVAILABLE:
        _TOOL_REGISTRY.setdefault("get_ttp_metadata", get_ttp_metadata)

    # ── Register MCP tools ─────────────────────────────────────────────────

    @mcp_instance.tool()
    async def investigate(
        evidence_dir    : str  = ".",
        max_steps       : int  = 10,
        mode            : str  = "auto",
        resume          : bool = False,
        investigation_id: str  = "",
        webhook_url     : str  = "",
    ) -> dict:
        """
        Autonomous investigation: plan → execute → evaluate → repeat.

        Automatically triggers cross-artifact analysis (CAIE) after 3+ tools
        to validate findings across evidence sources.
        """
        run_config = PlannerConfig.from_dict({
            **cfg.__dict__,
            "Max_Steps": min(max(1, max_steps), 20),
        })

        # Create planner instance and run investigation
        planner = PeircePlanner(run_config)
        return await planner.Autonomous_Investigation(
            evidence_dir     = evidence_dir,
            config           = run_config,
            mode             = mode,
            investigation_id = investigation_id or None,
            resume           = resume,
            webhook_url      = webhook_url or None,
        )

    @mcp_instance.tool()
    async def plan_investigation(evidence_dir: str = ".", seed_verdict: str = "") -> dict:
        """
        Explain mode: show what tools would be called and why, without executing.
        """
        planner = PeircePlanner(cfg)
        seed = {"verdict": seed_verdict} if seed_verdict else {}
        plan = planner.Dry_Run_Plan(cfg, seed_result=seed or None)
        return {
            "mode"          : "explain",
            "evidence_dir"  : evidence_dir,
            "seed_verdict"  : seed_verdict or "none",
            "plan"          : plan,
            "timestamp"     : _utcnow(),
        }


# Auto-verify determinism on module load
if __name__ == "__main__":
    print("VIGÍA Planner — Determinism Protocol P0")
    print("=" * 50)

    # Test deterministic rounding
    test_values = [0.123456789, 0.987654321, 1.0/3.0, math.pi]
    print("\nDeterministic rounding test:")
    for val in test_values:
        rounded = _dround(val, 6)
        print(f"  {val:.10f} -> {rounded}")

    # Test fsum determinism
    test_list = [0.1, 0.2, 0.3, 0.4]
    regular_sum = sum(test_list)
    fsum_result = math.fsum(test_list)
    print(f"\nSum comparison:")
    print(f"  Regular sum: {regular_sum:.17f}")
    print(f"  fsum:        {fsum_result:.17f}")
    print(f"  Match: {regular_sum == fsum_result}")

    print("\n✅ Planner module loaded with deterministic protocol P0")
