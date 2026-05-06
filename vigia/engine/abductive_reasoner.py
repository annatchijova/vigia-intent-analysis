"""
vigia/engine/abductive_reasoner.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. MAGIC NUMBER: _log(x) ahora usa NEG_INF = -10**18 en lugar de -10**6.
   En sistemas bayesianos con 100+ señales, -10**6 puede no ser suficiente
   para anular completamente una hipótesis. -10**18 garantiza anulación.
2. FRACTION PURITY: Todos los cálculos usan Fraction sin contaminación float.
3. BOUND CHECK: _exp(x) ahora tiene clamping para evitar overflow en casos extremos.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from fractions import Fraction

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX

EPS = Fraction(1, 10**9)
COLLAPSE_THRESHOLD = Fraction(4, 5)
PRUNING_THRESHOLD = Fraction(1, 25)
MIN_SIGNALS = 3
NEUTRAL = Fraction(1, 2)
LN2 = Fraction(693147180559945309417232121458, 1000000000000000000000000000000)

# FIX P0: NEG_INF suficientemente pequeño para anular hipótesis en sistemas grandes
# Con 100 señales y prior 0.01, necesitamos que -10**18 sea >> 100 * log(0.01) ≈ -460
# -10**18 es seguro para cualquier sistema práctico.
NEG_INF = Fraction(-10**18, 1)


@dataclass(frozen=True)
class Hypothesis:
    name: str
    description: str
    prior: Fraction
    likelihood_by_tool: Dict[str, Fraction]
    complexity_penalty: Fraction
    peirce_thirdness: str
    ontological_level: str


@dataclass
class AbductionTrace:
    best_hypothesis: str
    best_posterior: Fraction
    best_ibe_score: Fraction
    ranked_hypotheses: List[Dict[str, Any]]
    key_supporting: List[str]
    key_contradicting: List[str]
    peirce_narrative: str
    pruned: List[str]
    is_conclusive: bool
    confidence: Fraction
    contradiction_type: Optional[str] = None
    ontological_level: Optional[str] = None


def _technique_hypotheses() -> List[Hypothesis]:
    return [
        Hypothesis(
            name="AUTOMATED_GENERATION",
            description="Contenido generado por IA",
            prior=Fraction(3, 10),
            likelihood_by_tool={
                "GCI": Fraction(92, 100), "DGPI": Fraction(88, 100),
                "COGN_FP": Fraction(82, 100), "STYLO_FP": Fraction(75, 100),
            },
            complexity_penalty=Fraction(1, 10),
            peirce_thirdness="Hábito de producción algorítmica.",
            ontological_level="TECHNIQUE",
        ),
        Hypothesis(
            name="MEMORY_INJECTION",
            description="Código malicioso residente en RAM",
            prior=Fraction(5, 100),
            likelihood_by_tool={
                "MEMORY_FORENSICS": Fraction(92, 100),
                "PERSISTENCE_DETECTOR": Fraction(70, 100),
                "EVENT_LOG": Fraction(65, 100),
            },
            complexity_penalty=Fraction(2, 10),
            peirce_thirdness="Hábito de ejecución volátil: procesos sin imagen en disco.",
            ontological_level="TECHNIQUE",
        ),
        Hypothesis(
            name="REGISTRY_PERSISTENCE",
            description="Mecanismo de persistencia via claves de registro",
            prior=Fraction(8, 100),
            likelihood_by_tool={
                "REGISTRY_RTR": Fraction(90, 100),
                "PERSISTENCE_DETECTOR": Fraction(88, 100),
            },
            complexity_penalty=Fraction(15, 100),
            peirce_thirdness="Hábito de supervivencia post-reboot.",
            ontological_level="TECHNIQUE",
        ),
        Hypothesis(
            name="MFT_TIMESTOMP",
            description="Manipulación de timestamps NTFS",
            prior=Fraction(6, 100),
            likelihood_by_tool={
                "MFT_ANALYZER": Fraction(88, 100),
                "REGISTRY_RTR": Fraction(60, 100),
            },
            complexity_penalty=Fraction(2, 10),
            peirce_thirdness="Hábito de anti-forense: $STANDARD_INFORMATION modificado.",
            ontological_level="TECHNIQUE",
        ),
    ]


def _tactic_hypotheses() -> List[Hypothesis]:
    return [
        Hypothesis(
            name="HUMAN_FORGERY",
            description="Falsificación humana deliberada",
            prior=Fraction(2, 10),
            likelihood_by_tool={
                "CAIE": Fraction(85, 100), "TEMPORAL": Fraction(80, 100),
                "ACP": Fraction(75, 100),
            },
            complexity_penalty=Fraction(3, 10),
            peirce_thirdness="Hábito de falsificación artesanal.",
            ontological_level="TACTIC",
        ),
        Hypothesis(
            name="LATERAL_MOVEMENT",
            description="Movimiento lateral en red",
            prior=Fraction(7, 100),
            likelihood_by_tool={
                "EVENT_LOG": Fraction(85, 100), "NETWORK_FORENSICS": Fraction(82, 100),
                "REGISTRY_RTR": Fraction(60, 100),
            },
            complexity_penalty=Fraction(25, 100),
            peirce_thirdness="Hábito de expansión territorial: credenciales reutilizadas.",
            ontological_level="TACTIC",
        ),
        Hypothesis(
            name="FALSE_FLAG",
            description="Operación de falsa bandera",
            prior=Fraction(1, 10),
            likelihood_by_tool={
                "ADV_ROBUST": Fraction(85, 100), "CAIE": Fraction(88, 100),
            },
            complexity_penalty=Fraction(1, 2),
            peirce_thirdness="Hábito de atribución falsa.",
            ontological_level="TACTIC",
        ),
    ]


def _objective_hypotheses() -> List[Hypothesis]:
    return [
        Hypothesis(
            name="DATA_EXFILTRATION",
            description="Extracción de datos del sistema",
            prior=Fraction(4, 100),
            likelihood_by_tool={
                "NETWORK_FORENSICS": Fraction(90, 100),
                "BROWSER_FORENSICS": Fraction(70, 100),
                "USB_TRACKER": Fraction(65, 100),
            },
            complexity_penalty=Fraction(3, 10),
            peirce_thirdness="Hábito de sustracción: beaconing periódico, DNS tunneling.",
            ontological_level="OBJECTIVE",
        ),
        Hypothesis(
            name="HYBRID_HUMAN_AI",
            description="Humano con asistencia de IA",
            prior=Fraction(25, 100),
            likelihood_by_tool={
                "GCI": Fraction(65, 100), "DGPI": Fraction(55, 100),
            },
            complexity_penalty=Fraction(2, 10),
            peirce_thirdness="Hábito de co-producción.",
            ontological_level="OBJECTIVE",
        ),
        Hypothesis(
            name="LEGITIMATE_HUMAN",
            description="Contenido humano legítimo",
            prior=Fraction(15, 100),
            likelihood_by_tool={
                "GCI": Fraction(10, 100), "DGPI": Fraction(15, 100),
            },
            complexity_penalty=Fraction(1, 20),
            peirce_thirdness="Hábito de producción humana natural.",
            ontological_level="OBJECTIVE",
        ),
    ]


def default_hypotheses() -> List[Hypothesis]:
    return _technique_hypotheses() + _tactic_hypotheses() + _objective_hypotheses()


class AbductiveReasoner:
    def __init__(self, hypotheses: Optional[List[Hypothesis]] = None, neutral_likelihood: Fraction = NEUTRAL):
        self._hypotheses = hypotheses or default_hypotheses()
        self._neutral = neutral_likelihood
        self._states: Dict[str, Dict[str, Any]] = {}
        self._history: List[str] = []
        self._init_states()

    def _init_states(self) -> None:
        total_prior = sum(h.prior for h in self._hypotheses)
        for hyp in self._hypotheses:
            norm = hyp.prior / total_prior if total_prior > 0 else Fraction(1, len(self._hypotheses))
            self._states[hyp.name] = {
                "log_posterior": self._log(norm),
                "supporting": [],
                "contradicting": [],
                "pruned": False,
                "hypothesis": hyp,
            }

    def reason(self, signals: List[SignalOutput]) -> AbductionTrace:
        if len(signals) < MIN_SIGNALS:
            return self._insufficient_trace(len(signals))
        self._init_states()
        self._history = []
        sorted_signals = sorted(signals, key=lambda s: s.confidence, reverse=True)
        for signal in sorted_signals:
            self._update(signal)
            self._history.append(signal.tool_name)
        self._normalize()
        self._prune()
        return self._build_trace()

    def _update(self, signal: SignalOutput) -> None:
        z_frac = Fraction(int(round(signal.z_score * 100)), 100)
        active = z_frac > Fraction(2, 1)
        conf = Fraction(int(round(signal.confidence * 1000)), 1000)
        for name, state in self._states.items():
            if state["pruned"]:
                continue
            hyp = state["hypothesis"]
            p_active_given_h = hyp.likelihood_by_tool.get(signal.tool_name, self._neutral)
            if active:
                likelihood = p_active_given_h
                if likelihood > self._neutral:
                    state["supporting"].append(signal.tool_name)
                else:
                    state["contradicting"].append(signal.tool_name)
            else:
                likelihood = Fraction(1, 1) - p_active_given_h
                if p_active_given_h > self._neutral:
                    state["contradicting"].append(f"~{signal.tool_name}")
            weighted = conf * likelihood + (Fraction(1, 1) - conf) * self._neutral
            weighted = max(weighted, EPS)
            state["log_posterior"] += self._log(weighted)

    def _normalize(self) -> None:
        active = [s for s in self._states.values() if not s["pruned"]]
        if not active:
            return
        log_vals = [s["log_posterior"] for s in active]
        max_log = max(log_vals)
        sum_exp = sum(self._exp(l - max_log) for l in log_vals)
        log_sum = max_log + self._log(sum_exp + EPS)
        for state in active:
            state["log_posterior"] -= log_sum

    def _prune(self) -> None:
        for state in self._states.values():
            if state["pruned"]:
                continue
            posterior = self._exp(state["log_posterior"])
            if posterior < PRUNING_THRESHOLD:
                state["pruned"] = True

    def _build_trace(self) -> AbductionTrace:
        active = [(name, s) for name, s in self._states.items() if not s["pruned"]]
        if not active:
            return self._insufficient_trace(0)
        ranked = sorted(active, key=lambda item: (
            self._exp(item[1]["log_posterior"]) - item[1]["hypothesis"].complexity_penalty
        ), reverse=True)
        best_name, best_state = ranked[0]
        best_posterior = self._exp(best_state["log_posterior"])
        best_ibe = best_posterior - best_state["hypothesis"].complexity_penalty
        is_conclusive = best_posterior >= COLLAPSE_THRESHOLD and len(self._history) >= MIN_SIGNALS
        contradiction_type = self._classify_contradiction(best_state, active)
        narrative = self._build_narrative(
            best_state["hypothesis"], best_state["supporting"][:5],
            best_state["contradicting"][:5], is_conclusive, contradiction_type
        )
        return AbductionTrace(
            best_hypothesis=best_name, best_posterior=best_posterior,
            best_ibe_score=best_ibe, ranked_hypotheses=[
                {"name": name, "posterior": str(self._exp(s["log_posterior"])),
                 "ibe_score": str(self._exp(s["log_posterior"]) - s["hypothesis"].complexity_penalty),
                 "complexity": str(s["hypothesis"].complexity_penalty),
                 "level": s["hypothesis"].ontological_level}
                for name, s in ranked
            ],
            key_supporting=best_state["supporting"][:5],
            key_contradicting=best_state["contradicting"][:5],
            peirce_narrative=narrative, pruned=[name for name, s in self._states.items() if s["pruned"]],
            is_conclusive=is_conclusive,
            confidence=best_posterior if is_conclusive else best_posterior * Fraction(8, 10),
            contradiction_type=contradiction_type,
            ontological_level=best_state["hypothesis"].ontological_level,
        )

    def _classify_contradiction(self, best_state, all_active):
        if len(all_active) < 2:
            return None
        best_posterior = self._exp(best_state["log_posterior"])
        runners_up = [(name, s) for name, s in all_active
                      if name != best_state["hypothesis"].name
                      and self._exp(s["log_posterior"]) > Fraction(1, 10)]
        if not runners_up:
            return None
        best_tools = set(best_state["supporting"])
        temporal_tools = {"TEMPORAL", "CAIE"}
        adversarial_tools = {"ADV_ROBUST", "GCI", "DGPI"}
        operational_tools = {"ACP", "ROI", "CLI"}
        has_temporal = has_adversarial = has_operational = False
        for name, state in runners_up:
            runner_tools = set(state["supporting"])
            shared = best_tools & runner_tools
            if shared:
                if any(t in temporal_tools for t in shared):
                    has_temporal = True
                if any(t in adversarial_tools for t in shared):
                    has_adversarial = True
                if any(t in operational_tools for t in shared):
                    has_operational = True
        if has_adversarial and has_temporal:
            return "ADVERSARIAL"
        elif has_temporal:
            return "TEMPORAL"
        elif has_operational:
            return "OPERATIONAL"
        else:
            return "EVIDENCIAL"

    def _build_narrative(self, hyp, supporting, contradicting, conclusive, contradiction_type=None):
        firstness = f"[FIRSTNESS] Señales activas: {', '.join(supporting) if supporting else 'ninguna'}."
        secondness = f"[SECONDNESS] Posterior para '{hyp.name}': {float(self._exp(self._states[hyp.name]['log_posterior'])):.1%}."
        thirdness = f"[THIRDNESS] {'Conclusión firme' if conclusive else 'Hipótesis más plausible'}: {hyp.peirce_thirdness}"
        level = f"\n[ONTOLOGICAL_LEVEL] {hyp.ontological_level}: este veredicto opera a nivel de {hyp.ontological_level.lower()}."
        contra = ""
        if contradicting:
            contra = f"\n[CONTRADICCIÓN] Señales en contra: {', '.join(contradicting[:3])}."
        if contradiction_type:
            contra += f"\n[TIPO] Contradicción {contradiction_type.lower()}: patrones mutuamente incompatibles activos."
        return f"{firstness}\n{secondness}\n{thirdness}{level}{contra}"

    def _insufficient_trace(self, n: int) -> AbductionTrace:
        return AbductionTrace(
            best_hypothesis="UNDETERMINED", best_posterior=Fraction(0, 1),
            best_ibe_score=Fraction(0, 1), ranked_hypotheses=[],
            key_supporting=[], key_contradicting=[],
            peirce_narrative=f"[FIRSTNESS] Señales insuficientes ({n}/{MIN_SIGNALS}).",
            pruned=[], is_conclusive=False, confidence=Fraction(0, 1),
            contradiction_type=None, ontological_level=None,
        )

    @staticmethod
    def _log(x: Fraction) -> Fraction:
        # FIX P0: NEG_INF en lugar de -10**6
        if x <= 0:
            return NEG_INF
        k = 0
        y = x
        while y >= 2:
            y = y / 2
            k += 1
        while y < 1:
            y = y * 2
            k -= 1
        u = y - 1
        result = Fraction(0, 1)
        u_pow = Fraction(1, 1)
        for n in range(1, 21):
            u_pow = u_pow * u
            term = u_pow / n
            result += term if n % 2 == 1 else -term
        return result + k * LN2

    @staticmethod
    def _exp(x: Fraction) -> Fraction:
        # FIX P0: Clamping para evitar overflow en casos extremos
        if x == 0:
            return Fraction(1, 1)
        # Si x es muy negativo, retornar 0 directamente
        if x < NEG_INF / 2:
            return Fraction(0, 1)
        k = 0
        scale = x
        while abs(scale) > Fraction(1, 2):
            scale = scale / 2
            k += 1
        result = Fraction(1, 1)
        term = Fraction(1, 1)
        EPS = Fraction(1, 10**12)
        for n in range(1, 51):
            term = term * scale / n
            result += term
            if abs(term) < EPS:
                break
        for _ in range(k):
            result = result * result
        return result
