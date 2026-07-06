# Auditoría de Seguridad — Sellado del Veredicto, Filtro Eco, Protocolo de Refutación y Escrituras Atómicas

**Fecha:** 2026-07-06 (revisada tras inducción experimental)
**Alcance:** cuatro vías de ataque sobre el núcleo forense determinista de VIGÍA.
**Base:** rama `claude/sealed-verdict-security-najnug` sobre `main`.
**Evidencia reproducible:** `scratchpad/q2_induction.py` (Q2), suite de tests (Q4).

---

## Nota epistemológica (obligatoria — método peirceano)

Una **abducción plausible no es un hallazgo confirmado.** En VIGÍA el razonamiento
debe recorrer la cadena completa: Firstness → Secondness → Thirdness, y
Abducción → Deducción → **Inducción** (intentar falsar las predicciones y verificar
si ocurren). Sin la etapa inductiva, el máximo nivel afirmable es *"hipótesis
plausible con evidencia arquitectónica"*, no *"CONFIRMADO"*.

Cada hallazgo de este documento lleva su nivel epistemológico explícito:

| Etiqueta | Significado |
|----------|-------------|
| **HECHO DE CÓDIGO** | Observación directa y verificable del fuente (no requiere inducción). |
| **CONFIRMADO POR INDUCCIÓN** | Predicción deducida, ejecutada experimentalmente y observada. |
| **FALSADO** | Predicción ejecutada que NO ocurrió — la hipótesis se rechaza. |
| **HIPÓTESIS PLAUSIBLE** | Abducción con evidencia arquitectónica, sin inducción ejecutada. |

> **Corrección respecto de la versión inicial de esta auditoría:** la v1 marcó Q2 como
> "EXPLOTABLE — CONFIRMADO" sobre evidencia arquitectónica, con el vector equivocado
> (*inyección* de un artefacto exculpatorio). La inducción **falsó** ese vector y
> **confirmó** uno distinto (*relabel* de un incriminatorio existente). Esta versión
> corrige el vector, el nivel epistemológico y la redacción.

---

## Resumen ejecutivo

| # | Pregunta | Veredicto | Nivel |
|---|----------|-----------|-------|
| 1 | ¿Se puede manipular el veredicto sellado sin romper el hash? ¿Se sella antes de fijar el veredicto? | Integridad del hash sólida; el veredicto sellado **sí** es manipulable envenenando el input (demostrado por Q2). No hay bug de "sellar antes de fijar" en el camino primario. | CONFIRMADO POR INDUCCIÓN (vía Q2) |
| 2 | ¿`eco_check.py` puede ser engañado por un artefacto exculpatorio crafteado? | **Sí, por RELABEL** (no por inyección): controlando `semantic_role` + evadiendo la blocklist por paráfrasis, MALICE→NOISE end-to-end. | CONFIRMADO POR INDUCCIÓN |
| 3 | ¿El Protocolo de Refutación tiene bypass? ¿El LLM cambia el veredicto tras el sellado? | El LLM está fuera del lazo sellado. Pero `run_llm_cases.py` etiqueta mal un pseudo-bundle, y la "refutación obligatoria" es un chequeo de presencia auto-rellenado. | HECHO DE CÓDIGO |
| 4 | ¿Race condition en escrituras atómicas? ¿Otros paths sin el patrón L-023? | El fix L-023 estaba parcialmente desplegado: camino primario del Modo 1 no atómico. **Corregido en este cambio** con independencia verificada. | HECHO DE CÓDIGO + fix verificado |

**Conclusión transversal:** la fortaleza criptográfica de EBS v1 protege contra
manipulación *post-sellado*. La debilidad no está en el hash sino en **lo que el hash
promete**: atesta *integridad* y *coherencia decisión↔riesgo*, nunca *corrección del
veredicto*. El experimento Q2 lo demuestra: un bundle con hash perfectamente válido
puede sellar un veredicto NOISE que debería ser MALICE.

---

## Q2 — Filtro Eco / neutralización de MALICE (inducción completa)

**Veredicto: CONFIRMADO POR INDUCCIÓN — vector RELABEL, no inyección.**
Evidencia reproducible: `scratchpad/q2_induction.py`.

