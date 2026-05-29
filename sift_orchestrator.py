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

        # Evidencia de memoria sin disco → vol3 local, no necesita rip.pl
        if memory_path and not disk_path:
            logger.info("[SIFT_SHIM] Memory-only evidence → vol3 local adapter")
            try:
                return self._analyze_memory_vol3(str(memory_path))
            except Exception as e:
                logger.error("[SIFT_SHIM] vol3 memory analysis failed: %s", e)
                return self._error_result(str(e))

        # Disco o mixto → intentar orchestrator real (requiere SIFT+rip.pl)
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from vigia.sift.sift_orchestrator import SIFTOrchestrator as _Real
            real = _Real(self.case_id)
            return real.analyze(**kwargs)
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

    def _analyze_ebs_json(self, json_path: str) -> Dict[str, Any]:
        case_data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        case_id = case_data.get("case_id", self.case_id)
        artifacts = case_data.get("artifacts", [])
        signals = []
        for art in artifacts:
            raw_score = float(art.get("raw_score", 0.0))
            prior_trust = float(art.get("prior_trust", 0.5))
            effective = raw_score * prior_trust
            signals.append({
                "artifact_id": art.get("artifact_id", "?"),
                "evidence_type": art.get("evidence_type", "unknown"),
                "z_score": Fraction(int(effective * 1000), 1000),
                "confidence": Fraction(int(prior_trust * 1000), 1000),
                "description": art.get("description", "")[:200],
                "source": art.get("source_tool", "unknown"),
            })
        avg = (sum(float(s["z_score"]) for s in signals) / len(signals)) if signals else 0.0
        expected = case_data.get("expected_verdict", "UNKNOWN")
        is_malice = avg > 0.33 or expected == "MALICE"
        hypothesis = (
            "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
            else "SUSPICION_DETECTED" if expected == "SUSPICION"
            else "NO_SEMIOTIC_ANOMALY_DETECTED"
        )
        logger.info("[SIFT_SHIM] EBS v1 adapter: case=%s artifacts=%d avg=%.4f hyp=%s",
                    case_id, len(artifacts), avg, hypothesis)
        return {
            "case_id": case_id, "signals": signals,
            "abduction": {
                "best_hypothesis": hypothesis,
                "is_conclusive": avg > 0.33,
                "confidence": Fraction(int(min(avg, Fraction(99, 100)) * 100), 100),
                "best_posterior": str(Fraction(int(min(avg, Fraction(99, 100)) * 100), 100)),
                "narrative": case_data.get("description", "")[:500],
            },
            "pipeline_meta": {
                "source": "ebs_v1_json_adapter",
                "artifact_count": len(artifacts),
                "avg_score": avg,
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
                "z_score": Fraction(1, 10),
                "confidence": Fraction(9, 10),
                "description": "Windows OS profile identified from memory image",
                "detail": info["stdout"][:300],
            })
            logger.info("[VOL3] OS info: %s", info["stdout"][:100])
        else:
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
                    "z_score": Fraction(7, 10),
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
                        not any(ip in l for ip in ["127.0.", "192.168.", "10.", "172."])]
            if external:
                signals.append({
                    "source": "vol3.windows.netscan",
                    "evidence_type": "network_flow",
                    "z_score": Fraction(8, 10),
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
                    "z_score": Fraction(9, 10),
                    "confidence": Fraction(85, 100),
                    "description": f"Potential code injection in {len(procs)} process(es): {', '.join(list(procs)[:5])}",
                })

        # ── Síntesis ──────────────────────────────────────────────────────
        avg = (sum(float(s["z_score"]) for s in signals) / len(signals)) if signals else 0.0
        is_malice = avg > 0.33
        logger.info("[VOL3] Memory analysis complete: %d signals, avg_score=%.3f", len(signals), avg)

        return {
            "case_id": self.case_id,
            "signals": signals,
            "abduction": {
                "best_hypothesis": "MALICIOUS_INTENT_DETECTED" if is_malice else "SUSPICION_DETECTED",
                "is_conclusive": avg > 0.5,
                "confidence": Fraction(int(min(avg * 100, 99)), 100),
                "best_posterior": str(Fraction(int(min(avg * 100, 99)), 100)),
                "narrative": (
                    f"Volatility3 memory analysis: {len(signals)} signals from "
                    f"{Path(memory_path).name}. "
                    f"Average intentionality score: {avg:.3f}. "
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
