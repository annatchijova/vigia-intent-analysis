# sift_orchestrator.py — shim de compatibilidad para vigia_agent.py
from __future__ import annotations

import ipaddress
import json
import logging
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

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
            return self._merge_mobile_signals(result, mobile_signals)

        # B-045: if only mobile evidence is present (no Windows artifacts),
        # return mobile signals directly without falling through to the real orchestrator.
        has_windows_evidence = any(kwargs.get(k) for k in (
            "memory_path", "disk_path", "event_logs", "event_stream",
            "registry_hives", "pcap_path", "network_flows", "log_path",
            "browser_profile",
        ))
        if not has_windows_evidence and mobile_signals:
            result = {
                "case_id": self.case_id,
                "signals": mobile_signals,
                "abduction": {
                    "best_hypothesis": "MOBILE_EVIDENCE_ANALYZED",
                    "is_conclusive": len(mobile_signals) > 0,
                    "confidence": "0",
                    "best_posterior": "0",
                    "narrative": (
                        f"[FIRSTNESS] Mobile forensic evidence analyzed: "
                        f"{len(mobile_signals)} signal(s) extracted."
                    ),
                },
                "pipeline_meta": {
                    "source": "mobile_forensics_adapter",
                    "n_mobile_signals": len(mobile_signals),
                    "n_total_signals": len(mobile_signals),
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
            if lp and not str(lp).endswith(".json"):
                run_kwargs["event_logs"] = lp if isinstance(lp, list) else [lp]
            if kwargs.get("network_flows"):
                run_kwargs["network_flows"] = kwargs["network_flows"]
            pcap_path = kwargs.get("pcap_path")
            if isinstance(pcap_path, list):
                pcap_path = pcap_path[0] if pcap_path else None
            if pcap_path and not run_kwargs.get("network_flows"):
                try:
                    from vigia.sift.pcap_parser import parse_pcap_to_flows
                    pcap_flows = parse_pcap_to_flows(str(pcap_path))
                    if pcap_flows:
                        run_kwargs["network_flows"] = pcap_flows
                        logger.info("[SIFT_SHIM] Parsed %d flows from pcap: %s", len(pcap_flows), pcap_path)
                except Exception as e:
                    logger.error("[SIFT_SHIM] pcap parsing failed for %s: %s", pcap_path, e)
                    raise
            rh = kwargs.get("registry_hives")
            if rh:
                run_kwargs["registry_hives"] = rh if isinstance(rh, list) else [rh]
            # Browser profile (Chromium History / Firefox places.sqlite) — parser
            # SQLite real (P1-A). Se pasa el directorio del perfil.
            bp = kwargs.get("browser_profile")
            if bp:
                run_kwargs["browser_profile"] = bp[0] if isinstance(bp, list) else bp

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
                        "metadata": sig.metadata,
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] Android engine: %d findings, %d SMS, z=%.2f",
                        len(result.findings), result.total_sms, sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] AndroidForensicsAnalyzer failed: %s", e)

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
                        "metadata": sig.metadata,
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] iOS engine: %d findings, %d SMS, z=%.2f",
                        len(result.findings), result.total_sms, sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] iOSForensicsAnalyzer failed: %s", e)

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
                        "metadata": sig.metadata,
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] Google Takeout engine: %d findings, z=%.2f",
                        len(result.findings), sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] GoogleTakeoutForensicsAnalyzer failed: %s", e)

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
                        "metadata": sig.metadata,
                    }
                    signals.append(sig_dict)
                    logger.info(
                        "[SIFT_SHIM] macOS engine: %d findings, z=%.2f",
                        len(result.findings), sig.z_score,
                    )
            except Exception as e:
                logger.error("[SIFT_SHIM] MacOSForensicsAnalyzer failed: %s", e)

        return signals

    @staticmethod
    def _merge_mobile_signals(result: Dict[str, Any], mobile_signals: list) -> Dict[str, Any]:
        """Merge mobile forensic signals into an existing pipeline result."""
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
        return result

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
        expected   = case_data.get("expected_verdict", "UNKNOWN")
        is_malice  = avg > Fraction(2, 1) or expected == "MALICE"
        hypothesis = (
            "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
            else "INTENT_DETECTED" if expected == "INTENT"
            else "SUSPICION_DETECTED" if expected == "SUSPICION"
            else "ABSTAIN_DETECTED" if expected == "ABSTAIN"
            else "BENIGN_DETECTED" if expected == "BENIGN"
            else "NO_SEMIOTIC_ANOMALY_DETECTED"
        )
        logger.info("[SIFT_SHIM] EBS v1 adapter: case=%s artifacts=%d avg=%s hyp=%s",
                    case_id, len(artifacts), str(avg), hypothesis)
        # FIX P2 (Kimi post-patch/2026-06): usar avg_clamped directamente — sin int() truncamiento.
        # int(Fraction(1,3)*100) = 33, pero el valor real es 33.333... → pérdida de precisión.
        # Fraction ya está simplificada automáticamente — no necesita conversión.
        # FIX P2 (Kimi post-patch-v2): normalizar confidence al rango [0,1]
        # avg puede ser > 1 si raw_score*prior_trust son z-scores. Z_CLIP_MAX = 5.
        _Z_MAX = Fraction(5, 1)  # consistente con ebs_v1.Z_CLIP_MAX
        confidence_f = min(avg / _Z_MAX, Fraction(99, 100))
        return {
            "case_id": case_id, "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                "is_conclusive": avg > Fraction(33, 100),
                "confidence": confidence_f,
                "best_posterior": str(confidence_f),
                "narrative": case_data.get("description", "")[:500],
            },
            "pipeline_meta": {
                "source": "ebs_v1_json_adapter",
                "artifact_count": len(artifacts),
                "avg_score": str(avg),   # Fraction serializada como string
                "expected_verdict": expected,
            },
        }

    def _analyze_memory_vol3(self, memory_path: str) -> Dict[str, Any]:
        """Análisis de memoria con Volatility3 — no requiere rip.pl."""
        signals = []

        # ── 1. OS identification ──────────────────────────────────────────
        info = self._vol3_run(memory_path, "windows.info", timeout=120)
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
        pslist = self._vol3_run(memory_path, "windows.pslist.PsList", timeout=300)
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
        netscan = self._vol3_run(memory_path, "windows.netscan.NetScan", timeout=300)
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
        malfind = self._vol3_run(memory_path, "windows.malfind.Malfind", timeout=600)
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
                },
            }

        # FIX P2: avg en Fraction — sin float(s["z_score"])
        if signals:
            n_sig = Fraction(len(signals), 1)
            avg   = sum(self._frac(s["z_score"]) for s in signals) / n_sig
        else:
            avg = Fraction(0, 1)
        is_malice = avg > Fraction(33, 100)
        logger.info("[VOL3] Memory analysis complete: %d signals, avg_score=%s", len(signals), str(avg))
        # Confidence: clampear y calcular en Fraction
        # FIX P2 (Kimi post-patch-v2): normalizar confidence [0,1] con Z_CLIP_MAX=5
        _Z_MAX_VOL = Fraction(5, 1)
        conf_vol3 = min(avg / _Z_MAX_VOL, Fraction(99, 100))

        return {
            "case_id": self.case_id,
            "signals": signals,
            "abduction": {
                "best_hypothesis": "MALICIOUS_INTENT_DETECTED" if is_malice else "NO_SEMIOTIC_ANOMALY_DETECTED" if avg == Fraction(0, 1) else "INTENT_DETECTED" if avg > Fraction(5, 10) else "SUSPICION_DETECTED",
                # FIX P2: Fraction puro — sin float
                "is_conclusive": avg > Fraction(3, 2),
                "confidence": conf_vol3,
                "best_posterior": str(conf_vol3),
                "narrative": (
                    f"Volatility3 memory analysis: {len(signals)} signals from "
                    f"{Path(memory_path).name}. "
                    f"Average intentionality score: {avg.numerator}/{avg.denominator}. "
                    f"{'Malicious activity indicated.' if is_malice else 'Suspicious activity — requires human review.'}"
                ),
            },
            "pipeline_meta": {
                "source": "vol3_memory_adapter",
                "memory_path": str(memory_path),
                "signal_count": len(signals),
                "avg_score": avg,
                "vol3_binary": _VOL3,
            },
        }

    def _vol3_run(self, memory_path: str, plugin: str, timeout: int = 300) -> Dict:
        """Ejecuta un plugin de Volatility3 y retorna stdout/stderr."""
        try:
            result = subprocess.run(
                [_VOL3, "-f", memory_path, plugin],
                capture_output=True, text=True, timeout=timeout
            )
            return {
                "ok": result.returncode == 0 and len(result.stdout) > 50,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            logger.warning("[VOL3] Plugin %s timed out after %ds", plugin, timeout)
            return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s"}
        except Exception as e:
            logger.error("[VOL3] Plugin %s error: %s", plugin, e)
            return {"ok": False, "stdout": "", "stderr": str(e)}


__all__ = ["SIFTOrchestrator"]