### Cadena peirceana

- **Abducción:** un exculpatorio crafteado puede neutralizar un veredicto MALICE
  evadiendo la blocklist Eco por paráfrasis.
- **Deducción D1:** si es correcto, un memo con sinónimos hace
  `text_obvious_bait_hits()` devolver `[]`.
- **Deducción D2:** el "apartado" (set-aside) **remueve** el artefacto del scoring, luego:
  *inyectar* un exculpatorio nuevo debería ser neto cero; *relabelar* un incriminatorio
  existente debería degradar si cruza el gate de corroboración.
- **Inducción:** ejecutada sobre 6 casos MALICE reales del corpus.

### Evidencia experimental (scorer HEAD, sin fix)

**D1 — bypass de la blocklist (CONFIRMADO):**
`text_obvious_bait_hits(memo)` → `[]`. La blocklist de 50 términos
(`vigia/core/eco_check.py:32-47`) se evade con sinónimos profesionales:
"credential dump"→"diagnostic scripts", "delete logs"→"clear transient event records",
"exfil"→"off-site backup", sin nombrar `mimikatz`/`vssadmin`.

**Inducción sobre casos MALICE reales:**

| Caso | base | A: inyectar | B: relabel 1 | C: relabel varios |
|------|------|-------------|--------------|-------------------|
| VIGIA-NGDC-001 | MALICE | MALICE | MALICE | SUSPICION |
| VIGIA-REAL-NROMANOFF | MALICE | MALICE | **SUSPICION** | SUSPICION |
| VIGIA-LINUX-004 | MALICE | MALICE | MALICE | **NOISE** |
| VIGIA-REAL-009 | MALICE | MALICE | **SUSPICION** | **NOISE** |
| VIGIA-REAL-008 | MALICE | MALICE | MALICE | SUSPICION |
| VIGIA-REAL-DEFI-DRAIN-001 | MALICE | MALICE | **SUSPICION** | SUSPICION |

- **Exp A (inyectar exculpatorio nuevo): FALSADO — 0/6 degradaron.** El apartado
  remueve del scoring, así que un artefacto extra es neto cero. **La hipótesis
  original de la auditoría ("plantar un artefacto exculpatorio") es incorrecta.**
- **Exp B (relabelar 1 incriminatorio + texto limpio): 3/6 → SUSPICION** (casos cerca
  del gate B-068).
- **Exp C (relabelar varios): 6/6 → SUSPICION/NOISE.**

**Confirmación end-to-end del veredicto SELLADO** (agente completo, no sólo scorer;
el agente es el path que sella y difiere del scorer): copia relabeleada (Exp C) →
`VIGIA-REAL-009: MALICE→NOISE`, `VIGIA-LINUX-004: MALICE→NOISE`. El veredicto que va a
la corte flipea de MALICE a NOISE.

### El vector real (corregido) y su modelo de amenaza

El vector no es la blocklist ni la inyección: es la **confianza en `semantic_role`**.
`vigia_scorer.py:_semantic_role` lee el campo directo del artefacto; la única
validación (`vigia/pipeline/vigia_integration_bridge.py:554-562`) chequea el *valor de
enum*, sin firma ni proveniencia. Quien controla el `semantic_role` del case JSON puede
convertir evidencia incriminatoria real en "exculpatoria" y, con texto que evade Eco,
apartarla del scoring.

**Precondición (honesta):** el atacante debe controlar el `semantic_role` del input —
un examinador comprometido, o cualquier etapa upstream que derive `semantic_role` de
contenido no confiable. **No es un exploit remoto no autenticado**; es una debilidad de
frontera de confianza en cómo se trata `semantic_role`.

### Asimetría estructural (agravante)

- **Incriminatorio** debe cruzar el gate B-068 (`vigia_scorer.py:899-919`): ≥4
  artefactos O ≥3 tipos. — **HECHO DE CÓDIGO.**
- **Exculpatorio** necesita 1 artefacto relabeleado que pase la wordlist para *cancelar*
  evidencia incriminatoria. Sin barra de corroboración propia. — **HECHO DE CÓDIGO.**
