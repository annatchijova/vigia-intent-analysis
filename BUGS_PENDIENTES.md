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
→ 163 passed, 6 xfailed
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
