# BUGS_PENDIENTES.md — VIGÍA Bug Registry (Pendientes)

Registro de bugs **realmente pendientes**: abiertos, documentados sin fix
aplicado, o con una decisión de arquitectura sin tomar. Formato: un bloque
por bug, con el mismo número que tuvo siempre — nunca se renumera.

Los bugs ya resueltos, cerrados, aplicados o descartados viven en
[`BUGS_HISTORICO.md`](./BUGS_HISTORICO.md) — separados el 2026-07-25 para
que este archivo quede navegable. Útil para quien quiera hacer red team
sobre VIGÍA: ahí está todo lo que ya se encontró y se corrigió. La
numeración es compartida entre ambos archivos: un mismo B-XXX nunca
aparece en los dos a la vez.

---

## B-010 — TODO: migrar forensic_technical_detector.py a SemioticDetectorV2

| Campo | Valor |
|-------|-------|
| **Estado** | ABIERTO |
| **Severidad** | P3 — deuda técnica, no bug funcional |
| **Archivo** | `vigia/core/forensic_technical_detector.py` |
| **Línea** | 194 |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |

### Descripción

```python
# TODO: migrar a SemioticDetectorV2 en v3.0
```

El detector técnico forense sigue usando la arquitectura v1. `SemioticDetectorV2`
existe pero no está wired aquí. No es un bug funcional — el detector opera
correctamente con la arquitectura actual. Es deuda de migración para v3.0.

### Fix cuando corresponda

Evaluar si SemioticDetectorV2 cubre todos los casos de forensic_technical_detector.
Migración debe ser auditada por el colectivo antes de aplicar.

---

## B-111 — Mode 3 (Ollama/hermes3:8b): comportamiento no confiable en evidencia testimonial densa — N=2, ESTOCÁSTICO

| Campo | Valor |
|-------|-------|
| **Estado** | OBSERVADO — evidencia insuficiente para escalar a KNOWN_LIMITATIONS |
| **Severidad** | P3 (experimental — Mode 3 ya clasificado como no-primario) |
| **Detectado en** | Experimento comparativo ciego 2026-07-13, KIWI-006 y KIWI-007 |
| **N observaciones** | 2 corridas KIWI-006 (1 alucinación, 1 limpia) + 1 corrida KIWI-007 (JSON truncado) |

### Observaciones

**Corrida 1 — KIWI-006, primera ejecución:** `hermes3:8b` alucinó
`"carnegie_pattern": "JAILBREAK_ATTEMPT"` y
`"security_alert": "EVIDENCE_DELIMITER_MISMATCH"` — campos inexistentes en el
esquema VIGÍA. El modelo interpretó el contenido del testimonio (vigilancia,
contactos bloqueados, coordinación de testigos) como evidencia de un ataque sobre
sí mismo. El análisis Peircean correcto también estaba presente en la misma
respuesta, embebido junto a los campos alucinados. JSON válido.

**Corrida 2 — KIWI-007, primera ejecución:** `hermes3:8b` retornó JSON inválido
(objeto truncado a mitad del campo A02, después de completar A01). La herramienta
detectó el fallo y retornó `"error": "LLM did not return valid JSON."` con el
fragmento en `"raw_response"`. Requirió síntesis manual para A02 y A03.

**Corrida 3 — KIWI-006, re-ejecución con prompt IDÉNTICO (2026-07-13, misma sesión):**
Resultado limpio. Sin alucinación. JSON válido completo. Cadena Peircean correcta.
Veredicto NOISE 0.25, razonable y consistente con CAIE.

### Estado de la evidencia

N=2 corridas de KIWI-006 (1 alucinación / 1 limpia con mismo prompt). El
comportamiento es **estocástico, no determinista** — el mismo input no reproduce
el mismo error. N=1 para KIWI-007 (truncado), sin re-corrida todavía.

No escala a KNOWN_LIMITATIONS porque:
- N insuficiente para establecer frecuencia de error
- La re-corrida de KIWI-006 fue limpia → no es un patrón consistente
- Mode 3 ya está clasificado como experimental/complementario en el README y CLAUDE.md

### Qué observar en corridas futuras

- ¿La alucinación de jailbreak reaparece en KIWI-006 con una tercera corrida?
- ¿KIWI-007 trunca consistentemente o fue un evento único?
- ¿Otros casos testimoniales densos (KIWI-007 análogos) muestran el mismo patrón?
- Si la tasa de alucinación se confirma en >20% de corridas en casos testimoniales:
  escalar a KNOWN_LIMITATIONS con recomendación de `gemma3:27b` para Mode 3
  en producción sobre narrativa densa.

### Nota sobre no-reproducibilidad

La no-reproducibilidad del error es, en sí misma, un dato relevante: un error
consistente se detecta en testing; uno estocástico puede llegar a producción sin
señal previa. Si se confirma con más muestras que la tasa no es despreciable,
ese argumento de opacidad sería el fundamento para la limitación formal, no los
dos eventos aislados actuales.

---

## B-112 — CAIE catalogue gap candidato: SELF_INCRIMINATION_LOG — evidencia auto-incriminatoria epistemicamente distinta de log espoofeable por tercero

| Campo | Valor |
|-------|-------|
| Detectado | 2026-07-13 |
| Caso fuente | KIWI-001-A02 y KIWI-003-A03/A04 (expediente MPF7779408) |
| Estado | CANDIDATO — N=1 caso judicial real |

### Descripcion

Cuando el propio actor aporta voluntariamente credenciales o logs que lo incriminan a si mismo en documentacion judicial, el artefacto es epistemicamente irrefutable aunque CAIE le asigne `spoofability=0.85` (log_entry). La metrica de spoofability modela un atacante externo que fabrica evidencia; no aplica cuando la evidencia proviene del propio acusador.

En KIWI-001 (A02) y KIWI-003 (A03/A04), el denunciante (actor_a) presento sus propias credenciales de servidor de stalkeo y admitio haber hackeado a una ex pareja. CAIE computa adjusted=0.0071 y 0.0081 respectivamente por spoofability=0.85 — valores que subestiman el peso epistemico real. Si existiera una fractura `SELF_INCRIMINATION_LOG`, el composite superaria el umbral de SUSPICION en ambos casos sin necesidad de escalada manual.

### Restriccion de generalizacion

Los tres casos KIWI (001, 002, 003) pertenecen al mismo expediente judicial (MPF7779408) vistos desde angulos distintos — **no son 3 muestras independientes, son 1 caso real mirado 3 veces**. La observacion es N=1 de caso judicial real. Se necesita un segundo expediente independiente con la misma estructura (acusador que aporta evidencia auto-incriminatoria) antes de generalizar este patron como gap de catalogo real e implementar la fractura.

### Criterio de escalada

Observar el patron en un segundo expediente judicial independiente (distinto a MPF7779408). No implementar la fractura hasta entonces.

---

## B-113 — CAIE catalogue gap candidato: INSTITUTIONAL_REJECTION — rechazo institucional independiente como corroboracion forense

| Campo | Valor |
|-------|-------|
| Detectado | 2026-07-13 |
| Caso fuente | KIWI-003-A05 (expediente MPF7779408) |
| Estado | CANDIDATO — N=1 caso judicial real |

### Descripcion

En KIWI-003-A05, tres oficios presentaron 6 irregularidades formales y dos comisarias rechazaron independientemente ejecutar el allanamiento ordenado. El rechazo institucional de dos organismos independientes constituye corroboracion forense de la irregularidad documental — una fuente de evidencia que CAIE no captura porque `document_geometry` solo modela el artefacto fisico, no la reaccion institucional frente a el.

Si existiera una fractura `INSTITUTIONAL_REJECTION`, el artefacto A05 pasaria de adjusted=0.0327 a un peso significativamente mayor, dado que el rechazo policial elimina la explicacion de "error administrativo aislado" como hipotesis benigna.

### Restriccion de generalizacion

Misma restriccion que B-112: los tres casos KIWI son el mismo expediente MPF7779408 — **N=1 caso real**. No es evidencia de un gap sistematico del catalogo CAIE hasta que se observe en un segundo expediente independiente con rechazo institucional de documentacion en contexto forense.

### Criterio de escalada

Observar el patron en un segundo expediente judicial independiente (distinto a MPF7779408). No implementar la fractura hasta entonces.

---

## B-116 — `signal_quality_gate.py` designed and functional in isolation, NOT wired to scorer — dry-run shows 122/199 cases degraded

> **Update 2026-07-17 (condition 4 re-measured, Kimi-endorsed placeholder
> policy applied):** the four acquisition/conversion placeholders
> (`legacy_converter`, `manual_forensic_review`, `generate_forensic_hash`,
> `read_evidence`) no longer count as analysis tools — they are skipped in
> the `tool_name -> source_tool -> evidence_type` fallback, exactly like the
> literal "unknown". Single source of truth: `_NON_ANALYSIS_PLACEHOLDERS`
> in `vigia/core/signal_quality_gate.py` (not replicated in scripts).
> Re-measured dry-run (corpus grew 202 -> 205 evaluable): MODE B passed
> 77 -> 87; ABSTAIN_INSUFFICIENT_TOOLS 66 -> 40 (the -26 matches the
> census: 31/66 had >=2 distinct evidence_type; the uncovered cases now
> land honestly in the next checks — DEPENDENT_SIGNALS/LOW_Z_VARIANCE);
> degraded-with-expected-MALICE 46 -> 42. Gate remains UNWIRED (zero
> production callers): no verdict moved. Tests:
> `tests/test_b116_placeholder_tools.py` (9, red-first).

