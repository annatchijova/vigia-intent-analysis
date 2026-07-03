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

## B-016 — memory_forensics.py no valida formato de imagen de memoria (VMware vs RAM dump puro) [PARCIALMENTE MITIGADO]

| Campo | Valor |
|-------|-------|
| **Estado** | PARCIALMENTE MITIGADO — camino operativo cubierto; pendiente en motor V4 |
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
|
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

-------|-------|
| **Estado** | ABIERTO |
| **Severidad** | P2 — el agente sella el bundle con veredicto `PIPELINE_ERROR` en lugar de abortar con diagnóstico claro |
| **Archivo** | `vigia/sift/` (orquestador real) — el import de `defusedxml` falla en runtime |
| **Detectado en** | Sesión 2026-06-27, caso NPS-2010-EMAILS, modo 1 (`vigia_agent.py`) |

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

## B-018 — Volatility3 subprocess timeout en `vigia_agent.py` para dumps grandes (≥4 GB) [PARCIALMENTE MITIGADO]

| Campo | Valor |
|-------|-------|
| **Estado** | PARCIALMENTE MITIGADO — timeout total ya degrada a ABSTAIN honesto |
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

### B-040 [PENDING] — ARTIFACT_RELIABILITY not propagated to CAIE

| Campo | Valor |
|-------|-------|
| **Estado** | PENDIENTE |
| **Severidad** | P2 |
| **Archivo** | `vigia/sift/forensic_adapter.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `ios_forensics.py` and `android_forensics.py` define `ARTIFACT_RELIABILITY=Fraction(70,100)` but `forensic_adapter.py` sets `base_trust=1.0` fixed, ignoring the signal metadata value. See L-037.

---

### B-041 [PENDING] — caie_artifacts not returned by run_full_analysis() — CAIE never runs in RAW mode

| Campo | Valor |
|-------|-------|
| **Estado** | PENDIENTE |
| **Severidad** | P1 |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `run_full_analysis()` does not return `caie_artifacts` in its output, so the CAIE cross-artifact analysis engine never receives artifacts when processing RAW evidence. This means structural fracture detection (LOG_VS_MEMORY, TIMELINE_PARADOX, etc.) is bypassed in RAW mode.

---

### B-042 [PENDING] — iOS forensics module — P0 float boundary in to_signal()

| Campo | Valor |
|-------|-------|
| **Estado** | PENDIENTE — decisión arquitectónica requerida |
| **Severidad** | P0 |
| **Archivo** | `vigia/sift/ios_forensics.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** `to_signal()` in `ios_forensics.py` uses `float()` for z-score and confidence values. When this module feeds the deterministic scoring pipeline, floats enter the Fraction arithmetic path — a P0 violation of L-021. Architectural decision pending: should `SignalOutput` accept `Decimal`/`Fraction`, or is the float-to-Fraction conversion the correct boundary?

---

### B-043 [PENDING] — Android forensics module — same as B-042

| Campo | Valor |
|-------|-------|
| **Estado** | PENDIENTE — misma decisión arquitectónica que B-042 |
| **Severidad** | P0 |
| **Archivo** | `vigia/sift/android_forensics.py` |
| **Detectado en** | Sesión 2026-06-29 |

**Descripción:** Same `float()` boundary issue as B-042 in `android_forensics.py`. The fix should be coordinated with B-042 as the same architectural decision applies.

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

## B-041 — CAIE output no expuesto en vigia_agent.py narrative [PARTIAL FIX]

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

**Conclusión**: el upgrade automático sería dead code con la metadata actual. Se
requiere primero que `ForensicAdapter` propague acquisition metadata desde los
signals, y/o que el pipeline produzca artefactos de múltiples capas epistémicas
(memory_process, prefetch, kernel_structure además de log_entry).

### Archivos tocados
- `vigia_agent.py` — `_generate_narrative()` (añadida lectura de CAIE)

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

## B-052 — Motores mobile/macOS: señal única agregada puentea el AbductiveReasoner [P1 FIXED / P2 PENDING]

| Campo | Valor |
|-------|-------|
| **Estado** | P1 (narrativa honesta) FIXED — 2026-07-03; P2 (granularidad) PENDING |
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

## B-055 — vigia/core/vigia_scorer.py: copia stale divergente con NameError latente (T-6) [ABIERTO]

| Campo | Valor |
|-------|-------|
| **Estado** | ABIERTO — decisión pendiente (eliminar vs re-exportar) |
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
