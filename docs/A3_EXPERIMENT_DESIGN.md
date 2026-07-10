# A3_EXPERIMENT_DESIGN.md — Diseño del experimento de calibración gamma×FRS

> **Estado: DISEÑO — NO EJECUTABLE HOY.** Este documento especifica el
> experimento que se correrá CUANDO exista el dataset que exige la regla
> L-033 (≥20 señales reales etiquetadas, con ambas polaridades). Hoy no
> existe: hay 7 señales reales, todas de casos MALICE. **Cero código tocado
> en esta sesión** — es investigación pura (ítem A3 del
> `docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md`, Fase 2).
>
> Tag de restauración de la sesión: `pre-a3-experiment-design-20260709-194707`.

---

## 0. El bloqueo, cuantificado

### 0.1 Inventario real de señales gamma-relevantes (2026-07-09)

Señales del corpus con `evidence_type ∈ {event_log, windows_event_log}` —
la clase de evidencia que la cadena de atenuación gamma castiga y que L-033
identifica como fuente de falsos negativos:

| Caso | evidence_type | Señales | Expected | Origen |
|------|---------------|---------|----------|--------|
| `VIGIA-MAGNET-2022-WINDOWS` | `windows_event_log` | 4 (EVTX-SEC-001 cuenta backdoor, EVTX-SYS-001 TermService, ZeroTier 7045, reset Administrator 4724) | MALICE | Magnet CTF 2022, imagen de disco analizada en Mode 2 |
| `VIGIA-REAL-SRL-DC-CDRIVE` | `event_log` | 3 (ScriptBlock PowerShell, WinRM 43MB, Security.evtx 235MB + 9 archives) | MALICE | Caso real SRL, único disco real del corpus |
| **Total** | | **7** | **7/7 MALICE** | |

Consecuencias estadísticas del inventario:

1. **Polaridad única.** No existe NINGUNA señal `event_log`/`windows_event_log`
   con ground truth benigno. Cualquier ajuste de gamma que "recupere" las 7
   señales MALICE es trivialmente óptimo contra este dataset — y ciego al
   costo en falsos positivos, que es exactamente el riesgo que el gamma fijo
   protege (L-001, `BREAK_006`: la falsa bandera con logs fabricados).
2. **Dos casos = dos clusters.** Las 7 señales no son independientes: comparten
   caso, atacante, adquisición y analista. El "n" efectivo es ~2, no 7.
3. **Regla L-033 vigente:** no tocar gamma sin ≥20 señales reales etiquetadas.
   Este documento no la relaja; especifica qué hacer cuando se cumpla.

### 0.2 La cadena bajo estudio (referencia exacta de código — solo lectura)

La "cadena de atenuación gamma×FRS" son las etapas 4 y 5 de
`SIFTOrchestrator` (`vigia/sift/sift_orchestrator.py`):

```
z_raw  (señal del módulo SIFT, escala sigma)
  │  etapa 4 — GAMMA:      vigia/sift/sift_orchestrator.py:642-676
  │    z_post_gamma = gamma(evidence_type, metadata) × z_raw
  │    · tabla fija:        _math_utils.py:295-307  (apply_artifact_reliability)
  │        event_log=3/5, windows_event_log=7/10, registry=7/10,
  │        memory=19/20, mft=4/5, network=3/4, …
  │    · dinámica EVTX:     _math_utils.py:314-364  (apply_artifact_reliability_dynamic, L-038)
  │        gamma = 3/5 + (1 − 3/5) × chain_factor × score_factor, cap 19/20
  │        chain_factor = min(1, n_chains/100)
  │    · metadata sellada:  z_original, gamma_applied, gamma_type
  │  etapa 5 — FRS:         sift_orchestrator.py:691-697
  │    grupos de redundancia por entidad (pid/ip/tool) con delta_t=60s
  │    señales no dominantes del grupo: z × 1/(1+n_redundant)
  │                                     (_math_utils.py:399-427, apply_frs)
  ▼
z_post_frs → AbductiveReasoner: _Z_ACTIVE=3/2, _Z_CRITICAL=3/1
             (vigia/inference/abductive_reasoner.py:63-64)
```