- **Fail-open** (`vigia_scorer.py:490-491`): si `eco_check` no importa, `_eco_bait_hits`
  devuelve `[]` → todo exculpatorio se aparta sin filtro. — **HECHO DE CÓDIGO.**

### Sobre `devil_advocate_gen.py` (considerado explícitamente)

`devil_advocate_gen.compose_devil_advocate_struct` **no mitiga** este ataque, y su
asimetría lo agrava: el `devil_advocate` sólo se genera para veredictos MALICE/INTENT
(R7, `forensics/verify_ebs_v1.py:364-393`). Cuando el ataque degrada a **NOISE**, no se
genera refutación alguna — el sistema exige "abogado del diablo" para condenar pero **no
tiene un abogado del fiscal que desafíe una exculpación**. El ataque aterriza exactamente
en ese punto ciego. Verificado por lectura de código + confirmado por el experimento
(salida NOISE = sin capa de refutación).

---

## Q1 — Manipulación del veredicto sellado

### Lo que está bien (HECHO DE CÓDIGO)

- `bundle_hash` cubre todo el payload incluido `caie_analysis` y `abduction_trace`
  (`vigia/core/bundle_builder.py:190-213`) — Invariante I2. Mutación post-sellado rompe
  el hash. Verificador stdlib independiente (`forensics/verify_ebs_v1.py`).
- En el camino primario (`vigia_agent.py`) el veredicto se fija ANTES de sellar
  (`classify_agent_verdict` en `_seal_bundle:1158`, sobre `abduction` ya finalizada por
  el override L-036 en `_generate_narrative`). No hay ventana "sellado→cambio".

### El vector real (CONFIRMADO POR INDUCCIÓN vía Q2)

El verificador chequea integridad (R1) y coherencia decisión↔riesgo (R3,
`verify_ebs_v1.py:304-335`), pero **nunca re-ejecuta el scorer**. Por eso el sello promete
"estos bytes no cambiaron y la decisión EBS es coherente con su riesgo" — **no** "el
veredicto forense es correcto". El experimento Q2 lo demuestra: el bundle sellado de
`VIGIA-REAL-009` relabeleado lleva veredicto NOISE con hash válido, cuando la evidencia
real es MALICE. **No hace falta romper el hash: se envenena el input y se sella la mentira
auto-consistente.**

### Observación secundaria (HIPÓTESIS PLAUSIBLE)

- **Q1-A** — R3 valida `decision_trace.decision` contra `risk`, pero `caie_analysis.verdict`
  (el veredicto forense titular) no se cruza con el riesgo. `build_bundle` los fija
  consistentes; el verificador confía en el campo, no lo reconcilia. No inducido.

---

## Q3 — Protocolo de Refutación / LLM tras el sellado

**Todos HECHOS DE CÓDIGO (observación directa), salvo donde se indique.**

- **El LLM no cambia el veredicto EBS sellado.** Modo 1 es 100% determinista
  (`vigia_agent.py:817-820`); el sellado toma el resultado del scorer determinista, no de
  `reason_with_llm`. Verificado trazando **todos** los llamadores de `BundleBuilder.seal`
  / `build_bundle` (`pipeline.py:729`, `bundle_builder.py:537`, `ebs.py:1105`) — ninguno
  recibe el veredicto del LLM. *(Verificación arquitectónica por trazado de llamadores.)*
- **Pseudo-bundle mal etiquetado.** `run_llm_cases.py:170-207` escribe
  `results/llm_mode/<CASE>_llm_bundle.json` con `"bundle_version": "ebs_v1"` cuyo titular
  es `llm_verdict` (extraído del LLM) + flag `verdict_changed`, **sin bloque `integrity`
  ni hash** (`write_text` plano). `verify_ebs_v1.py` lo rechazaría, pero la etiqueta
  `ebs_v1` induce a confiar en un veredicto de LLM sin sellar.
