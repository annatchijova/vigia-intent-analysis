*[English](./MUTATION_BASELINE.md) · Español*

# Línea base de mutation testing — 2026-08-01

Primera medición. Método, alcance y limitaciones: `docs/MUTATION_TESTING.md`.

**Herramienta:** `mutmut` 3.7.0 · **Python:** 3.11.15 · **Commit base:** `3bf7a8e`
**Suite de referencia:** 2042 passed, 0 failed (sin los módulos que requieren `mcp`, L-045)

---

## 1. Qué se midió — y qué no

Se midieron **3 de los 8 módulos** de `only_mutate`:

| Módulo | Medido |
|--------|--------|
| `vigia/collapse_decision.py` | sí |
| `vigia/core/likelihood_engine.py` | sí |
| `vigia/core/decision_layer.py` | sí |
| `vigia_scorer.py` | **no** |
| `vigia/tools/caie.py` | **no** |
| `vigia/core/semiotic_detector_v2.py` | **no** |
| `vigia/core/evidence_aggregator.py` | **no** |
| `vigia/core/causal_closure.py` | **no** |

**Por qué no los ocho.** El barrido completo genera 7.043 mutantes. Ritmo
medido en esta máquina (4 CPU, `--max-children 4`): **19,5 mutantes/min**, es
decir **~5,3 horas**. Un barrido interrumpido a mitad no es una línea base:
el número dependería de dónde se paró. Se prefirió una medición **completa de
un alcance declarado**. Los cinco restantes son el trabajo del job semanal
(`.github/workflows/mutation.yml`).

Las cifras de abajo valen **para esos tres módulos**. No son el mutation score
de VIGÍA, y no deben citarse como tal.

---

## 2. Resultado — corrida inicial

| Módulo | Killed | Survived | Total | Score |
|--------|-------:|---------:|------:|------:|
| `vigia/collapse_decision.py` | 4 | 25 | 29 | **13,8 %** |
| `vigia/core/decision_layer.py` | 96 | 131 | 227 | **42,3 %** |
| `vigia/core/likelihood_engine.py` | 72 | 94 | 166 | **43,4 %** |
| **TOTAL** | **172** | **250** | **422** | **40,8 %** |

Por función, los peores focos:

| Score | Killed / Surv | Función |
|------:|--------------:|---------|
| 0,0 % | 0 / 14 | `CollapseDecisionLayer.explain` |
| 26,2 % | 17 / 48 | `RiskBoundedDecisionLayer._generate_reason` |
| 26,7 % | 4 / 11 | `CollapseDecisionLayer.resolve` |
| 28,6 % | 6 / 15 | `RiskBoundedDecisionLayer.__init__` |
| 35,7 % | 41 / 74 | `LikelihoodEngine.infer` |
| 50,9 % | 59 / 57 | `RiskBoundedDecisionLayer.decide` |
| 56,0 % | 14 / 11 | `decision_layer._decide` |
| 62,0 % | 31 / 19 | `LikelihoodEngine.__init__` |

---

## 3. Triaje — `vigia/collapse_decision.py`

Único módulo triado mutante a mutante en esta primera pasada.

**Cobertura de línea: 77,94 %. Mutation score: 13,8 %.** Es la demostración
de manual de para qué sirve esta métrica: las líneas se ejecutaban, el
comportamiento no se verificaba.

De los 25 supervivientes, **ninguno resultó equivalente**. Los 25 eran huecos
reales. Desglose derivado de los diffs, uno a uno:

| Clase | Nº | Ejemplo |
|-------|---:|---------|
| Cadena comparada (centinela de regla) | 8 | `"sensor_independence"` → `"XXsensor_independenceXX"` |
| Operador de comparación | 9 | `>=` → `>`, `<` → `<=`, `in` → `not in`, `==` → `!=` |
| Constante numérica de umbral | 5 | `base_score >= 0.5` → `>= 1.5` |
| Cadena devuelta (texto de narrativa) | 3 | `"Standard verdict"` → `"STANDARD VERDICT"` |
| **Total** | **25** | |

Los tres hallazgos que más pesan:

**Centinelas.** `"sensor_independence"` → `"XXsensor_independenceXX"`
sobrevivía. Esa comparación es la regla clave declarada del módulo
("cualquier ruptura de `sensor_independence` → INCONCLUSIVE"). Nadie
comprobaba que la regla dispara con la cadena que realmente se usa.

