# Veredicto de Auditoría Adversaria — Kimi
## Sobre "PROPUESTA L-029 — Qué hacer con DARVO" (dossier 56e71ef, sesión multi-agente de Claude)

**Fecha:** 2026-07-17 · **Método:** audit-before-patch + red-team-auditing (A–D–I, refutación obligatoria)
**Base verificada:** `origin/main` @ `6114b14b` (contiene merge del dossier + B-140 + los fixes K-1..K-4/B-137/B-136/B-116 del branch kimi-audit-followups)
**Leyenda:** CODE FACT · PLAUSIBLE HYPOTHESIS · CONFIRMED BY INDUCTION · FALSIFIED

---

## 0. Veredicto general

**El dossier sobrevive a la auditoría. Las tres respuestas de cabecera se sostienen con evidencia propia mía, no solo la suya. Reproduje su experimento central con el gate REAL (no una réplica) y salieron sus números exactos.** Hay una ancla stale, una precisión de scope necesaria en B-141, y una trampa de implementación para F2 que el dossier no explicita. Nada de eso toca las decisiones.

| Ítem del dossier | Veredicto | Nivel |
|---|---|---|
| B-141 (P1, run_vigia sin señales) | CONFIRMADO, con precisión de scope | CONFIRMED BY INDUCTION (ambos deployments) |
| B-142 (canal DARVO muerto) | CONFIRMADO | CONFIRMED BY INDUCTION |
| ELI = falso positivo (B-140) | CONFIRMADO, substrings verbatim | CODE FACT + INDUCTION |
| Censo: 5 anotados = N=1 expediente | CONFIRMADO | CONFIRMED BY INDUCTION |
| §2.1 "los 5 ya aciertan" + scores | CONFIRMADO (0.2696 / 0.4360 / 0.2872 exactos) | CONFIRMED BY INDUCTION |
| §2.2 simulación boost/penalty | CONFIRMADO fila por fila con gate real | CONFIRMED BY INDUCTION |
| §2.2 fila fractura CAIE simétrica | NO RE-EJECUTADA (cap) | PLAUSIBLE (mecanismo + precedente E2) |
| 3 rutas silenciosas false_flag + R6/R7 | CONFIRMADO (1 ancla stale) | CODE FACT |
| KIWI-002 ceguera (agresor no se narra) | CONFIRMADO | CONFIRMED BY INDUCTION |
| RT-FN-COLLUSION-001 join-key forjado | CONFIRMADO | CODE FACT |
| Fixes K-1..K-4 en main | LOS CUATRO CORRECTOS | CONFIRMED (tests verdes + lectura) |

---

## 1. B-141 (P1): run_vigia descarta todas las señales → CONFIRMADO BY INDUCTION

Ejecutado en ambos deployments:

- **Deployment dataclass (sin pydantic):** `TypeError: SignalOutput.__init__() got an unexpected keyword argument 'description'`. Como `description=d.get("description")` se pasa INCONDICIONALMENTE (`vigia/pipeline/pipeline.py:1382-1388`), toda señal, tenga o no descripción, levanta TypeError, el `except` por señal loguea "Señal inválida ignorada" y sigue: `run_vigia` corre con `signals == []`. Exactamente como dice el dossier.
- **Deployment pydantic (este entorno, pydantic 2.11.4):** NO hay TypeError. Pydantic v2 por defecto ignora kwargs extra (`extra='ignore'`): la señal se construye y la descripción SE PIERDE EN SILENCIO, sin log. Es el mismo bug con síntoma distinto: en vez de pipeline vacío, pérdida muda de datos.
- **Consecuencia para el fix (F0.4):** no alcanza con arreglar el TypeError. El fix correcto es dejar de pasar `description=` (el canal que la quería se retira en la misma tanda por B-142), y el test rojo debe cubrir AMBOS modos: dataclass (rechazo ruidoso) y pydantic (drop silencioso). Si el fix solo quita el kwarg, ambos modos quedan sanos por construcción.

## 2. B-142 + ELI: canal muerto y falso positivo → CONFIRMADO BY INDUCTION

