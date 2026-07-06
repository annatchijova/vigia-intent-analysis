# AUDITORÍA — FUGA INDIRECTA DE ETIQUETA Y 4 HIPÓTESIS ASOCIADAS

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-07-06 |
| **Tag de restauración** | `pre-session-20260706-021939` (creado local; el push del tag al remoto fue rechazado con HTTP 403 — el remoto solo acepta pushes a la rama designada. El tag existe en el clon local de esta sesión). |
| **Alcance** | Solo medición. Ningún archivo de código fue modificado. |
| **Método** | Lectura de código con cita `archivo:línea` + ejecución empírica del scorer/adaptadores sobre casos reales del corpus y valores de frontera sintéticos. Todo output citado abajo es salida real de ejecución en este working tree (HEAD `849475b`). |

---

## RESUMEN EJECUTIVO

- **H1 (fuga por metadatos): CONFIRMADA — pero la puerta no es el nombre del caso, es `expected_verdict`, y son DOS puertas.** El nombre (`case_id`) no entra al path de decisión (verificado). En cambio `normalize_case_schema()` lee la etiqueta ground-truth y reduce `raw_score × 0.25` para casos benignos legacy — y esa función corre CON etiqueta en el harness de evaluación (`tests/run_vigia_case.py`), en la API y en calibración. Medido: **15/15 casos BEN flipean de veredicto** según la etiqueta esté o no. Peor: `scripts/convert_legacy_cases.py` **persistió esa misma reducción en los archivos del corpus canónico** — la fuga sobrevive al fix B-075 porque vive en los datos, no en el runtime.
- **H2 (combinatoria mobile): consistente con la doctrina declarada.** SIP + phishing + contactos no-parseados → `SUSPICION_DETECTED` (dominado por SIP z=2.4). B-072/073/074 se comportan como está documentado.
- **H3 (TOCTOU): asimetría real.** `read_evidence` está endurecido; `generate_forensic_hash` no (open() plano, sin O_NOFOLLOW, sin verificación post-read), y ningún código cruza el hash de custodia con el hash de lectura. El pipeline de texto del agente tiene 4 patrones check-then-use.
- **H4 (copias divergentes): 144 nombres de función con cuerpos distintos en >1 archivo.** Las copias divergentes de CAIE y del detector técnico están muertas (sin importadores); hay dos validadores de seguridad divergentes ambos vivos; y coexisten TRES escaleras de decisión con umbrales incompatibles.
- **H5 (bordes de umbral): todos los umbrales son estrictos (`>`), con dos consecuencias medidas:** los peldaños mobile que emiten exactamente z=3.0 nunca pueden producir INTENT, y el ladder del adaptador vol3 tiene la rama `INTENT_DETECTED` **estructuralmente muerta** (umbral 1/2 evaluado después de descartar >1/3).

---

## H1 — FUGA DE ETIQUETA POR METADATOS INDIRECTOS

### 1a. El nombre del caso (`case_id`) — REFUTADO como vector

Trazado completo de `case_id` en código no-test (`grep -rn case_id` sobre `vigia/`, `vigia_agent.py`, `vigia_scorer.py`, `sift_orchestrator.py`):

- `vigia_agent.py`: audit trail, logs, nombre de archivo de salida, y `artifact_id = f"{case_id}-001"` (línea 1594) en el pipeline de texto.
- Ese `artifact_id` llega a `SemioticDetectorV2.analyze(text, artifact_id, timestamp)` (`vigia/core/semiotic_detector_v2.py:400`) pero solo como **rótulo de memoria temporal** (`self._memory.add(...)`, línea 429). El pattern-matching corre exclusivamente sobre `text` (líneas 411-412); `check_sequences()` (líneas 272-285) decide solo por `phase`, nunca por el contenido del `artifact_id`.
- `sift_orchestrator.py`: `case_id` va a `ChainOfCustody`, metadata de resultado y logs (líneas 144, 225, 686, 927...). Sin parseo.
- **Ningún** `startswith`/regex/`in` sobre `case_id` en el path de decisión (única coincidencia: `consolidate_cases.py:400`, tooling de datos).
- Las menciones `REAL-003`, `FN-...` en `vigia/core/forensic_technical_detector.py:144-188` son **comentarios** junto a regexes que matchean contra el texto de la evidencia, no contra el nombre del caso.

**Conclusión 1a:** no hay evidencia de que el nombre del caso entre a CAIE, devil_advocate (`vigia/core/devil_advocate_gen.py`: cero ocurrencias de `case_id`), ni a ninguna función de scoring.

### 1b. `expected_verdict` en `normalize_case_schema` — CONFIRMADO (puerta runtime)

`vigia/pipeline/vigia_integration_bridge.py:472-492`, rama de schema 100% legacy:

```python
expected_verdict = case.get("expected_verdict", "").upper()
is_benign = (expected_verdict in ("NOISE", "BENIGN", "ABSTAIN") and len(expected_mitre) == 0)
if is_benign:
    ...
    art["raw_score"] = round(old_score * 0.25, 4)
    art["prior_trust"] = 0.3
```

La etiqueta ground-truth **modifica el input del scoring**: divide los scores por 4 y baja la confianza — exactamente cuando la respuesta esperada es "benigno".

**Quién llama a esta función CON la etiqueta presente** (medido por lectura de call-sites):

