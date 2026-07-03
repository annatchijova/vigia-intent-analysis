# Auditoría — Narrativa degradada en evidencia macOS (post-tanda 1)

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Tag de restauración:** `pre-macos-narrativa-audit-20260703-044406`
**Alcance:** ruta de evidencia macOS (`cases/tuck-2019-macos`) desde
`vigia_agent.py` → shim `sift_orchestrator.py` → `_analyze_mobile` →
`MacOSForensicsAnalyzer` → narrativa/veredicto. Comparada con la ruta V4 +
AbductiveReasoner que sí produce narrativa Peircean completa.
**Motivación:** Tuck-2019 macOS da exit code 3 correcto pero la narrativa
muestra "Pipeline error"/UNDETERMINED. Con el reasoner ya funcionando
(tanda 1), ¿por qué la narrativa macOS sigue degradada? ¿Qué artefactos
necesita el reasoner para generar Firstness/Secondness/Thirdness en macOS?
**Método:** lectura de código + ejecución real del agente sobre la evidencia
tuck-2019 + inspección de bundles históricos. Todo cita `archivo:línea`.
**Acción tomada:** NINGUNA sobre el código. Solo investigación y este documento.

---

## Resumen ejecutivo

1. **El "Pipeline error"/UNDETERMINED con exit 3 que se observa es un bundle
   PRE-tanda-1, no el comportamiento actual.** Los bundles committeados
   `results/agent_batch/VIGIA-TUCK-2019-RAW_bundle.json` (`best_hypothesis:
   INTENT_DETECTED`, `narrative: "[FIRSTNESS] Pipeline error.", n_signals=5`)
   son exactamente el síntoma que la tanda 1 corrigió: 5 señales, reasoner
   crasheado por INVARIANTE 4, override L-036 → INTENT/exit 3. Re-ejecutar
   ese caso hoy ya no produce "Pipeline error".

2. **Pero la narrativa macOS SIGUE degradada por una razón distinta y de
   diseño:** la evidencia macOS **no pasa por el AbductiveReasoner en
   absoluto**. Va por la ruta *mobile-only* del shim (`_analyze_mobile` →
   `MOBILE_EVIDENCE_ANALYZED`), que construye su propia narrativa de 3 líneas
   y nunca invoca el motor v2. Ejecución real hoy sobre `cases/tuck-2019-macos`:
   `MOBILE_EVIDENCE_ANALYZED`, **exit 4 (ABSTAIN)**, narrativa mobile — no la
   Peircean del reasoner.

3. **Aunque se enrutara a V4, el reasoner igual no correría:**
   `MacOSForensicsAnalyzer` **colapsa TODOS sus findings en UNA sola
   `SignalOutput`** (`macos_forensics.py:134-213`, escalera de z-score). El
   reasoner exige `≥3 señales primarias` (`abductive_reasoner.py:90-91`,
   fix F5 de tanda 3). Una señal macOS → `len(primary)=1 < 3` →
   `[FIRSTNESS] Señales primarias insuficientes` — nunca las tres capas del
   motor v2. **macOS no puede, por construcción actual, generar la narrativa
   Peircean completa del reasoner.**

4. **Qué necesita el reasoner para Firstness/Secondness/Thirdness en macOS
   (respuesta directa a la pregunta):** ≥3 señales primarias en
   `SignalOutput`, cada una con su `metadata.artifact_type` y layer, en vez
   de una señal agregada. Concretamente, `MacOSForensicsAnalyzer` tendría que
   emitir una señal por **dominio de artefacto** (Safari/history, Quarantine,
   TCC, LaunchAgents/persistence, encrypted-apps) y enrutar por V4 en vez del
   adaptador mobile. Ver §4.

5. **Matiz importante:** la narrativa mobile actual **no es "Pipeline error"**
   — es informativa y honesta (3 capas Firstness/Secondness/Thirdness
   sintéticas, generadas por `_mobile_hypothesis` + F4). El "degradado" real
   post-tanda-1 es que (a) no es la narrativa del motor abductivo v2, y (b)
   el veredicto cae en ABSTAIN (fuente única) donde el caso tuck-2019 es un
   MALICE conocido con 23 findings de Safari. El problema de fondo es de
   **granularidad de señal + enrutamiento**, no de la narrativa en sí.

