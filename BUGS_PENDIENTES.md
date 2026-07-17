# BUGS_PENDIENTES.md — VIGÍA Bug Registry

Registro de bugs detectados, su impacto forense, y el fix aplicado.
Formato: un bloque por bug. Los bugs resueltos permanecen en el registro
como audit trail — no se eliminan.

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

## B-010 — TODO: migrar forensic_technical_detector.py a SemioticDetectorV2

| Campo | Valor |
|-------|-------|
| **Estado** | ABIERTO |
| **Severidad** | P3 — deuda técnica, no bug funcional |
| **Archivo** | `vigia/core/forensic_technical_detector.py` |
| **Línea** | 194 |
| **Detectado en** | Sesión post-hackathon 2026-06-25 |

### Descripción

```python
# TODO: migrar a SemioticDetectorV2 en v3.0
```

El detector técnico forense sigue usando la arquitectura v1. `SemioticDetectorV2`
existe pero no está wired aquí. No es un bug funcional — el detector opera
correctamente con la arquitectura actual. Es deuda de migración para v3.0.

### Fix cuando corresponda

Evaluar si SemioticDetectorV2 cubre todos los casos de forensic_technical_detector.
Migración debe ser auditada por el colectivo antes de aplicar.

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
| **Estado** | P1 (narrativa honesta) FIXED — 2026-07-03; **P2 CERRADO 2026-07-10 — NOT ADOPTED por decisión sellada §9.4 (opción (ii) pura, colectivo + firma de Anna)**: el split por dominios lógicos manufactura corroboración — todos los dominios macOS son D3, mismo canal físico. SUSPICION es el techo doctrinal para D3-only (**L-051 / §9.4-LIM**). La implementación del split queda como registro histórico en la rama `claude/b052-p2-domain-signals-xk5ecq` (`c5c8d38`+`a74d360`, **NO MERGEAR**); `densidad_causal_D3` descartada por experimento pre-registrado (r=0.9185, zona gris fail-closed). Mitigación implementada: clase `suspicion_class` (GENERIC \| D3_RICH_NO_TRIANGULATION) en narrativa + pipeline_meta, solo texto (`docs/B052_P2_DESIGN.md` §10; 12 tests). |
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
| **Estado** | NO APLICADO — gate pre-registrado (firma Anna: `fixed>=1 AND broken==0`) rechazó el cambio con fixed=30 / **broken=3**. Fix implementado, medido y **revertido**. Sentinelas `xfail(strict=True)` en `tests/test_b097_motor_suspicion_verdict.py`. |
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
3. **Gap de motor real y cerrable (distinto en naturaleza de 1):**
   `VIGIA-FN-003` exige análisis de memoria profundo (regiones RWX,
   parent-process-mismatch) que el motor no ejecuta hoy — a diferencia de 1,
   esto NO requiere una fuente de datos externa nueva, sería extender un
   engine que ya existe. Candidato genuino a backlog de ingeniería (no de
   doctrina).
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

## B-111 — Mode 3 (Ollama/hermes3:8b): comportamiento no confiable en evidencia testimonial densa — N=2, ESTOCÁSTICO

| Campo | Valor |
|-------|-------|
| **Estado** | OBSERVADO — evidencia insuficiente para escalar a KNOWN_LIMITATIONS |
| **Severidad** | P3 (experimental — Mode 3 ya clasificado como no-primario) |
| **Detectado en** | Experimento comparativo ciego 2026-07-13, KIWI-006 y KIWI-007 |
| **N observaciones** | 2 corridas KIWI-006 (1 alucinación, 1 limpia) + 1 corrida KIWI-007 (JSON truncado) |

### Observaciones

