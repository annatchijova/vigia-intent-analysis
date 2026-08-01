*[English](./MUTATION_TESTING.md) · Español*

# Mutation Testing — VIGÍA

**Estado:** infraestructura activa. Alcance: ruta de veredicto sellado.
**Herramienta:** `mutmut` 3.7. **Configuración:** `[tool.mutmut]` en `pyproject.toml`.

---

## 1. Qué mide, y por qué no es cobertura

Mutation testing no prueba el código: prueba **la suite de tests**. Inyecta un
defecto deliberado y pequeño en el fuente — un *mutante* — y ejecuta los tests
contra esa versión rota.

- Si algún test falla, el mutante está **muerto** (killed). La suite detecta ese
  cambio de lógica.
- Si todos los tests pasan, el mutante **sobrevive**. Existe una modificación
  real del comportamiento que nadie nota.

**Mutation score = mutantes muertos / mutantes ejecutados.**

La distinción operativa frente a la cobertura de línea:

| Métrica | Pregunta que responde |
|---------|-----------------------|
| Cobertura de línea | ¿Se **ejecutó** esta línea durante los tests? |
| Mutation score | ¿Se **verificó**? Si la rompo, ¿falla algo? |

Una línea puede estar al 100% de cobertura y al 0% de mutation score: si un test
la ejecuta pero no hace ningún `assert` sobre su efecto, está *visitada*, no
*verificada*.

## 2. Por qué VIGÍA en particular

Tres razones específicas de este proyecto, no genéricas:

1. **La ruta de veredicto es aritmética de umbrales.** `vigia_scorer.py` son
   ~1.900 líneas de comparaciones, `Fraction`, tablas de lookup y gates
   (`n_artifacts < 2`, `_n_domains >= 2 and (_n_gate_arts >= 4 or ...)`). Es
   código donde el operador mutado **es** la lógica de negocio. Un off-by-one
   aquí no revienta: emite otro veredicto, y lo sella.
2. **El listón Daubert.** Si un veredicto MALICE puede acabar en un tribunal,
   "los tests pasan" es más débil de lo que parece. El mutation score es la
   evidencia de que la suite **discrimina**, no sólo de que existe.
3. **Desarrollo asistido por agentes.** Es la defensa más directa contra el
   fallo que `docs/ENGINEERING_DISCIPLINE.md` y la disciplina de parcheo
   quirúrgico intentan prevenir: un modelo reescribe más de lo que pretendía y
   la suite lo aprueba.

## 3. Cómo se ejecuta

```bash
# Barrido completo del alcance configurado (largo — ver §6).
python3 -m mutmut run --max-children 4

# Resultados: resumen y listado de supervivientes.
python3 -m mutmut results

# Ver el diff exacto de un mutante concreto.
python3 -m mutmut show <mutant_id>

# Volver a probar sólo un mutante tras escribir un test que debería matarlo.
python3 -m mutmut run <mutant_id>
```

`mutmut` copia el fuente a `mutants/` e inyecta allí. **`mutants/` nunca se
commitea** (`.gitignore`): contiene código de la ruta de veredicto con defectos
deliberados inyectados — misma clase de riesgo que el benchmark
`tests/unit/test_m4_floor.py`, y mismo tratamiento.

## 4. Alcance — y por qué es deliberadamente estrecho

`only_mutate` en `pyproject.toml` lista los módulos mutados:

| Módulo | Cobertura de línea (baseline 2026-06-22) |
|--------|------------------------------------------|
| `vigia_scorer.py` | ruta de veredicto raíz |
| `vigia/tools/caie.py` | 69,55% |
| `vigia/core/semiotic_detector_v2.py` | 80,94% |
| `vigia/core/evidence_aggregator.py` | 92,50% |
| `vigia/core/likelihood_engine.py` | 88,68% |
| `vigia/core/decision_layer.py` | 86,30% |
| `vigia/core/causal_closure.py` | 82,76% |
| `vigia/collapse_decision.py` | 77,94% |

**Criterio de admisión: que ya haya tests que puedan morder.** Mutar un módulo
al 0% de cobertura no enseña nada que la cobertura no diga ya más barato — el
mutante sobrevive trivialmente y sólo añade ruido al triaje. Con el total del
repo en 19,16%, mutar todo sería mayoritariamente ruido.

`mutate_only_covered_lines = true` aplica el mismo criterio a nivel de línea.

Ampliar el alcance = añadir módulos a `only_mutate` **después** de subirles la
cobertura, no antes.

## 5. Tests invisibles a la mutación

Cuatro módulos de test están excluidos de la selección del runner
(`pytest_add_cli_args_test_selection`) por una razón estructural, no por
conveniencia:

- `tests/test_m3_scorer_caie_parity.py`
- `tests/test_registry_integrity.py`
- `tests/test_requirements_ci_contract.py`
- `tests/test_security_md_rate_limit_contract.py`

Son tests **meta-repo**: no ejecutan la ruta de veredicto, **inspeccionan texto
fuente** (regex sobre `caie.py`, `inspect.getsource`, `rglob` de `*.md`). Dentro
de `mutants/` el fuente contiene todas las variantes mutantes en línea
(`x_funcname__mutmut_N`, literales envueltos como `"XXFOOXX"`), así que estos
tests leen artefactos del harness y fallan por una razón que no es la lógica
bajo prueba.

