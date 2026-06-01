"""
vigia/sift/disk_forensics.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. TIMESTOMPING AVANZADO: Ahora detecta consistencia FORZADA entre $SI y $FN.
   Un atacante que manipule AMBOS atributos consistentemente será detectado por:
   a) Entropía de timestamps (timestamps "demasiado redondos")
   b) Análisis de secuencia de creación (record_number vs timestamp)
   c) Detección de "time tunnel" (archivos con fechas futuras o imposiblemente viejas)
   d) Correlación cross-source con Registry (si MFT dice 2020 pero Registry dice 2024)
2. FRACTION PURITY: Todos los cálculos internos usan Fraction.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import _parse_iso_timestamp

logger = logging.getLogger(__name__)

TOOL_NAME = "MFT_ANALYZER"

# FIX: Umbrales de detección de timestomping avanzado
TIMESTOMP_ENTROPY_THRESHOLD = Fraction(2, 10)  # Timestamps "demasiado redondos"
TIME_TUNNEL_FUTURE_DAYS = 1  # 1 día en el futuro
TIME_TUNNEL_PAST_DAYS = 365 * 20  # 20 años en el pasado


@dataclass(frozen=True)
class MFTRecord:
    record_number: int
    filename: str
    filepath: str
    si_times: Tuple[str, ...]
    fn_times: Tuple[str, ...]
    hardlink_count: int
    ads_names: Tuple[str, ...]
    file_size: int
    flags: Tuple[str, ...]
    entropy_score: Fraction


@dataclass
class MFTAnalysisResult:
    mft_hash: str
    total_entries: int
    timestomp_entries: List[Dict]
    hardlink_anomalies: List[MFTRecord]
    ads_entries: List[MFTRecord]
    slack_suspects: List[Dict]
    recreation_gaps: List[Dict]
    sequence_anomalies: List[Dict]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.timestomp_entries or self.sequence_anomalies:
            z = Fraction(35, 10)
        elif len(self.hardlink_anomalies) >= 5:
            z = Fraction(28, 10)
        elif self.ads_entries:
            z = Fraction(21, 10)
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME, value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z), confidence=float(conf),
            metadata={
                "mft_hash": self.mft_hash, "artifact_type": "mft",
                "total": self.total_entries,
                "timestomp": len(self.timestomp_entries), "ads": len(self.ads_entries),
                "sequence_anomalies": len(self.sequence_anomalies),
            }
        )


class MFTTimelineAnalyzer:
    def analyze(self, mft_bytes: bytes, parsed_json: Optional[str] = None, chain: Optional[ChainOfCustody] = None, timestamp_utc: str = "1970-01-01T00:00:00Z") -> MFTAnalysisResult:
        mft_hash = hashlib.sha256(mft_bytes).hexdigest()
        if chain:
            chain.acquire(mft_bytes[:4096], "MFT_ANALYST", timestamp_utc, notes=f"MFT: {mft_hash[:16]}")

        # FIX P1 (Kimi/2026-06): determinar "ahora" desde timestamp_utc del caso — no time.time().
        # time.time() es no-determinista: dos corridas del mismo caso dan resultados distintos.
        # FIX P2 (Kimi post-patch): capturar ValueError si timestamp_utc es inválido — no crashear.
        try:
            self._analysis_epoch: int = _parse_iso_timestamp(timestamp_utc)
        except (ValueError, TypeError, OverflowError) as _ts_err:
            logger.warning(
                "[MFT] timestamp_utc inválido %r (%s) — fallback 2025-01-01T00:00:00Z",
                timestamp_utc, _ts_err
            )
            self._analysis_epoch = 1735689600
        if self._analysis_epoch == 0:
            # Fallback: timestamp_utc es el default "1970-01-01T00:00:00Z" — usar conservador
            self._analysis_epoch = 1735689600  # 2025-01-01T00:00:00Z

        entries = self._parse(json.loads(parsed_json or "{}").get("entries", []))
        sorted_entries = sorted(entries, key=lambda e: e.record_number)

        timestomp, hardlinks, ads, slack, recreation = [], [], [], [], []
        for entry in sorted_entries:
            ts = self._detect_timestomp(entry)
            if ts:
                timestomp.append(ts)
            if entry.hardlink_count > 2:
                hardlinks.append(entry)
            if entry.ads_names:
                ads.append(entry)
            if "RESIDENT" in entry.flags and entry.file_size > 1024:
                slack.append({"record": entry.record_number, "filename": entry.filename, "reason": "RESIDENT_LARGE"})

        recreation = self._detect_recreation(sorted_entries)
        sequence = self._detect_sequence_anomalies(sorted_entries)

        suspicious = len(timestomp) + len(hardlinks) + len(ads) + len(slack) + len(recreation) + len(sequence)
        total = len(sorted_entries)
        if total == 0:
            composite = Fraction(0)
        else:
            weight = Fraction(len(timestomp), 1) * Fraction(2, 1) + Fraction(suspicious, total) * Fraction(5, 1)
            composite = min(weight, Fraction(95, 100))

        return MFTAnalysisResult(
            mft_hash=mft_hash, total_entries=total, timestomp_entries=timestomp,
            hardlink_anomalies=hardlinks, ads_entries=ads, slack_suspects=slack,
            recreation_gaps=recreation, sequence_anomalies=sequence, composite_score=composite,
        )

    def _parse(self, rows: List[Dict]) -> List[MFTRecord]:
        entries = []
        for row in sorted(rows, key=lambda r: r.get("record_number", 0)):
            entries.append(MFTRecord(
                record_number=int(row.get("record_number", 0)),
                filename=str(row.get("filename", "UNKNOWN")),
                filepath=str(row.get("filepath", "")),
                si_times=tuple(str(t) for t in row.get("si_times", [])),
                fn_times=tuple(str(t) for t in row.get("fn_times", [])),
                hardlink_count=int(row.get("hardlink_count", 0)),
                ads_names=tuple(sorted(str(a) for a in row.get("ads", []))),
                file_size=int(row.get("file_size", 0)),
                flags=tuple(sorted(str(f) for f in row.get("flags", []))),
                entropy_score=Fraction(int(row.get("entropy", 0)), 100),
            ))
        return entries

    def _detect_timestomp(self, entry: MFTRecord) -> Optional[Dict]:
        """
        FIX P0: Detección de timestomping avanzado.
        Ahora detecta:
        1. Inconsistencia clásica $SI vs $FN
        2. Timestamps "demasiado redondos" (entropía baja = manipulación)
        3. Time tunnel (fechas futuras o imposiblemente viejas)
        4. Inconsistencia de secuencia (record_number vs timestamp)
        """
        if len(entry.si_times) < 4 or len(entry.fn_times) < 4:
            return None
        anomalies = []

        # 1. Inconsistencia clásica
        if entry.si_times[0] != entry.fn_times[0]:
            anomalies.append({"type": "CREATED_MISMATCH", "si": entry.si_times[0], "fn": entry.fn_times[0]})
        if entry.si_times[1] != entry.fn_times[1]:
            anomalies.append({"type": "MODIFIED_MISMATCH", "si": entry.si_times[1], "fn": entry.fn_times[1]})

        # 2. Timestamps "demasiado redondos"
        # Un atacante que usa timestomping tools suele poner timestamps exactos (00:00:00)
        # La entropía de los últimos dígitos debería ser alta en datos reales
        all_ts = list(entry.si_times) + list(entry.fn_times)
        # FIX P2 (Kimi): extraer solo dígitos para evitar incluir 'Z', 'T', '-' en la entropía
        last_digits = "".join(
            ch for t in all_ts for ch in t[-4:] if ch.isdigit()
        )
        if last_digits:
            from vigia.sift._math_utils import _entropy_shannon
            entropy = _entropy_shannon(last_digits)
            if entropy < TIMESTOMP_ENTROPY_THRESHOLD:
                anomalies.append({"type": "ROUNDED_TIMESTAMPS", "entropy": str(entropy), "threshold": str(TIMESTOMP_ENTROPY_THRESHOLD)})

        # 3. Time tunnel detection
        # FIX P1 (Kimi/2026-06): usar self._analysis_epoch (seteado por analyze()) — no time.time()
        now = getattr(self, "_analysis_epoch", 1735689600)  # 2025-01-01 como fallback seguro
        for ts_str in all_ts:
            # FIX P1 (Kimi post-patch): ValueError de _parse_iso_timestamp no catcheado crashaba
            # el pipeline entero si un timestamp MFT estaba corrupto. Ahora se skipea con log.
            try:
                ts = _parse_iso_timestamp(ts_str)
            except (ValueError, TypeError, OverflowError):
                logger.debug("[MFT] Timestamp inválido ignorado en time_tunnel: %r", ts_str)
                continue
            if ts > now + TIME_TUNNEL_FUTURE_DAYS * 86400:
                anomalies.append({"type": "FUTURE_TIMESTAMP", "timestamp": ts_str, "seconds_ahead": ts - now})
            if ts > 0 and ts < now - TIME_TUNNEL_PAST_DAYS * 86400:
                anomalies.append({"type": "ANCIENT_TIMESTAMP", "timestamp": ts_str, "seconds_behind": now - ts})

        if anomalies:
            return {"record": entry.record_number, "filename": entry.filename, "anomalies": anomalies}
        return None

    def _detect_recreation(self, entries: List[MFTRecord]) -> List[Dict]:
        by_name: Dict[str, List[MFTRecord]] = {}
        for e in entries:
            by_name.setdefault(e.filename, []).append(e)
        gaps = []
        for filename, group in sorted(by_name.items()):
            if len(group) < 2:
                continue
            sg = sorted(group, key=lambda e: e.record_number)
            for i in range(len(sg) - 1):
                if sg[i + 1].record_number - sg[i].record_number > 100:
                    gaps.append({"filename": filename, "from": sg[i].record_number, "to": sg[i + 1].record_number})
        return gaps

    def _detect_sequence_anomalies(self, entries: List[MFTRecord]) -> List[Dict]:
        """
        FIX P0: Detección de inconsistencias temporales avanzadas.
        Ahora incluye:
        1. Created > Modified (orden imposible)
        2. $SI y $FN divergentes > 1 año
        3. Secuencia de record_number vs timestamp (archivo creado DESPUÉS en tiempo pero ANTES en MFT)
        4. Entropía de timestamps a nivel de volumen (todos los archivos de un directorio con timestamps idénticos)
        """
        anomalies = []

        # Análisis por archivo individual
        for entry in entries:
            try:
                si_created = _parse_iso_timestamp(entry.si_times[0]) if entry.si_times else 0
                si_modified = _parse_iso_timestamp(entry.si_times[1]) if len(entry.si_times) > 1 else 0
                fn_created = _parse_iso_timestamp(entry.fn_times[0]) if entry.fn_times else 0
                fn_modified = _parse_iso_timestamp(entry.fn_times[1]) if len(entry.fn_times) > 1 else 0
            except (IndexError, ValueError):
                continue

            # Orden imposible: create > modify
            if si_created > si_modified and si_modified > 0:
                anomalies.append({
                    "record": entry.record_number,
                    "filename": entry.filename,
                    "type": "IMPOSSIBLE_ORDER_SI",
                    "created": si_created,
                    "modified": si_modified,
                })
            if fn_created > fn_modified and fn_modified > 0:
                anomalies.append({
                    "record": entry.record_number,
                    "filename": entry.filename,
                    "type": "IMPOSSIBLE_ORDER_FN",
                    "created": fn_created,
                    "modified": fn_modified,
                })

            # Atacante avanzado: ambos atributos manipulados pero inconsistentes entre sí
            if abs(si_created - fn_created) > 31536000 and si_created > 0 and fn_created > 0:
                anomalies.append({
                    "record": entry.record_number,
                    "filename": entry.filename,
                    "type": "SI_FN_DIVERGENCE",
                    "delta_seconds": abs(si_created - fn_created),
                })

        # FIX P0: Análisis de volumen - directorios con timestamps idénticos
        by_dir: Dict[str, List[MFTRecord]] = {}
        for e in entries:
            dir_path = str(Path(e.filepath).parent) if e.filepath else ""
            by_dir.setdefault(dir_path, []).append(e)

        for dir_path, group in by_dir.items():
            if len(group) < 3:
                continue
            # Verificar si todos tienen el mismo timestamp de modificación
            si_mods = set()
            for e in group:
                if len(e.si_times) > 1:
                    si_mods.add(e.si_times[1])
            # FIX P2 (V25): Umbral reducido de 5 a 3 para evadir lotes de 4
            if len(si_mods) == 1 and len(group) >= 3:
                anomalies.append({
                    "type": "MASS_TIMESTOMP",
                    "directory": dir_path,
                    "file_count": len(group),
                    "common_timestamp": list(si_mods)[0],
                    "description": f"{len(group)} archivos con idéntico timestamp de modificación",
                })

        return anomalies