> **Update 2026-07-22 (clase B-211 purgada del gate; condición 4
> re-medida sin cambios):** `_get_z_score()` devolvía `abs(z)` sin coerción
> pese a declarar `-> float`; con z_scores `Fraction` (el transporte normal
> del pipeline VIGÍA) los seis `f"{...:.2f}"` del módulo crashean en
> Python < 3.12 (el pinneado por la CI) — reproducido. El crash era latente
> por la misma razón que B-211: cero callers de producción. Fix:
> `float(abs(...))` — contractual con la firma declarada; el gate opera en
> espacio float por diseño (umbrales 2.0/0.5) y no está en el path sellado.
> Tests: `tests/test_b116_gate_fraction_z.py` (4, rojo-primero; incluye
> paridad Fraction/float). Dry-run re-medido post-fix: idéntico al
> 2026-07-17 (MODE B: 87 pasan, 42 MALICE degradados) — la condición 4
> sigue sin cumplirse, el gate sigue SIN cablear.

> **Update 2026-07-22 (MODE C — condición 1 demostrada en modo medición,
> condición 4 medida con unidades honestas):**
> `scripts/dryrun_b116_mode_c.py` computa z reales por señal
> (mediana/MAD·1.4826 de la población benigna del dataset Tanda C
> `signal_calibration_dataset_20260709.json`, baseline propia para tipos
> con n≥5, fallback agrupado declarado). Resultado corpus 202: pasan 117
> (MODE B: 87); degradados expected-MALICE **27** (MODE B: 42), separables
> en 3 clases con causa raíz: C1 metadata degenerada de la serie REAL/SRL
> (16, `evidence_type`/`source_tool` nunca poblados en la conversión), C2
> señales débiles bajo baseline agrupada (5, indistinguible hasta resolver
> C1), C3 tensión doctrinal mono-canal vs diversidad (6, cf. L-067, ex-L-051). El
> gate sigue SIN cablear. Camino al desbloqueo, gates pre-registrados y
> decisiones pendientes de Anna: `docs/B116_CONDITION4_DESIGN.md`.
>
> **Update 2026-07-22 bis (excavación refutó C1/C2 — MALICE degradados
> 27 → 7, todos doctrinales):** la serie REAL/SRL declara su canal en el
> campo `type` que ni el gate ni el dry-run leían (C1 era artefacto del
> instrumento, NO del corpus — backfill innecesario, corpus intacto), y
> no transporta `raw_score` en JSON (C2 ídem: ahora
> `UNMEASURABLE_FROM_JSON`, 24 casos). Fixes: eslabón `type` en
> `_get_tool_name()` (tests `tests/test_b116_type_fallback.py`) +
> honestidad de medición en `scripts/dryrun_b116_mode_c.py`. Residuo:
> 7 casos, TODOS clase C3 doctrinal (mono-tool genuino o uniformidad de
> scores que B-171 lee como fabricación y el gate como ruido). La
> condición 4 queda bloqueada únicamente por la decisión doctrinal
> cap-vs-WARN de Anna — ver §3-bis/§4 del diseño.
>
> **Update 2026-07-22 ter — CABLEADO EN MODO SOMBRA (decisión de Anna:
> WARN, no cap):** `vigia/core/signal_quality_shadow.py` (línea base MODE C
> congelada con proveniencia: dataset Tanda C sha256 60023fd5aef6bf41…)
> + anexo `signal_quality_shadow` en el retorno principal de
> `_vigia_score()` — evaluado DESPUÉS de fijar verdict/score/confidence,
> import defensivo, contrato no-lanzar; cero autoridad de veredicto.
> Corrida comparativa pre-registrada: **0 flips** de verdict/score/
> confidence en 202 casos (snapshot antes de la edición vs después).
> Distribución sombra: 117 QUALITY_OK, 84 WARN, 1 early-return sin anexo
> (paths ERROR/exculpatorio retornan antes del Step 5 — esperado). Tests:
> `tests/test_b116_shadow_mode.py` (5: presencia, cero autoridad, crash
> del sombra no rompe scoring, no-imputación, no-lanzar). La promoción de
> WARN a cualquier autoridad requiere corrida comparativa nueva + firma
> de Anna. El estado POSPUESTO se levanta a: **CABLEADO COMO SOMBRA —
> observación en curso**.

| Campo | Valor |
|-------|-------|
| **Estado** | CABLEADO COMO SOMBRA (WARN) — 2026-07-22, decisión de Anna. El gate evalúa y anexa `signal_quality_shadow` al resultado del scorer con CERO autoridad de veredicto (corrida comparativa: 0 flips en 202 casos). Condición 4 reducida a decisión doctrinal ya tomada. Ver los updates cronológicos abajo y `docs/B116_CONDITION4_DESIGN.md` §5-bis. (Estado previo: POSPUESTO — bloqueado por desajuste de interfaz y calidad de datos.) |
| **Severidad** | P2 (gate-level architectural gap — el mecanismo ahora observa en sombra; promoción a autoridad requiere nueva corrida 0-flips + firma) |
| **Archivo** | `vigia/signal_quality_gate.py` AND `vigia/core/signal_quality_gate.py` (identical duplicates) |
| **Detectado en** | Post-hackathon session 2026-07-14, dry-run script `scripts/dryrun_signal_quality_gate.py` |

### Description

`SignalQualityGate` implements five checks before a verdict can be emitted:
tool diversity (>= 2 tools), signal strength (z >= 2.0), tool independence
(<= 60% from same tool), z-score variance (range >= 0.5), and noise inflation
detection. The module is complete, tested in isolation, and conceptually aligned
with VIGIA's Daubert corroboration requirements (vigia_scorer.py lines 1194-1240).

However, it has **zero callers** in the codebase. No import of
`SignalQualityGate` exists anywhere outside its own file. Additionally, the
module is duplicated: `vigia/signal_quality_gate.py` and
`vigia/core/signal_quality_gate.py` are byte-identical copies.

### Dry-run results (2026-07-14)

A full corpus dry-run (`scripts/dryrun_signal_quality_gate.py`) tested the gate
against all 199 cases using two signal-mapping modes:

**MODE A** (raw_score passed directly as z_score):
198/199 cases fail — unusable. raw_score lives in [0.0, 0.98]; gate demands
z >= 2.0 for "strong". Pure unit mismatch.

**MODE B** (raw_score * 4.0 as z_score — generous rescaling):

| Gate reason | Cases failed | Detail |
|-------------|-------------|--------|
| `ABSTAIN_INSUFFICIENT_TOOLS` | 67 | Only 1 unique `source_tool` in case |
| `ABSTAIN_WEAK_SIGNALS` | 20 | No raw_score >= 0.50 |
| `ABSTAIN_DEPENDENT_SIGNALS` | 18 | > 60% artifacts from same tool |
| `ABSTAIN_LOW_Z_VARIANCE` | 17 | raw_scores too uniform |
| **Total degraded** | **122** | |
| **Passed gate** | **76** | |

Of the 122 degraded cases, **23 are currently MALICE** — including 11 from the
VIGIA-REAL-001 to REAL-010 series (the most validated corpus in the project).
These cases have `source_tool=unknown` because the field was never populated
during conversion, not because they lack forensic provenance.

### Root cause (three independent blockers)

1. **Interface mismatch**: gate expects `tool_name` + `z_score` (statistical
   z-scores from a calibrated distribution). The scorer produces `source_tool` +
   `raw_score` in [0.0, 1.0]. No z-score computation exists in the current
   scoring pipeline — `fit_calibration.py` produces z_scores per tool
   (`z_scores` dict in sample schema, line 41) but is not yet wired into the
   main scoring path.

2. **Data quality**: 67/199 cases (33%) have only 1 unique `source_tool`,
   and many of those use `source_tool=unknown`. The field does not reflect
   the actual diversity of forensic tools that produced the evidence.

3. **Duplicate module**: `vigia/signal_quality_gate.py` and
   `vigia/core/signal_quality_gate.py` are identical. The `vigia.core.*` path
   is the modern convention; the root copy should be removed when wiring.

### Unblocking conditions

This gate can be wired when ALL of the following are met:

1. `fit_calibration.py` is integrated into the scoring pipeline, producing
   real z-scores per signal (not raw_scores in [0,1]).
2. The z-score output schema includes a `tool_name` field compatible with
   `SignalQualityGate._get_tool_name()`, or the gate is adapted to read
   `evidence_type` (which IS reliably populated).
3. The `source_tool=unknown` problem in legacy cases is resolved (either by
   backfilling from bundle metadata or by having the gate fall back to
   `evidence_type` diversity instead of `source_tool` diversity).
4. A new dry-run confirms 0 true-positive MALICE cases are degraded.

**NOTE for `fit_calibration.py` roadmap**: when z-score output is finalized,
verify compatibility with `SignalQualityGate.evaluate()` input schema. The
gate's `_get_z_score()` reads `signal.z_score` (attribute) or
`signal["z_score"]` (dict key). The calibrator's sample schema uses
`z_scores` (plural, nested dict by tool). These must align before wiring.

### Avance parcial (2026-07-16) — el gate sigue SIN cablear

Tres de los cuatro ítems de desbloqueo avanzaron; el gate permanece sin
callers de producción por diseño (la condición 4 — dry-run con 0 casos MALICE
verdaderos degradados — sigue sin cumplirse):

