# Auditoría — Robustez del Pipeline VIGÍA: modos de fallo de la narrativa Peircean

**Fecha:** 2026-07-02
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Alcance:** camino `vigia_agent.py` → shim `sift_orchestrator.py` (raíz) →
`vigia/sift/sift_orchestrator.py` (V4) → `vigia/inference/abductive_reasoner.py`
(bridge v1→v2) → `vigia/inference/abductive_reasoner_v2.py` → narrativa y bundle.
**Motivación:** el pipeline produce consistentemente `[FIRSTNESS] Pipeline error.`
en la narrativa Peircean **incluso cuando sí corrió y generó señales válidas**
(exit code 3, z>3). Gap de presentación que compromete la credibilidad forense
del sistema ante un tribunal (Daubert: un perito que declara INTENT con una
narrativa que dice "Pipeline error" es impugnable en el primer cross-examination).
**Método:** lectura de código + reproducción empírica. Cada hallazgo cita
`archivo:línea`. Los reproducidos se marcan `[REPRODUCIDO]`.
**Acción tomada:** NINGUNA sobre el código. Solo investigación y este documento.

**Documentos relacionados:** `AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md`
(extracción y veredicto, 2026-07-02), `AUDIT_NARRATIVAS_20260702.md`
(consistencia narrativa↔bundle, 2026-07-02). Esta auditoría cubre la tercera
pata: **la generación de la narrativa determinista en sí**.

---

## Estado de implementación (2026-07-03, rama `claude/vigia-pipeline-robustness-cv9lk1`)

Las 4 tandas de §5 fueron implementadas. Resumen:

| Fix | Estado | Dónde |
|---|---|---|
| **F1** invariante 4 + CCS por hipótesis + desempate + mapeo ABSTAIN_V2 | ✅ | `abductive_reasoner.py` (`_build_hypotheses`, `_v2_result_to_trace`), `abductive_reasoner_v2.py` (`phase_thirdness`) |
| **F2** error del reasoner nunca genérico | ✅ | `reason()` con try total + `REASONER_ERROR`; orquestador V4 narra `tipo: mensaje` y expone `results.reasoner_error` |
| **F3** override L-036 antes de serializar | ✅ | `vigia_agent._generate_narrative` (override primero, anotado `[OVERRIDE L-036 …]`); `run()` genera narrativa antes del log AGENT_EXIT |
| **F4** narrativa Peircean siempre-informativa | ✅ | Capas FIRSTNESS/SECONDNESS/THIRDNESS deterministas desde señales + capa del motor v2 (`phases[].notes`, ya no se descartan) |
| **F5** señales primarias vs derivadas | ✅ | Tagging `signal_class` en orquestador (SIFT=primary; engine/timeline/adv/unanalyzed=derived); gates ≥3, <3→ABSTAIN y L-036 cuentan solo primarias |
| **F6** mobile por z real + escalación en merge | ✅ | shim `_mobile_hypothesis()`; `_merge_mobile_signals` escala si mobile z>3 y el veredicto previo no está flaggeado |
| **F7** "no analizado" visible y ruidoso | ✅ | Señal sintética `*_UNANALYZED` por motor caído y por rechazo PathGuard; sección "ARTEFACTOS NO ANALIZADOS" en narrativa; NOISE+unanalyzed→ABSTAIN |
| **F8** textos menores (vol3 0-señales, CAIE ERROR, `source`, drops) | ✅ | shim + `vigia_agent` + `pipeline_meta.n_signal_conversion_drops` |
| **F9** tests de regresión | ✅ | `tests/test_pipeline_robustness_narrative.py` (27 tests) + fix del self-test estanco `test_abstain_conditions` en v2 |

**Hallazgos adicionales descubiertos DURANTE la implementación** (extienden §3.1):

| ID | Severidad | Punto de fallo | Fix |
|----|-----------|----------------|-----|
| **N16** | **P0** | `run_pipeline` v2 pasaba `inversion_resolved=(verdict != NO_CONTRADICTION)`: la AUSENCIA de contradicción se trataba como "no resuelto" → ABSTAIN-INVERSION disparaba en TODO caso sin contradicción Memory/Disk → el veredicto REJECT era prácticamente inalcanzable vía wrapper | ✅ `inversion_resolved` = NO_CONTRADICTION (trivialmente resuelta) ∨ CONTRADICTION_IS_EVIDENCE ∨ dominant_layer definido |
| **N17** | **P0** | `AbductiveReasonerV2` acumula estado (`selected_hypothesis`, `phase_log`) entre corridas — el wrapper reutilizaba la instancia y un THIRDNESS sin selección (empate) **heredaba la hipótesis ganadora de la llamada anterior** | ✅ reset de estado al inicio de `run_pipeline` + instancia fresca por llamada en el wrapper. `[REPRODUCIDO]` |
| **N18** | P1 | Guard anti-swallow: H2-BENIGN ganando por mayoría de señales quietas sellaba NOISE conclusivo aunque existiera una señal primaria crítica (z>3) diluida | ✅ H2 + señal crítica → `SUSPICION_DETECTED`, no conclusivo |
| **N19** | P2 | El log `AGENT_EXIT` del audit trail se computaba ANTES del override L-036 → el audit trail podía registrar un veredicto distinto del sellado (y `run_all_agent.py` lee ese entry) | ✅ narrativa (y override) se generan antes del log AGENT_EXIT |

