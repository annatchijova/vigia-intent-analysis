# vigia/tools/temporal_drift.py
"""
Temporal Drift Detector - Detección de Cronología Imposible

Principio: Los atacantes falsifican timestamps, pero NO pueden falsificar
TODOS los timestamps en TODOS los lugares consistentemente.

Author: VIGÍA Collective
License: Open Source
"""

from datetime import datetime, timezone, timedelta
from fractions import Fraction
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TemporalEvent:
    """Un evento con timestamp."""
    source: str  # "Email:Date", "PDF:CreationDate", "EXIF:DateTimeOriginal"
    timestamp: datetime
    confidence: Fraction  # ¿Qué tan confiable es este timestamp?
    metadata: Dict = None


@dataclass(frozen=True)
class TemporalAnalysis:
    """Resultado de análisis temporal."""
    events: List[TemporalEvent]
    impossible_sequences: List[Tuple[TemporalEvent, TemporalEvent, str]]
    excessive_drifts: List[Tuple[TemporalEvent, TemporalEvent, str]]
    timezone_violations: List[Tuple[TemporalEvent, TemporalEvent, str]]
    verdict: str
    confidence: Fraction
    reasoning: str
    evidence: Dict


class TemporalDriftDetector:
    """
    Detecta inconsistencias cronológicas que revelan manipulación.
    
    Busca:
    - Timestamps imposibles (modificado antes de creado)
    - Drift excesivo (email enviado 6h antes de ser escrito)
    - Anacronismos léxicos (doc "de 2020" menciona eventos de 2023)
    - Timezone inconsistencies (mismo usuario en 3 zonas en 2h)
    """
    
    # Umbrales de drift aceptable
    MAX_CREATION_TO_SEND = timedelta(hours=72)
    MAX_MODIFY_TO_SEND = timedelta(hours=24)
    MAX_FUTURE_TOLERANCE = timedelta(hours=2)  # Tolerancia para relojes adelantados
    MIN_TIMEZONE_GAP_HOURS = 6  # Zonas horarias a >6h de distancia son sospechosas
    
    def analyze(self, events: List[TemporalEvent]) -> TemporalAnalysis:
        """
        Analiza secuencia de eventos temporales.
        
        Args:
            events: Lista de TemporalEvent a analizar
            
        Returns:
            TemporalAnalysis con veredicto y evidencia
        """
        if not events:
            return self._empty_analysis()
        
        # Normalizar todos los timestamps a UTC
        normalized_events = self._normalize_timezones(events)
        
        # Detectar patrones sospechosos
        impossible = self._detect_impossible_sequences(normalized_events)
        drifts = self._detect_excessive_drift(normalized_events)
        tz_violations = self._detect_timezone_anomalies(events)  # Usa eventos originales
        
        # Evaluación
        verdict, confidence, reasoning, evidence = self._evaluate_temporal_consistency(
            impossible, drifts, tz_violations
        )
        
        return TemporalAnalysis(
            events=normalized_events,
            impossible_sequences=impossible,
            excessive_drifts=drifts,
            timezone_violations=tz_violations,
            verdict=verdict,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _evaluate_temporal_consistency(
        self,
        impossible: List,
        drifts: List,
        tz_violations: List
    ) -> Tuple[str, Fraction, str, Dict]:
        """Evalúa consistencia temporal y genera veredicto."""
        signals = []
        evidence = {}
        
        # SEÑAL 1: Secuencias imposibles (CRÍTICO)
        if impossible:
            weight = Fraction(10, 10)  # Confianza máxima
            signals.append((
                weight,
                f"IMPOSSIBLE_CHRONOLOGY: {len(impossible)} violations (events out of causal order)"
            ))
            evidence['impossible_sequences'] = {
                'severity': 'CRITICAL',
                'count': len(impossible),
                'examples': [
                    {
                        'event1': e1.source,
                        'time1': e1.timestamp.isoformat(),
                        'event2': e2.source,
                        'time2': e2.timestamp.isoformat(),
                        'reason': reason
                    }
                    for e1, e2, reason in impossible[:3]  # Top 3
                ]
            }
        
        # SEÑAL 2: Drifts excesivos
        if len(drifts) > 2:
            weight = Fraction(7, 10)
            signals.append((
                weight,
                f"EXCESSIVE_DRIFT: {len(drifts)} events with suspicious timing gaps"
            ))
            evidence['excessive_drifts'] = {
                'severity': 'HIGH',
                'count': len(drifts),
                'examples': [
                    {
                        'event1': e1.source,
                        'event2': e2.source,
                        'reason': reason
                    }
                    for e1, e2, reason in drifts[:3]
                ]
            }
        elif drifts:
            weight = Fraction(4, 10)
            signals.append((
                weight,
                f"Moderate drift detected: {len(drifts)} events"
            ))
            evidence['moderate_drift'] = {
                'severity': 'MEDIUM',
                'count': len(drifts)
            }
        
        # SEÑAL 3: Violaciones de timezone
        if tz_violations:
            weight = Fraction(6, 10)
            signals.append((
                weight,
                f"TIMEZONE_VIOLATION: {len(tz_violations)} incompatible location/time pairs"
            ))
            evidence['timezone_violations'] = {
                'severity': 'HIGH',
                'count': len(tz_violations),
                'examples': [
                    {
                        'event1': e1.source,
                        'event2': e2.source,
                        'reason': reason
                    }
                    for e1, e2, reason in tz_violations[:3]
                ]
            }
        
        # DECISIÓN
        if not signals:
            return (
                "BENIGN",
                Fraction(9, 10),
                "Temporal consistency verified - all timestamps coherent",
                {'event_count': len(impossible) + len(drifts) + len(tz_violations)}
            )
        
        total_confidence = sum(s[0] for s in signals)
        reasoning_parts = [s[1] for s in signals]
        
        # Saturar confianza
        if total_confidence > Fraction(10, 10):
            total_confidence = Fraction(10, 10)
        
        reasoning = "TEMPORAL_INCONSISTENCY: " + "; ".join(reasoning_parts)
        
        if total_confidence >= Fraction(8, 10):
            verdict = "MALICIOUS"
        elif total_confidence >= Fraction(5, 10):
            verdict = "SUSPICIOUS"
        else:
            verdict = "BENIGN"
        
        evidence['total_signals'] = len(signals)
        evidence['confidence_raw'] = float(total_confidence)
        
        return verdict, total_confidence, reasoning, evidence
    
    def _detect_impossible_sequences(self, events: List[TemporalEvent]) -> List:
        """
        Detecta secuencias cronológicamente imposibles.
        
        Ejemplos:
        - ModDate < CreationDate
        - Email enviado antes de que el attachment existiera
        - Documento modificado en el futuro
        """
        violations = []
        now = datetime.now(timezone.utc)
        
        # Agrupar eventos por tipo
        creation_events = [e for e in events if 'creat' in e.source.lower() or 'original' in e.source.lower()]
        modification_events = [e for e in events if 'mod' in e.source.lower() or 'modified' in e.source.lower()]
        send_events = [e for e in events if 'send' in e.source.lower() or 'date' in e.source.lower()]
        
        # PATRÓN 1: Modificado antes de creado
        for create in creation_events:
            for modify in modification_events:
                # Verificar si son del mismo artefacto
                if self._same_artifact(create.source, modify.source):
                    if modify.timestamp < create.timestamp:
                        delta = create.timestamp - modify.timestamp
                        violations.append((
                            modify, create,
                            f"Modified {self._format_delta(delta)} before created"
                        ))
        
        # PATRÓN 2: Email enviado antes de que attachment existiera
        for send in send_events:
            for create in creation_events:
                if 'attachment' in create.source.lower() or 'pdf' in create.source.lower():
                    if send.timestamp < create.timestamp:
                        delta = create.timestamp - send.timestamp
                        violations.append((
                            send, create,
                            f"Email sent {self._format_delta(delta)} before attachment created"
                        ))
        
        # PATRÓN 3: Timestamps en el futuro
        for event in events:
            if event.timestamp > now + self.MAX_FUTURE_TOLERANCE:
                delta = event.timestamp - now
                violations.append((
                    event, None,
                    f"Timestamp {self._format_delta(delta)} in the future"
                ))
        
        # PATRÓN 4: Modificado después de enviar (menos crítico pero sospechoso)
        for send in send_events:
            for modify in modification_events:
                if self._same_artifact(send.source, modify.source):
                    if modify.timestamp > send.timestamp:
                        delta = modify.timestamp - send.timestamp
                        if delta > timedelta(minutes=5):  # Tolerancia de 5min
                            violations.append((
                                send, modify,
                                f"Attachment modified {self._format_delta(delta)} AFTER email sent"
                            ))
        
        return violations
    
    def _detect_excessive_drift(self, events: List[TemporalEvent]) -> List:
        """Detecta drifts temporales sospechosos."""
        drifts = []
        
        # Buscar pares de eventos relacionados
        send_events = [e for e in events if 'send' in e.source.lower() or 'date' in e.source.lower()]
        attachment_events = [e for e in events if 'pdf' in e.source.lower() or 'attachment' in e.source.lower()]
        
        for send in send_events:
            for attach in attachment_events:
                # Email enviado mucho después de crear attachment
                if 'creat' in attach.source.lower():
                    drift = send.timestamp - attach.timestamp
                    if drift > self.MAX_CREATION_TO_SEND:
                        drifts.append((
                            send, attach,
                            f"Email sent {self._format_delta(drift)} after attachment created (threshold: 72h)"
                        ))
                    elif drift < timedelta(0):
                        # Ya detectado en impossible_sequences
                        pass
                
                # Email enviado mucho después de modificar attachment
                if 'mod' in attach.source.lower():
                    drift = send.timestamp - attach.timestamp
                    if drift > self.MAX_MODIFY_TO_SEND:
                        drifts.append((
                            send, attach,
                            f"Email sent {self._format_delta(drift)} after last modification (suspicious delay)"
                        ))
        
        return drifts
    
    def _detect_timezone_anomalies(self, events: List[TemporalEvent]) -> List:
        """
        Detecta inconsistencias de timezone.
        
        Ejemplo: Email dice UTC-5, pero metadata de attachment dice UTC+8
        (mismo usuario en 13 horas de diferencia)
        """
        violations = []
        
        # Filtrar solo eventos con tzinfo
        tz_events = [e for e in events if e.timestamp.tzinfo is not None]
        
        if len(tz_events) < 2:
            return violations
        
        # Agrupar por fuente aproximada (ej: todos los eventos de "Email")
        grouped = {}
        for event in tz_events:
            source_type = event.source.split(':')[0]
            if source_type not in grouped:
                grouped[source_type] = []
            grouped[source_type].append(event)
        
        # Buscar inconsistencias dentro de cada grupo
        for source_type, group_events in grouped.items():
            if len(group_events) < 2:
                continue
            
            for i, e1 in enumerate(group_events):
                for e2 in group_events[i+1:]:
                    # Calcular diferencia temporal real
                    time_diff_seconds = abs((e1.timestamp - e2.timestamp).total_seconds())
                    
                    # Si los eventos están cerca en tiempo (< 2h)
                    if time_diff_seconds < 7200:
                        # Pero en timezones muy distintas
                        tz1_offset = e1.timestamp.utcoffset().total_seconds() / 3600
                        tz2_offset = e2.timestamp.utcoffset().total_seconds() / 3600
                        tz_diff = abs(tz1_offset - tz2_offset)
                        
                        if tz_diff > self.MIN_TIMEZONE_GAP_HOURS:
                            violations.append((
                                e1, e2,
                                f"Same source in timezones {tz_diff:.0f}h apart within {time_diff_seconds/60:.0f} minutes"
                            ))
        
        return violations
    
    def _normalize_timezones(self, events: List[TemporalEvent]) -> List[TemporalEvent]:
        """Normaliza todos los timestamps a UTC."""
        normalized = []
        
        for event in events:
            if event.timestamp.tzinfo is None:
                # Asumir UTC si no hay tzinfo
                normalized_ts = event.timestamp.replace(tzinfo=timezone.utc)
            else:
                # Convertir a UTC
                normalized_ts = event.timestamp.astimezone(timezone.utc)
            
            # Crear nuevo evento con timestamp normalizado
            normalized.append(TemporalEvent(
                source=event.source,
                timestamp=normalized_ts,
                confidence=event.confidence,
                metadata=event.metadata
            ))
        
        return normalized
    
    def _same_artifact(self, source1: str, source2: str) -> bool:
        """Determina si dos fuentes se refieren al mismo artefacto."""
        # Simplificación: compara prefijos
        prefix1 = source1.split(':')[0].lower()
        prefix2 = source2.split(':')[0].lower()
        
        # PDF:CreationDate y PDF:ModDate son del mismo artefacto
        return prefix1 == prefix2
    
    def _format_delta(self, delta: timedelta) -> str:
        """Formatea timedelta de forma legible."""
        total_seconds = abs(delta.total_seconds())
        
        if total_seconds < 60:
            return f"{int(total_seconds)}s"
        elif total_seconds < 3600:
            return f"{int(total_seconds/60)}m"
        elif total_seconds < 86400:
            return f"{total_seconds/3600:.1f}h"
        else:
            return f"{total_seconds/86400:.1f}d"
    
    def _empty_analysis(self) -> TemporalAnalysis:
        """Análisis para caso sin eventos."""
        return TemporalAnalysis(
            events=[],
            impossible_sequences=[],
            excessive_drifts=[],
            timezone_violations=[],
            verdict="ABSTAIN",
            confidence=Fraction(0),
            reasoning="No temporal events to analyze",
            evidence={}
        )


# =============================================================================
# EXTRACTOR DE TIMESTAMPS (HELPER)
# =============================================================================

class TimestampExtractor:
    """Extrae timestamps de artefactos comunes."""
    
    @staticmethod
    def extract_from_pdf(pdf_path: Path) -> List[TemporalEvent]:
        """Extrae timestamps de metadata PDF."""
        events = []
        
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            metadata = doc.metadata
            
            # CreationDate
            if metadata.get('creationDate'):
                try:
                    ts = TimestampExtractor._parse_pdf_date(metadata['creationDate'])
                    events.append(TemporalEvent(
                        source="PDF:CreationDate",
                        timestamp=ts,
                        confidence=Fraction(8, 10),
                        metadata={'raw': metadata['creationDate']}
                    ))
                except Exception as exc:
                    logger.warning("[TemporalDrift] Failed to parse PDF CreationDate %r: %s", metadata.get('creationDate'), exc)

            # ModDate
            if metadata.get('modDate'):
                try:
                    ts = TimestampExtractor._parse_pdf_date(metadata['modDate'])
                    events.append(TemporalEvent(
                        source="PDF:ModDate",
                        timestamp=ts,
                        confidence=Fraction(8, 10),
                        metadata={'raw': metadata['modDate']}
                    ))
                except Exception as exc:
                    logger.warning("[TemporalDrift] Failed to parse PDF ModDate %r: %s", metadata.get('modDate'), exc)

            doc.close()
        except Exception as exc:
            logger.warning("[TemporalDrift] Failed to open PDF %s: %s", pdf_path, exc)
        
        return events
    
    @staticmethod
    def extract_from_email(email_path: Path) -> List[TemporalEvent]:
        """Extrae timestamps de headers de email."""
        events = []
        
        try:
            import email
            from email import utils
            
            with open(email_path, 'rb') as f:
                msg = email.message_from_binary_file(f)
            
            # Date header
            if msg.get('Date'):
                try:
                    ts_tuple = utils.parsedate_to_datetime(msg['Date'])
                    events.append(TemporalEvent(
                        source="Email:Date",
                        timestamp=ts_tuple,
                        confidence=Fraction(9, 10),
                        metadata={'raw': msg['Date']}
                    ))
                except Exception as exc:
                    logger.warning("[TemporalDrift] Failed to parse Email Date header %r: %s", msg.get('Date'), exc)

            # Received headers (múltiples)
            for received in msg.get_all('Received', []):
                try:
                    # Parsear timestamp del Received header
                    # Formato: "from server by server; DATE"
                    parts = received.split(';')
                    if len(parts) > 1:
                        date_str = parts[-1].strip()
                        ts = utils.parsedate_to_datetime(date_str)
                        events.append(TemporalEvent(
                            source="Email:Received",
                            timestamp=ts,
                            confidence=Fraction(10, 10),  # Received es más confiable
                            metadata={'raw': date_str}
                        ))
                except Exception as exc:
                    logger.warning("[TemporalDrift] Failed to parse Received header %r: %s", received, exc)
                    continue
        except Exception as exc:
            logger.warning("[TemporalDrift] Failed to open email %s: %s", email_path, exc)
        
        return events
    
    @staticmethod
    def _parse_pdf_date(pdf_date_str: str) -> datetime:
        """
        Parsea formato de fecha PDF.
        
        Formato: D:YYYYMMDDHHmmSSOHH'mm'
        Ejemplo: D:20250120143000+05'00'
        """
        import re
        
        # Remover prefijo D:
        if pdf_date_str.startswith('D:'):
            pdf_date_str = pdf_date_str[2:]
        
        # Extraer componentes
        year = int(pdf_date_str[0:4])
        month = int(pdf_date_str[4:6])
        day = int(pdf_date_str[6:8])
        hour = int(pdf_date_str[8:10]) if len(pdf_date_str) > 8 else 0
        minute = int(pdf_date_str[10:12]) if len(pdf_date_str) > 10 else 0
        second = int(pdf_date_str[12:14]) if len(pdf_date_str) > 12 else 0
        
        # Parsear timezone
        tz_pattern = r"([+-])(\d{2})'(\d{2})'"
        tz_match = re.search(tz_pattern, pdf_date_str)
        
        if tz_match:
            sign = 1 if tz_match.group(1) == '+' else -1
            tz_hours = int(tz_match.group(2))
            tz_minutes = int(tz_match.group(3))
            tz_offset = timedelta(hours=sign * tz_hours, minutes=sign * tz_minutes)
            tz = timezone(tz_offset)
        else:
            tz = timezone.utc
        
        return datetime(year, month, day, hour, minute, second, tzinfo=tz)


# =============================================================================
# INTEGRACIÓN CON VIGÍA
# =============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python temporal_drift.py <pdf_or_email_path>")
        sys.exit(1)
    
    test_path = Path(sys.argv[1])
    
    # Extraer eventos
    if test_path.suffix.lower() == '.pdf':
        events = TimestampExtractor.extract_from_pdf(test_path)
    elif test_path.suffix.lower() in ['.eml', '.msg']:
        events = TimestampExtractor.extract_from_email(test_path)
    else:
        print(f"Unsupported file type: {test_path.suffix}")
        sys.exit(1)
    
    if not events:
        print("No temporal events found")
        sys.exit(0)
    
    # Analizar
    detector = TemporalDriftDetector()
    analysis = detector.analyze(events)
    
    print(f"\n{'='*70}")
    print(f"TEMPORAL DRIFT ANALYSIS: {test_path.name}")
    print(f"{'='*70}")
    print(f"Events Analyzed: {len(analysis.events)}")
    
    for event in analysis.events:
        print(f"  - {event.source}: {event.timestamp.isoformat()}")
    
    print(f"\nImpossible Sequences: {len(analysis.impossible_sequences)}")
    for e1, e2, reason in analysis.impossible_sequences:
        if e2:
            print(f"  ⚠️  {e1.source} ({e1.timestamp}) vs {e2.source} ({e2.timestamp})")
            print(f"      Reason: {reason}")
        else:
            print(f"  ⚠️  {e1.source} ({e1.timestamp})")
            print(f"      Reason: {reason}")
    
    print(f"\nExcessive Drifts: {len(analysis.excessive_drifts)}")
    for e1, e2, reason in analysis.excessive_drifts:
        print(f"  ⚠️  {reason}")
    
    print(f"\nTimezone Violations: {len(analysis.timezone_violations)}")
    for e1, e2, reason in analysis.timezone_violations:
        print(f"  ⚠️  {reason}")
    
    print(f"\n{'='*70}")
    print(f"VERDICT: {analysis.verdict}")
    print(f"CONFIDENCE: {int(analysis.confidence * 100)}%")
    print(f"{'='*70}")
    print(f"\nREASONING:\n{analysis.reasoning}")
    print(f"\nEVIDENCE:\n{analysis.evidence}")
    print(f"{'='*70}\n")
