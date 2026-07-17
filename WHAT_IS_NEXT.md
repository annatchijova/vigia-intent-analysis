# WHAT_IS_NEXT.md — Estado real del proyecto y qué sigue

> **Actualizado: 2026-07-07.** El hackathon SANS FIND EVIL 2026 está cerrado;
> todo lo listado acá es track POST HACKATHON. Este documento reemplaza la
> versión anterior (que era solo el track teórico Magnani/Aliseda/Nishida —
> ahora §4, con sus claims corregidos: `resolve()` ya no está "ausente").
> Todo commit derivado de este documento se etiqueta `POST HACKATHON`.

---

## 0. Estado verificado hoy (2026-07-07)

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Corpus (batch agente) | **167/199** (R4-3/B-088 cerró BREAK-014: el drowning por volumen del mismo dominio ya no compra MALICE) | `results/agent_batch/_batch_summary.json` |
| Suite | **866 passed**, 1 skipped, 7 xfailed | corrida 2026-07-07 (excluye `tests/e2e`, que requiere sandbox SIFT del entorno) |
| Trackers | `BUGS_PENDIENTES.md` (ES) y `BUGS_PENDIENTES_EN.md` sincronizados hasta **B-084** | este commit |
| Última tanda cerrada | TANDAS 1–4, Fase 2 semantic_role, LaBestia, Q2/Q4, Round 2/2.1, Round 3, censo P0-001 + fixes adyacentes | B-077..B-084 |

> **Actualización 2026-07-17 (sesión de revisión abductiva de trackers):** la
> tabla de arriba quedó histórica. Estado vigente: corpus batch committeado
> **187/199** (2026-07-14, `results/agent_batch/_batch_summary.json`); gate
> vivo de B-136 Fase 3 **189/201** (2026-07-17); suite **1455 passed / 0
> failed** (registro B-136; en entornos sin `mcp` los módulos que lo importan
> se excluyen — L-045). Trackers ES/EN sincronizados hasta **B-137**.
> Cerrados desde la última edición de este documento: B-085..B-137 (detalle
> en trackers), incluidos B-097 (aplicado con firma de Anna el 2026-07-10),
> B-136 (Opción 1 en tres fases) y el cierre NOT ADOPTED de B-052-P2 (§1.2).
> Pendientes vigentes verificados contra código: B-010, B-111..B-113
> (candidatos), B-116 (pospuesto), B-122 (parcial), B-123/B-124 (pospuestos),
> B-129 (Fase 2 no antes de 2026-08-14), L-029/FW-009, L-033/A3, L-041/A7.

Trayectoria del corpus en la semana: 143 → 153 (B-076, umbral SUSPICION) →
165 (B-077, semantic_role) → 163 (B-081, monotonicidad con gate) → **166**
(Round 2.1, relabel de 3 etiquetas que codificaban la dilución).

### Cerrado del 2026-07-05 al 07 (detalle en trackers B-077..B-084)

- **B-084** — TANDAS 1–4 (AUDITORIA_FUGA_INDIRECTA): H1b, B-059/enfsi
  unificado, H4, H5, H1c — puerta de datos cerrada, corpus honesto 152/199.
- **B-077** — semantic_role (D1+D2): el agente ciego distingue rol semántico
  de la evidencia; +13 casos.
- **B-078** — LaBestia: 3 fallos encadenados del sandbox de búsqueda.
- **B-079** — Q2: eco_check fail-closed.
- **B-080** — Q4/L-023: escritura atómica en el camino primario
  (`vigia_agent.py`) y en `vigia/models/ebs.py` ×2; `.sha256` re-leído de disco.
- **B-081** — M2-1/M2-2 + Round 2.1: invariantes de monotonicidad del scorer.
- **B-082** — R3-1..R3-4: guard temporal TCV, canonicalización v2, assert de
  etiquetas del runner, orden causal en el verificador de cadena.
- **B-083** — Censo P0-001 de `float()` (37 sitios, veredicto: frontera de
  contrato sana) + 4 fixes adyacentes (timestamp WebKit, división entera,
  gamma racional, umbrales Fraction del reasoner).