**Corrida 1 — KIWI-006, primera ejecución:** `hermes3:8b` alucinó
`"carnegie_pattern": "JAILBREAK_ATTEMPT"` y
`"security_alert": "EVIDENCE_DELIMITER_MISMATCH"` — campos inexistentes en el
esquema VIGÍA. El modelo interpretó el contenido del testimonio (vigilancia,
contactos bloqueados, coordinación de testigos) como evidencia de un ataque sobre
sí mismo. El análisis Peircean correcto también estaba presente en la misma
respuesta, embebido junto a los campos alucinados. JSON válido.

**Corrida 2 — KIWI-007, primera ejecución:** `hermes3:8b` retornó JSON inválido
(objeto truncado a mitad del campo A02, después de completar A01). La herramienta
detectó el fallo y retornó `"error": "LLM did not return valid JSON."` con el
fragmento en `"raw_response"`. Requirió síntesis manual para A02 y A03.

**Corrida 3 — KIWI-006, re-ejecución con prompt IDÉNTICO (2026-07-13, misma sesión):**
Resultado limpio. Sin alucinación. JSON válido completo. Cadena Peircean correcta.
Veredicto NOISE 0.25, razonable y consistente con CAIE.

### Estado de la evidencia

N=2 corridas de KIWI-006 (1 alucinación / 1 limpia con mismo prompt). El
comportamiento es **estocástico, no determinista** — el mismo input no reproduce
el mismo error. N=1 para KIWI-007 (truncado), sin re-corrida todavía.

No escala a KNOWN_LIMITATIONS porque:
- N insuficiente para establecer frecuencia de error
- La re-corrida de KIWI-006 fue limpia → no es un patrón consistente
- Mode 3 ya está clasificado como experimental/complementario en el README y CLAUDE.md

### Qué observar en corridas futuras

- ¿La alucinación de jailbreak reaparece en KIWI-006 con una tercera corrida?
- ¿KIWI-007 trunca consistentemente o fue un evento único?
- ¿Otros casos testimoniales densos (KIWI-007 análogos) muestran el mismo patrón?
- Si la tasa de alucinación se confirma en >20% de corridas en casos testimoniales:
  escalar a KNOWN_LIMITATIONS con recomendación de `gemma3:27b` para Mode 3
  en producción sobre narrativa densa.

### Nota sobre no-reproducibilidad

La no-reproducibilidad del error es, en sí misma, un dato relevante: un error
consistente se detecta en testing; uno estocástico puede llegar a producción sin
señal previa. Si se confirma con más muestras que la tasa no es despreciable,
ese argumento de opacidad sería el fundamento para la limitación formal, no los
dos eventos aislados actuales.

---

## B-112 — CAIE catalogue gap candidato: SELF_INCRIMINATION_LOG — evidencia auto-incriminatoria epistemicamente distinta de log espoofeable por tercero

| Campo | Valor |
|-------|-------|
| Detectado | 2026-07-13 |
| Caso fuente | KIWI-001-A02 y KIWI-003-A03/A04 (expediente MPF7779408) |
| Estado | CANDIDATO — N=1 caso judicial real |

### Descripcion

Cuando el propio actor aporta voluntariamente credenciales o logs que lo incriminan a si mismo en documentacion judicial, el artefacto es epistemicamente irrefutable aunque CAIE le asigne `spoofability=0.85` (log_entry). La metrica de spoofability modela un atacante externo que fabrica evidencia; no aplica cuando la evidencia proviene del propio acusador.

En KIWI-001 (A02) y KIWI-003 (A03/A04), el denunciante (actor_a) presento sus propias credenciales de servidor de stalkeo y admitio haber hackeado a una ex pareja. CAIE computa adjusted=0.0071 y 0.0081 respectivamente por spoofability=0.85 — valores que subestiman el peso epistemico real. Si existiera una fractura `SELF_INCRIMINATION_LOG`, el composite superaria el umbral de SUSPICION en ambos casos sin necesidad de escalada manual.

### Restriccion de generalizacion

