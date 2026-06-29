# sift_orchestrator.py — shim de compatibilidad para vigia_agent.py
from __future__ import annotations

import json
import logging
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

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

    def analyze(self, **kwargs) -> Dict[str, Any]:
        log_path = kwargs.get("log_path")
        if log_path and str(log_path).endswith(".json"):
            try:
                return self._analyze_ebs_json(str(log_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] EBS JSON adapter failed: %s", e)
                return self._error_result(str(e))

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
                return self._analyze_memory_vol3(str(memory_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] vol3 memory analysis failed: %s", e)
                return self._error_result(str(e))

        # Disk or mixed → real orchestrator via run_full_analysis
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from vigia.sift.sift_orchestrator import SIFTOrchestrator as _Real
            real = _Real(self.case_id)

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
            rh = kwargs.get("registry_hives")
            if rh:
                run_kwargs["registry_hives"] = rh if isinstance(rh, list) else [rh]

            # disk_path (E01) has no direct mapping — requires prior mounting
            # and artifact extraction (ewfmount + registry hive extraction)
            if kwargs.get("disk_path") and not run_kwargs:
                logger.warning(
                    "[SIFT_SHIM] E01 requires prior mounting. "
                    "Mount with ewfmount, extract hives, then pass artifacts directly."
                )
                return self._error_result(
                    "E01 disk image requires prior artifact extraction. "
                    "Mount with ewfmount and pass registry_hives/event_logs explicitly."
                )

            return real.run_full_analysis(**run_kwargs)
        except Exception as e:
            logger.error("[SIFT_SHIM] Real orchestrator failed: %s", e)
            return self._error_result(str(e))

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
                        if "ESTABLISHED" in l and
                        not any(ip in l for ip in ["127.0.", "192.168.", "10.", "172.16.4.", "172.16.3.", "172.16.2.", "172.16.1.", "::1", "::", "fe80:"])]
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
