"""Glossary of sealed vocabulary, explained in two languages.

Terms are the literal tokens a bundle uses: verdict values, schema names,
field names, Peircean layers, status and confidence enums. The token itself
is never translated; only the explanation is. Both explanations are mandatory
fields, so EN/ES parity is structural rather than checked after the fact.

Renderers collect the terms they actually emit in a :class:`GlossaryCollector`
and print only those, sorted, so a report's glossary matches its body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class GlossaryEntry:
    term: str
    en: str
    es: str
    see_also: tuple[str, ...] = ()


def _e(term: str, en: str, es: str, *see_also: str) -> GlossaryEntry:
    return GlossaryEntry(term=term, en=en, es=es, see_also=tuple(see_also))


_ENTRIES: tuple[GlossaryEntry, ...] = (
    # ------------------------------------------------------------ verdicts
    _e("NOISE",
       "Verdict rung 1 of 5. Everything observed is explained by misconfiguration, "
       "software error or normal operations.",
       "Peldaño 1 de 5. Todo lo observado se explica por mala configuración, error "
       "de software u operación normal."),
    _e("SUSPICION",
       "Verdict rung 2 of 5. A structural anomaly exists; no evidence of deliberate "
       "concealment or coordination.",
       "Peldaño 2 de 5. Hay una anomalía estructural; no hay evidencia de "
       "ocultamiento deliberado ni de coordinación."),
    _e("INTENT",
       "Verdict rung 3 of 5. Deliberate decisions were made to produce the outcome. "
       "Requires two independent sources and the refutation protocol.",
       "Peldaño 3 de 5. Se tomaron decisiones deliberadas para producir el "
       "resultado. Exige dos fuentes independientes y el protocolo de refutación.",
       "devil_advocate"),
    _e("MALICE",
       "Verdict rung 4 of 5. Active concealment of intent (anti-forensics). Requires "
       "two sources, the refutation protocol and a populated devil_advocate.",
       "Peldaño 4 de 5. Ocultamiento activo de la intención (antiforense). Exige "
       "dos fuentes, el protocolo de refutación y un devil_advocate completo.",
       "devil_advocate"),
    _e("ABSTAIN",
       "Verdict rung 5 of 5. Insufficient evidence to classify; the gap is a "
       "documented limitation, not a benign finding.",
       "Peldaño 5 de 5. Evidencia insuficiente para clasificar; el hueco es una "
       "limitación documentada, no un hallazgo benigno."),
    _e("ERROR",
       "Exit-code label of a run that did not complete. Not a forensic finding and "
       "not a bundle field.",
       "Etiqueta de exit code de una corrida que no terminó. No es un hallazgo "
       "forense ni un campo del bundle."),
    # ------------------------------------------------------------- families
    _e("ebs_v1",
       "Bundle family: sealed pipeline bundle with evidence_graph, decision_trace "
       "and an integrity block. Verified by forensics/verify_ebs_v1.py.",
       "Familia de bundle: bundle sellado del pipeline con evidence_graph, "
       "decision_trace y un bloque integrity. Se verifica con "
       "forensics/verify_ebs_v1.py.",
       "bundle_hash", "analysis_fingerprint"),
    _e("agent_audit",
       "Bundle family: output of vigia_agent.py (Mode 1). Digest of the whole file "
       "lives in the .sha256 sidecar.",
       "Familia de bundle: salida de vigia_agent.py (Modo 1). El digest de todo el "
       "archivo vive en el sidecar .sha256.",
       "agent_verdict", "audit_trail"),
    _e("mcp_investigation",
       "Bundle family: Mode 2 Claude Code / MCP investigation with findings and a "
       "hash-chained tool_execution_log.",
       "Familia de bundle: investigación de Modo 2 en Claude Code / MCP con "
       "hallazgos y un tool_execution_log encadenado por hashes.",
       "tool_execution_log", "chain_tip_sha256"),
    _e("unknown",
       "Bundle family could not be identified. Nothing is inferred from such a file.",
       "No se pudo identificar la familia de bundle. No se infiere nada de ese "
       "archivo."),
    # --------------------------------------------------------- Peirce layers
    _e("Firstness",
       "Peirce's first layer: the sign itself, described without interpretation "
       "(what was observed).",
       "Primera capa de Peirce: el signo en sí, descripto sin interpretar (qué se "
       "observó)."),
    _e("Secondness",
       "Peirce's second layer: the sign against its context; how it deviates from "
       "a baseline.",
       "Segunda capa de Peirce: el signo frente a su contexto; cómo se desvía de un "
       "baseline."),
    _e("Thirdness",
       "Peirce's third layer: the inferred law; what repeatable deliberate pattern "
       "produces the sign.",
       "Tercera capa de Peirce: la ley inferida; qué patrón deliberado y repetible "
       "produce el signo."),
    # ----------------------------------------------------- status / confidence
    _e("CONFIRMED",
       "Finding status: supported by at least two independent sources.",
       "Estado de hallazgo: sostenido por al menos dos fuentes independientes."),
    _e("INFERRED",
       "Finding status: supported by one source; corroboration attempted but not "
       "obtained.",
       "Estado de hallazgo: sostenido por una sola fuente; se intentó corroborar sin "
       "éxito."),
    _e("REFUTED",
       "Finding status: initially flagged, then disproved by content analysis.",
       "Estado de hallazgo: marcado al inicio y luego refutado por el análisis de "
       "contenido."),
    _e("HIGH", "Confidence label used in Mode 2 findings (highest of three).",
       "Etiqueta de confianza usada en hallazgos de Modo 2 (la más alta de tres)."),
    _e("MEDIUM", "Confidence label used in Mode 2 findings (middle of three).",
       "Etiqueta de confianza usada en hallazgos de Modo 2 (la del medio de tres)."),
    _e("LOW", "Confidence label used in Mode 2 findings (lowest of three).",
       "Etiqueta de confianza usada en hallazgos de Modo 2 (la más baja de tres)."),
    # --------------------------------------------------------- custody fields
    _e("bundle_hash",
       "SHA-256 over the whole EBS v1 payload except the integrity block "
       "(Invariant I2). Any change to any field changes it.",
       "SHA-256 sobre todo el payload EBS v1 salvo el bloque integrity (Invariante "
       "I2). Cualquier cambio en cualquier campo lo altera."),
    _e("analysis_fingerprint",
       "SHA-256 over the EBS v1 payload minus timestamps and ids: two runs on the "
       "same evidence share it.",
       "SHA-256 sobre el payload EBS v1 sin timestamps ni ids: dos corridas sobre "
       "la misma evidencia lo comparten."),
    _e("graph_hash", "SHA-256 of the EBS v1 evidence_graph (minus generated_at).",
       "SHA-256 del evidence_graph de EBS v1 (sin generated_at)."),
    _e("decision_hash", "SHA-256 of the whole EBS v1 decision_trace.",
       "SHA-256 de todo el decision_trace de EBS v1."),
    _e("policy_hash", "SHA-256 of the EBS v1 policy_spec (minus created_at).",
       "SHA-256 del policy_spec de EBS v1 (sin created_at)."),
    _e("engine_attestation_hash",
       "Hash attesting the engine build that produced the bundle. Empty when not "
       "supplied.",
       "Hash que atestigua la build del motor que produjo el bundle. Vacío cuando no "
       "se suministró."),
    _e("ecl_hash", "Hash of the evidence collection log, when one was supplied.",
       "Hash del log de recolección de evidencia, cuando se suministró."),
    _e("sealed_at", "Timestamp at which the EBS v1 integrity block was written.",
       "Timestamp en que se escribió el bloque integrity de EBS v1."),
    _e("evidence_sha256",
       "Agent bundle: SHA-256 of the primary evidence read at session start. Also "
       "seeds the session nonce.",
       "Bundle de agente: SHA-256 de la evidencia primaria leída al inicio de la "
       "sesión. También siembra el nonce de sesión."),
    _e("runtime_fingerprint",
       "Agent bundle: hash of the interpreter and dependency versions that ran the "
       "analysis.",
       "Bundle de agente: hash de las versiones de intérprete y dependencias que "
       "corrieron el análisis."),
    _e("analysis_timestamp", "Agent bundle: wall-clock time of the run.",
       "Bundle de agente: hora de reloj de la corrida."),
    _e("agent_verdict",
       "Agent bundle: the sealed four-value verdict (NOISE, SUSPICION, MALICE, "
       "ABSTAIN). Mode 1 has no INTENT rung.",
       "Bundle de agente: el veredicto sellado de cuatro valores (NOISE, SUSPICION, "
       "MALICE, ABSTAIN). El Modo 1 no tiene peldaño INTENT."),
    _e("best_hypothesis",
       "Agent bundle: label of the winning abductive hypothesis. A hypothesis "
       "label, not a verdict.",
       "Bundle de agente: etiqueta de la hipótesis abductiva ganadora. Es una "
       "etiqueta de hipótesis, no un veredicto.",
       "agent_verdict"),
    _e("bundle_sha256",
       "Mode 2 bundle: SHA-256 the investigator recorded for the bundle at sealing.",
       "Bundle de Modo 2: SHA-256 que el investigador registró para el bundle al "
       "sellarlo."),
    _e("primary_evidence_sha256",
       "Mode 2 bundle: SHA-256 of the primary evidence artifact, hashed before it "
       "was read.",
       "Bundle de Modo 2: SHA-256 del artefacto de evidencia primario, hasheado "
       "antes de leerlo."),
    _e("evidence_hash", "Mode 2 bundle: alternative field name for the evidence hash.",
       "Bundle de Modo 2: nombre alternativo del campo del hash de evidencia."),
    _e("chain_tip_sha256",
       "Mode 2 bundle: entry_hash of the last tool_execution_log entry, stored as a "
       "sibling so truncating the log is detectable.",
       "Bundle de Modo 2: entry_hash de la última entrada de tool_execution_log, "
       "guardado como hermano para que truncar el log sea detectable.",
       "tool_execution_log"),
    _e("timestamp_sealed", "Mode 2 bundle: time at which the investigator sealed it.",
       "Bundle de Modo 2: hora en que el investigador lo selló."),
    # ------------------------------------------------------ process records
    _e("audit_trail",
       "Agent bundle: ordered record of every agent action, each entry with its "
       "own entry_sha256.",
       "Bundle de agente: registro ordenado de cada acción del agente, cada entrada "
       "con su propio entry_sha256."),
    _e("tool_execution_log",
       "Mode 2 bundle: hash-chained list of tool calls (prev_hash, entry_hash, "
       "optional entry_hmac). Verified by verify_tool_log.py.",
       "Bundle de Modo 2: lista de llamadas a herramientas encadenada por hashes "
       "(prev_hash, entry_hash, entry_hmac opcional). Se verifica con "
       "verify_tool_log.py.",
       "chain_version"),
    _e("chain_version",
       "tool_execution_log schema: v1 protects only result_summary; v2 covers the "
       "whole entry.",
       "Esquema de tool_execution_log: v1 protege sólo result_summary; v2 cubre toda "
       "la entrada."),
    _e("refutation_gate_log",
       "Mode 2 bundle: record of candidate verdicts a Daubert gate rejected before "
       "emission, and why.",
       "Bundle de Modo 2: registro de veredictos candidatos que un gate Daubert "
       "rechazó antes de emitirlos, y por qué."),
    _e("devil_advocate",
       "The strongest benign explanation the analysis had to defeat. Mandatory for "
       "INTENT and MALICE; empty means the verdict did not meet Daubert.",
       "La explicación benigna más fuerte que el análisis tuvo que vencer. "
       "Obligatoria para INTENT y MALICE; vacía significa que el veredicto no cumplió "
       "Daubert."),
    _e("self_corrections_applied",
       "Agent bundle: count of pre-emission corrections the pipeline applied to "
       "itself.",
       "Bundle de agente: cantidad de correcciones previas a la emisión que el "
       "pipeline se aplicó a sí mismo."),
    _e("sans_compliance",
       "Agent bundle: checklist of hackathon submission criteria (audit trail, "
       "self-correction, ...). Not a PICERL phase.",
       "Bundle de agente: checklist de criterios de entrega del hackathon (audit "
       "trail, autocorrección, ...). No es una fase PICERL.",
       "PICERL"),
    _e("sans_phase",
       "Mode 2 bundle: the SANS incident-response phase the investigator recorded.",
       "Bundle de Modo 2: la fase de respuesta a incidentes SANS que registró el "
       "investigador.",
       "PICERL"),
    _e("system_state",
       "EBS v1: engine version, calibration model hash and stability parameters at "
       "sealing time.",
       "EBS v1: versión del motor, hash del modelo de calibración y parámetros de "
       "estabilidad al momento del sellado."),
    # ------------------------------------------------- decision-trace fields
    _e("reason_code",
       "EBS v1 decision_trace: machine-readable reason for the sealed decision.",
       "decision_trace de EBS v1: razón legible por máquina de la decisión sellada."),
    _e("abstain_reason",
       "EBS v1 decision_trace: why the pipeline abstained, when it did.",
       "decision_trace de EBS v1: por qué el pipeline se abstuvo, cuando lo hizo."),
    _e("hard_temporal_gate",
       "CAIE flag: a temporal impossibility forced the verdict regardless of score.",
       "Flag de CAIE: una imposibilidad temporal forzó el veredicto sin importar el "
       "score."),
    _e("r3_calibration_note",
       "CAIE note explaining how the R3 coherence check relates the EBS decision to "
       "the forensic verdict.",
       "Nota de CAIE que explica cómo el chequeo de coherencia R3 relaciona la "
       "decisión EBS con el veredicto forense."),
    _e("caie_fractures_source",
       "CAIE provenance marker: live_caie means fractures were computed at run time, "
       "not declared in the input.",
       "Marcador de procedencia de CAIE: live_caie significa que las fracturas se "
       "calcularon en la corrida, no se declararon en el input."),
    _e("composite_score", "CAIE: the composite intent score before the verdict ladder.",
       "CAIE: el score compuesto de intención antes de la escalera de veredictos."),
    _e("posterior", "EBS v1 decision_trace: posterior probability sealed by the pipeline.",
       "decision_trace de EBS v1: probabilidad posterior sellada por el pipeline."),
    _e("risk", "EBS v1 decision_trace: bounded risk value sealed by the pipeline.",
       "decision_trace de EBS v1: valor de riesgo acotado sellado por el pipeline."),
    _e("z_score",
       "Agent signal: deviation of the signal from its baseline, as an exact "
       "Fraction.",
       "Señal del agente: desviación de la señal respecto de su baseline, como "
       "Fraction exacta.",
       "Fraction"),
    _e("Fraction",
       "Exact rational number (numerator/denominator). VIGÍA's scoring uses "
       "Fractions so two machines get identical results; they are never percentages.",
       "Número racional exacto (numerador/denominador). El scoring de VIGÍA usa "
       "Fractions para que dos máquinas den resultados idénticos; nunca son "
       "porcentajes."),
    # ---------------------------------------------------------- frameworks
    _e("PICERL",
       "SANS incident-response lifecycle: Preparation, Identification, Containment, "
       "Eradication, Recovery, Lessons Learned.",
       "Ciclo de respuesta a incidentes de SANS: Preparación, Identificación, "
       "Contención, Erradicación, Recuperación, Lecciones aprendidas."),
    _e("Daubert",
       "US admissibility standard for expert evidence: testable method, known error "
       "rate, peer review, general acceptance. VIGÍA's gates exist to meet it.",
       "Estándar de admisibilidad de EE. UU. para prueba pericial: método "
       "comprobable, tasa de error conocida, revisión de pares, aceptación general. "
       "Los gates de VIGÍA existen para cumplirlo."),
    _e("Carnegie",
       "Dale Carnegie's persuasion taxonomy, used to name which legitimate "
       "expectation an actor weaponized (authority transfer, social proof, urgency).",
       "Taxonomía de persuasión de Dale Carnegie, usada para nombrar qué expectativa "
       "legítima explotó un actor (transferencia de autoridad, prueba social, "
       "urgencia)."),
    _e("CAIE",
       "Cross-Artifact Intent Engine: VIGÍA module that looks for fractures between "
       "artifacts (timeline, provenance, content) as intent signals.",
       "Cross-Artifact Intent Engine: módulo de VIGÍA que busca fracturas entre "
       "artefactos (línea de tiempo, procedencia, contenido) como señales de "
       "intención."),
    _e("MITRE ATT&CK",
       "Public knowledge base of adversary techniques. Ids look like T1055 or "
       "T1070.006.",
       "Base de conocimiento pública de técnicas adversarias. Los ids se ven como "
       "T1055 o T1070.006."),
    _e("verdict_disagreement",
       "Reader flag: the bundle carries two verdict-bearing fields with different "
       "values. Both are shown; neither is chosen.",
       "Flag del lector: el bundle lleva dos campos con veredicto y valores "
       "distintos. Se muestran ambos; no se elige ninguno."),
)

GLOSSARY: dict[str, GlossaryEntry] = {e.term: e for e in _ENTRIES}


def is_term(term: str) -> bool:
    return term in GLOSSARY


@dataclass
class GlossaryCollector:
    """Collects the terms a renderer emits; renders only those, sorted."""

    _used: set = field(default_factory=set)

    def mark(self, *terms: str) -> None:
        for term in terms:
            if term in GLOSSARY:
                self._used.add(term)

    def mark_verdict(self, value: object) -> None:
        """Mark a verdict token only if it is on the sealed scale."""
        if isinstance(value, str) and value in GLOSSARY:
            self._used.add(value)

    def used(self) -> list[str]:
        return sorted(self._used)

    def rows(self, lang: str) -> list[tuple[str, str]]:
        out = []
        for term in self.used():
            entry = GLOSSARY[term]
            text = entry.en if lang == "en" else entry.es
            if entry.see_also:
                text += " (" + ", ".join(f"`{s}`" for s in entry.see_also) + ")"
            out.append((term, text))
        return out


def all_terms() -> Iterable[str]:
    return GLOSSARY.keys()


__all__ = ["GlossaryEntry", "GLOSSARY", "GlossaryCollector", "is_term", "all_terms"]
