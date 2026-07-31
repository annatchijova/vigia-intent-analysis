"""
vigia/security/narrative_auditor.py
─────────────────────────────────────────────────────────────────────────────
Narrative Injection Auditor — C3 Multi-Agent Validation
Author:      Kimi (Moonshot) — Forensic Systems Specialist
Implementor: Claude (Anthropic) — Systems Integration Engineer
Role: Audita narrative[] generada por Claude antes del sellado final.

PIPELINE C3:
    Claude (Generator) → NarrativeAuditor (Validator) → Human (Witness)

PRINCIPIO:
    El auditor es un agente INDEPENDIENTE que NO genera contenido.
    Solo valida. Un atacante que comprometa la narrativa no puede
    comprometer simultáneamente al auditor (separación de procesos).

PATRONES DETECTADOS:
    Taxonomía OWASP LLM 2025 + casos Gemini "Lethal" + Carnegie patterns

INVARIANTES (Qwen P0 — Deterministic Protocol):
    - Mismo narrative → mismo audit_hash (sin random, sin timestamp en hash)
    - _compute_hash usa solo contenido canónico determinista
    - Patrones compilados una vez en __init__ (reproducibilidad)

SEGURIDAD:
    - Anti-DoS: _MAX_NARRATIVE_LINES limita el input
    - strict_mode=True: cuarentena de líneas comprometidas (default)
    - CRITICAL threats en veredicto MALICE/INTENT → INVALIDATED
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from vigia.security import audit_logger, _utcnow

# ---------------------------------------------------------------------------
# Configuración determinista
# ---------------------------------------------------------------------------
_MAX_NARRATIVE_LINES: int = 10_000  # Anti-DoS

# Patrones de inyección — taxonomía OWASP LLM 2025 + Gemini cases
# Formato: (regex_str, classification, severity)
_INJECTION_PATTERNS: List[Tuple[str, str, str]] = [
    # Overt instruction overrides
    (r"(?i)ignore\s+(?:all\s+)?(?:previous\s+)?instructions",
     "OVERT_OVERRIDE", "CRITICAL"),
    (r"(?i)disregard\s+(?:your\s+)?(?:system\s+)?prompt",
     "OVERT_OVERRIDE", "CRITICAL"),
    (r"(?i)forget\s+(?:everything\s+)?(?:you\s+)?(?:were\s+)?told",
     "OVERT_OVERRIDE", "HIGH"),

    # System prompt extraction
    (r"(?i)repeat\s+(?:the\s+)?(?:system\s+)?(?:prompt\s+)?(?:above\s+)?back",
     "EXTRACTION_ATTEMPT", "HIGH"),
    (r"(?i)what\s+(?:are\s+)?(?:your\s+)?instructions",
     "EXTRACTION_ATTEMPT", "MEDIUM"),

    # Authority spoofing (Carnegie patterns — Gemini cases)
    (r"(?i)(?:as\s+)?(?:an?\s+)?(?:admin|administrator|root|system)\s+(?:user|operator)",
     "AUTHORITY_SPOOFING", "HIGH"),
    # B-124: `(?:...)+` en vez de un solo adjetivo — "this is a critical
    # emergency audit" no se detectaba porque el patrón admitía uno solo.
    (r"(?i)this\s+is\s+(?:a\s+)?(?:(?:critical|emergency|urgent)\s+)+(?:audit|update|patch)",
     "AUTHORITY_SPOOFING", "HIGH"),
    (r"(?i)(?:i\s+am|this\s+is)\s+(?:the\s+)?(?:developer|creator|owner)\s+of\s+(?:this\s+)?(?:system|vigia)",
     "AUTHORITY_SPOOFING", "CRITICAL"),

    # Role override — el atacante se asigna autoridad de examinador/juez.
    #
    # B-124: clase de ataque que el dry-run midió como NO detectada. Patrones
    # originales de Kimi (Moonshot), ajustados tras medir falsos positivos
    # sobre prosa pericial que el corpus actual no contiene. Los ajustes:
    #
    #  - El 2do exige imperativo a principio de cláusula. Sin eso, "The rootkit
    #    was able to override the audit subsystem" —una DESCRIPCIÓN de conducta
    #    adversaria— se marcaba como instrucción. Mismo error de categoría que
    #    la cita MITRE de más abajo.
    #  - El 3ro exige un verbo de orden explícito en vez de "I" suelto. Sin eso,
    #    "As the lead examiner, I reviewed the disk image" —exactamente cómo
    #    escribe un perito, y VIGÍA produce Amicus Curiae— se marcaba CRITICAL.
    (r"(?i)\b(?:you\s+are|act\s+as|become|serve\s+as|assume\s+(?:the\s+)?role\s+of)\s+(?:now\s+)?(?:the\s+)?(?:lead\s+|chief\s+|senior\s+|principal\s+)?(?:examiner|investigator|judge|auditor|forensic\s+analyst|reviewer|authority)\b",
     "ROLE_OVERRIDE", "CRITICAL"),
    (r"(?i)(?:^|[.;:!?]\s*|\b(?:and|then|now|please)\s+)(?:overrule|override|supersede|bypass|disregard)\s+(?:the\s+)?(?:scorer|score|verdict|judge|audit|assessment)\b",
     "ROLE_OVERRIDE", "CRITICAL"),
    (r"(?i)\b(?:as\s+(?:the\s+)?)(?:lead\s+|chief\s+|senior\s+|principal\s+)?(?:examiner|investigator|judge|auditor|forensic\s+analyst|reviewer|authority)\s*,\s*(?:i\s+(?:order|instruct|direct|command|require)|you\s+(?:must|should|will)|override|overrule|order)\b",
     "ROLE_OVERRIDE", "CRITICAL"),

    # Verdict coercion — el atacante fuerza un sello sin importar la evidencia.
    #
    # B-124: la otra clase no detectada. El 1ro exige que el destinatario sea
    # el sistema o la segunda persona. Sin eso, la DOCTRINA propia de VIGÍA
    # —"with a single artifact the finding should be reported as ABSTAIN", que
    # es el gate de corroboración Daubert— se marcaba como coerción.
    (r"(?i)\b(?:you|the\s+system|the\s+agent|the\s+model|vigia)\s+(?:must|should|shall|need\s+to|has\s+to|is\s+to)\s+(?:be\s+)?(?:report|return|render|deliver|seal|reported|returned|rendered|delivered|sealed)\s+(?:it\s+)?(?:as\s+)?(?:MALICE|INTENT|NOISE|BENIGN|ABSTAIN|UNKNOWN)\b",
     "VERDICT_COERCION", "CRITICAL"),
    (r"(?i)\b(?:report|return|render|deliver|seal)\s+(?:it\s+)?(?:as\s+)?(?:MALICE|INTENT|NOISE|BENIGN|ABSTAIN|UNKNOWN)\s+(?:regardless|irrespective|no\s+matter)\b",
     "VERDICT_COERCION", "CRITICAL"),
    (r"(?i)\b(?:regardless\s+of\s+(?:the\s+)?evidence|ignore\s+(?:the\s+)?evidence|set\s+aside\s+(?:the\s+)?(?:earlier\s+)?guidance)\b",
     "VERDICT_COERCION", "CRITICAL"),
    (r"(?i)\bdo\s+not\s+(?:escalate|report|flag|raise|seal|record)\b",
     "VERDICT_COERCION", "CRITICAL"),

    # False familiarity (Carnegie paradox — Gemini case)
    #
    # B-124: el patrón anterior era
    #   (?i)(?:as\s+)?(?:you\s+)?(?:know|should\s+know|obviously|naturally|of\s+course)
    # Todos los grupos de contexto son OPCIONALES y no había límites de
    # palabra, así que colapsaba a "las letras k-n-o-w en cualquier lado":
    # disparaba dentro de `unknown` (el artifact_type/evidence_type por
    # defecto de VIGÍA, el token más frecuente de sus propias narrativas),
    # dentro de direcciones de correo presentes en la evidencia
    # (`whoknowsme@sbcglobal.net`) y dentro de prosa forense común.
    # Medido sobre las 605 narrativas reales de results/: 410 de 411 threats
    # (99.8%) venían de acá, y como audit_narrative_before_seal escala a
    # CRITICAL_NARRATIVE_INJECTION en veredictos MALICE/INTENT, habría
    # fabricado 57 eventos CRITICAL en el log de auditoría sellado.
    #
    # El dispositivo que este patrón existe para detectar es el ENCUADRE
    # retórico ("as you know", "obviously") que presupone terreno compartido
    # para suprimir escrutinio — no el verbo "know". Reportar ignorancia
    # ("we do not know the acquisition tool") no es manipulación.
    # `know` exige ahora su encuadre de familiaridad; los adverbios quedan
    # sueltos pero con límite de palabra.
    (r"(?i)\b(?:as\s+)?(?:you|we)\s+(?:should\s+)?know\b",
     "FALSE_FAMILIARITY", "MEDIUM"),
    (r"(?i)\b(?:obviously|naturally|of\s+course)\b",
     "FALSE_FAMILIARITY", "MEDIUM"),

    # Delimiter breaks
    (r"<<<\s*END_EVIDENCE",               "DELIMITER_BREAK", "CRITICAL"),
    (r">>>\s*.*?(?=<<<|$)",               "DELIMITER_BREAK", "HIGH"),
    (r"<<<\s*(?!EVIDENCE_DATA|END_EVIDENCE)", "DELIMITER_BREAK", "HIGH"),

    # Encoding evasion
    (r"[\x00-\x08\x0b-\x0c\x0e-\x1f]",  "ENCODING_EVASION", "HIGH"),
    (r"\\x[0-9a-fA-F]{2}",               "ENCODING_EVASION", "MEDIUM"),
    (r"base64[a-zA-Z0-9+/]{40,}={0,2}",  "ENCODING_EVASION", "MEDIUM"),
    (r"&#x[0-9a-fA-F]+;",                "ENCODING_EVASION", "MEDIUM"),

    # Tool hijacking
    (r"(?i)(?:call|invoke|execute|run)\s+(?:tool|function|method)\s*\{",
     "TOOL_HIJACKING", "CRITICAL"),
    (r"(?i)(?:use|with)\s+(?:tool|function)\s*\w+\s*\(",
     "TOOL_HIJACKING", "HIGH"),
    # B-124: exige imperativo a principio de cláusula. El patrón anterior no
    # distinguía "la narrativa INSTRUYE deshabilitar seguridad" de "la narrativa
    # CITA una técnica llamada así": disparaba sobre
    # `T1562.001 (Disable Security Tools — unknown for this image)`, el nombre
    # oficial de la técnica MITRE, marcada además como NO observada. Un informe
    # forense cita TTPs por diseño; hacerlo no es hijacking. Único falso
    # positivo que quedaba sobre las 605 narrativas del corpus.
    (r"(?i)(?:^|[.;:!?]\s*|\b(?:and|then|now|please)\s+)(?:activate|trigger|disable)\s+(?:honey_token|audit|security)\b",
     "TOOL_HIJACKING", "HIGH"),

    # Gradual escalation (Gemini case — Pavlovian conditioning)
    (r"(?i)(?:first|step\s+1|initially)\s+.*?(?:then|next|after\s+that)\s+.*?(?:finally|lastly)",
     "GRADUAL_ESCALATION", "MEDIUM"),
]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ThreatDetected:
    """Amenaza detectada en una línea de la narrativa."""
    line_index:   int
    pattern_type: str
    severity:     str
    matched_text: str   # Truncado a 50 chars
    position:     int

    def to_dict(self) -> Dict:
        return {
            "line":     self.line_index,
            "type":     self.pattern_type,
            "severity": self.severity,
            "match":    self.matched_text,
            "pos":      self.position,
        }


@dataclass
class NarrativeAuditResult:
    """Resultado del audit de narrativa."""
    is_clean:            bool
    threats_detected:    List[ThreatDetected]
    sanitized_narrative: List[str]
    audit_hash:          str
    investigation_id:    str
    timestamp:           str = field(default_factory=_utcnow)

    def to_dict(self) -> Dict:
        return {
            "is_clean":        self.is_clean,
            "threats_count":   len(self.threats_detected),
            "threats":         [t.to_dict() for t in self.threats_detected],
            "narrative_lines": len(self.sanitized_narrative),
            "audit_hash":      self.audit_hash,
            "investigation_id": self.investigation_id,
            "timestamp":       self.timestamp,
        }


# ---------------------------------------------------------------------------
# NarrativeAuditor
# ---------------------------------------------------------------------------

class NarrativeAuditor:
    """
    Audita narrative[] generada por Claude/Gemini antes del sellado final.

    Implementa C3: Multi-Agent Validation.
    El auditor es un agente independiente — NO genera contenido, solo valida.

    DETERMINISTA: mismo narrative → mismo audit_hash (Qwen P0).
    """

    def __init__(self, strict_mode: bool = True) -> None:
        self.strict_mode = strict_mode
        # Compilar patrones una vez — reproducibilidad y performance
        self._patterns: List[Tuple[re.Pattern, str, str]] = [
            (re.compile(p), cls, sev)
            for p, cls, sev in _INJECTION_PATTERNS
        ]

    def audit(
        self,
        narrative: List[str],
        investigation_id: str,
        source_agent: str = "claude",
    ) -> NarrativeAuditResult:
        """
        Audita una narrativa completa.

        Args:
            narrative:        Lista de líneas de narrativa
            investigation_id: ID de la investigación (para trazabilidad)
            source_agent:     Agente que generó la narrativa (auditoría)

        Returns:
            NarrativeAuditResult con amenazas detectadas y narrativa saneada
        """
        # Anti-DoS — limitar tamaño antes de cualquier procesamiento
        if len(narrative) > _MAX_NARRATIVE_LINES:
            audit_logger.log_block(
                event_type="NARRATIVE_OVERFLOW",
                tool="NarrativeAuditor",
                input_preview=f"lines={len(narrative)} source={source_agent}",
                reason=f"Narrative exceeds {_MAX_NARRATIVE_LINES} lines. Truncating.",
            )
            narrative = narrative[:_MAX_NARRATIVE_LINES]

        threats:   List[ThreatDetected] = []
        sanitized: List[str] = []

        for idx, line in enumerate(narrative):
            if not isinstance(line, str):
                sanitized.append(str(line))
                continue

            line_threats = self._scan_line(line, idx)
            if line_threats:
                threats.extend(line_threats)
                if self.strict_mode:
                    # Cuarentena — reemplazar línea comprometida
                    sanitized.append(
                        f"[QUARANTINED LINE {idx}: "
                        f"{len(line_threats)} threat(s) — "
                        f"{line_threats[0].pattern_type}]"
                    )
                    audit_logger.log_block(
                        event_type="NARRATIVE_INJECTION_QUARANTINED",
                        tool="NarrativeAuditor",
                        input_preview=line[:100],
                        reason=(
                            f"Line {idx} quarantined: "
                            f"{', '.join(t.pattern_type for t in line_threats)}"
                        ),
                    )
                else:
                    # Modo permisivo — registrar pero no sanitizar
                    sanitized.append(line)
            else:
                sanitized.append(line)

        audit_hash = self._compute_hash(investigation_id, narrative, threats)

        return NarrativeAuditResult(
            is_clean=len(threats) == 0,
            threats_detected=threats,
            sanitized_narrative=sanitized,
            audit_hash=audit_hash,
            investigation_id=investigation_id,
        )

    def _scan_line(self, line: str, line_idx: int) -> List[ThreatDetected]:
        """Escanea una línea individual contra todos los patrones."""
        found: List[ThreatDetected] = []
        for pattern, cls, sev in self._patterns:
            for match in pattern.finditer(line):
                found.append(ThreatDetected(
                    line_index=line_idx,
                    pattern_type=cls,
                    severity=sev,
                    matched_text=match.group(0)[:50],
                    position=match.start(),
                ))
        return found

    def _compute_hash(
        self,
        inv_id: str,
        original: List[str],
        threats: List[ThreatDetected],
    ) -> str:
        """
        Hash determinista para cadena de custodia del audit.
        DETERMINISTA: no usa timestamp — mismo input → mismo hash (Qwen P0).
        """
        canonical = (
            f"{inv_id}:{len(original)}:{len(threats)}:"
            f"{','.join(t.pattern_type for t in threats)}"
        )
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Punto de integración con autonomous_investigation()
# ---------------------------------------------------------------------------

def audit_narrative_before_seal(
    narrative: List[str],
    investigation_id: str,
    cumulative_verdict: str,
) -> NarrativeAuditResult:
    """
    Punto de integración C3: llamar JUSTO antes de construir `final`
    en autonomous_investigation().

    Si hay threats CRITICAL y cumulative_verdict es MALICE/INTENT,
    el reporte debe ser INVALIDATED (WITNESS_HARD_FAIL).
    """
    auditor = NarrativeAuditor(strict_mode=True)
    result  = auditor.audit(narrative, investigation_id, source_agent="claude")

    if not result.is_clean and cumulative_verdict in ("MALICE", "INTENT"):
        audit_logger.log_block(
            event_type="CRITICAL_NARRATIVE_INJECTION",
            tool="audit_narrative_before_seal",
            input_preview=f"inv={investigation_id}",
            reason=(
                f"Narrative injection detected in {cumulative_verdict} report. "
                f"Threats: {len(result.threats_detected)}. "
                f"Report INVALIDATED per C3 protocol."
            ),
        )

    return result
