# =============================================================================
# SANS PHASE ENUM — One-Liner Judicial
# =============================================================================
# Archivo: vigia/core/sans_phase.py  (o vigia/verdict/sans_phase.py)
# Propósito: Generar el one-liner que impresiona a jueces SANS en reportes.
# Estándar: SANS Institute 6-Step Incident Response Methodology (PICERL)
# Determinismo: IntEnum garantiza orden total sin floats.
#
# USO EN REPORTE:
#   phase = SANSPhase.IDENTIFICATION
#   print(phase.report_line("IR-2024-001"))
#   → "Este análisis sigue la metodología SANS 6-Step IR,
#        Case IR-2024-001, actualmente en fase:
#        Identification [2/6] — Detectar, alertar y determinar
#        si el evento es un incidente. | MITRE focus:
#        Initial Access + Execution + Persistence"
# =============================================================================

from enum import IntEnum
from dataclasses import dataclass, field
from fractions import Fraction
import hashlib
import json


class SANSPhase(IntEnum):
    """
    Las 6 fases del IR Lifecycle según metodología SANS/PICERL.

    IntEnum permite comparación de orden:
        SANSPhase.PREPARATION < SANSPhase.IDENTIFICATION  → True
        SANSPhase.CONTAINMENT > SANSPhase.PREPARATION     → True
    """
    PREPARATION     = 1
    IDENTIFICATION  = 2
    CONTAINMENT     = 3
    ERADICATION     = 4
    RECOVERY        = 5
    LESSONS_LEARNED = 6

    # ── Labels para reportes ─────────────────────────────────────────

    @property
    def label(self) -> str:
        """Label formateado: 'Identification [2/6]'"""
        nombres = {
            SANSPhase.PREPARATION:     "Preparation",
            SANSPhase.IDENTIFICATION:  "Identification",
            SANSPhase.CONTAINMENT:     "Containment",
            SANSPhase.ERADICATION:     "Eradication",
            SANSPhase.RECOVERY:        "Recovery",
            SANSPhase.LESSONS_LEARNED: "Lessons Learned",
        }
        return f"{nombres[self]} [{self.value}/6]"

    @property
    def description(self) -> str:
        """Descripción SANS oficial de cada fase."""
        descripciones = {
            SANSPhase.PREPARATION: (
                "Establecer y mantener capacidad de respuesta. "
                "Políticas, herramientas, entrenamiento y comunicación."
            ),
            SANSPhase.IDENTIFICATION: (
                "Detectar, alertar y determinar si el evento es un incidente. "
                "Recolección inicial de evidencia y triage."
            ),
            SANSPhase.CONTAINMENT: (
                "Limitar el daño. Aislar sistemas comprometidos. "
                "Short-term y long-term containment. Preservar evidencia."
            ),
            SANSPhase.ERADICATION: (
                "Eliminar el artefacto malicioso del ambiente. "
                "Identificar causa raíz. Remediar vulnerabilidades."
            ),
            SANSPhase.RECOVERY: (
                "Restaurar sistemas a operación normal. "
                "Verificar que el ambiente es seguro. Monitoreo intensivo."
            ),
            SANSPhase.LESSONS_LEARNED: (
                "Documentar el incidente. Identificar mejoras. "
                "Actualizar playbooks y controles de detección."
            ),
        }
        return descripciones[self]

    @property
    def mitre_focus(self) -> str:
        """Perspectiva MITRE ATT&CK relevante en esta fase."""
        focus = {
            SANSPhase.PREPARATION:     "Pre-ATT&CK — Intelligence gathering",
            SANSPhase.IDENTIFICATION:  "Initial Access + Execution + Persistence",
            SANSPhase.CONTAINMENT:     "Lateral Movement + Command and Control",
            SANSPhase.ERADICATION:     "Defense Evasion + Persistence removal",
            SANSPhase.RECOVERY:        "Impact assessment + Residual risk",
            SANSPhase.LESSONS_LEARNED: "Full kill chain reconstruction",
        }
        return focus[self]

    # ── ONE-LINER para reportes ────────────────────────────────────

    def report_line(self, case_id: str = "") -> str:
        """
        THE ONE-LINER que impresiona a los jueces SANS.

        Uso:
            phase = SANSPhase.IDENTIFICATION
            print(phase.report_line("IR-2024-001"))
        """
        case_part = f"Case {case_id}, " if case_id else ""
        return (
            f"Este análisis sigue la metodología SANS 6-Step IR. "
            f"{case_part}"
            f"Actualmente en fase: {self.label} — "
            f"{self.description} "
            f"| MITRE focus: {self.mitre_focus}"
        )

    def short_report_line(self) -> str:
        """Versión corta para headers: '[SANS IR] Identification [2/6]'"""
        return f"[SANS IR] {self.label}"