Los tres casos KIWI (001, 002, 003) pertenecen al mismo expediente judicial (MPF7779408) vistos desde angulos distintos — **no son 3 muestras independientes, son 1 caso real mirado 3 veces**. La observacion es N=1 de caso judicial real. Se necesita un segundo expediente independiente con la misma estructura (acusador que aporta evidencia auto-incriminatoria) antes de generalizar este patron como gap de catalogo real e implementar la fractura.

### Criterio de escalada

Observar el patron en un segundo expediente judicial independiente (distinto a MPF7779408). No implementar la fractura hasta entonces.

---

## B-113 — CAIE catalogue gap candidato: INSTITUTIONAL_REJECTION — rechazo institucional independiente como corroboracion forense

| Campo | Valor |
|-------|-------|
| Detectado | 2026-07-13 |
| Caso fuente | KIWI-003-A05 (expediente MPF7779408) |
| Estado | CANDIDATO — N=1 caso judicial real |

### Descripcion

En KIWI-003-A05, tres oficios presentaron 6 irregularidades formales y dos comisarias rechazaron independientemente ejecutar el allanamiento ordenado. El rechazo institucional de dos organismos independientes constituye corroboracion forense de la irregularidad documental — una fuente de evidencia que CAIE no captura porque `document_geometry` solo modela el artefacto fisico, no la reaccion institucional frente a el.

Si existiera una fractura `INSTITUTIONAL_REJECTION`, el artefacto A05 pasaria de adjusted=0.0327 a un peso significativamente mayor, dado que el rechazo policial elimina la explicacion de "error administrativo aislado" como hipotesis benigna.

### Restriccion de generalizacion

Misma restriccion que B-112: los tres casos KIWI son el mismo expediente MPF7779408 — **N=1 caso real**. No es evidencia de un gap sistematico del catalogo CAIE hasta que se observe en un segundo expediente independiente con rechazo institucional de documentacion en contexto forense.

### Criterio de escalada

Observar el patron en un segundo expediente judicial independiente (distinto a MPF7779408). No implementar la fractura hasta entonces.

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

---

## B-116 — `signal_quality_gate.py` designed and functional in isolation, NOT wired to scorer — dry-run shows 122/199 cases degraded

> **Update 2026-07-17 (condition 4 re-measured, Kimi-endorsed placeholder
> policy applied):** the four acquisition/conversion placeholders
> (`legacy_converter`, `manual_forensic_review`, `generate_forensic_hash`,
> `read_evidence`) no longer count as analysis tools — they are skipped in
> the `tool_name -> source_tool -> evidence_type` fallback, exactly like the
> literal "unknown". Single source of truth: `_NON_ANALYSIS_PLACEHOLDERS`
> in `vigia/core/signal_quality_gate.py` (not replicated in scripts).
> Re-measured dry-run (corpus grew 202 -> 205 evaluable): MODE B passed
> 77 -> 87; ABSTAIN_INSUFFICIENT_TOOLS 66 -> 40 (the -26 matches the
> census: 31/66 had >=2 distinct evidence_type; the uncovered cases now
> land honestly in the next checks — DEPENDENT_SIGNALS/LOW_Z_VARIANCE);
> degraded-with-expected-MALICE 46 -> 42. Gate remains UNWIRED (zero
> production callers): no verdict moved. Tests:
> `tests/test_b116_placeholder_tools.py` (9, red-first).

| Campo | Valor |
|-------|-------|
| **Estado** | POSPUESTO — bloqueado por desajuste de interfaz y calidad de datos |
| **Severidad** | P2 (gate-level architectural gap — safety mechanism exists but does not fire) |
| **Archivo** | `vigia/signal_quality_gate.py` AND `vigia/core/signal_quality_gate.py` (identical duplicates) |
| **Detectado en** | Post-hackathon session 2026-07-14, dry-run script `scripts/dryrun_signal_quality_gate.py` |

### Description

`SignalQualityGate` implements five checks before a verdict can be emitted:
tool diversity (>= 2 tools), signal strength (z >= 2.0), tool independence
(<= 60% from same tool), z-score variance (range >= 0.5), and noise inflation
detection. The module is complete, tested in isolation, and conceptually aligned
with VIGIA's Daubert corroboration requirements (vigia_scorer.py lines 1194-1240).

