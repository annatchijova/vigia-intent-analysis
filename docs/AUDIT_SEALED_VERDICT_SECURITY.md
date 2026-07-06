# Auditoría de Seguridad — Sellado del Veredicto, Filtro Eco, Protocolo de Refutación y Escrituras Atómicas

**Fecha:** 2026-07-06
**Alcance:** cuatro vías de ataque sobre el núcleo forense determinista de VIGÍA.
**Modo:** investigación y documentación — **sin modificación de código**.
**Base:** rama `claude/sealed-verdict-security-najnug` sobre `main` (tags remotos restaurados localmente antes de auditar).

> Convención de severidad (marco Daubert): **ALTA** = puede sellarse/verificarse un
> veredicto sustancialmente incorrecto sin fricción; **MEDIA** = ruptura de cadena de
> custodia o de confianza bajo condiciones alcanzables; **BAJA** = latente / requiere
> condiciones poco comunes.

---

## Resumen ejecutivo

| # | Pregunta | Veredicto | Severidad |
|---|----------|-----------|-----------|
| 1 | ¿Se puede manipular el veredicto sellado sin romper el hash? ¿Se sella antes de fijar el veredicto? | **La integridad del hash es sólida, pero el veredicto sellado ES manipulable indirectamente** vía envenenamiento del input del scorer. No hay bug de "sellar antes de fijar" en el camino primario. | ALTA (indirecta, vía Q2) |
| 2 | ¿`eco_check.py` puede ser engañado por un artefacto exculpatorio crafteado? | **EXPLOTABLE — CONFIRMADO.** | ALTA |
| 3 | ¿El Protocolo de Refutación Obligatoria tiene bypass? ¿El LLM puede cambiar el veredicto tras el sellado? | **El LLM no entra en el veredicto EBS sellado.** Pero (a) `run_llm_cases.py` produce un pseudo-bundle mal etiquetado `ebs_v1` cuyo titular es el veredicto del LLM, y (b) la "refutación obligatoria" es un **chequeo de presencia** auto-rellenado por plantilla, no una refutación real. | MEDIA |
| 4 | ¿Race condition en escrituras atómicas? ¿Otros paths sin el patrón L-023? | **CONFIRMADO.** El fix L-023 está desplegado sólo parcialmente; el camino primario (Modo 1) y ambos `EBS.save()` escriben el bundle sellado de forma NO atómica. | ALTA |

**Conclusión transversal:** la fortaleza criptográfica de EBS v1 (encadenamiento SHA-256 +
HMAC, verificador stdlib independiente) es real y protege contra manipulación *post-sellado*.
La debilidad no está en el hash sino en **lo que el hash promete**: atesta *integridad* y
*coherencia decisión↔riesgo*, nunca *corrección del veredicto*. Un adversario que controla el
input (Q2) obtiene un bundle con hash perfectamente válido sobre un veredicto neutralizado, y
lo escribe por un path que ni siquiera es atómico (Q4).

---

## Q1 — Manipulación del veredicto sellado / sellado prematuro

### Lo que está bien (no es el vector)

- **`bundle_hash` cubre TODO el payload (Invariante I2).** `vigia/core/bundle_builder.py:190-213`
  hashea `bundle_id + version + timestamp + evidence_graph(con graph_hash) + decision_trace +
  policy_spec + actions + system_state + config_attestation`, e incluye `caie_analysis`
  (donde vive el veredicto forense titular) y `abduction_trace` cuando existen
  (`:203-206`). Cualquier mutación *post-sellado* de un campo rompe el hash.
- **Verificador independiente stdlib.** `forensics/verify_ebs_v1.py` reimplementa el mismo
  protocolo sin importar código de producción (`:7-17`) — un tercero puede recomputar los
  hashes. R1 (integridad) recomputa `graph_hash`/`policy_hash`/`bundle_hash`
  (`:187-231`).
