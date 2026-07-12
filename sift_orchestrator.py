# sift_orchestrator.py — shim de compatibilidad para vigia_agent.py
from __future__ import annotations

import ipaddress
import json
import logging
import os
import re
import subprocess
import sys

from vigia.sift.memory_forensics import vol3_effective_timeout as _vol3_eff_timeout
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# B-075 / P2-C (Fase 1, 2026-07-05): mapa veredicto-del-motor → hipótesis del
# agente. Es la tabla de correspondencia entre el espacio de veredictos del
# scorer canónico (vigia_scorer._vigia_score) y el espacio de hipótesis que
# consumen classify_agent_verdict (substring match) y el comparador batch
# (run_all_agent._MAP). UNKNOWN del motor ("anomalía débil, requiere análisis
# humano") va a UNDETERMINED, que classify_agent_verdict resuelve a ABSTAIN —
# honesto: el motor no formó opinión.
# ─────────────────────────────────────────────────────────────────────────────
_MOTOR_HYPOTHESIS_MAP: Dict[str, str] = {
    "MALICE":    "MALICIOUS_INTENT_DETECTED",
    "SUSPICION": "SUSPICION_DETECTED",
    "UNKNOWN":   "UNDETERMINED",
    "ABSTAIN":   "ABSTAIN_DETECTED",
    "NOISE":     "NO_SEMIOTIC_ANOMALY_DETECTED",
    "ERROR":     "PIPELINE_ERROR",
}

# IPv4/IPv6 en el output de Volatility3 netscan (columnas separadas por espacios)
_IP_TOKEN_RE = re.compile(
    r"\b(?:\d{1,3}(?:\.\d{1,3}){3}|[0-9a-fA-F:]{2,}:[0-9a-fA-F:]*)\b"
)


def _is_external_ip(ip_str: str) -> bool:
    """
    True si la IP es enrutable en internet (candidata a C2/exfil).

    FIX (auditoría FN, P1-C): reemplaza el filtro por substring
    `any(ip in linea for ip in ["10.", "::", ...])`, que clasificaba como
    internas IPs externas legítimas con la subcadena de una red privada —
    p.ej. 85.10.20.30 (contiene "10."), 45.155.10.99, o casi cualquier IPv6
    (contiene "::"). Esas conexiones C2 se descartaban silenciosamente.
    Ahora se decide por red real con el módulo ipaddress.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    # is_global = enrutable en el internet público. Excluye en un solo check
    # privado, loopback, link-local, multicast, unspecified, reservado,
    # documentación (RFC 5737: 203.0.113.0/24, etc.) y CGNAT — todos los
    # rangos no enrutables que un C2 real nunca usaría como destino.
    return ip.is_global


def _netscan_has_external_conn(line: str) -> bool:
    """
    Dada una línea de netscan, extrae la IP foránea (segunda IP de la línea:
    LocalAddr, ForeignAddr) y decide si es externa.

    Conservador ante ambigüedad: si no se pueden extraer dos IPs, se trata la
    conexión como externa (no se descarta) — preferimos un falso positivo
    revisable a un falso negativo silencioso de C2.
    """
    ips = _IP_TOKEN_RE.findall(line)
    # Filtrar tokens que no parsean como IP (evita capturar timestamps raros)
    valid = [t for t in ips if _safe_ip(t) is not None]
    if len(valid) >= 2:
        foreign = valid[1]  # LocalAddr, ForeignAddr
        return _is_external_ip(foreign)
    if len(valid) == 1:
        return _is_external_ip(valid[0])
    return True  # no se pudo determinar → conservar (posible C2)


def _safe_ip(token: str) -> Optional[ipaddress._BaseAddress]:
    try:
        return ipaddress.ip_address(token)
    except ValueError:
        return None

# Vol3 binary: buscar en venv primero
_VOL3 = str(Path(sys.executable).parent / "vol")
if not Path(_VOL3).exists():
    _VOL3 = "vol3"


def _unanalyzed_marker(engine: str, error: Exception) -> Dict[str, Any]:
    """
    B-089 (N14, superficie shim): marcador de artefacto mobile NO ANALIZADO
    cuando su analyzer crashea — el equivalente dict del `_unanalyzed_signal`
    F7 del orquestador real. z=0 y signal_class=derived: no cuenta para
    gates ni escalación del merge; solo hace visible la pérdida (0 hallazgos
    sobre evidencia no analizada NO es evidencia de benignidad).
    """
    return {
        "tool": f"{engine.upper()}_UNANALYZED",
        "z_score": 0.0,
        "confidence": 0.0,
        "value": 0.0,
        "metadata": {
            "artifact_type": engine,
            "unanalyzed": True,
            "signal_class": "derived",
            "error": f"{type(error).__name__}: {error}"[:200],
        },
    }


def _motor_caie_summary(motor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    B-094: traduce la CAIE viva del scorer (_vigia_score) al shape que la
    narrativa del agente consume en `results["caie"]` — el mismo canal que
    B-041a abrió para la CAIE del orquestador. Sin esto, un veredicto no-NOISE
    causado por una fractura queda sin explicación en la narrativa sellada
    (anti-patrón Daubert). Devuelve None si el motor no reportó fracturas
    (nada que surfacear; la narrativa no inventa un bloque CAIE vacío).

    Fiel a lo que el scorer computó: NO fabrica un structural_verdict ni un
    composite CAIE separado (el scorer aplica un boost al composite global, no
    corre el veredicto estructural completo del orquestador). Reporta las
    fracturas reales y el boost aplicado.
    """
    if not isinstance(motor, dict):
        return None
    details = motor.get("caie_fracture_details") or []
    n = int(motor.get("caie_fractures", 0) or 0)
    if n <= 0 and not details:
        return None
    boost = motor.get("fracture_malice_boost", 0.0)
    fractures = [
        {
            "type": f.get("fracture_type", "?"),
            "severity": f.get("severity", "?"),
            "interpretation": f.get("interpretation", ""),
            "ttp_id": f.get("ttp_id", ""),
        }
        for f in details if isinstance(f, dict)
    ]
    return {
        "status": "OK",
        "source": "motor_live_caie",
        "fractures_detected": n,
        "fractures": fractures,
        "fracture_malice_boost": str(boost),
        "daubert_note": (
            f"{n} fractura(s) CAIE viva(s) contribuyeron al veredicto "
            f"(boost +{boost} aplicado al composite del scorer). "
            f"Fuente: vigia_scorer._vigia_score (B-094)."
        ),
    }


def _mobile_hypothesis(mobile_signals: List[Dict[str, Any]]) -> tuple:
    """
    F6 (AUDITORIA_PIPELINE_ROBUSTEZ, N5): deriva la hipótesis mobile de los
    z-scores reales — no de una etiqueta fija. Antes MOBILE_EVIDENCE_ANALYZED
    con is_conclusive=len(signals)>0 clasificaba SIEMPRE NOISE (exit 0),
    incluso con hallazgos z>3 (el override L-036 tampoco aplicaba porque la
    hipótesis no estaba en su lista de disparo).

    Mapping (mismo criterio que el adaptador vol3 + gate Daubert de 2 fuentes
    para MALICIOUS):
      ≥2 señales z>3  → MALICIOUS_INTENT_DETECTED
      max z > 3       → INTENT_DETECTED
      max z > 2       → SUSPICION_DETECTED
      resto           → MOBILE_EVIDENCE_ANALYZED (con is_conclusive=False:
                        1-2 señales limpias no bastan para afirmar benigno —
                        el agente abstiene por el gate <3)

    Returns: (hypothesis, max_z: Fraction, is_conclusive: bool, n_critical: int)
    """
    z_values = []
    for s in mobile_signals:
        try:
            z_values.append(abs(Fraction(str(s.get("z_score", 0)))))
        except (ValueError, ZeroDivisionError):
            z_values.append(Fraction(0, 1))
    max_z = max(z_values) if z_values else Fraction(0, 1)
    n_critical = sum(1 for z in z_values if z > Fraction(3, 1))

    if n_critical >= 2:
        hypothesis = "MALICIOUS_INTENT_DETECTED"
    elif max_z > Fraction(3, 1):
        hypothesis = "INTENT_DETECTED"
    elif max_z > Fraction(2, 1):
        hypothesis = "SUSPICION_DETECTED"
    else:
        hypothesis = "MOBILE_EVIDENCE_ANALYZED"
    is_conclusive = max_z > Fraction(3, 1)
    return hypothesis, max_z, is_conclusive, n_critical


