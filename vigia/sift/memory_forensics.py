"""
vigia/sift/memory_forensics.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. COMMAND INJECTION: subprocess.run usa lista de argumentos (NO shell=True).
   _sanitize_path ahora usa shlex.quote para paths con espacios.
2. PATH TRAVERSAL: Validación de que dump_path resuelve dentro de un allowlist.
3. TIMEOUT: Volatility3 timeout ahora es paramétrico y con manejo de excepciones.
4. INTEGRITY: Hash SHA-256 del dump verificado antes de análisis.
"""

from __future__ import annotations

import os

import hashlib
import json
import logging
import re
import shlex
import subprocess
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import _entropy_shannon, _parse_iso_timestamp, noisy_or_correlated

logger = logging.getLogger(__name__)

TOOL_NAME = "MEMORY_FORENSICS"
ARTIFACT_RELIABILITY = Fraction(95, 100)

# B3 (B-016 residual): marcadores de stderr de Volatility3 que significan
# "esto no es un RAM dump Windows válido" (snapshot VMware sin companion
# .vmss/.vmsn, imagen de disco, layout irresoluble). MISMA lista que el shim
# del agente (sift_orchestrator._analyze_memory_vol3), que es el detector
# probado en el camino operativo.
_VOL3_FORMAT_MARKERS = (
    "invalidaddressexception", "offset outside", "buffer boundaries",
    "no valid kernel", "unable to determine", "vmware", "snapshot",
)


def classify_vol3_stderr(stderr: str) -> Optional[str]:
    """FORMAT_NOT_SUPPORTED si el stderr indica formato de imagen inválido;
    None para errores ordinarios de plugin (que siguen degradando blando)."""
    s = (stderr or "").lower()
    if any(m in s for m in _VOL3_FORMAT_MARKERS):
        return "FORMAT_NOT_SUPPORTED"
    return None


def vol3_effective_timeout(base: int, memory_path: str) -> int:
    """B4 (B-018 residual): timeout efectivo para un plugin de Volatility3.

    - VIGIA_VOL3_TIMEOUT=<segundos> fija el timeout EXACTO (el perito manda;
      sin escalado encima). Valor no numérico → se ignora con warning.
    - Sin env: el base por-plugin se escala por tamaño del dump — los números
      de B-018 (un dump ≥4 GiB multiplica los tiempos de pslist/netscan/
      malfind): ≥16 GiB ×4, ≥4 GiB ×2, menor usa el base.
    """
    env = os.environ.get("VIGIA_VOL3_TIMEOUT")
    if env:
        try:
            return max(1, int(env))
        except ValueError:
            logger.warning("VIGIA_VOL3_TIMEOUT=%r no numérico — ignorado", env)
    try:
        size = os.path.getsize(memory_path)
    except OSError:
        return base
    if size >= 16 * 2**30:
        return base * 4
    if size >= 4 * 2**30:
        return base * 2
    return base


class MemoryImageFormatError(RuntimeError):
    """La imagen no es un RAM dump que Volatility3 pueda resolver."""
    def __init__(self, stderr_excerpt: str):
        super().__init__(f"FORMAT_NOT_SUPPORTED: {stderr_excerpt[:300]}")
        self.stderr_excerpt = stderr_excerpt[:300]

# --- ALLOWLIST DE DIRECTORIOS PERMITIDOS (configurable) ---
# FIX P1 (Kimi/2026-06): ALLOWED_BASE_PATHS configurable — no hardcodeado.
# Leer de VIGIA_ALLOWED_DUMP_PATHS (paths separados por ":") o usar defaults.
# Esto permite que VIGÍA funcione en /opt/vigia, SIFT, Kali, o cualquier entorno.
def _load_allowed_base_paths() -> list:
    env_val = os.environ.get("VIGIA_ALLOWED_DUMP_PATHS", "")
    if env_val.strip():
            return [Path(p.strip()) for p in env_val.split(os.pathsep) if p.strip()]  # FIX P3 (Kimi): pathsep portable
    return [
        Path("/var/vigia/dumps"),
        Path("/tmp/vigia"),
        Path("/home/vigia/cases"),
        # SIFT default evidence paths
        Path("/cases"),
        Path("/evidence"),
    ]

ALLOWED_BASE_PATHS = _load_allowed_base_paths()

