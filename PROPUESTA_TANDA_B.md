# Propuesta Tanda B — 9 decisiones de diseño

**Fecha:** 2026-07-03
**Rama:** `claude/vigia-pipeline-robustness-cv9lk1`
**Origen:** `TRIAGE_BUGS_LIMITACIONES_20260703.md` §5 Tanda B (B1–B8) + B-055
(hallazgo T-6 de la Tanda A).
**Estado:** PROPUESTA — nada implementado. Cada ítem trae: problema, propuesta
concreta, riesgo (impacto en corpus / flips posibles) y recomendación.
**Orden:** por relación impacto/riesgo — primero lo que protege veredictos con
riesgo mínimo, al final lo que requiere más decisión o más esfuerzo.

Convención de recomendaciones:
- **IMPLEMENTAR AHORA** — beneficio claro, riesgo acotado y verificable con
  suite+corpus; no requiere decisión de producto.
- **DECISIÓN DE ANNA** — hay ≥2 opciones defendibles con trade-off real; el
  código es trivial una vez elegida.
- **DIFERIR** — correcto hacerlo, pero requiere trabajo previo (dataset,
  corrida dedicada) o depende de otro ítem.

---

## Resumen para revisión rápida

| # | Ítem | Impacto | Riesgo | Recomendación |
|---|------|---------|--------|---------------|
| 1 | B-055 — copia stale del scorer | Alto (trampa NameError) | Nulo | **IMPLEMENTAR AHORA** (re-export) |
| 2 | P2-D — provenance_collapsed → ABSTAIN | Alto (honestidad de veredicto) | Bajo, medible | **IMPLEMENTAR AHORA** (con corrida de corpus previa) |
| 3 | L-037b — artifact_reliability → CAIE base_trust | Medio (precondición B-041b) | Bajo hoy / medio a futuro | **IMPLEMENTAR AHORA** (con corrida de corpus) |
| 4 | B-028 — semántica de is_conclusive | Medio (consistencia) | Bajo | **DECISIÓN DE ANNA** (opción A recomendada) |
| 5 | L-024 — `/mnt` en la allowlist | Medio (hardening) | Bajo-medio (operativo) | **DECISIÓN DE ANNA** (opción A recomendada) |
| 6 | P2-E — timestamps en to_signal() | Medio (habilita timeline) | Bajo | **IMPLEMENTAR AHORA** (2 motores primero) |
| 7 | N11 — event_stream en modo agente | Medio (2 motores muertos) | Medio | **DECISIÓN DE ANNA** (alcance) |
| 8 | B-013 — golden rules con raw_score bajo | Medio (FP de MALICE) | Medio (toca CAIE) | **DECISIÓN DE ANNA** |
| 9 | U7/U3 — de-floateo (record_hash + trust_fusion) | Medio (Daubert cross-arch) | Bajo (U7) / medio (U3) | U7 **IMPLEMENTAR AHORA**, U3 **DIFERIR** |

---

## 1. B-055 — Eliminar la trampa: copia stale de `vigia/core/vigia_scorer.py`

**Problema.** Hay dos copias del scorer. La viva (`vigia_scorer.py`, raíz, 764
líneas) tiene `_EPC_FACTOR_TABLE` (B-019), B-031, B-026 y toda la evolución.
La de `vigia/core/` (523 líneas) divergió: referencia `_EPC_FACTOR_TABLE` sin
definirla → **NameError garantizado** en `_vigia_score` para toda cadena de
custodia no-BROKEN, en cuanto alguien la importe. Ya fue flaggeada "stale and
unused" por el patch r7 (2026-06-19) y quedó ahí. Es una mina enterrada: el
nombre `vigia.core.vigia_scorer` es el import "natural" que cualquier código
nuevo elegiría (yo mismo caí durante la Tanda A).

**Propuesta concreta.** Convertirla en re-export de una línea:

```python
# vigia/core/vigia_scorer.py — DEPRECATED: el scorer canónico vive en la raíz.
# Este módulo existía como copia divergente (B-055/T-6) y se congela como
# re-export para que no pueda volver a divergir.
from vigia_scorer import *          # noqa: F401,F403
from vigia_scorer import _vigia_score, _normalize_case, _EPC_FACTOR_TABLE  # noqa: F401
```