| Caller | Línea | Etiqueta presente |
|--------|-------|-------------------|
| `tests/run_vigia_case.py` (harness por caso, invocado por `scripts/run_vigia_full.py`) | 134 → `_vigia_score(case)` en 142 | **SÍ** |
| `vigia_api.py` raíz y `vigia/vigia_api.py` (`_run_pipeline`) | 56-62 | **SÍ** |
| `scripts/run_calibration.py` (ajuste de calibración) | 82 | **SÍ** |
| `scripts/run_vigia_full.py` (rama bundle) | 36 | **SÍ** |
| `show_4_hashes.py` | 63 | **SÍ** |
| `vigia_scorer._normalize_case` → llamado dentro de `_vigia_score` | `vigia_scorer.py:409` | depende del caller |
| **Agente modo motor** (`sift_orchestrator._resolve_hypothesis`) | 644: `blind = {k: v ... if k != "expected_verdict"}` | **NO** — la etiqueta se remueve antes de `_vigia_score`; `is_benign` no puede ser True |

**Medición (label-flip a través del scorer real):**

```
$ python3: para cada data/cases/benign/*.json →
  _vigia_score(_normalize_case(caso))  vs  _vigia_score(_normalize_case(caso sin expected_verdict))

VIGIA-BEN-001..015 (schema legacy, exp=NOISE):
  con etiqueta  → NOISE   (raw_scores 0.2/0.225/0.2375, score≈0.0246)
  sin etiqueta  → SUSPICION ×12 / MALICE ×3  (raw_scores 0.8/0.9/0.95, score≈0.2543)

15/15 casos legacy benignos cambian de veredicto por la sola presencia de la etiqueta.
(FP-CULTURAL-CLEAN y VIGIA-LINUX-002 son schema canónico → la rama de reducción no aplica; no flipean.)
```

Nota estructural: la reducción vive **solo** en la rama 100%-legacy — la rama canónica retorna en `vigia_integration_bridge.py:458` antes del bloque `is_benign`.

### 1c. `convert_legacy_cases.py` — CONFIRMADO (puerta de datos; sobrevive a B-075)

`scripts/convert_legacy_cases.py:149-160` replica la misma lógica ("Misma lógica que normalize_case_schema", comentario en línea 150) y **escribe el resultado a disco**:

```
$ original  data/cases/benign/VIGIA-BEN-001.json   → artifacts sin raw_score (legacy)
$ convertido data/cases/converted/VIGIA-BEN-001.json:
    raw_scores = [0.175, 0.2125, 0.2375], prior_trust = [0.3, 0.3, 0.3]   ← ×0.25 persistido

$ censo data/cases/converted/: 22 casos con etiqueta benigna;
  15 con la huella completa de la reducción (prior_trust=0.3 en todos los artefactos)

$ scoring CIEGO del convertido (sin expected_verdict):
  converted VIGIA-BEN-001 → NOISE (score 0.0207)
```

**Esto es B-075 por otra puerta, y es la más grave de las dos**: el fix de B-075 (resolve() ciego, tag `pre-fase1-flip-default-20260705`) remueve la etiqueta **en runtime**, pero estos archivos ya tienen los scores moldeados por la etiqueta **en el dato**. Un run "ciego" sobre `data/cases/converted/` acierta los benignos no por detección sino porque el conversor ya dividió los scores por 4 sabiendo la respuesta. La invariancia al label-flip (prueba usada en AUDITORIA_MOTOR_SIN_LABEL §3b) **no detecta esta puerta**: flippear la etiqueta del archivo convertido no restaura los scores originales.

Implicación directa no medida aquí (pendiente): qué fracción de los 199 casos del corpus de la métrica publicada (143→153/199) proviene de `data/cases/converted/` u otros archivos generados por este conversor. `run_all_agent.py:23-27` incluye `data/cases/converted` y `data/cases/benign` en sus directorios de corpus.

### 1d. Otras salidas de `expected_verdict` (inspeccionadas, sin efecto en decisión)

- `vigia_scorer.py:863` — copia la etiqueta al dict de **reporte** (post-veredicto).
- `sift_orchestrator.py:736` — `is_malice = avg > 2 or expected == "MALICE"`: es el eco de etiqueta legacy ya documentado en B-075, retenido solo bajo `VIGIA_EBS_RESOLVE=legacy` (default es `motor`, valores desconocidos caen a motor).
- `vigia/pipeline/vigia_integration_bridge.py:1002` — sanitiza la etiqueta hacia el reporte.

---

## H2 — COMBINATORIA MOBILE (B-072/073/074)

Escenario pedido: SIP disabled + SMS phishing + contactos no-parseados, simultáneos. SIP es señal macOS (`macos_forensics.py`), phishing y contactos son iOS (`ios_forensics.py`) — coexisten como dos señales que se combinan en `_mobile_hypothesis` (`sift_orchestrator.py:95`).

**Medición (construcción directa de los dataclasses + `to_signal()` + `_mobile_hypothesis`):**

```
iOS  (SMS_PHISHING_RECEIVED, contacts_parsed=False, calls_parsed=False) → z=1.6
mac  (SIP_DISABLED)                                                     → z=2.4
COMBINADO → ('SUSPICION_DETECTED', max_z=12/5, is_conclusive=False, n_critical=0)

Variante contactos parseados Y vacíos (data_minimization real):
iOS → z=2.2 (rama B-073 v2)   COMBINADO → SUSPICION_DETECTED (max_z=12/5)
```

**Consistencia con la doctrina declarada — SÍ, en los tres puntos:**

| Doctrina | Comportamiento medido |
|----------|----------------------|
| B-072: parseo fallido NO escala (contadores en 0 ≠ agenda vacía) | `contacts_parsed=False` → `data_minimization=False` → iOS queda en 1.6 (rama phishing-solo), no en 2.2 |
| B-073 v2: phishing pasivo no alcanza SUSPICION solo; sí combinado con señales parseadas | solo → 1.6 (< 2 aun con bump máximo 0.4); con data_minimization parseada → 2.2 > 2 |
| B-074: SIP escala por sí solo | z=2.4 → SUSPICION; y NO infla las ramas de combinación fuerte (3.4 exige `has_antiforensic_finding` separado, `macos_forensics.py:180`) |

