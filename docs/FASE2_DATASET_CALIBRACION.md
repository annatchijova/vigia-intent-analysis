# Fase 2 — Dataset de calibración del ladder y primer ajuste con ground truth (B-076)

**Fecha:** 2026-07-05
**Rama:** `claude/audits-bugs-analysis-kr3bcy`
**Origen:** backlog de B-075 (los 56 desacuerdos del corpus en modo motor);
`PLAN_ABDUCTIVO_PENDIENTES_20260705.md` §3 Fase 2 — "ground truth primero,
calibración después" (regla L-033: no mover factores sin dataset etiquetado).
**Tag de restore:** `pre-fase2-dataset-20260705-232536`

---

## 1. El dataset

`data/calibration_ladder_dataset_20260705.json` — 198 casos del corpus
(find_cases), cada uno con: etiqueta (`expected`), veredicto/score/confianza
del **motor ciego** (`_vigia_score` sin `expected_verdict`), y los features
que el ladder usa para decidir: `n_artifacts`, artefactos/clases DEVICE
(vía `evidence_role`), `mean_effective_trust`, fracturas CAIE, y distancia
al umbral más cercano. Es el dataset que la regla L-033 exigía antes de
tocar cualquier factor — 198 señales reales etiquetadas, no 20.

El generador es reproducible (motor determinista + corpus versionado); los
números de abajo salen de él.

**Nota de versión:** el archivo commiteado fue regenerado DESPUÉS de aplicar
E1 (refleja el estado vigente: 46 desacuerdos, umbral SUSPICION=0.10). El
§2 documenta el análisis PRE-E1 (56 desacuerdos, umbral 0.18) que motivó el
experimento; para reproducir ese estado exacto: checkout del tag
`pre-fase2-dataset-20260705-232536` y re-correr el generador.

## 2. Los 56 desacuerdos, caracterizados

| Cluster (exp→got) | n | Rango de scores | ¿A <0.05 de un umbral? | Diagnóstico |
|---|---|---|---|---|
| INTENT→MALICE | 12 | 0.344–0.841 | 2 | **Estructural**: el ladder no tiene escalón INTENT (§4) |
| SUSPICION→UNKNOWN | 10 | 0.101–0.148 | **10** | **Umbral**: toda la banda [0.10, 0.18) — E1 |
| MALICE→SUSPICION | 10 | 0.211–0.464 | 8 | 9 por umbral MALICE (0.33), 1 por gate de corroboración (FN-001: score 0.464, 2 clases device) |
| ABSTAIN→NOISE | 9 | 0.006–0.053 | 2 | Etiqueta-vs-doctrina (§5): scores bajísimos, L-012 |
| SUSPICION→NOISE | 3 | 0.029–0.059 | 2 | señal estructural no modelada (KIWI: testigos coludidos, trust 0.1) — familia L-016 |
| NOISE→MALICE | 2 | 0.421–0.445 | 0 | los 2 FP duros (cluster cultural_marker, cf. auditoría §4.1) |
| MALICE→NOISE | 2 | 0.018–0.071 | 1 | FN duros (constelación FN-002, familia L-014) |
| resto (singletons) | 8 | — | — | mixto |

Errores duros de dirección: ~7. Todo lo demás es escalón adyacente o
estructural.

## 3. Experimentos (bucle A–D–I, cada uno medido ANTES de decidir)

### E1 — Umbral SUSPICION 0.18 → 0.10 · **APLICADO** (B-076)

- **Abducción:** los 10 SUSPICION→UNKNOWN caen TODOS en [0.101, 0.148] —
  si el umbral fuera 0.10, serían correctos "de una pieza".
- **Deducción:** bajarlo solo puede afectar a casos con score en [0.10, 0.18).
  Censo en el dataset: además de los 10, hay exactamente **1** caso correcto
  en esa banda (VIGIA-REAL-SRL-DC-MEMORY, exp=UNKNOWN, score 0.167) — y el
  comparador acepta cualquier veredicto para expected=UNKNOWN, así que el
  colateral esperado es **cero**.
