# FOSSIL HUNT — Pasada 2: tipos de fractura no cubiertos + alcance B-115 (2026-07-11/12)

**Tipo:** cacería y diagnóstico. **NO contiene fixes.** Complementa
`docs/FOSSIL_HUNT_20260711.md` (pasada 1: M1-TCV y M2-FALSE_FLAG_PATTERN).

Harness: `scripts/experiments/scorer_gate.py` (materializado en esta pasada —
ablación por instancia/tipo sobre `_vigia_score` real, con `--narrative-diff` y
modo `--corpus`).

---

## 1. Cobertura de la pasada 2

### 1.1 Tipos nombrados en el encargo (RED_HERRING, MULTI_ACTOR_ATTRIBUTION_CHALLENGE, MISSING_AUTHORIZATION, TEMPORAL_IDENTITY_VIOLATION, COGNITIVE_DOS, MEMORY_VS_DISK, PARENT_ANOMALY)

**Ninguno existe en el CAIE vivo.** Existen solo como `caie_fractures`
pre-computadas dentro de los JSONs de casos (~40 tipos exóticos distintos:
RED_HERRING, PARENT_ANOMALY, MEMORY_VS_DISK, SELF_AUTHORIZATION,
SUPPLY_CHAIN_INJECTION, etc.).

Hallazgo estructural: **`caie_source = live_caie` en 198/198 casos evaluados.**
El path `json_fallback` de `_vigia_score` (línea ~651) no se ejercita nunca en el
corpus — toda `caie_fracture` declarada en un JSON es **dato muerto** para el
veredicto. Consecuencias:

- No pueden ser fósiles de corpus hoy (no tocan el score). Auditoría cerrada
  por vacuidad.
- **Riesgo latente L-A:** si el import de CAIE fallara (deploy parcial,
  standalone), esos tipos entrarían al scorer, donde ninguno está en
  `MALICIOUS_FRACTURE_TYPES` ni `CREDIBILITY_REDUCING_TYPES` — serían inertes
  para el boost **pero** harían `fractures` no-vacío, habilitando la rama
  `mean_effective < 0.15 and fractures → SUSPICION` y el estado quadripartite.
  Un JSON adversarial con `caie_fractures` inventadas podría fabricar SUSPICION
  solo en modo degradado. Anotar, no urgente.

### 1.2 Tipos del CAIE vivo que la pasada 1 no analizó

Instancias disparadas en el corpus y su ablación (scorer_gate):

| Tipo | Casos | ¿Decide veredicto? | Lectura |
|------|-------|--------------------|---------|
| FALSE_FLAG_ATTRIBUTION_MISMATCH | FF-GENUINE-001, case_003_false_flag | No (0.4458 → 0.4458, **delta exactamente 0**) | Legítima por diseño (bandera falsa genuina, Case C del fix H-02) — pero **inerte en el scorer**, ver M3 |
| NARRATIVE_POISONING_DETECTED | VIGIA-BREAK-016 | No (0.752 → 0.702) | Legítima por diseño (el caso ES narrative poisoning). ADN fósil latente, ver L-B |
| CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED | VIGIA-CAN-028 | No (es penalidad: removerla SUBE 0.388 → 0.538) | Legítima (reporte VIGÍA falsificado, HMAC FAIL declarado). Cosmético: sella "Hash mismatch: unknown... != unknown..." cuando el caso no incluye los valores de hash |
| TIMESTAMP_PRECISION_ANOMALY | VIGIA-CAN-037 | No (0.99 → 0.99, **delta 0**) | Legítima (firma de 7 ceros = timestomping por diseño) — pero **inerte en el scorer**, ver M3 |
| USN_JOURNAL_GAP | VIGIA-CAN-037 | No (0.99 → 0.685, MALICE se sostiene) | Legítima (flag explícito `usn_journal_gap` en caso de timestomping diseñado) |

### 1.3 Reglas dormantes (0 disparos en el corpus)

