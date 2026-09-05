# Veredicto sellado VIGÍA, hoja de revisión experta

| Campo | Valor |
| --- | --- |
| Caso | `VIGIA-KIWI-006-WITNESS-SELF-INCRIM` |
| Familia de bundle | `mcp_investigation` |
| Bundle de origen | `VIGIA-KIWI-006_bundle.json` |
| SHA-256 de origen | `8dbc6c9c030cbbed967678dcc1b3c5f3cc1960c98ff95beb4b06667013e5e5e7` |
| Audiencia | perito forense experto |
| Versión del formato de reporte | `1.0` |

> Este documento NO tiene autoridad de veredicto. Presenta un resultado sellado tal cual; no calculó nada, no reconcilió nada y puede regenerarse desde los bytes del bundle en cualquier momento. Si este texto y el bundle alguna vez difieren, el bundle tiene razón y este archivo quedó viejo.

> Los valores citados del bundle aparecen exactamente como fueron sellados, con su idioma, ortografía y forma numérica originales. Eso es la evidencia, no un defecto de presentación.

Bundle de investigación Modo 2: hallazgos y un `tool_execution_log` a prueba de manipulación, escritos durante una investigación en Claude Code / MCP. Los nombres de campo varían entre casos.

## 1. Cadena de custodia

Cada ancla de custodia que define esta familia, presente o explícitamente ausente. Los valores son los literales sellados.

| Campo | Valor sellado |
| --- | --- |
| `bundle_sha256` | `13b04eb93519b85deebdcde019c3220e22600a7daa561ea6df3e0b03df3f532d` |
| `integrity.bundle_hash` | *no presente en este bundle* |
| `primary_evidence_sha256` | `8e605c769e184e35725fd3d065933611c1fbed110f614d997c2cfcb3db6837a1` |
| `evidence_hash` | *no presente en este bundle* |
| `chain_tip_sha256` | *no presente en este bundle* |
| `timestamp_sealed` | `2026-06-25T17:23:08.052174+00:00` |

Los hashes sólo son comparables dentro de una misma familia de bundle. El `bundle_hash` de EBS v1, el digest del sidecar de un bundle de agente y el `bundle_sha256` de Modo 2 se calculan sobre payloads distintos (KNOWN_LIMITATIONS L-030, L-031).

## 2. Campos con veredicto

| Campo | Valor | Confianza | JSON pointer |
| --- | --- | --- | --- |
| `final_verdict` | **SUSPICION** | *no presente en este bundle* | `/final_verdict` |

## 3. Tríada peirceana por hallazgo (tal cual)

### `F-001` Linguistic Contagion Between Non-Independent Witnesses (SUSPICION)

**Firstness**

```text
Testimonios de Testigo-A y Hermano-Denunciante comparten frases literales: 'el hermano del', 'hermano del denunciante', 'de la imputada', 'material de la'.
```

**Secondness**

```text
Testigos independientes no deberien compartir frasologia especifica referencial. Score stylometry: 70% probabilidad entidad unica.
```

**Thirdness**

```text
COORDINATION SUSPICION: acuerdo previo entre testigos. Carnegie: social proof — multiples voces convergentes simulan validacion independiente.
```

### `F-002` Systematic Grice Relation Maxim Violation — Tactical Evasion (SUSPICION)

**Firstness**

```text
Los tres testimonios evitan sistematicamente los temas centrales del caso (contacto verificado, evidencia digital directa). Ninguno puede corroborar afirmaciones con prueba tecnica.
```

**Secondness**

```text
Testimonios cooperativos esperados (Grice): responden directamente a la pregunta relevante. Los tres testimonios desvian o son incapaces de corroborar la afirmacion central.
```

**Thirdness**

```text
TACTICAL_EVASION: los testigos construyen una narrativa emocional (miedo, locura) en lugar de evidencia factica. deception_probability=0.30.
```

### `F-003` Universal Conflict of Interest — Zero Independent Witnesses (SUSPICION)

**Firstness**

```text
Tres testigos: Testigo-A (vinculo con hermano), Hermano-Denunciante (parte directa), Madre-Denunciante (pariente del denunciante). independent_witnesses=0.
```

**Secondness**

```text
En testimonio valido para Daubert, se requieren testigos sin conflicto de interes documentado. Los tres tienen relacion directa con el denunciante.
```

