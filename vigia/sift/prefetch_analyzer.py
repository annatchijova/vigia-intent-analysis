"""
vigia/sift/prefetch_analyzer.py

Analizador de Prefetch de Windows.
Detecta ejecución de programas sospechosos, borrado selectivo de prefetch
(indicador de anti-forense), y correlación con otros artefactos.

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

import datetime
import hashlib
import logging
import struct
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody

logger = logging.getLogger(__name__)

# B-208: real last_execution_time/run_count recovery for MAM-compressed
# (Win10+) prefetch requires XPRESS Huffman decompression + SCCA-structure
# parsing. pyscca (libscca-python, libyal) already does this correctly and
# is the reference implementation real forensic tools use — hand-rolling it
# here would duplicate a well-audited binary-format parser with no
# independent way to validate correctness. It is a compiled extension (not
# pure pip), so it is treated as an OPTIONAL enrichment: Mode 1 stays
# offline/zero-dependency without it, degrading only the precision of these
# two fields, never the core detection path (filename/blacklist matching,
# which is signature- and stem-based and does not depend on pyscca).
try:
    import pyscca
    _PYSCCA_AVAILABLE = True
except ImportError:
    pyscca = None
    _PYSCCA_AVAILABLE = False
    logger.warning(
        "[PREFETCH_ANALYZER] pyscca (libscca-python) not installed — "
        "last_execution_time/run_count will report 'unknown'/1 placeholders "
        "instead of real values recovered from Win10+ MAM-compressed prefetch. "
        "Optional: pip install libscca-python (requires system libscca)."
    )

# FILETIME epoch (1601-01-01) in seconds before the Unix epoch, for exact
# integer conversion of pyscca's 100ns-tick FILETIME integers to UTC.
_FILETIME_EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)

TOOL_NAME = "PREFETCH_ANALYZER"
ARTIFACT_RELIABILITY = Fraction(70, 100)


def _enrich_via_pyscca(path: Path) -> Optional[Tuple[str, int]]:
    """Best-effort real ``(last_execution_time, run_count)`` via pyscca.

    Returns None on any failure — pyscca absent, or content pyscca cannot
    parse (e.g. a synthetic/garbage .pf used in tests). This is deliberately
    separate from the signature check in ``_parse_pf``: a signature-valid
    file that pyscca cannot fully parse still yields a PrefetchRecord with
    placeholder timing fields, it is never counted as unparsed for that
    reason alone.
    """
    if not _PYSCCA_AVAILABLE:
        return None
    scca_file = pyscca.file()
    try:
        scca_file.open(str(path))
        run_count = scca_file.run_count
        latest_ticks = 0
        for slot in range(8):
            ticks = scca_file.get_last_run_time_as_integer(slot)
            if ticks and ticks > latest_ticks:
                latest_ticks = ticks
        if latest_ticks == 0:
            return None
        # FILETIME: 100ns ticks since 1601-01-01 — integer division only,
        # no float in this conversion (sub-microsecond remainder discarded,
        # ISO 8601 report precision is microseconds).
        microseconds = latest_ticks // 10
        timestamp = _FILETIME_EPOCH + datetime.timedelta(microseconds=microseconds)
        iso = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return iso, run_count
    except Exception as exc:
        logger.debug("[PREFETCH_ANALYZER] pyscca could not parse %s: %s", path, exc)
        return None
    finally:
        try:
            scca_file.close()
        except Exception:
            pass

# LOL-bins y herramientas de hacking cuya ejecución es sospechosa.
# Ruta: suspicious_executions → z=2.5 si >=3 hits, z=1.8 si 1-2 hits.
ANTI_FORENSIC_PREFETCH_SIGNS = [
    "mimikatz.exe", "psexec.exe", "procdump.exe", "nc.exe", "netcat.exe",
    "rundll32.exe", "regsvr32.exe", "mshta.exe", "certutil.exe",
]

# B-132: Herramientas de borrado seguro cuya presencia en Prefetch confirma
# comportamiento anti-forense activo (destrucción de evidencia).
# Ruta: anti_forensic_deletions → z=3.2 (el z más alto del analyzer).
# Separadas de ANTI_FORENSIC_PREFETCH_SIGNS porque rundll32/regsvr32 están
# en entornos benignos; sdelete en Prefetch NO tiene justificación forense
# legítima en un caso de exfiltración.
ANTI_FORENSIC_TOOL_EXECUTION_SIGNS = [
    "sdelete.exe",    # Sysinternals SDelete: borrado seguro de archivos — destrucción de evidencia
    "sdelete64.exe",  # Variante 64-bit del mismo
]

# B-132: Herramientas especializadas que indican reconocimiento o exfiltración.
# Ruta: suspicious_executions → mismo z que ANTI_FORENSIC_PREFETCH_SIGNS.
SUSPICIOUS_TOOL_SIGNS = [
    "smallftpd.exe",                  # Servidor FTP no autorizado — vector de exfiltración
    "netstumbler.exe",                # Herramienta de war-driving WiFi — reconocimiento de red
    "netstumblerinstaller_0_4_0 (1",  # Instalador de NetStumbler (nombre extraído del stem .pf)
    "veracrypt format.exe",           # Creación de volumen VeraCrypt — posible ocultamiento (con espacio)
    "veracrypt.exe",                  # Ejecutable principal de VeraCrypt
]


@dataclass
class PrefetchRecord:
    filename: str
    hash: str
    last_execution_time: str
    run_count: int
    volume_serial: str
    volume_path: str
    dependencies: List[str]


@dataclass
class PrefetchAnalysisResult:
    source_path: str
    total_files: int
    suspicious_executions: List[Dict[str, Any]]
    anti_forensic_deletions: List[Dict[str, Any]]
    timeline_gaps: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)
    # Nº de .pf presentes que no se pudieron parsear (firma inválida/corrupto).
    unparsed_files: int = 0

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.anti_forensic_deletions:
            z = Fraction(32, 10)
        elif len(self.suspicious_executions) >= 3:
            z = Fraction(25, 10)
        elif self.suspicious_executions:
            z = Fraction(18, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "source_path": self.source_path,
                "total_files": self.total_files,
                "suspicious_count": len(self.suspicious_executions),
                "suspicious_executables": [e["filename"] for e in self.suspicious_executions],
                "anti_forensic_count": len(self.anti_forensic_deletions),
                "artifact_type": "prefetch",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                # Detección real por nombre de ejecutable (ambos formatos
                # SCCA/MAM). unanalyzed=True solo si HABÍA .pf pero ninguno se
                # pudo parsear — no presentar "0 hallazgos" como "limpio".
                "unparsed_files": self.unparsed_files,
                "unanalyzed": (
                    self.total_files > 0
                    and self.unparsed_files == self.total_files
                ),
                "finding_types": sorted(list(set(
                    s.get("type", "UNKNOWN") for s in self.suspicious_executions
                ) | set(
                    a.get("type", "UNKNOWN") for a in self.anti_forensic_deletions
                ))),
            }
        )


class PrefetchAnalyzer:
    """Analiza archivos .pf de Windows Prefetch."""

    def __init__(self):
        self._suspicious_names = {n.lower() for n in ANTI_FORENSIC_PREFETCH_SIGNS}
        # B-132: herramientas de borrado seguro → anti_forensic_deletions → z=3.2
        self._anti_forensic_exec_names = {n.lower() for n in ANTI_FORENSIC_TOOL_EXECUTION_SIGNS}
        # B-132: herramientas especializadas sospechosas → suspicious_executions
        self._suspicious_tool_names = {n.lower() for n in SUSPICIOUS_TOOL_SIGNS}

    def analyze_directory(
        self,
        prefetch_dir: str,
        chain: Optional[ChainOfCustody] = None,
        timestamp_utc: str = "1970-01-01T00:00:00Z",
    ) -> PrefetchAnalysisResult:
        from vigia.sift._math_utils import _parse_iso_timestamp

        p = Path(prefetch_dir).resolve()
        if not p.exists() or not p.is_dir():
            return PrefetchAnalysisResult(
                source_path=str(p), total_files=0,
                suspicious_executions=[], anti_forensic_deletions=[], timeline_gaps=[],
            )

        pf_files = sorted(p.glob("*.pf"))
        suspicious = []
        anti_forensic = []
        unparsed = 0

        for pf in pf_files:
            try:
                record = self._parse_pf(pf)
            except Exception:
                # FIX (auditoría FN, P1-B): antes cada .pf que fallaba el parse
                # se descartaba en silencio. Ahora se cuenta para poder marcar
                # el análisis como parcial en vez de "0 hallazgos = limpio".
                unparsed += 1
                continue
            name_lower = record.filename.lower()
            if name_lower in self._anti_forensic_exec_names:
                # B-132: herramienta de borrado seguro → anti_forensic bucket → z=3.2
                anti_forensic.append({
                    "type": "ANTI_FORENSIC_TOOL_EXECUTION",
                    "filename": record.filename,
                    "run_count": record.run_count,
                    "last_execution": record.last_execution_time,
                    "severity": str(Fraction(90, 100)),
                })
            elif name_lower in self._suspicious_names or name_lower in self._suspicious_tool_names:
                suspicious.append({
                    "type": "SUSPICIOUS_EXECUTION",
                    "filename": record.filename,
                    "run_count": record.run_count,
                    "last_execution": record.last_execution_time,
                    "severity": str(Fraction(85, 100)),
                })

        # Detección de borrado: si hay menos de 10 archivos .pf en un sistema
        # Windows típico (que suele tener 50-150), es sospechoso
        if len(pf_files) < 10 and len(pf_files) > 0:
            anti_forensic.append({
                "type": "PREFETCH_WIPE",
                "file_count": len(pf_files),
                "expected_min": 50,
                "severity": str(Fraction(75, 100)),
                "description": "Cantidad anormalmente baja de archivos prefetch",
            })

        # Calcular composite score
        sev_sum = sum(Fraction(s["severity"]) for s in suspicious)
        af_sum = sum(Fraction(a["severity"]) for a in anti_forensic)
        composite = min(sev_sum + af_sum, Fraction(95, 100))

        if chain:
            chain.acquire(b"PREFETCH_ANALYSIS", "PREFETCH_ANALYZER", timestamp_utc)

        return PrefetchAnalysisResult(
            source_path=str(p),
            total_files=len(pf_files),
            suspicious_executions=suspicious,
            anti_forensic_deletions=anti_forensic,
            timeline_gaps=[],
            composite_score=composite,
            unparsed_files=unparsed,
        )

    @staticmethod
    def _executable_name(stem: str) -> str:
        """
        Nombre del ejecutable desde el stem del .pf.

        Convención de Windows Prefetch: `EJECUTABLE.EXE-HHHHHHHH.pf`, donde
        HHHHHHHH es un hash de 8 hex. El nombre real es todo lo anterior al
        último `-` (si el sufijo son exactamente 8 hex). El bug original hacía
        stem.replace("-","") → "MIMIKATZ.EXE1234ABCD", que jamás matcheaba
        "mimikatz.exe" en la blacklist.
        """
        base, sep, suffix = stem.rpartition("-")
        if sep and len(suffix) == 8 and all(c in "0123456789ABCDEFabcdef" for c in suffix):
            return base
        return stem

    def _parse_pf(self, path: Path) -> PrefetchRecord:
        """
        Parseo de Prefetch. Acepta AMBOS formatos:
          - Clásico SCCA (XP..Win8, versiones 17/23/26/30): firma "SCCA" en
            el offset 4.
          - Comprimido MAM (Win10+): firma "MAM\\x03"/"MAM\\x04" en el offset 0.

        FIX (auditoría FN, P1-B): antes solo se aceptaba MAM y además se leía
        la firma en el offset equivocado — todo .pf clásico se descartaba en
        silencio (falso negativo de ejecución de malware).
        """
        data = path.read_bytes()
        if len(data) < 8:
            raise ValueError("Archivo prefetch demasiado pequeño")

        head = data[0:4]
        sig_at_4 = data[4:8]
        is_mam = head in (b"MAM\x04", b"MAM\x03")
        is_scca = sig_at_4 == b"SCCA"
        if not (is_mam or is_scca):
            raise ValueError("Firma de prefetch inválida (ni SCCA ni MAM)")

        # El nombre del ejecutable se deriva del nombre del .pf (válido para
        # ambos formatos; no requiere descomprimir el contenedor MAM).
        filename = self._executable_name(path.stem)

        file_hash = hashlib.sha256(data).hexdigest()[:16]

        # B-208: real timing/run_count when pyscca can parse this file
        # (requires MAM decompression it already implements); placeholders
        # otherwise — same honest-degradation contract as before, now
        # narrowed to only the two fields pyscca actually recovers.
        enriched = _enrich_via_pyscca(path)
        last_execution_time = enriched[0] if enriched else "unknown"
        run_count = enriched[1] if enriched else 1

        return PrefetchRecord(
            filename=filename,
            hash=file_hash,
            last_execution_time=last_execution_time,
            run_count=run_count,
            volume_serial="unknown",
            volume_path="unknown",
            dependencies=[],
        )