Prefiero re-export a borrado: conserva compatibilidad con cualquier import
externo no detectado (notebooks, scripts de Anna) y garantiza una sola fuente
de verdad. Requiere que la raíz esté en `sys.path` — cierto en todos los entry
points actuales (todos insertan el root).

**Riesgo.** Nulo para el corpus (ningún camino vivo la importa — verificado:
solo `vigia_api.py` ×2 importan la raíz). Riesgo residual: un consumidor
externo que dependiera del *comportamiento divergente* de la copia stale —
improbable, porque ese comportamiento es un crash.

**Recomendación: IMPLEMENTAR AHORA.** 15 minutos incluido el test
(`import vigia.core.vigia_scorer` → `_vigia_score` funciona e idéntico al de
la raíz).

---

## 2. P2-D — `provenance_collapsed` → ABSTAIN (no NOISE)

**Problema.** `vigia_scorer.py:684-700` (scorer vivo): si el trust efectivo
medio colapsa (`mean_effective < 0.01`) sin fracturas, el veredicto es
**NOISE** con confianza alta (`1 - mean_effective` ≈ 0.99). Semánticamente
está invertido: una cadena de custodia colapsada significa "no puedo confiar
en NADA de esta evidencia" — eso es ABSTAIN ("no puedo determinar"), no NOISE
("analicé y está limpio"). Es la misma familia de falso-negativo que P0-A:
convertir incapacidad de análisis en benignidad. El comentario del código ya
lo dice: "inadmissible under Daubert" — un veredicto inadmisible no puede
presentarse como benigno confiado.

**Propuesta concreta.** En la rama `elif provenance_collapsed:`:

```python
verdict    = "ABSTAIN"
confidence = 0.0   # sin base epistémica — la confianza no puede ser 1-mean
reason     = ("PROVENANCE COLLAPSED: effective trust < 0.01 sin fracturas — "
              "cadena de custodia insuficiente para afirmar benignidad. "
              "Inadmisible bajo Daubert; requiere re-adquisición.")
```

Nota adicional: la `confidence = 1.0 - mean_effective` actual es doblemente
engañosa (99% de confianza derivada de la *ausencia* de confianza).

**Riesgo.** Cambia veredictos de la clase exacta {trust colapsado, 0
fracturas}: NOISE→ABSTAIN. En el corpus de 198 (que va por el adaptador EBS,
no por el scorer) el impacto esperado es 0; en los casos MCP/batch que sí usan
el scorer hay que medir. Un flip NOISE→ABSTAIN es *deseado* aquí (es el bug),
pero puede bajar la accuracy nominal si algún caso etiquetado NOISE dependía
de esta rama. **Protocolo:** correr `run_all_agent.py` + los casos reales de
`results/` con scorer antes/después y listar cada flip con su causa.

**Recomendación: IMPLEMENTAR AHORA**, con la corrida comparativa como parte
del PR. Si aparece un flip en caso etiquetado, se documenta como corrección de
etiqueta (mismo criterio que el commit a3d7a2c, que ya re-etiquetó 4 casos
ABSTAIN por esta misma familia de razones).

---

## 3. L-037b — Propagar `artifact_reliability` a CAIE (`base_trust`)

**Problema.** `forensic_adapter.py:150` hardcodea `base_trust=1.0` para todo
artefacto que entra a CAIE. Los motores SIFT ya declaran su confiabilidad
(`metadata["artifact_reliability"]`, p.ej. macOS `0.78`, event_log dinámico
L-038), pero CAIE la ignora: un event log fabricable pesa igual que un dump de
memoria. Además es precondición declarada de B-041b (CAIE→veredicto).

**Propuesta concreta.** En `signal_to_caie_artifact`:

```python
_rel = (signal.metadata or {}).get("artifact_reliability", "1")
try:
    base_trust = max(0.0, min(1.0, float(Fraction(str(_rel)))))
except (ValueError, ZeroDivisionError):
    base_trust = 1.0
```

(3 líneas + import; `Fraction(str(...))` porque los motores lo serializan como
string de Fraction.)

**Riesgo.** Hoy BAJO en modo agente: el resultado CAIE es narrativa + campo del
bundle, **no retroalimenta el veredicto** (B-041b diferido) — los composites
CAIE bajan (más conservadores), la sección CAIE de la narrativa cambia, cero
flips de veredicto de agente. PERO el scorer MCP (`_vigia_score`) usa CAIE
vivo para fracturas: si la evaluación de fracturas pondera `base_trust`, los
casos MCC/batch con scorer pueden mover score. **Protocolo:** suite + corpus +
re-correr los bundles reales con scorer y comparar `composite_score`/verdict.

