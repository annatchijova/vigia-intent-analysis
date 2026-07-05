# Fase 1 — resolve() en el adaptador EBS (B-075 / P2-C)

**Fecha:** 2026-07-05
**Rama:** `claude/audits-bugs-analysis-kr3bcy`
**Origen:** `PLAN_ABDUCTIVO_PENDIENTES_20260705.md` §3 Fase 1; evidencia base
`AUDITORIA_MOTOR_SIN_LABEL.md`.
**Tag de restore:** `pre-fase1-label-leak-20260705-221206`
**Estado:** implementado detrás de `VIGIA_EBS_RESOLVE` (default **legacy** —
el flip del default es la decisión de doctrina pendiente, §5).

---

## 1. La sorpresa registrada (C)

Con `expected_verdict` retirado, el motor determinista produce la distribución
real (MALICE 108 / SUSPICION 35 / UNKNOWN 14 / NOISE 41) pero el agente colapsa
a NOISE 189 / ABSTAIN 9 — **cero detecciones**. Expectativa violada: el agente
dice derivar su veredicto de la evidencia. Mecanismo: en `_analyze_ebs_json` la
única vía a un veredicto malicioso era la etiqueta; la alternativa "de
evidencia" era `avg > Fraction(2,1)`, inalcanzable para inputs normalizados
[0,1] (máx observado 0.87).

## 2. Hipótesis rivales y su suerte (A → D → I)

| Hipótesis | Predicción discriminante | Resultado |
|---|---|---|
| **H1** — el adaptador usa la etiqueta como atajo de mapeo y el camino honesto nunca se construyó | la estructura del código lo muestra directamente | CORROBORADA estructuralmente (`sift_orchestrator.py`, rama legacy) — pero no dice cómo arreglarlo |
| **H2** — error de unidades: `avg>2` fue escrito para escala z; re-escalar umbrales a [0,1] recuperaría la distribución del motor | un barrido exhaustivo de umbrales sobre `avg` debería acercarse al motor ciego | **REFUTADA por medición** (2026-07-05): mejor acuerdo alcanzable **58.6%** (4 clases) / **74.7%** (binario) sobre 198 casos. Las clases se solapan por completo: MALICE avg min=0.000/max=0.873; NOISE avg max=0.788; UNKNOWN mediana 0.637 > MALICE mediana 0.506. El escalar no porta la información del ladder |
| **H3** — falta la **función de selección** (Aliseda: generación vs selección); la etiqueta tapó ese hueco desde el origen | si la selección canónica existe en otro lado del repo, invocarla debería reproducir la distribución del motor con 0 dependencia de la etiqueta | **CORROBORADA**: la selección ES el ladder de `_vigia_score` (TrustFusion → CorrelationDecay → CAIE → Decision; umbrales 0.33/0.18/0.08 + gates Daubert B-068/B-070), demostradamente ciego al label (seal byte-idéntico bajo flip, auditoría §3b). Con resolve() cableado, el agente end-to-end reproduce EXACTAMENTE la distribución del motor (§4) |

## 3. Qué se implementó

- `sift_orchestrator._resolve_hypothesis()`: quita `expected_verdict`, invoca
  `vigia_scorer._vigia_score` (lazy import) y mapea el veredicto vía
  `_MOTOR_HYPOTHESIS_MAP` (MALICE→MALICIOUS_INTENT_DETECTED,
  SUSPICION→SUSPICION_DETECTED, UNKNOWN→UNDETERMINED (→ABSTAIN),
  NOISE→NO_SEMIOTIC_ANOMALY_DETECTED, ABSTAIN→ABSTAIN_DETECTED,
  ERROR→PIPELINE_ERROR). Confianza = la del motor (Fraction, clamp [0, 99/100]);
  `is_conclusive` con el mismo guard B-027 (>1/3 y fuera de la familia abstain).
- Selección de modo en `_analyze_ebs_json`: `VIGIA_EBS_RESOLVE=motor|legacy`
  (cualquier otro valor → legacy). El modo y la traza de resolve quedan
  SELLADOS en `pipeline_meta` (`ebs_adapter_mode`, `resolve.motor_verdict/
  motor_score/motor_confidence/motor_reason`) — el bundle declara qué función
  de selección decidió (trazabilidad Daubert).
- `expected_verdict` queda como passthrough de evaluación en `pipeline_meta`
  (mismo criterio que el motor); en modo motor NUNCA participa del scoring.
- La rama legacy queda **byte-idéntica** y es el default (regla de seguridad
  del plan: la línea del leak sostiene el corpus 199/199 y no se retira hasta
  decidir el flip con estos números a la vista).

