"""
vigia/sift/event_log_correlator.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. ReDoS: Todos los regex con (.+?) reemplazados por versiones seguras
   con límites de longitud y sin backtracking catastrófico.
2. XML ENTITY EXPANSION: ET.parse con forbid_entities implícito.
3. INPUT SIZE: Limitar logs a 50MB para evitar memory exhaustion.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import subprocess
try:
    from defusedxml import ElementTree as ET
except ImportError as _defused_err:
    raise ImportError(
        "FIX P2: defusedxml es obligatorio para protección contra XXE/Billion Laughs. "
        "Instalar: pip install defusedxml>=0.7.1"
    ) from _defused_err
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.core.chain_of_custody import ChainOfCustody
from vigia.sift._math_utils import _parse_iso_timestamp, noisy_or_correlated

logger = logging.getLogger(__name__)

TOOL_NAME = "EVENT_LOG"
MAX_LOG_SIZE_BYTES = 50 * 1024 * 1024  # 50MB límite

_EVENT_CATALOG: Dict[int, Tuple[str, Fraction, str, str]] = {
    4624: ("Logon exitoso", Fraction(10, 100), "Initial Access", "Security"),
    4625: ("Logon fallido", Fraction(40, 100), "Credential Access", "Security"),
    4648: ("RunAs explícito", Fraction(60, 100), "Lateral Movement", "Security"),
    4672: ("Admin logon", Fraction(55, 100), "Privilege Escalation", "Security"),
    4768: ("Kerberos TGT", Fraction(20, 100), "Credential Access", "Security"),
    4769: ("Kerberos ST", Fraction(20, 100), "Lateral Movement", "Security"),
    4771: ("Pre-auth falló", Fraction(65, 100), "Credential Access", "Security"),
    4688: ("Proceso creado", Fraction(15, 100), "Execution", "Security"),
    4698: ("Scheduled task creada", Fraction(75, 100), "Persistence", "Security"),
    4702: ("Scheduled task modificada", Fraction(70, 100), "Persistence", "Security"),
    1102: ("Audit log borrado", Fraction(99, 100), "Defense Evasion", "Security"),
    4719: ("Política auditoría cambiada", Fraction(90, 100), "Defense Evasion", "Security"),
    104: ("System log borrado", Fraction(99, 100), "Defense Evasion", "System"),
    7045: ("Nuevo servicio", Fraction(75, 100), "Persistence", "System"),
    4103: ("PS module logging", Fraction(30, 100), "Execution", "PowerShell"),
    4104: ("PS script block", Fraction(35, 100), "Execution", "PowerShell"),
    1: ("Sysmon ProcessCreate", Fraction(25, 100), "Execution", "Sysmon"),
    8: ("Sysmon CreateRemoteThread", Fraction(90, 100), "Defense Evasion", "Sysmon"),
    22: ("Sysmon DNS", Fraction(15, 100), "Command and Control", "Sysmon"),
    25: ("Sysmon ProcessTampering", Fraction(95, 100), "Defense Evasion", "Sysmon"),
}

_ATTACK_CHAINS = [
    ("PASS_THE_HASH", (4624, 4648, 4672), [60, 120, 60], Fraction(88, 100), "T1550.002"),
    ("LOG_WIPE_AFTER_ATTACK", (4624, 1102), [3600, 1800], Fraction(97, 100), "T1070.001"),
    ("BRUTE_FORCE_SUCCESS", (4625, 4625, 4625, 4624), [300, 300, 300], Fraction(85, 100), "T1110"),
    ("NEW_SERVICE_LOG_CLEAR", (7045, 1102), [600, 1200], Fraction(95, 100), "T1543.003"),
    ("GOLDEN_TICKET", (4768, 4769, 4769, 4769), [60, 60, 60], Fraction(92, 100), "T1558.001"),
    ("REMOTE_THREAD_INJECTION", (8,), [1], Fraction(93, 100), "T1055"),
]

_HIGH_SEVERITY_EIDS = frozenset({1102, 104, 4698, 4702, 4720, 7045, 4625, 4648, 4672, 8})


@dataclass(frozen=True)
class EventRecord:
    event_id: int
    timestamp: int
    channel: str
    computer: str
    user: str
    process_id: int
    thread_id: int
    message: str


@dataclass(frozen=True)
class EventLogFinding:
    finding_type: str
    severity: Fraction
    event_ids: Tuple[int, ...]
    timestamps: Tuple[int, ...]
    description: str
    evidence: str
    mitre_technique: str
    rule_ref: str


@dataclass
class EventLogAnalysisResult:
    source_files: List[str]
    total_events: int
    time_range: Tuple[int, int]
    findings: List[EventLogFinding] = field(default_factory=list)
    chain_detections: List[Dict] = field(default_factory=list)
    log_gaps: List[Dict] = field(default_factory=list)
    anomalous_hours: List[Dict] = field(default_factory=list)
    composite_score: Fraction = Fraction(0)
    analysis_notes: List[str] = field(default_factory=list)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if any("LOG_WIPE" in c.get("chain_name", "") for c in self.chain_detections):
            z = Fraction(38, 10)
        elif len(self.chain_detections) >= 2:
            z = Fraction(32, 10)
        elif self.findings:
            z = Fraction(24, 10)
        conf = min(self.composite_score * Fraction(11, 10), Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME, value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z), confidence=float(conf),
            metadata={
                "total_events": self.total_events, "findings": len(self.findings),
                "artifact_type": "event_log",
                "finding_types": sorted(list(set(f.finding_type for f in self.findings) | set(c.get("chain_name", "") for c in self.chain_detections))),
                "chains": len(self.chain_detections), "gaps": len(self.log_gaps),
                "composite_score": str(self.composite_score),
            }
        )


class WindowsEventLogParser:
    def __init__(self):
        self._available = False
        try:
            import Evtx.Evtx as evtx
            self._evtx = evtx
            self._available = True
        except ImportError:
            pass

    def parse_evtx(self, evtx_path: str) -> List[EventRecord]:
        if not self._available:
            return []
        records = []
        try:
            # FIX: Limitar tamaño de archivo
            p = Path(evtx_path)
            if p.exists() and p.stat().st_size > MAX_LOG_SIZE_BYTES:
                logger.warning("Archivo EVTX excede límite de 50MB: %s", evtx_path)
                return []
            with self._evtx.Evtx(evtx_path) as log:
                for record in log.records():
                    try:
                        r = self._parse_xml(record.xml())
                        if r:
                            records.append(r)
                    except Exception:
                        continue
        except Exception as e:
            logger.error("Error parseando %s: %s", evtx_path, e)
        return records

    def parse_xml(self, xml_path: str) -> List[EventRecord]:
        records = []
        try:
            p = Path(xml_path)
            if p.exists() and p.stat().st_size > MAX_LOG_SIZE_BYTES:
                logger.warning("Archivo XML excede límite de 50MB: %s", xml_path)
                return []
            tree = ET.parse(xml_path)  # FIX P2: defusedxml garantiza protección XXE
            for elem in tree.findall(".//{http://schemas.microsoft.com/win/2004/08/events/event}Event"):
                r = self._parse_element(elem)
                if r:
                    records.append(r)
        except Exception as e:
            logger.error("Error XML %s: %s", xml_path, e)
        return records

    def _parse_xml(self, xml_str: str) -> Optional[EventRecord]:
        try:
            # FIX: Limitar tamaño de string XML
            if len(xml_str) > 1024 * 1024:  # 1MB por registro
                return None
            root = ET.fromstring(xml_str)  # FIX P2: defusedxml garantiza protección XXE
            return self._parse_element(root)
        except ET.ParseError:
            return None

    def _parse_element(self, elem: ET.Element) -> Optional[EventRecord]:
        ns = {"w": "http://schemas.microsoft.com/win/2004/08/events/event"}
        system = elem.find("w:System", ns)
        if system is None:
            return None
        eid_elem = system.find("w:EventID", ns)
        if eid_elem is None or eid_elem.text is None:
            return None
        try:
            eid = int(eid_elem.text)
        except ValueError:
            return None
        tc = system.find("w:TimeCreated", ns)
        ts_str = tc.get("SystemTime", "") if tc is not None else ""
        ts = _parse_iso_timestamp(ts_str)
        ch = system.find("w:Channel", ns)
        channel = ch.text if ch is not None else ""
        comp = system.find("w:Computer", ns)
        computer = comp.text if comp is not None else ""
        exec_e = system.find("w:Execution", ns)
        pid = int(exec_e.get("ProcessID", "0")) if exec_e is not None else 0
        tid = int(exec_e.get("ThreadID", "0")) if exec_e is not None else 0
        sec = system.find("w:Security", ns)
        user = sec.get("UserID", "") if sec is not None else ""
        ed = elem.find("w:EventData", ns)
        msg_parts = []
        if ed is not None:
            for d in ed:
                msg_parts.append(f"{d.get('Name', '')}={d.text or ''}")
        msg = "; ".join(msg_parts)[:1000]
        return EventRecord(event_id=eid, timestamp=ts, channel=channel, computer=computer, user=user, process_id=pid, thread_id=tid, message=msg)


class AttackChainDetector:
    _MAX_GAP_EVENTS = 2

    def detect(self, events: List[EventRecord]) -> List[Dict]:
        detections = []
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        by_id = defaultdict(list)
        for e in sorted_events:
            by_id[e.event_id].append(e)
        for name, seq, windows, severity, mitre in _ATTACK_CHAINS:
            matches = self._find_chain(sorted_events, by_id, name, seq, windows, severity, mitre)
            detections.extend(matches)
        return detections

    def _find_chain(self, events, by_id, name, seq, windows, severity, mitre):
        matches = []
        if not seq:
            return matches
        first_id = seq[0]
        for anchor in by_id.get(first_id, []):
            chain_events = [anchor]
            valid = True
            for idx, next_id in enumerate(seq[1:]):
                window = windows[idx + 1] if idx + 1 < len(windows) else windows[-1]
                window_end = anchor.timestamp + window
                candidates = [e for e in by_id.get(next_id, [])
                            if chain_events[-1].timestamp <= e.timestamp <= window_end]
                if not candidates:
                    valid = False
                    break
                chain_events.append(candidates[0])
            if valid and len(chain_events) == len(seq):
                matches.append({
                    "chain_name": name, "severity": str(severity), "mitre": mitre,
                    "event_ids": [e.event_id for e in chain_events],
                    "timestamps": [e.timestamp for e in chain_events],
                    "computers": sorted(set(e.computer for e in chain_events)),
                    "rule_ref": f"ELC-CHAIN:{name}",
                })
        return matches


class LogGapDetector:
    def detect(self, events: List[EventRecord], channel: str) -> List[Dict]:
        if len(events) < 2:
            return []
        gaps = []
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        for i in range(1, len(sorted_events)):
            gap = sorted_events[i].timestamp - sorted_events[i - 1].timestamp
            if gap >= 1800:
                sev = Fraction(40, 100) if gap < 7200 else (Fraction(60, 100) if gap < 86400 else Fraction(85, 100))
                gaps.append({
                    "channel": channel, "gap_seconds": gap, "severity": str(sev),
                    "description": f"Gap de {gap // 60} minutos en {channel}",
                    "rule_ref": "ELC-GAP-R1",
                })
        return gaps


class AnomalousHourDetector:
    def detect(self, events: List[EventRecord]) -> List[Dict]:
        anomalies = []
        for event in events:
            if event.event_id not in _HIGH_SEVERITY_EIDS:
                continue
            sid = event.timestamp % 86400
            hour = sid // 3600
            dow = ((event.timestamp // 86400) + 4) % 7
            weekend = dow >= 5
            off_hours = hour < 7 or hour >= 19
            if off_hours or weekend:
                spec = _EVENT_CATALOG.get(event.event_id)
                base = spec[1] if spec else Fraction(50, 100)
                amplified = min(base * Fraction(13, 10), Fraction(99, 100))
                anomalies.append({
                    "event_id": event.event_id, "hour_utc": hour,
                    "is_weekend": weekend, "severity": str(amplified),
                    "description": f"Event {event.event_id} fuera de horario ({hour:02d}h)",
                    "rule_ref": "ELC-HOUR-R1",
                })
        return anomalies


class EventLogCorrelator:
    def __init__(self):
        self._parser = WindowsEventLogParser()

    def analyze(self, log_paths: List[str], chain: Optional[ChainOfCustody] = None, timestamp_utc: str = "1970-01-01T00:00:00Z") -> EventLogAnalysisResult:
        all_events = []
        source_files = []
        # FIX (auditoría FN, P1-D/E): rastrear archivos presentes que NO se
        # pudieron parsear, para distinguir "analizado, sin eventos" de "no se
        # pudo analizar". Antes un .log de texto plano (sufijo no reconocido) o
        # un .evtx sin la librería Evtx producían 0 eventos en silencio →
        # veredicto benigno espurio. Ahora se reportan como UNANALYZED.
        unparsed_files: List[str] = []
        for lp in log_paths:
            path = Path(lp)
            if not path.exists():
                continue
            # FIX: Validación de tamaño
            if path.stat().st_size > MAX_LOG_SIZE_BYTES:
                logger.warning("Log omitido por tamaño >50MB: %s", lp)
                unparsed_files.append(f"{lp} [>50MB, omitido]")
                continue
            source_files.append(lp)
            if chain:
                chain.acquire(path.read_bytes()[:4096], "EVENTLOG_ANALYST", timestamp_utc)
            suffix = path.suffix.lower()
            before = len(all_events)
            if suffix == ".evtx":
                if not self._parser._available:
                    # Librería Evtx ausente: el .evtx binario NO se analiza.
                    unparsed_files.append(f"{lp} [librería 'Evtx' ausente]")
                    continue
                all_events.extend(self._parser.parse_evtx(lp))
            elif suffix in {".xml", ".txt", ".log", ".evt"}:
                # .log/.txt: se intenta parseo XML (logs exportados suelen ser
                # XML). parse_xml captura errores y devuelve [] si no es XML.
                all_events.extend(self._parser.parse_xml(lp))
            else:
                unparsed_files.append(f"{lp} [formato no soportado: {suffix or 'sin extensión'}]")
                continue
            if len(all_events) == before:
                # El archivo se reconoció pero no produjo eventos parseables.
                unparsed_files.append(f"{lp} [0 eventos parseados]")

        if not all_events:
            notes = ["No eventos parseados."]
            if unparsed_files:
                # Marcador UNANALYZED: aguas abajo esto debe mapear a ABSTAIN,
                # no a benigno. La ausencia de eventos aquí es un fallo de
                # análisis, no evidencia de que no hubo actividad.
                notes.append("UNANALYZED_ARTIFACT: " + "; ".join(unparsed_files[:10]))
            return EventLogAnalysisResult(
                source_files=source_files, total_events=0, time_range=(0, 0),
                analysis_notes=notes,
            )

        timestamps = [e.timestamp for e in all_events]
        time_range = (min(timestamps), max(timestamps))

        channels = {e.channel for e in all_events}
        all_gaps = []
        for ch in channels:
            all_gaps.extend(LogGapDetector().detect([e for e in all_events if e.channel == ch], ch))

        chains = AttackChainDetector().detect(all_events)
        hours = AnomalousHourDetector().detect(all_events)
        direct = self._direct_findings(all_events)

        severities = [f.severity for f in direct] + [Fraction(c["severity"]) for c in chains]
        corr_groups = {}
        for i, f1 in enumerate(direct):
            for j, f2 in enumerate(direct):
                if i < j and f1.event_ids == f2.event_ids and abs(f1.timestamps[0] - f2.timestamps[0]) < 300:
                    corr_groups.setdefault(i, set()).add(j)
                    corr_groups.setdefault(j, set()).add(i)
        for i, c1 in enumerate(chains):
            for j, c2 in enumerate(chains):
                if i < j and c1.get("computers") == c2.get("computers"):
                    idx1 = len(direct) + i
                    idx2 = len(direct) + j
                    corr_groups.setdefault(idx1, set()).add(idx2)
                    corr_groups.setdefault(idx2, set()).add(idx1)

        composite = noisy_or_correlated(severities, corr_groups, Fraction(15, 100))
        notes = self._generate_notes(all_events, chains, all_gaps, direct)

        return EventLogAnalysisResult(
            source_files=source_files, total_events=len(all_events), time_range=time_range,
            findings=direct, chain_detections=chains, log_gaps=all_gaps,
            anomalous_hours=hours, composite_score=composite, analysis_notes=notes,
        )

    def _direct_findings(self, events: List[EventRecord]) -> List[EventLogFinding]:
        findings = []
        for event in events:
            spec = _EVENT_CATALOG.get(event.event_id)
            if spec and spec[1] >= Fraction(70, 100):
                findings.append(EventLogFinding(
                    finding_type=f"HIGH_SEVERITY_{event.event_id}", severity=spec[1],
                    event_ids=(event.event_id,), timestamps=(event.timestamp,),
                    description=f"Event {event.event_id}: {spec[0]}", evidence=event.message[:500],
                    mitre_technique="", rule_ref=f"ELC-DIRECT:{event.event_id}",
                ))
        return findings

    def _generate_notes(self, events, chains, gaps, findings):
        notes = []
        if any(e.event_id in {1102, 104} for e in events):
            notes.append("CRÍTICO: Log borrado (1102/104) detectado.")
        if chains:
            notes.append(f"CADENAS: {len(chains)} secuencia(s): {[c['chain_name'] for c in chains]}")
        if gaps:
            notes.append(f"GAPS: {len(gaps)} gap(s) de actividad no registrada.")
        return notes