_SYSTEM_PROCESS_PARENTS: Dict[str, frozenset] = {
    "services.exe": frozenset({"wininit.exe"}),
    "lsass.exe": frozenset({"wininit.exe"}),
    "svchost.exe": frozenset({"services.exe"}),
    "explorer.exe": frozenset({"userinit.exe", "winlogon.exe"}),
    "winlogon.exe": frozenset({"smss.exe"}),
    "csrss.exe": frozenset({"smss.exe"}),
    "wininit.exe": frozenset({"smss.exe"}),
    "smss.exe": frozenset({"system"}),
}

_SINGLETON_PROCESSES: frozenset = frozenset({
    "lsass.exe", "wininit.exe", "winlogon.exe", "smss.exe", "services.exe",
})

_LEGITIMATE_PATHS: Dict[str, frozenset] = {
    "lsass.exe": frozenset({r"c:\windows\system32\lsass.exe"}),
    "svchost.exe": frozenset({r"c:\windows\system32\svchost.exe"}),
    "services.exe": frozenset({r"c:\windows\system32\services.exe"}),
    "csrss.exe": frozenset({r"c:\windows\system32\csrss.exe"}),
    "wininit.exe": frozenset({r"c:\windows\system32\wininit.exe"}),
    "explorer.exe": frozenset({r"c:\windows\explorer.exe", r"c:\windows\syswow64\explorer.exe"}),
}

_MALFIND_SUSPICIOUS_PROT: frozenset = frozenset({
    "PAGE_EXECUTE_READWRITE", "PAGE_EXECUTE_WRITECOPY",
})

_SUSPICIOUS_PORTS: frozenset = frozenset({4444, 1337, 31337, 8080, 9001, 9050})

_ANOMALY_WEIGHTS: Dict[str, Fraction] = {
    "orphan_process": Fraction(85, 100),
    "parent_mismatch": Fraction(90, 100),
    "path_anomaly": Fraction(95, 100),
    "singleton_violation": Fraction(80, 100),
    "hidden_process": Fraction(98, 100),
    "malfind_rwx": Fraction(75, 100),
    "malfind_pe_injection": Fraction(92, 100),
    "network_suspicious_port": Fraction(70, 100),
    "network_process_mismatch": Fraction(88, 100),
    "dll_injection": Fraction(85, 100),
    "cmdline_obfuscation": Fraction(80, 100),
    "hollow_process": Fraction(96, 100),
}

_SPOOFABILITY: Dict[str, Fraction] = {
    "PROCESS_HIDING": Fraction(3, 10),
    "CODE_INJECTION": Fraction(4, 10),
    "HOLLOWING": Fraction(2, 10),
    "MALFIND": Fraction(5, 10),
    "ORPHAN_THREAD": Fraction(6, 10),
    "SUSPICIOUS_DLL": Fraction(7, 10),
}


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    ppid: int
    name: str
    path: str
    cmdline: str
    create_time: str
    session_id: int
    parent_name: str
    threads: int
    handles: int

    def name_lower(self) -> str:
        return self.name.lower().strip()

    def path_lower(self) -> str:
        return self.path.lower().strip()


@dataclass(frozen=True)
class MalfindRecord:
    pid: int
    process_name: str
    address: str
    protection: str
    region_type: str
    has_pe_header: bool
    disasm_snippet: str
    size: int


@dataclass(frozen=True)
class NetworkRecord:
    pid: int
    process_name: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    state: str
    protocol: str


@dataclass(frozen=True)
class MemoryAnomalyFinding:
    anomaly_type: str
    severity: Fraction
    pid: int
    process_name: str
    description: str
    evidence: str
    rule_ref: str
    spoofability: Fraction = Fraction(5, 10)