**Decisiones de diseño documentadas:**
- `ABSTAIN_V2` (abstención deliberada del motor v2: veto duro, CCS≤1/2, empate)
  **NO** es overrideable por L-036 — la abstención razonada tiene precedencia
  sobre el conteo de señales. `REASONER_ERROR` (fallo, no razonamiento) SÍ es
  overrideable.
- `MALICIOUS_INTENT_DETECTED` desde el bridge requiere ≥2 tipos de artefacto
  con z>3 (gate Daubert de dos fuentes); un solo tipo capea en
  `INTENT_DETECTED`.
- Evidencia mobile limpia de fuente única → `ABSTAIN` (antes NOISE): 1 señal
  sin corroboración no alcanza para afirmar benignidad. Flip intencional.

**Verificación:** suite completa 323 passed (21 fallos preexistentes en
`tests/e2e/test_integration_end_to_end.py`, idénticos en HEAD — entorno MCP,
no regresión); self-tests v2 9/9; F9 27/27. Corpus `run_all_agent.py`: ver
resultado en el mensaje de commit correspondiente.

---

## Resumen ejecutivo

1. **Causa raíz encontrada y reproducida.** `[FIRSTNESS] Pipeline error.` no es
   un error del pipeline de extracción: es el **AbductiveReasoner (bridge v1→v2)
   crasheando el 100% de las veces que recibe ≥3 señales**, por una violación de
   su propia INVARIANTE 4 (`AssertionError`) al construir la hipótesis benigna
   con `supporting_artifacts=[]` y `applied_rules=[]`. La ironía es exacta: la
   narrativa "Pipeline error" aparece **precisamente cuando hay señales
   suficientes** para razonar; con menos de 3 señales sale el mensaje honesto
   "Señales insuficientes".

2. **La narrativa Peircean completa del core determinista es código muerto.**
   No existe ninguna ejecución real (sin parchear el código o correr con
   `python -O`) que llegue a `[FIRSTNESS]/[SECONDNESS]/[THIRDNESS]` del motor
   v2. Ningún test del repo ejercita `AbductiveReasoner.reason()` — por eso el
   crash sobrevivió.

3. **Bomba latente detrás del crash:** aun arreglando el assert, el bridge
   **siempre selecciona H2-BENIGN** por un empate garantizado de CCS resuelto
   alfabéticamente, y traduce el veredicto v2 ABSTAIN al nombre de la hipótesis
   ganadora. Un fix ingenuo del assert convertiría el síntoma actual
   (UNDETERMINED → override L-036 → INTENT, exit 3) en un **falso negativo
   NOISE (exit 0)** — peor que el bug visible. El fix debe ser conjunto
   (§5, F1+F2).

4. **El exit 3 que se observa hoy no viene del reasoner** — viene del override
   determinista L-036 en `vigia_agent._generate_narrative()`, que se aplica
   **después** de que las secciones "MAIN HYPOTHESIS" y "PEIRCEAN NARRATIVE" ya
   se serializaron. Resultado: bundle sellado con veredicto INTENT y narrativa
   que dice "UNDETERMINED / Pipeline error" — la incoherencia exacta reportada.

5. Se mapean **15 puntos nuevos de fallo silencioso** (N1–N15) además de los ya
   documentados en la auditoría de falsos negativos, y se propone un plan de
   fixes en 4 tandas priorizadas (§5).

---

## 1. POR QUÉ aparece "[FIRSTNESS] Pipeline error" — traza completa

### 1.1 El camino del string

El string se origina en **un único punto** del código de producción:

```
vigia/sift/sift_orchestrator.py:751
    "narrative": abduction.peirce_narrative if abduction else "[FIRSTNESS] Pipeline error.",
```

`abduction` es `None` **solo** si `self.reasoner.reason(all_signals)` lanzó una
excepción (paso 9 del pipeline V4):

```
vigia/sift/sift_orchestrator.py:670-674
    abduction = None
    try:
        abduction = self.reasoner.reason(all_signals)
    except Exception as e:
        logger.error("AbductiveReasoner falló: %s", e)
```

Es decir: **"Pipeline error" significa exclusivamente "el razonador abductivo
crasheó"** — la extracción de señales, gamma, FRS, CAIE, timeline y adversarial
robustness ya corrieron y sus señales están en el bundle. Por eso coexisten
`signals` válidas con z>3 y la narrativa de error.

### 1.2 Por qué el reasoner crashea — INVARIANTE 4 `[REPRODUCIDO]`

`AbductiveReasoner.reason()` (`vigia/inference/abductive_reasoner.py:69-112`)
es un bridge v1→v2:

```python
def reason(self, signals):
    if len(signals) < 3:
        return AbductionTrace(peirce_narrative=f"[FIRSTNESS] Señales insuficientes ({len(signals)}).")
    artifacts  = self._signals_to_artifacts(signals)   # línea 76 — fuera del try
    hypotheses = self._build_hypotheses(signals)       # línea 79 — fuera del try  ← CRASH ACÁ
    ...
    try:
        result = self._v2.run_pipeline(...)            # líneas 93-105 — único bloque protegido
    except Exception as e:
        return AbductionTrace(peirce_narrative=f"[FIRSTNESS] Error en pipeline v2: {e}")
    return self._v2_result_to_trace(result, signals)
```

`_build_hypotheses` construye la hipótesis benigna así
(`abductive_reasoner.py:201-209`):

