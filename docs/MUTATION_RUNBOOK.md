# Runbook de mutation testing — operación y averías

Documento **autosuficiente**. Está escrito para que cualquier persona o agente
que llegue sin contexto previo pueda ejecutar, leer y reparar el barrido de
mutación sin preguntarle a nadie.

- **Qué es y por qué**: `docs/MUTATION_TESTING.md`
- **Resultados medidos y triaje**: `docs/MUTATION_BASELINE.md`
- **Este documento**: cómo se opera y qué hacer cuando falla.

Todas las averías de §3 **ocurrieron de verdad** al montar esto el 2026-08-01.
No son hipótesis: son el registro de lo que se rompió, cómo se diagnosticó y
cómo se arregló.

---

## 1. Operación normal

No hay que hacer nada. `.github/workflows/mutation.yml` corre solo los **lunes
a las 03:00 UTC**: un job por módulo, en paralelo.

Para leer el resultado: pestaña **Actions** → corrida de *VIGÍA Mutation
Testing*. Cada job escribe su resumen:

```
killed=172 survived=250 total=422 score=40%
```

Cada job publica además un artefacto `mutation-<modulo>` con dos ficheros:

| Fichero | Contenido |
|---------|-----------|
| `survivors.txt` | Sólo los supervivientes. **Es la lista de trabajo.** |
| `all.txt` | Todos los mutantes con su estado. Sirve para recontar. |

Para lanzarlo a mano: **Actions → VIGÍA Mutation Testing → Run workflow**. El
campo `only_mutate` acepta la ruta de un módulo (p. ej. `vigia_scorer.py`);
vacío mide todos.

### Cómo leerlo sin equivocarse

1. **Comparar el total, no sólo el porcentaje.** Con
   `mutate_only_covered_lines = true`, escribir tests **agranda** el universo
   de mutantes: líneas antes no cubiertas pasan a ser mutables. En la primera
   línea base `collapse_decision.py` pasó de `4/29` a `35/35` — numerador y
   denominador se movieron a la vez.
2. **Un superviviente no es siempre un defecto.** Tres clases, y separarlas es
   el trabajo real: hueco de test genuino / mutante equivalente (no altera el
   comportamiento observable) / rama defensiva inalcanzable. Ver
   `MUTATION_TESTING.md` §7.
3. **Score bajo ≠ código malo.** Significa "tests flojos en esa zona".

---

## 2. Ejecución local

### 2.1 Entorno desde cero

```bash
pip install -r requirements.txt -r requirements-ci.txt
pip install scipy mutmut
```

Si `pip install mcp` falla con `Cannot uninstall PyJWT ... RECORD file not
found`, el intérprete tiene PyJWT del gestor de paquetes del sistema. Es
`KNOWN_LIMITATIONS.md` L-045. Dos salidas:

- usar un virtualenv limpio (recomendado), o
- `pip install --ignore-installed PyJWT mcp`.

Sin `mcp`, los módulos que importan `vigia/vigia_sift_bridge.py` no colectan.
No afecta al barrido: ya están excluidos en la selección de tests y no cubren
la ruta de veredicto.

### 2.2 Requisito previo — suite verde

```bash
python3 -m pytest tests/ vigia/tests/ -q --tb=short --no-cov
```

**Sobre una suite roja el mutation score no significa nada**: todo mutante se
declara muerto por el fallo preexistente y el resultado sale ~100%. El
workflow tiene un job `baseline` que lo comprueba antes de mutar. En local hay
que comprobarlo a mano.

### 2.3 Barrido

```bash
python3 -m mutmut run --max-children 4   # ojo: los 8 módulos son ~6 horas
python3 -m mutmut results                # supervivientes
python3 -m mutmut results --all true     # todos, con estado
python3 -m mutmut show <nombre_mutante>  # el diff exacto de un mutante
```

### 2.4 Acotar a un módulo

**`mutmut run <patrón>` NO acota nada** — comprobado: con cinco patrones de
módulo ejecutó los 7.043 mutantes igual. El único mecanismo que funciona es
`only_mutate` en `pyproject.toml`. El ciclo:

1. editar `only_mutate` dejando sólo el módulo deseado;
2. `rm -rf mutants && python3 -m mutmut run --max-children 4`;
3. **restaurar `pyproject.toml`** en cuanto termine la generación — el sandbox
   `mutants/` ya tiene su propia copia y no la vuelve a leer.

El paso 3 importa: `tests/test_mutation_config_contract.py` exige que
`vigia_scorer.py` siga en `only_mutate`, así que un acotado olvidado deja la
suite roja. Es deliberado — el contrato existe para que un acotado temporal no
se convierta en el alcance permanente sin que nadie lo note.

### 2.5 Espacio en disco

`mutants/` ocupa **~300 MB** con los 8 módulos (137 MB sólo el scorer mutado:
mutmut escribe cada variante en línea). Está en `.gitignore`. Se puede borrar
en cualquier momento; sólo cuesta regenerarlo.

---

## 3. Averías conocidas

### 3.1 `failed to collect stats. runner returned 1`

**Qué significa.** Antes de mutar, mutmut corre la suite entera para mapear qué
test cubre qué función. Corre con `-x`: **un solo test que falle aborta el
barrido completo**. El mensaje no dice cuál.

**Cómo encontrar el culpable.** El log muestra el `FAILED` justo encima del
traceback. Si no aparece, activar el modo detallado añadiendo `debug = true`
en la sección `[tool.mutmut]` de `pyproject.toml`, relanzar, y **quitarlo
después** (imprime la suite entera).

**Causas vistas, en orden de frecuencia:**

**a) Tests que inspeccionan texto fuente en vez de ejecutar comportamiento.**
Dentro de `mutants/`, el fuente contiene *todas* las variantes mutantes en
línea (`x_funcname__mutmut_N`, literales envueltos como `"XXFOOXX"`). Un test
que hace regex sobre `caie.py`, `inspect.getsource`, o `rglob` de `*.md` lee
artefactos del harness y falla por una razón que no es la lógica bajo prueba.
Ya hay cuatro excluidos por esto (`MUTATION_TESTING.md` §5). **Si aparece uno
nuevo: excluirlo sólo si no puede matar ningún mutante de `only_mutate`** —
es decir, si no ejecuta ese código. Si sí lo ejecuta, excluirlo falsea el
score y hay que arreglar el test.

**b) Ficheros de datos ausentes.** Si la suite falla dentro de `mutants/` con
`FileNotFoundError`, falta algo en `also_copy`. Añadirlo. El síntoma peligroso
es el contrario: si esto pasa desapercibido, **todos** los mutantes se
declaran muertos y el score sale 100% falso.
`tests/test_mutation_config_contract.py` lo cubre.

**c) Fallo que sólo ocurre bajo mutmut.** Ver §3.4.

### 3.2 `BadTestExecutionCommandsException` / pytest sale con código 4

**Qué significa.** Código 4 de pytest = error de uso. Casi siempre: mutmut pasó
un identificador de test que ya no resuelve (`ERROR: not found: ...`).

**Caso real y su causa raíz.** Ocurrió porque `tests/caie/test_canonical_cases.py`
pasaba un **generador** a `@pytest.mark.parametrize`. Un generador se agota al
consumirse y el objeto queda capturado en el marcador, a nivel de módulo.
mutmut colecta varias veces en el mismo proceso (`list_all_tests`, `stats`,
`clean run`), así que la segunda colección recibía un generador vacío: los 52
casos canónicos dejaban de existir y sus identificadores no resolvían.

**Cómo diagnosticarlo:** `debug = true` en `[tool.mutmut]` hace que se imprima
el error real de pytest, que nombra el identificador que no resuelve.

**Prevención activa:** `tests/test_parametrize_argvalues_are_reiterable.py`
cierra esta clase — incluido un barrido AST contra expresiones generadoras
usadas como `argvalues`. Si ese test falla, el defecto ha vuelto.

### 3.3 La suite se pone roja *después* de correr mutmut

Síntoma: tests que pasaban empiezan a fallar sin que se haya tocado el código.

