# Dossier de arquitectura del scorer — investigación multi-agente (2026-07-12)

**Propósito:** evidencia medida para las decisiones de arquitectura pendientes del
scorer. Solo diagnóstico y recomendaciones — **cero cambios de motor en esta
investigación**.

**Método:** workflow de 10 sondas empíricas paralelas sobre el motor real
(`_vigia_score` + `CrossArtifactIncongruenceEngine`), 1.15M tokens de agentes,
~2.4M case-scorings en la sonda de coeficientes sola. Corpus: 193 case_ids únicos
(198 archivos dict; 5 duplicados last-wins), baseline 153/193 reproducido
independientemente por 6 de las 10 sondas. Evidencia cruda:
`docs/SCORER_ARCH_PROBES_20260712.json`; scripts y datasets intermedios
en scratchpad de sesión (efímero — los números citados acá y en el JSON son el
registro durable).

**Estado de verificación — leer antes de decidir:** la pasada de verificación
adversarial (33 agentes) cayó completa por límite de cuota. Reemplazo honesto:
(a) **spot-checks del agente principal** reproduciendo los números más decisivos
contra el motor real, y (b) consistencia cruzada entre sondas independientes.
Etiquetas usadas abajo (doctrina propia del proyecto):

- **CONFIRMED** = reproducido independientemente (spot-check propio, o el mismo
  número medido por ≥2 sondas con métodos distintos).
- **INFERRED** = una sola sonda, método documentado, sin reproducción
  independiente todavía.

Spot-checks realizados: MAGNET-2020 score exacto 0.3297 ✓; censo de 18 SPOF
reproducido con `scorer_gate.py --corpus` (18 exactos) ✓; flip de determinismo
por orden de emisión reproducido en el motor real (2 flips) ✓; CAN-008
retipado+rúbrica → MALICE 0.4359 bit-igual con snippet propio ✓; TypeError de
`Fraction.__format__` ✓.

---

## 1. El mapa en una página

El scorer que tenemos hoy es, medido:

1. **Un pipeline autorado, no computado** [INFERRED]: zerear todos los raw_score
   colapsa 133/193 veredictos; solo 18/97 MALICE sobreviven por estructura
   (fracturas/gates). El veredicto vive mayormente en la autoría de datos.
2. **Con un segundo canal binario disfrazado de aditivo** [CONFIRMED]: una
   fractura sev-0.8 aporta +0.36 > umbral 0.33 — el "boost aditivo" es en la
   práctica un override. 18/97 MALICE son single-fracture single-point-of-failure
   (16 de ellos sobre los dos discriminadores M2). El cap 0.5 nunca intervino en
   un veredicto; la granularidad de severidad no se usa (94% de la masa es una
   única fractura 0.8/0.85).
3. **Cuya protección anti-FP vive entera en el gate R4-3** [INFERRED]: con
   boost=1.0 sin cap, cero MALICE nuevos — el corpus no tiene ni un benigno que
   dispare fractura maliciosa, así que el lado FP del coeficiente está
   completamente sin restricción empírica.
4. **Con constantes de dos estratos** [INFERRED]: un estrato pre-histórico sin
   derivación documentada (0.45/0.25, cap 0.65, support, 0.9+0.1, hard-gate 0.9)
   y un estrato post-2026-05-19 donde cada cambio es un incidente validado sobre
   el mismo corpus que reporta accuracy. El 58% del agreement descansa en un
   umbral (0.33) cuyo registro de calibración es una oración.
5. **Float de punta a punta en el path de decisión** [CONFIRMED]: el invariante 4
   ("no floating-point en el path de decisión") es falso tal como está
   implementado. Hoy es empíricamente orden-invariante (~1000 permutaciones, 0
   flips), pero existe un flip construido REAL (UNKNOWN↔SUSPICION por puro orden
   de emisión de fracturas) y 41% del corpus tiene valores pre-redondeo a 1e-12
   de un cliff.

## 2. Decisiones, con la evidencia al lado

### D-A — ¿Boost aditivo o tier estructural explícito?

**Evidencia:** el diseño aditivo es aritméticamente binario [CONFIRMED: 18 SPOF
reproducidos]; CAIE `evaluate()` ya separa canal estructural de probabilístico y
bajo esa separación 16 de los 18 SPOF serían SUSPICION-con-flag-estructural, no
MALICE [INFERRED]. Los 22 MALICE/INTENT sub-llamados tienen todos boost=0 — el
único cuello de botella del lado malicioso es **cobertura de detectores de
fractura**, no pesos [INFERRED, consistente con 3 sondas].