```python
ben_trace = DecisionTrace(
    decision_id="H2-trace",
    conclusion="Sin evidencia concluyente de actividad maliciosa",
    supporting_artifacts=[],   # ← viola INVARIANTE 4
    applied_rules=[],          # ← viola INVARIANTE 4 (segundo assert)
    ...)
```

Y `DecisionTrace.__post_init__` (`vigia/inference/abductive_reasoner_v2.py:245-254`)
lo rechaza por diseño:

```python
assert len(self.supporting_artifacts) >= 1, ("INVARIANTE 4 VIOLADA — ... Conclusión sin evidencia = ESPECULACIÓN ...")
assert len(self.applied_rules) >= 1, ("INVARIANTE 4 VIOLADA — ... applied_rules vacío ...")
```

Reproducción (señales del caso real VANKO-FALLBACK-002, 5 señales, una con z=3.5):

```
AssertionError: INVARIANTE 4 VIOLADA — 'H2-trace':  Conclusión sin evidencia = ESPECULACIÓN
  Toda conclusión forense requiere ≥1 artefacto verificable.
  (abductive_reasoner.py:201 → abductive_reasoner_v2.py:246)
```

La excepción ocurre **antes** del `try` interno (línea 79 < línea 93), así que
el mensaje diagnóstico "[FIRSTNESS] Error en pipeline v2: {e}" nunca se emite.
Escapa de `reason()`, la captura el `except Exception` del orquestador, y el
error real (`INVARIANTE 4 VIOLADA...`) queda **solo en el log de consola** —
no entra al bundle sellado. El bundle solo conserva el genérico
"[FIRSTNESS] Pipeline error."

Nota: incluso si H2 se arreglara sola, H1-MALICIOUS tiene la misma bomba
condicional: `supporting_artifacts=list(active_tools)` (`:161`) queda vacío
cuando ninguna señal supera z>1.5 (caso típico post-atenuación gamma×FRS,
ver P2-A de la auditoría FN).

### 1.3 Por qué igual sale exit 3 con z>3 — el override L-036

Con `abduction=None`, el orquestador emite
`best_hypothesis="UNDETERMINED"` + `narrative="[FIRSTNESS] Pipeline error."`
(`vigia/sift/sift_orchestrator.py:748-751`). Después, en el agente:

1. `_generate_narrative()` (`vigia_agent.py:746`) serializa **primero** las
   secciones "MAIN HYPOTHESIS" (línea 768: `Hypothesis: UNDETERMINED`) y
   "PEIRCEAN NARRATIVE" (línea 773: `[FIRSTNESS] Pipeline error.`).
2. **Después** (líneas 850-866, fix L-036) cuenta señales con z>3
   (`n_critical`) y, como `hyp == "UNDETERMINED"`, muta
   `abduction["best_hypothesis"] = "INTENT_DETECTED"` (o `MALICIOUS_...` con
   ≥2 críticas) — **pero nunca regenera `abduction["narrative"]` ni las
   secciones ya serializadas**.
3. `_seal_bundle()` clasifica sobre la hipótesis mutada → verdict `INTENT` →
   exit code 3 (`vigia_agent.py:916`, `:1596`).

**Resultado observable — exactamente el síntoma reportado:**

| Campo | Valor | Fuente |
|---|---|---|
| exit code | 3 (INTENT) | override L-036 post-narrativa |
| `abduction.best_hypothesis` (bundle) | `INTENT_DETECTED` | mutado en `:850-866` |
| narrativa "MAIN HYPOTHESIS" | `UNDETERMINED` (stale) | serializada en `:768` antes del override |
| narrativa "PEIRCEAN NARRATIVE" | `[FIRSTNESS] Pipeline error.` (stale) | serializada en `:773` antes del override |

Detalle agravante en el caso VANKO: la señal z=3.5 que dispara el override es
`ADV_ROBUST` — el **meta-indicador** del `AdversarialRobustnessEngine`
(significant silence / coordinated evasion, `vigia/tools/adversarial_robustness.py:50-114`),
no evidencia primaria. El override L-036 no distingue señales de artefacto de
meta-señales derivadas (ver N4, §3).

### 1.4 Confirmación empírica en el corpus

`results/srl2018/VANKO-FALLBACK-002_bundle.json`: 5 señales
(`EVENT_LOG z=0, CROSS_RESONANCE z=0, CASE_PATTERN_LIBRARY z=0,
UNIFIED_TIMELINE z=0, ADV_ROBUST z=3.5`), `pipeline_meta` completo
(`n_sift_signals=1, n_engine_signals=2, n_total_signals=5`), y
`abduction = {best_hypothesis: UNDETERMINED, narrative: "[FIRSTNESS] Pipeline error."}`.
El patrón "1 señal SIFT real inflada a 5 con motores engine, reasoner crasheado"
es exactamente la mecánica descripta arriba.

---

## 2. Condiciones de cada estado narrativo

### 2.1 Tabla de estados

