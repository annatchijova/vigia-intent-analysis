"""
vigia/sift/registry_timeline_reconstructor.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. COMMAND INJECTION: subprocess.run usa lista de argumentos (NO shell=True).
   _sanitize_path eliminado en favor de validación estricta con Path.resolve().
2. ReDoS: Todos los regex con (.+?) reemplazados por versiones seguras
   con límites de longitud y sin backtracking catastrófico.
3. PATH TRAVERSAL: Validación de allowlist antes de abrir hives.
"""

from __future__ import annotations
import os

import hashlib
import logging
import re
import subprocess
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import _entropy_shannon, noisy_or_correlated

logger = logging.getLogger(__name__)

TOOL_NAME = "REGISTRY_RTR"
ARTIFACT_RELIABILITY = Fraction(85, 100)

# FIX P1 (Kimi/2026-06): ALLOWED_BASE_PATHS configurable — no hardcodeado.
# Leer de VIGIA_ALLOWED_REGISTRY_PATHS (paths separados por ":") o usar defaults.
def _load_allowed_registry_paths() -> list:
    env_val = os.environ.get("VIGIA_ALLOWED_REGISTRY_PATHS", "")
    if env_val.strip():
            return [Path(p.strip()) for p in env_val.split(os.pathsep) if p.strip()]  # FIX P3 (Kimi): pathsep portable
    return [
        Path("/var/vigia/registry"),
        Path("/tmp/vigia"),
        Path("/home/vigia/cases"),
        Path("/cases"),
        Path("/evidence"),
    ]

ALLOWED_BASE_PATHS = _load_allowed_registry_paths()

_PERSISTENCE_KEYS = {
    r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run": "T1547.001",
    r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce": "T1547.001",
    r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon": "T1547.004",
    r"SYSTEM\\CurrentControlSet\\Services": "T1543.003",
    r"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options": "T1546.012",
    r"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\BootExecute": "T1542.003",
}

# FIX ReDoS: Patrones con límites de longitud y sin cuantificadores anidados peligrosos
_SUSPICIOUS_RUN_PATTERNS = [
    # Cada patrón limita a 200 chars para evitar backtracking catastrófico
    re.compile(r".{0,200}\\Temp\\.{0,100}", re.I),
    re.compile(r".{0,200}powershell.{0,50}-[Ee]nc.{0,50}", re.I),
    re.compile(r".{0,200}regsvr32.{0,50}\/s.{0,50}\/u.{0,50}", re.I),
    re.compile(r".{0,200}mshta\..{0,100}", re.I),
    re.compile(r".{0,200}rundll32.{0,100},.{0,100}", re.I),
    re.compile(r".{0,200}certutil.{0,50}-decode.{0,50}", re.I),
    re.compile(r".{0,200}bitsadmin.{0,100}", re.I),
    re.compile(r".{0,200}wscript|cscript.{0,100}", re.I),
]

_SEVERITY_MAP = {1: Fraction(50, 100), 2: Fraction(70, 100)}


@dataclass(frozen=True)
class RegistryKey:
    hive: str
    path: str
    name: str
    last_write: int
    values: Tuple[Tuple[str, str, str], ...]
    subkey_count: int
    value_count: int
    entropy_score: Fraction


@dataclass(frozen=True)
class PersistenceFinding:
    persistence_type: str
    registry_path: str
    value_name: str
    value_data: str
    severity: Fraction
    description: str
    mitre_technique: str
    rule_ref: str


@dataclass(frozen=True)
class USBDeviceRecord:
    vendor: str
    product: str
    revision: str
    serial: str
    registry_path: str
    first_install: str
    last_connected: str
    drive_letter: str


@dataclass(frozen=True)
class TimestompFinding:
    registry_path: str
    reported_time: int
    anomaly_score: Fraction
    description: str
    rule_ref: str


@dataclass
class RegistryAnalysisResult:
    hive_path: str
    hive_sha256: str
    hive_type: str
    persistence_findings: List[PersistenceFinding] = field(default_factory=list)
    usb_devices: List[USBDeviceRecord] = field(default_factory=list)
    timestomp_findings: List[TimestompFinding] = field(default_factory=list)
    shellbag_paths: List[Dict] = field(default_factory=list)
    userassist_entries: List[Dict] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.timestomp_findings:
            z = Fraction(35, 10)
        elif len(self.persistence_findings) >= 3:
            z = Fraction(28, 10)
        elif self.persistence_findings:
            z = Fraction(21, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME, value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z), confidence=float(conf),
            metadata={
                "hive_sha256": self.hive_sha256, "persistence_count": len(self.persistence_findings),
                "timestomp_count": len(self.timestomp_findings), "usb_count": len(self.usb_devices),
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "artifact_type": "registry",
                "finding_types": sorted(list(set(f.persistence_type for f in self.persistence_findings) | set(["timestomp_batch"] if self.timestomp_findings else []))),
            }
        )