**Recomendación:** formalizar lo que ya es verdad: un veredicto MALICE cuya masa
la aporta una sola fractura debe REPORTARSE como "fracture-carried" en el bundle
(tier estructural explícito), no como masa probabilística. Es un cambio de
honestidad narrativa primero (barato) y de arquitectura después (opcional). No
gastar en re-ponderar el composite: donde hay masa de raw, funciona (78/97).

### D-B — ¿Recalibración global de coeficientes/umbrales? → NO ahora

**Evidencia:** boost en meseta [0.39, 1.0-sin-cap] con **cero** configuraciones
que mejoren 153 en todo el espacio barrido (~107 combos + barridos finos)
[INFERRED, cross-consistente con dominancia]; penalty corpus-muerto (1/193 casos
lo porta); refit conjunto de umbrales: +5 in-sample pero **−7 leave-family-out**
[INFERRED] — el corpus castiga el refit; B-076 casi sin optimismo (+9 real); el
propio repo ya rechazó una vez la recalibración por partes de un set acoplado
(B-069) [INFERRED]. Y la trampa de fondo: ~50 casos de tuning identificados
siguen en el corpus de evaluación — **153/193 es accuracy de training set** y
debe reportarse así [INFERRED, múltiples sondas].

**Excepción puntual medible:** MALICE 0.33 no es óptimo local — 0.32 domina
estrictamente (+1: MAGNET-2020, exp INTENT, score exacto 0.3297 [CONFIRMED]).
Pero es UN caso, y perseguir el cluster 0.10–0.33 bajando umbrales está
rechazado por el CV. Tratarlo como decisión del caso MAGNET (¿reetiqueta?
¿señal legítima que falta?) — no como calibración.

**Prerrequisitos para habilitar una recalibración futura:** (1) casos benignos
adversariales que disparen LINGUISTIC_ATTRIBUTION_SIGNAL / SOCIAL_ENGINEERING_
PATTERN espuriamente (hoy el costo de falsa alarma del boost es invisible);
(2) higiene de corpus (§4); (3) familias independientes suficientes para CV.

### D-C — Doctrina de dos fuentes: forma vs masa

**Evidencia:** el gate R4-3 certifica cardinalidad de dominios de recolección,
no independencia de masa probatoria — los 18 SPOF pasan todos por la rama
cross-domain donde la "segunda fuente" es escenografía de masa casi nula
alrededor de un solo detector semiótico [INFERRED]. El mecanismo dominante de
fragilidad NO es el umbral 0.33 sino el **cliff de existencia** del gate
(`adjusted_score > 0` cuenta como corroborador): 17 de 24 flips MALICE→SUSPICION
por perturbación ±0.10 ocurren con el score todavía >0.33 [INFERRED]. Las ramas
hard-mass y per-cost del gate están calibradas sobre 1 y 2 casos [INFERRED].

**Recomendación:** quirúrgico primero — corroborador con masa mínima
(`adjusted ≥ ε` en vez de `> 0`), medible en una tarde con `scorer_gate`. La
re-derivación del gate como modelo de independencia real queda para cuando el
corpus tenga cobertura (hoy sería otra regla N=1).

### D-D — Rúbrica raw_score para la sesión de re-puntuación → LISTA

**Evidencia [CONFIRMED en lo central]:** la rúbrica de 5 bandas es descriptiva
de la norma de autoría que el corpus YA usa (memory_process mediana 0.92 en
casos MALICE; raw ≤0.10 significa "observación limpia") — por eso es
no-circular: los 0.05–0.07 de los artefactos invertidos hoy **afirman
limpieza** de la señal de ataque central del caso. Documento completo con
anclas de comparables reales: `docs/RUBRIC_RAW_SCORE_20260712.md`.

Dry-run sobre el motor real (retipado D-5 + rúbrica, atómico):

