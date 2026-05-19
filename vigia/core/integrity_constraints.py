# vigia/core/integrity_constraints.py
"""
Rastreador de Supuestos e Integridad — VIGÍA
============================================

ATMS-Inspired Assumption Tracking para análisis forense determinista.

ORIGEN:
    Módulo propuesto por el debate ChatGPT/Claude (colectivo VIGÍA,
    2026-05-18) e implementado por Kimi (Moonshot AI).
    Integrado con ajustes de seguridad por Claude (Anthropic).

PROBLEMA QUE RESUELVE:
    VIGÍA detecta colapsos temporales (TEMPORAL_PARADOX, TEMPORAL_CAUSALITY_
    VIOLATION) pero no propaga la invalidación a hipótesis downstream que
    dependían del supuesto colapsado.

    Ejemplo forense:
        H_DE_002 (timestamp manipulation) depende del supuesto
        "timestamps_comparable". Si CAIE detecta TEMPORAL_CAUSALITY_VIOLATION,
        ese supuesto colapsa. Sin este módulo, H_DE_002 continúa activa
        con su score original — produciendo un falso positivo silencioso.
        Con este módulo, H_DE_002 queda invalidada y el bundle lo documenta.

FILOSOFÍA DAUBERT:
    El AssumptionTracker produce trazabilidad completa: qué constraints
    se evaluaron, cuáles se violaron, y qué hipótesis quedaron invalidadas.
    Eso es exactamente lo que un perito necesita explicar en el estrado:
    "Mi conclusión dependía del supuesto X; CAIE detectó que X era falso;
    por lo tanto la conclusión se invalida automáticamente."

INVARIANTES DE SEGURIDAD:
    - IntegrityConstraint es frozen=True — inmutable después de registro.
    - La mutación de estado ocurre via reemplazo del objeto, no modificación.
    - condition_fn debe ser pura (sin efectos secundarios). No se verifica
      automáticamente — responsabilidad del llamador.
    - to_bundle() retorna un dict JSON-serializable (solo tipos primitivos).
      No incluye callables ni objetos con referencias circulares.

DETERMINISMO:
    La evaluación de constraints es determinista dado el mismo conjunto de
    artifacts. El orden de evaluación sigue el orden de registro.
    evaluate_all() es idempotente si se llama múltiples veces con los mismos
    artifacts — cada llamada reemplaza los resultados anteriores.

LIMITACIONES CONOCIDAS (scope v1.0):
    - No implementa propagación de invalidación en profundidad > 1
      (A invalida B, B invalida C no se propaga automáticamente).
      Roadmap v2.0: grafo de dependencia completo con BFS/DFS.
    - condition_fn recibe la lista de artifacts sin filtrado previo.
      El llamador es responsable de pasar artifacts válidos.
    - No hay persistencia entre ejecuciones — el tracker es stateful
      solo dentro de una ejecución del pipeline.

Licencia: Apache 2.0
Repositorio: https://github.com/annatchijova/vigia-intent-analysis
Autora principal: Annia Tchijova
Diseño e implementación base: Kimi (Moonshot AI)
Ajustes de seguridad e integración: Claude (Anthropic)
Versión: 1.1 — 19 de mayo de 2026
Audiencia: SANS FIND EVIL Hackathon 2026 / SIFT Workstation

HISTORIAL DE PATCHES:
    B7     : condition_fn — helper _get_evidence_type soporta dicts y Artifact
    B8     : FRACTURE_ASSUMPTION_MAP — LOW_COUNT_ANOMALY agregado,
             LOG_VS_MEMORY corregido (no invalida memory_dump_unmodified),
             fractures de CAIE faltantes agregadas al mapa
    B9     : evaluate_all — condition_fn recibe tuple inmutable, no lista viva
    Fix P2 : register — validación de supuestos desconocidos con warning

LIMITACIONES CONOCIDAS:
    - Profundidad de propagación de invalidación: 1.
      A invalida B, B invalida C no se propaga automáticamente.
      Roadmap v2.0: grafo de dependencia completo con BFS/DFS.
    - condition_fn se asume pura (sin efectos secundarios). No se verifica
      automáticamente. Responsabilidad del llamador.
    - LOW_COUNT_ANOMALY en FRACTURE_ASSUMPTION_MAP: pendiente confirmar
      que este fracture_type existe en CAIE v2.0. Si no existe, este entry
      es defensivo pero nunca se activará. Ver integrity_constraints.py issue #1.
    - No hay persistencia entre ejecuciones. El tracker es stateful solo
      dentro de una ejecución del pipeline.
    - evaluate_all() es idempotente si se llama múltiples veces con los
      mismos artifacts, pero no si se llama DESPUÉS de invalidate_assumption().
      El orden correcto es: evaluate_all() → invalidate_assumption().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constraint inmutable
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IntegrityConstraint:
    """
    Constraint de integridad forense sobre una hipótesis abductiva.

    Attributes:
        constraint_id         : identificador único, formato "IC_<descripción>"
        hypothesis_id         : hipótesis que depende de este constraint
                                (debe coincidir con un ID en AbductiveIntentEngine)
        description           : descripción humano-legible para el bundle
        condition_fn          : función pura que evalúa la constraint sobre
                                la lista de artifacts. Retorna True=SATISFIED,
                                False=VIOLATED. Debe ser libre de efectos
                                secundarios y no lanzar excepciones (usar
                                try/except interno si es necesario).
        required_assumptions  : supuestos que deben sostenerse para que la
                                constraint sea evaluable. Si un supuesto se
                                invalida, la hipótesis queda automáticamente
                                en ASSUMPTION_COLLAPSED.
        status                : estado de evaluación. Valores posibles:
                                NOT_EVALUATED, SATISFIED, VIOLATED,
                                NOT_APPLICABLE, ASSUMPTION_COLLAPSED
        evidence              : descripción del resultado de evaluación
                                (para el bundle forense)
    """
    constraint_id: str
    hypothesis_id: str
    description: str
    condition_fn: Callable[[list], bool]
    required_assumptions: tuple = ()
    status: str = "NOT_EVALUATED"
    evidence: Optional[str] = None

    def with_status(self, status: str, evidence: str) -> "IntegrityConstraint":
        """Retorna una nueva instancia con status y evidence actualizados."""
        return IntegrityConstraint(
            constraint_id=self.constraint_id,
            hypothesis_id=self.hypothesis_id,
            description=self.description,
            condition_fn=self.condition_fn,
            required_assumptions=self.required_assumptions,
            status=status,
            evidence=evidence,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización JSON-safe (excluye condition_fn)."""
        return {
            "constraint_id":        self.constraint_id,
            "hypothesis_id":        self.hypothesis_id,
            "description":          self.description,
            "required_assumptions": list(self.required_assumptions),
            "status":               self.status,
            "evidence":             self.evidence,
        }