| # | Narrativa | Condición exacta | ¿Alcanzable hoy? |
|---|---|---|---|
| E1 | `[FIRSTNESS] Pipeline error.` | Orquestador V4 corrió y `reason()` lanzó excepción. **Hoy: SIEMPRE que `len(all_signals) >= 3`** (INVARIANTE 4, §1.2). | ✅ — es el estado dominante |
| E2 | `[FIRSTNESS] Señales insuficientes (N).` | Orquestador V4 corrió con 0-2 señales (`abductive_reasoner.py:70-73`). | ✅ |
| E3 | `[FIRSTNESS] No razonamiento ejecutado.` | Default del dataclass `AbductionTrace` (`:49`). Ningún camino lo retorna sin sobreescribir. | ❌ inalcanzable |
| E4 | `[FIRSTNESS] Error en pipeline v2: {e}` | Excepción DENTRO de `run_pipeline()` v2 (`:106-109`). Hoy inalcanzable: el crash ocurre antes, en `_build_hypotheses` (`:79`). | ❌ inalcanzable |
| E5 | `[FIRSTNESS] N señales procesadas por motor v2.`<br>`[SECONDNESS] Veredicto v2: ... CCS: ...`<br>`[THIRDNESS] Hipótesis seleccionada: ...` | ≥3 señales **y** `_build_hypotheses` sin violar invariantes **y** `run_pipeline` sin excepción (`:240-242`). | ❌ **código muerto** — requiere fix F1 |
| E6 | `[FIRSTNESS] Mobile forensic evidence analyzed: N signal(s) extracted.` | Shim raíz: evidencia con marcadores Android/iOS/Takeout/macOS, **sin ningún artefacto Windows** (`memory_path`, `disk_path`, `event_logs`, etc. — lista en `sift_orchestrator.py:135-139`), y ≥1 señal mobile (`:140-160`). Hipótesis fija `MOBILE_EVIDENCE_ANALYZED`. | ✅ |
| E7 | `[FIRSTNESS] Semiotic analysis of N artifacts. ...` | Text pipeline fallback: `ImportError` al importar el shim (`vigia_agent.py:596-599`) + evidencia de texto (`:1362-1372`). Firstness-only. | ✅ (raro) |
| E8 | `Volatility3 memory analysis: N signals from X. Average intentionality score...` | Adaptador vol3 del shim (memoria sin disco, `sift_orchestrator.py:646-661`). **Sin tags Peirce.** Bug de texto: con 0 señales dice "Suspicious activity — requires human review" (`:659`) junto a hipótesis `NO_SEMIOTIC_ANOMALY_DETECTED` (`:650`) — narrativa y veredicto se contradicen (observado en `DC-MEM-003_bundle.json`). | ✅ |
| E9 | *(descripción del caso, truncada a 500 chars)* | Adaptador EBS-JSON del shim (`sift_orchestrator.py:467`): `narrative = case_data["description"]`. Ni Peirce ni generada — es texto del input. | ✅ |
| E10 | `[ERROR] ...` / `[ABSTAIN] ...` / `[SECURITY] ...` | Estados de error explícitos: `_error_result` (`:374-383`), vol3 sin plugins OK (`:610-631`, → ABSTAIN), formato no soportado (`:505-526`), symlink (`vigia_agent.py:1265`), binario sin orquestador (`:1284`), `run_pipeline` ausente (`:1385`), fallo operacional (`:1396`). | ✅ |
| E11 | `[No narrative available]` | `_run_pipeline` capturó `OSError/ValueError/KeyError/ZeroDivisionError` y armó una abducción **sin** clave `narrative` (`vigia_agent.py:609-615`); `_generate_narrative` imprime el placeholder (`:773`). | ✅ |

### 2.2 Qué tiene que pasar para que se genere la narrativa completa

Para que un bundle del core determinista contenga una narrativa Peircean con
las tres capas, **hoy** haría falta TODO esto a la vez:

1. Evidencia que el shim rutee al orquestador V4 real (disk/mixed — no
   memoria-sola, no JSON, no mobile-sola): `sift_orchestrator.py:162-239`.
2. ≥3 señales sobrevivientes tras PathGuard + motores + gamma + FRS.
3. `_build_hypotheses` sin violar INVARIANTE 4 → **imposible sin fix** (H2
   siempre viola; H1 también si ninguna señal supera z>1.5).
4. `run_pipeline` v2 sin excepción.

Y aun cumpliendo 1-4, lo que se obtiene (E5) son **3 líneas genéricas** que no
narran ningún hallazgo: no nombran artefactos, no describen la anomalía contra
baseline, no citan el patrón inferido. La paradoja es que el motor v2 **sí
genera** narrativa Peircean real por fase — `phases[].notes` con
`"FIRSTNESS: N artefactos observados, M silencios significativos (Eco).
Layers presentes: [...]"`, `"SECONDNESS: N anomalías contrastadas contra
baseline..."`, etc. (`abductive_reasoner_v2.py:873-877, 907-910, 950+`) y las
retorna en `_build_output` (`:1190-1197`) — pero el bridge
`_v2_result_to_trace` las **descarta** y fabrica sus 3 líneas propias
(`abductive_reasoner.py:239-242`). La única narrativa completa real del sistema
hoy la produce el LLM en Mode 2 (amicus curiae) — el core determinista nunca.

---

## 3. Mapa completo de puntos de fallo silencioso

"Silencioso" = el agente dice (o implica) haber analizado, pero el artefacto no
se procesó, o el resultado del procesamiento no llega al veredicto/narrativa.

### 3.1 Hallazgos NUEVOS de esta auditoría (N1–N15)