- **En el camino primario (`vigia_agent.py`) el veredicto se fija ANTES de sellar.**
  `_seal_bundle` clasifica con `classify_agent_verdict(abduction, …)` (`vigia_agent.py:1158`)
  sobre una `abduction` ya finalizada; el override L-036 ocurre antes, dentro de
  `_generate_narrative` (`:850-887`). No hay ventana temporal "sellado → cambio de veredicto".

### El vector real: el hash atesta integridad, NO corrección

El verificador comprueba **coherencia decisión↔riesgo** (R3, `verify_ebs_v1.py:304-335`) —
que `decision ∈ {ACCEPT,REJECT,ABSTAIN}` sea consistente con `risk` vs `epsilon` — pero
**nunca re-ejecuta el scorer**. Por diseño no puede: es stdlib-puro. Consecuencia:

> El sellado promete "estos bytes no cambiaron y la decisión EBS es coherente con su riesgo".
> **No** promete "el veredicto forense es correcto". Si el scorer produce un veredicto
> neutralizado (Q2), el pipeline lo sella con hash válido y el verificador lo aprueba a
> Level 2/3. **No hace falta romper el hash: se envenena el input y se sella la mentira
> auto-consistente.**

Ésta es la respuesta central a Q1: *sí* se puede "manipular el veredicto sellado sin romper
el hash", no tocando el bundle sino su **entrada** (ver Q2).

### Observaciones secundarias

- **Q1-A (MEDIA) — `caie_analysis.verdict` no se cruza con `risk`/`decision`.** R3 valida
  `decision_trace.decision` contra `risk`, pero el veredicto forense titular vive en
  `caie_analysis.verdict` y **no** se re-deriva ni se cruza contra el riesgo. `build_bundle`
  los fija consistentes en el mismo snapshot (`bundle_builder.py:466-476, 507-518`), pero el
  verificador confía en el campo, no lo reconcilia. Un bundle con `caie_analysis.verdict`
  desalineado del riesgo pasaría R3 si su `decision` mapeada es coherente.
- **Q1-B (BAJA, latente) — pérdida del override L-036 si falta `abduction`.** En
  `_generate_narrative`, `abduction = results.get("abduction", {})` (`vigia_agent.py:832`).
  Si la clave `abduction` no existe, el override L-036 (que puede **elevar** a MALICE/INTENT,
  `:863-879`) muta un dict descartable que nunca se re-inserta en `results`; el sellado
  vuelve a leer `results.get("abduction", {})` → vacío. Divergencia potencial narrativa↔sello
  en el sentido *conservador* (se pierde una elevación). Requiere que `abduction` esté ausente
  — inusual, pero es una asimetría de estado a cerrar.

**Veredicto Q1:** integridad post-sellado = sólida. "Sellar antes de fijar el veredicto" = no
en el camino primario (latente Q1-B). Pero el veredicto sellado **es** manipulable sin tocar
el hash, envenenando la entrada del scorer (Q2), y el verificador atesta integridad+coherencia,
nunca corrección.

---

## Q2 — Bypass del filtro Eco vía artefacto exculpatorio crafteado

**Veredicto: EXPLOTABLE — CONFIRMADO.** Un adversario que controla el contenido de un
artefacto con `semantic_role: "exculpatory"` neutraliza señales MALICE reales. La compuerta
D1 que debería atraparlo es **una lista estática de ~40 términos y nada más**, trivialmente
derrotable por paráfrasis. Los propios autores documentaron el hueco como no resuelto.

### Cadena de datos

1. **Clasificación exculpatoria = campo del JSON, sin autenticar.**
   `vigia_scorer.py:493-495` lee `semantic_role` directo del artefacto. La única validación
   (`vigia/pipeline/vigia_integration_bridge.py:554-562`) es un chequeo de *valor de enum* —
   sin firma, sin binding de proveniencia, sin cadena de custodia. Quien controla el case JSON
   controla `semantic_role`.