El caso canónico de L-033: `z_raw=3.2` (343 cadenas PASS_THE_HASH,
composite 19/20) × gamma 0.60 = **1.92** — cae de CRITICAL (≥3.0) a apenas
ACTIVE (≥1.5). Con la dinámica L-038 ya implementada, 343 cadenas saturan
`chain_factor=1` y el gamma sube a ~0.95×score_factor — pero las constantes
de esa curva (`threshold_n=100`, base 3/5, cap 19/20) **nunca fueron
calibradas contra datos**: son diseño a priori. Son parte del espacio de
parámetros del experimento.

**Interacción gamma×FRS que el experimento debe medir y que ningún análisis
aislado de gamma ve:** la dinámica L-038 premia la corroboración
(`n_chains`↑ → gamma↑), pero FRS castiga la redundancia (misma entidad en
60s → z÷(1+n)). Eventos corroborantes del mismo pid/ip pueden ser
bonificados por gamma y luego divididos por FRS. La cantidad observable del
experimento es la **atenuación total** `A = z_post_frs / z_raw`, no solo el
factor gamma.

### 0.3 Parámetros libres (espacio del experimento)

| Parámetro | Valor actual | Fuente |
|-----------|--------------|--------|
| `gamma[event_log]` | 3/5 | `_math_utils.py:299` |
| `gamma[windows_event_log]` (base dinámica) | 3/5 → cap 19/20 | `_math_utils.py:358-363` |
| `threshold_n` (saturación de corroboración) | 100 cadenas | `_math_utils.py:351` |
| cap dinámico | 19/20 | `_math_utils.py:363` |
| FRS factor | 1/(1+n_redundant) | `_math_utils.py:416` |
| `delta_t` agrupación FRS | 60 s | `sift_orchestrator.py:692` |

Alcance A3: **solo los cuatro primeros** (la clase event_log). FRS
(`1/(1+n)`, `delta_t`) se mide pero no se ajusta en este experimento — si los
datos muestran que el problema dominante es FRS y no gamma, eso es un
resultado (y abre un ítem nuevo), no una licencia para ajustar dos capas a
la vez con n=20.

---

## 1. Unidad de análisis y definiciones

**Unidad = señal**, no caso:

```
señal := (case_id, artifact_id, evidence_type,
          z_raw,                    # escala sigma, PRE-gamma (metadata z_original)
          metadata_corroboración,   # n_chains, composite_score
          ground_truth_polarity,    # ∈ {malicious, benign} — POR SEÑAL
          ground_truth_source)      # cita verificable (answer key, scenario doc)
```

Advertencia de escala: en `data/cases/converted/*.json` los `z_score`
serializados están normalizados a [0,1] (p.ej. 361/400) — **no** son la
escala sigma del orchestrator. El dataset de calibración debe capturar
`z_raw` en escala sigma desde `metadata.z_original` de bundles Mode 1
re-ejecutados, nunca desde la serialización del corpus convertido.

Métricas por señal, a los dos umbrales del reasoner (T ∈ {3/2, 3/1}):

- **FN de atenuación:** `polarity=malicious ∧ z_raw ≥ T ∧ z_post < T`
  (la cadena hundió una señal legítima — el defecto L-033).
- **FP de atenuación insuficiente:** `polarity=benign ∧ z_post ≥ T`
  (la cadena dejó pasar ruido/fabricación — el riesgo BREAK_006).

donde `z_post` se evalúa dos veces: `z_post_gamma` (aísla gamma) y
`z_post_frs` (cadena completa).