---

## 1. Qué sigue, en orden

El orden hereda la economía de investigación del
`docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md` (bucle A–D–I), actualizado con lo
que ya se cerró desde entonces. La Fase 0 (sorpresas protegidas) y la Fase 1
(A1: agente ciego — cerrada por B-075 + B-076 + B-077) ya no están pendientes.

### 1.1 Higiene del corpus (Grupo D + secuela de R3-3) — primero, es precondición

1. ~~**Deduplicación física del corpus**~~ — **CERRADO (R3-3b + R3-3c,
   2026-07-07)**: etiquetas divergentes 0 (guard sobre las 5 CASES_DIRS);
   las 20 copias muertas byte-idénticas retiradas; los árboles fuente
   (`benign/`, `legacy/`: 36 schema-distinto + 13 variantes) se conservan
   deliberadamente — alimentan los conversores y el guard los vigila. El
   bundle `VIGIA_BREAK_001-010` excluido vía SKIP_STEMS (double-contaba y
   auto-pasaba). Bonus del test rojo: el substring de SKIP_STEMS se tragaba
   `VIGIA_BREAK_005_FALSE_CORRELATION` desde su creación — hoy entra al
   corpus y el agente lo acierta. Corpus 166/199 honesto (mismo número,
   denominador mejor).
2. ~~**Metadata de adquisición por lotes**~~ — **CERRADO (B-085, 2026-07-07)**:
   validador schema-aware (el 145/199 mezclaba defectos reales con falsos
   positivos del validador sobre artefactos narrativos) + lote aditivo honesto
   sobre 145 casos (`scripts/complete_acquisition_metadata.py`, doctrina
   L-037: documenta proveniencia real, no la fabrica). Validador
   **54→194/199 PASS**; corpus 166/199, 0 regresiones. Residuo con defectos
   reales de forma (5 casos: OWL-NEXUS5, NPS-2010-EMAILS ×2, NPS-2014-USB,
   CTF-2021-iOS) + 1 etiqueta a revisar en Tanda C (CTF-2021-iOS saltó
   NOISE→MALICE con expected UNKNOWN al subir el trust). La precondición de
   la Tanda C (A4) quedó satisfecha.

### 1.2 Doctrina y calibración (Grupo A / Tanda C — requieren decisión de Anna y/o ground truth)

> **Precondición Tanda C — CONSTRUIDA (2026-07-09).** El dataset de calibración
> a nivel señal existe: `data/signal_calibration_dataset_20260709.json`
> (generador `scripts/build_signal_calibration_dataset.py`, hash Daubert, test).
> Ver `docs/TANDA_C_SIGNAL_CALIBRATION.md`. Resultado medido, honesto:
> **A4 desbloqueado** (979 señales reales etiquetadas, ambas polaridades — L-033
> satisfecho para el re-fit de perfiles) pero **A3 sigue bloqueado** (solo 7
> señales gamma reales, todas MALICE — L-033 NO satisfecho para gamma). El
> bloqueo de A3 pasó de "no hay dataset" a "faltan ~13+ señales gamma reales con
> clase benigna": es adquisición de datos (más casos de disco crudo con
> `event_log` etiquetado), no ingeniería.

En orden de dependencia:

1. ~~**A2 / B-052-P2** — granularidad mobile/macOS~~ — **CERRADO 2026-07-10,
   NOT ADOPTED** por decisión sellada §9.4-LIM (L-051): SUSPICION es el techo
   doctrinal para casos mobile/macOS D3-only; la migración `to_signals()` no
   se adopta. Los pins de Grupo C (§1.3) quedan como arnés de regresión.
2. ~~**A5 / B-041b** — CAIE retroalimenta el veredicto~~ — **CERRADO**:
   B-041b superado por B-075/B-076 (ver tracker B-041); su prerequisito A2
   se cerró NOT ADOPTED.