However, it has **zero callers** in the codebase. No import of
`SignalQualityGate` exists anywhere outside its own file. Additionally, the
module is duplicated: `vigia/signal_quality_gate.py` and
`vigia/core/signal_quality_gate.py` are byte-identical copies.

### Dry-run results (2026-07-14)

A full corpus dry-run (`scripts/dryrun_signal_quality_gate.py`) tested the gate
against all 199 cases using two signal-mapping modes:

**MODE A** (raw_score passed directly as z_score):
198/199 cases fail — unusable. raw_score lives in [0.0, 0.98]; gate demands
z >= 2.0 for "strong". Pure unit mismatch.

**MODE B** (raw_score * 4.0 as z_score — generous rescaling):

| Gate reason | Cases failed | Detail |
|-------------|-------------|--------|
| `ABSTAIN_INSUFFICIENT_TOOLS` | 67 | Only 1 unique `source_tool` in case |
| `ABSTAIN_WEAK_SIGNALS` | 20 | No raw_score >= 0.50 |
| `ABSTAIN_DEPENDENT_SIGNALS` | 18 | > 60% artifacts from same tool |
| `ABSTAIN_LOW_Z_VARIANCE` | 17 | raw_scores too uniform |
| **Total degraded** | **122** | |
| **Passed gate** | **76** | |

Of the 122 degraded cases, **23 are currently MALICE** — including 11 from the
VIGIA-REAL-001 to REAL-010 series (the most validated corpus in the project).
These cases have `source_tool=unknown` because the field was never populated
during conversion, not because they lack forensic provenance.

### Root cause (three independent blockers)

1. **Interface mismatch**: gate expects `tool_name` + `z_score` (statistical
   z-scores from a calibrated distribution). The scorer produces `source_tool` +
   `raw_score` in [0.0, 1.0]. No z-score computation exists in the current
   scoring pipeline — `fit_calibration.py` produces z_scores per tool
   (`z_scores` dict in sample schema, line 41) but is not yet wired into the
   main scoring path.

2. **Data quality**: 67/199 cases (33%) have only 1 unique `source_tool`,
   and many of those use `source_tool=unknown`. The field does not reflect
   the actual diversity of forensic tools that produced the evidence.

3. **Duplicate module**: `vigia/signal_quality_gate.py` and
   `vigia/core/signal_quality_gate.py` are identical. The `vigia.core.*` path
   is the modern convention; the root copy should be removed when wiring.

### Unblocking conditions

This gate can be wired when ALL of the following are met:

1. `fit_calibration.py` is integrated into the scoring pipeline, producing
   real z-scores per signal (not raw_scores in [0,1]).
2. The z-score output schema includes a `tool_name` field compatible with
   `SignalQualityGate._get_tool_name()`, or the gate is adapted to read
   `evidence_type` (which IS reliably populated).
3. The `source_tool=unknown` problem in legacy cases is resolved (either by
   backfilling from bundle metadata or by having the gate fall back to
   `evidence_type` diversity instead of `source_tool` diversity).
4. A new dry-run confirms 0 true-positive MALICE cases are degraded.

**NOTE for `fit_calibration.py` roadmap**: when z-score output is finalized,
verify compatibility with `SignalQualityGate.evaluate()` input schema. The
gate's `_get_z_score()` reads `signal.z_score` (attribute) or
`signal["z_score"]` (dict key). The calibrator's sample schema uses
`z_scores` (plural, nested dict by tool). These must align before wiring.

### Avance parcial (2026-07-16) — el gate sigue SIN cablear

Tres de los cuatro ítems de desbloqueo avanzaron; el gate permanece sin
callers de producción por diseño (la condición 4 — dry-run con 0 casos MALICE
verdaderos degradados — sigue sin cumplirse):