El veredicto combinado (SUSPICION, no INTENT/MALICE) es coherente: ninguna señal supera 3, y `n_critical=0` mantiene el gate Daubert de 2 fuentes para MALICIOUS.

**Borde detectado en la combinación (alimenta H5):** dos dispositivos con z exactamente 3.0 cada uno → `('SUSPICION_DETECTED', 3, False, 0)`. Ver H5.

---

## H3 — TOCTOU EN LECTURA DE EVIDENCIA

### Lo que está bien (medido por lectura)

`read_evidence` (`vigia/vigia_sift_bridge.py:1052-1179`): un solo `os.open(path, O_RDONLY | O_NOFOLLOW)`, `os.fstat(fd)` (sobre el fd, no el path), lectura+hash en una pasada, y verificación post-read `total != file_size` → `_IntegrityViolation` → purgatorio. El hash corresponde exactamente a los bytes leídos. Residual conocido: una sustitución in-place del mismo tamaño durante la lectura no dispara el chequeo de tamaño, pero el sha256 sigue cubriendo lo efectivamente leído — la custodia interna del tool es consistente.

### Hallazgos

1. **Asimetría hash vs read** — `generate_forensic_hash` (`vigia/vigia_sift_bridge.py:1338-1371`) usa `open(file_path, "rb")` plano: sin `O_NOFOLLOW`, sin `fstat` del fd, sin verificación post-read. La ventana entre el walk `os.lstat` de `_sanitize_path` (`vigia/security/security.py:1006`, paso 5) y el `open()` es un check-then-use clásico. El tool de lectura rechaza symlinks; el tool que ancla la cadena de custodia los sigue.

2. **El protocolo hash→read son dos opens sin cross-check** — El playbook exige `generate_forensic_hash` ANTES de `read_evidence` (invariante 2 de CLAUDE.md). Son dos tool-calls con fds independientes; el archivo puede cambiar entre ambas. Grep sobre el repo: **ningún código compara** el `sha256` devuelto por `generate_forensic_hash` con el `sha256` que `read_evidence` computa para el mismo path. La detección de una divergencia queda enteramente a cargo del analista/LLM que mire ambos JSON.

3. **Check-then-use en `vigia_agent.py`** (todas ventanas symlink-swap; `read_text`/`open()` siguen symlinks):
   - línea 574 `is_symlink()` → línea 578 `open()` (hasher de sesión — el que deriva el nonce);
   - líneas 592-597 filtro `is_symlink()` en `rglob` → línea 600 `open()` por archivo;
   - línea 1534 `is_symlink()` → línea 1572 `read_text()` (pipeline de texto);
   - líneas 1576-1577 filtro en `rglob` → línea 1579 `read_text()`.

4. **El hash de sesión y la lectura del pipeline son opens distintos** — el agente hashea la evidencia en `vigia_agent.py:578` y el pipeline la re-lee en 1572 sin re-verificar contra ese hash.

Contraste: `vigia/core/path_guard.py:218-237` ya implementa el patrón correcto (`O_NOFOLLOW` con fallback documentado) — el endurecimiento existe en el repo, pero no está aplicado en los cuatro puntos de arriba.

---

## H4 — COPIAS DIVERGENTES

Censo AST (funciones top-level + métodos, excluyendo tests): **144 nombres definidos en más de un archivo con cuerpos distintos**. Los relevantes al path de decisión/seguridad:

| Par | Divergencia | Estado |
|-----|-------------|--------|
| `caie_legacy_root.py` vs `vigia/tools/caie.py` | `detect_fractures`, `adjusted_score` con cuerpos distintos | Legacy **muerto**: cero importadores (grep). Todo el runtime importa `vigia.tools.caie`. Riesgo latente: el fallback `_try_imports(["vigia.tools.caie", "caie"])` en `vigia_integration_bridge.py:115` importaría un `caie.py` plano si alguna vez aparece en `sys.path` |
| `vigia/core/vigia_core_forensic_technical_detector.py` vs `vigia/core/forensic_technical_detector.py` | `_sanitize` divergente | Copia `vigia_core_*` **muerta** (cero importadores). Nota: `vigia/tools/vigia_case_adapter.py:78` usa import plano `from forensic_technical_detector import ...` — cuál archivo resuelve depende de `sys.path` en el momento del import |
| `vigia/forensics/vision_audit_final.py` vs `vigia/forensics/vision_audit.py` | `analyze_intent` divergente | `_final` **muerto**; el vivo es `vision_audit.py` (importado por `pipeline.py:97`, bridge, planner) |
| `report_exporter.py` vs `report_exporter_v2.py` (vigia/pipeline/) | `sign_hash` divergente | **Ninguno** tiene importadores fuera de sí mismo (grep) |
| `_sanitize_grep_pattern` — `vigia/vigia_sift_bridge.py:174` vs `vigia/security/sandbox.py:353` | cuerpos distintos | **Ambos vivos** — dos validadores de seguridad con semánticas divergentes para la misma superficie |
| `_sanitize_path` — `vigia/security/security.py:1006` (canónico) vs `vigia/vigia_sift_bridge.py:3412` (shim fallback) | cuerpos distintos | shim solo activo si el import del canónico falla |
| `to_caie_fracture` — `vigia/forensics/temporal_forensics.py:238` vs `temporal_forensics_redteam.py:232` | cuerpos distintos | ambos en árbol; `vigia/tools/vigia_entanglement.py` existe para resolver el lazy-import del redteam |