**Thirdness**

```text
La ausencia total de testigos independientes es condicion estructural documentable — no interpretacion. Es un hecho objetivo derivado de la relacion entre los testigos y el denunciante.
```

### `F-004` Examiner Methodology Gap — No Independent Technical Verification (SUSPICION)

**Firstness**

```text
Todos los artefactos provienen de AT-001 manual_forensic_review. write_blocker_used=false en todos. No hay extraccion digital independiente, no hay network logs, no hay device forensics.
```

**Secondness**

```text
Daubert exige al menos dos fuentes independientes para INTENT. n_independent_sources=1. Los raw_scores (0.6-0.8) exceden baseline tipico (0.4-0.6) sin calibracion documentada.
```

**Thirdness**

```text
El gap metodologico es la razon tecnica por la cual el candidato INTENT no puede ser sellado. Device forensics adicional podria resolver la ambiguedad.
```

## 4. Scores sellados exactos

Cada valor es el literal sellado en el bundle: Fractions serializadas como `numerador/denominador`, floats como su literal JSON. Nada se redondea ni se convierte. Un float en un camino sellado es en sí mismo un hallazgo (KNOWN_LIMITATIONS L-021, L-073).

| JSON pointer | Literal sellado |
| --- | --- |
| `/findings/0/confidence` | `MEDIUM` |
| `/findings/1/confidence` | `LOW` |
| `/findings/2/confidence` | `CONFIRMED` |
| `/findings/3/confidence` | `CONFIRMED` |
| `/refutation_gate_log/candidate_confidence` | `85` |

## 5. Gates Daubert, refutación y abogado del diablo

Registros de un gate, un downgrade o una autocorrección, tal como quedaron guardados. Son las correcciones previas a la emisión que hacen defendible un veredicto.

### `/refutation_gate_log`

| Campo | Valor sellado |
| --- | --- |
| `benign_hypothesis_result` | PARTIAL PASS — explica contagio linguistico e individual Grice violations, no explica evidence_withheld + independent_witnesses=0 + universal conflict_of_interest combinados. Sin segunda fuente tecnica independiente, INTENT no puede ser confirmado. |
| `benign_hypothesis_tested` | Testigos discutieron el caso entre si (contagio linguistico natural), actuaron independientemente con comunicacion deficiente (Grice), conflictos de interes conocidos pero no probatoriamente maliciosos. |
| `candidate_confidence` | 85 |
| `candidate_verdict` | INTENT |
| `finding_id` | CANDIDATE-INTENT-001 |
| `forensic_note` | Arquitectura de auto-correccion pre-emision. Ningun veredicto incorrecto fue sellado. El LLM no puede sobreescribir este gate. |
| `gate_applied` | Daubert Corroboration Gate |
| `gate_result` | CANDIDATE REJECTED pre-emission. Emitted as SUSPICION. |
| `gate_rule` | n_independent_sources < 2 for this evidence class → cap SUSPICION |
| `source` | reason_with_llm (ollama/deepseek-r1:8b) |

### Entradas `devil_advocate`

`/findings/0/devil_advocate`

```text
Testigos que conocen el caso pueden naturalmente usar el mismo vocabulario al describirlo. La contagion linguistica puede ser resultado de discusiones familiares previas, no de coordinacion maliciosa.
```

`/findings/1/devil_advocate`

```text
Probabilidad de deception del 30% indica que el 70% restante puede explicarse por comunicacion deficiente, nerviosismo, o desconocimiento tecnico. No supera umbral INTENT.
```

`/findings/2/devil_advocate`

```text
Los testigos vinculados pueden tener conocimiento genuino de los hechos. El parentesco no invalida per se un testimonio bajo el sistema acusatorio argentino. La judicatura evalua credibilidad con este contexto.
```

`/findings/3/devil_advocate`

```text
Manual forensic review es metodologia legitima para evidencia testimonial. No toda evidencia digital es tecnicamente extractable. La ausencia de device forensics puede ser limitacion operativa.
```

## 6. Registro de ejecución

- Tipo de registro: `tool_execution_log`
- Entradas: 12
- `chain_version`: `1`
- `chain_tip_sha256`: ausente
- `chain_tip_hmac`: ausente