1. **Duplicado eliminado** (blocker 3): `vigia/signal_quality_gate.py` borrado;
   `vigia/core/signal_quality_gate.py` es la única copia (eran byte-idénticas,
   mismo md5, cero imports del path raíz).
2. **Fallback de diversidad implementado** (condición de desbloqueo 3, opción
   B): `_get_tool_name()` ahora resuelve `tool_name` → `source_tool` →
   `evidence_type`, tratando `"unknown"` como ausente. Tests:
   `tests/test_b116_quality_gate_fallback.py` (8 tests).
3. **Dry-run reconstruido y versionado**: el script original del 2026-07-14
   nunca se commiteó; `scripts/dryrun_signal_quality_gate.py` lo reconstruye
   (mismos MODE A/B) y queda en el repo para que la medición sea reproducible.

**Medición fresca (2026-07-16, corpus 202 casos evaluables):**

| | MODE A (z=raw) | MODE B (z=raw*4) |
|---|---|---|
| Pasan gate | 0 | 77 |
| Degradados | 202 | 125 |
| `ABSTAIN_INSUFFICIENT_TOOLS` | 66 | 66 |
| Degradados con expected_verdict=MALICE | 104 | 46 |

(Los números del 2026-07-14 contaban 199 casos y "23 currently MALICE" —
métrica distinta: veredicto emitido vs `expected_verdict` que usa el script
versionado. No son comparables uno a uno.)

**Hallazgo del censo de `source_tool` en los 66 casos INSUFFICIENT_TOOLS:**
los valores dominantes son placeholders de conversión/adquisición, no
herramientas de análisis: `None` (91 artifacts), `legacy_converter` (88),
`manual_forensic_review` (43), `generate_forensic_hash` (35),
`read_evidence` (8). El fallback conservador (solo `"unknown"` tratado como
ausente) no los cubre: 31 de los 66 casos tienen >= 2 `evidence_type`
distintos y pasarían el check de diversidad si esos placeholders se trataran
como ausentes. **Decisión pendiente (Anna):** definir el set de placeholders
de conversión que no cuentan como herramienta (`legacy_converter`,
`manual_forensic_review`, `generate_forensic_hash`, `read_evidence`) — es
política de datos, no código; con esa decisión el fallback existente los
cubre con un cambio de una línea.

### Why not adapt the gate instead

The gate's checks are doctrinally correct as designed. Adapting it to accept
raw_score instead of z_score would weaken its statistical meaning: a raw_score
of 0.8 from `read_evidence` and a raw_score of 0.8 from `Volatility3/malfind`
have vastly different forensic weight, but the gate would treat them identically.
The right fix is upstream: produce calibrated z-scores, then the gate works
as intended.

### Decision

Postponed. Gate remains unwired. Documented as B-116 for tracking. The
`vigia_scorer.py` corroboration gate (lines 1194-1240) partially covers the
same Daubert requirement using `evidence_type` diversity and domain-based
counting, but does not implement noise inflation detection or z-score
variance checks — those are unique to `SignalQualityGate` and will add
forensic value once the interface is resolved.

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

## B-122 — Audit trail gap: 20 of 23 MCP tools lack TOOL_INVOKED logging

| Campo | Valor |
|-------|-------|
| **Estado** | PARCIALMENTE RESUELTO — 3 tools prioritarias ya cubiertas, 20 pendientes |
| **Severidad** | P2 (Daubert chain-of-custody gap — tool invocations not recorded in audit trail) |
| **Archivo** | `vigia/vigia_sift_bridge.py` |
| **Detectado en** | Module archaeology audit 2026-07-14 |

### Description

CLAUDE.md requires every tool call to be logged to `audit_trail` with
timestamp, tool_name, arguments_hash, and result_summary. Of the 23 MCP
tools exposed by `Vigia_Sift_Bridge`, only 3 have the `audit_logger.log_info
(event_type="TOOL_INVOKED", ...)` call that records the invocation attempt
before path sanitization:

**Already covered (3 — evidence-touching tools):**
- `generate_forensic_hash` — logs before `_sanitize_path_local()`
- `read_evidence` — logs before `_sanitize_path_local()`
- `list_files` — logs before `_sanitize_path_local()`

**NOT covered (20):**
`activate_honey_token`, `analyze_stylometry`, `audit_grice_maxims`,
`audit_image_metadata`, `audit_network`, `calculate_human_entropy`,
`calculate_shannon_entropy`, `check_syscall_latency`, `deactivate_honey_token`,
`detect_eco_overinterpretation`, `detect_habit_incongruence`,
`detect_human_jitter`, `get_phonetic_dict_stats`, `infer_intent`,
`list_processes`, `mount_sift_evidence`, `reason_with_llm`,
`reload_phonetic_dict`, `search_pattern`, `validate_and_correct_analysis`

### Risk assessment

The 3 covered tools are the highest priority: they touch evidence files
directly and form the chain-of-custody anchor (hash before read). The 20
uncovered tools are Phase 2-4 analysis tools — their invocations are
typically recorded in the `tool_execution_log` chain (v2, with HMAC) by
the calling agent, but NOT in the per-tool audit log. An examiner auditing
a specific tool's invocation history would find gaps.

### Known technical debt

`audit_logger.log_info()` uses synchronous `fsync()` on every call. Adding
it to all 20 tools would add ~20 blocking disk flushes per investigation.
Acceptable for the 3 evidence tools (correctness > performance), but the
broader rollout should batch or async the fsync. Documented as accepted
debt, not a blocker.

### Decision

The 3 prioritized tools are covered. The remaining 20 are deferred to a
dedicated session where the fsync performance concern can be addressed
alongside the instrumentation.

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

## B-123 — Causal Closure Score gate designed and tested, NOT wired — dry-run inviable (0/258 cases have data)

| Campo | Valor |
|-------|-------|
| **Estado** | POSPUESTO — bloqueado por cadena completa de productores huérfanos |
| **Severidad** | P2 (Daubert gate — prevents MALICE verdicts without causal coherence) |
| **Archivos** | `vigia/core/causal_closure.py`, `vigia/patterns/adversarial_silence.py`, `vigia/temporal/coherence_validator.py`, `vigia/core/explainable_governance.py` |
| **Test existente** | `tests/test_audit_gates.py` (pasa en aislamiento) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### Description

Causal Closure Score (CCS) gate that caps the maximum verdict at ABSTAIN
when the causal coherence of the evidence is below 50%. The formula:

```
CCS = 0.3 * temporal_coherence
    + 0.2 * semantic_resonance
    + 0.3 * abductive_parsimony
    + 0.2 * adversarial_silence

If CCS < 0.50 -> verdict capped at ABSTAIN
```

Each dimension defaults to `Fraction(1/2)` (maximum uncertainty) when not
available. The gate is doctrinally correct: high signal + low causal
coherence = fabrication profile (Daubert).

### Why not wired today

**The 4 input dimensions do not exist in ANY case of the corpus (0/258).**
Without real data, CCS = exactly 0.50 for every case (all defaults), and
the gate passes unconditionally (`>= 0.50`). Wiring the gate today would
be cosmetic — it would add processing cost without changing a single verdict.

### Blocking dependency chain

The gate requires 4 producer modules, all disconnected from the scoring pipeline:

| CCS dimension | Intended producer | Status |
|---|---|---|
| `temporal_coherence` | `vigia/temporal/coherence_validator.py` | Orphaned (this cluster) |
| `semantic_resonance` | `vigia/inference/cross_artifact_resonance.py` | Live, but does NOT produce this field |
| `abductive_parsimony` | `vigia/abduction/hypothesis_lineage.py` | Orphaned (93KB, entire namespace disconnected) |
| `adversarial_silence` | `vigia/patterns/adversarial_silence.py` | Orphaned (this cluster) |

### Comparison with B-116 (signal_quality_gate)