| Caso | Hoy | Retipado+rúbrica | Nota |
|---|---|---|---|
| CAN-008 | SUSPICION 0.1953 | **MALICE 0.4359** [CONFIRMED bit-igual] | rama cross-domain, **cero fracturas, boost 0** — el camino más resistente a cross-examination |
| CAN-047 | SUSPICION 0.1909 | **MALICE 0.4233** [INFERRED] | ídem |
| CAN-046 | SUSPICION 0.2221 | **SUSPICION 0.3085** — NO llega [INFERRED] | en TODA la banda defendible (cruza 0.33 solo con raw ≥0.90, y el corpus tiene un contraejemplo benigno: LINUX-005, binario Go entropía 7.4 autorado 0.62). **Candidato a criterio CAN-026 (reetiqueta), no a re-score** |

**Regla dura descubierta:** rúbrica y retipado deben aplicarse **atómicamente**
— la rúbrica sin retipar deja a CAN-046 colarse a 0.333 con el perfil de
evidencia equivocado [INFERRED]. Resultado esperado de la sesión: +2 agree
(155/193), riesgo de regresión nulo fuera de los 3 archivos.

### D-E — Determinismo: migración a Fraction del path de decisión → PRIORIDAD

**Evidencia [CONFIRMED]:** flip construido real (2 flips UNKNOWN↔SUSPICION en el
motor por orden de emisión, score 0.0999 vs 0.1000); acumuladores boost/penalty
en float `+=`; `math.prod` en Noisy-OR; umbrales Fraction comparados contra
floats redondeados (los umbrales "estrictos" son efectivamente INCLUSIVOS a
0.3300/0.1000/0.0800); `0.7**k` (libm pow) reintroducido en el decay R4-3 — la
clase exacta de hazard que las tablas P0 eliminaron; y un crash real: severity
string/None en `temporal_violations` tumba el scorer entero en la rama de
máxima autoridad (hard gate) [INFERRED].

**Recomendación:** migración de ~15 líneas a Fraction (loop de boost, loop SU,
los dos caps `min()`, combinación final), tabla Fraction para `0.7**k`, y
`_sev_float` en las dos lecturas del hard gate. Criterio de aceptación:
**corpus bit-idéntico** (hoy es orden-invariante empíricamente, así que la
migración debe dar 0 cambios — si cambia algo, eso ES el hallazgo).

### D-F — Calibrador LR / ENFSI → fix de 1 línea ahora, reporting después, jamás en el veredicto

**Evidencia:** el path sellado tiene CERO cableado de calibración; el feed está
bitroteado — `CaseAdapter` muere en `f'{raw_score:.8f}'` sobre Fraction en
py3.11 [CONFIRMED], convierte 0/68 casos; el modelo commiteado
(`models/calibrated_lr.json`, n=14 test, FPR@0.5=0.25) es un fósil
irreproducible que nada carga; el hook H28 busca un archivo `*_isotonic.json`
que ningún script produjo jamás [INFERRED]. La doctrina B-059/ENFSI ya decidió:
LR es capa de REPORTE con escala verbal canónica; los veredictos siguen por
umbral.

**Recomendación:** (1) fix de 1 línea del format ahora — desbrickea toda
calibración futura por casi nada; (2) reporting LR ENFSI-conforme junto al
veredicto determinístico cuando haya datos que lo defiendan (n=14 con 25% FPR
es indefendible bajo Daubert); (3) nunca LR-en-el-veredicto: contradiría
doctrina sellada.

### D-G — Divergencia de modos: unificar hacia el motor, inequívoco

**Evidencia [INFERRED, magnitud tal que el margen de error no cambia la
dirección]:** motor vs tool MCP coinciden en 55/193 (28.5%) con **fracturas
bit-idénticas en 193/193** — toda la divergencia es doctrina aguas abajo
(escala Noisy-OR, umbrales 0.5/0.2, CDL). 40 flips duros MALICE-vs-NOISE, todos
unidireccionales (tool dice NOISE donde el motor sella MALICE; 39/40 con
expected=MALICE). Contra ground truth: motor 153 vs tool 49 — unificar hacia el
tool costaría 110 veredictos correctos; hacia el motor, 6.

**Recomendación:** `evaluate()` deja de emitir veredicto standalone: devuelve
composite+fracturas como señales y delega el veredicto a la capa de decisión
del motor (o etiqueta su campo verdict como no-sellable). Hoy una investigación
en modo MCP que llama `cross_artifact_analysis` ve un veredicto que contradice
el bundle sellado en el 71.5% de los casos. El CDL `coverage_ratio<0.3` es un
tripwire de clase-única sin relación con su propósito declarado — re-scope o
eliminar en la unificación.

