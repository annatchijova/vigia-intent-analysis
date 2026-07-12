# PREP — Cierre del día de terreno 2026-07-11 → plan para el día de implementación

**Cupo:** termina 23:59 PT del 2026-07-12. Este documento existe para no gastar
cupo de implementación discutiendo diseño. Todo lo de hoy fue solo lectura
(salvo docs/ y el harness nuevo en scripts/experiments/).

---

## 1. Estado de las 4 tareas del día

| Tarea | Estado | Entregable |
|---|---|---|
| 1. Extensión scorer_gate con diff narrativo | **HECHA** | `scripts/experiments/scorer_gate.py` — ablación por instancia (`--instance N`) y por tipo (`--filter T1,T2`), `--narrative-diff` (muestra la interpretación sellada que se removería, reason antes/después, quadripartite antes/después), modo `--corpus`, salida `--json`. Verificado sobre FN-001, MAGNET-2020, CAN-037 |
| 2. Diseño discriminadores M2 | **HECHA** | `docs/M2_DISCRIMINATORS_DESIGN_20260711.md` — taxonomía `marker_class` (4 clases), 2 fracturas nuevas con teoría correcta, inversión del guard H-02 (ausencia de evidencia de manipulación como default seguro), impacto simulado: 0 a −5 etiquetas, +2 controles negativos, 22 narrativas selladas pasan de indefendibles a consistentes |
| 3. Cacería extendida (pasada 2) | **HECHA** | `docs/FOSSIL_HUNT_20260711_PASS2.md` — no hay M-nuevo a nivel de caso; **M3 encontrado a nivel motor**: desincronización scorer↔CAIE (FALSE_FLAG_ATTRIBUTION_MISMATCH, LOG_VS_MEMORY y TIMESTAMP_PRECISION_ANOMALY pesan **0** en el veredicto sellado; ATTRIBUTION_INCONSISTENCY es fantasma). Latentes anotados: NARRATIVE_POISONING con keywords substring (familia del `'red'`), path json_fallback muerto (198/198 live) |
| 4. Alcance B-115 | **HECHA** | En PASS2 §3 — **SISTÉMICO: 26/54 casos de consolidated_canonical** (no 2). Causa raíz: el dataset fuente `vigia_cases_canonical_v2.json` trae dos series de fechas en el mismo artefacto (`timestamp` enero, coherente con narrativa al segundo; `metadata.*_time` abril, +84–169d, generadas en una segunda pasada procedural). TCV **prefiere** la serie rota. 13 de los 26 disparan TCV hoy; 6 deciden veredicto; 13 latentes |

Cierre de la pasada 2 sobre los tipos que nombraste: RED_HERRING,
MULTI_ACTOR_ATTRIBUTION_CHALLENGE, MISSING_AUTHORIZATION,
TEMPORAL_IDENTITY_VIOLATION, COGNITIVE_DOS, MEMORY_VS_DISK y PARENT_ANOMALY
**no existen en el CAIE vivo** — solo como `caie_fractures` declaradas en JSONs,
que son dato muerto (el fallback nunca se ejercita). Auditados y descartados
como fósiles de corpus; riesgo latente documentado.

## 2. Orden de ataque recomendado para mañana (con estimaciones)

Presupuesto realista de implementación efectiva: ~8–10 h de cupo.

| # | Ítem | Est. | Justificación del orden |
|---|---|---|---|
| 0 | Resolver D-1…D-7 (§3) — vos, async, antes de empezar | 15 min de lectura | Bloquea todo lo demás |
| 1 | **M1-TCV quirúrgico** (caie.py Rule 6): matar rama substring (`'red'`/`'network'`/`'conexión'` sobre texto libre), matar fallback a `timestamp` genérico (TCV solo con `network_log_time` + `process_creation_time` estructurados), tratar timestamp ausente como MISSING (incluye el default `_utcnow` para el path TCV) | 2–3 h con corrida de corpus + tests de contraste | Mata 6 veredictos-por-fósil de una vez. Tests: BREAK-016 / LINUX-003 / TDUNGAN / case_097 / case_009 **conservan** TCV; MAGNET-2020 / FN-001 / REAL-006 / CAN-031/026/012/042 **la pierden**. Costo métrico honesto: −5 (ver D-1) |
| 2 | **M3 alineación scorer↔CAIE**: frozensets de vigia_scorer + test de paridad automática contra los tipos que caie.py genera | 0.5–1 h + corrida | Barato, cierra el incentivo invertido antes de introducir las fracturas nuevas de M2 (que necesitan entrar al set MALICIOUS en el mismo lugar) |
| 3 | **M2 vía inferida** (diseño §2): clasificador `marker_class` por inventario de campos + `LINGUISTIC_ATTRIBUTION_SIGNAL` + `SOCIAL_ENGINEERING_PATTERN` + inversión guard H-02 + sacar `ip_geolocation`/`user_agent` del bucket cultural | 3–4 h + corrida comparativa | El bloque más grande (22 disparos, 20 veredictos). Con la vía inferida no se toca ningún caso sellado |
| 4 | **Lint semántico de aceptación** (diseño §2.4): fractura sellada no puede contradecir la thirdness del caso — corrible en CI | 1 h | Convierte la cacería en regresión permanente: los fósiles no vuelven |
| 5 | *Stretch* — **B-115 datos**: script de re-anclaje de `metadata.*_time` en canonical_v2 + 26 derivados (si D-2 aprueba tocar datos) | 2 h + re-sello | Puede caer a otro día sin riesgo: con el ítem 1 hecho, la serie rota deja de alimentar veredictos |
| 6 | *Stretch* — re-tipado subgrupo C (5 casos) si D-5 aprueba | 1–1.5 h | Recupera los −5 temporales de M2 |

