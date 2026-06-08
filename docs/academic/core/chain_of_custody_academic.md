<!--
VIGIA Academic Documentation
Module: cc27fff8
Batch ID: vigia-doc-0043-cc27fff8
Generated: 2026-05-20T14:56:47.853722+00:00
-->

---

## ENGLISH

### What Is This Module?

`vigia/core/chain_of_custody.py` is the laboratory notebook of the VIGÍA digital-forensics platform. It chronicles every manipulation of a digital evidence artifact—who accessed it, when, and what changed—by generating cryptographic fingerprints (SHA-256 hashes) and universal timestamps. Imagine a permanently bound logbook in which each new page is physically linked to the previous one; removing or altering a page breaks the seal and exposes the tampering.

### Key Concepts

| Concept | Plain-Language Definition | Scientific Function |
|---|---|---|
| **Chain of Custody** | A chronological ledger of every action taken on a piece of digital evidence. | Guarantees integrity and provenance for legal and scientific review. |
| **Custody Record** | One entry in the ledger: actor + timestamp + action + fingerprint. | Provides an atomic, indivisible unit of accountability. |
| **SHA-256 Hash** | A 256-bit deterministic integer fingerprint computed from file contents via exact arithmetic on bits and bytes. | Detects alteration; any microscopic change yields a completely different integer identifier. |
| **Timestamp** | A standardized UTC temporal marker. | Establishes strict temporal order and prevents back-dating. |
| **Actor** | The human operator or automated system performing the action. | Attributes responsibility and enables end-to-end audit tracing. |
| **Immutability** | The property that historical records cannot be changed retroactively. | Ensures that past observations remain scientifically valid and legally defensible. |
| **Evidence Bundle** | A compiled export of the chain for court or peer review. | Facilitates reproducibility and cross-institutional verification. |
| **Deterministic Integer Arithmetic** | Operations on discrete whole numbers (bits and bytes) without approximation. | Eliminates platform-dependent variance; identical inputs always yield identical hash integers on any system. |

### Glossary

- **Deterministic Integer Arithmetic**: Mathematical operations performed on exact whole numbers. SHA-256 processes data as discrete integers, so every identical file always produces the same hash value on every computer, with no rounding or approximation errors.
- **Hash (SHA-256)**: A one-way function that maps data of arbitrary size to a fixed 256-bit integer. It acts as a unique specimen barcode.
- **Actor**: The entity (person or service account) responsible for an action. Equivalent to a dated signature in a paper lab notebook.
- **Immutability**: Once a record is written, it cannot be silently modified. Any tampering creates a detectable logical discontinuity.
- **Timestamp**: A temporal coordinate, expressed in UTC, marking when an event occurred.
- **Evidence Bundle**: A standardized package containing the evidence together with its complete chain-of-custody log.

【Scientific Note】
Terminology inspired by semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—is sometimes mistaken for metaphysical speculation. It is not. In digital forensics, these concepts function exactly like sensor calibration theory. Peirce’s *interpretant* is the measurable output produced when a sign (the evidence artifact) interacts with an observer (the forensic system). Eco’s *encyclopedia* corresponds to the contextual calibration matrix that allows different laboratories to agree on what a pattern means. Grice’s *cooperative maxims* are the communication protocol ensuring that the custodial record is not noise but meaningful signal. Treating the chain of custody as a semiotic sensor rig turns mysticism into metrology.

---

## ESPAÑOL

### ¿Qué es este módulo?

`vigia/core/chain_of_custody.py` es el cuaderno de laboratorio de la plataforma forense VIGÍA. Rastrea cada manipulación de un artefacto de evidencia digital—quién lo tocó, cuándo y qué cambió—mediante huellas criptográficas (hash SHA-256) y marcas temporales universales. Imaginese un registro encuadernado de forma permanente donde cada página nueva está unida a la anterior; arrancar o alterar una página rompe el sello y delata la intrusión.

### Conceptos clave

| Concepto | Definición en lenguaje sencillo | Función científica |
|---|---|---|
| **Cadena de custodia** | Registro cronológico de cada acción sobre una evidencia digital. | Garantiza integridad y procedencia para revisión legal y científica. |
| **Registro de custodia** | Una línea del registro: actor + marca temporal + acción + huella. | Unidad atómica e indivisible de responsabilidad. |
| **Hash SHA-256** | Huella digital entera determinista de 256 bits calculada mediante aritmética exacta sobre bits y bytes. | Detecta alteración; cualquier cambio mínimo genera un identificador entero completamente distinto. |
| **Marca temporal** | Marcador de tiempo estandarizado en UTC. | Establece orden temporal estricto e impide fechados retroactivos. |
| **Actor** | Operador humano o sistema automatizado que ejecuta la acción. | Atribuye responsabilidad y permite trazabilidad completa. |
| **Inmutabilidad** | Propiedad de que los registros históricos no pueden cambiarse retroactivamente. | Asegura que observaciones pasadas sigan siendo válidas científica y legalmente. |
| **Paquete de evidencia** | Exportación compilada de la cadena para tribunal o revisión por pares. | Facilita reproducibilidad y verificación interinstitucional. |
| **Aritmética entera determinista** | Operaciones sobre números enteros discretos (bits y bytes) sin aproximación. | Elimina varianza entre plataformas; entradas idénticas siempre producen el mismo hash en cualquier sistema. |

### Glosario

- **Aritmética entera determinista**: Operaciones matemáticas sobre números enteros exactos. Como SHA-256 procesa datos como enteros puros, todo archivo idéntico siempre produce el mismo valor de hash en cualquier computadora, sin errores de redondeo ni aproximación.
- **Hash (SHA-256)**: Función unidireccional que asigna a datos de tamaño arbitrario un entero fijo de 256 bits. Actúa como un código de barras único para el espécimen.
- **Actor**: Entidad (persona o cuenta de servicio) responsable de una acción. Equivalente a una firma fechada en un cuaderno de papel.
- **Inmutabilidad**: Una vez escrito un registro, no puede modificarse en silencio. Cualquier manipulación crea una discontinuidad lógica detectable.
- **Marca temporal**: Coordenada temporal, generalmente en UTC, que marca cuándo ocurrió un evento.
- **Paquete de evidencia**: Paquete estandarizado que contiene la evidencia y su registro completo de cadena de custodia.

【Nota Científica】
La terminología inspirada en la semiótica—Charles Sanders Peirce, Umberto Eco y H.P. Grice—es a veces confundida con especulación metafísica. No lo es. En forense digital, estos conceptos funcionan exactamente como la teoría de calibración de sensores. El *interpretante* de Peirce es la salida medible cuando un signo (el artefacto de evidencia) interactúa con un observador (el sistema forense). La *enciclopedia* de Eco corresponde a la matriz de calibración contextual que permite que distintos laboratorios acuerden qué significa un patrón. Los *máximas cooperativas* de Grice son el protocolo de comunicación que garantiza que el registro de custodia no sea ruido, sino señal significativa. Tratar la cadena de custodia como un aparato semiótico-sensorial convierte el misticismo en metrología.

---

## РУССКИЙ

### Что представляет собой этот модуль?

`vigia/core/chain_of_custody.py` — это лабораторный журнал платформы
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