`LOG_VS_MEMORY`, `VERDICT_CONFLICT`, `DOCUMENT_FORGERY`, `METADATA_CONCEALMENT`,
`NETWORK_VS_HOST`, `CRYPTOGRAPHIC_INCONSISTENCY` (verificada), `MFT_ENTRY_ANOMALY`.
Auditadas estáticamente: son flag-driven (metadata estructurada declarada:
`digital_perfection_detected`, `firewall_claim`+puertos, monotonicidad MFT#) —
la comparación es coherente y reproducible; no tienen la mecánica de substring
de M1. Sin ADN fósil relevante, salvo la nota de que `VERDICT_CONFLICT` lee
`metadata.verdict` (veredicto derivado, no hecho observable — contradice el
propio criterio L-028 escrito en la Rule 2 vecina). Menor.

---

## 2. M3 — Desincronización scorer ↔ CAIE (fósil de motor, no de caso)

**El hallazgo nuevo de la pasada 2.** No es una fractura sin sentido: es que el
mapa de pesos del scorer quedó fosilizado respecto del catálogo real de CAIE.

### Firstness (qué se observa)

`vigia_scorer.py` (~líneas 956–977):

- `MALICIOUS_FRACTURE_TYPES` (boost sev×0.45) **no incluye**:
  - `FALSE_FLAG_ATTRIBUTION_MISMATCH` — la fractura Daubert-correcta que el fix
    H-02 introdujo para banderas falsas genuinas (Case C + Rule 1b);
  - `LOG_VS_MEMORY` — que en el `evaluate()` de CAIE es
    `_STRUCTURAL_MALICE_TYPES` (fuerza MALICE en el tool MCP);
  - `TIMESTAMP_PRECISION_ANOMALY` — firma de herramienta anti-forense,
    spoofability 0.05.
- `CREDIBILITY_REDUCING_TYPES` **incluye** `ATTRIBUTION_INCONSISTENCY`, un tipo
  que **CAIE v2.0 no genera** (fantasma — la misma familia que el saneo P4
  documentado ahí mismo decía haber cerrado).

### Secondness (verificación empírica, scorer_gate)

- FF-GENUINE-001 / case_003: ablacionar FALSE_FLAG_ATTRIBUTION_MISMATCH deja el
  score **bit-idéntico** (0.4458 → 0.4458). La fractura correcta pesa 0.
- VIGIA-CAN-037: ablacionar TIMESTAMP_PRECISION_ANOMALY deja 0.99 → 0.99.
- Mientras tanto, la fractura fósil FALSE_FLAG_PATTERN (M2) pesa 0.36 y decide
  20 veredictos MALICE.

### Thirdness (el patrón)

**El incentivo está invertido:** el camino semánticamente correcto (bandera
falsa confirmada con ataque real; firma de timestomp) no aporta score, y el
camino fósil (cultura alta + técnica baja) aporta 0.36. Cualquier autor de
casos que quiera que su bandera falsa "funcione" en el motor está empujado a
modelarla como M2, perpetuando el fósil. Misma familia que P1-K (2026-05-19:
CRYPTOGRAPHIC_INCONSISTENCY_UNVERIFIED invisible al scorer) y que el saneo P4 —
el catálogo de tipos evoluciona en caie.py y el mapa de pesos del scorer se
fosiliza. Inconsistencia adicional inter-modo: el tool MCP
`cross_artifact_analysis` declara LOG_VS_MEMORY como MALICE estructural, pero el
veredicto sellado del Modo 1 lo ignora — dos modos, dos doctrinas.

**Dossier:**
1. *Evidencia real sin el fósil:* n/a — es un fósil de mapa de pesos, no de caso.
2. *Distancia al umbral:* FF-GENUINE-001/case_003 hoy salen MALICE por otros
   caminos (composite alto). El daño es de incentivo y de narrativa, no de
   etiqueta actual.
3. *Contradicción de diseño:* el comentario P4 del propio scorer dice
   "sanitised — only types CAIE v2.0 generates" mientras lista un tipo que CAIE
   no genera y omite tres que sí.
4. *Lectura:* **fósil de motor confirmado (M3).** Fix barato (alinear dos
   frozensets + test de paridad scorer↔CAIE), pero requiere corrida comparativa:
   agregar FALSE_FLAG_ATTRIBUTION_MISMATCH al set MALICIOUS sube score en
   FF-GENUINE-001/case_003 (ya MALICE — sin cambio de etiqueta esperado) y
   TIMESTAMP_PRECISION/LOG_VS_MEMORY pueden mover otros casos.

### Latentes anotados (sin daño de corpus hoy)

- **L-B — NARRATIVE_POISONING_DETECTED:** keywords por substring en texto libre
  (`"approved"`, `"aprobado"`, `"benign"`, `"caso cerrado"`…) × producto
  cartesiano contra cualquier artefacto técnico con raw>0.7 → sev 0.85 c/u
  (boost saturable al cap 0.5 con un par de matches). En el corpus solo dispara
  en BREAK-016 (TP por diseño). Con logs reales ("change request approved") es
  una máquina de falsos positivos de la misma familia que el `'red'` de M1.
- **L-A — json_fallback:** ver §1.1.
- Cosmético: CRYPTO_UNVERIFIED sella "unknown != unknown" si el caso no trae
  hashes (CAN-028).

---

## 3. B-115 — ¿aislado o sistémico? SISTÉMICO (26/54 de consolidated_canonical)

### Alcance medido

Barrido de los 199 casos (173 con ≥2 timestamps) buscando split de épocas
(mayor gap entre timestamps consecutivos del caso > 30 días):

- **45 casos con split >30d**, pero hay que separar:
  - **26 en `consolidated_canonical/` — TODOS defecto B-115** (48% del
    directorio, que tiene 54 casos).
  - 15 en `data/cases/` + 4 en `converted/` — **multi-época legítima** en casi
    todos (FLAREON: zip 2026 conteniendo challenges 2019-2025; NOKIA/NITROBA/
    DOMEXUSERS: adquisición 2026 de evidencia 2004-2008; MAGNET-2020: la
    audit policy 2009 es un dato real del SO). Ahí el problema no es el dato —
    es que TCV compare a través de esas épocas (eso es M1, ya documentado).

### Mecánica exacta del defecto (causa raíz encontrada)

En los 26 casos afectados conviven **dos series de fechas dentro del mismo
artefacto**:

- `timestamp` (top-level): serie ~enero 2026 — **coherente con la narrativa**
  al segundo. Ej. CAN-031: `a004_01` 22:15:30 (PowerShell) → `a004_03` 22:16:18
  (búsqueda Google, +48 s) → `a004_02` 22:16:33 (ticket IT, +63 s) — exactamente
  los deltas que declara la descripción del caso.
- `metadata.process_creation_time` / `metadata.network_log_time`: serie
  ~abril 2026, **+84 a +105 días** adelantada (algunos casos +134/+169 con
  fechas sept/oct 2026, ¡futuras respecto de la adquisición declarada!).

Ambas series avanzan ~+1 día por índice de caso (case_084 → 01-16/04-10,
case_087 → 01-17/04-12, case_091 → 01-18/04-14…): **dos pasadas procedurales de
generación de fechas**, no errores manuales.

**Origen:** el defecto ya está en el dataset fuente
`vigia_cases_canonical_v2.json` (presente en `scripts/` y `data/cases/`) — los
artefactos ahí traen `timestamp` de enero Y `metadata.*_time` de abril. No es
el consolidador: es la autoría/generación de la metadata de enriquecimiento de
canonical_v2, que estampó fechas frescas sin re-anclarlas a la línea de tiempo
del `timestamp`.

**Amplificador:** la regla TCV **prefiere** `metadata.*_time` sobre `timestamp`
(`net.metadata.get("network_log_time") or net.timestamp`), así que consume
exactamente la serie rota y compara abril-contra-enero → TCVs cross-epoch de
84–169 días.

### Inventario (26 casos, por gap)

| Gap | Casos |
|-----|-------|
| >130d (fechas futuras post-adquisición) | CAN: case_020_mimetismo (169d), case_110_paradoja_auditor (158d), case_016_auto_gaslighting (135d) |
| 84–105d (patrón ene→abr núcleo) | case_010, case_005, case_007, case_004 (F-03), case_111, case_109, case_105, case_108 (F-04), case_103, case_101, case_100, case_099, case_096, case_098, case_092, case_091, case_089, case_087, case_085, case_084, case_008_paranoia |
| 45–82d | case_094 (F-05, 45d), case_012 (F-06, 14d de split efectivo vía net_lt) |

De los 26: **13 disparan TCV hoy** (los que además tienen `memory_process` +
match del filtro "network"), **6 deciden veredicto** (F-03…F-06 de la pasada 1
más los cross-epoch de case_094/case_012), y los 13 restantes son **latentes**
(la TCV aparecería si un artefacto cambia de tipo o de descripción).

### Respuesta a la pregunta del encargo

**Sistémico.** No son 2 casos: son 26, todos del mismo lote (canonical_v2), con
mecánica de generador identificable y dos amplificadores (preferencia de TCV por
`metadata.*_time` + filtro substring M1). CAN-026 y CAN-031 son simplemente los
dos donde el efecto llegó a decidir el veredicto con contradicción narrativa
visible.

Nada corregido — inventario para decidir mañana si el fix es de datos
(re-anclar `metadata.*_time` a la serie coherente), de regla (exigir coherencia
a TCV), o ambos.

---

*Harness: `scripts/experiments/scorer_gate.py` (`--filter`, `--instance`,
`--narrative-diff`, `--corpus`). Corpus: 199 casos. Cero escrituras fuera de
docs/ y scripts/experiments/. Restore tag vigente: `restore-fossil-hunt-20260711`.*
