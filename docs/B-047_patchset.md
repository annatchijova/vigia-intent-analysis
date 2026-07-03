# B-047 — Patch set: `_build_correlation_groups()` → `Dict[int, Set[int]]`

**Bug:** `android_forensics.py`, `ios_forensics.py` y `macos_forensics.py` retornan
`List[List[int]]` desde `_build_correlation_groups()`, pero `noisy_or_correlated()`
espera `Dict[int, Set[int]]`. `google_takeout_forensics.py` tiene el formato
correcto y es la semántica de referencia.

**Estrategia:** un helper canónico compartido en `_math_utils.py` (junto a su único
consumidor), los cuatro módulos delegan, y un guard fail-loud en
`noisy_or_correlated` hace imposible reintroducir el formato viejo en silencio.
Mismo criterio que B-023 y B-026 opción B.

**Estado de anclaje de este patch set:**

| Archivo | Anclado contra fuente | Acción |
|---|---|---|
| `vigia/sift/macos_forensics.py` | Sí (fuente completa en sesión) | 2 parches — `apply_b047.py` |
| `vigia/sift/ios_forensics.py` | Sí (fuente completa en sesión) | 2 parches — `apply_b047.py` |
| `vigia/sift/google_takeout_forensics.py` | Sí (fuente completa en sesión) | 2 parches — `apply_b047.py` |
| `vigia/sift/_math_utils.py` | **No** — archivo no visto | Inserción manual (Pasos 1 y 2) |
| `vigia/sift/android_forensics.py` | **No** — archivo no visto | Anchor esperado + verificación (Paso 6) |

El engine `scripts/surgical_patch.py` aborta solo si el conteo del anchor ≠ 1,
así que si algo cambió desde la sesión, falla en seco en vez de parchear mal.

---

## Paso 0 — Precondiciones (no saltear)

```bash
cd ~/ruta/al/repo
git status                      # working tree limpio antes de empezar
git tag pre-b047-correlation-groups-$(date +%Y%m%d)
pytest tests/ -q --no-cov       # baseline esperado: 188 passed, 6 xfailed
```

Después, la verificación que zanja el modo de fallo actual y da el dato que
falta para el Paso 2:

```bash
grep -n -B 2 -A 30 "def noisy_or_correlated" vigia/sift/_math_utils.py
```

Dos cosas a leer en esa salida:

1. **El nombre del segundo parámetro** — se necesita para el guard del Paso 2.
2. **El modo de fallo pre-fix** con lista no vacía:
   - Si el cuerpo hace `.items()` o `.get()` sobre el mapa → hoy explota con
     `AttributeError` en cuanto un caso macOS/iOS/Android produce ≥2 findings
     del mismo `corr_group`. Fail-loud accidental.
   - Si hace membership (`if i in ...`) → `0 in [[0,1]]` es `False` siempre →
     hoy trata todo como independiente en silencio → composite inflado
     (Noisy-OR sin descuento de correlación), sesgo hacia FP sin traza.

Anotar cuál de los dos era en la entrada de registro del Paso 9 — es parte del
audit trail del bug.

---

## Paso 1 — Helper canónico en `_math_utils.py` (inserción manual, código nuevo)

Agregar la función debajo de `noisy_or_correlated()` (o donde convenga en el
archivo, es aditivo). Asegurar que el import de typing del archivo incluya
`Dict`, `List`, `Sequence`, `Set`.

```python
def build_correlation_groups(corr_tags: Sequence[str]) -> Dict[int, Set[int]]:
    """Build the correlation map in the format noisy_or_correlated expects:
    Dict[int, Set[int]] where each finding index maps to the set of its
    correlated peers (same non-empty corr_group tag, self excluded).

    Only groups with >= 2 members produce entries. Findings with an empty
    corr_group are independent and never appear in the map.

    B-047 fix: single shared implementation replacing four per-module copies.
    android/ios/macos returned List[List[int]] — a format this function's
    consumer does not accept; google_takeout_forensics had the correct format
    and this replicates its exact semantics.

    Args:
        corr_tags: corr_group tag of each finding, in finding order.
                   Index i in the returned map refers to corr_tags[i].
    """
    tag_groups: Dict[str, List[int]] = {}
    for i, tag in enumerate(corr_tags):
        if tag:
            tag_groups.setdefault(tag, []).append(i)
    result: Dict[int, Set[int]] = {}
    for indices in tag_groups.values():
        if len(indices) < 2:
            continue
        for idx in indices:
            peers = {j for j in indices if j != idx}
            if idx in result:
                result[idx] |= peers
            else:
                result[idx] = peers
    return result
```

Nota de fidelidad: el bloque `if idx in result: result[idx] |= peers` es copia
textual de la semántica de takeout. Con un solo tag por finding la rama `|=` es
inalcanzable, pero se conserva para equivalencia exacta con la implementación
de referencia — el test de equivalencia lo verifica.

---