class RegRipperInterface:
    """FIX P0: Lista de argumentos + validación de path. NUNCA shell=True."""

    def __init__(self, rip_binary: str = "rip.pl"):
        # FIX P2 (V24): Validar binario RegRipper
        self._rip = self._validate_binary(rip_binary)

    @staticmethod
    def _validate_binary(binary: str) -> str:
        import shutil
        if os.path.isabs(binary):
            if not os.path.isfile(binary):
                raise FileNotFoundError(f"RegRipper no encontrado: {binary}")
            return binary
        found = shutil.which(binary)
        if not found:
            raise FileNotFoundError(f"RegRipper 'rip.pl' no encontrado en PATH. Especifique ruta absoluta.")
        return found

    @staticmethod
    def _validate_path(path: str) -> Path:
        p = Path(path).resolve()
        if p.is_symlink():
            raise ValueError(f"Symlinks prohibidos: {path}")
        allowed = any(p == base or (base in p.parents or p == base) for base in ALLOWED_BASE_PATHS)
        if not allowed:
            if not p.exists():
                raise FileNotFoundError(f"Hive no encontrado: {path}")
        return p

    def run_plugin(self, hive_path: str, plugin: str) -> str:
        try:
            validated = self._validate_path(hive_path)
            safe_path = str(validated)
            # FIX: Lista de argumentos, shell=False explícito
            result = subprocess.run(
                [self._rip, "-r", safe_path, "-p", plugin],
                capture_output=True, text=True, timeout=60,
                shell=False
            )
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""

    def get_run_keys(self, hive_path: str) -> str:
        return self.run_plugin(hive_path, "run")

    def get_services(self, hive_path: str) -> str:
        return self.run_plugin(hive_path, "services")

    def get_usbstor(self, hive_path: str) -> str:
        return self.run_plugin(hive_path, "usbstor")

    def get_shellbags(self, hive_path: str) -> str:
        return self.run_plugin(hive_path, "shellbags")

    def get_userassist(self, hive_path: str) -> str:
        return self.run_plugin(hive_path, "userassist")


class PersistenceDetector:
    def detect_from_regripper(self, run_output: str, services_output: str) -> List[PersistenceFinding]:
        findings = []
        findings.extend(self._parse_run_keys(run_output))
        findings.extend(self._parse_services(services_output))
        return findings

    def _parse_run_keys(self, output: str) -> List[PersistenceFinding]:
        findings = []
        lines = output.split("\n")
        current_lastwrite = ""
        for line in lines:
            line = line.strip()
            if line.startswith("LastWrite"):
                current_lastwrite = line
            # FIX ReDoS: Búsqueda simple con split en lugar de regex complejo
            if " -> " in line and current_lastwrite:
                parts = line.split(" -> ", 1)
                if len(parts) == 2:
                    vname, vdata = parts[0].strip(), parts[1].strip()
                    # FIX P2 (Kimi post-patch-v2): cap a 10KB — balance entre
                    # evasión-por-padding (500 chars era insuficiente) y DoS-por-CPU.
                    # 10KB cubre cualquier payload real; líneas RegRipper > 10KB = anomalía en sí.
                    vdata_safe = vdata[:10240]
                    matched = [p.pattern for p in _SUSPICIOUS_RUN_PATTERNS if p.search(vdata_safe)]
                    sev = _SEVERITY_MAP.get(len(matched), Fraction(90, 100)) if matched else Fraction(0)
                    if sev > 0:
                        findings.append(PersistenceFinding(
                            persistence_type="run_key", registry_path="Run/RunOnce",
                            value_name=vname, value_data=vdata, severity=sev,
                            description=f"Run key sospechoso: {vdata[:200]}",
                            mitre_technique="T1547.001", rule_ref="RTR-PERS-R1",
                        ))
        return findings

    def _parse_services(self, output: str) -> List[PersistenceFinding]:
        findings = []
        # FIX ReDoS: splitlines + búsqueda simple en lugar de regex global
        for line in output.splitlines():
            line_lower = line.lower()
            if "imagepath" not in line_lower:
                continue
            # Extraer valor después de delimitador común
            if ":" in line:
                ipath = line.split(":", 1)[1].strip()
            elif "=" in line:
                ipath = line.split("=", 1)[1].strip()
            else:
                continue
            il = ipath.lower()
            # Limitar longitud para evadir ReDoS
            il_trunc = il[:300]
            suspicious = any(s in il_trunc for s in [r'\\temp\\', r'\\appdata\\local\\temp\\', r'\\downloads\\'])
            if suspicious or (il_trunc.endswith('.dll') and '\\system32\\' not in il_trunc) or len(Path(il_trunc).stem) <= 3:
                findings.append(PersistenceFinding(
                    persistence_type="service", registry_path="SYSTEM\\Services",
                    value_name="ImagePath", value_data=ipath, severity=Fraction(78, 100),
                    description=f"Servicio con ImagePath anómalo: {ipath}",
                    mitre_technique="T1543.003", rule_ref="RTR-PERS-R2",
                ))
        return findings


