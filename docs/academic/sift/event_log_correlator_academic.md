<!--
VIGIA Academic Documentation
Module: fda3319e
Batch ID: vigia-doc-0133-fda3319e
Generated: 2026-05-20T14:56:47.873182+00:00
-->

---
doc_hash: fda3319e
module: unknown
languages: [EN, ES]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

## ENGLISH

### What Is This Module?

This module is a deterministic forensic pipeline that reads Windows event logs (EVTX and XML) and converts them into structured investigative findings. It is designed for scientists and investigators who need rigorous, reproducible results without requiring knowledge of the Python programming language.

The module treats every log as a **sequence of integer-coded symbols**. It parses binary and XML artifacts, binds them into immutable records, and then correlates those records using exact integer arithmetic—never approximations. It searches for known attack signatures (ordered integer Event ID sequences), detects missing events via integer sequence deltas, and flags temporal anomalies using circular integer-hour binning.

This release incorporates three Priority-0 security hardening measures:  
1. **ReDoS-resistant** regular expressions with bounded length and no catastrophic backtracking.  
2. **XML parsing** with implicit entity expansion forbidden.  
3. A deterministic **50 MB integer ceiling** on input logs to prevent memory exhaustion.

---

### Key Concepts

| Concept | Plain-Language Definition | Integer-Arithmetic Role |
|---|---|---|
| **Event Record** | A single line or item in a Windows log file | Stored as an integer Event ID paired with an integer epoch timestamp |
| **Forensic Artifact** | Any digital object carrying investigative value | Handled as a bounded byte sequence (≤ 52 428 800 bytes) |
| **Attack Chain** | A deterministic sequence of actions left by an intruder | Matched against ordered integer EID vectors with exact alignment |
| **Logic Gap** | A missing or out-of-sequence event | Computed via integer delta between sequence numbers or timestamps |
| **Semiotic Triad** | A formal sign–object–interpretant mapping framework | Implemented as deterministic rule tables keyed by integer identifiers |
| **Signal Vector** | A numeric fingerprint of a log entry | Produced by `to_signal()` as an integer-encoded representation for direct comparison |

---

### Component Reference

| Name | Type | Purpose |
|---|---|---|
| `TOOL_NAME` | Constant | Human-readable string identifier of the module |
| `MAX_LOG_SIZE_BYTES` | Constant | Hard integer ceiling: 52 428 800 bytes (50 MiB) |
| `_ATTACK_CHAINS` | Constant | Immutable tuples of integer Event ID sequences representing known attack patterns |
| `_HIGH_SEVERITY_EIDs` | Constant | A `frozenset` of critical integer Event IDs |
| `_MAX_GAP_EVENTS` | Constant | Integer threshold for the maximum acceptable discontinuity in a chain |
| `EventRecord` | Class | Immutable container for one log entry (integer EID, integer timestamp, metadata) |
| `EventLogFinding` | Class | A single interpreted detection result with integer severity ranking |
| `EventLogAnalysisResult` | Class | Aggregate container collecting all findings and integer summary statistics |
| `WindowsEventLogParser` | Class | Deterministic binary/XML parser that enforces the integer size guard |
| `AttackChainDetector` | Class | Integer-sequence alignment engine; matches logs to `_ATTACK_CHAINS` |
| `LogGapDetector` | Class | Detects integer-sequence or temporal voids exceeding `_MAX_GAP_EVENTS` |
| `AnomalousHourDetector` | Class | Bins events into 24 integer-hour slots and flags deviations via integer counts |
| `EventLogCorrelator` | Class | Orchestrator that runs the full deterministic integer pipeline |
| `to_signal()` | Function | Maps an `EventRecord` to an integer signal vector for deterministic comparison |
| `parse_evtx()` | Function | Reads binary EVTX streams; aborts if the integer byte limit is exceeded |
| `parse_xml()` | Function | Reads XML logs with entity expansion explicitly disabled |
| `detect()` | Function (polymorphic) | Integer-based anomaly flag; implemented by each detector class |
| `analyze()` | Function | End-to-end deterministic pipeline returning an `EventLogAnalysisResult` |

---

### Glossary

| Term | Definition |
|---|---|
| **EVTX** | The native binary event log format used by modern Windows operating systems. |
| **ReDoS** | Regular Expression Denial of Service; caused by catastrophic backtracking in pattern matching. Eliminated here through length-bounded safe expressions. |
| **XML Entity Expansion** | A memory-exhaustion attack that nests entity references inside XML. Prevented by implicit forbidding during parse. |
| **Memory Exhaustion** | System instability caused by unbounded input consumption. Prevented by the integer 50 MB cap. |
| **Event ID (EID)** | An integer code assigned by the operating system to classify the type of a log entry. |
| **Semiotics** | The formal study of signs and symbols; in this module, a rule-based deterministic framework for interpreting log data. |
| **Backtracking** | Algorithmic reversal during regex execution. Removed to guarantee deterministic runtime bounds. |

---

> **【Scientific Note】**  
> The terminology of Peirce, Eco, and Grice is sometimes mistaken for mysticism or literary criticism. Within this module, it is employed strictly as a formal epistemological framework—analogous to a physical sensor. A thermocouple does not “mystically” know temperature; it produces an integer millivolt value via deterministic junction physics. Likewise, Peircean *representamina*, Eco’s *codes*, and Gricean *maxims* are deterministic rule-sets that map raw log symbols to investigative findings through exact integer thresholds. They are engineering tools for meaning extraction, not metaphysics.



