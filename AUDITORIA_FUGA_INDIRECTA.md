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

1. **H1c (P1)** — La reducción por etiqueta persistida en `data/cases/converted/` contamina cualquier métrica "ciega" que incluya esos 15+ archivos. Requiere regenerar los convertidos sin el bloque `is_benign` del conversor y re-medir el corpus.
2. **H1b (P1)** — Eliminar (o aislar tras flag de reproducción, patrón B-075) el bloque `is_benign` de `normalize_case_schema`; contamina harness (`run_vigia_case.py`), API y **calibración** (`run_calibration.py`).
3. **H5-vol3 (P2)** — Rama INTENT muerta + MALICIOUS de fuente única en el adaptador vol3: mismo tipo de hallazgo que el "umbral muerto 3c" de AUDITORIA_MOTOR_SIN_LABEL.
4. **H3 (P2)** — Endurecer `generate_forensic_hash` al patrón de `read_evidence`/`path_guard` y decidir si el protocolo de custodia exige cross-check hash≡read.
5. **H5-mobile / H4 (P3)** — Documentar (o corregir) la banda muerta del peldaño 3.0; borrar o archivar las copias muertas divergentes.

---

*Auditoría ejecutada sin modificar código. Todos los números provienen de ejecuciones reproducibles sobre HEAD `849475b` con los comandos descriptos en cada sección.*
