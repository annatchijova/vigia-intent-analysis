# Auditoría — B-047 correlation groups type mismatch

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Tag de restauración:** `pre-b047-correlation-audit-20260703-044406`
**Alcance:** `_build_correlation_groups()` en los motores mobile/macOS y su
consumo por `noisy_or_correlated()` (`vigia/sift/_math_utils.py`).
**Motivación:** `_build_correlation_groups()` retorna `List[List[int]]` pero
`noisy_or_correlated` espera `Dict[int, Set[int]]`; se manifiesta solo con ≥2
findings compartiendo `corr_group`. ¿Path exacto? ¿Qué casos reales lo
triggean? ¿Fix mínimo seguro?
**Método:** lectura de código + ejecución del path correlacionado sobre
evidencia real (tuck-2019, 23 findings correlacionados) + prueba del guard.
**Acción tomada:** NINGUNA sobre el código. Solo investigación y este documento.

---

## Resumen ejecutivo

1. **B-047 ya está CORREGIDO en el código vivo** (commit `d8ce147`, "fix B-047
   — correlation groups unified to Dict[int, Set[int]]"). Los cuatro motores
   (android, ios, macos, google_takeout) delegan al helper canónico
   `build_correlation_groups()` que retorna `Dict[int, Set[int]]`, y
   `noisy_or_correlated` tiene un guard fail-loud (`TypeError`) contra el
   formato viejo. **No hay `List[List[int]]` residual en ningún motor SIFT.**

2. **Pero el bug tracker miente: la entrada sigue marcada `[PENDING]`** en
   `BUGS_PENDIENTES.md:2425` y `BUGS_PENDIENTES_EN.md:2636`, y además tiene
   **dos errores factuales** que hay que corregir al cerrarla (§4). La acción
   de esta auditoría es documental: la corrección de código ya ocurrió; falta
   sincronizar el tracker.

3. **El path exacto que lo disparaba** (§2): `analyze()` → `corr_groups =
   self._build_correlation_groups()` → `if corr_groups:` (lista no vacía =
   truthy) → `noisy_or_correlated(sev, corr_groups, …)` →
   `sorted(correlation_groups.items())` → **`AttributeError: 'list' object has
   no attribute 'items'`** (pre-guard) o **`TypeError` explícito** (post-guard).
   Fail-loud, no corrupción de score.

4. **Caso real que lo triggea — reproducido en vivo:** `cases/tuck-2019-macos`
   produce **23 findings, todos `corr_group="browser_suspicious"`** → el path
   correlacionado con ≥2 miembros. Ejecutado hoy con el código corregido:
   `composite_score = 19/20`, sin crash. Pre-`d8ce147` este mismo caso habría
   reventado con `AttributeError` en `noisy_or_correlated`. Es el gatillo
   canónico del bug — y la razón de que B-048 (wiring macOS) lo mencione.

5. **Fix mínimo seguro:** ninguno de código — ya está aplicado y con 17 tests
   de regresión pasando (`vigia/tests/test_b047_correlation_groups.py`). El
   único cambio pendiente es **documental**: mover la entrada a `[RESUELTO]`
   con el modo de fallo y las correcciones factuales de §4.

---

## 1. Estado verificado del código (2026-07-03)

| Verificación | Comando | Resultado |
|---|---|---|
| `List[List[int]]` residual en motores | `grep "List\[List\[int\]\]" vigia/sift/*forensics*.py` | solo en **comentarios** ("replaces List[List[int]] format") — 0 en código |
| Delegación al helper | `grep "return build_correlation_groups" vigia/sift/*.py` | **4** (android, ios, macos, google_takeout) |
| Helper canónico único | `grep "def build_correlation_groups" vigia/sift/_math_utils.py` | **1** (`:255`) |
| Guard en el consumidor | `_math_utils.py:225-230` | `TypeError` si `correlation_groups` no es dict ni None |
| Tests de regresión | `pytest vigia/tests/test_b047_correlation_groups.py` | **17 passed** |

Firma real de `noisy_or_correlated` (`_math_utils.py:219-224`):
`(severities, correlation_groups: Optional[Dict[int, Set[int]]] = None,
penalty, penalty_map)`. Consume `correlation_groups.items()` en `:237`.

Helper canónico (`_math_utils.py:255-287`): `build_correlation_groups(
corr_tags: List[str]) -> Dict[int, Set[int]]` — agrupa por tag no vacío, solo
grupos con ≥2 miembros, cada índice → set de sus pares (self excluido).

Los cuatro motores mobile (`macos_forensics.py:358-361` y equivalentes)
delegan idéntico:
```python
def _build_correlation_groups(self) -> Dict[int, set]:
    """...B-047 fix; replaces List[List[int]] format..."""
    return build_correlation_groups([f.corr_group for f in self._findings])
```

Los cinco motores Windows (memory, network, event_log, registry, disk)
**nunca tuvieron el bug**: construyen el `corr_groups` como dict inline
(`memory_forensics.py:541` `corr_groups: Dict[int, set] = {}`, etc.). No
usan el helper pero ya emiten el formato correcto.

---

## 2. Path exacto de código (modo de fallo pre-fix)

```
MacOSForensicsAnalyzer.analyze()                       macos_forensics.py:339
        │  corr_groups = self._build_correlation_groups()
        │      (pre-fix: List[List[int]] — una lista por grupo)
        │      (post-fix: Dict[int, Set[int]] vía helper)
        ▼
if corr_groups:                                        (implícito en el flujo)
        │  lista NO vacía → truthy → entra al bloque de correlación
        ▼
noisy_or_correlated(severities, corr_groups, Fraction(15,100))   macos:340
        │
        ▼
_math_utils.py:225   if not isinstance(correlation_groups, dict):   ← GUARD (post-fix)
        │                raise TypeError(...)                          → TypeError explícito
        │
_math_utils.py:237   for idx, group in sorted(correlation_groups.items())  ← (pre-guard)
                         → AttributeError: 'list' object has no attribute 'items'
```

**Condición de disparo:** `_build_correlation_groups()` devuelve una lista NO
vacía, lo que ocurre **si y solo si ≥2 findings comparten el mismo
`corr_group` no vacío** (con 0-1 findings correlacionados la lista queda vacía
→ falsy → el bloque de correlación se saltea y nunca se llama al path roto).

**Modo de fallo:** fail-loud en ambas versiones — `AttributeError` opaco
(pre-guard) o `TypeError` con mensaje y referencia a `build_correlation_groups`
(post-guard, `:226-230`). En ningún caso hubo corrupción silenciosa de score:
el `composite` nunca se computó con el formato inválido. El `analyze()`
crasheaba entero → el motor caía → (post-tanda-3 de robustez) se marcaría como
`*_UNANALYZED`, pre-eso quedaba como excepción capturada por el shim.

Prueba del guard en vivo:
```
noisy_or_correlated([1/2, 1/2], [[0, 1]], 15/100)
→ TypeError: noisy_or_correlated: correlation_groups must be Dict[int, Set[int]] or None...
```

---

## 3. Casos reales del corpus que lo triggean

| Caso | Motor | Findings correlacionados | ¿Dispara? | Estado hoy |
|---|---|---|---|---|
| **`cases/tuck-2019-macos`** | macOS | **23**, todos `corr_group="browser_suspicious"` | **SÍ** (23 ≥ 2) | `composite=19/20`, sin crash `[REPRODUCIDO]` |
| `smoke_b048.py` (fixture sintético) | macOS | 2 URLs `corr_group="browser_suspicious"` | SÍ (2 ≥ 2) | diseñado explícitamente para ejercitar el path B-047 |
| Owl-Android (`evidence/owl-2019-nexus5-*`) | Android | 1 finding | NO (1 < 2) | lista vacía → path se saltea |
| Magnet iOS/Android (EBS-JSON) | — | van por adaptador EBS, no por los engines mobile | NO | no invoca `_build_correlation_groups` |

**tuck-2019 es el caso canónico**: 23 findings de Safari sospechoso, todos en
el mismo `corr_group`. Es exactamente el "≥2 findings compartiendo corr_group"
del enunciado, y con el corpus actual es el único caso real (no sintético) que
lo alcanza. Por eso el bug era LATENTE hasta que se cableó macOS (B-048) y se
descargó evidencia macOS con múltiples findings correlacionados: la
combinación B-048 + tuck-2019 es la que habría explotado B-047 en producción
si `d8ce147` no lo hubiera precedido.

Nota: la entrada `[PENDING]` afirma "ningún caso del corpus produce ≥2 findings
con el mismo corr_group" — **eso ya no es cierto**: tuck-2019 tiene 23. La
afirmación era válida cuando se escribió (antes de descargar tuck), no hoy.

---

## 4. Fix mínimo seguro

**De código: ninguno — ya aplicado en `d8ce147` y verificado (17 tests,
tuck-2019 sin crash).** El diseño del fix (helper canónico + delegación +
guard fail-loud) es el correcto: elimina la cuadruplicación que originó el bug
e imposibilita reintroducir el formato viejo en silencio.

**Documental (lo único pendiente): mover B-047 a `[RESUELTO]`** en ambos
trackers, corrigiendo dos errores factuales de la entrada `[PENDING]` actual:

1. **Ubicación de `noisy_or_correlated`:** la entrada dice
   `vigia/core/noisy_or.py` — **no existe**; está en `vigia/sift/_math_utils.py:219`.
2. **Módulos afectados:** la entrada lista 3 (android, ios, macos) y omite que
   `google_takeout_forensics` ya tenía el formato correcto y que el fix
   unificó los **cuatro** al helper. Los 5 motores Windows nunca estuvieron
   afectados (dict inline).
3. **Modo de fallo:** la entrada dice "TypeError"; pre-guard era
   `AttributeError` (`.items()` sobre lista). Post-fix es `TypeError` por el
   guard nuevo. Vale documentar ambos.

Contenido de reemplazo sugerido: la entrada ya redactada en
`B-047_addendum.md:117-163` (sección "Entrada final para BUGS_PENDIENTES.md"),
que tiene el modo de fallo confirmado y los 4 módulos — usar esa, actualizando
el `<hash>` a `d8ce147` y el estado a RESUELTO.

**Riesgo de la acción documental:** nulo (no toca código). **Riesgo de NO
hacerla:** un lector del tracker cree que hay un crash latente sin corregir,
puede intentar "arreglar" algo ya arreglado y romper la delegación, o bloquear
un merge por un bug inexistente.

---

## 5. Conclusión

B-047 es un **falso pendiente**: el código está correcto desde `d8ce147`, con
guard y tests, y el caso que lo disparaba (tuck-2019, 23 findings
correlacionados) corre hoy sin crash produciendo `composite=19/20`. La única
acción es sincronizar `BUGS_PENDIENTES{,_EN}.md` a `[RESUELTO]` con las tres
correcciones factuales de §4 — la entrada de reemplazo ya existe en
`B-047_addendum.md`. No hay fix de código que implementar.

---

## 6. Limitaciones de esta auditoría

1. No se corrió la suite completa en esta sesión (sí los 17 tests de B-047 +
   la ejecución directa de tuck-2019); la afirmación "0 regresiones" se apoya
   en el commit `d8ce147` y su addendum, no en una corrida nueva de los 198.
2. No se auditó si algún motor futuro (no-mobile, no-Windows) podría reintroducir
   `List[List[int]]` — el guard lo atraparía en runtime, pero no hay lint
   estático que lo prevenga en tiempo de escritura.

---

*Auditoría B-047 — el bug ya está muerto; lo que sigue vivo es su entrada en el
tracker. Cerrar el ticket es el fix.*
