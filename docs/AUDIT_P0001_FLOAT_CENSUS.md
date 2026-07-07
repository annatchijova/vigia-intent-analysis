# AUDIT P0-001 — Censo exhaustivo de `float()` en el path de scoring determinístico

| Campo | Valor |
|-------|-------|
| **Audit ID** | P0-001-CENSUS |
| **Fecha** | 2026-07-07 |
| **Base** | commit `e0e7be0`, tag de restauración `restore-point-float-census-e0e7be0` |
| **Alcance** | 10 módulos SIFT Windows (shellbag, amcache, memory, disk, usb, browser, unified_timeline, event_log, prefetch, registry) + `ios_forensics.py` + `android_forensics.py` |
| **Tipo** | Solo investigación — cero cambios de código |
| **Antecedente** | P0-001 (BUGS_PENDIENTES_EN.md) — fix 2026-06-30 de la reconversión float→Fraction en la frontera SIFT→scorer |

---

## Resumen ejecutivo

Se censaron **37 call sites de `float()`** en los 12 módulos del alcance. **36 de los 37**
pertenecen a un único patrón uniforme: la conversión Fraction→float en el constructor de
`SignalOutput` dentro de `to_signal()` (3 campos × 12 módulos: `value`, `z_score`,
`confidence`). Este patrón es la **frontera de contrato documentada** en la decisión de
alcance de P0-001: `SignalOutput` es un DTO tipado en `float` por diseño, y toda la
aritmética interna de los módulos es `Fraction` pura hasta esa línea.

El sitio restante (`android_forensics.py:551`, `int(float(raw_ts))`) es auxiliar
(parseo de timestamp Chrome/WebKit) y no toca la aritmética de score, pero tiene una
pérdida de precisión real documentada abajo (timestamps WebKit en µs exceden 2⁵³).

**Veredicto del censo: ningún sitio dentro del alcance viola el invariante #4 de
CLAUDE.md** ("Determinism is not optional"), porque todos los consumidores aguas abajo
re-cuantizan el float por rutas deterministas (`Decimal(str(x)).quantize(...)`,
`Fraction(str(x))`, `_dround`). Sí se detectaron **4 hallazgos adyacentes** fuera del
alcance estricto pero dentro del path de scoring, incluyendo una recurrencia del patrón
pre-P0-001 en `_math_utils.py:341`. Ver §5.

---

## 1. Mapa de flujo de datos (contexto para la columna "riesgo")

```
Módulo SIFT (Fraction pura)
  └─ to_signal() ── float() ──►  SignalOutput DTO (float por contrato)
                                    │
        ┌───────────────────────────┼──────────────────────────────┐
        ▼                           ▼                              ▼
  z_score                      confidence                       value
        │                           │                              │
  sift_orchestrator.py:646     unified_timeline_engine.py:99   forensic_adapter.py:173
  Fraction(Decimal(str(z))     Fraction(Decimal(str(c))        raw_score = float(v)
  .quantize(0.01, HALF_EVEN))  .quantize(0.001, HALF_EVEN))         │
  ── fix P0-001 ──             ── fix P0-001 ──                caie.py:657/783
        │                           │                          _dround(Decimal(str(...)))
  gamma (Fraction) → :669           │                          ── determinista ──
  z_score=float(z_adjusted)    vigia_agent.py _to_frac()
        │                      Fraction(str(x)) exacta
        ├─► FRS (_math_utils: clamp_float_to_fraction →
        │    Fraction(v).limit_denominator(1e9), determinista)
        ├─► abductive_reasoner.py — comparaciones float
        │    (> 2.0, > 1.5, > 3.0, <= 0.5) — ver §5.3
        └─► vigia_agent.py L-036 override — _to_frac() → Fraction
```

Conclusión estructural: los tres campos float del DTO **sí llegan al scorer**, pero
cada punto de entrada re-cuantiza por una ruta determinista. El riesgo residual no es
no-determinismo sino (a) doble redondeo acotado por el paso de cuantización, y
(b) las comparaciones de umbral en float del reasoner (§5.3).

---

## 2. Censo — Categoría A: frontera `SignalOutput` (36 sitios)

