# Plan Abductivo — Auditorías y Bugs Pendientes (verificado contra código vivo)

**Fecha:** 2026-07-05
**Rama:** `claude/audits-bugs-analysis-kr3bcy`
**Alcance:** todos los documentos de auditoría del repo (6 en raíz + 8 en `docs/`),
`BUGS_PENDIENTES.md` (B-001..B-074), `KNOWN_LIMITATIONS.md`,
`TRIAGE_BUGS_LIMITACIONES_20260703.md`, `PROPUESTA_TANDA_B.md` y `WHAT_IS_NEXT.md`.
**Método:** el de `docs/skills/abductive-engineering` — bucle Peirceano
Abducción → Deducción → Inducción (A–D–I), con verificación puntual de cada ítem
"pendiente" contra el código vivo (el caso B-047 demostró que el tracker se
estanca en ambas direcciones). Cada verificación cita `archivo:línea`.
**Acción tomada sobre el código:** NINGUNA. Investigación + plan.

---

## Resumen ejecutivo

1. **La documentación va sistemáticamente por detrás del código.** Las Tandas A
   y B del triage 2026-07-03 están **completas e implementadas con tests**
   (`tests/test_tanda_b.py`), igual que B-051, B-047, B-067, B-068/B-070,
   B-071..B-074 v2 (incluida la doctrina SIP), la Fase 1 del whitelist mobile
   y el hallazgo crítico de AUDIT_NARRATIVAS (NROMANOFF, resuelto por
   eliminación). Varios de esos ítems siguen figurando como PENDING en
   trackers y auditorías.
2. **Lo verdaderamente pendiente se concentra en la Tanda C** (calibración con
   ground truth): la fuga de `expected_verdict` en el adaptador EBS —
   confirmada viva en `sift_orchestrator.py:619-626` con su umbral muerto
   `avg > Fraction(2,1)` — es el ítem de mayor riesgo Daubert del sistema.
3. **Suite hoy:** 667 passed, 1 failed (test centinela de BUG-NLP-002),
   1 skipped, 6 xfailed. Dos ficheros no colectan en entorno CI limpio por el
   hallazgo nuevo S-1.
4. **Hallazgos nuevos de esta sesión:** S-1 (deriva de `requirements-ci.txt`:
   faltan `psutil` y `mcp`, misma clase que T-2/defusedxml — patrón
   recurrente, pide test de contrato), S-2 (BUG-NLP-002 abierto con test rojo
   sin `xfail`), S-3 (fuga de etiqueta re-confirmada), S-4 (B-040 y B-017
   cerrables: el fix ya existe, el tracker no lo refleja).

---

## 1. Estado real verificado (código vs. documentación)

### 1.1 Ya resuelto aunque algún documento diga lo contrario