**Etiquetado de polaridad por señal (no por caso):** un caso MALICE contiene
señales benignas (logons legítimos del admin en Data Leakage Case) y un caso
benigno puede contener anomalías reales sin intención. La polaridad la fija
la **fuente externa de ground truth** (answer key numerada, scenario guide),
citada señal por señal en `ground_truth_source`. Señal sin cita externa
verificable → fuera del dataset (doctrina L-037: proveniencia real, no
fabricada).

---

## 2. Método estadístico (pregunta 1 del encargo)

### 2.1 Decisión: NO regresión logística como estimador — grid search racional restringido

La opción "regresión logística de ground truth sobre `z_post_gamma`" se
evaluó y se descarta **como estimador** por cuatro razones:

1. **n y dependencia.** Con 20–40 señales agrupadas en ~6–10 casos, las
   señales intra-caso están correlacionadas (mismo atacante, misma
   adquisición). Un MLE logístico que las trate como i.i.d. produce errores
   estándar inválidos; el remedio (GEE / errores cluster-robustos / Firth
   ante separación completa, que con n=20 y buen detector es *probable*)
   añade maquinaria que este n no puede sostener.
2. **El parámetro de interés no es P(malicious|z).** Gamma es un factor
   multiplicativo dentro de una cadena de decisión por umbrales fijos. La
   pregunta operativa es "¿qué gamma minimiza FN sin crear FP a los umbrales
   3/2 y 3/1?" — una pregunta de separación a umbral, no de probabilidad
   calibrada. Ajustar una sigmoide para después re-derivar un umbral es un
   rodeo con varianza extra.
3. **Determinismo (Invariante 4).** El pipeline de veredicto es aritmética
   `Fraction`. Un gamma salido de un MLE float (`0.6473921…`) no vive en la
   rejilla racional del scorer. Todo candidato debe nacer en la rejilla.
4. **Precedente B-069.** La calibración "elegante" por analogía ya fue
   rechazada por el gate comparativo (70.8→70.4%). La lección: el estimador
   importa menos que el gate; elegir el estimador más simple que el gate
   pueda auditar.

**Estimador elegido: búsqueda exhaustiva sobre rejilla racional con objetivo
lexicográfico.**

```
Rejilla:   Γ = {10/20, 11/20, …, 19/20}                (por evidence_type)
           para windows_event_log dinámico, además:
           threshold_n ∈ {25, 50, 100, 200}, cap ∈ {17/20, 18/20, 19/20}

Objetivo lexicográfico (en este orden, sin ponderaciones):
  (1) FP de atenuación insuficiente (señal-nivel, ambos umbrales) == 0 nuevos
  (2) minimizar FN de atenuación (señal-nivel, ambos umbrales)
  (3) a igualdad: el gamma MÁS BAJO (el candidato más conservador que
      logra el mismo FN — protege BREAK_006 por construcción)
```

La rejilla completa tiene |Γ|×4×3 = 120 combinaciones para el tipo dinámico
y 10 para `event_log` fijo — exhaustivamente evaluable, determinista,
reproducible con un script stdlib. Sin optimizador, sin semilla, sin float.

### 2.2 Validación: leave-one-case-out (LOCO), agrupado por caso

Con ~6–10 casos, el único remuestreo honesto es dejar fuera **un caso
entero** (todas sus señales) por fold — dejar fuera señales sueltas filtra
información del caso al fold. Para cada fold se repite el grid search y se
registra el gamma ganador. Criterio de estabilidad en §3 (Gate 4).

### 2.3 Regresión logística: SÍ, pero como diagnóstico offline

Fuera del camino de veredicto (script de análisis, float permitido ahí):

- `logit P(malicious) = a + b·z_post_gamma`, errores estándar
  cluster-robustos por `case_id` (o Firth si hay separación completa).
- Se exige: `b > 0` con IC95% que excluya 0, y AUC(z_post_gamma) ≥
  AUC(z_raw) − 0.05 — es decir, la atenuación calibrada no destruye el
  ordenamiento que el detector ya tenía.