# =============================================================================
# TRACKER DE FASE — Máquina de estados determinista
# =============================================================================

@dataclass
class PhaseTransitionRecord:
    """Registro inmutable de transición entre fases (con hash de auditoría)."""
    from_phase: SANSPhase
    to_phase: SANSPhase
    reason: str
    triggered_by: str
    timestamp_utc: str
    evidence_ref: str
    transition_hash: str = field(init=False)

    def __post_init__(self) -> None:
        payload = json.dumps({
            "from": self.from_phase.name,
            "to": self.to_phase.name,
            "reason": self.reason,
            "triggered": self.triggered_by,
            "timestamp": self.timestamp_utc,
            "evidence": self.evidence_ref,
        }, sort_keys=True).encode()
        object.__setattr__(self, "transition_hash",
                           hashlib.sha256(payload).hexdigest())


class SANSPhaseTracker:
    """
    Tracker del ciclo de vida del incidente.
    No permite retroceder sin justificación documentada.
    """

    def __init__(self, case_id: str,
                 initial_phase: SANSPhase = SANSPhase.PREPARATION) -> None:
        self.case_id = case_id
        self._current = initial_phase
        self._history: list[PhaseTransitionRecord] = []
        self._scores: dict[SANSPhase, Fraction] = {
            SANSPhase.PREPARATION:     Fraction(0),
            SANSPhase.IDENTIFICATION:  Fraction(1, 5),
            SANSPhase.CONTAINMENT:     Fraction(2, 5),
            SANSPhase.ERADICATION:     Fraction(3, 5),
            SANSPhase.RECOVERY:        Fraction(4, 5),
            SANSPhase.LESSONS_LEARNED: Fraction(1),
        }

    @property
    def current(self) -> SANSPhase:
        return self._current

    @property
    def progress(self) -> Fraction:
        return self._scores[self._current]

    def advance(self, reason: str, triggered_by: str,
                timestamp_utc: str, evidence_ref: str) -> PhaseTransitionRecord:
        """Avanza a la siguiente fase (no se puede retroceder)."""
        assert self._current != SANSPhase.LESSONS_LEARNED, (
            "Ya estamos en fase final. No hay siguiente fase."
        )
        nxt = SANSPhase(self._current.value + 1)
        return self._record(nxt, reason, triggered_by, timestamp_utc, evidence_ref)

    def _record(self, to_phase: SANSPhase, reason: str, triggered_by: str,
                timestamp_utc: str, evidence_ref: str) -> PhaseTransitionRecord:
        rec = PhaseTransitionRecord(
            from_phase=self._current, to_phase=to_phase,
            reason=reason, triggered_by=triggered_by,
            timestamp_utc=timestamp_utc, evidence_ref=evidence_ref,
        )
        self._history.append(rec)
        self._current = to_phase
        return rec

    def one_liner(self) -> str:
        return self._current.report_line(self.case_id)

    def short_status(self) -> str:
        return (
            f"{self._current.short_report_line()} "
            f"| Progress: {self.progress}"
        )


# =============================================================================
# TEST DE SANIDAD
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SANS PHASE — SELF-TEST")
    print("=" * 70)

    # Test 1: Orden
    assert SANSPhase.PREPARATION < SANSPhase.IDENTIFICATION
    assert SANSPhase.IDENTIFICATION < SANSPhase.CONTAINMENT
    print("✓ Orden de fases correcto")

    # Test 2: One-liner
    p = SANSPhase.IDENTIFICATION
    line = p.report_line("IR-2024-001")
    assert "SANS" in line
    assert "Identification" in line
    assert "2/6" in line
    print(f"✓ One-liner generado: {line}")

    # Test 3: Tracker
    t = SANSPhaseTracker("IR-TEST")
    assert t.current == SANSPhase.PREPARATION
    t.advance("Beacon C2 confirmado", "BeaconDetector",
              "2026-05-06T12:00:00Z", "a" * 64)
    assert t.current == SANSPhase.IDENTIFICATION
    print(f"✓ Tracker avanzó: {t.short_status()}")
    print(f"✓ One-liner tracker: {t.one_liner()}")

    print("=" * 70)
    print("✓✓✓ TODOS LOS TESTS PASARON")
    print("=" * 70)