| Ítem | Documento que lo da por pendiente | Evidencia en código vivo |
|---|---|---|
| B-017 + T-1 + T-2 (defusedxml) | campo `Estado: ABIERTO` en tracker | `requirements-ci.txt:10`; import guarded en `event_log_correlator.py:18-28` |
| B-026 (prior_trust sin clamp) | triage §1 | `vigia_scorer.py:531-535` |
| B-027 (is_conclusive vs ABSTAIN) | triage §1 | `sift_orchestrator.py:642-647` |
| B-053/T-3 (pcap corrupto mata el caso) | triage §2 | `sift_orchestrator.py:279-290` (señal UNANALYZED, patrón F7) |
| L-023 (write no atómico del bundle) | KNOWN_LIMITATIONS | `bundle_builder.py:239-269` (mkstemp+fsync+replace) |
| B-054/F-L040-6 (fallback muerto) | AUDITORIA_L040 §5 | `vigia_agent.py:1602-1614` |
| Tanda B completa (B-055, P2-D, L-037b, B-028, L-024, P2-E, N11, U7, U3) | PROPUESTA_TANDA_B ("nada implementado") | `tests/test_tanda_b.py` (8 clases de test); `_EXP_NEG2_TABLE` en `trust_fusion.py:43-47`; prefijos `/mnt/vigia_*` en `vigia/sift/sift_orchestrator.py:115-118` |
| B-051 (OverflowError en exp) | AUDITORIA_L040 ("abrir B-051") | `likelihood_ratio.py:75-86,274-276` (LOG_LR_EXP_CAP=700) |
| B-047 | B-047_addendum ("insertar cierre") | tracker ES:2560 y EN:2724 ya `[RESUELTO]` |
| B-067 (fallback invertido del whitelist) | AUDITORIA_MOBILE_WHITELIST §3.2 | `caie.py:745-756` (desconocido = peor clase conocida 0.90/0.15) |
| Whitelist mobile Fase 1 | AUDITORIA_MOBILE_WHITELIST plan | `caie.py:296-298` (chat_message, call_log, … en EVIDENCE_PROFILES) |
| B-068/B-070 (FP NGDC-003, roles de evidencia) | — | cerrados según la propia auditoría |
| B-071..B-074 v2 + doctrina SIP | AUDITORIA_REDTEAM_P1_MOBILE (cuerpo original) | commits `d6d5fa4`, `04c1c7b`, `90220bb`, `6dfe330`, `b250e79` |
| NROMANOFF anchor contradictorio (AUDIT_NARRATIVAS P1) | AUDIT_NARRATIVAS | `vigia_output/` eliminado (T-4 del triage) |
| **B-040 (artifact_reliability → CAIE)** — cerrable | tracker: PENDIENTE | los 3 motores lo emiten (`ios_forensics.py:216`, `android_forensics.py:193`, `macos_forensics.py:220`) y el adapter lo propaga (`forensic_adapter.py:179-193`, fix L-037b) |

### 1.2 Hallazgos nuevos de esta sesión

| ID | Hallazgo | Severidad | Evidencia |
|---|---|---|---|
| **S-1** | `psutil` y `mcp` están en `requirements.txt:13,6` y `pyproject.toml` pero NO en `requirements-ci.txt` → `tests/e2e/test_integration_end_to_end.py` y `vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py` no colectan en CI limpio. Misma clase que T-2 (defusedxml). Tercera ocurrencia del patrón → pide **test de contrato de dependencias** | P2 | `[REPRODUCIDO en este entorno]` |
| **S-2** | BUG-NLP-002 (heurística OOV dígito+letra inalcanzable vía `analyze()`) sigue abierto y su test centinela falla en rojo (`TestL33tOOVUnreachable`), no está marcado `xfail` → la suite completa nunca está verde | P2 | `tests/test_adversarial_nlp_groundtruth.py:409` |
| **S-3** | Fuga de `expected_verdict` re-confirmada viva, con umbral muerto | P1 (Daubert) | `sift_orchestrator.py:619-626` |
| **S-4** | Trackers estancos: B-017 (campo Estado), B-040 (fix ya existente) cerrables | doc | ver §1.1 |

---

## 2. Inventario consolidado de lo verdaderamente pendiente

### Grupo A — Doctrina y calibración (Tanda C; requieren ground truth y/o decisión de Anna)

| # | Ítem | Estado verificado | Bloqueo declarado |
|---|---|---|---|
| A1 | **P2-C — fuga `expected_verdict` en adaptador EBS + umbral muerto `avg>2`** | vivo (`sift_orchestrator.py:619-626`); blind run: agente colapsa a NOISE 189/ABSTAIN 9 mientras el motor da MALICE 108/INTENT 35/NOISE 41/ABSTAIN 14 | load-bearing: el intento ingenuo regresó el corpus 198→60 |
| A2 | **B-052-P2 — granularidad mobile/macOS** (`to_signal()` → `to_signals()` por dominio, ruteo V4 ≥3 señales) | pendiente; la ruta mobile puentea el AbductiveReasoner | cambia TODOS los veredictos mobile (tuck-2019 ABSTAIN→INTENT/MALICE); corpus gate obligatorio |
| A3 | **P2-A / L-033 / L-034 — cadena de atenuación gamma×FRS** | vigente | regla L-033: no tocar sin ≥20 señales reales etiquetadas |
| A4 | **B-069 → re-fit conjunto perfiles+umbrales** | corrida comparativa rechazó la calibración aislada (70.8→70.4%) | requiere dataset etiquetado (`fit_calibration.py`) |
| A5 | **B-041b — CAIE retroalimenta el veredicto** | DIFERIDO | depende de A2 (multi-capa) — L-037b ya cumplida |
| A6 | **B-013 (reapertura condicional)** — umbral `GOLDEN_RULE_MIN_SCORE` | cerrado por diseño | reabrir solo si aparece FP real post-L-037b |
| A7 | **L-041 — SMS semántico** | por diseño | léxicos + calibración multi-caso |

