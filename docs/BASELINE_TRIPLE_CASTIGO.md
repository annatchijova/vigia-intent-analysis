# BASELINE_TRIPLE_CASTIGO — Medición previa a R4-3 sobre VIGIA-BREAK-014

| Campo | Valor |
|-------|-------|
| **Contexto** | Investigación previa a R4-3 (TAXA_DOMINIOS_RECOLECCION §5.3 advertía "riesgo de triple castigo": FRS + correlación CAIE + corrección por dominio podrían atenuar 3× la misma señal) |
| **Fecha** | 2026-07-07 |
| **Base** | tag `restore-point-kimi-cr-baseline-e7dc85f` |
| **Sujeto** | `VIGIA-BREAK-014` — 100 `log_entry` (95 irrelevantes raw 0.05 + 5 decisivos raw 0.15) + 1 `memory_process` (raw 0.92); expected SUSPICION; el agente hoy emite **MALICE 77/100** (fail de corpus) |
| **Alcance** | Solo medición — 0 cambios de código de producto; scripts efímeros en scratchpad, comandos reproducibles en §5 |

---

## Resumen ejecutivo — el hallazgo invierte la pregunta

**No hay triple castigo. Hay CERO castigo.** En el path que puntúa BREAK-014
(EBS-JSON → `resolve()` → `vigia_scorer._vigia_score`), la redundancia del
mismo tipo no se atenúa en absoluto: el score crece ~linealmente con N y
**95 logs irrelevantes (raw 0.05) mueven el veredicto DOS bandas**
(SUSPICION 0.2324 → MALICE 0.3867). El veredicto correcto (expected
SUSPICION) es exactamente el que el motor emite cuando el ruido NO está.

Los tres mecanismos de atenuación sospechados:

| Mecanismo | ¿Participa en el path de BREAK-014? | Efecto medido sobre redundancia |
|---|---|---|
| **FRS** (`build_redundancy_groups`/`process_all_groups`) | **NO** — solo existe en el path V4 de señales SIFT (`vigia/sift/sift_orchestrator.py:693`); 0 menciones en `vigia_scorer.py` y en el shim raíz | Aislado: **satura perfecto** (§4) — factor 0.02 a N=100 |
| **Correlación CAIE** | Sí (live_caie) | **No atenúa redundancia** — crece ~lineal con N; 0 fracturas (su maquinaria detecta CONTRADICCIONES cross-layer, no redundancia del mismo tipo) |
| **CorrelationDecay del motor** | Sí | Atenúa por-artefacto (trust) pero el composite **acumula sin saturación**: +≈0.0016/log constante hasta cruzar MALICE |

Implicación para R4-3: el riesgo real no es atenuar tres veces — es que la
corrección por dominio se implemente en motor Y CAIE a la vez (doble castigo
*futuro*), mientras que el path V4 ya tiene FRS. **La maquinaria de
saturación que R4-3 necesita ya existe (FRS); lo que falta es aplicarla —
agrupada por dominio de recolección — en el path del motor, donde hoy no hay
ninguna.**

---

## 1. Trazado del path (Firstness)

`VIGIA-BREAK-014.json` entra por `vigia_agent.py` → shim raíz
`sift_orchestrator._analyze_ebs_json` → `_resolve_hypothesis` (B-075) →
`vigia_scorer._vigia_score`: TrustFusion → CorrelationDecay → CAIE (live) →
Decision → Quadripartite. Verificado por grep: ni `vigia_scorer.py` ni el
shim raíz contienen `process_all_groups`/`build_redundancy_groups`/`apply_frs`
— **FRS es exclusivo del path V4** (señales de motores SIFT vivos), que este
caso nunca toca.

Estado actual sin modificaciones (medición 1):

```
_vigia_score(BREAK-014) → verdict=MALICE  score=0.3867  confidence=0.77
                          composite_base=0.3867  caie_fractures=0 (live_caie)
                          mean_effective_trust=0.7757
agente (bundle sellado)  → agent_verdict=MALICE  posterior=77/100
expected                 → SUSPICION  (fail de corpus vigente)
```

---

## 2. Curvas del motor — score vs N logs irrelevantes

Decisivos fijos (5×0.15 + 1×0.92 memory_process), agregando N logs
irrelevantes (raw 0.05, mismo `log_entry`):

| N | verdict | score | confidence |
|---|---------|-------|------------|
| 0 | **SUSPICION** | 0.2324 | 0.46 |
| 1 | SUSPICION | 0.2342 | 0.47 |
| 5 | SUSPICION | 0.2413 | 0.48 |
| 10 | SUSPICION | 0.2502 | 0.50 |
| 25 | SUSPICION | 0.2762 | 0.55 |
| 50 | SUSPICION | 0.3176 | 0.64 |
| 95 | **MALICE** | 0.3867 | 0.77 |

Pendiente ≈ **+0.0016 por log irrelevante, constante** — sin saturación. El
cruce SUSPICION→MALICE (umbral 0.33, gate B-068) ocurre entre N=50 y N=95.
La confianza sube de 0.46 a 0.77 por puro volumen del mismo canal.