| ID | Severidad | Punto de fallo | Efecto | Ref |
|----|-----------|----------------|--------|-----|
| **N1** | **P0** | `_build_hypotheses` viola INVARIANTE 4 (H2 siempre; H1 si nada supera z>1.5) → `AssertionError` → `abduction=None` | Narrativa "Pipeline error" en el 100% de los casos con ≥3 señales; el razonamiento abductivo del core **nunca corre**. `[REPRODUCIDO]` | `abductive_reasoner.py:201-209`, `_v2.py:246,251` |
| **N2** | **P0** | Empate de CCS garantizado (H1 y H2 comparten el MISMO objeto `ccs`, `:216`) + desempate `sorted(key=(ccs.value, hypothesis_id), reverse=True)` → `"H2-BENIGN" > "H1-MALICIOUS"` lexicográfico | Si se arregla N1 sin tocar esto, **el bridge siempre selecciona la hipótesis benigna**, incluso con todas las señales activas. `[REPRODUCIDO con fix simulado: 5 señales, z=3.5 → H2-BENIGN]` | `abductive_reasoner.py:216`, `_v2.py:943-948` |
| **N3** | **P0** | `_v2_result_to_trace` asigna `best_hypothesis = selected_hypothesis` ignorando que `verdict == "ABSTAIN"` | Un ABSTAIN del motor v2 se presenta como "H2-BENIGN" → `classify_agent_verdict` lo clasifica **NOISE (exit 0)**, no ABSTAIN. Combinado con N1+N2: el fix ingenuo del assert empeora el sistema (INTENT→NOISE). | `abductive_reasoner.py:224-266`, `vigia_agent.py:83-112` |
| **N4** | **P1** | Inflación del conteo de señales: los motores engine (CROSS_RESONANCE, CASE_PATTERN_LIBRARY, UNIFIED_TIMELINE, ADV_ROBUST) emiten señales **derivadas** que cuentan igual que las de artefacto para (a) el gate ≥3 del reasoner, (b) el gate `n_signals<3 → ABSTAIN` de `classify_agent_verdict`, y (c) el override L-036 | 1 artefacto real se infla a 5 señales (caso VANKO: `n_sift=1, n_total=5`) → los gates de corroboración no disparan; y un z>3 de ADV_ROBUST (meta-indicador) puede por sí solo producir INTENT/exit 3 | `sift_orchestrator.py (vigia/sift):589-663`, `vigia_agent.py:110,835-866` |
| **N5** | **P1** | `MOBILE_EVIDENCE_ANALYZED` con `is_conclusive = len(signals)>0` fijo; la hipótesis no contiene INTENT/MALICE, no está en `ABSTAIN_HYPOTHESES`, y el override L-036 no aplica (hyp ∉ {"", UNDETERMINED, UNKNOWN}) | Evidencia mobile con hallazgos z>3 → **siempre NOISE / exit 0** ("NO EVIL"). `[REPRODUCIDO: classify_agent_verdict → NOISE con z=4]` | shim `sift_orchestrator.py:140-160`, `vigia_agent.py:99-112` |
| **N6** | **P1** | `_merge_mobile_signals` fusiona señales mobile en el resultado **después** de que la abducción ya se computó, sin re-ejecutar el reasoner | En evidencia mixta (Windows+mobile) el veredicto y la narrativa ignoran los hallazgos mobile; solo el override L-036 puede rescatarlos, y solo si la hipótesis quedó UNDETERMINED | shim `:357-370` |
| **N7** | **P1** | Motor SIFT que lanza excepción (memory/registry/eventlog/disk/network) → `results["X"] = {"error": ...}` sin señal y **sin marca `unanalyzed`** | El artefacto desaparece del veredicto; `unanalyzed_artifacts` solo cuenta señales con `metadata.unanalyzed=True` (stubs honestos), no motores que crashearon | `vigia/sift/sift_orchestrator.py:327-397, 734-741` |
| **N8** | **P1** | `results["unanalyzed_artifacts"]` y `pipeline_meta.n_unanalyzed_artifacts` no se muestran en la narrativa del agente ni influyen en `classify_agent_verdict` | "No analizado" queda enterrado en el JSON; el lector de la narrativa no se entera de qué clases de evidencia quedaron ciegas | `vigia_agent.py:746-902` |
| **N9** | **P2** | CAIE con `status=ERROR` se omite de la narrativa (solo se muestran `OK` y `NO_ARTIFACTS`) | Un fallo del motor de fracturas cross-artefacto es invisible en el reporte | `vigia_agent.py:804-833` |
| **N10** | **P1** | Orden de operaciones en `_generate_narrative`: el override L-036 muta la hipótesis DESPUÉS de serializar "MAIN HYPOTHESIS" y "PEIRCEAN NARRATIVE" | Narrativa y veredicto sellado divergen dentro del mismo bundle (§1.3) — el gap de presentación reportado | `vigia_agent.py:760-775` vs `:850-866` |
| **N11** | **P2** | `MetabolicProfiler` y `BehavioralFingerprint` requieren `event_stream`, pero el agente nunca lo genera y el shim re-mapea `event_stream→event_logs` | Dos motores engine muertos en modo agente (sin marca de "no corrió") | shim `:175-177`, `vigia/sift:592-625` |
| **N12** | **P2** | Adaptador vol3 con 0 señales: narrativa "Suspicious activity — requires human review" con hipótesis benigna | Narrativa contradice el veredicto (observado en DC-MEM-003) | shim `:650-660` |
| **N13** | **P2** | `sans_compliance.accuracy_validation` exige clave `tool` en cada señal, pero las señales de los adaptadores del shim (vol3, EBS-JSON, mobile) usan `source` | Flag de compliance falso-negativo en bundles de adaptador — **cerrado (B-088): F8 acepta ambos, helper `_accuracy_validation` pineado** | `vigia_agent.py:936-942` |
| **N14** | **P2** | `_to_signal_safe` devuelve None ante cualquier excepción de `to_signal()` — la señal se pierde con un log y nada más | Igual que N7 pero en la conversión resultado→señal — **cerrado (B-089): conversiones primarias emiten `*_UNANALYZED`; derivadas solo contador F8. Camino shim mobile también cerrado (2026-07-10): `_unanalyzed_marker` en los 4 adaptadores + `results.unanalyzed_artifacts` en la rama mobile-only y el merge** | `vigia/sift:267-275` |
| **N15** | **P1** | **Cero tests** ejercitan `AbductiveReasoner.reason()` (grep sobre `tests/` y `vigia/tests/`: 0 archivos) | Por eso N1 (un crash del 100%) vivió en producción sellando bundles; cualquier fix futuro tampoco tiene red | — |