2. **Neutralización del composite (mecánica "apartar").** `vigia_scorer.py:502-544`: un
   artefacto exculpatorio que **no** dispara D1 se aparta (`_exculpatory_set_aside`) y se
   elimina de `artifacts` (`:528`), desapareciendo de media composite, diversidad de tipos,
   `n_artifacts` y la compuerta de corroboración B-068 (`:899-919`). Dos desenlaces:
   - **Downgrade de compuerta:** al retirar un artefacto DEVICE-class, el caso cae bajo el
     umbral `≥4 artefactos OR ≥3 tipos` → **MALICE → SUSPICION**.
   - **Colapso a NOISE:** si toda la evidencia device restante es exculpatoria-y-limpia,
     retorna `verdict: NOISE, confidence: 0.9` (`:530-544`). El doc §3 confirma un caso real
     MALICE→NOISE (`case_018`). Es el sucesor arquitectónico de la fuga ×0.25 de TANDA-4/H1c.

3. **Qué chequea realmente D1.** `vigia_scorer.py:487-491` importa
   `text_obvious_bait_hits`; `vigia/core/eco_check.py:70-74` es todo el filtro: match
   case-insensitive de palabra completa contra `OBVIOUS_BAIT_TERMS` (`:32-47`, ~40 literales:
   `hack`, `mimikatz`, `c2`, `exfil`, `port scan`, `tor exit`…). **No hay** análisis de
   entropía, ni test de "demasiado perfecto", ni Grice, ni estilometría, ni consistencia
   cruzada. La doctrina "documentación demasiado perfecta = señal" está **documentada pero no
   implementada** — es una blocklist de malas palabras. Además `_artifact_text`
   (`:497-500`) sólo lee `description` + `metadata.content_preview`.

### El ataque concreto

Malice real en disco: acceso a credenciales por PowerShell + borrado de logs
(`wevtutil`/`vssadmin`) a las 02:00 en un servidor de finanzas.

Artefacto exculpatorio plantado (`semantic_role: exculpatory`, DEVICE-class), redactado como
memo de autorización y **sin ningún término de `OBVIOUS_BAIT_TERMS`**:

> "Per change ticket CHG-2026-0042, the 02:00–04:00 maintenance window on the finance host was
> pre-approved by the change advisory board. The on-call engineer was authorized to run
> diagnostic and remediation scripts and to clear transient event records as routine
> housekeeping. Signed, IT Operations Manager."

Evasión por sinónimos (un swap por término): "credential dump"→"diagnostic scripts";
"log_deleted"/"delete logs"→"clear transient event records"; "exfil"→"off-site backup";
"lateral movement"→"connected to adjacent hosts"; `mimikatz`/`vssadmin`→nunca se nombran.
`text_obvious_bait_hits()` → `[]` → D1 no dispara → se aparta → MALICE degrada a SUSPICION,
o a NOISE (conf 0.9) si era el artefacto corroborante.

### Asimetría de corroboración (falla de diseño núcleo)

- Evidencia **incriminatoria** debe pasar B-068: `≥4 artefactos OR ≥3 tipos`
  (`vigia_scorer.py:909`).
- Evidencia **exculpatoria** necesita **1 artefacto** + pasar la wordlist para *cancelar* lo
  incriminatorio. No hay guard `n≥2` en el bucle de apartado (`:505-525`).

El doc `docs/FASE2_EVIDENCIA_EXCULPATORIA.md` §4.5 punto 5 reconoce el hueco: *"un memo
forjado examiner-declared por error sería un FN sin fricción"*.

**Fail-open adicional (`vigia_scorer.py:490-491`):** si `vigia.core.eco_check` no importa,
`_eco_bait_hits` retorna `[]` incondicionalmente → D1 desactivado silenciosamente → **todo**
exculpatorio se aparta sin importar su contenido.

