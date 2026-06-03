<!--
VIGIA Academic Documentation
Module: 2640bfa6
Batch ID: vigia-doc-0085-2640bfa6
Generated: 2026-05-20T14:56:47.862861+00:00
-->

---

## ENGLISH

### What Is This Module?
The **VIGÍA Forensic PDF Reporter** is a deterministic document-assembly system. It transforms a structured expert verdict—called a `ForensicVerdict`—into a court-admissible PDF report. Think of it as a scientific instrument that takes raw analytical conclusions and encodes them into a standardized legal document. The system guarantees reproducibility by relying exclusively on **deterministic integer arithmetic** for all checksums, timestamps, counters, and threshold comparisons. No floating-point approximations are used at any stage, ensuring that two identical inputs always yield bit-identical outputs.

The module contains three principal components:
1. **PeirceDaubertStyles** — A typographic-formatting engine that applies court-approved visual standards (fonts, margins, heading hierarchies) analogous to a journal’s LaTeX template.
2. **VigiaForensicReporter** — The core assembly engine. It ingests a `ForensicVerdict`, maps its contents across four technical layers, and renders them into a structured PDF.
3. **Convenience Functions (`generate_forensic_pdf`, `generate_report`)** — One-button interfaces that initiate the full pipeline, returning the exact file path of the generated document.

### Key Concepts

| Term | Plain-Language Definition | Role in the Module |
|---|---|---|
| **ForensicVerdict** | A structured data object containing the final expert opinion, findings, and custody metadata. | Serves as the sole input to the reporter. |
| **Peirce Semiotics** | A triadic framework: *Firstness* (raw possibility), *Secondness* (actual fact), *Thirdness* (governing law/rule). | Structures reasoning within each of the four technical analysis layers. |
| **Daubert Standard** | Legal criteria for admitting expert scientific evidence; demands testability, known error rates, and peer review. | Ensures the report’s methodology section meets admissibility requirements. |
| **Digital Chain of Custody** | An auditable trail linking every digital artifact to its origin via cryptographic hash and database records. | Enforced through SHA-256 integer fingerprints and SQLite relational links. |
| **Deterministic Integer Arithmetic** | Exact mathematical operations on whole numbers, free from rounding or representation error. | Guarantees that hashes, timestamps, layer metrics, and counts are fully reproducible. |
| **σ Deviation (Sigma)** | A quantized measure of variation from a baseline, expressed as an exact integer ratio to avoid rounding ambiguity. | Evaluated in the four technical layers to flag anomalies without floating-point drift. |
| **Logic Break** | A deterministic indicator of discontinuity within an integer-verified process, signaling a breach or anomaly. | Triggers detailed logging when a layer’s integer metrics exceed exact thresholds. |
| **SHA-256** | A cryptographic hash algorithm yielding a 256-bit integer fingerprint. | Provides integrity verification for every forensic artifact. |
| **SQLite Link** | A persistent reference pointer stored in a relational database file. | Creates a queryable, tamper-evident custody record. |

### Glossary

- **Artifact** — Any digital object collected as evidence (e.g., a memory image, log file, or network packet capture).
- **Firstness** — The mode of being of a quality or possibility; in forensic terms, the latent potential for an anomaly before it is triggered.
- **Secondness** — The mode of being of an actual fact or event; the moment an anomaly is detected.
- **Thirdness** — The mode of being of a law or habit; the deterministic rule that connects a detected event to its legal or technical interpretation.
- **Grado Pericial** — Expert grade; the formal evidentiary standard required of a forensic report in legal proceedings.
- **Deterministic System** — A system in which identical initial conditions always produce identical outputs, excluding all probabilistic approximation.

### 【Scientific Note】
The terminology of Peirce, Eco, and Grice is sometimes mistaken for metaphysical speculation. In this module, these terms function exactly like a **multi-layered sensor array**. **Firstness** is analogous to raw sensor voltage—unprocessed potential. **Secondness** is the triggered threshold alarm—an actual event. **Thirdness** is the calibrated inference engine that maps the alarm to a known failure mode. Umberto Eco’s code theory and Grice’s cooperative maxims serve as communication-protocol specifications, ensuring that the report’s signs (text, tables, hashes) unambiguously transmit the expert’s findings to the court, just as a deterministic bus protocol transmits sensor data to a controller without floating-point drift.

---

## ESPAÑOL

