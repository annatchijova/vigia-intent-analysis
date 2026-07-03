# Investigación abductiva — por qué el FP VIGIA-NGDC-003 puede existir

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Método:** protocolo peirciano de VIGÍA aplicado reflexivamente al propio scorer
(Firstness → Secondness → Thirdness + Refutación de Eco). Solo lectura +
experimentos reproducibles; ningún cambio de código.
**Relación:** profundiza el diagnóstico de B-068 (fix del gate). La abducción
surface un **segundo canal del mismo error que B-068 NO cerró** — candidato B-070.

---

## Resumen

El FP no es un defecto aislado del gate de corroboración. Es la consecuencia
**necesaria** de tres hechos de diseño que colisionan sobre un caso de
herramienta dual-use. La documentación del escenario — artefactos cuyo propio
contenido dice "la intención no puede resolverse" — se contabilizaba como
corroboración de intención **y** se sumaba al score de malicia. Los artefactos
más literalmente sobre la *indecidibilidad* de la intención eran los que la
*decidían*. B-068 cortó ese efecto en el gate; **sigue abierto en el composite**
(8 casos del corpus afectados, 1 flip de veredicto, inflación de confianza de
hasta +0.30).

---

## FIRSTNESS — qué observo (fenomenología, sin interpretar)

`VIGIA-NGDC-003` (National Gallery DC 2012 — Joe instala el keylogger LogKext
en la MacBook familiar durante el divorcio de Tracy) puntuaba **MALICE**
(pre-B-068), `expected_verdict=SUSPICION`, `confidence_expected=67`.

Sus artefactos (5):

| # | evidence_type | raw_score | adjusted (aporte al composite) | naturaleza |
|---|---------------|-----------|-------------------------------|------------|
| 1 | `malware_infrastructure` | 0.88 | 0.1222 | técnico (dispositivo) |
| 2 | `keylogger_capture` | 0.71 | 0.0953 | técnico (dispositivo) |
| 3 | `keylogger_capture` | 0.82 | 0.1128 | técnico (dispositivo) |
| 4 | `behavioral_context` | 0.65 | 0.0783 | **narrativa de escenario** |
| 5 | `outcome_signal` | 0.55 | 0.0681 | **narrativa de escenario** |