- **Inducción (gate):** aplicado en `vigia_scorer.py:820`. Dataset re-corrido:
  desacuerdos 56 → **46** (+10 exactos, 0 regresiones; el MALICE→UNKNOWN de
  score 0.148 pasa a MALICE→SUSPICION — sigue fail, un escalón más cerca).
  Corpus end-to-end y suite: ver §6.

### E2 — Escalón INTENT por presencia de fracturas · **REFUTADO** (documentado)

- **Abducción:** MALICE = INTENT + ocultamiento (escala de veredictos);
  Invariante 6: los artefactos de fabricación suben el peso MALICE. Si las
  fracturas CAIE marcan ocultamiento, "score>0.33 sin fracturas → INTENT,
  con fracturas → MALICE" separaría los 12 INTENT→MALICE.
- **Deducción/medición:** 11/12 INTENT→MALICE tienen 0 fracturas ✓ — pero
  **49/93 MALICE correctos también tienen 0 fracturas** → el criterio
  flipearía 49 aciertos a INTENT. Neto: −38.
- **Veredicto:** las fracturas CAIE no son el discriminador de ocultamiento
  (muchos MALICE llevan el anti-forense como CONTENIDO de señal, no como
  fractura cross-artifact). El escalón INTENT sigue siendo un hueco
  estructural (§4); cualquier discriminador futuro necesita un feature de
  ocultamiento más rico, y este dataset para probarlo.

### E3 — NOISE con <3 artefactos → ABSTAIN · **REFUTADO** (documentado)

- **Abducción:** "limpio con 2 artefactos" no es afirmable (familia P2-D/F7);
  un gate de soporte flipearía los ABSTAIN→NOISE delgados.
- **Medición:** arreglaría 5, **rompería 4** casos benignos correctos de 2
  artefactos (FP-001, RELAY-MAIN, SKILL-EVALS, case_004). Neto ≈ +1, con
  costo doctrinal (todo caso benigno pequeño abstendría).
- **Veredicto:** no aplicar como regla ciega. El cluster ABSTAIN→NOISE es
  mayormente etiqueta-vs-doctrina (§5), no un bug del ladder.

## 4. Hallazgo estructural — el ladder no tiene INTENT

> **DECISIÓN 2026-07-05 (Anna, para corpus sintético): opción (a).** El
> comparador batch acepta MALICE donde la etiqueta dice INTENT — es
> sobre-severidad, no error de dirección (+12). La sub-severidad
> (INTENT→SUSPICION) sigue siendo FAIL. Implementado en `run_all_agent.py`
> (regla `over_severity`) y replicado en el campo `agree` del generador del
> dataset (`scripts/generate_ladder_dataset.py`). Las opciones (b)
> discriminador de ocultamiento real y (c) revisión de etiquetas INTENT
> quedan abiertas para el futuro.

El espacio de veredictos del motor es {MALICE, SUSPICION, UNKNOWN, NOISE,
ABSTAIN, ERROR}: **no puede emitir INTENT jamás**. Los 14 casos etiquetados
INTENT (12→MALICE, 2→SUSPICION) no pueden acertar en modo motor por
construcción. Opciones (decisión de doctrina, con E2 ya refutado como
discriminador barato):

- (a) El comparador trata INTENT⊆MALICE como acierto (la escala dice que
  MALICE ⊃ INTENT + ocultamiento; un MALICE donde la etiqueta dice INTENT es
  sobre-severidad, no error de detección). +12 inmediato, honesto si se
  documenta como "severidad, no dirección".
- (b) Diseñar el discriminador de ocultamiento real (features: señales
  anti-forenses en contenido, timestomping, log deletion — no solo fracturas
  CAIE) y añadir el escalón INTENT al ladder. Trabajo mayor, con este
  dataset como banco de pruebas.
- (c) Revisar las 14 etiquetas INTENT (¿algunas son MALICE mal etiquetado?).

## 5. Auditoría de los 9 ABSTAIN→NOISE