**Tests** (`tests/test_fase1_resolve.py`, 10 — escritos ANTES del fix, 9 rojos
/1 verde sobre el código previo):
- Blind gate: RT-NOLABEL-001 sin etiqueta → MALICIOUS_INTENT_DETECTED (antes: NOISE).
- Equivalencia con el scorer canónico en los 4 fixtures red-team.
- Invariancia al label-flip en modo motor: `abduction` y `signals` idénticos
  bajo MALICE/NOISE/sin-etiqueta (el contrato del §3b de la auditoría).
- Pin del leak legacy (documentado, no deseado): si truena, alguien cambió el
  default sin pasar por la decisión de doctrina.
- Default legacy + fallback de valores desconocidos.
- Honestidad: el FN conocido de FN-002 se emite tal cual en modo motor (no se
  maquilla con la etiqueta); guard B-027 en el camino nuevo.

## 4. Corridas comparativas (gate obligatorio, patrón B-069)

| Métrica | Legacy (default) | Modo motor |
|---|---|---|
| Suite completa | **719 passed, 0 failed, 7 xfailed** | ídem (misma corrida) |
| Corpus vs etiquetas (`run_all_agent`) | **199/199 PASS** | **143/199 PASS** |
| Distribución de veredictos | eco de la etiqueta (194/196 medido en auditoría) | **MALICE 108 / NOISE 41 / SUSPICION 35 / UNKNOWN 15** — idéntica al motor ciego de la auditoría |
| Detecciones maliciosas sin etiqueta | **0** | **143** (MALICE+SUSPICION) |
| Label-flip (VIGIA-CAN-008 y fixtures) | veredicto y seal cambian con la etiqueta | veredicto, abduction y señales invariantes |

Desglose de los 56 FAIL del modo motor (exp→got): 12 INTENT→MALICE,
10 SUSPICION→UNKNOWN, 10 MALICE→SUSPICION, 9 ABSTAIN→NOISE, 3 SUSPICION→NOISE,
2 NOISE→MALICE (FP), 2 MALICE→NOISE (FN), 2 INTENT→SUSPICION, y 6 singletons.
Lectura: **~41 de los 56 son desacuerdos de severidad adyacente** (misma
dirección, escalón vecino), no errores de dirección. Los errores duros de
dirección son ~7 (2 FP + 5 FN benigno-vs-malicioso), consistentes con los 3 FP
/ 17 FN del motor ciego medidos por la auditoría (la diferencia es la
normalización binaria de aquella tabla).

## 5. La decisión pendiente (doctrina — Anna)

El 199/199 actual **no mide detección**: mide reproducción de la etiqueta (el
agente ciego detecta 0). El 143/199 del modo motor es el número honesto de la
capacidad real end-to-end hoy. Opciones:

- **(a) Flip ya**: `VIGIA_EBS_RESOLVE=motor` como default. El corpus pasa a
  medir de verdad; README/claims deben actualizarse de 199/199 a 143/199 (o a
  la métrica binaria de la auditoría, más representativa). Los 56 desacuerdos
  se convierten en el backlog de calibración de la Fase 2 (dataset ground
  truth → gamma → re-fit B-069 → B-052-P2).
- **(b) Flip después de Fase 2**: calibrar primero con el dataset (los 22
  desacuerdos INTENT↔MALICE / SUSPICION↔UNKNOWN son sensibles a umbrales),
  flipear cuando el número honesto sea mejor. Riesgo: el 199/199 sigue
  presentándose mientras tanto.
- **(c) Doble sello transitorio**: default motor + sellar también el veredicto
  legacy en `pipeline_meta` para comparación continua. Más honesto que (b),
  más gradual que (a).

Recomendación técnica: **(a) o (c)** — desde esta implementación, cada corrida
en modo legacy es una decisión activa de seguir sellando la etiqueta como si
fuera un veredicto. La regla del plan se cumplió: los tests rojos ya pasan en
verde por el camino nuevo; lo único que falta para retirar el leak es la
decisión explícita.

## 6. Falibilismo (condiciones de reapertura)

- Si tras la calibración de Fase 2 el modo motor no converge mejor con el
  ground truth, la causa está aguas arriba de la selección: agregación
  mono-señal (B-052-P2) ahogando la entrada de resolve() — esa dependencia se
  vuelve precondición y se reordena la fase.
- Los 9 ABSTAIN→NOISE merecen auditoría propia: el motor "limpia" casos que la
  etiqueta declara indecidibles — puede ser señal de L-014 (convergencia
  blanda) o de etiquetas conservadoras. Ninguno de los dos se arregla a ciegas.
- `UNKNOWN→UNDETERMINED→ABSTAIN` (mapa nuevo) es una decisión de mapeo, no de
  medición: si Fase 2 muestra que UNKNOWN del motor separa bien SUSPICION de
  ruido, el mapa puede refinarse — con corrida comparativa, como siempre.