| | B-116 signal_quality_gate | B-123 causal_closure |
|---|---|---|
| Data available in corpus | raw_score/source_tool exist | None of the 4 dimensions exist |
| Dry-run possible | Yes (with rescaling) | No (all default to 0.50) |
| Measurable impact | 122/199 degraded | 0/258 (trivial — no data) |
| Blocking dependency | 1 module (fit_calibration.py) | 4 orphaned modules (full chain) |
| Unblocking effort | Medium (z-score integration) | High (wire 4 producers + schema) |

### Decision on the 4 files

**NOT candidates for deletion.** Unlike the dead weight removed in B-121,
these files implement real, doctrinally correct forensic logic:

- `causal_closure.py` — the gate itself, Fraction arithmetic, tested
- `adversarial_silence.py` — adversarial gap detection (CLAUDE.md invariant: "deliberate artifact deletion elevates MALICE signal weight")
- `coherence_validator.py` — temporal causality violation detection
- `explainable_governance.py` — ExplanationEngine for ACCEPT/REJECT/ABSTAIN narrative + Daubert compliance section

They are preserved as pending-to-wire capability, not abandoned code.

### Unblocking conditions

The gate can be wired when ALL of the following are met:

1. At least 2 of the 4 producer modules are wired to the scoring pipeline
   and produce real values for their CCS dimension.
2. The corpus includes cases with real CCS dimension values (not all defaults).
3. A meaningful dry-run (with real data) shows acceptable impact on the corpus.

---

## B-124 — Verdict/governance cluster: 6 modules designed, tested, NOT wired — same pattern as B-123

| Campo | Valor |
|-------|-------|
| **Estado** | POSPUESTO — same blocking pattern as B-123 (cadena de productores huérfanos) |
| **Severidad** | P2 (governance gates not firing — safety mechanisms exist but are disconnected) |
| **Detectado en** | Module archaeology audit 2026-07-14 (`docs/module_archaeology.html`) |

### The 6 files

**Scoring-adjacent (highest conceptual severity):**

1. **`vigia/core/ockham_adversarial.py`** (224 lines) — Adversarial simplicity
   penalty: penalizes benign hypotheses that are "too simple" in the presence
   of malice signals (SolarWinds pattern). Needs `candidate_cost` /
   `next_best_cost` (Fraction) + `malice_signal_strength` from
   `hypothesis_lineage.py` (orphaned, vigia/abduction/). The concept "ockham"
   exists live in `abductive_intent_engine.py` (`_build_ockham_rationale`) but
   as a SEPARATE inline implementation — this module is NOT invoked by it.

2. **`vigia/core/dissent_report.py`** (305 lines) — Minority signal escalation:
   "9 modules say BENIGN + 1 behavioral module says MALICE = escalation
   required." Needs results from ALL cluster modules to generate a dissent
   report. Zero callers.

**Defensive / security:**

3. **`vigia/core/config_sentinel.py`** — Config tampering guardian: monitors
   critical modules (CAIE, TrustFusion, OckhamAdversarial, SignalRouter) for
   silent degradation. Zero callers. Its absence means no runtime detection
   of module configuration drift.

4. **`vigia/core/narrative_auditor.py`** (283 lines) — C3 multi-agent narrative
   injection validator (OWASP LLM 2025 taxonomy + Carnegie patterns). Zero
   production callers. `scripts/run_demo.py` loads dynamically from DIFFERENT
   paths (`scripts/narrative_auditor.py`, `scripts/vigia_prod/security/
   narrative_auditor.py`) that do NOT resolve to this file.

**Abduction infrastructure:**

5. **`vigia/core/peirceplanner_bounded.py`** (375 lines) — Miller's Law (7+2)
   bound on abductive reasoning + oscillation detection (A->B->A -> ABSTAIN).
   Needs `AbductiveHypothesis` with `ockham_cost` from `hypothesis_lineage.py`
   (orphaned). Without this, nothing prevents unbounded/oscillating abduction
   in the live planner.