---

## ESPAÑOL

### ¿Qué es este módulo?

Este módulo es una tubería forense determinista que lee registros de eventos de Windows (EVTX y XML) y los convierte en hallazgos investigativos estructurados. Está diseñado para científicos e investigadores que necesitan resultados rigurosos y reproducibles sin conocer el lenguaje de programación Python.

El módulo trata cada registro como una **secuencia de símbolos codificados en enteros**. Analiza artefactos binarios y XML, los vincula en registros inmutables y luego los correlaciona mediante aritmética entera exacta —nunca aproximaciones. Busca firmas de ataque conocidas (secuencias ordenadas de ID de evento enteros), detecta eventos faltantes mediante deltas enteros de secuencia y señala anomalías temporales utilizando contenedores circulares de horas enteras.

Esta versión incorpora tres endurecimientos de seguridad Prioridad-0:  
1. Expresiones regulares **resistentes a ReDoS** con longitud acotada y sin retroceso catastrófico.  
2. **Análisis XML** con prohibición implícita de expansión de entidades.  
3. Un **techo entero determinista de 50 MB** para los registros de entrada a fin de prevenir el agotamiento de memoria.

---

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Rol de la aritmética entera |
|---|---|---|
| **Registro de evento** | Una línea o ítem individual en un archivo de registro Windows | Almacenado como ID de evento entero + marca temporal entera |
| **Artefacto forense** | Objeto digital con valor investigativo | Manejado como secuencias de bytes acotadas (≤ 52 428 800 bytes) |
| **Cadena de ataque** | Secuencia determinista de acciones dejadas por un intruso | Emparejada como vectores ordenados de EID enteros con alineación exacta |
| **Vacío lógico** | Evento faltante o fuera de secuencia | Calculado mediante delta entero entre números de secuencia o marcas temporales |
| **Tríada semiótica** | Marco formal de mapeo signo–objeto–interpretante | Implementado como tablas de reglas deterministas con claves enteras |
| **Vector de señal** | Huella numérica de una entrada de registro | Producido por `to_signal()` como representación codificada en enteros para comparación directa |

---

### Referencia de componentes

| Nombre | Tipo | Propósito |
|---|---|---|
| `TOOL_NAME` | Constante | Identificador legible por humanos del módulo |
| `MAX_LOG_SIZE_BYTES` | Constante | Techo entero rígido: 52 428 800 bytes (50 MiB) |
| `_ATTACK_CHAINS` | Constante | Tuplas inmutables de secuencias de EID enteros que representan patrones de ataque conocidos |
| `_HIGH_SEVERITY_EIDs` | Constante | Un `frozenset` de identificadores de evento críticos en enteros |
| `_MAX_GAP_EVENTS` | Constante | Umbral entero para la discontinuidad máxima aceptable en una cadena |
| `EventRecord` | Clase | Contenedor inmutable para una entrada de registro (EID entero, marca temporal entera, metadatos) |
| `EventLogFinding` | Clase | Un único resultado de detección interpretado con clasificación de severidad entera |
| `EventLogAnalysisResult` | Clase | Contenedor agregado que recolecta todos los hallazgos y estadísticas resumen enteras |
| `WindowsEventLogParser` | Clase | Analizador binario/XML determinista que impone el guardián de tamaño entero |
| `AttackChainDetector` | Clase | Motor de alineación de secuencias enteras; empareja registros con `_ATTACK_CHAINS` |
| `LogGapDetector` | Clase | Detecta vacíos de secuencia o temporales que exceden `_MAX_GAP_EVENTS` |
| `AnomalousHourDetector` | Clase | Agrupa eventos en 24 franjas horarias enteras y señala desviaciones mediante conteos enteros |
| `EventLogCorrelator` | Clase | Orquestador que ejecuta la tubería determinista de enteros completa |
| `to_signal()` | Función | Mapea un `EventRecord` a un vector de señal entero para comparación determinista |
| `parse_evtx()` | Función | Lee flujos EVTX binarios; aborta si se excede el límite entero de bytes |
| `parse_xml()` | Función | Lee registros XML con la expansión de entidades explícitamente deshabilitada |
| `detect()` | Función (polimórfica) | Bandera de anomalía basada en enteros; implementada por cada clase detectora |
| `analyze()` | Función | Tuberial determinista de extremo a extremo que devuelve un `EventLogAnalysisResult` |

---

### Glosario

| Término | Definición |
|---|---|
| **EVTX** | El formato binario nativo de registros de eventos usado por los sistemas operativos Windows modernos. |
| **ReDoS** | Denegación de servicio mediante expresiones regulares; causada por retroceso catastrófico. Eliminado aquí mediante expresiones seguras con límite de longitud. |
| **Expansión de entidades XML** | Ataque de agotamiento de memoria que anida referencias de entidades dentro de XML. Prevenido mediante prohibición implícita durante el análisis. |
| **Agotamiento de memoria** | Inestabilidad del sistema causada por consumo descontrolado de entradas. Prevenido por el límite entero de 50 MB. |
| **ID de evento (EID)** | Código entero asignado por el sistema operativo para clasificar el tipo de entrada de registro. |
| **Semiótica** | El estudio formal de signos y símbolos; en este módulo, un marco determinista basado en reglas para interpretar datos de registro. |
| **Retroceso
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
