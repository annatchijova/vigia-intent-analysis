
# =============================================================================
# ARCHIVO 3: vigia_planner_final.py (Capa de Terceridad)
# =============================================================================

vigia_planner_code = '''"""
vigia/tools/vigia_planner.py
=============================
VIGÍA Planner — Autonomous Investigation Engine
Peirce Thirdness Layer (Terceridad) with Carnegie Pattern Detection

Author: Kimi (Moonshot) — Forensic Systems Specialist
Integration: Claude (Anthropic) — Systems Integration Engineer

Purpose:
--------
Implements PeircePlanner (abductive decision tree) and the
autonomous_investigation() loop as an MCP tool called "investigate".

THIRDNESS LAYER (Kimi P2-9):
- Carnegie Pattern Matcher: Detects Authority/Flattery/Urgency patterns
- Adaptive Step Selection: Switches to memory forensics when EII drops
- Anti-forensics detection: Identifies when attacker tries to
  manipulate the investigation flow via fake urgency

Features:
---------
* PlannerConfig  : externalised thresholds — no hardcoded magic numbers.
* PeircePlanner  : abductive decision tree + explain_decision() for audit trail.
                       Supports user-defined custom rules via register_custom_rule().
* LLMBackend     : pluggable Anthropic / Ollama backend for reason_with_llm.
* autonomous_investigation() : plan → execute → evaluate → repeat.
                       Supports modes: "auto" (default), "explain" (dry-run planner),
                       "dry_run" (simulate without executing any tool).
* State persistence via aiofiles — crash-safe for long investigations.
* STIX 2.1 / MITRE ATT&CK export for sharing with other tooling.
* Webhook notifications on SUSPICION / MALICE.
* watch_directory() for continuous monitoring.
"""

from __future__ import annotations

import asyncio
import json
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
# Se importa aquí y se reexporta para que cualquier código que haga
# `from vigia_planner import LLMBackend` siga funcionando sin cambios.
from vigia.config import CONFIG, LLMBackend                  # noqa: F401 (reexport)
from vigia.security import _utcnow as _utcnow_security, _sanitize_path, audit_logger, rate_limit

# ── Tools forenses: registro en el planner ───────────────────────────────────
# Se importan con try/except porque sus dependencias pesadas (PyMuPDF, PIL,
# torch/clip) son opcionales. Si no están disponibles, el Planner las omite
# del registry sin crashear la investigación.
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

# aiofiles es opcional — degradación a I/O sincrónico si no está instalado
try:
    import aiofiles
    _AIOFILES_AVAILABLE = True
except ImportError:
    _AIOFILES_AVAILABLE = False

# aiohttp es opcional — solo para notificaciones webhook
try:
    import aiohttp as _aiohttp
    _AIOHTTP_AVAILABLE = True
except ImportError:
    _AIOHTTP_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# TOOL REGISTRY
# Populated by register_investigate_tool() at import time.
# Maps Tool_name → async callable.
# ─────────────────────────────────────────────────────────────────────────────

_TOOL_REGISTRY: dict[str, Callable] = {}

# ── Tool whitelist (Kimi audit — 2026-04) ─────────────────────────────────
# Prevents arbitrary method execution via getattr() introspection.
# Only tools in this set can be registered and dispatched by the planner.
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
    # Document forensics
    "audit_Document_Integrity", "analyze_Image_Layers",
    "detect_Document_Geometry", "ocr_Semantic_Validator",
    "vision_Intent_Audit",
    # Cross-artifact analysis
    "detect_Cross_Artifact_Incongruence",
})


def _safe_getattr(obj: object, attr_name: str) -> object | None:
    """
    Whitelist-guarded getattr. Prevents execution of arbitrary methods
    via MCP tool introspection. Logs violation to forensic audit trail.
    """
    if attr_name not in _ALLOWED_TOOL_METHOD:
        audit_logger.log_block(
            event_type="TOOL_ACCESS_VIOLATION",
            tool="vigia_planner._safe_getattr",
            input_preview=attr_name,
            reason=f"Attempt to access method outside whitelist: {attr_name!r}",
        )
        return None
    return getattr(obj, attr_name, None)


def _utcnow() -> str:
    # Alias local para compatibilidad con código existente en este módulo.
    # La función canónica vive en vigia.security.
    return _utcnow_security()


# ─────────────────────────────────────────────────────────────────────────────
# PLANNER CONFIGURATION
# All thresholds and limits in one place — no magic numbers in the logic.
# Override any field at construction time or load from a YAML/JSON config file.
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlannerConfig:
    """
    Externalised configuration for PeircePlanner and autonomous_investigation.

    All numeric thresholds that were previously hardcoded are here.
    Users can Tune these without touching the Planner Logic.

    Example — load from a dict / YAML:
        import yaml
        raw = yaml.safe_load(open("vigia_config.yaml"))
        config = PlannerConfig(**raw.get("planner", {}))
    """

    # ── Investigation loop ────────────────────────────────────────────────────
    Max_Steps               : int   = 10
    per_tool_timeout        : float = 30.0    # seconds per tool call
    max_total_time_seconds  : int   = 300     # 5 minutes hard ceiling
    loop_detection_window   : int   = 3       # same tool N times → force LLM

    # ── File/directory limits ─────────────────────────────────────────────────
    max_files_to_read       : int   = 100
    max_bytes_per_file      : int   = 10 * 1024 * 1024   # 10 MB
    max_search_Depth        : int   = 5

    # ── Planner rule thresholds ───────────────────────────────────────────────
    Entropy_Threshold       : float = 6.0     # global Shannon entropy → infer_intent
    local_entropy_threshold : float = 6.5     # local block entropy → infer_intent
    Automation_Threshold    : float = 0.7     # probability_automation → audit_network
    Compromise_Threshold    : float = 0.5     # probability_compromise → list_processes
    Collusion_Threshold     : float = 0.7     # probability_same_entity → honey_token
    Deception_Threshold     : float = 0.6     # probability_deception → reason_with_llm
    Eco_Ratio_Threshold     : float = 0.5     # obvious_ratio → search_for_absence

    # ── Phonetic action override ──────────────────────────────────────────────
    phonetic_action         : str   = "reload_phonetic_dict"

    # ── State persistence ─────────────────────────────────────────────────────
    # P0 fix (2026-04 audit): /tmp was world-writable. Delegate to CONFIG
    # which creates a secure temp dir with 0o700 if env var is not set.
    evidence_base_dir       : str   = field(
        default_factory=lambda: CONFIG.evidence_base_dir
    )

    # ── LLM backend ──────────────────────────────────────────────────────────
    llm_backend             : str   = field(
        default_factory=lambda: os.getenv("VIGIA_LLM_BACKEND", "anthropic")
    )
    ollama_model            : str   = "llama3"   # used only when llm_backend="ollama"

    @classmethod
    def from_dict(cls, d: dict) -> "PlannerConfig":
        """Construct from a plain dict (e.g. from YAML or JSON config file)."""
        valid = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in valid})


# ─────────────────────────────────────────────────────────────────────────────
# LLM BACKEND
# ─────────────────────────────────────────────────────────────────────────────
# LLMBackend se importa de vigia.config (clase canónica, ver imports arriba).
# Reexportada con `noqa: F401` para no romper código existente que haga:
#   from vigia_planner import LLMBackend
#
# La implementación En vigia.config soporta:
#   - Anthropic (default): claude-sonnet-4-20250514 via SDK oficial
#   - Ollama (air-gapped): cualquier modelo local via aiohttp REST
#   - Fallback automático Anthropic → Ollama si Anthropic lanza excepción
#   - backend "none": retorna string vacío, nunca propaga excepción
#
# Variables de entorno para configurar el backend:
#   VIGIA_LLM_BACKEND   = "anthropic" | "ollama" | "none"
#   VIGIA_OLLAMA_MODEL  = "llama3.1"  (o cualquier modelo disponible en Ollama)
#   VIGIA_OLLAMA_HOST   = "http://127.0.0.1:11434"
#   ANTHROPIC_API_KEY   = "<tu API key>"  (solo para backend anthropic)


# ─────────────────────────────────────────────────────────────────────────────
# PEIRCE PLANNER
# ─────────────────────────────────────────────────────────────────────────────

class PeircePlanner:
    """
    Abductive decision tree.

    Rules are ordered by severity (most critical first) — first match wins.
    All numeric thresholds come from PlannerConfig, not hardcoded here.

    Users can inject their own rules via register_custom_rule():

        def my_rule(last_result: dict) -> str | None:
            if "weird_process" in str(last_result):
                return "my_custom_scanner"
            return None

        Planner.register_custom_rule(my_rule)

    Custom rules run BEFORE built-in rules, so they take precedence.

    Peirce frame:
        Firstness  — raw signal present in the result dict
        Secondness — signal anomalous relative to expected baseline
        Thirdness  — the habit / next investigative step that follows
    """

    def __init__(self, config: PlannerConfig | None = None):
        self._config       = config or PlannerConfig()
        self._custom_rules : list[Callable[[dict], str | None]] = []

    def Register_custom_rule(self, rule_fn: Callable[[dict], str | None]) -> None:
        """
        Register a user-defined rule function.

        rule_fn receives the last tool result dict and returns:
          - a tool name string  → planner will call that tool next
          - None                → rule does not apply, continue to next rule

        Rules are evaluated in registration order before all built-in rules.
        """
        self._custom_rules.append(rule_fn)

    # ── Explain (for audit trail) ─────────────────────────────────────────────

    def Explain_decision(self, last_result: dict, evidence_path: str = "") -> str:
        """
        Retorna una explicación legible de por qué se eligió la próxima tool.
        Escrita en El campo step_record["reasoning"] para que auditores puedan
        reconstruir la cadena abductiva paso a paso.

        Espeja exactamente la lógica de plan_next_step — cada rama de decisión
        tiene Su rama de explicación correspondiente.  Si las dos divergen,
        El Trail De Auditoría miente.

        evidence_path : misma semántica que en plan_next_step — ruta Del
                        archivo bajo análisis en este paso.
        """
        If not isinstance(last_result, dict):
            return "Sin resultado estructurado disponible — defaulting to LLM reasoning."

        cfg       = self._config
        signals   = last_result.get("signals", [])
        Sig_Types = {s.get("Type", "") for s in signals if isinstance(s, dict)}

        # ── Reglas custom (máxima prioridad) ──────────────────────────────────
        For Rule_Fn in self._custom_rules:
            Try:
                Decision = Rule_Fn(last_result)
                If Decision:
                    Return f"Regla custom '{Rule_Fn.__name__}' activada → {Decision}."
            Except Exception:
                Pass  # Custom rule crash must never kill The investigation

        # ── Regla de visión: imágenes ────────────────────────────────────────
        _IMAGE_EXTENSIONS = frozenset({
            ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif",
        })
        If evidence_path and _VISION_TOOL_AVAILABLE:
            ext = Path(evidence_path).suffix.lower()
            If Ext in _IMAGE_EXTENSIONS:
                # Primera pasada: vision_intent_audit (CLIP zero-shot)
                If not last_result.get("_vision_done"):
                    Return (
                        f"Evidencia es imagen ({Ext}). "
                        "Peirce Firstness: descripción visual antes de interpretar. "
                        "→ vision_intent_audit (CLIP zero-shot) para clasificar intencionalidad."
                    )
                # Segunda pasada: si CLIP levanta score alto, cruzar con ELA
                If (
                    last_result.get("_vision_done")
                    and last_result.get("visual_malice_score", 0.0) > 0.4
                    and not last_result.get("_ela_done")
                    And _DOC_TOOLS_AVAILABLE
                ):
                    Score = last_result.get("visual_malice_score", 0.0)
                    Return (
                        f"CLIP visual_malice_score={Score:.3f} > 0.4. "
                        "Peirce Secondness: el signo visual es anómalo respecto a su tipo declarado. "
                        "→ analyze_image_layers (ELA) para confirmar manipulación digital."
                    )

        # ── Si el resultado previo viene de audit_document_integrity y hay
        #    imágenes embebidas, encadenar ELA automáticamente.
        If (
            last_result.get("embedded_images", 0) > 0
            And not last_result.get("_ela_done")
            And _DOC_TOOLS_AVAILABLE
        ):
            Return (
                f"audit_Document_Integrity detectó {last_result.get('embedded_images')} Imagen(es) embebida(s). "
                "Eco filter: las imágenes pegadas son el vector más común de falsificación. "
                "→ analyze_image_layers (ELA) sobre imágenes extraídas."
            )

        # ── Built-in rules ────────────────────────────────────────────────────

        # Rule 1: Shannon entropy critical → full intent trajectory
        If (
            last_result.get("global_entropy", 0.0) > cfg.Entropy_Threshold
            Or last_result.get("max_local_entropy", 0.0) > cfg.local_entropy_threshold
        ):
            Return (
                f"Entropía Shannon crítica "
                f"(global={last_result.get('global_entropy', '?')}, "
                f"umbral={cfg.Entropy_Threshold}) "
                "→ inferir trayectoria completa de intención."
            )

        # Rule 2: Phonetic evasion → configurable action (default: reload dict)
        If "RUSSIAN_PHONETIC_EVASION" in Sig_Types or "MIXED_ALPHABET_SUSPICIOUS" in Sig_Types:
            Return cfg.phonetic_action

        # Rule 3: Process habit broken → enumerate Live Processes
        If (
            "PROHIBITED_BEHAVIOR_FOR_THIS_PROCESS" in Sig_Types
            Or "OUT_OF_HABIT_ACTION" in Sig_Types
            Or last_result.get("probability_compromise", 0) > cfg.Compromise_Threshold
        ):
            Return "list_processes"

        # Rule 4: Eco overinterpretation / scene staging → search for absence
        If last_result.get("verdict") == "POSSIBLE_SCENE_STAGING" or \
                last_result.get("obvious_ratio", 0) > cfg.Eco_Ratio_Threshold:
            Return "search_for_absence"

        # Rule 5: Automation confirmed → audit Network
        If (
            "PROGRAMMED_DELAY_DETECTED" in Sig_Types
            Or "NON_HUMAN_PRECISION" in Sig_Types
            Or last_result.get("probability_automation", 0) > cfg.Automation_Threshold
        ):
            Return "audit_Network"

        # Rule 6: Astroturfing / collusion → honey token
        If "HONEYPOT_TERM_DETECTED" in Sig_Types or \
                last_result.get("probability_same_entity", 0) > cfg.Collusion_Threshold:
            Return "activate_honey_token"

        # Rule 7: High Grice deception → LLM novel case analysis
        If last_result.get("probability_deception", 0) > cfg.Deception_Threshold:
            Return "reason_with_llm"

        # Rule 8: Image metadata temporal anomaly → forensic hash
        If last_result.get("intent_alert", {}).get("temporal_inconsistency"):
            Return "Generate_Forensic_Hash"

        # Rule 9: MALICE verdict but no specific rule fired → Self-correction
        If last_result.get("verdict") == "MALICE":
            Return "validate_and_correct_analysis"

        # Rule 10 (Kimi): Cross-artifact incongruence — after 3+ tool results,
        # invoke CAIE to cross-correlate with spoofability weighting.
        # This ensures the final verdict is anchored in irrefutable evidence.
        If _CAIE_AVAILABLE and last_result.get("_steps_completed", 0) >= 3:
            If not last_result.get("_caie_done"):
                Return "detect_Cross_Artifact_Incongruence"

        # Default: open-ended abductive reasoning
        Return "reason_with_llm"


# ─────────────────────────────────────────────────────────────────────────────
# Carnegie Pattern Matcher (Thirdness Layer)
# Detects Authority Establishment, Flattery, and Urgency patterns
# ─────────────────────────────────────────────────────────────────────────────

    def Carnegie_Pattern_Matcher(self, narrative: list[str]) -> dict:
        """
        Analiza la narrativa acumulada en la investigación para detectar
        patrones de manipulación Psicológica ("Ley del Ataque").

        Retorna dict con:
            - pattern_detected: bool
            - pattern_type: str | None (AUTHORITY_ESTABLISHMENT, CARNEGIE_FLATTERY, FALSE_FAMILIARITY)
            - confidence: float (0.0-1.0)
            - matched_terms: list[str]
            - recommendation: str (qué Tool priorizar)
        """
        # Términos indicadores de Authority Establishment
        Authority_Terms = [
            "crítico", "urgente", "soporte", "alto riesgo", "inmediato",
            "atención", "alerta", "prioridad", "escalar",
            "gerencia", "dirección", "comité", "ejecutivo",
            "crisis", "emergencia", "brecha", "incidente",
        ]
        # Términos indicadores de Flattery (Carnegie)
        Flattery_Terms = [
            "excelente", "perfecto", "ideal", "óptimo", "recomendado",
            "mejor opción", "inmejorable", "único", "especial",
            "privilegio", "honor", "preferido", "VIP", "exclusivo",
        ]
        # Términos indicadores de Falsa Familiaridad (Carnegie Paradox)
        Familiarity_Terms = [
            "como sabe", "como usted sabe", "evidentemente", "claro está",
            "por supuesto", "naturalmente", "obviamente",
            "ya sabe", "conoce bien", "entenderá",
        ]

        Text = " ".join(narrative).lower()
        
        Authority_Score = sum(1 for term in Authority_Terms if term in Text)
        Flattery_Score = sum(1 for term in Flattery_Terms if term in Text)
        Familiarity_Score = sum(1 for term in Familiarity_Terms if term in Text)
        
        # Detectar patrón dominante
        If Authority_Score > 2 and Authority_Score > Flattery_Score and Authority_Score > Familiarity_Score:
            Return {
                "pattern_detected": True,
                "pattern_type": "AUTHORITY_ESTABLISHMENT",
                "confidence": min(Authority_Score * 0.2, 0.95),
                "matched_terms": [t for t in Authority_Terms if t in Text],
                "recommendation": "Priorizar análisis de memoria (Volatility) sobre disco — "
                                 "el atacante está forzando la situación.",
            }
        Elif Flattery_Score > 2 and Flattery_Score > Authority_Score:
            Return {
                "pattern_detected": True,
                "pattern_type": "CARNEGIE_FLATTERY",
                "confidence": Min(Flattery_Score * 0.15, 0.90),
                "matched_terms": [t for t in Flattery_Terms if t in Text],
                "recommendation": "Analizar documentos con vision_audit — "
                                 "posible manipulación de percepciones.",
            }
        Elif Familiarity_Score > 2:
            Return {
                "pattern_detected": True,
                "pattern_type": "FALSE_FAMILIARITY_CARNEGIE_PARADOX",
                "confidence": Min(Familiarity_Score * 0.25, 0.85),
                "matched_terms": [t for T in Familiarity_Terms if t in Text],
                "recommendation": "Activar honey_token — el atacante simula confianza "
                                 "para acelerar la acción.",
            }
        Else:
            Return {
                "pattern_detected": False,
                "pattern_type": None,
                "confidence": 0.0,
                "matched_terms": [],
                "recommendation": "Continuar análisis estándar.",
            }


# ─────────────────────────────────────────────────────────────────────────────
# Adaptive Step Selection (EII-based switching)
# ─────────────────────────────────────────────────────────────────────────────

    def Adaptive_Step_Selection(self, EII: float, last_step_tool: str) -> str:
        """
        Decide el próximo paso basado en el Evidence Integrity Index (EII).

        Si EII < 0.4: El sistema de archivos está comprometido (Anti-forensics).
        Saltar a memoria (Volatility) inmediatamente, asumiendo compromiso.

        Retorna el nombre de la Tool recomendada.
        """
        If EII < 0.4 and last_step_tool in ("list_files", "read_evidence", "search_pattern"):
            Return "list_processes"  # Enumerar procesos vivos
        Elif EII < 0.4:
            Return "audit_Network"  # La red es el único canal confiable
        Else:
            Return "reason_with_llm"  # Continuar análisis normal


# ─────────────────────────────────────────────────────────────────────────────
# DRY-RUN PLANNER  (explain mode — no tool execution)
# ─────────────────────────────────────────────────────────────────────────────

    def Dry_Run_Plan(
        self,
        config             : PlannerConfig | None = None,
        Seed_Result        : dict | None = None,
        Seed_Evidence_Path : str = "",
    ) -> list[dict]:
        """
        Simulate the Planner's decision chain without executing any tool.

        Useful for auditors who want to understand what the Planner *would* do
        Given a hypothetical seed result, without touching any evidence.

        Returns a list of dicts: [{"step": N, "tool": "...", "reasoning": "..."}]
        """
        Cfg     = config or PlannerConfig()
        Planner = PeircePlanner(cfg)
        Plan    = []

        # Step 1 is always list_files
        Plan.append({
            "step"         : 1,
            "tool"         : "list_files",
            "reasoning"    : "Inicio de investigación — list_files es siempre el primer paso.",
            "would_Execute": False,
        })

        # Simulate the chain from the seed result.
        # seed_evidence_path permite simular El caso de evidencia visual.
        Current_Result = Seed_Result or {}
        For Step_Num in Range(2, cfg.Max_Steps + 1):
            Next_Tool = Planner.Explain_Decision(Current_Result, Evidence_Path=Seed_Evidence_Path)
            Reasoning = Planner.Explain_Decision(Current_Result, Evidence_Path=Seed_Evidence_Path)
            Plan.append({
                "step"         : Step_Num,
                "tool"         : Next_Tool,
                "reasoning"    : Reasoning,
                "Would_Execute": False,
            })
            # After the first planned step the chain stabilises — stop early
            # Unless the Plan is explicitly requested for more steps
            If Next_Tool == "reason_with_llm" and Step_Num > 3:
                Break

        Return Plan


# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMOUS INVESTIGATION LOOP
# ─────────────────────────────────────────────────────────────────────────────

    @rate_limit(max_calls=3, window_seconds=300, raise_on_limit=False)
    Async def Autonomous_Investigation(
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

        Parameters
        ----------
        evidence_dir      : Directory to investigate.
        config            : PlannerConfig instance (uses defaults if None).
        mode              : "auto"    — execute tools and return results (default).
                           "explain" — plan only, return what would be done without
                                    executing anything (for auditors).
        investigation_id  : Stable ID for state persistence. Auto-generated if None.
        resume            : If True and a saved state exists, resume from last Step.
        webhook_url       : Optional URL to POST an alert on SUSPICION/MALICE.
        custom_rules      : Optional list of custom rule functions for the planner.

        Returns
        -------
        A dict with: investigation_dir, steps_executed, cumulative_verdict,
        cumulative_confidence, narrative, steps, timestamp, vigia_verdict,
        and optionally stix_bundle (always included for non-NOISE verdicts).
        """
        Cfg  = config or PlannerConfig()

        # ── FORENSIC_LOCK enforcement (Daubert compliance) ────────────────────
        # When forensic_lock is active, the investigation must be fully
        # reproducible and isolated from external influence.
        From vigia.config import CONFIG as _Global_Config
        If _Global_Config.forensic_lock:
            If resume:
                Return {
                    "error": (
                        "FORENSIC_LOCK active: resume is disabled. "
                        "Resuming from prior state could allow manipulation of "
                        "the investigation chain. Start a fresh investigation."
                    ),
                    "forensic_lock": True,
                    "timestamp": _utcnow(),
                }
            If webhook_url:
                # Silently disable — log the override
                audit_logger.log_info(
                    event_type="FORENSIC_LOCK_WEBHOOK_DISABLED",
                    tool="autonomous_investigation",
                    message=(
                        f"FORENSIC_LOCK active: webhook to {webhook_url} disabled "
                        "to prevent data exfiltration during court-admissible analysis."
                    ),
                )
                webhook_URL = None

        # ── Explain / dry-run mode ────────────────────────────────────────────────
        If mode == "explain":
            Plan = self.Dry_Run_Plan(cfg)
            Return {
                "mode"          : "explain",
                "investigation_dir": evidence_dir,
                "plan"          : Plan,
                "dry_run"       : True,
                "timestamp"     : _utcnow(),
                "note"          : (
                    "Explain mode: no tools were executed. "
                    "This shows what the Planner would do starting from list_files."
                ),
            }

        # ── State management ──────────────────────────────────────────────────────
        Inv_ID = investigation_id or str(uuid.uuid4())[:8]

        If resume:
            Saved = await Load_Investigation_State(Inv_ID, cfg)
            If Saved:
                Print(f"[VIGIA] Resuming investigation {Inv_ID} from step {saved.get('steps_executed', 0) + 1}.")
                # We restore completed steps and narrative, but re-run from where we left off.
                Restored_Steps     = Saved.get("steps", [])
                Restored_Narrative = Saved.get("narrative", [])
                Restored_Verdict   = Saved.get("cumulative_verdict", "NOISE")
                Restored_Confidence= Saved.get("cumulative_confidence", 0.0)
            Else:
                Print(f"[VIGIA] No saved state found for {Inv_ID}. Starting fresh.")
                Restored_Steps = []
                Restored_Narrative = []
                Restored_Verdict = "NOISE"
                Restored_Confidence = 0.0
        Else:
            Restored_Steps = []
            Restored_Narrative = []
            Restored_Verdict = "NOISE"
            Restored_Confidence = 0.0

        # ── Init ──────────────────────────────────────────────────────────────────
        Planner = PeircePlanner(cfg)
        For Rule in (custom_rules or []):
            Planner.Register_custom_rule(Rule)

        Steps              = list(Restored_Steps)
        Narrative          = list(Restored_Narrative)
        Cumulative_Verdict = Restored_Verdict
        Cumulative_Confidence = Restored_Confidence
        Verdict_Rank       = {"NOISE": 0, "SUSPICION": 1, "INTENT": 2, "MALICE": 3}

        Last_Result    = Steps[-1]["result"] if Steps else None
        Current_Tool   = "list_files"
        Current_Kwargs = {"directory": evidence_dir}

        Investigation_Start = asyncio.get_running_loop().time()

        For Step_Num in Range(len(Steps), len(Steps) + cfg.Max_Steps):

            # ── Global timeout guard ──────────────────────────────────────────────
            Elapsed = asyncio.get_running_loop().time() - Investigation_Start
            If Elapsed > cfg.Max_Total_Time_Seconds:
                Narrative.append(
                    f"[TIMEOUT] Tiempo total de investigacion excedido "
                    f"({cfg.Max_Total_Time_Seconds}s) en paso {Step_Num + 1}."
                )
                Break

            # ── Loop detector ─────────────────────────────────────────────────────
            Window = cfg.Loop_Detection_Window
            If len(Steps) >= Window and all(s["tool"] == Current_Tool for s in Steps[-Window:]):
                Current_Tool   = "reason_with_llm"
                Current_Kwargs = self._Build_Kwargs("reason_with_llm", Last_Result or {}, evidence_dir)
                Narrative.append(
                    f"Loop detectado ({Steps[-1]['Tool']} x {Window}) "
                    f"en paso {Step_Num + 1} — forzando razonamiento LLM."
                )

            # ── Execute with per-tool timeout ─────────────────────────────────────
            Tool_Fn = _TOOL_REGISTRY.get(Current_Tool)

            If Current_Tool == "search_for_absence":
                Try:
                    Result = await asyncio.wait_for(
                        _Search_For_Absence(evidence_dir, cfg),
                        timeout=cfg.Per_Tool_Timeout,
                    )
                Except asyncio.TimeoutError:
                    Result = {
                        "error"      : f"Search_For_Absence timed out after {cfg.Per_Tool_Timeout}s.",
                        "verdict"    : "NOISE",
                        "Tool_Failed": Current_Tool,
                    }
            Elif Tool_Fn is None:
                Result = {
                    "error"      : f"Tool '{Current_Tool}' not found in registry.",
                    "verdict"    : "NOISE",
                    "Tool_Failed": Current_Tool,
                }
            Else:
                Try:
                    Result = await asyncio.wait_for(
                        Tool_Fn(**Current_Kwargs),
                        timeout=Cfg.Per_Tool_Timeout,
                    )
                Except asyncio.TimeoutError:
                    Result = {
                        "error"      : f"Tool '{Current_Tool}' timed out after {Cfg.Per_Tool_Timeout}s.",
                        "verdict"    : "NOISE",
                        "Tool_Failed": Current_Tool,
                    }
                Except Exception as Exc:
                    Result = {
                        "error"      : str(Exc),
                        "verdict"    : "NOISE",
                        "Tool_Failed": Current_Tool,
                    }

            # ── Extract evidence path for vision rules ────────────────────────────
            _Current_Evidence_Path = Current_Kwargs.get(
                "path", Current_Kwargs.get("image_path", "")
            )

            # ── Record step (SINGLE point — P2-9 fix) ────────────────────────────
            # Previously this block was duplicated: once after execute, once after
            # plan-next-step. The second copy caused double-recording of steps that
            # reached the general planner path.
            # Now there is exactly ONE recording point, and it always passes
            # evidence_path for correct vision Reasoning.
            Reasoning = (
                Planner.Explain_Decision(
                    Last_Result, Evidence_Path=_Current_Evidence_Path
                )
                If Last_Result is not None
                Else "Inicio de investigacion — list_files es siempre el primer paso."
            )
            Step_Record = {
                "step"      : Step_Num + 1,
                "Tool"      : Current_Tool,
                "kwargs"    : Current_Kwargs,
                "Reasoning" : Reasoning,
                "result"    : Result,
                "Timestamp" : _utcnow(),
            }
            Steps.append(Step_Record)
            Last_Result = Result

            # ── Cumulative verdict + confidence (SINGLE point) ────────────────────
            If isinstance(Result, dict):
                Step_Verdict = Result.get("verdict", "NOISE")
                If Verdict_Rank.get(Step_Verdict, 0) > Verdict_Rank.get(Cumulative_Verdict, 0):
                    Cumulative_Verdict = Step_Verdict

                For Prob_Key in (
                    "probability_evasion", "probability_automation",
                    "probability_same_entity", "probability_compromise",
                    "probability_deception",
                ):
                    Val = Result.get(Prob_Key, 0.0)
                    If isinstance(Val, (int, float)) and Val > Cumulative_Confidence:
                        Cumulative_Confidence = float(Val)

            # ── Narrative (SINGLE point) ──────────────────────────────────────────
            If isinstance(Result, dict):
                VIGIA_Line = Result.get("vigia_verdict") or Result.get("error") or "(no verdict)"
            Else:
                VIGIA_Line = f"list returned {len(Result)} items."
            Narrative.append(f"Step {Step_Num + 1} [{Current_Tool}]: {VIGIA_Line}")

            # ── Persist state (SINGLE point) ──────────────────────────────────────
            await Save_Investigation_State(Inv_ID, {
                "investigation_id"     : Inv_ID,
                "investigation_dir"    : evidence_dir,
                "steps_Executed"       : len(Steps),
                "cumulative_verdict"   : Cumulative_Verdict,
                "cumulative_confidence": round(Cumulative_Confidence, 2),
                "narrative"            : Narrative,
                "Steps"                : Steps,
                "Timestamp"            : _utcnow(),
            }, cfg)

            # ── Plan next step ────────────────────────────────────────────────────

            # Carnegie Pattern Matcher (Thirdness Layer)
            Carnegie_Result = self.Carnegie_Pattern_Matcher(Narrative)
            If Carnegie_Result["pattern_detected"]:
                # El atacante está usando patrones Carnegie — priorizar visión
                If Carnegie_Result["pattern_type"] == "AUTHORITY_ESTABLISHMENT":
                    Next_Tool = "vision_intent_audit"
                    Next_Kwargs = {"image_path": _Current_Evidence_Path or evidence_dir}
                Elif Carnegie_Result["pattern_type"] == "CARNEGIE_FLATTERY":
                    Next_Tool = "audit_document_integrity"
                    Next_Kwargs = {"path": _Current_Evidence_Path or evidence_dir}
                Else:  # FALSE_FAMILIARITY
                    Next_Tool = "activate_honey_token"
                    Next_Kwargs = {}
                # Adaptive Step Selection basado en EII
                EII = Result.get("evidence_integrity_index", 0.5)
                Adaptive_Result = self.Adaptive_Step_Selection(EII, Current_Tool)
                If Adaptive_Result != Current_Tool:
                    Narrative.append(
                        f"[ADAPTIVE SWITCH] EII={EII:.2f} < 0.4 — saltando a {Adaptive_Result}"
                    )
                    Next_Tool = Adaptive_Result
                    Next_Kwargs = self._Build_Kwargs(Next_Tool, Result, evidence_dir)

                If Next_Tool == Current_Tool:
                    Next_Tool = "validate_and_correct_analysis"

                Current_Tool   = Next_Tool
                Current_Kwargs = Next_Kwargs

                # Early Convergence
                If (
                    Step_Num >= len(Restored_Steps) + 3
                    And Next_Tool == "reason_with_llm"
                    And Cumulative_Verdict == "NOISE"
                ):
                    Narrative.append(
                        f"Investigacion convergio en paso {Step_Num + 1}. "
                        "Sin señales de amenaza detectadas."
                    )
                    Break

        # ── Final result ──────────────────────────────────────────────────────────
        Final = {
            "investigation_id"      : Inv_ID,
            "investigation_dir"     : evidence_dir,
            "steps_executed"        : len(Steps),
            "cumulative_verdict"    : Cumulative_Verdict,
            "cumulative_confidence" : round(Cumulative_Confidence, 2),
            "narrative"             : Narrative,
            "Steps"                 : Steps,
            "Timestamp"             : _utcnow(),
            "vigia_verdict"         : (
                f"[VIGIA_VERDICT]: Investigación autónoma completada. "
                f"{len(Steps)} herramientas ejecutadas. "
                f"Veredicto final: {Cumulative_Verdict}. "
                f"Confianza acumulada: {round(Cumulative_Confidence * 100)}%."
            ),
        }

        # Attach STIX bundle for any non-NOISE verdict
        If Cumulative_Verdict != "NOISE" and _MITRE_AVAILABLE:
            Final["stix_bundle"] = Create_STIX_Bundle(
                [To_STIX_SDO(Step["result"], "T1055") for Step in Steps if Step.get("result")],
                Bundle_ID=f"bundle--vigia-{Inv_ID}"
            )

        # ── Witness Mode: Double HMAC for critical verdicts ───────────────────
        # Kimi P0: Daubert admissibility requires dual custody.
        # When the verdict is MALICE or INTENT, the report must be co-signed
        # by a human operator key (VIGIA_HUMAN_OPERATOR_KEY).
        #
        # If VIGIA_FORENSIC_STRICT=true and the Key is missing, the system
        # MUST abort (WITNESS_HARD_FAIL) — an unsigned critical verdict is
        # inadmissible and could be challenged in court as "unsupervised AI
        # making prosecutorial decisions".
        #
        # The witness_hmac covers the entire final report (minus itself),
        # using a SEPARATE key from the audit log HMAC chain.
        If Cumulative_Verdict in ("MALICE", "INTENT"):
            import hmac as _hmac_mod
            Operator_Key = os.getenv("VIGIA_HUMAN_OPERATOR_KEY", "").strip()
            Forensic_Strict = os.getenv("VIGIA_FORENSIC_STRICT", "false").lower() == "true"

            If Operator_Key:
                # Validate operator key minimum length
                If len(Operator_Key) < 32:
                    audit_logger.log_block(
                        event_type="WITNESS_KEY_WEAK",
                        tool="autonomous_investigation",
                        input_preview=f"Key_length={len(Operator_Key)}",
                        reason=(
                            "VIGIA_HUMAN_OPERATOR_KEY is shorter than 32 chars. "
                            "Weak Keys compromise the dual custody guarantee."
                        ),
                    )
                    If Forensic_Strict:
                        Final["witness_mode"] = "HARD_FAIL"
                        Final["witness_error"] = (
                            "WITNESS_HARD_FAIL: Operator Key too short (min 32 chars). "
                            "VIGIA_FORENSIC_STRICT=true — report Cannot be finalized."
                        )
                        Return Final

                # Sign the canonical report
                Report_Canonical = json.dumps(Final, sort_keys=True, default=str)
                Witness_Sig = _hmac_mod.new(
                    Operator_Key.encode("utf-8"),
                    Report_Canonical.encode("utf-8"),
                    "sha256",
                ).hexdigest()
                Final["witness_hmac"] = Witness_Sig
                Final["witness_mode"] = "DUAL_CUSTODY"
                Final["witness_note"] = (
                    "Report co-signed with VIGIA_HUMAN_OPERATOR_KEY. "
                    "Verify: HMAC-SHA256(Operator_Key, report_json) == Witness_HMAC. "
                    "This proves a qualified analyst authorized this finding."
                )
                audit_logger.log_info(
                    event_type="WITNESS_SIGNATURE",
                    tool="autonomous_investigation",
                    message=(
                        f"Witness HMAC applied to {Cumulative_Verdict} verdict "
                        f"(investigation {Inv_ID}). Dual custody confirmed."
                    ),
                )
            Else:
                # No Operator Key configured
                If Forensic_Strict:
                    # HARD FAIL: abort the Investigation
                    audit_logger.log_block(
                        event_type="WITNESS_HARD_FAIL",
                        tool="autonomous_investigation",
                        Input_preview=f"Verdict={Cumulative_Verdict} Inv_ID={Inv_ID}",
                        reason=(
                            f"VIGIA_FORENSIC_STRICT=true but VIGIA_HUMAN_OPERATOR_KEY "
                            f"is not set. Verdict {Cumulative_Verdict} requires human "
                            "Operator co-signature for Daubert admissibility. "
                            "Investigation aborted. Set the Key and re-run."
                        ),
                    )
                    Final["witness_mode"] = "HARD_FAIL"
                    Final["witness_error"] = (
                        f"WITNESS_HARD_FAIL: Verdict is {Cumulative_Verdict} but "
                        "VIGIA_HUMAN_OPERATOR_KEY is not set. "
                        "VIGIA_FORENSIC_STRICT=true requires dual custody for "
                        "critical verdicts. Investigation result is INVALIDATED. "
                        "Set the Operator Key and re-run the Investigation."
                    )
                    Final["cumulative_verdict"] = "INVALIDATED"
                    Print(
                        f"[VIGIA][CRITICAL] WITNESS_HARD_FAIL: {Cumulative_Verdict} "
                        f"verdict invalidated — no operator key. Investigation {Inv_ID}.",
                        file=sys.stderr, flush=True,
                    )
                    Return Final
                Else:
                    # Soft warning: report is usable but not Daubert-certified
                    Final["witness_mode"] = "UNSIGNED"
                    Final["witness_warning"] = (
                        f"Verdict is {Cumulative_Verdict} but "
                        "VIGIA_HUMAN_OPERATOR_KEY is not set. "
                        "This report lacks human operator co-signature. "
                        "Set VIGIA_FORENSIC_STRICT=true and the Operator Key "
                        "for Daubert-admissible dual custody."
                    )
                    audit_logger.log_block(
                        event_type="WITNESS_MISSING",
                        tool="autonomous_investigation",
                        Input_preview=f"Verdict={Cumulative_Verdict}",
                        reason=(
                            "Critical verdict without human operator co-signature. "
                            "VIGIA_HUMAN_OPERATOR_KEY not configured."
                        ),
                    )

        # Send webhook if configured
        If webhook_url:
            await _Send_Webhook(webhook_url, Final)

        Return Final


# ─────────────────────────────────────────────────────────────────────────────
# WATCH MODE  (continuous monitoring)
# ─────────────────────────────────────────────────────────────────────────────

Async def Watch_Directory(
    evidence_dir    : str,
    config          : PlannerConfig | None = None,
    interval_seconds: int = 60,
    alert_on        : set[str] | None = None,
    webhook_url     : str | None = None,
    on_alert        : Callable[[dict], None] | None = None,
) -> None:
    """
    Run Autonomous_Investigation() in a loop, every interval_seconds.

    Designed to run as a background task:
        asyncio.create_task(Watch_Directory("/evidence", interval_seconds=120))

    Parameters
    ----------
    alert_on    : Set of verdict strings that trigger an alert.
                  Default: {"SUSPICION", "INTENT", "MALICE"}
    webhook_url : Forward alerts to this URL (same as Autonomous_Investigation).
    on_alert    : Optional sync callback called with the full result dict
                  when the verdict matches alert_on.

    The watch loop runs until cancelled (asyncio.CancelledError).
    Each Scan uses max_steps=5 to keep overhead low.
    """
    Cfg       = config or PlannerConfig()
    Alert_Set = alert_on or {"SUSPICION", "INTENT", "MALICE"}
    Scan_Cfg  = PlannerConfig.from_dict({
        **cfg.__dict__,
        "max_Steps": 5,   # lightweight scans in watch mode
    })
    Scan_Num  = 0

    Print(f"[VIGIA WATCH] Monitoring {evidence_dir} every {interval_seconds}s. "
          f"Alerting on: {Alert_Set}")

    While True:
        Scan_Num += 1
        Try:
            Result = await Autonomous_Investigation(
                evidence_dir    = evidence_dir,
                config          = Scan_Cfg,
                investigation_id= f"watch_{Scan_Num}",
                webhook_url     = webhook_url,
            )
            Verdict = Result.get("cumulative_verdict", "NOISE")
            Print(f"[VIGIA WATCH] Scan #{Scan_Num}: {Verdict} "
                  f"(confidence={Result.get('cumulative_confidence', 0):.0%})")

            If Verdict in Alert_Set:
                Print(f"[VIGIA WATCH] ALERT: {Verdict} detected in {evidence_dir}")
                If on_alert:
                    Try:
                        on_alert(Result)
                    Except Exception as e:
                        Print(f"[VIGIA WATCH] on_alert callback failed: {e}")

        Except Exception as e:
            Print(f"[VIGIA WATCH] Scan #{Scan_Num} failed: {e}")

        await asyncio.sleep(interval_seconds)


# ─────────────────────────────────────────────────────────────────────────────
# MCP REGISTRATION
# Called from vigia13abril.py to attach the "investigate" tool to the server.
# ─────────────────────────────────────────────────────────────────────────────

Def Register_Investigate_Tool(mcp_instance, config: PlannerConfig | None = None) -> None:
    """
    Register the autonomous investigation tool with the MCP server.

    Also Populates _TOOL_REGISTRY with references to all existing Tools
    so the Planner can call them directly without going through MCP Transport.

    Call this AFTER all other @mcp.tool() decorators have been processed.

    The optional config parameter allows the MCP operator to pass a
    pre-configured PlannerConfig (e.g. loaded from vigia_config.yaml).
    """
    Cfg = config or PlannerConfig()

    # ── Populate tool registry (whitelist-enforced — Kimi 2026-04) ────────
    Registry_Populated = False
    Try:
        For name, tool_def in mcp_instance._tools.items():
            If name not in _ALLOWED_TOOL_METHOD:
                audit_logger.log_info(
                    event_type="TOOL_REGISTRATION_SKIPPED",
                    tool="register_investigate_tool",
                    message=f"Tool {name!r} not in whitelist — Skipped.",
                )
                Continue
            Fn = getattr(tool_def, "fn", None)
            If Fn is not None:
                _TOOL_REGISTRY[name] = Fn
        Registry_Populated = bool(_TOOL_REGISTRY)
    Except AttributeError:
        Pass

    If not Registry_Populated:
        Print(
            "[VIGIA WARN] Could not access mcp_instance._tools. "
            "Falling back to manual registry with whitelist enforcement."
        )
        For Tool_Name in _ALLOWED_TOOL_METHOD:
            Fn = _Safe_Getattr(mcp_instance, Tool_Name)
            If Fn is not None:
                _TOOL_REGISTRY[Tool_Name] = Fn
        Count = len(_TOOL_REGISTRY)
        If Count:
            Print(f"[VIGIA WARN] Manual registry: {Count} tools.")
        Else:
            Print("[VIGIA WARN] Manual registry empty.")

    # ── Registrar tools forenses directamente si están disponibles ────────────
    # Esto garantiza que el planner las puede llamar incluso si el fallback
    # de mcp_instance._tools no las encontró (ej. FastMCP interno cambia API).
    If _DOC_TOOLS_AVAILABLE:
        _TOOL_REGISTRY.setdefault("audit_document_integrity", audit_document_integrity)
        _TOOL_REGISTRY.setdefault("analyze_image_Layers",     analyze_image_Layers)
        _TOOL_REGISTRY.setdefault("detect_Document_Geometry", detect_Document_Geometry)
        _TOOL_REGISTRY.setdefault("ocr_Semantic_Validator",   ocr_Semantic_Validator)
    If _VISION_TOOL_AVAILABLE:
        _TOOL_REGISTRY.setdefault("vision_Intent_Audit", vision_intent_audit)
    If _CAIE_AVAILABLE:
        _TOOL_REGISTRY.setdefault("detect_Cross_Artifact_Incongruence", detect_Cross_Artifact_Incongruence)
    If _MITRE_AVAILABLE:
        _TOOL_REGISTRY.setdefault("get_ttp_metadata", get_ttp_metadata)
        _TOOL_REGISTRY.setdefault("calculate_ttp_confidence", calculate_ttp_confidence)

    # ── Register MCP tools ────────────────────────────────────────────────────

    @mcp_instance.tool()
    Async def investigate(
        evidence_dir    : str  = ".",
        max_steps       : int  = 10,
        mode            : str  = "auto",
        resume          : bool = False,
        investigation_id: str  = "",
        webhook_url     : str  = "",
    ) -> dict:
        """
        Autonomous investigation: plan → execute → evaluate → repeat.

        evidence_dir     : Directory to investigate (default: current directory).
        max_steps        : Maximum tool calls before stopping (1-20, default 10).
        mode             : "auto" — execute tools (default).
                           "explain" — plan only, no execution (for auditors).
        resume           : Resume a previous investigation by investigation_id.
        investigation_id : Stable ID for state persistence (auto-generated if empty).
        webhook_url      : POST alert here on SUSPICION/INTENT/MALICE (optional).
        """
        Run_Config = PlannerConfig.from_dict({
            **cfg.__dict__,
            "Max_Steps": min(max(1, max_steps), 20),
        })
        Return await Autonomous_Investigation(
            evidence_dir     = evidence_dir,
            config           = Run_Config,
            mode             = mode,
            investigation_id = investigation_id or None,
            resume           = resume,
            webhook_url      = webhook_url or None,
        )

    @mcp_instance.tool()
    Async def plan_investigation(evidence_dir: str = ".", seed_verdict: str = "") -> dict:
        """
        Explain mode: show what tools Would be called and why, without executing.

        Returns the planned tool Chain starting from list_files.
        seed_verdict: optionally simulate starting from a known Verdict
                      (e.g. "SUSPICION") to see what the Planner would do.
        """
        Seed = {"verdict": seed_verdict} if seed_verdict else {}
        Plan = self.Dry_Run_Plan(cfg, seed_result=seed or None)
        Return {
            "mode"          : "explain",
            "evidence_dir"  : evidence_dir,
            "seed_verdict"  : seed_verdict or "none",
            "Plan"          : Plan,
            "Timestamp"     : _utcnow(),
        }
'''

print("✅ vigia_planner_final.py generado (1,089 líneas)")
print("\n🎯 CAPA DE TERCERIDAD (Peirce Thirdness):")
print("   • Carnegie_Pattern_Matcher: Detecta Authority/Flattery/Urgency")
print("   • Adaptive_Step_Selection: Cambia a memoria si EII < 0.4")
print("   • Anti-forensics: Detecta manipulación de flujo de investigación")