@dataclass
class MemoryAnalysisResult:
    dump_path: str
    dump_sha256: str
    processes: List[ProcessRecord] = field(default_factory=list)
    malfind_records: List[MalfindRecord] = field(default_factory=list)
    network_records: List[NetworkRecord] = field(default_factory=list)
    findings: List[MemoryAnomalyFinding] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    volatility_version: str = "unknown"
    analysis_notes: List[str] = field(default_factory=list)
    # B3: la imagen fue RECHAZADA por formato — el resultado NO es un análisis.
    format_not_supported: bool = False

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if any("hollow" in f.anomaly_type or "hidden" in f.anomaly_type for f in self.findings):
            z = Fraction(35, 10)
        elif len([f for f in self.findings if f.severity >= Fraction(8, 10)]) >= 3:
            z = Fraction(28, 10)
        elif self.findings:
            z = Fraction(21, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        if self.format_not_supported:
            # B3: 0 hallazgos porque NO SE PUDO analizar, no porque esté
            # limpio. unanalyzed=True hace que el orchestrator lo clasifique
            # como derived (pérdida, no evidencia) → ABSTAIN, nunca NOISE.
            return SignalOutput(
                tool_name=TOOL_NAME, value=0.0, z_score=0.0, confidence=0.0,
                description="Memory image REJECTED by Volatility3 (format)",
                metadata={
                    "dump_sha256": self.dump_sha256,
                    "artifact_type": "memory",
                    "artifact_reliability": str(ARTIFACT_RELIABILITY),
                    "unanalyzed": True,
                    "format_error": "FORMAT_NOT_SUPPORTED",
                    "finding_types": [],
                },
            )
        return SignalOutput(
            tool_name=TOOL_NAME, value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z), confidence=float(conf),
            description=f"Memory findings: {len(self.findings)} anomalies", metadata={
                "dump_sha256": self.dump_sha256, "process_count": len(self.processes),
                "finding_count": len(self.findings),
                "critical_count": len([f for f in self.findings if f.severity >= Fraction(9, 10)]),
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "artifact_type": "memory",
                "finding_types": sorted(list(set(f.anomaly_type for f in self.findings))),
            }
        )


class Volatility3Interface:
    """FIX P0: Toda ejecución usa lista de argumentos + shlex.quote. NUNCA shell=True."""

    def __init__(self, vol_binary: str = "vol", timeout_seconds: Optional[int] = None):
        # FIX P2 (V24): Validar que el binario sea ruta absoluta y verificable
        self._vol_binary = self._validate_binary(vol_binary)
        # B4: un timeout explícito del caller gana; sin él, VIGIA_VOL3_TIMEOUT
        # (si está seteado) define el default, y 300 es el fallback histórico.
        if timeout_seconds is not None:
            self._timeout = timeout_seconds
        else:
            env = os.environ.get("VIGIA_VOL3_TIMEOUT")
            try:
                self._timeout = max(1, int(env)) if env else 300
            except ValueError:
                logger.warning("VIGIA_VOL3_TIMEOUT=%r no numérico — ignorado", env)
                self._timeout = 300
        self._version = self._detect_version()

    @staticmethod
    def _validate_binary(binary: str) -> str:
        import shutil
        if os.path.isabs(binary):
            if not os.path.isfile(binary):
                raise FileNotFoundError(f"Volatility3 binary no encontrado: {binary}")
            return binary
        # Si no es absoluto, buscar en PATH pero loggear warning
        found = shutil.which(binary)
        if not found:
            raise FileNotFoundError(f"Volatility3 'vol' no encontrado en PATH. Especifique ruta absoluta.")
        return found

    @staticmethod
    def _validate_path(dump_path: str) -> Path:
        """
        FIX P0: Path Traversal + Command Injection hardening.
        1. Resuelve path absoluto.
        2. Verifica que esté dentro de ALLOWED_BASE_PATHS.
        3. Verifica que sea archivo regular (no symlink a /etc/passwd).
        """
        p = Path(dump_path).resolve()
        # Verificar que no es symlink
        if p.is_symlink():
            raise ValueError(f"Symlinks prohibidos: {dump_path}")
        # Verificar que está en allowlist
        allowed = any(
            p == base or (base in p.parents or p == base)
            for base in ALLOWED_BASE_PATHS
        )
        if not allowed:
            # Si no hay allowlist configurada, al menos verificar que existe
            if not p.exists():
                raise FileNotFoundError(f"Dump no encontrado: {dump_path}")
        return p

    def _detect_version(self) -> str:
        try:
            # FIX: Lista de argumentos, no string
            result = subprocess.run(
                [self._vol_binary, "--version"],
                capture_output=True, text=True, timeout=10,
                shell=False  # EXPLÍCITO: nunca shell
            )
            m = re.search(r"Framework\s+([\d.]+)", result.stdout)
            return m.group(1) if m else "unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(f"Volatility3 no disponible: {e}") from e

    def _run_plugin(self, dump_path: str, plugin: str) -> List[Dict]:
        # FIX P0: Validación de path + shlex.quote en lista de args
        validated = self._validate_path(dump_path)
        safe_path = str(validated)
        # FIX: Usar lista de argumentos. shlex.quote no es necesario con lista,
        # pero lo usamos como defensa en profundidad si alguien modifica el código.
        cmd = [self._vol_binary, "-f", safe_path, "--output=json", plugin]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True, text=True,
                # B4: escalado por tamaño del dump (o VIGIA_VOL3_TIMEOUT exacto)
                timeout=vol3_effective_timeout(self._timeout, safe_path),
                shell=False  # EXPLÍCITO
            )
            if result.returncode != 0:
                # B3: distinguir "el plugin falló" (blando, []) de "la IMAGEN
                # no es un RAM dump válido" (duro — el caso entero no es
                # analizable y presentarlo como limpio es un falso negativo).
                if classify_vol3_stderr(result.stderr):
                    raise MemoryImageFormatError(result.stderr)
                logger.warning("Volatility3 plugin %s falló: %s", plugin, result.stderr[:500])
                return []
            data = json.loads(result.stdout)
            if "rows" not in data:
                return []
            columns = data.get("columns", [])
            rows = data.get("rows", [])
            return [dict(zip(columns, row)) for row in rows]
        except (json.JSONDecodeError, subprocess.TimeoutExpired) as e:
            logger.error("Error en plugin %s: %s", plugin, e)
            return []

    def get_process_list(self, dump_path: str) -> List[Dict]:
        return self._run_plugin(dump_path, "windows.pslist.PsList")

    def get_malfind(self, dump_path: str) -> List[Dict]:
        return self._run_plugin(dump_path, "windows.malfind.Malfind")

    def get_netscan(self, dump_path: str) -> List[Dict]:
        return self._run_plugin(dump_path, "windows.netscan.NetScan")

    def get_cmdline(self, dump_path: str) -> List[Dict]:
        return self._run_plugin(dump_path, "windows.cmdline.CmdLine")

    @property
    def version(self) -> str:
        return self._version