### ¿Qué es este módulo?
El **Reportero Forense PDF VIGÍA** es un sistema determinista de ensamblaje de documentos. Transforma un veredicto experto estructurado—denominado `ForensicVerdict`—en un informe pericial PDF admisible en juicio. Considérelo como un instrumento científico que toma conclusiones analíticas brutas y las codifica en un documento legal estandarizado. El sistema garantiza la reproducibilidad al basarse exclusivamente en **aritmética entera determinista** para todas las sumas de verificación, marcas temporales, conteos y comparaciones de umbrales. No se utilizan aproximaciones de coma flotante en ninguna etapa, asegurando que dos entradas idénticas siempre produzcan salidas idénticas bit a bit.

El módulo contiene tres componentes principales:
1. **PeirceDaubertStyles** — Motor de formato tipográfico que aplica estándares visuales aprobados para tribunales (fuentes, márgenes, jerarquías de títulos), análogo a una plantilla LaTeX de revista científica.
2. **VigiaForensicReporter** — Motor de ensamblaje central. Ingiere un `ForensicVerdict`, asigna sus contenidos a cuatro capas técnicas y los renderiza en un PDF estructurado.
3. **Funciones de conveniencia (`generate_forensic_pdf`, `generate_report`)** — Interfaces de un solo botón que inician la canalización completa, devolviendo la ruta exacta del archivo generado.

### Conceptos clave

| Término | Definición en lenguaje sencillo | Rol en el módulo |
|---|---|---|
| **ForensicVerdict** | Objeto de datos estructurado que contiene la opinión pericial final, los hallazgos y los metadatos de custodia. | Fuente de entrada única del generador. |
| **Semiótica de Peirce** | Marco triádico: *Primedad* (posibilidad bruta), *Segundidad* (hecho real), *Terceridad* (ley/regla gobernante). | Estructura el razonamiento dentro de cada una de las cuatro capas de análisis técnico. |
| **Estándar Daubert** | Criterios legales para admitir evidencia científica experta; exige comprobabilidad, tasas de error conocidas y revisión por pares. | Garantiza que la sección de metodología del informe cumpla los requisitos de admisibilidad. |
| **Cadena de Custodia Digital** | Rastro auditable que vincula cada artefacto digital con su origen mediante hash criptográfico y registros de base de datos. | Aplicada mediante huellas dactilares enteras SHA-256 y enlaces relacionales SQLite. |
| **Aritmética Entera Determinística** | Operaciones matemáticas exactas sobre números enteros, libres de redondeo o error de representación. | Asegura que los hashes, marcas temporales, métricas de capa y conteos sean plenamente reproducibles. |
| **Desviación σ (Sigma)** | Medida cuantizada de variación respecto a una línea base, expresada como razón entera exacta para evitar ambigüedad de redondeo. | Evaluada en las cuatro capas técnicas para señalar anomalías sin deriva de coma flotante. |
| **Ruptura Lógica** | Indicador determinista de discontinuidad dentro de un proceso verificado por enteros, señalando una brecha o anomalía. | Activa registro detallado cuando las métricas enteras de una capa exceden umbrales exactos. |
| **SHA-256** | Algoritmo hash criptográfico que produce una huella digital de 256 bits como número entero. | Provee verificación de integridad para cada artefacto forense. |
| **Enlace SQLite** | Puntero de referencia persistente almacenado en un archivo de base de datos relacional. | Crea un registro de custodia consultable y resistente a alteraciones. |

### Glosario

- **Artefacto** — Cualquier objeto digital recopilado como evidencia (p. ej., imagen de memoria, archivo de registro o captura de paquetes de red).
- **Primedad** — Modo de ser de una cualidad o posibilidad; en términos forenses, el potencial latente de una anomalía antes de que se active.
- **Segundidad** — Modo de ser de un hecho o evento actual; el momento en que se detecta una anomalía.
- **Terceridad** — Modo de ser de una ley o hábito; la regla determinista que conecta un evento detectado con su interpretación legal o técnica.
- **Grado Pericial** — Nivel experto; el estándar probatorio formal exigido a un informe forense en procedimientos legales.
- **Sistema Determinista** — Sistema en el que condiciones iniciales idénticas siempre producen salidas idénticas, excluyendo toda aproximación probabilística.

### 【Nota Científica】
La terminología de Peirce, Eco y Grice es a veces confundida con especulación metafísica. En este módulo, estos términos operan exactamente como una **matriz de sensores multicapa**. La **Primedad** es análoga al voltaje crudo del sensor—potencial no procesado. La **Segundidad** es la alarma de umbral activada—un evento real. La **Terceridad** es el motor de inferencia calibrado que asocia la alarma con un modo de fallo conocido. La teoría de códigos de Umberto Eco y las
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
