# B6 — Consistencia de mapas `artifact_type` / `evidence_type` (registro de tipos)

**Origen:** `docs/PLAN_ABDUCTIVO_PENDIENTES_20260705.md` §Grupo B, ítem B6
(antecedente B-060, Lente 7/8 de `AUDITORIA_INVARIANTES_ASIMETRIAS_20260703.md`).

**Propuesta original (B-060):** «un registro único `ARTIFACT_TYPE_REGISTRY`
(tipo → layer, evidence_type, ontology, gamma) que todos consuman, **o al menos
un test que falle si un `artifact_type` emitido por algún motor no está en todos
los mapas**.»

**Decisión (2026-07-10):** se implementa la **segunda variante** (test de
enforcement), no el registro único. Razones:
1. El registro único es un refactor que tocaría ≥6 motores y reescribiría la
   construcción de señales — alto riesgo, cambia scoring en múltiples rutas.
2. El test de enforcement da el 90% del valor (evita la deriva silenciosa
   futura, la clase exacta de B-052/B-060) con riesgo casi nulo.
3. La auditoría previa a parchear (abajo) muestra que los mapas están **hoy
   internamente consistentes**, con un único gap **activo** real que este
   trabajo cierra.

---

## 1. Terreno: dos namespaces de claves distintos

Los motores emiten DOS claves de metadata que indexan mapas diferentes:

| Metadata key | Mapas que la consumen | Efecto |
|--------------|-----------------------|--------|
| `artifact_type` | `_LAYER_MAP`, `_ONTOLOGY_MAP` (`forensic_adapter.py`) vía `signal_to_abductive_record` | capa epistémica (`LAYER_EPISTEMIC_WEIGHT`) + nivel ontológico del **AbductiveReasoner** |
| `evidence_type` | `_EVIDENCE_MAP` (`forensic_adapter.py`) → `EVIDENCE_PROFILES` + `_DOMAIN_MAP` (`caie.py`) vía `signal_to_caie_artifact` | spoofability/perfil + dominio de recolección en **CAIE** |

Agregar un motor nuevo exige tocar ambos namespaces sin ningún enforcement —
el acoplamiento accidental que B-060 (Lente 8) señaló.

`LAYER_EPISTEMIC_WEIGHT`: MEMORY 9/10, NETWORK 8/10, **REGISTRY 6/10**,
**DISK_MFT 4/10**. El default silencioso de un `artifact_type` no mapeado es
`DISK_MFT` (peso 4/10) — el más bajo. Un tipo que debería ser REGISTRY/NETWORK
queda sub-ponderado.

---

## 2. Auditoría previa a parchear (estado medido 2026-07-10)

### 2.1 Consistencia interna de los mapas — OK
- `_LAYER_MAP` y `_ONTOLOGY_MAP` tienen **conjuntos de claves idénticos** (24 c/u).
- Los 27 `evidence_type` de salida de `_EVIDENCE_MAP` están **todos** cubiertos
  por `EVIDENCE_PROFILES` y `_DOMAIN_MAP` (cierre completo).

### 2.2 `artifact_type` emitidos por motores vs `_LAYER_MAP`

Scan estático de literales `"artifact_type": "X"` / `["artifact_type"] = "X"` en
`vigia/sift`, `vigia/tools`, `vigia/inference`, `vigia/core`, `sift_orchestrator.py`.
**7 tipos emitidos NO están en `_LAYER_MAP`/`_ONTOLOGY_MAP`:**

| tipo | emisor | clase | ¿activo? | veredicto |
|------|--------|-------|----------|-----------|
| `behavioral` | behavioral_fingerprint / metabolic_profiler | **derived** (`_mark_derived`, z=0) | sí | inocuo — z=0, fuera del gate crítico `z>3` del reasoner; no es una capa física |
| `resonance` | cross_artifact_resonance | **derived** (z=0) | sí | inocuo |
| `pattern` | case_pattern_library | **derived** (z=0) | sí | inocuo |
| `timeline` | unified_timeline_engine | **derived** (z=0) | sí | inocuo |
| `pcap` | shim (`sift_orchestrator.py`) | **derived** (z=0 inline) | sí | inocuo |
| `ioc` | ioc_manager (`IOCMatchResult.to_signal`) | primary (z≤3.5) | **NO** | latente — `to_signal()` no está cableado; `enrich_signal` es un stub (`return signal`) |
| `windows_event_log` | EventLogCorrelator vía shim `vigia/sift/sift_orchestrator.py:472` | **primary** (z libre) | **SÍ** | **GAP ACTIVO** — ver §3 |

**5 son derivadas z=0** → excluidas del gate crítico del reasoner (que solo mira
`z>3`); forzarlas a una `EvidenceLayer` física sería incorrecto (son
meta-análisis, no evidencia física). **1 (`ioc`) es latente** (sin cablear).
Estas 6 se **grandfatherean** en el test con su justificación.