**Umbrales.** `base_score >= 0.5` → `>= 1.5` sobrevivía: el umbral de MALICE
podía moverse a un valor inalcanzable sin que nada fallara.

**Operadores.** Cambian el veredicto exactamente en el punto de corte, que es
donde una decisión forense se juega.

### Corrección

`tests/test_collapse_decision_boundaries.py` — 22 tests, cada uno apuntando a
mutantes nombrados.

| | Antes | Después |
|---|---:|---:|
| Killed | 4 | **35** |
| Survived | 25 | **0** |
| Total | 29 | 35 |
| Score | 13,8 % | **100 %** |

**El denominador subió de 29 a 35 y eso es correcto**, no un error de conteo:
`mutate_only_covered_lines = true` sólo muta líneas que algún test ejecuta.
Los tests nuevos cubren líneas que antes nadie tocaba, así que esas líneas
pasan a ser mutables. Subir la cobertura **agranda** el universo de mutantes.
Comparar scores entre corridas exige comprobar también el denominador.

### La disciplina que impuso

Hay que pisar el **punto de corte exacto** (0.5, 0.2, 0.3, `len == 2`), no un
valor cómodo del intervalo. Un test con `base_score = 0.9` pasa igual con el
umbral en 0.5 que en 0.8: no distingue, luego no mata. Es exactamente la
diferencia que la cobertura de línea no puede ver.

---

## 4. Pendiente

- Triaje de los 131 supervivientes de `decision_layer.py` y los 94 de
  `likelihood_engine.py`. Los focos están en §2; a diferencia de
  `collapse_decision`, aquí sí cabe esperar mutantes equivalentes (ramas
  defensivas, `__init__` con valores por defecto), y hay que separarlos antes
  de escribir un solo test.
- Medición de los 5 módulos restantes, incluido `vigia_scorer.py`. Trabajo del
  job semanal.

---

## 5. Defectos encontrados montando la medición

No forman parte del score, pero son el rendimiento real de esta primera
pasada. Los cuatro pertenecen a la misma familia: **tests que inspeccionan el
repositorio en vez de ejecutar comportamiento se rompen, o mienten, cuando
existe una segunda copia del árbol.**

| Defecto | Commit |
|---------|--------|
| **Corpus canónico que se evaporaba en silencio.** `tests/caie/test_canonical_cases.py` pasaba un generador a `@pytest.mark.parametrize`. Un generador se agota al consumirse y el objeto queda capturado en el marcador: en cualquier proceso que colecte dos veces, la segunda colección produce **cero** parámetros y los 52 casos canónicos dejan de existir — no como fallo, como ausencia. pytest ya lo avisaba (`PytestRemovedIn10Warning`) y habría dejado de funcionar en pytest 10. | `ef1201b` |
| **Barridos del árbol que contaban el sandbox.** `test_b224_contradiction_detector_dormancy` afirma que cierta regla no tiene productor *en todo el repositorio*; con `mutants/` presente contaba la copia mutada de `vigia_agent.py` como productor nuevo. Un barrido que no distingue código del repo de un directorio de build no sostiene la afirmación que dice sostener. Igual en `test_b117_stale_formula_sweep` y, latente, en `test_requirements_ci_contract`. | `1a5638a` |
| **El propio contrato de la config, dentro del sandbox.** `test_mutation_config_contract` valida el alcance declarado leyendo `pyproject.toml`; dentro de `mutants/` leía la copia acotada y fallaba contra un acotado deliberado. El test es correcto; el sandbox no es su sitio. | `624bd41` |
| **Anomalía abierta**, sin diagnóstico: `test_lr_calibrator_serialization` falla sólo bajo la fase `stats` de mutmut (2 de 2), y pasa en los otros cuatro contextos probados. Ver `MUTATION_TESTING.md` §5.1. | `7403e71` |

---

## 6. Limitación del harness

`mutmut run <patrón>` acepta filtros de nombre de mutante, pero pasarlos **no
acotó el barrido**: ejecutó los 7.043 igual. El mecanismo que sí funciona es
`only_mutate` en `pyproject.toml`, que es el que usa el `workflow_dispatch` de
`mutation.yml`. Acotar a mano exige el ciclo: editar `only_mutate` → lanzar →
esperar a que termine la generación → restaurar la config (el sandbox conserva
su propia copia).