Los artefactos 4 y 5 son documentación del escenario (fuente: "Digital Corpora
scenario documentation"). Su propio texto declara la indecidibilidad:
- #4 `behavioral_context`: *"Neither motivation can be ruled out from the
  artifact record."*
- #5 `outcome_signal`: *"This prosocial outcome is consistent with both the
  parental monitoring hypothesis ... and the spousal surveillance hypothesis."*

El evidence técnico es la salida de **una sola herramienta** de vigilancia
(su infraestructura + dos agregados de su captura de teclas).

---

## SECONDNESS — anomalía estructural contra la línea base

Los 4 casos NGDC son la **misma familia forense** (National Gallery DC 2012,
keylogger LogKext, Joe/Tracy). Eso los hace una línea base natural:

| Caso | expected | conf_exp | Técnicos (art/tipos) | ¿pasa gate solo-técnicos? | vía |
|------|----------|----------|----------------------|---------------------------|-----|
| NGDC-001 | MALICE | 97 | 6 / **5** | **sí** (holgado) | evidencia heterogénea convergente (email+red+FS+recovery) |
| NGDC-002 | MALICE | 83 | 6 / 2 | **sí** | **volumen** técnico (6 artefactos ≥ 4) |
| NGDC-004 | MALICE | 81 | 6 / 3 | **sí** | 3 tipos técnicos |
| **NGDC-003** | **SUSPICION** | **67** | **3 / 2** | **NO** | — falla ambas ramas del gate |

NGDC-003 es el **único** hermano cuyo evidence técnico es simultáneamente de
bajo volumen (3 < 4) y baja diversidad (2 < 3). Es también el único que los
autores marcaron a 67% (vs 97/83/81). El gate (`n_art ≥ 4 OR n_types ≥ 3`)
estaba **estructuralmente en lo correcto**: el evidence de dispositivo de
NGDC-003 no alcanza el umbral de corroboración.

Sólo pasó por **doble efecto** de los 2 artefactos narrativos (medido):

1. **Inflan el conteo del gate:** 3 art / 2 tipos → **5 art / 4 tipos** → el
   gate pasa.
2. **Inflan el composite:** score solo-técnicos **0.2803** → con contexto
   **0.4296** (**+0.1493**, cruza el umbral MALICE de 0.33). Y la confianza
   `min(0.95, score×2)`: **0.56 → 0.86** (+0.30, sobrepasa el 0.67 del caso).

B-068 corrigió (1). **(2) sigue vivo.**

---

## THIRDNESS — la ley que hace posible el FP

El FP no es un accidente: es la salida forzada de tres hechos de diseño cuando
se los somete a un caso dual-use.

**(a) `raw_score` mide fuerza-de-anomalía, no certeza-de-intención.**
Un keylogger corriendo como root exfiltrando cada hora es una anomalía técnica
máxima — con firma **idéntica** sea la intención legal (monitoreo parental de
una menor) o ilegal (espionaje conyugal). Para una herramienta dual-use, fuerza
de anomalía y certeza de intención se **desacoplan**.

**(b) El modelo de datos no distingue evidencia-de-dispositivo de
contexto-narrativo.** Ambos fluyen por el mismo pipeline: `raw_score` → composite,
`evidence_type` → conteo del gate. Un artefacto que documenta el *motivo* o el
*desenlace* del caso entra al scorer con exactamente el mismo estatus que un
volcado de memoria.

**(c) El gate de corroboración es el ÚNICO órgano del sistema que adjudica
certeza-de-intención** (la frontera MALICE/SUSPICION). Y la operacionaliza como
*cantidad/diversidad de evidencia*.

**Bajo (a)+(b)+(c), el error es necesario:** los artefactos narrativos — incluso
los que en su propio texto declaran "la intención no puede resolverse" — se
cuentan como corroboración de intención y se suman al composite de malicia. **El
artefacto que dice "esto no decide la intención" es contabilizado como si la
decidiera.** Esa inversión es la ley.

Condición mínima de reproducción: (evidence técnico bajo el gate) ∧ (hay
artefactos de contexto) ∧ (score en la banda 0.33–0.65). NGDC-003 es el único
caso del corpus en esa intersección — por eso quedó **latente**: su hermano
NGDC-002 enmascara el patrón (6 artefactos técnicos → MALICE con o sin contexto).

---

## REFUTACIÓN (razor de Eco) — ¿pudo el MALICE ser correcto?

Hipótesis benigna a refutar: *"el expected está desactualizado; NGDC-003 es
realmente MALICE."* Para sostenerse debería explicar TODO el evidence sin
contradicción. No lo hace:

1. El propio caso, en `peirce_expected.thirdness`, argumenta que SUSPICION es
   *"the only epistemologically honest verdict"*.
2. `confidence_expected=67` frente a 97/83/81 de los hermanos = marca
   deliberada de intención disputada.
3. El evidence técnico **solo** puntúa 0.2803 (banda SUSPICION) y **falla el
   gate**. Todo el MALICE lo cargaban los 2 artefactos cuyo texto niega la
   resolución de intención. Sostener MALICE exige **ignorar el contenido de los
   propios artefactos**.

La hipótesis benigna explica todo; la de MALICE requiere descartar evidence.
**Refutada. SUSPICION se mantiene** — y era un FP real, no un expected viejo.

---

## Lo que la abducción surface más allá de B-068 — canal composite (candidato B-070)

B-068 cerró el **canal del gate** (contexto ya no cuenta como clase de
corroboración). El **canal del composite sigue abierto**: los artefactos de
contexto siguen sumando su `raw_score` al score de malicia. Medición sobre el
corpus (8 casos tienen artefactos de contexto):

| case_id | score s/contexto → c/contexto | efecto |
|---------|-------------------------------|--------|
| VIGIA-LINUX-005 | 0.1458 → 0.1868 | **FLIP UNKNOWN→SUSPICION** (el contexto solo cruza el umbral) |
| VIGIA-NGDC-003 | 0.2803 → 0.4296 | confianza 0.56→0.86; verdict salvado por B-068 |
| VIGIA-NGDC-002 | 0.4785 → 0.5680 | MALICE (ya lo era; contexto infla confianza) |
| VIGIA-NGDC-001 | 0.7052 → 0.7781 | idem |
| VIGIA-LINUX-001 | 0.3432 → 0.4541 | idem |
| VIGIA-REAL-NROMANOFF | 0.4188 → 0.4370 | idem |
| VIGIA-REAL-NFURY | 0.2352 → 0.2465 | idem |
| VIGIA-LINUX-002 | 0.0519 → 0.0696 | NOISE (benigno; sin flip) |

**Un flip de veredicto** (LINUX-005) y varias inflaciones de confianza atribuibles
a evidence narrativo. El score de malicia no debería subir por un artefacto que
documenta el *desenlace* o el *motivo* — menos aún por uno que declara la
intención indecidible.

### Propuesta (decisión de doctrina — NO implementada)

Coherente con la ley identificada, hay tres opciones, en orden de menor a mayor
cambio:

1. **Excluir las clases de contexto también del composite** (no solo del gate):
   simétrico a B-068. Riesgo: mueve 8 casos (medido); 1 flip esperado
   (LINUX-005 SUSPICION→UNKNOWN — que puede ser *correcto*: sin evidence
   técnico suficiente, UNKNOWN es más honesto). Requiere corrida comparativa
   completa y revisión caso por caso.
2. **Peso de contexto → 0 en el composite, retención como narrativa**: los
   artefactos de contexto informan el reporte (motivo, desenlace) pero no
   mueven el número. Es la separación que (b) no hace hoy.
3. **Tipar `signal_class` a nivel de dato** (device vs narrative) y que scorer,
   gate y CAIE lo respeten — cierra la causa raíz (b) de una vez, en lugar de
   parchear cada consumidor. Mayor esfuerzo; conecta con la propuesta de
   registro único de tipos de B-060.

Es decisión de doctrina de la dueña del proyecto: si la evidencia narrativa
debe mover el score de intención, o solo la narrativa del reporte. B-068 ya
garantiza que **ningún veredicto** actual del corpus es incorrecto por esto; el
canal composite afecta score/confianza y un flip UNKNOWN↔SUSPICION.

---

## Metodología y reproducibilidad

- Traza de score y gate: `_vigia_score` real sobre los 4 casos NGDC y variantes
  (con/sin artefactos de contexto), proceso efímero, código en disco intacto.
- Alcance del canal composite: barrido sobre `data/cases/**` (8 casos con
  clases de contexto), score con y sin esos artefactos.
- Referencias: B-068 (fix del gate), B-060 (registro único de tipos),
  familia B-058/B-062 (dos-caminos de veredicto). Clases de contexto tomadas
  de `_CONTEXT_EVIDENCE_TYPES` (vigia_scorer.py, B-068).
- **Ningún archivo de código modificado.**