| Capa | Defensa pretendida | Implementación real | Bypass |
|------|--------------------|---------------------|--------|
| `semantic_role` | Declarado por examinador, sellado | Chequeo de enum solamente | Campo controlado por input |
| Filtro D1 Eco | "Docs demasiado perfectos = señal" | Blocklist estática ~40 palabras | Paráfrasis / sinónimos |
| Corroboración | Barra Daubert simétrica | Ninguna en el lado exculpatorio | Un artefacto basta |
| Alcance de texto | Contenido completo | Sólo `description`+`content_preview` | Bait fuera del preview |
| Módulo ausente | — | Fail-open, D1 desactivado | Silencioso |

---

## Q3 — Bypass del Protocolo de Refutación / LLM tras el sellado

### El LLM no puede cambiar el veredicto EBS sellado

- **Modo 1 es 100% determinista.** `_generate_narrative` declara y cumple "No LLMs — all
  derived from pipeline data" (`vigia_agent.py:817-820`). El veredicto es función pura de
  `abduction.best_hypothesis` (`classify_agent_verdict`, `:120-183`).
- **El sellado toma el resultado del scorer determinista, no del LLM.**
  `build_bundle`/`BundleBuilder.seal` (`bundle_builder.py:413-537`) recibe `scorer_result`;
  `reason_with_llm` (`vigia/vigia_sift_bridge.py:2668-2740`) es una herramienta MCP cuyo
  `verdict` es una señal separada que nunca alimenta al scorer. Cambiar el veredicto *tras*
  sellar rompería el hash (Q1). **Estructuralmente el LLM está fuera del lazo de decisión
  sellado** — consistente con el Invariante 3.

### Debilidad 3-A (MEDIA): pseudo-bundle mal etiquetado `ebs_v1` con veredicto del LLM

`run_llm_cases.py` escribe `results/llm_mode/<CASE>_llm_bundle.json` con
`"bundle_version": "ebs_v1"` (`:170-184`) cuyo **titular es `llm_verdict`** — extraído
directo del LLM (`_extract_llm_verdict`, `:84-120`) — con un flag explícito
`verdict_changed = llm_verdict != fallback` (`:181`). La tabla PASS/FAIL se computa contra
`llm_verdict`, no contra el determinista (`:233-235`).

Este archivo **no está sellado**: no tiene `integrity`, ni `bundle_hash`, ni cadena — es un
`out_path.write_text(json.dumps(bundle…))` plano (`:207`). `verify_ebs_v1.py` lo rechazaría
(sin bloque `integrity`/estructura). Pero un humano que lea el archivo y confíe en la etiqueta
`ebs_v1` + `llm_verdict` está confiando en un veredicto de LLM sin sellar. Es una **falla de
frontera de confianza / etiquetado engañoso**: lo más cercano a "el LLM cambia el veredicto",
por diseño en ese runner.

### Debilidad 3-B (MEDIA): la "refutación obligatoria" es un chequeo de presencia

El Protocolo de Refutación Obligatoria (CLAUDE.md) exige un `devil_advocate` poblado para
INTENT/MALICE, y su Paso 2 dice: *si la hipótesis benigna explica todo → degradar*. La
implementación:

- **La compuerta sólo verifica presencia.** `verify_ebs_v1.py:364-393` (R7): si
  `caie_analysis.verdict ∈ {MALICE,INTENT}` y `devil_advocate` está vacío → falla. Sólo eso.
- **`devil_advocate` se auto-genera por plantilla determinista.**
  `compose_devil_advocate_struct` (`vigia/core/devil_advocate_gen.py:33-145`).
- **En el camino standalone (`build_bundle`) `pattern_signal_metadata` es SIEMPRE `None`**
  (`bundle_builder.py:520-535`, confirmado en el docstring `:18-23`), por lo que emite un
  narrativa fija *"Pattern-matching data was not available… documented scope limitation…"*
  con `pattern_evidence_gaps: []` (`devil_advocate_gen.py:126-134`).