- **Canal muerto:** ejecutado. Con objetos `SignalOutput` reales (que no tienen `description` ni `evidence_type`), `detect_darvo_pattern` devuelve siempre penalty 0 y `adjust_consistency_score(1.0, signals)` devuelve 1.0 incondicionalmente. Con dicts (path Modo 1 / anotación) el detector sí vive (penalty 3/10 en mi prueba). El canal del pipeline es código muerto hoy y se despertaría con cualquier refactor del contrato de señales: la recomendación del dossier (retirar, no estrechar) es la correcta.
- **ELI FP:** verificado verbatim en `data/cases/VIGIA-REAL-MAGNET-2021-IOS-ELI.json`: A02 contiene "Psiphon proxy configured with **4 S3 server list URLs**" ('server' dentro, etype log_entry) y A04 contiene "no messages, **no contacts** database" ('no contact' dentro de un plural inglés). El comentario in-code "exactamente los 5 casos correctos" es FALSO y debe corregirse como dice F0.3, con los substrings verbatim, nunca en silencio.
- **Censo ejecutado sobre todo el corpus:** exactamente 5 anotados = {ELI, KIWI-001, KIWI-003, KIWI-004, KIWI-005}. Cero más.

## 3. Censo N=1 y KIWI-002 → CONFIRMADO

- Los artifacts de KIWI-004 y KIWI-005 son **byte-idénticos** (como JSON) a los de KIWI-003; los archivos difieren solo en case_id/wrapper. La frase del dossier "copias byte-idénticas" es verdadera al nivel evidencia (que es el que importa para N).
- MPF7779408 está en los 7 casos KIWI + RT-FN-COLLUSION-001 (ver §6).
- **KIWI-002 ejecutado:** `surveillance_count=0`, `zero_contact_count=0`, sin anotación. La ceguera estructural del agresor (no describe su propia infraestructura) es un hecho medido, no una metáfora. Es el argumento más fuerte del dossier y es real.

## 4. §2.1 y §2.2: la espina empírica → CONFIRMADO BY INDUCTION (con gate REAL)

- Los 5 anotados pasan su etiqueta en el batch (pass=True). Y ejecutando el motor: scores base EXACTOS a los del dossier: ELI 0.2872 SUSPICION, KIWI-001 0.2696 SUSPICION, KIWI-003/4/5 0.4360 MALICE.
- **Mi experimento:** inyecté un delta post-score dentro de una copia del scorer (`final_score += ±p·k`) y dejé correr el gate B-068 y el ladder REALES sobre los 5 casos. Resultados, fila por fila contra su tabla:
  - boost k=0.05, 0.10: 0 flips (peso muerto) ✓
  - **boost k=0.20: ELI y KIWI-001 flipan SUSPICION→MALICE (2 regresiones)** ✓ — y el flip atraviesa el gate REAL, lo que confirma su claim "el gate cross-domain ABRE para los 5". Una MALICE sellada acuñada desde el FP de un plural inglés, reproducida en mi máquina.
  - penalty k≤0.10: 0 flips ✓
  - **penalty k=0.20: KIWI-003/004/005 flipan MALICE→SUSPICION (3 regresiones)** ✓ — degrada las MALICE verdaderas del POV víctima.
- Fila floor NOISE→SUSPICION: inerte por CODE FACT (ningún anotado es NOISE). Fila fractura CAIE simétrica: NO la re-ejecuté (cap honesto); el mecanismo es el mismo arbitraje de composite y el precedente E2 (−38) está citado. No pesa en la decisión: las filas decisivas están confirmadas.

## 5. false_flag como veredicto: las rutas de fallo → CONFIRMADO (1 ancla stale)

- `vigia_scorer.py:394-399`: ValueError ruidoso para veredicto fuera de vocabulario ✓. Ojo: en `vigia_api.py:45` el llamado NO tiene catch, así que ahí el fallo es crash ruidoso (bueno), no ABSTAIN silencioso.
- `bundle_builder.py` (~:511): `_VERDICT_MAP` con default `"ABSTAIN"` para veredicto desconocido — silencioso ✓. Y devil_advocate solo se compone para MALICE/INTENT (~:570-579): un `false_flag` lo saltea ✓.
  - **Observación colateral mía (P3, fuera del dossier):** `_VERDICT_MAP` tampoco contiene INTENT; un INTENT crudo cae al default ABSTAIN en este path. Puede ser intencional (vocabulario EBS REJECT/ABSTAIN/ACCEPT), pero conviene que el colectivo lo mire una vez.
- `run_all_agent.py:68/126/128/200`: re-lectura de veredictos con default "UNKNOWN" ✓.
- `vigia_agent.py:197`: el clasificador substring `"MALICIOUS" in hyp` sellaría MALICE ante una hipótesis `FALSE_FLAG_MALICIOUS_*` ✓ — la ruta más fea: sella lo contrario de lo que el veredicto relacional querría decir, contra el bundle de la víctima.
- `verify_ebs_v1.py:413,426`: R6/R7 exigen devil_advocate SOLO para MALICE/INTENT ✓ — un veredicto `false_flag` se sellaría sin paso de falsación y los verificadores viejos lo certificarían para siempre. La trampa Daubert es real.
- **Ancla stale:** `sift_orchestrator.py:1149-1155` no existe como se cita; el mecanismo de colapso silencioso existe igual vía bundle_builder (verificado). Corregir la cita, no la sustancia.