**Veredicto de la auditoría:** no hay "Pipeline error" vigente en macOS
post-tanda-1; hay dos limitaciones de diseño encadenadas —
(A) enrutamiento mobile-only que puentea el reasoner, y
(B) agregación a señal única que impediría el reasoner aunque se enrutara a
V4. Ambas son pre-existentes a la tanda 1 y ortogonales a ella. Propuesta:
tratarlas como **B-052** (granularidad de señal macOS/mobile) en §4, sin
implementar aquí.

---

## 1. Traza: por qué macOS no llega al reasoner

### 1.1 Enrutamiento en el agente y el shim

```
cases/tuck-2019-macos/  (Safari/History.db, Preferences/QuarantineEventsV2, ...)
        │
        ▼
vigia_agent._build_orchestrator_kwargs()              vigia_agent.py:1421-1424
        │  all_names & (_MACOS_MARKER_FILES - _IOS_MARKER_FILES)
        │  → kwargs["macos_evidence_path"] = <dir>       (NO setea ninguna key Windows)
        ▼
shim SIFTOrchestrator.analyze()                        sift_orchestrator.py
        │  mobile_signals = _analyze_mobile(kwargs)      → MacOSForensicsAnalyzer → 1 señal
        │  has_windows_evidence = any(kwargs.get(k) for k in
        │      memory_path, disk_path, event_logs, event_stream, registry_hives,
        │      pcap_path, network_flows, log_path, browser_profile, prefetch_dir,
        │      mft_path, mft_json)                        (:175-179)  → False
        │  if not has_windows_evidence and mobile_signals:   (:180)  → TRUE
        ▼
RUTA MOBILE-ONLY                                       sift_orchestrator.py:180-210
        │  hypothesis, max_z, is_conclusive, n_critical = _mobile_hypothesis(...)
        │  return { abduction: {best_hypothesis, narrative (3 líneas propias)} }
        │
        └──────────  NUNCA llama run_full_analysis (V4)  ni  AbductiveReasoner  ✗
```

El gate `has_windows_evidence` (`:175-179`) es la bifurcación: como la
evidencia macOS no setea ninguna key Windows, cae en la rama mobile-only, que
`return`ea antes de tocar el orquestador V4 (`:238` `real.run_full_analysis`).
El AbductiveReasoner vive **dentro** de `run_full_analysis`
(`vigia/sift/sift_orchestrator.py:670-674`) — inalcanzable desde esta rama.

### 1.2 La narrativa que sí se genera (post-tanda-1, F4/F6)

`_mobile_hypothesis` (`sift_orchestrator.py:76-124`, fix F6 de tanda 3) deriva
la hipótesis del z real y arma una narrativa de 3 capas. Ejecución real sobre
tuck-2019 hoy:

```
--- MAIN HYPOTHESIS ---
Hypothesis: MOBILE_EVIDENCE_ANALYZED
Posterior confidence: 8/25
Conclusive: NO — requires human review
--- PEIRCEAN NARRATIVE ---
[FIRSTNESS] 1 señal(es): 1 primaria(s) de ['macos_forensic'], 0 derivada(s)...
[SECONDNESS] Ninguna señal primaria supera z>2 — sin desviación estructural...
[THIRDNESS] Hipótesis: MOBILE_EVIDENCE_ANALYZED. Conclusiva: no...
Razonamiento del motor abductivo:
  [FIRSTNESS] Mobile forensic evidence analyzed: 1 signal(s) extracted (engines: MACOS_FORENSICS).
  [SECONDNESS] Max z-score: 1.60; señales críticas (z>3): 0.
  [THIRDNESS] Hipótesis: MOBILE_EVIDENCE_ANALYZED. Sin desviación sobre umbral —
              fuente única, sin base para afirmar benignidad concluyente (gate <3 fuentes).
Exit code: 4 (ABSTAIN)
```