### Grupo B — Fixes acotados sin decisión de doctrina (paralelo, riesgo bajo)

| # | Ítem | Fix propuesto (ya diseñado en auditorías) | Esfuerzo |
|---|---|---|---|
| B1 | S-1 | sincronizar `requirements-ci.txt` + test de contrato: cada import de tests/vigia resoluble con requirements-ci instalado (mata la clase entera, tercera ocurrencia) | 1-2 h |
| B2 | S-2 / BUG-NLP-002 | arreglar la heurística OOV o marcar el centinela `xfail(strict=True)` — decisión pequeña; suite debe quedar verde | 1-2 h |
| B3 | B-016 residual | portar detector de magic-number/stderr a `memory_forensics.py` (motor V4) — verificado ausente | 1 h |
| B4 | B-018 residual | `VIGIA_VOL3_TIMEOUT` env var + escalado por tamaño, registrado en `pipeline_meta` — verificado ausente | 1-2 h |
| B5 | B-059 | módulo único `vigia/core/enfsi.py` (~40 líneas) — verificado inexistente; 3 implementaciones divergen | 2 h + decisión de escala |
| B6 | B-060 (fase registro) | `ARTIFACT_TYPE_REGISTRY` único o test que falle si un `artifact_type` no está en todos los mapas — verificado inexistente | 2 h — **RESUELTO 2026-07-10** (variante test de enforcement; `tests/test_b6_artifact_type_map_consistency.py`. Cazó y cerró un gap ACTIVO: `windows_event_log`→DISK_MFT en vez de REGISTRY. Ver B-096 + `docs/B6_ARTIFACT_TYPE_REGISTRY_DESIGN.md`; gate 0 flips/291) |
| B7 | B-061 | unificar clamp vs rechazo de `confidence` en ambas rutas | 1 h |
| B8 | A-1 | verificador de `daubert_record_hash` (hoy se crea y nunca se verifica) o documentar como anchor manual | 1-2 h |
| B9 | A-2 | `deactivate_honey_token` / expiry — verificado inexistente | 1 h |
| B10 | B-058 recomendación | comparador de `run_all_agent.py` lee `agent_verdict` sellado, no re-deriva | 1 h — **RESUELTO 2026-07-10** (`extract_verdict_from_bundle` + `run_llm_cases._fallback_verdict` leen el sellado; 60/209 bundles del corpus divergían, 0 tras el fix; ver B-095 en BUGS_PENDIENTES.md) |
| B11 | Higiene de trackers (S-4) | cerrar B-017 (campo), B-040; actualizar AUDITORIA_REDTEAM (cuerpo vs updates); matices NPS exec summary + NARCOS `is_conclusive`; TDUNGAN bundle huérfano; `.sha256` faltantes en `srl2018/` | 1-2 h |

### Grupo C — Cobertura de test mobile (AUDITORIA_COBERTURA_MOBILE_SIFT)

Los tres módulos mobile siguen ≈15% de cobertura vs 77-89% de sus hermanos SIFT.
B-071..B-074 v2 ya atacaron `_safe_sqlite_connect`, la conflación
no-parseable==vacío, phishing y SIP; queda el resto del plan de la auditoría:

1. Pin de la escalera `to_signal` completa en los 3 módulos (caza ramas muertas S2).
2. Bordes de banda de conversores de timestamp (S3).
3. `_safe_rglob` acotado y call-sites con `Path.rglob` directo (S4).
4. `_safe_plist_load` con límite de tamaño (S5).

Nota: escribir estos pins ANTES de A2 (B-052-P2) — son el arnés que protege esa
migración.

### Grupo D — Higiene del corpus