Solo ruido (N logs de 0.05, sin ningún decisivo):

| N | verdict | score |
|---|---------|-------|
| 1 | NOISE | 0.0042 |
| 25 | NOISE | 0.0536 |
| 50 | **SUSPICION** | 0.1043 |
| 95 | **SUSPICION** | 0.1888 |

**50 logs de nada (raw 0.05 c/u) fabrican SUSPICION** (umbral 0.10, B-076)
sin un solo artefacto decisivo. Es la demostración cuantificada del
diagnóstico del colectivo: N logs del mismo tipo se están contando como N
fuentes.

---

## 3. CAIE aislado — `cross_artifact_analysis` sobre los mismos cortes

| N (con decisivos) | verdict | composite | fracturas |
|---|---------|-----------|-----------|
| 0 | NOISE | 0.1562 | 0 |
| 25 | NOISE | 0.1963 | 0 |
| 50 | SUSPICION | 0.2340 | 0 |
| 95 | SUSPICION | 0.2959 | 0 |

| N (solo ruido) | verdict | composite |
|---|---------|-----------|
| 1 | INCONCLUSIVE | 0.0021 |
| 50 | INCONCLUSIVE | 0.0967 |
| 95 | INCONCLUSIVE | 0.1736 |

Mismo patrón: crecimiento ~lineal (+≈0.0015/log), **0 fracturas en todas las
corridas** — la "correlación" de CAIE detecta contradicciones entre capas
(golden rules, TCV), no redundancia intra-tipo. No es un mecanismo de
des-duplicación y no debe contarse como uno.

---

## 4. FRS aislado — el mecanismo que SÍ satura (path V4)

N señales idénticas del mismo emisor (`tool_name` y timestamp iguales,
z=1.2 c/u) por `build_redundancy_groups` + `process_all_groups`:

| N | Σz entrada | Σz salida | factor |
|---|-----------|-----------|--------|
| 1 | 1.20 | 1.200 | 1.000 |
| 5 | 6.00 | 2.160 | 0.360 |
| 10 | 12.00 | 2.280 | 0.190 |
| 25 | 30.00 | 2.352 | 0.078 |
| 50 | 60.00 | 2.376 | 0.040 |
| 100 | 120.00 | **2.388** | **0.020** |

Comportamiento exactamente correcto para R4-3: rendimiento decreciente con
convergencia (~2× la señal individual, sin importar N). **FRS ya implementa
la semántica "N copias ≈ una fuente gorda" — pero solo corre sobre señales
de motores SIFT vivos, nunca sobre los artefactos EBS-JSON del corpus.**

---

## 5. Reproducibilidad

```bash
# Curvas motor + CAIE (cortes de BREAK-014):
#   deepcopy del caso, artifacts = decisivos + irrelevantes[:N]
#   → vigia_scorer._vigia_score(case)  y  caie.cross_artifact_analysis(...)
# FRS aislado:
#   N × SignalOutput(tool_name="LOG_TOOL", z_score=1.2, metadata={"timestamp": 0})
#   → build_redundancy_groups(sigs, key=(tool_name, timestamp), delta_t=60)
#   → process_all_groups(sigs, groups, score_attr="z_score")
```

Los cortes usan los artefactos REALES del caso (sin sintetizar contenido);
el único sintético es el set de señales del §4 (FRS no es alcanzable desde
este caso por diseño — ese es el hallazgo).

---

## 6. Consecuencias para la implementación de R4-3

1. **El presupuesto de atenuación en el path del motor está VACÍO** — la
   corrección por dominio no compite con nada ahí. El riesgo de doble
   castigo queda acotado a UNA interacción: si se toca el motor y CAIE a la
   vez. Recomendación: un solo punto de aplicación (el motor, antes de
   Decision), CAIE intacto (sus fracturas son otra cosa).
2. **No inventar el mecanismo: FRS ya lo tiene.** La saturación medida en §4
   es la semántica deseada. R4-3 puede reutilizar `process_all_groups` con
   una key de agrupamiento **por dominio de recolección**
   (TAXA_DOMINIOS_RECOLECCION §3-4) en lugar de por entidad — o portar la
   fórmula. Coherencia entre paths gratis.
3. **Números de aceptación para la corrida comparativa:** BREAK-014 debe
   quedar SUSPICION con los 100 logs presentes (hoy MALICE 0.3867), y el
   corte solo-ruido N=95 debe quedar por debajo de SUSPICION o apenas en el
   umbral — sin romper los 49 MALICE correctos del corpus (la restricción
   que refutó E2 en FASE2_DATASET_CALIBRACION).
4. **La confianza también infla por volumen** (0.46→0.77): la corrección
   debe cubrir score Y confidence, o el gate de confianza seguirá
   sobrevendiendo el veredicto.

*VIGÍA — baseline previo a R4-3 | 2026-07-07 | solo medición, 0 código*
