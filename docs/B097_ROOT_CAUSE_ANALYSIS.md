# B-097 — Análisis de causa raíz sobre los 33 casos (investigación pura)

**Fecha:** 2026-07-10. **Mandato:** investigación pura — cero parches, sin
aplicar el fix B-097, sin tocar reasoner ni scorer. Los 33 casos con
`best_hypothesis=SUSPICION_DETECTED` vía `ebs_v1_json_adapter` se analizan
**como un solo conjunto**, sin separar a priori por lo que el fix haría.
**Método:** disciplina abductiva — FIRSTNESS (observación medida y
reproducible), SECONDNESS (contraste con el diseño), THIRDNESS (patrón
inferido), separando OBSERVACIÓN de INFERENCIA en cada paso.
**Reproducción:** `scripts/experiments/b097_analysis.py` (in-process,
`_vigia_score` sobre el caso ciego — la etiqueta se remueve antes de puntuar;
determinista). **Restore tag:** `pre-session-20260710-145339`.

---

## 1. FIRSTNESS — qué se observa (medido, por caso)

Para cada caso: `expected_verdict`, composición real de la evidencia
(n_arts, n_types, evidence_types→dominios TAXA, spoofability de perfil),
score del motor, y la rama exacta del ladder que produjo SUSPICION (el
`reason` del scorer la registra textualmente).

**Las ramas del ladder que producen SUSPICION** (`vigia_scorer.py:1105-1234`):
- **S1** — `final_score > 0.33` pero el **gate de corroboración R4-3 v2 no
  abre** ninguna de sus 3 ramas (cross-domain con masa / masa dura /
  costo-por-artefacto).