6. **`vigia/core/advanced_signal_router.py`** — Signal routing by artifact type.
   Conceptually superseded by the scorer's inline `evidence_type` lookup in
   `effective_trusts`, but not confirmed identical in behavior. Zero callers.

### Why not wired today (same pattern as B-123)

All 6 depend on inputs that do not exist in the current pipeline or corpus:
- Ockham needs hypothesis costs from the orphaned abduction namespace
- Dissent needs results from ALL governance modules (circular dependency)
- Config sentinel monitors modules that are themselves not wired
- Narrative auditor is unreachable from any production path
- PeircePlanner bounded needs the orphaned hypothesis lineage tracker
- Signal router is conceptually superseded

A dry-run is inviable: without real input data, every module would operate
on defaults or empty inputs, producing no meaningful impact measurement.

### Decision

All 6 preserved as pending-to-wire capability. NOT candidates for deletion
(real forensic logic, Fraction arithmetic, doctrinally correct). Blocked by
the same orphaned producer chain as B-123 (vigia/abduction/, vigia/temporal/,
vigia/patterns/). The full unblocking roadmap is:

1. Wire `vigia/abduction/` namespace (hypothesis_lineage, artifact_graph,
   counter_fact) — unblocks ockham_adversarial + peirceplanner_bounded
2. Wire CCS producers (B-123) — unblocks causal_closure gate
3. Wire governance modules in order: ockham -> dissent -> config_sentinel
4. Wire narrative_auditor as C3 validation step before bundle sealing

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

## B-129 — PeircePlanner bounded: Fase 1 observation adapter [PENDIENTE Fase 2]

| Campo | Valor |
|-------|-------|
| **Estado** | FASE 1 COMPLETADA — pendiente Fase 2 (calibracion) y Fase 3 (integracion) |
| **Severidad** | P3 (no afecta veredictos, modulo de observacion) |
| **Archivos** | `vigia/core/planner_adapter.py` (nuevo), `vigia/core/peirceplanner_bounded.py` (existente) |
| **Detectado en** | Investigation 2026-07-14 |

### Description

Adapter that translates VIGIA case artifacts into EvidenceSignal and
Hypothesis objects for run_bounded_planner(). Output is observation-only
— does NOT feed the scorer or verdict path.

### Investigation findings

1. AbductiveIntentEngine (vigia/inference/) is partially wired (L-027)
   but its HYPOTHESIS_TEMPLATES require MITRE artifact names that real
   cases do not have. Translation layer never written.
2. peirceplanner_bounded and AbductiveIntentEngine are compatible with
   a ~15 line adapter (cost:int -> ockham_cost:Fraction).
3. Both share the same unwired gap (L-027).

### Observation baseline (198/199 cases)

- Agreement with scorer: 22% (44 cases) — severely miscalibrated
- Under-alerts (planner NOISE, scorer SUSPICION+): 90 cases
- Root cause: confidence-as-weight is wrong indicator (measures
  certainty, not anomaly severity). z_score or raw_score better.

### Pending (Fase 2 — calibration, NOT before 2026-08-14)

1. Calibrate weight: experiment with z_score, raw_score * (1 - spoofability),
   or a composite
2. Resolve L-027 or bypass with generic hypotheses (not MITRE-specific)
3. Re-run against corpus, target >70% agreement before considering Fase 3
4. 30-day observation period before any gate that moves verdicts

### Pending (Fase 3 — integration, NOT before Fase 2 validated)

1. Architecture decision: parallel signal (like Grice gate) vs replacement
   of classify_agent_verdict vs scorer factor
2. Full corpus dry-run with same rigor as B-126/B-127
3. Oscillation detection is the primary value-add (ABSTAIN for
   contradictory evidence) — focus integration design on that

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
| **Estado** | DOCUMENTADO — fix arquitectónico pendiente (decisión de diseño: routing al engine del scorer + perfiles de evidencia nuevos) |
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