## Paso 2 — Guard fail-loud en `noisy_or_correlated` (inserción manual, condicionada al Paso 0)

Insertar como primeras líneas del cuerpo de la función, después del docstring,
antes de cualquier uso del mapa. **Renombrar `corr_map` al nombre real del
segundo parámetro según la salida del grep del Paso 0.**

```python
    if not isinstance(corr_map, dict):
        raise TypeError(
            f"noisy_or_correlated: correlation map must be Dict[int, Set[int]], "
            f"got {type(corr_map).__name__}. "
            f"Use build_correlation_groups() to construct it. (B-047)"
        )
```

`raise`, no `assert` — bajo `python -O` los asserts desaparecen (mismo motivo
que B-011/B-012).

---

## Pasos 3, 4 y 5 — Parches anclados (macos, ios, takeout)

Aplicar con `apply_b047.py` (dry-run por defecto, `--apply` para escribir;
usa el engine `scripts/surgical_patch.py`: conteo de anchor == 1, backup `.bak`,
`ast.parse` post-escritura con restore automático). Los anchors, para review:

### 3. `vigia/sift/macos_forensics.py` — 2 parches

**3a. Import:**

anchor:
```python
from vigia.sift._math_utils import noisy_or_correlated
```
replacement:
```python
from vigia.sift._math_utils import build_correlation_groups, noisy_or_correlated
```

**3b. Método:**

anchor:
```python
    def _build_correlation_groups(self) -> List[List[int]]:
        """Group correlated findings by corr_group tag (P0-003 fix)."""
        groups: Dict[str, List[int]] = {}
        for i, f in enumerate(self._findings):
            if f.corr_group:
                groups.setdefault(f.corr_group, []).append(i)
        return [idxs for idxs in groups.values() if len(idxs) >= 2]
```
replacement:
```python
    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; replaces List[List[int]] format)."""
        return build_correlation_groups([f.corr_group for f in self._findings])
```

`Dict` ya está en el import de typing del módulo y `set` es builtin — no se
toca la línea de typing. Anotación consistente con la que takeout usaba.

### 4. `vigia/sift/ios_forensics.py` — 2 parches

Mismo par anchor/replacement que el Paso 3 (el texto del import y del método es
idéntico carácter a carácter en ambos archivos; cada anchor es único dentro de
su propio archivo).

### 5. `vigia/sift/google_takeout_forensics.py` — 2 parches

**5a. Import:** mismo par que 3a.

**5b. Método** (elimina la implementación local — ahora vive en el helper — y
su docstring con la nota del bug, que queda obsoleta):

anchor:
```python
    def _build_correlation_groups(self) -> Dict[int, set]:
        """Build correlation map in the format noisy_or_correlated expects:
        Dict[int, Set[int]] where each key maps to its correlated peers.

        NOTE: Android/iOS/macOS _build_correlation_groups return List[List[int]]
        which is a latent bug — noisy_or_correlated expects Dict[int, Set[int]].
        This module uses the correct format.
        """
        tag_groups: Dict[str, List[int]] = {}
        for i, f in enumerate(self._findings):
            if f.corr_group:
                tag_groups.setdefault(f.corr_group, []).append(i)
        result: Dict[int, set] = {}
        for indices in tag_groups.values():
            if len(indices) < 2:
                continue
            for idx in indices:
                peers = {j for j in indices if j != idx}
                if idx in result:
                    result[idx] |= peers
                else:
                    result[idx] = peers
        return result
```
replacement:
```python
    def _build_correlation_groups(self) -> Dict[int, set]:
        """Correlation map for noisy_or_correlated — delegates to the shared
        helper in _math_utils (B-047 fix; canonical semantics live there)."""
        return build_correlation_groups([f.corr_group for f in self._findings])
```

---

## Paso 6 — `vigia/sift/android_forensics.py` (verificar antes de aplicar)

No vi el archivo en esta sesión, así que no va en `apply_b047.py`. El registro
B-047 lo agrupa con ios/macos (mismo patrón), y B-045 confirma que comparte
estructura con ios. Anchor **esperado**, a confirmar contra el archivo vivo:

```bash
grep -n -A 7 "def _build_correlation_groups" vigia/sift/android_forensics.py
grep -c "from vigia.sift._math_utils import noisy_or_correlated" vigia/sift/android_forensics.py
```

Si la salida coincide carácter a carácter con el anchor del Paso 3 (probable),
aplicar el mismo par de parches — se pueden agregar dos entradas a
`apply_b047.py` copiando el bloque de ios y cambiando la ruta. Si difiere en
algo, **parar y revisar**: el anchor no es negociable (invariante 1 del
surgical-patcher — conteo exacto 1, o abort).

Al aplicarlo, duplicar en el archivo de tests el test
`test_macos_delegates_and_survives_noisy_or` con el analyzer y el dataclass de
finding de android (nombres a confirmar en el archivo — no los inventé).

---

## Paso 7 — Tests