Los 12 módulos comparten el patrón. En todos, `z` y `conf` son `Fraction` exactas en el
momento de la conversión (`z` con denominador 10; `conf = composite_score × 11/10
[× ARTIFACT_RELIABILITY]`, con `ARTIFACT_RELIABILITY` definida como `Fraction` en cada
módulo). `Z_CLIP_MAX` es `float 5.0` importado de `vigia/core/ebs_v1.py:76`.

### 2.1 Estilo Windows (10 módulos, 30 sitios): `value=float(z) / Z_CLIP_MAX`

| # | Sitio | Campo | Contexto |
|---|-------|-------|----------|
| 1–3 | `vigia/sift/shellbag_analyzer.py:60,61,62` | value, z_score, confidence | `to_signal()` de `ShellbagAnalysisResult` |
| 4–6 | `vigia/sift/amcache_shimcache.py:73,74,75` | value, z_score, confidence | `to_signal()` de resultado amcache/shimcache |
| 7–9 | `vigia/sift/memory_forensics.py:188,189` (189 tiene 2 calls) | value, z_score, confidence | `to_signal()` de resultado de memoria |
| 10–12 | `vigia/sift/disk_forensics.py:97,98` (98 tiene 2 calls) | value, z_score, confidence | `to_signal()` de resultado de disco |
| 13–15 | `vigia/sift/usb_device_tracker.py:61,62,63` | value, z_score, confidence | `to_signal()` de tracker USB |
| 16–18 | `vigia/sift/browser_forensics.py:88,89,90` | value, z_score, confidence | `to_signal()` de browser |
| 19–21 | `vigia/sift/unified_timeline_engine.py:60,61,62` | value, z_score, confidence | `to_signal()` de `TimelineAnalysisResult` |
| 22–24 | `vigia/sift/event_log_correlator.py:125,126` (126 tiene 2 calls) | value, z_score, confidence | `to_signal()` de correlator de event log |
| 25–27 | `vigia/sift/prefetch_analyzer.py:66,67,68` | value, z_score, confidence | `to_signal()` de prefetch |
| 28–30 | `vigia/sift/registry_timeline_reconstructor.py:142,143` (143 tiene 2 calls) | value, z_score, confidence | `to_signal()` de registry timeline |

**Qué hace el float ahí:** cierra la aritmética `Fraction` del módulo y puebla el DTO
`SignalOutput` (tipado `value: float, z_score: float, confidence: float` tanto en la
variante Pydantic como en la dataclass de `ebs_v1.py`). El validador del DTO además
clipea `z_score` a ±`Z_CLIP_MAX` y clampa `confidence` a [0,1] — ambos en float.

**Riesgo:** **BAJO — llega al scorer, pero por puertas de re-cuantización determinista.**
- `z_score`: los valores emitidos tienen ≤2 decimales (denominador 10, clip a 5), por lo
  que el round-trip `Fraction → float → str → Decimal.quantize(0.01) → Fraction`
  (orchestrator:646) es **sin pérdida** para todo valor actualmente emitible.
- `confidence`: `composite_score` puede producir fracciones con expansión decimal no
  terminante (p. ej. 1/3). `float()` + `quantize(0.001)` aguas abajo implica doble
  redondeo acotado a ±0.0005 — determinista, pérdida aceptada por diseño (mismo
  argumento empírico que L-040: 0 flips en 21 casos de corpus).
- `value`: consumido por CAIE como `raw_score` vía `Decimal(str(x))` + `_dround`
  (caie.py:657) — determinista.

**Fix propuesto:** **NO CAMBIAR el tipo del DTO** (decisión de alcance P0-001 vigente:
`SignalOutput` es float por contrato — los tools forenses externos emiten IEEE 754).
Mejora opcional de auditabilidad, no urgente:
- Emitir la fracción exacta en metadata: `metadata["z_frac"] = str(z)`,
  `metadata["conf_frac"] = str(conf)` en cada `to_signal()`. Costo trivial, permite a
  cualquier verificador tercero reconstruir el valor exacto sin depender del round-trip.
- Unificar el estilo de `value` con el móvil (ver §2.2): `float(z / Fraction(int(Z_CLIP_MAX)))`
  — un solo redondeo en vez de dos (`float(z)` y luego `/5.0`).

### 2.2 Estilo móvil (2 módulos, 6 sitios): `value=float(z / z_clip)`