3. **A4 / B-069** — re-fit de perfiles. **MEDIDO 2026-07-09: resultado NEUTRO,
   NO APLICADO.** Con el dataset (979 señales) se corrió el re-fit dataset-driven
   detrás del gate comparativo (`scripts/experiment_a4_profile_refit.py`, solo
   mide): **0 flips** (0 fixed / 0 broken) en las variantes realistas; la única
   palanca que mueve algo (subir `base_weight`) reproduce la inflación de B-069
   sin arreglar nada. Confirma B-069 con método independiente. `caie.py` NO
   tocado. Los errores restantes del corpus son estructurales, no de perfiles.
   Ver `docs/TANDA_C_SIGNAL_CALIBRATION.md` §6. Cerrado como corpus-neutro (valor
   residual solo Daubert, que tampoco cambia veredictos).
4. **A3 / L-033/L-034** — cadena de atenuación gamma×FRS. **SIGUE BLOQUEADO por
   datos** (solo 7 señales gamma reales, todas MALICE — ver Tanda C §4). No
   tocar: calibrar con 7 señales de una polaridad violaría L-033. Desbloqueo =
   más evidencia cruda con `event_log`/`windows_event_log` etiquetada, incluida
   clase benigna.
5. **Hueco estructural INTENT del ladder + revisión ABSTAIN/L-012** — decisiones
   abiertas documentadas en `docs/FASE2_DATASET_CALIBRACION.md` §4–§5 (los
   experimentos E2/E3 ya fueron medidos y refutados).
6. **A7 / L-041** — SMS semántico (léxicos + calibración multi-caso).

### 1.3 Cobertura mobile (Grupo C) — **CERRADO en lo sustancial (B-086, 2026-07-07)**

104 pins nuevos + 2 fixes acotados; cobertura ios 41.5% / android 38.4% /
macos 44.5% (desde ≈15%). El arnés para B-052-P2 existe.

1. ~~Pin de la escalera `to_signal` completa~~ — 52 pins (13+11+14 ramas,
   cruce opsec_bump, interplay B-072, techos) + cazador de ramas muertas
   como invariante.
2. ~~Bordes de banda de timestamps~~ — 28 pins (cada borde exacto de los 3
   conversores + acuerdo iOS≡macOS + ts≤0/None).
3. `_safe_rglob` **acotado** (heapq.nsmallest, salida idéntica, 18 pins).
   ~~Residuo: migrar los call-sites con `Path.rglob` directo~~ — **CERRADO
   (B-139, 2026-07-17):** los tres scans de marcadores `rglob("*")`
   (ios/android/macos) migrados a `scan_marker_names()` acotado
   (`vigia/sift/_fs_utils.py`, 15 pins rojos primero). El bloque Magisk
   conserva sus listas deliberadamente: los `len()` alimentan el string de
   evidencia del finding y son lookups por nombre específico, no
   `rglob("*")` (refutación documentada en la entrada B-139).
4. ~~`_safe_plist_load` con límite~~ — `_PLIST_MAX_BYTES=8MiB`, rechazo antes
   de parsear, WARNING visible (rojo primero).

### 1.4 Fixes acotados restantes (Grupo B — paralelo, 1–2 h cada uno)

Del inventario original quedan (B5/enfsi cerrado 2026-07-06 con `f1e3f75`;
B11/higiene de trackers cerrado 2026-07-07; **B3/B4/B7/B8/B9 cerrados
2026-07-07 como tanda B-087** — 5 commits, tests rojos primero cada uno,
suite 1034):