# §9.4-LIM (decisión sellada 2026-07-10, opción (ii) pura + extensión de
# narrativa): texto doctrinal EXACTO para la clase D3_RICH_NO_TRIANGULATION.
_D3_TRIANGULATION_NOTE = (
    "[§9.4-LIM] SUSPICION — evidencia de filesystem robusta y multi-vector, "
    "pero confinada a un único canal físico (D3). El motor NO puede confirmar "
    "MALICE sin una segunda fuente independiente (memoria, red, o contenido). "
    "Se recomienda triangulación manual urgente antes de descartar el caso."
)


def _mobile_suspicion_class(mobile_signals: List[Dict[str, Any]],
                            max_z: Fraction) -> str:
    """
    §9.4-LIM: clasifica la situación probatoria de la ruta mobile-only en dos
    clases que hoy son indistinguibles para el analista humano:

      "GENERIC"                  — poca evidencia / ambigüedad real.
      "D3_RICH_NO_TRIANGULATION" — anomalías fuertes pero TODAS confinadas al
                                   canal físico D3 (filesystem local); por
                                   doctrina (ii) el motor no puede escalar sin
                                   una segunda fuente independiente (D2/D4/D5).

    Regla exacta (docs/B052_P2_DESIGN.md §10):
      cond2 := >=1 señal analizada (unanalyzed no cuenta)
               AND todas las analizadas resuelven dominio D3
                   (evidence_type|artifact_type → _EVIDENCE_MAP → _DOMAIN_MAP)
               AND max_z > 3   (mismo umbral crítico que _mobile_hypothesis)
               AND >=2 finding_types distintos (unión sobre señales)

    Fail-closed: dominio no resoluble o mapas no importables → GENERIC.
    SOLO clasifica — no toca hypothesis, score ni veredicto (narrativa +
    pipeline_meta; gate comparativo 0 flips pineado en tests).
    """
    try:
        from vigia.core.forensic_adapter import _EVIDENCE_MAP
        from vigia.tools.caie import _DOMAIN_MAP
    except Exception:
        return "GENERIC"

    analyzed = [s for s in mobile_signals
                if not (s.get("metadata") or {}).get("unanalyzed")]
    if not analyzed or max_z <= Fraction(3, 1):
        return "GENERIC"

    finding_types: set = set()
    for s in analyzed:
        meta = s.get("metadata") or {}
        ev = meta.get("evidence_type")
        if not ev:
            at = str(meta.get("artifact_type", "")).lower()
            ev = _EVIDENCE_MAP.get(at)
        domain = _DOMAIN_MAP.get(str(ev).lower()) if ev else None
        if not domain or domain[1] != "D3":
            return "GENERIC"
        finding_types.update(str(t) for t in (meta.get("finding_types") or []))

    if len(finding_types) < 2:
        return "GENERIC"
    return "D3_RICH_NO_TRIANGULATION"


