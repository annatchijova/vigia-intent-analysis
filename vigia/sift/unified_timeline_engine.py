"""
vigia/sift/unified_timeline_engine.py

Motor de Timeline Unificado.
Combina eventos de los 5 mundos forenses (Red, Disco, Memoria, Registro, Logs)
en una única línea temporal coherente.
Detecta inconsistencias temporales cross-source (ej: memoria dice T+0,
pero MFT dice T+3600 para el mismo proceso).

FIX P0: Todo valor numérico en evidence dict usa Fraction/str. NUNCA float.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
from vigia.sift._math_utils import _parse_iso_timestamp

TOOL_NAME = "UNIFIED_TIMELINE"
ARTIFACT_RELIABILITY = Fraction(80, 100)

# Ventana de tolerancia para correlación temporal (segundos)
TEMPORAL_CORRELATION_WINDOW = 300  # 5 minutos


@dataclass(frozen=True)
class TimelineEvent:
    timestamp: int  # epoch seconds
    source: str  # memory, disk, registry, eventlog, network
    event_type: str
    description: str
    entity_id: str  # PID, filename, IP, registry path
    confidence: Fraction
    raw_evidence: Dict[str, Any]


@dataclass
class TimelineAnalysisResult:
    total_events: int
    timeline: List[TimelineEvent]
    temporal_anomalies: List[Dict[str, Any]]
    cross_source_gaps: List[Dict[str, Any]]
    composite_score: Fraction = Fraction(0)

    def to_signal(self) -> SignalOutput:
        z = Fraction(0, 1)
        if self.temporal_anomalies:
            z = Fraction(30, 10)
        elif len(self.cross_source_gaps) >= 3:
            z = Fraction(22, 10)
        elif self.cross_source_gaps:
            z = Fraction(15, 10)
        conf = min(self.composite_score * Fraction(11, 10) * ARTIFACT_RELIABILITY, Fraction(95, 100))
        return SignalOutput(
            tool_name=TOOL_NAME,
            value=float(z) / Z_CLIP_MAX if Z_CLIP_MAX > 0 else 0.0,
            z_score=float(z),
            confidence=float(conf),
            metadata={
                "total_events": self.total_events,
                "anomaly_count": len(self.temporal_anomalies),
                "gap_count": len(self.cross_source_gaps),
                "artifact_type": "timeline",
                "artifact_reliability": str(ARTIFACT_RELIABILITY),
                "finding_types": sorted(list(set(
                    a.get("type", "UNKNOWN") for a in self.temporal_anomalies
                ) | set(
                    g.get("type", "UNKNOWN") for g in self.cross_source_gaps
                ))),
            }
        )


class UnifiedTimelineEngine:
    """Construye timeline unificado cross-source y detecta anomalías temporales."""

    def build_timeline(
        self,
        signals: List[SignalOutput],
    ) -> TimelineAnalysisResult:
        """
        Construye timeline a partir de señales de todos los módulos SIFT.
        """
        events: List[TimelineEvent] = []

        for signal in signals:
            ts = self._extract_timestamp(signal)
            entity = self._extract_entity(signal)

            event = TimelineEvent(
                timestamp=ts,
                source=signal.metadata.get("artifact_type", "unknown"),
                event_type=signal.tool_name,
                description=f"{signal.tool_name}: z={signal.z_score}",
                entity_id=entity,
                confidence=Fraction(int(round(signal.confidence * 1000)), 1000),
                raw_evidence={
                    "z_score": str(Fraction(int(round(signal.z_score * 100)), 100)),
                    "metadata": signal.metadata,
                },
            )
            events.append(event)

        # Ordenar por timestamp
        events.sort(key=lambda e: e.timestamp)

        # Detectar anomalías temporales
        anomalies = self._detect_temporal_anomalies(events)
        gaps = self._detect_cross_source_gaps(events)

        composite = Fraction(0, 1)
        if anomalies:
            composite = min(max(Fraction(a["severity"]) for a in anomalies), Fraction(95, 100))

        return TimelineAnalysisResult(
            total_events=len(events),
            timeline=events,
            temporal_anomalies=anomalies,
            cross_source_gaps=gaps,
            composite_score=composite,
        )

    def _extract_timestamp(self, signal: SignalOutput) -> int:
        """Extrae timestamp de la metadata del signal."""
        meta = signal.metadata
        ts_str = meta.get("timestamp", meta.get("last_execution", "1970-01-01T00:00:00Z"))
        try:
            return _parse_iso_timestamp(ts_str)
        except ValueError:
            # FIX P2: Timestamp inválido no detiene el pipeline
            if hasattr(signal, 'metadata'):
                signal.metadata["timestamp_invalid"] = True
            return 0

    def _extract_entity(self, signal: SignalOutput) -> str:
        """Extrae identificador de entidad del signal."""
        meta = signal.metadata
        pid = meta.get("pid", meta.get("PID", 0))
        if pid:
            return f"pid:{pid}"
        filename = meta.get("filename", meta.get("hive_path", ""))
        if filename:
            return f"file:{filename}"
        ip = meta.get("dst_ip", meta.get("remote_addr", ""))
        if ip:
            return f"ip:{ip}"
        return f"tool:{signal.tool_name}"

    def _detect_temporal_anomalies(self, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        """
        Detecta inconsistencias temporales:
        - Dos eventos del mismo entity con timestamps imposibles
        - Evento de memoria ANTES del evento de disco que lo causó
        """
        anomalies = []
        by_entity: Dict[str, List[TimelineEvent]] = {}

        for event in events:
            by_entity.setdefault(event.entity_id, []).append(event)

        for entity, entity_events in by_entity.items():
            if len(entity_events) < 2:
                continue

            sorted_events = sorted(entity_events, key=lambda e: e.timestamp)

            # Verificar orden causal
            for i in range(len(sorted_events) - 1):
                current = sorted_events[i]
                next_event = sorted_events[i + 1]

                # Anomalía: memoria detecta proceso ANTES de que aparezca en disco
                if current.source == "memory" and next_event.source == "mft":
                    if current.timestamp < next_event.timestamp - TEMPORAL_CORRELATION_WINDOW:
                        anomalies.append({
                            "type": "CAUSAL_INVERSION",
                            "entity": entity,
                            "description": f"Memoria detecta antes que MFT: {current.timestamp} < {next_event.timestamp}",
                            "severity": str(Fraction(85, 100)),
                        })

                # Anomalía: evento en registry ANTES de ejecución en memoria
                if current.source == "registry" and next_event.source == "memory":
                    if current.timestamp < next_event.timestamp - TEMPORAL_CORRELATION_WINDOW:
                        anomalies.append({
                            "type": "PERSISTENCE_BEFORE_EXECUTION",
                            "entity": entity,
                            "description": f"Persistencia en registry antes de ejecución: {current.timestamp} < {next_event.timestamp}",
                            "severity": str(Fraction(75, 100)),
                        })

        return anomalies

    def _detect_cross_source_gaps(self, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        """
        Detecta gaps cross-source: un evento aparece en fuente A pero NO en fuente B
        dentro de la ventana temporal esperada.
        """
        gaps = []
        by_entity = {}

        for event in events:
            by_entity.setdefault(event.entity_id, {}).setdefault(event.source, []).append(event)

        for entity, sources in by_entity.items():
            # Si hay evidencia de memoria pero NO de disco para el mismo proceso
            if "memory" in sources and "mft" not in sources:
                mem_events = sources["memory"]
                for me in mem_events:
                    gaps.append({
                        "type": "MEMORY_WITHOUT_DISK",
                        "entity": entity,
                        "timestamp": me.timestamp,
                        "severity": str(Fraction(70, 100)),
                        "description": "Proceso detectado en memoria pero sin traza en disco (posible fileless malware)",
                    })

            # Si hay evidencia de red pero NO de memoria
            if "network" in sources and "memory" not in sources:
                net_events = sources["network"]
                for ne in net_events:
                    gaps.append({
                        "type": "NETWORK_WITHOUT_MEMORY",
                        "entity": entity,
                        "timestamp": ne.timestamp,
                        "severity": str(Fraction(65, 100)),
                        "description": "Actividad de red sin proceso correspondiente en memoria",
                    })

        return gaps