### 3.2 Gaps de la auditoría anterior (estado verificado hoy)

De `AUDITORIA_FALSOS_NEGATIVOS_MODO_AGENTE.md` — se re-verificó en el código
actual qué sigue abierto y qué interactúa con la narrativa:

| ID previo | Estado hoy | Interacción con esta auditoría |
|---|---|---|
| P0-A (sin ABSTAIN) | ✅ corregido (`classify_agent_verdict`, exit 4) | La clasificación es correcta, pero N3 la puentea: un ABSTAIN v2 disfrazado de "H2-BENIGN" cae en NOISE |
| P0-B (PathGuard vs `VIGIA_EVIDENCE_DIR`) | ✅ corregido (`_evidence_allowlist`, `vigia/sift:111-142`; agente publica la var en `vigia_agent.py:1486-1490`) | Los rechazos de PathGuard siguen siendo `logger.error` + señal ausente — no se marcan como unanalyzed (variante de N7) |
| P0-C (shim descarta MFT/prefetch/browser) | ✅ corregido para MFT/prefetch/browser; hives USB/shellbag/amcache pendientes (stubs honestos) | Los stubs marcan `unanalyzed=True` pero N8 hace que eso no llegue a la narrativa |
| P1-A (stubs) | ✅/⏳ browser real; amcache/shellbag/usb stubs honestos | ídem N8 |
| P1-C (filtro IP substring) | ✅ corregido (`_is_external_ip` con `ipaddress.is_global`) | — |
| P1-D (dependencias ausentes) | ✅ vol3 → `UNANALYZED_ARTIFACT`→ABSTAIN; B-017 (`defusedxml`) ahora produce `PIPELINE_ERROR`→ABSTAIN vía shim `_error_result` | El mensaje sí queda en la narrativa (E10) — este es el patrón a imitar |
| P1-E (`.log` por sufijo) | ✅ corregido | — |
| P2-A (atenuación gamma×FRS) | ⏳ diferido (L-033) | Alimenta N1: si nada supera z>1.5, H1 también viola INVARIANTE 4 |
| P2-B (gate ≥3 señales) | vigente por diseño | N4 lo puentea con señales derivadas (en la dirección opuesta) |
| P2-C (fuga `expected_verdict`) | ⏳ retenida deliberadamente | E9: además de la fuga, ese adaptador ni siquiera genera narrativa propia |
| P2-E (timeline timestamps=0) | ✅ cerrado (B-090, 2026-07-10) | Verificado: la señal se emite pero F5 la marca `derived` y no cuenta para los gates — reproducción y pins en `TestB090EmptyTimelineExcludedFromGates` |

### 3.3 Correlación con el corpus (`AUDIT_NARRATIVAS_20260702.md`)

Los 15 bundles `PIPELINE_ERROR` del corpus se dividen en dos mecanismos
distintos que la auditoría de narrativas no separó:

- **PIPELINE_ERROR "verdadero"** (dependencia/formato): p.ej.
  `M57-PAT-2009-12-07` — narrativa `[ERROR] ... defusedxml es obligatorio...`.
  El error es visible y hoy mapea a ABSTAIN. Correcto.
- **"Pipeline error" enmascarado como UNDETERMINED** (N1): p.ej.
  `VANKO-FALLBACK-001/002` — el pipeline extrajo señales, el reasoner crasheó,
  y el bundle presenta `UNDETERMINED` + `[FIRSTNESS] Pipeline error.` sin
  ninguna pista del `AssertionError` real. Todo bundle V4 con ≥3 señales de
  las fechas auditadas cae en esta clase.

---

## 4. Diagnóstico consolidado

```
evidencia → shim → orquestador V4 → señales OK (gamma, FRS, CAIE, timeline, adv)
                                        │
                                        ▼
                       AbductiveReasoner.reason(all_signals)
                        │
                        ├── <3 señales → "Señales insuficientes (N)"        [E2 — honesto]
                        │
                        └── ≥3 señales → _build_hypotheses()
                                          └── H2-BENIGN: supporting_artifacts=[]
                                              → AssertionError (INVARIANTE 4)   [N1]
                                              → escapa (fuera del try, :79 vs :93)
                                              → orquestador: except → abduction=None
                                              → narrative = "[FIRSTNESS] Pipeline error."
                                              → best_hypothesis = "UNDETERMINED"
                                                     │
                                                     ▼
                       vigia_agent._generate_narrative()
                        1. serializa MAIN HYPOTHESIS = UNDETERMINED   (stale)  [N10]
                        2. serializa PEIRCEAN NARRATIVE = Pipeline error (stale)
                        3. override L-036: n_critical≥1 → INTENT_DETECTED
                           (n_critical puede venir de ADV_ROBUST, meta-señal)  [N4]
                                                     │
                                                     ▼
                       bundle sellado: verdict=INTENT, exit 3,
                       narrativa que dice UNDETERMINED / Pipeline error   ← síntoma reportado
```