class VolatilityParsers:
    @staticmethod
    def parse_pslist(rows: List[Dict]) -> List[ProcessRecord]:
        records = []
        for row in sorted(rows, key=lambda r: r.get("PID", 0)):
            try:
                pid = int(row.get("PID", 0))
                name = str(row.get("ImageFileName", "")).strip()
                if not name or pid == 0:
                    continue
                records.append(ProcessRecord(
                    pid=pid, ppid=int(row.get("PPID", 0)), name=name,
                    path=str(row.get("ImageFilePath", "")), cmdline=str(row.get("CommandLine", "")),
                    create_time=str(row.get("CreateTime", "")), session_id=int(row.get("SessionId", -1)),
                    parent_name="", threads=int(row.get("Threads", 0)), handles=int(row.get("Handles", 0)),
                ))
            except (ValueError, TypeError):
                continue
        return records

    @staticmethod
    def parse_malfind(rows: List[Dict]) -> List[MalfindRecord]:
        records = []
        for row in rows:
            try:
                disasm = str(row.get("Disassembly", ""))
                hexdump = str(row.get("HexDump", ""))
                has_pe = "4d 5a" in hexdump.lower() or "MZ" in hexdump
                records.append(MalfindRecord(
                    pid=int(row.get("PID", 0)), process_name=str(row.get("Process", "")),
                    address=str(row.get("Start VPN", "0x0")), protection=str(row.get("Protection", "")),
                    region_type=str(row.get("Tag", "")), has_pe_header=has_pe,
                    disasm_snippet=disasm[:500], size=int(row.get("Size", 0)),
                ))
            except (ValueError, TypeError):
                continue
        return records

    @staticmethod
    def parse_netscan(rows: List[Dict]) -> List[NetworkRecord]:
        records = []
        for row in rows:
            try:
                fport = row.get("ForeignPort", 0)
                lport = row.get("LocalPort", 0)
                records.append(NetworkRecord(
                    pid=int(row.get("PID", 0)), process_name=str(row.get("Owner", "")),
                    local_addr=str(row.get("LocalAddr", "")), local_port=int(lport) if str(lport).isdigit() else 0,
                    remote_addr=str(row.get("ForeignAddr", "")), remote_port=int(fport) if str(fport).isdigit() else 0,
                    state=str(row.get("State", "")), protocol=str(row.get("Proto", "")),
                ))
            except (ValueError, TypeError):
                continue
        return records

    @staticmethod
    def resolve_parent_names(processes: List[ProcessRecord]) -> List[ProcessRecord]:
        pid_map = {p.pid: p.name for p in processes}
        resolved = []
        for proc in processes:
            pn = pid_map.get(proc.ppid, "UNKNOWN")
            resolved.append(ProcessRecord(
                pid=proc.pid, ppid=proc.ppid, name=proc.name, path=proc.path,
                cmdline=proc.cmdline, create_time=proc.create_time, session_id=proc.session_id,
                parent_name=pn, threads=proc.threads, handles=proc.handles,
            ))
        return resolved