### 2.3 `evidence_type` emitidos por motores — OK
Scan: `memory_os_profile`, `memory_process`, `network_flow`. Los tres resuelven
en `EVIDENCE_PROFILES` ∩ `_DOMAIN_MAP`. Sin gaps.

### 2.4 Asimetría menor observada (no bloquea B6)
`_DOMAIN_MAP` tiene `memory_dump`, `network_artifact`, `network_connection` que
NO están en `EVIDENCE_PROFILES` (reciben dominio pero perfil default). Ningún
motor los emite como `evidence_type` (no aparecen en el scan), así que el efecto
es latente. Documentado como observación; candidato a limpieza futura, fuera del
alcance de B6.

---

## 3. El gap activo: `windows_event_log` → capa equivocada

`vigia/sift/sift_orchestrator.py:472` setea `artifact_type = "windows_event_log"`
sobre una señal **primaria** del `EventLogCorrelator`. Pero `_LAYER_MAP` solo
contiene la clave `"event_log"` (→ `REGISTRY`). Resultado:

```
_LAYER_MAP.get("windows_event_log", DISK_MFT)  →  DISK_MFT (peso 4/10)
```

cuando el tratamiento consistente con `"event_log"` sería **REGISTRY (6/10)**.
`abductive_reasoner_v2.py:396` usa `weight = LAYER_EPISTEMIC_WEIGHT[art.layer]`,
así que un log de eventos de Windows queda sub-ponderado ~33% en la capa
abductiva del **path on-disk**.

**Blast radius medido:**
- **Corpus JSON (motor): inerte.** Ningún artefacto del corpus (0/259 archivos)
  setea `metadata.artifact_type`; el bridge (`vigia_integration_bridge.py:639`)
  puebla `evidence_type` pero **no** `artifact_type`. Toda señal del motor cae a
  `.get("artifact_type","unknown") → "unknown" → DISK_MFT`. El fix **solo agrega**
  la clave `windows_event_log`; no altera `"unknown"`. ⇒ **0 flips garantizados**
  (confirmado empíricamente, §5).
- **Path on-disk (SIFT orquestador): corregido.** Es la única ruta donde el gap
  estaba activo. No hay caso on-disk de event log en el corpus, así que se
  verifica por unit test a nivel `forensic_adapter` (§4), no por el gate.

**Fix:** agregar `"windows_event_log"` a `_LAYER_MAP` (→ `REGISTRY`) y a
`_ONTOLOGY_MAP` (→ `TECHNIQUE`), idéntico al tratamiento de `"event_log"`. Cambio
puramente aditivo; no modifica ninguna clave existente.

---

## 4. Deliverable

1. **`tests/test_b6_artifact_type_map_consistency.py`** — test de enforcement:
   - `_LAYER_MAP` ≡ `_ONTOLOGY_MAP` en conjunto de claves (regresión "agregué a
     uno, olvidé el otro").
   - Cierre: todo valor de `_EVIDENCE_MAP` ∈ `EVIDENCE_PROFILES` ∩ `_DOMAIN_MAP`.
   - Cobertura: todo `artifact_type` emitido ∈ `_LAYER_MAP` ∪ grandfather.
   - Cobertura: todo `evidence_type` emitido resuelve en `EVIDENCE_PROFILES` ∩
     `_DOMAIN_MAP`.
   - Honestidad del grandfather: cada entrada sigue emitida y sigue sin mapear.
2. **Fix** de `windows_event_log` en los dos mapas de `forensic_adapter.py`.
3. **Unit test** del fix: `signal_to_abductive_record` con
   `artifact_type="windows_event_log"` → `layer == REGISTRY`.
4. **Gate comparativo** sobre el corpus: 0 flips (esperado inerte, medido).

## 5. Verificación

- Red primero: el test de cobertura falla con `windows_event_log` sin mapear
  (2 tests rojos), los 6 de consistencia/grandfather verdes.
- Fix → 9/9 verde, incluyendo el end-to-end `signal_to_abductive_record` →
  `layer == REGISTRY`.
- **Gate comparativo corpus (run_all_agent, baseline stasheado vs fix): 0 flips
  en 291 bundles** (verdict / n_primary / n_unanalyzed). Confirma empíricamente
  la inercia sobre el motor JSON; el path on-disk queda corregido y cubierto por
  el unit test end-to-end.
- Suite completa verde.

## 6. Alcance y límites

- El scan estático no detecta `artifact_type` computados dinámicamente
  (`f"{x}_type"`, `importlib`); ninguno de los emisores actuales lo hace. Misma
  limitación documentada que `test_requirements_ci_contract.py`.
- No cierra el acoplamiento estructural (sigue habiendo dos namespaces y varios
  mapas). Cierra la **deriva silenciosa**: un motor nuevo que emita un tipo no
  cubierto ahora rompe el test en vez de degradar en silencio.
- Las 6 entradas grandfathered documentan por qué su default es seguro; si
  alguna pasa a ser primaria/activa o gana z>0, debe mapearse y removerse del
  allowlist (el test lo fuerza al fallar la cláusula de honestidad).