**Histograma (ordenado por cantidad, luego por nombre)**

| Etiqueta | Cantidad |
| --- | --- |
| `infer_intent` | 2 |
| `reason_with_llm` | 2 |
| `analyze_stylometry` | 1 |
| `audit_grice_maxims` | 1 |
| `calculate_shannon_entropy` | 1 |
| `contradiction_detector` | 1 |
| `detect_eco_overinterpretation` | 1 |
| `generate_forensic_hash` | 1 |
| `read_evidence` | 1 |
| `validate_and_correct_analysis` | 1 |

**Primeras 25 entradas**

| `seq` | `tool` | `target` | `result_summary` |
| --- | --- | --- | --- |
| 1 | reason_with_llm | LLM mode probe | llm_backend=ollama CONFIRMED |
| 2 | generate_forensic_hash | evidence/VIGIA-KIWI-006.json | SHA256=8e605c769e184e35725fd3d065933611c1fbed110f614d997c2cfcb3db6837a1 |
| 3 | read_evidence | evidence/VIGIA-KIWI-006.json | Hash match confirmed. 4504 bytes. 4 artifacts loaded. |
| 4 | calculate_shannon_entropy | A01 content | entropy=4.51, NORMAL human text range. NOISE. |
| 5 | infer_intent | A01 testimony | NOISE — tool not applicable to static testimony (designed for conversational trajectories). |
| 6 | infer_intent | A02 testimony | NOISE — tool not applicable to static testimony. |
| 7 | audit_grice_maxims | A01+A02+A03 testimonies | SUSPICION. Maxim RELATION violation. TACTICAL_EVASION. deception_probability=0.30. |
| 8 | detect_eco_overinterpretation | All 4 artifacts | NORMAL_DISTRIBUTION. obvious_ratio=0.0. No staging detected (false negative likely — tool uses term-frequency). |
| 9 | analyze_stylometry | A01+A02+A03 testimonies | INTENT. LINGUISTIC_CONTAGION A01-A02. same_entity_probability=0.70. COORDINATION_SUSPICION. |
| 10 | reason_with_llm | Full accumulated evidence | INTENT confidence=85. Carnegie: social proof manipulation. Coordinated fabrication pattern. |
| 11 | validate_and_correct_analysis | Candidate INTENT | MALICE_ANALYSIS flag: single_source, no_baseline, Daubert Gate fires. EVIDENCE_DELIMITER_MISMATCH. |
| 12 | contradiction_detector | CANDIDATE-INTENT-001 | BEFORE: INTENT(85%) \| AFTER: SUSPICION \| REASON: Daubert Corroboration Gate n_independent_sources=1 |

## 7. Cómo verificar este bundle por tu cuenta

Cada chequeo de abajo es independiente de este documento. Corrélo sobre el archivo del bundle, no sobre este reporte.

Bundle de investigación Modo 2: `python3 verify_tool_log.py VIGIA-KIWI-006_bundle.json` recorre la cadena de hashes de `tool_execution_log` (v1 y v2, más el ancla `chain_tip_sha256` cuando está). Exit 0 cadena intacta, 1 cadena rota, 2 error de uso. Pasá `--hmac-key-file` para verificación con clave.

Correr un verificador sobre la familia equivocada reporta no conformidad por diseño (docs/EXECUTION_MODES.md). Usá el comando que corresponde a la familia indicada en la cabecera.

## 8. Limitaciones conocidas

Limitaciones declaradas por el bundle, huecos encontrados por el lector, y las limitaciones del repositorio que acotan cualquier presentación de esta familia.

El lector de bundles no reportó huecos.

**Limitaciones que el propio bundle declara**

- L-001: All 4 artifacts from single examiner AT-001 (manual_forensic_review). No independent technical source. Prevents INTENT confirmation under Daubert.
- L-002: write_blocker_used=false for all artifacts. Digital evidence chain of custody not established at device level.
- L-003: infer_intent tool designed for conversational AI evasion trajectories — not applicable to static testimonial evidence. Applied and disregarded (NOISE).
- L-004: detect_eco_overinterpretation did not detect coordination pattern — tool uses term-frequency matching, not semantic coordination analysis. False negative likely.
- L-005: LLM backend = ollama (deepseek-r1:8b). Local model. reason_with_llm output treated as signal, not verdict.
- L-006: Device forensics (phone extraction, network logs, download verification) would resolve open INTENT candidate. Not available in current evidence set.