Y el contrafáctico peligroso: arreglar solo el assert produce
`H2-BENIGN` seleccionado por empate alfabético [N2], veredicto v2 ABSTAIN
traducido a "H2-BENIGN" [N3] → `classify_agent_verdict` → **NOISE exit 0**.
`[REPRODUCIDO]`: con el assert parcheado y las señales del caso VANKO, el
resultado es `best_hypothesis=H2-BENIGN, verdict v2=ABSTAIN, CCS=1/5` →
narrativa E5 correcta pero veredicto benigno espurio.

---

## 5. Propuesta de fixes priorizados

Principio rector: **la narrativa Peircean debe ser informativa en todos los
casos donde hay señales** — incluyendo estados degradados. "Degradado honesto"
(qué corrió, qué no, qué señales hay, por qué no hay veredicto) siempre le gana
a un genérico "Pipeline error".

### Tanda 1 — P0: el reasoner debe correr, y sin sesgo benigno (F1, F2)

Estos dos van **juntos en el mismo commit** — F1 solo, empeora el sistema (§4).

**F1 — Reparar `_build_hypotheses` + desempate + mapeo de veredicto.**
`vigia/inference/abductive_reasoner.py`:
- H2-BENIGN: `supporting_artifacts=["BASELINE_EXPECTATION"]` (o los tools con
  z≤1.5, que son su evidencia de soporte real) y
  `applied_rules=["NULL_HYPOTHESIS"]`. H1: si `active_tools` está vacío,
  `["NO_ACTIVE_SIGNALS"]` — la invariante v2 es correcta; el bridge debe
  cumplirla, no esquivarla.
- CCS por hipótesis: los `CausalLink.consistent_with_hypothesis` de H2 deben
  ser la **negación** de los de H1 (hoy comparten el mismo objeto `ccs`,
  `:216`) — así el empate estructural desaparece.
- Desempate residual en `phase_thirdness`: nunca resolver a favor de una
  hipótesis por orden lexicográfico. Con CCS empatado → ABSTAIN explícito
  (es la semántica v2 de "no hay mejor explicación").
- `_v2_result_to_trace`: si `verdict == "ABSTAIN"` →
  `best_hypothesis = "ABSTAIN_V2"` (∈ `ABSTAIN_HYPOTHESES` del agente, agregar
  la entrada) — nunca el nombre de la hipótesis. Mapear también
  `reason_code` al trace para la narrativa.
- Riesgo: cambia veredictos del corpus. Mitigación: correr
  `run_all_agent.py` (198 casos) antes/después y documentar cada flip con su
  causa (los flips esperables son UNDETERMINED→{ABSTAIN_V2, H1, H2} — todos
  más honestos que el estado actual).

**F2 — El error del reasoner nunca más genérico ni solo-en-logs.**
`vigia/sift/sift_orchestrator.py:670-674, 743-754`:
- En el `except`: capturar `type(e).__name__: e` (+ último frame del
  traceback) y emitir
  `narrative = "[FIRSTNESS] {n} señales extraídas. [SECONDNESS] Razonador abductivo falló: {err}. [THIRDNESS] Sin inferencia — veredicto por override de señales o ABSTAIN."`
  y `best_hypothesis = "REASONER_ERROR"` (agregar a `ABSTAIN_HYPOTHESES`).
- Guardar `results["reasoner_error"]` con el detalle completo para el bundle.
- Ampliar el `try` de `reason()` para cubrir también `_signals_to_artifacts`,
  `_build_hypotheses` y `_v2_result_to_trace` (hoy solo cubre `run_pipeline`)
  → el mensaje E4 "[FIRSTNESS] Error en pipeline v2: {e}" vuelve alcanzable
  como segunda red.

### Tanda 2 — P0/P1: coherencia narrativa ↔ veredicto sellado (F3, F4)

**F3 — Reordenar `_generate_narrative` (N10).**
`vigia_agent.py:746-902`: mover el bloque override L-036 (`:847-866`) **antes**
de construir `narrative_parts`. Cuando el override muta la hipótesis, anotar en
la narrativa la traza completa:
`Hypothesis: INTENT_DETECTED [OVERRIDE L-036 sobre UNDETERMINED — 1 señal z>3: ADV_ROBUST z=3.50]`.
El bundle y la narrativa no pueden volver a divergir porque se generan del
mismo estado post-override.

**F4 — Narrativa Peircean determinista siempre-informativa.**
Construir la sección PEIRCEAN NARRATIVE desde datos que **siempre** existen,
usando la narrativa del reasoner solo como capa superior:
- FIRSTNESS: inventario real — n señales por `artifact_type`, layers presentes,
  `unanalyzed_artifacts` (N8), motores con error (N7), top-3 z-scores con
  tool+artefacto.