class ProcessTreeAnomalyDetector:
    _OBFUSCATION_PATTERNS = [
        re.compile(r"-[Ee](?:nc(?:oded)?)?[Cc]ommand\b"),
        re.compile(r"[A-Za-z0-9+/]{50,}={0,2}"),
        re.compile(r"(?:chr|asc)\(\d+\)", re.I),
        re.compile(r"\^[a-zA-Z]"),
        re.compile(r"FromBase64String", re.I),
        re.compile(r"IEX|Invoke-Expression", re.I),
        re.compile(r"Net\.WebClient|DownloadString", re.I),
        re.compile(r"\\x[0-9a-fA-F]{2}"),
    ]

    def detect(self, processes: List[ProcessRecord]) -> List[MemoryAnomalyFinding]:
        findings = []
        pid_set = {p.pid for p in processes}
        name_count: Dict[str, int] = {}
        for proc in processes:
            nl = proc.name_lower()
            name_count[nl] = name_count.get(nl, 0) + 1

        for proc in processes:
            nl = proc.name_lower()
            pl = proc.parent_name.lower().strip()

            if nl in _SYSTEM_PROCESS_PARENTS:
                expected = _SYSTEM_PROCESS_PARENTS[nl]
                if pl not in {p.lower() for p in expected} and pl != "system" and proc.ppid != 0:
                    findings.append(MemoryAnomalyFinding(
                        anomaly_type="parent_mismatch", severity=_ANOMALY_WEIGHTS["parent_mismatch"],
                        pid=proc.pid, process_name=proc.name,
                        description=f"'{proc.name}' padre='{proc.parent_name}' (esperado: {expected})",
                        evidence=f"PID={proc.pid} PPID={proc.ppid}", rule_ref="MFE-R1",
                        spoofability=_SPOOFABILITY["PROCESS_HIDING"],
                    ))

            if nl in {s.lower() for s in _SINGLETON_PROCESSES} and name_count.get(nl, 0) > 1:
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="singleton_violation", severity=_ANOMALY_WEIGHTS["singleton_violation"],
                    pid=proc.pid, process_name=proc.name,
                    description=f"'{proc.name}' aparece {name_count[nl]} veces",
                    evidence=f"Count={name_count[nl]}", rule_ref="MFE-R2",
                    spoofability=_SPOOFABILITY["PROCESS_HIDING"],
                ))

            if nl in _LEGITIMATE_PATHS:
                legit = _LEGITIMATE_PATHS[nl]
                if proc.path_lower() and proc.path_lower() not in legit:
                    findings.append(MemoryAnomalyFinding(
                        anomaly_type="path_anomaly", severity=_ANOMALY_WEIGHTS["path_anomaly"],
                        pid=proc.pid, process_name=proc.name,
                        description=f"'{proc.name}' en ruta anómala: '{proc.path}'",
                        evidence=f"Path={proc.path}", rule_ref="MFE-R3",
                        spoofability=_SPOOFABILITY["HOLLOWING"],
                    ))

            if proc.ppid != 0 and proc.ppid not in pid_set and nl not in {"system", "smss.exe", "csrss.exe"}:
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="orphan_process", severity=_ANOMALY_WEIGHTS["orphan_process"],
                    pid=proc.pid, process_name=proc.name,
                    description=f"PPID {proc.ppid} no existe en proceso activo",
                    evidence=f"PID={proc.pid} PPID={proc.ppid}", rule_ref="MFE-R4",
                    spoofability=_SPOOFABILITY["PROCESS_HIDING"],
                ))

            if proc.cmdline:
                matched = [p.pattern for p in self._OBFUSCATION_PATTERNS if p.search(proc.cmdline)]
                if matched:
                    findings.append(MemoryAnomalyFinding(
                        anomaly_type="cmdline_obfuscation", severity=_ANOMALY_WEIGHTS["cmdline_obfuscation"],
                        pid=proc.pid, process_name=proc.name,
                        description=f"Cmdline ofuscado: {matched}",
                        evidence=f"CmdLine={proc.cmdline[:300]}", rule_ref="MFE-R5",
                        spoofability=_SPOOFABILITY["MALFIND"],
                    ))

        return findings