| # | Sitio | Campo | Contexto |
|---|-------|-------|----------|
| 31–33 | `vigia/sift/ios_forensics.py:199,200,201` | value, z_score, confidence | `to_signal()` iOS; `z_clip = Fraction(int(Z_CLIP_MAX), 1)`; incluye `opsec_bump` con cap en Fraction |
| 34–36 | `vigia/sift/android_forensics.py:175,176,177` | value, z_score, confidence | `to_signal()` Android; mismo esquema que iOS, con comentario de frontera explícito |

**Qué hace el float ahí:** idéntico rol de frontera que §2.1, pero con una diferencia
técnica: la división se hace **en Fraction** (`z / z_clip` exacta) y se redondea una
sola vez al convertir. Es el estilo *más* correcto de los dos.

**Riesgo:** **BAJO** — igual que §2.1. Nota de consistencia: para un mismo `z`, el
estilo Windows (`float(z)/5.0`, dos redondeos) y el móvil (`float(z/5)`, un redondeo)
pueden diferir en el último ulp de `value`. Ambos son deterministas (IEEE 754), y la
diferencia desaparece tras el `_dround` de CAIE, pero es una asimetría gratuita.

**Fix propuesto:** ninguno necesario en iOS/Android — es el patrón de referencia.
Alinear los 10 módulos Windows a este estilo si se toca esa zona por otro motivo.

---

## 3. Censo — Categoría B: sitio auxiliar (1 sitio)

### 3.1 `vigia/sift/android_forensics.py:551` — `int(float(raw_ts))`

```python
ts = self._chrome_ts_to_unix(int(float(raw_ts))) if raw_ts is not None else 0
```

**Contexto:** parseo de `last_visit_time` (History de Chrome, SQLite). `raw_ts` sale
del driver sqlite3 normalmente como `int`; el `float()` existe para tolerar strings
con parte decimal (`"1.7e16"`, `"13300000000000.0"`). El resultado alimenta el campo
`timestamp` de findings de navegación — ordenamiento de timeline y metadata del bundle.

**Riesgo:** **BAJO — auxiliar, no llega a la aritmética del scorer.** Pero hay pérdida
de precisión real: los timestamps WebKit en microsegundos (~1.33×10¹⁶ para 2022+,
~1.7×10¹⁶ para 2024) **exceden 2⁵³ ≈ 9.0×10¹⁵**, el límite de representación entera
exacta de un double. `float(raw_ts)` puede desplazar el valor hasta ±2 µs. Como
`_chrome_ts_to_unix` divide luego a segundos, el efecto observable es un posible
corrimiento de ±1 segundo solo si el instante cae a <2 µs de un borde de segundo.
Determinista (siempre redondea igual), pero es imprecisión evitable en un artefacto
que puede terminar citado en un bundle sellado.

**Fix propuesto:**
```python
ts = self._chrome_ts_to_unix(int(Decimal(str(raw_ts)))) if raw_ts is not None else 0
```
`Decimal(str(...))` acepta int, float-string y notación científica sin pasar por la
mantisa de 53 bits (para `raw_ts` ya entero, `int(Decimal(str(x)))` es la identidad).
`Decimal` ya está importado en el módulo. Alternativa mínima: `int(raw_ts) if
isinstance(raw_ts, int) else int(Decimal(str(raw_ts)))`.

---

## 4. Tabla resumen del censo

| Categoría | Sitios | Riesgo | ¿Llega al scorer? | Acción |
|-----------|--------|--------|-------------------|--------|
| A — frontera `SignalOutput` (§2) | 36 | BAJO | Sí, re-cuantizado determinísticamente en cada consumidor | Mantener (contrato P0-001). Opcional: `z_frac`/`conf_frac` en metadata |
| B — timestamp Chrome (§3) | 1 | BAJO | No (metadata/timeline) | `int(Decimal(str(raw_ts)))` |
| **Total** | **37** | | | |

Conteo por módulo: 3 sitios en cada uno de los 11 primeros módulos; 4 en
`android_forensics.py` (3 de frontera + 1 auxiliar). El comentario de
`android_forensics.py:171` menciona "float" pero no es un call site.

---

## 5. Hallazgos adyacentes — fuera del alcance estricto, dentro del path de scoring

Detectados al trazar los consumidores. Se registran para triage posterior; **ninguno
fue tocado en esta auditoría**.

