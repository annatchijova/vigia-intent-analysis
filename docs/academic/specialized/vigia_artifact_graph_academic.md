<!--
VIGIA Academic Documentation
Module: 3254c6ec
Batch ID: vigia-doc-0029-3254c6ec
Generated: 2026-05-20T14:56:47.850876+00:00
-->

---
doc_hash: 3254c6ec
module: unknown
languages: [EN]
generated_by: moonshot-kimi-k2.6-batch-api
license: Apache-2.0
---

---

# ENGLISH

## What Is This Module?
This module is a deterministic scientific pipeline that transforms a digital evidence collection (`ForensicBundle`) into a directed topological map—a **Semantic Knowledge Graph of Artifacts**. Instead of treating a cyber intrusion as a simple timeline, the system models attacker behavior as a network of privilege expansion: processes, files, network connections, credentials, and log entries become nodes, while their causal or correlational relationships become directed edges. The resulting graph exposes lateral movement, choke points, and logical fractures within the victim infrastructure. The engine is built for reproducibility: all internal metrics are computed with integer arithmetic and lexicographically sorted traversals, eliminating bit-level variations between runs.

## Key Concepts

| Concept | Scientific Meaning | Role in Investigation |
|---|---|---|
| `ForensicBundle` | A normalized evidence container holding heterogeneous digital traces. | Input data source. |
| Semantic Knowledge Graph | A directed graph where vertices are forensic entities and edges are semantically meaningful relations. | Structural model of the incident. |
| Artifact Node | A single entity: process, file, credential, configuration key, log entry, or abductive hypothesis. | Atom of evidence. |
| Directed Edge | An asymmetric link indicating influence, flow, or derivation. | Causal or correlational pathway. |
| Lateral Movement | Adversary progression through a network via incremental privilege escalation. | Topological expansion pattern. |
| `FallbackGraph` | A redundant graph engine implemented in pure standard-library code, activated when NetworkX is absent. | Resilience guarantee. |
| Deterministic Output | Bit-for-bit reproducible results achieved via integer counts and sorted iteration order. | Scientific validity. |

## Glossary

- **Abductive Hypothesis** — An inference to the best explanation. A hypothesis node is generated when observed artifacts display a pattern best explained by a specific intrusion mechanism, analogous to a scientist proposing a theory from anomalous measurements.
- **Betweenness** — A topological measure of how frequently a node lies on the shortest path between other nodes, indicating control or brokerage points.
- **GEXF / GraphML / JSON** — Standard, platform-neutral exchange formats for graph data (compatible with Gephi, yEd, Cytoscape, and D3.js).
- **In-Degree / Out-Degree** — Integer counts of incoming and outgoing edges. High out-degree may identify a pivot point; high in-degree may indicate a data-collection target.
- **Lexicographic Sorting** — Alphanumeric ordering of identifiers to guarantee that every execution produces an identical sequence.
- **NetworkX** — An optional external library for advanced graph algorithms. The core system does not depend on it.
- **PageRank** — A linkage-topology centrality metric (when applicable) that ranks nodes by structural importance rather than chronology.
- **Privilege Expansion** — The spatial spread of access rights across a system, modeled as topological growth rather than temporal progression.

【Scientific Note】
Terms such as abduction (Peirce), semiotics (Eco), and conversational maxims (Grice) are formal epistemological instruments, not mysticism. Think of the system as a sensor array: when a physical sensor detects smoke, it does not "believe" in fire; it registers a deviation from baseline and infers a source via known physical laws. Similarly, an **abductive hypothesis** node is generated when the graph registers a **logical fracture**—a pattern break—that is best explained by a specific intrusion mechanism. Umberto Eco’s semiotics provides a taxonomy for classifying signs (artifacts) by their relational function, while H.P. Grice’s maxims describe expected cooperative behavior; violations of these maxims in log data become detectable anomalies. The graph does not perform divination. It applies rigorous inference rules to observable evidence, exactly as a spectrometer infers chemical composition from emission lines.

---

# ESPAÑOL

## ¿Qué es este módulo?
Este módulo es una tubería científica determinista que transforma una colección de evidencia digital (`ForensicBundle`) en un mapa topológico dirigido: un **Grafo de Conocimiento Semántico de Artefactos**. En lugar de ver una intrusión como una simple línea temporal, el sistema modela el comportamiento del atacante como una red de expansión de privilegios: procesos, archivos, conexiones de red, credenciales y entradas de registro se convierten en nodos, mientras que sus relaciones causales o correlacionales se convierten en aristas dirigidas. El grafo resultante revela patrones de movimiento lateral, puntos de estrangulamiento y fracturas lógicas en la infraestructura. El motor está diseñado para la reproducibilidad: todas las métricas internas se calculan con aritmética entera y recorridos ordenados lexicográficamente, eliminando variaciones a nivel de bit entre ejecuciones.

## Conceptos Clave

| Concepto | Significado Científico | Rol en la Investigación |
|---|---|---|
| `ForensicBundle` | Contenedor normalizado de evidencia que alberga trazos digitales heterogéneos. | Fuente de datos de entrada. |
| Grafo de Conocimiento Semántico | Grafo dirigido donde los vértices son entidades forenses y las aristas son relaciones semánticamente significativas. | Modelo estructural del incidente. |
| Nodo Artefacto | Una entidad única: proceso, archivo, credencial, clave de configuración,
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