1. **Duplicado eliminado** (blocker 3): `vigia/signal_quality_gate.py` borrado;
   `vigia/core/signal_quality_gate.py` es la única copia (eran byte-idénticas,
   mismo md5, cero imports del path raíz).
2. **Fallback de diversidad implementado** (condición de desbloqueo 3, opción
   B): `_get_tool_name()` ahora resuelve `tool_name` → `source_tool` →
   `evidence_type`, tratando `"unknown"` como ausente. Tests:
   `tests/test_b116_quality_gate_fallback.py` (8 tests).
3. **Dry-run reconstruido y versionado**: el script original del 2026-07-14
   nunca se commiteó; `scripts/dryrun_signal_quality_gate.py` lo reconstruye
   (mismos MODE A/B) y queda en el repo para que la medición sea reproducible.

**Medición fresca (2026-07-16, corpus 202 casos evaluables):**

| | MODE A (z=raw) | MODE B (z=raw*4) |
|---|---|---|
| Pasan gate | 0 | 77 |
| Degradados | 202 | 125 |
| `ABSTAIN_INSUFFICIENT_TOOLS` | 66 | 66 |
| Degradados con expected_verdict=MALICE | 104 | 46 |

(Los números del 2026-07-14 contaban 199 casos y "23 currently MALICE" —
métrica distinta: veredicto emitido vs `expected_verdict` que usa el script
versionado. No son comparables uno a uno.)

**Hallazgo del censo de `source_tool` en los 66 casos INSUFFICIENT_TOOLS:**
los valores dominantes son placeholders de conversión/adquisición, no
herramientas de análisis: `None` (91 artifacts), `legacy_converter` (88),
`manual_forensic_review` (43), `generate_forensic_hash` (35),
`read_evidence` (8). El fallback conservador (solo `"unknown"` tratado como
ausente) no los cubre: 31 de los 66 casos tienen >= 2 `evidence_type`
distintos y pasarían el check de diversidad si esos placeholders se trataran
como ausentes. **Decisión pendiente (Anna):** definir el set de placeholders
de conversión que no cuentan como herramienta (`legacy_converter`,
`manual_forensic_review`, `generate_forensic_hash`, `read_evidence`) — es
política de datos, no código; con esa decisión el fallback existente los
cubre con un cambio de una línea.

### Why not adapt the gate instead

The gate's checks are doctrinally correct as designed. Adapting it to accept
raw_score instead of z_score would weaken its statistical meaning: a raw_score
of 0.8 from `read_evidence` and a raw_score of 0.8 from `Volatility3/malfind`
have vastly different forensic weight, but the gate would treat them identically.
The right fix is upstream: produce calibrated z-scores, then the gate works
as intended.

### Decision

Postponed. Gate remains unwired. Documented as B-116 for tracking. The
`vigia_scorer.py` corroboration gate (lines 1194-1240) partially covers the
same Daubert requirement using `evidence_type` diversity and domain-based
counting, but does not implement noise inflation detection or z-score
variance checks — those are unique to `SignalQualityGate` and will add
forensic value once the interface is resolved.

---

## B-123 — Causal Closure Score gate designed and tested, NOT wired — dry-run inviable (0/258 cases have data)

| Campo | Valor |
|-------|-------|
| **Estado** | POSPUESTO — bloqueado por cadena completa de productores huérfanos |
| **Severidad** | P2 (Daubert gate — prevents MALICE verdicts without causal coherence) |
| **Archivos** | `vigia/core/causal_closure.py`, `vigia/patterns/adversarial_silence.py`, `vigia/temporal/coherence_validator.py`, `vigia/core/explainable_governance.py` |
| **Test existente** | `tests/test_audit_gates.py` (pasa en aislamiento) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Description

Causal Closure Score (CCS) gate that caps the maximum verdict at ABSTAIN
when the causal coherence of the evidence is below 50%. The formula:

```
CCS = 0.3 * temporal_coherence
    + 0.2 * semantic_resonance
    + 0.3 * abductive_parsimony
    + 0.2 * adversarial_silence

If CCS < 0.50 -> verdict capped at ABSTAIN
```

Each dimension defaults to `Fraction(1/2)` (maximum uncertainty) when not
available. The gate is doctrinally correct: high signal + low causal
coherence = fabrication profile (Daubert).

### Why not wired today

**The 4 input dimensions do not exist in ANY case of the corpus (0/258).**
Without real data, CCS = exactly 0.50 for every case (all defaults), and
the gate passes unconditionally (`>= 0.50`). Wiring the gate today would
be cosmetic — it would add processing cost without changing a single verdict.

### Blocking dependency chain

The gate requires 4 producer modules, all disconnected from the scoring pipeline:

| CCS dimension | Intended producer | Status |
|---|---|---|
| `temporal_coherence` | `vigia/temporal/coherence_validator.py` | Orphaned (this cluster) |
| `semantic_resonance` | `vigia/inference/cross_artifact_resonance.py` | Live, but does NOT produce this field |
| `abductive_parsimony` | `vigia/abduction/hypothesis_lineage.py` | Orphaned (93KB, entire namespace disconnected) |
| `adversarial_silence` | `vigia/patterns/adversarial_silence.py` | Orphaned (this cluster) |

### Comparison with B-116 (signal_quality_gate)

| | B-116 signal_quality_gate | B-123 causal_closure |
|---|---|---|
| Data available in corpus | raw_score/source_tool exist | None of the 4 dimensions exist |
| Dry-run possible | Yes (with rescaling) | No (all default to 0.50) |
| Measurable impact | 122/199 degraded | 0/258 (trivial — no data) |
| Blocking dependency | 1 module (fit_calibration.py) | 4 orphaned modules (full chain) |
| Unblocking effort | Medium (z-score integration) | High (wire 4 producers + schema) |

### Decision on the 4 files

**NOT candidates for deletion.** Unlike the dead weight removed in B-121,
these files implement real, doctrinally correct forensic logic:

- `causal_closure.py` — the gate itself, Fraction arithmetic, tested
- `adversarial_silence.py` — adversarial gap detection (CLAUDE.md invariant: "deliberate artifact deletion elevates MALICE signal weight")
- `coherence_validator.py` — temporal causality violation detection
- `explainable_governance.py` — ExplanationEngine for ACCEPT/REJECT/ABSTAIN narrative + Daubert compliance section

They are preserved as pending-to-wire capability, not abandoned code.

### Unblocking conditions

The gate can be wired when ALL of the following are met:

1. At least 2 of the 4 producer modules are wired to the scoring pipeline
   and produce real values for their CCS dimension.
2. The corpus includes cases with real CCS dimension values (not all defaults).
3. A meaningful dry-run (with real data) shows acceptable impact on the corpus.

### Update 2026-07-23 — excavación completa + H-04 resuelto + productores caracterizados

Excavación triple contra código vivo (`docs/B123_EXCAVATION_20260723.md`):
el acoplamiento productores→CCS es SOLO documental (docstrings, cero
imports); `vigia_artifact_graph` (float no-determinista declarado) y
`vigia_counter_fact` (int) quedan descalificados como fuentes CCS;
materia prima real: timestamps en 82% del corpus (0% en VIGIA-REAL-*,
esquema CONTENT), `cost` abductivo entero vivo, CAR sin campo semántico
real (constantes de plantilla descartadas por `to_signal()`).

Intervenciones de riesgo cero aplicadas: **H-04 RESUELTO** (el gate
pasaba a MALICE_HIGH con cero información; ahora 2+ dimensiones ausentes
→ `insufficient_coverage` → ABSTAIN pre-umbral; los 2 xfail de
`test_audit_gates.py` promovidos a guardas + 2 tests de frontera) y
**caracterización de ASD/HLT** (tenían cero tests;
`tests/test_b123_producer_characterization.py`, 9 tests con valores
Fraction exactos sondeados). El cableo del CCS sigue POSPUESTO: las 4
dimensiones requieren decisiones de método D1-D4 (§5 del informe) antes
de cualquier sombra.

**Update 2026-07-23 bis — D1 medida, resultado negativo honesto:** las
dos opciones de temporal_coherence (TCV vs severidad) implementadas en
Fraction puro y corridas sobre el corpus
(`scripts/dryrun_b123_d1_temporal_coherence.py`): 0 desacuerdos entre
opciones, 1/202 casos ejercita la dimensión (2 declaran
EFFECT_BEFORE_CAUSE, 1 valida contra artefactos). Elegir método hoy
sería doctrina sin evidencia; cablear sería cosmético (1.0 casi
constante). D1 DIFERIDA por cobertura de corpus — el bloqueo de B-123
queda cuantificado y re-medible en un comando (informe §6).

---

## B-124 — Verdict/governance cluster: 6 modules designed, tested, NOT wired — same pattern as B-123

| Campo | Valor |
|-------|-------|
| **Estado** | POSPUESTO — same blocking pattern as B-123 (cadena de productores huérfanos) |
| **Severidad** | P2 (governance gates not firing — safety mechanisms exist but are disconnected) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### The 6 files

**Scoring-adjacent (highest conceptual severity):**

1. **`vigia/core/ockham_adversarial.py`** (224 lines) — Adversarial simplicity
   penalty: penalizes benign hypotheses that are "too simple" in the presence
   of malice signals (SolarWinds pattern). Needs `candidate_cost` /
   `next_best_cost` (Fraction) + `malice_signal_strength` from
   `hypothesis_lineage.py` (orphaned, vigia/abduction/). The concept "ockham"
   exists live in `abductive_intent_engine.py` (`_build_ockham_rationale`) but
   as a SEPARATE inline implementation — this module is NOT invoked by it.