| # | Ítem | Fix diseñado |
|---|------|--------------|
| ~~B1~~ | ~~S-1~~ | **CERRADO** — `requirements-ci.txt` sincronizado (psutil/pyyaml/pytest-cov/pytest-asyncio) + `tests/test_requirements_ci_contract.py` verde (verificado 2026-07-08) |
| ~~B2~~ | ~~S-2 / BUG-NLP-002~~ | **CERRADO** — `TestL33tOOVUnreachable::test_analyze_surfaces_l33tspeak_as_oov` con `xfail(strict=True)`: suite verde sin ocultar el hallazgo, XPASS truena si el tokenizer lo arregla (verificado 2026-07-08) |
| ~~B3~~ | ~~B-016 residual~~ | **CERRADO** — detector stderr en el motor V4 (B-087) |
| ~~B4~~ | ~~B-018 residual~~ | **CERRADO** — VIGIA_VOL3_TIMEOUT + escalado + pipeline_meta (B-087) |
| ~~B6~~ | ~~B-060~~ | **CERRADO 2026-07-08** — `check_adapter_map_consistency()` en `forensic_adapter.py` + `tests/test_b060_adapter_map_consistency.py` (LAYER≡ONTOLOGY, LAYER⊆EVIDENCE, superset identity; tests rojos primero con "dientes") |
| ~~B7~~ | ~~B-061~~ | **CERRADO** — clamp unificado, 4 implementaciones acordadas (B-087) |
| ~~B8~~ | ~~A-1~~ | **CERRADO** — verify_daubert_record_hash + self-check (B-087) |
| ~~B9~~ | ~~A-2~~ | **CERRADO** — deactivate + TTL + sweep auditado (B-087) |
| ~~B10~~ | ~~B-058~~ | **CERRADO 2026-07-08** — `extract_verdict_from_bundle` lee el `agent_verdict` sellado (autoritativo, decide el exit) con fallback legacy; doctrina en `verdict_matches`. Gate comparativo sobre 198 bundles: **0 regresiones, +3 mejoras** (casos INTENT sub-reportados como SUSPICION) |

**Nota (auditoría cruzada 2026-07-08):** B1 y B2 ya estaban implementados en el
código (requirements-ci sincronizado, xfail strict presente) pero figuraban como
pendientes en este documento — mismo patrón "el tracker miente" que documentó
`docs/AUDITORIA_B047_CORRELATION.md`. Verificados verdes y cerrados aquí.

Sumados por el censo P0-001 (B-083, opcionales):

| # | Ítem | Fix diseñado |
|---|------|--------------|
| C1 | metadata exacta | `z_frac`/`conf_frac` (str de Fraction) en `to_signal()` de los 12 módulos |
| C2 | consistencia de estilo | unificar `float(z)/Z_CLIP_MAX` (Windows) con `float(z/z_clip)` (móvil) |
| ~~C3~~ | ~~NaN silencioso~~ | **CERRADO 2026-07-07** — `value`/`z_score`/`confidence` fail-closed en `ebs_v1` y `signal_contract`, ambas variantes (B-083/B-083b, tests rojos primero) |

**Sincronización 2026-07-08 (auditoría de pendientes cruzada contra
`docs/AUDITORIA_PIPELINE_ROBUSTEZ.md`):** los hallazgos N13/N14/P2-E de esa
auditoría (2026-07-03) nunca habían recibido ID de tracker — quedaban solo en
el doc, sin entrada en `BUGS_PENDIENTES(_EN).md`. Asignados ahora:

| # | Ítem | Qué falta |
|---|------|-----------|
| B88 | N13 | **RESUELTO (verificado 2026-07-08)** — ya arreglado por F8: `accuracy_validation` lee `tool or source` |
| B89 | N14 | **RESUELTO (verificado 2026-07-08)** — ya arreglado por F8: el drop se contabiliza en `signal_conversion_drops`/`pipeline_meta`. El fix propuesto original (`_UNANALYZED`) era semánticamente incorrecto |
| B90 | P2-E | **RESUELTO impacto de veredicto (verificado 2026-07-08)** — F5 etiqueta la señal `derived`; `_is_primary_signal` la excluye de todo gate. La marca "⏳ abierto" de la auditoría era stale |

**Actualización 2026-07-08 (audit-before-patch):** los tres se verificaron contra
HEAD y resultaron YA resueltos por las tandas F5/F8 de la propia auditoría de
robustez (F1–F9 sí aterrizaron). La disciplina de audit-before-patch evitó
parchear código ya arreglado; se corrigió el registro en su lugar. Ver
`BUGS_PENDIENTES_EN.md` (B-088/B-089/B-090) para la evidencia de código.

