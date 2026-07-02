# B-047 — Addendum de verificación (2026-07-01)

Complementa `B-047_patchset.md` con los resultados de la verificación contra
el repo vivo. Donde este addendum contradice al patchset original, gana el
addendum — el original se escribió antes de ver `_math_utils.py` y
`android_forensics.py`.

---

## 1. Resultados de la verificación

**Baseline real: 188 passed, 6 xfailed — pero con el comando completo.**
El comando del patchset original (`pytest tests/ -q --no-cov`) colecta solo
parcialmente y da 163: falta `vigia/tests/`. El comando correcto, de acá en
adelante y para toda verificación:

```bash
PYTHONPATH=$(pwd) python3 -m pytest tests/ vigia/tests/ -q --no-cov --ignore=tests/integration
```

**`noisy_or_correlated` — firma real confirmada** (líneas 219-224 de
`_math_utils.py`): cuatro parámetros — `severities`, `correlation_groups`
(no `corr_map` como decía el placeholder del Paso 2), `penalty`,
`penalty_map`. El guard del patchset se reescribió contra esta firma y
respeta el `None` por defecto.

**Modo de fallo pre-fix confirmado:** de las dos hipótesis del diseño
(AttributeError vs. inflado silencioso), es la primera. La línea
`for idx, group in sorted(correlation_groups.items())` llama `.items()`
directo: con el formato viejo y ≥2 findings del mismo `corr_group`, la lista
no vacía pasa el `if correlation_groups:` y revienta con
`AttributeError: 'list' object has no attribute 'items'`. Fail-loud
accidental — no corrupción de score — pero un crash sin manejar en cualquier
caso real con findings correlacionados en macos/ios/android. El corpus
actual nunca lo disparó porque ningún caso produjo 2+ findings correlacionados
en esos módulos (Owl-Android: 1 finding → lista vacía → falsy → salta el
bloque).

**Semántica de correlación confirmada** (relevante para el test de
monotonía): mapa vacío o `None` → Noisy-OR independiente puro; con
correlación, el miembro de menor severidad de cada par se multiplica por
`(1 - penalty)`. Correlacionado ≤ independiente por construcción. La
"asunción documentada" del test pasó a hecho verificado.

**`android_forensics.py` — promovido de "esperado" a verificado:** método en
líneas 320-326, idéntico carácter a carácter al patrón de ios/macos; import
de `noisy_or_correlated` con conteo exactamente 1. Entra al script principal.

---

## 2. Cambios respecto al patchset original

| Paso original | Estado |
|---|---|
| Paso 1 (helper, inserción manual) | Reemplazado por `apply_b047_mathutils.py` — anchor real: el helper se inserta entre el cierre de `noisy_or_correlated` y `def apply_artifact_reliability(` |
| Paso 2 (guard, inserción manual) | Reemplazado por `apply_b047_mathutils.py` — anchor real: la firma completa + primera línea del cuerpo; parámetro real `correlation_groups`, contempla `None` |
| Paso 6 (android manual) | Obsoleto — android verificado, incluido en `apply_b047.py` |
| Paso 7 (tests) | Ubicación: `vigia/tests/` (patrón de la casa: `test_lr_calibrator_serialization.py` y `adversarial/` de sift viven ahí). Se agregó `test_android_delegates_via_duck_typing` — 17 tests nuevos en total |
| Paso 8 (verificación) | Comando pytest corregido (ver arriba) |

El tag de restauración **ya existe**: `pre-b047-correlation-groups-20260701`
(quedó creado en el primer intento, antes del falso negativo de los 163).
No repetir el comando — daría "already exists".

---

## 3. Orden de ejecución consolidado