**No hay "Pipeline error".** La narrativa es informativa. Pero es la del
adaptador mobile + la capa determinista del agente (F4), **no** las
`phases[].notes` del motor v2 (FIRSTNESS: N artefactos observados / SECONDNESS:
N anomalías vs baseline / THIRDNESS: hipótesis por Occam+CCS). Esa capa v2 es
la que el usuario espera y la que macOS no alcanza.

### 1.3 De dónde viene el "exit 3 + Pipeline error" reportado

Bundles históricos committeados (pre-tanda-1), inspeccionados:

| Bundle | best_hypothesis | narrative | n_signals |
|---|---|---|---|
| `results/agent_batch/VIGIA-TUCK-2019-RAW_bundle.json` | INTENT_DETECTED | **`[FIRSTNESS] Pipeline error.`** | 5 |
| `results/agent_batch/VIGIA-TUCK-2019-JSON_bundle.json` | INTENT_DETECTED | (descripción EBS del caso) | 5 |
| `results/VIGIA-TUCK-2019-MACOS_bundle_claude.json` | INTENT_DETECTED (concl=True) | `null` | 0 |

El RAW es el síntoma exacto de N1 (auditoría de robustez): 5 señales
extraídas, reasoner crasheado por INVARIANTE 4 → `abduction=None` →
`"[FIRSTNESS] Pipeline error."` + `UNDETERMINED`, y el override L-036 lo subió
a INTENT/exit 3. **Ese bundle es pre-tanda-1**; el commit `88bb83b` y
anteriores de esta rama ya lo corrigen para el camino V4. Esos 5 señales
provenían de un EBS-JSON de tuck (5 clusters), no del directorio macOS real
(que da 1 señal por la ruta mobile). Es decir: "tuck-2019 macOS exit 3 +
Pipeline error" mezcla dos entradas distintas — el JSON de 5 clusters
(reasoner, ahora arreglado) y el directorio (mobile, 1 señal, nunca tocó el
reasoner).

---

## 2. Por qué el reasoner no correría ni enrutando a V4

`MacOSForensicsAnalyzer.to_signal()` (`macos_forensics.py:134-213`) es una
**escalera de z-score que colapsa N findings en UNA señal**:

```python
if has_exploit_research and has_antiforensic:  z = 3.8
elif has_exploit_research:                      z = 3.5
...
elif has_suspicious_search:                     z = 1.6
elif self.findings:                             z = 1.2
return SignalOutput(tool_name="MACOS_FORENSICS", z_score=float(z), ...)
```

Sobre tuck-2019: 23 findings `SAFARI_SUSPICIOUS` (todos `corr_group=
"browser_suspicious"`) → `has_suspicious_search=True` → **z=1.6, una sola
señal**. El reasoner exige tres primarias:

```python
# vigia/inference/abductive_reasoner.py:90-91  (fix F5, tanda 3)
primary = [s for s in signals if _is_primary_signal(s)]
if len(primary) < 3:
    return AbductionTrace(peirce_narrative="[FIRSTNESS] Señales primarias insuficientes: 1 ...")
```

Aun forzando la evidencia macOS por V4, `n_primary=1 < 3` → nunca las tres
capas del motor v2. Esto lo comparten iOS, Android y Takeout: todos emiten
**una señal agregada por engine**. La granularidad del reasoner (una señal por
artefacto/layer, pensada para los motores Windows que emiten señales
separadas por memory/registry/eventlog/MFT/network) es incompatible con la
granularidad mobile (una señal por dispositivo).

---

## 3. Qué artefactos necesita el reasoner (respuesta directa)

El motor v2 razona sobre `ArtifactRecord`s con `layer` y `ontology_level`
(`abductive_reasoner.py:114-143`, `_signals_to_artifacts`). Para producir
Firstness/Secondness/Thirdness reales sobre macOS necesita, como mínimo:

1. **≥3 señales primarias** (`signal_class` != derived, sin `unanalyzed`),
   una por **dominio de artefacto macOS**, en vez de la señal agregada única.
   Candidatos naturales en `MacOSForensicsAnalyzer` (los `corr_group` ya
   existentes marcan las familias):
   - `browser_suspicious` — Safari History (`macos_forensics.py:479`)
   - `quarantine_suspicious` — QuarantineEventsV2 (`:581,598`)
   - `antiforensic` — SIP/OPSEC (`:498,614,862`)
   - `persistence` — LaunchAgents/LaunchDaemons (`:763,780,815`)
   - `encrypted_apps` — apps cifradas (`:660,836`)

2. **`metadata.artifact_type` distinto por señal** — el reasoner mapea layer
   desde `tool_name` (`abductive_reasoner.py:117-128`); hoy todo cae en
   `DISK_MFT` por defecto porque `MACOS_FORENSICS` no está en `layer_map`.
   Con señales por dominio, cada una necesita un `tool_name`/`artifact_type`
   que el `layer_map` reconozca (o extender el mapa con las layers macOS).

3. **Enrutamiento por V4, no mobile-only** — que la evidencia macOS con ≥3
   señales entre a `run_full_analysis` (donde vive el reasoner) en vez de
   `return`ear en la rama mobile-only del shim (`:180`).

Sin (1) y (3), la narrativa Peircean del motor determinista es inalcanzable
para macOS por diseño — exactamente como lo es para iOS/Android/Takeout.

---

## 4. Propuesta (B-052, sin implementar)

**B-052 — granularidad de señal en motores mobile/macOS: una señal por
dominio de artefacto, y enrutamiento por V4 cuando hay ≥3.**

Dos piezas, en orden de menor a mayor riesgo:

- **P1 (bajo riesgo) — narrativa:** aceptar que la ruta mobile no usa el
  reasoner y hacer que su narrativa lo diga explícitamente ("análisis por
  adaptador mobile de fuente única; el motor abductivo v2 requiere ≥3 fuentes
  independientes — no aplicable a evidencia de dispositivo único"). Es honesto
  y cierra la percepción de "degradado" sin tocar el scoring. Cero riesgo de
  regresión de corpus.

- **P2 (medio riesgo) — granularidad:** `to_signal()` → `to_signals()` que
  emita una `SignalOutput` por `corr_group` presente (con su `artifact_type`
  y layer), y enrutar por V4 cuando el conteo ≥3. Requiere: extender
  `layer_map` del reasoner con las layers macOS/mobile, recalibrar el z por
  dominio (hoy la escalera mezcla señales de varios dominios en un z único),
  y correr el corpus (198 casos + smoke B-048) para confirmar que el veredicto
  de tuck-2019 pasa de ABSTAIN a INTENT/MALICE sin romper los casos mobile
  existentes (Owl-Android 1-finding, Magnet iOS/Android). **No tocar sin la
  corrida de corpus** — cambia el veredicto de todos los casos mobile.

Recomendación: implementar P1 ya (cierra el issue percibido, cero riesgo) y
tratar P2 como trabajo de calibración separado con ground-truth mobile.

---

## 5. Limitaciones de esta auditoría

1. No se re-generó el bundle EBS-JSON de tuck (`VIGIA-TUCK-2019-JSON`) por V4
   post-tanda-1 — la afirmación de que "ya no da Pipeline error" se apoya en
   la corrección verificada de N1 en la auditoría de robustez, no en una
   corrida nueva de ese JSON específico.
2. No se auditó si algún caso mobile del corpus llega a ≥3 señales por otra
   vía (p.ej. evidencia mixta Windows+macOS que sí entra a V4 y mergea) — el
   foco fue la ruta mobile-only pura de tuck.
3. La propuesta B-052-P2 no se dimensionó contra el corpus (cambiaría
   veredictos mobile); es la primera verificación a correr si se implementa.

---

*Auditoría macOS — el "Pipeline error" ya no existe; lo que queda es que macOS
habla por el adaptador mobile, no por el motor abductivo, y con una sola voz
donde el reasoner necesita un coro de tres.*