class SIFTOrchestrator:
    """
    Shim de compatibilidad.
    - JSON EBS v1     → adaptador interno (sin herramientas externas)
    - memory_path     → vol3 local (LaBestia tiene vol3 en venv)
    - disk/mixed      → SIFTOrchestrator real (requiere rip.pl + SIFT conectado)
    """

    def __init__(self, case_id: str):
        self.case_id = case_id
        # L-037: examiner-declared acquisition metadata, set by vigia_agent.py
        self.acquisition_overrides: Dict[str, Any] = {}

    def analyze(self, **kwargs) -> Dict[str, Any]:
        # B-045: run mobile forensic engines (Android/iOS) independently.
        # These produce their own signals and merge into the final result.
        mobile_signals = self._analyze_mobile(kwargs)

        log_path = kwargs.get("log_path")
        if log_path and str(log_path).endswith(".json"):
            try:
                result = self._analyze_ebs_json(str(log_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] EBS JSON adapter failed: %s", e)
                result = self._error_result(str(e))
            return self._merge_mobile_signals(result, mobile_signals)

        memory_path = kwargs.get("memory_path")
        # Si el scanner de directorios devolvió una lista, tomar el primer elemento
        if isinstance(memory_path, list):
            memory_path = memory_path[0] if memory_path else None
        disk_path = kwargs.get("disk_path")
        if isinstance(disk_path, list):
            disk_path = disk_path[0] if disk_path else None

        # Auto-detección de memoria por extensión si el caller no pasó memory_path
        # explícitamente (compatibilidad con agentes que usan evidence_path/evidence).
        if not memory_path and not disk_path:
            for _k in ("evidence_path", "evidence", "log_path"):
                _v = kwargs.get(_k)
                if _v:
                    _p = Path(str(_v[0] if isinstance(_v, list) else _v))
                    if _p.suffix.lower() in (".img", ".vmem", ".raw", ".mem", ".dmp"):
                        memory_path = str(_p)
                        logger.info("[SIFT_SHIM] Auto-detected memory image via kwarg '%s': %s", _k, memory_path)
                        break

        # Evidencia de memoria sin disco → vol3 local, no necesita rip.pl
        if memory_path and not disk_path:
            logger.info("[SIFT_SHIM] Memory-only evidence → vol3 local adapter")
            try:
                result = self._analyze_memory_vol3(str(memory_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] vol3 memory analysis failed: %s", e)
                result = self._error_result(str(e))
            # B1-a (AUDITORIA_SHIM_RUTEO): esta rama analiza SOLO la memoria con
            # vol3. Cualquier otro artefacto detectado en la misma evidencia
            # (evtx, hives, pcap, mft, browser, prefetch) NO se ve en esta ruta.
            # Materializar la pérdida (patrón F7) para que "solo memoria" no se
            # selle como cobertura completa. No recupera las señales; las hace
            # visibles → degradación honesta, no silenciosa.
            self._mark_memory_only_dropped(result, kwargs)
            return self._merge_mobile_signals(result, mobile_signals)

        # B-045: if only mobile evidence is present (no Windows artifacts),
        # return mobile signals directly without falling through to the real orchestrator.
        has_windows_evidence = any(kwargs.get(k) for k in (
            "memory_path", "disk_path", "event_logs", "event_stream",
            "registry_hives", "pcap_path", "network_flows", "log_path",
            "browser_profile", "prefetch_dir", "mft_path", "mft_json",
        ))
        if not has_windows_evidence and mobile_signals:
            # F6 (N5): hipótesis derivada de los z reales — antes la etiqueta
            # fija MOBILE_EVIDENCE_ANALYZED clasificaba NOISE aunque hubiera
            # hallazgos z>3. Narrativa Peircean de 3 capas (F4).
            hypothesis, max_z, is_conclusive, n_critical = _mobile_hypothesis(mobile_signals)
            # B-089: los marcadores *_UNANALYZED no son engines que analizaron
            # — el inventario FIRSTNESS lista solo señales reales; la pérdida
            # va en [FIRSTNESS-LOSS] (contradicción clase N12 si se mezclan).
            _engines = sorted({
                str(s.get("tool", "?")) for s in mobile_signals
                if not (s.get("metadata") or {}).get("unanalyzed")
            })
            _posterior = min(max_z / Fraction(5, 1), Fraction(99, 100))
            # B-089 (N14 shim): artefactos mobile cuyo analyzer crasheó —
            # visibles en results.unanalyzed_artifacts (misma vía que el
            # orquestador real) para que _signal_stats/narrativa los vean.
            _unanalyzed_types = sorted({
                str((s.get("metadata") or {}).get("artifact_type",
                                                  s.get("tool", "?")))
                for s in mobile_signals
                if (s.get("metadata") or {}).get("unanalyzed")
            })
            _n_analyzed = len(mobile_signals) - sum(
                1 for s in mobile_signals
                if (s.get("metadata") or {}).get("unanalyzed")
            )

            # B-052 P1 (AUDITORIA_MACOS_NARRATIVA.md §4): FIRSTNESS con el
            # detalle real de hallazgos por engine (los metadata ya lo traen),
            # y declaración explícita de por qué el motor abductivo v2 no
            # corre en esta ruta — la ausencia de inferencia abductiva es una
            # limitación de diseño documentada, no un error de pipeline.
            _finding_bits = []
            for _s in mobile_signals:
                _meta = _s.get("metadata") or {}
                _fc = _meta.get("findings_count")
                if _fc is None:
                    continue
                _bit = f"{_s.get('tool', '?')}: {_fc} finding(s)"
                _ftypes = _meta.get("finding_types") or []
                if _ftypes:
                    _bit += f" [{', '.join(str(t) for t in _ftypes[:4])}]"
                _finding_bits.append(_bit)

            # §9.4-LIM: clase de SUSPICION — narrativa + pipeline_meta, y
            # (enforcement firmado 2026-07-10) techo de veredicto: cuando la
            # evidencia fuerte está TODA confinada a D3, el veredicto sellado
            # se capea en SUSPICION vía abduction.verdict_ceiling (el cap lo
            # aplica classify_agent_verdict, el camino único de sellado). La
            # hipótesis cruda del engine NO se falsea — patrón REFUTATION
            # GATE: autocorrección pre-emisión, documentada en la narrativa.
            _susp_class = _mobile_suspicion_class(mobile_signals, max_z)
            _ceiling_fields: Dict[str, Any] = {}
            _gate_log = ""
            if (_susp_class == "D3_RICH_NO_TRIANGULATION"
                    and hypothesis in ("INTENT_DETECTED",
                                       "MALICIOUS_INTENT_DETECTED")):
                _ceiling_fields = {
                    "verdict_ceiling": "SUSPICION",
                    "verdict_ceiling_reason": (
                        "§9.4-LIM: evidencia fuerte confinada al canal D3 "
                        "(sin triangulación D2/D4/D5) — techo doctrinal "
                        "SUSPICION (L-051)."
                    ),
                }
                _gate_log = (
                    "\nREFUTATION GATE LOG — §9.4-LIM\n"
                    f"  Candidato : {hypothesis} (max_z={float(max_z):.2f})\n"
                    "  Gate      : techo D3-only sin triangulación "
                    "(verdict_ceiling=SUSPICION, L-051)\n"
                    "  Resultado : candidato CAPEADO pre-emisión → el "
                    "veredicto sellado es SUSPICION. La hipótesis cruda se "
                    "preserva arriba; el LLM no puede anular este gate."
                )

            result = {
                "case_id": self.case_id,
                "signals": mobile_signals,
                "abduction": {
                    "best_hypothesis": hypothesis,
                    "is_conclusive": is_conclusive,
                    "confidence": str(_posterior),
                    "best_posterior": str(_posterior),
                    "narrative": (
                        (f"[FIRSTNESS] Mobile forensic evidence analyzed: "
                           f"{_n_analyzed} signal(s) extracted "
                           f"(engines: {', '.join(_engines)})."
                           if _n_analyzed else
                           "[FIRSTNESS] 0 señales mobile analizadas.")
                        + (f" Hallazgos: {'; '.join(_finding_bits)}."
                           if _finding_bits else "") + "\n"
                        + (f"[FIRSTNESS-LOSS] {len(_unanalyzed_types)} "
                           f"artefacto(s) mobile NO analizado(s) — analyzer "
                           f"crasheó: {', '.join(_unanalyzed_types)}. 0 "
                           f"hallazgos sobre evidencia no analizada NO es "
                           f"evidencia de benignidad.\n"
                           if _unanalyzed_types else "")
                        + f"[SECONDNESS] Max z-score: "
                        f"{float(max_z):.2f}; señales críticas (z>3): {n_critical}.\n"
                        f"[THIRDNESS] Hipótesis: {hypothesis}. "
                        + ("Anomalía estructural en evidencia mobile — revisión prioritaria."
                           if max_z > Fraction(2, 1) else
                           "Sin desviación sobre umbral — fuente única, sin base "
                           "para afirmar benignidad concluyente (gate <3 fuentes).")
                        + "\n"
                        "Motor abductivo v2: NO ejecutado en esta ruta "
                        "(adaptador mobile de fuente única). El razonador "
                        "requiere ≥3 fuentes primarias independientes y cada "
                        "engine de dispositivo emite una única señal agregada. "
                        "Esto es una limitación de diseño documentada "
                        "(B-052, AUDITORIA_MACOS_NARRATIVA.md), no un error "
                        "de pipeline."
                        + ("\n" + _D3_TRIANGULATION_NOTE
                           if _susp_class == "D3_RICH_NO_TRIANGULATION" else "")
                        + _gate_log
                    ),
                    **_ceiling_fields,
                },
                "results": (
                    {"unanalyzed_artifacts": _unanalyzed_types}
                    if _unanalyzed_types else {}
                ),
                "pipeline_meta": {
                    "source": "mobile_forensics_adapter",
                    "n_mobile_signals": len(mobile_signals),
                    "n_mobile_unanalyzed": len(_unanalyzed_types),
                    "n_total_signals": len(mobile_signals),
                    "max_mobile_z": str(max_z),
                    # B-052 P1: estado del razonador explícito y consultable —
                    # distingue "no corrió por diseño" de "corrió y falló".
                    "abductive_reasoner": "NOT_RUN_MOBILE_SINGLE_SOURCE",
                    # §9.4-LIM: GENERIC | D3_RICH_NO_TRIANGULATION — consultable
                    # por el analista sin parsear la narrativa.
                    "suspicion_class": _susp_class,
                    # enforcement del techo (True solo cuando el cap se declaró)
                    "s94_lim_enforced": bool(_ceiling_fields),
                },
            }
            return result

        # Disk or mixed → real orchestrator via run_full_analysis
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from vigia.sift.sift_orchestrator import SIFTOrchestrator as _Real
            real = _Real(self.case_id)
            # L-037: propagate examiner-declared acquisition overrides
            if self.acquisition_overrides:
                real.acquisition_overrides = self.acquisition_overrides

            # Map shim kwargs → run_full_analysis parameters
            run_kwargs: Dict[str, Any] = {}
            if kwargs.get("memory_path"):
                run_kwargs["memory_dump_path"] = kwargs["memory_path"]
            es = kwargs.get("event_stream") or kwargs.get("event_logs")
            if es:
                run_kwargs["event_logs"] = es if isinstance(es, list) else [es]
            lp = kwargs.get("log_path")
            if lp and not str(lp).endswith(".json") and not run_kwargs.get("event_logs"):
                run_kwargs["event_logs"] = lp if isinstance(lp, list) else [lp]
            if kwargs.get("network_flows"):
                run_kwargs["network_flows"] = kwargs["network_flows"]
            pcap_path = kwargs.get("pcap_path")
            if isinstance(pcap_path, list):
                pcap_path = pcap_path[0] if pcap_path else None
            pcap_error: Optional[str] = None
            if pcap_path and not run_kwargs.get("network_flows"):
                try:
                    from vigia.sift.pcap_parser import parse_pcap_to_flows
                    pcap_flows = parse_pcap_to_flows(str(pcap_path))
                    if pcap_flows:
                        run_kwargs["network_flows"] = pcap_flows
                        logger.info("[SIFT_SHIM] Parsed %d flows from pcap: %s", len(pcap_flows), pcap_path)
                except Exception as e:
                    # B-053/T-3 FIX (TRIAGE 2026-07-03): antes este `raise`
                    # caía al except global de analyze() → PIPELINE_ERROR
                    # para el caso ENTERO — un pcap corrupto (o tshark
                    # ausente, L-039) descartaba también los evtx/hives que
                    # SÍ podían analizarse. Ahora el pcap se marca como
                    # UNANALYZED (patrón F7) y el resto de la evidencia
                    # continúa; el veredicto degrada a ABSTAIN solo si no
                    # queda ninguna otra señal (gate N8/F7).
                    logger.error("[SIFT_SHIM] pcap parsing failed for %s: %s", pcap_path, e)
                    pcap_error = f"{type(e).__name__}: {e}"
            rh = kwargs.get("registry_hives")
            if rh:
                run_kwargs["registry_hives"] = rh if isinstance(rh, list) else [rh]
            # Browser profile (Chromium History / Firefox places.sqlite) — parser
            # SQLite real (P1-A). Se pasa el directorio del perfil.
            bp = kwargs.get("browser_profile")
            if bp:
                run_kwargs["browser_profile"] = bp[0] if isinstance(bp, list) else bp
            # Prefetch directory (P1-B) — parser real por nombre de ejecutable.
            pd = kwargs.get("prefetch_dir")
            if pd:
                run_kwargs["prefetch_dir"] = pd[0] if isinstance(pd, list) else pd
            # $MFT (P0-C): parsear el binario a JSON para el analyzer. Antes
            # MFT/disco quedaba ciego en modo agente — falso negativo.
            mp = kwargs.get("mft_path")
            if isinstance(mp, list):
                mp = mp[0] if mp else None
            if mp:
                try:
                    from vigia.sift.mft_parser import parse_mft_file
                    run_kwargs["mft_json"] = parse_mft_file(str(mp))
                    logger.info("[SIFT_SHIM] Parsed $MFT: %s", mp)
                except Exception as e:
                    logger.error("[SIFT_SHIM] MFT parsing failed for %s: %s", mp, e)
            elif kwargs.get("mft_json"):
                run_kwargs["mft_json"] = kwargs["mft_json"]

            # disk_path (E01) has no direct mapping — requires prior mounting
            # and artifact extraction (ewfmount + registry hive extraction)
            if kwargs.get("disk_path") and not run_kwargs:
                logger.warning(
                    "[SIFT_SHIM] E01 requires prior mounting. "
                    "Mount with ewfmount, extract hives, then pass artifacts directly."
                )
                return self._merge_mobile_signals(
                    self._error_result(
                        "E01 disk image requires prior artifact extraction. "
                        "Mount with ewfmount and pass registry_hives/event_logs explicitly."
                    ),
                    mobile_signals,
                )

            result = real.run_full_analysis(**run_kwargs)

            # B-053/T-3: si el pcap no se pudo parsear, materializar la
            # pérdida en el resultado — señal sintética + lista de artefactos
            # no analizados. Integra con F7: sección "ARTEFACTOS NO
            # ANALIZADOS" en la narrativa y NOISE→ABSTAIN si aplica.
            if pcap_error:
                result.setdefault("signals", []).append({
                    "tool": "PCAP_UNANALYZED",
                    "z_score": 0.0,
                    "confidence": 0.0,
                    "value": 0.0,
                    "metadata": {
                        "artifact_type": "pcap",
                        "unanalyzed": True,
                        "signal_class": "derived",
                        "error": pcap_error[:200],
                        "path": str(pcap_path),
                    },
                })
                _inner = result.setdefault("results", {})
                if isinstance(_inner, dict):
                    _ua = _inner.setdefault("unanalyzed_artifacts", [])
                    if "pcap" not in _ua:
                        _ua.append("pcap")
                _meta = result.setdefault("pipeline_meta", {})
                _meta["pcap_error"] = pcap_error[:200]

            return self._merge_mobile_signals(result, mobile_signals)
        except Exception as e:
            logger.error("[SIFT_SHIM] Real orchestrator failed: %s", e)
            return self._merge_mobile_signals(self._error_result(str(e)), mobile_signals)

    # ── Mobile forensics (B-045) ────────────────────────────────────────

    def _analyze_mobile(self, kwargs: Dict[str, Any]) -> list:
        """Run Android/iOS forensic engines if evidence paths are present."""
        signals = []

        android_path = kwargs.get("android_evidence_path")
        if android_path:
            try:
                from vigia.sift.android_forensics import AndroidForensicsAnalyzer
                analyzer = AndroidForensicsAnalyzer()
                result = analyzer.analyze(Path(android_path))
                sig = result.to_signal()
                if sig and (sig.z_score > 0 or result.findings or result.total_sms > 0):
                    sig_dict = {
                        "tool": sig.tool_name,
                        "z_score": sig.z_score,
                        "confidence": sig.confidence,
                        "value": sig.value,
                        # F5: señal de artefacto real → primaria (cuenta para
                        # gates de corroboración y override L-036 del agente).
                        "metadata": {
                            **(sig.metadata or {}),
                            "signal_class": "primary",
                        },
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] Android engine: %d findings, %d SMS, z=%.2f",
                        len(result.findings), result.total_sms, sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] AndroidForensicsAnalyzer failed: %s", e)
                signals.append(_unanalyzed_marker("android", e))

        ios_path = kwargs.get("ios_evidence_path")
        # B-048 precedence: if the same directory also matched macOS strong
        # markers, run only the macOS engine — shared Safari artifacts
        # (History.db) would otherwise be processed and counted by both.
        if ios_path and ios_path == kwargs.get("macos_evidence_path"):
            logger.warning(
                "[SIFT_SHIM] iOS engine skipped for %s: directory also matched "
                "macOS strong markers; macOS engine takes precedence to avoid "
                "double-counting shared Safari artifacts (B-048).",
                ios_path,
            )
            ios_path = None
        if ios_path:
            try:
                from vigia.sift.ios_forensics import iOSForensicsAnalyzer
                analyzer = iOSForensicsAnalyzer()
                result = analyzer.analyze(Path(ios_path))
                sig = result.to_signal()
                if sig and (sig.z_score > 0 or result.findings or result.total_sms > 0):
                    sig_dict = {
                        "tool": sig.tool_name,
                        "z_score": sig.z_score,
                        "confidence": sig.confidence,
                        "value": sig.value,
                        # F5: señal de artefacto real → primaria (cuenta para
                        # gates de corroboración y override L-036 del agente).
                        "metadata": {
                            **(sig.metadata or {}),
                            "signal_class": "primary",
                        },
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] iOS engine: %d findings, %d SMS, z=%.2f",
                        len(result.findings), result.total_sms, sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] iOSForensicsAnalyzer failed: %s", e)
                signals.append(_unanalyzed_marker("ios", e))

        # B-046: Google Takeout forensics
        takeout_path = kwargs.get("takeout_evidence_path")
        if takeout_path:
            try:
                from vigia.sift.google_takeout_forensics import GoogleTakeoutForensicsAnalyzer
                analyzer = GoogleTakeoutForensicsAnalyzer()
                result = analyzer.analyze(Path(takeout_path))
                sig = result.to_signal()
                if sig and (sig.z_score > 0 or result.findings):
                    sig_dict = {
                        "tool": sig.tool_name,
                        "z_score": sig.z_score,
                        "confidence": sig.confidence,
                        "value": sig.value,
                        # F5: señal de artefacto real → primaria (cuenta para
                        # gates de corroboración y override L-036 del agente).
                        "metadata": {
                            **(sig.metadata or {}),
                            "signal_class": "primary",
                        },
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] Google Takeout engine: %d findings, z=%.2f",
                        len(result.findings), sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] GoogleTakeoutForensicsAnalyzer failed: %s", e)
                signals.append(_unanalyzed_marker("takeout", e))

        # B-048: macOS forensics
        macos_path = kwargs.get("macos_evidence_path")
        if macos_path:
            try:
                from vigia.sift.macos_forensics import MacOSForensicsAnalyzer
                analyzer = MacOSForensicsAnalyzer()
                result = analyzer.analyze(Path(macos_path))
                sig = result.to_signal()
                if sig and (sig.z_score > 0 or result.findings):
                    sig_dict = {
                        "tool": sig.tool_name,
                        "z_score": sig.z_score,
                        "confidence": sig.confidence,
                        "value": sig.value,
                        # F5: señal de artefacto real → primaria (cuenta para
                        # gates de corroboración y override L-036 del agente).
                        "metadata": {
                            **(sig.metadata or {}),
                            "signal_class": "primary",
                        },
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] macOS engine: %d findings, z=%.2f",
                        len(result.findings), sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] MacOSForensicsAnalyzer failed: %s", e)
                signals.append(_unanalyzed_marker("macos", e))

        return signals

    @staticmethod
    def _merge_mobile_signals(result: Dict[str, Any], mobile_signals: list) -> Dict[str, Any]:
        """
        Merge mobile forensic signals into an existing pipeline result.

        F6 (AUDITORIA_PIPELINE_ROBUSTEZ, N6): las señales mobile se fusionan
        DESPUÉS de que la abducción del pipeline Windows ya se computó — la
        escalación explícita de abajo evita que un hallazgo mobile crítico
        (z>3) quede silenciado por un veredicto benigno/indeterminado del
        resto de la evidencia.
        """
        if not mobile_signals:
            return result
        existing = result.get("signals", [])
        if isinstance(existing, list):
            result["signals"] = existing + mobile_signals
        meta = result.get("pipeline_meta", {})
        meta["n_mobile_signals"] = len(mobile_signals)
        if "n_total_signals" in meta:
            meta["n_total_signals"] = meta["n_total_signals"] + len(mobile_signals)
        result["pipeline_meta"] = meta

        # B-089 (N14 shim): los marcadores *_UNANALYZED del camino mobile
        # entran a results.unanalyzed_artifacts del resultado base — la vía
        # que _signal_stats/narrativa consumen (misma forma que el
        # orquestador real: lista ordenada de artifact_type).
        _mob_unanalyzed = sorted({
            str((s.get("metadata") or {}).get("artifact_type",
                                              s.get("tool", "?")))
            for s in mobile_signals
            if (s.get("metadata") or {}).get("unanalyzed")
        })
        if _mob_unanalyzed:
            inner = result.get("results")
            if not isinstance(inner, dict):
                inner = {}
                result["results"] = inner
            existing_unanalyzed = inner.get("unanalyzed_artifacts") or []
            inner["unanalyzed_artifacts"] = sorted(
                set(existing_unanalyzed) | set(_mob_unanalyzed)
            )
            meta["n_mobile_unanalyzed"] = len(_mob_unanalyzed)

        hypothesis, max_z, _concl, n_critical = _mobile_hypothesis(mobile_signals)
        abduction = result.get("abduction")
        if isinstance(abduction, dict) and max_z > Fraction(3, 1):
            current = str(abduction.get("best_hypothesis") or "").upper()
            already_flagged = any(
                k in current for k in
                ("MALICIOUS", "INTENT", "SUSPICION", "CRITICAL", "OVERRIDE")
            )
            if not already_flagged:
                escalated = ("MALICIOUS_INTENT_DETECTED"
                             if n_critical >= 2 else "INTENT_DETECTED")
                abduction["mobile_escalation"] = {
                    "from": abduction.get("best_hypothesis"),
                    "to": escalated,
                    "max_mobile_z": str(max_z),
                    "n_critical_mobile": n_critical,
                }
                abduction["best_hypothesis"] = escalated
                abduction["is_conclusive"] = True
                abduction["narrative"] = (
                    (abduction.get("narrative") or "")
                    + f"\n[MOBILE] Escalación determinista: {len(mobile_signals)} "
                      f"señal(es) mobile con max z={float(max_z):.2f} > 3 — "
                      f"hipótesis elevada a {escalated} "
                      f"(era: {abduction['mobile_escalation']['from']})."
                )
                meta["mobile_escalation_applied"] = True
        return result

    @staticmethod
    def _mark_memory_only_dropped(result: Dict[str, Any], kwargs: Dict[str, Any]) -> None:
        """
        B1-a (AUDITORIA_SHIM_RUTEO): la rama memory-only del shim analiza SOLO
        la memoria con vol3 (el motor de memoria confiable para evidencia real).
        Cualquier otro artefacto detectado en la misma evidencia (evtx, hives,
        pcap, mft, browser, prefetch) NO se analiza en esta ruta. Este helper
        materializa esa pérdida con el patrón F7 ya usado para pcap: una señal
        `unanalyzed` (signal_class=derived → no cuenta para el gate de
        corroboración ni infla el conteo) por artefacto descartado, más la
        lista `results.unanalyzed_artifacts` que classify_agent_verdict lee para
        degradar NOISE→ABSTAIN. NO recupera las señales (eso sería B1-c) — las
        hace VISIBLES para que "solo memoria" no se selle como cobertura total.
        """
        dropped: List[tuple] = []
        for key, art_type in (
            ("event_logs", "windows_event_log"),
            ("event_stream", "windows_event_log"),
            ("registry_hives", "registry"),
            ("pcap_path", "pcap"),
            ("network_flows", "network"),
            ("browser_profile", "browser"),
            ("prefetch_dir", "prefetch"),
            ("mft_path", "mft"),
            ("mft_json", "mft"),
        ):
            if kwargs.get(key):
                dropped.append((key, art_type, kwargs.get(key)))
        # log_path solo si NO es JSON (los .json entran por _analyze_ebs_json antes)
        _lp = kwargs.get("log_path")
        if _lp and not str(_lp).endswith(".json"):
            dropped.append(("log_path", "event_log", _lp))
        if not dropped:
            return

        sigs = result.setdefault("signals", [])
        if not isinstance(sigs, list):
            return
        inner = result.setdefault("results", {})
        ua = inner.setdefault("unanalyzed_artifacts", []) if isinstance(inner, dict) else None
        for key, art_type, val in dropped:
            sigs.append({
                "tool": f"{art_type.upper()}_UNANALYZED",
                "z_score": 0.0,
                "confidence": 0.0,
                "value": 0.0,
                "metadata": {
                    "artifact_type": art_type,
                    "unanalyzed": True,
                    "signal_class": "derived",
                    "error": "memory-first routing: not analyzed by vol3 memory adapter (B1-a)",
                    "path": str(val),
                    "dropped_kwarg": key,
                },
            })
            if isinstance(ua, list) and art_type not in ua:
                ua.append(art_type)
        meta = result.setdefault("pipeline_meta", {})
        if isinstance(meta, dict):
            meta["memory_only_dropped"] = [k for k, _, _ in dropped]

    # ── Adaptadores internos ──────────────────────────────────────────────

    def _error_result(self, msg: str) -> Dict[str, Any]:
        return {
            "case_id": self.case_id, "signals": [],
            "abduction": {
                "best_hypothesis": "PIPELINE_ERROR",
                "is_conclusive": False,
                "narrative": f"[ERROR] {msg}",
            },
            "pipeline_meta": {"error": msg},
        }

    @staticmethod
    def _frac(val: Any, default: str = "0") -> Fraction:
        """
        FIX P1 (Kimi/2026-06-v2): Rechazar float explícitamente — TypeError.
        P0-compliant: nunca float en la cadena de scoring.
        Callers deben pasar str(json_value) antes de llamar a _frac.
        """
        if val is None:
            return Fraction(default)
        if isinstance(val, Fraction):
            return val
        if isinstance(val, int):
            return Fraction(val, 1)
        if isinstance(val, float):
            # P0 HARD REJECTION — float no permitido en scoring.
            # Si este raise llega a producirse, es un bug en el caller.
            # En producción, los callers deben hacer str(json_val) antes.
            raise TypeError(
                f"[P0] Float rechazado en scoring: {val!r}. "
                f"El caller debe convertir a str antes: _frac(str({val!r}))"
            )
        if isinstance(val, str):
            stripped = val.strip()
            if not stripped or stripped.lower() in ("nan", "inf", "-inf", "+inf"):
                return Fraction(default)
            try:
                return Fraction(stripped)
            except (ValueError, ZeroDivisionError):
                return Fraction(default)
        raise TypeError(f"_frac: tipo no convertible: {type(val)!r}")

    def _resolve_hypothesis(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        B-075 — resolve(): selección abductiva SIN etiqueta (P2-C, Fase 1).

        Formalización mínima siguiendo a Aliseda (2006; 2000): la abducción
        tiene dos momentos distintos — la GENERACIÓN de hipótesis candidatas
        y la SELECCIÓN de una hipótesis entre las ya generadas. En este
        adaptador la generación es el espacio fijo de hipótesis del agente
        (_MOTOR_HYPOTHESIS_MAP.values()); la selección estaba ausente: la
        tapaba la etiqueta `expected_verdict` (label leak) con el umbral
        muerto `avg > 2` como única alternativa, inalcanzable para inputs
        normalizados [0,1] (AUDITORIA_MOTOR_SIN_LABEL §3c).

        La función de selección canónica del repo YA existe: el ladder de
        decisión de `vigia_scorer._vigia_score` (TrustFusion →
        CorrelationDecay → CAIE → Decision → Quadripartite; umbrales
        0.33/0.18/0.08, hard gate temporal, gate de corroboración Daubert
        B-068/B-070). Es determinista, Fraction-based, y demostradamente
        ciega a la etiqueta (label-flip: mismo veredicto/score/seal —
        auditoría §3b). resolve() = invocar esa selección sobre la evidencia
        con la etiqueta REMOVIDA y mapear el veredicto al espacio de
        hipótesis del agente.

        H2 ("umbral re-escalado sobre avg bastaría") fue refutada por
        medición 2026-07-05: mejor acuerdo alcanzable 58.6% (4 clases) /
        74.7% (binario) contra el motor ciego — el escalar avg no porta la
        información del ladder.

        Devuelve dict con: hypothesis, confidence (Fraction), is_conclusive,
        resolve_meta (trazabilidad Daubert: qué decidió y por qué).
        """
        blind = {k: v for k, v in case_data.items() if k != "expected_verdict"}
        try:
            from vigia_scorer import _vigia_score  # lazy: evita costo/ciclos en import
            motor = _vigia_score(blind)
            motor_verdict = str(motor.get("verdict", "ERROR"))
            error = None
        except Exception as e:  # motor crasheado ≠ evidencia limpia → ABSTAIN
            logger.error("[SIFT_SHIM] resolve(): motor falló: %s", e)
            motor = {}
            motor_verdict = "ERROR"
            error = f"{type(e).__name__}: {e}"

        hypothesis = _MOTOR_HYPOTHESIS_MAP.get(motor_verdict, "UNDETERMINED")
        try:
            confidence = Fraction(str(motor.get("confidence", 0)))
        except (ValueError, ZeroDivisionError):
            confidence = Fraction(0)
        confidence = max(Fraction(0), min(confidence, Fraction(99, 100)))
        # Paralelo exacto del guard B-027: nunca conclusivo para la familia
        # abstain/error; para el resto, el mismo umbral 1/3 del camino legacy.
        is_conclusive = (
            confidence > Fraction(33, 100)
            and not any(k in hypothesis for k in ("ABSTAIN", "UNDETERMINED", "ERROR"))
        )
        resolve_meta = {
            "selection_function": "vigia_scorer._vigia_score (Aliseda selection)",
            "motor_verdict": motor_verdict,
            "motor_score": str(motor.get("score", "")),
            "motor_confidence": str(motor.get("confidence", "")),
            "motor_reason": str(motor.get("reason", ""))[:200],
        }
        if error:
            resolve_meta["error"] = error
        return {
            "hypothesis": hypothesis,
            "confidence": confidence,
            "is_conclusive": is_conclusive,
            "resolve_meta": resolve_meta,
            # B-094: CAIE viva del scorer — se surfacéa en el bundle/narrativa.
            "caie_summary": _motor_caie_summary(motor),
        }

    def _analyze_ebs_json(self, json_path: str) -> Dict[str, Any]:
        case_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        case_id = case_data.get("case_id", self.case_id)
        artifacts = case_data.get("artifacts", [])
        signals = []
        for art in artifacts:
            # FIX P1-v2: str() explícito antes de _frac — JSON devuelve float nativo
            # str(0.75) = "0.75" → Fraction(3,4) exacto; str(0.1) = "0.1" → Fraction(1,10) exacto
            raw_score   = self._frac(str(art.get("raw_score",  "0")), "0")
            prior_trust = self._frac(str(art.get("prior_trust", "1/2")), "1/2")
            effective   = raw_score * prior_trust  # Fraction × Fraction — exacto
            signals.append({
                "artifact_id": art.get("artifact_id", "?"),
                "evidence_type": art.get("evidence_type", "unknown"),
                "z_score":    effective,    # Fraction — P0-safe
                "confidence": prior_trust,  # Fraction — P0-safe
                "description": art.get("description", "")[:200],
                "source": art.get("source_tool", "unknown"),
            })
        # FIX P2: avg en Fraction — sin float()
        if signals:
            n   = Fraction(len(signals), 1)
            avg = sum(self._frac(s["z_score"]) for s in signals) / n
        else:
            avg = Fraction(0, 1)
        expected = case_data.get("expected_verdict", "UNKNOWN")

        # ── B-075 / P2-C (Fase 1): selección de modo ────────────────────────
        # "motor"  → resolve(): la hipótesis sale del scorer canónico SIN la
        #            etiqueta (label-blind, ver _resolve_hypothesis). DEFAULT
        #            desde la decisión de doctrina de Anna (opción (a), flip
        #            2026-07-05 — docs/FASE1_RESOLVE_EBS.md §5): el corpus
        #            pasa a medir detección real (143/199 honesto), no
        #            reproducción de etiqueta (199/199 eco).
        # "legacy" → comportamiento histórico: la etiqueta determina la
        #            hipótesis (label leak documentado, P2-C). Retenido SOLO
        #            como modo explícito de reproducción/evaluación de
        #            bundles históricos — nunca default. Cualquier valor
        #            desconocido cae a motor (el modo honesto), no a legacy.
        mode = os.environ.get("VIGIA_EBS_RESOLVE", "motor").strip().lower()
        if mode != "legacy":
            mode = "motor"

        resolve_meta: Optional[Dict[str, Any]] = None
        if mode == "motor":
            resolved = self._resolve_hypothesis(case_data)
            hypothesis = resolved["hypothesis"]
            resolve_meta = resolved["resolve_meta"]
        else:
            # LABEL LEAK (P2-C) — vigente solo en modo legacy. El umbral
            # avg > 2 es inalcanzable para inputs [0,1] (AUDITORIA_MOTOR_SIN_
            # LABEL §3c): la única vía real a MALICE aquí es la etiqueta.
            is_malice  = avg > Fraction(2, 1) or expected == "MALICE"
            hypothesis = (
                "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
                else "INTENT_DETECTED" if expected == "INTENT"
                else "SUSPICION_DETECTED" if expected == "SUSPICION"
                else "ABSTAIN_DETECTED" if expected == "ABSTAIN"
                else "BENIGN_DETECTED" if expected == "BENIGN"
                else "NO_SEMIOTIC_ANOMALY_DETECTED"
            )
        logger.info("[SIFT_SHIM] EBS v1 adapter: case=%s artifacts=%d avg=%s hyp=%s mode=%s",
                    case_id, len(artifacts), str(avg), hypothesis, mode)
        # FIX P2 (Kimi post-patch/2026-06): usar avg_clamped directamente — sin int() truncamiento.
        # int(Fraction(1,3)*100) = 33, pero el valor real es 33.333... → pérdida de precisión.
        # Fraction ya está simplificada automáticamente — no necesita conversión.
        # FIX P2 (Kimi post-patch-v2): normalizar confidence al rango [0,1]
        # avg puede ser > 1 si raw_score*prior_trust son z-scores. Z_CLIP_MAX = 5.
        _Z_MAX = Fraction(5, 1)  # consistente con ebs_v1.Z_CLIP_MAX
        if mode == "motor":
            # La confianza y la conclusividad vienen de la función de
            # selección (mismo guard B-027, umbral 1/3 — ver _resolve_hypothesis).
            confidence_f = resolved["confidence"]
            is_conclusive = resolved["is_conclusive"]
        else:
            confidence_f = min(avg / _Z_MAX, Fraction(99, 100))
            # B-027 FIX: is_conclusive respeta la hipótesis. Antes se
            # derivaba SOLO del promedio de scores, y un caso
            # ABSTAIN_DETECTED con scores individuales altos sellaba la
            # contradicción lógica "no puedo formar opinión" +
            # is_conclusive=True en el mismo bundle.
            is_conclusive = (avg > Fraction(33, 100)
                             and "ABSTAIN" not in hypothesis
                             and "UNDETERMINED" not in hypothesis)
        pipeline_meta: Dict[str, Any] = {
            "source": "ebs_v1_json_adapter",
            "artifact_count": len(artifacts),
            "avg_score": str(avg),   # Fraction serializada como string
            # Passthrough para tooling de evaluación (mismo criterio que el
            # motor en vigia_scorer). En modo motor NUNCA participa del
            # scoring — la invariancia al label-flip lo prueba
            # (tests/test_fase1_resolve.py::TestLabelFlipInvariance).
            "expected_verdict": expected,
            "ebs_adapter_mode": mode,
        }
        if resolve_meta is not None:
            pipeline_meta["resolve"] = resolve_meta
        # B-094: surfacear la CAIE viva del scorer en results["caie"] — el
        # canal que vigia_agent._generate_narrative consume (inner.get("caie")).
        # Solo en modo motor y solo si hubo fracturas (el helper devuelve None
        # si no hay nada que explicar).
        _out: Dict[str, Any] = {
            "case_id": case_id, "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                "is_conclusive": is_conclusive,
                "confidence": confidence_f,
                "best_posterior": str(confidence_f),
                "narrative": case_data.get("description", "")[:500],
            },
            "pipeline_meta": pipeline_meta,
        }
        _caie_summary = resolved.get("caie_summary") if mode == "motor" and resolved else None
        if _caie_summary:
            _out["results"] = {"caie": _caie_summary}
        return _out

    def _analyze_memory_vol3(self, memory_path: str) -> Dict[str, Any]:
        """Análisis de memoria con Volatility3 — no requiere rip.pl."""
        signals = []

        # ── 1. OS identification ──────────────────────────────────────────
        info = self._vol3_run(memory_path, "windows.info", timeout=_vol3_eff_timeout(120, memory_path))
        if info["ok"]:
            signals.append({
                "source": "vol3.windows.info",
                "evidence_type": "memory_os_profile",
                "z_score": Fraction(5, 10),
                "confidence": Fraction(9, 10),
                "description": "Windows OS profile identified from memory image",
                "detail": info["stdout"][:300],
            })
            logger.info("[VOL3] OS info: %s", info["stdout"][:100])
        else:
            stderr_lower = info["stderr"].lower()
            if any(k in stderr_lower for k in [
                "invalidaddressexception", "offset outside", "buffer boundaries",
                "no valid kernel", "unable to determine", "vmware", "snapshot"
            ]):
                logger.error(
                    "[VOL3] Format rejected — image is not a valid Windows RAM dump "
                    "(VMware snapshot or disk image detected). "
                    "Requires companion .vmss/.vmsn or different acquisition tool. "
                    "stderr: %s", info["stderr"][:300]
                )
                return {
                    "case_id": self.case_id,
                    "signals": [],
                    "abduction": {
                        "best_hypothesis": "FORMAT_NOT_SUPPORTED",
                        "is_conclusive": False,
                        "confidence": "0/1",
                        "best_posterior": "0/1",
                        "narrative": (
                            f"Image {Path(memory_path).name} rejected by Volatility3: "
                            "not a valid Windows RAM dump. Likely a VMware disk snapshot "
                            "or disk image requiring prior mounting. "
                            "See BUGS_PENDIENTES #16."
                        ),
                    },
                    "pipeline_meta": {
                        "source": "vol3_memory_adapter",
                        "memory_path": str(memory_path),
                        "error": "FORMAT_NOT_SUPPORTED",
                        "vol3_stderr": info["stderr"][:300],
                    },
                }
            logger.warning("[VOL3] windows.info failed: %s", info["stderr"][:200])

        # ── 2. Process list ───────────────────────────────────────────────
        pslist = self._vol3_run(memory_path, "windows.pslist.PsList", timeout=_vol3_eff_timeout(300, memory_path))
        if pslist["ok"]:
            suspicious = [l for l in pslist["stdout"].splitlines()
                          if any(p in l.lower() for p in
                                 ["cmd.exe", "powershell", "wscript", "cscript",
                                  "mshta", "regsvr32", "rundll32", "msiexec",
                                  "certutil", "bitsadmin", "wmic"])]
            if suspicious:
                signals.append({
                    "source": "vol3.windows.pslist",
                    "evidence_type": "memory_process",
                    "z_score": Fraction(28, 10),
                    "confidence": Fraction(75, 100),
                    "description": f"{len(suspicious)} living-off-the-land processes detected",
                    "detail": "\n".join(suspicious[:10]),
                })
            else:
                signals.append({
                    "source": "vol3.windows.pslist",
                    "evidence_type": "memory_process",
                    "z_score": Fraction(1, 10),
                    "confidence": Fraction(6, 10),
                    "description": "Process list analyzed — no obvious LOLBAS processes",
                })

        # ── 3. Network connections ────────────────────────────────────────
        netscan = self._vol3_run(memory_path, "windows.netscan.NetScan", timeout=_vol3_eff_timeout(300, memory_path))
        if netscan["ok"]:
            external = [l for l in netscan["stdout"].splitlines()
                        if "ESTABLISHED" in l and _netscan_has_external_conn(l)]
            if external:
                signals.append({
                    "source": "vol3.windows.netscan",
                    "evidence_type": "network_flow",
                    "z_score": Fraction(18, 10),
                    "confidence": Fraction(8, 10),
                    "description": f"{len(external)} established connections to external IPs",
                    "detail": "\n".join(external[:10]),
                })

        # ── 4. Code injection (malfind) ───────────────────────────────────
        malfind = self._vol3_run(memory_path, "windows.malfind.Malfind", timeout=_vol3_eff_timeout(600, memory_path))

        # B4: rastro de timeouts para pipeline_meta.
        _vol3_runs = {"windows.info": info, "windows.pslist.PsList": pslist,
                      "windows.netscan.NetScan": netscan,
                      "windows.malfind.Malfind": malfind}
        _plugin_timeouts = sorted(p for p, r in _vol3_runs.items()
                                  if r.get("timed_out"))
        if malfind["ok"] and len(malfind["stdout"]) > 100:
            hits = [l for l in malfind["stdout"].splitlines()
                    if l and not l.startswith("Volatility") and not l.startswith("PID")]
            procs = set()
            for line in hits:
                parts = line.split()
                if parts:
                    procs.add(parts[0])
            if procs:
                signals.append({
                    "source": "vol3.windows.malfind",
                    "evidence_type": "memory_process",
                    "z_score": Fraction(35, 10),
                    "confidence": Fraction(85, 100),
                    "description": f"Potential code injection in {len(procs)} process(es): {', '.join(list(procs)[:5])}",
                })

        # FIX (auditoría FN, P1-D): distinguir "analizado y limpio" de "no se
        # pudo analizar". Si NINGÚN plugin de Volatility3 corrió con éxito
        # (binario `vol` ausente, imagen ilegible, todos los plugins en timeout),
        # 0 señales NO significa evidencia benigna — significa que no se analizó.
        # Antes esto caía en NO_SEMIOTIC_ANOMALY_DETECTED (benigno, exit 0);
        # ahora abstiene con UNANALYZED_ARTIFACT (→ ABSTAIN en el agente).
        any_plugin_ok = bool(
            info["ok"] or pslist["ok"] or netscan["ok"] or malfind["ok"]
        )
        if not any_plugin_ok:
            vol_missing = any(
                "no such file" in r["stderr"].lower()
                or "not found" in r["stderr"].lower()
                for r in (info, pslist, netscan, malfind)
            )
            reason = (
                "Volatility3 binary not found — memory image NOT analyzed"
                if vol_missing else
                "All Volatility3 plugins failed — memory image could not be analyzed"
            )
            logger.error("[VOL3] %s: %s", reason, Path(memory_path).name)
            return {
                "case_id": self.case_id,
                "signals": [],
                "abduction": {
                    "best_hypothesis": "UNANALYZED_ARTIFACT",
                    "is_conclusive": False,
                    "confidence": "0/1",
                    "best_posterior": "0/1",
                    "narrative": (
                        f"[ABSTAIN] {reason}: {Path(memory_path).name}. "
                        "Absence of signals reflects an analysis failure, not "
                        "the absence of malicious activity. Verify the vol3 "
                        "binary and image format before drawing conclusions."
                    ),
                },
                "pipeline_meta": {
                    "source": "vol3_memory_adapter",
                    "memory_path": str(memory_path),
                    "error": "VOL3_UNAVAILABLE" if vol_missing else "VOL3_ALL_PLUGINS_FAILED",
                    "vol3_binary": _VOL3,
                    # B4 (B-018): este ES el caso NARCOS — todos los plugins
                    # caídos. El rastro distingue "binario ausente" de
                    # "todos en timeout" (pipeline_status=timeout_all).
                    "vol3_plugin_timeouts": _plugin_timeouts,
                    "pipeline_status": ("timeout_all"
                                        if _plugin_timeouts and len(_plugin_timeouts) == len(_vol3_runs)
                                        else "failed"),
                    "vol3_timeout_config": {
                        "env_VIGIA_VOL3_TIMEOUT": os.environ.get("VIGIA_VOL3_TIMEOUT"),
                        "effective_per_plugin": {p: r.get("timeout_used")
                                                 for p, r in _vol3_runs.items()},
                    },
                },
            }

        # FIX P2: avg en Fraction — sin float(s["z_score"])
        if signals:
            n_sig = Fraction(len(signals), 1)
            avg   = sum(self._frac(s["z_score"]) for s in signals) / n_sig
        else:
            avg = Fraction(0, 1)

        # ── TANDA 3 (H5, AUDITORIA_FUGA_INDIRECTA) — escalera corregida ────
        # Pre-fix: `avg > 1/3 → MALICIOUS` con `INTENT si avg > 1/2` evaluado
        # DESPUÉS — orden de umbrales invertido respecto a la severidad:
        # INTENT_DETECTED era estructuralmente inalcanzable (exigía avg>1/2
        # tras haber fallado avg>1/3; verificado por barrido de 5001 puntos).
        # Además una SOLA señal (p.ej. inyección z=3.5) emitía la hipótesis
        # MALICIOUS — contra la doctrina de 2 fuentes (misma barra que
        # _mobile_hypothesis y el gate Daubert del scorer B-068/B-070).
        # Post-fix, mismos umbrales que _mobile_hypothesis (z>3 crítico,
        # z>2 sospecha; estrictos):
        #   ≥2 señales z>3 → MALICIOUS_INTENT_DETECTED (gate de 2 fuentes)
        #   max_z > 3      → INTENT_DETECTED (ahora alcanzable: 1 señal 3.5)
        #   señal débil    → SUSPICION_DETECTED (banda pre-fix conservada:
        #                    cualquier señal no nula sigue siendo al menos
        #                    sospecha — sin cambio en esa banda)
        #   sin señal / 0  → NO_SEMIOTIC_ANOMALY_DETECTED
        # Nota de alcance: n_critical cuenta señales (hallazgos de plugins
        # distintos sobre la misma imagen), el mismo criterio que el path
        # mobile usa para dispositivos. La independencia plena de fuente la
        # arbitra aguas abajo el gate B-068 del scorer sobre clases DEVICE.
        z_values = [abs(self._frac(s["z_score"])) for s in signals]
        max_z = max(z_values) if z_values else Fraction(0, 1)
        n_critical = sum(1 for z in z_values if z > Fraction(3, 1))

        if n_critical >= 2:
            hypothesis = "MALICIOUS_INTENT_DETECTED"
        elif max_z > Fraction(3, 1):
            hypothesis = "INTENT_DETECTED"
        elif max_z > Fraction(2, 1):
            hypothesis = "SUSPICION_DETECTED"
        elif avg == Fraction(0, 1):
            hypothesis = "NO_SEMIOTIC_ANOMALY_DETECTED"
        else:
            hypothesis = "SUSPICION_DETECTED"

        logger.info(
            "[VOL3] Memory analysis complete: %d signals, avg_score=%s, max_z=%s, n_critical=%d → %s",
            len(signals), str(avg), str(max_z), n_critical, hypothesis,
        )
        # Confidence: clampear y calcular en Fraction
        # FIX P2 (Kimi post-patch-v2): normalizar confidence [0,1] con Z_CLIP_MAX=5
        _Z_MAX_VOL = Fraction(5, 1)
        conf_vol3 = min(avg / _Z_MAX_VOL, Fraction(99, 100))

        return {
            "case_id": self.case_id,
            "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                # FIX P2: Fraction puro — sin float
                # B-027 FIX: este path nunca produce hipótesis ABSTAIN hoy,
                # pero el flag queda condicionado por coherencia (si la
                # escalera de hipótesis incorporara ABSTAIN, el flag no puede
                # quedar en True). Los paths UNANALYZED/FORMAT_NOT_SUPPORTED
                # de arriba ya emiten is_conclusive=False explícito.
                # TANDA 3: conclusivo = al menos una señal crítica (max_z>3),
                # espejo exacto de _mobile_hypothesis (antes: avg > 3/2,
                # escala inconsistente con el resto de la escalera).
                "is_conclusive": max_z > Fraction(3, 1),
                "confidence": conf_vol3,
                "best_posterior": str(conf_vol3),
                # F8 (N12): el texto de cierre coincide con la hipótesis. Antes
                # 0 señales / avg=0 decían "Suspicious activity — requires
                # human review" junto a NO_SEMIOTIC_ANOMALY_DETECTED — la
                # narrativa contradecía el veredicto (observado en DC-MEM-003).
                "narrative": (
                    f"Volatility3 memory analysis: {len(signals)} signals from "
                    f"{Path(memory_path).name}. "
                    f"Average intentionality score: {avg.numerator}/{avg.denominator}. "
                    + (f"Malicious activity indicated ({n_critical} critical signals — "
                       "two-source gate satisfied)." if hypothesis == "MALICIOUS_INTENT_DETECTED"
                       else ("Deliberate-intent signal from a single critical finding — "
                             "corroboration by a second source required for MALICE."
                             if hypothesis == "INTENT_DETECTED"
                             else ("No signals extracted — analysis produced no reviewable "
                                   "output; absence of extraction output is not evidence "
                                   "of benignity." if not signals
                                   else ("No anomalous signals above threshold — nothing "
                                         "to review in this image." if avg == Fraction(0, 1)
                                         else "Suspicious activity — requires human review."))))
                ),
            },
            "pipeline_meta": {
                "source": "vol3_memory_adapter",
                "memory_path": str(memory_path),
                "signal_count": len(signals),
                "avg_score": avg,
                # TANDA 3: trazabilidad de la escalera — qué decidió y por qué
                "max_z": max_z,
                "n_critical_signals": n_critical,
                "ladder": "mobile_hypothesis_thresholds_v2 (z>3 critical, z>2 suspicion, 2-source gate)",
                "vol3_binary": _VOL3,
                # B4 (B-018): la pérdida por timeout es VISIBLE en el bundle.
                "vol3_plugin_timeouts": _plugin_timeouts,
                "pipeline_status": "timeout_partial" if _plugin_timeouts else "completed",
                "vol3_timeout_config": {
                    "env_VIGIA_VOL3_TIMEOUT": os.environ.get("VIGIA_VOL3_TIMEOUT"),
                    "effective_per_plugin": {p: r.get("timeout_used")
                                             for p, r in _vol3_runs.items()},
                },
            },
        }

    def _vol3_run(self, memory_path: str, plugin: str, timeout: int = 300) -> Dict:
        """Ejecuta un plugin de Volatility3 y retorna stdout/stderr.

        B4 (B-018): timed_out/timeout_used viajan en el resultado para que
        _analyze_memory_vol3 deje rastro en pipeline_meta — "0 señales por
        timeout" tiene que ser distinguible de "0 señales porque está limpio".
        """
        try:
            result = subprocess.run(
                [_VOL3, "-f", memory_path, plugin],
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "ok": result.returncode == 0 and len(result.stdout) > 50,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timed_out": False,
                "timeout_used": timeout,
            }
        except subprocess.TimeoutExpired:
            logger.warning("[VOL3] Plugin %s timed out after %ds", plugin, timeout)
            return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s",
                    "timed_out": True, "timeout_used": timeout}
        except Exception as e:
            logger.error("[VOL3] Plugin %s error: %s", plugin, e)
            return {"ok": False, "stdout": "", "stderr": str(e),
                    "timed_out": False, "timeout_used": timeout}


__all__ = ["SIFTOrchestrator"]
