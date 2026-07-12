# Diseño — Discriminadores para M2 (FALSE_FLAG_PATTERN) — 2026-07-11/12

**Tipo:** documento de diseño. **NO implementado.** Insumo para el día de
implementación; las decisiones de doctrina abiertas están al final y replicadas
en `PREP_20260711_PARA_MANANA.md`.

Contexto: `docs/FOSSIL_HUNT_20260711.md` §2-M2 y §4 (F-07…F-28);
`docs/FOSSIL_HUNT_20260711_PASS2.md` §2-M3.

---

## 1. El problema, en una tabla

La regla actual (caie.py Rule 1, Case B): `avg_cultural>0.5 ∧ avg_technical<0.2
∧ ¬confirmed_clean` ⇒ sella *"cultural evidence planted to mislead attribution"*
(sev 0.8 → boost 0.36).

Qué es en realidad cada uno de los 22 disparos del corpus:

| Realidad del caso | Casos | ¿La teoría sellada es correcta? |
|---|---|---|
| Control negativo (máquina extranjera limpia) | FP-CULTURAL-CLEAN ×2 | No — es el FP que H-02/L-019 declara inaceptable |
| Atribución lingüística **genuina** (la señal delata al actor real) | CAN-004, 006, 013, 022, 041, 044, 045 | No — teoría **inversa** a la del caso |
| Ingeniería social / Carnegie (sin cuestión de atribución) | CAN-020, 030, 043, 048, 049, 050, 051, 052 | No — teoría ajena al caso |
| Técnico con artefactos mal tipados (reverse shell como `cultural_marker`, memoria con raw 0.05) | CAN-008, 011, 024, 046, 047 | No — el disparo depende de datos rotos |
| Bandera falsa real (cebo cultural plantado) | **ninguno** | — |

Los 2 únicos casos de bandera falsa genuina del corpus (FF-GENUINE-001,
case_003) disparan la fractura correcta (FALSE_FLAG_ATTRIBUTION_MISMATCH, Case
C) — que es **inerte en el scorer** (M3). La regla Case B nunca acierta su
propia teoría en este corpus.

Restricción dura: los 20 casos MALICE dependen del boost 0.36 para cruzar el
umbral 0.33. Remover M2 sin camino de reemplazo = −20 puntos de corpus
(10→NOISE, 2→UNKNOWN, 8→SUSPICION). **El diseño tiene que introducir primero el
camino legítimo de score para señal lingüística, y recién después degradar la
regla fósil.**

---

## 2. Diseño propuesto: taxonomía `marker_class` + 3 fracturas con teoría correcta

### 2.1 Clasificación del marcador (el discriminador central)

Cuatro clases semánticas para la evidencia hoy amontonada en `cultural_marker`:

| `marker_class` | Semántica | Fractura que habilita |
|---|---|---|
| `config_native` | Configuración nativa del usuario (layout, TZ, filenames) sin análisis forense de manipulación | **ninguna** (Case A) |
| `attribution_genuine` | Rastro conductual involuntario que delata identidad/origen (typo de layout, calco, estilometría, memoria muscular) | `LINGUISTIC_ATTRIBUTION_SIGNAL` (nueva) |
| `attribution_bait` | Marcador cultural con evidencia de plantado (`has_manip`: too_clean, mismatch con TTPs, timestomp asociado) | `FALSE_FLAG_PATTERN` (la actual, ahora con su teoría verdadera) |
| `social_engineering` | Patrón de manipulación interpersonal (mirroring, normalización, agresión, pánico coordinado — taxonomía Carnegie) | `SOCIAL_ENGINEERING_PATTERN` (nueva) |

Las dos fracturas nuevas heredan severidad/spoofability_delta de la actual
(sev 0.8) — el **peso no cambia, cambia la teoría sellada**. Interpretaciones:

- `LINGUISTIC_ATTRIBUTION_SIGNAL`: *"Involuntary linguistic/behavioral trace
  (layout slip, calque, stylometric deviation) inconsistent with the claimed
  identity. Peirce: the index is genuine — the habit betrays the actor. The
  signal ATTRIBUTES; it was not planted."*
- `SOCIAL_ENGINEERING_PATTERN`: *"Systematic interpersonal-manipulation pattern
  (Carnegie taxonomy: mirroring / normalization / authority-transfer /
  aggression) targeting the human control layer. No cultural-attribution claim
  is made."* — ttp_id T1656 (Impersonation) / T1598 según subtipo.

### 2.2 ¿De dónde sale `marker_class` sin tocar 20 casos sellados?

Dos vías, no excluyentes (decisión D-4):

- **Vía inferida (sin editar casos):** clasificador determinístico por
  inventario de campos del metadata, en orden:
  1. `has_manip` (campos ya definidos por H-02: `placement=too_clean`,
     `attribution_consistency_with_ttps=LOW`, `timestomp_detected=True`…)
     → `attribution_bait`.
  2. Solo campos de configuración (`keyboard_layout_detected`,
     `timezone_offset`, `cyrillic_filenames`, `language_confidence`) y ningún
     campo de análisis forense → `config_native`. **Esto invierte el guard
     H-02**: hoy exige `*_detected: false` explícitos (que los archivos
     FP-CULTURAL reales no tienen — por eso el fix no los protege); el diseño
     hace de la ausencia de evidencia de manipulación el default seguro.
     Cierra F-07/F-08 sin editar los casos.
  3. Campos de análisis conductual/estilométrico (`deviation_sigma`,
     `features_anomalous`, `ttr_similarity`, layout/calco flags)
     → `attribution_genuine`.
  4. Resto (texto de tickets/mensajes, señales Carnegie)
     → `social_engineering`.