## 3. Hallazgos de doctrina de métrica (afectan cualquier decisión futura)

- **La banda UNKNOWN es estructuralmente irrecompensable** bajo el comparador
  (expected UNKNOWN acepta todo → un veredicto UNKNOWN nunca puede ganar
  agreement, solo perderlo). Cualquier calibración contra agreement la vacía.
  Decisión pendiente: si UNKNOWN es requisito de producto (tier de triage
  humano), el comparador debe recompensarlo; si no, eliminar la banda [INFERRED].
- **ABSTAIN es arquitectónicamente inalcanzable** para evidencia ordinaria de
  baja confianza: los 7 casos expected-ABSTAIN resuelven todos a NOISE y
  ninguna ruta ABSTAIN tiene cobertura de corpus [INFERRED]. O se crea una banda
  ABSTAIN alcanzable (low-score+low-trust) o se documenta que ABSTAIN es solo
  para colapso de procedencia.
- **153/193 es accuracy in-sample** — ~50 casos de tuning identificados están en
  el corpus de evaluación; +12 del agreement vienen de un cambio de doctrina del
  comparador y +13 de doctrina (no de veredictos correctos) [INFERRED]. Todo
  reporte externo debería decirlo.
- **Higiene de corpus:** 5 pares de case_id duplicados donde la variante
  converted/ puntúa DISTINTO (3 pares flipean agree/disagree) — el headline
  depende de la convención de dedupe. Decidir canónico antes de cualquier freeze
  [INFERRED].
- **json_fallback degrada honesto pero fuerte:** 153 → 79 sin CAIE vivo. ¿El
  modo standalone es target de primera clase (entonces necesita su propio
  regression gate) o narrative-only (entonces documentarlo)? [INFERRED]

## 4. Orden de ataque recomendado (para tu decisión, no ejecutado)

| # | Ítem | Costo | Valor |
|---|---|---|---|
| 1 | D-E determinismo: Fraction en ~15 líneas + shield hard-gate + tabla pow. Gate: corpus bit-idéntico | 2–3 h | Repara el invariante 4 real; pre-requisito de cualquier refactor de CAIE que cambie orden de emisión |
| 2 | D-F fix 1 línea CaseAdapter | 15 min | Desbrickea la calibración futura |
| 3 | D-D sesión de re-puntuación con rúbrica (tarea #15, ya con green-light D-5): CAN-008/047 recuperan por composite limpio; CAN-046 → propuesta de criterio CAN-026 | 1–2 h | +2 agree; cierra el lote subgrupo C; saca 2 xfails |
| 4 | D-C corroborador con masa mínima (ε) en el gate — diseñar, medir con scorer_gate, decidir | 2–3 h | Ataca el mecanismo #1 de fragilidad (cliff de existencia) |
| 5 | §3 doctrina de métrica: política UNKNOWN/ABSTAIN + dedupe canónico + disclosure in-sample | doctrinal (tuyo) | Sin esto, toda métrica futura sigue siendo ambigua |
| 6 | D-G unificación de modos (evaluate() delega veredicto) | 3–4 h | Elimina la contradicción tool-vs-bundle del modo MCP |
| 7 | D-A tier "fracture-carried" explícito en el bundle | 1–2 h | Honestidad narrativa Daubert de los 18 SPOF |
| — | **NO hacer ahora:** recalibración global de coeficientes/umbrales (meseta + CV negativo + FP-side sin datos); LR en el path de veredicto (contradice B-059) | — | — |

## 5. Límites de esta investigación

- Sin verificación adversarial independiente (cuota); el estado de cada
  hallazgo está etiquetado y los 5 más decisivos fueron reproducidos a mano.
  Si algo de esto va a sostener un cambio grande, correr la pasada de
  verificación cuando la cuota reponga (el workflow es reanudable:
  `resumeFromRunId wf_c28ab882-615`, las 10 sondas están cacheadas).
- Los scripts y datasets intermedios de las sondas viven en scratchpad efímero;
  lo durable es este dossier + `docs/SCORER_ARCH_PROBES_20260712.json`
  + `docs/RUBRIC_RAW_SCORE_20260712.md`.
- Todos los números son de ESTE corpus con SU comparador; ninguna sonda midió
  generalización fuera de las 12 familias de casos existentes — esa es
  precisamente la limitación que el dossier recomienda atacar antes de
  recalibrar.