### 5.1 `vigia/sift/_math_utils.py:341` — recurrencia del patrón pre-P0-001 ⚠️

```python
composite_frac = Fraction(int(round(float(composite_raw) * 20)), 20)
```

Dentro de `apply_artifact_reliability_dynamic` (gamma dinámico L-038 para
`windows_event_log`), rama en que `composite_score` llega por metadata como numérico.
Es **exactamente la clase de bug que P0-001 corrigió** en el orchestrator: `round()`
sobre el resultado IEEE 754 de una pre-multiplicación (`1.245*100 = 124.4999…`).
Mitigante: la rama principal recibe `composite_score` como string `"num/den"` (parseo
exacto en :338-339), así que esta rama solo se ejercita con metadata numérica.
**Propuesta:** `composite_frac = Fraction(Decimal(str(composite_raw)))` y redondear a
granularidad 1/20 en aritmética racional: `Fraction(round(composite_frac * 20), 20)`
(round sobre Fraction es exacto).

### 5.2 Round-trips Fraction→float dentro de FRS — `_math_utils.py:419,557,650` y `sift_orchestrator.py:669`

FRS y gamma computan en Fraction pero escriben de vuelta `float(new_z_frac)` sobre el
atributo `z_score` del DTO, que luego se vuelve a levantar con
`clamp_float_to_fraction` (`Fraction(value).limit_denominator(10**9)` — determinista,
pero ruta de conversión distinta a `Fraction(str(x))`/`Decimal(str(x))` usada en el
resto del pipeline). Coherente con el contrato float del DTO; el costo es acumular
pares de redondeo por cada etapa (gamma → FRS → reasoner). Tolerable hoy; candidato a
homogeneizar la ruta de reconversión si se revisita L-040.

### 5.3 `vigia/inference/abductive_reasoner.py:139,185,213-214,239,332,406-407` — umbrales comparados en float

El reasoner clasifica señales con `s.z_score > 2.0 / > 1.5 / > 3.0 / <= 0.5` en float.
Los cuatro literales son exactamente representables en binario y los z emitidos por los
módulos tienen ≤2 decimales, así que hoy no hay caso que flippee. El riesgo teórico es
un `z_adjusted` (post-gamma, Fraction arbitraria) infinitesimalmente por encima de un
umbral que al pasar por `float()` (orchestrator:669) redondee exactamente al umbral e
invierta el `>`. Mismo perfil que L-040: sin impacto empírico en el corpus actual.
**Propuesta si se revisita:** comparar sobre `_to_frac(s.z_score)` como ya hace
`vigia_agent.py:847-848` para el override L-036.

### 5.4 `vigia/sift/android_forensics.py:338-340` — división float implícita en `_chrome_ts_to_unix`

`int(ts / 1_000_000)` usa división verdadera (float) sobre enteros ~1.7×10¹⁶. Error
relativo ~1e-16 → ~µs en el cociente; puede desplazar el segundo truncado solo en
bordes a <2 µs. No es un call site de `float()` (por eso no cuenta en el censo), pero
es la continuación del flujo de §3.1. **Propuesta:** división entera `ts // 1_000_000`
(equivale a la truncación actual de `int()` para positivos, sin pasar por float).

---

## 6. Método

1. Tag de restauración `restore-point-float-census-e0e7be0` creado antes de cualquier acción.
2. `grep -nE '\bfloat\s*\('` sobre los 12 archivos del alcance → 34 líneas, 37 call
   sites reales (4 líneas con 2 calls; 1 match en comentario descartado).
3. Lectura de contexto completo de cada `to_signal()` divergente (shellbag como
   representante del patrón Windows, unified_timeline, ios, android) y verificación
   por grep del patrón idéntico en los 8 restantes.
4. Trazado de consumidores de los tres campos float del DTO: `sift_orchestrator.py`
   (gamma :646/:669, FRS :693), `_math_utils.py` (FRS/clamp), `forensic_adapter.py` →
   `caie.py` (`raw_score`), `abductive_reasoner.py` (umbrales), `vigia_agent.py`
   (`_to_frac`, override L-036), `unified_timeline_engine.py` (consumo :99-101).
5. Cero modificaciones de código. Este documento es el único artefacto.

---

*VIGÍA — AUDIT P0-001 float census | 2026-07-07 | Solo investigación*