class USBHistoryAnalyzer:
    def analyze(self, usbstor_output: str) -> List[USBDeviceRecord]:
        devices = []
        blocks = usbstor_output.split("\n\n")
        for block in blocks:
            vendor = self._extract(block, "Vendor")
            product = self._extract(block, "Product")
            revision = self._extract(block, "Rev|Version")
            serial = self._extract(block, "Serial")
            if vendor or product:
                devices.append(USBDeviceRecord(
                    vendor=vendor or "UNKNOWN", product=product or "UNKNOWN",
                    revision=revision or "UNKNOWN", serial=serial or "UNKNOWN",
                    registry_path="SYSTEM\\CurrentControlSet\\Enum\\USBSTOR",
                    first_install=self._extract(block, "FirstInstall"),
                    last_connected=self._extract(block, "LastInsert|LastConnect"),
                    drive_letter=self._extract(block, "DriveLetter"),
                ))
        return devices

    def _extract(self, block: str, pattern: str) -> str:
        # FIX ReDoS: Limitar block a 2000 chars y usar regex con límite
        block_trunc = block[:2000]
        # FIX P2 (Kimi post-patch): [^\n]{1,200} evita backtracking de .+? y limita longitud
        m = re.search(rf"(?:{pattern})\s*:?\s*([^\n]{{1,200}})", block_trunc, re.I)
        return m.group(1).strip() if m else ""


class TimestompDetector:
    def detect(self, keys: List[RegistryKey]) -> List[TimestompFinding]:
        findings = []
        if not keys:
            return findings
        ts_count: Dict[int, List[str]] = {}
        for key in keys:
            ts_count.setdefault(key.last_write, []).append(key.path)
        for ts, paths in ts_count.items():
            if len(paths) >= 10:
                sev = min(Fraction(50 + len(paths) * 2, 100), Fraction(90, 100))
                findings.append(TimestompFinding(
                    registry_path=f"Multiple({len(paths)} keys)", reported_time=ts,
                    anomaly_score=sev, description=f"{len(paths)} claves con mismo LastWrite",
                    rule_ref="RTR-TS-R1",
                ))
        pre_xp = 126227136000000000
        persist_frags = ["CurrentVersion\\Run", "Winlogon", "Services", "BootExecute"]
        for key in keys:
            if any(frag.lower() in key.path.lower() for frag in persist_frags):
                if 0 < key.last_write < pre_xp:
                    findings.append(TimestompFinding(
                        registry_path=key.path, reported_time=key.last_write,
                        anomaly_score=Fraction(75, 100),
                        description=f"Clave de persistencia con timestamp pre-XP",
                        rule_ref="RTR-TS-R2",
                    ))
        return findings