- L-004: la narrativa y el contenido de prompts son input redactado por el perito, no evidencia.
- L-020: los bundles de Modo 2 no llevan `audit_trail` granular.
- L-022: la validación de `devil_advocate` es en parte arquitectónica.
- L-030 / L-031: los caminos de sellado difieren; los hashes no son comparables entre familias y `verify_ebs_v1.py` rechaza bundles no-EBS por diseño.
- L-056: las arquitecturas de alerta de Modo 1 y Modo 2 divergen.
- L-074: esta presentación muestra los campos sellados tal cual y no puede llenar huecos que una familia no registra.

## 9. Glosario de términos sellados usados arriba

Los términos de abajo son los tokens literales que usa el bundle. Se explican, nunca se traducen.

- `CONFIRMED`: Estado de hallazgo: sostenido por al menos dos fuentes independientes.
- `Daubert`: Estándar de admisibilidad de EE. UU. para prueba pericial: método comprobable, tasa de error conocida, revisión de pares, aceptación general. Los gates de VIGÍA existen para cumplirlo.
- `Firstness`: Primera capa de Peirce: el signo en sí, descripto sin interpretar (qué se observó).
- `Fraction`: Número racional exacto (numerador/denominador). El scoring de VIGÍA usa Fractions para que dos máquinas den resultados idénticos; nunca son porcentajes.
- `INFERRED`: Estado de hallazgo: sostenido por una sola fuente; se intentó corroborar sin éxito.
- `LOW`: Etiqueta de confianza usada en hallazgos de Modo 2 (la más baja de tres).
- `MEDIUM`: Etiqueta de confianza usada en hallazgos de Modo 2 (la del medio de tres).
- `SUSPICION`: Peldaño 2 de 5. Hay una anomalía estructural; no hay evidencia de ocultamiento deliberado ni de coordinación.
- `Secondness`: Segunda capa de Peirce: el signo frente a su contexto; cómo se desvía de un baseline.
- `Thirdness`: Tercera capa de Peirce: la ley inferida; qué patrón deliberado y repetible produce el signo.
- `bundle_hash`: SHA-256 sobre todo el payload EBS v1 salvo el bloque integrity (Invariante I2). Cualquier cambio en cualquier campo lo altera.
- `bundle_sha256`: Bundle de Modo 2: SHA-256 que el investigador registró para el bundle al sellarlo.
- `chain_tip_sha256`: Bundle de Modo 2: entry_hash de la última entrada de tool_execution_log, guardado como hermano para que truncar el log sea detectable. (`tool_execution_log`)
- `chain_version`: Esquema de tool_execution_log: v1 protege sólo result_summary; v2 cubre toda la entrada.
- `devil_advocate`: La explicación benigna más fuerte que el análisis tuvo que vencer. Obligatoria para INTENT y MALICE; vacía significa que el veredicto no cumplió Daubert.
- `evidence_hash`: Bundle de Modo 2: nombre alternativo del campo del hash de evidencia.
- `mcp_investigation`: Familia de bundle: investigación de Modo 2 en Claude Code / MCP con hallazgos y un tool_execution_log encadenado por hashes. (`tool_execution_log`, `chain_tip_sha256`)
- `primary_evidence_sha256`: Bundle de Modo 2: SHA-256 del artefacto de evidencia primario, hasheado antes de leerlo.
- `refutation_gate_log`: Bundle de Modo 2: registro de veredictos candidatos que un gate Daubert rechazó antes de emitirlos, y por qué.
- `timestamp_sealed`: Bundle de Modo 2: hora en que el investigador lo selló.
- `tool_execution_log`: Bundle de Modo 2: lista de llamadas a herramientas encadenada por hashes (prev_hash, entry_hash, entry_hmac opcional). Se verifica con verify_tool_log.py. (`chain_version`)

---

Generado por `vigia.report` 1.0 a partir del bundle cuyo SHA-256 es `8dbc6c9c030cbbed967678dcc1b3c5f3cc1960c98ff95beb4b06667013e5e5e7`. No se registra fecha a propósito: los mismos bytes de bundle tienen que producir siempre los mismos bytes de reporte.
