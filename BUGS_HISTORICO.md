# BUGS_HISTORICO.md — VIGÍA Bug Registry (Histórico / Resueltos)

Registro histórico de bugs **ya resueltos, cerrados, aplicados o
descartados** — separado de [`BUGS_PENDIENTES.md`](./BUGS_PENDIENTES.md) el
2026-07-25 para que el archivo de pendientes reales quedara navegable. Se
conserva completo como audit trail (los bugs resueltos no se eliminan,
solo se archivan) — cada entrada mantiene el número que tenía en el
registro original. Lectura recomendada para quien quiera hacer red team
sobre VIGÍA: acá está todo lo que ya se encontró y se corrigió.

Formato: un bloque por bug, con su impacto forense y el fix aplicado.

---

## B-001 — `daubert_note` UnboundLocalError en el path CollapseDecisionLayer

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/tools/caie.py` |
| **Función** | `CrossArtifactIncongruenceEngine.evaluate()` |
| **Líneas originales** | 1754, 1757 (`+=`); 1815–1823 (asignación `=`) |
| **Commit fix** | ver commit "POST HACKATHON: fix daubert_note UnboundLocalError in CDL path" |
| **Detectado en** | Sesión post-hackathon 2026-06-23, revisión de coverage gap #2 |

### Descripción

Dentro de `evaluate()`, el bloque `CollapseDecisionLayer` (CDL) ejecutaba:

```python
# líneas 1754 y 1757 — ANTES del fix
daubert_note += f" CDL: {cdl_explanation}"
```

…pero `daubert_note` no se asignaba hasta la línea 1815, en un bloque posterior:

```python
# línea 1815 — asignación original (DESPUÉS del CDL)
daubert_note = (
    f"Daubert: {irrefutable_count}/{len(self._artifacts)} "
    ...
)
```

Esto produce `UnboundLocalError: local variable 'daubert_note' referenced
before assignment` cada vez que el CDL downgrade el veredicto
(`INCONCLUSIVE` o `SUSPICION`).

### Impacto

- La excepción era **silenciada** por el bloque `except Exception as exc:` del
  CDL, que solo logueaba el error a nivel `logging.ERROR`.
- El **downgrade del veredicto** (`verdict = "INCONCLUSIVE"` /
  `verdict = "SUSPICION"`) se ejecuta **antes** del `+=` defectuoso, por lo
  que el veredicto final **era correcto**.
- Lo que se perdía era la **nota explicativa del CDL** en `daubert_note`:
  el campo `"daubert_note"` en el resultado nunca incluía la cláusula
  `"CDL: ..."` cuando el CDL actuaba.
- Impacto en admisibilidad Daubert: el bundle resultante no reflejaba que el
  CDL había intervenido, lo que oscurecía el trail de razonamiento bajo
  cross-examination.

### Fix aplicado

Movido el bloque `irrefutable_count` / `daubert_note = (...)` a **antes** del
bloque CDL. La variable solo depende de `self._artifacts`, disponible en toda
la función. El bloque CDL puede entonces hacer `+=` sobre una variable ya
inicializada.

Eliminado el bloque duplicado en la posición original.

**Orden tras el fix** (líneas aproximadas post-edición):

```
~1715: irrefutable_count = sum(...)       # ← movido aquí
~1719: daubert_note = (...)               # ← movido aquí
~1713: # COLLAPSE DECISION LAYER (CDL)
~1770: daubert_note += f" CDL: ..."       # ahora válido
~1773: daubert_note += f" CDL: ..."       # ahora válido
~1911: "daubert_note": daubert_note       # uso final
```

### Verificación

```
pytest tests/ -k "caie or order_sensitivity or spoofability" -v --no-cov
→ 63 passed, 0 failed
```

---

## B-002 — `likelihood_engine.py` constructor mal llamado y ruta de importación plana

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/core/likelihood_engine.py` |
| **Función** | `LikelihoodEngine.__init__()` (carga de calibrador) |
| **Líneas originales** | 101 (`import_module`), 102 (`LRCalibrator(...)`) |
| **Commit fix** | `4649427` |
| **Detectado en** | Sesión post-hackathon 2026-06-24 |

### Descripción

Dos errores concatenados en la carga del calibrador LR:

1. **Ruta de importación plana** (línea 101): `import_module("lr_calibration")` fallaba
   fuera del directorio raíz porque el módulo no estaba en el `sys.path` plano.
2. **Constructor posicional incorrecto** (línea 102): `LRCalibrator(calibration_path)`
   llamaba al constructor con un argumento posicional que el constructor no acepta;
   la clase expone `LRCalibrator.load(path)` como método de fábrica.

### Impacto

- El motor de likelihood fallaba al instanciar el calibrador en cualquier entorno
  donde `vigia/` no estuviera en el `sys.path` raíz.
- El error era silencioso en algunos paths de importación dinámica, produciendo un
  calibrador `None` sin excepción visible, lo que generaba resultados incorrectos
  aguas abajo sin traza de error clara.

**APLICADO** 2026-06-24 — Fixed in vigia/core/likelihood_engine.py:
- Line 101: `import_module("lr_calibration")` → `import_module("vigia.core.lr_calibration")`
- Line 102: `LRCalibrator(calibration_path)` → `LRCalibrator.load(calibration_path)`
5/5 serialization tests pass. Commit: 4649427.

### Verificación

```
pytest tests/ -k "serialization" -v --no-cov
→ 5 passed, 0 failed
```

**RESUELTO** 2026-06-24 — El último importador plano era scripts/run_calibration.py,
eliminado en commit 10ced2c (B-004). No quedan referencias a `from likelihood_ratio import`
ni `import likelihood_ratio` en el repo (verificado con grep). No requirió cambios
en likelihood_ratio.py — el archivo ya usaba vigia.core.ebs_v1 internamente.

---

## B-003 — Terminología errónea "isotónica" en comentarios y logs de `pipeline.py`

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/pipeline/pipeline.py` |
| **Función** | `VigiaPipeline.__init__()`, `VigiaPipeline.run()`, `run_vigia()` |
| **Líneas corregidas** | 110, 207, 218, 464, 466, 479, 485, 487, 1303, 1305, 1332 |
| **Commit fix** | `43edd73` |
| **Detectado en** | Sesión post-hackathon 2026-06-24 |

### Descripción

Los comentarios y mensajes de log usaban "calibración isotónica" / "regresión isotónica"
para describir el paso H28 (LRCalibrator). La calibración siempre fue
`LogisticRegression` — nunca isotonic regression. La confusión terminológica
provenía de un nombre de archivo de persistencia (`_isotonic.json`) que se copió
en los comentarios sin revisión.

### Impacto

- Puramente documental / auditivo. Sin impacto en el comportamiento del pipeline.
- El término incorrecto habría confundido a un revisor Daubert sobre el método
  estadístico real empleado.

### Fix aplicado

Reemplazados todos los usos de "isotónica/isotónico/isotónicamente/isotonic_regression"
en comentarios y strings de log por los términos correctos ("logística/logístico/
logísticamente/logistic_regression"). Las rutas de archivo `_isotonic.json`
(líneas 212 y 1311) no fueron modificadas — son identificadores de fichero,
no terminología estadística.

### Verificación

```
pytest tests/ -q --no-cov
→ 188 passed, 6 xfailed
```

**APLICADO** 2026-06-24 — Commit: 43edd73.

---

## B-004 — `run_calibration.py` importaciones planas (pre-reorganización)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `scripts/run_calibration.py` |
| **Función** | Module-level imports |
| **Líneas originales** | 29 (`sys.path.insert`), 31–35 (flat imports) |
| **Commit fix** | `10ced2c` |
| **Detectado en** | Sesión post-hackathon 2026-06-24 |

### Descripción

El script usaba un `sys.path.insert` para agregar el directorio `scripts/` al path,
y luego importaba con nombres planos:

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vigia_integration_bridge import (CaseAdapter, ...)
from likelihood_ratio import LikelihoodEngine
from lr_calibration import LRCalibrator
```

Después de la reorganización del paquete, los módulos residen en:
- `vigia/pipeline/vigia_integration_bridge.py`
- `vigia/core/likelihood_ratio.py`
- `vigia/core/lr_calibration.py`

El hack `sys.path.insert` enmascaraba el error fuera del entorno de desarrollo.

### Fix aplicado

Eliminado `sys.path.insert`. Reemplazadas las importaciones planas por rutas de paquete:

```python
from vigia.pipeline.vigia_integration_bridge import (CaseAdapter, ...)
from vigia.core.likelihood_ratio import LikelihoodEngine
from vigia.core.lr_calibration import LRCalibrator
```

**APLICADO** 2026-06-24 — Commit: 10ced2c.

---

## B-005 — `run_calibration.py` ruta de datos hardcodeada (directorio del script)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `scripts/run_calibration.py` |
| **Función** | `main()` — corpus glob |
| **Líneas originales** | 180–186 (glob patterns), 241–247 (output paths) |
| **Commit fix** | `10ced2c` |
| **Detectado en** | Sesión post-hackathon 2026-06-24 |

### Descripción

El corpus se buscaba relativo al directorio del script (`scripts/`):

```python
base = os.path.dirname(os.path.abspath(__file__))
files = (
    glob.glob(os.path.join(base, "VIGIA-SYN-*.json")) + ...
)
```

Los archivos de casos residen en `data/cases/converted/` bajo la raíz del repo.
Con la ruta hardcodeada, el script encontraba 0 casos a menos que se ejecutara
desde `scripts/` con los JSON copiados manualmente. Los modelos de salida también
se guardaban en `scripts/models/` en lugar de `models/` en la raíz del repo.

### Fix aplicado

Añadido flag `--data` (default `data/cases/converted`) y `repo_root` como base:

```python
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(repo_root, args.data)
files = glob.glob(os.path.join(data_dir, "*.json")) + ...
out_path = os.path.join(repo_root, args.out)
```

Verificación: 78 casos cargados, Brier Score 0.149, modelo guardado en
`models/calibrated_lr.json` (raíz del repo).

**APLICADO** 2026-06-24 — Commit: 10ced2c.

---

## B-006 — `LRCalibrator.load()` no valida `train_hash` contra el dataset actual

| Campo | Valor |
|-------|-------|
| **Estado** | APLICADO |
| **Archivo** | `vigia/core/lr_calibration.py` |
| **Función** | `LRCalibrator.load()` |
| **Línea original** | 455 |
| **Commit fix** | 1db3360 |
| **Detectado en** | Sesión post-hackathon 2026-06-24, revisión BUGS_PENDIENTES |

### Descripción

`LRCalibrator.load()` cargaba el calibrador serializado sin verificar que el
`train_hash` almacenado en el JSON coincidiera con el dataset actualmente en uso.
Esto permitía que un calibrador entrenado sobre un dataset diferente se cargara
silenciosamente, produciendo probabilidades calibradas incorrectas sin ningún error
ni advertencia — un fallo de trazabilidad Daubert.

### Impacto forense

Un calibrador desincronizado del dataset activo produce scores de verosimilitud
incorrectos. En un contexto forense esto es inaceptable: los valores numéricos
quedarían sin respaldo reproducible, invalidando la cadena de custodia.

### Fix aplicado

Se agregó el parámetro opcional `expected_train_hash: str = ""` a `load()`.

- Si se pasa vacío (default), el comportamiento es idéntico al anterior — compatible
  hacia atrás sin cambios en código existente.
- Si se pasa un hash, se compara contra `cal._backend._train_hash` inmediatamente
  antes del `return cal`. Si no coinciden, se lanza `ValueError` con mensaje
  descriptivo que incluye ambos hashes y la instrucción de regenerar con
  `scripts/run_calibration.py`.

### Verificación

```
5/5 tests passed — vigia/tests/test_lr_calibrator_serialization.py
Smoke test: load sin hash OK, load con hash correcto OK, load con hash incorrecto → ValueError OK
```

**APLICADO** 2026-06-24 — Commit: 1db3360.

---

## B-007 — Floats P0 introducidos por Claude Code en el scorer (descartado)

**Estado:** DESCARTADO — nunca llegó al repositorio.

**Descripción:** Durante una sesión con Claude Code se detectó que el código
generado introducía ~10 violaciones P0 (floats en el scoring path) en algo
relacionado al scorer. Al identificarlo se descartó el código completo antes
de hacer cualquier commit. Git nunca vio el cambio. El scorer en HEAD mantiene
las tablas Fraction (`_SUPPORT_SCORE_TABLE`, `_EXP_NEG2_TABLE`, `_EPC_FACTOR_TABLE`)
intactas tal como quedaron en el P0 patch 2026-06-14 (commit 1807529).

**Lección:** Validar siempre con `grep -n "math\.log\|math\.exp\|[0-9]\.[0-9]"
vigia_scorer.py` antes de aceptar cualquier cambio al scoring path.

---

## B-008 — float() en SignalOutput constructors (vigia/sift/) — L-021 Fase 3

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — auditoría P0-001, 2026-06-30 |
| **Severidad** | P2 → CERRADO por decisión de diseño |
| **Archivos** | `vigia/sift/sift_orchestrator.py`, `vigia/sift/unified_timeline_engine.py` |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |
| **Corregido** | 2026-06-30 |

### Resolución (auditoría P0-001)

**Decisión de diseño:** `SignalOutput` es un DTO que cruza el boundary entre herramientas
SIFT (floats IEEE 754 de herramientas forenses externas) y el scorer Fraction-puro. El tipo
`float` en SignalOutput es **correcto por diseño**. Los 22 constructores con `float()` son
consistentes con este contrato.

**El bug real** estaba en la reconversión float→Fraction en el boundary SIFT→scorer:
`Fraction(int(round(val * 100)), 100)` — `round()` sobre float pre-multiplicado sufre
error de representación IEEE 754. Fix: `Decimal(str(val)).quantize(...)`.

Divergencia confirmada: `1.245` → viejo: `5/4`, nuevo: `31/25`.

Ver P0-001 y L-040 al final del archivo para detalles completos.

---

## B-009 — float() en vigia/abduction/vigia_artifact_graph.py — path de abducción activo

| Campo | Valor |
|-------|-------|
| **Estado** | DESCARTADO — 2026-06-26 |
| **Severidad** | P1 — path activo, no SIFT-only |
| **Archivo** | `vigia/abduction/vigia_artifact_graph.py` |
| **Líneas** | 432, 433, 457 |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |

### Descripción

```python
z = float(node_data.get("z_score", 0.0))       # L432
conf = float(node_data.get("confidence", 0.0))  # L433
severity = float(anomaly.get("severity", ...))   # L457
```

A diferencia de B-008, este módulo está en el path de abducción activo
(no es SIFT-only). Si `z_score` o `severity` vienen como `str` desde la
frontera de L-021 (`evaluate()` ahora emite strings), `float(str_value)`
funciona pero introduce float en el path de razonamiento abductivo —
inconsistente con el invariante L-021.

### Fix

Reemplazar `float(...)` por `Decimal(str(...))` en las tres líneas.
Verificar que los callers downstream aceptan `Decimal`.

**DESCARTADO** 2026-06-26 — vigia_artifact_graph.py es un módulo de visualización
puro (grafos de nodos/edges para display). Los float() calculan tamaños de pixel
(int(15 + min(15, z * 3))), pesos de aristas y etiquetas de display — ninguno
vuelve al path de scoring ni de veredicto. El módulo no tiene importadores en
código de producción (grep confirmado). Convertir a Decimal en contexto de
renderizado sería sobreingeniería sin beneficio Daubert. Cerrado como falso
positivo de auditoría L-021.

---

## B-011 — assert en guard P0 de abductive_reasoner_v2.py (python -O lo desactiva)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit 9c7d923 |
| **Severidad** | P1 — guard Daubert desaparece en modo optimizado |
| **Archivo** | `vigia/inference/abductive_reasoner_v2.py` |
| **Línea** | 143 |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |

### Descripción

```python
assert not isinstance(value, float), (
    f"INVARIANTE 1 VIOLADA en '{context}':..."
)
```

Este `assert` es el guard P0 que impide que floats entren al path de scoring
abductivo. Con `python -O` (modo optimizado), todos los `assert` se eliminan
en compilación y el guard desaparece silenciosamente — floats pasan sin
detección, violando el invariante Daubert de reproducibilidad exacta.

### Fix

```python
if isinstance(value, float):
    raise ValueError(
        f"INVARIANTE 1 VIOLADA en '{context}': "
        f"Se detectó float: {repr(value)}. "
        f"Todo cálculo de score DEBE usar Fraction(numerador, denominador). "
        f"Corrección: Fraction({value}).limit_denominator(10**9). "
        f"Fundamento: Daubert requiere reproducibilidad exacta."
    )
```

---

## B-012 — assert en verify_determinism_cross_arch() de caie.py (python -O lo desactiva)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit 9c7d923 |
| **Severidad** | P2 — función de verificación, no path de scoring |
| **Archivo** | `vigia/tools/caie.py` |
| **Líneas** | 2239, 2242, 2248 |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |

### Descripción

`verify_determinism_cross_arch()` usa `assert` para verificar determinismo
bit-idéntico. Con `python -O`, los asserts se eliminan y la función retorna
`True` sin verificar nada — falsa sensación de verificación aprobada.

No está en el path de scoring de producción (se llama explícitamente), pero
es la función que valida el Deterministic Forensic Protocol P0.

### Fix

Reemplazar cada `assert condicion, mensaje` por `if not condicion: raise RuntimeError(mensaje)`.

---

## B-013 — LOG_VS_MEMORY dispara con raw_score bajo (diseño vs contrato) [CERRADO POR DISEÑO]

| Campo | Valor |
|-------|-------|
| **Estado** | CERRADO POR DISEÑO — decisión de Anna, Tanda B (2026-07-03) |
| **Severidad** | P1 — afecta monotonicidad del sistema |
| **Archivo** | `vigia/tools/caie.py` — `_extract_assertions()` |
| **Detectado en** | Sesión post-hackathon 2026-06-25, propiedad-testing |

### Descripción

Un artefacto `log_entry` con `raw_score=0.3` (evidencia débil) que contiene
`dst_ip` dispara la fractura `LOG_VS_MEMORY` con `is_structural=True`, forzando
`structural_verdict=MALICE` y `verdict=MALICE` aunque:
- `probabilistic_verdict=NOISE`
- `composite_score=0.0116` (muy bajo)

### Secuencia reproducible

```python
A_mem  = Artifact('mem_tool', 'memory_process', 0.1, 'Clean', {'pid': 4521})
A_weak = Artifact('log_tool', 'log_entry', 0.3, 'Weak', {'dst_ip': '10.0.0.1'})

run([A_mem])           # verdict=INCONCLUSIVE, fractures=0
run([A_weak, A_mem])   # verdict=MALICE, fractures=1 — salto no monotónico
```

### Causa raíz

`_extract_assertions()` no considera `raw_score` — solo presencia/ausencia de
campos de metadata. La fractura LOG_VS_MEMORY dispara si `dst_ip` existe en
el log, independientemente de cuán débil sea la evidencia.

La regresión L-028 (que reemplazó metadata["verdict"] por assertions) eliminó
la dependencia del veredicto upstream pero también eliminó el gate implícito
de severidad que ese veredicto proporcionaba.

### Opciones de resolución

A. Agregar gate de raw_score en `_extract_assertions()` para
   `log_claims_outbound_connection`: solo afirmar si `raw_score >= threshold`.
   Riesgo: introduce threshold arbitrario (anti-Daubert).

B. Que la fractura estructural requiera corroboración mínima de score antes
   de forzar MALICE. La contradicción existe, pero sin fuerza probatoria.

C. Documentar como comportamiento intencional: la contradicción lógica existe
   independientemente del score. El score mide "cuán sospechoso", la fractura
   mide "cuán imposible". Son dimensiones ortogonales.

### Nota

Opción C es la más Daubert-compatible: "este log AFIRMA una conexión saliente
Y la memoria NO LA MUESTRA — eso es una contradicción objetiva, independiente
de cuán confiable sea el log". La fuerza del hallazgo se modula por severity
(0.75 sin PID overlap, 0.95 con overlap), no por el raw_score del log.

### Cierre por diseño (Tanda B, decisión de Anna)

Doctrina adoptada: **la contradicción estructural ES la señal** — la
magnitud individual de los artefactos es irrelevante cuando dos fuentes se
contradicen. El filtro correcto contra artefactos-basura es el trust de
adquisición (L-037b, propagación de artifact_reliability a CAIE base_trust —
mismo commit Tanda B), no un umbral arbitrario de raw_score.

**Caveat registrado (Anna, 2026-07-03):** "No hay FP aún. No encontrados al
menos — no significa que no haya escenarios que puedan pasar."
**Condición de reapertura:** si aparece un FP real de golden rule con
artefactos débiles POST-L-037b, reabrir con la opción A del
PROPUESTA_TANDA_B.md ítem 8 (umbral `GOLDEN_RULE_MIN_SCORE`), calibrado con
ese caso como dato.

---

## B-014 — _extract_assertions() no filtra IPs reservadas/loopback

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit 41908e4 (reserved IP filter in _extract_assertions) |
| **Severidad** | P1 — falso positivo garantizado, Daubert-indefendible |
| **Archivo** | `vigia/tools/caie.py` — `_extract_assertions()` |
| **Detectado en** | Sesión post-hackathon 2026-06-25, property-testing |

### Descripción

`_extract_assertions()` afirma `log_claims_outbound_connection` para cualquier
valor string no vacío en `dst_ip`/`dest_ip`, incluyendo IPs que no pueden
ser conexiones salientes reales:

```
127.0.0.1   → MALICE  (loopback — es localhost)
0.0.0.0     → MALICE  (dirección nula)
255.255.255.255 → MALICE  (broadcast)
localhost   → MALICE  (nombre de loopback)
::1         → MALICE  (IPv6 loopback)
```

Una conexión a `127.0.0.1` es comunicación intra-proceso — no puede ser
exfiltración C2. Disparar LOG_VS_MEMORY por eso es un falso positivo
estructural que ningún perito forense podría defender en juicio.

### Fix

Agregar lista de IPs/rangos reservados que no constituyen "conexión saliente":
- `127.0.0.0/8` (loopback)
- `0.0.0.0`
- `255.255.255.255`
- `localhost`, `::1`, `fe80::`

---

## B-015 — PID y dst_ip no se normalizan (whitespace, tabs, newlines)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit 3607cc7 (PID str().strip(), IP type validation) |
| **Severidad** | P1 — rompe correlación PID y dispara fractura con IPs malformadas |
| **Archivo** | `vigia/tools/caie.py` — `_extract_assertions()`, PID canonicalization |
| **Detectado en** | Sesión post-hackathon 2026-06-25, adversarial fuzzing |

### Descripción

Valores con whitespace no se normalizan antes de procesarse:

**PID:** `str('4521 ') == '4521 '` ≠ `str(4521) == '4521'`
→ PID overlap no se detecta → severity 0.75 en vez de 0.95

**dst_ip:** `'1.2.3.4 '` (con espacio) es string no vacía
→ `_dest_valid = isinstance(str, str) and bool('1.2.3.4 '.strip())` = True
→ fractura dispara con IP malformada que ningún sistema real emitiría así

### Fix

Normalizar con `.strip()` antes de cualquier comparación:
- PID: `str(pid).strip()` en lugar de `str(pid)`
- dst_ip/dest_ip: ya tienen `.strip()` en `_dest_valid` pero el valor
  malformado igual entra al bundle

---

## AUDITORÍA NEGATIVA — Propiedades Verificadas y No Vulnerables (2026-06-25/26)

Este apartado documenta invariantes y vectores de ataque que fueron probados
exhaustivamente y NO encontraron bugs. Su propósito es evitar repetir auditorías
sobre superficie ya cubierta.

### Motor CAIE (vigia/tools/caie.py)

| Propiedad | Resultado | Método |
|-----------|-----------|--------|
| Insertion order invariance (I1) | PASS | 3 permutaciones, mismo fracture_graph |
| Re-evaluation idempotency (I2) | PASS | 10 runs consecutivos, mismo state vector |
| Score determinism (I3) | PASS | 10 runs paralelos, composite_score idéntico |
| Semantic content invariance (I4) | PASS | description ignorada por _extract_assertions |
| Benign non-regression (I5) | PASS | 0 MALICE en 16 casos VIGIA-BEN-* |
| Negative invariance (I6) | PASS | sin dst_ip → no fractura; score bajo → cambia |
| Output aliasing | PASS | r["fractures"].append() no afecta estado interno |
| Input mutation | PASS | add_artifact() hace deepcopy, metadata original intacta |
| NaN/inf en raw_score | PASS | Finite Math Shield zeroa el score, fractura structual se evalúa correctamente |
| Objetos arbitrarios en metadata (UUID, datetime, Path, bytes) | PASS | str() canonicalization absorbe todos |
| Campos Unicode invisibles en keys (ZWSP, NBSP, cyrílico) | RESUELTO→PASS | B-016 fix: NFKC+strip |
| Nested dict hash collision | RESUELTO→PASS | B-017 fix: json.dumps sort_keys=True |
| PID int/str/float coercion | RESUELTO→PASS | str().strip() canonicalization |
| network_connections truthiness | RESUELTO→PASS | isinstance(list/dict) validation |
| source_tool casing/whitespace | RESUELTO→PASS | casefold() en Noisy-OR grouping |
| reserved IPs (loopback, broadcast) | RESUELTO→PASS | B-014 fix: _is_reserved_ip() |
| Metadata dict aliasing post-add_artifact | RESUELTO→PASS | copy.deepcopy() en add_artifact |

### Scorer (vigia_scorer.py)

| Propiedad | Resultado | Método |
|-----------|-----------|--------|
| Ley 1: run(A) == run(deepcopy(A)) | PASS | case_001_temporal |
| Ley 2: json roundtrip invariance | PASS | json.dumps/loads preserve score |
| Ley 4: input immutability | PASS | case no mutado post-run |
| Ley 5: idempotency (sin timestamps) | PASS | 3 runs consecutivos |
| Ley 6: monotonicidad | PASS (por diseño) | score crece al agregar artefactos |
| Ley 7: score ∈ [0,1] | PASS | isfinite, bounded |
| Ley 3: order invariance | PASS | artifacts reversed → mismo score |
| Bundle vacío | DOCUMENTADO | verdict=ERROR con campo error explicativo |

### Pipeline (vigia/pipeline/pipeline.py)

| Propiedad | Resultado | Método |
|-----------|-----------|--------|
| Reentrancia (run case1, case2, case1) | PASS | run3 == run1 exacto |
| Estado residual entre runs | PASS | fractures=0 constante en 4 runs |
| Input immutability | PASS | bundle no mutado post-run_full |
| Objetos compartidos (mismo artifact dos veces) | PASS | sin aliasing |
| Campos Unicode/raros en metadata | PASS | absorbidos silenciosamente |
| Recuperación post-excepción | PASS | pipe usado tras CaseSchemaError produce resultado idéntico a fresh pipe |
| Singletons mutables | N/A | todos los globals son constantes de lookup frozen |

### E/S y Sistema

| Propiedad | Resultado | Método |
|-----------|-----------|--------|
| datetime.now() local (sin UTC) | PASS | grep: cero resultados sin timezone |
| tempfile sin cleanup | PASS | document_integrity.py usa finally: os.unlink() |
| json.dumps sin sort_keys en paths de hash | PASS | adversarial_mutation_suite y vigia_planner usan sort_keys=True |
| NaN/inf en scores de pipeline | PASS | isfinite() confirmado |

---

## B-016 — memory_forensics.py no valida formato de imagen de memoria (VMware vs RAM dump puro) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07, Grupo B / B3): detector stderr portado al motor V4 (`classify_vol3_stderr` + `MemoryImageFormatError` + señal `unanalyzed`), tests rojos primero — ver B-087 |
| **Severidad** | P2 — produce error poco informativo en lugar de diagnóstico claro |
| **Archivo** | `vigia/sift/memory_forensics.py` (o el caller que invoca Volatility3) |
| **Detectado en** | Sesión 2026-06-27 |

### Descripción

Cuando se pasa un archivo `.img` que es en realidad una snapshot de VMware
(formato VMEM/snapshot), Volatility3 falla con `InvalidAddressException`.
El agente acepta el archivo sin verificar si es un dump de RAM puro o una imagen
VMware que requiere archivos companion (`.vmss` o `.vmsn`) para resolver las
estructuras internas.

### Impacto

- El error de Volatility3 no es informativo: el usuario ve `InvalidAddressException`
  sin contexto de por qué falla.
- Si faltan los archivos companion VMware, no hay forma de continuar el análisis
  de memoria — la investigación queda truncada sin diagnóstico claro.
- En un contexto forense, esto puede enmascarar evidencia no examinada como
  "evidencia no disponible" cuando el problema es operativo, no de contenido.

### Fix cuando corresponda

Agregar detección de formato antes de invocar Volatility3:
1. Leer los primeros bytes del archivo y verificar el magic number.
   - RAM dump puro (LiME): magic `0x4C694D45`
   - VMEM VMware: header diferente; requiere `.vmss`/`.vmsn` companion
2. Si se detecta formato VMware, emitir mensaje de error claro indicando que
   se requieren los archivos companion y qué hacer.
3. Documentar la limitación en `KNOWN_LIMITATIONS.md` si no se puede resolver
   en el scope actual.

### Actualización (2026-07-03, triage)

El adaptador vol3 del shim — el camino que realmente corre en modo agente —
ya detecta el caso (stderr: InvalidAddressException / no valid kernel / …) y
emite `FORMAT_NOT_SUPPORTED` → ABSTAIN. Pendiente solo: portar el mismo
detector a `memory_forensics.py` (motor V4, requiere binario `vol`). Tanda B.

---

## B-017 — `defusedxml` ausente en el venv produce PIPELINE_ERROR silencioso [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda A (TRIAGE 2026-07-03), tag `pre-tanda-a-20260703-134624` |
| **Severidad** | P2 — el agente sella el bundle con veredicto `PIPELINE_ERROR` en lugar de abortar con diagnóstico claro |
| **Archivo** | `vigia/sift/` (orquestador real) — el import de `defusedxml` falla en runtime |
| **Detectado en** | Sesión 2026-06-27, caso NPS-2010-EMAILS, modo 1 (`vigia_agent.py`) |

### Actualización de cierre (2026-07-03, Tanda A — T-1/T-2)

El triage amplió el alcance real del bug:
- **T-1**: el `raise ImportError` a nivel de módulo en
  `event_log_correlator.py` mataba el paquete `vigia.sift` ENTERO (los 14
  motores V4, vía el import incondicional de `vigia/sift/__init__.py:19`) —
  no solo el análisis de event logs. `[REPRODUCIDO]`
- **T-2**: el gatillo real: `defusedxml` estaba en `requirements.txt` y
  `pyproject.toml` pero NO en `requirements-ci.txt` — un entorno CI arrancaba
  sin él.

Fix aplicado:
1. `requirements-ci.txt`: agregado `defusedxml>=0.7.1`.
2. `event_log_correlator.py`: import GUARDED (`ET = None`); sin defusedxml
   los archivos XML/EVTX se marcan `UNANALYZED_ARTIFACT` (→ ABSTAIN) y el
   resto de los motores opera. La protección XXE se mantiene: NUNCA se cae a
   `xml.etree` — sin defusedxml simplemente no se parsea XML.
3. Tests: `tests/test_tanda_a_triage.py::TestA1DefusedxmlResilient` (4) —
   incluye subproceso con defusedxml bloqueado que verifica que
   `vigia.sift` importa y el orquestador se construye.

*(Nota de higiene 2026-07-05, Fase 0: la nota de cierre anterior se había
insertado partiendo la tabla de campos en dos, dejando `Estado: ABIERTO`
huérfano debajo — el campo decía ABIERTO mientras el título decía RESUELTO.
Tabla restaurada y Estado sincronizado; hallazgo S-4 de
`docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md`.)*

### Descripción

Cuando `defusedxml` no está instalado en el venv, el orquestador real falla al importar
el módulo y lanza la excepción:

```
FIX P2: defusedxml es obligatorio para protección contra XXE/Billion Laughs.
Instalar: pip install defusedxml>=0.7.1
```

El agente captura el error en el bloque `except` del orchestrator shim, emite 0 señales,
y sella el bundle con `verdict = PIPELINE_ERROR`. El proceso termina con exit code 0 y
`alert_level = LOW`, lo que enmascara el fallo de infraestructura como si fuera un
resultado forense válido.

### Impacto

- El bundle queda sellado con `PIPELINE_ERROR` — un veredicto de error de pipeline,
  no un veredicto forense. Si no se lee el log de ejecución, el resultado parece
  un NOISE legítimo.
- El pipeline determinista no procesa ningún artefacto: 0 señales, 0 z-scores.
  La ausencia de señales no es evidencia de inocencia — es un artefacto del fallo.
- En un entorno de producción o auditoría, esto podría registrar un "no malicioso"
  sobre evidencia que nunca fue analizada.
- `defusedxml` es una dependencia de seguridad obligatoria (protección XXE/Billion
  Laughs en parsing XML). Su ausencia no es opcional.

### Fix cuando corresponda

1. Agregar `defusedxml>=0.7.1` a `requirements.txt` (y `pyproject.toml` si aplica).
2. En el arranque del agente (`vigia_agent.py`), verificar que el import de `defusedxml`
   tenga éxito antes de iniciar el pipeline. Si falla, abortar con exit code ≠ 0 y
   mensaje explícito — no sellar un bundle con `PIPELINE_ERROR`.
3. En el orquestador shim, distinguir entre "pipeline ejecutado y produjo 0 señales"
   (NOISE legítimo) y "pipeline no ejecutado por fallo de dependencia" (error de
   infraestructura — no emitir veredicto forense).

### Workaround inmediato

```bash
pip install defusedxml>=0.7.1
```

### Vectores descartados como falsos positivos

- **B-009** (floats en vigia_artifact_graph.py): módulo de visualización puro, sin callers en scoring path. float() correcto para cálculos de tamaño de píxeles y pesos de display.
- **Copilot Bug 28/11/15** (signal_mapper.py .lower() sobre tool_name): archivo inexistente, bug completamente alucinado por Copilot. Patrón no existe en el codebase.
- **_calibration_dataset acumulación**: inicializado en __init__ pero nunca se llena entre runs — no hay estado residual.

---

## B-018 — Volatility3 subprocess timeout en `vigia_agent.py` para dumps grandes (≥4 GB) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07, Grupo B / B4): VIGIA_VOL3_TIMEOUT + escalado por tamaño + rastro completo en pipeline_meta (timeout_partial/timeout_all) — ver B-087 |
| **Severidad** | P1 — el pipeline sella un bundle con 0 señales sin advertir que Volatility3 no terminó |
| **Archivo** | `vigia/pipeline/` / `vigia_agent.py` (orquestador de subprocess vol3) |
| **Detectado en** | Sesión 2026-06-27, batch NARCOS SRL-2018, 12 dumps ≥4 GB |

### Descripción

El pipeline lanza Volatility3 como subprocess (`vol3` o venv `vol`) y asume que termina
en ~2 segundos. Para dumps de memoria RAM de ≥4 GB, los plugins individuales necesitan:
- `windows.info`: ~8–10 s
- `windows.pslist`: ~15–20 s
- `windows.netscan`: ~25–35 s
- `windows.malfind`: ~25–40 s

Cuando el subprocess expira antes de que vol3 produzca output, el pipeline interpreta
el stdout vacío como "0 señales" y sella el bundle con `signal_count=0`.

La distinción crítica que se pierde:
- `0 señales` porque el dump es benigno → NOISE válido
- `0 señales` porque vol3 no terminó → artefacto de infraestructura

### Síntoma observado

En el batch NARCOS (12 dumps), los bundles `_claude.json` (nuevos) producen 0 señales
con `vol3_binary=vol3` (binario de sistema, más lento). Los bundles `_bundle.json`
(corridos previamente con timeout mayor o sin timeout) producen señales reales:
- `NARCOS-JOHN-PRIMARY-Day2_bundle.json`: 4 señales (LOLBAS, netscan, malfind 30 proc)
- `NARCOS-STEVE-Day4_bundle.json`: 2 señales (pslist, malfind 21 proc)
- `NARCOS-JANE-*_bundle.json`: 0 señales reales (Jane genuinamente limpia o B-018)

El bundle usa `vol3_binary=/home/.../venv/bin/vol` cuando el timeout es suficiente,
y `vol3_binary=vol` (sistema) cuando no lo es — el path del binario es un indicador
indirecto del timeout.

### Impacto forense

Un investigador que vea 0 señales en un dump de John Primary Day2 (donde hay LOLBAS,
Discord C2, jRAT 4782 y malfind en 30 procesos) podría cerrar el caso como NOISE.
Esto es un fallo de cadena de custodia, no un fallo de análisis.

En el contexto NARCOS: Jane Day2/3/4 muestran 0 señales. No es posible distinguir
desde el bundle solo si Jane está limpia o si el pipeline se agotó antes de terminar.

### Fix cuando corresponda

1. Aumentar el timeout del subprocess vol3 a ≥60 s por plugin (o configurable vía
   `VIGIA_VOL3_TIMEOUT_SECONDS`).
2. Capturar el returncode del subprocess: si vol3 termina por timeout (SIGKILL/SIGTERM),
   emitir `PIPELINE_TIMEOUT` en `pipeline_meta.error`, no `signal_count=0`.
3. Distinguir en el bundle: `"pipeline_status": "completed"` vs `"pipeline_status": "timeout"`.
4. En el log de auditoría, registrar el tiempo de ejecución real del subprocess.

### Workaround inmediato

Correr vol3 directamente sobre el dump antes de llamar a `vigia_agent.py`:

```bash
vol -f /path/to/dump windows.info
vol -f /path/to/dump windows.pslist
vol -f /path/to/dump windows.netscan
vol -f /path/to/dump windows.malfind
```

Y usar esos resultados como contexto para `reason_with_llm` en modo Claude Code.

### Nota de auditoría

Los bundles `NARCOS-*_claude.json` en `results/srl2018/` están afectados por este bug.
Los bundles `NARCOS-*_bundle.json` (corridos con timeout suficiente) son los
archivos de referencia para el análisis forense de esta sesión.

### Actualización (2026-07-03, triage)

Post P1-D: si TODOS los plugins timeoutean → `UNANALYZED_ARTIFACT` → ABSTAIN
(no benigno, no crash). Pendiente para completar el análisis en dumps
grandes: `VIGIA_VOL3_TIMEOUT` (env var) + escalado por tamaño de imagen,
registrando el timeout usado en `pipeline_meta`. Tanda B.

---

## B-019 — `_EPC_FACTOR_TABLE` valores incorrectos para k=4..15 en `vigia_scorer.py`

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `04506c0` |
| **Severidad** | P0 — path de scoring determinista, afecta reproducibilidad Daubert |
| **Archivo** | `vigia_scorer.py` (scorer standalone, entry point principal Mode 1) |
| **Función** | Módulo-level — tabla de lookup `_EPC_FACTOR_TABLE` |
| **Líneas originales** | 85–100 (valores k=4..15 en la tabla) |
| **Commit fix** | `04506c0` — POST HACKATHON: fix B-EPC |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

La tabla `_EPC_FACTOR_TABLE` es un array de lookup que reemplaza la operación
`(19/20)**k` para evitar float en el path de scoring (invariante P0 / L-021).
Cada entrada corresponde a un valor `k = max(0, len(provenance_chain) - 3)`,
es decir, la penalización por cada eslabón de cadena de custodia más allá de 3.

Los valores para k=0..3 eran correctos (k=0 trivial, k=1..3 calculados manualmente
con precisión suficiente). Los valores para **k=4..15** eran aproximaciones racionales
calculadas manualmente con errores de redondeo — no correspondían a `Fraction(19,20)**k`
exacto.

Ejemplo del error para k=4:

```python
# ANTES (incorrecto):
4: Fraction(80461, 98785),      # ≈ 0.81452... pero (19/20)**4 = 130321/160000 ≈ 0.81451

# DESPUÉS (correcto):
4: Fraction(130321, 160000),    # = 19**4 / 20**4 exacto
```

Las discrepancias se acumulan a partir de k=4 con errores relativos del orden de 1e-5
a 1e-6. Si bien el impacto por artefacto individual es pequeño, en cadenas largas
(k=10..15, provenance_chain de 13–18 eslabones) el EPC score acumulado divergía de
la fórmula matemática declarada.

### Impacto forense

- **Reproducibilidad Daubert comprometida:** un tercero que replicara el cálculo con
  `(Fraction(19,20))**k` exacto obtendría un `effective_trust` diferente al producido
  por el scorer, rompiendo el invariante "bit-idéntico entre arquitecturas".
- **Afectados:** casos con provenance_chain de más de 3 eslabones (k ≥ 1 efectivo).
  En la práctica, casos de alta fidelidad forense con cadenas largas (imágenes E01
  con múltiples niveles de custodia) recibían penalizaciones EPC ligeramente distintas
  a las declaradas en la documentación del modelo.
- **Severidad P0** porque la tabla es parte del Deterministic Forensic Protocol:
  cualquier divergencia numérica, aunque pequeña, invalida la attestation de
  reproducibilidad en el bundle sellado.

### Fix aplicado

Reemplazados los 12 valores incorrectos (k=4..15) por los valores exactos
`Fraction(19**k, 20**k)` para cada k:

```python
_EPC_FACTOR_TABLE: dict[int, Fraction] = {
     0: Fraction(1),
     1: Fraction(19, 20),
     2: Fraction(361, 400),
     3: Fraction(6859, 8000),
     4: Fraction(130321, 160000),
     5: Fraction(2476099, 3200000),
     6: Fraction(47045881, 64000000),
     7: Fraction(893871739, 1280000000),
     8: Fraction(16983563041, 25600000000),
     9: Fraction(322687697779, 512000000000),
    10: Fraction(6131066257801, 10240000000000),
    11: Fraction(116490258898219, 204800000000000),
    12: Fraction(2213314919066161, 4096000000000000),
    13: Fraction(42052983462257059, 81920000000000000),
    14: Fraction(799006685782884121, 1638400000000000000),
    15: Fraction(15181127029874798299, 32768000000000000000),
}
```

Verificación: `all(Fraction(19,20)**k == _EPC_FACTOR_TABLE[k] for k in range(16))` → True.

### Verificación

```
python3 -c "
from fractions import Fraction
table = {  # valores post-fix
    0: Fraction(1), 1: Fraction(19,20), 2: Fraction(361,400),
    3: Fraction(6859,8000), 4: Fraction(130321,160000),
    # ...
}
assert all(Fraction(19,20)**k == table[k] for k in table)
print('PASS — todos los valores son exactamente (19/20)^k')
"
```

---

## B-020 — Colapso semántico de ABSTAIN a NOISE en `sift_orchestrator.py`, `run_all_agent.py` y `run_llm_cases.py`

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `60e4d65` |
| **Severidad** | P1 — pérdida de distinción epistémica Daubert en bundles sellados |
| **Archivos** | `sift_orchestrator.py` (línea 179), `run_all_agent.py` (línea 84), `run_llm_cases.py` (línea 54) |
| **Función** | `SIFTOrchestrator._build_hypothesis()`, `extract_verdict_from_bundle()`, `_HYP_MAP` |
| **Líneas originales** | sift_orchestrator.py:179, run_all_agent.py:81–86, run_llm_cases.py:51–56 |
| **Commit fix** | `60e4d65` — POST HACKATHON: fix ABSTAIN_DETECTED |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

Los tres componentes del pipeline secundario (sift_orchestrator, run_all_agent,
run_llm_cases) no contemplaban `ABSTAIN` como rama de salida propia. El flujo de
decisión terminaba en un `else` que colapsaba todo veredicto no reconocido a
`NO_SEMIOTIC_ANOMALY_DETECTED`, que el mapper traducía a `NOISE`.

**Cadena del bug en `sift_orchestrator.py`:**

```python
# ANTES:
hypothesis = (
    "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
    else "SUSPICION_DETECTED" if expected == "SUSPICION"
    else "NO_SEMIOTIC_ANOMALY_DETECTED"   # ← capturaba ABSTAIN por defecto
)

# DESPUÉS:
hypothesis = (
    "MALICIOUS_INTENT_DETECTED" if (expected == "MALICE" or is_malice)
    else "SUSPICION_DETECTED" if expected == "SUSPICION"
    else "ABSTAIN_DETECTED" if expected == "ABSTAIN"   # ← rama propia
    else "NO_SEMIOTIC_ANOMALY_DETECTED"
)
```

**Mappers afectados:**

- `run_all_agent.py`: el dict de alias no tenía entrada `"ABSTAIN_DETECTED"`, por lo
  que caía al fallback `NOISE` (línea 169: `aliases["ABSTAIN"] → "UNKNOWN"`, pero
  `"ABSTAIN_DETECTED"` no estaba mapeada).
- `run_llm_cases.py`: `_HYP_MAP` tenía `"ABSTAIN": "ABSTAIN"` pero no
  `"ABSTAIN_DETECTED": "ABSTAIN"` — los bundles con hipótesis `ABSTAIN_DETECTED`
  no se mapeaban correctamente.

### Impacto forense

La distinción entre `NOISE` y `ABSTAIN` es semánticamente crítica bajo el estándar
Daubert:

- **NOISE** = "el sistema analizó la evidencia y no encontró anomalías". Implica que
  el análisis se completó y el resultado es negativo.
- **ABSTAIN** = "el sistema no tiene datos suficientes para pronunciarse". Implica que
  el análisis está incompleto o la evidencia es insuficiente para un veredicto.

Los casos **VIGIA-SEP800-001**, **VIGIA-SET68I-001** y **VIGIA-ANDROID11-001**
tenían `expected_verdict: "ABSTAIN"` (firmware sin datos de usuario, imagen de 10GB
sin extraer). Al colapsar a NOISE, sus bundles sellaban:

```
"verdict": "NOISE"
"best_hypothesis": "NO_SEMIOTIC_ANOMALY_DETECTED"
```

…lo que afirmaba falsamente que el análisis se había completado sin anomalías, en
lugar de declarar insuficiencia epistémica. Bajo cross-examination, esto sería
indefendible: el perito habría "certificado" la inocencia de evidencia no analizada.

### Fix aplicado

Tres inserciones de una línea cada una:

1. `sift_orchestrator.py:179` — rama `else "ABSTAIN_DETECTED" if expected == "ABSTAIN"` antes del `else` final.
2. `run_all_agent.py:84` — entrada `"ABSTAIN_DETECTED": "ABSTAIN"` en el dict de aliases.
3. `run_llm_cases.py:54` — entrada `"ABSTAIN_DETECTED": "ABSTAIN"` en `_HYP_MAP`.

### Verificación

```python
# sift_orchestrator: caso ABSTAIN produce hipótesis correcta
assert build_hyp("ABSTAIN") == "ABSTAIN_DETECTED"

# run_all_agent: mapper convierte correctamente
assert extract_verdict(bundle_with_abstain_detected) == "ABSTAIN"

# run_llm_cases: _HYP_MAP cubre la rama
assert _HYP_MAP["ABSTAIN_DETECTED"] == "ABSTAIN"
```

Casos afectados corregidos: SEP800, SET68I y ANDROID11 ahora sellan con
`verdict = "ABSTAIN"` / `best_hypothesis = "ABSTAIN_DETECTED"` en lugar de NOISE.

---

## B-021 — `sift_orchestrator.py` vol3 path emitted SUSPICION with 0 signals

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `1b0df1c` |
| **Severidad** | P1 — incorrect verdict on genuinely clean memory dumps |
| **Archivo** | `sift_orchestrator.py` |
| **Función** | Volatility3 orchestrator path — verdict emission |
| **Línea original** | 337 |
| **Commit fix** | `1b0df1c` — POST HACKATHON: fix B-021/B-022 |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

The Volatility3 orchestrator path had a binary hypothesis: `MALICIOUS_INTENT_DETECTED`
or `SUSPICION_DETECTED`. When `avg == Fraction(0, 1)` — i.e., memory analysis produced
zero signals — the fallback branch emitted `SUSPICION_DETECTED` instead of
`NO_SEMIOTIC_ANOMALY_DETECTED`.

```python
# BEFORE:
verdict = (
    "MALICIOUS_INTENT_DETECTED" if avg > threshold
    else "SUSPICION_DETECTED"   # ← fired even when avg == Fraction(0,1)
)

# AFTER:
verdict = (
    "MALICIOUS_INTENT_DETECTED" if avg > threshold
    else "NO_SEMIOTIC_ANOMALY_DETECTED" if avg == Fraction(0, 1)   # ← new middle branch
    else "SUSPICION_DETECTED"
)
```

A clean memory dump correctly analyzed by Volatility3 (no malicious processes, no
network anomalies, no malfind hits) received an incorrect `SUSPICION` verdict solely
because it produced zero signals — which is the expected result for a clean dump.

### Impacto forense

- A genuinely clean memory image was sealed with `verdict = SUSPICION_DETECTED`, implying
  anomalies were present when none were. Under Daubert cross-examination, the analyst
  would be unable to identify what anomaly triggered the suspicion verdict — because
  there was none. The bundle would be indefensible.
- `SUSPICION` requires a "documented baseline deviation" (see Verdict Scale). Zero signals
  is the absence of deviation, not a deviation. The verdict violated its own definition.
- Affected any case processed through the vol3 path where the memory image was clean:
  the incorrect verdict propagated into the sealed bundle and accuracy metrics.

### Fix aplicado

Added middle branch at line 337: emit `NO_SEMIOTIC_ANOMALY_DETECTED` when
`avg == Fraction(0, 1)`. `SUSPICION_DETECTED` is now only emitted when `avg > Fraction(0, 1)`
but below the `MALICIOUS_INTENT_DETECTED` threshold — i.e., when there are real signals
that do not reach the malice threshold.

### Verificación

```python
# vol3 path with 0 signals → NO_SEMIOTIC_ANOMALY_DETECTED
assert orchestrator.build_vol3_verdict(avg=Fraction(0, 1)) == "NO_SEMIOTIC_ANOMALY_DETECTED"

# vol3 path with weak signals → SUSPICION_DETECTED
assert orchestrator.build_vol3_verdict(avg=Fraction(1, 10)) == "SUSPICION_DETECTED"
```

---

## B-022 — `run_all_agent.py` accuracy comparator aliased `ABSTAIN` → `UNKNOWN`

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `1b0df1c` |
| **Severidad** | P1 — ABSTAIN cases counted as FAIL in accuracy metrics |
| **Archivo** | `run_all_agent.py` |
| **Función** | Accuracy comparator dict |
| **Línea original** | 168 |
| **Commit fix** | `1b0df1c` — POST HACKATHON: fix B-021/B-022 |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

The accuracy comparator dict contained the entry `"ABSTAIN": "UNKNOWN"`, while the
main verdict mapper used `"ABSTAIN": "ABSTAIN"`. The two dicts were inconsistent:

```python
# run_all_agent.py line 168 — BEFORE:
comparator_aliases = {
    ...
    "ABSTAIN": "UNKNOWN",   # ← diverged from main mapper
}

# main verdict mapper (correct):
verdict_map = {
    ...
    "ABSTAIN": "ABSTAIN",
}
```

When a case had `expected_verdict = "ABSTAIN"` and the scorer correctly produced a
bundle with `verdict = "ABSTAIN"`, the comparator translated the produced verdict to
`"ABSTAIN"` but the expected value went through the alias dict and became `"UNKNOWN"`.
The comparison `"ABSTAIN" == "UNKNOWN"` evaluated to False → the case was counted as
FAIL in accuracy metrics.

### Impacto forense

- All ABSTAIN cases (e.g., VIGIA-SEP800-001, VIGIA-SET68I-001, VIGIA-ANDROID11-001)
  that correctly produced ABSTAIN verdicts were counted as accuracy failures, depressing
  the reported accuracy score.
- The artifact made the system appear less accurate than it was, specifically on the
  class of cases where the correct answer is epistemic abstention. This is the opposite
  of a conservative error: the system was correct but reported as wrong.
- Accuracy numbers computed with this bug in place must be treated as underestimates
  for the ABSTAIN class.

### Fix aplicado

Removed the `"ABSTAIN": "UNKNOWN"` alias from the comparator dict. `"ABSTAIN"` now
maps to itself in both dicts, restoring consistency. ABSTAIN cases that produce the
correct verdict are now counted as PASS.

### Verificación

```python
# ABSTAIN case with correct verdict → PASS
bundle = {"verdict": "ABSTAIN"}
expected = "ABSTAIN"
assert comparator.compare(bundle, expected) == "PASS"
```

---

## B-023 — `_apply_quadripartite` silently collapsed unknown verdicts to `ABSTAIN`

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `fb95648` |
| **Severidad** | P1 — unrecognized verdict strings silently produced forensically incorrect ABSTAIN bundles |
| **Archivo** | `vigia_scorer.py` |
| **Función** | `_apply_quadripartite()` |
| **Línea original** | 332 |
| **Commit fix** | `fb95648` — POST HACKATHON: fix B-023 |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

`_apply_quadripartite()` used `.get()` with a silent fallback to map verdict strings
to their raw score representation:

```python
# BEFORE:
raw = _VERDICT_TO_RAW.get(verdict, "ABSTAIN")
```

Any verdict string not present in `_VERDICT_TO_RAW` — whether from a typo, a new
verdict state added to the scale without updating the table, or a pipeline bug
producing a malformed string — was silently mapped to `"ABSTAIN"` with no error,
no log entry, and no diagnostic output.

This violated the Daubert fail-loud principle: a forensic system that silently
produces an incorrect result is less defensible than one that halts with an explicit
error, because the incorrect result may be presented as evidence without any visible
indication that something went wrong.

### Impacto forense

- A typo in a verdict string (e.g., `"MALICEE"`, `"intent"`, `"SUSPICION "` with
  trailing whitespace) would produce a sealed bundle with `verdict = "ABSTAIN"` —
  the epistemic abstention verdict — without any indication that the verdict is the
  result of a lookup failure rather than a genuine analytical decision.
- A new verdict state added to the scale (e.g., `"INCONCLUSIVE"`) without updating
  `_VERDICT_TO_RAW` would silently collapse to ABSTAIN across all cases that reached
  that state. The bug would be invisible in the bundle output, discoverable only by
  auditing the source table.
- Under cross-examination: the analyst would be unable to explain why the bundle
  emits ABSTAIN for a case that reached a non-ABSTAIN verdict state.

### Fix aplicado

Replaced `.get()` with explicit membership check. If `verdict` is not in
`_VERDICT_TO_RAW`, a `ValueError` is raised with full diagnostic (Daubert fail-loud
principle):

```python
# AFTER:
if verdict not in _VERDICT_TO_RAW:
    raise ValueError(
        f"_apply_quadripartite: unrecognized verdict '{verdict}'. "
        f"Valid values: {sorted(_VERDICT_TO_RAW.keys())}. "
        f"Update _VERDICT_TO_RAW if a new verdict state was added to the scale."
    )
raw = _VERDICT_TO_RAW[verdict]
```

The failure is now loud, explicit, and traceable — the bundle is never sealed with
a silently incorrect verdict.

### Verificación

```python
# recognized verdict → normal path
assert _apply_quadripartite("MALICE") == expected_raw_malice

# unrecognized verdict → ValueError, not silent ABSTAIN
try:
    _apply_quadripartite("MALICEE")
    assert False, "should have raised"
except ValueError as e:
    assert "unrecognized verdict" in str(e)
```

---

## B-024 — `epc_factor = 0.1` float literal in EPC path (BROKEN chain case)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `fb95648` (same as B-023) |
| **Severidad** | P0 — float in deterministic scoring path, L-021 homogeneity violation |
| **Archivo** | `vigia_scorer.py` |
| **Función** | EPC (Evidence Provenance Chain) scoring path |
| **Línea original** | 476 |
| **Commit fix** | `fb95648` — POST HACKATHON: fix B-023 |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

When `provenance_chain` is empty or `chain_status == "BROKEN"`, the EPC scoring path
assigned `epc_factor` using the float literal `0.1`:

```python
# BEFORE:
if chain_status == "BROKEN" or not provenance_chain:
    epc_factor = 0.1   # ← float literal in deterministic scoring path
else:
    epc_factor = _EPC_FACTOR_TABLE[k]   # ← Fraction from lookup table
```

The normal path (`_EPC_FACTOR_TABLE`) returns a `Fraction` with exact rational
arithmetic (invariant P0 / L-021). The BROKEN/empty path introduced a `float` at
the same variable in the same function, making the type of `epc_factor` dependent
on a runtime branch condition. Any downstream multiplication of `epc_factor` by a
`Fraction` score in the BROKEN path produced a `float` result, propagating the
homogeneity violation through the rest of the scoring computation.

This is classified P0 — the same severity as B-019 — because it represents a
direct violation of the Deterministic Forensic Protocol: a `float` in the scoring
path makes the result architecture-dependent and non-reproducible under the
bit-identical cross-architecture requirement.

### Impacto forense

- **Reproducibility violation:** on any case where `chain_status == "BROKEN"` or the
  provenance chain is absent, the `effective_trust` computation used a `float`
  intermediate. Two architectures (e.g., x86-64 Linux vs ARM64 macOS) may produce
  different IEEE 754 rounding results for the same case, producing different sealed
  bundles from identical input — breaking the Daubert attestation of reproducibility.
- **Homogeneity violation:** the EPC scoring function mixed `Fraction` and `float`
  arithmetic within a single execution depending on a runtime branch. This is
  structurally different from a clean boundary conversion and violates the L-021
  invariant that the entire scoring path operate in `Fraction`.
- **Affected cases:** any case with a broken or absent provenance chain — which
  includes adversarially submitted evidence, corrupted images, and cases where
  chain-of-custody documentation was not provided.

### Fix aplicado

Replaced the float literal with the exact `Fraction` equivalent:

```python
# AFTER:
if chain_status == "BROKEN" or not provenance_chain:
    epc_factor = Fraction(1, 10)   # exact rational: 0.1 = 1/10
else:
    epc_factor = _EPC_FACTOR_TABLE[k]
```

`epc_factor` is now always a `Fraction` regardless of branch, restoring type
homogeneity across the entire EPC scoring path.

### Verificación

```python
from fractions import Fraction

# BROKEN chain → Fraction, not float
epc = compute_epc_factor(chain_status="BROKEN", provenance_chain=[])
assert isinstance(epc, Fraction), f"expected Fraction, got {type(epc)}"
assert epc == Fraction(1, 10)

# empty chain → same
epc = compute_epc_factor(chain_status="OK", provenance_chain=[])
assert isinstance(epc, Fraction)
assert epc == Fraction(1, 10)
```

---

## B-025 — Architectural investigation: `Fraction` vs `float` boundary in scorer [CERRADO — subsumido]

| Campo | Valor |
|-------|-------|
| **Estado** | CERRADO — subsumido por AUDITORIA_L040_LIKELIHOOD_RATIO.md §4 (2026-07-03) |
| **Severidad** | P2 — architectural debt, not a functional bug |
| **Archivo** | `vigia_scorer.py` |
| **Función** | `_dround()`, `_dsum()`, and scoring formula path |
| **Línea original** | N/A — pervasive architectural question |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

The scorer maintains two documented invariants with different scopes:

**Invariant 1 — No non-deterministic floating-point operations:**
`pow()`, `math.log()`, and `math.exp()` are banned from the scoring path.
Enforced via three Fraction lookup tables: `_EPC_FACTOR_TABLE`, `_SUPPORT_SCORE_TABLE`,
`_EXP_NEG2_TABLE`. These tables return exact `Fraction` values.

**Invariant 2 — Deterministic output to 15 decimal places:**
Enforced via `_dround(value, digits)`, which calls `round(float(value), digits)` and
returns a `float`. This means the final score values emitted by the pipeline are
`float`, not `Fraction`.

The two invariants are different contracts. `_dround()` converts `Fraction` to `float`
at the output boundary. The scoring formulas between the lookup tables and `_dround()`
may operate on `Fraction`, `float`, or a mix — depending on how intermediate
computations are expressed.

The architectural question that has never been explicitly documented:

> Was `Fraction` arithmetic intended only for the lookup tables themselves (i.e., only
> the inputs to the formulas are exact rationals, but intermediate arithmetic may use
> float), or was `Fraction` intended to govern the entire pipeline up to the final
> `_dround()` call?

The existing code and comments use the term "Deterministic rounding" rather than
"Exact rational arithmetic", which suggests the former interpretation — `Fraction` as
a source of exact constants, not as the arithmetic type for the whole pipeline.
However, this has never been stated as an explicit architectural decision.

The risk of ambiguity: if a future contributor reads the `Fraction` tables as evidence
that "the pipeline uses exact rational arithmetic" and adds `Fraction`-typed
intermediate variables accordingly, they may collide with existing `float` paths and
introduce subtle type inconsistencies. Conversely, if someone assumes "everything is
float downstream of the tables" and removes a `Fraction` intermediate, they may
inadvertently introduce a rounding error that was load-bearing.

### Impacto forense

No current functional bug is known. The risk is future regression during refactoring:
without an explicit documented contract, the boundary between `Fraction` and `float`
arithmetic in the scoring path is implicit and fragile.

Under Daubert, the admissibility argument relies on claiming that the scoring pipeline
is deterministic and reproducible. If the exact boundary of `Fraction` arithmetic is
undocumented, a court-appointed reviewer cannot independently verify whether intermediate
computations are exact or subject to IEEE 754 rounding — which weakens the
reproducibility argument at the intermediate step level.

### Investigación requerida

Before any refactoring of `_dround()`, `_dsum()`, or the scoring formulas:

1. **Audit** every intermediate variable between a lookup table read and `_dround()`.
   Determine whether each is `Fraction` or `float` in the current implementation.
2. **Decide and document** the intended contract: "Fraction governs lookup table values
   only" or "Fraction governs all intermediate scoring arithmetic up to `_dround()`".
3. **Write the decision into a code comment** at the top of the scoring function —
   something that a future contributor will see before modifying the arithmetic path.
4. If the decision is "Fraction for intermediates too": audit for any implicit `float`
   casts introduced by arithmetic operators (e.g., `Fraction * int` stays `Fraction`,
   but `Fraction * float` becomes `float`).

This investigation is a prerequisite for any future L-021 Phase 3 work on this file.

### Cierre (2026-07-03)

La investigación pedida existe: `AUDITORIA_L040_LIKELIHOOD_RATIO.md` §4 mapea
los 7 paths float del camino de veredicto (U1-U7) con estado de cobertura,
divergencias medidas (~1 ulp, sin acumulación) y plan de de-floateo por
tablas (patrón `_EXP_NEG2_TABLE` del scorer / `security.py` P1-005), con U7
(record_hash cross-plataforma) como prioridad. Trabajo restante trackeado en
la Tanda B del TRIAGE_BUGS_LIMITACIONES_20260703.md.

---

## B-026 — `prior_trust` not validated at scorer boundary — negative values produce impossible states [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda A (TRIAGE 2026-07-03) |
| **Severidad** | P1 — produces `confidence > 1.0` and incorrect `NOISE` verdict |
| **Archivo** | `vigia_scorer.py` |
| **Función** | EPC / provenance trust scoring path |
| **Línea original** | 474 |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

The EPC trust computation reads `prior_trust` from the case JSON without validating
its range:

```python
# line 474 — CURRENT (no validation):
prov_trust = a.get("prior_trust", 1.0)
```

`prior_trust` is intended to be a trust coefficient in `[0.0, 1.0]`. There is no
clamp and no rejection. Any value from the case JSON is accepted as-is.

**Failure cascade when `prior_trust < 0`:**

```
prov_trust = -0.5                              # from case JSON, unchecked
effective = prov_trust × epc_factor × temp_factor
          = -0.5 × Fraction(19,20) × 1.0
          = -0.475                             # negative

mean_effective = sum(effectives) / len(...)   # still negative if all are negative

# provenance_collapsed branch triggers (mean_effective < 0.01):
verdict    = "NOISE"
confidence = _dround(1.0 - mean_effective, 2)
           = _dround(1.0 - (-0.475), 2)
           = _dround(1.475, 2)
           = 1.48                              # confidence > 1.0 — impossible state
```

Two simultaneous violations are produced:
1. **Wrong verdict:** `NOISE` is emitted because the collapsed-provenance branch fires,
   but the actual situation is invalid input — not a clean provenance chain.
2. **Confidence outside `[0, 1]`:** `1.48` is not a valid probability. Any downstream
   consumer that validates `confidence ∈ [0, 1]` will fail; any that does not will
   silently propagate an impossible value into the sealed bundle.

The same logic applies to `prior_trust > 1.0`, which produces `effective > epc_factor`
— meaning the chain-of-custody penalty is overridden by a supra-unity trust value,
which has no forensic meaning.

### Impacto forense

- A sealed bundle with `confidence = 1.48` is facially invalid and indefensible under
  cross-examination. The filed report would contain a number that is mathematically
  impossible for a probability value. This is a Daubert red flag: it suggests the
  pipeline did not validate its own inputs, which undermines the reliability prong.
- A sealed bundle with `verdict = NOISE` and `confidence = 1.48` makes two contradictory
  claims: "no anomaly detected" (the verdict) and "148% certainty" (the confidence).
  A court-appointed reviewer would immediately identify this as a pipeline error.
- The vulnerability requires no special privilege: any caller that controls the case
  JSON can inject an out-of-range `prior_trust` and produce a deterministically
  incorrect sealed bundle, without triggering any error or log entry.

### Fix pendiente

Two design options — a decision is needed before patching:

**Option A — Clamp silently (soft boundary):**
```python
prov_trust = max(0.0, min(1.0, a.get("prior_trust", 1.0)))
```
Keeps the pipeline running. Masks bad input without alerting the caller.
Risk: a misconfigured case JSON silently produces a different result than intended.
Not preferred under Daubert (fail-quiet).

**Option B — Reject with ValueError (fail-loud, Daubert-preferred):**
```python
prov_trust = a.get("prior_trust", 1.0)
if not (0.0 <= prov_trust <= 1.0):
    raise ValueError(
        f"prior_trust out of range: {prov_trust!r}. "
        f"Expected a value in [0.0, 1.0]. "
        f"Check the case JSON for artifact {a.get('artifact_id', '?')}."
    )
```
Halts the pipeline on invalid input. The bundle is never sealed with an impossible
state. Consistent with the fail-loud principle applied in B-023 (`_apply_quadripartite`).

The Daubert principle favors Option B: a pipeline that halts on invalid input is more
forensically defensible than one that silently produces a wrong answer. Implement
Option B at line 474 before the trust computation begins.

### Cierre (2026-07-03, Tanda A — A2)

Clamp con el mismo Finite Math Shield que `raw_score` dos líneas arriba:
no-numérico/NaN/inf → 1.0 (default neutro); después `max(0, min(1, v))`.
Aplicado en el scorer VIVO (`vigia_scorer.py:478`, raíz) y también en la
copia `vigia/core/vigia_scorer.py`. **Hallazgo colateral T-6 (nuevo,
B-055):** la copia `vigia/core/vigia_scorer.py` está stale y divergente —
referencia `_EPC_FACTOR_TABLE` sin definirla (NameError latente en
`_vigia_score` para toda cadena no-BROKEN) y ya estaba flaggeada como "stale
and unused" por el patch r7 (2026-06-19). Ver B-055.
Tests: `TestA2PriorTrustClamp` (9) — negativos, NaN, ±inf, string, None,
clamp >1, y control de que valores válidos no cambian.

---

## B-027 — `is_conclusive=True` semantically incompatible with `ABSTAIN_DETECTED` [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda A (TRIAGE 2026-07-03) |
| **Severidad** | P1 — semantic contradiction in sealed bundle |
| **Archivo** | `sift_orchestrator.py` |
| **Función** | EBS path (line 195) and vol3 path (line 340) |
| **Líneas originales** | 195, 340 |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

`is_conclusive` is set purely by comparing the average score against a threshold,
without considering the verdict:

```python
# EBS path (line 195):
is_conclusive = avg > Fraction(33, 100)

# vol3 path (line 340):
is_conclusive = avg > Fraction(3, 2)
```

Neither path checks whether `best_hypothesis == "ABSTAIN_DETECTED"`. If
`expected_verdict = "ABSTAIN"` but the average score happens to exceed the
threshold (e.g., because individual artifact scores were high despite the case
being classified as ABSTAIN for evidentiary reasons), the bundle seals with:

```json
{
  "best_hypothesis": "ABSTAIN_DETECTED",
  "is_conclusive": true
}
```

These two fields are mutually exclusive by definition:

- `ABSTAIN_DETECTED` means "the system has insufficient epistemic basis to reach
  a verdict." It is the explicit declaration that the analysis is inconclusive.
- `is_conclusive = True` means "the system reached a certain conclusion."

Sealing both simultaneously is a logical contradiction. Under cross-examination,
the expert would be unable to explain why the system declared both "I am certain"
and "I cannot form an opinion" in the same bundle.

### Impacto forense

A Daubert challenge to a bundle containing `is_conclusive=True` and
`best_hypothesis=ABSTAIN_DETECTED` would immediately succeed: the bundle is
self-refuting. No methodology that produces contradictory output about its own
certainty can satisfy the Daubert reliability prong. This is more damaging than a
wrong verdict — it is evidence that the pipeline lacks internal consistency.

### Fix pendiente

Force `is_conclusive = False` whenever `hypothesis == "ABSTAIN_DETECTED"`,
regardless of the average score:

```python
# EBS path:
is_conclusive = avg > Fraction(33, 100) and hypothesis != "ABSTAIN_DETECTED"

# vol3 path:
is_conclusive = avg > Fraction(3, 2) and hypothesis != "ABSTAIN_DETECTED"
```

Alternatively, compute `is_conclusive` after `hypothesis` is determined and apply
the gate there. Either formulation prevents the contradiction. The fix is one line
per path.

### Cierre (2026-07-03, Tanda A — A3)

1. Adaptador EBS (`sift_orchestrator.py`, shim): `is_conclusive` ahora exige
   además `"ABSTAIN" not in hypothesis and "UNDETERMINED" not in hypothesis`.
   (Las líneas citadas originalmente, 195/340, hoy son ~606/794 — T-5.)
2. Path vol3: anotado (su escalera de hipótesis nunca produce ABSTAIN; los
   paths UNANALYZED/FORMAT_NOT_SUPPORTED ya emitían False explícito).
3. Guard central en `vigia_agent._seal_bundle`: cualquier camino futuro que
   selle veredicto ABSTAIN con `is_conclusive=True` se degrada a False con
   anotación `is_conclusive_downgraded` — cierra la clase entera.
Tests: `TestA3IsConclusiveCoherent` (3), incluye control de que MALICE
conclusivo legítimo no se degrada.

---

## B-028 — `is_conclusive=True` silently ignored for all verdicts except `MALICE` [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda B opción A (aprobada 2026-07-03) |
| **Severidad** | P2 — flag has no observable effect outside MALICE path |
| **Archivo** | `vigia_agent.py` |
| **Función** | Post-scoring agent action dispatch |
| **Línea original** | 737 |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28 |

### Descripción

The agent only acts on `is_conclusive` when the hypothesis contains the substring
`"MALICI"`:

```python
# vigia_agent.py line 737:
if _is_conclusive and "MALICI" in _hypothesis.upper():
    # ... escalation / high-confidence MALICE action path
```

For any other hypothesis — `SUSPICION_DETECTED`, `NO_SEMIOTIC_ANOMALY_DETECTED`,
`ABSTAIN_DETECTED` — `is_conclusive=True` has no effect on agent behavior. The flag
is written into the bundle but never consumed by the dispatch logic. A conclusive
`SUSPICION` case is handled identically to an inconclusive `SUSPICION` case.

This means `is_conclusive` is currently a MALICE-only flag with a misleading name.
Its name and the code that sets it (see B-027) imply general applicability, but its
consumption is silently restricted to a single verdict branch.

### Impacto forense

- The flag misleads any downstream consumer (SANS judges, audit tools, court exhibits)
  that reads `is_conclusive=True` for a SUSPICION or NOISE bundle and expects it to
  carry operational meaning. It does not.
- If the intent was always MALICE-only, the flag name is incorrect and its presence
  in non-MALICE bundles adds noise to the sealed record without informational value.
- Combined with B-027: a bundle can simultaneously claim `is_conclusive=True`,
  `best_hypothesis=ABSTAIN_DETECTED`, and trigger zero agent action — a three-way
  inconsistency.

### Decisión requerida

Two options, both valid depending on intent:

**Option A — Extend `is_conclusive` to other verdicts:**
Define what "conclusive" means for SUSPICION, NOISE, and ABSTAIN, and implement
the corresponding dispatch branches in `vigia_agent.py`. This requires a design
decision for each verdict: what action, if any, should a conclusive SUSPICION
trigger that an inconclusive SUSPICION should not?

**Option B — Rename and restrict the flag to MALICE only:**
Rename `is_conclusive` to `is_conclusive_malice` (or `high_confidence_malice`)
in both the orchestrator and the agent. Set it only in the MALICE branch. Remove
it from SUSPICION, NOISE, and ABSTAIN bundles entirely. Update all callers.

Option B is lower risk and more honest about the current behavior. Option A is
more architecturally complete but requires non-trivial design work per verdict.
Document the decision in the orchestrator before implementing either option.

### Cierre (Tanda B, opción A — aprobada por Anna)

Semántica definida y documentada (docstring de `classify_agent_verdict`):
el flag modula (1) el gate de corroboración <3 primarias y (2) el piso del
nivel de alerta — MALICE conclusivo (existente) e INTENT conclusivo (nuevo:
LOW → MEDIUM, "a conclusive intent finding cannot present as LOW"); es
informativo para NOISE/SUSPICION; incompatible con ABSTAIN (guard B-027).
Sin flips de veredicto/exit code: el alert no alimenta classify.
Tests: `TestB028IntentAlertFloor` (3).

---

## AUDITORÍA DE SESIÓN — Epistemic State Fuzzing (2026-06-28, día 14 post-hackathon)

This section documents the audit methodology applied in the 2026-06-28 session so
that future sessions do not re-audit already-covered ground. It is an epistemic
record, not a bug report. Each technique below is tagged with the bugs it found
(if any) or confirmed as clear.

### Técnicas aplicadas

**1. Epistemic state coverage**
Verified that all verdict states (MALICE, SUSPICION, NOISE, ABSTAIN, UNKNOWN,
INTENT, BENIGN) exist consistently across every mapper in the pipeline:
`sift_orchestrator.py`, `run_all_agent.py`, `run_llm_cases.py`, `vigia_scorer.py`,
`decision_layer.py`. Found and fixed: B-020 (ABSTAIN collapsed to NOISE), B-021
(vol3 path binary MALICE/SUSPICION with no middle branch), B-022 (ABSTAIN→UNKNOWN
alias in accuracy comparator).

**2. Asymmetry search**
Searched for states that appear in one module and disappear two modules later
without explicit handling. Found: B-021, B-022, B-023.

**3. Dangerous defaults**
Audited all `.get("verdict", X)` and `.get(key, fallback)` patterns in the scoring
path. Found: B-023 (`_VERDICT_TO_RAW.get` with silent ABSTAIN fallback — replaced
with fail-loud `ValueError`).

**4. Duplicate constants**
Searched for float literals 0.95, 0.8, 0.75, 0.1, and the ratio 19/20 in the
scoring path. Found: B-024 (`epc_factor = 0.1` float in the BROKEN chain branch —
replaced with `Fraction(1, 10)`).

**5. Round-trip testing**
Verified `build_bundle` vs `load_bundle` symmetry. Finding: no canonical
`load_bundle` function exists. `extract_verdict_from_bundle` recovers only the
verdict string. `load_and_verify` only checks integrity. Full state reconstruction
from a sealed bundle is not supported. Documented as an architectural limitation;
no patch was applied.

**6. Mathematical invariants**
Verified the invariant `effective ≤ prior_trust`. CONFIRMED: `epc_factor ∈ (0,1]`,
`temp_factor = exp(-2x) ∈ (0.135, 1]` — invariant holds in the normal path.
Found: B-026 (`prior_trust` not validated at the input boundary — negative values
break the invariant and produce `confidence > 1.0`).

**7. Impossible states**
Searched for semantically contradictory field combinations in sealed bundles. Found:
B-027 (`is_conclusive=True` + `best_hypothesis=ABSTAIN_DETECTED`), B-028
(`is_conclusive` silently ignored for all non-MALICE hypotheses).

**8. Bare `except` / `except Exception` audit**
Audited all broad exception handlers in the primary files:
- `vigia_agent.py` — 1 handler found; assessed as acceptable conservative fallback.
- `vigia_scorer.py` — 5 handlers found; pending individual review.
- `sift_orchestrator.py` — 4 handlers found; pending individual review.

### Archivos cubiertos (no re-auditar sin cambios nuevos)

| Archivo | Técnicas aplicadas | Resultado |
|---------|--------------------|-----------|
| `sift_orchestrator.py` | 1, 2, 7, 8 — states, defaults, `is_conclusive`, vol3 path | B-021, B-027, B-028 |
| `run_all_agent.py` | 1, 2 — mappers, aliases, comparator | B-022 |
| `run_llm_cases.py` | 1 — `_HYP_MAP`, equivalence sets | B-020 (partial) |
| `vigia_scorer.py` | 3, 4, 6 — EPC path, `_VERDICT_TO_RAW`, `prior_trust`, `_dround` boundary | B-023, B-024, B-025, B-026 |
| `vigia_agent.py` | 7, 8 — `is_conclusive` handling, exception handlers | B-028 |
| `vigia/core/decision_layer.py` | 1 — verdict emission | Clear |

### Pendiente (no auditado en esta sesión)

- `caie.py` — `except Exception` handlers (quantity and scope unknown)
- `pipeline.py` — `except Exception` handlers
- `vigia/inference/abductive_reasoner.py` — `is_conclusive` emission site
- `quadripartite.py` — state space coverage
- `bundle_builder.py` — round-trip completeness
- All report generators — verdict state propagation to output fields

### Bugs encontrados en esta sesión

B-019 a B-028. Ver entradas individuales en este archivo para descripción completa,
impacto forense Daubert, y estado del fix.

### Próximos objetivos de auditoría

- `except Exception` en `vigia_scorer.py` líneas 228, 370, 429, 444, 502
- `except Exception` en `sift_orchestrator.py` líneas 36, 65, 101, 374
- Handlers en `caie.py`
- Cobertura de espacio de estados en `quadripartite.py`
- Propagación de estados en los generadores de reporte

---

## B-029 — `quadripartite.py` Check 3 `else` branch is dead code (`ABSTAIN_CONTRADICTION` unreachable for non-OSCIL reasons) [CERRADO]

| Campo | Valor |
|-------|-------|
| **Estado** | CERRADO — 2026-07-03 (la propia entrada declara: documentation only, no patch needed) |
| **Severidad** | P3 — dead code, no functional impact |
| **Archivo** | `vigia/verdict/quadripartite.py` |
| **Función** | `classify()` — Check 3 ABSTAIN branch |
| **Líneas originales** | 297–303 |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28, `quadripartite.py` state space audit |

### Descripción

The ABSTAIN branch in `classify()` (Check 3) has the following structure:

```python
if abstain_reason and "OSCIL" in abstain_reason.upper():
    state = ABSTAIN_CONTRADICTION      # oscillation detected
elif confidence < MEDIUM_CONFIDENCE_THRESHOLD:
    state = ABSTAIN_INSUFFICIENT       # low confidence
else:
    state = ABSTAIN_INSUFFICIENT       # ← identical to elif — dead code
```

The `else` branch is unreachable in any meaningful sense: it produces the same state
(`ABSTAIN_INSUFFICIENT`) as the `elif` branch. The only difference between the two
paths is the `confidence` check, which is now irrelevant because both outcomes are
identical. Any ABSTAIN case with a non-oscillation `abstain_reason` and confidence at
or above `MEDIUM_CONFIDENCE_THRESHOLD` falls through to the dead `else` and receives
`ABSTAIN_INSUFFICIENT` — indistinguishable from the low-confidence path.

The three ABSTAIN sub-states defined by the quadripartite model:
- `ABSTAIN_DEGRADED` — handled by Check 1 before this point (provenance collapse).
- `ABSTAIN_CONTRADICTION` — only reachable when `"OSCIL" in abstain_reason.upper()`.
- `ABSTAIN_INSUFFICIENT` — reachable via `elif` (low confidence) and via the dead
  `else` (non-oscillation reason with sufficient confidence — currently a no-op).

### Impacto forense

No functional impact: `ABSTAIN_INSUFFICIENT` is the correct fallback for cases where
the reason for abstention is not oscillation and confidence is insufficient. The dead
`else` does not produce an incorrect result — it just makes the `elif` condition
meaningless because the `else` duplicates it.

The concern is investigative rather than operational: the dead `else` masks whether
`ABSTAIN_CONTRADICTION` was intended to be reachable for non-oscillation contradiction
reasons. If there are other types of contradiction (e.g., log-vs-memory fracture
producing an irresolvable split) that should produce `ABSTAIN_CONTRADICTION` but
currently map to `ABSTAIN_INSUFFICIENT` because they do not contain `"OSCIL"` in their
reason string, the distinction is silently lost.

### Investigación pendiente

Before treating this as documentation-only:

1. Review the full list of `abstain_reason` strings that can be emitted upstream
   (in `sift_orchestrator.py`, `abductive_reasoner.py`, and any CAIE path that sets
   `abstain_reason`). Determine whether any non-oscillation reason represents a
   logical contradiction rather than mere insufficiency.
2. If yes: the `"OSCIL"` check should be broadened to a set of contradiction-type
   reasons, or replaced with a structured enum rather than a substring match.
3. If no: the dead `else` should be removed and the condition simplified to:
   ```python
   if abstain_reason and "OSCIL" in abstain_reason.upper():
       state = ABSTAIN_CONTRADICTION
   else:
       state = ABSTAIN_INSUFFICIENT
   ```
   This eliminates the misleading `elif` and makes the control flow honest.

---

## B-030 — `quadripartite.py` unrecognized `raw_verdict` falls through to fallback (INVESTIGATED — NOT A BUG)

| Campo | Valor |
|-------|-------|
| **Estado** | CERRADO — investigated and dismissed |
| **Severidad** | N/A |
| **Archivo** | `vigia/verdict/quadripartite.py` |
| **Función** | `classify()` — fallback path |
| **Línea original** | 397 |
| **Commit fix** | — |
| **Detectado en** | Sesión post-hackathon 2026-06-28, `quadripartite.py` state space audit |

### Descripción

**Investigation summary:** if `raw_verdict` is not one of the recognized values
(`"MALICE"`, `"BENIGN"`, `"ABSTAIN"`), all six checks in `classify()` are bypassed
and the fallback at line 397 emits `ABSTAIN_INSUFFICIENT` with
`abstain_reason="Unrecognized raw verdict: '{raw_verdict}'"`.

**Finding:** this is correct behavior — fail-loud and self-documenting. The fallback
does not silently map to a forensically meaningful verdict; it produces an explicit
ABSTAIN with a diagnostic message that names the unrecognized input. Under
cross-examination, the bundle is fully explainable: "the input verdict was not
recognized; the system correctly abstained and recorded the reason."

**Layered defense confirmed:** B-023 (`_apply_quadripartite` now raises `ValueError`
for any unrecognized verdict string before calling `quadripartite.classify()`) means
the fallback at line 397 is unreachable in the production path for any
correctly-typed input. The unrecognized-verdict case is intercepted before it reaches
`quadripartite.py`. The two layers are independent and complementary:
- Layer 1 (B-023): `ValueError` at the scorer boundary — prevents sealed bundles
  from being produced with an unknown verdict type.
- Layer 2 (line 397): explicit `ABSTAIN_INSUFFICIENT` fallback — defensive last resort
  if quadripartite is ever called directly with novel input.

**Also investigated:** the string `"OSCILLATION_MITIGATED"` appears in the audit
trail `action` field during oscillation resolution, but does **not** propagate to
`abstain_reason`. Only terminal oscillation — where the resolution strategy fails and
`termination_reason="OSCILLATION_DETECTED"` — produces the `forensic_verdict` string
that is passed as `abstain_reason` to `quadripartite.classify()`. The `"OSCIL"` check
in Check 3 (B-029) correctly targets only that terminal state. There is no case where
`"OSCILLATION_MITIGATED"` reaches `abstain_reason` and accidentally triggers
`ABSTAIN_CONTRADICTION`.

### Conclusión

Not a bug. Dismissed. The fallback is correct, the layered defense is sound, and the
oscillation string routing is non-contradictory. No action required.

---

## Bugs de Sesión 2026-06-29 — Windows Disk Evidence & RAW Mode

### B-031 [FIXED] — `provenance_chain` mal tipado (string/dict) producía `len()` incorrecto en el factor EPC [entrada retrospectiva 2026-07-23]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — el shield existe en `vigia_scorer.py` y está cubierto por `tests/test_r4_boundaries.py` |
| **Archivo** | `vigia_scorer.py` (bloque `effective_trusts`, comentario `# B-031`) |
| **Detectado en** | Banda 2026-06-29 (evolución citada en `docs/PROPUESTA_TANDA_B.md` y `docs/REDTEAM_ROUND4_BOUNDARIES.md`) |

**Nota de proveniencia:** entrada RECONSTRUIDA el 2026-07-23 por el contrato
de integridad referencial (`tests/test_registry_integrity.py`): el ID se
citaba en cinco superficies (código de producción, dos dossiers, ambos
registros) pero nunca tuvo entrada propia. Fuentes de esta reconstrucción:
el comentario en código, la tabla de REDTEAM_ROUND4 ("`provenance_chain` =
'str' → NOISE, no crash — B-031 retypes non-list chain → []") y el test R4
que lo ejercita. No se reconstruyó lo que las fuentes no respaldan (fecha
exacta del fix, commit).

**Descripción:** un `provenance_chain` que llegaba como string o dict (en
vez de list) producía un `len()` semánticamente incorrecto en el cómputo
del factor EPC — `len("abc")==3` contaba caracteres como si fueran eslabones
de custodia. Fix: coerción `isinstance(list)`; un no-list cae a `[]`, que
aterriza en el path `chain_status BROKEN` (EPC 1/10, conservador).

---

### B-032 [FIXED] — vigia_agent.py mapped *.evtx to event_stream kwarg instead of event_logs

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia_agent.py` |
| **Función** | `_build_orchestrator_kwargs()` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `_build_orchestrator_kwargs()` mapped `.evtx` files to the `event_stream` parameter, but `SIFTOrchestrator.analyze()` routes `event_stream` to `MetabolicProfiler`, not to `EventLogCorrelator`. The correct parameter is `event_logs`. Result: `EventLogCorrelator` received no input and produced `z=0`, while the actual composite score from direct invocation was 19/20.

---

### B-033 [FIXED] — Agent did not auto-detect registry hives (SAM/SYSTEM/SOFTWARE/SECURITY)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia_agent.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** The autonomous agent did not auto-detect registry hive files (SAM, SYSTEM, SOFTWARE, SECURITY) when scanning evidence directories. These files lack extensions and were not matched by any glob pattern in the evidence scanner.

---

### B-034 [FIXED] — ChainOfCustody.acquire() missing notes kwarg in registry_timeline_reconstructor

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/sift/registry_timeline_reconstructor.py` |
| **Función** | `ChainOfCustody.acquire()` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `ChainOfCustody.acquire()` was called without the `notes` keyword argument required by the method signature, producing a `TypeError` on every registry hive acquisition.

---

### B-035 [FIXED] — forensic_adapter mapped event_log to log_entry (syslog generic) instead of windows_event_log

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/sift/forensic_adapter.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `forensic_adapter.py` mapped `event_log` to `log_entry` (syslog generic, `spoofability=0.85`). Windows EVTX is a binary format with checksums, much harder to tamper. Fix: Added `windows_event_log` to forensic_adapter mapping, CAIE profiles, and gamma tables. See L-033b, L-035.

---

### B-036 [FIXED] — z>5.0 threshold impossible in vigia_agent.py fallback hypothesis (Z_CLIP_MAX=5.0)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia_agent.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** The fallback hypothesis override in `vigia_agent.py` required `z>5.0` to trigger, but `Z_CLIP_MAX=5.0` clips all signals at 5.0. The threshold was impossible to reach. Fixed to `z>2.0`. See L-036.

---

### B-037 [FIXED] — EBS v1 adapter missing INTENT/BENIGN hypothesis mapping in sift_orchestrator.py

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `sift_orchestrator.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** The EBS v1 adapter in `sift_orchestrator.py` did not have mappings for `INTENT` and `BENIGN` hypothesis types. Cases producing these hypotheses would fall through to the default handler and produce incorrect bundle metadata.

---

### B-038 [FIXED] — composite_score not included in event_log signal metadata

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | Event log signal emission path |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `composite_score` was not included in event_log signal metadata. This field is required by `apply_artifact_reliability_dynamic()` (L-038) to compute dynamic gamma based on corroboration strength.

---

### B-039 [FIXED] — windows_event_log type missing from gamma tables in _math_utils.py

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/sift/_math_utils.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** The `windows_event_log` artifact type was not present in the gamma lookup tables in `_math_utils.py`. Signals of this type would fall through to the default gamma value instead of using the calibrated `gamma=0.70`.

---

### B-040 [RESUELTO] — ARTIFACT_RELIABILITY not propagated to CAIE

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — subsumido por L-037b (Tanda B PR-B2, 2026-07-03); cierre verificado en tracker 2026-07-05 (Fase 0, hallazgo S-4) |
| **Severidad** | P2 |
| **Archivo** | `vigia/sift/forensic_adapter.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `ios_forensics.py` and `android_forensics.py` define `ARTIFACT_RELIABILITY=Fraction(70,100)` but `forensic_adapter.py` sets `base_trust=1.0` fixed, ignoring the signal metadata value. See L-037.

**Resolución (verificada contra código vivo 2026-07-05):** el fix de L-037b
cubre exactamente este bug — `forensic_adapter.py:179-193` lee
`metadata["artifact_reliability"]` (Fraction-string), lo clampa a [0,1] con
fallback 1.0 y lo propaga como `base_trust` a CAIE. Los tres motores lo
emiten: `ios_forensics.py:216`, `android_forensics.py:193`,
`macos_forensics.py:220`. Tests:
`tests/test_tanda_b.py::TestL037bBaseTrustPropagation` (4). La entrada quedó
estanca porque el fix se registró bajo L-037b sin cerrar B-040.

---

### B-041 [SUPERSEDIDO — ver diagnóstico corregido más abajo] — caie_artifacts no retornado por run_full_analysis() — CAIE nunca corre en modo RAW

| Campo | Valor |
|-------|-------|
| **Estado** | SUPERSEDIDO — este diagnóstico original estaba EQUIVOCADO. La auditoría de seguimiento (2026-06-30, adyacente a `docs/AUDITORIA_PIPELINE_ROBUSTEZ.md`) encontró que CAIE SÍ corre dentro de `sift_orchestrator.py` y SÍ se retorna en `results["caie"]`. Ver la entrada corregida "B-041 — CAIE output no expuesto en vigia_agent.py narrative [PARTIAL FIX]" más abajo en este archivo para los bugs reales (B-041a, resuelto; B-041b, diferido — rastreado en la tabla resumen y en `KNOWN_LIMITATIONS.md`). Se deja en su lugar, no se borra, siguiendo la convención de auditabilidad de este tracker — un ID duplicado que quedó como `[PENDIENTE]` junto a su propia corrección es en sí mismo un defecto documental que merece rastro visible. |
| **Severidad** | P1 (como se archivó originalmente — ver la entrada corregida para la severidad real desagregada) |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción original (incorrecta):** `run_full_analysis()` no retornaba `caie_artifacts` en su salida, por lo que el motor de análisis cross-artifact CAIE nunca recibía artefactos al procesar evidencia RAW. Esto implicaría que la detección de fracturas estructurales (LOG_VS_MEMORY, TIMELINE_PARADOX, etc.) se saltea en modo RAW. **Esta premisa fue refutada por la auditoría de seguimiento** — no actuar sobre ella.

---

### B-042 [RESUELTO — borde cosmético, determinismo probado] — iOS forensics to_signal() float boundary

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04). El borde float NO está en el decision path. |
| **Severidad** | ~~P0~~ → cosmético (el float es el contrato de transporte de `SignalOutput`, no una fuga de determinismo) |
| **Archivo** | `vigia/sift/ios_forensics.py` |
| **Detectado en** | Sesión 2026-06-29; zanjado con test de determinismo 2026-07-04 |
| **Tag de restauración** | `pre-p1-mobile-verdict-20260704-022839` |

**Resolución (ENGINEERING_DISCIPLINE §5.2 "provalo"):** se escribió el test de
determinismo ANTES de tocar código (`tests/test_b042_b043_mobile_determinism.py`).
El decision path del veredicto mobile es el `z_score`; `sift_orchestrator.
_mobile_hypothesis` lo reconstruye con `Fraction(str(z_score))`. El test prueba
(10/10 pass) que:
- `z_score` es siempre un múltiplo limpio de 1/10 → `Fraction(str(float(z)))` es
  **identidad exacta** (round-trip lossless): el decisor recupera la Fraction
  interna sin pérdida.
- `value` (múltiplo de 1/50) también round-trip exacto.
- Dos llamadas a `to_signal()` → bytes idénticos.
- **Proceso fresco con `PYTHONHASHSEED` distinto (0/1/42) → z_score/value
  idénticos** (sin leak de orden de set/dict).

Conclusión: `float(z)` es el borde de transporte del contrato `SignalOutput`
(cuyos campos son float por diseño), y el decisor re-parsea a Fraction sin
pérdida. NO es una violación de L-021 en el decision path. `confidence` sí tiene
un borde float potencialmente lossy (composite × 11/10), pero `confidence` es
metadata — NO entra a `_mobile_hypothesis`. Sin cambio de código; el test queda
como regresión permanente del invariante.

**Refuerzo de cobertura (2026-07-04, tras red-team):** el test original tocaba
5 de ~11 salidas del ladder. Se agregó `TestLadderDomainExhaustive` (invariante
para TODO múltiplo de 1/10 en [0, Z_CLIP_MAX], superset de lo emitible) +
`TestLadderCoverage` (grid combinatorio: iOS 18 / Android 19 / macOS 22 valores
z distintos, incl. las ramas altas). 14 tests. Sigue sin cambio de código.

---

### B-043 [RESUELTO — borde cosmético] — Android (y macOS) forensics to_signal() float boundary

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04). Igual que B-042. |
| **Severidad** | ~~P0~~ → cosmético |
| **Archivo** | `vigia/sift/android_forensics.py` (y `macos_forensics.py`, misma forma) |

**Resolución:** el mismo test de determinismo cubre los tres módulos
(`android`/`ios`/`macos` parametrizados). 10/10 pass: el borde `float(z)` es
lossless para el decision path en los tres. Ver B-042 para el detalle.

---

### B-044 [FIXED] — `_build_orchestrator_kwargs()` ignora archivos .pcap — NetworkForensicsEngine nunca recibe datos

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-06-30 |
| **Severidad** | P1 |
| **Archivos** | `vigia/sift/pcap_parser.py` (nuevo), `sift_orchestrator.py`, `vigia_agent.py` |
| **Detectado en** | Sesión 2026-06-30 |

**Descripción:** `_build_orchestrator_kwargs()` en `vigia_agent.py` no detectaba archivos `.pcap` ni `.pcapng`. No existía ningún parser de pcap crudo en el repositorio. `NetworkForensicsEngine.analyze()` esperaba `List[NetworkFlow]` pero nunca recibía datos reales — solo podía activarse si un caller externo construía manualmente los objetos `NetworkFlow`.

**Caso de prueba:** `evidence/flare-on/flareon4/12/20170801_1300_filtered.pcap` — beaconing C2 confirmado (7220 paquetes hacia AWS 52.0.104.200), generaba 0 señales, exit code 0.

**Fix aplicado:**
1. Creado `vigia/sift/pcap_parser.py` — parser tshark (`-T json`) → `List[NetworkFlow]`, con cap de seguridad de 50000 paquetes y fail-loud en errores de tshark.
2. En `sift_orchestrator.py` (shim) — cuando recibe `pcap_path`, parsea el pcap con `parse_pcap_to_flows()` y pasa los flows como `network_flows` al `run_full_analysis()` real.
3. En `vigia_agent.py` `_build_orchestrator_kwargs()` — agregado `("*.pcap", "pcap_path")` y `("*.pcapng", "pcap_path")` a la lista de patrones de detección de directorio, y caso `elif suffix in (".pcap", ".pcapng")` para archivo único.

**Resultado post-fix:** NETWORK_FORENSICS emite señal con z=2.625, conf=0.95, 7220 flows, EXFILTRATION detectada.

---

## Sesión de Auditoría — Epistemic State Fuzzing (2026-06-28, día 14 post-hackathon)

Esta sección documenta la metodología aplicada en la sesión de auditoría del 2026-06-28.
Su propósito es evitar que sesiones futuras cubran el mismo terreno. Cada técnica está
etiquetada con los bugs que encontró (si los hay) o marcada como limpia. Para los detalles
completos de cada bug, consultar la entrada B-NNN correspondiente más arriba.

### Técnicas Aplicadas

**1. Cobertura de estados epistémicos**

Se verificó que todos los estados de veredicto — MALICE, SUSPICION, NOISE, ABSTAIN, UNKNOWN,
INTENT, BENIGN — existan de forma consistente en cada mapper y traductor del pipeline:
`sift_orchestrator.py`, `run_all_agent.py`, `run_llm_cases.py`,
`vigia_scorer.py`, `decision_layer.py`.

Bugs encontrados: B-020 (ABSTAIN colapsado a NOISE en tres componentes del pipeline), B-021
(la ruta vol3 tenía una decisión binaria MALICE/SUSPICION sin rama intermedia para cero
señales), B-022 (ABSTAIN aliasado a UNKNOWN en el diccionario del comparador de accuracy).

**2. Búsqueda de asimetrías**

Se trazó cada estado de veredicto desde su punto de emisión hasta su punto de consumo,
señalando estados que aparecen en un módulo y son descartados silenciosamente dos módulos
después sin un handler explícito ni un error.

Bugs encontrados: B-021 (caso de cero señales descartado), B-022 (ABSTAIN descartado en el
comparador), B-023 (cadena de veredicto no reconocida descartada en `_VERDICT_TO_RAW`).

**3. Defaults peligrosos**

Se auditaron todos los patrones `.get(key, fallback)` en la ruta de scoring, específicamente
aquellos donde el fallback es una cadena de veredicto o una constante semánticamente
significativa. Premisa: un fallback silencioso en una ruta de scoring forense convierte un
error de programación en un bundle sellado con el veredicto incorrecto, sin fallo visible.

Bugs encontrados: B-023 (`_VERDICT_TO_RAW.get(verdict, "ABSTAIN")` — ABSTAIN silencioso para
cualquier cadena de veredicto no reconocida; reemplazado con verificación explícita de
membresía + `ValueError`).

**4. Constantes duplicadas**

Se buscaron literales float 0.95, 0.8, 0.75, 0.1, y el patrón 19/20 en cualquier parte
de la ruta de scoring (`vigia_scorer.py`). Cada literal fue verificado contra la tabla de
lookup de `Fraction` correspondiente para detectar copias divergentes de la misma constante.

Bugs encontrados: B-024 (literal float `epc_factor = 0.1` en la rama de cadena BROKEN,
mientras la ruta normal usa `_EPC_FACTOR_TABLE[k]` que devuelve un `Fraction` — reemplazado
con `Fraction(1, 10)`).

**5. Prueba de round-trip**

Se verificó la simetría entre la construcción del bundle (`build_bundle`) y la carga del
bundle (`load_bundle` / `extract_verdict_from_bundle` / `load_and_verify`).

Hallazgo: no existe una función canónica `load_bundle`. `extract_verdict_from_bundle`
recupera solo la cadena del veredicto. `load_and_verify` verifica la integridad criptográfica
pero no reconstruye el estado de scoring. El round-trip completo (bundle sellado → estado
de scoring original) no está soportado. Documentado como limitación arquitectónica (no una
regresión); no se aplicó patch.

**6. Invariantes matemáticos**

Se verificó el invariante `effective ≤ prior_trust` en todas las rutas EPC. Confirmado:
`epc_factor ∈ (0, 1]` (de la tabla de lookup), `temp_factor = exp(-2x) ∈ (0.135, 1]`
— el invariante se mantiene bajo todas las entradas de la ruta normal.

Bugs encontrados: B-026 (`prior_trust` se lee del JSON del caso sin validación de rango
en la línea 474; un valor negativo rompe el invariante y se propaga a
`confidence > 1.0` en el bundle sellado).

**7. Estados imposibles**

Se buscaron combinaciones semánticamente contradictorias de campos en el mismo bundle
sellado — casos donde dos campos hacen afirmaciones mutuamente excluyentes sobre el
análisis.

Bugs encontrados: B-027 (`is_conclusive=True` co-ocurriendo con `best_hypothesis=ABSTAIN_DETECTED`
— certeza y abstención epistémica afirmadas simultáneamente), B-028 (`is_conclusive=True`
escrito en el bundle pero nunca consumido por el dispatch del agente para hipótesis
no-MALICE — el flag no tiene significado operacional fuera de MALICE).

**8. Auditoría de `except` desnudo / `except Exception`**

Se auditaron todos los handlers de excepciones amplios en los archivos principales de
scoring y orquestación. Los handlers amplios que absorben excepciones sin re-lanzar ni
registrar son un riesgo Daubert: convierten errores del pipeline en respuestas incorrectas
silenciosas.

Resultados:
- `vigia_agent.py` — 1 handler; evaluado como fallback conservador aceptable
  (captura errores de importación para módulos de enriquecimiento opcionales, registra, continúa).
- `vigia_scorer.py` — 5 handlers encontrados; revisión individual pendiente.
- `sift_orchestrator.py` — 4 handlers encontrados; revisión individual pendiente.

### Archivos Cubiertos — No Re-Auditar Sin Cambios Nuevos

| Archivo | Técnicas | Resultado |
|---------|----------|-----------|
| `sift_orchestrator.py` | 1, 2, 7, 8 — estados, defaults, `is_conclusive`, ruta vol3 | B-021, B-027, B-028 |
| `run_all_agent.py` | 1, 2 — mappers, aliases, comparador | B-022 |
| `run_llm_cases.py` | 1 — `_HYP_MAP`, conjuntos de equivalencia | B-020 (parcial) |
| `vigia_scorer.py` | 3, 4, 6 — ruta EPC, `_VERDICT_TO_RAW`, `prior_trust`, frontera `_dround` | B-023, B-024, B-025, B-026 |
| `vigia_agent.py` | 7, 8 — dispatch de `is_conclusive`, handlers de excepciones | B-028 |
| `vigia/core/decision_layer.py` | 1 — emisión de veredicto | Limpio |

Re-auditar cualquiera de los archivos anteriores solo está justificado si el archivo ha
cambiado desde esta sesión (verificar con `git log --since=2026-06-28 -- <archivo>`).

### No Auditados Aún en Esta Sesión

- `caie.py` — handlers `except Exception` (cantidad y alcance desconocidos)
- `pipeline.py` — handlers `except Exception`
- `vigia/inference/abductive_reasoner.py` — sitio de emisión de `is_conclusive`
- `quadripartite.py` — cobertura del espacio de estados
- `bundle_builder.py` — completitud de round-trip
- Todos los generadores de reportes — propagación de estados de veredicto a campos de salida final

### Bugs Encontrados en Esta Sesión

B-019 a B-028. Ver las entradas individuales más arriba para descripción, impacto Daubert,
fix propuesto o aplicado, y referencia de commit.

### Próximos Objetivos de Auditoría

- `except Exception` en `vigia_scorer.py` en las líneas 228, 370, 429, 444, 502
- `except Exception` en `sift_orchestrator.py` en las líneas 36, 65, 101, 374
- Handlers de excepciones en `caie.py`
- Cobertura del espacio de estados en `quadripartite.py`
- Propagación de estados de veredicto en todos los generadores de reportes

---

## L-037 — ForensicAdapter no propaga acquisition metadata a CAIE [FIXED]

**Fecha**: 2026-06-30
**Severidad**: Alta
**Componentes**: `vigia/sift/sift_orchestrator.py`, `sift_orchestrator.py` (shim), `vigia_agent.py`

### Síntoma
CAIE degrada `base_trust` de todos los artefactos a 0.10 (floor) en modo RAW.
Los SECURITY ALERTs reportaban 3 campos críticos ausentes (`acquisition_tool`,
`acquisition_hash`, `acquisition_timestamp`) y 2 warnings (`examiner_id`,
`write_blocker_used`) en CADA artefacto — trust residual ~0.10.

### Causa raíz
Ninguno de los 15 módulos SIFT que producen `SignalOutput` incluye acquisition
metadata en `signal.metadata`. `ForensicAdapter.signal_to_caie_artifact()` copia
`dict(sig.metadata)` completa — no filtra — pero si los campos nunca existen en
origen, CAIE no los encuentra. El dato no se pierde en propagación; nunca se genera.

### Fix aplicado
Inyección centralizada en `sift_orchestrator.py`, en el punto de convergencia gamma
(§4 del pipeline, donde todos los signals son re-empaquetados como `SignalOutput`
nuevo). Se construye `_acq_meta` una sola vez desde `self.chain.records[0]`:
- `acquisition_hash`: `sha256:{chain.records[0].artifact_hash}` (64 hex)
- `acquisition_timestamp`: `chain.records[0].timestamp` (ISO-8601+tz)

Merge order: `{_acq_meta, **sig.metadata, gamma_fields}` — signal's own metadata
nunca es sobreescrita (un signal que ya traiga `acquisition_hash` propio lo conserva).

`acquisition_tool`, `write_blocker_used`, `examiner_id` NO se sintetizan — deben
declararse explícitamente via CLI flags:
```
--acquisition-tool "ftk imager"
--write-blocker-used true
--examiner-id "Craig Wilson"
```
Sin flags, estos campos siguen ausentes → degradación honesta, no un bug oculto.

### Resultados (MAGNET-2020-WINDOWS)

| Métrica | Antes | Después | Cambio |
|---------|-------|---------|--------|
| Composite score | 0.0027 | **0.0088** | +226% |
| EVENT_LOG adjusted | 0.0014 | **0.0047** | +236% |
| REGISTRY_RTR adjusted | 0.0012 | **0.0041** | +242% |
| Critical campos ausentes (SIFT signals) | 3 | **1** | -67% |
| Warning campos ausentes | 2 | 2 | sin cambio |
| Gates CAIE pasados (SIFT signals) | 0/4 | **2/4** | VERIFIED tier |

Nota: la proyección inicial de trust 0.10→0.75 no se alcanzó porque
`trust_decay.apply_decay()` (línea 554 de caie.py) degrada trust por cadena de
proveniencia corta (single-link chain, break_severity=0.5) ANTES de la degradación
de acquisition metadata. Este trust_decay preexistente es comportamiento correcto
(no un bug) — documenta que la cadena de proveniencia tiene un solo eslabón.

### Archivos tocados
- `vigia/sift/sift_orchestrator.py` — inyección de `_acq_meta` en convergencia gamma
  + nuevo atributo `self.acquisition_overrides`
- `sift_orchestrator.py` (shim raíz) — propaga `acquisition_overrides` al orchestrator real
- `vigia_agent.py` — 3 CLI flags (`--acquisition-tool`, `--write-blocker-used`,
  `--examiner-id`), propagación via `VIGIAAgent.acquisition_overrides`

### Tests
188 passed, 6 xfailed, 0 regresiones.

---

## B-041 — CAIE output no expuesto en vigia_agent.py narrative [RESUELTO: B-041a aplicado; B-041b superado por B-075/B-076]

**Fecha**: 2026-06-30
**Severidad**: Media
**Componentes**: `vigia_agent.py`, `vigia/sift/sift_orchestrator.py`

### Diagnóstico original
Se reportó que `caie_artifacts` no era devuelto por `run_full_analysis()` y CAIE
nunca corría en modo RAW.

### Diagnóstico corregido (auditoría)
CAIE **sí corre** dentro de `sift_orchestrator.py` líneas 582-610. El resultado se
guarda en `results["caie"]` y se retorna en el dict. El bug real es:
- **B-041a**: `vigia_agent.py` nunca leía `results["results"]["caie"]` — las fracturas
  se computaban pero eran invisibles en el narrative y el bundle.
- **B-041b**: CAIE corre DESPUÉS de que abduction ya se computó — las fracturas nunca
  retroalimentan el veredicto.

### Fix aplicado (B-041a)
- **Archivo**: `vigia_agent.py`, método `_generate_narrative()`
- **Cambio**: Agregada sección `--- CAIE ---` al narrative que expone verdict, structural
  verdict, composite score, fractures (con tipo, severidad, golden rule / structural tags),
  y daubert note.
- **Impacto**: Fracturas CAIE ahora visibles en el bundle sellado para revisión humana.
- **Tests**: 188 passed, 6 xfailed, 0 regresiones.

### Upgrade automático INTENT→MALICE (B-041b) — DIFERIDO
Auditoría sobre MAGNET-2020-WINDOWS y MAGNET-2022-WINDOWS en modo RAW muestra que
CAIE produce INCONCLUSIVE con 0 fractures en ambos casos:
1. Todos los artefactos son `log_entry` (una sola capa) → 0 fractures cross-layer
2. `ForensicAdapter.signal_to_caie_artifact()` no inyecta metadata de adquisición →
   trust degradado de 0.45 a 0.10 por NIST SP 800-86 §4.3
3. CDL downgrade a INCONCLUSIVE por coverage 16.7% (1/6 capas)
4. Composite score 0.0027 (NOISE probabilístico)

**Conclusión (original, 2026-06-30)**: el upgrade automático sería dead code con la
metadata actual. Se requiere primero que `ForensicAdapter` propague acquisition
metadata desde los signals, y/o que el pipeline produzca artefactos de múltiples
capas epistémicas (memory_process, prefetch, kernel_structure además de log_entry).

### Re-verificación 2026-07-10 (método abductivo) — B-041b SUPERADO por B-075/B-076

El diagnóstico de B-041b se hizo contra el path VIEJO donde CAIE corría en
`sift_orchestrator.run_full_analysis` DESPUÉS de la abducción y su resultado
quedaba en `results["caie"]` sin retroalimentar el veredicto. B-075/B-076
(posteriores) hicieron del scorer label-blind `vigia_scorer._vigia_score` la
fuente autoritativa del veredicto, y ESE scorer **ya** acopla las fracturas al
veredicto pre-emisión. Separando capas (daubert):

- **OBSERVACIÓN (inducción reproducible, `tests/test_b041b_fracture_feedback.py`):**
  el scorer recomputa CAIE en vivo (B1, `vigia_scorer.py:611`) y aplica
  `fracture_malice_boost` (hasta +0.5) al composite en `vigia_scorer.py:1053`.
  Medido: par idéntico salvo una `TEMPORAL_CAUSALITY_VIOLATION` → control NOISE
  0.0701 / boost 0.0 vs fracturado SUSPICION 0.5058 / boost 0.45. Sobre una base
  ya corroborada (≥4 duros): score 0.7828 → **0.99** con la misma fractura. Las
  `MALICIOUS_FRACTURE_TYPES` (`vigia_scorer.py:956`) incluyen FALSE_FLAG_PATTERN,
  TCV, CRYPTOGRAPHIC_INCONSISTENCY, MFT_ENTRY_ANOMALY, USN_JOURNAL_GAP.
- **INFERENCIA:** el mecanismo que B-041b pedía existe, en forma mejor (continua,
  determinista, pre-emisión) que el upgrade discreto INTENT→MALICE propuesto.
- **REFUTACIÓN de "dead code":** sobre el corpus multi-capa real (NPS-2009,
  NGDC-001, NROMANOFF) CAIE emite **0 fracturas** — pero eso es correcto
  (ninguno tiene artefactos de fabricación), no mecanismo muerto: dispara sobre
  violaciones genuinas (inducción arriba). Ausencia-en-corpus ≠ mecanismo-roto.
- **B-041a** (CAIE visible en narrativa): aplicado (arriba). **B-041b** (fractura
  → veredicto): superado. B-041 se cierra; el `[PARTIAL FIX]` era stale.

Alcance no cubierto (posible follow-up, NO parte de B-041): la CAIE de
`sift_orchestrator` (narrativa) y la CAIE viva del scorer (veredicto) se
computan por separado — si divergieran, la narrativa podría exponer fracturas
que el veredicto no consumió (incongruencia clase N12). No verificado acá.

### Archivos tocados
- `vigia_agent.py` — `_generate_narrative()` (añadida lectura de CAIE) [B-041a]
- `tests/test_b041b_fracture_feedback.py` — pin de la clausura B-041b [2026-07-10]

---

## P0-001 — Pérdida de precisión en reconversión float→Fraction en boundary SIFT→Scorer [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | CORREGIDO — 2026-06-30 |
| **Severidad** | P0 — violación de invariante de determinismo |
| **Archivos** | `vigia/sift/sift_orchestrator.py:474`, `vigia/sift/unified_timeline_engine.py:99-101` |

### Descripción

Ver P0-001 en BUGS_PENDIENTES_EN.md para detalles completos. Resumen:
`Fraction(int(round(val * 100)), 100)` reemplazado por
`Fraction(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN))`.

Divergencia confirmada: `1.245` → viejo: `5/4`, nuevo: `31/25`.
Tests: 188 passed, 6 xfailed — idéntico al baseline.

---

## L-040 — likelihood_ratio.py opera en float, no Fraction [BAJA PRIORIDAD]

| Campo | Valor |
|-------|-------|
| **Estado** | ABIERTO — limitación documentada |
| **Severidad** | BAJA — sin impacto empírico en corpus actual |
| **Archivo** | `vigia/core/likelihood_ratio.py` |

### Descripción

`likelihood_ratio.py` consume `SignalOutput.z_score` y `.confidence` como `float` y
usa `math.exp`/`math.log` (operaciones IEEE 754). Viola literalmente el invariante
Fraction-only del CLAUDE.md para el path de veredicto.

**Evaluación empírica (2026-06-30):** 21 casos reales del corpus. 0 flips de veredicto,
delta = 0.0 en todos. Los z_scores del corpus actual son valores "limpios" donde float
y Decimal coinciden.

**Revisar si:** el corpus crece con casos cuyos z_scores caen cerca de umbrales de
decisión (posterior ~ 0.55 o 0.75) Y esos z_scores tienen representaciones IEEE 754
problemáticas.

### Actualización (2026-07-03, Tanda B — U7/U3 del mapa §4 de AUDITORIA_L040)

- **U7 cerrado (PR-B1):** `ForensicRecord.record_hash()` cuantiza los floats
  (Decimal 1e-6 ROUND_HALF_EVEN) antes de hashear — estable cross-arquitectura
  (bit 52 x86/ARM). El to_dict() de display no cambia.
- **U3 cerrado (PR-B2):** `trust_fusion.compute_temporal_trust_factor` usa la
  tabla precomputada `_EXP_NEG2_TABLE` (buckets 0.05, réplica del scorer) en
  vez de `math.exp` nativa. Nota: la bucketización cambia el factor hasta ~5%
  para severidades entre buckets — corrida comparativa: 0 flips, 0 moves (el
  corpus no ejercita este camino; el consumidor es la tool MCP trust_fusion).
- Restantes del mapa (U1 sigmoide H28, U4 LSE de eml_gci, U5, U6): tolerados
  (~1 ulp, sin acumulación, medido) — sin cambio de estado.

---

## B-045 — AndroidForensicsEngine y iOSForensicsAnalyzer nunca invocados [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-06-30 |
| **Severidad** | ALTA — evidencia Android/iOS producía 0 signals, UNDETERMINED |
| **Archivos modificados** | `vigia_agent.py`, `sift_orchestrator.py` (shim) |
| **Archivos afectados** | `vigia/sift/android_forensics.py`, `vigia/sift/ios_forensics.py` |
| **Tag de restauración** | `pre-b045-android-ios-wiring-*` |

### Descripción

`AndroidForensicsAnalyzer` y `iOSForensicsAnalyzer` estaban completamente implementados
(analyze(), to_signal(), _ANDROID_MARKER_FILES, _IOS_MARKER_FILES, etc.) pero nunca eran
invocados por el pipeline. `_build_orchestrator_kwargs` no detectaba markers Android/iOS
en directorios de evidencia, y el shim `sift_orchestrator.py` no tenía adaptadores para
estos motores.

Resultado: evidencia Android/iOS real producía 0 signals y veredicto UNDETERMINED con
exit code 0.

### Fix

1. **`vigia_agent.py` → `_build_orchestrator_kwargs()`**: al escanear un directorio,
   detectar `_ANDROID_MARKER_FILES` y `_IOS_MARKER_FILES` (importados desde los módulos,
   no duplicados) y pasar `android_evidence_path` / `ios_evidence_path` en kwargs.

2. **`sift_orchestrator.py` (shim) → `_analyze_mobile()`**: nuevo método que instancia
   `AndroidForensicsAnalyzer` / `iOSForensicsAnalyzer`, ejecuta `.analyze()` sobre el
   directorio de evidencia, y convierte a signal dict via `.to_signal()`.

3. **`sift_orchestrator.py` (shim) → `_merge_mobile_signals()`**: merge de signals
   móviles en el resultado del pipeline (compatible con todos los paths: EBS JSON,
   vol3, real orchestrator).

4. **Path solo-móvil**: si no hay evidencia Windows pero sí hay signals móviles,
   retornar directamente sin caer al real orchestrator.

### Validación

- Baseline: 188 passed, 6 xfailed — sin regresiones.
- Caso real: `evidence/owl-2019-nexus5-quick/` (Nexus 5, Magnet ACQUIRE):
  - Antes: 0 signals, UNDETERMINED, exit 0
  - Después: 1 signal ANDROID_FORENSICS (z=1.20, 21 SMS, 1 finding EMPTY_CONTACTS,
    data_minimization=true), exit 0 (correcto: z < threshold)

---

## B-046 — GoogleTakeoutForensicsAnalyzer nunca invocado [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-06-30 |
| **Severidad** | ALTA — evidencia Google Takeout producía 0 signals, UNDETERMINED |
| **Archivos modificados** | `vigia_agent.py`, `sift_orchestrator.py` (shim) |
| **Archivos afectados** | `vigia/sift/google_takeout_forensics.py` |
| **Tag de restauración** | `pre-b046-takeout-wiring-*` |

### Descripción

`GoogleTakeoutForensicsAnalyzer` estaba completamente implementado (analyze(), to_signal(),
_TAKEOUT_MARKER_FILES, etc.) pero nunca era invocado por el pipeline.
`_build_orchestrator_kwargs` no detectaba markers de Google Takeout en directorios de
evidencia, y el shim `sift_orchestrator.py` no tenía adaptador para este motor.

Mismo patrón exacto que B-045 (Android/iOS wiring).

Resultado: evidencia Google Takeout real producía 0 signals y veredicto UNDETERMINED con
exit code 0.

### Fix

1. **`vigia_agent.py` → `_build_orchestrator_kwargs()`**: al escanear un directorio,
   detectar `_TAKEOUT_MARKER_FILES` (importado desde el módulo, no duplicado) y pasar
   `takeout_evidence_path` en kwargs.

2. **`sift_orchestrator.py` (shim) → `_analyze_mobile()`**: bloque adicional que
   instancia `GoogleTakeoutForensicsAnalyzer`, ejecuta `.analyze()` sobre el directorio
   de evidencia, y convierte a signal dict via `.to_signal()`. Guard condition adaptado
   (sin `total_sms` — el módulo Takeout no tiene ese atributo).

### Validación

- Baseline: 188 passed, 6 xfailed — sin regresiones.
- Caso real: `evidence/takeout-2020/Takeout` (Google Takeout export):
  - Antes: 0 signals, UNDETERMINED, exit 0
  - Después: 1 signal GOOGLE_TAKEOUT_FORENSICS (z=4.20, 43 findings,
    BROWSER_EXPLOIT_RESEARCH + ROOT_TOOL_INSTALLED + SUSPICIOUS_INSTALLED_APP +
    LOCATION_HISTORY_GAP + OPSEC_ROOT_TOOLCHAIN), exit 0

---

## B-047 — _build_correlation_groups() retornaba List[List[int]], noisy_or_correlated espera Dict[int, Set[int]] [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit `d8ce147` (2026-07-01) |
| **Severidad** | LATENTE → cerrado antes de explotar con corpus grande |
| **Archivos** | `vigia/sift/_math_utils.py`, `android_forensics.py`, `ios_forensics.py`, `macos_forensics.py`, `google_takeout_forensics.py` |
| **Tag de restauración** | `pre-b047-correlation-groups-20260701` |
| **Detectado en** | Sesión 2026-06-30 |
| **Corregido** | 2026-07-01 |
| **Auditoría de cierre** | `AUDITORIA_B047_CORRELATION.md` (2026-07-03) |

### Descripción

Android/iOS/macOS retornaban `List[List[int]]`; takeout tenía el formato
correcto `Dict[int, Set[int]]`. El consumidor `noisy_or_correlated()` vive en
`vigia/sift/_math_utils.py:219` (la entrada [PENDING] original citaba
`vigia/core/noisy_or.py`, que no existe). No explotaba con el corpus de
entonces porque ningún caso producía >=2 findings con el mismo corr_group en
los módulos afectados (Owl-Android: 1 finding → lista vacía → falsy → salta
el bloque de correlación).

**Modo de fallo pre-fix confirmado (2026-07-01, grep sobre repo vivo):**
`sorted(correlation_groups.items())` sobre lista no vacía →
`AttributeError: 'list' object has no attribute 'items'` (no TypeError, como
decía la entrada original) → crash de `analyze()` en cualquier caso real con
findings correlacionados. Fail-loud accidental, no corrupción silenciosa de
score — el composite nunca se computó con el formato inválido.

### Fix aplicado

1. Helper canónico `build_correlation_groups(List[str]) -> Dict[int, Set[int]]`
   en `_math_utils.py:255`, junto a su único consumidor. Semántica exacta de la
   implementación de referencia de takeout (peers sin self, solo grupos >= 2,
   tags vacíos ignorados).
2. Los 4 módulos delegan al helper — elimina la cuadruplicación que originó
   el bug. Los 5 motores Windows nunca estuvieron afectados (dict inline).
3. Guard fail-loud en `noisy_or_correlated` (`_math_utils.py:225-230`):
   `TypeError` explícito si `correlation_groups` no es dict ni None (raise,
   no assert — criterio B-011/B-023/B-026 opción B). Reemplaza el
   AttributeError opaco y hace imposible reintroducir el formato viejo en
   silencio.

### Verificación

17 tests en `vigia/tests/test_b047_correlation_groups.py` (semántica
del helper, equivalencia contra la implementación de referencia congelada,
delegación de los 4 módulos, monotonía correlado<=independiente, guard).
Suite completa post-fix: 205 passed, 6 xfailed, 0 regresiones.
grep: 0 ocurrencias de List[List[int]] en código de módulos SIFT; 4 delegaciones.

**Gatillo real verificado post-cierre (2026-07-03):** la condición "ningún
caso produce >=2 findings correlacionados" quedó obsoleta al descargar
`cases/tuck-2019-macos` — produce 23 findings `corr_group="browser_suspicious"`
y ejercita el path correlacionado completo: `composite_score = 19/20`, sin
crash. Pre-fix, ese caso habría reventado `MacOSForensicsAnalyzer.analyze()`
con AttributeError (la combinación B-048 wiring + tuck-2019 lo habría
explotado en producción). Ver `AUDITORIA_B047_CORRELATION.md` §3.

---

## B-048 — MacOSForensicsAnalyzer nunca invocado [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-07-01 |
| **Severidad** | ALTA — evidencia macOS producía 0 signals, UNDETERMINED con exit 0 |
| **Archivos modificados** | `vigia_agent.py`, `sift_orchestrator.py` (shim) |
| **Archivo afectado** | `vigia/sift/macos_forensics.py` |
| **Tag de restauración** | `pre-b048-macos-wiring-20260701` |
| **Commit fix** | `<hash>` |

### Descripción

`MacOSForensicsAnalyzer` estaba completamente implementado pero ningún
componente del pipeline lo invocaba. Confirmado por triple grep (0
referencias en el agente, 0 en el shim, 0 imports en producción). Mismo
patrón que B-045 (Android/iOS) y B-046 (Takeout).

### Fix — patrón B-045/B-046 más dos guards anti doble conteo

Colisión detectada durante el diseño: `History.db` vive en
`_IOS_MARKER_FILES` y en `_MACOS_MARKER_FILES`, y toda evidencia macOS real
tiene un Safari History.db — el calco puro habría corrido ambos engines
sobre el mismo directorio y contado dos veces los mismos artefactos Safari.

1. `vigia_agent.py` → `_build_orchestrator_kwargs()`: detección con
   `_MACOS_MARKER_FILES - _IOS_MARKER_FILES` (computado desde los imports,
   sin duplicar datos). Evidencia iOS pura no dispara el detector macOS.
2. `sift_orchestrator.py` (shim): guard de precedencia — si
   `ios_evidence_path == macos_evidence_path`, corre solo el engine macOS
   con warning en el log.
3. `sift_orchestrator.py` (shim) → `_analyze_mobile()`: bloque
   `MacOSForensicsAnalyzer` tras el de Takeout (guard sin `total_sms`,
   mismo ajuste que requirió B-046).

El gate solo-móvil (`has_windows_evidence`, línea ~83) no requirió cambios:
decide por presencia de señales móviles, no por keys de plataforma.

### Riesgo residual documentado

Una extracción iOS full-filesystem que incluya `TCC.db` (iOS también lo
tiene y no está en `_IOS_MARKER_FILES`) dispararía el detector macOS; la
precedencia haría correr solo el engine macOS sobre evidencia iOS →
atribución de plataforma equivocada y pérdida de los findings
iOS-específicos (SMS, contacts, calls). Probabilidad baja con el corpus
actual (sin evidencia iOS descargada). Mitigación futura: precedencia por
score de markers fuertes por plataforma, o ejecución de ambos engines con
deduplicación de artefactos compartidos.

### Validación

Smoke end-to-end (`smoke_b048.py`, fixture sintético con schemas SQLite
reales): señal MACOS_FORENSICS presente con z=1.6 — exactamente el valor
del escalation ladder para `has_suspicious_search` (`Fraction(16,10)`),
determinismo confirmado; señal IOS_FORENSICS ausente pese a History.db en
el fixture (precedencia verificada); path correlacionado de B-047
ejercitado en producción (2 findings, mismo corr_group). Suite completa:
205 passed, 6 xfailed, 0 regresiones.

---

## L-042 — _detect_installed_apps() no detecta Signal en extracciones lógicas [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-07-02 |
| **Severidad** | ALTA — Signal nunca aparecía en `encrypted_apps` para extracciones lógicas |
| **Archivo modificado** | `vigia/sift/ios_forensics.py` |
| **Tag de restauración** | `pre-l042-ios-signal-detection-20260702-000337` |
| **Commit fix** | `<hash>` |

### Descripción

En extracciones lógicas (archivos sueltos sin estructura de directorios de
apps iOS completa), `signal.sqlite` aparece como archivo suelto en el
directorio de evidencia o en un subdirectorio inmediato, en lugar de bajo
`Library/Application Support/org.whispersystems.signal/`. El detector
existente usaba `rglob("*/org.whispersystems.signal")` — que busca un
directorio con ese nombre exacto — y nunca encontraba coincidencia.

Consecuencia: caso real Magnet 2022 iOS Jess con `signal.sqlite` presente
→ `encrypted_apps_count: 0`, señal IOS_FORENSICS subestimada.

### Fix

1. **`_IOS_MARKER_FILES`**: agregado `"signal.sqlite"` para que el motor
   reconozca evidencia iOS aunque solo esté este archivo presente.

2. **`_detect_installed_apps()`**: detección por nombre de archivo — busca
   `signal.sqlite` en `evidence_path` y en todos sus subdirectorios
   inmediatos (un nivel). Guard anti-doble conteo: no agrega la entrada si
   `org.whispersystems.signal` ya fue detectado por el path de bundle_id.
   Peso idéntico al path existente: `Fraction(60, 100)`, MITRE T1573.

### Validación

Caso real `evidence/magnet-2022-ios-jess/Jess_CTF_iPhone8/_extracted`:
- Antes: señal IOS_FORENSICS con `encrypted_apps_count: 0`
- Después: `encrypted_apps_count: 1` (Signal detectada), z=2.8, MEDIUM alert
- Suite completa: 205 passed, 6 xfailed, 0 regresiones

---

## B-049 — surgical_patch.py v1: falso positivo de verificación con parches aditivos [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — engine v2 (ENG-001), mismo commit que B-048 |
| **Severidad** | MEDIA — deshacía parches correctos; el restore fail-safe evitó daño al repo |
| **Archivo** | `scripts/surgical_patch.py` |
| **Detectado en** | 2026-07-01, aplicando B-048 sobre vigia_agent.py |

### Descripción

La verificación post-escritura chequeaba `anchor in written` y revertía si el
anchor seguía presente. En parches ADITIVOS (replacement = anchor + bloque
nuevo) el anchor debe seguir presente por diseño — la v1 los revertía como
fallos. B-047 no lo disparó porque todos sus parches eran sustitutivos.

### Fix (ENG-001, v2)

Verificación por presencia del replacement; exigencia de anchor ausente solo
para parches sustitutivos. Además: detección de idempotencia ([SKIP] si el
replacement ya está presente), que permite re-ejecutar scripts de parches
tras fallos parciales. Changelog completo en el docstring del engine.

---

## L-043 — PrefetchAnalysisResult.to_signal() no serializa lista de ejecutables sospechosos [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-07-02 |
| **Severidad** | MEDIA — los nombres de ejecutables detectados no llegaban al bundle ni al CAIE |
| **Archivo** | `vigia/sift/prefetch_analyzer.py` |
| **Método** | `PrefetchAnalysisResult.to_signal()` |
| **Detectado en** | 2026-07-02, auditoría de gaps de serialización |

### Descripción

`analyze_directory()` construía correctamente `self.suspicious_executions` —
lista de dicts con `filename`, `run_count`, `last_execution`, `severity` —
pero `to_signal()` solo serializaba el conteo (`suspicious_count`) en el
`metadata` del `SignalOutput`. La lista de nombres quedaba descartada en la
serialización: el bundle resultante sabía que había 12 ejecuciones sospechosas
pero no cuáles ejecutables eran.

### Fix

Una línea en `to_signal()`, entre `suspicious_count` y `anti_forensic_count`:

```python
"suspicious_executables": [e["filename"] for e in self.suspicious_executions],
```

### Validación

Suite completa: **317 passed, 6 xfailed, 0 regresiones** (13 tests de prefetch
pasan, incluyendo los tests de detección SCCA/MAM y nombre de ejecutable).

Caso real `evidence/owl-2019-hd1-windows` — bundle
`results/agent_batch/VIGIA-OWL-2019-HD1-L043_bundle.json`:

```json
"suspicious_count": 12,
"suspicious_executables": [
  "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE",
  "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE",
  "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE", "RUNDLL32.EXE"
]
```

12 archivos `.pf` distintos de RUNDLL32 (cada uno con hash de ruta diferente)
correctamente visibles. PIDGIN.EXE no aparece porque no está en
`ANTI_FORENSIC_PREFETCH_SIGNS` — es un gap de cobertura de la blacklist
separado del bug de serialización que este fix resuelve.

Restore tag: `pre-l043-prefetch-suspicious-executables-<timestamp>`

---

## B-050 — sift_orchestrator.py (shim): log_path sobreescribe event_logs [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | FIXED — 2026-07-02 |
| **Severidad** | ALTA — EVENT_LOG completamente ciego en cualquier evidencia que tenga archivos .log junto a .evtx |
| **Archivo** | `sift_orchestrator.py` (shim en raíz del repo) |
| **Línea** | 180 |
| **Detectado en** | 2026-07-02, al intentar reproducir B-050 sobre `evidence/owl-2019-hd1-windows` |

### Descripción

El shim `analyze()` en `sift_orchestrator.py` mapea kwargs de `_build_orchestrator_kwargs()`
a los parámetros de `run_full_analysis()`. El mapeo contenía dos asignaciones consecutivas
a `run_kwargs["event_logs"]`:

```python
# L.175-177: mapea .evtx correctamente
es = kwargs.get("event_stream") or kwargs.get("event_logs")
if es:
    run_kwargs["event_logs"] = es if isinstance(es, list) else [es]

# L.178-180: fallback para .log — SOBREESCRIBÍA sin guardia
lp = kwargs.get("log_path")
if lp and not str(lp).endswith(".json"):
    run_kwargs["event_logs"] = lp if isinstance(lp, list) else [lp]
```

El fallback de `log_path` existía para evidencia sin .evtx (solo archivo de texto).
Pero al no tener guardia de "ya está seteado", en cualquier directorio con ambos
tipos (como `owl-2019-hd1-windows`, que tiene `.evtx` + `security_audit.log`), el
`.log` sobreescribía la lista de .evtx. El `EventLogCorrelator` recibía el .log
en vez de los .evtx y producía 0 findings — EVENT_LOG no aparecía en los top signals.

**Nota sobre la ubicación del bug:** La descripción inicial apuntaba a
`vigia_agent.py` L.1236. Ese código (`kwargs["event_logs"] = [str(evidence_path)]`)
está en la rama `else` (archivo único) y es correcto — en esa rama `evidence_path`
ya es el archivo individual. El bug real estaba en el shim `sift_orchestrator.py`.

### Fix

Una línea en `sift_orchestrator.py` L.179:

```python
# ANTES:
if lp and not str(lp).endswith(".json"):

# DESPUÉS:
if lp and not str(lp).endswith(".json") and not run_kwargs.get("event_logs"):
```

El fallback de `log_path` solo actúa si no hay ya `.evtx` mapeados.

### Validación

Suite completa: **317 passed, 6 xfailed, 0 regresiones**.

Caso real `evidence/owl-2019-hd1-windows` (VIGIA-OWL-2019-HD1-WINDOWS-V5):
- Antes del fix: EVENT_LOG ausente de top signals (0 findings)
- Después del fix: **[EVENT_LOG] z=3.040 conf=0.95** en posición 1 de top signals
- finding_types: `['HIGH_SEVERITY_25', 'HIGH_SEVERITY_7045', 'PASS_THE_HASH']`
- 178 findings procesados de 4 archivos .evtx (2954 eventos)
- Exit code: 3 (INTENT/SUSPICION DETECTED)

Restore tag: `pre-eventlog-fix-<timestamp>`

---

## B-051 — likelihood_ratio.py: math.exp(combined_log_lr) sin guard → OverflowError [FIXED]

| Campo | Valor |
|-------|-------|
| **Estado** | CORREGIDO — 2026-07-03 |
| **Severidad** | P1 — crash determinista (DoS) de la Segundidad de Mode 4 |
| **Archivo** | `vigia/core/likelihood_ratio.py` (paso 5 de `infer()`) |
| **Detectado** | AUDITORIA_L040_LIKELIHOOD_RATIO.md §2.3 (análisis formal de L-040) |
| **Tag de restauración** | `pre-b051-overflow-20260703-041212` |

### Descripción

`lr_combined = math.exp(combined_log_lr)` no acotaba el argumento.
`combined_log_lr` es una suma no acotada (`Σ (z²/2)·conf × correction`) y
`math.exp` desborda con argumento > ~709.78 (límite float64). Umbrales exactos
reproducidos por bisección:

- Engine base (`z_cap=3.0`): **≥158 señales** z=3, conf=1 (158×4.5 = 711).
- Adaptador de `pipeline.py` (`z_cap=10.0` por defecto, `Z_CLIP_MAX=5.0`):
  **≥57 señales** z=5, conf=1 (57×12.5 = 712.5). El clamp ±20 del adaptador
  (`likelihood_engine.py`) llegaba tarde: `super().infer()` ya había crasheado.

Resultado: `OverflowError: math range error` → la fase de Segundidad de
Mode 4 (`pipeline.py`) muere con excepción, no con ABSTAIN. Un caso de batch
grande con señales de alta z (el corpus ya tiene VIGIA-BREAK-014 con 101
artefactos) o un adversario que inyecte señales tenía un DoS determinista.

### Fix

Clamp del argumento a `±LOG_LR_EXP_CAP = 700.0` antes de `math.exp`:

- `|combined_log_lr| ≤ 700` → resultado **bit a bit idéntico** al previo
  (ningún input que funcionaba cambia).
- `combined_log_lr > 700` → `lr = exp(700) ≈ 1.01e304`, `posterior = 1.0`,
  etiqueta ENFSI `very strong` — evidencia abrumadora saturada honestamente,
  no un crash. La saturación queda documentada en `ForensicRecord.notes`
  (`[B-051: combined_log_lr=... > 700 — argumento de exp saturado...]`) para
  Daubert.
- Ventana `(700, 709.78]` (n=156-157 con z=3): antes producía un exp finito
  gigante, ahora satura en `exp(700)`. Posterior, etiqueta ENFSI y toda salida
  relevante al veredicto son idénticos; solo cambia el `lr_combined` crudo del
  registro, con nota.

### Validación

- `tests/test_b051_overflow_guard.py` — 7 tests con los umbrales exactos:
  158×z=3 y 57×z=5 (adaptador) retornan finito con posterior=1.0 y nota
  B-051; log_lr ≤ 700 bit a bit intacto; record_hash sigue computable.
- Suite completa y corpus `run_all_agent.py` 198/198 sin regresiones
  (ver commit).

---

## B-052 — Motores mobile/macOS: señal única agregada puentea el AbductiveReasoner [P1 FIXED / P2 CERRADO POR DOCTRINA — NOT ADOPTED]

| Campo | Valor |
|-------|-------|
| **Estado** | P1 (narrativa honesta) FIXED — 2026-07-03; **P2 CERRADO 2026-07-10 — NOT ADOPTED por decisión sellada §9.4 (opción (ii) pura, colectivo + firma de Anna)**: el split por dominios lógicos manufactura corroboración — todos los dominios macOS son D3, mismo canal físico. SUSPICION es el techo doctrinal para D3-only (**L-067 / §9.4-LIM**, ex-L-051). La implementación del split queda como registro histórico en la rama `claude/b052-p2-domain-signals-xk5ecq` (`c5c8d38`+`a74d360`, **NO MERGEAR**); `densidad_causal_D3` descartada por experimento pre-registrado (r=0.9185, zona gris fail-closed). Mitigación implementada: clase `suspicion_class` (GENERIC \| D3_RICH_NO_TRIANGULATION) en narrativa + pipeline_meta, solo texto (`docs/B052_P2_DESIGN.md` §10; 12 tests). |
| **Severidad** | MEDIA — la narrativa Peircean del motor v2 es inalcanzable para evidencia mobile por diseño |
| **Archivos** | `sift_orchestrator.py` (shim, ruta mobile-only); P2: `vigia/sift/{macos,ios,android,google_takeout}_forensics.py` |
| **Detectado en** | `AUDITORIA_MACOS_NARRATIVA.md` (2026-07-03) |
| **Tag de restauración** | `pre-b052-p1-20260703-051457` |

### Descripción

La evidencia mobile/macOS va por la ruta mobile-only del shim, que nunca
invoca `run_full_analysis` (donde vive el AbductiveReasoner). Además cada
engine colapsa N findings en UNA `SignalOutput` (escalera de z), y el
reasoner exige ≥3 señales primarias — aunque se enrutara a V4, no correría.
Resultado: tuck-2019 (23 findings Safari) produce 1 señal z=1.6, ABSTAIN,
sin narrativa del motor v2. No es "Pipeline error": es limitación de diseño.

### P1 aplicado (solo presentación, cero cambio de scoring)

- FIRSTNESS de la ruta mobile enriquecido con hallazgos reales por engine
  (`findings_count` + `finding_types` desde metadata, defensivo).
- La narrativa declara explícitamente: "Motor abductivo v2: NO ejecutado en
  esta ruta (adaptador mobile de fuente única)... limitación de diseño
  documentada (B-052), no un error de pipeline."
- `pipeline_meta.abductive_reasoner = "NOT_RUN_MOBILE_SINGLE_SOURCE"` —
  distingue programáticamente "no corrió por diseño" de "corrió y falló".
- Tests: `TestB052MobileNarrative` (3) en
  `tests/test_pipeline_robustness_narrative.py`. Hipótesis/posterior
  verificados idénticos pre/post-P1.

### P2 pendiente (requiere calibración con corpus)

`to_signal()` → `to_signals()`: una señal por dominio de artefacto
(browser_suspicious / quarantine / antiforensic / persistence /
encrypted_apps — los corr_group ya marcan las familias), con
artifact_type/layer propio, y enrutamiento por V4 cuando el conteo ≥3.
Extender el layer_map del reasoner con layers mobile. **No tocar sin correr
el corpus completo**: cambia el veredicto de todos los casos mobile
(tuck-2019 pasaría de ABSTAIN a INTENT/MALICE). Ver
`AUDITORIA_MACOS_NARRATIVA.md` §4.

---

## B-053 — shim: un pcap corrupto abortaba el caso COMPLETO (T-3) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda A (TRIAGE 2026-07-03) |
| **Severidad** | P1 — pérdida total del análisis en evidencia mixta |
| **Archivo** | `sift_orchestrator.py` (shim, bloque pcap) |
| **Detectado en** | TRIAGE_BUGS_LIMITACIONES_20260703.md (T-3) |
| **Tag de restauración** | `pre-tanda-a-20260703-134624` |

### Descripción

El fallo de parseo pcap (tshark ausente — L-039 — o archivo corrupto) hacía
`raise`, que caía al `except` global de `analyze()` → `_error_result` →
**PIPELINE_ERROR para TODO el caso**. En evidencia mixta (pcap + evtx +
hives), un solo pcap roto descartaba también el análisis de los artefactos
sanos.

### Fix

Patrón F7: el error se captura, el pcap se materializa como señal sintética
`PCAP_UNANALYZED` (`unanalyzed=True`, error en metadata), se agrega "pcap" a
`results.unanalyzed_artifacts` y `pipeline_meta.pcap_error`, y el resto de la
evidencia CONTINÚA. El veredicto degrada a ABSTAIN solo si no queda ninguna
otra señal (gates N8/F7 existentes). La sección "ARTEFACTOS NO ANALIZADOS"
de la narrativa lo muestra.

### Validación

`TestA4PcapDoesNotAbortCase` (2): pcap roto + evtx → hipótesis ≠
PIPELINE_ERROR, señal PCAP_UNANALYZED presente; control con pcap sano.

---

## B-054 — Fallback de texto muerto: import de módulo inexistente + parser incompatible (F-L040-6) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda A (TRIAGE 2026-07-03) |
| **Severidad** | P2 — red de seguridad que nunca funcionó |
| **Archivo** | `vigia_agent.py` (`_run_text_pipeline`) |
| **Detectado en** | AUDITORIA_L040_LIKELIHOOD_RATIO.md (F-L040-6) |
| **Tag de restauración** | `pre-tanda-a-20260703-134624` |

### Descripción (dos bugs encadenados)

1. `from run_pipeline import run` apuntaba a un módulo que no existe en el
   root del repo → el fallback de texto SIEMPRE degradaba a
   PIPELINE_UNAVAILABLE. El módulo real es `vigia/scripts/run_pipeline.py`,
   con firma idéntica (`run(input_path, output_path, negation_enabled)`).
2. **Bug latente expuesto al revivirlo:** el pipeline semiótico serializa
   enteros en formato canónico taggeado (`mi_final = {"num": "29:int",
   "den": "70:int"}`) y el parser del agente esperaba ints crudos →
   `TypeError` en `Fraction(mi["num"], max(mi["den"], 1))`. Ese código nunca
   había corrido contra output real (el import roto lo mantenía muerto).

### Fix

1. Import corregido: `from vigia.scripts.run_pipeline import run` con
   fallback al import plano para layouts legados.
2. Decodificador `_tagged_int()` defensivo ("29:int" → 29; ints crudos
   siguen funcionando; strings inválidos → default).

### Validación

`TestA6TextFallbackAlive` (2): el import resuelve; end-to-end del fallback
sobre evidencia de texto real → hipótesis ≠ PIPELINE_UNAVAILABLE.

---

## B-055 — vigia/core/vigia_scorer.py: copia stale divergente con NameError latente (T-6) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda B (2026-07-03): re-export. Cierre sincronizado desde el tracker EN 2026-07-05 (Fase 0, hallazgo S-4) |
| **Severidad** | P2 — trampa para futuros imports; sin impacto en camino vivo |
| **Archivos** | `vigia/core/vigia_scorer.py` (stale, 523 líneas) vs `vigia_scorer.py` (vivo, 764 líneas) |
| **Detectado en** | Tanda A (aplicando B-026): `_vigia_score` de la copia core crashea con `NameError: _EPC_FACTOR_TABLE is not defined` para toda cadena de custodia no-BROKEN |

### Descripción

Existen dos copias del scorer. La viva (raíz) tiene `_EPC_FACTOR_TABLE`
(fix B-019), B-031 y el resto de la evolución; la de `vigia/core/` divergió y
referencia la tabla sin definirla — **NameError latente** en cuanto alguien
la importe (los consumidores reales, `vigia_api.py` ×2, importan la raíz).
Ya estaba flaggeada como "stale and unused" por el patch r7 (2026-06-19) y
nunca se actuó. El clamp B-026 se aplicó a AMBAS copias por consistencia.

### Propuesta

Eliminar `vigia/core/vigia_scorer.py` o convertirla en re-export de una
línea (`from vigia_scorer import *`) para que no pueda divergir. Requiere
verificar que ningún consumidor externo la importe (grep actual: solo
referencias en comentarios del patch r7). Tanda B.

### Resolución (Tanda B PR-B1, 2026-07-03)

Se aplicó la opción re-export: `vigia/core/vigia_scorer.py` quedó congelada
como re-export del scorer canónico de la raíz (misma identidad de objetos,
no copia). Tests: `tests/test_tanda_b.py::TestB055ScorerReexport` (3) —
verifican identidad de objeto, presencia de `_EPC_FACTOR_TABLE` vía el import
core y scoring sin NameError. Esta entrada ES quedó estanca (el tracker EN
ya la tenía `[RESOLVED]`); sincronizada 2026-07-05.

---

## B-056 — Scorer: provenance colapsada emitía NOISE confiado (P2-D) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Tanda B PR-B2 (2026-07-03) |
| **Severidad** | P1 — familia de falso negativo (incapacidad de análisis presentada como benignidad) |
| **Archivo** | `vigia_scorer.py` (rama `provenance_collapsed`) |
| **Detectado en** | AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md (P2-D), triage 2026-07-03 |
| **Tag de restauración** | `pre-tanda-b-20260703-141147` |

### Descripción

Con trust efectivo medio colapsado (`mean_effective < 0.01`) y sin fracturas,
el scorer emitía `NOISE` con `confidence = 1 - mean_effective` (~0.99): un
veredicto "analizado y limpio" con 99% de confianza **derivada de la ausencia
de confianza**. El propio reason decía "inadmissible under Daubert". Misma
familia que P0-A: incapacidad de confiar en la evidencia ≠ benignidad.

### Fix

Rama → `verdict="ABSTAIN"`, `confidence=0.0`, reason explícito (re-adquisición
requerida). `_VERDICT_TO_RAW`/`_ABSTAIN_REASONS` extendidos para que el
QuadripartiteClassifier resuelva el ABSTAIN de primera clase (antes: el
fail-loud de B-023 lo rechazaba con ValueError — correctamente ruidoso).

### Validación

Corrida comparativa sobre los 198 casos con scorer: **0 verdict flips, 0
score moves** (ningún caso del corpus toca la rama colapsada — el fix protege
la clase, no re-etiqueta casos). Tests: `TestP2DProvenanceCollapsedAbstain` (2).

---

## B-062 — pipeline.py: el "CAIE structural hard gate" decía sobrescribir el veredicto pero solo anota el bundle [RESUELTO — semántica documentada]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03). Decisión de diseño: el gate ES anotación, no orden |
| **Severidad** | P2 — divergencia de caminos de veredicto (familia B-058) + log engañoso (lente 9) |
| **Archivo** | `vigia/pipeline/pipeline.py:676-720` |
| **Alcance** | Modo 4 / CLI standalone (`vigia` en pyproject). **No afecta al Modo 1** (`vigia_agent.py` → `sift_orchestrator`), que no pasa por `pipeline.py` |
| **Detectado en** | Barrido de invariantes en `vigia/pipeline/` (2026-07-03), reproducido de punta a punta por el camino del CLI |
| **Tag de restauración** | `pre-pipeline-fixes-20260703-162541` |

### Descripción

Cuando CAIE detecta una regla de oro o una fractura de la lista de veto
estructural, el gate escribía `caie_analysis.gate_verdict="MALICE"` en el
bundle y logueaba *"verdict overridden → MALICE"*. Pero
`decision_trace.decision` — lo que imprime el CLI (`:1362`, `:1455`), lo que
registra el exec log (`:762`) y lo que exporta el reporte judicial del bridge
(`vigia_integration_bridge.py:992`) — no se modificaba nunca: CAIE corre
*después* de `RiskBoundedDecisionLayer.decide()` y no realimenta. El único
consumidor de `gate_verdict` en el repo es `show_4_hashes.py` (demo), que lo
trata como primera prioridad. Reproducido: CLI `decision: REJECT` con bundle
sellado `gate_verdict: MALICE` y log "verdict overridden".

### Resolución (decisión de diseño, aprobada 2026-07-03)

El gate **es una anotación sellada, no una orden**. Se corrigió el log
(*"CAIE structural veto annotated in sealed bundle ... decision_trace.decision
no se modifica"*) y se documentó la semántica de `gate_verdict` en el
docstring de `run_full` y en el comentario del bloque: el consumidor que
quiera priorizar la imposibilidad estructural debe leer
`caie_analysis.gate_verdict` explícitamente. Sin cambios de comportamiento en
veredictos ni en el bundle.

### Validación

Suite 405 passed (+11 nuevos), mismos 21 e2e preexistentes, 6 xfailed.
Corpus 198/198. Tests: `TestB062GateAnnotation` (1) en
`tests/test_b062_b064_pipeline_fixes.py` — verifica anotación sellada,
decisión intacta y log honesto.

---

## B-063 — forensic_adapter.py: señales con metadata=None crasheaban el adapter → CAIE se salteaba en silencio en el CLI [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03) |
| **Severidad** | P2 — módulo de enriquecimiento desactivado silenciosamente con el input documentado del propio CLI |
| **Archivo** | `vigia/core/forensic_adapter.py:134,166,184` (crash) + `vigia/pipeline/pipeline.py:1262` (origen del None) |
| **Alcance** | Camino CLI `run_vigia` (Modo 4). El bridge no está afectado (siempre construye el dict de metadata) |
| **Detectado en** | Reproducción diferencial durante el barrido de invariantes (2026-07-03) |
| **Tag de restauración** | `pre-pipeline-fixes-20260703-162541` |

### Descripción

`SignalOutput.metadata` tiene default `None` (`ebs_v1.py:104/128`, ambas
variantes pydantic y dataclass). `run_vigia()` construye señales con
`metadata=d.get("metadata")` → `None` si el campo no viene — y el formato de
entrada documentado en el docstring del CLI (`{"tool_name": "SDA", "value":
0.8, "z_score": 2.3, "confidence": 0.9}`) no lo trae. Los tres conversores del
`ForensicAdapter` hacían `sig.metadata.get(...)` → `TypeError`, capturado
aguas arriba como *"CAIE failed (non-blocking)"* → **CAIE nunca corría y nadie
se enteraba**. Verificado diferencialmente: misma corrida con `"metadata": {}`
y CAIE corre; sin él, se saltea. Consecuencia adicional: hacía inalcanzable el
gate de B-062 desde el input documentado.

### Fix

`_meta = sig.metadata or {}` al inicio de los tres conversores
(`signal_to_caie_artifact`, `signal_to_abductive_record`,
`signal_to_causal_link`) — cubre a todos los callers, no solo al CLI.
Paridad garantizada: `metadata=None` se comporta idéntico a `metadata={}`.

### Validación

Suite 405 passed, corpus 198/198. Tests: `TestB063MetadataNone` (6) —
incluye el formato exacto del docstring del CLI de punta a punta verificando
que "CAIE failed (non-blocking)" ya no aparece en el log.

---

## B-064 — Escrituras no atómicas de artefactos de cadena de custodia (ledger, manifest, firma, bundle, reporte) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03) |
| **Severidad** | P2 — familia L-023: un crash a mitad de escritura deja un artefacto de custodia truncado en disco |
| **Archivo** | `vigia/pipeline/evidence_bundle.py` (PDF/ledger/manifest/firma), `vigia/pipeline/vigia_integration_bridge.py:1185,1215` (bundle sellado y reporte), `vigia/pipeline/security_evidence_registry.py:187` (export del ledger) |
| **Detectado en** | Barrido de invariantes, lente "operación sin inversa/atomicidad" (2026-07-03) |
| **Tag de restauración** | `pre-pipeline-fixes-20260703-162541` |

### Descripción

El fix atómico de L-023 (Tanda A) quedó solo en `BundleBuilder.save`. Los
demás artefactos de custodia del camino pipeline se escribían con
`open("w")` + `write`/`json.dump` crudos: ledger, manifest y **firma** del
evidence bundle, el bundle sellado que persiste el bridge, su reporte ENFSI y
el export JSON del `EvidenceLedger`. Un crash o corte de energía entre el
open y el close deja el archivo truncado — y un manifest o una firma a medias
es una ruptura de cadena de custodia bajo Daubert.

### Fix

Nuevo helper compartido `vigia/core/atomic_io.py`
(`atomic_write_text`/`atomic_write_bytes`) con el patrón exacto de L-023:
mkstemp en el mismo directorio + fsync + `os.replace`, con limpieza del
tempfile si algo falla antes del replace. Aplicado a los 6 sitios de
escritura de los tres archivos. Helper compartido en lugar de 6 copias para
no reincidir en la lente 6 (algoritmos duplicados).

### Validación

Suite 405 passed, corpus 198/198. Tests: `TestB064AtomicWrites` (4) —
roundtrip texto/bytes, sin tempfiles huérfanos, y preservación del archivo
destino cuando la escritura falla a mitad de camino.

---

## B-065 — Agente: "Verdict: MALICE" junto a "LOW — No significant anomalies detected" — el floor B-028 estaba muerto para su población objetivo [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03), opciones A+B aprobadas |
| **Severidad** | P2 — contradicción interna citable en la narrativa sellada (44/198 bundles del corpus) |
| **Archivo** | `vigia_agent.py` (`_generate_narrative`, bloque FINAL ALERT LEVEL) |
| **Alcance** | Modo 1 (agente). Solo narrativa: `agent_verdict`, exit codes y el comparador del corpus no cambian |
| **Detectado en** | Reporte de Anna (2026-07-03): "cuando el agente corre y el caso es MALICE, dice luego LOW". Reproducido en fresco con `VIGIA-CAN-004` |
| **Tag de restauración** | `pre-b065-alert-floor-20260703-164437` |

### Descripción

Tres vocabularios que no se hablaban:

1. **El veredicto es categórico, a nivel hipótesis** — `classify_agent_verdict`
   mira el texto de `best_hypothesis` ("MALICI" → MALICE).
2. **El alert level era un detector de picos por señal individual** — solo
   contaba magnitudes (z>3 → CRITICAL; 2<z≤3 → HIGH; si no → LOW). Evidencia
   *distribuida* (muchas señales chicas coherentes, el patrón de un atacante
   cuidadoso) → todo z<2 → "LOW — **No significant anomalies detected**", que
   afirma benignidad dos líneas después de `Verdict: MALICE`.
3. **El floor B-028 existía para esto pero usaba un proxy** —
   `is_conclusive=True` + substring de la hipótesis. Los 44 bundles
   MALICE+LOW del corpus tienen `is_conclusive=False` → el floor nunca
   disparaba **precisamente en los casos para los que fue escrito**. Misma
   familia que B-058: una re-derivación paralela del veredicto que diverge
   del clasificador.

Reproducido con HEAD del día: `VIGIA-CAN-004` → `Verdict: MALICE` (exit 1) +
"LOW — No significant anomalies detected in this iteration." (4 señales
primarias z<0.5, posterior 463/10000, `is_conclusive=False`).

### Fix (A+B, aprobado 2026-07-03)

**A)** El piso se calcula sobre el **veredicto final real**:
`_generate_narrative` llama a `classify_agent_verdict` (el mismo camino único
que sella `agent_verdict` y decide el exit code — elimina la re-derivación en
vez de agregar otra). Umbrales de B-028 intactos: MALICE → HIGH si
`posterior ≥ 1/8`, si no MEDIUM; INTENT → mínimo MEDIUM (ahora también con
`is_conclusive=False` — antes ese caso quedaba LOW).

**B)** LOW nunca afirma benignidad: "LOW (per-signal magnitude) — no
individual primary signal exceeds z>2 in this iteration." Y cuando el piso se
aplica, la narrativa emite una línea de reconciliación explicando que el
veredicto se sostiene por agregación de hipótesis y cuál era el nivel de
magnitud por señal.

Docstring de `classify_agent_verdict` actualizado (la semántica 2 de
`is_conclusive` ya no aplica al piso). Tests de B-028 en `test_tanda_b.py`
actualizados a la semántica nueva — incluido
`test_non_conclusive_intent_keeps_low`, que asertaba el comportamiento buggy
(renombrado a `test_non_conclusive_intent_also_floors`).

### Validación

Suite 405 → **413 passed** (+8 tests nuevos en `tests/test_b065_alert_floor.py`),
mismos 21 e2e preexistentes del entorno, 6 xfailed. **Corpus 198/198** (el
comparador lee `agent_verdict`, que no cambia). Corrida fresca de
`VIGIA-CAN-004` post-fix: MEDIUM con "Alert floored (B-028/B-065)" + línea de
reconciliación — la contradicción desapareció.

### Nota de causa raíz conexa (pendiente, Tanda C)

Que 44 casos MALICE tengan `is_conclusive=False` y posteriors ~0.05 conecta
con el leak de `expected_verdict` en el adaptador EBS (ítem Tanda C). Este
fix elimina la contradicción visible en la narrativa; esa causa raíz sigue
abierta y es decisión de doctrina.

---

## B-066 — Whitelist mobile Fase 1: 8 tipos de evidencia + mapas del adapter + test de contrato [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03). Implementa AUDITORIA_MOBILE_WHITELIST §4 Fase 1; cierra la propuesta de B-060 |
| **Severidad** | P2 — evidencia mobile sin perfil: excluida de CAIE (skip silencioso) y puntuada con fallback no calibrado |
| **Archivo** | `vigia/tools/caie.py` (EVIDENCE_PROFILES), `vigia/core/forensic_adapter.py` (los 3 mapas) |
| **Tag de restauración** | `pre-fase1-mobile-whitelist-20260703-175549` |

### Fix

1. **8 perfiles mobile** en `EVIDENCE_PROFILES`, calibrados por analogía con
   la escala existente (§2 de la auditoría): `chat_message` (.35/.28), `sms`
   (.40/.26), `call_log` (.40/.26), `web_search` (.45/.24), `app_data`
   (.50/.22), `social_media` (.55/.22), `location_data` (.30/.30),
   `contact_data` (.60/.20). Cero apariciones en el corpus → sin efecto
   retroactivo.
2. **Mapas del adapter** (`_LAYER_MAP`/`_EVIDENCE_MAP`/`_ONTOLOGY_MAP`): los
   8 tipos + las 4 etiquetas agregadas de motor (`android_forensic`,
   `ios_forensic`, `macos_forensic`, `google_takeout` → `app_data` hasta
   B-052-P2). Cierra los defaults silenciosos de B-060.
3. **Test de contrato** (`tests/test_b066_b067_mobile_whitelist.py`):
   todo tipo emitido debe resolver en los 3 mapas Y todo valor de
   `_EVIDENCE_MAP` debe existir en `EVIDENCE_PROFILES` — la convención
   productor/consumidor ahora es contrato que falla en CI.

### Validación

Suite 413 → 439 passed (+26), mismos 21 e2e preexistentes, 6 xfailed.
Corpus agente 198/198. Comparativa scorer sobre 267 casos: **0 flips,
0 moves**.

---

## B-067 — Whitelist invertido: un tipo desconocido puntuaba MÁS ALTO que la peor clase conocida [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03) |
| **Severidad** | P2 — bypass de spoofability vía tipo inventado (el que `caie.py` `add_artifact` declara prevenir, abierto en el camino del scorer) |
| **Archivo** | `vigia/tools/caie.py` (`Artifact.profile` + default duplicado inline en `__post_init__`), `vigia_scorer.py:514` (weight default) |
| **Detectado en** | AUDITORIA_MOBILE_WHITELIST §3.2, hallazgo colateral cuantificado |
| **Tag de restauración** | `pre-fase1-mobile-whitelist-20260703-175549` |

### Descripción

El fallback para tipo desconocido era `(spoofability=0.50, weight=0.20)` —
producto `(1-s)×w = 0.10`, **mejor** que `log_entry` (0.85/0.15 → 0.0225) y
que `ip_geolocation` (0.90/0.15 → 0.015). Un caso JSON adversarial podía
inventar `evidence_type` para esquivar el perfil real de su tipo. El default
además estaba **duplicado** en dos lugares (`Artifact.profile` y un inline en
`__post_init__` que alimentaba `effective_spoofability`) — lente 6.

### Fix — y lo que la corrida comparativa obligó a corregir del plan

1. Fallback → `(0.90, 0.15)` = la peor clase conocida real; fuente única
   (`self.profile`), default duplicado eliminado.
2. **El fix naive rompía el corpus** (medido, no especulado): 6 flips, 3
   contra `expected_verdict` (VIGIA-LINUX-001/007, case_009 perdían MALICE
   esperado) — ~36 tipos en uso nunca perfilados dependían de facto del
   fallback generoso. Resolución: esos 36 tipos (incluido `"default"`, el
   placeholder de `normalize_case_schema` para artefactos sin tipo) se
   **pinnean explícitos al valor legacy exacto** (0.50/0.20, marcados
   "Uncalibrated -- pinned at legacy fallback value") → **veredicto** bit a
   bit idéntico, y el fallback duro queda solo para tipos realmente
   desconocidos. El bypass muere: inventar un tipo ya no paga.
3. Invariante protegida por test: `(1-s)×w` del desconocido ≤ mínimo de TODA
   la tabla — si un perfil futuro baja el mínimo, el test obliga a bajar el
   fallback.

### Aclaración de alcance (self-review 2026-07-03)

La frase "bit a bit idéntico" arriba aplica al **veredicto y al score** (267/267
casos, verificado), NO a la membresía interna de CAIE. Efecto secundario
medido y benigno de agregar los 36 tipos a `EVIDENCE_PROFILES`: el frozenset
`_VALID_EVIDENCE_TYPES` (que CAIE `add_artifact` enforcea) ahora los incluye,
así que **31 casos del corpus** pasan artefactos al motor de fracturas que
antes eran rechazados (ej. VIGIA-FLAREON-11: 0→11 artefactos aceptados; casos
llenos de `binary`/`malware_static_analysis`). Medición: **0 casos cambiaron
su nº de fracturas** → 0 cambio de score → 0 cambio de veredicto. Es
arguablemente una mejora (cerraba un falso-negativo latente: esos tipos son
evidencia legítima que debía participar del análisis cross-artefacto), pero se
documenta explícitamente porque "bit a bit idéntico" sin calificar era
impreciso sobre el procesamiento interno.

### Pendiente derivado (documentado, no resuelto)

Los 36 perfiles pinneados son legacy heredado, no calibración forense por
tipo. Calibrarlos mueve ~193 artefactos del corpus (~16%) — trabajo aparte
con corrida comparativa propia. Nota: la comparativa también mostró que
VIGIA-NGDC-003 emite MALICE con expected SUSPICION bajo los valores legacy —
candidato a corrección en esa calibración futura.

### Validación

Comparativa scorer 267 casos: **0 flips, 0 moves** (267/267 idénticos).
Suite 439 passed. Corpus agente 198/198. Tests:
`TestB067FallbackInversion` (3) — invariante contra toda la tabla, regresión
del experimento §3.2, y tipos mobile fuera del fallback.

---

## B-068 — FP VIGIA-NGDC-003: documentación del escenario contaba como corroboración de MALICE [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03) |
| **Severidad** | P1 — falso positivo MALICE en caso de intención genuinamente disputada (la clase de error más cara bajo Daubert: atribución indebida) |
| **Archivo** | `vigia_scorer.py` (gate de corroboración, rama `final_score > 0.33`) |
| **Detectado en** | Corrida comparativa de B-067 (FP latente bajo valores legacy); confirmado como FP real leyendo el caso |
| **Tag de restauración** | `pre-ngdc003-fix-20260703-182734` |

### Diagnóstico — ¿FP real o expected desactualizado?

**FP real.** NGDC-003 (National Gallery DC 2012 — Joe/LogKext) es un caso de
intención disputada por diseño: monitoreo parental de una menor (legal) vs
espionaje conyugal durante un divorcio (ilegal), implementados de forma
idéntica — el registro de artefactos no puede distinguir las dos hipótesis, y
el propio caso lo argumenta en `peirce_expected.thirdness`. SUSPICION es el
único veredicto epistemológicamente honesto; el expected está correcto.

El MALICE salía así: intent score 0.4296 > 0.33 sin fracturas, y el gate de
corroboración (`n_artifacts >= 4 OR n_types >= 3`) pasaba con 5 artefactos —
pero **2 de los 5 son documentación del escenario** (`behavioral_context`,
`outcome_signal`, fuente "Digital Corpora scenario documentation"), no
evidencia de dispositivo. La evidencia técnica real: 3 artefactos / 2 clases
→ el gate no debía pasar.

### Fix mínimo

El gate cuenta solo evidencia **técnica**: se excluyen las clases
contextuales/narrativas (`behavioral_context`, `behavioral_profile`,
`outcome_signal`, `acquisition_context`, `device_acquisition_timeline`,
`osint`). Describen motivo, circunstancias y outcomes — informan la
narrativa, pero no son fuentes independientes que corroboren una inferencia
de malicia ("two independent sources" = clases de evidencia de dispositivo).
Cuando el gate capea, el `reason` lo documenta explícitamente (patrón
REFUTATION GATE LOG). NGDC-001/002/004 no cambian: su corroboración es
técnica (6/6/6 artefactos de dispositivo).

### Validación

Comparativa scorer 267 casos: **exactamente 1 flip** —
`VIGIA-NGDC-003 MALICE→SUSPICION (== expected)` — y 0 moves. Suite 439 →
445 passed (+6 tests, `tests/test_b068_context_corroboration.py`: regresión
NGDC completa + gate sintético, incluido "un caso armado solo con clases
contextuales nunca sella MALICE"). Corpus agente 198/198.

---

## B-069 — Calibración de los 36 perfiles legacy: INTENTADA, RECHAZADA por la comparativa [NO APLICADO — gate negativo]

| Campo | Valor |
|-------|-------|
| **Estado** | NO APLICADO — la corrida comparativa (gate obligatorio) rechazó el cambio. Pins legacy de B-067 retenidos. |
| **Severidad** | N/A — resultado negativo documentado; ningún cambio de código sellado |
| **Archivo** | `vigia/tools/caie.py` (`EVIDENCE_PROFILES`, bloque de pins legacy de B-067) — editado y **revertido** |
| **Tag de restauración** | `pre-ngdc003-fix-20260703-182734` |

### Qué se intentó

Reemplazar los 36 perfiles pinneados al valor legacy (0.50/0.20, marcados
"Uncalibrated" en B-067) por perfiles calibrados **por tipo**, con el mismo
método que los perfiles mobile de B-066: analogía con la escala existente
(`binary`→0.45/0.24 hash-verificable, `git_forensics`→0.30/0.28 SHA-chained,
`disk_image`→0.20/0.30, `email_content`→0.60/0.20, clases contextuales
subidas a 0.70-0.85, etc.).

### Por qué se rechazó — la comparativa es el gate

Corrida comparativa completa sobre 267 casos, baseline = HEAD committeado
(post B-068):

- **Casos ARREGLADOS vs expected: 0.**
- **Casos ROTOS vs expected: 1** — `VIGIA-LINUX-002` NOISE→UNKNOWN. Es el
  caso benigno de *test de falso positivo* (contribuidor open-source
  legítimo, libarchive CVE). La calibración de `git_forensics` (0.10/0.28,
  "difícil de spoofear") hace que la actividad git **legítima** pese más y
  cruce el umbral NOISE→UNKNOWN: un FP nuevo en el caso que existe para
  atrapar FPs.
- Accuracy vs expected: 70.8% → **70.4%** (neta negativa).
- 27 score moves, casi todos **al alza** (inflación).

### Causa raíz de por qué la calibración batch no cierra

Los umbrales del scorer (MALICE>0.33, SUSPICION>0.18, UNKNOWN>0.08) fueron
"calibrados sobre la distribución real de casos EBS v1" (comentario en
`vigia_scorer.py`) **con los pesos legacy**. Subir los pesos por tipo infla
la distribución entera contra umbrales fijos → los casos benignos derivan
hacia arriba. Recalibrar los perfiles por tipo **sin** re-ajustar
conjuntamente los umbrales del veredicto rompe el balance.

### Conclusión (valor del resultado negativo)

La comparativa **prueba que los pins legacy no causan ningún error de
veredicto en el corpus** (0 casos que la recalibración pudiera arreglar). Los
36 perfiles legacy son "no calibrados" en el sentido de que no derivan de una
decisión forense por tipo, pero son **correctos en la práctica** para la
distribución actual. Recalibrarlos es riesgo sin recompensa hasta que exista
un re-fit conjunto perfiles+umbrales con dataset etiquetado (ver
`fit_calibration.py` y el roadmap "Bayesian calibration on labelled case
dataset" en `vigia_scorer.py`). Pendiente reclasificado: de "calibrar los 36
perfiles" a "re-fit conjunto perfiles+umbrales" — trabajo mayor, fuera del
alcance de un fix acotado.

### Validación

Ningún cambio de código sellado. `caie.py` revertido a HEAD (`a021a6a`);
árbol de trabajo limpio. La comparativa que sustenta esta decisión está
archivada como artefacto de sesión (baseline vs post, 267 casos).

---

## B-070 — Rol epistémico device/contextual/narrative: cierra el canal composite del FP NGDC-003 (Opción C) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-03). Opción C de AUDITORIA_ABDUCTIVA_NGDC003_FP; ataca la causa raíz (b) |
| **Severidad** | P2 — inflación de score/confianza de malicia por evidencia narrativa (1 canal que B-068 no cerró) |
| **Archivo** | `vigia/tools/caie.py` (registro `evidence_role`), `vigia_scorer.py` (filtro narrativa + refactor del gate B-068) |
| **Tag de restauración** | `pre-b070-signalclass-20260703-230411` |

### Causa raíz atacada

La investigación abductiva identificó la causa (b): el modelo de datos no
distinguía evidencia-de-dispositivo de contexto-narrativo, así que ambos
fluían al composite de malicia y al conteo del gate por igual. B-068 cortó el
**canal del gate**; el **canal del composite** seguía abierto (NGDC-003:
narrativa inflaba el score 0.2803→0.4296 y la confianza 0.56→0.86; corpus:
1 flip latente LINUX-005).

### Fix (Opción C — registro de roles, fuente única)

Nuevo registro `_EVIDENCE_ROLE` + `evidence_role()` en `caie.py` (semilla del
registro unificado de B-060). Tres roles:

- **DEVICE** (default, incl. tipos desconocidos): cuenta en composite **y** gate.
- **CONTEXTUAL** (`osint`, `acquisition_context`, `device_acquisition_timeline`):
  cuenta en composite (puede portar señal real, ej. deployment off-hours), **no**
  corrobora (gate).
- **NARRATIVE** (`behavioral_context`, `behavioral_profile`, `outcome_signal`):
  **fuera** del composite y del gate. Informa solo la narrativa del reporte.

El scorer aparta los artefactos NARRATIVE **antes** de todo el scoring (no
alimentan CAIE, ni composite, ni gate) y los retiene en `narrative_context`
para el reporte. El gate B-068 se **refactorizó** para leer el rol del
registro único en vez de su lista local de 6 tipos (comportamiento idéntico
del gate; ahora una sola fuente de verdad).

### Por qué 3 roles y no binario (la distinción clave)

`osint`/`acquisition_context` son **device-adyacentes** (OSINT real,
metadata de adquisición): portan señal de anomalía en el composite pero no son
fuentes independientes de dispositivo. Los 3 tipos NARRATIVE son documentación
de escenario (motivo/persona/desenlace) cuyo propio texto suele declarar la
intención indecidible. Un binario habría regresado **LINUX-005** (SUSPICION==
expected, sostenido por su artefacto `osint`): excluir OSINT del composite lo
habría tirado a UNKNOWN. El modelo de 3 roles cierra NGDC-003 sin tocar LINUX-005.

### Validación

Comparativa scorer 267 casos: **0 flips**, accuracy intacta (184/260 — el
veredicto ya estaba bien desde B-068; B-070 corrige score/confianza). 2 score
moves intencionales: NGDC-002 (0.568→0.4785, sigue MALICE), NGDC-003
(0.4296→0.2803, sigue SUSPICION, confianza 0.86→**0.56** honesta). LINUX-005
**sin cambio**. Suite 445→455 passed (+9 `test_b070_signal_class.py` +1
cobertura de gate en `test_b068`). Corpus agente 198/198 (no usa `_vigia_score`).

### Alcance

Solo camino scorer (Modo 4 / EBS-JSON / `vigia_api`). El agente (Modo 1) no
pasa por `_vigia_score`. B-068 (gate) queda subsumido y refactorizado sobre el
mismo registro. Pendiente futuro: extender `evidence_role` al registro
unificado completo de B-060 (layer+ontology+profile+role en una sola fuente).

---

## B-072 — Mobile: conflación "no-parseable == vacío" escalaba el veredicto [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04) |
| **Severidad** | P1 — falso INTENT/MALICE (familia P0-A: incapacidad de análisis presentada como señal) |
| **Archivo** | `ios_forensics.py::_analyze_contacts`, `android_forensics.py::_analyze_contacts` + `_analyze_call_log` |
| **Detectado en** | AUDITORIA_COBERTURA_MOBILE_SIFT §D |
| **Tag** | `pre-p1-mobile-verdict-20260704-022839` |

**Descripción:** cuando la tabla esperada no existía (schema desconocido), el
`OperationalError` se tragaba y el contador quedaba en su default 0 → se emitía
`EMPTY_CONTACTS`/`EMPTY_CALL_LOG` → alimentaba `data_minimization` → escalaba el
veredicto. Un fallo de parseo inocente se puntuaba idéntico a una agenda
deliberadamente borrada.

**Verificación §4.1 (audit-before-patch):** de los 4 métodos que el audit
señaló, solo 3 tenían el bug. `ios_forensics::_analyze_call_history` YA hacía
`return` en el `except` antes de emitir EMPTY — falso positivo del audit,
rechazado sin tocar.

**Fix v1 (2026-07-04, PARCIAL — cosmético):** flag `parsed` local — `EMPTY_*`
se emitía solo con conteo exitoso de 0. **El red-team (AUDITORIA_REDTEAM_P1_MOBILE)
lo refutó:** `to_signal` NO lee el finding — computa
`empty_contacts = self.total_contacts == 0` del contador crudo, que queda en 0
tras el parseo fallido. Reproducido: contacts+calls no-parseables seguían
escalando de z=2.4 a **z=3.0** vía `data_minimization`. El falso INTENT/MALICE
seguía vivo. Removí el finding, no la escalación.

**Fix v2 (2026-07-04, REAL):** centinela `contacts_parsed`/`calls_parsed` en las
dataclasses (default False), seteado True solo con conteo exitoso. `to_signal`
ahora computa `empty_contacts = self.contacts_parsed and self.total_contacts == 0`
— un parseo fallido o una DB ausente (parsed=False) NO escala `data_minimization`.
Verificado: escenario del red-team ahora z=2.4 (== caso con datos), mientras una
agenda REALMENTE parseada-y-vacía sí escala (z=3.0). La distinción quedó correcta.

**Validación:** `tests/test_b072_b074_mobile_verdict_fixes.py` — 9 de B-072
(5 del finding + 4 de `TestB072DataMinimizationEscalation`: parseo fallido no
escala, empty real sí, flags end-to-end). Suite 489, corpus 198/198.

---

## B-073 — iOS: has_phishing computado pero nunca usado en la escalera (rama muerta) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04) |
| **Severidad** | P2 — detección viva pero sin efecto en el veredicto |
| **Archivo** | `vigia/sift/ios_forensics.py::to_signal` |
| **Detectado en** | AUDITORIA_COBERTURA_MOBILE_SIFT §A |

**Descripción:** `has_phishing` (finding_type `SMS_PHISHING_RECEIVED`, emitido de
verdad por `_analyze_sms`) se computaba pero nunca entraba a la escalera z → un
caso de phishing puro caía al piso genérico 1.2.

**Fix v1:** rama `elif has_phishing: z=1.6`. Es una señal PASIVA (phishing
recibido, le pasó al usuario, no la generó él) → pesa menos que la búsqueda
ACTIVA de exploits (has_hacking_search=1.8). **El red-team
(AUDITORIA_REDTEAM_P1_MOBILE) lo marcó verdict-cosmético:** 1.6 (y hasta 2.0
con bump máximo) nunca cruza el umbral estricto >2 — ningún veredicto cambiaba.

**Fix v2 (2026-07-05, decisión de doctrina de Anna — opción b):** *"phishing
recibido puede alcanzar SUSPICION combinado con otras señales"*. Nueva rama
`elif has_phishing and (n_encrypted >= 2 or data_minimization): z=2.2` —
cruza el umbral estricto >2 de `_mobile_hypothesis` solo en combinación. Diseño:

- **Solo, nunca:** phishing puro = 1.6; con bump máximo = 2.0 (no es >2).
- **Combinado, sí:** con ≥2 apps cifradas o con `data_minimization`
  **parseada** (interacción B-072: contadores en 0 por parseo fallido NO
  habilitan la rama) → z=2.2 → SUSPICION_DETECTED.
- **Sigue pasivo:** 2.2 queda debajo de las combinaciones con búsqueda ACTIVA
  (hacking+data_min=2.6, enc2+hacking=2.8). Ramas existentes intactas
  (2 apps solas=2.0, hacking solo=1.8).
- Nota de mapeo (preexistente, para conciencia): la hipótesis
  `SUSPICION_DETECTED` sella `agent_verdict=INTENT` (exit 3) en la escala de
  4 valores del agente, cuyo tier INTENT representa "INTENT/SUSPICION".

**Validación:** 8 tests (2 de v1 + 6 de `TestB073DoctrineCombined`: combinado
cruza, solo no cruza ni con bump, B-072 interplay, pasivo < activo, ramas
existentes sin cambio). Suite 509, corpus 198/198. Restore tag:
`pre-b073-doctrine-20260705-014509`.

---

## B-074 — macOS: has_sip_disabled siempre False → ramas de veredicto muertas [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04). Decisión de Anna: VIGÍA debe detectar SIP disabled desde chequeo real. |
| **Severidad** | P1 — escalación anti-forense inalcanzable |
| **Archivo** | `vigia/sift/macos_forensics.py` (`_detect_sip_status` nuevo + wire en `analyze`) |
| **Detectado en** | AUDITORIA_COBERTURA_MOBILE_SIFT §A (confirmado empíricamente: `SIP_DISABLED` solo aparecía donde se lee) |

**Descripción:** `to_signal` lee `has_sip_disabled` (finding_type `SIP_DISABLED`)
en dos ramas anti-forenses (z=3.4 y z=2.4), pero NINGÚN analyzer emitía ese
finding → ramas estructuralmente MUERTAS. Un macOS con SIP deshabilitado +
tooling anti-forense nunca recibía la escalación codificada para ese escenario.

**Fix v1 (2026-07-04):** `_detect_sip_status` con solo el fallback de shell
history (`csrutil disable`/`enable --without`). **El red-team
(AUDITORIA_REDTEAM_P1_MOBILE) lo marcó de baja recall:** `csrutil disable`
corre SOLO desde Recovery OS, así que casi nunca aparece en los shell histories
del OS booteado que capturan las herramientas forenses → perdía la mayoría de
los Macs con SIP realmente deshabilitado.

**Fix v2 (2026-07-04, recall real):** se agregó la **fuente autoritativa NVRAM
`csr-active-config`** (parser `_parse_csr_config` + tabla `_CSR_FLAGS`). Lee
`nvram.plist` (key bare o con prefijo GUID), interpreta el valor de 32 bits
little-endian: `0x0` = SIP habilitado (note autoritativo, sin finding); ≠0 =
`SIP_DISABLED` con los flags CSR_ALLOW_* concretos en el evidence
(ej. `0x77` = UNTRUSTED_KEXTS, UNRESTRICTED_FS, TASK_FOR_PID, APPLE_INTERNAL,
UNRESTRICTED_DTRACE, UNRESTRICTED_NVRAM). **NVRAM gana sobre el shell history**
(un `csrutil disable` en history puede ser un intento fallido/re-habilitado; el
estado NVRAM es el real). El shell history queda como fallback cuando no hay
NVRAM. Degradación honesta (§5.3): sin ninguna fuente, "undetermined".

**Doctrina RESUELTA (2026-07-05, decisión de Anna):** SIP-disabled cuenta como
`has_antiforensic` (T1562.001) y escala por sí solo. Implementación con guarda
anti-FP verificada empíricamente:
- `has_antiforensic = has_antiforensic_finding or has_sip_disabled` (SIP cuenta).
- SIP solo → rama `has_sip_disabled` → **z=2.4 (SUSPICION)** — escala por sí solo.
- SIP + exploit → rama `exploit and has_antiforensic` → z=3.8.
- **Guarda anti-FP:** las ramas de combinación FUERTE (3.4 triple, 2.8) usan el
  flag EXPLÍCITO `has_antiforensic_finding` (acto anti-forense separado y
  deliberado), NO el inclusivo. Sin esto, el OR global colapsaba la rama triple:
  medido → SIP + 2 apps cifradas normales (Signal/WhatsApp de un dev con SIP
  off) saltaba a **3.4 (INTENT)** — falso positivo sobre perfiles inocentes.
  Con la guarda: SIP + apps normales = 2.4 (SUSPICION), y el triple genuino
  (SIP + acto anti-forense real + apps) = 3.4, distinguido.
- Controles sin cambio: real-AF+2apps=2.8, 2apps=2.0, exploit=3.5.

**Validación:** `tests/test_b072_b074_mobile_verdict_fixes.py` — 11 de B-074
(3 shell-history/rama + 4 `TestB074NvramAuthoritative` + 4 `TestB074CsrParser`).
NVRAM 0x77 → SIP_DISABLED con flags; 0x0 → note autoritativo; NVRAM gana sobre
history; key con prefijo GUID; parser bytes/int/hex/basura. Suite 499,
corpus 198/198. Restore tag: `pre-b074-nvram-20260704-...`.

---

## B-071 — Mobile: acceso SQLite de evidencia read-only + immutable (S1) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-04) |
| **Severidad** | P1 — escritura en evidencia (viola invariante read-only) + DB vacía silenciosa |
| **Archivo** | `vigia/sift/_sql_utils.py` (nuevo) + los 3 `_safe_sqlite_connect` |
| **Detectado en** | AUDITORIA_COBERTURA_MOBILE_SIFT §C / patrón sistémico S1 |

**Descripción:** los 3 `_safe_sqlite_connect` abrían `sqlite3.connect(str(path))`
read-WRITE. Una DB con WAL/journal sucio dispara auto-recovery que escribe
`-wal`/`-journal` de vuelta en `VIGIA_EVIDENCE_DIR` (viola invariante #1) y un
path inexistente CREA una DB vacía (0 hallazgos lee limpio). Ambos verificados
empíricamente.

**Fix v1 (mode=ro&immutable=1) — REFUTADO por el red-team:** cerraba la
escritura y la creación, pero `immutable=1` IGNORA el `-wal` → una DB en modo
WAL con datos en el `-wal` (estado normal de un teléfono vivo) se leía como
tabla vacía → **falso negativo grave** (evidencia inculpatoria invisible).
`mode=ro` solo tampoco servía: crea el `-shm` en evidencia. Cambié custodia por
completitud.

**Fix v2 (copy-to-working-dir) — REAL:** `safe_sqlite_connect` copia la familia
`db` + `-wal` + `-shm` + `-journal` a un working dir efímero y abre la COPIA
read-write ahí. Satisface los dos invariantes a la vez: cero escritura en
evidencia (el original nunca se abre) Y lectura completa del WAL. El working dir
se borra al cerrar la conexión (`_WorkingCopyConnection.close`) + backstop por
GC (`weakref.finalize`). Path ausente → None (no crea). DB malformada → error
lazy en el query (lo captura el parser). Una implementación, contrato compartido.

**Limitación honesta (§5.3):** copia el archivo — costo O(tamaño DB) por
artefacto; aceptable porque los callers acotan cuántas DBs abren (`_safe_rglob`
limit=N).

**Validación:** `tests/test_b071_sqlite_readonly.py` (12): escritura en la copia
NO toca la evidencia (hash idéntico), **datos del WAL visibles** (el FN), working
dir limpiado al cerrar, path ausente no crea, DB malformada lazy. Suite 491,
corpus 198/198. Restore tag: `pre-b071-rework-20260704-...`.

---

## B-075 — Adaptador EBS: fuga de expected_verdict al veredicto (P2-C) — resolve() implementado y default motor [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — resolve() implementado; **default motor desde 2026-07-05** (decisión de doctrina de Anna, opción (a): flip ya). Legacy queda solo como modo explícito de reproducción (`VIGIA_EBS_RESOLVE=legacy`); valores desconocidos caen a motor. Claims del README actualizados (143/199 detección ciega); tag del flip `pre-fase1-flip-default-20260705-223653` |
| **Severidad** | P1 — en modo legacy el veredicto sellado del agente para casos EBS ES la etiqueta (0 detecciones sin ella); riesgo Daubert directo |
| **Archivo** | `sift_orchestrator.py` (`_analyze_ebs_json`, `_resolve_hypothesis`, `_MOTOR_HYPOTHESIS_MAP`) |
| **Detectado en** | AUDITORIA_MOTOR_SIN_LABEL (blind run + label-flip 3b + umbral muerto 3c); formalizado en PLAN_ABDUCTIVO_PENDIENTES_20260705 §3 Fase 1 |
| **Tag de restauración** | `pre-fase1-label-leak-20260705-221206` |

### Descripción

Sin `expected_verdict`, el agente colapsaba a NOISE 189/ABSTAIN 9 (cero
detecciones) mientras el motor (`vigia_scorer._vigia_score`) produce
MALICE 108/SUSPICION 35/UNKNOWN 14/NOISE 41. La única vía del adaptador a un
veredicto malicioso era la etiqueta; el umbral alternativo `avg > 2` es
inalcanzable para inputs [0,1]. H2 ("re-escalar el umbral bastaría") fue
refutada por medición: mejor acuerdo posible con umbrales sobre avg = 58.6%
(4 clases) / 74.7% (binario).

### Fix aplicado (Fase 1, 2026-07-05)

`resolve()` — la selección abductiva de Aliseda (generación vs selección): el
adaptador invoca al scorer canónico con la etiqueta removida y mapea su
veredicto al espacio de hipótesis del agente. Modo `VIGIA_EBS_RESOLVE=motor`;
trazabilidad sellada en `pipeline_meta.resolve`. Tests:
`tests/test_fase1_resolve.py` (10; blind gate, equivalencia con el scorer,
invariancia al label-flip, pin del legacy, honestidad FN, guard B-027).

**Comparativa (gate B-069):** legacy 199/199 (eco de etiqueta, 0 detecciones
ciegas) vs motor 143/199 honesto con distribución idéntica al motor ciego;
~41/56 desacuerdos son de severidad adyacente. Detalle y matriz de decisión:
`docs/FASE1_RESOLVE_EBS.md`.

### Cierre (flip 2026-07-05)

Decisión de doctrina tomada: **opción (a), flip ya** — `VIGIA_EBS_RESOLVE=motor`
default; el corpus mide detección real (143/199); los 56 desacuerdos con las
etiquetas pasan a ser el backlog de calibración de Fase 2. La rama legacy se
retiene SOLO como modo explícito de reproducción de bundles históricos (los
tests B-027/B-058 que ejercitan sus contratos quedaron fijados a
`VIGIA_EBS_RESOLVE=legacy`); un valor desconocido de la env var cae a motor
(fail-honest, nunca reactiva el leak). Claims actualizados en
README.md/README_ES.md con nota de cambio de métrica;
`SUBMISSION_COMPLIANCE.md` intencionalmente sin tocar. Comparativa
antes/después sellada en `docs/FASE1_RESOLVE_EBS.md` §4-§5.

---

## B-076 — Ladder del scorer: umbral SUSPICION 0.18 recalibrado a 0.10 con ground truth (Fase 2, E1) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — aplicado 2026-07-05 con gate comparativo (patrón B-069): +10 aciertos, 0 regresiones |
| **Severidad** | P2 — 10 casos etiquetados SUSPICION emitían UNKNOWN (banda muerta [0.101, 0.148] entre los umbrales 0.08 y 0.18) |
| **Archivo** | `vigia_scorer.py:820` (ladder de decisión) |
| **Detectado en** | Dataset de calibración de Fase 2 (`data/calibration_ladder_dataset_20260705.json`, 198 casos): los 10 SUSPICION→UNKNOWN caían TODOS a <0.05 del umbral 0.18 |
| **Tag de restauración** | `pre-fase2-dataset-20260705-232536` |

### Descripción y medición previa (deducción antes del cambio)

El censo del dataset mostró que bajar el umbral a 0.10 solo podía afectar a
casos con score en [0.10, 0.18): los 10 SUSPICION mal clasificados más UN
solo caso correcto (VIGIA-REAL-SRL-DC-MEMORY, exp=UNKNOWN, score 0.167) —
que el comparador acepta con cualquier veredicto (expected=UNKNOWN pasa
siempre). Colateral esperado: cero.

### Gate comparativo (inducción)

- Suite: 719 passed / 7 xfailed (sin cambios).
- Corpus default (motor): 143/199 → **153/199** (+10 exactos, 0 regresiones).
- Desacuerdos: 56 → 46 (el MALICE→UNKNOWN de score 0.148 pasa a
  MALICE→SUSPICION: sigue fail, un escalón más cerca).

Experimentos hermanos medidos y NO aplicados (documentados en
`docs/FASE2_DATASET_CALIBRACION.md`): E2 (escalón INTENT por fracturas CAIE
— refutado: rompería 49 MALICE correctos) y E3 (NOISE con <3 artefactos →
ABSTAIN — refutado: neto ≈ +1 con costo doctrinal). El hueco estructural
INTENT del ladder y la revisión de etiquetas ABSTAIN/L-012 quedan como
decisiones abiertas (doc §4 y §5).

---

## B-077 — Agente ciego colapsaba a NOISE/ABSTAIN: semantic_role (Fase 2, D1+D2) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-06), commit `ffe5693` |
| **Severidad** | P1 — continuación de A1/P2-C (PLAN_ABDUCTIVO Fase 1): sin la fuga de expected_verdict (B-075), el agente carecía de señal semántica propia |
| **Archivo** | `vigia_scorer.py`, `vigia/vigia_sift_bridge.py` |
| **Documento** | `docs/FASE2_EVIDENCIA_EXCULPATORIA.md` |

**Descripción:** tras cerrar B-075 (resolve() motor default), la medición blind
mostró el hueco real: el pipeline no distinguía el rol semántico de la evidencia
(inculpatoria vs exculpatoria vs neutra). Implementación D1+D2 de la
investigación de Fase 2.

**Validación:** corpus 152/199 → **165/199** (+13), 0 regresiones. Suite verde.

---

## B-078 — LaBestia (sandbox de búsqueda): 3 fallos operativos encadenados [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-06), commits `e10a364`, `e649307`, `2275316` |
| **Severidad** | P1 — resultados de búsqueda forense silenciosamente vacíos |
| **Archivo** | `vigia/security/sandbox.py` |

**Descripción (3 capas, cada fix destapó la siguiente):**
1. Default de memoria de `safe_grep` obsoleto (256MB) + fallos de `find`/`grep`
   reportados como "sin resultados" en vez de error (`e10a364`).
2. El fix anterior trataba el exit code 123 como fallo — pero `xargs` colapsa a
   123 el "algún grep no matcheó", que es un resultado válido (`e649307`).
3. `RLIMIT_NPROC` del sandbox demasiado bajo: el fallo real de LaBestia en
   producción; docstrings corregidos a honestos (`2275316`).

**Validación:** `tests/test_h4_grep_sanitizer_unification.py` ampliado en los
3 commits. Suite verde en cada paso.

---

## B-079 — Q2 Capa 1: eco_check fail-open ante error interno [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-06), commit `0daf5a9` |
| **Severidad** | P1 — un filtro de sobreinterpretación que crashea no debe dejar pasar el caso |
| **Archivo** | `vigia/core/eco_check.py`, `vigia_scorer.py` |
| **Documento** | `docs/AUDIT_SEALED_VERDICT_SECURITY.md` (hallazgo Q2) |

**Descripción:** el filtro Eco (detección de evidencia "demasiado perfecta")
degradaba fail-open ante excepción interna. Ahora fail-closed + correcciones de
la revisión externa del patch. Suite verde.

---

## B-080 — Q4 / L-023: escritura atómica en el camino primario y en ebs.py [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-06/07), commits `dce9040`, `606469d` |
| **Severidad** | P1 — patrón pre-L-023 (open("w") directo) en el artefacto de custodia primario |
| **Archivo** | `vigia_agent.py`, `vigia/core/atomic_io.py`, `vigia/models/ebs.py:847` y `:1174` |
| **Documento** | `docs/AUDIT_SEALED_VERDICT_SECURITY.md` (hallazgo Q4) |

**Descripción:** (a) el bundle sellado del Modo 1 se escribía con
`Path.write_text` directo — enrutado por `atomic_io` (mkstemp+fsync+os.replace+
fsync del directorio, F-6) y el `.sha256` se computa RE-LEYENDO de disco, no de
memoria (F-1b: el chequeo anterior era tautológico). (b) Los dos `save()` de
`vigia/models/ebs.py` (`ForensicBundle.save`, `BundleBuilder.save`) seguían con
`open("w")` — mismos fixes, con verificación disco-vs-memoria → RuntimeError en
divergencia. Consumidores verificados independientes (models/ebs.py sin
consumidores de producción; pipeline usa core/ebs_v1 + core/bundle_builder).

**Validación:** suite verde, corpus 166/199, 0 flips.

---

## B-081 — M2-1/M2-2 + Round 2.1: invariantes de monotonicidad del scorer [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07), commits `433d61a` (audit), `f85f171` (fixes), `1d84c84` (doctrina) |
| **Severidad** | P1 — agregar evidencia inculpatoria podía BAJAR el score (no-monotonicidad) |
| **Archivo** | `vigia_scorer.py` |
| **Documento** | `docs/REDTEAM_ROUND2_MONOTONICITY.md` |

**Descripción:** Red-Team Round 2 confirmó dos violaciones de monotonicidad
(M2-1, M2-2). Fixes implementados con gate comparativo: corpus 165→163 (+1 fix,
3 conflictos de etiqueta que codificaban la dilución). Round 2.1 (decisión de
doctrina): relabel de esas 3 etiquetas → corpus **166/199**.

**Validación:** `tests/test_m2_monotonicity_invariants.py`. Suite verde.

---

## B-082 — R3-1..R3-4: cuatro fracturas emergentes del Red-Team Round 3 [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07), commits `03f6c10` (audit), `22f6edc`, `b981803`, `e0e7be0` |
| **Severidad** | P1/P2 — integridad del sello y del ground truth |
| **Archivo** | `vigia/tools/caie.py`, `vigia/core/canonicalize.py`, `vigia/core/hash_chain.py`, `verify_tool_log.py`, runner |
| **Documento** | `docs/REDTEAM_ROUND3_EMERGENT.md` |

**Descripción y fixes:**
- **R3-1:** guard de rango temporal en TCV (`22f6edc`).
- **R3-2:** canonicalización v2 cierra colisiones de tipo (`True`/`"true"`,
  `1`/`"1:int"`), versionada con v1 legacy retenido para bundles históricos
  (`b981803`).
- **R3-3:** assert de consistencia de etiquetas en el runner — 59 stems
  duplicados en el corpus, 3 con `expected_verdict` divergente resuelto
  silenciosamente por precedencia de directorio (`22f6edc`). La deduplicación
  física del corpus queda pendiente (Grupo D).
  - **R3-3b (censo total, 2026-07-07):** el guard original solo comparaba
    `data/cases/` contra `converted/`. Censo completo sobre las 5 CASES_DIRS:
    62 stems duplicados, **1 divergencia viva** —
    `case_008_multi_source_fraud_demo` SUSPICION (canónica, relabel doctrinal
    `cdeb32f` documentado en `_notes`) vs MALICE (`legacy/`, nunca recibió el
    relabel). Cerrada propagando el relabel a la copia legacy (la métrica no
    cambia: la ganadora ya era SUSPICION). `check_label_consistency` ahora
    cubre TODOS los pares de directorios (default `CASES_DIRS`) y `main()`
    aborta sobre el censo total. Las AMB-001/002 del hallazgo original ya
    estaban alineadas. 3 stems malformados documentados (listas JSON:
    `VIGIA_BREAK_001-010` ×2, `dataset_test_cases`, `vigia_input_defcon_nist`
    ×3 — los últimos dos excluidos por SKIP_STEMS; BREAK_001-010 entra como
    UNKNOWN y auto-pasa: retirarlo cambiaría el denominador 199, decisión de
    doctrina pendiente en Grupo D). Tests rojos primero: 3 rojos en
    `tests/test_r3_3_label_consistency.py`. Suite 863, corpus 166/199, 0 flips.
  - **R3-3c (dedup física, 2026-07-07):** censo clasificado de las 70 sombras:
    36 con schema distinto (árboles FUENTE — `benign/` y `legacy/` alimentan
    los conversores; no son copias muertas) y 13 variantes de contenido se
    CONSERVAN bajo el guard de etiquetas; las **20 byte-idénticas** (censo de
    consumidores: ninguno en suite) se retiraron con `git rm`. El bundle
    pre-migración `VIGIA_BREAK_001-010` se excluyó vía SKIP_STEMS (archivo
    conservado como historia; double-contaba 10 casos que existen
    individualmente y auto-pasaba como UNKNOWN). **Descubrimiento del test
    rojo:** el matching por substring de SKIP_STEMS se tragaba el caso real
    `VIGIA_BREAK_005_FALSE_CORRELATION` (contiene "correlation") — excluido
    en silencio del corpus DESDE SU CREACIÓN. Fix: `_is_skipped()` por
    prefijo (censo: cubre todos los auxiliares reales, 0 falsos positivos).
    Resultado neto: 199 casos de nuevo — sale el auto-pass falso, entra
    BREAK_005 y el agente lo ACIERTA (SUSPICION). Corpus **166/199 honesto**
    (mismo número, mejor denominador), 0 flips en los 197 restantes, 0
    promociones de sombra verificadas contra snapshot. Tests rojos primero:
    2+1 rojos. Suite 866. Bundle huérfano `VIGIA_BREAK_001-010_agent_bundle`
    retirado de results/.
- **R3-4:** validación de orden causal en el verificador de la cadena, eje
  separado del sello (`e0e7be0`).

**Validación:** suite verde y corpus 166/199 en cada fix.

---

## B-083 — Censo P0-001 de float() + fixes adyacentes (timestamps, gamma, umbrales) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07), commits `b620385` (censo), `15e858d` (fixes) |
| **Severidad** | P2 — precisión y doctrina Fraction-pura; ningún sitio violaba determinismo |
| **Archivo** | `vigia/sift/android_forensics.py`, `vigia/sift/_math_utils.py`, `vigia/inference/abductive_reasoner.py` |
| **Documento** | `docs/AUDIT_P0001_FLOAT_CENSUS.md` |

**Descripción:** censo exhaustivo de los 37 call sites de `float()` en los 12
módulos del path de scoring (10 SIFT Windows + iOS + Android). Veredicto: 36/37
son la frontera de contrato del DTO `SignalOutput` (decisión de alcance P0-001
vigente); todos los consumidores re-cuantizan determinísticamente. Fixes
aplicados sobre los hallazgos adyacentes:
- §3.1: `int(float(raw_ts))` perdía µs por encima de 2^53 (timestamps WebKit
  ~1.7e16) → `int(Decimal(str(raw_ts)))`.
- §5.4: `int(ts / 1_000_000)` cruzaba bordes de segundo por redondeo IEEE 754
  (ts=18396007234999999 → …235 en vez de …234) → división entera `//`.
- §5.1: recurrencia del patrón pre-P0-001 en el gamma dinámico
  (`int(round(float(x)*20))`; x=0.42500000000000004 → 8/20 en vez de 9/20) →
  `Fraction(round(Fraction(str(x)) * 20), 20)`.
- §5.3: umbrales del reasoner abductivo comparados en float → `_z_frac()` +
  umbrales `Fraction` (semántica idéntica, doctrina Fraction-pura).

**Pendiente del censo (mejoras opcionales):** emitir `z_frac`/`conf_frac`
exactas en metadata de `to_signal()`; unificar el estilo `float(z)/Z_CLIP_MAX`
(Windows, doble redondeo) con `float(z/z_clip)` (móvil, redondeo único).
Observación menor — **CERRADA (2026-07-07, mismo día):** el clip de
`ebs_v1.SignalOutput` convertía NaN → 5.0 en silencio (semántica de `min` con
NaN) — un z_score corrupto entraba como señal CRÍTICA máxima. Unificado al
patrón fail-closed de `signal_contract`: `value`/`z_score` no-finitos →
ValueError en ambas variantes (Pydantic y fallback dataclass, esta última
verificada bloqueando pydantic). Clip/clamp sobre finitos sin cambio. Tests
rojos primero: `tests/test_b083_signaloutput_fail_closed.py` (14, 8 rojos
pre-fix). Suite 849, corpus 166/199, 0 flips.

**B-083b — confidence también (2026-07-07):** el mismo patrón aplicado a
`confidence` en `ebs_v1` Y `signal_contract`. El gap real estaba en los
fallbacks dataclass: `max(0.0, min(1.0, nan))` → 1.0 — una confidence
corrupta entraba como confianza MÁXIMA silenciosa (±inf clampeaban a 1.0/0.0).
En las variantes Pydantic, `Field(ge/le)` ya rechazaba NaN por semántica de
comparación; el chequeo `math.isfinite` ahora es explícito para que el
contrato no dependa de ese detalle. Tests rojos primero: 6 rojos (los dos
fallbacks, cargados bloqueando pydantic) + pins de las variantes Pydantic.
Suite 860, corpus 166/199, 0 flips.

**Validación:** `tests/test_census_adjacent_fixes.py` (13, valores divergentes
hallados por búsqueda exhaustiva). Suite verde, corpus 166/199, 0 flips.

---

## B-084 — TANDAS 1–4 de AUDITORIA_FUGA_INDIRECTA: H1b, B-059, H4, H5, H1c [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-06), commits `b3246c9`, `f1e3f75`, `b43a8af`, `b31c4c5`, `c865da9` |
| **Severidad** | P1 — fuga indirecta de etiquetas y escaleras rotas |
| **Documento** | `docs/AUDITORIA_FUGA_INDIRECTA.md` |

**Descripción (una entrada por tanda):**
- **TANDA 1 / B-059** (`f1e3f75`): escala ENFSI unificada en
  `vigia/core/enfsi.py` — cierra el ítem B5 del PLAN_ABDUCTIVO (3
  implementaciones divergentes).
- **TANDA 2 / H4** (`b43a8af`): `_sanitize_grep_pattern` unificado fail-closed
  + fix de NameError latente en `safe_grep`.
- **TANDA 3 / H5** (`b31c4c5`): escalera vol3 corregida — INTENT alcanzable +
  gate de 2 fuentes para MALICIOUS.
- **TANDA 4 / H1c** (`c865da9`): puerta de datos cerrada — 15 casos BEN
  regenerados sin la reducción ×0.25; corpus honesto 152/199.
- **H1b previo** (`b3246c9`): cuarentena del bloque `is_benign` en
  `normalize_case_schema`.
- Contexto de auditoría: revisión de etiquetas BEN-001..015 (`9a33982`, 0
  cambios, 15 FPs del motor documentados) y addendum B-076 calibrado sobre
  datos contaminados (`651ca10`).

**Validación:** suite verde por tanda; el corpus post-TANDA-4 (152/199) es la
base honesta sobre la que Fase 2 (B-077) midió su +13.

---

## B-085 — Validador schema-aware + lote de metadata de adquisición (WHAT_IS_NEXT §1.1.2) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07) |
| **Severidad** | P2 — higiene de corpus; precondición del dataset de calibración (Tanda C / A4) |
| **Archivo** | `validate_case.py`, `scripts/complete_acquisition_metadata.py` (nuevo), 145 casos del corpus |
| **Antecedente** | AUDITORIA_MOTOR_SIN_LABEL §1 (54/199 PASS) y §3 (hipótesis causal ya refutada: metadata ausente ≠ FP/FN) |

**Abducción (el titular escondía dos defectos distintos):** el "145/199 FAIL"
mezclaba (a) casos EBS legítimamente incompletos y (b) **falsos positivos del
propio validador**: el corpus tiene DOS schemas de artefacto — EBS-señales
(raw_score → CAIE) y narrativo/semiótico (content/peirce_layer → vía de
texto) — y validate_case.py solo conocía el primero. Los 41 errores
"raw_score=-1 fuera de rango" del audit eran el DEFAULT del validador aplicado
a artefactos narrativos sin raw_score. Censo clasificado: 90 EBS acq-ok,
85 EBS sin acq, 24 narrativos/mixtos.

**Fix 1 — validador schema-aware:** `artifact_schema()` discrimina por la
señal (raw_score presente → contrato EBS; content/forensic_anomalies →
contrato narrativo mínimo: artifact_id + contenido interpretable; ninguno →
error de schema irreconocible). El contrato EBS queda EXACTAMENTE igual.
Bonus: reset de acumuladores module-level (segunda llamada in-process
arrastraba errores).

**Fix 2 — lote aditivo honesto (doctrina L-037):** el script NO fabrica
proveniencia física — documenta la real: `acquisition_tool` = método de
`_migration_note` o declaración explícita de caso de corpus;
`acquisition_hash` = sha256 del bundle FUENTE si existe en disco, si no
auto-atestación del artefacto (con `acquisition_note` declarando qué cubre);
`acquisition_timestamp` = fecha de migración o de esta documentación
retroactiva; `write_blocker_used=False` (no hubo medio físico). Solo AGREGA
campos ausentes en artefactos EBS no-contexto; nunca sobreescribe; no toca
narrativos. 145 casos tocados.

**Inducción (gates):**
- Validador: 54/199 → **194/199 PASS**. Los 5 restantes son defectos reales
  de forma: OWL-NEXUS5 (20 artefactos narrativos sin artifact_id),
  NPS-2010-EMAILS ×2 y NPS-2014-USB (artefactos EBS sin timestamp),
  CTF-2021-iOS — documentados, NO parcheados a ciegas.
- Suite **876 passed** (+10 tests del validador, 4 rojos pre-fix).
- Corpus **166/199 — 0 regresiones**. 2 movimientos sin cambio de pass/fail,
  ambos coherentes con el mecanismo (metadata presente → acquisition_assurance
  sube → trust sube): VIGIA-MAGNET-2022-iOS-JESS NOISE→SUSPICION (expected
  INTENT: **un escalón más cerca del ground truth** — era FN documentado) y
  VIGIA-CTF-2021-iOS NOISE→MALICE (expected UNKNOWN, auto-pasa; salto de 3
  bandas anotado para revisión de etiqueta en Tanda C).

**Tests:** `tests/test_validator_schema_aware.py` (10; rojos primero).

---

## B-086 — Pins mobile S2/S3/S4/S5: el arnés previo a B-052-P2 (WHAT_IS_NEXT §1.3) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07) |
| **Severidad** | P2 — deuda de arnés; los 3 módulos mobile tenían ≈15% de cobertura vs 77–89% de sus hermanos SIFT |
| **Archivo** | `tests/test_mobile_pins_s2_ladder.py`, `tests/test_mobile_pins_s3_timestamps.py`, `tests/test_mobile_pins_s4_s5_safe_helpers.py` (nuevos); fixes S4/S5 en los 3 módulos mobile |
| **Antecedente** | AUDITORIA_COBERTURA_MOBILE_SIFT (patrones S2–S5); decisión de Anna: arnés antes que Grupo B |

**Propósito:** red de seguridad para B-052-P2 (`to_signal()` → `to_signals()`
cambia TODOS los veredictos mobile). Con las escaleras fijadas rama por rama,
una regresión rompe con diff legible, no como corpus opaco.

**S2 — escaleras completas (52 pins):** las 13 ramas iOS + 11 Android + 14
macOS con inputs mínimos exactos; el cruce `opsec_bump` 3.0→3.4 sobre el
umbral estricto >3 (el que el audit señaló sin fijar) queda pineado como
comportamiento vigente; interplay B-072 (parsed=False no minimiza), techos
reales (3.9 iOS / 4.2 Android < Z_CLIP), cap de confidence, value=z/5.
**Cazador de ramas muertas:** todo finding_type que la escalera LEE debe
tener emisor fuera de to_signal — hoy 0 muertas (B-073/074 cerraron las
conocidas); el pin impide reintroducir la clase.

**S3 — bordes de banda de timestamps (28 pins):** cada borde EXACTO de
`_chrome_ts_to_unix` (>1e15/1e12/1e10, WebKit) y `_coredata_to_unix`
(>1e17/1e14/1e11, Core Data ×2) + `_cocoa_ts_to_unix` (float trunca);
pin de acuerdo iOS≡macOS (implementaciones gemelas); ts≤0/None → 0. Los
umbrales difieren entre módulos A PROPÓSITO (épocas distintas) — una
"unificación" ingenua dispara acá.

**S4 — `_safe_rglob` acotado (fix + 18 pins):** materializaba y ordenaba el
árbol ENTERO antes del slice — el limit no protegía la memoria. Ahora
`heapq.nsmallest` (memoria O(limit)) con salida IDÉNTICA — los pins de
contrato (primeros N en orden global, symlinks/dirs excluidos, no-dir → [])
son el testigo de la equivalencia. Los call-sites con `Path.rglob` directo
(ios:269/604/608/641, android:240/360-362) quedan para la sesión B-052-P2:
migrarlos cambia semántica de detección y ahora existe el arnés para hacerlo.

**S5 — `_safe_plist_load` con techo (fix + 6 pins):** un plist VÁLIDO pero
gigante se cargaba entero (bomba de memoria). `_PLIST_MAX_BYTES=8MiB`,
rechazo ANTES de parsear, logueado a WARNING (degradación honesta §5.3 — "no
pude leer" ≠ "no hay persistencia"). Test rojo primero (2 rojos pre-fix).

**Inducción:** suite **980 passed** (+104). Cobertura: ios 41.5%, android
38.4%, macos 44.5% (desde ≈15%). Corpus **166/199, 0 flips nuevos** (los 2
movimientos observados son los ya documentados en B-085).

---

## B-087 — Grupo B, tanda completa: B3/B4/B7/B8/B9 (5 fixes acotados sin doctrina) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07), commits `7ce09e5`, `2f9ee9b`, `1fc85d3`, `2572958`, `3737946` |
| **Severidad** | P1–P3 según ítem |
| **Antecedente** | PLAN_ABDUCTIVO_PENDIENTES §2 Grupo B; AUDITORIA_INVARIANTES_ASIMETRIAS (B-061, A-1, A-2) |

Protocolo por ítem: restore tag, tests rojos primero, suite verde, corpus
166/199, commit propio. Suite final de la tanda: **1034 passed**.

- **B3 / B-016 residual** (`7ce09e5`): detector de formato stderr portado al
  motor V4 de memoria — `classify_vol3_stderr` (lista compartida con el shim)
  + `MemoryImageFormatError` + señal `unanalyzed=True`/confidence=0. Un vol3
  que rechaza la imagen ya no lee "limpio" (falso negativo P0-A). 5 rojos.
- **B4 / B-018 residual** (`2f9ee9b`): `VIGIA_VOL3_TIMEOUT` (valor exacto,
  el perito manda) + escalado por tamaño sin env (≥4 GiB ×2, ≥16 GiB ×4) +
  rastro en pipeline_meta (`vol3_plugin_timeouts`, `vol3_timeout_config`,
  `pipeline_status` completed/timeout_partial/timeout_all) — el caso
  NARCOS-Jane ("0 señales por timeout" vs "limpio") ahora es distinguible
  desde el bundle. 9 rojos.
- **B7 / B-061** (`1fc85d3`): confidence fuera-de-rango FINITO unificado a
  CLAMP en ambas rutas (ebs_v1 + signal_contract; Field sin ge/le, el
  validador clampea) — el mismo input ya no crashea o no según el
  despliegue. Frontera no-finita B-083/B-083b intacta y pineada; acuerdo de
  las 4 implementaciones pineado. 7 rojos.
- **B8 / A-1** (`2572958`): `verify_daubert_record_hash()` — el hash dejó de
  ser decorativo: recomputación con la cuantización U7 del productor,
  estable ante round-trip JSON, fail-closed; self-check en
  `signal_adapter.run_full_pipeline` (una asimetría de serialización rompe
  en el productor, no en el peritaje). 8 rojos (colección).
- **B9 / A-2** (`3737946`): ciclo de vida del honey token —
  `deactivate_honey_token` con auditoría y contención estricta (realpath en
  `_HONEY_TOKEN_DIR` + basename `honey_*`; traversal bloqueado), TTL opcional
  persistido en sidecar `.meta.json`, sweep perezoso de vencidos con
  auditoría (`HONEY_TOKEN_EXPIRED`). 11 rojos.

**Queda del Grupo B:** B1 (requirements-ci contrato de imports), B2 (OOV/
xfail), B6 (ARTIFACT_TYPE_REGISTRY), B10 (comparador lee agent_verdict
sellado), C1/C2 del censo P0-001.

---

## B-088 — `sans_compliance.accuracy_validation` exige clave `tool`, los adaptadores del shim emiten `source` [RESUELTO — ya corregido por F8, verificado y pineado]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (ver header) — nota histórica: no tuvo ID de tracker hasta 2026-07-08 |
| **Severidad** | P2 |
| **Archivo** | `vigia_agent.py:936-942` |
| **Detectado en** | `docs/AUDITORIA_PIPELINE_ROBUSTEZ.md` §3.1, hallazgo **N13** (2026-07-03) |

**Descripción:** `sans_compliance.accuracy_validation` exige la clave `tool`
en cada señal para calcular su flag de compliance. Los adaptadores del shim
(vol3, EBS-JSON, mobile) emiten `source` en lugar de `tool`. El resultado es
un flag de compliance **falso negativo** en todo bundle producido por un
camino de adaptador — el análisis es compliant, pero el flag dice lo
contrario.

**Implicación forense:** un examinador o auditor que lea el flag de
compliance en un bundle de camino adaptador (dumps de memoria vol3, evidencia
mobile, importaciones EBS-JSON) concluiría incorrectamente que el análisis
falló un chequeo de compliance que en realidad pasó. Es un riesgo de falsa
alarma, no un falso negativo sobre el veredicto mismo — el pipeline de
veredicto no consume este flag.

**Camino de fix:** aceptar `source` como alias de `tool` en
`accuracy_validation`, o normalizar la salida del adaptador para que emita
`tool` de forma consistente con los módulos SIFT nativos antes de que corra
el chequeo de compliance. Requiere decidir cuál nombre de campo es canónico
antes de parchear (evitar reabrir una inconsistencia de mapeo de adaptador
estilo B-060).

**Resolución (2026-07-10):** el audit-before-patch contra HEAD encontró el
fix YA aplicado (F8): la expresión aceptaba `(s.get("tool") or s.get("source"))`
con el comentario "F8 (N13) — aceptar ambos". Esta entrada estaba desactualizada
respecto del código. Cierre con protocolo: la expresión inline se extrajo al
helper `_accuracy_validation()` (behavior-preserving, fail-closed sin señales o
sin z_score) y se pineó con 4 tests de regresión
(`TestB088AccuracyValidationSourceAlias`). Verificado en superficie Mode 1: los
199 bundles del corpus emiten el flag correcto (198 True; 1 False pre-existente
y legítimo, idéntico en baseline). Gate comparativo: 0 flips en verdict, score,
accuracy_validation, n_primary, n_unanalyzed y n_total.

---

## B-089 — `_to_signal_safe` descarta señales silenciosamente ante cualquier excepción de `to_signal()`, sin marca `unanalyzed` [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (ver header) — nota histórica: no tuvo ID de tracker hasta 2026-07-08 |
| **Severidad** | P2 |
| **Archivo** | `vigia/sift:267-275` |
| **Detectado en** | `docs/AUDITORIA_PIPELINE_ROBUSTEZ.md` §3.1, hallazgo **N14** (2026-07-03) |

**Descripción:** `_to_signal_safe` captura cualquier excepción lanzada por
`to_signal()` y retorna `None` con una entrada de log — nada más. La señal se
pierde silenciosamente: no se setea marca `unanalyzed=True` (el mecanismo que
`_to_signal_safe` saltea), así que el conteo de `unanalyzed_artifacts` tampoco
la ve. Es la misma clase de falla que N7 (crashes de motores SIFT tragados sin
marca), pero en el paso de conversión resultado→señal en lugar del paso del
motor.

**Implicación forense:** un artefacto cuya conversión `to_signal()` crashea
desaparece del bundle exactamente como si nunca hubiera existido — sin rastro
en la narrativa, sin rastro en el conteo de artefactos no analizados. Es el
mismo hueco de cobertura silencioso que se corrigió para N7/N8 (Tanda 1/F7 en
`docs/AUDITORIA_PIPELINE_ROBUSTEZ.md`) — F7 cubrió crashes a nivel motor y
rechazos de PathGuard; este camino a nivel conversión no quedó incluido en ese
fix.

**Camino de fix:** ante una excepción de `to_signal()`, emitir una señal
sintética `*_UNANALYZED` (el mismo mecanismo que F7 ya construyó para crashes
de motor) en lugar de retornar `None` a secas, para que el artefacto sea
visible en `unanalyzed_artifacts`/la sección "ARTEFACTOS NO ANALIZADOS" de la
narrativa.

**Resolución (2026-07-10):** el audit contra HEAD encontró un fix PARCIAL
posterior a la auditoría (F8: el drop se contabiliza en
`results["signal_conversion_drops"]` + `pipeline_meta`), pero el hueco central
seguía: `return None` → sin señal `*_UNANALYZED`, el artefacto no entraba en
`n_unanalyzed_artifacts` ni en la narrativa. Fix aplicado exactamente como
proponía esta entrada: ante excepción de `to_signal()`, `_to_signal_safe` emite
`self._unanalyzed_signal(method_name, ...)` (mecanismo F7: z=0, conf=0,
`unanalyzed=True`, `signal_class=derived` — invisible para los gates, visible
en el bundle) y CONSERVA el contador F8. **Distinción doctrinal** (hallazgo del
code-review de este mismo fix): el stub se emite SOLO para conversiones de
motores PRIMARIOS; las conversiones DERIVADAS (metabolic/resonance/behavioral/
patterns/timeline/adversarial) mantienen el contador F8 sin stub — F7 nunca
marcó crashes de motores derivados, y "falló una síntesis" no es "evidencia sin
analizar": un stub derivado degradaría NOISE→ABSTAIN sin pérdida de evidencia
real. Tests rojos primero (`TestB089ToSignalCrashVisible`, 5 tests: señal
emitida, drop contado, nunca primaria, camino sano intacto, derivadas sin
stub). Gate comparativo 199 casos: 0 flips en los 6 campos comparados (el
corpus no produce crashes de conversión — el fix solo cambia el comportamiento
ante fallas).

**Alcance restante — CERRADO (2026-07-10, mismo protocolo):** los adaptadores
mobile del shim raíz (`/sift_orchestrator.py::_analyze_mobile`) emiten ahora
`_unanalyzed_marker(engine, e)` en sus 4 `except` (dict F7-shape: z=0,
`unanalyzed=True`, `signal_class=derived`). Medido pre-fix: un crash del
analyzer con solo evidencia mobile caía al orquestador real con 0 señales y
sellaba `UNDETERMINED` con **`n_unanalyzed_artifacts: 0`** — el bundle
afirmaba "0 artefactos sin analizar" con el 100% de la evidencia sin analizar.
Post-fix: la rama mobile-only expone `results.unanalyzed_artifacts` (misma
vía que consume `_signal_stats`), la narrativa agrega `[FIRSTNESS-LOSS]`, y
`_merge_mobile_signals` lleva los marcadores al resultado base en el camino
mixto. **El veredicto NO cambia** (ABSTAIN en ambos mundos — verificado con
`classify_agent_verdict`); cambia la trazabilidad de la pérdida (§5.3). El
marcador z=0 no puede disparar la escalación del merge (umbral >3, test lo
pinea). 7 tests rojos primero (`TestShimMobileUnanalyzed`). Gate comparativo
199 casos: 0 flips en verdict/score/n_primary/n_unanalyzed/n_total.

---

## B-090 — UNIFIED_TIMELINE emite señal derivada aun con `timestamps=0` [RESUELTO — por F5, verificado con reproducción]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (ver header) — nota histórica: no tuvo ID de tracker hasta 2026-07-08. Marcado explícitamente "⏳ abierto" en la propia tabla de estado de la auditoría fuente, ítem **P2-E** |
| **Severidad** | P2 |
| **Archivo** | `sift_orchestrator.py` — cableado del motor `UNIFIED_TIMELINE` |
| **Detectado en** | `docs/AUDITORIA_PIPELINE_ROBUSTEZ.md` §3.2 |

**Descripción:** el motor `UNIFIED_TIMELINE` emite una señal derivada
independientemente de si efectivamente encontró eventos con timestamp
(incluido el caso `timestamps=0`). Esa señal derivada cuenta para el gate
`≥3 señales` del reasoner y para el gate `n_signals<3 → ABSTAIN` de
`classify_agent_verdict` igual que una señal respaldada por evidencia real —
el mismo patrón de inflación documentado y parcialmente corregido bajo **N4**
(Tanda 1/F5, tagging `signal_class`: SIFT=primary,
engine/timeline/adv/unanalyzed=derived). F5 marca la señal como `derived`, lo
cual la excluye de los gates de señal primaria en los casos que N4 cubre —
pero la auditoría fuente lista P2-E como aún abierto después de que F5 se
aplicó, lo que significa que el caso específico de timeline vacío de
`UNIFIED_TIMELINE` no quedó confirmado como cerrado por ese fix.

**Implicación forense:** un caso cuya única "evidencia" para cruzar el gate de
conteo de señales sea una derivación de timeline vacía no debería poder
contribuir a un veredicto no-ABSTAIN. Requiere re-verificación contra el
tagging `signal_class` actual para confirmar si F5 ya cerró esto o si el caso
específico de timeline vacío todavía se filtra.

**Camino de fix:** re-correr la reproducción de N4/F5 de
`docs/AUDITORIA_PIPELINE_ROBUSTEZ.md` §1 contra el HEAD actual con un caso de
timestamp cero. Si el tag `derived` ya lo excluye, cerrar como
RESUELTO-por-F5 y actualizar esta entrada. Si no, condicionar la emisión de
señal de `UNIFIED_TIMELINE` a `timestamps>0`, o asegurar que el tag `derived`
también se aplique acá.

**Resolución (2026-07-10):** re-verificación contra HEAD con la reproducción
que esta entrada exigía (señales SIN timestamp → `build_timeline` →
`to_signal`): la señal SÍ se emite (z=0, `total_events>0`), pero el wiring
(`sift_orchestrator.py`, `_mark_derived` en la conexión del motor) la etiqueta
`signal_class=derived` y `_is_primary_signal` la excluye del gate `<3` y del
override L-036 — el contrafáctico sin tag daría `True` (el hueco que P2-E
temía). **Cerrado como RESUELTO-por-F5**, pineado con 4 tests dedicados (+1 compartido con B-093) en
`TestB090EmptyTimelineExcludedFromGates`, incluido el gate real vía
`_signal_stats` (2 primarias + timeline vacía = n_primary 2).

Hallazgo adyacente durante la reproducción → **B-093** (metadata=None
crasheaba `build_timeline`; la timeline desaparecía del bundle en silencio).

---

## B-108 — `UnifiedTimelineEngine` crashea con `metadata=None` y la timeline desaparece del bundle en silencio [RESUELTO]

> **Nota de numeración (2026-07-11, precedente L-029/L-051):** registrado
> originalmente como B-093 (2026-07-10), en colisión con el B-093 de la banda
> mobile (2026-07-09, cronológicamente anterior — conserva el número).
> Renumerado a B-108; los mensajes de commit conservan el número viejo.

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-10), test rojo primero |
| **Severidad** | P3 — robustez; la señal timeline es derivada (no afecta veredicto), pero su pérdida era silenciosa |
| **Archivo** | `vigia/sift/unified_timeline_engine.py` (`_extract_timestamp`, `_extract_entity`, `build_timeline`) |
| **Detectado en** | Reproducción de B-090 (2026-07-10) — el test de timeline vacía crasheó con una señal legal |

**Descripción:** `metadata=None` es el default legal del contrato
`SignalOutput` (EBS v1), pero `_extract_timestamp` / `_extract_entity` /
`build_timeline` hacían `signal.metadata.get(...)` sin guard →
`AttributeError`. El wiring del orquestador envuelve `build_timeline` en
`try/except` que solo loggea: UNA señal sin metadata hacía desaparecer la
timeline ENTERA del bundle sin marca alguna — la misma clase de pérdida
silenciosa que N7/N14, un nivel más arriba.

**Fix:** guard `isinstance(signal.metadata, dict)` en los tres puntos de
acceso (default `{}`). Sin cambio de comportamiento para señales con
metadata. Test rojo primero
(`TestB090EmptyTimelineExcludedFromGates::test_none_metadata_signal_does_not_crash_timeline`).
Gate comparativo 199 casos: 0 flips (ninguna señal del corpus llega sin
metadata al motor; el fix solo cubre el caso de falla).

---

## B-091 — R4-3: saturación por dominio de recolección en el scorer EBS [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-07) |
| **Severidad** | P1 — 95 logs irrelevantes compraban MALICE (drowning por volumen del mismo canal) |
| **Archivo** | `vigia_scorer.py` (etapa 2 + gate B-068 v2), `vigia/tools/caie.py` (classify_domain v2 revivido) |
| **Antecedentes** | docs/TAXA_DOMINIOS_RECOLECCION.md (taxonomía v2, CR-001..004); docs/BASELINE_TRIPLE_CASTIGO.md (curvas pre-fix) |
| **Diseño** | Aprobado por el colectivo (6 modelos): Noisy-OR asume independencia; 100 logs del mismo tipo no son 100 fuentes |

**Arquitectura final (4 corridas comparativas — el gate B-069 rechazó 3 diseños intermedios):**
1. `classify_domain()` revivido en caie.py con la taxonomía v2 (53 tipos + los
   6 de código; sub-bandas D1a/D1b, D5-hard/media/soft; era código muerto con
   `log_entry→"network"`). Nuevo `classify_domain_subband()`.
2. **Etapa 1 BIT-EXACTA al legacy M2-1** (mejor-prefijo por tipo): las
   corridas probaron que la cabeza no puede desviarse — el corpus contiene
   gemelos de FORMA idéntica con etiquetas opuestas (CAN-018 MALICE vs
   CAN-032 SUSPICION: ambos 3× memory_process + 1 ip_geolocation) que solo el
   score calibrado separa; y CAN-029 exige que lsass NO se agrupe con
   memory_process en la cabeza.
3. **Etapa 2 (R4-3): decay DE COLA por sub-banda** — posiciones 1-4 intactas,
   de la 5ta en adelante w=r^(pos-4) (D1a/D5-soft/D0 r=0.5; D1b/D2/D3/D4
   r=0.7). EXENTOS: D5-media/hard (costo por-artefacto: 10 binarios SON 10
   actos — FLAREON) y artefactos sin evidence_type (schema narrativo SRL; la
   corrida 3 mostró que saturarlos aplasta 14 MALICE). Monotonicidad M2-1
   preservada (pins verdes).
4. **Gate B-068 v2 — tres ramas doctrinales** (la corrida 1 probó que
   "≥2 dominios" a secas es a la vez más estricto y más laxo que el legacy):
   cross-domain con masa (≥2 dominios Y ≥4 arts o ≥3 tipos), masa dura
   (≥3 tipos o ≥4 artefactos con spoofability ≤0.30 — CAN-029), costo
   por-artefacto (≥4 D5-hard/media — FLAREON). Un canal blando solo no abre
   ninguna. Trazabilidad: `r43_domain_scores`/`r43_active_domains` en el
   resultado.

**Criterios de aceptación (todos cumplidos):**
- BREAK-014: MALICE 0.3867/conf 0.77 → **SUSPICION 0.2322/conf 0.46** ✓
- Curva post-fix PLANA: N=25/50/95 logs irrelevantes → score 0.2322 constante
  (pre-fix: +0.0016/log hasta cruzar MALICE) ✓
- 95 logs solos: SUSPICION 0.1888 → **NOISE 0.0109** ✓
- Los 96 MALICE correctos: **0 regresiones** ✓
- Corpus **166 → 167/199** (UN solo flip: BREAK-014 a PASS) ✓
- Suite **1049 passed** (16 tests nuevos rojos-primero en
  `tests/test_r4_3_domain_saturation.py`) ✓

**Registro de diseños rechazados por el gate comparativo (disciplina B-069):**
r=0.5 uniforme (corrida 1: 153/199, 13 regresiones — FRS crudo además viola
monotonicidad); dos-completos + r por sub-banda (corrida 2: 164/199, 4 FPs
nuevos: trío 2.7 vs 2.1 legacy); regla de calificación del 2do dominio por
spoofability (corrida 3: 131/199 — aplastó narrativos SRL y CAN-MALICE);
cabeza posicional (1,0.7,0.4,0.1) sin best-prefix (corrida 4: 165/199, el par
CAN-029/CAN-032 se cruza). La lección: la cabeza estaba CALIBRADA; solo la
cola era el defecto.
---

## B-092 — browser_forensics ignoraba el WAL de SQLite (`immutable=1`): rows solo-WAL de Chromium/Firefox invisibles [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-09, test rojo primero, suite 1065 passed, gate comparativo 166/199 → 166/199 con 0 flips (neutralidad estructural, ver abajo) |
| **Severidad** | P1 — clase de falso negativo: hasta el 100% de la señal de un perfil puede vivir solo en un `-wal` no checkpointeado |
| **Archivo** | `vigia/sift/browser_forensics.py` (`_connect_ro` → `_connect_evidence` vía `safe_sqlite_connect`, helper B-071) |
| **Detectado** | `docs/SAFARI_WAL_FIX_ANALYSIS.md` §5.2 — la auditoría del hallazgo WAL de Safari localizó acá la conexión legacy superviviente |
| **Tag de restauración** | `pre-b071-browser-wal-20260709-202353` |

### Descripción

`_connect_ro` abría las DBs de evidencia con `mode=ro&immutable=1`, que
nunca lee el sidecar `-wal`. Una `History` de Chromium o `places.sqlite` de
Firefox en modo WAL con transacciones sin checkpoint (estado normal de una
máquina viva al adquirirla) se leía como si esos rows no existieran — la
misma clase de falso negativo cuantificada sobre el artefacto macOS real
(`cases/tuck-2019-macos`): 48/198 URLs y 23/23 findings vivían solo en el
WAL, es decir el 100% de la señal de ese artefacto. macOS/iOS/Android ya
usaban el helper B-071; browser_forensics (ruta Windows Chrome/Edge/Firefox)
era el último módulo en la conexión legacy.

### Fix aplicado

- `_connect_ro` borrado; el nuevo `_connect_evidence` delega en
  `safe_sqlite_connect(db, "BROWSER", logger)` (working copy + familia
  completa de sidecars + WAL aplicado; evidencia intacta).
- El retorno `None` (fallo de apertura/copia a nivel OS) eleva
  `sqlite3.DatabaseError` para que `analyze_profile` marque el perfil
  `UNANALYZED_ARTIFACT` — nunca "limpio con 0 hallazgos" (patrón N7/N8).
- Docstring de `analyze_profile` actualizado (prometía `immutable=1`).

### Validación

- **Rojo primero:** `tests/test_browser_wal_visibility.py` (5 tests) —
  fixtures WAL de laboratorio (declaradas como tales): rows de
  downloads+urls (Chromium) y moz_places (Firefox) escritos solo al `-wal`
  (writer abierto, misma receta que `test_b071_sqlite_readonly.py`).
  Pre-fix: 3 fallaron exactamente en el FN (perfil reportado limpio).
  Post-fix: 5/5 verdes, familia de evidencia verificada intacta por hash.
- Suite: 1065 passed, 7 xfailed, 0 fallos (tests/ + vigia/tests/, e2e
  excluido — depende del sandbox).
- **Gate comparativo (ambos brazos corridos localmente):** baseline en el
  tag de restauración 166/199; post-fix 166/199; diff por caso: 0 fixed,
  0 broken, 0 movimientos de veredicto. La neutralidad es estructural, no
  suerte: los 199 casos del batch son narrativas JSON — ninguno rutea un
  perfil de navegador crudo con sidecar WAL, así que esta ruta no puede
  mover el corpus en ningún sentido. La evidencia discriminante del fix es
  el test rojo, mismo estándar que B-071.

---

## B-093 — Banda mobile de EVIDENCE_PROFILES sin entrada en _DOMAIN_MAP: exenta del decay R4-3 [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-09), aplicado con gate comparativo (patrón B-069) |
| **Severidad** | P2 — el vector de drowning de BREAK-014 (L-049) seguía abierto para la vía mobile |
| **Archivo** | `vigia/tools/caie.py` (`_DOMAIN_MAP`), `tests/test_r4_3_domain_saturation.py` |
| **Antecedentes** | `docs/MACOS_MODULES_DESIGN.md` §9.1-b (donde se detectó y razonó el mapeo); `docs/TAXA_DOMINIOS_RECOLECCION.md` (el censo fue sobre `data/cases/`, donde la banda mobile no aparece — "ningún tipo queda en UNKNOWN" era cierto solo para el corpus) |
| **Detección** | Re-mapeo del diseño macOS contra TAXA v2: los 8 tipos mobile calibrados en `EVIDENCE_PROFILES` (caie.py: `chat_message`, `sms`, `call_log`, `web_search`, `app_data`, `social_media`, `location_data`, `contact_data`) clasificaban `UNKNOWN:<tipo>` / banda `UNKNOWN` |

**Consecuencias medidas pre-fix (las dos):**

1. **Exentos del decay de cola R4-3** (el loop de saturación salta banda
   UNKNOWN): flood sintético de `web_search` raw 0.85 → score 0.5454 (N=10),
   0.9806 (N=50), **0.9900 (N=100)** — crecimiento sin límite, la curva que
   R4-3 mató para `log_entry`. Peor: **100× web_search de raw 0.05 (ruido
   puro) FABRICABA SUSPICION 0.3566** — el análogo exacto del hallazgo de
   BASELINE_TRIPLE_CASTIGO ("50 logs de nada fabricaban SUSPICION").
2. **Sesgo pro-MALICE en el gate B-068 v2**: cada `UNKNOWN:<tipo>` cuenta como
   dominio propio — `UNKNOWN:web_search` + `UNKNOWN:app_data` + D3 = 3
   "dominios" de artefactos que en realidad comparten el mismo canal de
   fabricación (disco local, user-space), abaratando la rama cross-domain.

**Fix (asignación por modo de fabricación, TAXA §1 — el canal, no el contenido):**
`web_search`, `app_data`, `contact_data`, `call_log`, `sms`, `chat_message`,
`location_data` → `("filesystem_metadata", "D3")` — registros locales en disco
escritos por apps en user-space, fabricables editando el archivo (un loop
inserta N filas en el SQLite; sin costo por-artefacto ni tamper-evidence).
`social_media` → `("network_telemetry", "D4")` — registro del lado del
servicio, no fabricable editando el disco local. Nota `location_data`: el tipo
cubre el cache local del dispositivo; telemetría de OPERADOR debe tipificarse
distinto, no reclasificar este tipo.

**Criterios de aceptación (todos cumplidos):**
- 4 tests rojos-primero (`TestMobileBandDomainMap`): clasificación de los 8
  tipos, curva plana del flood, ruido puro → NOISE, monotonicidad M2-1 ✓
- Curva post-fix PLANA: web_search raw 0.85 → 0.3776 / 0.3903 / **0.3903**
  (N=10/50/100, asíntota r=0.7 de D3); raw 0.05 ×100 → **NOISE 0.0276** ✓
- **Gate comparativo (B-069) sobre los 199 casos: 0 flips de verdict, 0 flips
  de score — los 199 resultados son idénticos byte a byte; el pass-rate del
  corpus queda invariante en 167/199** — predicho (la banda mobile no aparece
  en el corpus JSON) y verificado con baseline limpio (fix stasheado) vs
  after. Nota de alcance: precisamente porque el corpus no ejercita la banda,
  el gate solo prueba NO-regresión; la cobertura positiva del mapeo son los
  tests sintéticos ✓
- Suite completa verde ✓

**Alcance restante (no cubierto por este fix — medido, no especulado):**

1. **Engines mobile SIFT**: siguen emitiendo UNA señal agregada tipificada
   `app_data` vía `_EVIDENCE_MAP` (B-052-P2 pendiente); B-092 solo garantiza
   que cuando esas señales (o casos EBS mobile futuros) lleguen al scorer,
   saturen y corroboren por el canal correcto (D3) en vez de por dominios
   fantasma UNKNOWN.
2. **Rama hard-mass del gate — `location_data`**: su spoofability calibrada
   (0.30) está exactamente en el borde `<=0.30` que la rama hard-mass cuenta
   como tipo duro. Medido post-fix: 4× `location_data` raw 0.85 → **MALICE
   0.3649** (×100 → MALICE 0.474 — el composite SÍ satura; el gate abre
   igual). No es regresión (pre-fix daba MALICE con composite mayor), pero el
   cierre de B-092 es del composite y los dominios fantasma, NO de esta rama.
   Resolverlo es doctrina de calibración (¿location_data merece 0.30? ¿el
   borde debe ser estricto?) — requiere su propio gate comparativo.
3. **Rama cross-domain — mix D3+D4**: 4× `web_search` + 4× `social_media`
   raw 0.85 → **MALICE 0.5051** (2 dominios reales). Tensión documentada: el
   propio perfil de `social_media` lo describe como "Social app client cache
   — editable" (fabricable en disco local), lo que argumentaría D3; el mapeo
   D4 sigue la doctrina "registro del lado del servicio". Si la calibración
   futura lo mueve a D3, este vector colapsa a 1 dominio. Decisión de
   doctrina, requiere su propio gate.
4. **Ruido puro**: verificado que NO alimenta ninguna rama — 100× raw 0.05 →
   NOISE para `web_search` (0.0276), `app_data` (0.0251) y `location_data`
   (0.0356, el tipo duro). Test parametrizado lo pinea.

---

## B-094 — Las fracturas CAIE del path motor mueven el veredicto pero son invisibles en la narrativa sellada [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — POST HACKATHON (2026-07-10), test rojo primero + gate comparativo |
| **Severidad** | P1 — anti-patrón Daubert: veredicto no-NOISE sin explicación en el bundle sellado |
| **Archivo** | `vigia_scorer.py` (retorna `caie_fracture_details`), `sift_orchestrator.py` (`_motor_caie_summary`, `_resolve_hypothesis`, `_analyze_ebs_json`), `vigia_agent.py` (`_generate_narrative`) |
| **Detectado en** | Cierre de B-041 (2026-07-10): red-team de la hipótesis de divergencia N12 entre la CAIE del orquestador (narrativa) y la CAIE viva del scorer (veredicto) |

**Descripción (método abductivo + red-team):** B-041a expuso la CAIE del
ORQUESTADOR (`results["caie"]`, path disk/mixed). Pero el path MOTOR (JSON/EBS,
default de Mode 1 desde B-075) corre su propia CAIE viva en `_vigia_score`,
aplica `fracture_malice_boost` al composite, y luego **descartaba toda la info
de fracturas**: `_analyze_ebs_json` no devolvía `results["caie"]` ni propagaba
`caie_fractures`/`fracture_malice_boost`. Consecuencia sellada.

**Inducción diferencial (CONFIRMADO, `tests/test_b041b_fracture_feedback.py::TestB094...`):**
un caso de 2 artefactos donde una `TEMPORAL_CAUSALITY_VIOLATION` es la ÚNICA
vía a no-NOISE:
- CON fractura → **INTENT**; SIN fractura (orden temporal invertido) → **NOISE**.
- Ambos bundles pre-fix: `caie_fractures`/`fracture_malice_boost` **ausentes**;
  SECONDNESS **idéntico**: "Ninguna señal primaria supera z>2 — sin desviación
  estructural contra baseline". El bundle INTENT no explicaba su propia causa —
  el anti-patrón que CLAUDE.md prohíbe explícitamente ("MALICE sin explicarlo
  con matemática exacta es adivinación").

**Fix (SOLO visibilidad — el veredicto ya usaba la fractura):**
1. `_vigia_score` retorna `caie_fracture_details` (lista tipo/severidad/
   interpretación/ttp) además del conteo.
2. `_motor_caie_summary()` traduce la CAIE viva al shape que consume la
   narrativa (`inner["caie"]`, mismo canal de B-041a), fiel: reporta fracturas
   + boost, NO fabrica structural_verdict/composite que el scorer no computó.
3. `_analyze_ebs_json` (modo motor, si hubo fracturas) expone
   `results["caie"]`; `_generate_narrative` lo renderiza en SECONDNESS y en un
   bloque `--- CAIE (motor) ---` con las fracturas y sus TTP.

**Verificación E2E (Mode 1):** el bundle INTENT ahora muestra "CAIE (viva): 1
fractura(s) contribuyeron al veredicto (boost +0.45)" y lista la TCV con
severity=1.0, TTP T1070.006 e interpretación.

**Gate comparativo (B-069), 199 casos, baseline limpio (fix stasheado):
0 flips en verdict/score/n_primary/n_unanalyzed — 167/199 invariante.** El
corpus emite 0 fracturas (sin artefactos de fabricación), así que el fix es
inerte sobre él y solo activa la narrativa cuando una fractura real dispara.
8 tests (`TestB094MotorPathSurfacesFractures` + pins E2E de narrativa). Suite
1150 passed.

**Nota de alcance:** el otro brazo de la divergencia N12 (¿la CAIE del
orquestador y la del scorer coinciden en el path disk/mixed?) no se ejercita
en el corpus actual (todos van por el path motor JSON) — no verificado.

---

## B-095 — El comparador batch re-deriva el veredicto desde `best_hypothesis` (pre-gate) en vez de leer `agent_verdict` sellado (post-gate) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-10 (cierra B10 del Grupo B, recomendación B-058) |
| **Severidad** | P2 |
| **Archivo** | `run_all_agent.py` (`extract_verdict_from_bundle`); `run_llm_cases.py` (`_fallback_verdict`) |
| **Detectado en** | `docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md` §Grupo B, ítem B10 |

**Descripción:** los dos comparadores de corpus derivaban el veredicto de un
bundle sellado leyendo `pipeline_results.abduction.best_hypothesis` (o el
`AGENT_EXIT` del audit_trail) y mapeándolo con una tabla + prefix matching.
Ambas fuentes son **pre-gate**: son la salida cruda del reasoner. El campo
top-level `agent_verdict` es el veredicto **post-gate** — la salida de
`classify_agent_verdict`, "el mismo camino único que sella agent_verdict y
decide el exit" (CLAUDE.md). Cuando la auto-corrección pre-emisión de VIGÍA
ajusta el veredicto del reasoner (p.ej. el gate de corroboración sube
SUSPICION→INTENT, o baja a ABSTAIN por conteo de señales), las dos fuentes
divergen y el comparador reporta el equivocado.

**Método abductivo:**
- *Hipótesis:* comparador re-deriva pre-gate ⇒ divergencia cuando el gate mueve el veredicto.
- *Deducción:* un bundle con `agent_verdict="INTENT"` y `best_hypothesis="SUSPICION_DETECTED"` debe reportarse INTENT (forma real de `VIGIA-FN-001`).
- *Inducción:* medido sobre `results/agent_batch/` — **60 de 209 bundles sellados divergían** (dominante `sealed=INTENT → comparador=SUSPICION`; también `sealed=ABSTAIN/NOISE → comparador=UNKNOWN`). ~29% de los veredictos propios de VIGÍA mal reportados por el harness.

**Implicación forense:** el informe pass/fail-vs-`expected_verdict` que imprime
el runner batch estaba mal para ~29% de los casos — enmascarando aciertos y
fallos reales del detector detrás de una derivación heurística que no coincidía
con lo que VIGÍA efectivamente selló y por lo que decidió el exit code.

**Fix (2026-07-10):** ambos comparadores leen primero `agent_verdict` sellado y
solo lo aceptan si es un veredicto canónico conocido; cualquier otra cosa
(None, bundle legacy sin el campo, vocabulario futuro) cae a la heurística
previa, preservando la compatibilidad byte a byte con los 82/291 bundles legacy
sin sellar.

**Verificación:** red test primero (`tests/test_b10_comparator_reads_sealed_verdict.py`,
14 tests: divergencia sellado/pre-gate + invariante legacy + segunda ubicación
`_fallback_verdict`). E2E sobre el corpus real: **60 → 0 divergencias** en los
209 sellados; 82 legacy intactos. Suite completa verde. `git diff` de producto:
+11 líneas en `run_all_agent.py`, +7 en `run_llm_cases.py`; sin tocar scoring,
gates ni doctrina de corroboración.

**Higiene adjunta (B11):** removido `tests/test_audit_no_default_key (1).py`,
duplicado byte-idéntico de `tests/test_audit_no_default_key.py` (artefacto de
copia con sufijo " (1)") — los 12 tests corrían dos veces.

---

## B-096 — `windows_event_log` ausente de `_LAYER_MAP`/`_ONTOLOGY_MAP`: la señal primaria de event log cae a DISK_MFT en vez de REGISTRY [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-10 (cierra B6 del Grupo B; enforcement del acoplamiento B-060) |
| **Severidad** | P2 |
| **Archivo** | `vigia/core/forensic_adapter.py` (`_LAYER_MAP`, `_ONTOLOGY_MAP`) |
| **Detectado en** | B6 — test de consistencia de mapas de tipos (`docs/B6_ARTIFACT_TYPE_REGISTRY_DESIGN.md`) |

**Descripción:** el `EventLogCorrelator` emite una señal **primaria** con
`metadata["artifact_type"] = "windows_event_log"`
(`vigia/sift/sift_orchestrator.py:472`), pero `_LAYER_MAP`/`_ONTOLOGY_MAP` solo
contenían la clave `"event_log"`. Sin la clave, `signal_to_abductive_record`
hacía `_LAYER_MAP.get("windows_event_log", DISK_MFT)` → **DISK_MFT (peso 4/10)**
cuando el tratamiento consistente con `"event_log"` es **REGISTRY (6/10)**.
`abductive_reasoner_v2.py:396` usa `weight = LAYER_EPISTEMIC_WEIGHT[art.layer]`,
así que un log de eventos de Windows quedaba sub-ponderado ~33% en la capa
abductiva del path on-disk. Es la clase exacta de deriva silenciosa que B-060
(Lente 7/8) describió: dos namespaces de mapas (`artifact_type` y
`evidence_type`), varios mapas, y un tipo no cubierto degrada al peor default.

**Método abductivo:** el test de enforcement B6 (variante «test que falle si un
`artifact_type` emitido no está en todos los mapas», propuesta original de
B-060) enumeró por scan estático los tipos que los motores emiten y comparó
contra los mapas. De 7 tipos no mapeados, 6 son derivados z=0 / latentes
(inocuos, grandfathered con justificación); `windows_event_log` era el único
**activo** — señal primaria con z libre.

**Blast radius:**
- **Corpus JSON (motor): inerte.** Ningún artefacto del corpus (0/259) setea
  `metadata.artifact_type`; el bridge puebla `evidence_type` pero no
  `artifact_type`, así que toda señal del motor cae a `"unknown"→DISK_MFT`,
  invariante al agregar la clave. **Gate comparativo (run_all_agent, baseline
  stasheado vs fix): 0 flips en 291 bundles** (verdict/n_primary/n_unanalyzed).
- **Path on-disk (SIFT orquestador): corregido.** Única ruta donde el gap estaba
  activo; sin caso on-disk de event log en el corpus, se cubre por unit test
  end-to-end (`signal_to_abductive_record` → `layer == REGISTRY`).

**Fix (2026-07-10):** agregar `"windows_event_log"` a `_LAYER_MAP` (→ `REGISTRY`)
y `_ONTOLOGY_MAP` (→ `TECHNIQUE`), idéntico a `"event_log"`. Cambio puramente
aditivo (no modifica ninguna clave existente).

**Enforcement (B6):** `tests/test_b6_artifact_type_map_consistency.py` (10 tests):
`_LAYER_MAP`≡`_ONTOLOGY_MAP`; cierre de `_EVIDENCE_MAP` en
`EVIDENCE_PROFILES`∩`_DOMAIN_MAP`; todo `artifact_type`/`evidence_type` emitido
mapeado o grandfathered con justificación; honestidad del grandfather (sin
entradas muertas ni ya-mapeadas). Un motor nuevo que emita un tipo no cubierto
ahora rompe el test en vez de degradar en silencio. No cierra el acoplamiento
estructural (siguen los dos namespaces); cierra la deriva silenciosa.

---

## B-097 — Path motor: colapso SUSPICION→INTENT en el sellado [APLICADO 2026-07-10 — firma Anna, triple fuente]

| Campo | Valor |
|-------|-------|
| **Estado** | APLICADO — 2026-07-10 con firma de Anna (validación por triple fuente independiente), tras el rechazo inicial del gate pre-registrado (`fixed>=1 AND broken==0`, fixed=30 / broken=3, fix revertido en esa primera sesión). Los sentinelas `xfail(strict=True)` de `tests/test_b097_motor_suspicion_verdict.py` pasaron a guardas de regresión normales. Ver "ACTUALIZACIÓN 2026-07-10" abajo; el rastro del rechazo se conserva como historia de auditoría. |
| **Severidad** | P1 (métrica de corpus y semántica de veredicto) — resultado negativo documentado |
| **Archivo** | `vigia_agent.py` (`classify_agent_verdict`) — editado y revertido |
| **Detectado en** | Observación registrada en `docs/B052_P2_DESIGN.md` §10.1 (sesión enforcement §9.4-LIM) |
| **Tag de restauración** | `pre-session-20260710-141412` |

### Causa raíz (investigada caso por caso, 33/33 uniforme)

El motor (`_vigia_score`) calcula **SUSPICION**; B-075 lo mapea a la hipótesis
`SUSPICION_DETECTED`; `classify_agent_verdict` la sube a **INTENT**
(`"SUSPICION" in hyp → INTENT`) porque históricamente SUSPICION no era un
veredicto sellado. Verificado re-corriendo los 33 casos afectados: TODOS
tienen `best_hypothesis=SUSPICION_DETECTED`, fuente `ebs_v1_json_adapter`.
**Ningún caso es de la causa alternativa** (motor calculó INTENT de verdad /
etiqueta mal puesta) — con la salvedad de los 3 broken (abajo), cuya etiqueta
INTENT parece correcta y cuyo motor sub-puntúa.

### Hallazgo colateral CRÍTICO — corrección del baseline

El "167/199" reportado como accuracy vigente en sesiones recientes venía del
`_batch_summary.json` **stale committeado** (restaurado por `git checkout --
results/` tras los gates), NO de las corridas reales. El baseline honesto
post-B10 es **140/199**: el comparador pre-B10 "aprobaba" ~30 casos leyendo la
hipótesis pre-gate (SUSPICION) cuando el veredicto sellado era INTENT — la
métrica 167 estaba inflada por el bug del comparador que B-095 cerró. B-095 no
cambió ningún veredicto; volvió la métrica honesta y destapó B-097.

### Qué se intentó y qué midió el gate

Fix mínimo label-blind: en `classify_agent_verdict`, hipótesis con SUSPICION
(sin INTENT/MALICIOUS) sella `SUSPICION` directamente (posible desde que
§9.4-LIM introdujo SUSPICION como veredicto sellado con `EXIT_INTENT` y piso
de alerta MEDIUM).

**Gate autoritativo (run_all_agent completo, before/after, 0 flaky):**

```
ACCURACY : before 140/199  →  after 167/199   (neto +27)
FIXED    : 30 (todos exp=SUSPICION, INTENT→SUSPICION)
BROKEN   : 3  (todos exp=INTENT,    INTENT→SUSPICION):
             VIGIA-MAGNET-2014-TIMELINE
             VIGIA-MAGNET-2022-IOS-JESS-KEYCHAIN
             VIGIA-MAGNET-2022-iOS-JESS
Flips de veredicto totales: 49 (incluye 16 que siguen FAIL pero pasan
INTENT→SUSPICION, p.ej. exp=MALICE — se alejan de la etiqueta sin cambiar
pass/fail)
```

**Regla pre-registrada:** `fixed>=1 AND broken==0 → aplicar; si no NOT
APPLIED`. broken=3 ≠ 0 → **NO APLICADO** (fail-closed, sin excepciones).

### Los 3 broken — la decisión que queda para Anna

Los 3 casos tienen motor=SUSPICION y etiqueta INTENT con narrativas
sustanciales (cluster de 4 artefactos + metadata wiped; keychain GrayKey;
opsec deliberado multi-app). Hoy **pasan gracias al colapso**: el bug los sube
justo hasta su etiqueta — respuesta correcta por la razón equivocada (el motor
los sub-puntúa). Un fix label-blind (B-075/B-076, obligatorio) necesariamente
los mueve. Opciones para desbloquear (decisión de doctrina/ground-truth, no
del agente):
  (a) aceptar el neto +27 (relajar la regla broken==0 para este caso),
  (b) revisar la calibración del motor para esos 3 (que crucen a INTENT por
      mérito propio) y re-correr el gate,
  (c) revisar las 3 etiquetas (¿INTENT o SUSPICION?) — ground-truth, firma
      requerida.

Hasta esa decisión: el colapso persistía (documentado), los sentinelas
`xfail(strict=True)` lo mantenían visible, y la métrica honesta de referencia
era **140/199** (pre-merge de main 2026-07-10; el merge movió el baseline).

**ACTUALIZACIÓN 2026-07-10 (mismo día, sesión posterior) — APLICADO con firma.**
Anna firmó la aplicación del fix, superando la regla pre-registrada original,
sobre la base de validación por TRIPLE FUENTE independiente en los 33 casos:
(1) etiqueta ground-truth = SUSPICION en los 30 recuperados; (2) banda interna
del motor = SUSPICION (0.10<score≤0.33, B-076) — el motor calculaba bien, solo
el sellado colapsaba; (3) batch ciego Claude Code + Cronos (46 casos,
2026-07-10) confirmó SUSPICION en la enorme mayoría. Además: SUSPICION recibe
exit code PROPIO (5) — hasta hoy compartía el 3 con INTENT ("3=intent/
suspicion"), confuso para consumidores; INTENT conserva el 3 (contrato
histórico; grep confirmó cero consumidores externos de códigos específicos).
Los sentinelas xfail se convirtieron en guardas de regresión normales.
Invariante R4-1 verificado explícitamente post-fix: snapshots bit-identical
{10:0.1861, 50:0.1866, 100:0.1866} intactos. Los 3 casos expuestos
(TIMELINE/JESS/JESS-KEYCHAIN, pasaban por accidente del colapso) quedan como
fallos honestos pendientes de corrección de datos (conversión sub-tipificada,
docs/B097_ROOT_CAUSE_ANALYSIS.md §5b). Gate del día en la entrada del commit.

### Divergencias del batch ciego (46 casos) — pendientes de revisión manual, NO accionadas

El contraste ciego Claude+Cronos dejó 7 divergencias que se ANOTAN para
revisión caso por caso posterior (decisión de Anna: sin urgencia, backlog):
- **VIGIA-REAL-MAGNET-2021-IOS-ELI** y **VIGIA-REAL-MAGNET-2022-ANDROID**:
  Claude ciego = INTENT, coincide con el agente CONTRA la etiqueta SUSPICION —
  candidatos a revisión de etiqueta (misma clase que OWL-NEXUS5).
- **VIGIA-REAL-MAGNET-2020-WIN-PAGEFILE-ABSENT**: Claude = MALICE vs gate de
  corroboración que capea (score 0.48, mono-canal D2). Conflicto legítimo
  Claude vs doctrina (ii) — la doctrina gana hoy; revisar si el caso amerita
  excepción de canal duro.
- **VIGIA-2026-DEMO-008**: Claude = MALICE vs etiqueta SUSPICION (Claude más
  severo que etiqueta y motor).
- **VIGIA-LINUX-005**, **VIGIA-REAL-M57-JO-Dec07**, **VIGIA-REAL-M57-PAT-Dec07**:
  Claude = NOISE vs etiqueta SUSPICION — acá la banda interna del motor
  (SUSPICION) le gana a Claude; probable sub-lectura del LLM sobre evidencia
  D2 rala. Nota: los tres casos FP/FN diseñados y el guard H-02 de
  FP-CULTURAL van al backlog normal sin urgencia (decisión 2026-07-10).

### Re-verificación 2026-07-10 (sesión posterior, misma tarde) — gap de sincronización `main` detectado y cerrado

Anna reprodujo el colapso SUSPICION→INTENT con evidencia de volumen sobre
los 199 casos (line-level: `vigia_agent.py:188-189` antes del fix) y lo
reportó como "confirmado". Investigación: el fix YA estaba aplicado y
committeado (`2d7a909`) — pero **solo en la rama de trabajo
`claude/macos-modules-design-xk5ecq`**, nunca mergeado a `main`. La
reproducción de Anna corrió contra `main`, que seguía en `841650e`
(pre-fix) — confirmado línea por línea (`git show origin/main:vigia_agent.py`
mostraba el `if "INTENT" in hyp or "SUSPICION" in hyp: ... else "INTENT"`
original). No es una regresión del fix: es que el fix nunca había llegado a
la rama que se estaba probando.

**Re-validación completa desde cero (no se asumió el resultado previo):**
- Strings exactos del motor re-verificados en código (no supuestos):
  `MALICIOUS_INTENT_DETECTED`, `INTENT_DETECTED`, `SUSPICION_DETECTED`
  (`sift_orchestrator.py:29-30,192-196`) — los tres mutuamente excluyentes;
  la rama `"INTENT" in hyp` y la rama `"SUSPICION" in hyp` del fix no se
  solapan en la práctica.
- R4-1 snapshots bit-identical: 10/10 verde, valores intactos.
- `run_all_agent.py` fresco sobre los 199: **167/199 PASS** (autoritativo,
  leído de `_batch_summary.json`, no de log truncado). Los ~30 casos
  listados por Anna (CAN-014/016/017/032, LINUX-005, NGDC-003,
  NITROBA-M57-001, REAL-005, SET630-001, BREAK_001/003/004/006/007/008/009/
  010, KIWI_001/002, case_002, case_008, REAL-M57-JO/PAT-Dec07, REAL-NFURY)
  **ya no aparecen en la lista de 32 fallos** — todos sellan SUSPICION.
- Honestidad sobre el punto 3 del pedido ("0 flips en los que ya estaban
  bien"): la medición real da **3**, no 0 — TIMELINE, JESS, JESS-KEYCHAIN
  (exp=INTENT, motor=SUSPICION) pasaban por accidente del colapso viejo;
  ya documentados arriba, no son casos nuevos. Se reporta el número real,
  no el esperado.
- Suite completa (`pytest tests/ vigia/tests/ -q --no-cov
  --ignore=tests/integration`): **1242 passed, 6 xfailed, 1 xpassed**.

**Cierre del gap:** `main` fast-forwardeado a `54e3cb6` (incluye B-097 +
corrección de etiqueta OWL-NEXUS5) y pusheado. La rama de trabajo y `main`
quedan sincronizadas — evita que este malentendido se repita.

### Casos FP/FN diseñados para fallar — categorización para decidir tratamiento (NO accionado, solo análisis)

Revisando los `audit_note` de cada caso (no solo la lista), se separan en
clases con implicaciones distintas para "cómo resolverlo":

1. **Requieren un canal de evidencia que VIGÍA nunca tuvo (fuera de alcance,
   no bug):** `VIGIA-FN-001` (exige consultar sistemas de RRHH — ausencia del
   empleado), `VIGIA-FN-002` y `VIGIA-FP-002`/`VIGIA-FP-003` (exigen contexto
   de autorización/Change Management — un sistema ITSM externo que VIGÍA no
   integra). Ningún fix de código los cierra sin agregar una fuente de datos
   completamente nueva — son candidatos a entrada en KNOWN_LIMITATIONS.md
   como límite de alcance permanente, no a "arreglo".
2. **Tensión de calibración ya documentada (L-016) o su gemela:**
   `VIGIA-BREAK-012` (consenso ponderado por confiabilidad de canal vs
   mayoría — L-016) y `VIGIA-BREAK-015` (evidencia "abrumadora" para un
   humano pero `prior_trust` bajo la capa por el gate de corroboración
   Daubert). Resolverlos significa retocar el ladder del scorer o el gate de
   corroboración — cambio de scorer, no de hoy; candidato a L-0XX nuevo
   (BREAK-015) que documente la tensión explícitamente en vez de dejarlo
   como un fallo mudo.
3. **Diagnóstico histórico corregido — no es gap de motor:**
   `VIGIA-FN-003` ya activa la fractura
   `PROCESS_INJECTION_ANTIFORENSIC` sobre regiones RWX y
   `parent-process-mismatch`. El `SUSPICION` actual no significa que el
   detector no corra: el gate B-068 rechaza elevar dos observaciones de la
   misma colección de memoria a corroboración independiente de `MALICE`.
   Véase B-196. Es una adjudicación de suficiencia/procedencia de evidencia,
   no backlog de detector.
4. **Guard H-02 (FP-CULTURAL ×2):** ya rastreado por separado, sin cambio de
   estado hoy.

Recomendación (para decisión de Anna, no aplicada): documentar 1 y 2 en
KNOWN_LIMITATIONS.md/L-0XX (honestidad Daubert — "el sistema no puede, y por
qué" es más defendible que un fallo silencioso repetido en cada corrida del
corpus), dejar 3 en el backlog de motor separado de la doctrina de scoring,
y mantener 4 donde está.

## B-106 — Shadowing del paquete `forensics` rompe la verificación de bundles in-process

> **Nota de numeración (2026-07-11, precedente L-029/L-051):** esta entrada se
> registró originalmente como B-097 en la rama de trabajo, en colisión con el
> B-097 de `main` (colapso SUSPICION→INTENT en el sellado, firmado por Anna,
> cronológicamente anterior). Renumerada a B-106 al mergear; los mensajes de
> commit y los bundles históricos conservan el número viejo — cualquier
> referencia a "B-097 (shadowing)" en commits de la rama apunta acá.

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/pipeline/pipeline.py` |
| **Función** | `VigiaPipeline.load_and_verify()`, `VigiaPipeline.verify_bundle_external()` |
| **Commit fix** | "POST HACKATHON: fix forensics package shadowing in bundle verification (B-097)" (número pre-renumeración; ver nota) |
| **Detectado en** | Auditoría de pipeline 2026-07-10 (`PIPELINE_AUDIT_2026-07-10.md`, punto 6) |

### Descripción

`vigia/core/bundle_builder.py` (y otros módulos) insertan `<repo>/vigia` en
`sys.path` en tiempo de import. Con eso, el nombre top-level `forensics`
resuelve a `vigia/forensics/` — que NO contiene `verify_ebs_v1` — y el
`from forensics.verify_ebs_v1 import verify_bundle` de `load_and_verify()`
crashea con `ModuleNotFoundError` en todo proceso fresco que importe el
pipeline antes que el paquete `forensics/` real (fallo orden-dependiente).
`verify_bundle_external()` además construía el path del script relativo a
`vigia/pipeline/` (`vigia/pipeline/forensics/verify_ebs_v1.py`, inexistente),
por lo que siempre caía al mismo import roto. El fallback del `except
ImportError` re-insertaba un directorio ya presente en `sys.path` (no-op).
La hipótesis original del auditor externo ("import circular / no-determinismo")
fue REFUTADA — no hay ciclo y la resolución es determinística por entry point;
el bug real es el shadowing orden-dependiente.

### Impacto

- La verificación de bundles desde el pipeline estaba rota en todo proceso
  fresco. `tests/integration/test_ebs_v1_integration.py` solo sobrevivía por
  orden accidental de imports intra-archivo.
- Mitigante: el verificador standalone (`forensics/verify_ebs_v1.py` por CLI)
  funcionaba independientemente.

### Fix aplicado

`_REPO_ROOT` explícito (dos niveles sobre `vigia/pipeline/`) +
`_import_verify_bundle()` que carga el verificador por path de archivo con
`importlib` — resolución determinística e independiente del orden de imports.
Regresión: `tests/test_pipeline_verify_import_shadowing.py` (subprocess fresco
con el shadow activo, ambos paths de verificación).

---

## B-098 — H28 (LRCalibrator) funcionalmente muerto por mismatch de nombres + excepts silenciosos

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/pipeline/pipeline.py`, `vigia/core/likelihood_engine.py` |
| **Función** | `VigiaPipeline.__init__()`, `run_vigia()`, `LikelihoodEngine.__init__()` |
| **Commit fix** | "POST HACKATHON: revive dead H28 calibrator path and stop swallowing its failures (B-098)" |
| **Detectado en** | Auditoría de pipeline 2026-07-10 (punto 2) |

### Descripción

H28 derivaba `<nombre>_isotonic.json` desde `calibration_path` con un
`str.replace` ingenuo y buscaba SOLO ese archivo. Ninguna herramienta del repo
lo produce: `scripts/run_calibration.py` escribe `calibrated_lr.json` y
documenta `VigiaPipeline(calibration_path='models/calibrated_lr.json')`. El
enrichment H28 (posterior calibrado en el bundle + recalibración de z-scores
en `run_vigia`) estaba muerto con el flujo documentado, invisiblemente: el
`except` del constructor logueaba "no encontrado" a nivel INFO para CUALQUIER
fallo (incluido archivo corrupto). Además: el except per-señal de `run_vigia`
era totalmente silencioso y el log de resumen contaba señales sin calibrar
como calibradas; `likelihood_engine.py` tenía un `except: pass` literal que
hacía irrecuperable la causa de una degradación a FALLBACK.

### Impacto

- Con el flujo documentado, el posterior nunca se calibraba (H28 no-op
  silencioso). Señales mezcladas calibradas/sin calibrar entraban al sellado
  sin marca ni log honesto.

### Fix aplicado

`_candidate_calibrator_paths()`: derivación suffix-aware (pathlib), variante
`_isotonic` primero (compat), `calibration_path` mismo como fallback (el flujo
documentado funciona). Constructor distingue `FileNotFoundError` (INFO,
degradación documentada) de otras causas (WARNING con causa real); candidato
corrupto no bloquea al siguiente. `run_vigia` cuenta fallos per-señal y reporta
"calibradas N/M + primera causa". `likelihood_engine` loguea la causa del
FALLBACK. Regresión: `tests/test_lr_calibrator_path_resolution.py`.
Nota de comportamiento: quien pase `calibration_path` ahora obtiene la
calibración H28 documentada (antes no-op silencioso); flujos default sin
cambio.

---

## B-099 — Drift interno H27 degenerado: constante 1.0 disfrazada de medición en el decision path

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/pipeline/pipeline.py`, `vigia/core/risk_bounded_layer.py` |
| **Función** | bloques H27 de `run_full()` y `run_vigia()`; nuevo `RiskBoundedDecisionLayer.internal_drift_from_z_scores()` |
| **Commit fix** | "POST HACKATHON: replace degenerate H27 internal-drift PSI with chi2-gated analytic estimator (B-099)" |
| **Detectado en** | Auditoría de pipeline 2026-07-10 (punto 3) |

### Descripción

Los dos bloques H27 computaban un drift interno que saturaba a 1.0 para
entrada benigna y anómala por igual, y esa constante entraba al decision path
sellado (D multiplica el riesgo hasta ×3 en `compute_risk` y puede flipear
ACCEPT→ABSTAIN→REJECT). Medido: el bloque de `run_vigia` (referencia gaussiana
muestreada con seed 42) saturaba el 100% de 20k muestras N(0,1) genuinas a
n=2-3 y 67-100% hasta n=50; el split-half de `run_full` saturaba 82-97% y por
construcción no puede detectar un shift (ambas mitades lo comparten). La
hipótesis del auditor externo culpaba al seed fijo — REFUTADA: el seed era
deliberado (determinismo) e irrelevante; la causa real es el `eps=1e-6` de
`compute_psi` (un bin vacío en una muestra chica dispara PSI > 0.25).

### Impacto

- Sesgo conservador sistemático en Modos 4/CLI/`run_vigia` (riesgo de falso
  REJECT — Daubert-relevante). El Modo 1 (`vigia_agent.py`) no atraviesa este
  código. Bundle real observado con `drift_score=1.0` sellado
  (`VIGIA-REAL-009`).

### Fix aplicado

`internal_drift_from_z_scores()`: referencia analítica por CDF normal (sin
RNG), suavizado Dirichlet (bins vacíos acotados), y descuento del cuantil 0.95
del nulo (~χ²(k−1)/n, que solo ya excede la regla 0.25 para n≤~15). Medido:
falsa saturación ≤2% en datos genuinos; N(2,1) detectado desde n=4 y ~100%
desde n=8; all-z=5 satura desde n=4. Bajo n=4 el estimador no tiene potencia
en ninguna dirección → retorna None y ambos callers caen al drift externo
documentado con log INFO (revierte parcialmente P1-21, umbral 4→2: emitir un
número sin potencia nunca fue anti-evasión). Regresión:
`tests/test_h27_internal_drift.py`. Pendiente operacional: re-baseline de
resultados de corpus producidos con el estimador saturado (ver L-054).

---

## B-100 — Veredicto ABSTAIN cerraba la narrativa con alerta "LOW" de apariencia evaluada

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia_agent.py` |
| **Función** | `_generate_narrative()` (piso de alerta B-065) |
| **Commit fix** | "POST HACKATHON: INDETERMINATE alert for ABSTAIN verdicts + startup dep-drift warning (B-100, B-101)" |
| **Detectado en** | Auditoría de pipeline 2026-07-10 (punto 5); `docs/AUDIT_NARRATIVAS_20260702.md` (FALLO_OCULTO PARCIAL) |

### Descripción

El piso de alerta B-065 cubría MALICE/INTENT/SUSPICION pero no ABSTAIN: un
caso con `best_hypothesis=PIPELINE_ERROR` (o artefactos sin analizar, o
señales insuficientes) cerraba con "LOW (per-signal magnitude)..." — un nivel
de apariencia evaluada sobre evidencia que no fue analizada. 5 bundles
sellados del corpus presentan esa combinación. La línea de reconciliación
además afirmaba "hypothesis-level aggregation" cuando no se agregó nada.

### Fix aplicado

ABSTAIN con magnitud LOW presenta ahora
"INDETERMINATE — ABSTAIN verdict (<hipótesis>): the evidence was not (fully)
analyzed, so no alert level can be asserted." y una línea de reconciliación
específica. NOISE genuino conserva LOW (regresión-testeado). Regresión:
`tests/test_b100_b101_abstain_alert_and_deps.py`.

---

## B-101 — Deriva venv-vs-requirements silenciosa (defusedxml, psutil declaradas pero no instaladas)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (código) — la instalación en el entorno de ejecución real es operacional |
| **Archivo** | `vigia_agent.py` |
| **Función** | nuevo `_warn_missing_critical_deps()` al inicio de `main()` |
| **Commit fix** | "POST HACKATHON: INDETERMINATE alert for ABSTAIN verdicts + startup dep-drift warning (B-100, B-101)" |
| **Detectado en** | Auditoría de pipeline 2026-07-10 (punto 5) |

### Descripción

`defusedxml` y `psutil` están declaradas en los tres manifiestos
(`requirements.txt`, `requirements-ci.txt`, `pyproject.toml`) pero ausentes
del entorno de ejecución. Post-fix del import guarded (2026-07-03), la
ausencia de defusedxml degrada honestamente (XML/EVTX → UNANALYZED → ABSTAIN,
exit 4) pero sin ninguna señal de arranque del PORQUÉ: 10/200 casos del corpus
perdían su señal XML/EVTX en silencio operacional. 5 bundles sellados pre-fix
en `results/` aún contienen el PIPELINE_ERROR original (ver L-054).

### Fix aplicado

Chequeo de arranque ruidoso pero NO fatal en `main()`: WARN a stderr por cada
dependencia crítica declarada y ausente. Se implementó la variante WARN y no
el abort propuesto originalmente en este registro (línea ~802): abortar
contradiría el diseño degrade-not-crash ya testeado
(`tests/test_tanda_a_triage.py`). Regresión:
`tests/test_b100_b101_abstain_alert_and_deps.py`. Nota: la corrección del
changelog V07 (describía un fallback `forbid_dtd` inexistente) va en el mismo
commit.

---

## B-102 — Apilamiento triple de la calibración logística al resucitar H28

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (detectado por code review adversarial en la misma sesión que lo introdujo) |
| **Archivo** | `vigia/pipeline/pipeline.py`, `vigia/core/likelihood_engine.py`, `vigia/core/lr_calibration.py` |
| **Commit fix** | "POST HACKATHON: code review fixes — calibration stacking (B-102), NaN drift (B-103), ABSTAIN alert gaps" |
| **Detectado en** | Code review de 8 ángulos sobre los fixes de la sesión (B-098..B-101 y B-106) (2026-07-10) |

### Descripción

El fix B-098 resucitó las dos piernas H28 que estaban muertas — sin advertir
que la capa del `LikelihoodEngine` (viva desde siempre, `likelihood_ratio.py`
Paso 2) YA aplica `calibrated_log_lr` por señal cuando `mode=CALIBRATED`. Con
el flujo documentado, la misma sigmoide se aplicaba TRES veces: z-scores
reescritos en `run_vigia` → log-LRs calibrados de nuevo por el engine →
posterior re-calibrado por el H28 de `run_full`. Posteriors distorsionados
respecto al corpus con que se ajustó el calibrador, con
`lr_calibration_method='logistic_regression'` sellado reclamando un ECE que
ya no vale. Además los tres loaders resolvían el path de forma divergente
(el de `run_vigia` sin manejo per-candidato: un `_isotonic` corrupto abortaba
la calibración entera; el del engine sin resolución de candidatos: layouts
legacy quedaban en FALLBACK mientras H28 calibraba).

### Fix aplicado

Una sola capa de calibración con fallback explícito: (1) resolución de
candidatos unificada en `candidate_calibrator_paths()`
(`vigia/core/lr_calibration.py`), usada por el constructor del pipeline y por
`LikelihoodEngine` (ahora con catch per-candidato); (2) el H28 de `run_full`
se gatea por modo del engine — si `CALIBRATED`, no re-calibra y sella
`lr_calibration_method='engine_calibrated'` (antes sellaba 'uncalibrated'
aunque el engine calibrara: misreport preexistente); (3) el bloque de
reescritura de z-scores de `run_vigia` se ELIMINA (era la tercera
aplicación), junto con su recomputación de drift redundante (run_full la
rehace y sobreescribe — solo generaba un log contradictorio). Regresión:
`tests/test_lr_calibrator_path_resolution.py::TestNoDoubleCalibration` y
`::test_engine_uses_candidate_resolution`.

---

## B-103 — NaN en z-scores se binea como observación extrema y satura el drift

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/core/risk_bounded_layer.py` (`internal_drift_from_z_scores`) |
| **Commit fix** | mismo commit que B-102 |
| **Detectado en** | Code review de 8 ángulos sobre B-099 (2026-07-10) |

### Descripción

La semántica de comparación de `min`/`max` de Python con NaN clipeaba
silenciosamente los NaN al bin superior del estimador B-099: cada
`z_score=NaN` contaba como observación extrema ≈+3. Medido: 6 z benignos →
drift 0.0; los mismos 6 + 3 NaN → drift 1.0; `[nan]*4` → 1.0 en vez de
indeterminado. `run_full` filtraba NaN en su caller (`z == z`) pero
`run_vigia` no — y `json.loads` acepta el literal `NaN` por default, así que
un JSON de señales podía inflar el riesgo ×3 con basura.

### Fix aplicado

Filtro de no-finitos (`math.isfinite`) DENTRO del estimador — la defensa vive
en el único choke point, no en cada caller. Menos de 4 valores finitos →
None (indeterminado → fallback externo documentado). Regresión:
`tests/test_h27_internal_drift.py::test_non_finite_values_are_dropped`.

---

## B-104 — Float/libm (math.erf, math.log) en el drift sellado del decision path

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/core/risk_bounded_layer.py` (`internal_drift_from_z_scores`) |
| **Commit fix** | "POST HACKATHON: bit-for-bit deterministic H27 drift kernel — no libm in the sealed path (B-104)" |
| **Detectado en** | Code review de 8 ángulos (hallazgo diferido, ángulo convenciones §5.2) |

### Descripción

El estimador B-099 computaba `system_state.drift_score` (valor sellado) vía
`math.erf` y `math.log` — funciones de libm que no son correctly-rounded y
pueden diferir en el último bit entre plataformas → digests de bundle
distintos para el mismo caso (violación del invariante #4 / §5.2 "no float
in the decision path"). Exposición preexistente (`drift_score` fue siempre
float), re-comprometida por el rewrite del estimador.

### Fix aplicado

Kernel 100% aritmética entera/racional: probabilidades de referencia N(0,1)
CONGELADAS como constantes racionales por k (numeradores sobre 10^17, el bin
central absorbe el residuo → cada fila suma exactamente 1); k por
`bit_length` (sin log2); binning por conversión exacta float→Fraction; PSI
vía `_ln_fraction` (reducción de rango por potencias de 2 + serie atanh,
error máximo 8.9e-16 vs math.log); tabla χ² racional (k clampeado a 12 →
sin fallback sqrt). El único `float()` final es conversión correctly-rounded
de un racional exacto. Validación: diferencia máxima 1.7e-15 vs la
implementación float en 3000 sweeps, cero flips de frontera; tests golden
pinean los outputs exactos. El PSI crudo ahora se loguea a DEBUG (hallazgo
de trazabilidad del review).

---

## B-105 — Decimal en severity de fracturas CAIE: bomba de tiempo de reloj que mataba casos al serializar

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/tools/caie.py` (~1374, ~1932), `vigia_agent.py` (`_json_serial`) |
| **Commit fix** | "POST HACKATHON: fix Decimal severity leak that killed cases at serialization (B-105)" |
| **Detectado en** | Re-baseline de corpus 2026-07-11 — VIGIA-BREAK-016 selló MALICE a la mañana y devolvió NO_BUNDLE a la tarde con código idéntico |

### Descripción

Dos constructores de `Fracture` pasaban `_dround(...)` — un `Decimal` —
como `severity`, violando el contrato del dataclass (`severity: float`):
LOG_VS_MEMORY (0.95/0.75) y NARRATIVE_POISONING_DETECTED (0.85). El
dataclass crudo viaja al resultado sellado del agente por un path de
salida (el path de `cross_artifact_analysis` sanitiza a str por separado),
y el serializador canónico rechaza correctamente tipos desconocidos → el
caso entero moría con TypeError cuando la fractura disparaba. El disparo
está gateado por el trust decay temporal de la evidencia → crash
dependiente del reloj sobre código sin cambios (bisección por worktrees:
todos los commits incluida la tag de restore crasheaban a la misma hora).

### Fix aplicado

Literales float en ambos constructores (valores exactos, sin redondeo,
como todos los constructores hermanos) + frontera tolerante en
`_json_serial`: un Decimal extraviado se codifica EXACTO
(`Fraction(Decimal)`, convención `__fraction__`) con WARNING que nombra
la violación de contrato upstream — degradación honesta en vez de
destruir trabajo válido (§5.3); los tipos desconocidos se siguen
rechazando. Regresión: `tests/test_b105_decimal_serialization.py`
(frontera + trigger determinístico de la fractura + caso E2E).

---

## B-107 — `fit_calibration.py` hacía `sys.exit(1)` a nivel de import; harness de integración roto por imports planos post-B-106

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/core/fit_calibration.py`, `tests/integration/test_ebs_v1_integration.py`, `vigia_agent.py` |
| **Commit fix** | "POST HACKATHON: fit_calibration import must raise, not exit; integration harness qualified imports (B-107)" |
| **Detectado en** | Intento de correr el harness de integración con numpy recién instalado (2026-07-11) |

### Descripción

Tres hallazgos encadenados al cerrar la deriva venv (numpy y scikit-learn
declarados en `requirements.txt:20/:46`, ausentes del entorno — clase B-101):

1. **`sys.exit(1)` a nivel de módulo**: los guards de dependencia de
   `fit_calibration.py` mataban el INTÉRPRETE entero al importar el módulo
   sin numpy/sklearn — pytest moría con INTERNALERROR SystemExit durante la
   colección en vez de reportar un error de import por archivo. Un módulo de
   librería debe hacer raise, no exit. También tenía su propio insert
   vestigial de `<repo>/vigia` (clase B-106).
2. **Imports planos rotos por B-106**: el harness de integración
   (`test_ebs_v1_integration.py`, 7 sitios) usaba `from pipeline import ...`,
   que solo resolvía por el efecto colateral del insert que B-106 eliminó —
   7/55 tests en FAIL (`ModuleNotFoundError: pipeline`), invisible al CI
   porque el harness está excluido del pytest run. Bisección con worktree:
   55/55 en el tag de restore, 48/55 en HEAD → regresión de la serie,
   corregida con imports calificados (`vigia.pipeline.pipeline`).
3. **Grado de análisis dependiente del venv**: sin numpy el
   GraphStabilityEngine cae a bootstrap con `random.Random` que el propio
   código marca "NO Daubert-grade"; sin sklearn no hay modo FULL de KDE.
   Ambos agregados a `_CRITICAL_RUNTIME_DEPS` (con mapeo sklearn→scikit-learn
   para el hint de pip).

### Gates

Suite 1280 passed / 0 failed; harness de integración 55/55; corpus
199 casos con numpy y con numpy+sklearn: **0 flips de veredicto** en ambos
gates (167/199 estable).

---

## B-109 — Cuatro módulos muertos con nombres colisionantes + warning que exigía una dependencia no declarada

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/security.py`, `vigia/vigia_namespace_shim.py`, `vigia/core/pipeline.py`, `vigia/forensics/vision_audit_final.py` (eliminados), `vigia/core/graph_stability.py` |
| **Commit fix** | "POST HACKATHON: dead-module sweep + drift provenance beside the seal (B-109, B-110)" |
| **Detectado en** | Barrido de higiene post-L-052 (2026-07-11) |

### Descripción

Cuatro módulos muertos de la clase de riesgo L-052 (qué copia carga no debe
depender del spelling del import):

1. `vigia/security.py` — shim eclipsado por el paquete `vigia/security/`
   (los paquetes tienen precedencia): inalcanzable, e importaba un módulo
   top-level `security` que NO existe — habría crasheado de ser alcanzable.
2. `vigia/vigia_namespace_shim.py` — sin importers; nombraba engañosamente
   `_REPO_ROOT` al directorio `vigia/` y admitía placeholders en su docstring.
3. `vigia/core/pipeline.py` — definía OTRA `class VigiaPipeline` homónima a
   la real (`vigia/pipeline/pipeline.py`), sin ningún importer vivo.
4. `vigia/forensics/vision_audit_final.py` — copia vieja de vision_audit,
   referenciada solo por el shim muerto (2).

Los cuatro eliminados (recuperables de git). Además, el warning del
BootstrapSampler exigía "Instala numpy+scipy": el sampler solo necesita
numpy (declarado); scipy NO está declarado en ningún manifiesto y cambiaría
el estimador de correlación (spearmanr vs fallback stdlib) — un valor del
decision path (S) que requiere gate comparativo firmado. Texto corregido.

---

## B-110 — Proveniencia del drift H27 y PSI crudo irrecuperables del output

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Archivo** | `vigia/core/risk_bounded_layer.py`, `vigia/pipeline/pipeline.py` |
| **Commit fix** | mismo commit que B-109 |
| **Detectado en** | Findings diferidos del code review de 8 ángulos (2026-07-10) |

### Descripción

Dos huecos de trazabilidad Daubert del drift sellado: (a) el PSI crudo era
irrecuperable de todo output — un examinador no podía distinguir "PSI apenas
sobre el nulo χ²" de "PSI muy por encima"; (b) el bundle no registraba si el
`drift_score` sellado provino del recálculo interno H27 o del parámetro
externo (fallback documentado).

### Fix aplicado

`internal_drift_details()` (el estimador escalar delega en él): drift,
raw_psi, null_95, n_finite, n_dropped_nonfinite, bins. `run_full` retorna
`result["drift_provenance"]` — fuente (internal_h27 / external_fallback /
recomputation_failed), valor solicitado vs aplicado, e intermedios — JUNTO
al sello, no adentro (doctrina §5.1); meterlo EN el payload sellado es una
decisión de esquema ebs_v1 (compat R3-2) que queda para la mantenedora.
También: cache del verificador en `_import_verify_bundle` (no re-ejecutar el
módulo por bundle en loops de batch). Regresión:
`tests/test_h27_internal_drift.py::TestDriftDetailsAndProvenance`.

---

## CAIE-FUTURE-001 — SECURE_DELETE_ARTIFACT (candidate rule, not implemented)

| Campo | Valor |
|-------|-------|
| **Estado** | CANDIDATA — sin caso en corpus que la active |
| **Severidad** | P3 (enhancement) |

Regla CAIE propuesta para detectar borrado seguro deliberado (SDelete,
shred, wipe). Detectable por `metadata.secure_delete_tool` o patrones
en USN Journal (secuencia delete+create en rafaga sobre archivos de
evidencia). No implementada porque no hay caso en el corpus de 199
que la active — seria codigo muerto sin verificacion.

Implementar cuando aparezca un caso real que la necesite.

---

## CAIE-FUTURE-002 — REGISTRY_TAMPERING (candidate rule, not implemented)

| Campo | Valor |
|-------|-------|
| **Estado** | CANDIDATA — sin caso en corpus que la active |
| **Severidad** | P3 (enhancement) |

Regla CAIE propuesta para detectar limpieza de registros de ejecucion
(prefetch, shimcache, amcache). Detectable por gaps en secuencias que
deberian ser continuas (prefetch faltante para binarios con evidencia
de ejecucion, shimcache entries borrados selectivamente). No implementada
por la misma razon que SECURE_DELETE_ARTIFACT.

---

## B-114 — `add_from_tool_result()` en CAIE construye `Artifact` sin pasar por los guardrails de `add_artifact()` [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-16, sesión post-hackathon (delegación a `add_artifact()`; ver B-136 para el hallazgo mayor de la misma auditoría) |
| **Severidad** | P3 (guardrail bypass, no explotado en el caso probado) |
| **Archivo** | `vigia/tools/caie.py` |
| **Función** | `CrossArtifactIncongruenceEngine.add_from_tool_result()` (línea ~1135) vs `add_artifact()` (línea ~1089) |
| **Detectado en** | Sanity check Nivel 1 del pipeline CLIP (2026-07-13), branch `claude/clip-pipeline-sanity-check-roh22k` |

### Descripción

`add_from_tool_result()` construye un `Artifact` y lo agrega directamente a
`self._artifacts` (línea ~1169), en vez de delegar a `add_artifact()`. Esto
salta dos guardrails que `add_artifact()` sí aplica a cualquier llamador que
pase por él:

1. **`_MAX_ARTIFACTS`** — protección anti-flooding (DoS). `add_from_tool_result()`
   no chequea el límite antes de appendear.
2. **Whitelist de `evidence_type`** — `add_artifact()` rechaza tipos que no
   estén en `_VALID_EVIDENCE_TYPES` (deriva de `EVIDENCE_PROFILES`).
   `add_from_tool_result()` no valida esto; un `evidence_type` arbitrario
   entraría sin spoofability weighting definido.

`vision_intent_audit` (CLIP) usa `add_from_tool_result()` con
`evidence_type="document_visual"`, que sí está en la whitelist — no se
explotó en el sanity check de CLIP corrido en esta sesión. Pero el bypass es
estructural: **cualquier tool MCP que use `add_from_tool_result()` en vez de
`add_artifact()` hereda el mismo hueco**, no es específico de CLIP.

### Criterio de escalada

Revisar qué otros tools MCP (además de `vision_intent_audit`) llaman
`add_from_tool_result()`, y si alguno puede pasar un `evidence_type`
influenciado por input externo (no hardcodeado como en vision_audit.py).
Si es así, escalar a P1/P2 — es una vía de bypass del whitelist con
influencia de atacante. Fix candidato: que `add_from_tool_result()` delegue
a `add_artifact()` en vez de appendear directo.

### Fix aplicado (2026-07-16)

El fix candidato del párrafo anterior, tal cual: `add_from_tool_result()`
construye el `Artifact` y retorna `self.add_artifact(...)` (bool), con lo que
`_MAX_ARTIFACTS` y la whitelist de `evidence_type` aplican también a este
camino. Efecto lateral intencional de la delegación: los artifacts del wrapper
ahora se indexan en `_temporal_index`/`_network_index` como los de cualquier
otro caller (antes eran invisibles para las reglas TCV y NETWORK_VS_HOST).

Censo de callers ejecutado (criterio de escalada de esta entrada): 4 sitios —
`vision_audit` (firma correcta, tipos whitelisted, no explotable) y 3 sitios
con la llamada rota que nunca llegaba al append (ver B-136). El scorer
(`vigia_scorer.py:652`) alimenta CAIE vía `add_artifact()` directo, así que
este fix no toca el camino de veredicto.

### Verificación

- Red tests: `tests/test_b114_caie_guardrail_delegation.py` (6 tests):
  flooding rechazado en `_MAX_ARTIFACTS`, `evidence_type` fuera de whitelist
  rechazado, adición whitelisted intacta (extracción de score, override
  digital_perfection), indexación temporal ahora aplicada.
- Gate comparativo de corpus: sin cambios de veredicto (ver commit).

---

## B-115 — `VigiaAdversarialNLP._inject_caie_fractures()` llama a `add_from_tool_result()` con kwargs inexistentes — nunca inyectó nada a CAIE [SUBSUMIDO EN B-136]

| Campo | Valor |
|-------|-------|
| **Estado** | SUBSUMIDO EN B-136 (2026-07-16) — alcance real: 3 sitios con la misma llamada rota, y el engine destino se descarta igual. El fix mecánico de kwargs fue evaluado y REFUTADO (empeoraría el trail: éxito falso hacia un objeto descartado). La "decisión de normalización" se disolvió: `verdict.confidence` YA ES `(mcp-1)/4` (adversarial_nlp.py:1131) |
| **Severidad** | P2 (silenciosamente roto desde su introducción — misma clase de bug que el `await` faltante en `vision_intent_audit`) |
| **Archivo** | `vigia/tools/adversarial_nlp.py:1585-1604` (`_inject_caie_fractures`) |
| **Detectado en** | Cableado del PDF pericial al pipeline (2026-07-13), branch `claude/clip-pipeline-sanity-check-roh22k` |

### Descripción

`_inject_caie_fractures()` llama:

```python
caie.add_from_tool_result(
    source_tool="vigia_adversarial_nlp",
    evidence_type="linguistic_forensics",
    raw_score=verdict.mcp,
    description=fractura,
    metadata={...},
)
```

pero la firma real de `CrossArtifactIncongruenceEngine.add_from_tool_result()`
(`vigia/tools/caie.py:1135-1141`) es
`(self, tool_name: str, result: dict, evidence_type: str = "log_entry", provenance_chain=None)`.
Ninguno de `source_tool`, `raw_score`, `description`, `metadata` existe como
parámetro — cada llamada lanza `TypeError`, capturado por el `except Exception`
genérico de línea 1599-1604 y logueado como `CAIE_INJECTION_FAILED`. Resultado:
**ninguna fractura de análisis estilométrico (SDA-NR/CLI/ACP/ROI) llegó jamás a
CAIE**, desde que este código se escribió — mismo patrón que el `await` faltante
en `vision_intent_audit` (fix aplicado en este mismo branch), pero acá el fix
no es mecánico.

### Por qué no se arregló en el momento

Un fix ingenuo (renombrar kwargs a `tool_name`/`result`) no alcanza: la firma
real de `add_from_tool_result()` NO acepta `raw_score` directo — lo deriva
internamente de claves conocidas del dict (`suspicion_score`,
`visual_malice_score`, `probability_*`). `verdict.mcp` es 1.0–5.0 (Multiplicador
de Certeza Pericial), no está en esa lista, y `Artifact.__post_init__` clampea
`raw_score` a `[0.0, 1.0]` — pasar `mcp` crudo colapsaría todo a 1.0. Hace
falta decidir la normalización correcta (`(mcp-1)/4`? usar `verdict.confidence`
en su lugar?) y esa es una decisión de metodología forense, no un fix mecánico
— fuera de alcance de la tarea que motivó este hallazgo.

### Criterio de escalada

Decidir la normalización de `mcp`→`raw_score` (o si corresponde usar
`verdict.confidence`), y usar `add_artifact()` en vez de
`add_from_tool_result()` directamente — ver B-114: `add_from_tool_result()` no
pasa por los guardrails de `add_artifact()` (límite anti-flooding, whitelist
de `evidence_type`), así que replicar ese patrón acá perpetuaría el mismo hueco.

---

## REVIEW-001 — VIGIA-BREAK-012 label review (BENIGN vs SUSPICION)

| Campo | Valor |
|-------|-------|
| **Estado** | PENDIENTE DE REVISION |
| **Severidad** | P4 (label hygiene) |

Caso adversarial disenado para confundir: 4/5 fuentes comprometidas
reportan anomalia, 1 legitima dice lo contrario. El motor da SUSPICION
(coherente con la mayoria de fuentes). La etiqueta dice BENIGN (porque
la fuente correcta es la unica legitima). Amerita dossier propio —
la pregunta no es si el motor falla sino si BENIGN es la etiqueta
correcta cuando el motor no puede distinguir fuentes comprometidas
de legitimas.

---

## B-117 — Inverted posterior semantics in `risk_bounded_layer.py` — `VigiaPipeline` emitted backwards verdicts

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P0 (verdict inversion in governance layer) |
| **Archivo** | `vigia/core/risk_bounded_layer.py` |
| **Función** | `RiskBoundedDecisionLayer.compute_risk()` |
| **Commit fix** | `f8c9f9f1` |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Description

`LikelihoodEngine.infer()` emits `posterior` = P(fabrication | evidence).
`risk_bounded_layer.compute_risk()` calculated:

```python
r = (1 - P) * (1 + lambda*D) * (1 + gamma*(1-S)) * (1 + omega*(1-I))
```

With P = P(fabrication), `(1-P)` inverts the semantics:
- Fabricated case: P = 0.99 -> (1-P) = 0.01 -> r low -> **ACCEPT** (wrong)
- Genuine case: P = 0.01 -> (1-P) = 0.99 -> r high -> **REJECT** (wrong)

Every verdict from `VigiaPipeline` through this layer was semantically backwards.

### How it was missed

The orphan `vigia/governance/risk_bounded_layer_v2.py` documented this exact
bug as fix P0-001, but approached it by redefining P as P(authenticity) — a
valid alternative fix. However, v2 was never wired: `pipeline.py` imports
exclusively from `vigia.core.risk_bounded_layer` (v1). Meanwhile,
`pre_release_check.py` incorrectly declared v2 as "the active version",
masking the fact that the buggy v1 was the one in production.

Existing tests (T40, T41, T42, T97) all used `posterior=0.5`, which is
invisible to the inversion (`0.5 == 1 - 0.5`).

### Fix applied

Changed `r = (1-P) * (...)` to `r = P * (...)`, keeping
P = P(fabrication) as emitted by `LikelihoodEngine`. Added inline comment
and docstring guard citing this bug.

### Impact assessment

- **AFFECTED entry point**: `VigiaPipeline` via `vigia_api.py`, `show_4_hashes.py`
- **NOT affected**: `vigia_scorer.py` (own threshold logic, no `risk_bounded_layer`)
- **NOT affected**: `vigia_agent.py` (uses `vigia_scorer`, not pipeline)
- **Corpus 184/199**: unaffected (all produced by `vigia_scorer`)
- **Real cases**: confirmed unaffected (all ran via `vigia_agent`/`vigia_scorer`)

### Cleanup

- `vigia/governance/risk_bounded_layer_v2.py` deleted (dead weight — its
  P0-001 guard is now resolved in v1).
- `scripts/pre_release_check.py` BANNED_FILENAMES corrected (v1 is canonical,
  not deprecated).

### Update 2026-07-26 — la fórmula vieja `(1-P)·(...)` había sobrevivido en 8
lugares además del código, incluyendo dos que generan output real

Mientras se resolvía B-214, se encontró que el fix del código (v1, arriba)
nunca se propagó a los comentarios, docstrings y generadores de narrativa
que citan la misma fórmula. Barrido completo (`grep` en todo el repo,
excluyendo el corpus académico generado) encontró la fórmula pre-B-117
invertida en 8 lugares vivos:

`vigia/pipeline/pipeline.py` (dos docstrings distintos: el header del
módulo y `run_full()`), `vigia/models/ebs.py`, `VIGIA_ESTADO_TECNICO_ES.md`
y su espejo en `docs/`, `docs/VIGIA_TECHNICAL_STATE_EN.md`,
`docs/vigia_paper_methodology.md` (el diagrama de capas Y la explicación en
prosa, que además tenía el *significado* invertido: "r = 0 cuando P = 1,
fabricación cierta" es exactamente el bug de decisión invertida que B-117
corrigió, descripto ahí como si fuera el diseño intencional),
`docs/vigia-real-006_execution_summary.md` (un walkthrough cuya propia
aritmética mostrada, `r=0.1734`, ya contradecía su propio chequeo de umbral
mostrado — "REJECT > 0.35? No" — Y la decisión final declarada — "REJECT" —;
corregido recalculando con la fórmula real, lo que además resuelve esa
contradicción interna), y `forensics/evidence_narrative_gen.py` (una
etiqueta de narrativa mostrada junto al risk score REAL, correctamente
calculado — un perito leyendo la narrativa generada e intentando reproducir
el número a mano usando la fórmula indicada habría obtenido el resultado
equivocado).

**Un caso NO se corrigió, deliberadamente:**
`vigia/scripts/generate_execution_log.py:227` pasa esta misma fórmula
(más valores placeholder D/S/I fabricados: `"D": 0.1` hardcodeado, `S`/`I`
derivados con fórmulas ad-hoc que no corresponden a ningún cálculo real)
a una entrada de log `RISK_CALCULATION` — pero el script en realidad llama a
`vigia.core.decision_layer.decide()` (línea 142), un motor de decisión
completamente distinto, basado en umbrales de MI, que no calcula D, S, ni I
en absoluto. No es un signo invertido: es un formato de log diseñado para un
subsistema (`risk_bounded_layer.py`) reutilizado para describir otro
completamente distinto (`decision_layer.py`), con datos fabricados en los
campos que no aplican — un problema más profundo de integridad de audit
trail (el script genera "Agent Execution Logs... para los entregables
SANS" según su propio docstring), no un simple string desactualizado. Este
script SÍ procesa casos reales (no es un generador sintético/demo). Queda
documentado en detalle, sin fix, en `tests/test_b117_stale_formula_sweep.py`
y pendiente de investigación propia.

Test permanente: `tests/test_b117_stale_formula_sweep.py` — barre todo el
repo buscando la fórmula invertida y falla si reaparece en cualquier lugar
no cubierto por una excepción documentada y justificada explícitamente.
Suite completa: 2008 passed, 191 skipped, 29 xfailed — cero regresiones
(todos los cambios son comentarios/docstrings/prosa, ninguna lógica
tocada).

---

## B-118 — `vigia/core/signal_contract.py` name collision caused BUG-EML-001 — file deleted

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P1 (confirmed production incident — three modules at 0% coverage) |
| **Archivo** | `vigia/core/signal_contract.py` (DELETED) |
| **Detectado en** | Module archaeology audit 2026-07-14; original incident documented in `tests/test_eml_import_regression.py` |

### Description

`vigia/core/signal_contract.py` was a one-line re-export of EBS v1 data models.
It collided by name with `vigia/tools/signal_contract.py`, which defines the
real `SignalBuilder` class (with `from_raw()` and `from_z_score()`).

This collision caused BUG-EML-001: three modules (`eml_symbolic.py`,
`eml_gci.py`, `signal_adapter.py`) imported `SignalBuilder` from
`vigia.core.signal_contract` (wrong path), got `ImportError`, and sat
silently at 0% coverage until someone noticed. The bug was fixed previously
by correcting the imports to point to `vigia.tools.signal_contract`.

### Why deleted now

The file had zero callers after the BUG-EML-001 fix. Its continued existence
was a latent re-infection risk: any new module importing `signal_contract`
from `vigia.core` would silently get the wrong module (EBS v1 re-exports
instead of `SignalBuilder`). Unlike other orphans that are merely unused,
this file's NAME is the danger — it actively misleads Python's import
resolution. The regression guard `tests/test_eml_import_regression.py`
remains in place and passes (3/3) after deletion.

### Verification

- `grep -rn "from vigia.core.signal_contract import"` — zero live callers
- `test_eml_import_regression.py` — 3/3 PASSED after deletion
- Full suite — 1366 passed, 0 regressions

---

## B-119 — `vigia/core/vigia_core_semiotic_detector.py` fail-open stub deleted

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P2 (fail-open stub — silent false-negative if wired by accident) |
| **Archivo** | `vigia/core/vigia_core_semiotic_detector.py` (DELETED) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Description

4-line stub: `SemioticDetectorV2.analyze()` unconditionally returned
`{"alert_level": "NORMAL", ...}` — a hardcoded no-op. Zero callers in the
codebase. Already marked DEPRECATED in `pre_release_check.py`.

The real semiotic detector lives in `vigia/core/semiotic_detector_v2.py` (the
canonical version with pattern matching, FSV computation, and forensic DB
lookup). The stub shared the class name `SemioticDetectorV2`, making it
uniquely dangerous: if any module imported from the wrong path, the entire
semiotic detection layer would silently return NORMAL for all inputs —
fail-open, no error, no warning.

### Why deleted

Unlike unused-but-harmless modules, this file's danger IS its existence.
A stub that always says "nothing to see here" is strictly worse than a missing
file (which would at least raise ImportError). Zero callers, zero value,
maximum latent risk. Same deletion criterion as B-118 (signal_contract.py).

### Verification

- Zero callers confirmed (`grep -rn` excluding pre_release_check and tests)
- Full suite: 1366 passed, 0 regressions

---

## B-120 — `vigia/cli.py` false PASS from unimplemented verification stubs + legacy ledger without HMAC

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P1 (false verification PASS from `pip install -e .` entry point) |
| **Archivo** | `vigia/cli.py` |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Description

`vigia/cli.py` is the `vigia` entry point registered in `pyproject.toml:69`
(`vigia = "vigia.cli:main"`). Anyone running `pip install -e .` gets a `vigia`
command that runs this code.

Three problems:

1. **`verify_signature()` returned `status: True` unconditionally** — no PKI
   verification was implemented. Any bundle, regardless of signature validity,
   passed this check.
2. **`verify_timestamp()` returned `status: True` unconditionally** — no
   RFC 3161 verification was implemented. Same false PASS.
3. **`verify_ledger()` uses legacy hash chain without HMAC** — an attacker
   with write access can rewrite and recompute the entire chain undetected.
   This is the exact pattern CLAUDE.md says "MUST NOT be used for new
   investigations."

Because `verify_bundle()` computes `overall_status = all(status for check)`,
the two false-PASS stubs made the overall result look valid even when no
signature or timestamp verification occurred.

### Fix applied

1. `verify_signature()`: returns `status: False` with explicit "NOT
   IMPLEMENTED" note.
2. `verify_timestamp()`: returns `status: False` with explicit "NOT
   IMPLEMENTED" note.
3. `verify_ledger()`: added warning in output clarifying legacy schema
   without HMAC, directing to `verify_tool_log.py` for new bundles.
4. Module docstring updated to clearly document what IS and IS NOT verified.
5. `verify_bundle()` logic unchanged — `all()` now correctly reflects False
   from the unimplemented checks.

### Verification

- Tested with synthetic bundle: `overall_status` now correctly False (was
  True before fix with identical bundle).
- Full suite: 1366 passed, 0 regressions.

---

## B-121 — Bulk removal of 15 confirmed dead-weight files (duplicates, superseded, prohibited, legacy monolith)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P3 (dead weight — no active risk, but repo bloat and confusion potential) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Files removed (15)

**Byte-identical duplicates (3):**

| Removed | Canonical copy (live) |
|---------|----------------------|
| `tests/temporal_forensics_redteam.py` | `vigia/forensics/temporal_forensics_redteam.py` |
| `vigia/core/forensic_db.py` | `vigia/tools/forensic_db.py` |
| `scripts/init_patterns_db.py` | `vigia/tools/init_patterns_db.py` (invoked by CI) |

**Superseded by newer version with real integration (5):**

| Removed | Superseded by |
|---------|---------------|
| `vigia/core/negation_handler.py` | `_detect_negation()` inline in `semiotic_detector_v2.py` |
| `vigia/memory/case_pattern_library.py` | `vigia/inference/case_pattern_library.py` |
| `vigia/tools/behavioral_fingerprint.py` | `vigia/inference/behavioral_fingerprint.py` |
| `vigia/tools/cross_artifact_resonance.py` | `vigia/inference/cross_artifact_resonance.py` |
| `vigia/utils/path_guard.py` | `vigia/core/path_guard.py` (hardened: TOCTOU/flock/symlink) |

**Abandoned designs (4):**

| Removed | Reason |
|---------|--------|
| `vigia/llm_backend_v2.py` | Both halves orphaned; `reason_with_llm` in bridge supersedes |
| `vigia/core/llm_backend.py` | Same — `pre_release_check.py` marks DEPRECATED |
| `vigia/core/shadow_mode.py` | Explicitly PROHIBITED in `pre_release_check.py` BANNED_MODULES |
| `vigia/sift/mft_timeline_analyzer.py` | Self-declared shim: "DEPRECATED: use disk_forensics.MFTTimelineAnalyzer" |

**Legacy artifacts (3):**

| Removed | Reason |
|---------|--------|
| `vigia/core/vigia_core_forensic_technical_detector.py` | Fragment of monolith, DEPRECATED in `pre_release_check.py` |
| `vigia/pipeline/BRIDGE_PATCH_FINAL.py` | Patch instructions already applied to bridge, historical note |
| `vigia/vigia_core.py` | Legacy monolith (202 lines), zero importers in entire repo |

### NOT removed

- `vigia/tools/vigia_case_adapter.py` — has a real caller via subprocess in
  `tests/unit/test_m4_floor.py:41`. Cannot be deleted without fixing that test.
- `vigia/tools/geopolitical.py` and `vigia/core/geopolitical_v2.py` — real
  functionality (APT attribution / false flag detection), disconnected from
  production but preserved as pending-to-wire capability.

### Verification

- Zero callers confirmed for all 15 files (grep across entire repo)
- 3 duplicate pairs confirmed byte-identical (diff)
- Full suite: 1366 passed, 0 regressions

---

## B-125 — `vigia/forensics/document_integrity.py` dead duplicate deleted (unpatched ancestor of tools/ version)

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P3 (dead duplicate with stale code — `round(float, 2)` in `suspicion_score` instead of Fraction) |
| **Archivo** | `vigia/forensics/document_integrity.py` (DELETED) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`, DEAD_WEIGHT category) |

### Description

Copy-paste duplicate of `vigia/tools/document_integrity.py` (the live version
registered in `vigia_sift_bridge.py`). The internal header literally said
`vigia/tools/document_integrity.py` — confirming it was a copy artifact.

The live version (`vigia/tools/`) received the `_MAX_IMAGE_PIXELS` fix
(commit `450d30db`, B-117 session) and uses the correct import from
`vigia.forensics.vision_audit`. This orphan copy retained the pre-fix code
including `round(float, 2)` in `suspicion_score` (a determinism violation
under CLAUDE.md invariant #4 — the live version uses Fraction).

### Why it was pending

Identified in the archaeology report as DEAD_WEIGHT (confirmed duplicate)
but was not included in the B-121 bulk deletion because the `_MAX_IMAGE_PIXELS`
fix earlier in that session had touched the live version, and the orphan
was deferred to avoid confusion with the actively-patched file.

### Verification

- Zero callers confirmed (`grep -rn` across entire repo)
- Full suite: 1366 passed, 0 regressions

---

## B-126 — Grice v3.2 phenomenon-based detector + scorer testimony gate [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P1 (2 casos del corpus corregidos: KIWI-006, KIWI-007) |
| **Archivos** | `vigia/vigia_sift_bridge.py` (Grice v3.2), `vigia_scorer.py` (gate), `sift_orchestrator.py` (B-127 pipeline injection) |
| **Detectado en** | Mode 2 blind re-run 2026-07-14 |

### Description

The Grice RELATION detector v1 was a near-constant: it used a 15-keyword
topic list that fired on ~100% of natural-language testimony with zero
discriminating power. Replaced with v3.2 phenomenon-based bilingual
(EN+ES) detector with four linguistic features: factual_impossibility,
quantity_asymmetry, evidence_withholding, fundamental_ignorance.

Threshold=25 (Daubert: single phenomenon insufficient). Tiered
adj_density (>=10% -> weight 30) to preserve Carnegie urgency detection.

Scorer gate (defense in depth): fires only when verdict=NOISE AND
testimony-only AND no exculpatory artifacts AND max(prior_trust)<=0.30
AND Grice=SUSPICION.

### Iteration history

v2.1 (English-only, phrase memorization) -> v3 (phenomenon patterns) ->
v3.1 (negation fix) -> v3.2 (bilingual EN/ES bug fixed). Each iteration
validated against adversarial cases + full corpus.

### Verification

- 1365 tests passed, 0 regressions
- Corpus: 185/199 -> 187/199 (+2 FIX, 0 regressions)
- CRONOS traces: 6b81f266, 3b11e32e

---

## B-127 — Pipeline integration for Grice testimony gate [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P2 (enables B-126 to fire in autonomous batch mode) |
| **Archivos** | `sift_orchestrator.py`, `vigia_scorer.py` (prior_trust boundary fix) |
| **Detectado en** | B-126 dry-run showed gate inactive in batch (no grice_verdict in case data) |

### Description

`sift_orchestrator.py::_resolve_hypothesis()` now calls
`audit_grice_maxims()` conditionally before `_vigia_score()` for
testimony-only cases without exculpatory artifacts. Also fixed
prior_trust boundary from `< 0.30` to `<= 0.30` (KIWI-007 has
prior_trust=0.30 on the panic button artifact).

### Verification

- Dry-run: +2 FIX (KIWI-006, KIWI-007), 0 regressions from B-127
- 9 pre-existing MALICE->SUSPICION divergences confirmed unrelated
- Batch regenerated: 187/199 PASS, 12 FAIL (full 199 cases)

---

## B-128 — Delete dead duplicate vigia/core/semiotic_detector.py [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P3 (dead duplicate with pre-hardening code) |
| **Archivo** | `vigia/core/semiotic_detector.py` (DELETED) |
| **Detectado en** | Verification audit 2026-07-14 |

### Description

Orphan copy of semiotic_detector_v2.py (v2.1, pre-hardening). Header
says 'semiotic_detector_v2.py' but file named without _v2. Missing
NEGATION_STRONG, _sanitize_text — known vulnerabilities already fixed
in the live v2.2. Zero callers confirmed. Same pattern as B-125a.

---

## B-130 — UnifiedTimelineEngine crashea con timestamps int epoch [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P1 (crashea el motor completo; elimina silenciosamente una fuente de evidencia del veredicto) |
| **Archivo** | `vigia/sift/unified_timeline_engine.py` |
| **Función** | `UnifiedTimelineEngine._extract_timestamp` (línea ~130) |
| **Detectado en** | VIGIA-REAL-VANKO-2026 corrida RAW 2026-07-14 |
| **Commit fix** | ver commit "POST HACKATHON: fix B-130 — UnifiedTimelineEngine crashes on int epoch timestamps" |

### Descripción

`_extract_timestamp` recuperaba el valor crudo de la metadata así:

```python
ts_str = meta.get("timestamp", meta.get("last_execution", "1970-01-01T00:00:00Z"))
```

El valor por defecto del `.get()` solo se aplica cuando la clave está **ausente**. Cuando
la clave existe pero contiene un `int` (timestamp epoch, común en metadata de
Prefetch/Registry), el `int` se retorna tal cual y se pasa directamente a
`_parse_iso_timestamp`, que asume `str` y llama inmediatamente a
`ts_str.replace("Z", "+00:00")`. Esto lanza `AttributeError` (int no tiene `.replace()`),
no `ValueError`. El bloque `except ValueError` existente nunca lo capturaba.

El `AttributeError` subía al `except Exception` exterior del orquestador, que solo
logueaba el crash a nivel `ERROR` y continuaba. `build_timeline` nunca completaba; la
señal `UNIFIED_TIMELINE` quedaba ausente del bundle. En la corrida RAW de
VIGIA-REAL-VANKO-2026, esto eliminó una fuente de evidencia y contribuyó a un veredicto
ABSTAIN (empate exacto CCS 1/2) que podía ser artefactual.

### Causa raíz (Peircean)

- **Firstness:** `AttributeError: 'int' object has no attribute 'replace'` en
  `_parse_iso_timestamp`, línea ~206.
- **Secondness:** `meta.get("timestamp", default)` retorna el valor almacenado sin
  modificarlo cuando la clave existe. Epoch entero es un formato de timestamp válido y
  común en los parsers de Prefetch y Registry. El contrato de la función decía
  `ts_str: str` pero el caller nunca lo verificaba.
- **Thirdness:** Cualquier señal cuya metadata contiene un timestamp numérico (Prefetch,
  Registry, o cualquier parser que use `int(epoch)` directamente) crashea silenciosamente
  el motor de timeline completo.

### Fix aplicado

En `_extract_timestamp`: se agregó un guard `isinstance(ts_val, (int, float))` antes
de llamar a `_parse_iso_timestamp`. Si el valor ya es numérico, se retorna directamente
como `int(ts_val)` sin intentar parsearlo como ISO. Se ensanchó el `except` a
`(ValueError, TypeError, AttributeError)` como defensa adicional.

```python
if isinstance(ts_val, (int, float)):
    return int(ts_val)
try:
    return _parse_iso_timestamp(ts_val)
except (ValueError, TypeError, AttributeError):
    ...
```

### Tests de regresión agregados

`tests/test_pipeline_robustness_narrative.py::TestB090EmptyTimelineExcludedFromGates`:

- `test_int_epoch_timestamp_does_not_crash_timeline` — timestamps int, verifica que los
  valores epoch se preservan exactos.
- `test_float_epoch_timestamp_does_not_crash_timeline` — epoch float, verifica truncado
  a int.

### Impacto en veredicto

VIGIA-REAL-VANKO-2026: ABSTAIN (empate CCS 1/2) obtenido con el motor de timeline
silenciosamente ausente. Tras el fix, re-corrida confirmó que el ABSTAIN es GENUINO,
no artefactual (empate persiste con la timeline funcionando).

---

## B-131 — Metadata de adquisición no se propaga a señales derivadas de los motores [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-16, sesión post-hackathon (helper `_inject_acq_meta` + gate comparativo de corpus) |
| **Severidad** | P2 (metadata de adquisición ausente en señales derivadas; degradación honesta de base_trust a 0.10 para esas señales) |
| **Archivos** | `vigia/sift/sift_orchestrator.py` (Gamma loop, pasos 6 y 8) |
| **Detectado en** | VIGIA-REAL-VANKO-2026 corrida RAW 2026-07-14 |

### Descripción

El Gamma loop (paso 4 en `sift_orchestrator._analyze`) inyecta la metadata de
adquisición (`acquisition_tool`, `acquisition_hash`, `acquisition_timestamp`,
`examiner_id`, `write_blocker_used`) de los flags CLI en todas las señales de
`raw_signals`. Esto produce señales correctamente enriquecidas en `gamma_adjusted` y
luego en `frs_adjusted`.

Sin embargo, las señales creadas **después** del Gamma loop lo evitan completamente:

- **Paso 6** (motores): `CrossArtifactResonance` (`CROSS_RESONANCE`),
  `CasePatternLibrary` (`CASE_PATTERN_LIBRARY`), `MetabolicProfiler`,
  `BehavioralFingerprint` — todos producen nuevos objetos `SignalOutput` a partir de
  `frs_adjusted`. Estos objetos nuevos NO heredan `_acq_meta`.
- **Paso 8** (adversarial): `AdversarialRobustnessEngine` (`ADV_ROBUST`) produce un
  nuevo `SignalOutput`. Mismo problema.

CAIE degrada `base_trust` a `0.10` para señales sin campos de adquisición críticos
(NIST SP 800-86 §4.3). En la corrida de VIGIA-REAL-VANKO-2026:

- `CROSS_RESONANCE`, `CASE_PATTERN_LIBRARY`, `ADV_ROBUST`: perdieron TODOS los campos
  de adquisición → degradadas a `base_trust=0.10`.
- `REGISTRY_RTR`, `EVENT_LOG`, `PREFETCH_ANALYZER`: tenían los campos de adquisición
  (del Gamma) pero mostraron `write_blocker_used=False` (correcto: el examinador pasó
  `--write-blocker-used false`) → degradación leve, comportamiento esperado.

### Causa raíz

Gap arquitectónico: `_acq_meta` es una variable local en `_analyze`, construida una
sola vez durante el paso 4 y usada únicamente en el Gamma loop. No existe ningún punto
de inyección para las señales de los motores ni para la señal adversarial, que se
construyen fuera del loop.

### Enfoque del fix (a implementar tras dry-run)

Inyectar `_acq_meta` en cada señal de los motores y en `adv_signal` usando el mismo
patrón de merge que el Gamma loop: `{**_acq_meta, **sig.metadata, ...}` (la metadata
propia de la señal tiene precedencia). Un helper `_inject_acq_meta(sig, acq_meta)`
que retorne un nuevo `SignalOutput` con metadata fusionada evitaría duplicación de
código.

**Antes de implementar:** dry-run de corpus completo para confirmar que no hay
regresiones de veredicto. Las señales derivadas con metadata de adquisición pueden
desplazar valores de base_trust y mover casos borderline SUSPICION/INTENT. Tratar con
el mismo rigor que B-126/B-127.

### Observación

`write_blocker_used=False` en señales primarias (REGISTRY_RTR, EVENT_LOG,
PREFETCH_ANALYZER) es **comportamiento correcto**, no un bug. El examinador pasó
`--write-blocker-used false`, lo que es honesto: no se usó write blocker. CAIE degrada
el trust correspondiente según NIST SP 800-86. El sistema funciona como fue diseñado.

### Fix aplicado (2026-07-16)

Helper estático `SIFTOrchestrator._inject_acq_meta(sig, acq_meta)` en
`vigia/sift/sift_orchestrator.py`, aplicado en los 6 puntos de creación de señales
post-Gamma: paso 6 (Metabolic, Resonance, Behavioral, Patterns), paso 7
(UnifiedTimeline — mismo gap, no listado en el reporte original pero misma ley) y
paso 8 (AdversarialRobustness). Merge con la misma precedencia del Gamma loop:
`{**_acq_meta, **sig.metadata}` — la metadata propia de la señal gana.
`acq_meta` vacío o `sig=None` son no-ops.

### Verificación

- Reproducción en vivo pre-fix: `run_full_analysis(event_stream=...)` con
  `acquisition_overrides` seteados → METABOLIC_PROFILER, BEHAVIORAL_FINGERPRINT,
  UNIFIED_TIMELINE y ADV_ROBUST sin `acquisition_tool`/`examiner_id`/`write_blocker_used`,
  CAIE disparando ACQUISITION_METADATA_MISSING_CRITICAL (base_trust 0.10).
- Post-fix: las 4 señales derivadas llevan los 3 campos declarados. CAIE solo
  reclama `acquisition_hash`/`acquisition_timestamp`, honestamente ausentes en una
  corrida sintética sin registros ACQUIRE en la cadena (degradación honesta, correcta).
- Red tests: `tests/test_b131_acq_meta_propagation.py` (6 tests — propagación,
  precedencia, no-op, passthrough de None).
- Gate comparativo de corpus (`run_all_agent.py --rerun`, 201 casos): baseline
  pre-fix 189/201 PASS, post-fix 189/201 PASS, cero flips de veredicto por caso
  (diff campo a campo del `_batch_summary.json`). Suite completa: 1376 → 1397
  passed (+21 tests nuevos B-131/B-133/B-134/B-135), 0 regresiones.

---

## B-132 — PREFETCH_ANALYZER lista anti-forense incompleta: sdelete.exe no reconocido [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO |
| **Severidad** | P1 (herramienta anti-forense activa no detectada → z sub-óptimo → contribuyó al ABSTAIN de VIGIA-REAL-VANKO-2026) |
| **Archivo** | `vigia/sift/prefetch_analyzer.py` |
| **Detectado en** | VIGIA-REAL-VANKO-2026 corrida RAW 2026-07-14 |
| **Commit fix** | ver commit "POST HACKATHON: fix B-132 — prefetch anti-forensic calibration..." |

### Descripción

`PrefetchAnalyzer` tenía una sola lista de herramientas sospechosas
(`ANTI_FORENSIC_PREFETCH_SIGNS`) que contenía LOL-bins genéricos (rundll32, regsvr32,
mshta, certutil) más herramientas de hacking conocidas (mimikatz, psexec, procdump).
Esta lista **no incluía** herramientas específicas del caso Vanko:

| Herramienta encontrada en prepared/prefetch/ | En lista antes del fix | Ruta correcta |
|------|------|------|
| `SDELETE.EXE` (borrado seguro — destrucción de evidencia) | NO | `anti_forensic_deletions` → z=3.2 |
| `SMALLFTPD.EXE` (servidor FTP — vector de exfiltración) | NO | `suspicious_executions` → z=2.5 |
| `NETSTUMBLER.EXE` (war-driving WiFi — reconocimiento) | NO | `suspicious_executions` → z=2.5 |
| `VERACRYPT FORMAT.EXE` (cifrado de volúmenes — ocultamiento) | NO | `suspicious_executions` → z=2.5 |

Consecuencia: el analizador producía z=1.75 (post-gamma) basado únicamente en 34 hits
de RUNDLL32.EXE genérico. Con sdelete correctamente rutado a `anti_forensic_deletions`,
z pre-gamma sube de 2.5 a 3.2 → post-gamma estimado ~2.24 (cruza umbral z>2).

### Causa raíz (Peircean)

- **Firstness:** `PREFETCH_ANALYZER z=1.75`, `anti_forensic_count=0` pese a que
  `SDELETE.EXE-FBA93810.pf` existía en `prepared/prefetch/`.
- **Secondness:** Las tres herramientas clave (`SDELETE.EXE`, `SMALLFTPD.EXE`,
  `NETSTUMBLER.EXE`) no estaban en ninguna lista del analizador. La detección de
  `anti_forensic_deletions` solo cubría PREFETCH_WIPE (menos de 10 archivos .pf
  totales) — no la presencia de herramientas de borrado seguro.
- **Thirdness:** Lista calibrada para casos genéricos de malware LOL-bin, no para
  casos de insider threat con herramientas específicas de exfiltración/reconocimiento.

### Fix aplicado

Tres listas separadas con routing diferenciado:

1. **`ANTI_FORENSIC_PREFETCH_SIGNS`** (sin cambios) — LOL-bins → `suspicious_executions`
2. **`ANTI_FORENSIC_TOOL_EXECUTION_SIGNS`** (nueva) — herramientas de borrado seguro →
   `anti_forensic_deletions` → z=3.2:
   - `"sdelete.exe"`, `"sdelete64.exe"`
3. **`SUSPICIOUS_TOOL_SIGNS`** (nueva) — herramientas especializadas →
   `suspicious_executions`:
   - `"smallftpd.exe"`, `"netstumbler.exe"`,
     `"netstumblerinstaller_0_4_0 (1"`, `"veracrypt format.exe"`, `"veracrypt.exe"`

En el loop de detección: guard `_anti_forensic_exec_names` tiene precedencia sobre
`_suspicious_names | _suspicious_tool_names` para evitar doble-conteo.

### Tests de regresión agregados (8 nuevos tests)

`tests/test_prefetch_real.py::TestB132CalibrationFix`:

- `test_sdelete_goes_to_anti_forensic_not_suspicious` — sdelete en `anti_forensic_deletions`, NO en `suspicious_executions`
- `test_sdelete_triggers_z32_path` — `to_signal()` produce z=3.2 cuando sdelete está presente
- `test_sdelete64_also_anti_forensic` — variante 64-bit también detectada
- `test_smallftpd_goes_to_suspicious` — smallftpd en `suspicious_executions`
- `test_netstumbler_goes_to_suspicious` — netstumbler en `suspicious_executions`
- `test_veracrypt_format_goes_to_suspicious` — veracrypt format.exe (con espacio) en `suspicious_executions`
- `test_existing_mimikatz_still_in_suspicious` — regresión: mimikatz sigue en `suspicious_executions`
- `test_finding_type_in_metadata` — `finding_types` incluye ambos tipos cuando ambos disparan

Suite completa: **1376 passed, 0 failures** (vs 1368 antes del fix = +8 nuevos tests).

### Artefacto faltante en prepared/ — también corregido

`smallftpd-1.0.3-fix.lnk` existía en `cylr_extracted/.../Recent/` pero no había sido
copiado a `prepared/`. Copiado a `prepared/lnk_files/` como evidencia adicional.

### Gap permanente documentado — transfers.log / ftpd.ini / pcaps WiFi

Los siguientes artefactos **NO existen en la extracción CyLR** ni en el montaje del E01:
- `transfers.log` — log de transferencias FTP
- `ftpd.ini` — configuración del servidor FTP con `auto_run=1`
- WiFi pcaps — capturas de tráfico de red

Estos artefactos aparecen en el bundle del análisis Mode 2 de junio
(`results/agent_batch/VIGIA-REAL-VANKO_agent_bundle.json`) porque ese análisis
usó un case JSON pre-construido (`data/cases/converted/VIGIA-REAL-VANKO.json`) con 7
señales extraídas manualmente del E01 montado con ntfs-3g. **No vinieron del CyLR.**

Para obtenerlos de la extracción CyLR, buscar manualmente en:
- `cylr_extracted/.../Users/defaultprinter/` — posible ubicación de transfers.log y ftpd.ini
- `cylr_extracted/.../Users/PC User/` — posible ubicación alternativa

O extraerlos directamente del E01 con SIFT en una sesión separada.

### Comparación de veredictos — dos bundles preservados

| Bundle | Artefactos | PREFETCH z | Veredicto |
|--------|-----------|------------|-----------|
| `results/VIGIA-REAL-VANKO-2026_bundle.json` | Solo CyLR: registro, event logs, prefetch (sin sdelete detectado) | 1.75 (post-gamma) | **ABSTAIN** (CCS 1/2) |
| `results/VIGIA-REAL-VANKO-2026-v2_bundle.json` | CyLR + fix B-132 + LNK copiado | **2.24** (post-gamma; z_raw=3.2 × 0.70) | **ABSTAIN** (CCS 1/2 — tie genuino confirmado; bundle SHA-256: `7e0c2eb48479318c...`) |

El bundle ABSTAIN se preserva deliberadamente: demuestra que el motor sabe abstenerse
genuinamente en vez de alucinar un veredicto cuando la evidencia es insuficiente.

---

## B-133 — `knowledgeC.db` en `_MACOS_MARKER_FILES` activa la guarda B-048 y omite el motor iOS [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-16, sesión post-hackathon (`knowledgeC.db` agregado a `_IOS_MARKER_FILES` + dry-run de routing) |
| **Severidad** | P1 — el motor iOS se omite silenciosamente en cualquier extracción iOS que contenga knowledgeC.db |
| **Archivos** | `vigia/sift/macos_forensics.py` (`_MACOS_MARKER_FILES`), `vigia/sift/ios_forensics.py` (`_IOS_MARKER_FILES`), `vigia_agent.py` (guarda B-048) |
| **Detectado en** | VIGIA-MAGNET-2022-iOS-JESS, corrida RAW 2026-07-14 |
| **Síntoma observado** | `[SIFT_SHIM] iOS engine skipped for _extracted_full: directory also matched macOS strong markers; macOS engine takes precedence (B-048)` |

### Descripción

`vigia_agent.py` contiene una guarda B-048 que da precedencia al motor macOS cuando
el directorio de evidencia contiene archivos exclusivos de macOS:

```python
if all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES):
    kwargs["macos_evidence_path"] = str(evidence_path)
```

`_MACOS_MARKER_FILES` incluye `knowledgeC.db`. Este archivo **también existe en iOS**
(ruta: `/private/var/mobile/Library/CoreDuet/Knowledge/knowledgeC.db` — base de datos
de actividad de apps del subsistema CoreDuet). Cuando una extracción iOS contiene
`knowledgeC.db`, la diferencia `_MACOS_MARKER_FILES - _IOS_MARKER_FILES` no es vacía
y la guarda B-048 activa el motor macOS, dejando el motor iOS sin ejecutarse.

### Causa raíz (Peircean)

- **Firstness:** Motor iOS omitido con mensaje explícito B-048; `ios_evidence_path`
  no en kwargs; cero señales IOS_FORENSICS en el bundle.
- **Secondness:** `knowledgeC.db` está en `_MACOS_MARKER_FILES` como marcador de
  sistema macOS, pero en iOS sirve una función idéntica (timeline de actividad por app).
  El artefacto es multiplataforma; la lista de marcadores asume exclusividad.
- **Thirdness:** La guarda B-048 fue diseñada para evitar que extracción macOS
  con `History.db` sea procesada como iOS. La presencia de `knowledgeC.db` en
  `_MACOS_MARKER_FILES` pero no en `_IOS_MARKER_FILES` es un gap de cobertura:
  cualquier extracción iOS completa (GrayKey, UFED, etc.) que incluya el path de
  CoreDuet activa el motor equivocado.

### Fix diseñado

Agregar `knowledgeC.db` a `_IOS_MARKER_FILES` en `vigia/sift/ios_forensics.py`:

```python
_IOS_MARKER_FILES = {
    "sms.db", "AddressBook.sqlitedb", "CallHistory.storedata",
    "History.db", "Info.plist", "keychain-2.db",
    "signal.sqlite",
    "knowledgeC.db",  # B-133: iOS CoreDuet activity database — also present on iOS
}
```

Con este cambio, `_MACOS_MARKER_FILES - _IOS_MARKER_FILES` ya no incluye
`knowledgeC.db`, y la guarda B-048 solo activa el motor macOS para archivos
genuinamente exclusivos de macOS (TCC.db, .Spotlight-V100, etc.).

**Precaución:** Requiere dry-run completo sobre los 199 casos antes de aplicar —
existe riesgo de que algún caso macOS del corpus tenga `knowledgeC.db` como único
marcador y pase a procesar como iOS erróneamente.

### Workaround (sesión 2026-07-14)

Mover `knowledgeC.db` y `knowledgeC.db-wal` a un subdirectorio `_mode2_only/`
fuera del path de evidencia de Mode 1. Permite que el motor iOS se ejecute
correctamente. No modifica código.

### Impacto documentado en el caso VIGIA-MAGNET-2022-iOS-JESS

Primera corrida Mode 1 contra `_extracted_full/` (con `knowledgeC.db`): motor iOS
omitido, bundle con cero señales de ios_forensics, ABSTAIN por falta de señales.
Segunda corrida (después de mover `knowledgeC.db` a `_mode2_only/`): motor iOS
correctamente invocado, 22 findings, IOS_FORENSICS z=2.80, bundle sealed.

### Fix aplicado (2026-07-16)

`knowledgeC.db` agregado a `_IOS_MARKER_FILES` en `vigia/sift/ios_forensics.py`
(con comentario B-133 explicando la colisión multiplataforma). Con esto,
`_MACOS_MARKER_FILES - _IOS_MARKER_FILES` queda con marcadores genuinamente
exclusivos de macOS (TCC.db, .fseventsd, .Spotlight-V100, system.log,
QuarantineEventsV2, plists) y la guarda B-048 de `vigia_agent.py` ya no
secuestra extracciones iOS completas.

### Verificación

- Red tests: `tests/test_b133_knowledgec_ios_marker.py` (6 tests):
  - extracción iOS completa (sms.db + knowledgeC.db + Info.plist) → routing iOS,
    macOS NO activado;
  - extracción macOS real (History.db + knowledgeC.db + TCC.db + system.log) →
    routing macOS intacto;
  - directorio que matchea ambos motores → ambos paths al mismo directorio, que
    es exactamente el caso que la guarda de precedencia del shim
    (`sift_orchestrator.py`, iOS skipped) sigue resolviendo;
  - regresión B-048: el set exclusivo macOS sigue no-vacío (>= 5 marcadores).
- Dry-run de routing sobre los directorios con marcadores presentes en el repo
  (2 directorios: `cases/tuck-2019-macos/Preferences`, `cases/tuck-2019-macos/Safari`):
  cero flips pre/post.
- **Cobertura honesta del dry-run:** los casos JSON del corpus (201) no ejercitan
  el routing por marcadores (son archivos únicos, no directorios de evidencia), y
  el repo no contiene extracciones raw macOS/iOS completas (JESS/VANKO viven fuera
  del repo). El riesgo residual documentado en el diseño — un caso macOS cuyo
  ÚNICO marcador exclusivo sea `knowledgeC.db` — no tiene instancia en el repo;
  toda extracción macOS real del corpus usado hasta ahora incluye TCC.db o
  .fseventsd. Si apareciera un caso así, flipearía a iOS: queda anotado como
  limitación de cobertura del gate, no como regresión observada.

---

## B-134 — `_detect_installed_apps` no detecta Wire via `store.wiredatabase` — brecha UUID de iOS [RESUELTO — Wire; WeChat documentado como limitación]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (Wire) — 2026-07-16, sesión post-hackathon. WeChat via keychain sigue como limitación documentada (sin fix portátil entre versiones) |
| **Severidad** | P2 — falso negativo en detección de Wire; WeChat requiere análisis separado |
| **Archivo** | `vigia/sift/ios_forensics.py::_detect_installed_apps` |
| **Detectado en** | VIGIA-MAGNET-2022-iOS-JESS, análisis Mode 2 2026-07-14 |

### Descripción

`_detect_installed_apps` detecta aplicaciones instaladas en iOS mediante dos mecanismos:

1. Búsqueda de directorio con nombre de bundle ID (ej. `"com.wire"`, `"com.tencent.xin"`)
2. Caso especial para Signal: presencia del archivo `signal.sqlite` independientemente
   del nombre de directorio

iOS almacena apps de terceros en directorios nombrados con UUID, no con bundle ID:
`/private/var/mobile/Containers/Data/Application/<UUID>/`. Ningún directorio tiene
nombre `com.wire` ni `com.tencent.xin` — la búsqueda por bundle ID produce cero
resultados para ambas apps.

**Wire:** La extracción del caso VIGIA-MAGNET-2022-iOS-JESS contiene
`store.wiredatabase` (base de datos de mensajes de Wire). Este archivo existe porque
ios_forensics.py tiene lógica para buscarlo y extraerlo: la app está instalada y
tiene datos. Sin embargo, no hay mecanismo para que este hallazgo se retroalimente
a `_detect_installed_apps` como señal de app instalada.

**WeChat:** Únicamente presente como residuo en `keychain-2.db` (credenciales
guardadas). Sin contenedor de app ni base de datos de mensajes en la extracción —
WeChat probablemente fue desinstalada o el GrayKey no extrajo su contenedor.
`_detect_installed_apps` no tiene lógica de keychain.

### Causa raíz

La detección de Signal mediante `signal.sqlite` es un caso especial hardcodeado.
El mecanismo general (búsqueda por nombre de directorio con bundle ID) no funciona
en iOS porque el sistema operativo usa UUIDs para los contenedores de apps.
Cada app de mensajería adicional requiere su propio caso especial filename-based.

### Fix diseñado — Wire

Agregar detección por filename en `_detect_installed_apps`:

```python
# B-134: Wire detection via store.wiredatabase (same pattern as signal.sqlite)
if (evidence_path / "store.wiredatabase").exists():
    apps.append("Wire")
```

**Precaución:** Requiere dry-run corpus. `store.wiredatabase` es específico de Wire
y no es un nombre de archivo ambiguo, por lo que el riesgo de falso positivo es bajo.

### Fix diseñado — WeChat (parcial)

WeChat no tiene un nombre de archivo de base de datos único y portátil que sea
confiable entre versiones. La detección via keychain requiere parsear
`keychain-2.db` y cruzar los `server` fields contra dominios WeChat conocidos.
Más complejo que el fix de Wire — documentar como limitación separada (L-059 o
nueva entrada) hasta tener casos de calibración.

### Gap de cobertura permanente — apps con UUID container solamente

Apps que no dejan ningún archivo con nombre distintivo fuera de su contenedor UUID
son indetectables por `_detect_installed_apps` sin acceso al manifiesto de
instalación (`applicationState.db` o `MobileInstallation.plist`). Estos archivos
sí existen en extracciones completas pero no son parseados por ios_forensics.py.
Documentado como limitación de cobertura, no bug a resolver en esta tanda.

### Fix aplicado (2026-07-16) — Wire

Detección por filename de `store.wiredatabase` en `_detect_installed_apps`
(`vigia/sift/ios_forensics.py`), mismo patrón y peso que el caso especial de
`signal.sqlite`: raíz del directorio de evidencia + un nivel de subdirectorio,
guard anti doble-conteo si el contenedor `com.wire` ya fue detectado por
bundle ID. Severidad `Fraction(60, 100)`, consistente con la entrada
`com.wire` de `ENCRYPTED_APPS`.

WeChat NO se toca en esta tanda (sin filename portátil entre versiones;
requiere parseo de keychain — sigue como limitación documentada arriba).

### Verificación

- Red tests: `tests/test_b134_wire_filename_detection.py` (5 tests): detección
  en raíz y en subdirectorio, no doble-conteo con contenedor bundle-ID presente,
  regresión del caso Signal, directorio vacío sin falsos positivos.
- `store.wiredatabase` es un nombre específico de Wire (riesgo de falso positivo
  bajo, igual que el diseño preveía). Gate de corpus sin cambios de veredicto.

---

## B-135 — `SecurityAudit` defaultea `_DEFAULT_LOG_DIR` a `VIGIA_EVIDENCE_DIR` — escribe `security_audit.log` en directorio de evidencia [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-16, sesión post-hackathon (Opción A: `VIGIA_LOG_DIR`, consistente con `vigia/config.py`) |
| **Severidad** | P2 — violación del principio de evidencia read-only; no afecta la integridad del análisis |
| **Archivo** | `vigia/security/security.py`, línea 47: `_DEFAULT_LOG_DIR` |
| **Detectado en** | VIGIA-MAGNET-2022-iOS-JESS, dos corridas Mode 1 RAW 2026-07-14 |
| **Síntoma observado** | `security_audit.log` creado en `evidence/magnet-2022-ios-jess/Jess_CTF_iPhone8/_extracted_full/` tras cada corrida `vigia_agent.py` |

### Descripción

```python
# vigia/security/security.py línea 47
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_EVIDENCE_DIR", "/var/log/vigia")
```

Cuando `VIGIA_EVIDENCE_DIR` está configurado (requerido por la guía de investigación
del CLAUDE.md), `SecurityAudit.__init__` construye la ruta del log como:

```
Path(VIGIA_EVIDENCE_DIR) / "security_audit.log"
```

Esto escribe el archivo de audit directamente en el directorio de evidencia, violando
el principio "Evidence is read-only. Never write to VIGIA_EVIDENCE_DIR." (CLAUDE.md §5.1,
VIGÍA CLAUDE.md Invariante 1).

### Causa raíz

`_DEFAULT_LOG_DIR` usa `VIGIA_EVIDENCE_DIR` como ruta de fallback conveniente —
en el contexto original (pre-SIFT), este valor siempre era `/var/log/vigia` o
similar. Cuando el investigador configura `VIGIA_EVIDENCE_DIR` a un directorio de
evidencia forense real, el log termina en ese directorio.

### Fix diseñado

Separar `_DEFAULT_LOG_DIR` de `VIGIA_EVIDENCE_DIR`:

```python
# Opción A — nueva variable de entorno
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")

# Opción B — ruta fija relativa al repo
_DEFAULT_LOG_DIR: Final[str] = os.getenv("VIGIA_LOG_DIR", str(Path(__file__).parents[2] / "logs"))
```

La Opción A es preferible: respeta la configuración existente vía entorno, no
asume la estructura del repo, y da al operador control explícito. `VIGIA_LOG_DIR`
debería documentarse en INSTALL.md y en la sección de variables de entorno del CLAUDE.md.

**Precaución:** Cambio de comportamiento observable para cualquier instalación donde
`VIGIA_LOG_DIR` no está configurado y `VIGIA_EVIDENCE_DIR` apunta a `/var/log/vigia`
(instalaciones por defecto antiguas). Verificar que ningún test hardcodea la ruta del
log de auditoría como dependiente de `VIGIA_EVIDENCE_DIR`.

### Mitigación hasta que el fix esté aplicado

Configurar `VIGIA_LOG_DIR` explícitamente antes de invocar `vigia_agent.py`:

```bash
export VIGIA_LOG_DIR="/tmp/vigia_logs"
python3 vigia_agent.py --evidence "$VIGIA_EVIDENCE_DIR" --case-id CASE-001
```

O eliminar manualmente `security_audit.log` del directorio de evidencia después
de cada corrida (workaround del caso VIGIA-MAGNET-2022-iOS-JESS: eliminado manualmente
dos veces durante la sesión 2026-07-14).

### Fix aplicado (2026-07-16)

Opción A del diseño: `_DEFAULT_LOG_DIR = os.getenv("VIGIA_LOG_DIR", "/var/log/vigia")`
en `vigia/security/security.py`. Hipótesis benigna ("el default era intencional")
refutada empíricamente: `vigia/config.py` ya resolvía `log_dir` desde
`VIGIA_LOG_DIR` con el mismo default — el uso de `VIGIA_EVIDENCE_DIR` en
security.py era una inconsistencia, no una decisión. `VIGIA_LOG_DIR` documentado
en INSTALL.md (sección 7, campos opcionales) y en la sección Environment
Prerequisites del CLAUDE.md.

El fallback seguro existente (`_create_secure_fallback_log`, tempdir 0o700 +
mkstemp 0o600) cubre el caso donde `/var/log/vigia` no es escribible — sin
cambio de comportamiento para instalaciones que ya seteaban `log_path` explícito.

### Verificación

- Red tests: `tests/test_b135_security_log_dir.py` (5 tests): el default ignora
  `VIGIA_EVIDENCE_DIR`, honra `VIGIA_LOG_DIR`, fallback `/var/log/vigia`,
  end-to-end `SecurityAudit()` + `log_info()` deja el directorio de evidencia
  byte a byte intacto, y `log_path` explícito sigue ganando.
- Precaución del diseño verificada: ningún test del repo hardcodea la ruta del
  audit log como dependiente de `VIGIA_EVIDENCE_DIR` (suite completa verde).

---

## B-136 — El patrón "inyección a CAIE" fuera del scorer es un no-op estructural: engines locales descartados + kwargs inexistentes en 3 de 4 sitios [RESUELTO — Opción 1 aplicada]

> **Resolución (2026-07-17, decisión delegada por la mantenedora, calibración
> en docs/PROPUESTA_B136_CAIE_WIRING_20260717.md):** Opción 1 en dos fases.
> **Fase 1:** perfiles `linguistic_forensics` (0.60/0.18), `batch_forensics`
> (0.45/0.22), `temporal_fraud` (0.55/0.20) en `EVIDENCE_PROFILES` (analogía
> con la escala existente, método B-066; cero apariciones en corpus =
> extensión sin efecto retroactivo); rol B-070 `CONTEXTUAL` para los tres
> (informan el composite, NO corroboran el gate DEVICE); dominio de
> recolección `content_artifact`/`D5-soft` (N fracturas del MISMO documento
> o lote están correlacionadas — exentarlas del decay de cola dejaría que un
> solo documento infle el composite: el drowning que R4-3 mató).
> `document_visual`/`document_geometry` quedan DEVICE (asimetría documentada;
> reclasificar tiene efecto retroactivo y exige su propia corrida).
> **Fase 2:** los cuatro sitios ya no instancian engines efímeros: cada tool
> CONSTRUYE artefactos listos-para-caso y los expone en su resultado bajo
> `caie_artifacts` (raw_score clampeado a [0,1]; adversarial_nlp normaliza
> con min(1,(mcp-1)/4) — la decisión B-115 disuelta es ahora el único punto
> de conversión; el diseño original pasaba mcp∈[1,5] crudo). Los logs de
> éxito falsos (`CAIE_ARTIFACT_INJECTED`, `ENTANGLEMENT_CAIE_INJECTED`)
> fueron eliminados; `analyze_and_inject` → `analyze_and_build_artifacts`
> (cero callers al renombrar). **Verificación:** 23 tests nuevos
> (`tests/test_b136_document_domain_profiles.py`,
> `tests/test_b136_caie_wiring.py`, red-first: 12 y 9 en rojo pre-fix);
> suite completa 1440 passed / 0 failed; corpus gate en vivo 189/201 PASS,
> 199 casos comunes vs baseline, CERO flips (`fixed==0` es lo esperado: los
> tipos nuevos no existen en el corpus; el cableado no mueve veredictos
> hasta que el ensamblador de casos incorpore `caie_artifacts`). Pendiente
> aguas abajo: que el ensamblador de casos incorpore `caie_artifacts` del
> resultado de cada tool a `case["artifacts"]` — punto único de integración,
> fuera del alcance de este fix.

> **Fase 3 (2026-07-17): ensamblador cerrado.** `ForensicAdapter.build_context`
> ahora absorbe los `caie_artifacts` que las tools exponen en `raw_results`
> (punto único para ambos ensambladores: pipeline y sift orchestrator), con
> contrato fail-closed: entradas malformadas se saltean, raw_score clampeado
> a [0,1], custody metadata jamás sintetizada (ley B-131: degradación honesta
> dentro de CAIE). `vigia/pipeline/pipeline.py` pasa los resultados de visión
> (única de las 4 tools que invoca directamente). Tests:
> `tests/test_b136_case_assembly.py` (6, red-first). Suite 1455/0. Corpus
> gate: 189/201, CERO flips — esperado y honesto: los casos JSON no ejercitan
> el loop de visión con imágenes; el primer caso con evidencia visual real
> ejercitará el camino completo.

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — Opción 1 aplicada 2026-07-17 en tres fases (perfiles de dominio documento, wiring de las 4 tools a `caie_artifacts`, absorción en el ensamblador de casos); ver bloque de resolución arriba |
| **Severidad** | P2 — dead code que emite logs de auditoría falsos (`CAIE_ARTIFACT_INJECTED` sin efecto real); ninguna fractura de estos tools llegó jamás al veredicto |
| **Archivos** | `vigia/tools/adversarial_nlp.py:1595`, `vigia/core/entanglement.py:597`, `vigia/forensics/temporal_forensics_redteam.py:740`, `vigia/forensics/vision_audit.py:514` |
| **Detectado en** | Sesión post-hackathon 2026-07-16, auditoría B-114/B-115 |

### Descripción (Peirceana)

- **Firstness:** Cuatro sitios construyen `caie = CrossArtifactIncongruenceEngine()`
  como variable local, agregan artifacts, y la función retorna sin que nada lea el
  engine (`detect_fractures()` nunca se llama sobre esa instancia; el objeto se
  descarta). No existe ningún singleton ni engine compartido en el repo: censo de
  instanciaciones = scorer (`vigia_scorer.py:652`, construye el suyo desde las
  señales del caso), self-tests de caie.py, y estos 4 sitios.
- **Secondness:** El único consumidor real de CAIE es el scorer, que construye su
  engine desde los artifacts sellados del caso vía `add_artifact()`. Una API de
  inyección solo tiene efecto si alguien lee el engine inyectado. El baseline
  correcto (vision_audit docstring: "Produces DOCUMENT_FORGERY fractures
  automatically") nunca fue verdad: la fractura se produciría solo dentro del
  objeto descartado.
- **Thirdness:** La ley: "inyectar en un engine efímero es código muerto que
  además produce trail de auditoría engañoso". `vision_audit` loguea
  `CAIE_ARTIFACT_INJECTED` como éxito; `entanglement` loguea
  `ENTANGLEMENT_CAIE_INJECTED`. Para una herramienta que reclama trail Daubert,
  un log de auditoría que afirma una inyección sin efecto es un problema de
  integridad del trail, no solo deuda técnica.

### Censo de los 4 sitios

| Sitio | Firma de llamada | evidence_type pasado | ¿En whitelist? | Doble rotura |
|-------|------------------|----------------------|----------------|--------------|
| `vision_audit.py:543,552` | CORRECTA (`tool_name=`, `result=`) | `document_visual` / `document_geometry` | Sí | Solo engine descartado |
| `adversarial_nlp.py:1597` (B-115) | ROTA (`source_tool=`, `raw_score=`, ...) → TypeError silenciado | `linguistic_forensics` | **NO** | kwargs + engine descartado + tipo fuera de whitelist |
| `entanglement.py:599` | ROTA (mismos kwargs inexistentes) | `batch_forensics` | **NO** | kwargs + engine descartado + tipo fuera de whitelist |
| `temporal_forensics_redteam.py:741` | ROTA (mismos kwargs inexistentes) | `temporal_fraud` | **NO** | kwargs + engine descartado + tipo fuera de whitelist |

### Por qué NO se aplicó el fix mecánico de B-115 (refutación tipo Eco)

El fix "obvio" (corregir kwargs) fue evaluado y **rechazado**: hoy la llamada rota
lanza TypeError y queda logueada honestamente como `CAIE_INJECTION_FAILED`.
Corregir solo los kwargs convertiría ese fallo honesto en un **éxito falso**
(inyección a objeto descartado, sin efecto, con log de éxito) — estrictamente
peor bajo el estándar de honestidad del trail. El fix real es arquitectónico.

### Hallazgo lateral que disuelve la "decisión de normalización" de B-115

`adversarial_nlp.py:1131` ya define `confidence = min(1.0, (mcp - 1.0) / 4.0)` —
las dos opciones que B-115 contraponía (`(mcp-1)/4` vs `verdict.confidence`)
son el mismo valor. Cuando se cablee el fix arquitectónico, `verdict.confidence`
es el `raw_score` correcto sin necesidad de decisión adicional.

### Fix diseñado (pendiente de decisión de Anna)

1. **Routing:** las fracturas de estos tools deben llegar al engine que el scorer
   construye — la vía natural es que los tools emitan sus hallazgos como
   artifacts/señales del caso (mismo camino que todo lo demás), NO que mantengan
   engines paralelos. Eliminar los 4 bloques de inyección local y sus logs.
2. **Perfiles:** si se desea que estos artifacts pesen en CAIE, agregar
   `linguistic_forensics`, `batch_forensics`, `temporal_fraud` a
   `EVIDENCE_PROFILES` con spoofability calibrada (decisión de calibración
   forense — misma clase que B-092).
3. **Gate:** cualquier cableado real requiere corrida comparativa de corpus
   (regla `fixed>=1 AND broken==0`), porque fracturas nuevas mueven veredictos.

### Relación con B-114 y B-115

- B-114 (bypass de guardrails en `add_from_tool_result`) queda RESUELTO — el
  wrapper ahora delega en `add_artifact()`. Esto NO arregla B-136 (el engine
  sigue siendo descartado), pero cierra el hueco estructural para cualquier
  caller futuro del wrapper.
- B-115 queda SUBSUMIDO en esta entrada: su alcance real es 3 sitios, no 1, y
  el fix mecánico está refutado (ver arriba).

---

## B-137 — `TCC.db` en `_MACOS_MARKER_FILES` activa la guarda B-048 y omite el motor iOS (residual de B-048, hermano de B-133) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-17 (`TCC.db` agregado a `_IOS_MARKER_FILES`, mismo patrón que B-133) |
| **Severidad** | P2 — el motor iOS se omite silenciosamente en cualquier extracción iOS full-filesystem que contenga TCC.db |
| **Archivos** | `vigia/sift/ios_forensics.py` (`_IOS_MARKER_FILES`), `vigia_agent.py` (comentario de la guarda B-048) |
| **Detectado por** | Auditoría adversaria de Kimi K-1 (2026-07-17) sobre el branch `claude/unresolved-bugs-1231gn` |
| **Documentado previamente como** | "Riesgo residual documentado" bajo la entrada B-048 (nunca cerrado, sin ID propio) |

### Descripción

Idéntica clase de bug que B-133. La guarda B-048 da precedencia al motor macOS
cuando el directorio de evidencia contiene marcadores exclusivos de macOS:

```python
if all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES):
    kwargs["macos_evidence_path"] = str(evidence_path)
```

`_MACOS_MARKER_FILES` incluía `TCC.db`. Este archivo **también existe en iOS**
(ruta: `/private/var/mobile/Library/TCC/TCC.db` — base de datos del subsistema
de privacidad Transparency, Consent & Control). Una extracción iOS full-filesystem
que contenga `TCC.db` hace que la diferencia `_MACOS_MARKER_FILES - _IOS_MARKER_FILES`
no sea vacía → se activa el motor macOS → el motor iOS no se ejecuta → se pierden
los findings iOS-específicos (SMS, contacts, calls).

### Causa raíz (Peircean)

- **Firstness:** `macos_evidence_path` seteado y `ios_evidence_path` presente para
  el mismo directorio; la precedencia del shim corre solo macOS; cero señales
  IOS_FORENSICS.
- **Secondness:** `TCC.db` estaba en `_MACOS_MARKER_FILES` como marcador macOS,
  pero TCC es un subsistema de Apple presente en ambas plataformas. El artefacto
  es multiplataforma; la lista de marcadores asumía exclusividad.
- **Thirdness:** Misma ley que B-133 — cualquier artefacto cross-platform presente
  en exactamente uno de los dos sets rompe la resta de exclusividad. El propio
  comentario de la guarda B-048 (`vigia_agent.py`) admitía este residual para
  TCC.db pero delegaba en el "shim precedence guard", que solo cubre el caso
  same-directory, no la atribución de plataforma equivocada.

### Fix aplicado (2026-07-17)

`TCC.db` agregado a `_IOS_MARKER_FILES` en `vigia/sift/ios_forensics.py` (con
comentario B-137 explicando la colisión). Con esto,
`_MACOS_MARKER_FILES - _IOS_MARKER_FILES` conserva 7 marcadores genuinamente
exclusivos de macOS (`.fseventsd`, `.Spotlight-V100`, `system.log`,
`QuarantineEventsV2`, `com.apple.loginitems.plist`, `com.apple.recentitems.plist`,
`SystemVersion.plist`) y la guarda B-048 ya no secuestra extracciones iOS. El
comentario de la guarda en `vigia_agent.py` se actualizó (ya no describe TCC.db
como residual abierto).

### Riesgo simétrico (aceptado, misma clase que B-133)

Un directorio macOS cuyo ÚNICO marcador exclusivo fuera `TCC.db` ahora ruteaería a
iOS. Tan hipotético como el caso de knowledgeC.db: toda extracción macOS real del
corpus incluye `.fseventsd`/`system.log`/etc., y el motor iOS sobre un TCC.db
macOS-only produce ~cero findings (benigno y visible). La solución de fondo
(routing por layout de directorios en vez de por nombres) queda para cuando exista
un caso macOS real en el corpus que lo ejercite.

### Verificación

- `tests/test_b137_tcc_ios_marker.py` (6 tests): extracción iOS con TCC.db → routing
  iOS, macOS NO activado; extracción macOS real → routing macOS intacto; knowledgeC.db
  (B-133) + TCC.db (B-137) juntos con marcador iOS → routing iOS puro; regresión B-048:
  el set exclusivo macOS sigue >= 5.
- **Inducción pre/post:** contra el estado pre-fix (TCC.db fuera de `_IOS`), 4 de 6
  tests fallan — el fallo de routing muestra `macos_evidence_path` seteado para una
  extracción iOS con TCC.db, exactamente el hijack. Post-fix: 12/12 (B-137 + B-133).
- El testigo `assert "TCC.db" in exclusive` del test de B-133 se corrigió a
  `system.log` (TCC.db dejó de ser marcador macOS-exclusivo; la aserción codificaba
  la creencia falsa que B-137 corrige — el invariante protegido, set exclusivo >= 5,
  se conserva).
- **Cobertura honesta:** igual que B-133, los 201 casos JSON del corpus no ejercitan
  el routing por marcadores; no hay extracción raw iOS/macOS full en el repo. El fix
  se sostiene por la clase de bug ya confirmada en B-133, no por un caso raw nuevo.

---

## B-138 — Dos tests fuera de `tests/e2e` importaban `mcp` en duro y rompían la colección completa de pytest en entornos sin `mcp` [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-17 (`pytest.importorskip("mcp")` en los 4 puntos dependientes) |
| **Severidad** | P3 (higiene de suite — sin efecto en veredictos) |
| **Archivos** | `tests/test_grupob_b9_honey_token_lifecycle.py`, `vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py`, `tests/test_h4_grep_sanitizer_unification.py`, `tests/test_b10_comparator_reads_sealed_verdict.py` |
| **Detectado en** | Sesión de revisión abductiva 2026-07-17 (corrida de suite en entorno sin `mcp`) |

### Descripción

L-045 documenta que `mcp` no es instalable en entornos CI mínimos, y la
doctrina de suite excluye `tests/e2e` por esa razón. Pero dos archivos fuera
de `tests/e2e` importaban el bridge (que importa `mcp`) a nivel de módulo:
la colección entera de pytest abortaba con "Interrupted: 3 errors during
collection" antes de correr un solo test. Además, 5 tests en otros dos
archivos importaban el bridge (directo o vía `run_llm_cases`) dentro del
cuerpo del test y fallaban como FAILED en vez de saltearse.

### Fix

`pytest.importorskip("mcp")` antes del import del bridge en los dos archivos
que rompían la colección; skip puntual en `test_bridge_reexports_canonical`
(h4) y fixture autouse en `TestLlmFallbackReadsSealedVerdict` (b10). En
entornos con `mcp` instalado nada cambia (importorskip es no-op y los tests
corren igual que antes).

### Verificación

- Pre-fix (inducción, entorno sin `mcp`): colección interrumpida con 3
  errores; con esos 2 archivos excluidos a mano, 5 FAILED por
  `ModuleNotFoundError: mcp`.
- Post-fix: los 4 archivos dan 22 passed / 7 skipped / 0 failed y la suite
  completa (sin `tests/integration` ni `tests/e2e`) colecciona y corre
  verde en el mismo entorno.

---

## B-139 — Scans de marcadores `rglob("*")` sin acotar en los tres motores mobile/macOS (residuo §1.3 de WHAT_IS_NEXT) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-17 (`scan_marker_names()` acotado en `vigia/sift/_fs_utils.py`, 3 call-sites migrados) |
| **Severidad** | P3 (robustez de recursos — sin efecto en veredictos para árboles dentro del límite, que son todos los reales) |
| **Archivos** | `vigia/sift/ios_forensics.py`, `vigia/sift/android_forensics.py`, `vigia/sift/macos_forensics.py`, `vigia/sift/_fs_utils.py` (nuevo) |
| **Detectado en** | Residuo documentado en WHAT_IS_NEXT §1.3 (S4 / AUDITORIA_COBERTURA_MOBILE_SIFT §C); retomado en la sesión de revisión abductiva 2026-07-17 |

### Descripción

S4 acotó los lookups por patrón con `_safe_rglob` (heapq.nsmallest, memoria
O(limit)), pero la validación de marcadores de los tres motores seguía
materializando TODOS los nombres del árbol
(`{f.name for f in evidence_path.rglob("*")}`) antes de intersecar con el
set de marcadores: memoria O(árbol) y caminata sin límite ante un árbol de
evidencia hostil o gigante — la misma clase que S4 cerró para el resto.

### Fix

Helper compartido `scan_marker_names()` (mismo patrón de módulo que
`_math_utils`/`_sql_utils`): retiene solo nombres que SON marcadores
(memoria O(markers)), filtra symlinks, cuenta directorios solo con
`include_dirs=True` (macOS: `.fseventsd` es marcador de directorio), y
corta la caminata en `MARKER_SCAN_MAX_ENTRIES` (500k) con WARNING visible
— degradación honesta, nunca silenciosa. Para árboles dentro del límite el
resultado es idéntico al patrón viejo (pin de equivalencia en los tests).

**Refutación aplicada (alcance):** el bloque Magisk de `_detect_root`
(`list(evidence_path.rglob("com.topjohnwu.magisk"))` etc.) se deja
deliberadamente intacto: sus `len()` alimentan el string de evidencia del
finding (cambiarlos alteraría narrativa emitida) y son lookups por nombre
específico — no `rglob("*")` — con puñados de matches en la práctica.

### Verificación

- `tests/test_b139_bounded_marker_scan.py` (15 tests, rojos primero):
  contrato del helper (equivalencia con el patrón viejo, symlinks,
  dirs/include_dirs, truncado con WARNING y sin WARNING dentro del límite)
  + pins de los tres motores (marcador detectado / nota de "No *-specific
  artifacts" intacta en ambas direcciones, incluido `.fseventsd` como dir).
- Pins mobile existentes (B-086/B-133/B-137 y afines): 256 passed.
- **Cobertura honesta (misma salvedad que B-133/B-137):** los 201 casos
  JSON del corpus no ejercitan el scan de marcadores sobre árboles raw; la
  equivalencia se sostiene por el pin de equivalencia y los pins de motor,
  no por una corrida de corpus (que trivialmente daría 0 flips).

---

## B-140 — L-029/FW-009 Fase 1: el detector DARVO era estructuralmente ciego al path motor; anotación cableada sin efecto en veredicto [RESUELTO — Fase 1]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (Fase 1: anotación) — 2026-07-17. El efecto en veredicto, `false_flag` como tipo de veredicto y la revisión pareada cross-bundle siguen abiertos como doctrina/arquitectura (ver L-029) |
| **Severidad** | P2 (el patrón HIGH más antiguo del registro de limitaciones sin progreso de código desde 2026-06-24) |
| **Archivos** | `vigia/core/darvo_detector.py`, `vigia_scorer.py` (Step 4c), `sift_orchestrator.py` (`_motor_darvo_summary` + canal), `vigia_agent.py` (sección de narrativa) |
| **Detectado en** | Sesión de revisión abductiva 2026-07-17 (verificación de L-029 contra código vivo) |

### Descripción (Peirceana)

- **Firstness:** `compute_darvo_penalty` lee campos con `getattr()` únicamente.
  Los artefactos del path Modo 1 (EBS JSON) son dicts planos → `getattr`
  devuelve default → el detector retorna 0 SIEMPRE fuera del pipeline.
  KIWI-001-A02 ("PHP error ... trampolin", log_entry) y A04 ("Blog honeypot
  ... accesos ... bloqueado", file_metadata) contienen exactamente los
  keywords del detector y jamás dispararon en el path motor.
- **Secondness:** El único caller era `VigiaPipeline` (objetos SignalOutput).
  El caso canónico de L-029 (KIWI) corre por el path motor — donde el
  detector era invisible por construcción. La limitación decía "no cableado
  al orchestrator/agente"; la realidad era peor: aunque se cableara, con
  dicts no podía disparar.
- **Thirdness:** La ley: un detector que asume el shape de UN caller queda
  mudo en silencio frente a los demás — misma clase que B-136 (inyección a
  engine efímero) y B-063 (metadata=None): el fallo estructural silencioso
  en la frontera de formatos.

### Fix (Fase 1 — anotación, cero movimiento de veredicto)

1. `_field()` en el detector: lee dict O objeto; total frente a campos
   malformados (str() coercion, metadata no-dict). El comportamiento con
   objetos (pipeline) queda PINEADO sin cambios.
2. `detect_darvo_pattern()` estructurado: conteos, penalidad Fraction, ids
   de artefactos disparadores (trazabilidad Daubert).
   **Calibración de la anotación (refutación medida):** `pattern_present`
   exige la asimetría COMPLETA (vigilancia Y cero-contacto). Con keywords
   de vigilancia solos ('log', 'server'...) anotaban 52/201 casos del
   corpus (incluidos benignos) — narrativa engañosa; con ambos lados,
   exactamente los 5 correctos (KIWI-001/003/004/005 +
   MAGNET-2021-IOS-ELI, este último ya candidato a revisión de etiqueta en
   B-097). La penalidad conserva la fórmula original: es el contrato del
   pipeline (consistency_score) y no se tocó.
3. `_vigia_score` Step 4c: bloque `darvo_pattern` en la salida sellada
   (penalidad como str, conteos, ids, `verdict_effect: none`). SOLO
   anotación — ni veredicto ni score cambian.
4. Canal de narrativa: `_motor_darvo_summary` (mismo shape B-094) →
   `results["darvo"]` → sección "DARVO PATTERN" en la narrativa sellada,
   que declara explícitamente que el veredicto NO fue modificado.

### Verificación

- `tests/test_b140_darvo_motor_annotation.py` (17 tests, rojos primero):
  soporte dict + pin de objetos (valores pre-B-140 exactos), asimetría
  completa requerida, malformados no crashean, anotación fiel en el scorer,
  pin de igualdad veredicto/score/confianza contra gemelo sin keywords,
  helper del orchestrator, y el caso real KIWI-001 (2 vigilancia +
  cero-contacto, penalidad 3/5).
- **Gate comparativo (worktree limpio en HEAD vs árbol con el cambio,
  `run_all_agent --rerun` completo en ambos):** 201 casos comunes,
  **CERO flips de veredicto**. Un primer baseline se descartó por
  contaminación (corrió con el árbol a mitad de edición — subprocess por
  caso re-importa de disco); el gate válido usó worktree aislado.
- Suite completa verde (ver commit).
- `results/` restaurado vía `git checkout -- results/` tras el gate
  (práctica B-097: los bundles regenerados no se commitean).

### Corrección F0 (2026-07-17, tanda firmada — nunca en silencio)

El claim de calibración "exactamente los 5 correctos" era **falso**: la
investigación L-029 (dossier + auditoría independiente de Kimi, ambas
verificadas por ejecución) demostró que MAGNET-2021-IOS-ELI era un falso
positivo de substrings — `'server'` matcheaba dentro de "4 S3 server list
URLs" y `'no contact'` dentro de "no messages, no contactS database" (un
plural inglés); el caso es mono-actor, sin estructura DARVO. Tasa observada
pre-F0: 1 FP / 5 disparos. F0 introdujo matching con word-boundaries
(B-142): el censo honesto es **exactamente 4 anotados = KIWI-001/003/004/005,
o sea UN expediente (MPF7779408) + 2 copias declaradas — N=1 real**. La
divergencia B-097 de ELI (Claude ciego INTENT vs etiqueta SUSPICION) es de
intención de evasión, no de DARVO — issues independientes. Ver
`docs/PROPUESTA_L029_DARVO_20260717.md` §1 y B-142.

---

## B-141 — `run_vigia` descarta TODAS las señales por TypeError silencioso (`description=` a un `SignalOutput` que no tiene ese campo) [RESUELTO — F0]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — F0 (2026-07-17, tanda firmada): helper `_signals_from_dicts` sin el kwarg `description` inexistente; test en AMBOS deployments (pydantic in-process + dataclass vía subprocess con pydantic enmascarado, adición del veredicto de Kimi §1) en `tests/test_f0_l029_darvo_hardening.py` |
| **Severidad** | P1 — el camino `run_vigia` ejecuta el pipeline con CERO señales en el deployment dataclass |
| **Archivo** | `vigia/pipeline/pipeline.py:1382-1392` |
| **Detectado en** | Investigación abductiva L-029 (`docs/PROPUESTA_L029_DARVO_20260717.md` §6), juez de ingeniería, verificado por el sintetizador |

### Descripción

La conversión dict→SignalOutput de `run_vigia` pasa `description=d.get("description")`,
pero `SignalOutput` (`vigia/tools/signal_contract.py`) solo tiene
`tool_name, signal_id, value, z_score, confidence, metadata`. En el deployment
dataclass la construcción lanza `TypeError: unexpected keyword argument
'description'`; el `try/except` por señal loguea "Señal inválida ignorada" y
descarta la señal — TODAS las señales, siempre. Verificado por ejecución en este
árbol. Bajo pydantic v2 (extra ignorado) la señal sobrevive pero `description` se
descarta en silencio.

### Fix pendiente

Retirar el kwarg inexistente (o mover description a metadata), test rojo primero
que fije que `run_vigia` construye señales desde dicts. Ver dossier §5-F0.4.

---

## B-142 — Canal de penalidad DARVO del pipeline muerto en runtime + ELI falso positivo + comentario in-code falso [RESUELTO — F0]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — F0 (2026-07-17, tanda firmada): canal de penalidad del pipeline RETIRADO (no estrechado) + matching word-boundary que corrige el FP ELI + comentario in-code falso corregido. Tripwire de esquema en `tests/test_f0_l029_darvo_hardening.py` (si `SignalOutput` gana `description`/`evidence_type`, el test truena y fuerza re-evaluar la decisión). Censo post-F0: exactamente 4 anotados (KIWI-001/003/004/005) |
| **Severidad** | P2 — integridad del registro B-140 + superficie latente en el decision path del pipeline |
| **Archivos** | `vigia/core/darvo_detector.py`, `vigia/pipeline/pipeline.py:629-630`, `data/cases/VIGIA-REAL-MAGNET-2021-IOS-ELI.json` |
| **Detectado en** | Investigación abductiva L-029 (censo de 201 casos + 6 refutadores), verificado por ejecución |

### Tres hechos verificados

1. **El canal `adjust_consistency_score` del pipeline es código muerto en
   runtime**: los `SignalOutput` reales no tienen `description` ni
   `evidence_type` como atributos → el detector devuelve penalidad 0
   incondicionalmente. El "efecto vivo en 45/200 casos" que sugería el censo
   proxy sobre artifacts JSON no ocurre en el camino real. Riesgo: el canal se
   DESPERTARÍA con cualquier refactor del contrato de señales, sin gate de
   asimetría (fórmula surveillance-only). Propuesta: retirarlo, no estrecharlo.
2. **ELI es falso positivo del detector B-140**: `'server'` matchea dentro de
   "4 S3 server list URLs" y `'no contact'` dentro de "no contacts database".
   Caso mono-actor de evasión de comunicaciones — sin estructura DARVO. El
   censo real de anotaciones verdaderas es 4 (1 expediente + 2 copias), no 5.
3. **El comentario "exactamente los 5 casos correctos" en `darvo_detector.py`
   es falso** y debe corregirse junto con el registro B-140 (nunca en silencio).

---

## B-143 — F1 (L-029): endurecimiento de la anotación DARVO sellada — caveat L-004 + devil_advocate obligatorio + matched_spans [RESUELTO — F1]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-17, tanda F1 (dossier §5-F1 + refutaciones FF-1/F2 de los jueces) |
| **Severidad** | P2 (la anotación sellada porta fuerza prejudicial ante un jurado aunque `verdict_effect: none`) |
| **Archivos** | `vigia/core/darvo_detector.py` (matched_spans), `vigia_scorer.py` (Step 4c), `vigia_agent.py` (narrativa) |

### Qué cambia

1. **Caveat L-004 legible por máquina DENTRO del bloque sellado**
   (`trigger_class`): un disclaimer fuera del registro sellado es el patrón
   que las cortes descuentan; adentro, viaja con el claim.
2. **`devil_advocate` OBLIGATORIO** en el bloque (Protocolo de Refutación
   aplicado a la única salida sellada apuntada a un rol humano): la
   hipótesis benigna se genera y sella siempre, determinista.
3. **`matched_spans`** por keyword (familia + keyword + ventana de
   contexto) — decisión FIRMA: spans SÍ (la lista de keywords ya es
   pública en el repo; la transparencia gana).
4. **Sin atribución nominal**: `attributed_actor`/`role_attribution` NO
   entran al bloque sellado (refutación F1 del juez Daubert: atribución
   HMAC-sellada desde texto libre = vector de difamación realizado).
5. La narrativa sellada surfacea caveat + devil_advocate junto al bloque.

### Verificación

`tests/test_f1_darvo_annotation_hardening.py` (8 tests, rojos primero);
pin de igualdad veredicto/score intacto (B-140); gate 0-flips compartido
con F2 (ver B-144).

---

## B-144 — F2 (L-029): pareo cross-bundle como arquitectura — tool MCP + registros de linkage firmados, CERO autoridad de veredicto [RESUELTO — F2]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — 2026-07-17, tanda F2 (dossier §5-F2 + trampa de metadata del veredicto de Kimi §6) |
| **Severidad** | P2 (arquitectura: la inversión de roles DARVO solo es expresable ENTRE bundles — L-029 causa raíz 1) |
| **Archivos** | `vigia/tools/paired_review.py` (nuevo), `vigia/core/case_linkage.py` (nuevo), `vigia/vigia_sift_bridge.py` (registro opcional `VIGIA_PAIRED_REVIEW_ENABLED`), `run_all_agent.py` (pase de linkage) |

### Qué entrega

1. **`compare_paired_bundles(path_a, path_b)`** (tool MCP, Modo 2):
   sub-métricas deterministas — igualdad de `case_origin` leída de
   `artifacts[].metadata` (trampa de Kimi: top-level es None en todos los
   KIWI), delta de `prior_trust` en Fraction (0.3 vs 0.8 ES la señal
   L-029), `detect_darvo_pattern` sobre la unión (dispara en la unión
   aunque KIWI-002 solo sea ciego — el valor del pareo), framing
   complementario, solapamiento de provenance. La Terceridad la hace el
   analista/LLM que llama, FUERA del loop de decisión (invariante 3).
   Caveats adversariales obligatorios en el propio output;
   `verdict_authority: "none"`.
2. **Registros de linkage** (`emit_linkage_records`, pase en el batch
   junto a `check_label_consistency`): un registro firmado por grupo de
   `case_origin` con (a) dedup de copias por SHA256 del array de
   artifacts — sin él, UN expediente emitiría múltiples linkages contra
   evidencia duplicada (L-016, juez 12); (b) caveat de colisión SIEMPRE
   que hay evidencia duplicada — el registro reporta el hecho sin juzgar
   intención: KIWI-004/005 se declaran copias, RT-FN-COLLUSION-001 no (y
   eso ES el patrón de colusión), pero "declararse copia" también es
   narrativa; (c) label-blind por construcción; (d) sin timestamps en el
   registro (replay determinista) + HMAC-SHA256 sobre el registro
   canónico cuando hay `VIGIA_HMAC_KEY`.
3. **Fixture permanente**: RT-FN-COLLUSION-001 (case_origin MPF7779408 +
   artifact_ids de KIWI-006 reusados, byte-idéntico a nivel artifacts) —
   el ataque de join-key forjado preexistente en el repo; el test fija
   que su inclusión produce caveat de colisión, nunca certificación de
   limpieza.

### Diferido (sin cambio)

Scoring pareado completo / tipo de bundle nuevo: bloqueado por N=1
auto-referencial (un solo par POV genuino, ambas mitades de la misma
examinadora). Ver dossier §5-F2.3.

### Verificación

`tests/test_f2_paired_review.py` (11 tests, rojos primero: pareo real
KIWI-002↔003, label-blind en ambas APIs, dedup, fixture RT, HMAC,
determinismo orden-independiente); registro del bridge con py_compile (el
smoke test MCP requiere entorno con `mcp` — L-045; pendiente para la
próxima sesión con bridge vivo); gate 0-flips compartido con F1.

---

## B-145 — VIGIA-REAL-007 (Nitroba) `expected_verdict`: hallazgo de INTEGRIDAD DE ETIQUETA, no un defecto de scoring — MALICE estaba mal desde el primer commit del caso, corregido 2026-07-12 en las 3 copias activas; 4 portadores no activos todavía leen MALICE (censo extendido 2026-07-19, punto 4) [PARCIALMENTE RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | PARCIALMENTE RESUELTO — las 3 copias fuente de caso **activas** (`data/cases/{,converted/,legacy/}`) fueron corregidas el 2026-07-12 (`cf8a37c5`, `3f3a271f`). El censo extendido 2026-07-19 (punto 4) encontró **4 portadores no activos** todavía en `MALICE`; `data/vigia_forensic_cases.json` (la única fuente viva sin fecha) fue entonces re-etiquetada a `SUSPICION` (2026-07-19). **3 portadores no-consumidores permanecen en `MALICE` por decisión:** `cases/input/VIGIA-REAL-007.json` (`OUTSIDE_ALLOWLIST`) y 2 snapshots de calibración fechados (insumos de calibración offline congelados — editarlos rompería la reproducibilidad de B-076). Ninguno alimenta la métrica publicada (todos fuera de `CASES_DIRS`). |
| **Severidad** | P2 — integridad de la **etiqueta** de ground truth. Clasificado por separado de un defecto del motor de scoring: ningún sitio de `vigia_scorer.py` produjo jamás un veredicto incorrecto contra esta evidencia. |
| **Archivo** | `data/cases/VIGIA-REAL-007.json`, `data/cases/converted/VIGIA-REAL-007.json`, `data/cases/legacy/VIGIA-REAL-007.json`, `cases/input/VIGIA-REAL-007.json` (4 copias trackeadas del caso, según el patrón de copias-sombra R3-3/R3-3b/R3-3c) |
| **Detectado en** | Arqueología de historia git solicitada por @annatchijova, 2026-07-18 — traza completa `git log -p --follow` de `expected_verdict` a través de las 4 copias, todas las ramas, tras des-shallowear el clon (`git fetch --unshallow`; el clon shallow de la sesión de trabajo solo exponía un commit squasheado). |

**Afirmación bajo investigación:** se reportó que el caso tenía `expected_verdict:
SUSPICION` "desde siempre" en una copia hosteada de forma independiente (aprobada
por Rob T. Lee), divergiendo a `MALICE` en este repo "en algún momento" vía una
edición fuera de la autorización de escritura normal, luego restaurada a
`SUSPICION`.

**Lo que la historia git realmente muestra (con alcance Daubert — afirmado solo
donde hay evidencia directa):**

1. **No existe ningún commit de corrupción en la historia trackeada de este
   repo.** `MALICE` está presente en el *primer* commit que introduce cada copia:
   - `f4e8946d` (2026-04-28 23:48:59 -0300, "data: agregar 71 casos SYN + 15
     casos BEN al corpus") crea `data/cases/VIGIA-REAL-007.json` desde cero
     (61 inserciones, 0 borrados) con `"expected_verdict": "MALICE"` ya
     presente. (Nota: el mensaje del commit describe casos SYN/BEN; también
     agregó silenciosamente este caso REAL — un desajuste menor entre mensaje
     de commit y contenido, no evidencia de manipulación en sí mismo.)
   - `4016b39b` (2026-05-18) crea `data/cases/converted/VIGIA-REAL-007.json`
     vía `scripts/convert_legacy_cases.py`, ya en `MALICE`.
   - `05956f77` (2026-05-19) crea `data/cases/legacy/VIGIA-REAL-007.json`
     (`_consolidation.consolidated_at: 2026-04-28T05:51:15Z`, coincidiendo con
     la fuente `f4e8946d`), ya en `MALICE`.
   - `bde03ae2` (2026-05-02) es el commit que introduce la ur-fuente,
     `data/vigia_forensic_cases.json` ("Digital Corpora Nitroba Harassment"),
     y también lee ya `"expected_verdict": "MALICE"`.
   - No hay ningún commit en `git log --all` que cambie este campo
     DE `SUSPICION` A `MALICE`. Si la copia hosteada de forma independiente
     era genuinamente `SUSPICION` desde su creación, la divergencia es
     anterior a la historia git de este repo — no ocurrió como un evento de
     edición dentro del repo, y no puede reconstruirse forensemente más allá
     desde esta base de código sola.
   - **Corrección a la afirmación original:** "restaurado hace días" solo es
     exacto para `data/cases/{,converted/,legacy/}VIGIA-REAL-007.json`. No
     describe un acto de *restaurar* un valor SUSPICION previo — el registro
     git muestra una *corrección por primera vez* de una etiqueta que era
     `MALICE` desde el momento en que cada copia entró a este repositorio.

2. **La corrección (2026-07-12) fue un re-etiquetado deliberado, documentado y
   de autor único — no una escritura sin supervisión.**
   - `cf8a37c5447f60a64bd69f597aff28101965115f` (Anna Tchijova, 2026-07-12
     20:14:03 -0300): `data/cases/VIGIA-REAL-007.json`
     ```
     -  "expected_verdict": "MALICE",
     +  "expected_verdict": "SUSPICION",
     ```
     Mensaje del commit: *"anonymous harassment via willselfdestruct.com shows
     clear intentionality but NO concealment layer (no log deletion, no
     timestamp manipulation, no process masquerading). Under VIGIA's verdict
     scale, SUSPICION is correct — MALICE requires active anti-forensics.
     The motor already sealed SUSPICION correctly."* Alcance: 3 archivos
     (`README.md`, `README_ES.md`, este único archivo de caso). También
     actualiza las métricas de corpus publicadas 167/199 → 174/199.
   - `3f3a271f12d64bbd26c4687a9390e92e167920da` (Anna Tchijova, 2026-07-12
     23:05:51 -0300): el mismo diff `MALICE → SUSPICION` aplicado a
     `data/cases/converted/VIGIA-REAL-007.json` y
     `data/cases/legacy/VIGIA-REAL-007.json`, dentro de un commit mucho más
     grande que regeneró los 199 bundles de agente post-M1/M2/M3/Rule-16.
     Mensaje del commit: *"Also syncs Nitroba MALICE->SUSPICION relabel in
     converted/ and legacy/ copies (missed in the original relabel commit)."*
     Cada otra línea `expected_verdict` tocada por este commit es una adición
     pura (solo `+`, archivos de bundle regenerados nuevos bajo
     `results/agent_batch/`) — confirmado diffeando el commit completo:
     ninguna otra etiqueta *fuente* de caso fue cambiada en silencio. Esto
     descarta el patrón de "divergencia silenciosa sistémica" B-095/case_008
     para este evento — el re-etiquetado estuvo acotado a Nitroba únicamente,
     ambas veces.

3. **Brecha residual — `cases/input/VIGIA-REAL-007.json` todavía lee `MALICE`.**
   Creado en `625f293e` (2026-07-02, "move case JSONs from evidence/ to
   cases/input/"), nunca tocado por ninguno de los dos commits de
   re-etiquetado. Confirmado por lectura directa al momento de esta auditoría
   (2026-07-18): línea 95, `"expected_verdict": "MALICE"`. Según
   `docs/AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md:149,486`, `cases/input/`
   está marcado `OUTSIDE_ALLOWLIST` por PathGuard — no es consumido por el
   pipeline activo de scoring/corpus, así que este residual **no** afecta
   ninguna métrica publicada. Es una inconsistencia viva, no corregida
   actualmente (esta auditoría es de solo lectura por instrucciones; no se
   modificó ningún archivo de caso).

4. **Censo extendido (2026-07-19) — el residual es más amplio que una copia.**
   Un escaneo de árbol completo de cada portador del string `VIGIA-REAL-007`,
   extrayendo la etiqueta específica del caso (no un grep a nivel de archivo),
   muestra que la corrección `MALICE → SUSPICION` alcanzó solamente las tres
   copias fuente de caso *activas*. Cuatro portadores **no activos** todavía
   leen `MALICE` para este caso al 2026-07-19:
   - `cases/input/VIGIA-REAL-007.json` — `MALICE` (ya documentado en el punto 3;
     `OUTSIDE_ALLOWLIST`).
   - `data/vigia_forensic_cases.json` — `case_id=VIGIA-REAL-007 → MALICE`. Es la
     ur-fuente del punto 1. **No** se carga como caso individual: está listada
     en `SKIP_STEMS` (`run_all_agent.py:36-37`; igualmente referenciada en
     contexto de skip por `scripts/redteam_round3_emergent.py:144` y
     `scripts/dryrun_signal_quality_gate.py:45`). Misma forma que las copias
     corregidas (`expected_verdict` a secas, sin campo motor), así que es una
     etiqueta genuinamente des-sincronizada — solo que no una que la métrica
     batch consuma. El punto 3 no la listó como residual vivo; esta entrada
     corrige esa omisión.
   - `data/calibration_ladder_dataset_20260705.json` — `cases[54]:
     {expected: MALICE, motor_verdict: SUSPICION}`.
   - `data/signal_calibration_dataset_20260709.json` — `records[422..424]:
     {ground_truth: MALICE, case_motor_verdict: SUSPICION}` (3 registros).

   **Refutación — ¿algo de esto invierte la métrica de corpus publicada? No.**
   El conjunto de casos activo que lee el runner determinista es `CASES_DIRS`
   (`run_all_agent.py:22-28`: `data/cases`, `converted`, `benign`,
   `consolidated_canonical`, `legacy`). Ninguno de los cuatro portadores
   residuales está en él. La guarda de copias-sombra R3-3
   (`check_label_consistency`) escanea solo `CASES_DIRS`, así que pasa — las
   tres copias activas coinciden en `SUSPICION` — y por diseño no ve estos
   cuatro. La precisión de corpus publicada queda por lo tanto intacta; esto
   sigue siendo INTEGRIDAD DE ETIQUETA, no un defecto de scoring.

   **Caveat honesto — los dos datasets de calibración son snapshots offline
   congelados, no bugs.** Cada registro 007 porta la etiqueta de ground truth
   vieja (`MALICE`) Y el veredicto actual del motor (`SUSPICION`) lado a lado,
   en un archivo cuyo nombre lleva fecha estampada. El análisis de consumidores
   (2026-07-19) confirma que la estructura es deliberada:
   `calibration_ladder_dataset_20260705.json` es referenciado solo por su
   generador (`scripts/generate_ladder_dataset.py:110`) y por un **comentario**
   en `vigia_scorer.py:1181` documentando que el umbral SUSPICION 0.18→0.10
   (B-076) se calibró offline contra él — el scorer **no** lo carga en runtime;
   la constante calibrada está horneada en el código. `signal_calibration_dataset_
   20260709.json` es referenciado solo por su generador, un experimento de
   refit offline (`scripts/experiment_a4_profile_refit.py:51`), y un test.
   Ninguno es ground truth de runtime. Editarlos alteraría retroactivamente el
   insumo de una calibración documentada (B-076 es anterior al re-etiquetado
   del 2026-07-12), rompiendo su reproducibilidad. **No** fueron editados, por
   decisión.

   **Resolución (2026-07-19):** `data/vigia_forensic_cases.json` — el único
   residual que es una fuente viva sin fecha y sin campo motor, misma clase que
   las tres copias ya corregidas — fue re-etiquetado `MALICE → SUSPICION` para
   `case_id VIGIA-REAL-007` (parche quirúrgico de una sola línea, anclado en la
   línea de descripción única; JSON re-validado; diff = 1 línea;
   `confidence_expected: 91` dejado intacto, coincidiendo con el alcance mínimo
   de `cf8a37c5`; suite completa en verde, 1624 passed).
   `cases/input/VIGIA-REAL-007.json` permanece en `MALICE` por su estatus previo
   `OUTSIDE_ALLOWLIST` (sin cambios). Los dos datasets de calibración permanecen
   en `MALICE` por la decisión de arriba. Estado neto de fuentes vivas: 007
   ahora lee `SUSPICION` en toda fuente que el pipeline pudiera cargar; los
   portadores `MALICE` restantes son todos no-consumidores documentados.

**Clasificación: INTEGRIDAD DE ETIQUETA, no un bug del motor de scoring.** En
ningún punto de esta historia se demostró que el veredicto propio del motor
determinista para esta evidencia estuviera equivocado — el hallazgo es que el
*comparador de ground truth* (`expected_verdict`) contra el que se lo medía
portaba un valor incorrecto desde el momento en que el caso entró al control de
versiones. Enmarcado en el propio lenguaje de `cf8a37c5`: "the motor already
sealed SUSPICION correctly." Ningún code path, gate o cómputo en Fraction de
`vigia_scorer.py` está implicado.

**REFUTATION GATE LOG — B-145**
```
Candidate verdict : label was corrupted by an unauthorized/unsupervised
                     write at some point after initial (correct) creation
Gate applied       : full-history git archaeology (git log -p --follow,
                     --all, post-unshallow) across all 4 tracked copies
Gate rule          : a corruption event requires a commit transitioning
                     SUSPICION -> MALICE; none exists in `git log --all`
Gate result        : Candidate REJECTED. Evidence instead shows MALICE
                     present at first commit of every copy (f4e8946d,
                     4016b39b, 05956f77, bde03ae2); no prior SUSPICION
                     value is recorded in this repository's history.
Forensic note      : the independently-hosted copy's claimed SUSPICION
                     origin cannot be confirmed or refuted from this
                     repo's git history alone — it is outside this
                     evidence set. Documented as an open gap, not
                     asserted either way.
```

**Verificación:** `git log --all --follow -p -- <cada una de las 4 rutas>`,
hunks de diff y metadata completa de commits reproducidos arriba; `git show
cf8a37c5 --stat` y `git show 3f3a271f --stat` confirman el alcance de archivos;
`grep -n expected_verdict` re-ejecutado contra las 4 copias vivas confirma el
estado actual en disco (`SUSPICION` ×3, `MALICE` ×1 en `cases/input/`). No se
modificó ningún archivo de caso como parte de esta entrada.

---

## B-146 — Verificación cross-versión de bundles sellados: VERIFICADA PRESENTE, no una brecha (propuesta Punto 4 de Qwen, refutada por auditoría de código 2026-07-19)

| Campo | Valor |
|-------|-------|
| **Estado** | NO ES UN BUG — la feature ya está implementada y testeada. Registrado para que no se re-investigue. |
| **Severidad** | N/A (resultado de auditoría, sin defecto) |
| **Archivo** | `vigia/core/canonicalize.py`, `vigia/core/bundle_builder.py`, `vigia/core/ebs_v1.py`, `tests/test_canonicalize_lockstep.py` |
| **Propuesto por** | Modelo externo (Qwen), 2026-07-19, como "Point 4 — cross-version verification of sealed bundles". Verificado contra código vivo según §4.1 antes de aceptación. |

**Afirmación bajo investigación (Qwen):** si el formato de
serialización/hash del bundle sellado evoluciona, ¿puede un VIGÍA *más nuevo*
verificar un bundle sellado por una versión *más vieja* sin un fallo falso?
Remedio propuesto: anclar un campo explícito `vigia_schema_version` dentro del
payload hasheado para que un verificador futuro aplique las reglas históricas.

**Lo que el código vivo muestra — el mecanismo ya existe:**

1. `canonicalize.py:58` — `CANONICALIZE_VERSION = "2"` es la versión de las
   reglas de serialización. `_canonicalize_v1` (líneas 73-111) se preserva
   *explícitamente* "solo para verificar bundles historicos" (docstring
   líneas 22-37).
2. El contrato de verificación es exactamente la propuesta de Qwen: los
   verificadores **prueban v2 y caen a v1** (`canonicalize.py:26-28`: "la
   verificación prueba v2 y CAE A v1: todo bundle sellado bajo v1 sigue
   verificando idéntico (results/)"). Un bundle sellado bajo las reglas
   viejas verifica bit-idéntico bajo el código nuevo.
3. Los campos de versión están dentro del payload sellado:
   `bundle_builder.py:227,231,241` (`vigia_version`, `canonical_version:
   "1.0.0"`, `bundle_version`); `ebs_v1.py:74` (`EBS_VERSION = "1.0"`),
   `ebs_v1.py:744` (`bundle_version` serializado en el dict del bundle).
4. `tests/test_canonicalize_lockstep.py` (12 passed, 2026-07-19) verifica el
   encoder canónico en lockstep "para v2 y para el fallback v1".
5. Evidencia corroborante del fix de CI del mismo día (commit `b2d4ad80`): la
   copia de verificador borrada `tests/verify_ebs_v1_parcheado.py` "had already
   lost the R3-2 dual-canon fallback, so it would REJECT historical v1 bundles
   if ever run" (`test_canonicalize_lockstep.py:48-50`). El fallback dual-canon
   *es* el mecanismo de verificación cross-versión — su pérdida se trata como
   defecto, confirmando que el invariante es de primera clase.

**REFUTATION GATE LOG — B-146**
```
Candidate finding : sealed bundles lack a version anchor, so a future VIGÍA
                    could falsely reject (or wrongly validate) an old bundle
Gate applied      : live-code audit of the canonicalize / bundle_builder /
                    ebs_v1 sealing core + lockstep test
Gate rule         : the proposal is a real gap only if no in-payload version
                    exists AND the verifier does not dispatch on it
Gate result       : REJECTED. CANONICALIZE_VERSION + bundle_version/EBS_VERSION
                    are present in the hashed payload; the verifier tries v2
                    and falls back to v1; the lockstep test covers both. The
                    feature Qwen proposed already exists.
Residual (optional): an explicit end-to-end "seal-under-v1, verify-under-current"
                    regression test would be belt-and-suspenders. The lockstep
                    test plus the historical `results/` v1 bundles (which still
                    verify) already exercise the path; no defect blocks this.
```

**Verificación:** `grep -n CANONICALIZE_VERSION vigia/core/canonicalize.py`;
lectura completa de `canonicalize.py` (encoders v1 + v2 + docstring
dual-canon); `grep -n "version" vigia/core/bundle_builder.py
vigia/core/ebs_v1.py`; `pytest tests/test_canonicalize_lockstep.py` → 12
passed. No se cambió código.

---

## B-147 — Agotamiento adversarial de recursos / ReDoS en parseo de artefactos (propuesta Punto 3 de Qwen): dos vectores nombrados REFUTADOS; una brecha latente de guarda de ingesta encontrada

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (2026-07-19) — los dos vectores que Qwen nombró están refutados (ver abajo). La única brecha latente (`disk_forensics.py:131`) fue endurecida con una guarda de degradación honesta + tests rojos primero. |
| **Severidad** | P3 — endurecimiento de disponibilidad. No se encontró ningún camino explotable vivo. |
| **Archivo** | `vigia/tools/caie.py` (`_extract_assertions`), parser JSON (empírico), `vigia/sift/{pcap_parser,memory_forensics,disk_forensics}.py`, `vigia/vigia_command_center.py` |
| **Propuesto por** | Modelo externo (Qwen), 2026-07-19, como "Point 3 — parsing pathologies / ReDoS / Billion Laughs". Verificado contra código vivo + empíricamente según §1.3 antes de aceptación. |

**Afirmación bajo investigación (Qwen):** un artefacto maliciosamente
construido (JSON anidado profundamente, o texto que dispare backtracking
catastrófico de regex en `_extract_assertions`) cuelga u OOMea el pipeline en
lugar de ser rechazado limpiamente; degradar honestamente a
`UNANALYZED | RESOURCE_EXHAUSTION`.

**Resultado vector por vector:**

1. **Backtracking catastrófico en las regexes de `_extract_assertions` —
   REFUTADO.** `caie.py:1020-1089`: la función **no usa regex en absoluto**.
   Lee metadata ya parseada vía `dict.get()`, chequeos de tipo con
   `isinstance`, y membresía de substring plana (`"lsass" in target`). No hay
   superficie de regex que atacar en esta función.
2. **Cuelgue / OOM por JSON anidado profundo — REFUTADO empíricamente.**
   `python3 -c` con un array anidado a profundidad 100000 y un objeto anidado
   a profundidad 100000 levantan ambos un **`RecursionError` acotado y
   atrapable** (salida de proceso 0; sin timeout a 20s, sin OOM, sin
   segfault). El parser JSON de CPython no se cuelga por profundidad de
   anidamiento; "Billion Laughs" es un ataque de expansión de entidades XML y
   no aplica a `json.loads`.
3. **DoS por volumen (inundación de artefactos) — YA CUBIERTO.** En `caie.py`,
   `CrossArtifactIncongruenceEngine.add_artifact` aplica `_MAX_ARTIFACTS`
   (Kimi P0) y rechaza el exceso (evento de auditoría
   `CAIE_ARTIFACT_LIMIT`).

**Auditoría de parseo de ingesta (el residual real, angosto).** Se auditaron
cuatro sitios `json.loads` externos/semi-confiables para degradación honesta:

| Sitio | Guarda presente | Disposición |
|------|---------------|-------------|
| `pcap_parser.py:86` | `except json.JSONDecodeError` → `RuntimeError` con contexto | Con guarda |
| `memory_forensics.py:362` | `except (json.JSONDecodeError, subprocess.TimeoutExpired)` → log + `[]` | Con guarda |
| `vigia_command_center.py:154` | `except json.JSONDecodeError: continue` + `except Exception: pass` externo | Con guarda |
| `disk_forensics.py:131` | **ninguna** — `json.loads(parsed_json or "{}")` sin envolver | **Brecha (latente)** |

**El hallazgo de `disk_forensics.py:131`, acotado con honestidad:**
- `MFTTimelineAnalyzer.analyze(self, mft_bytes, parsed_json: Optional[str] = None, ...)`
  parsea `parsed_json` (un parámetro externo) sin try/except. Un valor
  malformado levanta `json.JSONDecodeError` (o `RecursionError` con
  anidamiento profundo) sin atrapar, crasheando el análisis MFT en lugar de
  degradar.
- **No explotable en vivo hoy:** ningún caller dentro del repo pasa
  `parsed_json` (`grep parsed_json` encuentra solo la firma); su default es
  `None` → `json.loads("{}")` → siempre válido. El crash requiere un caller
  externo que inyecte JSON malformado.
- **Por qué igualmente vale la pena endurecerlo:** 10 líneas más arriba (mismo
  método), el input externo hermano `timestamp_utc` *sí* está guardado, con
  la fundamentación explícita "FIX P2 (Kimi post-patch): capturar ValueError
  si timestamp_utc es inválido — no crashear". El `json.loads(parsed_json)`
  sin envolver rompe ese mismo contrato defensivo en el otro input externo
  del mismo método.

**REFUTATION GATE LOG — B-147**
```
Candidate finding : crafted artifacts (deep JSON / regex backtracking) hang or
                    OOM the pipeline; needs UNANALYZED/RESOURCE_EXHAUSTION guard
Gate applied      : code read of _extract_assertions; empirical json.loads depth
                    test; audit of 4 ingestion parse sites; caller trace of
                    parsed_json
Gate rule         : a vector is real only if it (a) has an exploitable surface
                    and (b) fails unbounded (hang/OOM/crash) rather than bounded
Gate result       : Vectors 1-3 REJECTED (no regex; bounded RecursionError;
                    _MAX_ARTIFACTS already caps volume). One latent gap survives
                    (disk_forensics.py:131), but is NOT live-reachable with
                    malicious input in the current wiring — recorded as a
                    hardening candidate, not a live vulnerability.
```

**Resolución (2026-07-19).** `disk_forensics.py:131` envuelto en
`try/except (json.JSONDecodeError, RecursionError, ValueError)` más un chequeo
de forma `isinstance(_parsed, dict)` → ante cualquier fallo, loguea un warning
de frontera y degrada a cero entradas MFT (degradación honesta, espejando la
guarda de `timestamp_utc` 10 líneas más arriba). Rojos primero:
`tests/test_disk_forensics_ingest_guard.py` — tres casos adversariales (JSON
malformado → JSONDecodeError; anidamiento a profundidad 100000 →
RecursionError; payload válido-pero-lista → AttributeError) crasheaban todos
pre-fix y ahora degradan a `total_entries == 0`; un cuarto test de regresión
confirma que un payload bien formado sigue parseando (1 entrada). Gate
comparativo: suite completa **1628 passed** (1624 previos + 4 nuevos), 0
flips — el JSON válido no se ve afectado por construcción (mismo camino
`.get("entries")` vía la rama `isinstance(dict)`).

**Verificación:** lectura de `caie.py:1020-1089`; test JSON de profundidad
100000 en `python3` (array y objeto → RecursionError acotado, exit 0);
`sed`/lectura de los 4 sitios de ingesta; `grep -rn parsed_json vigia/` (solo
la firma — ningún caller lo inyecta). No se cambió código como parte de esta
entrada de auditoría.

---

## B-148 — Conflación ausencia≡negativo en CAIE: "red nunca analizada" emitido como "analizada, sin actividad", alimentando una acusación falsa de fabricación (propuesto como "B-154"; id real asignado B-148) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (2026-07-19) — modelo NetworkObservation de cuatro estados en `_extract_assertions`; tests rojos primero; gate comparativo de corpus 0/201 flips. |
| **Severidad** | P2 — consistencia arquitectónica + integridad de evidencia. Una regla que ACUSA (fabricación de logs, severidad 0.75-0.95) estaba disparando sobre AUSENCIA de datos. |
| **Archivo** | `vigia/tools/caie.py` (`_extract_assertions`, rama de memoria ~1057-1089; consumido por la regla LOG_VS_MEMORY en `detect_fractures` ~1528) |
| **Detectado** | Auditoría de consistencia arquitectónica (2026-07-19): "¿VIGÍA aplica sus propios principios cuando audita?" — verificado contra `disposition.py` de Forge ("Findings and audit completeness are separate dimensions"; "inspired by VIGÍA's abstention gates") y `detect_negation` de `quality.py` de Cronos ("absence ... attenuating context, not positive confirmation"). Ambos están portados DESDE VIGÍA, y sin embargo este camino de CAIE regresionó respecto de la doctrina. |

**El bug.** Para un artefacto `memory_process`/`lsass_session`/`kernel_structure`,
el viejo modelo bivaluado emitía `memory_shows_no_network_activity` siempre que
`has_network` fuera falso — incluso cuando los campos de red estaban
**ausentes** (memoria nunca analizada a nivel red). Esa aserción es el único
input de la regla de fabricación LOG_VS_MEMORY (`caie.py:1528-1558`), así que
"no analicé la capa de red" se usaba para acusar a un log de fabricación. "No
encontré conexiones" y "no analicé la capa de red" son estados epistémicos
OPUESTOS; el modelo de datos perdía la distinción.

**El fix (modelo de cuatro estados, a nivel de aserción).** La PRESENCIA de la
clave (`in meta`), no la veracidad de `.get()`, decide si la capa de red fue
analizada:
- `ANALYZED_WITH_ACTIVITY` → `memory_shows_network_activity`
- `ANALYZED_NO_ACTIVITY` (campos presentes, válidos, vacíos) → `memory_shows_no_network_activity` (puede alimentar la regla)
- `NOT_ANALYZED` (sin campos de red en absoluto) → `memory_network_not_analyzed` (NO debe acusar)
- `ANALYSIS_FAILED` (campo presente, tipo incorrecto) → `memory_network_analysis_failed` (NO debe acusar)

**Rojos primero + gate.** `tests/test_caie_b154_network_absence.py` (5 tests):
los casos ausente y malformado disparaban `memory_shows_no_network_activity`
pre-fix (ROJO) y ahora no; los casos presente-vacío y poblado quedan sin
cambios (guardas de regresión). **Gate comparativo de corpus (mandato de Anna,
broken==0): 0 flips de veredicto en 201 casos** — baseline (caie.py revertido)
vs corregido producen veredictos sellados bit-idénticos; conjuntos de casos
idénticos, 0 asimetría. Es decir, ningún caso real dependía de la acusación
disparada por ausencia.

**La suite misma codificaba el bug (la corroboración más fuerte).** Cinco tests
adversariales existentes dependían de LOG_VS_MEMORY disparado por ausencia.
Cuatro eran mis-codificaciones genuinas — su fixture canónico de "la memoria
contradice el log" usaba memoria con red AUSENTE (`_S1_ARTIFACTS`:
`{"pid": 4521}`, "Process memory shows nothing"); corregidos a
presente-pero-vacío (`network_connections: []`), una contradicción genuina de
"analizada, sin actividad". El quinto es la sonda T-5 real → **B-149**.

**Verificación:** rojos primero, ROJO y luego VERDE; suite completa 1632
passed / 31 xfailed; diff del gate de corpus sin `scripts` = 0 flips
(corridas de script + crudas preservadas).

---

## B-150 — `_parse_iso_timestamp` interpretaba timestamps tz-naive en la zona horaria local del host (fuga de determinismo) [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO (2026-07-19) — los timestamps naive ahora se asumen UTC explícitamente, con log de divulgación; test rojo primero de invariancia de TZ. |
| **Severidad** | P3 — determinismo/portabilidad (§5.2). Latente: los timestamps del corpus llevan sufijo Z (aware), así que no hay impacto de veredicto en ningún host; la fuga solo dispara con un input tz-naive. |
| **Archivo** | `vigia/sift/_math_utils.py:200-224` (`_parse_iso_timestamp`) — consumido por el timeline de disco/MFT (`disk_forensics.py` `_analysis_epoch`) y `event_log_correlator.py`. |
| **Detectado** | Auditoría de invariantes temporales (2026-07-19, el "residual B-150" de la familia Punto-3/temporal de ChatGPT). Id real asignado B-150. |

**El bug.** `dt = datetime.fromisoformat(ts_str)` produce un datetime **naive**
para un string sin offset (p. ej. `"2026-07-19T10:00:00"`), y
`int(dt.timestamp())` sobre un datetime naive lo interpreta en la **zona
horaria local del proceso**. El mismo timestamp naive sella por lo tanto un
epoch distinto en un host UTC vs uno `America/New_York` — delta medido de
14400s (4h, EDT). Una fuga de determinismo en un valor que puede llegar a un
veredicto sellado vía `_analysis_epoch`.

**El fix.** Después de `fromisoformat`, si `dt.tzinfo is None`, asumir UTC
**explícitamente** (`dt.replace(tzinfo=timezone.utc)`) y emitir un WARNING de
frontera — espejando el patrón asumir-UTC-y-loguear de CAIE
`TCV_TIMESTAMP_NAIVE_ASSUMED_UTC` ya usado en el camino del veredicto. Los
inputs aware (Z u offset explícito) quedan sin cambios (basados en instante).
Sin interpretación silenciosa en la zona local del host.

**Rojos primero.** `tests/test_b150_naive_timestamp_utc.py`: bajo
`TZ=America/New_York` el parseo naive divergía del parseo UTC pre-fix (ROJO,
delta 14400s) y ahora es igual (VERDE); un test de regresión en host UTC y un
test de offset explícito fijan los caminos sin cambios. Suite completa 1635
passed, 0 failed. No hizo falta gate de corpus — el fix solo cambia inputs
naive, que el corpus no contiene, y en un host UTC naive==UTC antes y después
de todos modos.

---

## B-152 — Dos caminos de sellado de bundle distintos con superficies de integridad diferentes (hallazgo de arquitectura); capa de reasoning trace cableada junto al bundle de agente [DOCUMENTADO + Fase 1.5 aterrizada]

| Campo | Valor |
|-------|-------|
| **Estado** | Hallazgo de arquitectura DOCUMENTADO; reasoning trace Cronos-en-VIGÍA cableado en Modo-1 (Fase 1.5). |
| **Severidad** | P3 (documentación / consistencia arquitectónica). Sin defecto — una propiedad real de doble camino que los mantenedores futuros deben conocer. |
| **Archivo** | `vigia/core/bundle_builder.py` (camino EBS), `vigia_agent.py:_seal_bundle` (camino de agente), `vigia/core/reasoning_trace.py` (nuevo). |

**Hallazgo de arquitectura (Anna, 2026-07-19): VIGÍA tiene DOS caminos de
sellado con superficies de integridad diferentes.** Aflorado al diseñar dónde
adjuntar el reasoning trace. No son intercambiables:

- **Camino EBS** (`bundle_builder.seal`): `bundle_hash = _sha256_dict(bundle_payload)`
  sobre un conjunto de claves FIJO; el bundle serializado es
  `bundle_payload + integrity`, y el verificador re-deriva sobre
  `{k:v for k in bundle if k != "integrity"}` (`verify_ebs_v1.py:294`).
  Superficie de integridad = "todo excepto una lista de exclusión nombrada".
  Un campo nuevo queda dentro del hash salvo exclusión explícita.
- **Camino de agente** (`vigia_agent._seal_bundle`, el sello primario de
  Modo-1): `bundle_digest = sha256(json.dumps(entire bundle dict))`. SIN
  mecanismo de exclusión — el archivo `.json` en disco ES el contenido
  hasheado (`sha256sum -c`). `bundle_sha256` ni siquiera está embebido (sin
  auto-referencia). Cualquier campo agregado al dict cambia el digest.

Consecuencia: "adjuntar un hermano narrativo FUERA del hash del veredicto" es
una operación distinta según el camino — una clave excluida para EBS, un
**archivo separado** para el bundle de agente. Asumir el mecanismo EBS para el
camino de agente habría cambiado en silencio cada `bundle_digest` de agente.
Registrado para que esta propiedad de doble camino no se redescubra por las
malas.

**Cableado de Fase 1.5 (reasoning trace junto al bundle de agente).**
`vigia/core/reasoning_trace.py` (adaptado de Cronos, determinista, solo
Fraction, doctrina B-148 aplicada en la API) es escrito por `vigia_agent` como
archivo hermano `<stem>_reasoning_trace.json`, FUERA de `bundle_digest`, con
su propia integridad `ToolExecutionLogChain`.
`verify_reasoning_trace(bundle, trace)` liga a los dos: FALLA ante
manipulación de la cadena, mismatch de `case_id`, o — la guarda
proceso-no-resultado — `trace.verdict != bundle.agent_verdict` (testeado rojo
primero). El trace se deriva de datos que el bundle ya selló: la hipótesis
abductiva, evidencia NOT_ANALYZED para artefactos no analizados (B-148), y
auto-correcciones como entradas `contradiction_detector` encadenadas — que es
el mecanismo de Modo-1 que B-151(b) decía faltante (ahora disponible; si cada
gate del scorer emite una sigue siendo la decisión pendiente bajo B-151b).

**Gate (las tres pruebas de Anna).** (a/b) `tests/test_reasoning_trace_bundle_gate.py`
prueba contra 15 bundles reales de `results/agent_batch/*` que construir el
trace deja `bundle_digest` byte-idéntico (el dict nunca se muta; el trace es
un archivo separado) y que el trace verifica contra cada uno. (c)
`test_reasoning_trace.py::test_verify_trace_FAILS_on_verdict_divergence` es el
rojo primero: un trace que registra un veredicto distinto del bundle sellado
hace que el verificador FALLE explícitamente. End-to-end: `vigia_agent.py`
sobre un caso real escribe el hermano, el `sha256sum -c` propio del bundle
sigue verificando (digest intacto), y el trace verifica contra él. Suite
completa 1674 passed. Fail-soft: un error de escritura del trace nunca
descarta el bundle sellado (§5.3).

**Alcance (honesto).** El trace se deriva actualmente de datos resumidos del
bundle sellado (hipótesis + no analizados + auto-correcciones), así que para
casos sin nada de lo último queda delgado (calidad MINIMAL). La
instrumentación paso a paso más rica del loop de ejecución vivo, y la
exposición MCP del trace, son fases posteriores.

---

## B-153 — FastAPI `/analyze/path` no confina `case_path` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 condicional: sólo si el wrapper está expuesto a red no confiable. |
| **Archivos** | `vigia_api.py`, `vigia/vigia_api.py` |
| **Detectado por** | Auditoría Codex 2026-07-21, rama `codex`. |

Ambos endpoints hacen `REPO / payload.case_path` y pasan el resultado al
pipeline sin rechazar rutas absolutas, `..`, symlinks, directorios ni escapes.
Una ruta absoluta descarta `REPO` en `pathlib`. Con stubs inertes, ambos
wrappers aceptaron y reenviaron un archivo existente fuera del checkout. No se
afirma exfiltración arbitraria: el pipeline requiere JSON con forma de caso;
sí se confirma ruptura de scope/cadena de custodia. No hay autenticación y el
bind default era `0.0.0.0` (CORS no es autenticación).

**Corrección aplicada:** `vigia/api_case_paths.py` concentra la frontera para
ambos wrappers. Sólo acepta `.json` regular, no-symlink, bajo `cases/` o
`data/cases/`; rechaza ruta absoluta, `..`, directorio, extensión ajena y
escape sin revelar cuál fue el path local. Ambos modos ahora hacen bind a
`127.0.0.1` por default y validan/normalizan el caso antes de scorear. Las 15
regresiones API cubren los vectores y el caso permitido. Un operador que elija
exponer el servicio más allá de loopback todavía debe diseñar autenticación;
esa política no se inventó en este parche.

---

## B-154 — `/v1/chat/completions` crashea con escalares JSON válidos [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 — disponibilidad/protocolo; no cambia evidencia ni veredicto. |
| **Archivo** | `vigia_api.py` |
| **Detectado por** | Auditoría Codex 2026-07-21. |

`json.loads(text)` acepta `42` y `null`, pero el endpoint evalúa
`"artifacts" in case_data` y lanza `TypeError` no capturado en lugar de la guía
que devuelve para `[]`. `ChatRequest.messages` no normaliza contenido en la
frontera.

**Corrección aplicada:** sólo un objeto JSON con `artifacts` llega al pipeline;
escalar, `null`, lista, JSON inválido o contenido no textual devuelve guía de
uso. Las regresiones fijan `42`, `null`, `[]` y confirman que un objeto válido
sigue llegando al pipeline inerte de prueba.

---

## B-155 — `PathGuard` permite colisión de prefijo y escape `..` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 — integridad forense / frontera de adquisición SIFT. |
| **Archivos** | `vigia/core/path_guard.py`, consumidor `vigia/sift/sift_orchestrator.py` |
| **Detectado por** | Auditoría Codex 2026-07-21; fixture temporal propio, sin evidencia personal. |

La allowlist usa `str(abs_path).startswith(str(base))`, que no prueba
contención por componentes. Con base `/tmp/vigia`, un sibling
`/tmp/vigia-forge-...` pasa; rutas con `..` también pasan. `safe_open()` abre la
misma ruta con `os.open()`: la apertura externa fue reproducida. El
orchestrator entrega paths aceptados a los motores SIFT. Los tests no cubrían
prefijo ni `..`.

**Corrección aplicada:** `PathGuard` rechaza `..` antes de normalizar y compara
roots y candidato por componentes léxicos, sin seguir symlinks. `safe_open()`
usa la misma representación normalizada. Se conservan los chequeos existentes
de symlink, regularidad, `fstat` y TOCTOU. Regresiones cubren colisión de
prefijo, traversal, lectura positiva y rechazo de `safe_read`.

---

## B-156 — Validadores Volatility/RegRipper fallan abiertos fuera de allowlist [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 — defensa en profundidad y consumidores Python directos. |
| **Archivos** | `vigia/sift/memory_forensics.py`, `vigia/sift/registry_timeline_reconstructor.py` |
| **Detectado por** | Auditoría Codex 2026-07-21. |

Ambos validadores calculan `allowed`, pero si es falso sólo lanzan cuando el
path además no existe; cualquier archivo existente fuera de `/tmp/vigia`,
`/evidence`, etc. retorna. La reproducción controlada confirmó ambos retornos
fuera de root. SIFT suele anteponer PathGuard, pero B-155 lo atraviesa y los
consumidores directos llegan aquí sin esa capa.

**Corrección aplicada:** ambos validadores delegan en `PathGuard` con su
allowlist configurada. Un archivo existente fuera de root ahora produce
`PermissionError`; ausencia sigue siendo `FileNotFoundError` y otros rechazos
explícitos siguen visibles. Regresiones fijan ambos rechazos y la aceptación de
un archivo regular dentro de root.

---

## B-157 — Wrapper API empaquetado usa `vigia/` como root por default [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 — disponibilidad/operación local; no cambia el motor ni expone datos. |
| **Archivo** | `vigia/vigia_api.py` |
| **Detectado por** | Auditoría Codex 2026-07-21. |

Si `VIGIA_REPO` no está definido, el módulo usa `Path(__file__).parent`, es
decir `checkout/vigia/`, pero busca `data/cases`, `cases`, `scripts/vigia_ask.sh`
y `forensics/verify_ebs_v1.py` que viven en el root del checkout. El modo
`python -m vigia.vigia_api` queda incompleto salvo que el operador conozca y
configure la variable de entorno.

**Corrección aplicada:** el default es ahora el padre del paquete (root del
checkout), independiente del directorio de trabajo; `VIGIA_REPO` continúa
siendo un override explícito. La regresión importa el wrapper sin esa variable.

---

## B-158 — API devuelve detalles internos de excepción y ruta de checkout [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 condicional — divulgación de diagnóstico a clientes que alcancen la API. |
| **Archivos** | `vigia_api.py`, `vigia/vigia_api.py` |
| **Detectado por** | Auditoría Codex 2026-07-21. |

Ambos endpoints de análisis hacen `HTTPException(500, str(e))`: una excepción
del pipeline puede devolver rutas, nombres de binarios o detalles de una falla
interna al cliente. Además `/health` raíz retorna `str(REPO)`. Una reproducción
con excepción inerte de fixture confirma que el `detail` público conserva el
texto controlado. No cambia evidencia ni veredicto; requiere un cliente capaz
de llegar al endpoint.

**Corrección aplicada:** ambos wrappers registran el contexto server-side y
devuelven el único detalle estable `Error interno en el pipeline forense.`.
`/health` informa sólo estado. Regresiones con excepción controlada verifican
que ningún `detail` público conserva el texto interno.

---

## B-159 — El contrato público de Modo 2 afirma replay idéntico, pero sus informes tienen autoridad de conclusión independiente [DOCUMENTADO + texto corregido — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de integridad epistemológica/provenance; no es corrupción del scorer. |
| **Alcance** | `README.md`, `CLAUDE.md`, `KNOWN_LIMITATIONS.md`, comparación de Modo 1/Modo 2. |
| **Detectado por** | Auditoría Codex sobre replay batch y ejecuciones temporales, 2026-07-21. |

El README afirmaba que el veredicto determinista era idéntico en todos los
modos y que Claude sólo narraba sobre un bundle sellado. Esa afirmación no
coincidía con el contrato operativo ni con los artefactos: `CLAUDE.md` permite
que Modo 2 emita escalones que Modo 1 no tiene, y los informes Mode 2 archivados
incluyen conclusiones propias (por ejemplo `VIGIA-BREAK-015_claude*.json`:
`MALICE`) mientras el agente determinista actual y el bundle archivado sellan
`SUSPICION`. Modo 2 no modifica ese bundle; produce una investigación MCP con
alcance de evidencia, agregación y esquema de reporte distintos.

La comprobación no reescribió `results/agent_batch`: ejecuciones en `/tmp` del
agente actual volvieron a sellar `SUSPICION` para BREAK-012 y BREAK-015. Para
BREAK-012, además, el caso canónico ya fue relabelado de `BENIGN` a
`SUSPICION` porque tiene dos sujetos (jdoe exonerado; atacante desconocido
sospechado); informes históricos con `BENIGN` no prueban una divergencia actual.

**Caracterización de BREAK-015:** el caso declara
`SPATIAL_IDENTITY_COLLAPSE`, `BIOMETRIC_IMPOSTURE` e
`IDENTITY_BIFURCATION`, pero el scorer Modo 1 recalcula CAIE vivo y no tiene
un productor determinista para esas tres clases. La ejecución actual midió
`caie_fractures=0`, `fracture_malice_boost=0` y score `0.2382`, que pertenece
a la banda `SUSPICION` (< `0.33`). Convertir las fracturas declaradas en
autoridad directa para obtener `MALICE` reabriría la clase L-063 (JSON del
examinador con autoridad de veredicto). Un arreglo real requiere un detector
determinista y corpus negativo para esa clase de bifurcación de identidad; no
se retocaron umbrales ni se forzó un PASS.

**Corrección aplicada:** se reemplazaron las promesas de identidad de veredicto
por el contrato verificable: Modo 1 es la salida sellada corpus-wide; Modo 2 no
puede mutarla ni reemplazarla, pero su informe interactivo puede ser una
investigación independiente. Si divergen, se preservan ambos artefactos y sus
límites. El scorer y las etiquetas no se tocaron.

---

## B-160 — El extractor Android ignoraba una tabla `calls` válida dentro de `contacts2.db` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 — pérdida silenciosa de cobertura de evidencia mobile; no autoriza por sí sola un veredicto más severo. |
| **Archivo** | `vigia/sift/android_forensics.py` (`analyze`, `_analyze_contacts`, `_analyze_call_log`). |
| **Detectado por** | Auditoría Codex del falso negativo `OWL-NEXUS5`, 2026-07-21. |

El descubrimiento Android buscaba `contacts2.db` exclusivamente como libreta de
contactos (`raw_contacts` o `contacts`) y sólo buscaba historial de llamadas en
archivos llamados `calllog.db`. En la extracción real
`evidence/owl-2019-nexus5-quick/Agent Data/contacts2.db`, la base SQLite es
legible y contiene la tabla `calls` con **7** filas, pero no contiene ninguna
de las dos tablas de contactos. El resultado vivo quedaba
`contacts_parsed=False`, `calls_parsed=False`, `total_calls=0` y anotaba
"could not count contacts"; los siete registros no se analizan.

Esto no es el mismo defecto que B-072: B-072 impide correctamente que un
schema no parseable se convierta en una agenda o historial *vacío*. Aquí el
schema es reconocible y la evidencia existe, pero el dispatcher la asocia al
nombre del archivo en vez de inspeccionar la tabla disponible. Tampoco explica
por sí solo el NOISE de OWL: el mensaje de coordinación queda fuera por L-041,
el case JSON tiene 20 placeholders `unknown`/score cero, y el camino mobile
emite una sola señal agregada (B-052-P2). Es una pérdida independiente de
cobertura que debe repararse con tests de `contacts2.db` que contenga `calls`,
preservando la semántica fail-closed de B-072.

**Corrección aplicada:** después de tratar `contacts2.db` como contactos, el
dispatcher también lo pasa por el contador de llamadas ya existente. La ausencia
de tabla `calls` dentro de ese archivo es normal y no agrega una nota ni genera
un falso `EMPTY_CALL_LOG`; una tabla `calls` leíble, incluso vacía, conserva la
semántica B-072. No se introdujo heurística sobre el contenido de las llamadas.

**Validación:** dos tests rojos primero fijan (a) siete llamadas en
`contacts2.db` → `calls_parsed=True`, `total_calls=7`, sin `EMPTY_CONTACTS`;
y (b) tabla `calls` parseable vacía → `EMPTY_CALL_LOG`, sin
`EMPTY_CONTACTS`. `tests/test_b072_b074_mobile_verdict_fixes.py`: **35
passed**. Sobre la extracción OWL real, el resultado vivo ahora reporta 21 SMS
y 7 llamadas, con `contacts_parsed=False` correctamente. Una ejecución completa
en un bundle temporal siguió sellando **ABSTAIN** y 0 findings Android: el fix
recupera cobertura, pero no finge que el conteo de llamadas resuelva L-041,
los placeholders del case JSON ni B-052-P2.

---

## B-161 — El verificador del reasoning trace no anclaba la cola que declara [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de integridad forense/provenance. No altera un veredicto Modo 1 sellado, pero debilita un sibling que se presenta como evidencia de proceso. |
| **Archivo** | `vigia/core/reasoning_trace.py:verify_reasoning_trace`. |
| **Detectado por** | Auditoría Codex de `OWL-NEXUS5-CASE_bundle_chatgpt_reasoning_trace.json`, 2026-07-21. |

`ForensicReasoningTrace.seal()` escribe `chain_tip_sha256` (y, cuando hay una
clave configurada, `chain_tip_hmac`) junto a su `tool_execution_log` v2. Sin
embargo, `verify_reasoning_trace()` llama a `verify_tool_execution_log(log)` sin
pasarle ninguno de los anclajes declarados. Por lo tanto sólo verifica los
enlaces internos que recibe; nunca comprueba que la última entrada sea igual a
`trace["chain_tip_sha256"]`.

**Prueba roja (en memoria; ningún artefacto de evidencia fue editado):** el
trace OWL tenía tres entradas. Al eliminar la última, reemplazar
`chain_tip_sha256` por el hash de la nueva última entrada y llamar a
`verify_reasoning_trace(bundle, trace)`, el resultado siguió siendo
`valid=True, errors=[]`. El trace OWL real además informó `hmac_checked=False`
y `tip_checked=False` porque no se suministró una clave HMAC persistente.

Es una omisión de wiring distinta del residual documentado en R3-5. Incluso
cuando el verificador empiece a revisar la cola SHA-256 declarada, quien pueda
reescribir todo el sibling hash-only (incluida su punta) sigue siendo
indetectable sin HMAC persistente u otro autenticador externo. El defecto
inmediato es más acotado y testeable: una cola declarada que no cambia debe
detectar un log truncado o extendido, tal como ya hace `verify_bundle_tool_log()`.

**Corrección aplicada:** `verify_reasoning_trace()` ahora pasa
`trace["chain_tip_sha256"]` y, si está presente, `trace["chain_tip_hmac"]` a
`verify_tool_execution_log()`. La ausencia de una punta SHA-256 declarada es
ahora un error de verificación. El verificador público da a esa punta el mismo
tratamiento R3-5 que ya usa `verify_bundle_tool_log()`.

**Validación:** tests rojos primero rechazan ahora un trace truncado que
conserva su punta declarada original y rechazan un HMAC declarado falsificado
cuando el verificador recibe la clave configurada.
`tests/test_reasoning_trace.py`, `tests/test_reasoning_trace_bundle_gate.py` y
`tests/test_r3_5_chain_tip_truncation.py`: **60 passed**. El trace OWL existente
sigue verificando, ahora con `tip_checked=True`; permanece honestamente
hash-only (`hmac_checked=False`) hasta que se configure una clave HMAC
persistente.

---

## B-163 — El shim del agente proyectaba señales desde el JSON crudo y no desde el schema que puntúa [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de coherencia de evidence/provenance y explicabilidad. |
| **Archivo** | `sift_orchestrator.py:_analyze_ebs_json`. |
| **Detectado por** | Seguimiento Codex de B-162 sobre `OWL-NEXUS5-CASE`, 2026-07-21. |

El modo agente tiene dos consumidores del mismo JSON EBS legacy. La selección
abductiva llama a `_vigia_score()`, que normaliza la entrada; el render de
señales en `_analyze_ebs_json()` iteraba el JSON sin normalizar. En OWL, por
ello, el motor sellaba correctamente `ABSTAIN` por pérdida de normalización,
pero la narrativa presentaba 20 señales `artifact_id="?"`,
`evidence_type="unknown"`, score cero y fuente desconocida. La explicación no
describía los artefactos que el motor realmente evaluó.

No autoriza cambiar el score ni interpretar `content`: la reparación debe usar
la misma normalización determinista y ciega a la etiqueta para construir las
señales de presentación, manteniendo `expected_verdict` sólo como passthrough
histórico del modo `legacy`. Un caso con contenido estructurado aún debe
permanecer `ABSTAIN` hasta que exista un extractor raw específico de fuente.

**Corrección aplicada:** `_analyze_ebs_json()` normaliza el caso una vez al
entrar, antes de construir señales y antes de delegar la selección al motor.
La normalización es la misma, determinista y label-blind, que recibe el scorer;
no cambia `raw_score` a partir de contenido ni de `metadata.significance`.

**Validación:** `tests/test_b163_agent_normalization_projection.py` fue rojo
antes del patch (`?`/`unknown`) y ahora fija tanto la equivalencia de proyección
con el normalizador como la invariancia al label-flip. Junto con B-162,
Fase-1 y la regresión del veredicto SUSPICION:
`tests/test_b163_agent_normalization_projection.py`,
`tests/test_b162_structured_legacy_degradation.py`,
`tests/test_fase1_resolve.py`, `tests/test_b097_motor_suspicion_verdict.py` y
`tests/test_label_leak_normalize_case_schema.py`: **35 passed**. OWL ahora
conserva 20 IDs, cero placeholders, cero tipos `unknown` y los cinco tipos
canónicos; la hipótesis sigue siendo honestamente `ABSTAIN_DETECTED`.

---

## B-164 — `mount_sift_evidence` exigía dos raíces disjuntas y por eso era inalcanzable [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 operacional/forense: la tool MCP privilegiada no podía montar una imagen válida aun con evidencia disponible. |
| **Archivo** | `vigia/vigia_sift_bridge.py:mount_sift_evidence`. |
| **Detectado por** | Resolución MCP estricta de `OWL-NEXUS5-CASE`, seguida de auditoría Codex, 2026-07-21. |

La tool primero pasaba tanto `image_path` como `mount_point` por
`_sanitize_path_local()`, que confina al directorio `VIGIA_EVIDENCE_DIR`. Luego
exigía que el mismo `mount_point` resolviera dentro de `/mnt/analysis`. Salvo
que el directorio de evidencia coincidiera con `/mnt/analysis`, una solicitud
no podía satisfacer ambos contratos: era rechazada antes de la comprobación de
privilegios y antes de ejecutar el montaje. Esto explica por qué el análisis
raw de OWL necesitó un montaje manual de sólo lectura aunque la tool MCP existe.

**Corrección aplicada:** la imagen fuente sigue obligatoriamente bajo el
directorio de evidencia. El punto de montaje ya no acepta una ruta arbitraria:
acepta sólo un nombre de leaf `[A-Za-z0-9._-]` de 1–64 caracteres y crea ese
leaf privado (`0700`) bajo `VIGIA_EVIDENCE_DIR/mounted/`. Así el filesystem
montado continúa dentro del mismo ancla de confianza y puede ser leído luego
por `list_files`, `read_evidence` y `search_pattern`, sin conceder al caller
autoridad para elegir un destino privilegiado fuera de la evidencia. El leaf se
verifica explícitamente con `lstat` para rechazar symlinks y archivos.

**Límite deliberado:** el montaje sigue exigiendo que el proceso MCP tenga
privilegios de root; esa compuerta es real y ahora se alcanza antes de crear un
leaf por una solicitud no privilegiada. La reparación no monta imágenes durante
los tests ni altera la imagen raw ni el montaje forense existente.

**Validación:** `tests/test_b164_mcp_mount_root.py` fue rojo antes del patch
(no existían `_MOUNT_ROOT` ni el sanitizador de leaf) y ahora prueba la ruta
evidence-local, el acceso posterior por el sanitizador de evidencia, el rechazo
de vacío/traversal/absoluta/jerarquía/NUL y que una solicitud válida llega a la
compuerta de privilegios en lugar del gate imposible; también rechaza un leaf
existente que sea archivo o symlink: **11 passed**.

---

## B-165 — El extractor Android negaba evidencia Android mientras parseaba su perfil Chrome [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de cobertura/provenance: un resultado podía contener browsing Android parseado y a la vez declarar que no había artefactos Android. |
| **Archivo** | `vigia/sift/android_forensics.py:AndroidForensicsAnalyzer.analyze`. |
| **Detectado por** | Seguimiento Codex sobre la extracción raw accesible de `OWL-NEXUS5-CASE`, 2026-07-21. |

El conjunto original de marcadores Android sólo contenía DBs de plataforma
(`mmssms.db`, `contacts2.db`, `packages.xml`, etc.). La extracción accesible de
OWL preserva un perfil real de Android Chrome en
`com.android.chrome/app_chrome/Default/History`, pero no esos DBs globales.
El analizador parseaba sus 93 URLs y, antes de hacerlo, agregaba la nota
contradictoria “No Android-specific artifacts found”.

**Corrección aplicada:** un `History` SQLite sólo cuenta como cobertura Android
si ocupa exactamente el layout de paquete Android Chrome. Un `History`
Chromium genérico no basta. Si éste es el único marcador, el resultado deja la
nota explícita de perfil Android de aplicación sin marcadores de plataforma.
No añade finding, score, confianza ni veredicto: reconocer una fuente no
convierte su contenido ni su nombre de paquete en intención o malicia.

**Validación:** `tests/test_b165_android_package_profile_coverage.py` fue rojo
y ahora fija el layout válido, el rechazo del `History` Chromium de escritorio
y la invariante de cero findings / `z_score=0.0`. Junto con los contratos de
marcadores, SQLite read-only y semántica de vacío:
`tests/test_b165_android_package_profile_coverage.py`,
`tests/test_b139_bounded_marker_scan.py`, `tests/test_b071_sqlite_readonly.py`
y `tests/test_b072_b074_mobile_verdict_fixes.py`: **64 passed**. Sobre OWL raw:
93 entradas de browser, nota de cobertura correcta, cero findings y señal cero.

---

## B-166 — El batch reutilizaba bundles aunque cambiasen evidencia, runtime o configuración [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de provenance/medición: una métrica cacheada podía presentarse como resultado del motor actual. |
| **Archivos** | `run_all_agent.py`, `vigia_agent.py`, nuevo `vigia/core/runtime_fingerprint.py`. |
| **Detectado por** | Auditoría Codex del batch `OWL-NEXUS5`, 2026-07-21. |

`run_all_agent.py` aceptaba cualquier bundle existente que tuviera
`agent_verdict`. No comparaba su `evidence_sha256`, el SHA del código, ni la
configuración que decide la ruta. El batch de 201 casos lo hizo visible: marcó
200 casos `CACHED:motor` aun cuando el SHA de `vigia_agent.py` vigente
(`3e49…a279e`) ya difería del SHA registrado en sus bundles
(`3038…3120`). `motor` sólo describía el modo del adaptador EBS del bundle
histórico; no demostraba que el runtime vigente lo hubiera producido.

**Corrección aplicada:** cada bundle nuevo sella `runtime_fingerprint` además
del hash de evidencia. Es un manifiesto SHA-256 versionado de los entry points
deterministas y de los `.py` bajo `vigia/`, más la versión del intérprete y el
contexto `VIGIA_*`/`PYTHONHASHSEED` que puede cambiar una decisión. Los valores
con forma de secreto sólo aportan presencia/ausencia al hash: nunca se escriben
en el bundle. El runner reproduce el default de `VIGIA_EVIDENCE_DIR` del
agente y reutiliza un bundle sólo si coincide el veredicto sellado, el hash del
caso y la huella de runtime/contexto. Un bundle histórico sin huella se rerunea
una vez; el output declara el motivo, por ejemplo
`[RERUN:runtime_or_context_changed_or_legacy_bundle]`.

**Límite declarado:** la huella identifica el source tree de VIGÍA, Python y
la configuración de proceso pertinente; no sustituye un lockfile ni pretende
atestar binarios/dependencias externas. Si esa capa importa para un caso, se
debe rerunear y preservar el entorno de ejecución.

**Validación:** `tests/test_b166_batch_cache_provenance.py` prueba igualdad
exacta, mutación de evidencia, mutación de runtime, bundle legacy, symlink,
modo `VIGIA_EBS_RESOLVE` y el default de evidence root. Junto a los contratos
existentes del comparador sellado:
`tests/test_b166_batch_cache_provenance.py`,
`tests/test_b058_batch_reads_sealed_verdict.py` y
`tests/test_b10_comparator_reads_sealed_verdict.py`: **34 passed**.
Una corrida directa read-only de OWL, con output temporal interno, emitió
`ABSTAIN` (exit 4) y el fingerprint top-level coincidió con el registrado en
`AGENT_INITIALIZED`.

---

## B-167 — El límite de 500 cuerpos SMS podía ocultar una extracción Android parcial [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de degradación honesta / cobertura mobile. No convierte contenido en intención ni sube un veredicto. |
| **Archivos** | `vigia/sift/android_forensics.py`, shim raíz `sift_orchestrator.py`. |
| **Detectado por** | Auditoría Codex al investigar el falso negativo OWL-NEXUS5, 2026-07-21. |

`AndroidForensicsAnalyzer._analyze_sms()` limitaba deliberadamente la lectura
de cuerpos no nulos a 500 filas para acotar recursos, pero la consulta no
tenía `ORDER BY`, no contaba la población de cuerpos elegibles y no registraba
si el límite se alcanzaba. `total_sms` quedaba expuesto como si describiera
una cobertura completa. El shim sólo emitía `*_UNANALYZED` cuando el analizador
lanzaba una excepción; una extracción parcialmente inspeccionada podía por lo
tanto mezclarse con otros artefactos y contribuir a un resultado limpio sin
marcador de pérdida.

**Prueba roja:** una `mmssms.db` SQLite sintética con 501 cuerpos no nulos
devolvía `total_sms=501`, sin atributo de truncación y sin marcador
`unanalyzed` en el resultado del shim. El cuerpo 501 quedaba fuera de la
consulta de contenido y el bundle no tenía forma de distinguirlo de una base
completamente inspeccionada.

**Corrección aplicada:** el límite de 500 se conserva, ahora con orden
determinista `ORDER BY _id ASC`. El resultado declara `sms_analyzable_rows`,
`sms_analyzed_rows` y `sms_content_truncated`; el `SignalOutput` preserva esos
campos. Cuando hay cuerpos omitidos, el shim agrega la señal derivada
`ANDROID_SMS_UNANALYZED` (`artifact_type=android_sms`, `z=0`,
`signal_class=derived`). No añade findings, no puntúa texto no inspeccionado y
no fabrica corroboración; usa el mecanismo F7 existente para que el agente
vea `results.unanalyzed_artifacts` y no generalice limpieza al sufijo no leído.

Esto es independiente de L-041: B-167 declara cobertura parcial; L-041 sigue
documentando que, aun dentro de las 500 filas leídas, el extractor sólo modela
la regla calibrada de menciones salientes a apps cifradas y no debe convertir
lenguaje genérico de coordinación en intención.

**Validación:** `tests/test_b167_android_sms_truncation.py` se escribió rojo
contra el HEAD previo y fija tanto la telemetría del analizador como la
propagación del marcador a `n_unanalyzed_artifacts` del shim.

---

## B-168 — Las dos entradas FastAPI prometían el mismo gateway pero exponían contratos distintos [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de superficie API / seguridad de despliegue. No altera el scoring ni los bundles. |
| **Archivos** | `vigia_api.py`, `vigia/vigia_api.py`, nuevos `vigia/api_defaults.py` y `vigia/openai_compat.py`, `INSTALL.md`, `INSTALL_ES.md`. |
| **Detectado por** | Auditoría Codex de la superficie menos ejercitada (API), 2026-07-21. |

Ambos módulos se describían como gateway FastAPI para OpenWebUI, pero sólo el
script raíz exponía el contrato OpenAI-compatible que ese cliente necesita:
`GET /v1/models` y `POST /v1/chat/completions`. Ejecutar o importar
`vigia.vigia_api` producía una API que parecía sana (`/health`, `/cases` y los
dos endpoints directos), pero no podía completar el handshake de OpenWebUI.
Al mismo tiempo, el wrapper empaquetado aceptaba CORS desde `*`, mientras que
el raíz aplicaba una lista explícita. La diferencia permitía que una elección
de import path cambiara tanto la funcionalidad publicada como el límite de
navegador, sin señal al operador.

**Prueba roja:** `tests/test_b168_api_contract_parity.py` falló contra el
HEAD previo: faltaban ambos endpoints bajo `vigia.vigia_api` y la inspección
de `app.user_middleware` encontró `allow_origins=['*']` sólo en ese wrapper.

**Corrección aplicada:** el shim OpenAI-compatible vive ahora una sola vez en
`vigia/openai_compat.py` y ambos wrappers lo instalan con sus propias funciones
de pipeline/narrativa. `vigia/api_defaults.py` concentra host loopback,
puerto y CORS por defecto para que las dos entradas no vuelvan a divergir.
Los documentos de instalación ahora reflejan el host real `127.0.0.1`, el
estado real de `/health`, y declaran el límite importante: la API no valida
keys, CORS no autentica, y una exposición remota exige un reverse proxy
autenticado y una política de red deliberada. No se inventó un protocolo de
credenciales incompatible con OpenWebUI.

**Validación:** la prueba de paridad fija endpoints, CORS y ejecución del
pipeline local stubbed desde ambos imports; junto a
`tests/test_vigia_api_boundaries.py`: **23 passed**. Las pruebas no abren
sockets ni leen archivos fuera de fixtures.

---

## B-169 — El audit trail MCP omitía la mayoría de las invocaciones de herramientas [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de procedencia de ejecución (Mode 2 / Mode 5). No modifica los veredictos, el scorer ni los bundles existentes. |
| **Archivos** | `vigia/vigia_sift_bridge.py`, `KNOWN_LIMITATIONS.md`, `tests/test_b169_mcp_invocation_audit.py`. |
| **Detectado por** | Revisión Codex de la superficie MCP y seguimiento de L-057, 2026-07-21. |

La bridge activa tenía tres `TOOL_INVOKED` escritos a mano
(`list_files`, `read_evidence`, `generate_forensic_hash`), pero otras
herramientas con consecuencias relevantes —`search_pattern`,
`mount_sift_evidence`, `reason_with_llm` y activación/desactivación de honey
tokens— podían ejecutarse sin evento de entrada. Además, las herramientas
externas registradas con `mcp.tool()(...)` al final del archivo no atravesaban
ninguna frontera común. El trail podía mostrar un resultado o un log interno,
pero no demostrar uniformemente que la herramienta había sido invocada con
una clase de parámetros determinada.

**Prueba roja:** una llamada stubbed a `search_pattern` retornaba normalmente
con cero eventos `TOOL_INVOKED`; un contrato AST encontró 22 decoradores MCP
directos y múltiples registraciones externas que evitaban todo wrapper común.

**Corrección aplicada:** `_register_mcp_tool()` es ahora la única ruta de
registro MCP. Envuelve tanto las 22 herramientas locales como las externas
opcionales y escribe `TOOL_INVOKED` antes de rate limit, validación, sandbox o
ejecución. La telemetría conserva nombre de argumento, tipo/cardinalidad y un
SHA-256 de prefijo de hasta 4 KiB para `str`/`bytes`; no vuelca texto de
evidencia, prompts, rutas ni secretos al log sólo para auditar la llamada. Se
retiraron los tres logs manuales anteriores para no duplicar eventos.

**Límite honesto:** el cambio acredita la entrada en el proceso bridge que
escribió la cadena HMAC. No autentica por sí mismo al cliente MCP, no vuelve
retroactivamente completos a bundles anteriores y no prueba tiempo de pared ni
que una respuesta post-hoc provenga de una sesión viva.

**Validación:** `tests/test_b169_mcp_invocation_audit.py` prueba que una
búsqueda registra entrada antes de procesar el patrón sensible y que ninguna
registración evade la frontera compartida. Junto con el contrato de montaje
B-164: **13 passed**. La prueba no monta imágenes ni ejecuta un subprocess
real.

---

## B-170 / L-063 — El fallback de CAIE otorgaba autoridad de veredicto a fracturas declaradas en JSON [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Limitación cerrada** | `L-063` — resuelta por degradación honesta: JSON conserva evidencia declarada, no autoridad de veredicto. |
| **Severidad** | P2 de integridad/autoridad de veredicto en modo degradado. |
| **Archivo** | `vigia_scorer.py`, `KNOWN_LIMITATIONS.md`, `tests/characterization/test_verdict_authority_inputs.py`. |
| **Detectado por** | Cierre de L-063, tras el barrido de entradas de autoridad de veredicto. |

Cuando `vigia.tools.caie` no se podía importar, `_vigia_score()` recuperaba
`case["caie_fractures"]` y lo usaba como si fuera salida de CAIE. Un caller que
conociera un `fracture_type` malicioso reconocido podía declarar una fractura
con severidad alta y obtener un salto determinista `NOISE -> SUSPICION`, sin que
el productor que normalmente deriva esa afirmación hubiera corrido. El campo
`caie_fractures_source="json_fallback"` quedaba sellado, pero una etiqueta de
procedencia no elimina por sí misma la autoridad que ya se aplicó.

**Prueba roja:** el caso de caracterización bloquea deliberadamente el import
de CAIE y entrega un único `FALSE_FLAG_PATTERN` desde JSON. Antes de B-170 el
resultado era `SUSPICION` y `fracture_malice_boost > 0`; la entrada no provenía
de artefactos ni de una ejecución CAIE viva.

**Corrección aplicada:** las fracturas declaradas permanecen como material
auditable (`caie_fracture_details`), pero en fallback no participan ni del
boost de malicia ni de la penalidad de credibilidad. El resultado declara
`caie_fracture_authority="unverified_json_no_verdict_authority"`. Si la lista
contiene un tipo que CAIE reconocería, la ausencia del productor pasa a ser
decisión-relevante: VIGÍA emite `ABSTAIN`, conserva la lista en
`unverified_json_caie_fractures`, y registra el veredicto/razón de score previo
al gate. Así el sistema no fabrica ni una escalada ni una limpieza a partir de
una afirmación no verificable; exige reejecución con CAIE vivo.

**Límite deliberado:** B-170 no inventa un productor ni intenta validar una
fractura desde texto libre. Tampoco modifica CAIE vivo: cuando está disponible,
éste sigue recalculando sus fracturas desde artefactos y conserva su autoridad
normal. L-064 y L-065 son canales de autoridad distintos y permanecen
pendientes.

**Validación:**
`tests/characterization/test_verdict_authority_inputs.py::TestT1FallbackFractureAuthority`
verifica: JSON reconocido + CAIE ausente = `ABSTAIN`, boost `0`, disclosure
sellada; tipo no reconocido = inerte; CAIE vivo = recomputa y descarta el JSON.

---

## B-171 / L-064 — `STATISTICAL_UNIFORMITY` declarada en JSON podía subir el veredicto en todos los modos [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Limitación cerrada** | `L-064` — resuelta por degradación honesta: la regularidad declarada permanece visible, pero no es un resultado de un productor del scorer. |
| **Severidad** | P2 de integridad/autoridad de veredicto, con alcance en todos los modos. |
| **Archivo** | `vigia_scorer.py`, `KNOWN_LIMITATIONS.md`, `tests/characterization/test_verdict_authority_inputs.py`, `tests/test_audit_gates.py`. |
| **Detectado por** | Cierre del canal T-2 de entradas de autoridad de veredicto. |

`temporal_violations[].type == "STATISTICAL_UNIFORMITY"` añadía
`severity * 0.35` a `fracture_malice_boost` aun cuando ningún módulo del runtime
del scorer había calculado esa estadística. Un JSON construido a mano podía
mover `NOISE -> SUSPICION` tanto con CAIE vivo como sin CAIE. La existencia de
un tool MCP de jitter no mitigaba el problema: recibe otra forma de entrada,
usa otro contrato y no alimentaba el bundle ni el scorer.

**Prueba roja:** una base de tres logs de score bajo obtiene una única
`STATISTICAL_UNIFORMITY` desde JSON. Antes de B-171 emitía `SUSPICION` con boost
positivo en los dos modos. La caracterización también confirmó el impacto real:
`case_002_log_fabrication` pasaba de `UNKNOWN` (0.0839) a `SUSPICION` (0.3354)
sólo por esa declaración.

**Corrección aplicada:** el scorer ya no agrega términos SU al acumulador ni
permite que esa declaración reduzca el trust vía `_compute_temporal_factor`.
La declaración se preserva en `unverified_statistical_uniformity_violations` y
el campo `statistical_uniformity_authority` declara explícitamente que no posee
autoridad. Cuando aparece, el resultado final es `ABSTAIN`, conserva el
veredicto y la razón de score previos, y exige una reejecución con un productor
determinista que derive la regularidad desde intervalos crudos.

**Límite deliberado:** no se fingió que el MCP jitter era ese productor ni se
aceptaron `interval_seconds_std`, `uniformity_flag` o texto narrativo como
prueba calculada. Construir el detector correcto requiere un contrato nuevo de
secuencias temporales crudas, aritmética exacta, corpus negativo y calibración.
La etiqueta de escenario de `case_002_log_fabrication` se mantiene; el motor
ahora abstiene honestamente hasta que exista esa evidencia.

**Validación:** `TestT2StatisticalUniformity` prueba `ABSTAIN`, boost `0` e
identidad exacta de score/trust frente a la misma evidencia sin SU, con CAIE
vivo y caído. Las regresiones de fracturas CAIE vivas, Decimal severity y el
gate de corroboración independiente se conservan con una fractura CAIE viva
test-only, no con un boost JSON.

---

## B-172 / L-062 — una declaración temporal podía imponer `MALICE` sin coincidir con los artefactos [MITIGADO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Limitación mitigada** | Porción de autoridad de `L-062`: una afirmación JSON `EFFECT_BEFORE_CAUSE` ya no puede disparar por sí sola el gate categórico. La tolerancia de relojes H-01 continúa abierta. |
| **Severidad** | P2 de integridad/autoridad de veredicto, con alcance en todos los modos que llaman al scorer determinista. |
| **Archivo** | `vigia_scorer.py`, `tests/test_b172_hard_temporal_pair_validation.py`, `tests/characterization/test_temporal_gate_curve.py`, `KNOWN_LIMITATIONS.md`, `docs/CODEX_AUDIT_2026-07-21.md`. |
| **Detectado por** | Auditoría de entradas de autoridad de veredicto y la curva de caracterización temporal L-062/H-01. |

El gate histórico evaluaba solamente la declaración
`temporal_violations[].type == "EFFECT_BEFORE_CAUSE"` y una severidad alta. Si
el JSON afirmaba una inversión de cinco segundos, el scorer emitía `MALICE`
aunque los timestamps de los artefactos reales mostraran que el supuesto efecto
ocurrió después de la causa. La copia anidada de timestamps y `delta_seconds`
eran una alegación del examinador, no una derivación verificable.

**Prueba roja:** `test_asserted_inversion_contradicted_by_artifacts_abstains`
declara `effect < cause`, pero entrega artefactos donde el efecto sucede dos
segundos después de la causa. Antes de B-172 obtenía `MALICE`; esa conclusión
no era falsificable desde la evidencia fuente.

**Corrección aplicada:** B-172 reconstruye el par desde IDs de artefacto
únicos y sus timestamps ISO-8601 de nivel superior. Ambos timestamps deben
tener zona horaria explícita, pertenecer a la ventana de plausibilidad fija de
CAIE y satisfacer realmente `effect < cause`. Sólo ese par verificado conserva
el gate histórico. Una alegación de severidad alta que no verifica se retiene
en `unverified_hard_temporal_violations`, se excluye de todas las penalidades
temporales y produce `ABSTAIN`, con razón y par previo sellados. El resultado
expone `hard_temporal_authority` y, cuando existe, el par validado.

**Límite deliberado:** esto no decide H-01. Una inversión real, incluso de
fracción de segundo, conserva por ahora el gate categórico anterior; los dos
`xfail` de `tests/test_audit_temporal_skew.py` siguen marcando esa doctrina
pendiente. Tampoco reemplaza L-065: B-172 valida coherencia entre la alegación
y los artefactos presentes, no autentica por sí sola la cadena de procedencia.

**Validación:** 74 tests pasan y 4 `xfail` documentados se conservan en la
batería de autoridad temporal, CAIE, `Fraction` y severidad `Decimal`. El caso
canónico con inversión real de cinco segundos mantiene `MALICE`; una alegación
contradicha o con artefacto ausente ahora emite `ABSTAIN`.

---

## B-173 — el import del bridge MCP mutaba `VIGIA_EVIDENCE_DIR` con estado operativo [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: la mutación ocurría antes de leer un artefacto y cambiaba el listado/mtime del árbol de evidencia. |
| **Archivo** | `vigia/vigia_sift_bridge.py`, `tests/test_b173_bridge_work_root.py`, `tests/test_b164_mcp_mount_root.py`, `CLAUDE.md`. |
| **Modos** | MCP activo (`launch_vigia_mcp.sh` ejecuta este bridge); cualquier import del módulo con `VIGIA_EVIDENCE_DIR` configurado. |
| **Principio afectado** | Invariante 1 de `CLAUDE.md`: evidencia read-only; los artefactos extraídos deben ir a un directorio de trabajo separado. |

**Observación reproducida:** con un directorio de evidencia vacío,
`VIGIA_EVIDENCE_DIR=<evidence> python3 -c 'import vigia.vigia_sift_bridge'`
creaba inmediatamente `honey_tokens/`, `purgatory/` y `mounted/` debajo de la
entrada. No era necesario invocar una herramienta. B-164 había hecho que el
mount fuera alcanzable al ubicarlo bajo el mismo root de lectura; eso reparó un
gate imposible pero confundió la raíz de entrada con la raíz operacional.

**Corrección aplicada:** B-173 introduce `VIGIA_WORK_DIR`, una raíz privada
`0700` disjunta de la evidencia. Si no se configura, el bridge crea una raíz
temporal privada por proceso. Honey tokens, cuarentena y mount points viven
allí. El bridge rechaza antes de crear directorios una workdir anidada, igual o
padre de `VIGIA_EVIDENCE_DIR`, y también rechaza componentes symlink. Las
herramientas de lectura aceptan sólo la evidencia original o el subárbol
controlado `WORK_BASE_DIR/mounted`; la fuente de `mount_sift_evidence` continúa
restringida exclusivamente a evidencia original.

**Validación:** 30 pruebas MCP pasan: import subprocess sin mutar evidencia,
rechazo de workdir insegura, mount root legible pero confinado, targets
malformados/symlinks rechazados, auditoría de invocación y sanitización grep.

**Límite deliberado:** el Purgatorio conserva una copia operativa y su hash;
no la reetiqueta como evidencia fuente ni resuelve por sí mismo L-065 (la
autenticación de cadenas de procedencia). El directorio de trabajo debe
preservarse explícitamente si el operador necesita retener ese estado entre
reinicios.

---

## B-174 — `safe_grep` autorizaba un directorio hermano por prefijo textual [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de confidencialidad: una búsqueda MCP podía leer fuera de sus roots autorizados si el directorio externo compartía el prefijo textual. |
| **Archivo** | `vigia/security/sandbox.py`, `tests/test_b174_safe_grep_allowed_root.py`. |
| **Modo** | MCP `search_pattern`, a través del helper reutilizable `safe_grep(..., allowed_dirs=...)`. |
| **Principio afectado** | La lista de directorios permitidos expresa una frontera de autoridad de filesystem, no una coincidencia de cadenas. |

**Observación reproducida:** con un root permitido `.../evidence`, un
directorio hermano `.../evidence-escape/private.txt` y
`allowed_dirs=[".../evidence"]`, el guard anterior hacía
`safe_folder.startswith(allowed_dir)`. La condición era verdadera y `find` +
`grep` devolvían el contenido de `private.txt`, aun cuando no era descendiente
de la evidencia autorizada.

**Corrección aplicada:** los roots permitidos se canonicalizan, se exige que
existan, sean directorios y no contengan symlinks; luego la pertenencia se
evalúa por componentes de `Path` (`==` o `is_relative_to`), nunca por prefijo
de texto. Una subcarpeta real sigue siendo legible; un hermano, una raíz
inválida o un symlink se rechazan antes de iniciar el subprocess.

**Validación:** 32 pruebas de sandbox/MCP pasan, incluidas la reproducción que
antes filtraba el texto externo y el control positivo de una carpeta hija real.
El cambio no modifica señales, score ni veredicto: reduce exclusivamente la
autoridad de lectura de la herramienta.

---

## B-175 — el exportador de grafos podía escribir dentro de evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: un artefacto derivado podía aparecer junto a la entrada y cambiar el árbol que se debía preservar. |
| **Archivo** | `vigia/abduction/vigia_artifact_graph.py`, `tests/test_b175_artifact_graph_output_boundary.py`. |
| **Modos** | CLI de Artifact Graph: JSON, GEXF y GraphML. |
| **Principio afectado** | `VIGIA_EVIDENCE_DIR` es entrada inmutable, aunque resida debajo de un root general de salida permitido como `/home` o `/tmp`. |

**Observación reproducida:** el CLI construía por defecto el output JSON con
`bundle_path.with_suffix(".graph.json")` y lo escribía directo con
`Path.write_text`, sin pasar por `_validate_output_path`. Por tanto un bundle
en `VIGIA_EVIDENCE_DIR/case.json` producía
`VIGIA_EVIDENCE_DIR/case.graph.json`. Los exportadores GEXF/GraphML sí
llamaban al validador, pero éste permitía cualquier path bajo `/home` o `/tmp`
sin excluir la raíz de evidencia y sólo revisaba un symlink en el padre
inmediato.

**Corrección aplicada:** JSON, GEXF y GraphML usan la misma validación. El
target y `VIGIA_EVIDENCE_DIR` se canonicalizan y se comparan por componentes;
cualquier target dentro de evidencia, incluso por un redirect, aborta. La
validación de roots permitidos también pasó de prefijo textual a
`Path.is_relative_to`, y cada componente existente del path de salida se
inspecciona con `lstat`: un symlink intermedio o final se rechaza antes de
escribir.

**Validación:** cuatro regresiones cubren export directo a evidencia, redirect
intermedio, el CLI JSON con su output por defecto y una carpeta hija real de
un root permitido. Junto con las pruebas B-164/B-169/B-173/B-174 de bridge y
sandbox, pasan 36 tests. La corrección afecta exclusivamente los destinos de
escritura; no cambia el contenido lógico del grafo ni los veredictos.

---

## B-176 — el rechazo del PDF pericial ocurría después de crear una carpeta en evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una configuración inválida de PDF alteraba el árbol de evidencia aun cuando no generaba el PDF. |
| **Archivo** | `vigia/tools/adversarial_nlp.py`, `tests/test_b176_pericial_pdf_evidence_boundary.py`. |
| **Modo** | Análisis de registro estilométrico que activa el PDF pericial opcional. |
| **Principio afectado** | Validar el destino antes de cualquier side effect; `VIGIA_EVIDENCE_DIR` nunca recibe estado derivado. |

**Observación reproducida:** `_export_pdf()` hacía
`os.makedirs(VIGIA_PERICIAL_PDF_DIR, exist_ok=True)` antes de comprobar si el
PDF terminaba debajo de `VIGIA_EVIDENCE_DIR`. Con
`VIGIA_PERICIAL_PDF_DIR=<evidence>/generated-reports`, el método devolvía
correctamente `None` y registraba `PDF_EXPORT_INTO_EVIDENCE_DIR`, pero ya
había creado `generated-reports/` dentro de la evidencia.

**Corrección aplicada:** se construye el target y se compara
canónicamente con la raíz de evidencia antes de `makedirs`; el test usa
pertenencia por componentes (`==` / `is_relative_to`), por lo que
`evidence-copy` no queda bloqueado por accidente y un symlink hacia evidencia
no puede ocultar el destino. Sólo si el target es externo se crea la carpeta y
se invoca el renderer.

**Validación:** dos regresiones prueban que el rechazo deja la evidencia vacía
y que el flujo externo crea el directorio, llama al renderer y preserva la
evidencia. La batería integrada de boundaries de exportación, sandbox y MCP
queda en 38 tests passing. No se modifican análisis, señales ni veredictos.

---

## B-177 — el agente autónomo permitía bundles dentro de evidencia si el CWD coincidía [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: el bundle sellado, checksum y trace podían contaminar la evidencia de entrada. |
| **Archivo** | `vigia_agent.py`, `tests/test_b177_agent_output_evidence_boundary.py`. |
| **Modo** | CLI del agente autónomo (Modo 1 / batch). |
| **Principio afectado** | Estar dentro del CWD permitido no autoriza a escribir dentro de la evidencia; ambos límites son necesarios. |

**Observación reproducida:** el guard anterior verificaba sólo que
`Path(output).resolve()` fuera descendiente de `Path.cwd()`. Un operador que
ejecutaba `vigia_agent.py` desde `VIGIA_EVIDENCE_DIR` recibía el output por
defecto `<case-id>_bundle.json` dentro de esa misma evidencia. `atomic_write_text`
podía crear además los directorios padre, y el flujo escribía tres siblings:
bundle, `.sha256` y `_reasoning_trace.json`.

**Corrección aplicada:** `_validate_agent_output_path()` define un contrato
testeable: canonicaliza el target, exige pertenencia al workdir y rechaza por
componentes cualquier solapamiento con `VIGIA_EVIDENCE_DIR`. `main()` lo llama
antes de construir el agente o escribir archivos y usa la ruta absoluta
resultante para los tres artifacts asociados. El cambio preserva los outputs
normales en `results/` y rechaza destinos fuera del CWD como antes.

**Validación:** tres regresiones cubren el output por defecto con CWD=evidencia,
un target explícito dentro de evidencia y un sibling `results/` válido. También
pasan el test end-to-end B-105 del bundle/trace/checksum y las fronteras B-175
y B-176. No altera el análisis ni los veredictos, sólo su destino de escritura.

---

## B-178 — exportación SQLite para SIFT podía escribir artefactos derivados dentro de evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una copia de la base pericial podía aparecer en el árbol de evidencia fuente. |
| **Archivo** | `vigia/tools/forensic_db.py`, `tests/test_b178_forensic_db_export_boundary.py`. |
| **Modo** | Exportación opcional SIFT del análisis pericial (`export_db_path`), disponible a través de `analyze_document_register`. |
| **Principio afectado** | Un path de salida controlado por caller es autoridad de escritura; la evidencia no puede recibir copias derivadas ni por ruta directa ni por redirect. |

**Observación reproducida:** `ForensicDatabaseManager.export_for_sift()`
canonicalizaba sólo el nombre final, creaba el padre si faltaba y pasaba el
path a `sqlite3.Connection.backup()`. No consultaba `VIGIA_EVIDENCE_DIR`. Una
DB fuente externa con `export_path=<evidence>/sift-export.db` creaba la copia
SQLite dentro de evidencia. Un padre symlink (`export-redirect -> evidence`)
también podía redirigir la exportación, porque se inspeccionaba únicamente el
archivo final, que aún no existía.

**Corrección aplicada:** `_validate_sift_export_path()` rechaza path vacío o
con NUL, inspecciona con `lstat` cada componente existente y rechaza symlinks,
canonicaliza el target y prohíbe por componentes cualquier solapamiento con
`VIGIA_EVIDENCE_DIR`. La primera validación ocurre antes de `makedirs`; una
segunda ocurre después de crear un padre externo, antes de que SQLite abra el
archivo. El flujo conserva la exportación legítima a un workdir externo.

**Validación:** tres regresiones cubren el write directo que antes ocurría, el
padre symlink que resolvía dentro de evidencia y el control positivo de una
exportación SQLite externa. Junto con B-175/B-176/B-177, pasan 12 tests. No
modifica señales, puntajes ni veredictos; sólo reduce la autoridad de salida de
una herramienta pericial.

---

## B-179 — la plantilla de configuración pericial podía contaminar evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una operación auxiliar podía crear directorios y sobrescribir un archivo de configuración en la evidencia fuente. |
| **Archivo** | `vigia/tools/adversarial_nlp.py`, `vigia/tools/forensic_db.py`, `tests/test_b179_config_template_evidence_boundary.py`. |
| **Modo** | API `ForensicEngine.save_config_template()` / `ConfigLoader.save_default_config()`. |
| **Principio afectado** | El hecho de que un output sea una plantilla y no un resultado analítico no le concede autoridad sobre `VIGIA_EVIDENCE_DIR`. |

**Observación reproducida:** `ConfigLoader.save_default_config(path)` convertía
el path a absoluto, ejecutaba `os.makedirs(parent)` y abría el archivo en modo
`"w"`, sin consultar la raíz de evidencia. Con
`path=<evidence>/templates/defaults.json` creaba `templates/` y escribía el
JSON de configuración. El comportamiento era alcanzable por la fachada pública
`save_config_template()` del motor pericial.

**Corrección aplicada:** B-179 extrae `validate_external_output_path()` como
contrato común de output para el gestor SQLite y la plantilla. Rechaza vacío y
NUL, componentes symlink existentes y todo destino que canónicamente sea
descendiente de `VIGIA_EVIDENCE_DIR`. Cada caller lo aplica antes de crear
padres y nuevamente después, antes de abrir/escribir. La plantilla externa se
mantiene soportada; los tests B-178 conservan la cobertura de la exportación
SIFT sobre el mismo guard.

**Validación:** tres regresiones cubren el destino directo dentro de evidencia,
el padre symlink que resuelve a evidencia y el control positivo externo. La
familia B-175 a B-179 queda en 15 tests passing. El cambio no toca detección,
score, modelado ni veredictos: sólo retira autoridad de escritura indebida.

---

## B-180 — constructor de paquetes sellados podía escribir en evidencia y recibir traversal por `case_id` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una API de empaquetado podía contaminar la fuente con PDF copiado, ledger, manifest, firma y ZIP; el identificador del caso también podía escapar del output externo. |
| **Archivo** | `vigia/security/output_boundary.py` (nuevo), `vigia/pipeline/evidence_bundle.py`, `vigia/tools/forensic_db.py`, `vigia/tools/adversarial_nlp.py`, `tests/test_b180_evidence_bundle_output_boundary.py`. |
| **Modo** | `build_evidence_bundle()` de la API de bundles verificables; el guard compartido cubre además SIFT y plantillas periciales. |
| **Principio afectado** | Un directorio de salida y un identificador de caso son ambos inputs de autoridad. Ningún artefacto derivado puede cruzar hacia `VIGIA_EVIDENCE_DIR`. |

**Observación reproducida:** `build_evidence_bundle()` ejecutaba
`os.makedirs(output_dir)` sin validar, luego escribía bajo
`<output_dir>/<case_id>_bundle/` el PDF, `ledger.json`, `manifest.json` y
potencialmente firma/ZIP. Con `output_dir=<evidence>` el paquete completo se
creaba dentro de la fuente. Aun después de validar sólo `output_dir`, un
`case_id="../evidence/b180"` habría permitido que `os.path.join()` construyera
un bundle fuera del root externo. Un directorio de salida symlink hacia
evidencia era el tercer vector equivalente.

**Corrección aplicada:** B-180 mueve el contrato genérico a
`vigia.security.output_boundary`: `validate_external_output_path()` valida
vacío/NUL, rechaza cada componente symlink con `lstat`, canonicaliza y bloquea
pertenencia por componentes a `VIGIA_EVIDENCE_DIR`, antes y después de crear
un padre externo. Lo usan el paquete, exportación SIFT y plantilla de config.
El builder además valida que `case_id` sea una etiqueta no vacía sin NUL,
separadores ni `.`/`..`; todas sus rutas hijas se derivan sólo de ese ID seguro.

**Validación:** cuatro regresiones B-180 cubren output directo en evidencia,
control positivo externo, traversal por ID y output symlink. Con B-178/B-179 y
las regresiones B-062/B-064 de atomicidad/registro, pasan 21 tests. La
corrección no modifica contenido forense, scores ni veredictos; restaura la
separación entre entrada preservada y paquete derivado.

---

## B-181 — `EvidenceLedger.export_json()` tenía atomicidad sin frontera de salida [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: un ledger encadenado podía escribirse en la evidencia de origen, por ruta directa o padre symlink. |
| **Archivo** | `vigia/pipeline/security_evidence_registry.py`, `tests/test_b181_evidence_ledger_export_boundary.py`. |
| **Modo** | API `EvidenceLedger.export_json(path)`. |
| **Principio afectado** | Una escritura atómica preserva el ledger destino, pero no autoriza que ese destino sea la evidencia fuente. Atomicidad y autorización son garantías distintas. |

**Observación reproducida:** la exportación usaba correctamente
`atomic_write_text(path, ...)`, pero recibía `path` sin validación. Con
`path=<evidence>/ledger.json` creaba el ledger en la entrada preservada. Con un
padre `ledger-redirect -> evidence`, el helper atómico creaba el tempfile y
publicaba el JSON a través del symlink. Ambos resultados fueron inducidos antes
del parche; la exportación externa servía como control positivo.

**Corrección aplicada:** el ledger pasa su destino por
`validate_external_output_path()` antes de crear el padre y una segunda vez
antes de invocar `atomic_write_text`. Conserva el write atómico B-064, por lo
que el nuevo control añade autorización sin debilitar la resistencia a crash.
El error es fail-closed (`SecurityError`) y no deja tempfiles ni directorios
dentro de evidencia.

**Validación:** tres regresiones cubren destino directo, padre symlink y
exportación externa; con B-178 a B-180 y las regresiones B-062/B-064 pasan 24
tests. El JSON, la cadena hash y sus semánticas no cambian.

---

## B-182 — el exportador PDF forense v2 podía publicar dentro de evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una vista PDF derivada podía aparecer en el árbol de evidencia fuente, sin publicación atómica. |
| **Archivo** | `vigia/pipeline/report_exporter_v2.py`, `tests/test_b182_report_pdf_output_boundary.py`. |
| **Modo** | API opcional `export_pdf()` del exportador forense standalone. |
| **Principio afectado** | Un renderer no obtiene autoridad de escritura sobre evidencia por recibir un `output_path`; una salida derivada debe estar confinada y publicarse de manera atómica. |

**Observación reproducida:** tras construir los bytes PDF, `export_pdf()` abría
el `output_path` entregado por el caller en modo binario de escritura. No había
ninguna comprobación contra `VIGIA_EVIDENCE_DIR`, por lo que
`<evidence>/report.pdf` era un destino válido; un padre symlink también podía
redirigir la publicación. `reportlab` no está instalado en este entorno pese a
ser dependencia declarada, así que la regresión instala un renderer mínimo
simulado y ejecuta el branch real de construcción/publicación: eso aísla la
frontera de filesystem y reproduce los dos writes antes del fix sin convertir
la disponibilidad local del renderer en una excusa para no probarla.

**Corrección aplicada:** el exportador valida el destino mediante el contrato
compartido `validate_external_output_path()` antes de renderizar. Una vez que
los bytes están listos crea sólo el padre externo, valida nuevamente para
cerrar la ventana de redirección, y usa `atomic_write_bytes()` para publicar.
El metadata devuelto contiene el path canónico validado. Las salidas externas
siguen soportadas; los destinos dentro de evidencia o que pasan por symlink
fallan cerrados con `SecurityError` sin crear archivos fuente.

**Validación:** tres regresiones B-182 cubren destino directo dentro de
evidencia, padre symlink y PDF externo atómico. Junto con B-178 a B-181 y
B-062/B-064 pasan 27 tests. No afecta contenido analítico, hashes del informe,
puntajes ni veredictos; limita exclusivamente la autoridad de publicación.

---

## B-183 — `BundleBuilder.save()` podía sellar un resultado dentro de evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: la API central de publicación de bundles podía crear o reemplazar un JSON derivado dentro de la evidencia fuente. |
| **Archivo** | `vigia/core/bundle_builder.py`, `tests/test_b183_bundle_builder_output_boundary.py`. |
| **Modo** | API Python `BundleBuilder.save()`, consumida por `run_vigia`, CLI y el bridge de integración. |
| **Principio afectado** | El sellado criptográfico prueba el contenido del bundle, no autoriza su destino. Una cadena de custodia no puede comenzar modificando la evidencia que pretende describir. |

**Observación reproducida:** aunque B-064 ya garantizaba tempfile, `fsync`,
`replace` y hash desde disco, `BundleBuilder.save()` aceptaba un path arbitrario
y ejecutaba `makedirs()` sobre su padre. Con
`path=<evidence>/bundle.json` escribía el bundle sellado en la fuente. Con un
padre `bundle-redirect -> evidence`, el tempfile y el `replace` se publicaban
por esa redirección. Ambos fallos se indujeron antes del cambio; un destino
externo fue el control positivo.

**Corrección aplicada:** el sumidero público valida el destino con
`validate_external_output_path()` antes de crear el directorio y una segunda
vez antes de abrir el tempfile. Así heredan el límite la API, `run_vigia`, su
CLI y cualquier caller futuro, sin confiar en que cada fachada recuerde
validarlo. Se conserva íntegro el protocolo B-064: misma serialización
canónica, `fsync`, publicación atómica y hash calculado desde lo escrito.

**Validación:** tres regresiones B-183 cubren output directo en evidencia,
padre symlink y bundle externo verificable. También pasan las tres regresiones
atómicas L-023 y los dos tests de import/verify del pipeline: 6 seleccionados.
No altera el bundle en memoria ni el veredicto: sólo niega un destino que nunca
debió tener autoridad de escritura.

---

## B-184 — el bridge de integración podía crear outputs en evidencia y escapar con `case_id` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: el bridge podía crear su árbol de resultados en evidencia; además un ID de caso con separadores redirigía el writer de reportes fuera del output declarado. |
| **Archivo** | `vigia/pipeline/vigia_integration_bridge.py`, `tests/test_b184_integration_bridge_output_boundary.py`. |
| **Modo** | `VigiaIntegrationEngine.run_case()` — usado por la demo, bridge MCP y callers Python de la integración legacy ↔ EBS. |
| **Principio afectado** | `output_dir` y `case_id` son inputs distintos de autoridad de escritura. El primero debe quedar fuera de evidencia y el segundo debe ser datos, no una ruta derivada. |

**Observación reproducida:** el engine convertía `output_dir` a absoluto y
ejecutaba `os.makedirs()` antes de llamar al pipeline. Con
`output_dir=<evidence>/bridge-output` creaba el directorio fuente incluso si
no se solicitaba bundle ni reporte; un symlink de output tenía el mismo efecto.
La segunda vía fue más grave: `case_id="escape/../../evidence/pwn"` producía
`report_escape/../../evidence/pwn.json`. Con un componente externo existente,
`atomic_write_text()` resolvía esos `..` y publicó un JSON real dentro de
evidencia. La regresión lo reprodujo mediante el flujo del bridge, con pipeline
y renderer mínimos simulados, no calculando paths aislados.

**Corrección aplicada:** al existir alguna salida solicitada, el bridge valida
el directorio antes de crear nada y vuelve a validarlo antes de derivar
artefactos. Bundle y reporte pasan además por el guard justo antes de su uso.
`case_id` ahora sólo acepta etiquetas no vacías sin NUL, `.`/`..` ni separadores
de plataforma; se rechaza antes de la normalización o del pipeline. Si no se
solicita ningún output, el bridge deja de crear un directorio innecesario.

**Validación:** cuatro regresiones B-184 cubren output directo dentro de
evidencia, output symlink, traversal real por `case_id` hacia el writer de
reporte y bundle externo válido. La familia B-178 a B-184 más B-062/B-064 pasa
34/34. No cambia evidencia, score ni decisión; restaura el confinamiento y
evita que un identificador de caso se convierta en escritura.

---

## B-185 — la SQLite operacional podía usar evidencia como almacenamiento por defecto [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: perfiles ACP, historial temporal y audit trail SQLite podían crear DB, WAL y lockfile dentro del árbol de evidencia. |
| **Archivo** | `vigia/tools/forensic_db.py`, `vigia/tools/nlp_constants.py`, `tests/test_b185_forensic_db_source_boundary.py`, `tests/test_entanglement_groundtruth.py`, `README.md`, `CLAUDE.md`. |
| **Modo** | `ForensicDatabaseManager()` implícito en ACP, temporal y Entanglement; también constructor con `db_path` explícito. |
| **Principio afectado** | La persistencia del analista es estado operacional, no evidencia. Un singleton no puede tomar una raíz de entrada como fallback de escritura. |

**Observación reproducida:** sin `db_path`, el singleton componía
`$VIGIA_EVIDENCE_PATH/vigia_forensic.db` (o `/mnt/evidence`) y habilitaba WAL.
En una investigación con la raíz legacy apuntando a evidencia, la mera
construcción creaba la base y sus sidecars. El constructor explícito tampoco
consultaba `VIGIA_EVIDENCE_DIR`: aceptaba tanto `<evidence>/vigia_forensic.db`
como `db-redirect -> evidence` seguido de `db-redirect/vigia_forensic.db`.
Los tres caminos fueron inducidos antes del parche; una DB externa fue el
control positivo.

**Corrección aplicada:** se introduce `VIGIA_FORENSIC_DB_PATH` como destino
explícito. Sin él, el orden seguro es `VIGIA_WORK_DIR/vigia_forensic.db` y,
si tampoco está configurado, un state-dir estilo XDG del usuario. La variable
legacy `VIGIA_EVIDENCE_PATH` conserva significado de input pero no participa
en la elección del destino. Todo `db_path`, implícito o explícito, pasa por
`validate_external_output_path()` antes de crear padres y otra vez antes de
que SQLite pueda crear DB/WAL/lock. README, contrato MCP y el fixture de
Entanglement documentan la nueva configuración.

**Validación:** cuatro regresiones B-185 cubren DB explícita en evidencia,
padre symlink, fallback seguro aun si la variable legacy apunta a evidencia y
DB externa válida. También pasan B-178 (backup SIFT) y 21 pruebas de
Entanglement; se excluyen las dos de `TestIdenticalDocumentCollapse`, ya
marcadas en ese archivo como defecto de cadena de custodia pendiente e
independiente. No modifica señal, score ni veredicto: separa el estado
persistente del analista de los bytes adquiridos.

---

## B-186 — el ledger persistente de cadena de custodia podía contaminar evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: el ledger SQLite crea una base y potenciales sidecars junto a la evidencia que pretende atestiguar. |
| **Archivo** | `vigia/forensics/vigia_chain_of_custody.py`, `tests/test_b186_chain_ledger_output_boundary.py`, `README.md`, `CLAUDE.md`. |
| **Modo** | API `ChainOfCustody`, CLI `vigia_chain_of_custody.py --db`, y cualquier flujo que persista bundles sellados. |
| **Principio afectado** | El ledger es estado derivado del investigador; no puede tener como destino implícito el CWD ni una raíz de evidencia. |

**Observación reproducida:** el constructor anterior usaba
`vigia_chain.db` relativo al directorio de trabajo. Si un operador lanzaba el
verificador desde `VIGIA_EVIDENCE_DIR`, la construcción escribía el ledger en
el input. Un `--db <evidence>/chain.db` explícito era aceptado; también una
ruta bajo un padre symlink que redirigía a evidencia. Finalmente, una ruta
externa válida con padre aún inexistente fallaba antes de crear el ledger. Las
cuatro condiciones fueron inducidas antes del parche.

**Corrección aplicada:** el default ahora resuelve, en orden,
`VIGIA_CHAIN_DB_PATH`, `VIGIA_WORK_DIR/vigia_chain.db` y un state-dir estilo
XDG. El módulo sigue siendo ejecutable sólo con stdlib, por lo que incorpora
un guard local equivalente al contrato de output: rechaza NUL, inspecciona
con `lstat` cada componente existente para denegar symlinks, resuelve la ruta
y prohíbe destinos iguales o descendientes de `VIGIA_EVIDENCE_DIR`. Crea el
padre con permisos `0750` y valida de nuevo inmediatamente antes de que
SQLite pueda crear DB/WAL/journal. README y el contrato MCP documentan la
nueva variable.

**Validación:** cuatro regresiones B-186 cubren el destino explícito dentro
de evidencia, el escape por padre symlink, el default seguro aun con CWD
ubicado dentro de evidencia y un destino externo nuevo. También pasan las 27
pruebas existentes de hardening de cadena de custodia: **31/31**. No altera
el contenido de ningún bundle, el hash canónico ni los veredictos; sólo
separa la persistencia del ledger de los bytes adquiridos.

---

## B-187 — el inicializador de patrones podía borrar o crear SQLite dentro de evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: el inicializador hace `DELETE` e inserciones idempotentes; un `--db` mal dirigido podía modificar un SQLite adquirido. |
| **Archivo** | `vigia/tools/init_patterns_db.py`, `tests/test_b187_patterns_db_output_boundary.py`. |
| **Modo** | Inicialización fresh/CI mediante `python3 vigia/tools/init_patterns_db.py [--db PATH]`. |
| **Principio afectado** | Una herramienta de construcción de corpus no recibe autoridad para reescribir evidencia por aceptar una ruta de DB arbitraria. |

**Observación reproducida:** `init_db()` creaba el padre, abría cualquier
ruta SQLite, instalaba schema y ejecutaba `DELETE FROM nlp_patterns`. Con
`VIGIA_EVIDENCE_DIR` configurado, tanto
`<evidence>/forensic_patterns.sqlite` como
`patterns-redirect -> <evidence>` seguido de
`patterns-redirect/forensic_patterns.sqlite` eran aceptados y modificados.
Ambos escapes fueron inducidos antes del parche; una DB nueva fuera de
evidencia fue el control positivo.

**Corrección aplicada:** el inicializador usa
`validate_external_output_path()` antes de crear el padre y vuelve a
validarlo antes de que SQLite pueda crear DB/WAL/journal. Conserva su DB de
patrones distribuida y el comportamiento idempotente para CI; sólo deniega
destinos dentro de evidencia o con componentes symlink. Como la invocación
documentada es directa, se añadió el bootstrap mínimo de `sys.path` para que
el import del guard funcione tanto con `python3 vigia/tools/init_patterns_db.py`
como con módulo/CI, sin exigir `PYTHONPATH`.

**Validación:** B-187 cubre destino directo en evidencia, redirección por
symlink, DB externa válida y la invocación directa documentada. La prueba fue
roja antes del parche (2 escapes reproducidos) y verde después: **4/4**.
Junto con B-186, pasan **8/8**. No modifica la semántica de los patrones ni
los veredictos; quita autoridad de escritura al argumento `--db` cuando
apunta a evidencia.

---

## B-188 — el detector semiótico simulaba un fallback inexistente ante DB de patrones ausente [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de degradación honesta: una dependencia semiótica ausente podía fallar con `no such table` después de aparentar un fallback de primer uso. |
| **Archivo** | `vigia/core/semiotic_detector_v2.py`, `tests/test_b188_missing_patterns_db_degradation.py`. |
| **Modo** | `SemioticDetectorV2` usado por el pipeline y por `vigia_case_adapter`; en modo agente, la falla del detector debe ser `ABSTAIN`, nunca `NOISE`. |
| **Principio afectado** | Un componente indisponible no puede presentarse como detector vacío ni como resultado limpio. El fallo debe ser explícito para que el adaptador conserve el fault y se abstenga. |

**Observación reproducida:** `_load_patterns()` abría la DB con `mode=ro`; si
no existía, capturaba el error y creaba `:memory:` con el comentario
“fallback … primer run”. Inmediatamente intentaba `SELECT … FROM
nlp_patterns` en esa memoria sin schema, por lo que la construcción abortaba
con `sqlite3.OperationalError: no such table`. Además, el URI se armaba por
interpolación de ruta, en vez de serializar un file URI. La regresión B-188
reprodujo la falla con una ruta ausente y verificó que no se creara archivo.

**Corrección aplicada:** se elimina el falso fallback. La ruta se convierte a
`Path(...).resolve().as_uri()` y se abre sólo con `mode=ro`; cualquier error
de apertura o schema se traduce en `RuntimeError` explícito: `semiotic pattern
database unavailable`. No se fabrica una memoria vacía que podría devolver
ausencia de patrones con apariencia de análisis. El adaptador existente ya
registra esa indisponibilidad como `detector_fault`, fija confianza cero y
emite `ABSTAIN`.

**Validación:** B-188 fue roja antes del parche con el `OperationalError`
contradictorio y verde después, confirmando tanto el error semántico explícito
como ausencia de DB creada. También pasan `test_red_team.py` y el conjunto
relevante: **7/7**. No cambia resultados cuando la DB distribuida está
disponible; cuando falta, hace visible el límite en lugar de permitir una
conclusión limpia sobre análisis semiótico no realizado.

---

## B-189 — el runner canónico podía publicar resultados dentro de la evidencia [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: `--output` tenía autoridad de escritura irrestricta; podía reemplazar o añadir un JSON de resultados dentro del input adquirido. |
| **Archivo** | `vigia/scripts/run_pipeline.py`, `tests/test_b189_pipeline_output_boundary.py`. |
| **Modo** | Pipeline determinista `python3 -m vigia.scripts.run_pipeline --input … --output …`. |
| **Principio afectado** | El resultado derivado debe vivir fuera de evidencia y publicarse atómicamente; una ruta de salida no puede volver al árbol que se está examinando. |

**Observación reproducida:** el runner leía el input y ejecutaba
`Path(output_path).write_text(...)` sin validar, sin crear padre y sin
publicación atómica. Un destino `<evidence>/pipeline-result.json` y un padre
`result-redirect -> <evidence>` fueron escritos con éxito. Inversamente, un
destino externo nuevo fallaba por `FileNotFoundError`. Las tres condiciones
fueron inducidas antes del parche.

**Corrección aplicada:** `run()` valida `--output` con
`validate_external_output_path()`, crea el padre externo con `0750`, vuelve a
validar antes de escribir y usa `atomic_write_text()` para temp+fsync+replace.
El log imprime el destino canonicalizado. La decisión, la canonicalización v1
de compatibilidad y el contenido JSON de una ejecución válida no cambian.

**Validación:** B-189 cubre output directo en evidencia, escape por symlink y
output externo con padre inexistente. Fue roja **3/3** antes del parche y
verde **3/3** después. Además pasan las 23 pruebas de `test_tanda_a_triage.py`:
**26/26**. El cambio impide contaminar adquisición y elimina el fallo espurio
del output externo sin ampliar las conclusiones del pipeline.

---

## B-190 — el logger de ejecución podía alterar evidencia y escapar con `case_id` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: una traza derivada del pipeline podía escribirse en el árbol adquirido o en un destino construido desde una etiqueta de caso. |
| **Archivo** | `vigia/core/execution_logger.py`, `vigia/pipeline/pipeline.py`, `tests/test_b190_execution_logger_output_boundary.py`. |
| **Modo** | Pipeline determinista y cualquier consumidor directo de `VigiaExecutionLogger`. |
| **Principio afectado** | La evidencia es de solo lectura: ni el trail que la describe ni el identificador de caso pueden obtener autoridad de escritura sobre ella. |

**Observación reproducida:** el constructor recibía `output_dir="data/logs"`,
creaba ese path relativo al CWD y concatenaba `case_id` sin tratarlo como un
identificador no confiable. Con `VIGIA_EVIDENCE_DIR=<evidence>` se indujeron
cuatro violaciones antes del parche: (1) `output_dir=<evidence>` creaba el
JSONL dentro de la adquisición; (2) un padre symlink que apuntaba a evidencia
también era aceptado; (3) `case_id="../evidence/escape"` escapaba del
directorio de logs; y (4) iniciar el proceso desde la evidencia hacía que el
default relativo publicara `data/logs` en ese mismo árbol. El logger no cambia
un veredicto, pero sí podía modificar el objeto cuyo análisis pretende dejar
trazado.

**Corrección aplicada:** `case_id` ahora es una etiqueta no vacía sin NUL ni
separadores de ruta. Cuando no se pasa un destino explícito, los logs usan
`VIGIA_EXECUTION_LOG_DIR`, luego `$VIGIA_WORK_DIR/logs`, y finalmente estado
privado XDG; nunca el CWD. El destino final se valida con la frontera común
`validate_external_output_path()` antes y después de crear su padre externo
con modo `0750`. Esa validación rechaza evidencia directa y todo componente
symlink. Se documentó `VIGIA_EXECUTION_LOG_DIR` junto al resto del estado
operativo privado. El logger mantiene el formato JSONL, la cadena de hashes y
el comportamiento de destinos externos legítimos.

**Validación:** las cinco pruebas B-190 fueron rojas antes del fix y verdes
después: evidencia directa, padre symlink, traversal de `case_id`, default
desde CWD de evidencia y output externo permitido. Además pasan
`tests/test_hash_chain_hardening.py` y `tests/test_tanda_a_triage.py`: **55
passed** (una advertencia histórica de timestamp no sellado). La inducción
confirma el cierre de la autoridad de escritura; no afirma atomicidad ante
caída de energía de la secuencia JSONL, que queda fuera de este fix.

---

## B-191 — el generador de execution logs se rompía al encontrar una señal [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de trazabilidad: el modo que debe registrar hallazgos SANS abortaba antes de emitir el primer `FORENSIC_FINDING` cuando el detector devolvía una señal normal. |
| **Archivo** | `vigia/scripts/generate_execution_log.py`, `tests/test_b191_execution_log_generator_schema.py`. |
| **Modo** | Generador JSONL individual/batch de Agent Execution Logs. |
| **Principio afectado** | Un trail forense debe consumir el contrato canónico del detector y conservar pesos exactos, no inventar un valor de display ni fallar en el camino con evidencia. |

**Observación reproducida:** `SemioticDetectorV2.analyze()` emite cada match
con `weight_num` y `weight_den`, y mantiene `_weight` sólo como display. El
generador pedía en cambio `match["weight"]` con fallback `0.5` y llamaba a
`VigiaExecutionLogger.log_event(pattern_weight=...)`; esa firma no existe.
Una inducción mínima con un match válido `7/10` produjo exactamente
`TypeError: ... unexpected keyword argument 'pattern_weight'`. Por tanto un
caso sin matches podía aparentar funcionar, mientras que el camino que debía
registrar un hallazgo no terminaba su log ni su veredicto final.

**Corrección aplicada:** el generador consume exclusivamente
`weight_num`/`weight_den`, los valida como enteros racionales no negativos con
denominador positivo, calcula la confianza de display mediante aritmética
entera y llama a la firma existente `pattern_weight_num` /
`pattern_weight_den`. Un schema de detector no canónico ahora falla con un
error explícito en vez de registrar un 50% inventado. La decisión del motor
no se modifica: sólo se restaura el consumidor de su output y su trazabilidad
exacta.

**Validación:** la prueba B-191 usó el mismo schema canónico del detector, fue
roja antes (`TypeError`) y verde después; verifica que el JSONL conserva
`_pattern_weight = 7/10` en su representación canónica. Junto con B-190 y el
hardening de cadena pasan **33 tests**. No se afirma que este generador sea el
autoridad de veredicto: su función es registrar fielmente la salida ya
producida por el detector y la capa de decisión.

---

## B-192 — el script de execution logs reintroducía el default inseguro [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad operacional: aunque el logger central ya tenía un default privado (B-190), el script que lo invoca le imponía el antiguo `data/logs` relativo al CWD. |
| **Archivo** | `vigia/scripts/generate_execution_log.py`, `tests/test_b192_execution_log_script_output_boundary.py`. |
| **Modo** | Generador standalone individual y batch de Agent Execution Logs. |
| **Principio afectado** | Una frontera de escritura sólo vale si cada entry point conserva sus defaults seguros; un wrapper no puede recuperar autoridad ambiental que el componente protegido ya había eliminado. |

**Observación reproducida:** una ejecución real del script con
`VIGIA_WORK_DIR=<tmp>` siguió publicando en `data/logs/` del checkout porque
`process_case(..., output_path=None)` sobrescribía el default del logger. La
inducción desde un CWD igual a `VIGIA_EVIDENCE_DIR` fue rechazada por B-190,
evitando contaminar evidencia, pero el modo no podía completar aunque tenía un
work directory válido. Esto refutó la hipótesis de que corregir sólo el
constructor cubría todos los entry points.

**Corrección aplicada:** `process_case` y `process_dataset` aceptan un
`output_dir` opcional; al no recibirlo delegan al default privado de
`VigiaExecutionLogger`. El CLI deja de preseleccionar `data/logs`, propaga
`--output-dir` al batch y describe el orden de destinos seguro. Un `--output`
o `--output-dir` explícito sigue siendo posible, pero queda sujeto a la misma
validación contra evidencia y symlinks de B-190.

**Validación:** B-192 fue roja antes por `SecurityError` al iniciar desde un
CWD de evidencia pese a tener `VIGIA_WORK_DIR`; queda verde y genera
`<work>/logs/B192-001_execution.jsonl` sin crear nada en evidencia. Con B-190,
B-191, hardening de cadena y triage pasan **57 tests**. El test de integración
real posterior confirmó que un match del detector produce el JSONL en el work
directory, no en el checkout.

---

## B-193 — el adaptador de casos podía sobrescribir evidencia con su export [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad forense: el CLI del adaptador aceptaba cualquier segundo argumento como output y lo abría con `"w"`, incluida evidencia adquirida. |
| **Archivo** | `vigia/tools/vigia_case_adapter.py`, `tests/test_b193_case_adapter_output_boundary.py`. |
| **Modo** | Conversión directa `python3 vigia/tools/vigia_case_adapter.py <caso.json> [output.json]`. |
| **Principio afectado** | El adaptador lee evidencia para derivar señales; su JSON de salida no puede recibir autoridad para alterar el input ni ser publicado parcialmente. |

**Observación reproducida:** con un caso mínimo externo y
`VIGIA_EVIDENCE_DIR=<evidence>`, la invocación CLI con
`<evidence>/derived.json` terminaba con exit `0` y creaba el archivo dentro de
evidencia. No había validación de path, control de symlink, creación segura de
padres ni publicación atómica. Es una ruptura de separación source/derived,
no una modificación de la lógica de adaptación.

**Corrección aplicada:** se incorporó `save_signals()`: valida el destino con
la frontera compartida antes y después de crear el padre externo `0750`, y
publica el JSON mediante `atomic_write_text()` (tempfile, fsync, replace y
fsync del directorio). El CLI usa esa función y reporta el path canonicalizado.
Los exports externos legítimos mantienen el mismo contenido JSON.

**Validación:** B-193 fue inducido antes mediante la escritura CLI directa.
Después, sus tres tests verifican rechazo dentro de evidencia, rechazo a través
de symlink y export externo canónico conservando el contenido. Con B-190–B-192
y hardening de cadena pasan **37 tests**. La validación protege la autoridad de
escritura; no pretende resolver por sí sola una sustitución hostil de directorio
entre operaciones de filesystem fuera del modelo de permisos del proceso.

---

## B-194 — la API validaba el pathname de un caso pero abría ese pathname después [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de integridad y alcance forense, condicionado a que un actor pueda mutar concurrentemente el directorio de casos. No supone que un cliente HTTP, por sí solo, tenga permiso de escritura en el checkout. |
| **Archivos** | `vigia/api_case_paths.py`, `vigia_api.py`, `vigia/vigia_api.py`, `tests/test_b194_api_case_snapshot_race.py`, `tests/test_vigia_api_boundaries.py`. |
| **Modo** | FastAPI `POST /analyze/path`, ambas rutas de importación documentadas. |
| **Principio afectado** | La selección de evidencia sólo es válida si el objeto que se analiza es el mismo que fue autorizado. `lstat()` seguido de `open(path)` no preserva esa identidad frente a sustitución entre operaciones. |

**Observación reproducida:** `resolve_case_path()` ya rechazaba rutas absolutas,
traversal y symlinks que existieran durante su inspección. Sin embargo devolvía
un `Path` y el pipeline lo abría más tarde por nombre. En un directorio temporal
controlado, se autorizó `data/cases/allowed.json`, se reemplazó esa hoja por un
symlink a `outside/case.json` y un `open()` ordinario leyó el JSON externo. La
inducción confirma una carrera de pathname; no afirma exfiltración de un secreto
arbitrario, porque el pipeline requiere JSON con forma de caso y la exposición
depende de la configuración de narración y despliegue.

**Corrección aplicada:** `snapshot_case_file()` conserva la validación léxica y
de archivo regular, pero su apertura autoritativa parte de un descriptor del
repositorio y recorre `data/cases` o `cases` componente por componente mediante
`dir_fd`, `O_DIRECTORY` y `O_NOFOLLOW`. Un symlink de hoja o de directorio que
aparezca después de validar falla cerrado. El descriptor de archivo ya ligado se
copia a un temporal privado con `fsync`; tanto el pipeline determinista como la
narración opcional consumen esa instantánea y nunca reabren el pathname aportado
por el cliente. La plataforma que no ofrece estas primitivas rehúsa el caso en
vez de volver silenciosamente al patrón vulnerable.

**Validación:** los tests B-194 fueron rojos antes (la primitiva no existía) y
verdes después. Simulan, por separado, sustitución de la hoja y del directorio
raíz tras la resolución inicial; ambos producen `CasePathError`. El contrato de
endpoint verifica también que las dos APIs devuelven 404 sin invocar el pipeline.
La prueba manual aislada obtuvo `SWAP_REJECTED` con el `ELOOP` esperado. Con las
regresiones de frontera y paridad API pasan **28 tests**. Una escritura directa
de contenido regular *dentro* de un case root que el atacante ya controla sigue
fuera de esta defensa: eso es autoridad de modificación de evidencia, no una
evasión de confinamiento de path.

---

## B-195 — el adaptador JSON presentaba la narrativa del caso como razonamiento del motor [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 epistemológico y de trazabilidad: una afirmación escrita por quien construyó el caso podía quedar sellada y visualizada como si la hubiera deducido el selector determinista. |
| **Archivos** | `sift_orchestrator.py`, `vigia_agent.py`, `tests/test_b195_case_description_provenance.py`. |
| **Modo** | Agente determinista sobre caso EBS JSON; afecta el bundle, su narrativa y el indicador `analytical_reasoning`. |
| **Principio afectado** | El contexto de escenario puede conservarse, pero su procedencia y falta de autoridad analítica deben sobrevivir cada transformación y handoff. La presentación no puede elevar un claim a evidencia. |

**Observación reproducida:** `_analyze_ebs_json()` era label-blind para el
scorer, pero copiaba `case_data["description"]` literalmente a
`abduction["narrative"]`. Luego `vigia_agent._generate_narrative()` lo imprimía
bajo **“Razonamiento del motor abductivo”** y `_seal_bundle()` lo usaba para
declarar `analytical_reasoning=True`. La inducción B-195 entregó una sola señal
de memoria y un `description` con la afirmación no respaldada “exfiltration was
completed and the operator was physically identified”; antes del fix esa frase
aparecía como razonamiento del motor aunque no estuviera en ningún artefacto ni
en el resultado del scorer. `VIGIA-FN-003` manifestó el mismo defecto: su
escenario decía que la exfiltración ocurría dentro de TLS, pero el motor sólo
había probado una fractura de inyección y concluía `SUSPICION` por falta de
corroboración.

**Corrección aplicada:** el campo `abduction.narrative` se construye ahora
únicamente a partir de la selección label-blind y de `motor_reason`, con
`narrative_provenance="deterministic_motor_selection"`. El texto de entrada se
preserva, sin alterar el score, como `scenario_context` con
`scenario_context_provenance="case_description_unverified"`; el reporte del
agente lo muestra en una sección separada, **“CASE CONTEXT (UNVERIFIED INPUT —
NOT ANALYTICAL EVIDENCE)”**. El modo `legacy` queda explícitamente rotulado como
reproducción, no como razonamiento nuevo.

**Validación:** las dos pruebas B-195 fueron rojas antes: la claim inyectada
ocupaba el campo de razonamiento y aparecía antes de cualquier contexto
etiquetado. Después quedan verdes y prueban que el relato del selector contiene
su razón propia, que el input se conserva con procedencia no verificada y que
el agente no mezcla ambas secciones. Junto con B-163, `fase1_resolve` y la suite
de robustez de narrativa pasan **67 tests**. Una ejecución directa de FN-003
conserva `SUSPICION` y su misma razón de gate; la frase sobre TLS ya no aparece
en el bloque de motor. Esta corrección no convierte descripciones de artefactos
en datos inocuos: esas descripciones siguen siendo observaciones del artefacto
y deben tener su propia procedencia de adquisición para servir como evidencia.

---

## B-196 — `VIGIA-FN-003` se mantenía como deuda de detector aunque el detector ya estaba activo [RESUELTO — reclasificado, Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de gobernanza de corpus: el backlog atribuía un `SUSPICION` a una capacidad ausente, lo que invitaba a retocar el scorer para forzar una conclusión que la evidencia actual no corrobora. |
| **Archivos** | `BUGS_PENDIENTES.md`, `docs/XFAIL_REDUCTION_STRATEGY_20260717.md`; observación en el bundle sellado `results/agent_batch/VIGIA-FN-003_agent_bundle.json`. |
| **Modo** | Agente determinista / motor EBS. |
| **Principio afectado** | Un veredicto menor que la etiqueta de un escenario no prueba ausencia de detección. La taxonomía de fallos debe distinguir detector, gate de corroboración y expectativa histórica. |

**Observación reproducida:** el bundle de `VIGIA-FN-003` no omite la señal de
memoria: CAIE registra la fractura viva `PROCESS_INJECTION_ANTIFORENSIC`, de
severidad `0.85`, y el boost exacto `0.3825`. Una reejecución actual del modo
`motor` devuelve `SUSPICION` con score `0.6022` y explica que, aunque supera
el umbral de `MALICE`, no abre una rama de corroboración: las dos observaciones
duras pertenecen a una sola colección/dominio de memoria. Al retirar metadata
de inyección el boost desaparece; al retirar el mismatch de parent process el
caso sigue siendo `SUSPICION`. El detector, por tanto, sí participa y altera
materialmente el resultado.

**Contraste:** `VIGIA-CAN-042`, con la misma clase de fractura, alcanza
`MALICE` (`0.6524`) porque aporta cuatro artefactos repartidos entre dos
colecciones de evidencia y satisface B-068. No es evidencia de que FN-003
necesite un detector RWX nuevo, sino del límite deliberado que evita contar
dos observaciones del mismo volcado como dos fuentes independientes.

**Resolución:** se retira FN-003 de la deuda de detector y se reclasifica como
disputa entre la etiqueta histórica `MALICE` y la suficiencia de la adquisición
disponible. La etiqueta del escenario se conserva por trazabilidad: no se
reescribe el corpus para hacer coincidir el motor. Elevarlo requeriría nueva
corroboración independiente (por ejemplo identidad, red, pago o adquisición
física), no aumentar pesos ni añadir una regla que ya existe. B-195 además
separa la frase narrativa sobre exfiltración TLS del razonamiento sellado: no
puede usarse como la corroboración que falta.

---

## B-197 — `run_vigia()` descartaba señales malformadas y sellaba la decisión parcial [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de integridad de entrada y degradación honesta: un entry point público podía transformar evidencia suministrada pero inválida en ausencia de evidencia sin que el bundle pudiera atestiguarlo. |
| **Archivo** | `vigia/pipeline/pipeline.py`, `tests/test_b197_pipeline_signal_boundary.py`. |
| **Modo** | `run_vigia()` (CLI/Python API e Integration Bridge). |
| **Principio afectado** | La frontera debe rechazar una solicitud incompleta antes de decidir; no puede conservar sólo las partes que lograron parsear y presentar el resultado como análisis del conjunto aportado. |

**Observación reproducida:** `_signals_from_dicts()` envolvía cada construcción
de `SignalOutput` en `except Exception`, emitía un warning y continuaba. Con
una señal válida seguida por `{"z_score": 9.0, "confidence": 1.0}` sin
`tool_name`, el helper retornaba una señal en vez de fallar; `run_vigia()`
entonces entraba a `run_full()` y sellaba un resultado para el subconjunto. El
bundle no contiene el conteo de objetos rechazados, su índice ni la causa de
conversión, de modo que un lector no podía distinguir «una evidencia» de «dos
evidencias, una perdida en la frontera». La variante con sólo la señal inválida
terminaba en error más tarde por cero señales, pero la variante mixta ocultaba
el problema.

**Corrección aplicada:** la frontera exige que `signals_data` sea una lista y
que cada entrada sea un objeto. Si la construcción o validación de
`SignalOutput` falla, `_signals_from_dicts()` lanza `ValueError` con el índice
`signals_data[i]` y encadena la causa original. `run_vigia()` por tanto no
inicia el pipeline, no sella un bundle y no presenta un veredicto parcial. Las
señales válidas conservan el mismo contrato de transporte; no se modificó el
scorer ni se introdujo un fallback de etiqueta.

**Validación:** las dos pruebas B-197 fueron rojas antes: tanto el helper como
`run_vigia()` aceptaban la lista mixta. Después verifican rechazo visible en
ambas fronteras. Junto con las regresiones F0/B-062/B-064 y la integración EBS
pasan **30 tests**. El cambio prefiere un error explícito sobre una abstención
sintética: el operador debe corregir o documentar la evidencia malformada antes
de iniciar otra corrida.

---

## B-198 — se confundía la repetición analítica con el sello de custodia por corrida [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 epistemológico y de verificabilidad: el producto afirmaba que igual input producía el mismo `bundle_hash`, aunque ese hash identifica deliberadamente artefactos de custodia distintos. No alteraba el veredicto ni era indeterminismo del scorer. |
| **Archivos** | `vigia/core/ebs_v1.py`, `vigia/core/bundle_builder.py`, `vigia/pipeline/pipeline.py`, `forensics/verify_ebs_v1.py`, `tests/test_b198_analysis_fingerprint.py`, `README.md`, ambas copias de `VIGIA_ESTADO_TECNICO_ES.md`, `docs/ENGINEERING_DISCIPLINE.md`; `vigia/models/ebs.py` queda explícitamente rotulado como ruta legacy, no como contrato de replay. |
| **Modo** | Pipeline EBS v1, API/CLI `run_vigia()` y verificador stdlib-only. |
| **Principio afectado** | Determinismo no significa borrar identidad ni tiempo de una cadena de custodia. Las dos propiedades deben tener nombres, scopes y verificadores distintos. |

**Observación reproducida:** dos llamadas idénticas a `run_vigia()` conservaron
la misma decisión, posterior, riesgo y proyección de contenido analítico, pero
produjeron distinto `integrity.bundle_hash`. La diferencia se redujo exactamente
a `bundle_id`, `timestamp`, `evidence_graph.generated_at`,
`policy_spec.created_at`, `system_state.timestamp`, `integrity.sealed_at` y el
`bundle_hash` que deriva de esos campos. Es correcto que el sello completo los
cubra: son la identidad y el momento de *esa* corrida. El problema era el claim
contrario en README/estado técnico y su evidencia citada: `tests/check_determinism.py`
ejecuta una herramienta aislada y elimina timestamps antes de hashear; no crea
ni compara bundles EBS. El test histórico T13 sólo lograba hashes iguales
forzando manualmente UUID y todos los timestamps.

**Corrección aplicada:** los bundles nuevos incluyen
`integrity.analysis_fingerprint`, SHA-256 de la proyección analítica canónica
que excluye sólo UUID y metadatos de tiempo por corrida. El `bundle_hash` no se
debilitó ni se reutiliza: sigue sellando el payload completo de custodia. El
pipeline y su CLI exponen ambas huellas. `quick_verify()` y el verificador
independiente re-derivan `analysis_fingerprint` cuando está declarado; si se
altera, fallan. Los bundles históricos que no tienen ese campo siguen siendo
válidos bajo su contrato previo y el verificador lo marca explícitamente como
legacy, no como una falsa comprobación.

**Validación:** la regresión B-198 fue roja antes (no existía la huella y los
dos verificadores aceptaban un digest decorativo). Después prueba: (1) mismo
contenido analítico → mismo `analysis_fingerprint` pero sellos de custodia
distintos; (2) corrupción del fingerprint rechazada por ambos verificadores;
(3) compatibilidad de un bundle sin ese campo; y (4) exposición por el entry
point público. Con las suites de sellado, contrato del verificador e
integración EBS pasan **25 tests**. La nueva huella no prueba que dos corridas
ocurrieron al mismo tiempo ni reemplaza al `bundle_hash`; prueba sólo que su
proyección analítica declarada coincide.

---

## B-199 — la API devolvía un veredicto del scorer y el hash de otra decisión EBS [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 epistemológico/de interfaz: una respuesta HTTP podía presentar un veredicto forense y un `bundle_hash` válido como si atestiguaran la misma decisión, aunque provenían de dos motores y escalas distintas. |
| **Archivos** | `vigia_api.py`, `vigia/vigia_api.py`, `vigia/core/bundle_builder.py`, `vigia/openai_compat.py`, `tests/test_b199_api_seal_coherence.py`, `KNOWN_LIMITATIONS.md`, estados técnicos EN/ES. |
| **Modo** | FastAPI/OpenWebUI, ambos imports soportados (`vigia_api` y `vigia.vigia_api`); el modo agente y las rutas de submission no fueron alterados. |
| **Principio afectado** | Un sello de integridad sólo puede acompañar la afirmación exacta que contiene. Si dos capas usan semánticas de riesgo diferentes, la interfaz debe exhibirlas como distintas o abstenerse, nunca unirlas por cercanía de nombre. |

**Observación reproducida:** cada wrapper calculaba primero `_vigia_score()` y
devolvía sus campos `verdict`, `score`, `confidence` y `reason`. En paralelo
adaptaba el mismo caso a `SignalOutput` y ejecutaba `VigiaPipeline.run_full()`
solamente para tomar `bundle_hash` y el resultado de `verify_ebs_v1.py`. En
`FP-CULTURAL-CLEAN-001`, por ejemplo, el scorer devolvía `NOISE` con score
`0.0659`, mientras el bundle adjuntado contenía `decision_trace.decision =
REJECT`, riesgo `0.982695` y razón `REJECT_POSTERIOR`. No es una mera
traducción de vocabulario: `NOISE` significa evidencia insuficiente de
intención, mientras `REJECT` EBS expresa alto riesgo de fabricación.

**Causa raíz:** se intentó usar el pipeline EBS como una fábrica genérica de
hashes para el scorer standalone. El adaptador de casos y el pipeline tienen
otra representación de señales y otro modelo de riesgo. Cambiar simplemente a
`build_bundle()` tampoco bastaba: esa función mapeaba `NOISE → ACCEPT` y
`MALICE → REJECT` reutilizando el score compuesto de intención como
`DecisionTrace.risk`. El verificador independiente rechazaba esos bundles: por
ejemplo, `NOISE` con riesgo `0.0659` y epsilon `0.05` debía ser `ABSTAIN`, y
`MALICE` con riesgo `0.823` también debía ser `ABSTAIN` bajo la política EBS.
La coincidencia aparente de cifras no constituía una calibración.

**Corrección aplicada:** los dos wrappers ya no ejecutan un segundo pipeline
para obtener un hash. Sellan exactamente el dict devuelto por `_vigia_score()`
y comprueban antes de responder que `caie_analysis.verdict` dentro del bundle
coincida con el veredicto HTTP. El bundle preserva score, confianza, razón y
veredicto forenses completos; como el scorer standalone no produce un posterior
EBS de fabricación calibrado, su `decision_trace` registra `ABSTAIN`, riesgo y
posterior neutrales `0.5`, y la razón
`STANDALONE_SCORER_UNCALIBRATED_EBS_RISK`. Es una abstención sobre *la capa
EBS*, no una modificación ni downgrade del veredicto forense directo. La API y
la superficie OpenAI-compatible muestran explícitamente `sealed_forensic_verdict`,
`ebs_decision` y `seal_scope=DIRECT_SCORER_ANALYSIS_ONLY`.

**Validación:** la regresión B-199 se escribió roja primero. Construye bundles
standalone controlados `NOISE`, `SUSPICION` y `MALICE`, verifica cada uno con el
verificador independiente y exige que conserve el veredicto forense pero se
abstenga en EBS. Después ejecuta ambos wrappers reales y exige `verify=PASS`,
igualdad entre el veredicto retornado y el sellado, y el scope declarado. Con
las fronteras FastAPI, paridad de imports y suites de sellado/verificador pasan
**50 tests**. Esto no afirma que el pipeline EBS completo sea inválido: afirma
que su decisión no puede utilizarse como prueba del scorer standalone hasta
tener una traducción de artefactos y calibración de riesgo explícitas.

---

## B-200 — la API llamaba `FAIL` a un verificador que no había podido ejecutarse [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de degradación honesta: una configuración `VIGIA_REPO` inexistente o un error de proceso se mostraba al cliente como fallo criptográfico del bundle. |
| **Archivos** | `vigia_api.py`, `vigia/vigia_api.py`, `tests/test_b199_api_seal_coherence.py`. |
| **Modo** | FastAPI/OpenWebUI, ambos imports públicos. |
| **Principio afectado** | Un resultado de verificación sólo puede decir `FAIL` si el verificador ejecutado alcanzó ese resultado. Ausencia de ejecutable, fallo de arranque o salida no reconocible son indisponibilidad operacional, no evidencia de alteración. |

**Observación reproducida:** el entorno tenía `VIGIA_REPO` configurado a un
checkout que ya no existe. Ambos wrappers construían correctamente el bundle,
pero lanzaban `python3 <repo-inexistente>/forensics/verify_ebs_v1.py`. Como la
subproceso devolvía stderr sin la palabra `PASS`, el código respondía
`verify="FAIL — ?"`. Ese texto sugiere que el contenido sellado fue rechazado,
cuando el programa de verificación ni siquiera se abrió.

**Corrección aplicada:** la API comprueba que el ejecutable del verificador
existe, captura errores al iniciar la subproceso y clasifica la salida de forma
explícita. `PASS` y `FAIL` se emiten solamente si el CLI produjo
`Resultado : PASS` o `Resultado : FAIL`; cualquier ausencia, error de arranque
o salida no interpretable se devuelve como `UNAVAILABLE — ?` y se registra en
el log del servidor sin exponer paths ni stderr al cliente. El archivo temporal
del bundle se elimina también si el proceso no logra arrancar.

**Validación:** la prueba nueva fuerza ambos wrappers a usar un `REPO` sin
`forensics/verify_ebs_v1.py`. Era roja antes (`FAIL — ?`) y ahora exige
`UNAVAILABLE — ?`, sin la palabra `FAIL`. La misma suite conserva el caso de
verificación normal `PASS` y los contratos de rutas/compatibilidad OpenAI:
**32 tests** pasan. La configuración rota sigue siendo responsabilidad del
operador; el cambio sólo impide que VIGÍA la convierta en una afirmación forense
falsa.

---

## B-201 — el API aceptaba casos JSON remotos sin límite de tamaño ni cardinalidad [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de disponibilidad: una petición no confiable podía materializar un archivo temporal y despachar al scorer un grafo sintético de tamaño no acotado. No cambiaba por sí misma un veredicto ni afectaba la adquisición local de evidencia. |
| **Archivos** | `vigia/api_payload.py`, `vigia_api.py`, `vigia/vigia_api.py`, `vigia/openai_compat.py`, `tests/test_b201_api_payload_boundary.py`, estados técnicos EN/ES. |
| **Modo** | `POST /analyze/json` y el caso JSON embebido en `POST /v1/chat/completions`, para ambos wrappers públicos. |
| **Principio afectado** | La frontera HTTP debe validar disponibilidad antes de persistir o analizar datos no confiables. Un límite de transporte no sustituye la validación semántica forense ni debe restringir la adquisición local. |

**Observación reproducida:** los dos endpoints aceptaban cualquier diccionario
JSON y el shim OpenAI-compatible lo escribía directamente a un temporal antes
de llamar al pipeline. Con un payload controlado de 1.025 artefactos, ambos
wrappers alcanzaban el scorer; si el request fallaba más tarde, la respuesta
era un error genérico. No existía contrato explícito de bytes ni de
cardinalidad, aunque el corpus versionado alcanza sólo 217.373 bytes y 101
artefactos por caso.

**Corrección aplicada:** `validate_case_payload()` define una frontera común
para los dos wrappers: objeto JSON serializable, máximo 1.048.576 bytes UTF-8
y máximo 1.024 artefactos. Se ejecuta antes de crear un temporal, narrativa o
scoring. `/analyze/json` rechaza con HTTP 422; el contrato compatible con
OpenAI devuelve una explicación de input clara. Los límites aplican sólo a
casos entregados por HTTP: ni la ingestión local, ni artefactos binarios, ni el
motor determinista cambian de alcance o de semántica.

**Validación:** B-201 se escribió roja primero: el request de 1.025 artefactos
alcanzaba el pipeline en ambas rutas. Después exige que los dos wrappers
rechacen antes de escribir o invocar al scorer. Junto con fronteras FastAPI,
paridad de imports y B-199 pasan **36 tests**; `py_compile` y `git diff
--check` también pasan. El umbral es deliberadamente amplio respecto del
corpus, pero explícito y verificable en vez de implícito e ilimitado.

---

## B-202 — `/analyze/path` podía snapshotear un fixture permitido sin límite de bytes [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de disponibilidad: la ruta estaba confinada correctamente, pero un JSON muy grande dentro de un root permitido podía copiarse entero a disco temporal antes de llegar al pipeline. |
| **Archivos** | `vigia/api_case_paths.py`, `tests/test_b202_api_path_snapshot_boundary.py`, estados técnicos EN/ES. |
| **Modo** | `POST /analyze/path` en ambos wrappers FastAPI; no modifica CLI, ingestión ni extracción forense de archivos grandes. |
| **Principio afectado** | Confinar un pathname y sellar el snapshot evita sustitución de evidencia, pero no acota su costo. La misma frontera debe preservar procedencia y disponibilidad. |

**Observación reproducida:** `snapshot_case_file()` abría el descriptor de un
JSON regular bajo `cases/` o `data/cases/` de forma segura y luego lo copiaba
íntegramente con `copyfileobj()`. Un fixture de más de 1 MiB dentro de un root
permitido llegaba a `NamedTemporaryFile`; por tanto una protección contra
traversal/symlinks no impedía una copia temporal no acotada. El mayor fixture
versionado hoy mide 217.373 bytes, de modo que el límite no excluye el corpus
actual.

**Corrección aplicada:** después de `openat` con `O_NOFOLLOW`, VIGÍA verifica
el tamaño del descriptor antes de crear el temporal y rechaza más de 1 MiB con
`CasePathError`. La copia conserva además un contador de bytes: si el inode
crece después del `fstat`, no escribe bytes que excedan el límite y el temporal
incompleto se elimina por la ruta de excepción. La ruta sigue ligada al mismo
descriptor confiable; no se reabre ni se cambia la semántica del caso.

**Validación:** B-202 fue roja primero al demostrar que el fixture sobredimensionado
llegaba a crear un temporal. Ahora exige rechazo previo a ese punto y prueba el
guard de crecimiento post-apertura con un stream de 1 MiB + 1 byte, incluida la
eliminación del temporal parcial que ese stream hubiera creado. Con B-194
(race/symlink), fronteras FastAPI y la regresión nueva pasan **27 tests**;
`py_compile` y `git diff --check` pasan. Este contrato afecta sólo la selección
HTTP de fixtures: un caso local mayor se puede adquirir y analizar por las
rutas forenses/CLI correspondientes, sin ser truncado ni reinterpretado por
la API.

---

## B-203 — la API presentaba un caso permitido rechazado por tamaño como `404` [RESUELTO — Codex 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de degradación honesta: el límite de disponibilidad de B-202 funcionaba, pero la capa HTTP ocultaba su razón bajo la misma respuesta usada para rutas inexistentes o prohibidas. |
| **Archivos** | `vigia/api_case_paths.py`, `vigia_api.py`, `vigia/vigia_api.py`, `tests/test_b203_api_case_limit_contract.py`, estados técnicos EN/ES. |
| **Modo** | `POST /analyze/path`, ambos imports públicos. |
| **Principio afectado** | Una API puede ocultar detalles de paths locales sin convertir una política declarada y verificable en una afirmación falsa de inexistencia. |

**Observación reproducida:** tras B-202, un `data/cases/oversized.json` regular
y permitido se rechazaba antes de pipeline y temporal, pero ambos wrappers
capturaban todo `CasePathError` y devolvían `404 Caso no encontrado`. El mismo
status y texto se usan correctamente para traversal, symlinks y archivos que
no existen, pero no describían el hecho ya comprobado: había un fixture
permitido que excedía el presupuesto documentado.

**Corrección aplicada:** `CaseSnapshotLimitError` especializa el error de path
para el único rechazo de tamaño declarado. Ambos wrappers lo traducen a `422`
con el límite de bytes; los demás `CasePathError` continúan devolviendo el
`404` opaco, por lo que la ruta no se convierte en un oráculo de filesystem.
La separación no modifica el snapshot, los veredictos ni la selección de casos.

**Validación:** B-203 fue roja primero en los dos wrappers (`404`); ahora exige
`422`, el motivo de límite y que el scorer no sea invocado. Junto con B-202,
B-194 y los límites JSON, pasan **29 tests**; `py_compile` y `git diff --check`
pasan.

---

## B-204 — el modo legacy promediaba artefactos normalizados por B-163, no los crudos históricos [RESUELTO — Codex+Claude 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 de reproducción histórica: el modo explícito `VIGIA_EBS_RESOLVE=legacy` existe solo para reproducir bundles pre-B-163, pero su promedio dejó de reproducirlos cuando B-163 normalizó el caso en la frontera del adaptador. |
| **Archivos** | `sift_orchestrator.py`, `tests/test_b204_legacy_avg_raw_reproduction.py`. |
| **Modo** | Solo `VIGIA_EBS_RESOLVE=legacy` (nunca default). El path motor no cambia de valor. |
| **Principio afectado** | Un modo de reproducción histórica que no reproduce la aritmética histórica es una afirmación falsa de fidelidad (§5.3 degradación honesta). |

**Observación reproducida:** para un artefacto legacy sin `raw_score` ni
`prior_trust`, la normalización B-163 sintetiza `raw_score >= 0.05` (clamp
inferior) y `prior_trust` 0.70–0.90 por capa peirceana. El promedio del
adaptador en modo legacy pasaba de `0` (crudo: defaults `0` × `1/2`) a
`17/400` (sintetizado: `0.05 × 0.85`) — un valor que ningún bundle histórico
contiene. `confidence_f` e `is_conclusive` del modo legacy derivan de ese
promedio.

**Corrección aplicada:** `_analyze_ebs_json` conserva `raw_case_data` junto al
caso normalizado y selecciona la fuente del promedio según el modo: artefactos
crudos solo bajo legacy explícito, normalizados para presentación y para el
path motor (donde el promedio es solo informativo — la hipótesis y la
confianza salen de `_resolve_hypothesis`). Una sola aritmética, dos entradas
explícitas.

**Validación:** B-204 fue roja primero contra el código previo (promedio
`17/400` en modo legacy); con el fix exige `0` crudo, verifica que el modo
motor sigue promediando la representación normalizada, que ambos modos
coinciden en casos canónicos (idempotencia del normalizador) y que la
presentación (`signals`) de B-163 no regresa a proyección cruda. La batería
existente de modo legacy/motor (`test_fase1_resolve`, `test_tanda_a_triage`,
`test_b058`, `test_b163`, `test_b166`, `test_b195` — 52 tests) pasa sin
cambios.

---

## B-205 — los escaneos de campos de B-171/B-172 crasheaban ante input degenerado [RESUELTO — Claude 2026-07-21]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de robustez de frontera: `_vigia_score({"artifacts": None})` levantaba `TypeError` en vez de devolver el `ERROR` limpio que el contrato Round 4 garantiza (el scorer nunca crashea por input degenerado). Mismo defecto con `"temporal_violations": None`. |
| **Archivos** | `vigia_scorer.py`, `tests/test_r4_boundaries.py`, `tests/test_hard_gate_severity_shield.py`. |
| **Modo** | Todos los modos que llaman al scorer determinista. |
| **Detectado por** | Corrida de la suite completa previa al merge de la rama `codex` — las baterías dirigidas de cada fix no incluían los contratos Round 4. |

**Observación reproducida:** B-171/B-172 introdujeron escaneos de
`artifacts` y `temporal_violations` (reconstrucción de pares temporales,
retiro de autoridad SU) que corren ANTES de la guarda histórica
`if not artifacts_all: → ERROR` (línea ~644). Un campo presente con valor
`None` — clave existente, así que el default de `.get()` no aplica — llegaba
al `for` y crasheaba. En `main` ambos casos devolvían `ERROR` limpio.

**Corrección aplicada:** coerción `isinstance(list)` de ambos campos
inmediatamente después de leerlos: un no-list cae a `[]`, que aterriza en el
mismo path `ERROR` que `main` producía. Sin cambio de semántica de scoring
para ningún input bien formado.

**Fallout hermano (mismo origen, sin número propio):** el fixture de
`test_hard_gate_severity_shield.py` declaraba `EFFECT_BEFORE_CAUSE` sobre
artefactos sin timestamps; bajo el contrato B-172 eso es una alegación no
verificable → ABSTAIN, y el test de severidad válida fallaba. El fixture
ahora porta timestamps corroborantes (effect < cause), preservando la
intención original del shield: probar la coerción de severidad, no una
alegación inverificable.

**Validación:** rojas primero las tres (`test_artifacts_none`,
`test_temporal_violations_none` nueva, `test_valid_high_severity_still_fires`);
verdes con el fix. Suite completa (`tests/` + `vigia/tests/`, sin
integration) verde antes del merge.

---

## B-206 — el SMS de coordinación de L-041 nunca estuvo en el case JSON de OWL-NEXUS5 [MITIGADO — Claude 2026-07-22]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de completitud de evidencia: el mensaje que el propio escenario fue diseñado para probar (`L-041`, descubierto 2026-06-30) nunca llegó a `data/cases/OWL-NEXUS5-CASE.json` — ningún fix de extractor semántico ni de normalización puede verlo si el artefacto no está en el archivo que Mode 1 lee. |
| **Archivos** | `data/cases/OWL-NEXUS5-CASE.json`, `vigia/pipeline/vigia_integration_bridge.py` (`_LEGACY_TYPE_TO_EVIDENCE`), `tests/test_b206_owl_sms_artifact_present.py`. |
| **Modo** | Solo afecta la lectura de este case JSON específico vía `_analyze_ebs_json`. |
| **Detectado por** | Continuación de la investigación de B-160/B-163/L-041 (bundle NOISE → ABSTAIN de OWL-NEXUS5), sesión 2026-07-22. |

**Observación reproducida:** los tres bundles históricos de OWL-NEXUS5 (ChatGPT,
fallback agent, y el motor re-corrido hoy tras B-163/B-205) coinciden en que
ninguno vio el SMS "Sarah, the delivery is today 7 tonight the confirmation
will come later through pidgin" (+13045184333, `sms._id=6`) ni su respuesta
"Thank you!" (`sms._id=5`). Verificado con `sqlite3` contra
`evidence/owl-2019-nexus5-quick/Agent Data/mmssms.db` (SHA-256
`0bc8bfcb4fbebe9cccc9fd3d37ffad5de7e33b09f3d524c648787dde2bf5fce6`, tablas
`android_metadata`/`sms` íntegras, ambos mensajes legibles). `grep -i
"pidgin\|13045184333"` contra el case JSON no encontró coincidencias: el
mensaje simplemente nunca fue incorporado al archivo, aunque la evidencia
cruda que lo contiene está presente y accesible en el repo desde antes.

**Nota lateral:** el intento previo de Codex de leer esa base con un `for db
in $(find ... -iname '*mmssms*')` sin comillas falló con "unable to open
database file" — no por un problema forense, sino porque el espacio en
`Agent Data/` partió el path en dos palabras por word-splitting de bash. La
base nunca estuvo dañada.

**Corrección aplicada:** se agregaron `ART-021`/`ART-022` (tipo legacy `sms`)
al case JSON con el contenido verificado de `mmssms.db`, y se agregó
`"sms": "sms"` a `_LEGACY_TYPE_TO_EVIDENCE` — antes ausente, así que un
artefacto `type: "sms"` habría caído al fallback `"default"` en vez del
perfil CAIE dedicado (`sms`: spoofability 0.40, ya existente en
`vigia/tools/caie.py`, distinto del de `chat_message`). El `id` legacy
(`ART-021`/`ART-022`) se preserva como `artifact_id` por el mecanismo B-162
ya existente — no fue necesario tocar esa lógica.

**Alcance del extractor semántico (medido, no atacado en esta sesión):**
corriendo `normalize_case_schema` contra los 265 JSON de `data/cases/**`,
**un solo caso** (este) tiene artefactos legacy sin extractor semántico
(`structured_content_without_semantic_extractor`) — los 20 originales, y
ahora también los 2 SMS nuevos (siguen sin contribuir score real más allá
del piso `raw_score=0.05`; el motor sigue en `ABSTAIN` honesto, ver B-160).
Generalizar ese extractor (alcance ampliado de L-041) queda pendiente,
deliberadamente no atacado aquí — bajo riesgo de calibración dado el
alcance medido, pero requiere el protocolo dry-run + adversarial completo
antes de cablearlo al scorer.

**Hallazgo lateral no atacado:** `PrefetchAnalyzer._parse_pf()`
(`vigia/sift/prefetch_analyzer.py`) reconoce la firma `MAM\x04` (Win10+
comprimido) pero nunca la descomprime — devuelve `last_execution_time`
fijo en `"unknown"` y `run_count=1` fijo para *todo* prefetch moderno, no
solo Pidgin. Confirmado con `xxd` sobre los tres `.pf` de Pidgin en
`evidence/owl-2019-hd1-windows/prefetch/`. Esto bloquea cualquier
correlación temporal entre la ejecución de Pidgin y el SMS de confirmación
en este caso, y probablemente afecta a todo el corpus con evidencia
Prefetch Win10+. No tiene número de bug propio todavía — requiere
descompresión XPRESS Huffman + parseo del formato binario real de
Prefetch; es un esfuerzo de implementación mayor, deliberadamente fuera de
alcance de esta sesión.

**Validación:** `tests/test_b206_owl_sms_artifact_present.py` — 3 tests:
mapeo legacy `sms`→`sms` (no colapsa a `chat_message`/`default`), presencia
de los dos artefactos SMS con su contenido exacto, y supervivencia del
`artifact_id` tras `normalize_case_schema`. Suite completa (`tests/` +
`vigia/tests/`, sin integration): **1848 passed** (+3 sobre el estado
post-merge de la rama codex), 0 failed.

---

## B-207 — extractor semántico de coordinación/transacción: candidato diseñado, NO cableado [MEDIDO, NOT APPLIED — Claude 2026-07-22]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 — el gap (B-160/B-206) sigue produciendo `ABSTAIN` en el único caso afectado. No es P1 porque el motor ya no miente (NOISE); ABSTAIN es honesto. |
| **Archivos** | `vigia/tools/coordination_language.py` (nuevo, no cableado), `scripts/dryrun_coordination_language.py` (nuevo), `tests/test_b207_coordination_language_detector.py` (nuevo). **`vigia_scorer.py` y `vigia_integration_bridge.py` NO se tocaron.** |
| **Modo** | Ninguno — el detector no participa de ningún pipeline de scoring. |
| **Detectado por** | Continuación directa de B-206/L-041, sesión 2026-07-22. |

**Por qué NO se cableó:** el precedente explícito de este repo para calibrar
cualquier parámetro o regla nueva del scorer es L-033 (gamma de event logs,
`docs/A3_EXPERIMENT_DESIGN.md`): exige **≥20 señales, ≥3 casos por
polaridad, ambas polaridades representadas**, con 5 gates (signal-level,
corpus A/B, invariantes, LOCO stability, diagnóstico). L-033 mismo sigue
`NOT APPLIED` por no alcanzar ese mínimo con 7 señales de una sola
polaridad. Medido para este candidato: **1/265 casos** del corpus
(`data/cases/**`) tiene artefactos legacy con `content` rico sin extractor
semántico (B-160), y **cero** son casos negativos conocidos para esta clase
de contenido. Cablear una regla de keywords/regex al scorer con un solo
caso positivo y cero negativos reales sería exactamente el error que L-033
ya bloqueó — y el propio L-041 advierte contra un set genérico de
precio/hora/ubicación por el mismo riesgo de falso positivo.

**Diseño del candidato:** regla deliberadamente angosta, no el set genérico
que L-041 desaconseja. Flaggea un texto SOLO si menciona un canal de
confirmación secundario ("confirmation will come through X", "message me
on X to confirm") **Y** hace un compromiso concreto de entrega/horario
("today"/"tonight"/hora explícita + verbo de entrega) **en el mismo
mensaje**. Exigir ambas condiciones a la vez —siguiendo el mismo principio
de corroboración múltiple que ya usan otros gates de este repo (Daubert
Corroboration Gate, B-172 hard temporal pair)— es lo que evita que
coordinación ordinaria dispare el detector. Estructura calcada de
`ENCRYPTED_APPS` en `android_forensics.py::_analyze_sms()` (dict de
patrones + severidad `Fraction`, sin floats).

**Medición (`scripts/dryrun_coordination_language.py`, exit 0, no altera
nada):** sobre 201 casos / 1035 artefactos reales, matchea exactamente el
artefacto esperado (`OWL-NEXUS5-CASE/ART-021`, el SMS de B-206) y ningún
otro. Sobre un set sintético de 10 mensajes de coordinación ordinaria
(citas, saludos, logística sin transacción) — construido a mano porque el
corpus no tiene negativos reales para esta clase de contenido — **0 falsos
positivos**.

**Qué desbloquearía el cableado:** un corpus con más casos de schema legacy
content-rico, con positivos y negativos reales (no sintéticos) suficientes
para pasar el protocolo G1–G5 de L-033. Hasta entonces, este módulo queda
como candidato medido y reproducible, no como parte del decision path.

**Validación:** `tests/test_b207_coordination_language_detector.py` — 8
tests: verdadero positivo (SMS real de OWL), la respuesta "Thank you!"
sola no matchea, 10 negativos sintéticos, canal solo sin horario no
matchea, horario solo sin canal no matchea, e input degenerado (`None`,
string vacío, no-string) no crashea. Suite completa: **1856 passed**
(+8 sobre B-206), 0 failed. `git diff --stat` confirma que
`vigia_scorer.py`/`vigia_integration_bridge.py` no cambiaron.

---

## B-208 — PrefetchAnalyzer nunca descomprimía el contenedor MAM (Win10+); last_execution_time/run_count eran placeholders fijos [RESUELTO — Claude 2026-07-22]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 de cobertura forense: bloqueaba cualquier correlación temporal sobre prefetch moderno (todo Win10+ del corpus, no solo OWL). No alteraba veredictos — `to_signal()` usa severidad fija por tipo de hallazgo, nunca `run_count`/`last_execution_time`. |
| **Archivos** | `vigia/sift/prefetch_analyzer.py`, `pyproject.toml` (`[project.optional-dependencies].prefetch`), `tests/test_b208_prefetch_pyscca_enrichment.py`. |
| **Modo** | Cualquiera que use `PrefetchAnalyzer.analyze_directory()`/`_parse_pf()` sobre prefetch Win10+ real. |
| **Detectado por** | Continuación de la investigación B-160/B-206 (correlación Pidgin↔SMS en OWL-NEXUS5), sesión 2026-07-22. |

**Observación reproducida:** `_parse_pf()` reconoce la firma `MAM\x04`/`MAM\x03`
(prefetch comprimido Win10+) pero nunca descomprimía el contenedor —
retornaba `last_execution_time="unknown"` y `run_count=1` fijos para
*todo* prefetch moderno, sin excepción. Confirmado con `xxd` sobre los
tres `.pf` de Pidgin en `evidence/owl-2019-hd1-windows/prefetch/`
(firma `MAM\x04` real).

**Decisión de arquitectura (consultada con Anna):** implementar
descompresión XPRESS Huffman + parseo binario SCCA a mano habría
duplicado, sin forma independiente de validarlo, un parser de formato
binario ya resuelto por una librería de referencia. `libscca-python`
(pyscca, proyecto libyal — el que usan las herramientas forenses reales)
ya está instalado en este entorno y funciona correctamente. Es una
extensión compilada (no pip-puro, requiere la librería C `libscca` del
sistema) — se integró como **enriquecimiento opcional con degradación
honesta**: si `pyscca` no está disponible, `_parse_pf()` cae a los
placeholders anteriores (`"unknown"`/`1`) sin romper nada; Mode 1 sigue
offline/cero-dependencias sin este extra. Nuevo extra en `pyproject.toml`:
`pip install vigia[prefetch]`.

**Corrección aplicada:** `_enrich_via_pyscca()` abre el `.pf` con pyscca,
toma el máximo de los hasta 8 slots de `last_run_time` (FILETIME, 100ns
desde 1601-01-01) y lo convierte a ISO 8601 con aritmética entera exacta
(`ticks // 10` → microsegundos, sin float). Si pyscca no está instalado,
o lanza excepción sobre contenido que no puede parsear (p. ej. los
fixtures sintéticos de `tests/test_prefetch_real.py`, que escriben solo
la firma + ceros), `_parse_pf()` sigue devolviendo un `PrefetchRecord`
válido con los placeholders — el chequeo de firma (que decide
`unparsed_files`) es independiente y no cambió.

**Verificado sobre evidencia real** (no versionada en git, local):
`PIDGIN.EXE-86E18E41.pf` reporta ahora `run_count=7`,
`last_execution_time="2017-02-02T21:25:05.097Z"` (antes: `1`/`"unknown"`).
Cruzado contra el SMS de B-206 (recibido 2017-02-01T00:41:15Z, "confirmation
will come later through pidgin"): las otras dos variantes de Pidgin
(`PIDGIN-2.11.0(.EXE/ (1).EXE`) muestran una única ejecución cada una el
mismo día, 2017-02-01 ~17:00-17:06 UTC — **~16 horas después** del SMS,
consistente con "later" tal como dice el mensaje. Esto es corroboración
temporal genuina, no ruido; no se cableó a ningún veredicto en esta sesión
(fuera de alcance — el mismo criterio conservador que B-207).

**Validación:** `tests/test_b208_prefetch_pyscca_enrichment.py` — 9 tests:
conversión FILETIME contra la constante públicamente conocida
`116444736000000000` (época Unix, verificable sin confiar en este código),
selección del slot más reciente entre varios, degradación sin pyscca,
degradación cuando pyscca lanza excepción, todos los slots en cero,
integración completa en `_parse_pf` (con y sin pyscca), y regresión
explícita de que los fixtures sintéticos de `test_prefetch_real.py` (SCCA
válido por firma pero basura interna) siguen parseando. Suite completa
(`tests/` + `vigia/tests/`, sin integration): **1865 passed** (+9 sobre
B-207), 0 failed. `tests/test_prefetch_real.py` (21 tests preexistentes)
sigue en verde sin modificaciones.
## B-211 — el material del signal_id formateaba Fraction con `.8f` — el bridge entero moría en Python 3.11 [RESUELTO — Claude 2026-07-22]

> Renumerado 2026-07-22 desde B-206 (colisión con el batch de Anna del
> 2026-07-21, commit 4ce432445, que ya había asignado B-206/207/208 a
> SMS-OWL/extractor/prefetch-MAM). Precedente de renumerado: L-067.

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 en entornos con el Python pinneado por la CI (3.11): `CaseAdapter.artifact_to_signal()` fallaba para CADA artefacto, `to_signals()` terminaba en `CaseSchemaError` y el bridge de integración (Mode 4/API) quedaba 100% inoperante. En Python ≥ 3.12 el path funciona — por eso el bug fue invisible en las máquinas de desarrollo. |
| **Archivo** | `vigia/pipeline/vigia_integration_bridge.py:755` (`_id_material`) |
| **Modo** | Mode 4 / API (todo lo que entra por `VigiaIntegrationEngine.run_case`) |
| **Detectado por** | Corrida de suite baseline post-merge codex en contenedor Python 3.11.15: `test_b184_keeps_a_valid_bundle_output_external` FAILED — único rojo de 1845. |

**Observación reproducida (Firstness):** `TypeError: unsupported format
string passed to Fraction.__format__` en
`f"{raw_score:.8f}|{z:.8f}"` — `raw_score` y `z` son `Fraction`.
`Fraction.__format__` con presentation types de float existe recién desde
Python 3.12. La CI pinnea 3.11 en `pytest.yml` y `vigia-forensic-ci.yml`.

**Por qué estuvo latente desde el origen (Thirdness):** el `except Exception`
de `artifact_to_signal()` degradaba el crash a "artefacto ignorado", y antes
de B-197 las señales descartadas se sellaban como decisión parcial sin error.
El endurecimiento de B-197 (cero señales → `CaseSchemaError`, no sellar) más
el test de B-184 que ejercita el camino feliz del bridge lo volvieron
visible en la primera corrida sobre 3.11. La línea existe desde el import
inicial del repo (`fb373be`).

**Corrección aplicada:** helper `_decimal_8f()` — réplica exacta del formato
`.8f` de 3.12+ en aritmética `Fraction` pura (`round(abs(x) * 10**8)`,
half-even, sin floats). Los `signal_id` sellados en entornos 3.12+ NO
cambian: misma cadena de material, mismo SHA-256. floats/ints conservan el
comportamiento histórico de `f"{v:.8f}"`.

**Validación:** roja primero (`test_b184_keeps_a_valid_bundle_output_external`
en 3.11), verde con el fix. Tests nuevos:
`tests/test_b211_fraction_format_signal_id.py` (6 — valores exactos, ties
half-even, passthrough float, paridad con `format()` nativo en ≥3.12,
conversión e2e del adaptador, determinismo del ID). Suite completa verde.

---

## B-212 — el workflow pytest.yml no instalaba fastapi: 4 módulos de tests de API sin colectar (deriva S-1, cuarta ocurrencia) [RESUELTO — Claude 2026-07-22]

> Renumerado 2026-07-22 desde B-207 (colisión con el batch de Anna del
> 2026-07-21, commit 4ce432445). Precedente de renumerado: L-067.

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 de CI: el job "VIGÍA Test Suite" (pytest.yml) abortaba la colección con exit 2 — `test_b168_api_contract_parity`, `test_b201_api_payload_boundary`, `test_b203_api_case_limit_contract`, `test_vigia_api_boundaries` (`ModuleNotFoundError: fastapi`). Ningún test corría en ese job. |
| **Archivos** | `requirements.txt`, `.github/workflows/pytest.yml` |
| **Detectado por** | Corrida CI 2026-07-22T22:26Z reportada por Anna. |

**Causa (Thirdness — la clase, no la instancia):** B-168 pinneó `fastapi`
en `requirements-ci.txt` ("Keep it in the minimal CI environment"), pero el
workflow `pytest.yml` instala `requirements.txt` + extras sueltos — nunca
lee `requirements-ci.txt`. Es la MISMA clase de deriva que el contrato S-1
(`tests/test_requirements_ci_contract.py`) cierra para requirements-ci
(defusedxml/T-2, psutil, pytest-cov), en el sentido inverso: el contrato
garantiza un archivo que uno de los dos workflows no instala. `fastapi`
además es dependencia de PRODUCCIÓN (la importan `vigia_api.py`,
`vigia/vigia_api.py` y `vigia/openai_compat.py`), así que su ausencia de
`requirements.txt` era un hueco real de instalación, no solo de CI.

**Corrección aplicada (dos capas):**
1. `fastapi>=0.100.0` agregado a `requirements.txt` (mismo pin que
   requirements-ci) — cierra la instancia y el hueco de producción.
2. `pytest.yml` instala `-r requirements.txt -r requirements-ci.txt` —
   el archivo que el contrato S-1 garantiza completo para la suite pasa a
   ser autoritativo también en este job; los extras sueltos redundantes
   (pytest, pytest-asyncio, pytest-cov, scikit-learn) salen del workflow
   (ya vienen de requirements-ci). `scipy` se conserva explícito (no está
   en ningún requirements y los tests de calibración lo usan).

**Validación:** los 4 módulos de API colectan y pasan en local (3.11.15,
mismo minor que el runner); suite completa verde. La verificación real del
workflow es la próxima corrida CI de este push.

---

## B-213 — `vigia_planner.py` muerto en import: `urllib` sin importar + sanitizador huérfano de la unificación P2-001 [RESUELTO — Claude 2026-07-22]

> Renumerado 2026-07-22 desde B-208 (colisión con el batch de Anna del
> 2026-07-21, commit 4ce432445). Precedente de renumerado: L-067.

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (módulo entero inimportable — `NameError: urllib` al definir `_NoRedirect` a nivel de módulo; cero callers de producción, así que nadie lo notó — misma clase que B-115/B-211) |
| **Archivo** | `vigia/tools/vigia_planner.py` |
| **Detectado por** | Barrido `ruff --select F821` sobre el repo (sesión 2026-07-22), import reproducido: `import vigia.tools.vigia_planner` → `NameError`. |

**Tres defectos concatenados:** (1) `urllib.request`/`urllib.error` usados a
nivel de módulo (guard SSRF del webhook) sin importarse — el módulo nunca
importó en la vida de este repo; (2) la copia local de `_sanitize_llm_input`
referenciaba `_LLM_DANGEROUS_TAGS`/`_CONTROL_CHARS`, movidas a
`vigia/security/security.py` por la unificación P2-001 (Kimi 2026-05-02) —
el docstring de security lo dice textual: "unificada con la versión del
planner"; la copia quedó atrás; (3) `_MAX_INTERPRETATION_LEN` referenciada,
jamás definida.

**Corrección:** imports de `urllib`; copia local eliminada e import del
sanitizador canónico desde `vigia.security` (idéntico: NFKC + tag strip +
control chars + padding guard sin truncado ciego);
`_MAX_INTERPRETATION_LEN = 500` (mismo tope que el fallback del mismo
case-block, conservador contra padding).

**Validación:** import OK, sanitizador canónico verificado, sentinel de
padding activo a 500. Tests: `tests/test_b213_b209_dead_on_call_modules.py`.

---

## B-209 — barrido F821: `analyze_focus()` moría en cada llamada; imports faltantes en redteam temporal y sanitizador judicial [RESUELTO — Claude 2026-07-22]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2/P3 (funciones muertas-al-llamar en módulos sin callers de producción — la clase B-115/B-211/B-213) |
| **Archivos** | `vigia/tools/visible_variables.py`, `vigia/forensics/temporal_forensics_redteam.py`, `vigia/tools/sanitize_judicial.py` |
| **Detectado por** | Mismo barrido `ruff --select F821` de B-213; cada hallazgo reproducido antes de tocar (disciplina audit-before-patch). |

**Corregidos:**
1. `visible_variables.analyze_focus()`: usaba `visible_artifacts` en el
   hash P1 ANTES de construirlo (`UnboundLocalError` reproducido en cada
   llamada) y el rationale citaba `total_rules`, variable local de
   `detect_phase()` inexistente en su scope. Fix: bloque P1 movido antes
   del hash; rationale reescrito sobre el contrato real P0-3 (entero
   0-100), sin inventar un conteo que no tiene. El path vivo del pipeline
   (`get_visible_tools`) nunca pasó por acá — cero impacto en veredictos.
2. `temporal_forensics_redteam`: `statistics.median` y `hashlib.sha256`
   usados sin import — crash al correr el análisis completo.
3. `sanitize_judicial`: `os.urandom` (salt) y `os.chmod` (0600) sin
   `import os` — NameError justo en los pasos de seguridad.

**Hallazgos DESCARTADOS del mismo barrido (falsos positivos / freeze
deliberado — se documentan para que el próximo barrido no los re-abra):**
- `vigia/security/security.py:142,165` y `vigia/forensics/vision_audit.py`
  (`Decimal`, `Image.Image`, `np.ndarray`): anotaciones entre comillas que
  nunca se evalúan en runtime; el código real usa imports lazy / `self.np`.
- `caie_legacy_root.py:1464` (`daubert_note` — el bug B-001 original):
  archivo deliberadamente congelado; `pipeline.py:1321` y
  `bundle_builder.py:463` declaran textual que ningún módulo runtime lo
  importa. "Arreglarlo" rompería la reproducción fiel de bundles
  históricos sellados con ese comportamiento. NO TOCAR.

**Validación:** ruff F821 residual = solo los 7 descartados documentados.
Suite completa 1862 passed, 0 failed.

---

## B-210 — barrido F811: bloque de stubs duplicado en `ebs.py` (trampa de deduplicación) y doble import en `vigia/security/__init__.py` [RESUELTO — Claude 2026-07-22]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 (sin efecto en runtime HOY — pero el duplicado de ebs.py era una trampa activa para la próxima "limpieza") |
| **Archivos** | `vigia/models/ebs.py`, `vigia/security/__init__.py` |
| **Detectado por** | Mismo barrido ruff de B-213/B-209, señal F811 (redefiniciones). |

**ebs.py:** las tres clases stub (`AbductionTrace`,
`PolicyStabilityController`, `SelfAdaptiveRiskPolicy`) estaban definidas
DOS veces, en bloques consecutivos. En Python gana la última definición —
y la diferencia importa: el `SelfAdaptiveRiskPolicy` del primer bloque NO
tenía los aliases `lambda_t`/`gamma_t` que `pipeline.py` y
`risk_bounded_layer.decide()` sincronizan (`self._policy.lambda_t`). La
trampa: el primer bloque parecía el canónico (mejores docstrings) y el
segundo parecía la copia — quien "deduplicara" borrando el segundo rompía
el pipeline en silencio. Eliminado el primer bloque (sombreado, jamás
efectivo); verificado que las definiciones vigentes son idénticas o
superconjunto, aliases presentes post-fix.

**security/__init__.py:** dos bloques de import casi idénticos con el
`__all__` atrapado entre ambos; el segundo agregaba `_sanitize_llm_input`
que el `__all__` no listaba. Consolidado en un bloque único; el conjunto
de nombres importables no cambia (verificado).

**No tocados (F811 restantes, cosméticos y de bajo valor/riesgo):**
`forensic_reporter.py:707` (re-import local de `canvas` ya guardado),
`vigia_sift_bridge.py:2935` (re-import local de `timezone`).

**Validación:** ruff F811/F821 limpio en ambos archivos; aliases
`lambda_t`/`gamma_t` verificados; suite completa 1862 passed, 0 failed.

## B-217 — `_compute_majority` pesaba los votos con la escala de alarma: BENIGN nunca podía ganar una mayoría, y la cadena dissent→ESCALATE estaba muerta de punta a punta [RESUELTO — Claude 2026-07-25]

| Campo | Valor |
|-------|-------|
| **Severidad** | P1 (garantía documentada del sistema, inexistente en el pipeline vivo). Origen: auditoría "Ronda 2" (metodología A-D-I, ver nota de proceso al final de este bloque), hallazgo F1. |
| **Archivo** | `vigia/core/dissent_report.py` (`_compute_majority`, línea ~132). |
| **Función** | `_compute_majority(opinions)`. |
| **Líneas originales** | `weight = op.confidence * _SEVERITY_WEIGHT[op.verdict]` dentro del loop de acumulación de `vote_counts`. |
| **Commit fix** | `e7efacb` (rama `claude/mcp-security-followup-30502`). |
| **Detectado en** | Auditoría "Ronda 2" (invariantes epistemológicos), re-verificada contra el archivo vivo antes de aplicar el fix. |

### Descripción

`_SEVERITY_WEIGHT` es una escala de ALARMA (`MALICIOUS=1.0, SUSPICIOUS=0.5,
BENIGN=0.0, ABSTAIN=0.0`), correctamente usada en otra parte de este mismo
módulo (línea ~244) para puntuar cuán alarmante es una opinión que
**disiente** de la mayoría. `_compute_majority` reutilizaba esa misma tabla
para pesar el voto de cada módulo hacia la mayoría — no solo para puntuar
alarma. Con `_SEVERITY_WEIGHT[BENIGN] = 0`, el voto de cualquier módulo que
opinara BENIGN pesaba matemáticamente cero, sin importar cuántos módulos
opinaran así ni con qué confianza.

Cadena causal completa, verificada eslabón por eslabón contra el código vivo:

1. `_SEVERITY_WEIGHT[BENIGN] = 0` → los votos BENIGN pesan cero →
   `vote_counts[BENIGN]` se queda en 0 sin importar cuántos módulos votaron
   así. Si **todos** los módulos opinan BENIGN, `total = sum(vote_counts.values())`
   colapsa a 0, y `_compute_majority` cae en el fallback de "no hay votos" y
   devuelve `(ABSTAIN, 0)`.
2. Ejecutado (inducción): 10 módulos opinando BENIGN unánimemente al 90% de
   confianza produjeron `majority_verdict=ABSTAIN`, `consensus=0%`, y los 10
   fueron reportados individualmente como "disidentes" de una mayoría que
   nunca se calculó de verdad.
3. `_is_suspicious_consensus` exige `majority == BENIGN` para activarse — con
   el bug, esa rama era código muerto por construcción: BENIGN jamás podía
   llegar a ser la mayoría calculada.
4. Dos hechos adicionales, confirmados por separado, no arreglados por este
   fix (verdaderos antes y después): `generate_dissent_report()` tiene cero
   *callers* en todo el repositorio (grep exhaustivo, no solo tests), y su
   consumidor nominal — el chequeo "Check 2: Specialist dissent → ESCALATE"
   de `QuadripartiteClassifier` en `vigia/verdict/quadripartite.py` — tiene un
   único *caller* de producción (`vigia_scorer.py`, línea ~499) que pasa
   `dissent_info={}` **hardcodeado**, así que `escalation_required` nunca
   puede llegar a ese chequeo aunque este fix esté aplicado.

### Impacto

La garantía estrella documentada en el docstring del módulo — *"9 módulos
dicen BENIGN + 1 módulo behavioral dice MALICE = escalación requerida"* — no
existía en el pipeline vivo. Existía en tests (los que se agregaron recién,
ver abajo) y en la documentación, pero no en ningún camino de ejecución real,
porque además el módulo no tiene *callers*. Ante un perito o un juez, un
sistema que promete una propiedad que su código de producción no ejecuta es
peor que uno que no la promete: la brecha entre lo documentado y lo real es,
en sí misma, un defecto de admisibilidad Daubert.

### Fix aplicado

Cambiar el peso de cada voto de `op.confidence * _SEVERITY_WEIGHT[op.verdict]`
a `op.confidence` solo. La pregunta que responde `_compute_majority` es "¿qué
votó cada módulo, ponderado por su propia confianza en ese voto?" — una
pregunta ortogonal a cuán alarmante es ese veredicto. El otro uso de
`_SEVERITY_WEIGHT` (puntuar la alarma de una opinión que sí disiente, línea
~244) queda intacto porque ahí la semántica de "escala de alarma" es
correcta.

Verificado empíricamente antes de escribir el fix, con tres escenarios
(unánime BENIGN, el escenario insignia de 9 BENIGN + 1 especialista
MALICIOUS, y una mayoría MALICIOUS genuina como control de que los caminos
no afectados no cambiaran), y fijado como test permanente en
`tests/test_dissent_report_majority.py` (el módulo no tenía ningún test
antes de este fix). Suite completa corrida antes y después: 1969 passed, 191
skipped, 29 xfailed — cero regresiones.

**Decisión pendiente (NO tomada en este fix):** este fix restaura la
corrección interna del módulo, pero no lo cablea al pipeline vivo. Falta
decidir entre (a) cablear `generate_dissent_report()` al pipeline real
(reemplazando el `dissent_info={}` hardcodeado en `vigia_scorer.py:499` por
un llamado real, alimentado con `ModuleOpinion`s de los módulos
especialistas), o (b) declarar el módulo experimental/dormido y ajustar
cualquier promesa del README en consecuencia. Ninguna de las dos opciones se
implementó todavía.

## B-219 — El *reason* del override CRITICAL por `ECO_SEMIOTIC_COLLISION` nunca nombraba la colisión, solo el MI (que podía estar en 0.000) [RESUELTO — Claude 2026-07-25]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (ataque contra el auditor, no contra el detector — el veredicto era correcto, la explicación no). Origen: auditoría "Ronda 2", hallazgo F3. |
| **Archivo** | `vigia/core/decision_layer.py` (`RiskBoundedDecisionLayer._generate_reason`, línea ~98). |
| **Función** | `_generate_reason(self, mi, level, fsv)`, llamada desde `decide()`. |
| **Líneas originales** | `_generate_reason` recibía `mi` y `level` pero nunca `has_collision`; para `level == "CRITICAL"` siempre devolvía el texto `"MI crítico ({mi_str})..."`, sin importar si el CRITICAL vino de `mi >= self.high` o del override `has_collision`. |
| **Commit fix** | `056977e` (rama `claude/mcp-security-followup-30502`). |
| **Detectado en** | Auditoría "Ronda 2", confirmado como CODE FACT (el string `"ECO_SEMIOTIC_COLLISION"` no aparecía en ninguna rama de `_generate_reason`) además de por inducción ejecutada. |

### Descripción

`decide()` calcula `has_collision = "ECO_SEMIOTIC_COLLISION" in critical_patterns`
y decide `level = "CRITICAL"` si `has_collision or mi >= self.high` — el
override es independiente de la magnitud de `mi`. Pero `_generate_reason(mi,
level, fsv)` nunca recibía `has_collision`, así que para cualquier
`level == "CRITICAL"` siempre atribuía el veredicto a que "MI crítico
({mi_str})", incluso cuando `mi` estaba en 0.000 y el verdadero disparador
fue la colisión semántica.

Ejecutado: `MI = 1/100 (0.010)` + `critical_patterns=["ECO_SEMIOTIC_COLLISION"]`
→ `alert_level = "CRITICAL"` (correcto) con
`reason = "MI crítico (0.010). ... Escalamiento inmediato requerido."` — un
perito leyendo solo el *reason* (no el metadata crudo) concluiría que el MI
fue el disparador. No lo fue; fue la colisión.

### Impacto

El veredicto (`CRITICAL`) siempre fue correcto — este no es un bug de
detección, es un bug de narrativa: la misma clase de "ataques contra el
auditor" identificada antes en esta rama (ver el fix de orden de
presentación narrativa en CAIE, commit `a0ebd5c`). Un perito o juez que
audite el caso por su explicación textual, sin cruzar el metadata crudo,
llegaría a una conclusión técnica incorrecta sobre qué produjo el
CRITICAL — exactamente el escenario que el marco de "ataques contra el
auditor" de esta sesión fue diseñado para cazar.

### Fix aplicado

Recomputar el mismo chequeo `has_collision` dentro de `_generate_reason`, a
partir de datos ya disponibles en su parámetro `fsv`
(`meta.get("critical_patterns", [])`) — sin necesidad de agregar un
parámetro nuevo, porque `_generate_reason` ya recibe el mismo `fsv` del que
`decide()` deriva `has_collision`. Para `level == "CRITICAL" and has_collision`,
el mensaje ahora nombra explícitamente `ECO_SEMIOTIC_COLLISION` como override
independiente del MI; para `level == "CRITICAL"` sin colisión, el mensaje
original ("MI crítico...") queda sin cambios.

Test agregado: `test_critical_override_reason_names_the_collision_not_just_mi`
en `tests/test_evidence_aggregator.py`, hermano del test preexistente
`test_critical_override_eco_semiotic_collision` (que solo verificaba
`alert_level`, nunca el texto del *reason*). Suite del área (38 tests:
`test_evidence_aggregator.py` + `test_red_team.py` + `test_h27_internal_drift.py`)
verde antes y después.

## B-222 — `.env.example`: nombre de variable de override de hash CLIP incompleto y default de `VIGIA_STRICT_MODEL_CHECK` invertido respecto al código [RESUELTO — Claude 2026-07-25]

| Campo | Valor |
|-------|-------|
| **Severidad** | P4 (deriva documentación/código, cero impacto en veredictos sellados — pero silenciaba un override de seguridad y bajaba un default seguro). |
| **Archivos** | `.env.example` (reescrito completo, traducido al inglés en el mismo commit); `vigia/forensics/vision_audit.py` (comentarios en líneas ~78 y ~94). |
| **Función** | `_load_clip_model_hashes()` (deriva el nombre de la variable de override por modelo); `_STRICT_MODEL_CHECK` (lectura del default). |
| **Líneas originales** | Comentario `VIGIA_CLIP_HASH_VIT_B_32` (sin `_PT`); `.env.example` con `VIGIA_STRICT_MODEL_CHECK=false`. |
| **Commit fix** | (rama `claude/mcp-security-followup-30502`, mismo commit que la actualización de `.env.example`). |
| **Detectado en** | Continuación de la auditoría "Ronda 2" — encontrado incidentalmente mientras se relevaban todas las variables `VIGIA_*` leídas en vivo para actualizar `.env.example`, verificado por ejecución antes de documentarlo. |

### Descripción

Dos discrepancias independientes entre lo documentado y el comportamiento real:

1. **Nombre de variable incompleto.** `_load_clip_model_hashes()` deriva el
   nombre de la variable de override por modelo como
   `"VIGIA_CLIP_HASH_" + filename.replace("-","_").replace(".","_").upper()`.
   Para `"ViT-B-32.pt"` eso da `VIGIA_CLIP_HASH_VIT_B_32_PT` — confirmado por
   ejecución directa. El comentario del propio módulo (línea ~78) y el
   `.env.example` anterior documentaban `VIGIA_CLIP_HASH_VIT_B_32`, sin el
   `_PT` de la extensión. Un operador que siguiera esa documentación seteaba
   una variable que `_load_clip_model_hashes()` nunca lee — el override no
   hacía nada, silenciosamente, sin ningún error que apuntara al typo.

2. **Default invertido.** `VIGIA_STRICT_MODEL_CHECK` tiene default `"true"`
   en el código (`os.getenv("VIGIA_STRICT_MODEL_CHECK", "true")`, comentado
   como "P1-7: default seguro"). El `.env.example` anterior lo seteaba
   explícitamente en `false` — al copiar el archivo a `.env`, esto bajaba la
   verificación de integridad del modelo CLIP de "segura por defecto" a
   permisiva, contradiciendo el propio encabezado de esa sección
   ("STRICT MODE — activar todos antes de cualquier uso forense en un
   entorno real").

### Impacto

Ninguno sobre veredictos ya sellados — ambas son variables de configuración
de entorno, no lógica de scoring. El impacto es operacional: un operador
que configurara el hash de CLIP vía el nombre documentado (sin `_PT`)
creería tener supply-chain integrity activa sobre el modelo de visión
cuando en realidad seguía usando el hash hardcodeado (vacío) o de archivo;
y cualquiera que copiara `.env.example` tal cual heredaba un
`VIGIA_STRICT_MODEL_CHECK=false` explícito, más permisivo que no setear la
variable en absoluto.

### Fix aplicado

Corregido el comentario en `vision_audit.py` (nombre completo con `_PT` +
nota de que fue confirmado por ejecución) y el `.env.example` reescrito
(variable renombrada a `VIGIA_CLIP_HASH_VIT_B_32_PT`;
`VIGIA_STRICT_MODEL_CHECK` cambiado a `true` con comentario explicando por
qué). Test permanente agregado:
`tests/test_clip_hash_env_var_naming.py` (4 tests: deriva el nombre
correcto, el override con `_PT` funciona, el nombre sin `_PT` se ignora
silenciosamente — documentando el modo de falla que causó esto — y el
default de `VIGIA_STRICT_MODEL_CHECK` es `true` cuando la variable no está
seteada).

## B-215 — `evidence_graph` no se puebla en bundles de `run_full`: `graph_hash` idéntico en todos los casos (ancla de integridad vacía de significado) [RESUELTO — Claude 2026-07-31]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (integridad Daubert): `graph_hash` debía ligar el bundle al grafo de evidencia del caso; siendo constante, no anclaba nada. `decision_hash` sí era case-specific, así que la reproducibilidad del veredicto no estaba comprometida. |
| **Archivos** | `vigia/pipeline/pipeline.py` (`VigiaPipeline.run_full` / nuevo helper `_signal_anchor_graph`). |
| **Detectado por** | Verificación empírica de 4 bundles `_claude_fable` (2026-07-23): OWL-NEXUS5 (22), MAGNET-iOS (6), OWL-COMPLETE (30), FLAREON-2017 (14) — todos con `graph_hash` `94147b51...`. |

### Hallazgo que refutó el fix "obvio" (decisión de arquitectura de Anna)

El fix literal del reporte ("poblar `evidence_graph` con los nodos de señal")
es **peligroso** y se refutó con inducción antes de aplicarlo:
`EvidenceGraph.global_stability()` devuelve `1.0` con `n==0` nodos (el default
del grafo vacío actual) pero `0.0` con `n>=2` nodos sin edges bootstrap-estables.
Ese `S` alimenta el score en `pipeline.py` (`r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))`);
con `γ=2`, `S` de 1.0→0.0 **triplica** ese factor. Demostrado: un caso benigno
con posterior 0.04 pasa de ACCEPT (risk 0.04) a ABSTAIN (risk 0.12). Poblar el
grafo naïvemente **cambiaría el veredicto sellado de todo el corpus** que pasa
por `run_full` sin grafo ajustado. Anna eligió el enfoque **anchor-only**:
`graph_hash` case-specific para integridad, sin tocar el scoring.

### Fix aplicado

Nuevo helper `VigiaPipeline._signal_anchor_graph(signals)`: cuando `run_full`
no recibe un grafo ajustado, sella un descriptor determinista con un nodo por
señal, etiquetado con un fingerprint canónico del contenido de la señal
(`_sha256_dict({tool_name, value, z_score})[:16]`, el mismo encoder que sella
el bundle → misma garantía de determinismo). Los labels se ordenan (anchor
order-independent). `bootstrap_rounds=0` marca el descriptor como NO-ajustado;
`edges=[]` (no se afirma estructura de dependencia). Un grafo ajustado
provisto explícitamente se sella sin cambios (rama intacta).

**Scoring intacto:** `graph_stability` se computa en `pipeline.py:561` desde el
*parámetro* `evidence_graph` (None → 1.0), NO desde el descriptor — que solo se
construye después, para el sellado. Verificado: ningún consumidor recomputa
`global_stability()` del grafo sellado (`verify_ebs_v1.py` solo recomputa el
SHA-256; `evidence_narrative_gen.py` lee `global_stability` como clave de dict
que `to_dict()` no emite).

Verificado empíricamente: dos casos con señales distintas dan `graph_hash`
distintos (`5fceae93...` vs `77cc006b...`); el mismo caso en pipelines frescos
reproduce el hash (determinismo); `graph_stability` sellado sigue 1.0 y el
veredicto no cambia por el descriptor. Verificador independiente
`forensics/verify_ebs_v1.py` sobre un bundle sellado real: PASS, Level 2, 10/11
checks OK (el único no-OK es el `R5_ECL_BINDING` WARN, feature de Level 3 ajena
a este bug). Suite completa (`tests/ vigia/tests/ tests/integration`): 1993
passed, 0 failed. Test permanente: `tests/test_b215_graph_hash_case_specific.py`
(5 tests, rojo-primero — `test_different_cases_get_different_graph_hash` y
`test_descriptor_marked_unfitted` fallan contra el código sin fix; los de
determinismo, orden-independencia y `graph_stability=1.0` pasan en ambos
estados, documentando que el fix preserva esos invariantes).

## B-216 — `tests/run_vigia_case.py` crashea al formatear `severity` None de un `caie_fracture` con `:.2f` [RESUELTO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3 (runner de display/demo, no el path sellado): `TypeError: unsupported format string passed to NoneType.__format__` al imprimir las fracturas CAIE de cualquier caso cuyas `caie_fractures` no traigan el campo `severity` (traen `type`/`description`). No afecta el veredicto ni el bundle. |
| **Archivo** | `tests/run_vigia_case.py` (línea ~162: `f"    [{f.get('fracture_type')}] severity={f.get('severity'):.2f}"`). |
| **Modo** | Solo el runner de display `tests/run_vigia_case.py` (usado por `scripts/run_vigia_full.py` como primera etapa). |
| **Detectado por** | Corrida de `run_vigia_full.py` sobre `VIGIA-OWL-2019-COMPLETE.json`; reproducido también sobre el `OWL-NEXUS5-CASE.json` original (bug preexistente, no del caso). |
| **Commit fix** | rama `claude/bugs-pendientes-advance`. |

### Verificación previa al fix (Firstness/Secondness)

Antes de tocar código, se relevó el corpus completo (`data/cases/**/*.json` +
`cases/**/*.json`, 293 archivos escaneados): 101 `caie_fractures` en total,
95 con `severity` numérico y 6 (los dos casos OWL) con solo `type`/
`description`. Reproducido en vivo: `python3 tests/run_vigia_case.py
data/cases/VIGIA-OWL-2019-COMPLETE.json` termina en el `TypeError` exacto
documentado, después de imprimir el veredicto — confirma que el bug es real
y está exactamente donde se lo señaló, no una anticipación stale.

### Fix aplicado

`fracture_type = f.get('fracture_type', f.get('type', '?'))` (fallback al
schema legacy) y `severity_str = f"{severity:.2f}" if severity is not None
else "N/A"`. Se prefirió `"N/A"` sobre el `f.get('severity') or 0` que
proponía la entrada original: un 0.00 fabricado se vería como un dato real
y violaría la doctrina de degradación honesta del propio repo
(`docs/ENGINEERING_DISCIPLINE.md` §5.3 — "never emit a result that looks
correct when correctness cannot be guaranteed"); `N/A` deja explícito que
esa fractura no trae severidad medida.

### Verificación posterior al fix

- Re-ejecutado contra las 101 fracturas del corpus completo (script de
  verificación, no solo los dos casos OWL): 0 crashes.
- `python3 tests/run_vigia_case.py data/cases/VIGIA-OWL-2019-COMPLETE.json`
  y `.../OWL-NEXUS5-CASE.json`: corren completos, `severity=N/A` en las 6
  fracturas sin severidad, veredicto se imprime normalmente.
- `cases/input/VIGIA-BREAK-012.json` (caso con `severity` real): sigue
  mostrando `severity=0.90`, sin cambio de comportamiento.
- Test permanente: `tests/test_b216_run_vigia_case_severity_format.py` (4
  tests: los dos casos OWL no crashean, un caso con severidad real
  renderiza el valor correcto, y el fallback a `type` funciona).
- Suite completa antes y después: 1982 passed, 191 skipped, 29 xfailed —
  cero regresiones.

## B-218 — El bundle sella `epsilon_used = epsilon_accept` incluso cuando el veredicto fue REJECT por `epsilon_reject`: el ε que queda registrado no es el que decidió [RESUELTO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2, con precondición dormida en el path por defecto (ver abajo). Origen: auditoría "Ronda 2", hallazgo F2. |
| **Archivos** | `vigia/core/risk_bounded_layer.py` (`RiskBoundedDecisionLayer.decide`); `vigia/pipeline/pipeline.py` (construcción del `SystemState` en `run_full`). |
| **Función** | `RiskBoundedDecisionLayer.decide()`; `VigiaPipeline.run_full()`. |
| **Líneas originales** | `epsilon_used=self._eps_accept` (siempre, sin importar el veredicto); `epsilon_accept=decision_trace.epsilon_used, epsilon_reject=decision_trace.epsilon_used` en `pipeline.py`. |
| **Commit fix** | rama `claude/bugs-pendientes-advance`. |

### Descripción (heredada de la documentación original, verificada de nuevo antes de tocar código)

`decide()` construía la `DecisionTrace` con `epsilon_used=self._eps_accept`
sin condicionar por el veredicto. Cuando el veredicto era REJECT, el umbral
que efectivamente decidió era `epsilon_reject`, no `epsilon_accept` — pero
el campo sellado siempre reportaba `epsilon_accept`. Separadamente, y más
grave: `pipeline.py` copiaba ese mismo `epsilon_used` a **ambos**
`SystemState.epsilon_accept` y `SystemState.epsilon_reject`, colapsando dos
umbrales de política potencialmente distintos en el bundle sellado.

**Precondición confirmada por ejecución (por qué esto era P2, no P1):**
`VigiaPipeline(adaptive_policy=True)` — el default — construye
`SelfAdaptiveRiskPolicy(epsilon_init=policy_spec.epsilon_accept)`, que fija
`self.epsilon_accept = self.epsilon_reject = epsilon_init` ya en el
constructor, ANTES de que `update_from_window()` corra siquiera. Es decir,
el path adaptativo por defecto colapsa los dos umbrales a un solo valor por
diseño, independientemente de este bug. El bug solo mordía si un
`PolicySpec` definía `epsilon_accept != epsilon_reject` explícitamente Y se
construía el pipeline con `adaptive_policy=False` — confirmado ejecutando
ambos casos antes de decidir el fix.

### Fix aplicado

Dos partes:

1. **`decide()`** ahora sella `epsilon_used = self._eps_reject` si el
   veredicto es `REJECT`, `self._eps_accept` en cualquier otro caso
   (`ABSTAIN` conserva `eps_accept` como valor de referencia — ningún umbral
   "decidió" un ABSTAIN, y `abstain_reason` ya expone ambos valores reales
   en su texto).
2. **`pipeline.py`** ya NO deriva `SystemState.epsilon_accept`/`epsilon_reject`
   de `decision_trace.epsilon_used` — ahora sella directamente
   `self._adaptive_policy.epsilon_accept`/`.epsilon_reject` (si hay política
   adaptativa) o `self._risk_layer._eps_accept`/`._eps_reject` (si no la
   hay), el mismo patrón que ya usaban `lambda_drift`/`gamma_stability` dos
   líneas arriba. Este es el fix real del problema de auditoría del bundle:
   ya no colapsa dos umbrales potencialmente distintos en un solo valor.

### Verificación

Ejecutado antes y después del fix (no solo deducido):

```
RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.40)
decide(posterior=0.70) → REJECT, epsilon_used=0.40 (antes: 0.05, incorrecto)
decide(posterior=0.01) → ACCEPT, epsilon_used=0.05 (sin cambio)
decide(posterior=0.30) → ABSTAIN, epsilon_used=0.05 (sin cambio, valor de referencia)

VigiaPipeline(policy=PolicySpec(epsilon_accept=0.05, epsilon_reject=0.40),
              adaptive_policy=False).run_full(...) → REJECT
  SystemState.epsilon_accept = 0.05  (antes: 0.05, por casualidad correcto en ACCEPT)
  SystemState.epsilon_reject = 0.40  (antes: 0.05, INCORRECTO)

VigiaPipeline() [default, adaptive_policy=True] .run_full(...)
  SystemState.epsilon_accept = SystemState.epsilon_reject = 0.05  (sin cambio,
  confirma que el path por defecto —el que usa el pipeline en la práctica—
  no se vio afectado por el fix)
```

Test permanente: `tests/test_b218_epsilon_sealing.py` (6 tests: umbral
correcto sellado por veredicto en `decide()`, caso simétrico sin cambios, y
el par de casos end-to-end con/sin política adaptativa a través de
`run_full()`). Suite completa antes y después: 1992 passed, 191 skipped, 29
xfailed — cero regresiones (la única falla observada en
`tests/integration/test_ebs_v1_integration.py`, sobre calibración
KDE/Ledoit-Wolf, es preexistente — confirmada idéntica con y sin este fix
vía `git stash`).

## B-220 — La caché de `bayesian_update` está indexada solo por `artifact_id`: ignora `custom_window`, aunque el parámetro es parte de la firma pública [RESUELTO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P3, era latente (ningún *caller* usaba el parámetro afectado). Origen: auditoría "Ronda 2", hallazgo F4. |
| **Archivo** | `vigia/core/trust_fusion.py` (`TrustFusionEngine.bayesian_update`). |
| **Función** | `bayesian_update(self, artifact_id, custom_window=None)`. |
| **Líneas originales** | `if artifact_id in self._bayesian_cache: return self._bayesian_cache[artifact_id]` — clave de caché era solo `artifact_id`. |
| **Commit fix** | rama `claude/bugs-pendientes-advance`. |

### Descripción (verificada de nuevo antes de tocar código)

`bayesian_update(artifact_id, custom_window=None)` usaba correctamente
`custom_window` para calcular la vecindad temporal, pero revisaba
`self._bayesian_cache` usando únicamente `artifact_id` como clave. Confirmado
por `git stash` (comparación antes/después con el mismo repro): con
`a1`(prior 0.9) en t=0, `a3`(prior 0.5) en t=10s y `a5`(prior 0.1,
contaminado) en t=200s — dentro de la ventana default de 300s pero fuera de
una ventana custom de 30s —, `bayesian_update('a3')` seguido de
`bayesian_update('a3', custom_window=30s)` devolvía el **mismo objeto** los
dos veces (posterior 0.15 filtrado a la llamada de 30s, que debería haber
visto solo a `a1` y calculado 0.9).

### Fix aplicado

`cache_key = (artifact_id, custom_window)` en vez de `artifact_id` solo.
`custom_window` es `None` o un `timedelta` — ambos hasheables, la tupla
funciona directamente como clave de dict sin conversión adicional. Los dos
lugares donde se escribe/lee la caché (`bayesian_update`) y los dos donde se
limpia (`add_artifact`, otro método) no necesitaron más cambios — `.clear()`
no depende de la forma de la clave.

### Verificación

Ejecutado antes y después (`git stash`):

```
ANTES: bayesian_update('a3') -> posterior=0.15
       bayesian_update('a3', custom_window=30s) -> posterior=0.15 (mismo objeto, INCORRECTO)

DESPUÉS: bayesian_update('a3') -> posterior=0.15
         bayesian_update('a3', custom_window=30s) -> posterior=0.9 (objeto distinto, CORRECTO)
```

Confirmado también que el orden de llamadas no importa (custom primero,
default después, da los mismos resultados correctos e independientes), que
llamadas idénticas siguen cacheando (no se desactivó el cacheo, solo se
corrigió la clave), y que `add_artifact` sigue invalidando la caché
correctamente con la clave nueva.

Re-confirmado por grep (el mismo chequeo que originalmente marcó esto como
latente): ningún *caller* de producción pasa `custom_window` hoy — el fix no
tiene efecto de comportamiento en ningún camino real, solo corrige qué pasa
si/cuando alguien empiece a usar el parámetro documentado.

Test permanente: `tests/test_b220_bayesian_cache_key.py` (6 tests: ventanas
distintas dan resultados distintos en ambos órdenes de llamada, llamadas
idénticas siguen cacheando, `add_artifact` sigue invalidando la caché, y un
guard que se auto-marca para revisión si algún *caller* de producción
empieza a usar `custom_window`). Suite completa antes y después: 1998
passed, 191 skipped, 29 xfailed — cero regresiones.

## B-122 — Audit trail gap: 20 of 23 MCP tools lack TOOL_INVOKED logging [RESUELTO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — cobertura universal ya existía, resuelto por un mecanismo distinto al que la entrada proponía. |
| **Severidad** | Era P2 (Daubert chain-of-custody gap). |
| **Archivo** | `vigia/vigia_sift_bridge.py`. |
| **Detectado en** | Module archaeology audit 2026-07-14; re-investigado 2026-07-26 mientras se corregía una discrepancia no relacionada del conteo "21 tools" en la documentación. |
| **Commit fix** | Ninguno de esta rama — ya estaba resuelto en el código vivo cuando se re-investigó; solo se corrige el registro. |

### Qué decía la entrada original

CLAUDE.md exige loguear cada llamada a `audit_trail`. De los tools expuestos
por `Vigia_Sift_Bridge`, solo 3 (`generate_forensic_hash`, `read_evidence`,
`list_files`) tenían su propio `audit_logger.log_info(event_type="TOOL_INVOKED",
...)` dentro del cuerpo de la función; 20 más estaban listados como
"NOT covered", con el fix pospuesto a una sesión dedicada porque instrumentar
los 20 manualmente sumaría ~20 `fsync()` síncronos más por investigación.

### Qué muestra el código vivo hoy

`_register_mcp_tool()` (línea ~206) es el **único** camino de registro de
tools MCP en todo el archivo — confirmado por `grep -c "mcp.tool()"` dando
exactamente 1 ocurrencia en todo el archivo, dentro de esa función. Envuelve
CADA tool, tanto los registrados por decorador (`@_register_mcp_tool`) como
los de estilo llamada (`_register_mcp_tool(func)`, los opcionales/gateados),
con `_audit_mcp_entry()`, que emite `audit_logger.log_info(event_type=
"TOOL_INVOKED", ...)` **antes** de ejecutar la función envuelta — es decir,
antes de cualquier sanitización de paths o lógica interna, igual o mejor que
la garantía que los 3 tools originales cumplían individualmente.

Verificado por ejecución directa (no solo lectura estática): llamar a
`deactivate_honey_token` y `get_phonetic_dict_stats` — dos de los tools que
la entrada original listaba como "NOT covered" — produce un evento
`TOOL_INVOKED` cada uno, sin ningún cambio de código por tool. Confirmado
además por AST walk que los 22 tools base y los 5 tools opcionales
siempre-cargados resuelven todos a `_register_mcp_tool`.

### Corrección de un detalle de la lista original

`check_syscall_latency` aparecía en la lista de "NOT covered (20)" como si
fuera un tool MCP sin instrumentar. No lo es: no tiene el decorador
`@_register_mcp_tool` ni ningún `_register_mcp_tool(check_syscall_latency)`,
y no tiene **ningún caller** en todo el archivo — nunca fue un tool MCP,
parece código muerto (detección de rootkits vía latencia de syscalls,
nunca cableado a nada). No participaba del conteo real de tools cubiertos ni
sin cubrir.

### Por qué esto cuenta como resuelto, no como "hallazgo nuevo"

La preocupación de fondo de B-122 (¿todo tool MCP deja un registro de
invocación contemporáneo, no reconstruido después?) está satisfecha —
mejor de lo que la entrada proponía: en vez de 3 sitios de instrumentación
manual + 20 pendientes, hay UN solo punto de aplicación estructural que no
puede olvidarse al agregar un tool nuevo (cualquier tool que no pase por
`_register_mcp_tool` simplemente no se registra en el servidor MCP en
absoluto). La preocupación de "known technical debt" sobre el costo de
`fsync()` × 20 tools adicionales quedó sin objeto: el costo ya se estaba
pagando en cada llamada a cualquier tool desde antes de esta verificación,
no es una regresión de performance nueva a evaluar.

### Verificación

Test permanente: `tests/test_b122_universal_tool_invoked_audit.py` (6 tests:
`mcp.tool()` se llama exactamente una vez en todo el módulo — un guard que
se auto-marca si algún día aparece un segundo camino de registro que podría
saltear el wrapper de auditoría —, `_register_mcp_tool` envuelve con
`_audit_mcp_entry`, dos tools previamente "sin cobertura" emiten
`TOOL_INVOKED` en ejecución real, y `check_syscall_latency` confirmado sin
decorador y sin callers). Suite completa: 1998 passed (antes de sumar este
archivo), 191 skipped, 29 xfailed.

## B-214 — `VigiaPipeline.run_full` saltea el gate de integridad de normalización que `vigia_agent.py` sí aplica: dos entry points, dos veredictos [RESUELTO — Claude 2026-07-26]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (footgun de arquitectura, no incorrección). |
| **Archivos** | `vigia/pipeline/pipeline.py` (`VigiaPipeline.run_full`), `vigia_agent.py` (agente Mode 1 completo). |
| **Modo** | Cualquier código que llame `run_full` directo para sellar en vez de pasar por el agente. |
| **Detectado por** | Cross-check Mode-1 vs Mode-2 (sesión 2026-07-23). |
| **Commit fix** | rama `claude/bugs-pendientes-advance`. |

### Descripción (heredada, sin cambios de sustancia)

`run_full` no corre el gate de integridad de normalización que sí aplica
`vigia_agent.py` (Mode 1) antes de sellar. Reproducido con dos casos reales
(`OWL-NEXUS5-CASE.json`, `VIGIA-OWL-2019-COMPLETE.json`): `run_full` sella
`decision=REJECT, posterior=1.0`; `vigia_agent.py` sobre el mismo JSON sella
`ABSTAIN` con razón `NORMALIZATION_INTEGRITY_LOSS`. Investigación adicional
en esta sesión confirmó que `run_full` (motor `LikelihoodEngine` +
`RiskBoundedDecisionLayer`, el path "EBS v1") y `vigia_agent.py` (que usa
`vigia_scorer.py` + `vigia_integration_bridge.py` para su scoring
determinístico) son en efecto **dos motores de scoring distintos**, no una
función con un flag opcional — cablear el gate de normalización en
`run_full` requeriría integrar dos sistemas de scoring separados, no solo
agregar un chequeo.

### Decisión tomada: opción (b), no (a)

La entrada original proponía dos caminos: (a) `run_full` corre el mismo
gate y degrada a ABSTAIN — cambia el veredicto sellado de cualquier caso
con `normalization_failures`, requiere decisión de arquitectura + dry-run
del corpus; o (b) documentar `run_full` explícitamente como "score crudo
sin gates" y señalar que el sellado autoritativo debe pasar por el agente.
Se aplicó (b): es la opción que la propia entrada ya sancionaba como segura
sin necesitar el dry-run que (a) exige, y no toca ningún veredicto sellado.

### Fix aplicado

Docstring de `run_full()` ampliada con una advertencia explícita: nombra
B-214, describe el gap exacto, cita los dos casos reales reproducidos, y
indica textualmente "no llames a `run_full` directamente" para sellado
autoritativo — usar `vigia_agent.py` en su lugar. Cero cambio de
comportamiento: la lógica de scoring de `run_full` no se tocó.

**Hallazgo adyacente corregido de paso:** la misma docstring, en el paso
`[Gobernanza]`, documentaba la fórmula pre-B-117 invertida
(`r = (1-P)·(1+λD)·(1+γ(1-S))·(1+ω(1-I))`) — el bug que B-117 corrigió en
2026-07-14 invirtiendo el sentido de los veredictos. La implementación viva
(`risk_bounded_layer.py`) usa `r = P·(...)` desde ese fix; la docstring
nunca se actualizó. Corregida a la fórmula real, con referencia a B-117.

### Verificación

Test permanente: `tests/test_b214_run_full_docstring_warning.py` (3 tests:
la docstring nombra B-214 y el gap, apunta explícitamente al agente para
sellado, y la fórmula ya no es la forma pre-B-117 invertida). Sintaxis
verificada con `ast.parse()` tras el edit. Suite completa antes y después:
2004 passed, 191 skipped, 29 xfailed — cero regresiones (cambio
documentación-only, sin lógica tocada).

---

## B-223 — `generate_execution_log.py` sella una entrada `RISK_CALCULATION` con la fórmula y variables de un motor de decisión distinto al que realmente usa, con D/S/I fabricados [RESUELTO — Claude 2026-07-31]

| Campo | Valor |
|-------|-------|
| **Severidad** | P2 (integridad de audit trail — el script genera "Agent Execution Logs... para los entregables SANS" según su propio docstring; no es un generador sintético/demo). |
| **Archivos** | `vigia/scripts/generate_execution_log.py` (`process_case`), `vigia/core/execution_logger.py` (`VigiaExecutionLogger`). |
| **Detectado en** | Barrido de la fórmula pre-B-117 invertida (2026-07-26). |

### Descripción

`process_case()` llama a `decision_layer.decide()` (motor MI-threshold,
sin D/S/I) pero sellaba una entrada `RISK_CALCULATION` con la fórmula y
variables P/D/S/I de `risk_bounded_layer.RiskBoundedDecisionLayer` — un
motor distinto que este script nunca ejecuta. `D=0.1` hardcodeado; `S` e
`I` derivados con fórmulas ad-hoc de `mi_float` sin relación con ningún
cálculo real de `graph_stability` ni `consistency_score`.

### Investigación previa al fix (audit-before-patch)

Antes de decidir entre las dos opciones que el propio registro dejaba
abiertas — (a) diseñar un schema honesto para el motor MI-based, o (b)
migrar el script a `risk_bounded_layer` — se investigó quién consume
estos logs: `grep` exhaustivo mostró que **nadie** llama a
`log_risk_calculation()` en producción excepto este mismo script
(`pipeline.py`, el consumidor real de `risk_bounded_layer`, nunca lo
llama — usa `log_event`/`log_abstain`/`log_verdict`). Es decir, el schema
P/D/S/I nunca se usó para su propósito real; su único emisor era el
fabricante de datos falsos. Eso descarta la opción (b) — no hay ninguna
señal de que el script debiera migrar de motor — y confirma que (a) es
la corrección correcta: el script corre `decision_layer.decide()`, así
que debe loguear honestamente lo que ese motor calcula.

### Fix aplicado

Nuevo método `VigiaExecutionLogger.log_mi_decision()` en
`execution_logger.py`: emite `event_type: "MI_DECISION"` con `engine`
(nombre completo del motor real), `mi`, `alert_level`, `thresholds` (los
`DEFAULT_LOW/MEDIUM/HIGH` reales de `decision_layer`), `decision`,
`reason_code`, y `reason` (la razón que el propio motor genera) — sin
`variables`, sin `formula`, sin D/S/I. `log_risk_calculation()` (el
método P/D/S/I para `risk_bounded_layer`) queda intacto para su
consumidor real si algún día se cablea.

`generate_execution_log.py` reemplaza el call site: usa
`DEFAULT_LOW/MEDIUM/HIGH` importados de `decision_layer` (no thresholds
hardcodeados nuevos) y `dec.get("reason", "")` (la razón real del motor,
no un `reason_code` inventado con vocabulario de otro sistema). Docstring
del módulo actualizado (`RISK_CALCULATION` → `MI_DECISION` en el diagrama
de fases).

**Auto-corrección durante el fix:** el primer borrador del docstring de
`log_mi_decision()` citó la fórmula `r=(1-P)·(1+λD)·...` — la forma
**invertida pre-B-117** — al explicar en qué se diferenciaba del otro
método. El propio `tests/test_b117_stale_formula_sweep.py` lo detectó
(falló contra el archivo nuevo). Corregido a la forma real
(`r=P·(1+λD)·...`, verificada contra `risk_bounded_layer.py:426`) antes
de commitear — el test cumplió exactamente la función para la que B-117
lo diseñó.

### Verificado

Ejecución real end-to-end (`process_case()` con un caso con `text`, no
mockeado): el JSONL resultante tiene evento `MI_DECISION`, cero eventos
`RISK_CALCULATION`, `engine` nombra el motor real, `thresholds` son los
reales del `decision_layer`, sin `variables`/`formula`/D/S/I en el
payload. Test permanente:
`tests/test_b223_mi_decision_no_fabricated_dsi.py` (4 tests, rojo-primero
— 3 de 4 fallan contra el código sin el fix, incluyendo un
`StopIteration` porque el evento `MI_DECISION` ni existía). `allowlist`
de `test_b117_stale_formula_sweep.py` actualizado: se retiró la excepción
de `generate_execution_log.py` (ya no contiene la fórmula obsoleta) y se
agregó la del nuevo test (cita la fórmula vieja como evidencia histórica
del bug, no como claim vivo). Suite completa: 2128 passed, 0 failed.
