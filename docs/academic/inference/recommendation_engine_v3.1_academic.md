<!--
VIGIA Academic Documentation
Module: adc5d097
Batch ID: vigia-doc-0103-adc5d097
Generated: 2026-05-20T14:56:47.866961+00:00
-->

---
doc_hash: adc5d097
module: unknown
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

# ENGLISH

## What Is This Module?

`recommendation_engine_v3.1.py` is the forensic recommendation engine **VIGÍA**. It serves as a deterministic conduit between an upstream risk-assessment layer (`RiskBoundedDecisionLayer`) and an immutable forensic ledger (`recommendation_ledger`). 

Think of it as a laboratory protocol automaton: it ingests a test result (`audit_id` paired with `policy_id`), appends a precise UTC timestamp, and computes a collision-free fingerprint using **SHA-256 over integer-delimited byte sequences**—never floating-point values. Before writing any record, it verifies that the safety gate (`podSelector`) is not accidentally set to “open all.” Finally, no action reaches the execution stage until a human operator supplies a cryptographic proof of consent via an **HMAC signature** (Rule X).

*Version note (C2):* This v3.1 release does **not** contain a webhook handler or the `_NoRedirect` class; those artifacts belong to a different version lineage.

### Key Concepts

| Concept | Description | Scientific Relevance |
|---|---|---|
| **Deterministic ID** (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Eliminates `PRIMARY KEY` collisions. Identical evidence + policy + time always yields the same 256-bit digest, satisfying the *Daubert* reproducibility standard. |
| **Field Separator** (`_SEPARATOR`) | The pipe symbol `\|` concatenating tokens before hashing | Guarantees unambiguous parsing of discrete alphanumeric strings into a single byte vector. |
| **podSelector Validation** (v3.1-3) | Empty `{}` selectors are rejected prior to `INSERT` | Prevents accidental namespace-wide isolation; acts as a **logical break** in the workflow. |
| **Rule X — HMAC Hold** | `operator_hmac_signature` remains `NULL` until a human operator signs | Enforces algorithmic-human dual control: software proposes, human disposes. |
| **Risk-Bounded Verdict** | Output from `RiskBoundedDecisionLayer` | The trigger event that causes the engine to instantiate a recommendation. |
| **Forensic Bundle Spec** | Output of `get_recommendation_spec()` | A structured **forensic artifact** containing complete metadata for chain-of-custody packaging. |
| **Resource Release** | `close()` method | Terminates connections and releases handles deterministically. |

### Glossary

- **Audit ID** — A unique pointer to a specific digital-evidence event.
- **Policy ID** — The governance rule identifier activated by the event.
- **Timestamp (UTC)** — A discrete temporal coordinate in Coordinated Universal Time, ensuring global uniqueness without timezone ambiguity.
- **SHA-256** — A cryptographic hash function operating entirely via deterministic integer arithmetic (bitwise logic and modular 32-bit addition over finite fields). It accepts discrete bytes and emits a fixed 256-bit integer digest; no floating-point approximations exist in its pipeline.
- **PRIMARY KEY** — A database integrity constraint ensuring every persisted record is uniquely addressable.
- **podSelector** — A label filter (Kubernetes-style) designating which computational pods a policy governs. An empty selector would match everything.
- **HMAC** — Hash-based Message Authentication Code. A deterministic signature proving both message integrity and operator identity.
- **Daubert Standard** — A legal benchmark requiring expert methods to be testable, reproducible, and peer-reviewable.
- **Logical Break** — A deliberate workflow interruption that stops propagation when pre-conditions violate safety boundaries.
- **Forensic Artifact** — Any structured data object (here, the recommendation specification) intended for inclusion in a forensic evidence bundle.

### 【Scientific Note】

> Terms drawn from semiotics—**Charles Sanders Peirce** (sign, index, symbol), **Umberto Eco** (code, overcoding), and **H. P. Grice** (implicature, cooperative maxims)—are occasionally dismissed as mysticism. They are not. Within this engine they behave exactly like a **sensor transduction model**:
> 
> - **Peirce’s index** is the causal trace left on a detector (the `audit_id`).  
> - **Eco’s code** is the calibration table that maps raw sensor voltage to a physical unit (the `policy_id`).  
> - **Grice’s maxims** are the noise-filtering rules that treat an empty `podSelector` as a violation of cooperative clarity and reject it.  
> 
> The resulting inference chain is deterministic, measurable, and falsifiable—no different from reading a thermometer or a mass spectrometer.



--- ESPAÑOL SECTION ---

# ESPAÑOL

## ¿Qué es este módulo?

`recommendation_engine_v3.1.py` es el **motor de recomendaciones forenses VIGÍA**. Actúa como un conducto determinista entre una capa superior de evaluación de riesgos (`RiskBoundedDecisionLayer`) y un libro mayor forense inmutable (`recommendation_ledger`).

Piénselo como un autómata de protocolo de laboratorio: ingiere un resultado de prueba (`audit_id` junto con `policy_id`), le anexa una marca temporal UTC exacta y calcula una huella digital libre de colisiones mediante **SHA-256 sobre secuencias de bytes delimitadas por enteros**—nunca valores de punto flotante. Antes de escribir registro alguno, verifica que la compuerta de seguridad (`podSelector`) no esté accidentalmente en modo “abrir todo”. Finalmente, ninguna acción alcanza la etapa de ejecución hasta que un operador humano aporte una prueba criptográfica de consentimiento mediante una **firma HMAC** (Regla X).

*Nota de versión (C2):* Esta versión 3.1 **no** contiene manejador de *webhook* ni la clase `_NoRedirect`; esos artefactos pertenecen a un linaje de versión distinto.

### Conceptos Clave

| Concepto | Descripción | Relevancia Científica |
|---|---|---|
| **ID determinista** (v3.1 B/2) | `SHA256(audit_id + '\|' + policy_id + '\|' + timestamp_utc)` | Elimina colisiones de `PRIMARY KEY`. La misma evidencia + política + tiempo siempre produce el mismo resumen de 256 bits, satisfaciendo
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