**Divergencia de mayor calado (no de nombre, de doctrina): tres escaleras de decisión coexisten con umbrales incompatibles** —

1. `vigia_scorer.py:820+`: final_score `>0.33 / >0.10 / >0.08` + gate de corroboración B-068/B-070.
2. `sift_orchestrator._mobile_hypothesis:95`: z `>3` (INTENT), `>2` (SUSPICION), MALICIOUS exige 2 señales `z>3`.
3. Adaptador vol3 (`sift_orchestrator.py:955-966`): `avg > 1/3` → `MALICIOUS_INTENT_DETECTED` **con una sola fuente** (una señal z=3.5 → avg=3.5 → MALICIOUS de hipótesis) — mientras el path mobile exige 2 fuentes críticas para la misma hipótesis. La hipótesis luego pasa por los gates del agente, pero el espacio de hipótesis que cada adaptador emite para la misma evidencia numérica no es homogéneo.

---

## H5 — BORDES DE UMBRAL (`>` vs `>=`)

Todos los umbrales de decisión inspeccionados son **estrictos** (`>`). Consecuencias medidas:

### Ladder del scorer (`vigia_scorer.py`)

```
final_score=0.33  → SUSPICION   (no MALICE-candidate)
final_score=0.10  → UNKNOWN     (no SUSPICION)
final_score=0.08  → NOISE       (no UNKNOWN)
```
Coherente con el texto del reason ("exceeds ... threshold"). `final_score` es `Decimal` (`_dround`) comparado contra `Fraction` — comparación exacta soportada por la torre numérica de CPython; sin falso borde por floats.

### Mobile (`_mobile_hypothesis` + peldaños de los ladders iOS/macOS)

```
1 señal z=2.0 exacto → MOBILE_EVIDENCE_ANALYZED   (no SUSPICION)
1 señal z=3.0 exacto → SUSPICION_DETECTED         (no INTENT)
2 señales z=3.0      → SUSPICION_DETECTED, n_critical=0  (no MALICIOUS, no INTENT)
```

- El peldaño iOS `n_encrypted>=2` emite **exactamente 2.0** (`ios_forensics.py:172-173`) — nunca cruza `>2` solo; con `opsec_bump` ≥0.2 sí. Para phishing la estrictez está **documentada como deliberada** (`ios_forensics.py:177-183`).
- Los peldaños que emiten **exactamente 3.0** (iOS `n_encrypted>=3 ∧ data_minimization`, línea 156-157; macOS `n_encrypted>=3 ∧ has_suspicious_search`, línea 182-183) **no pueden producir INTENT ni contar como críticos** sin bump: quedan clavados en SUSPICION aunque dos dispositivos coincidan. A diferencia del caso 2.0/B-073, **ningún comentario documenta que esta banda muerta del peldaño 3.0 sea intencional**.
- `is_conclusive = confidence > 33/100` en resolve() (`sift_orchestrator.py:665`): confianza exactamente 1/3 → no conclusivo (mismo criterio estricto que el guard B-027).

### Rama muerta en el adaptador vol3 (`sift_orchestrator.py:966`)

```python
"MALICIOUS_INTENT_DETECTED" if is_malice            # avg > 1/3
else "NO_SEMIOTIC_ANOMALY_DETECTED" if avg == 0
else "INTENT_DETECTED" if avg > Fraction(5, 10)      # ← inalcanzable: avg ≤ 1/3 aquí
else "SUSPICION_DETECTED"
```

Medido por barrido de 5001 puntos en [0, 5]: **`INTENT_DETECTED` es inalcanzable** (exigiría avg>1/2 después de haber fallado avg>1/3). Comportamiento efectivo: `avg∈(0, 1/3]` → SUSPICION_DETECTED (incluso avg=0.01), `avg>1/3` → MALICIOUS_INTENT_DETECTED. El orden de los umbrales está invertido respecto a la severidad: la hipótesis intermedia quedó por encima del umbral de la máxima.

---

## PRIORIZACIÓN SUGERIDA (sin implementar — solo derivada de lo medido)

1. **H1c (P1)** — ✅ **RESUELTO 2026-07-06** (ver Addendum 4). La reducción por etiqueta persistida en `data/cases/converted/` contamina cualquier métrica "ciega" que incluya esos 15+ archivos. Requiere regenerar los convertidos sin el bloque `is_benign` del conversor y re-medir el corpus.
2. **H1b (P1)** — ✅ **RESUELTO 2026-07-06** (ver Addendum 3). Eliminar (o aislar tras flag de reproducción, patrón B-075) el bloque `is_benign` de `normalize_case_schema`; contamina harness (`run_vigia_case.py`), API y **calibración** (`run_calibration.py`).
3. **H5-vol3 (P2)** — Rama INTENT muerta + MALICIOUS de fuente única en el adaptador vol3: mismo tipo de hallazgo que el "umbral muerto 3c" de AUDITORIA_MOTOR_SIN_LABEL.
4. **H3 (P2)** — Endurecer `generate_forensic_hash` al patrón de `read_evidence`/`path_guard` y decidir si el protocolo de custodia exige cross-check hash≡read.
5. **H5-mobile / H4 (P3)** — Documentar (o corregir) la banda muerta del peldaño 3.0; borrar o archivar las copias muertas divergentes.

---

## ADDENDUM 2026-07-06 — Q1: ¿LA CALIBRACIÓN B-069/B-076 SE HIZO SOBRE DATOS CONTAMINADOS? / Q2: ¿HAY LÓGICA SIMÉTRICA DE INFLACIÓN?