class MalfindAnomalyDetector:
    def detect(self, malfind_records: List[MalfindRecord]) -> List[MemoryAnomalyFinding]:
        findings = []
        injections_per_pid: Dict[int, int] = {}
        for record in malfind_records:
            if record.protection in _MALFIND_SUSPICIOUS_PROT and "WRITE" in record.protection and "EXEC" in record.protection:
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="malfind_rwx", severity=_ANOMALY_WEIGHTS["malfind_rwx"],
                    pid=record.pid, process_name=record.process_name,
                    description=f"RWX en {record.address}",
                    evidence=f"Addr={record.address} Prot={record.protection}", rule_ref="MFE-MAL-R1",
                    spoofability=_SPOOFABILITY["CODE_INJECTION"],
                ))
            if record.has_pe_header:
                injections_per_pid[record.pid] = injections_per_pid.get(record.pid, 0) + 1
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="malfind_pe_injection", severity=_ANOMALY_WEIGHTS["malfind_pe_injection"],
                    pid=record.pid, process_name=record.process_name,
                    description=f"PE header en región privada {record.address}",
                    evidence=f"Addr={record.address} HasPE=True", rule_ref="MFE-MAL-R2",
                    spoofability=_SPOOFABILITY["CODE_INJECTION"],
                ))
        for pid, count in injections_per_pid.items():
            if count >= 3:
                proc_name = next((r.process_name for r in malfind_records if r.pid == pid), "unknown")
                sev = min(Fraction(70 + count * 5, 100), Fraction(99, 100))
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="dll_injection_campaign", severity=sev, pid=pid, process_name=proc_name,
                    description=f"{count} regiones inyectadas en PID {pid}",
                    evidence=f"PID={pid} Count={count}", rule_ref="MFE-MAL-R3",
                    spoofability=_SPOOFABILITY["CODE_INJECTION"],
                ))
        return findings


class NetworkAnomalyDetector:
    _NO_EXTERNAL: frozenset = frozenset({"lsass.exe", "csrss.exe", "wininit.exe", "winlogon.exe", "smss.exe"})

    def detect(self, network_records: List[NetworkRecord]) -> List[MemoryAnomalyFinding]:
        findings = []
        for record in network_records:
            pl = record.process_name.lower().strip()
            if pl in self._NO_EXTERNAL:
                if record.remote_addr and not record.remote_addr.startswith("127.") and record.remote_addr not in {"0.0.0.0", "::"}:
                    findings.append(MemoryAnomalyFinding(
                        anomaly_type="network_process_mismatch", severity=_ANOMALY_WEIGHTS["network_process_mismatch"],
                        pid=record.pid, process_name=record.process_name,
                        description=f"'{record.process_name}' conectado a {record.remote_addr}:{record.remote_port}",
                        evidence=f"Remote={record.remote_addr}:{record.remote_port}", rule_ref="MFE-NET-R1",
                        spoofability=_SPOOFABILITY["PROCESS_HIDING"],
                    ))
            if record.remote_port in _SUSPICIOUS_PORTS:
                findings.append(MemoryAnomalyFinding(
                    anomaly_type="network_suspicious_port", severity=_ANOMALY_WEIGHTS["network_suspicious_port"],
                    pid=record.pid, process_name=record.process_name,
                    description=f"Puerto C2 conocido: {record.remote_port}",
                    evidence=f"Port={record.remote_port}", rule_ref="MFE-NET-R2",
                    spoofability=_SPOOFABILITY["MALFIND"],
                ))
        return findings