```bash
cd ~/vigia-repo
source .venv/bin/activate

# Mover los artefactos nuevos/actualizados (los dos primeros PISAN los que ya moviste)
mv -f ~/Downloads/apply_b047.py ~/vigia-repo/apply_b047.py
mv -f ~/Downloads/B-047_addendum.md ~/vigia-repo/B-047_addendum.md
mv ~/Downloads/apply_b047_mathutils.py ~/vigia-repo/apply_b047_mathutils.py
mv ~/Downloads/test_b047_correlation_groups.py ~/vigia-repo/vigia/tests/test_b047_correlation_groups.py

# Dry-runs (leer la salida antes de aplicar; abortan si algún anchor no cuenta 1)
python3 apply_b047_mathutils.py
python3 apply_b047.py

# Aplicar — mathutils PRIMERO (el helper debe existir antes de que los módulos lo importen)
python3 apply_b047_mathutils.py --apply
python3 apply_b047.py --apply

# Verificación estructural
grep -rn "List\[List\[int\]\]" vigia/sift/*forensics*.py     # esperado: sin resultados
grep -rn "return build_correlation_groups" vigia/sift/       # esperado: 4 resultados
grep -n "def build_correlation_groups" vigia/sift/_math_utils.py   # esperado: 1

# Tests nuevos, después suite completa
PYTHONPATH=$(pwd) python3 -m pytest vigia/tests/test_b047_correlation_groups.py -v --no-cov
PYTHONPATH=$(pwd) python3 -m pytest tests/ vigia/tests/ -q --no-cov --ignore=tests/integration
# esperado: 205 passed (188 + 17 nuevos), 6 xfailed, 0 regresiones

# Cierre
rm vigia/sift/*.bak vigia/sift/_math_utils.py.bak 2>/dev/null   # opcional, tras verificar
git add -A
git commit -m "POST HACKATHON: fix B-047 — correlation groups unified to Dict[int, Set[int]] (shared helper + fail-loud guard)"
```

Regla de decisión: si la suite completa da algo distinto de 205/6, restaurar
(`git checkout .` o los `.bak`) y traer la salida antes de insistir. Con el
modo de fallo confirmado como AttributeError (no inflado silencioso), **no**
se esperan cambios de score en el corpus existente — ningún caso ejercitaba
el path correlacionado en los módulos afectados.

---

## 4. Entrada final para `BUGS_PENDIENTES.md`

Reemplaza tanto la entrada B-047 [PENDING] como la plantilla del Paso 9 del
patchset (esta versión tiene el modo de fallo completado):

```markdown
## B-047 — _build_correlation_groups() retornaba List[List[int]], noisy_or_correlated espera Dict[int, Set[int]] [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit <hash> |
| **Severidad** | LATENTE → cerrado antes de explotar con corpus grande |
| **Archivos** | `vigia/sift/_math_utils.py`, `android_forensics.py`, `ios_forensics.py`, `macos_forensics.py`, `google_takeout_forensics.py` |
| **Tag de restauración** | `pre-b047-correlation-groups-20260701` |
| **Detectado en** | Sesión 2026-06-30 |
| **Corregido** | 2026-07-01 |

### Descripción

Android/iOS/macOS retornaban `List[List[int]]`; takeout tenía el formato
correcto `Dict[int, Set[int]]`. No explotaba con el corpus actual porque
ningún caso producía >=2 findings con el mismo corr_group en los módulos
afectados (Owl-Android: 1 finding → lista vacía → falsy → salta el bloque
de correlación).

**Modo de fallo pre-fix confirmado (2026-07-01, grep sobre repo vivo):**
`sorted(correlation_groups.items())` sobre lista no vacía →
`AttributeError: 'list' object has no attribute 'items'` → crash de
`analyze()` en cualquier caso real con findings correlacionados. Fail-loud
accidental, no corrupción silenciosa de score — el composite nunca se
computó con el formato inválido.

### Fix aplicado

1. Helper canónico `build_correlation_groups(List[str]) -> Dict[int, Set[int]]`
   en `_math_utils.py`, junto a su único consumidor. Semántica exacta de la
   implementación de referencia de takeout (peers sin self, solo grupos >= 2,
   tags vacíos ignorados).
2. Los 4 módulos delegan al helper — elimina la cuadruplicación que originó
   el bug.
3. Guard fail-loud en `noisy_or_correlated`: `TypeError` explícito si
   `correlation_groups` no es dict ni None (raise, no assert — criterio
   B-011/B-023/B-026 opción B). Reemplaza el AttributeError opaco y hace
   imposible reintroducir el formato viejo en silencio.

### Verificación

17 tests nuevos en `vigia/tests/test_b047_correlation_groups.py` (semántica
del helper, equivalencia contra la implementación de referencia congelada,
delegación de los 4 módulos, monotonía correlado<=independiente, guard).
Suite completa: 205 passed, 6 xfailed, 0 regresiones.
grep: 0 ocurrencias de List[List[int]] en módulos SIFT; 4 delegaciones.
```

---

*B-047 addendum — Claude (Colectivo VIGÍA), 2026-07-01. Verificación en repo
vivo por Anna Tchijova (LaBestia).*