- Si el diagnóstico contradice al grid (b no significativo, o AUC cae), el
  resultado del experimento es **ABSTAIN**: se documenta y NO se aplica
  ningún cambio. La contradicción señala que el dataset aún no soporta la
  decisión — más datos, no más ajuste.

### 2.4 Poder estadístico — declarado por adelantado, no descubierto después

Con el mínimo L-033 (20 señales, digamos 12 malicious / 8 benign):

- **Cota FP (regla de tres):** 0 FP observados sobre 8 señales benignas →
  límite superior 95% de la tasa FP real ≈ 3/8 = **37%**. Es una cota
  débil y hay que decirlo: a n=20 el experimento solo detecta
  descalibración *gruesa*.
- Por eso el criterio de aceptación (§3) es **comparativo y conservador**
  ("no empeorar nada, mejorar algo"), no "óptimo global". Idéntica doctrina
  que B-076 (+10 corregidos, 0 regresiones) y opuesta a lo que B-069 castigó.
- Objetivo recomendado, no mínimo: **≥30 señales, ≥10 benignas, ≥5 casos por
  polaridad** (alcanzable con las fuentes de §4). Con 10 benignas la cota
  FP baja a ~26%; con 20, a ~14%.

---

## 3. Criterio de aceptación numérico (pregunta 2 — patrón A4/B-069/B-076)

El cambio de gamma se aplica **solo si pasan los CINCO gates**. Cualquier
gate en rojo → `NOT APPLIED`, resultado negativo documentado en el tracker
(precedente B-069), working tree revertido al tag de restauración.

| Gate | Criterio numérico exacto | Baseline hoy |
|------|--------------------------|--------------|
| **G1 — señal-nivel** | Sobre el dataset de calibración: `FN_atenuación(post) < FN_atenuación(pre)` en al menos 1, **y** `FP_nuevos(post) == 0` a ambos umbrales (3/2 y 3/1), medido en `z_post_gamma` y en `z_post_frs` | pre por medir al congelar dataset |
| **G2 — corpus comparativo completo** | Corrida A/B sobre los 199 casos: `fixed ≥ 1`, `broken == 0`, accuracy estrictamente mejor; **0 flips no explicados** (todo flip listado caso a caso) | 166/199 |
| **G3 — invariantes** | Suite completa verde (sin regresión sobre baseline); pins de monotonicidad M2 (B-081) verdes; `BREAK_006` y `BREAK_010` siguen **sin** emitir MALICE; todos los gammas resultantes son `Fraction` de la rejilla /20 (cero floats en el camino de veredicto) | 1098 passed (2026-07-08) |
| **G4 — estabilidad LOCO** | El gamma ganador es idéntico o ±1 paso de rejilla (1/20) en ≥80% de los folds leave-one-case-out | n/a |
| **G5 — diagnóstico** | §2.3: `b > 0` significativo con clusters por caso; AUC no cae >0.05 | n/a |

Notas de doctrina:

- G2 es **el** gate (regla de trabajo vigente: "gate comparativo obligatorio
  para todo cambio que toque veredictos"). G1/G4/G5 existen para que un
  cambio no llegue a G2 por azar de un dataset chico.
- "Downgrade no es fracaso": si el grid concluye que el gamma actual (3/5)
  ya es el óptimo de la rejilla, ese resultado **cierra L-033 como
  calibración confirmada** — mismo valor probatorio que un cambio.
- El experimento se corre una vez por congelamiento de dataset. Si entra un
  caso nuevo después, se re-congela y se re-corre completo (nada de ajuste
  incremental).

---

## 4. Datasets forenses públicos candidatos (pregunta 3 — solo fuentes reales existentes)

Restricción de partida: **no se fabrica nada.** Se evaluaron las fuentes que
el propio repo ya investigó (`docs/digital_corpora_complete_report.md`,
`docs/nist_cfreds_full_report.md`) más dos corpora específicos de event logs,
verificando por web disponibilidad y licencia (2026-07-09).

### 4.1 Tabla de evaluación

| Fuente | Event logs reales | Polaridad aprovechable | Ground truth | Licencia | Señales gamma-relevantes estimadas |
|--------|-------------------|------------------------|--------------|----------|-------------------------------------|
| **NIST CFReDS — Data Leakage Case (2015)** | Windows 7 → **EVTX** (PC del insider) | **Ambas**: exfiltración insider (malicious) + actividad legítima de cuentas `admin11`/`ITechTeam` y días previos al reclutamiento (benign) | Answer key pública de 60 preguntas (Q11-Q12: execution logs, on/off, logon/logoff con respuestas explícitas) | NIST, uso libre | 4–8 (`windows_event_log`, mixtas) |
| **Digital Corpora — M57-Patents (2009)** | Windows XP → **EVT** (imágenes diarias de varias máquinas, 4 semanas) | **Benigna dominante**: la mayoría de máquinas-día no contiene incidente — la mejor fuente de polaridad benigna en disco real que existe | Escenario documentado; redacted images y detective reports públicos; ⚠ instructor packet (respuestas finas) encriptado — verificar acceso antes de comprometer conteos | CC0 / sin restricciones (Digital Corpora ToU) | 6–12 (`event_log` benignas; 2–4 por máquina-día) |
| **Digital Corpora — Lone Wolf (2018)** | Windows 10 (1709) → **EVTX** + memoria + pagefile | **Benigna** para la cadena gamma: el ilícito del caso (planificación) vive en documentos/cloud; los event logs son operación normal del SO, sin intrusión ni anti-forense | Scenario guide de 115 pp. pública | CC0 / sin restricciones | 3–6 (`windows_event_log` benignas) |
| **NPS — nps-2009-domexusers (+redacted)** | Windows XP → EVT, dos usuarios simulados reales | **Benigna pura** (creado para tool-testing, sin PII, sin incidente) | Documentación NPS del experimento | Redistribuible explícitamente | 2–4 (`event_log` benignas). Precedente de ingesta NPS ya existe en el corpus (NPS-2010-EMAILS, NPS-2014-USB) |
| **NIST CFReDS — Hacking Case (2004)** | Windows XP → EVT | Maliciosa | Answer key pública (31 preguntas) | NIST, uso libre | 2–3 (`event_log` maliciosas) |
| **EVTX-ATTACK-SAMPLES (sbousseaden)** | **EVTX reales** producidos por Windows ejecutando técnicas ATT&CK (~300 muestras) | Maliciosa, granularidad por-técnica perfecta | Mapeo ATT&CK por archivo | ⚠ **GPL** — copyleft; ver §5.4 | 5–10 (subconjunto curado, `windows_event_log` maliciosas) |
| **OTRF Security-Datasets (ex-Mordor)** | EVTX/JSON de técnicas ejecutadas en lab, **incluye eventos benignos de fondo** capturados durante la simulación | **Ambas** (los eventos de fondo son benignos etiquetables; los de la técnica, maliciosos) | Metadata por dataset + script de simulación reproducible | Verificar LICENSE del repo al incorporar (código MIT; confirmar datasets) | 4–8 (mixtas) |

Descartados: LogHub (su dataset "Windows" es CBS.log, no event log de
seguridad), DARPA OpTC (telemetría eCAR, no EVTX — formato fuera del alcance
del parser), Nitroba (solo PCAP), M57-Jean (XP, máquina víctima — los EVT
existen pero el answer key no etiqueta eventos de log; aprovechable solo como
benigno débil).

### 4.2 ¿Desbloquea L-033? Sí — presupuesto de señales

Escenario conservador (mínimos de la tabla, sin EVTX-ATTACK-SAMPLES ni
Mordor si sus licencias no convencen):

```
malicious:  7 existentes + 2 (Hacking Case) + 4 (DLC)          = 13
benign:     3 (Lone Wolf) + 6 (M57-Patents) + 2 (domexusers)
            + 2 (DLC cuentas legítimas)                         = 13
total                                                           = 26  ✓ ≥20
casos:      2 existentes + 5 nuevos                             = 7 clusters
```

Cumple la regla L-033 con ambas polaridades y supera el objetivo recomendado
de §2.4 en señales benignas (13 ≥ 10 → cota FP ~21%). Con EVTX-ATTACK-SAMPLES
y Mordor, el brazo malicioso gana diversidad de técnica (hoy: 2 atacantes).

### 4.3 Advertencias honestas por fuente

1. **EVT ≠ EVTX.** XP produce EVT binario legacy; `python-evtx` no lo parsea
   (necesita `libevt`/`python-evt` o export previo). Las señales de
   M57-Patents/domexusers/Hacking Case alimentan el tipo `event_log`
   (gamma=3/5), NO `windows_event_log` — lo cual es deseable: hoy el tipo
   `event_log` tiene CERO señales con corroboración calibrable y es el que
   L-033 señala. Pero el costo de ingeniería del parser EVT debe presupuestarse
   antes de comprometer los conteos.
2. **Telemetría de laboratorio ≠ fabricación.** Los EVTX de
   EVTX-ATTACK-SAMPLES/Mordor son registros producidos por un Windows real
   ejecutando la técnica — datos reales con proveniencia declarable
   (`case_origin: lab_telemetry`, doctrina L-037: documentar la proveniencia
   real, jamás inventarla). Lo prohibido sigue prohibido: editar eventos,
   inventar timestamps, sintetizar z.
3. **Los conteos de la tabla son estimaciones** hechas sobre la documentación
   de cada escenario, no sobre corridas. El número real de señales lo fija la
   corrida Mode 1/Mode 2 sobre la evidencia — puede ser menor. El presupuesto
   de §4.2 usa los mínimos por esa razón.
4. **M57-Patents:** verificar qué resuelven los materiales públicos (detective
   reports, redacted images) sin el instructor packet encriptado. Si la
   polaridad benigna de una máquina-día no es certificable con material
   público, esa máquina-día queda fuera (regla de §1: sin cita externa, fuera).

---

## 5. Proceso de incorporación al corpus (pregunta 4)

### 5.1 Pipeline existente (sin cambios de código — es el camino ya construido)

1. **Adquisición:** descargar imagen/artefactos; SHA-256 de cada archivo
   ANTES de leer contenido (invariante 2); registrar URL, fecha, hash del
   download en la metadata del caso.
2. **Análisis:** correr Mode 1 (`vigia_agent.py --evidence … --case-id …`)
   sobre la evidencia real → bundle sellado con señales y `metadata.z_original`
   (el z_raw pre-gamma que el experimento necesita, §1).
3. **Conversión:** `scripts/convert_legacy_cases.py` / `convert_md_cases.py`
   → `data/cases/converted/<CASE>.json` con el esquema vigente.
4. **Metadata de adquisición:** completar según doctrina B-085/L-037
   (`scripts/complete_acquisition_metadata.py` como referencia de campos) —
   documentar proveniencia real; campos ausentes degradan trust honestamente,
   no se rellenan.
5. **Guardas:** el dedup guard R3-3 vigila las 5 `CASES_DIRS`; los stems
   nuevos no deben colisionar con `SKIP_STEMS`; validador schema-aware B-085
   en PASS antes de entrar al corpus.

### 5.2 Esquema por caso (el vigente, con los campos que A3 exige poblados)

```json
{
  "case_id": "VIGIA-CFREDS-DLC-2015",
  "case_name": "...",
  "description": "...",
  "expected_verdict": "MALICE | NOISE | ...",
  "schema_version": "<vigente>",
  "acquisition": {
    "source_url": "https://cfreds.nist.gov/all/NIST/DataLeakageCase",
    "download_sha256": "…",
    "download_date": "…",
    "license": "NIST public / CC0 / GPL(ver §5.4)"
  },
  "artifacts": [
    {
      "artifact_id": "EVTX-…",
      "evidence_type": "windows_event_log",
      "description": "…",
      "prior_trust": 0.95,
      "acquisition_hash": "sha256:…",
      "acquisition_tool": "python-evtx",
      "provenance_chain": ["sha256:…"],
      "metadata": {
        "ground_truth_polarity": "benign",
        "ground_truth_source": "CFReDS DLC answer key, Q12 (leakage-answers.pdf)",
        "z_original": "…"
      }
    }
  ]
}
```

Los dos campos nuevos (`ground_truth_polarity`, `ground_truth_source`) viven
en `metadata` de cada artifact: **metadata pasiva** que solo lee el script de
análisis del experimento. Ni el scorer ni el orchestrator los consumen — la
incorporación no toca el camino de veredicto, y ningún caso existente
requiere migración (ausencia del campo = señal no elegible para el dataset
de calibración, nada más).

### 5.3 Aporte por dataset (qué entra, en qué orden)

Orden por (beneficio de polaridad ÷ esfuerzo):

| # | Dataset | Esfuerzo | Aporta | Por qué en este orden |
|---|---------|----------|--------|------------------------|
| 1 | Lone Wolf | Bajo (EVTX nativo, 1 imagen, guía pública) | 3–6 benignas `windows_event_log` | Primera señal benigna EVTX del corpus; parser ya existe |
| 2 | CFReDS Data Leakage | Medio (3 imágenes, answer key densa) | 4–8 mixtas `windows_event_log` | Única fuente con ambas polaridades certificadas por answer key numerada |
| 3 | domexusers | Bajo-medio (EVT legacy) | 2–4 benignas `event_log` | Benigno puro, redistribuible, precedente NPS ya ingerido |
| 4 | M57-Patents | Alto (multi-máquina, EVT, verificar instructor packet) | 6–12 benignas `event_log` | Volumen benigno; entra después de validar el parser EVT con domexusers |
| 5 | Hacking Case | Bajo-medio | 2–3 maliciosas `event_log` | Diversifica atacantes del brazo malicioso |
| 6 | EVTX-ATTACK-SAMPLES / Mordor | Bajo por muestra | 5–10 maliciosas + fondo benigno | Solo si se resuelve §5.4; diversidad de técnica ATT&CK |

El experimento puede congelarse tras el ítem 4 (≥20 con ambas polaridades,
§4.2); 5–6 mejoran poder y diversidad.

### 5.4 Licencias — decisión requerida antes de ingerir el ítem 6

- Digital Corpora: ToU explícitos — libre para investigación, sin
  autorización previa; CC0 salvo material con copyright embebido en las
  imágenes. NIST CFReDS: datasets públicos de referencia. NPS: creado para
  redistribución. → Los ítems 1–5 son compatibles con el repo (Apache-2.0)
  registrando `acquisition.license` por caso.
- **EVTX-ATTACK-SAMPLES es GPL.** Fixtures GPL dentro de un árbol Apache-2.0
  es una mezcla que requiere decisión explícita de Anna. Alternativa limpia:
  NO versionar los .evtx — descarga en tiempo de preparación
  (URL + SHA-256 pineado en `acquisition`), el repo solo guarda hashes y el
  JSON convertido con las señales derivadas. Documentar la decisión en el
  tracker antes de ingerir.
- OTRF Security-Datasets: confirmar el LICENSE del repo al momento de
  incorporar (el código es MIT; verificar que cubre los datasets).

---

## 6. Protocolo de ejecución (cuando el dataset exista)

1. **Congelar** el dataset de calibración: lista explícita de
   (case_id, artifact_id, polarity, source) en
   `data/calibration_gamma_dataset_<fecha>.json`; SHA-256 del archivo en el
   tracker. A partir de aquí, ninguna señal entra ni sale.
2. **Tag de restauración** (`pre-a3-gamma-<timestamp>`), regla de trabajo
   vigente.
3. **Medir el "pre":** FN/FP de atenuación con los parámetros actuales
   (§1) — es el baseline de G1. Publicarlo ANTES de ver ningún candidato
   (pre-registro: evita elegir el gate después de conocer el resultado).
4. **Grid search** (§2.1) + LOCO (§2.2) con script offline nuevo y aislado
   (propuesto: `scripts/analysis/a3_gamma_experiment.py`, stdlib-only,
   `Fraction` en todo el camino de decisión; el diagnóstico §2.3 puede usar
   float/scipy porque no toca veredictos). El script NO importa el scorer
   para mutarlo: re-implementa la fórmula de la cadena leyendo las mismas
   constantes, y un pin de igualdad contra `_math_utils.py` verifica que no
   divergen.
5. **Gates G1–G5** (§3). Todo en verde → aplicar el cambio de constantes en
   `_math_utils.py` con test rojo primero, corrida comparativa sellada en el
   tracker (formato B-076). Cualquier rojo → `NOT APPLIED`, documentar
   (formato B-069).
6. **Cierre documental:** actualizar L-033 (y L-038 si la curva dinámica
   cambió), `BUGS_PENDIENTES(_EN).md` en el mismo commit, y el
   REFUTATION GATE LOG si algún veredicto de caso cambió de candidato.

### 6.1 Qué NO hace este experimento

- **No toca L-034** (agregación sub-umbral multi-fuente). Dependencia
  declarada: recalibrar gamma cambia cuántas señales quedan sub-umbral, es
  decir, cambia el *tamaño* del hueco L-034. El experimento lo **mide**
  (conteo de señales en [1.0, 1.5) pre/post) y lo reporta; arreglarlo es un
  rediseño de capa de agregación fuera de alcance.
- **No recalibra perfiles CAIE ni umbrales del scorer** — eso es A4 (re-fit
  conjunto, `vigia/core/fit_calibration.py`), con su propio gate.
- **No ajusta FRS** (§0.3).
- **No se ejecuta hoy.** Precondición dura: dataset congelado ≥20 señales,
  ambas polaridades, ≥3 casos por polaridad como mínimo absoluto (con menos
  clusters, LOCO no es informativo).

---

## 7. Referencias

Internas: L-033/L-033b/L-034/L-037/L-038 (`KNOWN_LIMITATIONS.md`); B-069
(gate negativo, patrón), B-076 (gate positivo, patrón), B-085 (validador de
adquisición) en `BUGS_PENDIENTES_EN.md`; Fase 2 del
`docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md`; inventarios previos de
datasets en `docs/digital_corpora_complete_report.md` y
`docs/nist_cfreds_full_report.md`; cadena de código:
`vigia/sift/_math_utils.py`, `vigia/sift/sift_orchestrator.py`,
`vigia/inference/abductive_reasoner.py`.

Externas (verificadas 2026-07-09):

- Digital Corpora — Terms of Use: https://digitalcorpora.org/about-digitalcorpora/terms-of-use/
- Digital Corpora — Lone Wolf 2018: https://digitalcorpora.org/corpora/scenarios/2018-lone-wolf-scenario/
- Digital Corpora — M57-Patents: https://digitalcorpora.org/corpora/scenarios/m57-patents-scenario/
- Digital Corpora — nps-2009-domexusers: https://corp.digitalcorpora.org/corpora/drives/nps-2009-domexusers
- NIST CFReDS — Data Leakage Case: https://cfreds.nist.gov/all/NIST/DataLeakageCase
- NIST CFReDS — Hacking Case: https://cfreds.nist.gov/all/NIST/HackingCase
- EVTX-ATTACK-SAMPLES (GPL): https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES
- OTRF Security-Datasets: https://github.com/OTRF/Security-Datasets

---

*A3_EXPERIMENT_DESIGN — 2026-07-09 | diseño pre-registrado; se ejecuta al
congelar el dataset L-033 | cero código tocado en esta sesión.*