- SECONDNESS: desviaciones contra baseline — señales z>2 con su descripción,
  fracturas CAIE (incluyendo `status=ERROR`, N9).
- THIRDNESS: la inferencia v2 si corrió (usar `phases[].notes` reales del motor
  v2 en vez de descartarlas — `_build_output` ya las retorna, `_v2.py:1190-1197`);
  si no corrió, el override aplicado o el motivo de ABSTAIN.
Esto responde directamente el requerimiento: narrativa informativa en TODOS los
casos con señales, no solo con narrativa LLM.

### Tanda 3 — P1: veredictos silenciosamente benignos (F5, F6, F7)

**F5 — Separar señales primarias de derivadas (N4).**
Etiquetar `metadata["signal_class"] = "primary" | "derived"` en el orquestador
(engine/timeline/adv_robust = derived). Los gates ≥3 del reasoner, `<3→ABSTAIN`
de `classify_agent_verdict` y el conteo `n_critical` del override L-036 deben
contar **solo primarias** (una ADV_ROBUST z>3 puede escalar alerta, no fabricar
INTENT por sí sola). Riesgo medio: recalibra el corpus — correr los 198 casos.

**F6 — Mobile: veredicto por señal, no etiqueta fija (N5, N6).**
Shim: derivar la hipótesis mobile del máximo z (mismo mapping que el adaptador
vol3: z>3→MALICIOUS/INTENT, z>2→SUSPICION, 0 hallazgos→NO_ANOMALY) y
`is_conclusive` de los z, no de `len(signals)>0`. En evidencia mixta, pasar las
señales mobile al orquestador **antes** del reasoner (o re-ejecutar la
clasificación después del merge) en vez de fusionarlas post-abducción.

**F7 — "No analizado" visible y ruidoso (N7, N8).**
- Motor que lanza excepción → señal sintética `unanalyzed=True` con el error
  en metadata (como ya hacen los stubs honestos), no solo `results["X"]["error"]`.
- `_generate_narrative`: sección fija "ARTEFACTOS NO ANALIZADOS" cuando
  `unanalyzed_artifacts` o motores con error > 0, con la lista y el motivo.
- `classify_agent_verdict`: si `n_unanalyzed > 0` y el veredicto es
  NOISE, degradar a ABSTAIN (0 hallazgos sobre evidencia no analizada no es
  evidencia de benignidad — invariante ya declarada en el código,
  `vigia/sift:731-733`, pero sin efecto en el veredicto).

### Tanda 4 — P2: pulido y red de regresión (F8, F9)

**F8 — Textos menores:** vol3 con 0 señales → "No signals extracted — nothing
to review" (N12); CAIE ERROR en narrativa (N9); aceptar `source` además de
`tool` en `accuracy_validation` (N13); loggear+contar drops de `_to_signal_safe`
(N14).

**F9 — Tests de regresión del reasoner y la narrativa (N15).** Mínimo:
1. `reason()` con 3/5/10 señales mixtas **no lanza** y retorna narrativa E5
   con las tres capas.
2. Empate de CCS → ABSTAIN_V2, nunca H2-BENIGN por orden alfabético.
3. Señales todas z=0 → hipótesis benigna con narrativa coherente.
4. 1 primaria + 4 derivadas → gate de corroboración NO satisfecho (post-F5).
5. Mobile con z=4 → veredicto ≠ NOISE (post-F6).
6. Bundle end-to-end con ≥3 señales: `narrative` no contiene "Pipeline error"
   y `best_hypothesis` del bundle == hipótesis citada en la narrativa (post-F3).
7. Property test: para todo bundle sellado, si `agent_verdict ∈ {INTENT, MALICE}`
   la narrativa contiene la misma hipótesis y al menos una señal citada.

### Orden y esfuerzo estimado

| Tanda | Fixes | Esfuerzo | Riesgo de regresión | Precondición |
|---|---|---|---|---|
| 1 | F1+F2 | 1 día | Alto (flips de corpus esperables y deseables) — medir con los 198 casos | ninguna |
| 2 | F3+F4 | 1 día | Bajo (solo presentación + orden de mutación) | Tanda 1 |
| 3 | F5+F6+F7 | 2-3 días | Medio (recalibra gates) | Tanda 1 + corpus verde |
| 4 | F8+F9 | 1 día | Nulo | ideal junto a cada tanda |

---

## 6. Limitaciones de esta auditoría

1. Las reproducciones usan señales sintéticas equivalentes a las del bundle
   VANKO (misma estructura tool/z) — no se re-corrió el caso VANKO end-to-end
   contra su evidencia original (no disponible en el árbol).
2. No se auditó el camino MCP (Mode 2) ni `vigia/pipeline/` (Mode 4 batch):
   esta auditoría cubre el camino `vigia_agent.py` → shim → V4. El bridge
   crasheado (N1-N3) afecta a **cualquier** caller de
   `SIFTOrchestrator.run_full_analysis`, incluido Mode 4 si lo usa.
3. Los IDs N1-N15 son de esta auditoría; al incorporarlos a
   `BUGS_PENDIENTES.md` correspondería asignarles B-051+ (último usado: B-050).
4. No se midió el impacto de F1/F5 sobre la accuracy del corpus (198 casos) —
   es la primera verificación a correr al implementar.

---

*Auditoría de robustez — VIGÍA hace la decepción computacionalmente cara;*
*esta auditoría intenta que el propio pipeline no pueda decepcionarse a sí mismo.*