# ---------------------------------------------------------------------------
# Tracker de supuestos
# ---------------------------------------------------------------------------

class AssumptionTracker:
    """
    Rastrea dependencias entre supuestos e hipótesis abductivas.
    Cuando un supuesto colapsa (por fractura CAIE o evidencia externa),
    propaga la invalidación a todas las hipótesis que dependen de él.

    Uso típico desde ebs_v1.py:

        tracker = AssumptionTracker()
        tracker.register(IntegrityConstraint(...))
        tracker.evaluate_all(artifacts)

        # Cuando CAIE detecta fractura temporal:
        if any(f.fracture_type == "TEMPORAL_CAUSALITY_VIOLATION" for f in fractures):
            tracker.invalidate_assumption(
                "timestamps_comparable",
                invalidated_by="TEMPORAL_CAUSALITY_VIOLATION"
            )

        bundle["integrity_constraints"] = tracker.to_bundle()
    """

    # Supuestos implícitos del sistema — documentados como ciudadanos de primera clase
    # (propuesta de formalización del debate ChatGPT/Claude, 2026-05-18)
    SYSTEM_ASSUMPTIONS = frozenset({
        "email_collection_complete",
        "timestamps_comparable",
        "network_logs_complete",
        "memory_dump_unmodified",
        "filesystem_unmodified_post_incident",
        "registry_snapshot_contemporaneous",
        "chain_of_custody_unbroken",
        # Agregados con B8 fix (2026-05-18)
        "sensor_observability_uncompromised",
        "artifacts_sufficient_for_analysis",
    })

    def __init__(self) -> None:
        self._constraints: List[IntegrityConstraint] = []
        # assumption → lista de hypothesis_ids que dependen de ella
        self._assumption_graph: Dict[str, List[str]] = {}
        # registro de invalidaciones con trazabilidad completa
        self._invalidated: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Registro
    # ------------------------------------------------------------------

    def register(self, constraint: IntegrityConstraint) -> None:
        """
        Registra una constraint. El orden de registro determina el orden
        de evaluación en evaluate_all().

        Raises:
            ValueError: si constraint_id ya está registrado (duplicado).

        Warning (no error):
            Si required_assumptions contiene supuestos no presentes en
            SYSTEM_ASSUMPTIONS, se emite un warning de logging. Esto permite
            extensión futura sin bloquear, pero detecta typos en desarrollo.
        """
        existing_ids = {c.constraint_id for c in self._constraints}
        if constraint.constraint_id in existing_ids:
            raise ValueError(
                f"AssumptionTracker: constraint_id '{constraint.constraint_id}' "
                f"ya registrado. Los IDs deben ser únicos."
            )
        # Fix P2 (Annia Tchijova, 2026-05-18):
        # Validar que los supuestos declarados sean conocidos.
        # Warning, no error — permite extender SYSTEM_ASSUMPTIONS sin romper código.
        unknown_assumptions = [
            a for a in constraint.required_assumptions
            if a not in self.SYSTEM_ASSUMPTIONS
        ]
        if unknown_assumptions:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "AssumptionTracker: constraint '%s' declara supuestos no registrados "
                "en SYSTEM_ASSUMPTIONS: %s. Posible typo. "
                "Si es supuesto nuevo, agregarlo a SYSTEM_ASSUMPTIONS.",
                constraint.constraint_id,
                unknown_assumptions,
            )
        self._constraints.append(constraint)
        for assumption in constraint.required_assumptions:
            self._assumption_graph.setdefault(assumption, []).append(
                constraint.hypothesis_id
            )

    # ------------------------------------------------------------------
    # Evaluación
    # ------------------------------------------------------------------

    def evaluate_all(self, artifacts: list) -> None:
        """
        Evalúa todas las constraints registradas contra la lista de artifacts.

        Una constraint con required_assumptions que ya fueron invalidados
        recibe status ASSUMPTION_COLLAPSED — no se evalúa su condition_fn.

        Esta operación es idempotente: llamar múltiples veces con los mismos
        artifacts produce el mismo resultado.

        B9 fix (auditoría Doc4/Doc5, 2026-05-18):
        condition_fn recibe tuple(artifacts) en lugar de la lista viva.
        Una condition_fn buggeada o maliciosa no puede mutar los artifacts
        que verán los pasos posteriores del pipeline.
        """
        collapsed_assumptions = {
            rec["assumption"] for rec in self._invalidated
        }
        # Snapshot inmutable — condition_fn no puede mutar la lista original
        artifacts_snapshot = tuple(artifacts)

        updated: List[IntegrityConstraint] = []
        for c in self._constraints:
            # Si algún supuesto requerido ya colapsó, no evaluar
            collapsed = [
                a for a in c.required_assumptions
                if a in collapsed_assumptions
            ]
            if collapsed:
                updated.append(c.with_status(
                    "ASSUMPTION_COLLAPSED",
                    f"Supuestos colapsados: {collapsed}",
                ))
                continue

            # Evaluar condition_fn de forma segura sobre el snapshot inmutable
            try:
                satisfied = c.condition_fn(artifacts_snapshot)
                if satisfied:
                    updated.append(c.with_status("SATISFIED", "condition_met"))
                else:
                    updated.append(c.with_status("VIOLATED", "condition_failed"))
            except Exception as exc:
                updated.append(c.with_status(
                    "NOT_APPLICABLE",
                    f"evaluation_error: {type(exc).__name__}: {exc}",
                ))

        self._constraints = updated

    # ------------------------------------------------------------------
    # Invalidación de supuestos
    # ------------------------------------------------------------------

    def invalidate_assumption(
        self,
        assumption: str,
        invalidated_by: str,
    ) -> List[Dict[str, Any]]:
        """
        Invalida un supuesto y registra las hipótesis downstream afectadas.

        Args:
            assumption     : nombre del supuesto que colapsa
            invalidated_by : descripción de la causa (ej: fracture_type de CAIE)

        Returns:
            Lista completa de registros de invalidación hasta el momento.

        Daubert note:
            Cada invalidación genera un registro con timestamp-like ordering
            (posición en la lista), causa, y efecto. Este registro es parte
            del bundle forense — el perito puede trazar exactamente por qué
            una hipótesis quedó invalidada.
        """
        affected = self._assumption_graph.get(assumption, [])
        record: Dict[str, Any] = {
            "assumption":                       assumption,
            "invalidated_by":                   invalidated_by,
            "downstream_hypotheses_affected":   affected,
            "propagation_depth":                len(affected),
            "invalidation_index":               len(self._invalidated),
        }
        self._invalidated.append(record)

        # Marcar constraints afectadas como ASSUMPTION_COLLAPSED
        updated: List[IntegrityConstraint] = []
        for c in self._constraints:
            if assumption in c.required_assumptions and c.status != "ASSUMPTION_COLLAPSED":
                updated.append(c.with_status(
                    "ASSUMPTION_COLLAPSED",
                    f"Supuesto '{assumption}' invalidado por '{invalidated_by}'",
                ))
            else:
                updated.append(c)
        self._constraints = updated

        return self._invalidated

    # ------------------------------------------------------------------
    # Serialización para el bundle
    # ------------------------------------------------------------------

    def to_bundle(self) -> Dict[str, Any]:
        """
        Serializa el estado completo del tracker a dict JSON-serializable.
        Apto para embeber en ForensicBundle como sección de auditoría.

        El resultado incluye:
        - Todas las constraints evaluadas con su status final
        - Todos los supuestos invalidados con trazabilidad de causa y efecto
        - Contadores de resumen para el reporte ejecutivo
        """
        violated = [c for c in self._constraints if c.status == "VIOLATED"]
        collapsed = [c for c in self._constraints if c.status == "ASSUMPTION_COLLAPSED"]
        satisfied = [c for c in self._constraints if c.status == "SATISFIED"]

        return {
            "integrity_constraints_evaluated": [c.to_dict() for c in self._constraints],
            "assumptions_invalidated":         self._invalidated,
            "summary": {
                "total_constraints":    len(self._constraints),
                "satisfied":            len(satisfied),
                "violated":             len(violated),
                "assumption_collapsed": len(collapsed),
                "not_evaluated":        sum(
                    1 for c in self._constraints if c.status == "NOT_EVALUATED"
                ),
                "not_applicable":       sum(
                    1 for c in self._constraints if c.status == "NOT_APPLICABLE"
                ),
            },
            "daubert_note": (
                "Cada constraint documenta qué supuesto requería, "
                "si ese supuesto se sostuvo, y qué hipótesis quedó invalidada. "
                "Trazabilidad completa para declaración pericial."
            ),
        }

    # ------------------------------------------------------------------
    # Constraints canónicos del sistema
    # ------------------------------------------------------------------

    @classmethod
    def build_default(cls) -> "AssumptionTracker":
        """
        Retorna un tracker pre-cargado con los constraints implícitos
        del sistema VIGÍA, formalizados como ciudadanos de primera clase.

        Estos constraints estaban dispersos en el código como precondiciones
        implícitas de las hipótesis abductivas. Este método los hace
        explícitos y auditables.

        Referencia: propuesta de formalización del debate ChatGPT/Claude
        (colectivo VIGÍA, 2026-05-18).
        """
        tracker = cls()

        def _get_evidence_type(a) -> Optional[str]:
            """Helper que soporta tanto dicts (JSON) como objetos Artifact."""
            if isinstance(a, dict):
                return a.get("evidence_type")
            return getattr(a, "evidence_type", None)

        tracker.register(IntegrityConstraint(
            constraint_id="IC_phishing_requires_email",
            hypothesis_id="H_IA_001",
            description="La hipótesis de phishing requiere al menos un artefacto de tipo email_header.",
            # B7 fix (2026-05-18): getattr sobre dict siempre retorna None.
            # Usar helper que soporta tanto dicts (JSON pipeline) como objetos Artifact.
            condition_fn=lambda arts: any(
                _get_evidence_type(a) == "email_header" for a in arts
            ),
            required_assumptions=("email_collection_complete",),
        ))

        tracker.register(IntegrityConstraint(
            constraint_id="IC_timestamp_comparability",
            hypothesis_id="H_DE_002",
            description=(
                "La hipótesis de manipulación de timestamps requiere que los "
                "timestamps sean comparables (misma zona horaria, mismo formato, "
                "sin gaps de recolección). Este supuesto colapsa ante "
                "TEMPORAL_CAUSALITY_VIOLATION detectado por CAIE."
            ),
            condition_fn=lambda arts: True,  # La condición real viene de CAIE
            required_assumptions=("timestamps_comparable",),
        ))

        tracker.register(IntegrityConstraint(
            constraint_id="IC_lateral_movement_requires_network",
            hypothesis_id="H_LM_001",
            description="Lateral movement requiere logs de red completos para correlación.",
            condition_fn=lambda arts: any(
                _get_evidence_type(a) == "network_artifact" for a in arts
            ),
            required_assumptions=("network_logs_complete",),
        ))

        tracker.register(IntegrityConstraint(
            constraint_id="IC_memory_injection_requires_clean_dump",
            hypothesis_id="H_PE_001",
            description=(
                "La hipótesis de inyección de proceso requiere un dump de memoria "
                "no modificado post-captura. Chain of custody del dump es precondición."
            ),
            condition_fn=lambda arts: True,  # Delegado a chain_of_custody.py
            required_assumptions=("memory_dump_unmodified", "chain_of_custody_unbroken"),
        ))

        return tracker