Si el cupo aprieta: 1 y 2 son innegociables (máximo fósil removido por hora);
3 puede partirse (guard H-02 invertido solo = 1 h y cierra F-07/F-08).

## 3. Decisiones de doctrina que necesito de vos ANTES de arrancar

- **D-1 (M1, costo métrico):** matar substring+fallback baja el corpus −5:
  MAGNET-2020 pasa a SUSPICION y el comparador NO acepta SUSPICION donde la
  etiqueta dice INTENT (sí acepta MALICE por sobre-severidad); CAN-031/026/
  012/042 (exp MALICE) caen a SUSPICION. ¿Aceptamos la caída honesta, o
  re-etiquetamos MAGNET a SUSPICION/INTENT-flexible y tratamos los 4 CAN como
  casos a rebalancear con señal legítima? Mi lectura: la caída es el sistema
  diciendo la verdad; sostener esos 5 con TCVs falsas es exactamente lo que
  L-033/Daubert prohíbe.
- **D-2 (B-115):** ¿fix de regla solo, datos solo, o ambos? Recomiendo ambos
  con regla primero (ítem 1 ya lo cubre); datos después con re-sello explícito.
  Tocar canonical_v2 + 26 casos = operación de datos sellados, la decidís vos.
- **D-3 (determinismo):** `Artifact.timestamp` default `_utcnow()` (caie.py:724)
  viola el invariante 4 (REAL-006: TCV nacida de 1.9 ms de skew de objetos).
  ¿Cambio global del default a ausente/None (corrida completa de regresión) o
  solo neutralizarlo en TCV/índice temporal (quirúrgico, recomendado mañana;
  global a backlog)?
- **D-4 (M2):** ¿solo clasificador inferido, o también `marker_class` declarado
  en metadata para casos ambiguos (= tocar casos sellados)?
- **D-5 (M2, subgrupo C):** ¿re-tipar los 5 casos con artefactos mal tipados
  (reverse shell como cultural_marker, memoria raw 0.05) aceptando re-sello, o
  aceptar −5 temporales?
- **D-6 (M3):** ¿LOG_VS_MEMORY y TIMESTAMP_PRECISION_ANOMALY entran al set
  MALICIOUS en la misma tanda? (recomiendo sí — una corrida comparativa cubre
  todo el frozenset).
- **D-7 (M2×R4-3):** ¿SOCIAL_ENGINEERING_PATTERN corrobora como DEVICE o como
  CONTEXTUAL en el gate R4-3? Interacción a simular antes de re-tipar nada.

## 4. Bloqueos

Ninguno técnico. El único bloqueo real es D-1…D-7: todo el resto está
inventariado, con harness reproducible (`scorer_gate.py`) y números medidos
sobre el motor real.

## 5. Mapa de documentos

| Doc | Contenido |
|---|---|
| `docs/FOSSIL_HUNT_20260711.md` | Pasada 1: M1/M2, 28 fósiles, dossiers F-01…F-28 |
| `docs/FOSSIL_HUNT_20260711_PASS2.md` | Pasada 2: M3 (scorer↔CAIE), latentes L-A/L-B, alcance B-115 completo |
| `docs/M2_DISCRIMINATORS_DESIGN_20260711.md` | Diseño de discriminadores M2 (no implementado) |
| `scripts/experiments/scorer_gate.py` | Harness de ablación reproducible con diff narrativo |

*Restore tag vigente: `restore-fossil-hunt-20260711`. Rama:
`claude/fossil-hunt-daubert-o85ou4`.*
