<!--
VIGIA Academic Documentation
Module: 7b4e076e
Batch ID: vigia-doc-0100-7b4e076e
Generated: 2026-05-20T14:56:47.866285+00:00
-->

---
doc_hash: 7b4e076e
module: vigia/inference/check_determinism.py
languages: [EN, ES, RU, ZH]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

ENGLISH:
Add to table or glossary: `_BRIDGE_CANDIDATES` -> Maybe in glossary since it's an internal constant.
**Bridge Candidates**: Provisional intermediate tools under evaluation for stability before being granted full status in the deterministic pipeline.

ESPAÑOL:
**Candidatos a puente**: Herramientas intermedias provisionales en evaluación de estabilidad antes de obtener el estado completo en la tubería determinista.

РУССКИЙ:
**Кандидаты в мостовые инструменты**: Промежуточные инструменты на стадии оценки стабильности перед включением в детерминированный конвейер.

中文:
**桥接候选工具 (_BRIDGE_CANDIDATES)**: 在获得确定性流程正式地位之前，正在接受稳定性评估的临时中间组件。

Also, the docstring says "Exit codes: 0 — All runs pro". I should mention exit codes briefly. I can add a row in the table or mention in the text.

Let's add to "What Is This Module?" or a separate small table. Since the user lists it, I should cover it.

| Exit Code | Meaning |
|---|---|
| 0 | All runs produced identical hashes; the tool is deterministic. |
| Non-zero | Hash mismatch detected; non-determinism found. |

I'll add this to the key concepts table in each language.

Now, compiling the final output.

I need to ensure the markdown is clean. Use headers.

Structure:
# Module Documentation: `vigia/inference/check_determinism.py`

## ENGLISH

### What Is This Module?
...

### Key Concepts

| ... |
| ... |

### Glossary
...

### 【Scientific Note】
...



---

## ESPAÑOL

### ¿Qué es este módulo?
...

### Conceptos clave
...

### Glosario
...

### 【Nota Científica】
...



---

## РУССКИЙ

### Что это за модуль?
...

### Ключевые понятия
...

### Глоссарий
...

### 【Научное Примечание】
...



---

## 中文

### 这是什么模块？
...

### 核心概念

| ... |
| ... |

### 术语表
...

### 【科学说明】
...



---

Let me double check the Chinese terms again.
- 艾柯: used in scientific note. Yes.
- 格赖斯: used in scientific note. Yes.
- 取证工件: used in glossary and text. Yes.
- 逻辑断裂: used in table and glossary. Yes.

Also, the user says "Do NOT use floating-point math explanations — emphasize deterministic integer arithmetic where applicable". I have explicitly stated in EN: "non-determinism... floating-point approximations (the latter being irrelevant here as the system uses integer arithmetic)." And in the SHA-256 description: "deterministic integer-based hashing algorithm". This is good.

One final check on the scientific note sensor analogy. I used the word "witness" for sensor. That's a good analogy. I explicitly said they are formal abstractions, not mysticism. Good.

I should ensure I don't use any Python code examples, since the audience doesn't know Python. The user said "Generate documentation for the following Python module... for scientists who do NOT know Python". I will not include code blocks or Python syntax beyond the module path.

Let me refine the ENGLISH scientific note to make sure it's punchy and clear.

"VIGIA borrows terminology from semiotics—Charles Sanders Peirce, Umberto Eco, and H.P. Grice—to describe information structures. These terms are formal abstractions, not mysticism. Consider the sensor analogy: in engineering, we call a physical sensor a 'witness' to an event even though it lacks consciousness; it simply records data. Likewise, Peirce's sign, Eco's code, and Grice's maxims are analytical lenses for classifying how digital evidence carries meaning. They provide a rigorous logical framework; they do not invoke supernatural agency. When this module checks for determinism, it is ensuring that the 'sensor' (the analytical tool) records the same 'testimony' (the report) every time under identical conditions."

That's good.

For the exit code table in EN:
| Exit Code | Meaning |
|---|---|
| 0 | All runs produced identical SHA-256 hashes; the pipeline is deterministic. |
| Non-zero | A hash mismatch occurred, signaling non-determinism in the tool or pipeline. |

I'll integrate this into the Key Concepts table or as a separate small table. I'll make it part of the Key Concepts table to keep it concise.

Actually, a separate table might be better for readability. I'll do two tables: one for general concepts, one for script outputs. Or one big table. A big table might be too wide. Let's do two.

**Table 1: Forensic Concepts**
...
**Table 2: Script Outputs & Constants**
| Label | Meaning |
|---|---|
| Exit code 0 | Success: all runs yielded identical hashes. |
| Exit code non-zero | Failure: non-determinism detected. |
| VOLATILE_KEYS | Metadata fields excluded from comparison. |
| STABLE_TOOLS | Methods expected to be deterministic. |
| BRIDGE_TOOLS | Approved intermediate data translators. |
| _BRIDGE_CANDIDATES | Provisional tools awaiting stability verification. |