**Causa:** existe `mutants/`, y algún test barre el árbol entero
(`grep -r .`, `rglob`) contando la copia mutada como código del repositorio.
Pasó con `test_b117_stale_formula_sweep` y —más grave—
`test_b224_contradiction_detector_dormancy`, cuya única función es afirmar que
cierta regla no tiene productor *en todo el repositorio*: contaba
`mutants/vigia_agent.py` como productor nuevo.

**Arreglo:** añadir `--exclude-dir=mutants` al `grep`, o `"mutants" not in
p.parts` al `rglob`. Hay tres precedentes en el árbol.

**Atajo de diagnóstico:** `rm -rf mutants` y volver a correr. Si se pone verde,
es esto.

### 3.4 Un test falla sólo dentro de mutmut y no se reproduce fuera

Antes de excluir nada, comprobar los cinco contextos —así se distinguió un
problema del harness de un defecto real:

| Contexto | Comando |
|----------|---------|
| Aislado, en el sandbox | `cd mutants && pytest <ruta_del_test>` |
| Aislado, con el entorno de stats | `MUTANT_UNDER_TEST=stats MUTMUT_DEPENDENCY_DEPTH=-1 pytest <ruta>` |
| Suite completa, subproceso | `cd mutants && pytest <selección completa>` |
| Suite completa, **in-process** | `python3 -c "import os,pytest; os.chdir('mutants'); pytest.main([...])"` |
| mutmut real | `python3 -m mutmut run` |

El cuarto es el que más se parece a mutmut: corre pytest **dentro del mismo
proceso**, que es donde aparecen los fallos por estado global que no sobrevive
a una segunda colección. Si falla ahí, es un defecto real de la suite (fue el
caso del generador, §3.2). Si sólo falla en el quinto, es interacción con el
harness.

**Anomalía abierta:** `vigia/tests/test_lr_calibrator_serialization.py` falla
sólo bajo la fase `stats` (2 de 2 corridas) y pasa en los otros cuatro
contextos. Sin diagnóstico. Excluida, con el razonamiento completo en
`MUTATION_TESTING.md` §5.1. **Si alguien la diagnostica, actualizar esa
sección y quitar la exclusión.**

### 3.5 El job de CI se cancela por tiempo

El tope **duro** de un job en GitHub Actions es 360 minutos; no se puede subir.

Para redimensionar tras añadir módulos, con el ritmo medido (19,5
mutantes/min con `--max-children 4` en 4 CPU):

```
mutantes ≈ (nº de líneas con "__mutmut_" en mutants/<modulo>) × 0,49
minutos  ≈ mutantes / 19,5
```

Los 8 módulos en un solo job son ~359 min: **no caben**. Por eso el workflow
usa `strategy.matrix` con un job por módulo. `tests/test_mutation_config_contract.py`
verifica que el timeout siga por debajo de 360 y que la matriz cubra
exactamente `only_mutate` — dos listas que deben coincidir se desincronizan
solas, y un módulo declarado pero ausente de la matriz no se mediría nunca sin
que nada falle.

---

## 4. Cómo ampliar el alcance

1. Subir la **cobertura de línea** del módulo primero. Mutar código sin tests
   produce supervivientes triviales y sólo añade ruido al triaje.
2. Añadirlo a `only_mutate` en `pyproject.toml`.
3. Añadirlo a `strategy.matrix.module` en `.github/workflows/mutation.yml`.
   El contrato falla si se olvida este paso.
4. Recalcular el tiempo con la fórmula de §3.5.
5. Medir, triar, y registrar el resultado en `docs/MUTATION_BASELINE.md`.

## 5. Cómo retirar todo esto

Si alguna vez se decide que no compensa, hay que quitar **el conjunto
completo**, no sólo la herramienta:

- `[tool.mutmut]` en `pyproject.toml`
- `.github/workflows/mutation.yml`
- `tests/test_mutation_config_contract.py`
- `docs/MUTATION_TESTING.md`, `docs/MUTATION_BASELINE.md`, este fichero
- las entradas `mutants/`, `.mutmut-cache`, `mutmut-stats.json` de `.gitignore`

**No retirar** `tests/test_parametrize_argvalues_are_reiterable.py`,
`tests/test_collapse_decision_boundaries.py`, ni los `--exclude-dir=mutants`:
son correcciones de defectos reales del repositorio, independientes de la
herramienta que los expuso.