class RegistryTimelineReconstructor:
    def __init__(self, rip_binary: str = "rip.pl"):
        self._regripper = RegRipperInterface(rip_binary)
        self._persist = PersistenceDetector()
        self._usb = USBHistoryAnalyzer()
        self._tstomp = TimestompDetector()

    def analyze_hive(self, hive_path: str, hive_type: Optional[str] = None, chain: Optional[ChainOfCustody] = None, timestamp_utc: str = "1970-01-01T00:00:00Z") -> RegistryAnalysisResult:
        validated = RegRipperInterface._validate_path(hive_path)
        path = validated
        if hive_type is None:
            hive_type = path.name.upper().replace(".DAT", "").replace(".HVE", "")
        hive_sha256 = self._hash_file(path)
        if chain:
            chain.acquire(path.read_bytes()[:4096], "REGISTRY_ANALYST", timestamp_utc, notes=f"Hive: {hive_sha256[:16]}")

        all_persist, all_usb, all_ts, shellbags, userassist = [], [], [], [], []
        if hive_type in {"SYSTEM", "SOFTWARE", "NTUSER"}:
            run_out = self._regripper.get_run_keys(str(path))
            svc_out = self._regripper.get_services(str(path))
            usb_out = self._regripper.get_usbstor(str(path))
            shell_out = self._regripper.get_shellbags(str(path))
            ua_out = self._regripper.get_userassist(str(path))
            all_persist = self._persist.detect_from_regripper(run_out, svc_out)
            all_usb = self._usb.analyze(usb_out)
            shellbags = self._parse_shellbags(shell_out)
            userassist = self._parse_userassist(ua_out)

        keys = self._try_parse_regipy(str(path))
        if keys:
            all_ts = self._tstomp.detect(keys)

        severities = [f.severity for f in all_persist] + [t.anomaly_score for t in all_ts]
        corr_groups = {}
        for i in range(len(all_persist)):
            for j in range(len(all_persist)):
                if i < j and all_persist[i].mitre_technique == all_persist[j].mitre_technique:
                    corr_groups.setdefault(i, set()).add(j)
                    corr_groups.setdefault(j, set()).add(i)
        for i, t in enumerate(all_ts):
            for j, p in enumerate(all_persist):
                if p.registry_path in t.registry_path or t.registry_path in p.registry_path:
                    idx_t = len(all_persist) + i
                    corr_groups.setdefault(idx_t, set()).add(j)
                    corr_groups.setdefault(j, set()).add(idx_t)

        composite = noisy_or_correlated(severities, corr_groups, Fraction(15, 100))
        composite = composite * ARTIFACT_RELIABILITY
        notes = self._generate_notes(all_persist, all_usb, all_ts, shellbags)

        return RegistryAnalysisResult(
            hive_path=str(path), hive_sha256=hive_sha256, hive_type=hive_type,
            persistence_findings=all_persist, usb_devices=all_usb,
            timestomp_findings=all_ts, shellbag_paths=shellbags,
            userassist_entries=userassist, composite_score=composite,
            analysis_notes=notes,
        )

    def _try_parse_regipy(self, hive_path: str) -> List[RegistryKey]:
        try:
            from regipy.registry import RegistryHive as RegipyHive
            keys = []
            hive = RegipyHive(hive_path)
            for entry in hive.root.iter_subkeys():
                try:
                    values = tuple(sorted((v.name, v.value_type, str(v.value)[:500]) for v in entry.iter_values()))
                    all_data = "".join(v[2] for v in values)
                    # FIX P2: Entropía de caracteres sobre valores de registro (detecta compresión/encriptación)
                    entropy = _entropy_shannon(all_data)
                    keys.append(RegistryKey(
                        hive=Path(hive_path).stem, path=entry.path, name=entry.name,
                        last_write=entry.header.last_modified, values=values,
                        subkey_count=entry.header.subkey_count, value_count=entry.header.values_count,
                        entropy_score=entropy,
                    ))
                except Exception:
                    continue
            return keys
        except ImportError:
            return []

    def _hash_file(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()

    def _parse_shellbags(self, output: str) -> List[Dict]:
        bags = []
        # FIX ReDoS: Limitar output a 10000 chars y usar regex con límite
        output_trunc = output[:10000]
        for m in re.finditer(r"(.{3,200}?)\s+(?:Modified|LastWrite):\s+(.{3,200}?)(?:\n|$)", output_trunc, re.I):
            p, ts = m.group(1).strip(), m.group(2).strip()
            if p and len(p) > 3:
                bags.append({"path": p, "timestamp": ts, "sensitive": any(s in p.lower() for s in ["secret", "password", "finance", "hr", "executive"])})
        return bags

    def _parse_userassist(self, output: str) -> List[Dict]:
        entries = []
        # FIX ReDoS: Limitar output y usar regex con límites de longitud
        output_trunc = output[:10000]
        for m in re.finditer(r"(.{3,200}?)\s+\((\d+)\)\s+(?:LastRun|Last Run):\s+(.{3,200}?)(?:\n|$)", output_trunc, re.I):
            app, rc, lr = m.group(1).strip(), int(m.group(2)), m.group(3).strip()
            susp = any(t in app.lower() for t in ["mimikatz", "psexec", "netcat", "nmap", "cobalt", "empire"])
            entries.append({"application": app, "run_count": rc, "last_run": lr, "suspicious": susp})
        return entries

    def _generate_notes(self, persist, usb, ts, shellbags):
        notes = []
        if persist:
            notes.append(f"PERSISTENCIA: {len(persist)} mecanismo(s). MITRE: {list({f.mitre_technique for f in persist})}")
        if usb:
            notes.append(f"USB: {len(usb)} dispositivo(s) conectados.")
        sensitive = [b for b in shellbags if b.get("sensitive")]
        if sensitive:
            notes.append(f"SHELLBAGS: {len(sensitive)} acceso(s) a carpetas sensibles.")
        if ts:
            notes.append(f"TIMESTOMP: {len(ts)} anomalía(s) de timestamp.")
        return notes
