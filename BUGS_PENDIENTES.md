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

---