### Q1 — Calibración de umbrales vs contaminación. Respuesta corta: **sí, B-076 se calibró sobre datos contaminados — por la puerta de datos, no por la puerta runtime.** Y `run_calibration.py` entrenó el LRCalibrator sobre el mismo corpus contaminado, aunque ese modelo no entra al scorer por default.

**Atribución precisa de cada artefacto de calibración:**

| Artefacto | Generador | ¿is_benign runtime activo? | ¿Datos contaminados? |
|-----------|-----------|---------------------------|---------------------|
| Umbral B-076 (0.18→0.10) | `scripts/generate_ladder_dataset.py` → `data/calibration_ladder_dataset_20260705.json` | **NO** — remueve `expected_verdict` antes de `_vigia_score` (línea `blind = {k: v ...}`) | **SÍ** — lee `data/cases/converted/` vía `run_all_agent.find_cases`; la dedup por stem (`CASES_DIRS`: converted antes que benign) hace ganar al archivo convertido |
| Gate B-069 (143→153/199) | `run_all_agent.py` sobre los mismos `CASES_DIRS` | NO (camino motor, blind) | **SÍ** — mismos archivos fuente |
| `models/calibrated_lr.json` (LRCalibrator) | `scripts/run_calibration.py` | **NO se ejecuta la rama** — llama `normalize_case_schema(case)` CON etiqueta (línea 82) pero su corpus default es `data/cases/converted` (schema canónico → retorno temprano en `bridge:458` antes del bloque `is_benign`). Verificado: sin doble reducción (0.175 → 0.175) | **SÍ** — los scores ya venían reducidos del conversor |

**Medición 1 — el dataset B-076 contiene los scores contaminados, bit a bit:**

Las 15 filas `VIGIA-BEN-001..015` del dataset tienen `path=data/cases/converted/...` y su `score` coincide **exactamente** (diff < 1e-9) con re-puntuar ciego el archivo convertido. 15/198 filas = 7.6% del dataset de calibración. Ninguna proviene de los originales de `data/cases/benign/`.

**Medición 2 — descontaminación (re-scoring ciego desde los originales):**

```
caso         dataset  convertido_ciego  ORIGINAL_ciego  veredicto   banda
BEN-001       0.0207      0.0207           0.2543       SUSPICION   >0.18
BEN-002       0.0202      0.0202           0.3037       SUSPICION   >0.18
BEN-003       0.0127      0.0127           0.2391       SUSPICION   >0.18
BEN-004       0.0361      0.0361           0.4008       MALICE      >0.18
BEN-005..007  0.02xx      = dataset        0.25-0.27    SUSPICION   >0.18
BEN-008/009   0.035x      = dataset        0.4033/0.4008 MALICE     >0.18
BEN-010       0.0127      0.0127           0.1600       SUSPICION   (0.10, 0.18] ← BANDA DELTA B-076
BEN-011..015  0.02xx      = dataset        0.248-0.363  SUSPICION   >0.18
```

**Consecuencias medidas sobre B-076:**

1. El censo de E1 afirmó "colateral esperado: cero" para bajar el umbral 0.18→0.10 porque la banda (0.10, 0.18] solo contenía los 10 SUSPICION mal clasificados + 1 UNKNOWN. Con datos descontaminados, **VIGIA-BEN-010 (score 0.1600, exp=NOISE) cae dentro de la banda delta**: bajar el umbral habría creado al menos 1 regresión medible (NOISE→SUSPICION). La afirmación "0 colaterales" solo se sostiene sobre el corpus contaminado.
2. Los otros 14 casos descontaminados quedan **por encima de 0.18**: son falsos positivos latentes bajo ambos umbrales. En el dataset figuran como `agree=True` (motor NOISE) — es decir, **la métrica del corpus (143→153/199) contiene 15 aciertos que existen solo por la reducción persistida**. Sin ella serían 15 fallos (12 SUSPICION + 3 MALICE contra exp=NOISE).
3. Alcance del LRCalibrator: `models/calibration_metadata.json` (2026-06-24) registra corpus de 78 casos con **n_authentic = 22 (18 train + 4 test)** — exactamente los 22 convertidos con etiqueta benigna. El separador authentic/fabricated del calibrador se ajustó con la clase authentic artificialmente comprimida (÷4). Atenuante verificado: ni `_vigia_score` ni el pipeline cargan ese modelo por default (`calibration_path` default es `None`/`""`; `vigia_scorer.py` no referencia LRCalibrator) — el modelo contaminado solo afecta a quien lo pase explícitamente.

### Q2 — ¿Lógica simétrica de inflación para MALICE/SUSPICION? Respuesta corta: **no existe. La fuga es estrictamente asimétrica, solo hacia abajo y solo para etiqueta benigna.**

**Medición — label-flip a nivel conversor** (mismo caso sintético con 3 artefactos idénticos, variando solo `expected_verdict`, vía `convert_case()` importado de `scripts/convert_legacy_cases.py`):

```
expected_verdict IN -> raw_scores convertidos    prior_trust      verdict OUT
MALICE              -> [0.6, 0.75, 0.95]         [0.7,0.85,0.9]   MALICE
INTENT              -> [0.6, 0.75, 0.95]         [0.7,0.85,0.9]   MALICE
SUSPICION           -> [0.6, 0.75, 0.95]         [0.7,0.85,0.9]   SUSPICION
UNKNOWN             -> [0.6, 0.75, 0.95]         [0.7,0.85,0.9]   SUSPICION
ABSTAIN             -> [0.6, 0.75, 0.95]         [0.7,0.85,0.9]   SUSPICION
NOISE               -> [0.15, 0.1875, 0.2375]    [0.3,0.3,0.3]    NOISE
BENIGN              -> [0.15, 0.1875, 0.2375]    [0.3,0.3,0.3]    NOISE
```