`test_b047_correlation_groups.py` (adjunto) → colocar en `tests/`. Si el layout
correcto es `vigia/tests/`, mover ahí; los imports son absolutos y no cambian.

Cubre: semántica básica del helper (peers sin self, grupos ≥ 2, tags vacíos
ignorados), equivalencia exacta contra una copia congelada de la implementación
de referencia de takeout, delegación de macos/ios con paso completo por
`noisy_or_correlated` (retorna `Fraction`, no explota), monotonía (score
correlacionado ≤ independiente), y el guard TypeError.

El test del guard requiere el Paso 2 aplicado. Si se posterga el guard, marcar
ese test `xfail` — no borrarlo.

---

## Paso 8 — Verificación post-aplicación

```bash
# El formato viejo ya no existe en ningún módulo SIFT
grep -rn "List\[List\[int\]\]" vigia/sift/*forensics*.py    # esperado: sin resultados

# Los cuatro módulos delegan
grep -rn "return build_correlation_groups" vigia/sift/      # esperado: 4 resultados

# Suite completa
pytest tests/test_b047_correlation_groups.py -v
pytest tests/ -q --no-cov     # esperado: 188 + nuevos passed, 6 xfailed, 0 regresiones
```

Regla de decisión sobre el baseline: si algún test preexistente cambia de
estado, restaurar desde el tag y revisar antes de insistir — en particular si
el modo de fallo pre-fix era el silencioso (membership), un caso del corpus
con findings correlacionados puede haber tenido composite inflado y ahora dar
un score menor. Ese cambio sería **corrección, no regresión**, pero hay que
verificarlo caso por caso y documentarlo, no asumirlo.

---

## Paso 9 — Entrada para `BUGS_PENDIENTES.md`

Reemplazar la entrada B-047 [PENDING] existente por:

```markdown
## B-047 — _build_correlation_groups() retornaba List[List[int]], noisy_or_correlated espera Dict[int, Set[int]] [RESUELTO]

| Campo | Valor |
|-------|-------|
| **Estado** | RESUELTO — commit <hash> |
| **Severidad** | LATENTE → cerrado antes de explotar con corpus grande |
| **Archivos** | `vigia/sift/_math_utils.py`, `android_forensics.py`, `ios_forensics.py`, `macos_forensics.py`, `google_takeout_forensics.py` |
| **Tag de restauración** | `pre-b047-correlation-groups-<fecha>` |
| **Detectado en** | Sesión 2026-06-30 (registro) |
| **Corregido** | <fecha> |

### Descripción

Android/iOS/macOS retornaban `List[List[int]]`; takeout tenía el formato
correcto `Dict[int, Set[int]]`. No explotaba con el corpus actual porque
ningún caso producía >=2 findings con el mismo corr_group en los módulos
afectados.

**Modo de fallo pre-fix confirmado (grep sobre noisy_or_correlated):**
<completar: AttributeError con lista no vacía / inflado silencioso por
membership — ver B-047_patchset.md Paso 0>

### Fix aplicado

1. Helper canónico `build_correlation_groups(Sequence[str]) -> Dict[int, Set[int]]`
   en `_math_utils.py`, junto a su único consumidor. Semántica exacta de la
   implementación de referencia de takeout (peers sin self, solo grupos >= 2,
   tags vacíos ignorados).
2. Los 4 módulos delegan al helper — elimina la cuadruplicación que originó
   el bug.
3. Guard fail-loud en `noisy_or_correlated`: `TypeError` si el mapa no es
   dict (raise, no assert — criterio B-011/B-023/B-026 opción B). Hace
   imposible reintroducir el formato viejo en silencio.

### Verificación

pytest tests/test_b047_correlation_groups.py -v → todos passed
pytest tests/ -q --no-cov → 188 + nuevos passed, 6 xfailed, 0 regresiones
grep: 0 ocurrencias de List[List[int]] en módulos SIFT; 4 delegaciones al helper.
```

---

## Fuera de alcance de este patch set (deliberado)

- **L-041** — el propio registro lo dice: no implementar el pattern set
  transaccional sin datos de calibración (riesgo FP sobre SMS legítimos de
  agenda). Queda en cola hasta tener corpus.
- **L-037a** — diseño multi-adquisición, no un fix puntual; el merge order ya
  lo soporta, falta que los módulos declaren metadata propia. Sesión aparte.
- **Wiring de `macos_forensics.py`** — pendiente de tu confirmación: no hay
  B-entry de cableado para macOS (B-045 cubrió Android/iOS, B-046 Takeout).
  Si `_build_orchestrator_kwargs()` no detecta `_MACOS_MARKER_FILES` y el shim
  no tiene bloque para `MacOSForensicsAnalyzer`, este fix corre sobre código
  que nunca se invoca — B-045 versión macOS.

---

*B-047 patch set — preparado por Claude (Colectivo VIGÍA), 2026-07-01.*
*Disciplinas aplicadas: audit-before-patch, surgical-patcher, validate-at-the-boundary, git-discipline.*