- **S2** — `0.10 < final_score ≤ 0.33` ("Significant signal with structural
  support") — la banda que la recalibración B-076 define como SUSPICION.

### Tabla de los 33 (orden alfabético; sin agrupar por efecto del fix)

| Caso | exp | score | rama | n_arts | n_types | dominios (arts) |
|---|---|---|---|---|---|---|
| case_002_log_fabrication | SUSP | 0.3354 | **S1** (2 dom, masa 2<4) | 2 | 2 | D1a:1 D2:1 |
| case_008_multi_source_fraud_demo | SUSP | 0.1852 | S2 | 3 | 1 | UNK(?):3 |
| VIGIA-2026-DEMO-008 | SUSP | 0.1482 | S2 | 4 | 3 | mixto |
| VIGIA-BREAK-013 | SUSP | 0.2661 | S2 | 3 | 2 | D3:1 D2:2 |
| VIGIA-BREAK-014 | SUSP | 0.2322 | S2 | 101 | 2 | D1a:100 D2:1 |
| VIGIA_BREAK_001_SILENT_INCONSISTENCY | SUSP | 0.1317 | S2 | — | — | D1a-dominante |
| VIGIA_BREAK_003_CULTURAL_TRUE_POSITIVE | SUSP | 0.1250 | S2 | — | — | D5-soft/D1a |
| VIGIA_BREAK_004_SIGNAL_DROWNING | SUSP | 0.1317 | S2 | — | — | D1a-dominante |
| VIGIA_BREAK_006_PERFECT_ATTACK | SUSP | 0.1250 | S2 | — | — | D1a-dominante |
| VIGIA_BREAK_007_MISSING_LOGS | SUSP | 0.1010 | S2 | — | — | D1a-dominante |
| VIGIA_BREAK_008_AMBIGUOUS | SUSP | 0.1010 | S2 | — | — | D1a-dominante |
| VIGIA_BREAK_009_PROMPT_POISON | SUSP | 0.1010 | S2 | 2 | 1 | D1a:2 |
| VIGIA_BREAK_010_OVERPERFECT | SUSP | 0.1010 | S2 | — | — | D1a-dominante |
| VIGIA-CAN-014 | SUSP | 0.2685 | S2 | 4 | 2 | D2:3 D1a:1 |
| VIGIA-CAN-016 | SUSP | 0.2733 | S2 | 4 | 2 | D2:3 D1a:1 |
| VIGIA-CAN-017 | SUSP | 0.2876 | S2 | 4 | 2 | D2:3 D4:1 |
| VIGIA-CAN-032 | SUSP | 0.2948 | S2 | 4 | 2 | D2:3 D4:1 |
| VIGIA_KIWI_001 | SUSP | 0.2696 | S2 | 4 | 4 | D5s:1 D1a:1 D5m:1 D3:1 |
| VIGIA_KIWI_002_ZAPALLO_POV | SUSP | 0.2003 | S2 | 8 | 3 | D5s:4 D5m:3 D1a:1 |
| VIGIA-LINUX-005 | SUSP | 0.1868 | S2 | 4 | 4 | D3:1 D1a:1 D5s:1 D5m:1 |
| VIGIA-NGDC-003 | SUSP | 0.2803 | S2 | 5 | 4 | D4:1 D2:2 D0:2 |
| VIGIA-NITROBA-M57-001 | SUSP | 0.3135 | S2 | 5 | 3 | D3:1 D2:1 D1a:3 |
| VIGIA-REAL-005 | SUSP | 0.3792 | **S1** (2 dom, masa/hard insuf) | 3 | 1 | UNK(?):3 |
| VIGIA-REAL-M57-JO-Dec07 | SUSP | 0.1812 | S2 | 2 | 2 | D2:2 |
| VIGIA-REAL-M57-PAT-Dec07 | SUSP | 0.1870 | S2 | 2 | 2 | D2:2 |
| VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT | SUSP | 0.4800 | **S1** (1 dom, hard 2t/3a) | 3 | 2 | D2:3 |
| VIGIA-REAL-MAGNET-2021-IOS-ELI | SUSP | 0.2872 | S2 | 4 | 3 | D5s:2 D1a:1 D3:1 |
| VIGIA-REAL-MAGNET-2022-ANDROID | SUSP | 0.2057 | S2 | 4 | 3 | D3:2 D5s:1 D1a:1 |
| VIGIA-REAL-NFURY | SUSP | 0.2352 | S2 | — | — | D1a-dominante |
| VIGIA-SET630-001 | SUSP | 0.2578 | S2 | 3 | 3 | D3:2 D5m:1 |
| **VIGIA-MAGNET-2014-TIMELINE** | **INTENT** | 0.1992 | S2 | 4 | 1 | **D3:4** |
| **VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN** | **INTENT** | 0.2844 | S2 | 4 | 2 | D3:1 D1a:3 |
| **VIGIA-MAGNET-2022-iOS-JESS** | **INTENT** | 0.1395 | S2 | 6 | 2 | D1a:5 D3:1 |

(Los 33 scores provienen del mismo run in-process; todos los S2 verificados
dentro de (0.10, 0.33]. Nota de método: el caso BREAK_009 quedó inicialmente
oculto por un filtro de logs del entorno de análisis que casaba con la
subcadena "PROMPT" de su nombre — se re-verificó individualmente: 0.1010, S2,
2×log_entry D1a. 33/33 analizados, sin huecos.)

### Agregados (OBSERVACIÓN)

- **Ramas:** S2 = 30/33 (incluidos LOS TRES exp=INTENT); S1 = 3/33 (todos
  exp=SUSPICION).
- **Etiquetas:** SUSPICION 30, INTENT 3.
- **Dominios de artefactos en el conjunto:** D1a (log_symbolic) **144**,
  D2 28, D3 15, D5-soft 9, ? 7, D4 6, D5-media 6, D0 3.
  → **log_entry = 144 de ~236 artefactos (61%)** — perfil spoofability 0.85,
  el más blando del registro.
- **n_arts:** mediana 4 (rango 2–101). **n_types:** 12 casos con 1–2 tipos.

### Por qué classify lo subía a INTENT antes de B-095 (los 4 puntos del mandato)

Común a los 33 (verificado, no varía por caso): motor calcula SUSPICION →
B-075 lo mapea a `SUSPICION_DETECTED` → `classify_agent_verdict` regla 2
(`"SUSPICION" in hyp → INTENT`, `vigia_agent.py:180`) lo sella INTENT.
Pre-B-095 el comparador leía la hipótesis pre-gate y reportaba "SUSPICION"
(enmascarando el sellado real); B-095 volvió la métrica honesta y expuso el
colapso. El "bug que lo subía" es el mismo para los 33 — **no hay variación
por caso en esta capa**.

---

## 2. SECONDNESS — contraste con el diseño del scorer

1. **El ladder del motor NO tiene escalón INTENT** (OBSERVACIÓN,
   `vigia_scorer.py:1079-1242` + doctrina en `run_all_agent.py:256-262`):
   espacio {MALICE, SUSPICION, UNKNOWN, NOISE, ABSTAIN}. Un caso cuyo ground
   truth es INTENT **no tiene ningún score que lo selle INTENT** por el path
   motor: o cruza 0.33 + gate → MALICE (que el comparador acepta como
   sobre-severidad para exp=INTENT), o queda SUSPICION. El sellado INTENT que
   estos 3 casos exhiben hoy proviene EXCLUSIVAMENTE del colapso de classify.
2. **Los 3 S1 son el sistema funcionando como se diseñó** (OBSERVACIÓN del
   reason + doctrina B-068/R4-3 v2): score>0.33 pero un solo canal (o dos sin
   masa) no corrobora MALICE. Es el REFUTATION GATE arquitectónico — para
   estos 3 la etiqueta SUSPICION coincide con el cap correcto.
3. **El descuento por spoofability es de diseño, no un defecto**
   (B-067/EVIDENCE_PROFILES): `log_entry` 0.85 se descuenta fuerte porque un
   log es barato de fabricar. El scorer está haciendo exactamente lo que la
   doctrina pide con la evidencia QUE EL CASO DECLARA.

---

## 3. THIRDNESS — el patrón inferido

**No hay UN defecto de scoring; hay TRES mecanismos, y ninguno es un bug del
scorer:**

- **M1 — banda SUSPICION correcta (27 casos, todos exp=SUSPICION):** score en
  (0.10, 0.33], la banda que B-076 calibró como SUSPICION contra ground
  truth. El motor acierta; el único defecto era el colapso de classify
  (B-097) que lo sellaba INTENT.
- **M2 — gate de corroboración correcto (3 casos S1, todos exp=SUSPICION):**
  score>0.33 capeado por R4-3 v2. El motor acierta por la razón correcta
  (autocorrección pre-emisión). Ídem: solo el colapso lo distorsionaba.
- **M3 — sub-tipificación de la evidencia + escalón INTENT inexistente
  (3 casos exp=INTENT):** el motor "sub-puntúa" porque **los casos declaran
  su evidencia con tipos genéricos blandos** (INFERENCIA con evidencia
  concreta, §4), y aunque puntuara más alto, el ladder no tiene INTENT — solo
  podría "pasar" vía MALICE sobre-severo.

### Test de la hipótesis del colectivo (verificada, no asumida)

> *"¿Es posible que TODOS los 33 compartan un único defecto de scoring
> (sub-ponderación sistemática) y la diferencia arregla/rompe sea solo si la
> etiqueta coincide con el score sub-calculado?"*

**Veredicto: PARCIALMENTE CONFIRMADA, con refinamiento estructural.**

- **CONFIRMADO** el núcleo: los 3 exp=INTENT están en la MISMA rama S2 que 27
  de los exp=SUSPICION — mecánicamente indistinguibles del resto del
  conjunto. La única diferencia entre "arregla" y "rompe" es si la etiqueta
  ground-truth coincide con la banda calculada. Los 3 NO son estructuralmente
  distintos en el ladder.
- **REFUTADO** que sea un defecto del *scorer*: para 30 de 33 (M1+M2) el
  score/cap es correcto contra su propia etiqueta — un "fix de ponderación"
  del motor los EMPUJARÍA fuera de su banda correcta. La sub-ponderación
  sistemática existe pero vive en **los datos** (§4), no en los pesos.
- **REFINADO:** para los 3 exp=INTENT hay DOS defectos apilados que el
  colapso enmascaraba: (i) sub-tipificación de sus artefactos (los priva del
  peso/dominio que su evidencia real tendría), y (ii) la ausencia del escalón
  INTENT en el ladder del motor (aunque (i) se corrija, "INTENT por mérito"
  es imposible — solo MALICE sobre-severo).

---

## 4. La sub-tipificación, con evidencia concreta (los 3 exp=INTENT)

| Caso | Lo que la descripción dice | Cómo está tipificado | Tipo canónico disponible |
|---|---|---|---|
| MAGNET-2014-TIMELINE | **Prefetch** WINWORD (ejecución), **LNK** ×2 (USB + doc), doc con contenido | `file_timestamp` ×4 (spoof 0.70, D3) | `prefetch` (0.25, **duro**); LNK≈`file_metadata`; contenido≈D5 |
| MAGNET-2022-IOS-JESS-KEYCHAIN | Reporte **GrayKey** PDF, **keychain dumps** con credenciales en claro ×3 | `file_timestamp` + `log_entry` ×3 (0.70/0.85) | keychain≈`app_data`/credencial (banda mobile B-092) |
| MAGNET-2022-iOS-JESS | **Safari history/searches** ×3, instalación de apps, BFU state | `log_entry` ×5 + `registry_key` (0.85/0.55) | `web_search` (0.45, D3), `app_data` (0.50, D3) |

**Consecuencias medibles de la tipificación genérica (INFERENCIA):**
(a) spoofability alta → descuento fuerte → score deprimido; (b) dominios
colapsados a D1a/D3 genéricos → menos dominios distintos → el gate
cross-domain queda más lejos; (c) menos tipos distintos → masa del gate más
lejos. El patrón NO es exclusivo de los 3: log_entry es el 61% del conjunto
completo — es el catch-all de la conversión de casos legacy.

**Distancia al único "pass" posible post-fix para los 3 (MALICE sobre-severo):**
- JESS (0.1395) y JESS-KEYCHAIN (0.2844): si su score cruzara 0.33, la rama
  cross-domain YA abriría (2 dominios, masa ≥4) → MALICE → PASS
  (sobre-severidad aceptada). Les falta score, no estructura de gate.
- TIMELINE (0.1992): 1 dominio (D3), 1 tipo, 0 duros — ninguna rama abre ni
  cruzando 0.33. Con tipificación canónica (prefetch duro + tipos distintos)
  su estructura de gate cambiaría materialmente. Nota: 4×file_timestamp
  D3-only es exactamente la forma "D3-rico sin triangulación" de §9.4-LIM.

---

## 5. Implicaciones para las opciones de B-097 (sin decidir — son de Anna)

- **(a) aceptar neto +27:** consistente con M1/M2 (30 casos donde el motor ya
  acierta). El costo son los 3 M3, que hoy pasan por accidente del colapso.
- **(b) "calibrar el motor para los 3":** esta investigación la REFINA — no
  es calibración de pesos (eso rompería M1/M2, que están bien); es
  **re-tipificar los artefactos de esos 3 casos** a sus tipos canónicos
  (dato, no código) y re-medir. Con tipificación canónica, JESS/JESS-KEYCHAIN
  tienen camino estructural a MALICE sobre-severo; TIMELINE probablemente
  quede SUSPICION por doctrina §9.4-LIM (D3-only) — lo que sugiere que su
  etiqueta INTENT merece revisión bajo la doctrina (ii) vigente.
- **(c) revisar las 3 etiquetas:** TIMELINE es el candidato más claro
  (evidencia mono-canal D3 — bajo la doctrina sellada, SUSPICION es su techo
  estructural). Los 2 JESS tienen evidencia multi-canal real (D1a+D3) y
  narrativa fuerte — su INTENT es más defendible.
- Cualquier combinación requiere re-correr el gate completo de 199 tras el
  cambio de datos/etiquetas.

## 6. Límites de esta investigación

- Scores de la tabla obtenidos in-process con `_vigia_score` HEAD ciego a la
  etiqueta; los 33 coinciden con los bundles del gate B-097 (consistencia
  verificada por rama/verdict), pero 6 casos figuran "S2-band" sin cifra en
  la tabla (el output completo del script las tiene todas).
- La re-tipificación propuesta en §5(b) NO fue ejecutada (mandato: cero
  cambios) — su efecto sobre score/gate es INFERENCIA fundada en los perfiles
  B-067, no medición.
- `case_008`/`REAL-005` declaran `evidence_type` vacíos ("?") — la conversión
  de esos casos tiene un defecto adicional de tipificación (UNK cuenta como
  dominio propio, conservador).

---

*Investigación pura — cero código de producto tocado. Script reproducible:
`scripts/experiments/b097_analysis.py`.*