- Los 5 labels no-benignos producen scores **idénticos**: no hay inflación condicionada al veredicto. El único ajuste hacia arriba del conversor (`+0.10` si `len(forensic_anomalies) >= 2`, `convert_artifact`) es **evidence-driven**, independiente de la etiqueta (el 0.95 del tercer artefacto aparece igual en la fila NOISE: 0.2375 = 0.95×0.25).
- El score base sale del `peirce_layer` del artefacto (0.60/0.75/0.88), no del veredicto.

**Dirección real de la asimetría:** la reducción se aplica cuando la *etiqueta* dice benigno. Efecto primario medido: suprime artificialmente la tasa de falsos positivos del motor sobre los casos etiquetados benignos (los 15 de arriba). Modo de fallo derivado: un caso mal etiquetado como NOISE (malicia real con etiqueta benigna) entra al corpus con su evidencia atenuada ÷4 y `prior_trust` 0.3 — en ese escenario la asimetría sí oculta malicia.

**Hallazgo adicional (divergencia con la "misma lógica" declarada):** el comentario del conversor (línea 150) dice replicar `normalize_case_schema`, pero las dos implementaciones de `is_benign` divergen de forma medible:

| Condición | `normalize_case_schema` (bridge:473-476) | `convert_legacy_cases.convert_case` |
|-----------|------------------------------------------|-------------------------------------|
| ABSTAIN cuenta como benigno | **SÍ** | **NO** — `VERDICT_MAP` reescribe ABSTAIN→SUSPICION *antes* del check |
| Exige `expected_mitre_ttps == []` | **SÍ** | **NO** — ignora MITRE |

Además el conversor **reescribe las etiquetas mismas** en el corpus persistido (INTENT→MALICE, UNKNOWN→SUSPICION, ABSTAIN→SUSPICION): los UNKNOWN originales — que el comparador acepta con cualquier veredicto — dejan de existir como UNKNOWN en los archivos convertidos, endureciendo o distorsionando la evaluación de esos casos según la dirección de la reescritura.

---

## ADDENDUM 2 — 2026-07-06 — REVISIÓN DE ETIQUETAS VIGIA-BEN-001..015

| Campo | Valor |
|-------|-------|
| **Tag de restauración** | `pre-session-20260706-025125` (local; push de tags rechazado por el remoto, igual que el anterior) |
| **Mandato** | Re-etiquetar cada BEN con el veredicto del motor limpio SI la evidencia lo justifica; si la evidencia es claramente benigna, documentar como FP del motor y mantener NOISE. Sin tocar la reducción ×0.25. |
| **Resultado** | **0 etiquetas cambiadas — 15/15 documentados como FP del motor, candidatos a calibración Fase 2.** Ningún archivo de caso fue modificado. |

### Método

1. **Motor limpio, dos variantes por robustez**: (a) el original legacy de `data/cases/benign/` puntuado ciego (normalización canónica del bridge, sin etiqueta → sin reducción); (b) el convertido de `data/cases/converted/` con la reducción invertida (`raw_score/0.25`, `prior_trust` restaurado del mapeo Peirce del conversor). **Las dos variantes coinciden en veredicto en los 15 casos.**
2. **Revisión forense de la evidencia**: lectura completa de `description`, `content` y `forensic_anomalies` de los 3 artefactos de cada caso.
3. **Criterio de decisión**: el propio Protocolo de Refutación del repo (CLAUDE.md) — si la hipótesis benigna explica TODAS las anomalías estructurales sin contradicción, el veredicto correcto es NOISE.

### Tabla de revisión

| Caso | Motor limpio (orig / des-red) | Anomalía aparente | Corroboración benigna en la propia evidencia | Decisión |
|------|------------------------------|-------------------|---------------------------------------------|----------|
| BEN-001 | SUSPICION 0.2543 / 0.2178 | Cirílico en layout latino | Empleado ruso verificado en HR, hardware RU provisto por IT, geoIP+horario Moscú consistentes | **NOISE — FP del motor** |
| BEN-002 | SUSPICION 0.3037 / 0.2098 | Transferencia masiva 3AM a S3 | Cron de backup 2023, runbook p.47, auditoría Q3 PASSED, IAM role de servicio | **NOISE — FP del motor** |
| BEN-003 | SUSPICION 0.2391 / 0.1347 | DELETE sin WHERE | Admisión pública inmediata, recovery en 3 min, supervisor asume el error de permisos | **NOISE — FP del motor** (hipótesis de incompetencia benigna literal) |
| BEN-004 | **MALICE** 0.4008 / 0.3734 | 47 comandos con timing perfecto | Ansible Tower, playbook firmado, CAB #2024-06-05, sin TTY | **NOISE — FP del motor** |
| BEN-005 | SUSPICION 0.2543 / 0.2178 | 3 logins fallidos | Teclado nuevo con ticket IT-4492, jitter humano 6-7s, jornada normal posterior | **NOISE — FP del motor** |
| BEN-006 | SUSPICION 0.2543 / 0.2178 | 12 sudo en 2 horas | Mantenimiento mensual en calendario, CHG-0038, reporte post-mantenimiento firmado | **NOISE — FP del motor** |
| BEN-007 | SUSPICION 0.2667 / 0.2262 | PDF "confidential" en Desktop | Distribución oficial de RRHH a 45 managers, política HR-2023-044, acuse firmado | **NOISE — FP del motor** |
| BEN-008 | **MALICE** 0.4033 / 0.3563 | Ping periódico a 8.8.8.8 | Nagios del NOC desde 2022, dashboard público, config versionada | **NOISE — FP del motor** |
| BEN-009 | **MALICE** 0.4008 / 0.3734 | chmod 777 | Deuda técnica TD-2019-042 documentada, app sin red ni sudo, migración planificada | **NOISE — FP del motor** |
| BEN-010 | SUSPICION 0.1600 / 0.1347 | Email URGENT del CEO | DKIM/SPF PASS, reunión real en calendario, thread de pedido 7 días antes | **NOISE — FP del motor** |
| BEN-011 | SUSPICION 0.2483 / 0.2098 | USB en máquina de finanzas | Ticket SUP-2024-1120, técnico escoltado, drivers de impresora fiscal (sin red por política) | **NOISE — FP del motor** |
| BEN-012 | SUSPICION 0.3630 / 0.3337 | Proceso sin parent en pslist | `kworker` hijo de `kthreadd` (PID 2), comportamiento documentado del kernel | **NOISE — FP del motor** |
| BEN-013 | SUSPICION 0.2483 / 0.2098 | `rm -rf` diario de logs | Política de retención GDPR 30 días, aprobada por DPO, borra solo >30d | **NOISE — FP del motor** |
| BEN-014 | SUSPICION 0.2783 / 0.2098 | Conexión Tor | Periodista con autorización escrita del editor, 100% del tráfico a plataforma whistleblower | **NOISE — FP del motor** |
| BEN-015 | SUSPICION 0.2667 / 0.2262 | 100 timestamps idénticos | Restore de snapshot Veeam tras falla de hardware, ticket INF-2024-0551, 47 VMs | **NOISE — FP del motor** |