> **DECISIÓN 2026-07-05 (Anna, para corpus sintético):** las etiquetas
> sintéticas de AMB-001/002 se actualizaron ABSTAIN→NOISE para reflejar
> L-012 (la doctrina documentada en el README ya declaraba NOISE como el
> comportamiento correcto para señal nula — la etiqueta contradecía el
> diseño). Los archivos llevan campo de auditoría `_label_revision`; el test
> B-058 que usaba AMB-001 quedó independizado de la etiqueta del corpus
> (fuerza ABSTAIN inline). **El corpus real NO se tocó** — los otros 7 del
> cluster (ANDROID11 intake, ASCIISTUDIO, PAGINA-WEB-PAPA, WEDLM, SEP800,
> SET68I, FP-002) permanecen con su etiqueta original en el backlog.

Los 9 tienen score ≤ 0.053 (sin señal) y confianza NOISE 0.95–0.99 con 2–3
artefactos. Composición:

- **AMB-001/002**: NOISE es el comportamiento documentado POR DISEÑO
  (L-012, citado en el README: "Null-signal cases correctly return NOISE").
  La etiqueta ABSTAIN contradice la doctrina declarada → candidatos a
  re-etiquetar, no a tocar código.
- **ANDROID11-001**: caso de intake (imagen anidada sin extraer) — el
  ABSTAIN de la etiqueta describe el estado del ANÁLISIS, no de la
  evidencia. El motor solo ve 2 artefactos de custodia limpios. Génesis
  distinta: pedir señal `UNANALYZED` en el caso, no umbral.
- **ASCIISTUDIO / PAGINA-WEB-PAPA / WEDLM** (n=2, trust 0.95, score 0.0063) y
  **SEP800/SET68I/FP-002**: evidencia mínima limpia. La pregunta es de
  etiqueta (¿por qué ABSTAIN y no NOISE/BENIGN?) — misma familia L-012.
- Nota epistémica para trabajo futuro (no accionada): `confidence = 1 −
  score` para NOISE hace que MENOS señal produzca MÁS confianza de
  benignidad con 2 artefactos — la confianza de limpieza debería escalar
  con cobertura/diversidad, no solo con ausencia de anomalía. E3 mostró que
  el gate ciego no es la solución; queda como candidato de diseño con este
  dataset.

## 6. Gates de la tanda (protocolo)

| Corrida | Antes (post-flip B-075) | Después (E1/B-076) |
|---|---|---|
| Suite completa | 719 passed / 7 xfailed | **719 passed / 7 xfailed** |
| Corpus default (motor) | 143/199 | **153/199** |
| Desacuerdos | 56 | **46** |
| Regresiones | — | **0** |

## 7. Backlog restante y qué necesita cada cluster

**Actualización 2026-07-05 (post decisiones §4/§5):** con la doctrina del
comparador (+12) y la revisión de etiquetas AMB (+2), el backlog queda en
**32 desacuerdos** y el corpus en **167/199**:

| Cluster | n | Camino |
|---|---|---|
| MALICE→SUSPICION | 11 | 9-10 son umbral MALICE 0.33 (scores 0.148–0.32) — bajarlo requiere medir FP nuevos; 1 es el gate de corroboración (FN-001) — no tocar sin revisar B-068 |
| ABSTAIN→NOISE | 7 | corpus real, NO tocado (§5): intake ANDROID11 necesita señal UNANALYZED en el caso; el resto es revisión de etiquetas pendiente de Anna |
| SUSPICION→NOISE | 3 | estructural (L-016 testigos coludidos) — no es umbral |
| NOISE→MALICE (FP) | 2 | cluster cultural_marker — conecta con B-070/roles; revisar perfil de la clase |
| MALICE→NOISE (FN) | 2 | constelación L-014 — necesita señal emergente cross-artifact (CAIE), no umbral |
| BENIGN/NOISE→SUSPICION | 3 | efecto de banda de E1 (scores 0.13–0.27) — vigilar: son los candidatos a FP si se baja más algún umbral |
| INTENT→SUSPICION | 2 | sub-severidad, sigue FAIL por diseño de la doctrina (a) |
| otros | 2 | caso a caso con el dataset |