- **Refutación "obligatoria" = chequeo de presencia.** R7 (`verify_ebs_v1.py:364-393`)
  sólo exige que `devil_advocate` no esté vacío para MALICE/INTENT. En el camino standalone
  (`build_bundle`) `pattern_signal_metadata` es siempre `None`
  (`bundle_builder.py:520-535`), y `compose_devil_advocate_struct` emite una narrativa fija
  "no pattern data available… documented scope limitation" con `pattern_evidence_gaps: []`
  (`devil_advocate_gen.py:126-134`). No realiza falsificación ni puede degradar el veredicto.

---

## Q4 — Escrituras atómicas / race conditions (CORREGIDO en este cambio)

**Diagnóstico (HECHO DE CÓDIGO):** el fix L-023 (`mkstemp+fsync+os.replace`) vivía sólo en
`bundle_builder.py` y `atomic_io.py`; el **camino primario del Modo 1** (`vigia_agent.py`)
y ambos `EBS.save()` escribían el bundle sellado con `Path.write_text`/`open("w")` directo
— el patrón NO atómico que L-023 vino a corregir. Además el guardia "DISK MISMATCH" del
agente comparaba memoria-vs-memoria (tautológico), y `atomic_io` no hacía fsync del
directorio padre (durabilidad del rename).

**Fix aplicado en este cambio:**
1. `vigia_agent.py:1849/1867` → `atomic_io.atomic_write_text` (bundle + `.sha256`).
2. `.sha256` computado **re-leyendo de disco** (`vigia_agent.py`), no de memoria — el guardia
   deja de ser tautológico.
3. `atomic_io._atomic_write` → `_fsync_parent_dir()` tras `os.replace` (durabilidad F-6).

**Verificación de independencia (a pedido — evidencia, no aserción):**
- **Enumeración completa** de consumidores de `atomic_io`: **7 sitios de producción**, todos
  en `vigia/pipeline/` (`evidence_bundle.py:122/128/136/145`,
  `security_evidence_registry.py:190`, `vigia_integration_bridge.py:1211/1242`) + 3 tests
  (`test_b062_b064_pipeline_fixes.py`). Ningún otro módulo lo consume.
- **Independencia estática:** los 7 sitios llaman `atomic_write_*(path, content)` e ignoran
  el retorno `None`; ninguno depende de permisos, timing ni de la ausencia del dir-fsync. El
  dir-fsync sólo agrega durabilidad tras un `os.replace` exitoso; no cambia contenido,
  retorno ni lanza excepciones nuevas (best-effort guardado). El test de fallo
  (`test_atomic_write_failure_preserves_existing_target`) nunca alcanza el nuevo código
  (falla antes de `os.replace`).
- **Independencia empírica:** suite completa **805 passed, 1 skipped, 7 xfailed** —
  **idéntico al baseline** pre-cambio. 55 tests de consumidores verdes. Agente end-to-end
  `sha256sum -c: OK`.

**Fuera del alcance de este cambio (documentado, no corregido):** `vigia/models/ebs.py:812/1138`
(ambos `EBS.save()`) siguen el patrón pre-L-023; PDFs firmados
(`report_exporter*.py`), firma `.sig` de release. Requieren su propia verificación de
independencia antes de tocarse.

---

## Recomendaciones (registro — fuera del alcance de este cambio)

1. **Q2:** el fix correcto ataca el vector real, no la blocklist: **autenticar/atestiguar
   `semantic_role`** (firma o binding de proveniencia, no sólo validación de enum) y darle
   una **barra de corroboración** propia (simetría Daubert). Convertir el fail-open en
   fail-closed. Extender `_artifact_text` a contenido completo. Complementar la blocklist con
   señales estructurales. *(Diseño pendiente de decisión — la barra n≥2 sola no cierra el
   vector `semantic_role`.)*
2. **Q3:** no etiquetar `ebs_v1` a los bundles de `run_llm_cases.py`; hacer que la refutación
   del camino standalone ejecute una falsificación real capaz de degradar.
3. **Q1:** cruzar `caie_analysis.verdict` contra `risk`/`decision` en el verificador.
4. **Q4:** extender el fix a `ebs.py` `save()` y a los PDFs firmados, con la misma
   verificación de independencia.

---

*Auditoría revisada tras inducción experimental. Los niveles epistemológicos son
explícitos y cada hallazgo CONFIRMADO tiene evidencia reproducible citada.*