**Recomendación: IMPLEMENTAR AHORA** (con esa corrida). Deja B-041b a una sola
precondición (artefactos multi-capa, que llega con B-052-P2).

---

## 4. B-028 — Definir la semántica de `is_conclusive`

**Problema.** El flag participa en dos puntos: el gate `<3 señales and not
is_conclusive → ABSTAIN` de `classify_agent_verdict`, y el floor de alerta
que SOLO mira MALICE (`_is_conclusive and "MALICI" in hypothesis`). Para
INTENT/SUSPICION/NOISE se sella pero no tiene ningún otro efecto observable.
No produce veredictos incorrectos — produce un campo sub-especificado que un
perito contrario puede explotar ("¿qué significa exactamente este campo que a
veces importa y a veces no?").

**Propuesta concreta — dos opciones:**

- **Opción A (recomendada): simetría mínima + documentación.** Extender el
  floor de alerta a INTENT conclusivo (`alert >= "MEDIUM"` si
  `is_conclusive and "INTENT" in hyp`), y documentar en CLAUDE.md/README la
  semántica completa: "is_conclusive modula (1) el gate de corroboración <3 y
  (2) el piso del nivel de alerta; es informativo para NOISE". ~20 líneas +
  tests.
- **Opción B: solo documentación.** Declarar el flag informativo fuera de
  MALICE y cerrar B-028 sin tocar código.

**Riesgo.** Opción A: cambia `alert_level` (texto de narrativa) de casos
INTENT conclusivos de LOW/MEDIUM→MEDIUM/HIGH — cero flips de veredicto/exit
code (el alert no alimenta classify). Opción B: riesgo cero, deuda semántica
permanece documentada.

**Recomendación: DECISIÓN DE ANNA — sugiero Opción A.** Es barata, coherente
con el precedente del floor MALICE, y convierte la respuesta Daubert en una
línea ("el flag modula corroboración y alerta, documentado").

---

## 5. L-024 — Restringir `/mnt` en la allowlist de PathGuard

**Problema.** `vigia/sift/sift_orchestrator.py:107` permite `/mnt` completo.
Cualquier cosa montada en el host (incluyendo mounts no forenses: NFS
corporativo, discos personales) es leíble por el pipeline. Con P0-B resuelto
(VIGIA_EVIDENCE_DIR entra a la allowlist), `/mnt` genérico ya no es necesario
para operar.

**Propuesta concreta — dos opciones:**

- **Opción A (recomendada): restringir a prefijos forenses.** Reemplazar
  `Path('/mnt')` por `Path('/mnt/vigia')`, `Path('/mnt/ewf')`,
  `Path('/mnt/evidence')` (los patrones que la doc de montaje usa:
  `ewfmount → /mnt/ewf*`). El operador que monta en otro lado exporta
  `VIGIA_EVIDENCE_DIR` — que es exactamente el contrato documentado en
  CLAUDE.md.
- **Opción B: remover `/mnt` por completo.** Máximo hardening; depende 100%
  de VIGIA_EVIDENCE_DIR.

**Riesgo.** Operativo, no de corpus (el corpus no usa /mnt): un workflow
existente de Anna que monte en `/mnt/otra-cosa` sin exportar la variable
pasaría de "funciona" a "PathGuard reject" — que post-F7 es **visible**
(señal `PATHGUARD_REJECT_UNANALYZED` + ABSTAIN), no silencioso. Aun así es
fricción.

**Recomendación: DECISIÓN DE ANNA — sugiero Opción A.** Solo ella sabe qué
puntos de montaje usa en LaBestia. El cambio es de 3 líneas + test; lo
importante es elegir los prefijos correctos.

---

## 6. P2-E — Poblar timestamps en `to_signal()` (revivir UnifiedTimeline)

**Problema.** `unified_timeline_engine.py` busca `metadata["timestamp"]` /
`["last_execution"]` en las señales, pero **ningún** `to_signal()` de los
motores puebla esas claves → todos los eventos del timeline quedan en
timestamp=0 → las detecciones de inversión causal y correlación temporal
cross-source (ventana de 300s) no disparan nunca. El motor corre, consume
ciclos, y produce una señal derivada vacía de contenido temporal.

**Propuesta concreta.** Fase 1 (2 motores de mayor valor): `event_log_correlator`
ya computa `time_range=(min,max)` — agregar `"timestamp": self.time_range[1]`
y `"time_range": [...]` al metadata de `to_signal()`; `disk_forensics` (MFT)
tiene timestamps MACE por entrada — exponer el más reciente sospechoso.
Fase 2: registry/prefetch/browser (todos tienen last_execution/last_visit
internos). Sin tocar el timeline engine: solo alimentarlo con lo que ya pide.

**Riesgo.** Bajo por diseño post-F5: la señal del timeline es **derivada** —
no cuenta para gates de corroboración ni para el override L-036. El efecto es
(a) metadata más rico en señales primarias (inocuo), (b) el timeline empieza a
emitir correlaciones reales → su z puede subir → cambia narrativa/CAIE input,
no veredicto. Corpus: 0 flips esperados (los casos EBS no pasan por acá);
verificar con suite + los smoke de motores.

**Recomendación: IMPLEMENTAR AHORA (Fase 1).** Es deuda barata que además es
prerequisito para que ABSTAIN-2 ($SI/$FN delta) y la inversión causal del
reasoner v2 tengan datos reales algún día.

---

## 7. N11 — Metabolic/Behavioral muertos en modo agente

**Problema.** `MetabolicProfiler` y `BehavioralFingerprint` requieren
`event_stream` (lista de dicts con `timestamp` epoch), pero el agente nunca lo
genera y el shim re-mapea `event_stream→event_logs`. Dos motores engine
completos que jamás corren en Mode 1 — sin marca de "no corrió" (el lector del
bundle no sabe que existen).

**Propuesta concreta — dos opciones:**

- **Opción A: alimentarlos desde los eventos ya parseados.** El
  `EventLogCorrelator` ya produce `EventRecord`s con `timestamp` int epoch —
  exactamente el formato que `MetabolicProfiler.analyze()` pide. Cambio: que
  `run_full_analysis` construya `event_stream = [{"timestamp": e.timestamp,
  "event_id": e.event_id, ...} for e in eventos_parseados]` cuando procesa
  event logs, y lo pase a Metabolic/Behavioral. ~30 líneas; los dos motores
  emiten señales **derivadas** (post-F5) → sin impacto en gates.
- **Opción B: documentar "solo Mode 4".** Una línea en KNOWN_LIMITATIONS +
  marca `NOT_RUN` en pipeline_meta (patrón B-052-P1).

**Riesgo.** Opción A: dos motores nuevos emitiendo señales derivadas en todos
los casos con event logs → narrativa y CAIE input cambian; z derivados nuevos
podrían activar indicadores de AdversarialRobustness. Sin flips de veredicto
esperables (derivadas no votan), pero es el ítem con más superficie nueva de
la tanda. Opción B: riesgo cero.

**Recomendación: DECISIÓN DE ANNA — sugiero Opción B ahora, Opción A como
mejora post-merge.** El valor forense de Metabolic/Behavioral sobre un solo
evtx es especulativo hasta tener un caso que lo necesite; la honestidad
("estos motores no corren en Mode 1") se consigue con la Opción B en 20
minutos.

---

## 8. B-013 — Golden rules de CAIE con `raw_score` bajo

**Problema.** La golden rule `LOG_VS_MEMORY` (contradicción log-dice-X /
memoria-dice-Y) dispara por la *presencia* de la contradicción estructural,
sin umbral mínimo de score de los artefactos involucrados. Dos artefactos
débiles (raw_score ≈ 0.1, posiblemente ruido de parseo) pueden fabricar una
fractura golden → escalación de MALICE. La entrada original lo marca como
"diseño vs contrato": ¿la contradicción importa por sí misma o solo entre
evidencia creíble?

**Propuesta concreta — dos opciones:**

- **Opción A: umbral mínimo.** Golden rule dispara solo si AMBOS artefactos
  tienen `raw_score >= 0.3` (o `effective_trust >= 0.2`). Parámetro nombrado
  (`GOLDEN_RULE_MIN_SCORE`) con justificación en el docstring CAIE.
- **Opción B: cerrar por diseño.** Documentar que la contradicción estructural
  ES la señal (la magnitud individual es irrelevante cuando dos fuentes se
  contradicen), y que el filtro correcto es el trust de adquisición (L-037b,
  ítem 3), no el score.

**Riesgo.** Opción A toca el corazón de CAIE: casos reales donde la fractura
golden fue el driver del MALICE (VIGIA-REAL-* con fracturas) pueden degradar
→ **flips posibles en la dirección FN**. Requiere corrida completa de los
casos reales con scorer + revisión manual de cada flip. Opción B: riesgo cero,
pero deja la puerta a un FP de MALICE por artefactos-basura contradictorios.

**Recomendación: DECISIÓN DE ANNA — sugiero Opción B + ítem 3 (L-037b) como
mitigación real.** Con base_trust propagado, un artefacto basura entra a CAIE
con trust bajo y la fractura pierde peso por la vía correcta (confiabilidad de
la fuente), sin inventar un umbral arbitrario de score. Si después de L-037b
sigue habiendo FP, reabrimos la Opción A con datos.

---

## 9. U7/U3 — De-floateo restante de L-040

**Problema.** De los 7 paths float del mapa L-040 §4 quedan dos accionables:
- **U7:** `ForensicRecord.record_hash()` hashea floats con `round(x, 6)` cuyo
  `repr` depende del bit 52 de `math.exp` — **el mismo registro puede producir
  hashes distintos en x86 vs ARM** (el repo ya reconoce el problema en
  `security.py` P1-005). Para un sistema que promete verificación
  criptográfica del razonamiento, es el gap Daubert más citable.
- **U3:** `trust_fusion.compute_temporal_trust_factor` usa `math.exp` nativa
  (mitigada a medias por `_dround`).

**Propuesta concreta.**
- **U7:** cuantizar con Decimal ANTES de serializar para el hash:
  `Decimal(str(x)).quantize(Decimal("0.000001"), ROUND_HALF_EVEN)` y hashear
  la representación string canónica — el hash queda función de valores
  cuantizados idénticos cross-arch, no del repr float. ~15 líneas en
  `to_dict()`/`record_hash()` + test de estabilidad. **No rompe hashes
  históricos relevantes**: los ForensicRecord no se re-verifican contra
  registros viejos en ningún test/flujo actual (verificar en el PR).
- **U3:** tabla precomputada de 21 buckets (paso 0.05) como
  `_EXP_NEG2_TABLE` del scorer — patrón ya probado dos veces en el repo.

**Riesgo.** U7: bajo — cambia el valor de `record_hash` de registros nuevos
(los viejos no se re-verifican; confirmar). U3: cambia `temporal_trust_factor`
en el 2do-8vo decimal → `effective_trust` del scorer se mueve marginalmente →
**flips teóricamente posibles** en casos al borde de un umbral; requiere
corrida comparativa como el ítem 2.

**Recomendación: U7 IMPLEMENTAR AHORA (es puro sellado, sin efecto en
veredictos); U3 DIFERIR** a la misma corrida comparativa del ítem 2/3 (los
tres mueven el scorer — conviene medirlos juntos en una sola pasada
antes/después).

---

## Plan de ejecución sugerido (si aprobás las recomendaciones)

**PR-B1 — sin efecto en veredictos (implementar ya):**
ítems 1 (B-055 re-export), 6 (timestamps fase 1), 9-U7 (record_hash
cuantizado), 4-A si la aprobás (alert floor INTENT), 7-B (marca NOT_RUN).
Validación: suite + corpus, 0 flips esperados y verificados.

**PR-B2 — mueven el scorer (una sola corrida comparativa):**
ítems 2 (provenance_collapsed→ABSTAIN), 3 (L-037b base_trust), 9-U3 (tabla
exp). Validación: corpus + re-corrida de los casos reales con scorer,
tabla antes/después con cada flip justificado.

**Quedan esperando tu decisión:** ítem 5 (prefijos de /mnt — necesito saber
tus puntos de montaje), ítem 8 (golden rules — recomiendo B, pero es una
decisión de doctrina forense, no de código).

---

*Propuesta Tanda B — tres fixes que protegen veredictos, tres que necesitan
tu firma, y una regla de oro que preferimos defender con trust de adquisición
antes que con umbrales inventados.*