Es decir: en el camino primario/standalone, la "refutación obligatoria" es un campo de
relleno que **no realiza ninguna falsificación** y **nunca puede degradar** el veredicto. El
Paso 2 del protocolo (probar la hipótesis benigna contra toda la evidencia y degradar) es
**doctrina, no código ejecutado** en ese camino. El "bypass" no es esquivar la compuerta —
es que la compuerta se satisface con un artefacto auto-rellenado que no refuta nada.

**Veredicto Q3:** el LLM no puede alterar el veredicto sellado (bien). Pero existe un runner
que sella-en-apariencia (`ebs_v1`) un veredicto de LLM sin integridad, y la refutación
"obligatoria" del camino primario es cosmética (presencia, no falsificación real).

---

## Q4 — Escrituras atómicas / race conditions

**Veredicto: CONFIRMADO.** El fix L-023 (`mkstemp+fsync+os.replace`) vive sólo en
`vigia/core/bundle_builder.py:BundleBuilder.save` y `vigia/core/atomic_io.py` (+ writers de
`vigia/pipeline/`). **El punto de entrada primario del Modo 1 y ambos `EBS.save()` escriben el
bundle sellado exactamente con el patrón NO atómico que L-023 vino a corregir.**

### Sitios de escritura relevantes para custodia

| Archivo:línea | Qué escribe | ¿Atómico? | Riesgo |
|---------------|-------------|-----------|--------|
| `vigia_agent.py:1849` | **Bundle sellado Modo 1** (veredicto canónico hasheado) | **NO** (`write_text`) | **ALTA** |
| `vigia_agent.py:1867` | Sidecar `.sha256` del bundle | **NO** (`write_text`) | MEDIA |
| `vigia/models/ebs.py:812` | `ForensicBundle.save()` bundle sellado | **NO** (`open(…,"w")`) | **ALTA** |
| `vigia/models/ebs.py:1138` | Segundo `save()` (dict sellado) | **NO** (`open(…,"w")`) | **ALTA** |
| `vigia/scripts/run_pipeline.py:173` | Bundle de resultados pipeline | **NO** | MEDIA |
| `run_llm_cases.py:207` | `*_llm_bundle.json` (Q3-A) | **NO** | MEDIA |
| `run_all_agent.py:229` | Bundle resumen de batch | **NO** | BAJA/MEDIA |
| `convert_mans_to_ebs.py:224` | Registro EBS de caso | **NO** | MEDIA |
| `vigia/pipeline/report_exporter.py:238` | PDF forense firmado | **NO** (`open(…,"wb")`) | MEDIA |
| `vigia/pipeline/report_exporter_v2.py:251` | PDF forense firmado | **NO** | MEDIA |
| `scripts/generate_release_bundle.py:129` | Firma HMAC `.sig` de release | **NO** | MEDIA |
| `vigia/core/bundle_builder.py:265` | Bundle sellado (**fix de referencia**) | **SÍ** (mkstemp+fsync+replace + read-back) | — |
| `vigia/pipeline/evidence_bundle.py:122/128/136/145` | PDF/ledger/manifest/firma | **SÍ** (`atomic_write_*`) | — |
| `vigia/pipeline/security_evidence_registry.py:190` | Registro de evidencia | **SÍ** | — |
| `vigia/core/tool_log_chain.py` | Cadena tool_execution_log | **In-memory only** — hereda la atomicidad del bundle que la contiene | — |
| `vigia/security/security.py:442` | Audit log HMAC-encadenado | Append + `flock` + `fsync` (seguro) | BAJA |

### Hallazgos concretos

- **F-1 (ALTA) — Bundle sellado primario NO atómico.** `vigia_agent.py:1846-1849` escribe el
  bundle canónico con `Path.write_text` — sin tempfile, sin fsync, sin rename atómico. Crash a
  mitad de escritura = veredicto sellado truncado en `output_path`; un symlink plantado se
  sigue y se escribe a través; un escritor concurrente puede intercalar. Exactamente el
  escenario L-023. Ironía: el bloque siguiente levanta `RuntimeError` por "possible filesystem
  corruption or race condition" (`:1862-1864`) pero igual escribió no-atómicamente.