## 6. RT-FN-COLLUSION-001 y la trampa F2 → CONFIRMADO + nota mía

- Verificado: RT-FN-COLLUSION-001 porta `case_origin: MPF7779408` y reuso VERBATIM de los artifact_ids de KIWI-006 (A01-A04). El ataque de join-key forjado existe en el repo. Correcto dejarlo como fixture permanente del gate de linkage.
- **Trampa de implementación que el dossier no explicita (nueva, mía):** `case_origin` vive en `artifacts[].metadata.case_origin`, NO top-level (top-level es None en todos los KIWI). `framing` SÍ es top-level (perspective_actor_b, etc.), como el juez 12 corrigió. El pase de linkage F2 debe leer la join-key de metadata de artefactos y framing de top-level; si alguien implementa `case.get('case_origin')` a nivel raíz obtiene None y agrupa todo el corpus en un solo grupo None. Test obligatorio del gate: la join-key NO puede leerse de top-level.

## 7. Mis posiciones (auditor, no firmante)

1. **Ítem 1 (efecto veredicto): NO, y nunca por keywords de descripción.** Lo confirmé con su propio experimento corrido por mí: 0 ganancias posibles, regresiones en ambas direcciones, y el gate real abriendo para casos cuya "multiplicidad de dominios" es un solo narrador. La reapertura pre-registrada (B-112 + device-class + pisos) es la forma correcta de no cerrar la puerta para siempre.
2. **Ítem 2 (false_flag): NO, rechazo con firma.** Error de categoría + tres rutas silenciosas verificadas + el verificador de terceros certificando sin devil_advocate + el clasificador substring sellando contra la víctima. Los tres portadores (anotación + campo cuadripartito + Amicus) son suficientes y correctos.
3. **Ítem 3 (pareo sin autoridad): SÍ.** La ceguera KIWI-002 está medida; el join-key forjado existe en el repo; la dedup de copias es obligatoria (verificado que 004/005 son la misma evidencia que 003); label-blind por construcción, correcto.
4. **F0 en una sola tanda firmada: correcto.** Matcher compartido entre anotación y penalidad: separarlo en dos fases viola el contrato de firmas, como demostraron los jueces. Mi única adición: el fix B-141 y su test rojo deben cubrir los dos deployments (dataclass y pydantic).

## 8. Lo que NO verifiqué

- Fila fractura CAIE simétrica de §2.2 (cap PLAUSIBLE; mecanismo y precedente E2 consistentes).
- La sesión de jueces en sí (6 refutadores, scores 6/10, 7/10...): audité sus claims contra el árbol, no su proceso. Los scores de la tabla §7 son claims del sintetizador.
- El censo de tokens (~1.4M) y las 368 lecturas: no verificables desde el árbol; irrelevantes para las decisiones.
- `vigia/sift/pipeline.py` vs `vigia/pipeline/pipeline.py`: el dossier cita la segunda; verifiqué sobre la que existe en main.

## 9. Tabla de vectores descartados

| Vector | Resultado | Por qué |
|--------|-----------|---------|
| B-141 no reproduce (pydantic presente) | FALSIFIED parcialmente | reproduce distinto: drop silencioso en vez de TypeError; el defecto es real en ambos modos |
| Anotados >5 ocultos en subdirs | FALSIFIED | censo ejecutado: exactamente 5 |
| 004/005 no son copias reales | FALSIFIED al nivel evidencia | artifacts byte-idénticos; difieren solo case_id |
| El gate no abriría para ELI/K001 con boost | FALSIFIED | flipó a MALICE con el gate REAL |
| Scores del dossier inventados | FALSIFIED | 0.2696 / 0.4360 / 0.2872 reproducidos exactos |
| case_origin top-level | FALSIFIED | vive en artifacts[].metadata (trampa F2 documentada) |

---

*Auditado contra `origin/main@6114b14b`. Todo CONFIRMED BY INDUCTION fue ejecutado en mi entorno: construcción SignalOutput en ambos modos, detector DARVO en ambos paths, censo completo del corpus, scorer real sobre los 5 anotados con delta inyectado y gate B-068 real, más lectura anclada de cada ruta de fallo.*