**También corregido (documental, sin cambio de código):** la entrada B-041
original (`BUGS_PENDIENTES(_EN).md`) quedaba marcada `[PENDING]`/`[PENDIENTE]`
con un diagnóstico que la propia entrada siguiente (B-041a/B-041b) ya había
refutado y corregido — un ID duplicado con dos veredictos contradictorios en
el mismo archivo. Marcada `[SUPERSEDED]`/`[SUPERSEDIDO]`, apuntando a la
entrada correcta; no se borró, para conservar el rastro de auditoría.

### 1.5 Abiertos de larga data (sin cambio de estado)

- **B-010** — migrar `forensic_technical_detector.py` a SemioticDetectorV2 (TODO).
- **L-029 / FW-009** — detector DARVO: **Fase 1 CERRADA (B-140, 2026-07-17)** —
  anotación en el path motor (scorer → orchestrator → narrativa sellada, canal
  B-094), sin efecto en veredicto. Quedan abiertas (doctrina/arquitectura):
  efecto en veredicto, `false_flag` como tipo de veredicto del scorer, y la
  revisión pareada cross-bundle (KIWI-002+003). Ver L-029 en
  KNOWN_LIMITATIONS.md, bloque "Progress 2026-07-17".
- **L-040** — `likelihood_ratio.py` opera en float: limitación documentada,
  0 flips empíricos; revisar solo si el corpus crece cerca de los bordes de
  decisión (mapa de cierre en `docs/AUDITORIA_L040_LIKELIHOOD_RATIO.md` §4).
- **L-034** — agregación sub-umbral multi-fuente: documentada.
- **A6 / B-013** — reabrir solo si aparece FP real post-L-037b.

---

## 2. Reglas de trabajo (sin cambios)

- Tag de restauración antes de cada sesión de cambios.
- Audit-before-patch: leer las líneas exactas; verificar que el bug existe.
- Gate comparativo obligatorio para todo cambio que toque veredictos
  (patrón B-069: medir, y si empeora, NO aplicar).
- Suite verde + corpus 166/199 (o mejor, con explicación por caso) antes de
  commitear. 0 flips no explicados.
- Commits `POST HACKATHON — ...`; los trackers EN/ES se actualizan en el mismo
  commit que cierra el bug (lección de esta sincronización: B-071..B-074
  faltaban en EN, y todo lo posterior al 07-05 faltaba en ambos).

## 3. Qué NO hacer (sin cambios respecto al triage)

- No tocar la cadena gamma×FRS sin las ≥20 señales etiquetadas (L-033).
- No recalibrar perfiles aislados (B-069 lo refutó empíricamente).
- No cambiar claims de accuracy ni el framing de los BREAK cases sellados en
  `SUBMISSION_COMPLIANCE.md`.
- No convertir el tipo de `SignalOutput` a Fraction: es la frontera de contrato
  (decisión de alcance P0-001, reconfirmada por el censo B-083).

---

## 4. Track teórico (Magnani / Aliseda / Nishida) — actualizado

El plan de lectura original de este archivo sigue vigente como track de
investigación, con dos correcciones de estado:

1. **Aliseda — YA NO es "la pieza ausente".** La función
   `resolve(ccs, risk, epsilon)` que la versión anterior de este documento
   describía como el ítem técnico faltante **se implementó y es el motor
   default desde 2026-07-05** (B-075). Lo que queda del ítem Aliseda es
   *formalizarla*: especificar `resolve()` como función de selección
   (generación vs selección de hipótesis, tableaux) citable en
   `DAUBERT_JUDICIAL.md`, con la implementación ya existente como referente.
2. **Magnani** — nota interna mapeando cada detector técnico a abducción
   teórica vs manipulativa (`notes/magnani_manipulative.md`); sin código.
3. **Nishida** — verificar accesibilidad de fuentes primarias antes de
   comprometerse; si solo hay citas secundarias, decirlo explícitamente
   (la misma disciplina evidencial que VIGÍA aplica a claims forenses).

Orden sugerido sin cambios: Aliseda → Magnani → Nishida. Referencias completas
en el historial de git de este archivo (versión 2026-07-05).

---

*VIGÍA — WHAT_IS_NEXT | actualizado 2026-07-07 | corpus 166/199, suite 848*