**No pueden matar un mutante de `only_mutate`** — no invocan ese código — luego
excluirlos no altera el score. Es un hallazgo con valor propio: *un test que
inspecciona fuente en lugar de ejecutar comportamiento es estructuralmente
invisible a la mutación*. Aporta a la consistencia del repo, no a la
verificación de la lógica.

Los módulos que importan `vigia/vigia_sift_bridge.py` también quedan fuera. La
razón que sostiene la exclusión es que cubren la superficie MCP, **no** la ruta
de veredicto: ningún mutante de `only_mutate` depende de ellos, así que
excluirlos no altera el score.

*Corrección (2026-08-01):* se justificó primero como "no colectan sin `mcp`".
Eso era un fallo de entorno, no del repositorio — faltaba `fastmcp`, declarado
en `requirements.txt`, que resuelve el import. Con `requirements.txt` completo
colectan y pasan (suite completa: 2176 passed). `KNOWN_LIMITATIONS.md` L-045
describe un caso más estrecho del que aquí se supuso.

### 5.1 Anomalía abierta — `test_lr_calibrator_serialization.py`

`vigia/tests/test_lr_calibrator_serialization.py::test_sklearn_backend_roundtrip_matches_before_save`
está excluido por una razón distinta y **sin diagnóstico confirmado**.

Observado (2026-08-01):

| Contexto | Resultado |
|----------|-----------|
| Fase `stats` de mutmut | **FALLA** (2 de 2 corridas) |
| Aislado, en `mutants/` | pasa (5 passed) |
| Aislado, con `MUTANT_UNDER_TEST=stats` | pasa |
| Suite completa en subproceso, dentro de `mutants/` | pasa (2016 passed) |
| Suite completa replicando la invocación **in-process** de mutmut, con sus mismas variables de entorno | pasa (2023 passed) |

La diferencia residual no aislada: mutmut ejecuta `list_all_tests`
(`--collect-only`) y después `stats` **en el mismo proceso**, con su plugin
`StatsCollector` registrado. No se ha confirmado que ése sea el mecanismo.

Por qué importa registrarlo aunque se excluya: el test es determinista en su
entrada (`_synthetic_z_scores(seed=42)`, `random.Random` local, solver `lbfgs`)
y lo que compara es un round-trip `to_dict()`/`from_dict()` con `abs_tol=1e-6`.
Una igualdad de floats sobre una serialización no debería depender del proceso
que la ejecuta. Dado que el repo trata el determinismo como invariante duro
(Invariante 4, `Fraction` con `prec=28`), queda anotado en vez de enterrado.

Se excluye porque mutmut corre con `-x`: el fallo aborta la fase stats y con
ella el barrido entero. `LRCalibrator` no está en `only_mutate`, así que este
módulo no puede matar ningún mutante del alcance y su exclusión no altera el
score.

## 6. Coste

Es N ejecuciones de la suite, una por mutante. Con la suite del alcance en
~3,5 min y varios cientos de mutantes, un barrido completo es trabajo de horas.
`mutmut` mitiga con selección de tests por función (`track_dependencies`) y
caché de resultados entre corridas.

**No es un check de pre-commit.** Es una tarea nocturna o de release.

## 7. Cómo leer un superviviente

Un mutante superviviente cae en una de tres categorías. El triaje es manual y
es la parte que no se automatiza:

1. **Hueco de test genuino.** La lógica cambió y nadie se enteró. Se escribe el
   test que lo mata.
2. **Mutante equivalente.** El cambio no altera el comportamiento observable
   (`x = x + 0`, una guarda redundante, una rama defensiva inalcanzable). No es
   un defecto de la suite y no se puede matar. Se documenta.
3. **Código muerto / defensivo.** La rama no es alcanzable hoy. Ver
   `tests/test_b151a_single_artifact_cap.py`, que pinea justamente la
   inalcanzabilidad del cap de artefacto único: sobre esa rama casi todos los
   mutantes sobreviven, correctamente.

Reportar un mutation score sin separar (1) de (2) y (3) es inflar o deflactar la
cifra según convenga. El registro de triaje vive en §8.

## 8. Registro de corridas

Ver `docs/MUTATION_BASELINE.md` para la corrida de referencia, el score por
módulo y el triaje de supervivientes.

**Al comparar dos corridas, comprueba también el denominador.** Con
`mutate_only_covered_lines = true`, subir la cobertura **agranda** el universo
de mutantes: los tests nuevos cubren líneas que antes nadie tocaba y esas
líneas pasan a ser mutables. En la primera línea base, `collapse_decision.py`
pasó de 4/29 a 35/35 — el numerador y el denominador se movieron a la vez, y
leer sólo el porcentaje habría ocultado la mitad de lo ocurrido.

## 9. Limitaciones declaradas

- **No aplica a la capa LLM.** `reason_with_llm` y la narrativa no son
  deterministas; no hay oráculo estable que mate mutantes.
- **El score depende del alcance.** Un score alto sobre 8 módulos escogidos no
  dice nada sobre los ~170 restantes. La cifra debe citarse siempre con su
  `only_mutate`.
- **La exclusión de tests MCP y meta-repo es un caveat del score**, declarado
  aquí y en los comentarios de `pyproject.toml`, no una omisión silenciosa.