2. **`vigia/core/dissent_report.py`** (305 lines) — Minority signal escalation:
   "9 modules say BENIGN + 1 behavioral module says MALICE = escalation
   required." Needs results from ALL cluster modules to generate a dissent
   report. Zero callers.

**Defensive / security:**

3. **`vigia/core/config_sentinel.py`** — Config tampering guardian: monitors
   critical modules (CAIE, TrustFusion, OckhamAdversarial, SignalRouter) for
   silent degradation. Zero callers. Its absence means no runtime detection
   of module configuration drift.

4. **`vigia/core/narrative_auditor.py`** (283 lines) — C3 multi-agent narrative
   injection validator (OWASP LLM 2025 taxonomy + Carnegie patterns). Zero
   production callers. `scripts/run_demo.py` loads dynamically from DIFFERENT
   paths (`scripts/narrative_auditor.py`, `scripts/vigia_prod/security/
   narrative_auditor.py`) that do NOT resolve to this file.

**Abduction infrastructure:**

5. **`vigia/core/peirceplanner_bounded.py`** (375 lines) — Miller's Law (7+2)
   bound on abductive reasoning + oscillation detection (A->B->A -> ABSTAIN).
   Needs `AbductiveHypothesis` with `ockham_cost` from `hypothesis_lineage.py`
   (orphaned). Without this, nothing prevents unbounded/oscillating abduction
   in the live planner.

6. **`vigia/core/advanced_signal_router.py`** — Signal routing by artifact type.
   Conceptually superseded by the scorer's inline `evidence_type` lookup in
   `effective_trusts`, but not confirmed identical in behavior. Zero callers.

### Why not wired today (same pattern as B-123)

All 6 depend on inputs that do not exist in the current pipeline or corpus:
- Ockham needs hypothesis costs from the orphaned abduction namespace
- Dissent needs results from ALL governance modules (circular dependency)
- Config sentinel monitors modules that are themselves not wired
- Narrative auditor is unreachable from any production path
- PeircePlanner bounded needs the orphaned hypothesis lineage tracker
- Signal router is conceptually superseded

A dry-run is inviable: without real input data, every module would operate
on defaults or empty inputs, producing no meaningful impact measurement.

### Decision

All 6 preserved as pending-to-wire capability. NOT candidates for deletion
(real forensic logic, Fraction arithmetic, doctrinally correct). Blocked by
the same orphaned producer chain as B-123 (vigia/abduction/, vigia/temporal/,
vigia/patterns/). The full unblocking roadmap is:

1. Wire `vigia/abduction/` namespace (hypothesis_lineage, artifact_graph,
   counter_fact) — unblocks ockham_adversarial + peirceplanner_bounded
2. Wire CCS producers (B-123) — unblocks causal_closure gate
3. Wire governance modules in order: ockham -> dissent -> config_sentinel
4. Wire narrative_auditor as C3 validation step before bundle sealing

### Update 2026-07-25 — confirmado con ejecución: el hueco de `adversarial_penalty`
no es solo "no cableado", cambia el estado emitido

Continuación de la auditoría "Ronda 2" (ver B-217/B-221): investigando por qué
`vigia_scorer.py:1931` (`_apply_quadripartite`) pasa `dissent_info={}` (F1,
B-217), noté que la misma llamada también hardcodea `pivot_signals=[]`,
`investigation_roadmap=[]` y `adversarial_penalty=False` — los tres son
literales en `_apply_quadripartite` (línea ~503), no vienen de ningún cálculo
en `vigia_scorer.py`. `pivot_signals`/`investigation_roadmap` son datos de
display puro (alimentan el reporte del analista vía
`QuadripartiteClassifier._build_verdict` → `render_for_report`) — su ausencia
degrada el reporte a "see roadmap" pero no cambia ningún veredicto.

`adversarial_penalty`, en cambio, **sí gatea una rama activa** (Check 6,
`quadripartite.py` línea ~375): con `adversarial_penalty=True`, un veredicto
BENIGN recibe +5% de confianza efectiva (el bono existe precisamente porque
el sistema evaluó y descartó la hipótesis-demasiado-simple, según el
principio de `ockham_adversarial.py`). Confirmado por ejecución directa
contra `QuadripartiteClassifier.classify()`:

```
BENIGN, confidence=78%, stability=100%
  adversarial_penalty=False (estado real hoy) -> BENIGN_MEDIUM, confidence=78%
  adversarial_penalty=True  (si ockham estuviera cableado) -> BENIGN_HIGH,  confidence=83%
```

El +5% cruza el umbral HIGH/MEDIUM (80%) en este ejemplo — no es un ajuste
cosmético, cambia el `VerdictState` emitido. Como `ockham_adversarial.py`
tiene cero *callers* en todo el repo (confirmado por grep exhaustivo,
incluyendo tests — ni siquiera hay un test unitario de este módulo), la rama
`adversarial_penalty=True` de `_build_verdict`/Check 6 es alcanzable en el
código pero **inalcanzable en la práctica**: nada en el pipeline vivo puede
producir ese `True` hoy. Mismo patrón que F1 (B-217): una rama de decisión
correctamente implementada y con su propio test de branch, pero con el único
insumo que la activaría hardcodeado a un valor fijo en el único *caller* de
producción.