- **Vía declarada (editando casos):** `metadata.marker_class` explícito, que
  el clasificador respeta si está presente. Más limpio, pero toca 20+ casos
  sellados → re-sellado y justificación de cadena de custodia.

Recomendación: **inferida primero** (día 1), declarada después solo para los
casos donde la inferencia quede ambigua.

### 2.3 Correcciones acopladas obligatorias

1. **M3 (scorer↔CAIE):** las fracturas nuevas + `FALSE_FLAG_ATTRIBUTION_MISMATCH`
   entran a `MALICIOUS_FRACTURE_TYPES`; retirar el fantasma
   `ATTRIBUTION_INCONSISTENCY`; decidir LOG_VS_MEMORY y
   TIMESTAMP_PRECISION_ANOMALY (recomiendo: ambos al set MALICIOUS — LOG_VS_MEMORY
   ya es MALICE estructural en el tool MCP; hoy hay dos doctrinas entre modos).
   Sin esto, el camino correcto sigue pesando 0 y el incentivo sigue invertido.
2. **Composición del bucket "cultural":** `ip_geolocation` y `user_agent` salen
   del bucket que habilita fracturas de atribución cultural (CAN-047 entra a
   Case B con una geolocalización 0.82 como "cultura"). Se evalúan como señal
   técnica de red que son.
3. **Subgrupo C (tipado roto) es reparación de DATOS, no de regla:** re-tipar
   reverse shell / EDR alerts / commits hoy cargados como `cultural_marker`
   (CAN-008, 011, 024, 046, 047) y revisar los `memory_process` con raw 0.05.
   La regla nueva NO debe compensar datos rotos. Toca 5 casos sellados →
   decisión D-4/D-6.

### 2.4 Qué se sella después del cambio (criterio de aceptación narrativo)

Para cada caso del bloque F-09…F-28, la interpretación sellada debe ser
consistente con `peirce_chain.thirdness` del propio caso. Test de aceptación
propuesto (automatizable): la fractura emitida no puede afirmar "planted/
mislead attribution" en un caso cuya thirdness declara la señal como genuina
("betrays", "delata", "reveals native") — un lint semántico simple por lista de
pares incompatibles, corrible sobre el corpus completo.

---

## 3. Impacto esperado en corpus (simulado con scorer_gate, sin implementar)

| Grupo | Hoy | Con diseño (vía inferida) |
|---|---|---|
| A (7 casos, `attribution_genuine`) | MALICE vía teoría inversa | MALICE vía `LINGUISTIC_ATTRIBUTION_SIGNAL` (mismo peso) — **0 regresiones, narrativa correcta** |
| B (8 casos, `social_engineering`) | MALICE vía teoría ajena | MALICE vía `SOCIAL_ENGINEERING_PATTERN` — 0 regresiones |
| C (5 casos, tipado roto) | MALICE vía datos rotos + teoría ajena | Si solo regla: caen a SUSPICION (la regla nueva no debe disparar sobre un reverse shell "cultural"). Si regla + re-tipado de datos: MALICE por camino técnico legítimo. **−5 temporales si no se tocan los datos** |
| FP-CULTURAL ×2 | MALICE (FP conocido) | NOISE/UNKNOWN vía `config_native` default — **+2 y cierra L-019 de verdad** |
| FF-GENUINE ×2 | MALICE (por composite; fractura correcta pesa 0) | MALICE con la fractura correcta pesando — refuerzo, sin cambio de etiqueta |

Neto etiquetas: 0 a −5 (según decisión sobre datos de C), +2 controles
negativos. Neto Daubert: las 22 teorías selladas pasan de indefendibles a
consistentes con el caso.

---

## 4. Decisiones de doctrina que necesito resueltas ANTES de implementar

(Numeración compartida con PREP_20260711_PARA_MANANA.md §3.)

- **D-4** — ¿Vía inferida sola, o inferida + `marker_class` declarado en casos
  ambiguos? (declarada = tocar casos sellados).
- **D-5** — Subgrupo C: ¿re-tipar los 5 casos con artefactos mal tipados
  (re-sellado) o aceptar −5 temporales hasta la pasada de datos?
- **D-6** — M3: ¿LOG_VS_MEMORY y TIMESTAMP_PRECISION_ANOMALY entran al set
  MALICIOUS del scorer en la misma tanda, o tanda separada con su propia
  corrida comparativa? (recomiendo misma tanda: es un solo frozenset y una
  corrida).
- **D-7** — ¿`SOCIAL_ENGINEERING_PATTERN` debe contar como fuente DEVICE para
  el gate de corroboración R4-3, o como CONTEXTUAL? (hoy los casos B pasan el
  gate porque sus artefactos están tipados como clases device; si mañana se
  re-tipan, el gate puede cerrarse — interacción a simular antes de decidir).