### Por qué NO corresponde re-etiquetar ninguno

1. **La evidencia es inequívocamente benigna en los 15.** El corpus BEN está diseñado como trampas de falso positivo: cada caso presenta una señal alarmante en Firstness y su explicación benigna corroborada (HR, change tickets, calendario, GDPR, autorización legal) en Secondness/Thirdness. Bajo el Protocolo de Refutación, la hipótesis benigna explica todas las anomalías sin contradicción → NOISE.
2. **Re-etiquetar aquí sería B-075 invertido.** Ajustar el ground truth para que coincida con el motor es fuga de etiqueta en la dirección opuesta: el corpus dejaría de medir al motor y pasaría a confirmarlo. El desacuerdo motor-limpio-vs-etiqueta es el dato honesto que la reducción ×0.25 venía ocultando.
3. **Causa raíz de los 15 FPs (dato para Fase 2):** el conversor asigna `raw_score` mecánicamente desde `peirce_layer` (0.60/0.75/0.88, +0.10 si ≥2 `forensic_anomalies`) **sin leer la semántica de la evidencia**. En estos casos el campo `forensic_anomalies` contiene enunciados exculpatorios ("Documentación de empleado verificable en HR") que igualmente suman +0.10, y el artefacto de corroboración benigna (Thirdness) recibe el score MÁS alto (0.88→0.95). Los 3 MALICE (004/008/009) cruzan además el gate de corroboración B-068 porque los 3 artefactos aportan ≥3 clases DEVICE distintas. El FP es inducido por la conversión: el motor nunca ve un solo bit que distinga evidencia incriminatoria de exculpatoria.

### Corpus comparativo antes/después

Réplica del comparador (doctrina `generate_ladder_dataset.agree`: alias BENIGN→NOISE, UNKNOWN acepta todo, MALICE-donde-INTENT es acierto) sobre `find_cases(CASES_DIRS)`, motor blind:

```
ANTES  (etiquetas actuales): 166/198
DESPUÉS (0 etiquetas cambiadas): 166/198 — idéntico por construcción
Filas BEN-001..015: exp=NOISE, motor=NOISE (sobre datos reducidos), agree=True en las 15.
```

Nota de honestidad sobre la línea base: 166/198 difiere del 153/199 histórico de B-076 — la medición histórica se hizo sobre el HEAD de 2026-07-05; desde entonces entraron cambios de routing (`dbba7ca` B1-c) y esta réplica implementa el comparador del generador del dataset, no `run_all_agent` completo. Para el propósito de este addendum lo relevante es que ANTES y DESPUÉS se midieron con el mismo método y son idénticos.

**Estado resultante:** los 15 BEN quedan como candidatos de calibración Fase 2 con esta ficha: etiqueta NOISE correcta, motor limpio SUSPICION×12/MALICE×3, causa raíz en la conversión semántica-ciega. Cuando se remueva la reducción ×0.25 (pendiente, fuera de este mandato), estos 15 aparecerán como desacuerdos reales del motor — ese es el estado honesto del sistema, no una regresión.

---

## ADDENDUM 3 — 2026-07-06 — FIX P1 APLICADO: CUARENTENA DEL BLOQUE is_benign (H1b)

