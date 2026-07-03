# Triage — Bugs abiertos y limitaciones pendientes (verificados contra código vivo)

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Alcance:** todos los ítems no-cerrados de `BUGS_PENDIENTES.md` (B-001..B-052),
`KNOWN_LIMITATIONS.md` (L-001..L-043) y los pendientes surgidos de las cuatro
auditorías de esta rama (robustez, L-040, macOS, B-047).
**Método:** para cada ítem ABIERTO/PENDING, verificación puntual contra el
código vivo (el caso B-047 demostró que el tracker puede estar estanco en las
dos direcciones: bugs ya corregidos que siguen [PENDING], y "no explota con el
corpus actual" que dejó de ser cierto). Cada verificación cita `archivo:línea`.
**Acción tomada:** NINGUNA sobre el código. Investigación + propuesta.

---

## Resumen ejecutivo

- **43 entradas** en BUGS_PENDIENTES: 30 resueltas/descartadas, **13 abiertas**
  (B-010, B-013, B-016, B-017, B-018, B-025, B-026, B-027, B-028, B-029,
  B-041b, L-040, B-052-P2). Todas las abiertas fueron re-verificadas: **siguen
  reales**, pero **tres tienen alcance distinto al documentado** (B-017 es
  peor; B-016 y B-018 están parcialmente mitigadas por fixes posteriores).
- **KNOWN_LIMITATIONS:** la mayoría son limitaciones de diseño documentadas
  (Daubert scope, correcto no tocarlas). Quedan **4 accionables**: L-023
  (write no atómico del bundle — P0 declarado hace 3 semanas, sigue abierto),
  L-024 (`/mnt` en allowlist), L-037b (base_trust hardcodeado) y L-039
  (tshark, con un agravante nuevo).
- **Hallazgos nuevos de este triage** (no registrados en ningún tracker):
  **T-1** el import duro de defusedxml mata TODO el paquete `vigia.sift` (no
  solo event logs); **T-2** `defusedxml` falta en `requirements-ci.txt`
  (reproducido: este mismo entorno CI no lo tenía); **T-3** un pcap corrupto
  aborta el análisis COMPLETO de un caso mixto (`raise` en el shim); **T-4**
  el hallazgo crítico de AUDIT_NARRATIVAS (NROMANOFF sealed report con anchor
  contradictorio) quedó resuelto por eliminación del archivo — cerrable.
- **Propuesta:** 3 tandas — Tanda A (5 fixes acotados de alto retorno, ~1 día),
  Tanda B (decisiones de diseño con propuesta concreta), Tanda C (calibración
  con ground truth — no tocar a ciegas). Matriz completa en §5.

---

## 1. Verificación de los ítems ABIERTOS de BUGS_PENDIENTES

### B-017 — defusedxml ausente ⚠ PEOR de lo documentado `[REPRODUCIDO]`

**Documentado:** "produce PIPELINE_ERROR silencioso" en event logs.
**Estado real verificado:**

1. **El blast radius es todo el paquete `vigia.sift`**, no solo event logs:
   `event_log_correlator.py:18-24` hace `raise ImportError` a nivel de módulo,
   y `vigia/sift/__init__.py:19` lo importa incondicionalmente → sin
   defusedxml **ningún** motor V4 importa (memory, registry, disk, network,
   mobile vía `vigia.sift.*`, el orquestador entero). Reproducido en este
   entorno: `from vigia.sift.sift_orchestrator import ...` → ImportError.
2. **T-2 (nuevo): `defusedxml` está en `requirements.txt:43` y
   `pyproject.toml:41` pero NO en `requirements-ci.txt`** — un entorno
   instalado con requirements-ci (como este) arranca sin él. Es el gatillo
   concreto que mantiene vivo el bug.
3. **Mitigación parcial ya vigente:** post P0-A el shim captura el ImportError
   → `_error_result` → `PIPELINE_ERROR` → ABSTAIN exit 4 (ya no exit 0
   benigno). El bundle M57-PAT lo muestra: narrativa `[ERROR] ...defusedxml
   es obligatorio...`. Honesto, pero se pierde el 100% del análisis por una
   lib que solo necesita el parser XML.

**Fix propuesto (P1, bajo riesgo):**
- (a) Agregar `defusedxml>=0.7.1` a `requirements-ci.txt` (1 línea).
- (b) En `event_log_correlator.py`: degradar el `raise` a import guarded
  (`ET = None`) y que `analyze()` marque `.evtx/.xml` como
  `UNANALYZED_ARTIFACT` cuando falte (patrón ya existente para la lib `Evtx`,
  P1-E) — un parser XML ausente deshabilita SOLO el parseo XML, no los 14
  motores. La protección XXE se mantiene: sin defusedxml no se parsea XML,
  nunca se cae a `xml.etree`.
- (c) Test de regresión: `vigia.sift` importable con defusedxml simulado
  ausente (monkeypatch de sys.modules), evtx → unanalyzed → ABSTAIN.

### B-026 — prior_trust sin validar en el scorer — VIGENTE, fix trivial

Verificado en `vigia/core/vigia_scorer.py:282-295`: `raw_score` recibe
`isfinite` + clamp [0,1] (`:282-284`), pero dos líneas después
`prov_trust = a.get("prior_trust", 1.0)` entra **sin validación** a
`effective = prov_trust * epc_factor * temp_factor`. Un `prior_trust`
negativo/NaN/∞ produce trust efectivo imposible (score negativo, NaN
propagado al veredicto).

**Fix propuesto (P1, trivial):** replicar el patrón de `raw_score` exacto:
```python
if not isinstance(prov_trust, (int, float)) or not math.isfinite(prov_trust):
    prov_trust = 1.0
prov_trust = max(0.0, min(1.0, prov_trust))
```
más 3 tests (negativo, NaN, >1). Cero riesgo: solo rechaza valores que hoy
producen estados imposibles.

### B-027 — is_conclusive=True con ABSTAIN_DETECTED — VIGENTE, fix trivial

Verificado en el shim: `sift_orchestrator.py:606` (EBS:
`"is_conclusive": avg > Fraction(33, 100)`) y `:794` (vol3:
`avg > Fraction(3, 2)`) — ninguno mira la hipótesis. Un caso
`ABSTAIN_DETECTED` con scores individuales altos sella la contradicción
lógica "no puedo formar opinión" + "estoy seguro". Bajo cross-examination es
indefendible.

**Fix propuesto (P1, trivial):** en ambos puntos,
`is_conclusive = (avg > umbral) and hypothesis not in {"ABSTAIN_DETECTED", "UNDETERMINED", ...}`
(o directamente `and "ABSTAIN" not in hypothesis`). Además un guard central en
`_seal_bundle` (vigia_agent) que degrade `is_conclusive` a False cuando el
`agent_verdict` final sea ABSTAIN — cierra la clase entera, no solo estos dos
puntos. Tests con `expected_verdict=ABSTAIN` + scores altos.

### B-028 — is_conclusive solo actúa en MALICE — VIGENTE, decisión de diseño

Verificado: el único consumidor con efecto es el floor de alerta
(`vigia_agent.py`, bloque `_is_conclusive and "MALICI" in ...`). Para
INTENT/SUSPICION/NOISE el flag se sella pero no cambia nada.

**Propuesta (P2):** definir la semántica una vez: `is_conclusive` participa en
`classify_agent_verdict` ya (gate `<3 and not is_conclusive`), así que NO está
completamente muerto — actualizar la entrada del tracker con ese hecho y
decidir: (a) extender el floor de alerta a INTENT conclusivo (simétrico,
barato), o (b) documentar que el flag es informativo fuera de MALICE. Sin
urgencia forense: no produce veredictos incorrectos, produce un campo
sub-utilizado.

### B-016 — validación de formato de memoria — PARCIALMENTE MITIGADO

El adaptador vol3 del shim ya detecta el caso VMware/no-RAM
(`sift_orchestrator.py:636-668`: `InvalidAddressException`, `no valid kernel`…
→ `FORMAT_NOT_SUPPORTED` → ABSTAIN). Lo que sigue faltando es la validación
en `memory_forensics.py` (el motor V4) — pero ese motor requiere `vol` binario
y en modo agente el camino real es el adaptador. **Propuesta (P2):** portar el
mismo detector de stderr al motor V4, o degradar la severidad de la entrada a
"mitigado en el camino operativo, pendiente en motor V4".

### B-018 — timeout vol3 en dumps ≥4 GB — PARCIALMENTE MITIGADO

Timeouts fijos verificados (`sift_orchestrator.py:624-713`: 120/300/300/600s).
Post P1-D, si TODOS los plugins timeoutean → `UNANALYZED_ARTIFACT` → ABSTAIN
(honesto, no benigno). Lo que falta es poder completar el análisis.
**Propuesta (P2, acotada):** `VIGIA_VOL3_TIMEOUT` (env var, multiplicador) +
escalado por tamaño de imagen (`stat().st_size // GB * factor`), y registrar
en `pipeline_meta` el timeout usado. Sin cambio de veredicto para casos
actuales.

### B-013 — LOG_VS_MEMORY con raw_score bajo — decisión de diseño pendiente

Sin cambios desde su apertura. **Propuesta (P2):** umbral mínimo de
`raw_score` para que una golden rule dispare (p.ej. ambos artefactos
≥ Fraction(3,10)), documentado como parámetro CAIE con justificación — o
cerrar como "por diseño: la contradicción estructural importa más que la
magnitud". Requiere decisión de Anna, no código complejo.

### B-025 — frontera Fraction/float del scorer — SUBSUMIDO por L-040 §4

La investigación pedida en B-025 ya existe: `AUDITORIA_L040_LIKELIHOOD_RATIO.md`
§4 mapea los 7 paths float (U1-U7) con su estado de cobertura. **Propuesta:**
cerrar B-025 referenciando esa auditoría y abrir un único ítem consolidado
"de-floateo por tablas" con prioridades: **U7 primero** (cuantizar antes de
sellar `record_hash` — reproducibilidad cross-plataforma bit-52, patrón ya
resuelto en `security.py` P1-005), después U3 (trust_fusion exp → tabla como
`_EXP_NEG2_TABLE`), y el resto documentado como tolerado (~1 ulp, sin
acumulación — medido).

### B-010 / B-029 — housekeeping

B-010 (migrar forensic_technical_detector a SemioticDetectorV2): TODO de
mantenimiento sin impacto de veredicto — mantener abierto con prioridad P3.
B-029: la propia entrada dice "documentation only, no patch needed" —
**cerrable ya** con una línea de resolución.

### B-041b — CAIE no retroalimenta el veredicto — DIFERIDO con precondición cumplida

La condición que lo bloqueaba ("ForensicAdapter no propaga acquisition
metadata") se resolvió (L-037 FIXED). La segunda condición sigue: los
artefactos del agente son mono-capa (`log_entry`) → 0 fracturas cross-layer →
upgrade automático sería dead code. **Propuesta (P2):** re-evaluar después de
B-052-P2 (que introduce multi-capa mobile) y de L-037b; hasta entonces,
mantener DIFERIDO con esa dependencia explícita.

---

## 2. Verificación de los pendientes de KNOWN_LIMITATIONS

### L-023 — write del bundle no atómico (SEC-04) — **P0 declarado, sigue abierto** 

Verificado: `bundle_builder.py:241` sigue siendo `open(path, "w")` directo —
sin mkstemp, sin fsync, sin os.replace. La entrada dice "P0 — fix scheduled
post-hackathon" (2026-06-09, hace ~3 semanas). Nota atenuante: el camino del
agente (`vigia_agent.py main()`) SÍ re-verifica el digest contra disco
post-write (fix P2-8), pero `bundle_builder` (Mode 4/API) no.

**Fix propuesto (P1, patrón estándar):**
```python
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
with os.fdopen(fd, "w", encoding="utf-8") as f:
    f.write(text); f.flush(); os.fsync(f.fileno())
os.replace(tmp, path)
# hash re-computado desde disco después del replace
```
más test de igualdad hash-en-memoria vs hash-en-disco. Riesgo bajo; es el fix
que la propia entrada ya diseñó y nunca se aplicó.

### L-039 — tshark ausente + **T-3 (nuevo): un pcap corrupto mata el caso entero**

Verificado en el shim (`sift_orchestrator.py:272-281`): el fallo de parseo
pcap hace `raise`, que cae al `except` global de `analyze()` →
`_error_result` → **PIPELINE_ERROR para TODO el caso**. En evidencia mixta
(pcap + evtx + hives), un solo pcap corrupto o la ausencia de tshark descarta
también el análisis de los demás artefactos que SÍ podían procesarse.

**Fix propuesto (P1, patrón F7 ya existente):** reemplazar el `raise` por
log + señal sintética `PCAP_UNANALYZED` (unanalyzed=True, con el error) y
continuar con el resto de la evidencia. El veredicto degrada a ABSTAIN solo si
no queda nada más (vía N8/F7 ya implementados). Test: caso mixto con pcap
corrupto → evtx igual se analiza.

### L-037b — base_trust hardcodeado en ForensicAdapter — VIGENTE

Verificado: `forensic_adapter.py:150` `base_trust=1.0` fijo; el
`ARTIFACT_RELIABILITY` que cada motor declara en su metadata
(`artifact_reliability`, p.ej. `macos_forensics.py:207`) no se propaga a CAIE.
**Fix propuesto (P2, acotado):**
`base_trust=float(Fraction(meta.get("artifact_reliability", "1")))` con clamp
[0,1] y fallback 1.0 — 3 líneas + test. Requiere corrida de corpus (mueve
composite scores CAIE), por eso P2 y no P1.

### L-024 — `/mnt` genérico en la allowlist — VIGENTE, decisión corta

`vigia/sift/sift_orchestrator.py:107` sigue con `Path('/mnt')`. Con P0-B
resuelto (VIGIA_EVIDENCE_DIR entra a la allowlist), `/mnt` genérico ya no es
necesario para operar. **Propuesta (P2):** restringir a `/mnt/vigia` +
`/mnt/ewf*` (los puntos de montaje que la doc usa) o directamente removerlo —
el operador que monta en otro lado exporta VIGIA_EVIDENCE_DIR. Riesgo: casos
de usuarios que montan en /mnt/otra-cosa sin exportar la var → PathGuard
reject, que post-F7 ya es visible (señal unanalyzed), no silencioso.

### L-041 — análisis SMS limitado a keywords — por diseño, mantener

Requiere NLP semántico o léxicos por dominio. Sin cambio propuesto más allá de
documentación (ya está). P3.

### Limitaciones de diseño correctamente documentadas (no tocar)

L-001..L-018 (ataque perfecto, señal ahogada, ausencia de logs, umbral vs
ambigüedad, mono-fuente≠MALICE, etc.), L-027 (Terceridad stub en pipeline.py
— `consistency_score=1.0`, documentado), L-030/L-031 (dos caminos de sellado),
L-020/L-022. Son el scope Daubert declarado; el valor está en que sigan
documentadas, no en "arreglarlas".

---

## 3. Pendientes de las auditorías de esta rama (no trackeados aún)

| ID origen | Ítem | Estado | Propuesta |
|---|---|---|---|
| FN P0-C | Hives amcache/shellbag/usb: stubs honestos (ABSTAIN) | vigente | Mantener; implementar con `regipy` + hives de test cuando haya evidencia real que lo exija (P3) |
| FN P2-A / L-033 / L-034 | Cadena de atenuación gamma×FRS hunde z legítimos | vigente | **Tanda C**: no tocar sin ≥20 señales reales con ground truth (regla L-033). Diseñar primero el dataset de calibración |
| FN P2-C | Fuga `expected_verdict` en adaptador EBS | retenida deliberadamente | Rediseño mayor (separar etiqueta de scoring sin regresar el corpus). Tanda C |
| FN P2-D | `provenance_collapsed` → NOISE directo (no ABSTAIN) | vigente | Fix de 1 línea (NOISE→ABSTAIN) + corrida de corpus. Candidato a Tanda A si el corpus no flipea |
| FN P2-E | UnifiedTimeline con timestamps=0 | vigente | Poblar `metadata["timestamp"]` en los `to_signal()` de los motores (acotado, sin cambio de veredicto — el timeline es señal derivada post-F5). Tanda B |
| Robustez N11 | Metabolic/Behavioral muertos en modo agente (`event_stream` nunca se pasa) | vigente | Decisión: generar event_stream desde los eventos evtx ya parseados, o documentar "solo Mode 4". Tanda B |
| L-040 F-L040-6 | Fallback de texto muerto (`from run_pipeline import` — módulo inexistente) | vigente | O corregir el import a `vigia.scripts.run_pipeline` (si se quiere la red) o eliminar el fallback y devolver ABSTAIN directo con narrativa clara. Tanda A (elimina código muerto que aparenta ser red de seguridad) |
| L-040 U1-U7 | Paths float restantes | vigente | Consolidar con B-025 (ver arriba): U7 primero, U3 después. Tanda B |
| B-052-P2 | Granularidad por dominio + ruteo V4 mobile | pendiente | Tanda C (cambia veredictos mobile; requiere corpus) |
| AUDIT_NARRATIVAS P1 | NROMANOFF sealed report con anchor contradictorio | **RESUELTO por eliminación** — `vigia_output/` ya no existe (commit "remove fabricated LLM-generated report") | Cerrar el hallazgo en el tracker (T-4) |
| AUDIT_NARRATIVAS P2 | Executive summaries NPS-2010/2014 sin matiz de PIPELINE_ERROR | vigente (docs) | Añadir la frase correctiva a ambos reports (solo docs). Tanda A |

---

## 4. Hallazgos NUEVOS de este triage

| ID | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| **T-1** | Import duro de defusedxml mata todo `vigia.sift` (14 motores), no solo event logs | P1 | `event_log_correlator.py:18-24` + `vigia/sift/__init__.py:19` `[REPRODUCIDO]` |
| **T-2** | `defusedxml` ausente de `requirements-ci.txt` (sí está en requirements.txt/pyproject) — gatillo real de B-017 en entornos CI | P1 | `grep defusedxml requirements-ci.txt` → vacío `[REPRODUCIDO en este entorno]` |
| **T-3** | `raise` en el parseo pcap del shim aborta el caso COMPLETO (evidencia mixta pierde también los artefactos sanos) | P1 | `sift_orchestrator.py:279-281` |
| **T-4** | El hallazgo crítico de AUDIT_NARRATIVAS (NROMANOFF integrity anchor) quedó resuelto por eliminación del archivo — cerrable | — | `vigia_output/` inexistente |
| **T-5** | `is_conclusive` de B-027 tiene un tercer punto no listado: la ruta mobile lo deriva de `max_z>3` (correcto post-F6) — la entrada del tracker cita líneas viejas (195/340 → hoy 606/794) | doc | `sift_orchestrator.py:606,794` |

---

## 5. Matriz priorizada y plan propuesto

### Tanda A — fixes acotados, alto retorno, riesgo bajo (~1 día)

| # | Ítem | Fix | Esfuerzo | Riesgo |
|---|---|---|---|---|
| A1 | B-017 + T-1 + T-2 | requirements-ci + import guarded + unanalyzed | 2-3 h | bajo (patrón P1-E existente) |
| A2 | B-026 | clamp de prior_trust (patrón raw_score) | 30 min | nulo |
| A3 | B-027 | is_conclusive respeta hipótesis ABSTAIN + guard central en _seal_bundle | 1 h | bajo |
| A4 | T-3 / L-039 | pcap: raise → señal PCAP_UNANALYZED + continuar | 1 h | bajo (patrón F7) |
| A5 | L-023 | write atómico en bundle_builder (mkstemp+fsync+replace) | 1-2 h | bajo |
| A6 | F-L040-6 | eliminar/corregir fallback de texto muerto | 30 min | nulo |
| A7 | Housekeeping tracker | cerrar B-029, actualizar B-016/B-018 a "parcialmente mitigado", cerrar B-025 → referencia L-040 §4, cerrar T-4 | 30 min | nulo |

Validación de la tanda: suite completa + corpus 198 + los tests nuevos de cada fix.

### Tanda B — decisiones de diseño con propuesta concreta (requieren OK de Anna)

| # | Ítem | Decisión a tomar |
|---|---|---|
| B1 | B-028 | extender floor de alerta a INTENT conclusivo vs documentar flag informativo |
| B2 | B-013 | umbral mínimo de raw_score para golden rules vs cerrar por diseño |
| B3 | L-024 | restringir `/mnt` → `/mnt/vigia*` vs remover |
| B4 | L-037b | propagar artifact_reliability a base_trust CAIE (+corrida de corpus) |
| B5 | N11 | event_stream desde evtx vs documentar "solo Mode 4" |
| B6 | P2-E | poblar timestamps en to_signal() (timeline útil) |
| B7 | U7/U3 (L-040) | cuantizar record_hash + tabla exp en trust_fusion |
| B8 | P2-D | provenance_collapsed → ABSTAIN (corpus primero) |

### Tanda C — calibración con ground truth (NO tocar a ciegas)

- P2-A / L-033 / L-034 (gamma×FRS): diseñar dataset de ≥20 señales reales
  etiquetadas antes de mover un solo factor.
- P2-C (fuga expected_verdict): rediseño del adaptador EBS con recalibración.
- B-052-P2 (granularidad mobile): cambia todos los veredictos mobile.
- B-041b (CAIE→veredicto): depende de B-052-P2 + L-037b.
- L-041 (SMS semántico): requiere léxicos/modelo.

### Qué NO hacer

- No "arreglar" L-001..L-018, L-027, L-030/L-031: son el scope Daubert
  documentado; su valor probatorio está en la honestidad de la declaración.
- No tocar gamma (L-033) ni el leak (P2-C) sin el dataset de Tanda C — el
  intento anterior regresó el corpus de 198/198 a 60/198.

---

## 6. Limitaciones de este triage

1. Las verificaciones son puntuales (grep + lectura + reproducciones cortas),
   no corridas end-to-end por ítem; B-013/B-028 se verificaron sobre la
   entrada + el punto de código citado, sin reconstruir el escenario completo.
2. No se auditó `engine/` (likelihood_engine paralelo usado por
   tests/integration) ni los scripts `apply_b0*.py` residuales — candidatos a
   limpieza pero fuera del alcance de veredicto.
3. Los esfuerzos estimados asumen los patrones ya existentes en el repo
   (_safe_engine, F7 unanalyzed, P1-E, P2-8) — son reutilización, no diseño
   nuevo.

---

*Triage 2026-07-03 — trece abiertos verificados, cinco hallazgos nuevos, y un
plan en tres tandas: primero lo barato que protege veredictos, después las
decisiones, y al final lo que necesita datos para no romper lo que ya funciona.*