No se abre como bug nuevo — es la misma causa raíz ya documentada en este
B-124 (cadena de productores huérfanos en `vigia/abduction/`), solo que ahora
con la consecuencia concreta verificada por ejecución en vez de deducida.
Queda como evidencia adicional para priorizar el paso 3 del roadmap de
desbloqueo ("Wire governance modules in order: ockham -> dissent ->
config_sentinel") si se decide continuar esa vía.

### Update 2026-07-25 (bis) — `config_sentinel.py`: si se cableara hoy tal
cual está, mentiría sobre los dos módulos críticos que ya sabemos rotos

Continuando la excavación del cluster B-124, leí `ConfigAuditMonitor`
completo. Su propósito declarado es exactamente detectar esto: "Módulos
críticos desactivados al inicio" y sellar un `analyst_warning` en el bundle
si `CAIE`, `TrustFusion`, `OckhamAdversarial` o `SignalRouter` (su propio
`CRITICAL_MODULES`) están inactivos. Pero su `_MODULE_ENV_MAP` mapea cada
módulo a una variable de entorno que el monitor mismo lee — y de las 9
variables mapeadas, **7 no se leen en ningún otro lugar del repositorio**
(confirmado por grep exhaustivo, excluyendo tests y el propio
`config_sentinel.py`): `VIGIA_OCKHAM_ADVERSARIAL`,
`VIGIA_SIGNALROUTER_ENABLED`, `VIGIA_PDF_ENABLED`, `VIGIA_NETWORK_ENABLED`,
`VIGIA_REGISTRY_ENABLED`, `VIGIA_EMAIL_ENABLED`, `VIGIA_TEMPORAL_ENABLED`.
Solo `VIGIA_CAIE_ENABLED` y `VIGIA_TRUST_FUSION_ENABLED` gatean algo real.

`_getenv_bool` por diseño devuelve `True` (activo) cuando la variable no
está seteada — `NOT_SET` se interpreta como "activo por default", lo cual
tiene sentido SI la variable realmente controlara el módulo. Pero como
`VIGIA_OCKHAM_ADVERSARIAL` y `VIGIA_SIGNALROUTER_ENABLED` no controlan nada
(ya sabemos por este mismo B-124 que `ockham_adversarial.py` tiene cero
*callers* y que `advanced_signal_router.py` está "conceptualmente
superseded"), el monitor reportaría "activo" para exactamente los dos
módulos críticos que están completamente desconectados del pipeline vivo.

Ejecutado directamente contra `ConfigAuditMonitor` con el entorno limpio
(sin ninguna de las 9 variables seteada — el caso normal, porque nadie las
documenta):

```
integrity_level: FULL_INTEGRITY
analyst_warning: None

OckhamAdversarial    active=True  env_var=VIGIA_OCKHAM_ADVERSARIAL  env_value=NOT_SET
SignalRouter         active=True  env_var=VIGIA_SIGNALROUTER_ENABLED  env_value=NOT_SET
```

Un "guardián de configuración" que reporta `FULL_INTEGRITY` y "activo" para
los dos módulos que su propio archivo hermano (este B-124) documenta como
completamente huérfanos no es solo "no cableado" — si se cableara sin
corregir primero el `_MODULE_ENV_MAP`, daría falsa tranquilidad exactamente
donde el sistema está más roto. Mismo patrón epistemológico que "ataques
contra el auditor" (ver B-219): un mecanismo que, lejos de fallar
ruidosamente, produciría un reporte sellado que dice "todo bien" sobre un
módulo ausente.

No se abre como bug nuevo — sigue siendo parte de la causa raíz de B-124
(cadena de dependencias huérfanas), pero el fix correcto para
`config_sentinel.py` ya no es solo "cablearlo": `_MODULE_ENV_MAP` tiene que
reflejar cómo cada módulo se activa realmente (para `OckhamAdversarial` y
`SignalRouter`, hoy eso sería "nunca, porque no tienen *caller*", no una
variable de entorno que nadie lee) antes de que el monitor pueda ser
confiable. Verificado con test permanente:
`tests/test_config_sentinel_orphaned_module_env_map.py`.

---

## B-129 — PeircePlanner bounded: Fase 1 observation adapter [PENDIENTE Fase 2]

| Campo | Valor |
|-------|-------|
| **Estado** | FASE 1 COMPLETADA — pendiente Fase 2 (calibracion) y Fase 3 (integracion) |
| **Severidad** | P3 (no afecta veredictos, modulo de observacion) |
| **Archivos** | `vigia/core/planner_adapter.py` (nuevo), `vigia/core/peirceplanner_bounded.py` (existente) |
| **Detectado en** | Investigation 2026-07-14 |

### Description

Adapter that translates VIGIA case artifacts into EvidenceSignal and
Hypothesis objects for run_bounded_planner(). Output is observation-only
— does NOT feed the scorer or verdict path.

### Investigation findings

1. AbductiveIntentEngine (vigia/inference/) is partially wired (L-027)
   but its HYPOTHESIS_TEMPLATES require MITRE artifact names that real
   cases do not have. Translation layer never written.
2. peirceplanner_bounded and AbductiveIntentEngine are compatible with
   a ~15 line adapter (cost:int -> ockham_cost:Fraction).
3. Both share the same unwired gap (L-027).

### Observation baseline (198/199 cases)

- Agreement with scorer: 22% (44 cases) — severely miscalibrated
- Under-alerts (planner NOISE, scorer SUSPICION+): 90 cases
- Root cause: confidence-as-weight is wrong indicator (measures
  certainty, not anomaly severity). z_score or raw_score better.

### Pending (Fase 2 — calibration, NOT before 2026-08-14)

1. Calibrate weight: experiment with z_score, raw_score * (1 - spoofability),
   or a composite
2. Resolve L-027 or bypass with generic hypotheses (not MITRE-specific)
3. Re-run against corpus, target >70% agreement before considering Fase 3
4. 30-day observation period before any gate that moves verdicts

### Pending (Fase 3 — integration, NOT before Fase 2 validated)

1. Architecture decision: parallel signal (like Grice gate) vs replacement
   of classify_agent_verdict vs scorer factor
2. Full corpus dry-run with same rigor as B-126/B-127
3. Oscillation detection is the primary value-add (ABSTAIN for
   contradictory evidence) — focus integration design on that

---

## B-149 — T-5: un IoC de C2 de severidad alta puede colapsar a NOISE cuando el artefacto de memoria exculpatorio nunca fue analizado a nivel red (aflorado por B-148) [ABIERTO — solo sintético]

| Campo | Valor |
|-------|-------|
| **Estado** | ABIERTO — solo sintético (0/201 casos de corpus). Documentado como limitación, no parcheado en silencio. Deliberadamente NO empaquetado dentro de B-148. |
| **Severidad** | P2 (latente) — un IoC de C2 real y corroborado nunca debería leerse como NOISE ("nada que ver acá"). Actualmente reproducible solo sintéticamente. |
| **Archivo** | `vigia_scorer.py` (Noisy-OR ponderado por spoofability / cascada de veredicto); sonda: `vigia/tests/adversarial/test_spoofability_correlation_attack.py::test_red_team_anchor_bypass` (ahora `xfail(strict=True)`) |

**Por qué B-148 lo hizo aflorar.** La regla de fabricación LOG_VS_MEMORY
cumplía doble función: además de detectar fabricación, su disparo sobre
memoria sin red era INCIDENTALMENTE el mecanismo que impedía que un log de C2
de alta spoofability colapsara a NOISE. B-148 correctamente detiene el disparo
por ausencia (era un falso positivo), lo que remueve esa protección
incidental. Medido post-B-148: un IoC de C2 (`raw_score=0.95`, `log_entry`) +
un artefacto de memoria exculpatorio NO ANALIZADO a nivel red sin `verdict`
explícito → **veredicto = NOISE** (`test_red_team_anchor_bypass`), mientras
que con un artefacto exculpatorio de veredicto explícito se sostiene en
SUSPICION (`test_metadata_convention...`, ahora un pass de contradicción
genuina).

**Alcance honesto.** El gate de corpus de B-148 muestra que **0/201 casos
reales** exhiben esto — la protección anti-colapso descansaba sobre un falso
positivo, pero ningún caso real dependía de ella tampoco. Así que T-5 es un
comportamiento latente, no una regresión viva de corpus.

**Fix apropiado (diferido, necesita una decisión).** Un IoC de severidad alta,
corroborado independientemente, debe resistir el colapso a NOISE **por sus
propios méritos** — no vía una fractura acoplada a memoria ausente. Es un
cambio a nivel de scorer (p. ej. un piso de IoC que la ponderación por
spoofability no pueda empujar por debajo de SUSPICION), NO un re-acoplamiento
al bug de ausencia que B-148 corrigió. Trackeado por separado para que el fix
correcto se diseñe deliberadamente. Cuando aterrice, el `xfail(strict=True)`
sobre `test_red_team_anchor_bypass` pasa a XPASS y se remueve el marcador.

---

## B-151 — Downgrades del scorer: (a) clamp silencioso de score de artefacto único [RESUELTO, código muerto]; (b) entrada de cadena contradiction_detector mandatada no cableada en Modo-1 [ABIERTO — decisión de arquitectura]

| Campo | Valor |
|-------|-------|
| **Estado** | (a) RESUELTO (2026-07-19) — clamp hecho auditable; además se encontró inalcanzable. (b) ABIERTO — decisión de arquitectura, deliberadamente NO empaquetada con (a). |
| **Severidad** | (a) P3 (divulgación de un clamp de código muerto). (b) P2 (brecha doctrina-vs-implementación). |
| **Archivo** | (a) `vigia_scorer.py` clamp ~1216 + marcador ~1620; (b) `vigia_scorer.py` (sin `ToolExecutionLogChain` en el camino de decisión). |

**(a) Clamp silencioso de score de artefacto único — RESUELTO, con un giro
honesto.** `if n_artifacts < 2 and final_score > 0.65: final_score = 0.65`
reescribía en silencio el score sellado (una reducción de fuerza probatoria
sin razón/marcador, a diferencia de todo otro downgrade de la cascada). Fix:
capturar el score pre-cap y surfacear un marcador
`single_artifact_score_cap` + nota de razón en `base_result`, espejando el
patrón de divulgación `normalization_failures` / `temporal_pairs_skipped`.
Neutro al veredicto (el cap ya aplicaba; la divulgación es aditiva).

**Giro encontrado al verificar: el clamp es actualmente código muerto
INALCANZABLE.** Un artefacto de señal único se suprime a un score máximo de
~0.038 (`cryptographic_hash`, raw 0.99, todos los boosters) — muy por debajo
del cap 0.65 — así que el "downgrade silencioso" que este ítem nombró no es un
riesgo vivo; el clamp es defensivo y el marcador es divulgación prospectiva.
Fijado por `tests/test_b151a_single_artifact_cap.py`: si un artefacto único
alguna vez alcanza un score >= 0.65 el test falla, señalando que el camino del
marcador se volvió vivo. `_dround` devuelve float, así que `final_score` acá
es float por el diseño de redondeo determinista del scorer (no un camino puro
de Fraction) — la asignación `= 0.65` es consistente en tipos, sin inyección
nueva de float.

**(b) Entrada de cadena contradiction_detector no cableada en Modo-1 —
ABIERTO.** El "Self-Correction Event Schema" de CLAUDE.md manda que cada
downgrade dirigido por gate agregue una entrada `contradiction_detector` vía
`ToolExecutionLogChain`. Verificado: `vigia_scorer.py`, `bundle_builder.py`,
`pipeline.py`, `sift_orchestrator.py` contienen **cero** referencias a
`ToolExecutionLogChain` / `contradiction_detector` — el appender se instancia
solo en tests y en un script de red team. Es decir, el camino determinista de
Modo-1 no emite los eventos de auto-corrección a prueba de manipulación
mandatados (la cascada SÍ setea strings `reason` legibles por humanos para 7/8
downgrades — la brecha es el evento *encadenado*, no la razón). Es una
decisión de arquitectura — cablearlo en Modo-1, o enmendar la doctrina para
declarar que el evento de auto-corrección encadenado es una construcción de
Modo-2 (Claude Code) por diseño. Deliberadamente NO corregido como one-liner.
Aún sin decidir.

**Actualización 2026-07-26 — la atribución de arriba quedó OBSOLETA (ver
B-224).** Dos correcciones de hecho, ambas verificadas en vivo:

1. *El cableado existe.* `vigia/core/reasoning_trace.py` implementa el
   mecanismo mandatado, cita B-151b por nombre en su docstring, y está
   cableado en el camino de sellado de `vigia_agent.py` (~2180):
   `build_from_agent_bundle` encadena `pipeline_results["self_corrections"]`
   como entradas `contradiction_detector` vía `ToolExecutionLogChain`.
   Confirmado con una corrida real de Modo-1, que escribe un
   `<stem>_reasoning_trace.json` encadenado y con tail-anchor. La frase "el
   appender se instancia sólo en tests y en un script de red team" ya no es
   cierta.
2. *Lo que falta es el insumo, no el cableado.* B-224 documenta que
   `ContradictionDetector` no puede disparar nunca en Modo-1: 3 de sus 4
   reglas leen campos sin productor (`signal["tool"]`, `technical_result`) o
   una grafía que el vocabulario real nunca usa (`"BENIGN"` vs
   `NO_*_ANOMALY_DETECTED`), y `CONTRADICTION_THRESHOLD = 2` vuelve
   insuficiente a la única regla viva (máximo alcanzable = 1). Es decir, la
   rama de auto-correcciones del trace está vacía **siempre**, por
   construcción — no sólo en casos sin contradicciones.

**Lo que sigue abierto acá (independiente de B-224):** si cada gate del
scorer debe emitir su propio evento encadenado. Nota estructural relevante
para quien lo encare: los gates viven en `vigia_scorer.py`, que
`vigia_agent.py` **no importa** (cero referencias, verificado) — son dos
subsistemas disjuntos, y ningún marcador de gate (`normalization_failures`,
`temporal_pairs_skipped`, `pre_unverified_*_verdict`,
`single_artifact_score_cap`) llega jamás al bundle del agente. Por eso el fix
no es "leer los marcadores en `build_from_agent_bundle`": no hay marcadores
que leer en ese camino. La decisión de arquitectura sigue pendiente.

---

## B-162 — El adaptador legacy borraba silenciosamente un schema de evidencia estructurada sin modelar [REPARACIÓN PARCIAL — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de integridad de evidencia / degradación honesta. |
| **Archivos** | `vigia/pipeline/vigia_integration_bridge.py:_normalize_artifact_legacy`, puerta de normalización de `vigia_scorer.py`. |
| **Detectado por** | Auditoría Codex de `OWL-NEXUS5-CASE`, 2026-07-21. |

El adaptador legacy esperaba `artifact_id`, `forensic_anomalies` y
`analyst_flags`. El escenario OWL usa `id`, `content` estructurado anidado y
tipos mobile/social como `web_search` e `instant_message`. Antes de mapearlos,
los 20 artefactos se convertían silenciosamente en señales con
`artifact_id="?"`, `evidence_type="unknown"` y score cero. La corrida sellaba
`NOISE`, sin un marcador `normalization_failures` ni disposición `ABSTAIN`.

La medición repository-wide encontró 24 artefactos legacy con tipos sin mapear;
20 pertenecen a OWL. Mapear sólo esos nombres de tipo no repara un veredicto:
el adaptador no tiene extractor determinista para la semántica anidada de
mensajes, URLs y cuentas, por lo que cada artefacto sigue con score mínimo y
OWL queda en `NOISE` (score medido `0.0627`). Convertir prosa del escenario como
`metadata.significance` en anomalía o score haría autoritativa una narrativa
redactada, reabriendo la clase fuga de etiqueta / aserción del examinador.

**Reparación aplicada:** el normalizador conserva `id` como `artifact_id`,
reconoce la taxonomía mobile/social sólo como clase de colección y adjunta
`structured_content_without_semantic_extractor` cuando el contenido estructurado
carece de un extractor determinista. La puerta existente convierte el resultado
que habría sido `NOISE` en `ABSTAIN`. Ni `metadata.significance`, ni el texto de
la narrativa, ni `expected_verdict` pasan a ser inputs de score.

**Validación:** los tests red-first comprueban que el ID y la clase
`instant_message` se preservan, que el caso mínimo termina en `ABSTAIN` con el
marcador exacto de pérdida y que cambiar el label esperado entre `SUSPICION` y
`MALICE` no cambia ningún artefacto normalizado.
`tests/test_b162_structured_legacy_degradation.py`,
`tests/test_label_leak_normalize_case_schema.py`,
`tests/test_b066_b067_mobile_whitelist.py`,
`tests/test_p1_metadata_normalization_integrity.py` y
`tests/test_b6_artifact_type_map_consistency.py`: **58 passed**. Una ejecución
real de `vigia_agent.py` sobre el JSON OWL, en un bundle temporal con checksum y
reasoning trace válidos, cambió de `NOISE` a **`ABSTAIN`** (`motor_score=0.0627`)
sin elevar la prosa a evidencia.

**Residual abierto:** esto resuelve la salida falsamente limpia, no extrae el
significado forense de un chat, URL o cuenta anidados. Un extractor específico
para Android/Chrome/Musical.ly deberá trabajar sobre artefactos raw con hash y
provenance antes de que VIGÍA pueda derivar una puntuación o `SUSPICION` propia.

**Confirmación cross-mode, sin autoridad de veredicto (2026-07-21):** los
work-products preservados en
`results/OWL-NEXUS5-CASE_{report,bundle}_claude*` y
`results/OWL-NEXUS5-CASE_{report,bundle}_chatgpt.*` verifican sus checksums y
coinciden en que el `NOISE` legacy no describe adecuadamente la evidencia
recuperada. El v1 de Claude recorrió la extracción con 29 llamadas MCP y
ChatGPT hizo una revisión read-only manual de la imagen. El v2 de Claude
rectificó el alcance: un SMS de entrega estaba fuera de la primera consulta y
el Windows/Pidgin companion queda **UNRESOLVED**, no descartado. Conserva
`SUSPICION`, no `INTENT`/`MALICE`, porque el vínculo cross-device no fue
materializado. No son una regresión del motor ni una fuente de score: difieren,
por ejemplo, sobre qué texto de mensajes puede recuperarse y qué significa el
segundo dispositivo. Esa discordancia queda preservada, y refuerza que VIGÍA
debe seguir emitiendo `ABSTAIN` hasta que un extractor determinista,
source-specific y hash-bound materialice los hechos que pretende puntuar.

---

## B-215 — `evidence_graph` no se puebla en bundles de `run_full`: `graph_hash` idéntico en todos los casos (ancla de integridad vacía de significado) [DOCUMENTADO — Claude 2026-07-23]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (integridad Daubert): `graph_hash` debería ligar el bundle al grafo de evidencia específico del caso; si es constante, no ancla nada. `decision_hash` sí es case-specific y estable, así que la reproducibilidad del veredicto no está comprometida — pero un verificador que confíe en `graph_hash` como prueba de integridad del grafo está confiando en un valor vacío. |
| **Archivos** | `vigia/core/bundle_builder.py` (`graph_hash = _sha256_dict(evidence_graph.to_dict())`), `vigia/pipeline/pipeline.py` (construcción del `ForensicBundle` en `run_full`). |
| **Modo** | Bundles sellados vía `run_full`. |
| **Detectado por** | Verificación empírica de 4 bundles `_claude_fable` (sesión 2026-07-23). |

**Observación reproducida:** OWL-NEXUS5 (22 artefactos), MAGNET-2022-iOS-JESS (6),
OWL-COMPLETE (30) y FLAREON-2017 (14) — contenido y tamaño totalmente distintos —
producen el **mismo** `graph_hash` `94147b51c639cd0c...`. El `decision_hash`, en
cambio, difiere en los cuatro (`1fc52828` / `aa91ab1e` / `617cd69c` / `3e08cb52`).

**Causa raíz (Secondness):** `graph_hash` = SHA-256 de `evidence_graph.to_dict()`
menos `graph_hash`/`generated_at`. Que sea constante implica que el
`evidence_graph` del `ForensicBundle` construido por `run_full` está vacío o en un
default constante — no se lo puebla con los nodos/edges derivados de las señales
del caso. El grafo de evidencia (artefacto de cadena causal relevante para
Daubert) no está en el bundle.

**Fix propuesto (NO aplicado):** poblar `evidence_graph` en `run_full` con los
nodos de señal y sus relaciones antes de computar `graph_hash`; agregar un test
que asserte `graph_hash` distinto entre dos casos con artefactos distintos
(rojo-primero contra el estado actual). Requiere revisar qué consume
`evidence_graph` aguas abajo para no romper `verify_ebs_v1.py`.

**Hallazgos relacionados (NO bugs, registrados para no re-descubrirlos):**
(1) `bundle_hash` embebe `bundle_id` (UUID aleatorio) + timestamp y varía por
sello — es **intencional** y documentado en `bundle_builder.py:171` ("bundle_hash
is intentionally an identity for a specific custody event"); el ancla de
determinismo es `decision_hash`, no `bundle_hash`. (2) `ecl_hash` nunca se puebla
en bundles de `run_full`, así que `verify_ebs_v1.py` reporta `R5_ECL_BINDING`
WARN y topa en Level 2 — Level 3 requiere cablear el Evidence Chain Ledger
(`VIGIA_CHAIN_DB_PATH`), pendiente de integración; no es un fallo, es una feature
de Level 3 no conectada a este entry point.

## B-221 — Auditoría "Ronda 2" (invariantes epistemológicos): vectores investigados y descartados — registrados para no re-descubrirlos [DOCUMENTADO — Claude 2026-07-25]

| Campo | Valor |
|-------|-------|
| **Severidad** | N/A — no son bugs. Documentado como referencia de auditoría, no como defecto. |
| **Archivos** | `vigia/core/risk_bounded_layer.py` (`PolicyStabilityController`), `vigia/core/dissent_report.py` (`_compute_majority`, tie-break), `vigia/core/trust_fusion.py` (`NeighborhoodContext.mean_neighbor_trust`, `TrustFusionEngine.calculate_likelihood`, `add_artifact`). |
| **Método** | A-D-I (Abductivo-Deductivo-Inductivo): cada vector se ejecutó contra el código vivo antes de aceptarlo o descartarlo, no solo se dedujo. |
| **Detectado en** | Auditoría "Ronda 2", sesión 2026-07-25, re-verificado independientemente en esta sesión (no se aceptó ningún resultado del reporte pegado sin re-ejecutarlo). |

### Descripción

Cinco vectores se investigaron durante la auditoría "Ronda 2" y no se
convirtieron en bugs. Se documentan aquí explícitamente para que una
auditoría futura no vuelva a gastar tiempo re-descubriéndolos:

**1. F5 — `PolicyStabilityController`: ¿diverge el resultado entre la rama
numpy (`np.linalg.norm` + `np.array`) y el fallback stdlib (`math.sqrt` +
listas)?** FALSIFICADO. Hipótesis original (deducida, no ejecutada): el
veredicto podría depender silenciosamente de si `numpy` está instalado.
Re-ejecutado en esta sesión, forzando ambas ramas sobre la misma secuencia de
`stabilize()`: los tres parámetros resultantes (`lambda, gamma, epsilon`) son
**bit-idénticos** entre ambas rutas (`0x1.b851eb851eb85p+1` en ambos casos,
verificado con `.hex()` de float). Las dos ramas son aritméticamente
equivalentes para esta operación; la divergencia BLAS que motivó la
hipótesis es teórica para este caso, no demostrada. Se retira como hallazgo.

**2. Tie-break de `_compute_majority` favorece MALICIOUS ante empate.** NO
ES BUG. El desempate hacia el veredicto más severo ante un empate exacto de
votos es determinista y *fail-safe* — es la política correcta para un
sistema forense: ante incertidumbre genuina entre dos veredictos igual de
votados, escalar es más defendible que promediar hacia abajo.

**3. `NeighborhoodContext.mean_neighbor_trust` devuelve `1.0` cuando no hay
vecinos — ¿es "ausencia de evidencia tratada como confianza perfecta"?**
FALSIFICADO como riesgo de score. Verificado contra el código vivo:
`TrustFusionEngine.calculate_likelihood` hace *short-circuit* a `return 0.5`
cuando `neighborhood.neighbor_count == 0`, **antes** de leer
`mean_neighbor_trust` — el valor `1.0` nunca llega a participar del cálculo
de `likelihood`/`posterior`. El `1.0` sí aparece en el texto de la razón
narrativa (`BOOST: trust vecindad={neighborhood.mean_neighbor_trust:.3f}`)
en casos donde sí hay vecinos, así que no hay ninguna ruta donde el default
de "sin vecinos" se cuele en un score. Riesgo real: ninguno confirmado.

**4. `add_artifact` deduplica silenciosamente IDs duplicados.** Higiene, no
bug de severidad. `add_artifact` devuelve `False` sin excepción ni registro
cuando `artifact.artifact_id` ya existe (`trust_fusion.py`, línea ~207) — dos
artefactos con el mismo ID colapsan a uno sin aparecer en ningún
`rejected_details` o estructura equivalente. El comportamiento en sí es
deseable (protege contra doble conteo), pero es invisible: nada en el output
de `TrustFusionEngine` le dice a un perito que un artefacto fue descartado
por duplicado. Ticket menor, no bloqueante — no se abre como bug numerado
independiente porque no afecta ningún veredicto, se deja registrado aquí.

### Nota de proceso

Esta auditoría se hizo con disciplina A-D-I explícita después de una primera
pasada (B-217 a B-220 más este bloque) que había *deducido* algunos hallazgos
sin ejecutarlos. La re-verificación con inducción cambió el resultado: F1 se
agravó (se demostró que la cadena completa está muerta, no solo que el
módulo estaba huérfano), F2 y F4 bajaron de severidad al descubrirse sus
precondiciones dormidas, y F5 se retiró por completo al ejecutarlo y
encontrar resultados bit-idénticos. Se documenta el proceso, no solo el
resultado, porque el proceso es replicable: cualquier hallazgo futuro de este
tipo debe pasar por la misma re-verificación contra el código vivo antes de
aceptarse como confirmado.


## B-223 — `generate_execution_log.py` sella una entrada `RISK_CALCULATION` con la fórmula y variables de un motor de decisión distinto al que realmente usa, con D/S/I fabricados [DOCUMENTADO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (integridad de audit trail — el script genera "Agent Execution Logs... para los entregables SANS" según su propio docstring; no es un generador sintético/demo). |
| **Archivo** | `vigia/scripts/generate_execution_log.py` (función `process_case`, líneas ~142, ~218-230). |
| **Detectado en** | Barrido de la fórmula pre-B-117 invertida (2026-07-26, ver addendum de B-117 en `BUGS_HISTORICO.md`) — este fue el único de 9 lugares encontrados que NO se corrigió como un simple string desactualizado, porque el problema es más profundo. |

### Descripción

`process_case()` llama a `dec = decide(det, agg)` (línea 142), donde
`decide` es `vigia.core.decision_layer.decide()` — el motor de decisión
basado en umbrales de MI (`mi >= self.low/medium/high` → LOW/MEDIUM/HIGH/
CRITICAL) que se trabajó en esta misma sesión para B-219. Esta función
**no calcula** `D` (drift), `S` (graph stability), ni `I` (consistency) —
esos conceptos no existen en su modelo.

Sin embargo, el log `RISK_CALCULATION` que este script emite por cada caso
(línea 218-230) está formateado para el OTRO motor de decisión
(`risk_bounded_layer.RiskBoundedDecisionLayer`, el usado por `run_full`/EBS
v1), con:

```python
formula="r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))",
variables={
    "P": round(mi_float, 8),
    "D": 0.1,                                  # hardcodeado
    "S": round(1.0 - mi_float * 0.2, 8),       # fórmula ad-hoc, no del motor real
    "I": round(min(0.95, mi_float + 0.05), 8), # fórmula ad-hoc, no del motor real
},
```

`P` es en realidad `mi_float` (el manipulation index del otro sistema, no
un posterior de fabricación). `D=0.1` es un valor constante hardcodeado sin
relación con ningún drift medido. `S` e `I` se derivan con fórmulas
inventadas para esta ocasión (`1.0 - mi_float*0.2`, `min(0.95, mi_float +
0.05)`) que no corresponden a ningún cálculo de `graph_stability` ni
`consistency_score` reales — no existen en el camino de decisión que este
script efectivamente ejecuta.

### Impacto

Un examinador leyendo un Agent Execution Log JSONL generado por este script
vería una entrada `RISK_CALCULATION` con una fórmula y cuatro variables
(P/D/S/I) que dan la impresión de ser el cálculo real de riesgo que decidió
el veredicto — pero tres de las cuatro variables (D, S, I) son sintéticas,
inventadas para rellenar un schema de log que no corresponde al motor de
decisión realmente usado. Esto es más serio que un signo invertido en una
fórmula (que es "el mismo modelo, mal etiquetado"): acá es "un modelo
diferente, con datos fabricados, presentado como si fuera el real" —
exactamente el tipo de discrepancia entre "lo que el sistema hizo" y "lo
que el sistema dice que hizo" que la doctrina de audit trail de VIGÍA
(`docs/ENGINEERING_DISCIPLINE.md`, `CLAUDE.md`) existe para prevenir.

### Por qué no se corrigió en el momento

Arreglar solo el signo de la fórmula (`(1-P)` → `P`) sería cosmético y
daría falsa confianza — el problema de fondo (el log describe un modelo que
el script no usa) seguiría intacto. Un fix real requiere decidir qué debe
loguear `RISK_CALCULATION` para un caso resuelto vía `decision_layer.decide()`
— por ejemplo, un schema de log distinto para el motor MI-based (sin
D/S/I fabricados), o mapear explícitamente MI a un P/D/S/I real si el
script debería estar usando `risk_bounded_layer` en su lugar. Ninguna de
las dos opciones es un one-liner; ambas son decisiones de diseño que no
corresponde tomar sin más contexto sobre qué consumidor final lee estos
logs y qué garantías espera de ellos.

### Verificación hecha antes de documentar

Confirmado por lectura del import y la llamada real (`decide(det, agg)` en
`vigia.core.decision_layer`, no `RiskBoundedDecisionLayer`), y por lectura
completa de `decision_layer.py` (ya auditado a fondo en esta sesión para
B-219): no tiene ningún parámetro ni cálculo de D, S, o I. Test permanente
(documentando el estado, no un fix): `tests/test_b117_stale_formula_sweep.py`
tiene esta ruta en su allowlist con la justificación completa, y falla si
alguien intenta "arreglarla" con un simple cambio de signo sin actualizar
el test — forzando a que cualquier fix futuro pase por esta misma
investigación.

### Fix propuesto (NO aplicado)

Decisión de arquitectura pendiente: (a) diseñar un schema `RISK_CALCULATION`
propio para el motor MI-based que no invente D/S/I, o (b) auditar si este
script debería estar llamando a `risk_bounded_layer.RiskBoundedDecisionLayer`
en lugar de `decision_layer.decide()` para casos donde se necesite el
modelo P/D/S/I completo. Requiere entender primero quién consume estos
logs JSONL y con qué expectativa de schema.

---

## B-224 — El loop de auto-corrección de Modo-1 es estructuralmente inerte: 3 de 4 reglas de `ContradictionDetector` leen campos que ningún productor escribe, y el umbral vuelve insuficiente a la única regla viva [DOCUMENTADO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 (doctrina-vs-implementación + bandera de compliance). La auto-corrección es presentada como diferenciador central: `vigia_agent.py --help` dice "Self-correction: automatic — no flags needed" y "Max iterations: 3", y `CLAUDE.md` afirma que "la auto-corrección de VIGÍA ocurre pre-emisión". En Modo-1 no ocurre nunca. |
| **Archivos** | `vigia_agent.py` — `ContradictionDetector.detect()` (líneas 451-528), `CONTRADICTION_THRESHOLD = 2` (línea 55), `_apply_self_correction` (guard en ~813), bandera `sans_compliance.self_correction` (~1398). |
| **Detectado en** | Investigación del resto abierto de B-151(b) (2026-07-26). Medido sobre los 21 casos del corpus + prueba directa de alcanzabilidad por regla. |

### Descripción

`ContradictionDetector.detect()` implementa 4 reglas. Tres no pueden matchear
ninguna entrada, porque leen campos que ningún camino de producción escribe:

**Regla 1 — ENTROPY_VS_BEHAVIORAL.** Filtra por `signal["tool"] in
("memory_forensics", "disk_forensics")` y `signal["tool"] ==
"behavioral_fingerprint"`. Las señales de Modo-1 no tienen clave `tool`:
llevan `evidence_type` y `source`. Medido: **196 de 196 señales** en los 21
casos del corpus tienen `tool=None`. Verificado que la lógica de la regla en
sí funciona — el mismo escenario con `tool` en lugar de `source` dispara
correctamente (test de control incluido).

**Regla 2 — SEMIOTIC_VS_TECHNICAL.** Lee
`module_results["technical_result"]["alert_level"]` y requiere `HIGH`/
`CRITICAL`. `technical_result` y `semiotic_result` se **leen** en
`vigia_agent.py:464-465` y se **escriben en ningún lugar del repositorio** —
confirmado por grep exhaustivo sobre todos los `*.py`, incluyendo `tests/`.
El default `.get(..., "LOW")` gana siempre, y `"LOW"` no está en
`("HIGH", "CRITICAL")`.

**Regla 4 — VERDICT_FLIP.** Requiere `"BENIGN" in
best_hypothesis.upper()`. El vocabulario completo que el productor emite
(`vigia/inference/abductive_reasoner.py` + `vigia_agent.py`) es:
`UNDETERMINED`, `REASONER_ERROR`, `ABSTAIN_V2`, `MALICIOUS_INTENT_DETECTED`,
`INTENT_DETECTED`, `SUSPICION_DETECTED`, `NO_ANOMALY_DETECTED`,
`NO_SEMIOTIC_ANOMALY_DETECTED`, `PIPELINE_ERROR`. **Ninguno contiene
"BENIGN"** — Modo-1 escribe "benigno" como `NO_*_ANOMALY_DETECTED`. El propio
`vigia_agent.py:164` documenta que ambas grafías existen
("`NO_*_ANOMALY_DETECTED`, `BENIGN`"), pero la regla sólo chequea una.
Verificado que la lógica funciona: con el literal `"BENIGN"` dispara.

Queda la **Regla 3 (CONFIDENCE_COLLAPSE)** como única alcanzable, y agrega a
lo sumo **una** contradicción. `CONTRADICTION_THRESHOLD = 2` gatea la
corrección con `len(contradictions) >= 2`:

```python
if len(contradictions) < CONTRADICTION_THRESHOLD:
    ...
    return False, results          # sin corrección
```

Máximo alcanzable = 1 < 2. Por lo tanto `_apply_self_correction` retorna
`(False, results)` **para toda entrada posible** — no "ninguna en este
corpus", sino ninguna nunca.

### Impacto

Estructural, no dependiente del caso:

- `self_corrections_applied` es siempre `0` e `iterations_executed` siempre
  `1` — el loop de auto-corrección documentado como "max 3 iterations" no
  itera nunca. Medido: 21/21 casos.
- `sans_compliance.self_correction` (`= self.iteration > 0 or
  len(self.corrections_applied) > 0`) sólo puede ser `False`. Medido: 21/21
  `False`. Es particularmente sensible porque esa bandera fue introducida
  explícitamente como "FIX P1-5: real verifications instead of hardcoded True
  flags" — es una verificación real que reporta, correctamente, que algo no
  pasó; el problema es que no puede pasar.
- `contradictions_found = 0` en 21/21 casos del corpus, leído de los
  `audit_trail` de corridas reales (no de una simulación): ni siquiera llega
  al umbral, es cero absoluto.
- El evento encadenado `contradiction_detector` que manda el "Self-Correction
  Event Schema" de `CLAUDE.md` no puede ser emitido nunca por Modo-1.

### Relación con B-151(b) — su atribución quedó obsoleta

B-151(b) atribuye la ausencia de ese evento a que el cableado falta
("`vigia_scorer.py`, `bundle_builder.py`, `pipeline.py`,
`sift_orchestrator.py` contienen **cero** referencias a
`ToolExecutionLogChain` / `contradiction_detector` — el appender se instancia
sólo en tests y en un script de red team"). **Esa atribución es obsoleta.**
`vigia/core/reasoning_trace.py` implementa el mecanismo, cita B-151b por
nombre en su docstring, y está cableado en el camino de sellado de
`vigia_agent.py` (~2180): `build_from_agent_bundle` encadena
`pipeline_results["self_corrections"]` como entradas
`contradiction_detector`. Verificado en vivo: una corrida real de Modo-1
escribe un `<stem>_reasoning_trace.json` encadenado y con tail-anchor.

Es decir: **el cableado existe y funciona; lo que no existe es el insumo.**
La causa real está aguas arriba de donde B-151(b) la ubica. Nótese también
que `BUGS_HISTORICO.md` (entrada de la Fase 1.5 del reasoning trace) describe
el trace como "delgado (calidad MINIMAL)" para "casos sin nada de lo último" —
tratándolo como dependiente del caso. Con este hallazgo, la rama de
auto-correcciones del trace está vacía **siempre**, por construcción.

El resto legítimamente abierto de B-151(b) (¿debe cada gate del scorer emitir
un evento encadenado?) sigue abierto y es independiente de esto: los gates
viven en `vigia_scorer.py`, que `vigia_agent.py` **no importa** (cero
referencias, verificado) — son dos subsistemas disjuntos, y ningún marcador
de gate llega jamás al bundle del agente.

### Verificación hecha antes de documentar

Inducción sobre el sistema vivo, no deducción:

1. Corridas reales de `vigia_agent.py` sobre los 21 casos de `cases/input/`:
   `self_corrections_applied=0`, `iterations_executed=1`,
   `sans_compliance.self_correction=False`, y `contradictions_found=0` leído
   de cada `audit_trail`.
2. Inventario de claves de señal sobre las 21 corridas selladas: 196 señales,
   `tool=None` en todas; claves reales
   `{artifact_id, confidence, description, evidence_type, source, z_score}`.
3. Grep exhaustivo: `technical_result` / `semiotic_result` sin productor en
   ningún `*.py` del repo.
4. Enumeración del vocabulario de `best_hypothesis` en el código del
   productor (no sólo en el corpus) — sin ningún literal con "BENIGN".
5. Prueba directa de alcanzabilidad por regla, alimentando a `detect()` con
   escenarios construidos para disparar cada regla usando las formas de datos
   **reales**: reglas 1, 2 y 4 devuelven `[]`; regla 3 devuelve 1; el máximo
   apilando todo a la vez es 1, contra umbral 2.
6. Tests de control (positivos) que prueban que la lógica de las reglas 1 y 4
   funciona y que sólo el nombre de campo / la grafía están desalineados —
   para no confundir "regla inalcanzable" con "regla incorrecta".

Fijado por `tests/test_b224_contradiction_detector_dormancy.py` (10 tests).
Todas sus aserciones documentan el **estado roto actual**, no el deseado: van
a FALLAR cuando alguien cablee un productor o alinee el vocabulario, que es
justamente el punto.

### Fix propuesto (NO aplicado)

No aplicado porque **toda opción posible afecta veredictos** y requiere
re-validación del corpus más sign-off de Anna. Una corrección viva reescribe
`abduction["best_hypothesis"]` (ver `_apply_self_correction`, acciones
`OVERRIDE_ABDUCTIVE_CONCLUSION` / `ESCALATE_TO_CRITICAL`), así que revivir
cualquier regla puede mover veredictos sellados sobre casos reales del corpus.

Además hay una interacción que hace que los arreglos parciales no sirvan:
revivir **una sola** regla deja el máximo en 1, todavía < 2, y no cambia
nada. Un fix real requiere decidir en conjunto:

- (a) Alinear la regla 1 con las claves reales (`evidence_type` / `source`) —
  requiere definir qué valores de `evidence_type` cuentan como
  memoria/disco y cuál es el equivalente real de `behavioral_fingerprint`.
- (b) Alinear la regla 4 con el vocabulario real
  (`NO_*_ANOMALY_DETECTED` además de `BENIGN`).
- (c) Decidir si la regla 2 debe tener un productor (`technical_result`) o si
  debe eliminarse como concepto muerto.
- (d) Revisar `CONTRADICTION_THRESHOLD = 2` a la luz de cuántas reglas quedan
  realmente vivas: con 4 reglas nominales el umbral 2 era plausible; con 1
  viva es una condición imposible.
- (e) Alternativa honesta si no se quiere tocar el scoring: documentar la
  inercia en `KNOWN_LIMITATIONS.md` y ajustar `--help` / `CLAUDE.md` para no
  presentar la auto-corrección de Modo-1 como activa. Bajo la doctrina de
  degradación honesta (§5.3 de `docs/ENGINEERING_DISCIPLINE.md`), declarar
  una capacidad inerte es peor que declararla ausente.

También conviene notar que el docstring de `ContradictionDetector` enumera 5
tipos de contradicción pero sólo implementa 4 — `TEMPORAL_VS_CONTENT`
(listado como #1) no existe en el código.
