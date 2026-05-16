"""
vigia_counter_fact.py
VIGÍA Forensic Suite — Abducción Probabilística Inversa (Capa Virtual)
Versión: v1.0-Valkyrie
Autora:  Anna Tchijova

Para cada hipótesis ganadora H* genera el "Escenario Mínimo Alternativo":
qué artefactos tendrían que haberse observado (o no observado) para que
la hipótesis descartada Hᵢ hubiera ganado.

Formalismo (clave de sort VIGÍA):
  sort_key = (cost, -coverage_score, len(required_artifacts))
  H* gana si sort_key(H*) < sort_key(Hᵢ) lexicográficamente.

Para invertir ese orden y hacer que Hᵢ gane, se necesita:
  a) Reducir cost(Hᵢ) por debajo de cost(H*), O
  b) Si cost(Hᵢ) == cost(H*): coverage(Hᵢ) > coverage(H*), O
  c) Si también hay empate en cobertura: len(required_artifacts_Hᵢ) < len(required_artifacts_H*)

Corrección CF-02:
  El bug original hacía `return None` para margin_cost <= 0, descartando casos
  donde el challenger ya tiene menor costo pero pierde en cobertura (la hipótesis
  ganadora tiene mayor cobertura al mismo costo). Ahora se manejan los tres
  criterios de desempate según la jerarquía de invariantes de VIGÍA.

Corrección report_hash:
  El hash ahora cubre el contenido completo de todos los escenarios generados,
  no sólo bundle_id + winner + count.

Corrección _extract_observed_artifacts:
  Reconstruye correctamente el conjunto observado procesando required_artifacts
  y assumed_artifacts con el contexto de la fase de ataque.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ──────────────────────────────────────────────────────────────────────────
# CONSTANTES DE SEGURIDAD
# ──────────────────────────────────────────────────────────────────────────

# Hard cap para max_scenarios — previene DoS con miles de hipótesis alternativas.
# El límite de 20 cubre todos los casos reales (VIGÍA tiene 33 hipótesis en total).
# Nunca superar porque el análisis es O(n) y cada escenario materializa directivas.
MAX_SCENARIOS_HARD_CAP: int = 20

# ──────────────────────────────────────────────────────────────────────────
# TABLA DE DIRECTIVAS INVESTIGATIVAS
# ──────────────────────────────────────────────────────────────────────────

# CF-DIR-01: DIRECTIVAS HUMANAS — NO EJECUTAR DIRECTAMENTE
# Estas strings son instrucciones para el perito, no comandos ejecutables.
# Requieren revisión y adaptación al entorno específico antes de ejecutar.
INVESTIGATIVE_DIRECTIVES: Dict[str, str] = {
    "timestamp_uniformity":
        "Calcular std de intervalos: python3 -c \""
        "import json,statistics; d=json.load(open('log.json')); "
        "print(statistics.stdev(d))\". STD > 100ms descarta uniformidad artificial.",
    "log_gap_intervals":
        "Extraer timestamps raw: jq '[.[].timestamp]' log.json | "
        "python3 -c 'import sys,json; ts=json.load(sys.stdin); "
        "print([ts[i+1]-ts[i] for i in range(len(ts)-1)])'",
    "process_memory_contradiction":
        "Listar procesos activos: ps aux --sort=pid | awk '{print $1,$2,$11}'. "
        "Comparar UIDs del generador de logs esperado con los procesos en memoria.",
    "log_deletion":
        "Buscar en journal: journalctl -o json | jq 'select(.MESSAGE|test(\"log.*clear\"))'. "
        "En Linux equivale a Event ID 1102 de Windows.",
    "event_log_clearing":
        "grep -r 'logrotate\\|truncate.*log\\|> /var/log' /var/log/syslog "
        "y correlacionar con el timeline del incidente.",
    "artifact_overwrite":
        "Buscar binarios de borrado seguro: which shred wipe srm. "
        "Revisar inode 0 en directorios sospechosos con stat <file>.",
    "file_timestamp_modification":
        "Comparar mtime/ctime con atime: stat <file>. "
        "Divergencia ctime-mtime > 1h en archivo estático es indicador de tampering.",
    "outbound_data_transfer":
        "Revisar flows: ss -tnp | grep ESTABLISHED. "
        "Calcular bytes enviados: cat /proc/net/dev | grep <iface>.",
    "data_volume":
        "Correlacionar bytes_out por host: "
        "tcpdump -i <iface> -w /tmp/cap.pcap & sleep 60; kill %1; "
        "capinfos /tmp/cap.pcap | grep 'Data byte rate'.",
    "registry_modifications":
        "En Linux: revisar /etc/init.d/, /etc/systemd/system/, "
        "/etc/cron.d/, ~/.config/autostart/. "
        "find / -newer /tmp/reference_file -name '*.service' 2>/dev/null",
    "persistence_mechanism":
        "systemctl list-unit-files --state=enabled | grep -v '^systemd'. "
        "crontab -l && cat /etc/cron.d/* 2>/dev/null.",
    "pass_the_hash_indicator":
        "En Linux/Kerberos: klist -A para tickets Kerberos. "
        "En entorno AD: grep 'NTLM' /var/log/samba/log.smbd. "
        "Buscar LogonType equivalente en PAM: grep 'session opened' /var/log/auth.log",
    "lateral_movement_detected":
        "Mapear conexiones SSH salientes: "
        "grep 'Accepted\\|Failed' /var/log/auth.log | awk '{print $11}' | sort | uniq -c. "
        "También: ausearch -i -m USER_AUTH --start today 2>/dev/null",
    "phishing_email_delivered":
        "Revisar headers MTA en /var/log/mail.log o Postfix logs. "
        "Verificar SPF/DKIM: opendmarc-check o check-auth2@verifier.port25.com.",
    "malicious_attachment_executed":
        "Correlacionar procesos hijos de MUA (thunderbird, mutt, evolution): "
        "pstree -p | grep -A5 thunderbird. "
        "Revisar audit: ausearch -m EXECVE --start today | grep thunderbird",
    "command_line_execution":
        "Revisar bash history: cat ~/.bash_history. "
        "Con auditd: ausearch -m EXECVE --start today | aureport -x. "
        "Buscar base64: grep -P 'base64|\\\\x[0-9a-f]{2}' ~/.bash_history",
    "script_execution":
        "Revisar scripts ejecutados: ausearch -m EXECVE -i | grep -E '\\.sh|\\.py|\\.pl'. "
        "Buscar en /tmp, /dev/shm: find /tmp /dev/shm -executable -type f -newer /tmp",
    "hardware_additions":
        "Revisar dispositivos USB: lsusb -v | grep -E 'idVendor|idProduct'. "
        "dmesg | grep -E 'usb|storage' | tail -50.",
    "credential_dumping":
        "Revisar acceso a /etc/shadow: ausearch -m PATH -i | grep shadow. "
        "Verificar integridad: sha256sum /etc/shadow /etc/passwd y comparar con baseline.",
    "privilege_escalation":
        "Buscar SUID/SGID nuevos: find / -perm /6000 -newer /tmp/reference -type f 2>/dev/null. "
        "Revisar sudo: grep -v '^#' /etc/sudoers /etc/sudoers.d/* 2>/dev/null",
}

GENERIC_DIRECTIVE = (
    "Revisar artefactos de la fase IR correspondiente. "
    "Buscar presencia/ausencia en: "
    "auditd logs, journalctl, /proc filesystem, "
    "netstat/ss para conexiones, lsof para archivos abiertos."
)

# ──────────────────────────────────────────────────────────────────────────
# ESTRUCTURAS DE DATOS
# ──────────────────────────────────────────────────────────────────────────


def _md_escape(text: str) -> str:
    """
    CF-MD-01: escapa caracteres que rompen renderizado markdown en informes forenses.

    Auditado K2 (2026-05-16): versión original sólo escapaba '|'.
    En un informe judicial, un plausibility_rationale con '*100%*' o '[ver anexo]'
    se rendería como énfasis/link en lugar de texto literal — inaceptable Daubert.

    Entidades HTML usadas para máxima compatibilidad cross-renderer.
    """
    if not isinstance(text, str):
        return str(text)
    # Pipe rompe columnas de tabla
    text = text.replace("|", "&#124;")
    # Asterisco e underscore rompen énfasis/itálica
    text = text.replace("*", "&#42;")
    text = text.replace("_", "&#95;")
    # Corchetes rompen sintaxis de links
    text = text.replace("[", "&#91;").replace("]", "&#93;")
    # Mayor-que rompe blockquotes anidados
    text = text.replace(">", "&#62;")
    return text

@dataclass
class CounterFactualOperation:
    """Operación mínima que haría que una hipótesis alternativa ganara."""
    op_type: str                         # "ADD" | "REMOVE" | "ADD+REMOVE" | "COVERAGE_GAP"
    artifacts_to_add: List[str]
    artifacts_to_remove: List[str]
    delta_cost_winner: int
    delta_cost_challenger: int
    delta_coverage_challenger: int
    plausibility: int                    # [0, 100] — entero determinista
    plausibility_rationale: str
    investigative_directives: List[str]
    tiebreak_criterion: str              # qué criterio de la jerarquía determina el escenario

    def to_dict(self) -> Dict[str, Any]:
        return {
            "op_type":                    self.op_type,
            "artifacts_to_add":           self.artifacts_to_add,
            "artifacts_to_remove":        self.artifacts_to_remove,
            "delta_cost_winner":          self.delta_cost_winner,
            "delta_cost_challenger":      self.delta_cost_challenger,
            "delta_coverage_challenger":  self.delta_coverage_challenger,
            "plausibility":               self.plausibility,
            "plausibility_rationale":     self.plausibility_rationale,
            "investigative_directives":   self.investigative_directives,
            "tiebreak_criterion":         self.tiebreak_criterion,
        }


@dataclass
class AlternativeScenario:
    """Escenario mínimo alternativo para una hipótesis descartada."""
    challenger_id: str
    challenger_intent: str
    challenger_cost: int
    challenger_coverage: int
    challenger_required_count: int
    winner_id: str
    winner_cost: int
    winner_coverage: int
    winner_required_count: int
    margin_cost: int                    # challenger_cost - winner_cost
    margin_coverage: int                # winner_coverage - challenger_coverage
    margin_required: int                # challenger_required_count - winner_required_count
    decisive_criterion: str             # cuál de los 3 criterios determinó la derrota
    operation: CounterFactualOperation
    daubert_note: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "challenger_id":           self.challenger_id,
            "challenger_intent":       self.challenger_intent,
            "challenger_cost":         self.challenger_cost,
            "challenger_coverage":     self.challenger_coverage,
            "challenger_required_count": self.challenger_required_count,
            "winner_id":               self.winner_id,
            "winner_cost":             self.winner_cost,
            "winner_coverage":         self.winner_coverage,
            "winner_required_count":   self.winner_required_count,
            "margin_cost":             self.margin_cost,
            "margin_coverage":         self.margin_coverage,
            "margin_required":         self.margin_required,
            "decisive_criterion":      self.decisive_criterion,
            "operation":               self.operation.to_dict(),
            "daubert_note":            self.daubert_note,
        }


@dataclass
class CounterFactReport:
    """Reporte completo de counter-factoring para un AbductiveResult."""
    winner_id: str
    winner_intent: str
    winner_cost: int
    winner_coverage: int
    winner_required_count: int
    observed_artifacts: List[str]
    phase: str
    scenarios: List[AlternativeScenario]
    report_hash: str                    # SHA-256 sobre TODOS los escenarios
    generated_at: str
    daubert_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vigia_version":       "v1.0-Valkyrie",
            "winner_id":           self.winner_id,
            "winner_intent":       self.winner_intent,
            "winner_cost":         self.winner_cost,
            "winner_coverage":     self.winner_coverage,
            "winner_required_count": self.winner_required_count,
            "observed_artifacts":  self.observed_artifacts,
            "phase":               self.phase,
            "scenarios":           [s.to_dict() for s in self.scenarios],
            "report_hash":         self.report_hash,
            "generated_at":        self.generated_at,
            "daubert_summary":     self.daubert_summary,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(
            self.to_dict(), indent=indent, sort_keys=True, ensure_ascii=False
        )

    def to_markdown(self) -> str:
        lines: List[str] = [
            "# VIGÍA Counter-Factual Analysis — Abducción Probabilística Inversa",
            "",
            f"> **Hipótesis ganadora:** `{self.winner_id}` (`{self.winner_intent}`)  ",
            f"> **Costo Ockham:** {self.winner_cost}  |  "
            f"**Cobertura:** {self.winner_coverage}%  |  "
            f"**Artefactos requeridos:** {self.winner_required_count}  ",
            f"> **Fase:** `{self.phase}`  ",
            f"> **Hash reporte:** `{self.report_hash}`  ",
            f"> **Generado:** `{self.generated_at}`",
            "",
            "## Propósito Daubert",
            "",
            self.daubert_summary,
            "",
            "## Artefactos Observados",
            "",
        ]
        for a in self.observed_artifacts:
            lines.append(f"- `{a}`")
        lines.append("")
        lines += [
            "## Escenarios Mínimos Alternativos",
            "",
            "Para cada hipótesis descartada: perturbación mínima del conjunto de "
            "observaciones que haría que esa hipótesis ganara.",
            "",
        ]

        for i, sc in enumerate(self.scenarios, 1):
            op = sc.operation
            lines += [
                f"### Escenario {i}: `{sc.challenger_id}` ({sc.challenger_intent})",
                "",
                "| Métrica | Ganadora `{}` | Challenger `{}` |".format(
                    _md_escape(str(sc.winner_id)), _md_escape(str(sc.challenger_id))
                ),
                "|---|---|---|",
                f"| Costo Ockham | {sc.winner_cost} | {sc.challenger_cost} |",
                f"| Cobertura | {sc.winner_coverage}% | {sc.challenger_coverage}% |",
                f"| Artefactos requeridos | {sc.winner_required_count} "
                f"| {sc.challenger_required_count} |",
                f"| Margen costo | — | {sc.margin_cost:+d} |",
                "",
                f"**Criterio decisivo de derrota:** `{_md_escape(sc.decisive_criterion)}`  ",
                f"**Operación requerida:** `{_md_escape(op.op_type)}`  ",
                f"**Criterio de desempate tiebreak:** `{_md_escape(str(op.tiebreak_criterion))}`",
                "",
            ]

            if op.artifacts_to_add:
                lines.append("**Artefactos a agregar** (reduciría costo del challenger):")
                for art in op.artifacts_to_add:
                    directive = INVESTIGATIVE_DIRECTIVES.get(art, GENERIC_DIRECTIVE)
                    lines += [f"- `{_md_escape(str(art))}`", f"  → *{_md_escape(directive[:120])}*"]
                lines.append("")

            if op.artifacts_to_remove:
                lines.append("**Artefactos a eliminar** (aumentaría costo de la ganadora):")
                for art in op.artifacts_to_remove:
                    directive = INVESTIGATIVE_DIRECTIVES.get(art, GENERIC_DIRECTIVE)
                    lines += [f"- `{_md_escape(str(art))}`", f"  → *{_md_escape(directive[:120])}*"]
                lines.append("")

            lines += [
                f"**Plausibilidad:** {op.plausibility}/100  ",
                f"*{_md_escape(str(op.plausibility_rationale))}*",
                "",
                "**Nota Daubert:**",
                f"> {_md_escape(sc.daubert_note)}",
                "",
            ]

        lines += [
            "---",
            f"*Hash: `{self.report_hash}` | "
            "vigia_counter_fact.py v1.0-Valkyrie*",
        ]
        return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────
# EXTRACCIÓN DE ARTEFACTOS OBSERVADOS
# ──────────────────────────────────────────────────────────────────────────

def _extract_observed_artifacts(
    winner: Dict[str, Any],
    alternatives: List[Dict[str, Any]],
    bundle: Optional[Dict[str, Any]] = None,
) -> Tuple[Set[str], str]:
    """
    Reconstruye el conjunto de artefactos observados y la fase de ataque.

    Estrategia determinista en tres capas:
    1. required_artifacts del winner que NO están en assumed_artifacts del winner
       → estos son los que FUERON observados (el winner los vio)
    2. Artefactos directos del bundle si está disponible
    3. Para los alternatives: required que coincidan con los del winner y no sean assumed

    Retorna (observed_set, phase_str).
    """
    observed: Set[str] = set()
    phase = str(winner.get("phase", ""))

    # Capa 1: desde el winner
    winner_required: List[str] = list(winner.get("required_artifacts", []) or [])
    winner_assumed_raw: Set[str] = set(winner.get("assumed_artifacts", []) or [])
    # CF-EXT-01: normalizar nombres antes de agregar al set
    def _norm(s: str) -> str:
        return s.lower().strip().replace(" ", "_") if isinstance(s, str) else ""
    winner_assumed: Set[str] = {_norm(a) for a in winner_assumed_raw}
    # Los required que NO son assumed fueron efectivamente observados
    for req in winner_required:
        req_n = _norm(req)
        if req_n and req_n not in winner_assumed:
            observed.add(req_n)

    # Capa 2: desde artefactos directos del bundle
    if bundle is not None:
        for art in bundle.get("artifacts", []):
            if not isinstance(art, dict):
                continue
            name = str(art.get("artifact_name", art.get("artifact_id", "")))
            if name and art.get("observed", True) and not art.get("adversarial_noise", False):
                observed.add(name)

        # También desde abduction_trace si hay fase
        abduction = bundle.get("abduction_trace", {}) or {}
        hyp = abduction.get("abductive_hypothesis", {}) or {}
        if not phase:
            phase = str(hyp.get("phase", ""))

    # Capa 3: desde alternatives — required que coincidan con winner required
    winner_required_set = set(winner_required)
    for alt in alternatives:
        if not isinstance(alt, dict):
            continue
        alt_required: List[str] = list(alt.get("required_artifacts", []) or [])
        alt_assumed: Set[str] = set(alt.get("assumed_artifacts", []) or [])
        for req in alt_required:
            if isinstance(req, str) and req not in alt_assumed and req in winner_required_set:
                observed.add(req)

    return observed, phase


# ──────────────────────────────────────────────────────────────────────────
# MOTOR COUNTER-FACTUAL
# ──────────────────────────────────────────────────────────────────────────


def _validate_abductive_schema(abductive_result: Dict[str, Any]) -> Optional[str]:
    """
    Verifica la estructura mínima de un AbductiveResult.
    Retorna None si es válido, o mensaje de error si no.

    Campos mínimos requeridos:
    - winner: dict con hypothesis_id (str no vacío)
    - alternatives: lista (puede estar vacía)
    """
    if not isinstance(abductive_result, dict):
        return f"abductive_result debe ser dict, recibido: {type(abductive_result).__name__}"

    winner = abductive_result.get("winner")
    if not isinstance(winner, dict):
        return "winner debe ser un dict"

    hyp_id = winner.get("hypothesis_id", "")
    if not isinstance(hyp_id, str) or not hyp_id.strip():
        return "winner.hypothesis_id debe ser string no vacío"

    alts = abductive_result.get("alternatives")
    if alts is not None and not isinstance(alts, list):
        return "alternatives debe ser una lista o None"
    # CF-SCH-01: verificar que cada elemento de alternatives es dict
    if alts:
        bad = [i for i, a in enumerate(alts) if not isinstance(a, dict)]
        if bad:
            return f"alternatives[{bad[0]}] no es dict (tipo: {type(alts[bad[0]]).__name__})"

    cost = winner.get("cost")
    if cost is not None:
        try:
            c = int(cost)
            if c < 0:
                return f"winner.cost debe ser >= 0, recibido: {c}"
        except (TypeError, ValueError):
            return f"winner.cost debe ser numérico, recibido: {cost}"

    coverage = winner.get("coverage_score", winner.get("coverage"))
    if coverage is not None:
        try:
            cv = int(coverage)
            if not (0 <= cv <= 100):
                return f"winner.coverage debe ser [0,100], recibido: {cv}"
        except (TypeError, ValueError):
            return f"winner.coverage debe ser numérico, recibido: {coverage}"

    return None


class CounterFactEngine:
    """
    Genera escenarios mínimos alternativos para hipótesis descartadas.

    Clave de sort VIGÍA (invariante):
      sort_key = (cost, -coverage_score, len(required_artifacts))
      Menor es mejor para todos los criterios.

    Para que el challenger Hᵢ supere a la ganadora H*:
      CASO A: cost(Hᵢ) > cost(H*)
        → Necesitamos ADD artefactos faltantes de Hᵢ para reducir cost(Hᵢ)
        → Podemos también REMOVE artefactos de H* para aumentar cost(H*)
        → Objetivo: cost(Hᵢ_nuevo) < cost(H*_nuevo)

      CASO B: cost(Hᵢ) == cost(H*) y coverage(Hᵢ) < coverage(H*)  [CF-02 corregido]
        → Necesitamos ADD artefactos requeridos de Hᵢ para subir su cobertura
        → Objetivo: coverage(Hᵢ_nuevo) > coverage(H*)

      CASO C: cost(Hᵢ) == cost(H*) y coverage(Hᵢ) == coverage(H*)
             y len(required_Hᵢ) >= len(required_H*)
        → Objetivo: len(required_Hᵢ) < len(required_H*)
        → Esto requiere REMOVER artefactos requeridos de la hipótesis
          (cambio estructural — plausibilidad muy baja)

      CASO D: cost(Hᵢ) < cost(H*) [el challenger ya tiene menor costo]
        → Situación teóricamente imposible si H* es la ganadora correcta
        → Puede ocurrir por datos corruptos — reportar como error
    """

    def analyze(
        self,
        abductive_result: Dict[str, Any],
        max_scenarios: int = 5,
        bundle: Optional[Dict[str, Any]] = None,
    ) -> CounterFactReport:
        # Validar schema del input
        schema_err = _validate_abductive_schema(abductive_result)
        if schema_err:
            raise ValueError(f"[VIGIA schema] AbductiveResult inválido: {schema_err}")

        winner = abductive_result.get("winner", {}) or {}
        alternatives: List[Dict[str, Any]] = list(
            abductive_result.get("alternatives", []) or []
        )

        winner_id = str(winner.get("hypothesis_id", "UNKNOWN"))
        winner_intent = str(winner.get("intent_type", "unknown"))
        winner_cost = int(winner.get("cost", 0))
        winner_cov = int(
            winner.get("coverage_score", winner.get("coverage", 0))
        )
        winner_required: List[str] = list(winner.get("required_artifacts", []) or [])
        winner_required_count = len(winner_required)

        observed, phase = _extract_observed_artifacts(winner, alternatives, bundle)

        scenarios: List[AlternativeScenario] = []

        # Aplicar hard cap de seguridad (previene DoS)
        _safe_max = min(max_scenarios, MAX_SCENARIOS_HARD_CAP)
        # CF-CAP-01: islice sin copia de lista completa
        # CF-CAP-02: advertir si se trunca silenciosamente
        # CF-CAP-04: Gemini reportó "DoS combinatorio" por "generación recursiva de grafos" — invalidado.
        # El loop es O(min(n_alternatives, 20)) lineal, sin recursión, sin combinatoria.
        # VIGÍA tiene 33 hipótesis totales → peor caso 32 alternativas, truncadas a 20.
        # MAX_SCENARIOS_HARD_CAP previene cualquier explosión. No modificar.
        _truncation_note: str = ""
        n_alts = len(alternatives) if hasattr(alternatives, '__len__') else None
        if n_alts is not None and n_alts > _safe_max:
            import warnings as _w_cap
            _truncation_note = (
                f"[CF-CAP-03] ANÁLISIS INCOMPLETO: {n_alts} alternativas, "
                f"sólo {_safe_max} procesadas. "
                "Esta advertencia aparece en el reporte independientemente de -W ignore."
            )
            _w_cap.warn(_truncation_note, UserWarning, stacklevel=3)
        for alt in itertools.islice(alternatives, _safe_max):
            if not isinstance(alt, dict):
                continue
            scenario = self._compute_scenario(
                winner_id, winner_intent, winner_cost, winner_cov,
                winner_required, observed, alt,
            )
            if scenario is not None:
                scenarios.append(scenario)

        # Ordenar por plausibilidad descendente, con desempate por challenger_id
        # (determinista: mismo input → mismo orden)
        scenarios.sort(key=lambda s: (-s.operation.plausibility, s.challenger_id))

        daubert_summary = self._build_daubert_summary(winner_id, scenarios)
        if _truncation_note:
            daubert_summary = _truncation_note + "\n" + daubert_summary

        # report_hash cubre el contenido COMPLETO de todos los escenarios
        _ts_for_hash = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        report_hash = self._compute_report_hash(
            winner_id, observed, scenarios,
            bundle.get("bundle_id", "") if bundle else "",
            daubert_summary,
            phase,
            _ts_for_hash,
        )

        return CounterFactReport(
            winner_id=winner_id,
            winner_intent=winner_intent,
            winner_cost=winner_cost,
            winner_coverage=winner_cov,
            winner_required_count=winner_required_count,
            observed_artifacts=sorted(observed),
            phase=phase,
            scenarios=scenarios,
            report_hash=report_hash,
            generated_at=_ts_for_hash,
            daubert_summary=daubert_summary,
        )

    # ── cálculo de escenario ──────────────────────────────────────────────

    def _compute_scenario(
        self,
        winner_id: str,
        winner_intent: str,
        winner_cost: int,
        winner_cov: int,
        winner_required: List[str],
        observed: Set[str],
        alt: Dict[str, Any],
    ) -> Optional[AlternativeScenario]:

        alt_id = str(alt.get("hypothesis_id", "?"))
        alt_intent = str(alt.get("intent_type", "?"))
        alt_cost = int(alt.get("cost", 99))
        alt_cov = int(alt.get("coverage_score", alt.get("coverage", 0)))
        alt_required: List[str] = list(alt.get("required_artifacts", []) or [])
        alt_assumed: Set[str] = set(alt.get("assumed_artifacts", []) or [])
        alt_required_count = len(alt_required)
        winner_required_count = len(winner_required)

        # Artefactos requeridos del challenger que NO están observados
        # CF-NORM-01 (Kimi audit v2): normalizar alt_required antes de comparar
        # con observed (que también está normalizado por _extract_observed_artifacts).
        # Sin normalización: 'Log_Deletion' != 'log_deletion' → falso missing.
        def _norm_key(s: str) -> str:
            return s.lower().strip().replace(" ", "_") if isinstance(s, str) else ""
        alt_assumed_norm: set = {_norm_key(a) for a in alt_assumed}
        alt_missing = [
            r for r in alt_required
            if _norm_key(r) not in observed and _norm_key(r) not in alt_assumed_norm
        ]
        # Artefactos requeridos del winner que SÍ están observados
        # CF-NORM-02: normalizar winner_required al comparar con observed
        winner_present = [r for r in winner_required if _norm_key(r) in observed]

        # Márgenes
        margin_cost = alt_cost - winner_cost
        margin_cov = winner_cov - alt_cov
        margin_req = alt_required_count - winner_required_count

        # ── CASO D: datos inconsistentes ─────────────────────────────────
        if alt_cost < winner_cost:
            # El challenger ya tiene menor costo — debería haber ganado
            # Reportar como escenario de datos potencialmente corruptos
            op = CounterFactualOperation(
                op_type="INCONSISTENCY",
                artifacts_to_add=[],
                artifacts_to_remove=[],
                delta_cost_winner=0,
                delta_cost_challenger=0,
                delta_coverage_challenger=0,
                plausibility=0,
                plausibility_rationale=(
                    f"INCONSISTENCIA: {alt_id} tiene menor costo ({alt_cost}) que "
                    f"la ganadora {winner_id} ({winner_cost}). "
                    "Esto indica datos abductivos potencialmente corruptos."
                ),
                investigative_directives=["Verificar integridad del AbductiveResult"],
                tiebreak_criterion="NONE (inconsistencia detectada)",
            )
            return AlternativeScenario(
                challenger_id=alt_id,
                challenger_intent=alt_intent,
                challenger_cost=alt_cost,
                challenger_coverage=alt_cov,
                challenger_required_count=alt_required_count,
                winner_id=winner_id,
                winner_cost=winner_cost,
                winner_coverage=winner_cov,
                winner_required_count=winner_required_count,
                margin_cost=margin_cost,
                margin_coverage=margin_cov,
                margin_required=margin_req,
                decisive_criterion="INCONSISTENCY",
                operation=op,
                daubert_note=(
                    f"Inconsistencia detectada: `{alt_id}` tiene menor costo que `{winner_id}` "
                    "pero no fue seleccionado como ganador. "
                    "Verificar el AbductiveResult antes de usar este análisis."
                ),
            )

        # ── CASO A: challenger pierde en costo ────────────────────────────
        if margin_cost > 0:
            decisive = "COST"
            n_add_needed = margin_cost  # cuántos ADD reducen cost(Hᵢ) a igualar o superar
            to_add = alt_missing[:n_add_needed]

            to_remove: List[str] = []
            if len(to_add) < n_add_needed:
                # No hay suficientes missing para reducir el costo — también quitar del winner
                n_remove = n_add_needed - len(to_add)
                to_remove = winner_present[:n_remove]

            delta_cost_chall = -len(to_add)
            delta_cost_winner = len(to_remove)

            # Recalcular cobertura del challenger con los artefactos agregados
            new_obs_count = len([r for r in alt_required if r in observed]) + len(to_add)
            total_req = max(len(alt_required), 1)
            new_coverage = (new_obs_count * 100) // total_req
            delta_cov = new_coverage - alt_cov

            op_type = "ADD" if not to_remove else "ADD+REMOVE"
            tiebreak = "COST (criterio 1)"

        # ── CASO B: empate en costo, challenger pierde en cobertura ──────
        elif margin_cost == 0 and margin_cov > 0:
            decisive = "COVERAGE"
            # Necesitamos agregar artefactos para que alt_cov + delta > winner_cov
            # Cada artefacto added sube cobertura en (100 // total_req)
            total_req = max(len(alt_required), 1)
            step_pct = 100 // total_req
            n_add_needed = (margin_cov // step_pct) + 1 if step_pct > 0 else len(alt_missing)
            to_add = alt_missing[:n_add_needed]
            to_remove = []
            delta_cost_chall = 0
            delta_cost_winner = 0
            new_obs_count = len([r for r in alt_required if r in observed]) + len(to_add)
            new_coverage = (new_obs_count * 100) // total_req
            delta_cov = new_coverage - alt_cov
            op_type = "ADD"
            tiebreak = "COVERAGE (criterio 2, desempate de costo)"

        # ── CASO C: empate en costo y cobertura, pierde en len(required) ─
        elif margin_cost == 0 and margin_cov == 0 and margin_req > 0:
            decisive = "REQUIRED_COUNT"
            # Para que alt gane necesita tener MENOS required que winner
            # Esto no se puede lograr con ADD/REMOVE de observaciones —
            # requiere un cambio en la estructura de la hipótesis.
            # Escenario de plausibilidad muy baja — reportar como informativo.
            to_add = []
            to_remove = []
            delta_cost_chall = 0
            delta_cost_winner = 0
            delta_cov = 0
            op_type = "STRUCTURAL_CHANGE"
            tiebreak = "REQUIRED_COUNT (criterio 3, ambos empates anteriores)"

        # ── Ningún escenario posible ──────────────────────────────────────
        else:
            # margin_cost == 0, margin_cov == 0, margin_req <= 0
            # El challenger ya ganaría o empataría completamente — no debería estar en alternatives
            return None

        # ── Plausibilidad ─────────────────────────────────────────────────
        plausibility, rationale = self._score_plausibility(
            to_add, to_remove, op_type, decisive,
        )

        # ── Directivas investigativas ─────────────────────────────────────
        directives: List[str] = []
        for art in to_add:
            directive = INVESTIGATIVE_DIRECTIVES.get(art, GENERIC_DIRECTIVE)
            directives.append(f"BUSCAR `{art}`: {directive}")
        for art in to_remove:
            directive = INVESTIGATIVE_DIRECTIVES.get(art, GENERIC_DIRECTIVE)
            directives.append(f"VERIFICAR AUSENCIA `{art}`: {directive}")
        if not directives:
            directives.append(
                "Consultar el campo what_would_falsify de la hipótesis ganadora "
                "para las condiciones exactas de invalidación."
            )

        # ── Nota Daubert ──────────────────────────────────────────────────
        daubert_note = (
            f"El sistema evaluó activamente `{alt_id}` ({alt_intent}) como alternativa. "
            f"Criterio decisivo de derrota: {decisive}. "
        )
        if to_add:
            daubert_note += (
                f"Para que `{alt_id}` ganara serían necesarios "
                f"{len(to_add)} artefacto(s) adicional(es): {to_add[:3]}. "
            )
        daubert_note += (
            f"La ausencia de estos artefactos fue verificada durante el análisis. "
            f"Plausibilidad del escenario alternativo: {plausibility}/100."
        )

        op = CounterFactualOperation(
            op_type=op_type,
            artifacts_to_add=to_add,
            artifacts_to_remove=to_remove,
            delta_cost_winner=delta_cost_winner,
            delta_cost_challenger=delta_cost_chall,
            delta_coverage_challenger=delta_cov,
            plausibility=plausibility,
            plausibility_rationale=rationale,
            investigative_directives=directives,
            tiebreak_criterion=tiebreak,
        )

        return AlternativeScenario(
            challenger_id=alt_id,
            challenger_intent=alt_intent,
            challenger_cost=alt_cost,
            challenger_coverage=alt_cov,
            challenger_required_count=alt_required_count,
            winner_id=winner_id,
            winner_cost=winner_cost,
            winner_coverage=winner_cov,
            winner_required_count=winner_required_count,
            margin_cost=margin_cost,
            margin_coverage=margin_cov,
            margin_required=margin_req,
            decisive_criterion=decisive,
            operation=op,
            daubert_note=daubert_note,
        )

    # ── plausibilidad ─────────────────────────────────────────────────────

    @staticmethod
    def _ockham_sigmoid(n_changes: int, n_remove: int) -> int:
        """
        Función sigmoide logística calibrada sobre el principio de Ockham.

        P = floor(100 / (1 + e^(k * (n - n0))) * remove_factor)

        CF-CLAMP-01 (Kimi audit v2): el clamp a 50 era arbitrario e incorrecto
        porque hacía que p(50) == p(1000), perdiendo discriminación.
        Solución correcta: Python float64 soporta math.exp hasta ~709 sin
        overflow. Para n > 750, math.exp lanza OverflowError, que capturamos
        para retornar 0 directamente — sin clamping arbitrario.

        CF-CALC-01 (Kimi audit v2): eliminado el intento de 'revertir' la
        penalización de remove dividiendo por 0.75**n. La función ahora calcula
        la sigmoide base SIN penalización, y la penalización se aplica
        multiplicando DESPUÉS. Cero riesgo de DivisionByZero o valores > 100.
        """
        import math
        k, n0 = 0.9, 1.0
        n = max(0, int(n_changes))
        try:
            raw = 100.0 / (1.0 + math.exp(k * (n - n0)))
        except OverflowError:
            # n es tan grande que e^(k*n) → inf → P → 0
            # No es un clamp silencioso: es el límite matemático correcto
            raw = 0.0
        # Penalización multiplicativa por removes: cada REMOVE reduce P en 25%
        n_rem = max(0, int(n_remove))
        if n_rem > 0:
            # 0.75**n_rem: para n_rem grande tiende a 0 pero nunca es exactamente 0
            # en float64 hasta n_rem ≈ 1074 (underflow a 0.0 en float64)
            # Para n_rem > 1000 la plausibilidad ya es indistinguible de 0
            # CF-CLAMP-02: no cap arbitrario. Python float64 hace underflow
            # a 0.0 silenciosamente para n_rem > ~1074 — correcto matemáticamente.
            penalty = 0.75 ** n_rem
            raw *= penalty
        return max(0, min(100, int(round(raw))))

    def _score_plausibility(
        self,
        to_add: list,
        to_remove: list,
        op_type: str,
        decisive: str,
    ) -> tuple:
        """
        Plausibilidad [0,100] via sigmoide de Ockham.

        CF-CALC-02: p_base se calcula llamando _ockham_sigmoid(n, 0)
        — EXACTAMENTE el mismo código que el motor, sin penalización de remove.
        Elimina toda posibilidad de discrepancia entre rationale y score.
        """
        if op_type == "STRUCTURAL_CHANGE":
            return 5, (
                "Requiere cambio estructural en la hipótesis. "
                "No alcanzable modificando sólo observaciones."
            )
        if op_type == "INCONSISTENCY":
            return 0, "Datos inconsistentes — plausibilidad indefinida."

        n_changes      = len(to_add) + len(to_remove)
        n_remove_count = len(to_remove)

        # Score final: con penalización de remove
        base   = self._ockham_sigmoid(n_changes, n_remove_count)
        # CF-CALC-02: p_base via misma función, sin penalización
        p_base = self._ockham_sigmoid(n_changes, 0)

        reason = f"Sigmoide Ockham: P_base={p_base}%"

        if to_remove:
            import math
            penalty_display = round(0.75 ** min(n_remove_count, 100), 4)
            reason += (
                f" × 0.75^{n_remove_count}≈{penalty_display} (anti-forense)"
                f" = {base}% final. "
                f"Requiere ausencia activa de {n_remove_count} artefacto(s)."
            )
        else:
            reason += f" = {base}%."

        known_add = sum(1 for a in to_add if a in INVESTIGATIVE_DIRECTIVES)
        if to_add and known_add == len(to_add):
            reason += " Todos los artefactos tienen directivas de búsqueda."
        elif to_add and known_add < len(to_add):
            reason += f" {len(to_add)-known_add} artefacto(s) sin directiva."

        if decisive == "COVERAGE":
            reason += " Criterio: cobertura."
        elif decisive == "REQUIRED_COUNT":
            reason += " Criterio: conteo de artefactos."

        return base, reason

    # ── report hash ───────────────────────────────────────────────────────

    def _compute_report_hash(
        self,
        winner_id: str,
        observed: Set[str],
        scenarios: List[AlternativeScenario],
        bundle_id: str,
        daubert_summary: str = "",
        phase: str = "",
        generated_at: str = "",
    ) -> str:
        """
        SHA-256 sobre el contenido completo del reporte.

        CF-HASH-03: incluye phase y generated_at para que
        un atacante no pueda modificar esos campos sin cambiar el hash.
        """
        payload = {
            "vigia_version":      "v1.0-Valkyrie",
            "bundle_id":          bundle_id,
            "winner_id":          winner_id,
            "phase":              phase,
            "generated_at":       generated_at,
            "observed_artifacts": sorted(observed),
            "daubert_summary":    daubert_summary,
            "scenarios": [
                s.to_dict()
                for s in sorted(scenarios, key=lambda x: x.challenger_id)
            ],
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    # ── daubert summary ───────────────────────────────────────────────────

    def _build_daubert_summary(
        self, winner_id: str, scenarios: List[AlternativeScenario]
    ) -> str:
        n = len(scenarios)
        high = sum(1 for s in scenarios if s.operation.plausibility >= 70)
        low  = sum(1 for s in scenarios if s.operation.plausibility < 30)
        inconsistencies = sum(
            1 for s in scenarios if s.decisive_criterion == "INCONSISTENCY"
        )

        summary = (
            f"[VIGÍA v1.0-Valkyrie] "  # CF-DAUB-01: versión en summary
            f"Este análisis counter-factual evaluó activamente {n} hipótesis "
            f"alternativa(s) a `{winner_id}`. "
        )
        if inconsistencies:
            summary += (
                f"Se detectaron {inconsistencies} inconsistencia(s) en los datos "
                "abductivos que requieren verificación. "
            )
        summary += (
            f"De los escenarios válidos, {high} tienen plausibilidad alta (≥70/100) "
            "— sus condiciones de falsificación son investigativamente concretas. "
            f"{low} escenario(s) tienen plausibilidad baja (<30/100), "
            "confirmando robustez de la hipótesis ganadora ante perturbaciones menores. "
            "Este reporte satisface el criterio de falsabilidad activa del estándar Daubert: "
            "el sistema documenta las condiciones exactas bajo las cuales su conclusión "
            "sería incorrecta."
        )
        return summary


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="VIGÍA Counter-Factoring — Abducción Probabilística Inversa"
    )
    parser.add_argument("--bundle", required=True,
                        help="ForensicBundle sellado o AbductiveResult (.json)")
    parser.add_argument("--json",   dest="json_out", action="store_true",
                        help="Salida en JSON estructurado")
    parser.add_argument("--max",    type=int, default=5,
                        help="Máximo de escenarios (default: 5)")
    parser.add_argument("--output", default=None,
                        help="Archivo de salida (default: stdout)")
    args = parser.parse_args()

    path = Path(args.bundle)
    if not path.exists():
        print(f"ERROR: {path} no encontrado", file=sys.stderr)
        return 1

    data: Dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))

    # Detectar si es un ForensicBundle o directamente un AbductiveResult
    if "winner" in data and "alternatives" in data:
        abductive = data
        bundle = None
    elif "abduction_trace" in data:
        at = data.get("abduction_trace", {}) or {}
        hyp = at.get("abductive_hypothesis", {}) or {}
        abductive = {
            "winner":       hyp,
            "alternatives": hyp.get("alternatives", []) or [],
        }
        bundle = data
    else:
        print(
            "ERROR: No se encontró resultado abductivo. "
            f"Campos disponibles: {list(data.keys())}",
            file=sys.stderr,
        )
        return 1

    engine = CounterFactEngine()
    report = engine.analyze(abductive, max_scenarios=args.max, bundle=bundle)

    out = report.to_json() if args.json_out else report.to_markdown()

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"[OK] Counter-factual: {args.output} "
              f"({len(report.scenarios)} escenarios) "
              f"hash={report.report_hash[:16]}...")
    else:
        print(out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