Validador: 145/199 FAIL por metadata de adquisición ausente (hipótesis "el
validador causa los FP/FN" ya refutada en AUDITORIA_MOTOR_SIN_LABEL — es
higiene, no causa raíz). Completar metadata por lotes; es también precondición
práctica del dataset de calibración de la Tanda C.

### Grupo E — Track teórico (WHAT_IS_NEXT, post-hackathon)

Aliseda (formalizar `resolve(ccs, risk, epsilon)` como función de selección) →
Magnani (nota detectores manipulativos) → Nishida (verificar fuentes).
**No es ornamental: la función `resolve()` de Aliseda es exactamente la pieza
que falta para cerrar A1** — ver Fase 1 del plan.

---

## 3. El plan, en forma abductiva (bucle A–D–I)

Orden por **economía de investigación** (Peirce): coste del experimento ×
poder discriminante × amplitud del espacio de hipótesis que elimina. Primero
lo barato que protege todo lo demás; el experimento caro (corpus) una sola vez
por tanda, como gate.

### Fase 0 — Proteger el registro de sorpresas (½–1 día) — Grupo B11 + B1 + B2

Sin un tracker fiel y una suite verde no hay "hecho sorprendente" distinguible
de ruido: la abducción degenera. Es la fase más barata y habilita todas las
demás.

- Sincronizar trackers con el código (S-4) y `requirements-ci.txt` (S-1) con
  su test de contrato.
- Dejar la suite en verde estricto (S-2): o fix de BUG-NLP-002 o `xfail(strict)`.
- **Inducción de cierre:** suite completa + colección limpia en entorno
  instalado SOLO con requirements-ci.

### Fase 1 — La sorpresa central: el agente ciego colapsa (A1 / P2-C)

**Registro de la sorpresa (C):** con `expected_verdict` retirado, el motor
determinista produce la distribución real (MALICE 108 / INTENT 35 / NOISE 41 /
ABSTAIN 14) pero el agente colapsa a NOISE 189 / ABSTAIN 9 — cero detecciones.
Expectativa violada: el agente dice derivar su veredicto de la evidencia.

**Abducciones rivales (mantener ≥2 vivas):**
- H1 — el adaptador EBS usa la etiqueta como atajo de mapeo y el camino
  "honesto" nunca se construyó. *Estado: corroborada estructuralmente*
  (`sift_orchestrator.py:619-626` — la única vía a MALICE sin etiqueta es
  `avg > 2`, inalcanzable con inputs normalizados [0,1], máx observado 0.87).
- H2 — el umbral `avg>2` fue escrito para escala z y el adaptador recibe
  escala [0,1]: un error de unidades, no de doctrina. *Consecuencia deducible
  distinta de H1:* re-escalar el umbral a la distribución real de `avg`
  debería recuperar la distribución del motor sin leer la etiqueta.
- H3 — el problema no es el umbral sino que falta la **función de selección**
  (Aliseda): el agente genera hipótesis pero no tiene un
  `resolve(ccs, risk, epsilon) → veredicto` formal; la etiqueta tapó ese hueco
  desde el principio. H3 subsume a H1/H2 y explica además por qué quitarla
  regresó el corpus 198→60.

**Deducciones (predicciones discriminantes):**
1. Si H2 basta: calibrar el umbral sobre la distribución de `avg` del corpus
   (sin tocar nada más) acerca el blind-run del agente al del motor. Barato:
   los fixtures ya existen (`data/cases/red-team/RT-NOLABEL-001`, label-flip
   VIGIA-CAN-008).
2. Si H3 es necesaria: ninguna calibración de un escalar reproduce la
   distribución del motor; hará falta la función de selección con CCS/risk.
3. En ambos casos: con el fix, el **label-flip no debe cambiar ni veredicto ni
   seal** (hoy el agente cambia ambos — test rojo listo para escribirse).

**Inducción (experimentos, en orden de coste):**
1. Escribir primero los tests rojos: blind-run gate (agente sin etiqueta ≠
   colapso a NOISE) + label-flip invariance. Son la definición ejecutable de
   "resuelto".