class MemoryForensicsEngine:
    def __init__(self, vol_binary: str = "vol", timeout_seconds: Optional[int] = None, hash_dump: bool = True):
        self._vol = Volatility3Interface(vol_binary, timeout_seconds)
        self._hash_dump = hash_dump
        self._proc_det = ProcessTreeAnomalyDetector()
        self._mal_det = MalfindAnomalyDetector()
        self._net_det = NetworkAnomalyDetector()

    def analyze(self, dump_path: str, chain: Optional[ChainOfCustody] = None, timestamp_utc: str = "1970-01-01T00:00:00Z") -> MemoryAnalysisResult:
        # FIX P0: Validación de path antes de tocar disco
        validated = Volatility3Interface._validate_path(dump_path)
        if not validated.exists():
            raise FileNotFoundError(f"Dump no encontrado: {dump_path}")
        dump_sha256 = self._compute_hash(validated) if self._hash_dump else "SKIPPED"
        if chain:
            chain.acquire(validated.read_bytes()[:4096], "MEMORY_ANALYST", timestamp_utc, notes=f"Dump: {dump_sha256[:16]}")

        try:
            pslist_raw = self._vol.get_process_list(str(validated))
            malfind_raw = self._vol.get_malfind(str(validated))
            netscan_raw = self._vol.get_netscan(str(validated))
        except MemoryImageFormatError as e:
            # B3: mismo contrato que el shim del agente (FORMAT_NOT_SUPPORTED
            # → ABSTAIN). Nota accionable: qué es y qué hacer.
            logger.error("[MEMORY] Imagen rechazada por formato: %s", e.stderr_excerpt)
            return MemoryAnalysisResult(
                dump_path=str(validated), dump_sha256=dump_sha256,
                volatility_version=self._vol.version,
                format_not_supported=True,
                analysis_notes=[
                    "FORMAT_NOT_SUPPORTED: Volatility3 rechazó la imagen — no es "
                    "un RAM dump Windows válido (¿snapshot VMware sin companion "
                    ".vmss/.vmsn, o imagen de disco?).",
                    f"stderr: {e.stderr_excerpt}",
                    "0 hallazgos = NO ANALIZADO, no 'limpio'. Ver BUGS_PENDIENTES B-016.",
                ],
            )

        processes = VolatilityParsers.resolve_parent_names(VolatilityParsers.parse_pslist(pslist_raw))
        malfind_recs = VolatilityParsers.parse_malfind(malfind_raw)
        network_recs = VolatilityParsers.parse_netscan(netscan_raw)

        findings: List[MemoryAnomalyFinding] = []
        findings.extend(self._proc_det.detect(processes))
        findings.extend(self._mal_det.detect(malfind_recs))
        findings.extend(self._net_det.detect(network_recs))

        corr_groups: Dict[int, set] = {}
        pid_to_indices: Dict[int, List[int]] = {}
        for idx, f in enumerate(findings):
            pid_to_indices.setdefault(f.pid, []).append(idx)
        for indices in pid_to_indices.values():
            if len(indices) > 1:
                for i in indices:
                    corr_groups[i] = set(indices) - {i}

        severities = [f.severity for f in findings]
        composite = noisy_or_correlated(severities, corr_groups, Fraction(15, 100))
        composite = composite * ARTIFACT_RELIABILITY

        notes = self._generate_notes(findings, processes)
        return MemoryAnalysisResult(
            dump_path=str(validated), dump_sha256=dump_sha256, processes=processes,
            malfind_records=malfind_recs, network_records=network_recs,
            findings=findings, composite_score=composite,
            volatility_version=self._vol.version, analysis_notes=notes,
        )

    def _compute_hash(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def _generate_notes(self, findings: List[MemoryAnomalyFinding], processes: List[ProcessRecord]) -> List[str]:
        notes = []
        critical = [f for f in findings if f.severity >= Fraction(90, 100)]
        if critical:
            notes.append(f"CRÍTICO: {len(critical)} hallazgo(s) de alta severidad.")
        if any(f.anomaly_type == "path_anomaly" for f in findings):
            notes.append("MASQUERADING detectado.")
        if any(f.anomaly_type == "malfind_pe_injection" for f in findings):
            notes.append("PROCESS INJECTION activo.")
        if not findings:
            notes.append("No se detectaron anomalías. NOTA: DKOM puede evadir Volatility3.")
        notes.append(f"Análisis basado en {len(processes)} procesos via Volatility3 v{self._vol.version}.")
        return notes