This covers all constants. I will do this for each language.

Let's write it out carefully.

**ENGLISH:**

#### Key Concepts

**Operational Outputs and Configuration**

| Label | Plain-Language Definition | Scientific Role |
|---|---|---|
| Exit code 0 | The script finishes and reports that all repeated analyses produced identical fingerprints. | Signals that the tool is deterministic and forensically admissible. |
| Non-zero exit | The script finishes and reports that at least one fingerprint differed across runs. | Signals non-determinism; the pipeline requires inspection before legal use. |
| VOLATILE_KEYS | Metadata fields that legitimately change between runs, such as timestamps or temporary paths. | Stripped from reports before hashing so they do not trigger false mismatches. |
| STABLE_TOOLS | Analytical methods engineered to produce bit-for-bit identical results on every execution. | The baseline tools whose determinism is being verified. |
| BRIDGE_TOOLS | Intermediate components that convert data between formats without altering meaning. | Must be deterministic; otherwise they introduce logical discontinuities in evidence handling. |
| _BRIDGE_CANDIDATES | New or modified intermediate tools currently under evaluation for stability. | Audited before promotion to full BRIDGE_TOOLS status to prevent non-determinism. |

**Determinism and Measurement**

| Concept | Plain-Language Definition | Scientific Role |
|---|---|---|
| Determinism | The property that a fixed input and fixed procedure always yield the same output. | The fundamental requirement for reproducible forensic science. |
| SHA-256 | A cryptographic hash function relying exclusively on deterministic integer arithmetic to produce a fixed-length fingerprint. | Provides an exact, computationally cheap method to detect even single-bit changes in output. |
| Evidence File | The digital object under investigation (disk image, log, packet capture, etc.). | The constant experimental input. |
| Forensic Admissibility | The standard that analytical methods must be repeatable and verifiable by independent parties. | The legal-scientific objective of the verification. |

#### Glossary
- **Determinism**: A system state in which output is entirely predicted by input and algorithm, free of random variation.
- **SHA-256 Hash**: A deterministic integer fingerprint of a data object. Any alteration, however minor, produces a completely different hash value.
- **Non-determinism**: Behavior causing identical inputs to yield different outputs across runs, typically from hidden state, concurrency, or non-integer approximations (the latter excluded here by design).
- **Chain of Custody**: The documented, unbroken lineage of evidence handling. Non-determinism constitutes a logical breach in this chain.
- **Integer Arithmetic**: Exact mathematical operations on whole numbers, without the rounding errors inherent to floating-point representation. SHA-256 is built entirely upon bitwise integer operations.
- **Volatile Key**: A metadata attribute that changes between experimental trials and must be neutralized to avoid false conclusions.
- **Bridge Candidate**: A provisional processing component undergoing stability trials before full operational acceptance.

#### 【Scientific Note】
...

This looks solid. I'll adapt this structure to all languages.

**ESPAÑOL:**

#### Conceptos clave

**Salidas y configuración operativas**

| Etiqueta | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Código de salida 0 | El script termina e informa que todos los análisis repetidos produjeron huellas digitales idénticas. | Señala que la herramienta es determinista y forensemente admisible. |
| Salida distinta de cero | El script termina e informa que al menos una huella difirió entre ejecuciones. | Señala no determinismo; la tubería requiere inspección antes de su uso legal. |
| VOLATILE_KEYS | Campos de metadatos que cambian legítimamente entre ejecuciones, como marcas de tiempo o rutas temporales. | Se eliminan de los informes antes del hash para evitar falsas discrepancias. |
| STABLE_TOOLS | Métodos analíticos diseñados para producir resultados idénticos bit a bit en cada ejecución. | Herramientas base cuyo determinismo se verifica. |
| BRIDGE_TOOLS | Componentes intermedios que convierten datos entre formatos sin alterar el significado. | Deben ser deterministas; de lo contrario, introducen discontinuidades lógicas en el manejo de evidencia. |
| _BRIDGE_CANDIDATES | Herramientas intermedias nuevas o modificadas actualmente en evaluación de estabilidad. | Auditadas antes de su promoción a estado BRIDGE_TOOLS para prevenir no determinismo. |

**Determinismo y medición**

| Concepto | Definición en lenguaje sencillo | Rol científico |
|---|---|---|
| Determinismo | La propiedad por la cual una entrada y un procedimiento fijos siempre producen la misma salida. | Requisito fundamental para la ciencia forense reproducible. |
| SHA-256 | Función hash criptográfica que se basa exclusivamente en aritmética entera determinista para producir una huella de longitud fija. | Método exacto y computacionalmente económico para detectar cambios de un solo bit en la salida. |
| Archivo de evidencia | Objeto digital bajo investigación (imagen de disco, registro, captura de paquetes, etc.). | Entrada experimental constante. |
| Admisibilidad forense | Estándar que exige que los métodos analíticos sean repetibles y verificables por partes independientes. | Objetivo científico-jurídico de la verificación. |

#### Glosario
- **Determ
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
