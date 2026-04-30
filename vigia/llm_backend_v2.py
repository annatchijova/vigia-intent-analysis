#!/usr/bin/env python3
"""
vigia/engine/llm_backend_v2.py — Backend de LLM con degradación elegante.

Principio arquitectónico:
  'Nunca pedirle a un modelo lo que no puede hacer.
   Siempre tener un fallback determinista.'

Separa:
  - firstness (descripción) → cualquier backend
  - secondness (anomalías) → herramientas deterministas + narración LLM
  - thirdness (abducción) → motor simbólico si backend no tiene CAUSAL_REASONING
  - devil_advocate (refutación) → SIEMPRE Gorgias, NUNCA LLM
"""

from __future__ import annotations

from enum import IntEnum
from fractions import Fraction
from typing import Dict, List, Optional


class BackendCapability(IntEnum):
    """
    Capacidades en orden estrictamente creciente.
    Un backend con capacidad N puede realizar tareas de nivel <= N.
    """
    FIRSTNESS_ONLY = 0
    ANOMALY_DETECTION = 1
    CAUSAL_REASONING = 2
    FULL_SEMIOTIC = 3


MAX_CAPABILITY = BackendCapability.FULL_SEMIOTIC


class LLMBackendV2:
    """Backend unificado con degradación por capacidades."""

    BACKENDS = {
        "anthropic": {
            "capability": BackendCapability.FULL_SEMIOTIC,
            "cost_per_1k_tokens": 0.015,
            "requires_network": True,
            "default_model": "claude-sonnet-4-20250514"
        },
        "gemini": {
            "capability": BackendCapability.CAUSAL_REASONING,
            "cost_per_1k_tokens": 0.007,
            "requires_network": True,
            "default_model": "gemini-2.5-flash"
        },
        "ollama_q8": {
            "capability": BackendCapability.ANOMALY_DETECTION,
            "cost_per_1k_tokens": 0.0,
            "requires_network": False,
            "default_model": "qwen3:14b-q8_0"
        },
        "ollama_q4": {
            "capability": BackendCapability.FIRSTNESS_ONLY,
            "cost_per_1k_tokens": 0.0,
            "requires_network": False,
            "default_model": "llama3.1:8b-q4_K_M"
        }
    }

    def __init__(self, primary: str, fallback_chain: List[str] = None):
        self.primary = primary
        self.primary_capability = self.BACKENDS[primary]["capability"]
        self.fallback_chain = fallback_chain or []

    def _validate_capability(self, required: BackendCapability) -> None:
        if required > MAX_CAPABILITY:
            raise ValueError(
                f"Required capability {required.name} exceeds system maximum"
            )

    def _has_capability(self, backend_name: str, required: BackendCapability) -> bool:
        backend_info = self.BACKENDS.get(backend_name)
        if not backend_info:
            return False
        return backend_info["capability"] >= required

    def analyze_firstness(self, artifacts: List[Dict]) -> str:
        self._validate_capability(BackendCapability.FIRSTNESS_ONLY)
        prompt = self._build_firstness_prompt(artifacts)
        return self._call_with_fallback(prompt, BackendCapability.FIRSTNESS_ONLY)

    def analyze_secondness(self, anomaly_signals: List, baseline: Dict = None) -> Dict:
        self._validate_capability(BackendCapability.ANOMALY_DETECTION)
        if not anomaly_signals:
            return {"anomalies_detected": False, "narrative": "No anomalies detected."}
        if self.primary_capability >= BackendCapability.ANOMALY_DETECTION:
            prompt = self._build_secondness_narrative_prompt(anomaly_signals)
            narrative = self._call_with_fallback(prompt, BackendCapability.ANOMALY_DETECTION)
        else:
            narrative = self._build_structured_secondness(anomaly_signals)
        return {
            "anomalies_detected": True,
            "signal_count": len(anomaly_signals),
            "narrative": narrative,
            "signals": anomaly_signals
        }

    def analyze_thirdness(self, firstness: str, secondness: Dict) -> str:
        self._validate_capability(BackendCapability.CAUSAL_REASONING)
        if self.primary_capability >= BackendCapability.CAUSAL_REASONING:
            prompt = self._build_thirdness_prompt(firstness, secondness)
            return self._call_primary(prompt)
        else:
            return self._symbolic_abduction(firstness, secondness)

    def generate_devil_advocate(self, thirdness: str, evidence: Dict) -> str:
        return self._gorgias_counter_hypothesis(thirdness, evidence)

    def _call_with_fallback(self, prompt: str, required_capability: BackendCapability) -> str:
        self._validate_capability(required_capability)
        if self.primary_capability >= required_capability:
            return self._call_primary(prompt)
        for backend_name in self.fallback_chain:
            if self._has_capability(backend_name, required_capability):
                return self._call_backend(backend_name, prompt)
        return self._deterministic_response(prompt, required_capability)

    # ── Stubs ────────────────────────────────────────────────────

    def _call_primary(self, prompt: str) -> str:
        return ""

    def _call_backend(self, backend_name: str, prompt: str) -> str:
        return ""

    def _build_firstness_prompt(self, artifacts: List[Dict]) -> str:
        return ""

    def _build_secondness_narrative_prompt(self, signals: List) -> str:
        return ""

    def _build_thirdness_prompt(self, firstness: str, secondness: Dict) -> str:
        return ""

    def _deterministic_response(self, prompt: str, capability: BackendCapability) -> str:
        return ""

    def _structured_artifact_list(self, prompt: str) -> str:
        return ""

    def _build_structured_secondness(self, signals: List) -> str:
        return ""

    def _structured_anomaly_table(self, prompt: str) -> str:
        return ""

    def _symbolic_abduction(self, firstness: str, secondness: Dict) -> str:
        return ""

    def _symbolic_abduction_from_prompt(self, prompt: str) -> str:
        return ""

    def _gorgias_counter_hypothesis(self, thirdness: str, evidence: Dict) -> str:
        return ""