| Campo | Valor |
|-------|-------|
| **Tag de restauración** | `pre-session-20260706-030212` (local) |
| **Archivo** | `vigia/pipeline/vigia_integration_bridge.py` — `normalize_case_schema()` |
| **Fix** | El bloque de reducción benigna (`raw_score×0.25` + `prior_trust=0.3` cuando la etiqueta es NOISE/BENIGN/ABSTAIN) quedó tras el parámetro keyword-only `legacy_benign_reduction=False`. Default False en TODOS los callers — la normalización ya no lee `expected_verdict` en ningún path que alimente `_vigia_score`. El opt-in existe solo para reproducir bundles históricos pre-fix y emite `logger.warning` al activarse. |
| **Test** | `tests/test_label_leak_normalize_case_schema.py` — 12 tests: label-flip no cambia artefactos (5 etiquetas parametrizadas), `_vigia_score` invariante a la etiqueta (sintético + BEN-001 real), pin del comportamiento histórico bajo el flag, flag inerte para etiquetas no benignas y para schema canónico. 12/12 verdes. |
| **Verificación empírica** | Los 15 casos VIGIA-BEN re-medidos post-fix: **0/15 flips** (pre-fix: 15/15). Con y sin etiqueta: mismo veredicto y mismo score (SUSPICION×12, MALICE×3 — los FPs honestos del Addendum 2, ahora visibles también con la etiqueta presente). |
| **Corpus** | `python3 run_all_agent.py --timeout 90` → **167/199 PASS, 32 FAIL** — idéntico al valor documentado en README; 0 regresiones (esperado: el path del agente ya era blind por B-075, y los archivos convertidos aún portan la reducción persistida — H1c sigue abierto). |
| **Suite** | **731 passed, 7 xfailed** con el comando documentado (`pytest tests/ vigia/tests/ --ignore=tests/integration`) — línea base pre-fix: 719 passed / 7 xfailed; los 12 nuevos son los tests de este fix. Los 2 errores de colección iniciales eran `ModuleNotFoundError` del entorno (`psutil`, `mcp` — pre-existentes, idénticos con el fix stasheado), resueltos instalando dependencias. |

**Efecto colateral documentado:** los callers del harness (`tests/run_vigia_case.py`, `vigia_api.py`, `scripts/run_vigia_full.py`, `scripts/run_calibration.py`, `show_4_hashes.py`) dejan de aplicar la reducción — sus resultados sobre los 15 BEN *originales* (legacy) pasan a mostrar los FPs reales del motor en lugar de NOISE fabricado. Es el estado honesto; la mitigación real de esos FPs es trabajo de calibración Fase 2 (Addendum 2). Una futura re-calibración del LRCalibrator (`run_calibration.py`) ya no heredará la puerta runtime; la puerta de datos (H1c, archivos convertidos) sigue pendiente.

---

## ADDENDUM 4 — 2026-07-06 — TANDA 4 APLICADA: PUERTA DE DATOS H1c CERRADA

| Campo | Valor |
|-------|-------|
| **Tag de restauración** | `pre-tanda4-h1c-20260706-043436` (local) |
| **Cambios** | (1) `scripts/convert_legacy_cases.py`: el bloque de reducción benigna quedó en cuarentena tras `legacy_benign_reduction=False` (mismo patrón que el fix P1 del bridge) — la conversión es ciega a la etiqueta por default. (2) Los 15 archivos `data/cases/converted/VIGIA-BEN-*.json` regenerados sin la reducción: `raw_score/0.25` (inversa exacta), `prior_trust` restaurado del mapa Peirce del conversor (0.70/0.85/0.90), el campo derivado `signals` recomputado con la fórmula del adaptador (`z = raw×prior`, codificación Fraction canónica — verificada contra los valores contaminados previos), `_migration_note` ampliada con historia. |
| **Test** | `tests/test_h1c_converter_label_blind.py` — 13 tests: label-flip a nivel conversor (7 etiquetas parametrizadas → scores idénticos), sin huella de reducción por default, pin del corpus histórico bajo el opt-in, flag inerte para etiquetas maliciosas, los 15 archivos del corpus sin huella, `signals` consistente con los artifacts limpios, y BEN-001 regenerado puntúa honesto. |
| **Verificación empírica** | Scoring ciego de los 15 regenerados: **SUSPICION×12 / MALICE×3** — exactamente la predicción del Addendum 2 (columna "convertido des-reducido"). |
| **Suite** | **789 passed, 7 xfailed** (baseline tanda 3: 776+7; +13 de esta tanda). |
| **Corpus** | `run_all_agent.py --timeout 90` → **152/199 PASS, 47 FAIL**. Delta contra el 167/199 previo: **exactamente −15, cero colaterales** (verificado por diff de case_ids: los 47 fallos = los 32 previos + los 15 BEN). |

### El impacto honesto en el corpus

Los 15 "aciertos" que desaparecen no eran detección: eran el conversor
escribiendo la respuesta en los datos (÷4 al score porque la etiqueta decía
benigno). El 152/199 es el primer número del corpus donde ninguna fila
benigna está pre-resuelta. Los 15 BEN emergen como los falsos positivos
reales del motor documentados en el Addendum 2 (causa raíz: conversión
semántica-ciega peirce_layer→score que puntúa alto la evidencia
exculpatoria) — ese es el backlog de calibración de Fase 2, ahora visible en
la métrica en lugar de oculto bajo la reducción.

READMEs actualizados (EN+ES): agregado 167/199 → 152/199, corpus de
detección 146/159 (91.8%) → 131/159 (82.4%) con el segmento benigno 15/15 →
0/15 explicado, paso de la tanda agregado a la trayectoria del agregado, y
bloque de output esperado del runner. `SUBMISSION_COMPLIANCE.md`
intencionalmente sin tocar (registro de lo presentado).

**Residual documentado:** `data/calibration_ladder_dataset_20260705.json`
(base de B-076) es previo a la regeneración — sus 15 filas BEN conservan los
scores contaminados. Regenerarlo y re-examinar el umbral 0.10 de B-076 sobre
datos limpios queda como trabajo de Fase 2 (el Addendum Q1 ya midió que
BEN-010 limpio cae en la banda delta).

---

*Auditoría ejecutada sin modificar código en los addenda 1-2. El Addendum 3 introduce el primer cambio de código de esta serie (fix P1/H1b); el Addendum 4 cierra la puerta de datos (TANDA 4), ambos bajo protocolo completo. Números reproducibles con los comandos descriptos en cada sección.*