- **F-1b (MEDIA) — el guardia "DISK MISMATCH" es tautológico.** `disk_digest` se computa sobre
  `output_text` **en memoria** (`vigia_agent.py:1855`), no re-leyendo el archivo, y se compara
  contra `bundle_canonical_digest` (también en memoria). El comentario dice "Recalculate over
  the text written to disk" pero recalcula sobre la variable en memoria — no verifica el disco.
  Es más débil que `BundleBuilder.save`, que **sí** re-lee de disco y compara
  (`bundle_builder.py:278-288`).
- **F-2 (ALTA) — ambos `EBS.save()` reproducen el patrón pre-L-023.** `vigia/models/ebs.py:806-815`
  y `:1133-1140` escriben directo y retornan un hash computado **desde memoria** — no atesta lo
  que quedó en disco. Un write parcial o symlink swap seguiría devolviendo un hash "válido".
- **F-3 (MEDIA) — PDFs forenses firmados no atómicos.** `report_exporter.py:235-239` y
  `report_exporter_v2.py:251` firman el hash del PDF y luego escriben los bytes directo; un PDF
  truncado no matchea su firma → rompe la custodia del reporte de tribunal.
- **F-4 (MEDIA) — release `.sig`/`.tar.gz` y conversión MANS→EBS** no atómicos
  (`generate_release_bundle.py:129`, `convert_mans_to_ebs.py:224`).
- **F-6 (MEDIA, aplica incluso donde SÍ se usa el patrón) — sin fsync del directorio padre.**
  Ni `atomic_io._atomic_write` ni `BundleBuilder.save` hacen fsync del directorio contenedor
  tras `os.replace`. En crash inmediatamente posterior al rename, el rename puede perderse en
  algunos filesystems (ext4 por defecto): el veredicto revierte al archivo previo o desaparece
  — gap de durabilidad. Además `atomic_io` no hace read-back-verify (sí lo hace
  `bundle_builder.py`), y el guard de symlink es sobre el nombre final, no sobre el directorio
  (si `target_dir` es un symlink controlado, tempfile y artefacto se redirigen).

**Nota `tool_log_chain`:** `ToolExecutionLogChain` es un appender **en memoria** — nunca toca
disco; su atomicidad depende por completo del writer de bundle que lo contiene (vulnerable vía
`vigia_agent.py:1849`/`ebs.py`, seguro vía `bundle_builder.py`).

---

## Recomendaciones (fuera de alcance de esta tarea — sólo registro)

1. **Q4 (prioridad máxima):** enrutar `vigia_agent.py:1849/1867` y `vigia/models/ebs.py:812/1138`
   por `atomic_io.atomic_write_text` (o `BundleBuilder.save`); hacer el `.sha256` sobre el
   contenido **re-leído de disco**; agregar fsync de directorio padre a
   `atomic_io._atomic_write`.
2. **Q2:** dar a la evidencia exculpatoria su propia barra de corroboración (romper la asimetría
   `n≥2`); reemplazar/complementar la blocklist D1 con señales estructurales (entropía, Grice,
   estilometría, consistencia cruzada) en vez de wordlist; extender `_artifact_text` a contenido
   completo; convertir el fail-open de import en fail-closed.
3. **Q3:** no etiquetar `ebs_v1` a los bundles de `run_llm_cases.py` (o marcarlos
   `UNSEALED_LLM_ADVISORY`); hacer que la refutación en el camino standalone ejecute una
   falsificación real capaz de degradar, no un relleno de plantilla.
4. **Q1:** cruzar `caie_analysis.verdict` contra `risk`/`decision` en el verificador (R3+);
   cerrar la asimetría de estado `abduction` ausente en `_generate_narrative`.

---

*Auditoría generada en modo investigación. Ningún archivo de código fue modificado.*