# ---------------------------------------------------------------------------
# Integración CAIE — helper para ebs_v1.py
# ---------------------------------------------------------------------------

# Fracture types que invalidan supuestos del sistema
# Mapa: fracture_type → lista de supuestos que colapsan
#
# B8 fix (auditoría Doc5/Doc7, 2026-05-18):
# 1. LOW_COUNT_ANOMALY (Regla 5a de CAIE) estaba ausente — el tracker era ciego
#    ante ataques de baja densidad de artefactos. Agregado con supuesto nuevo.
# 2. LOG_VS_MEMORY: sobre-invalidación corregida. Este fracture significa que
#    los logs afirman algo que la memoria no corrobora → los logs son sospechosos,
#    NO el dump de memoria. memory_dump_unmodified removido de este entry.
# 3. Agregadas fractures de CAIE que estaban ausentes del mapa.
#
# NOTA sobre SYSTEM_ASSUMPTIONS: los nuevos supuestos introducidos aquí
# ("sensor_observability_uncompromised", "artifacts_sufficient_for_analysis")
# deben agregarse a AssumptionTracker.SYSTEM_ASSUMPTIONS para evitar warnings.
FRACTURE_ASSUMPTION_MAP: Dict[str, List[str]] = {
    # Temporales
    "TEMPORAL_CAUSALITY_VIOLATION":  ["timestamps_comparable"],
    "TIMESTAMP_PRECISION_ANOMALY":   ["timestamps_comparable"],
    # Integridad de logs vs. memoria
    "LOG_VS_MEMORY":                 ["network_logs_complete"],
    # Nota B8: memory_dump_unmodified removido — LOG_VS_MEMORY indica logs falsos,
    # no dump corrupto. El dump puede ser la única fuente verdadera.
    "NETWORK_VS_HOST":               ["network_logs_complete"],
    # Cadena de custodia
    "FALSE_FLAG_PATTERN":            ["chain_of_custody_unbroken"],
    "VERDICT_CONFLICT":              ["chain_of_custody_unbroken"],
    "DOCUMENT_FORGERY":              ["chain_of_custody_unbroken"],
    "METADATA_CONCEALMENT":          ["chain_of_custody_unbroken"],
    # Filesystem / MFT
    "MFT_ENTRY_ANOMALY":             ["filesystem_unmodified_post_incident"],
    "USN_JOURNAL_GAP":               ["filesystem_unmodified_post_incident"],
    # Narrativa y evidencia plantada
    "NARRATIVE_POISONING_DETECTED":  ["chain_of_custody_unbroken"],
    # Regla 5a CAIE: baja densidad de artefactos destruye confianza del sensor
    "LOW_COUNT_ANOMALY":             [
        "sensor_observability_uncompromised",
        "chain_of_custody_unbroken",
    ],
}


def apply_caie_fractures(
    tracker: AssumptionTracker,
    caie_fractures: list,
) -> None:
    """
    Helper para ebs_v1.py. Recibe la lista de fractures de CAIE y
    propaga las invalidaciones correspondientes al tracker.

    Uso:
        from vigia.core.integrity_constraints import (
            AssumptionTracker, apply_caie_fractures
        )
        tracker = AssumptionTracker.build_default()
        tracker.evaluate_all(artifacts)
        apply_caie_fractures(tracker, caie_fractures)
        bundle["integrity_constraints"] = tracker.to_bundle()
    """
    seen: set = set()
    for fracture in caie_fractures:
        ft = getattr(fracture, "fracture_type", None) or fracture.get("fracture_type")
        if ft not in FRACTURE_ASSUMPTION_MAP:
            continue
        for assumption in FRACTURE_ASSUMPTION_MAP[ft]:
            key = (assumption, ft)
            if key in seen:
                continue
            seen.add(key)
            tracker.invalidate_assumption(assumption, invalidated_by=ft)