2. Probar H2 (barato): umbral calibrado, corpus 198 + blind + fixtures.
3. Si H2 no alcanza (esperable), especificar `resolve()` con el marco de
   Aliseda (generación vs selección) — el entregable teórico del Grupo E deja
   de ser lectura y se convierte en la spec — e implementarla detrás del gate
   comparativo obligatorio.

**Falibilismo (condición de reapertura):** si tras `resolve()` el agente sigue
sin converger con el motor, la causa está aguas arriba — la agregación
mono-señal de A2 estaría ahogando la entrada de la selección → A2 pasa de
"siguiente" a "precondición" y se reordena la fase 2.

**Regla de seguridad:** nunca borrar la línea 620 "porque es fea". Está
soportando 198/198; se retira solo cuando los tests rojos de arriba pasen en
verde por el camino nuevo. (Downgrade no es fracaso; regresión silenciosa sí.)

### Fase 2 — Ground truth primero, calibración después (A3, A4, luego A2)

**Abducción de planificación:** cuatro ítems distintos (gamma, re-fit
perfiles, granularidad mobile, golden rules) declaran el mismo bloqueo — "no
tocar sin dataset etiquetado". La hipótesis económica: **el dataset es el
ítem**, no los cuatro fixes.

1. Construir el dataset de calibración: ≥20 señales reales con ground truth
   (regla L-033), reutilizando el corpus 198 + los 4 fixtures red-team +
   completar la metadata que el validador marca ausente (Grupo D — deja de
   ser higiene y pasa a ser insumo).
2. Con dataset en mano, en este orden (cada uno con corrida comparativa como
   gate de inducción, patrón B-069: si empeora, NO APLICADO y se documenta):
   a. A3 gamma×FRS (desbloquea los FN de z legítimos hundidos),
   b. A4 re-fit conjunto perfiles+umbrales,
   c. A2 B-052-P2 `to_signals()` mobile — con los pins del Grupo C ya escritos
      como arnés,
   d. A5 B-041b (recién entonces deja de ser dead code: habrá multi-capa).

### Fase 3 — Fixes acotados en paralelo (Grupo B3–B10)

Independientes de las fases 1-2; cada uno con su test de refutación (el test
que fallaría si el fix fuera cosmético — lección de AUDITORIA_REDTEAM_P1:
B-072/B-073 v1 fueron "verdict-cosméticos" y solo el red-team lo vio).
Candidatos a una tanda tipo A: B3, B4, B7, B9 (mecánicos); B5, B6, B8
requieren una decisión corta de doctrina cada uno.

### Fase 4 — Cobertura mobile como inversión (Grupo C)

Escribir los pins de escalera y bordes de banda ANTES de la migración A2/c.
No es deuda estética: es el instrumento de medición de la fase 2.

### Qué NO hacer (sin cambios respecto al triage)

- No "arreglar" L-001..L-018, L-027, L-030/L-031: son el scope Daubert
  declarado; su valor probatorio está en seguir documentadas.
- No tocar gamma ni el leak sin el dataset (el intento anterior: 198→60).
- No re-auditar lo listado en "AUDITORÍA NEGATIVA" del tracker sin cambios
  nuevos en esos archivos.

---

## 4. Limitaciones de este análisis

1. Verificaciones puntuales (grep + lectura + suite completa una vez), no
   corridas end-to-end por ítem; el corpus 198 no se ejecutó en esta sesión.
2. Dos ficheros de test quedaron fuera de la corrida local por S-1 (deps CI);
   con `psutil` instalado colectan, `mcp` no pudo instalarse en este entorno
   (conflicto PyJWT del sistema) — verificación pendiente en un venv limpio.
3. Los resúmenes de auditorías largas se contrastaron contra código vivo solo
   en los puntos con impacto de veredicto; los puramente documentales se
   tomaron del texto.

---

*Plan 2026-07-05 — la documentación corre detrás del código: dos tandas enteras
ya aplicadas figuraban como pendientes. Lo que de verdad queda es una sola
pregunta grande (¿de dónde sale el veredicto del agente cuando nadie le sopla
la etiqueta?) rodeada de fixes pequeños. El plan la trata como Peirce manda:
sorpresa registrada, tres hipótesis rivales, predicciones discriminantes
baratas primero, y el corpus como juez — no como decorado.*
