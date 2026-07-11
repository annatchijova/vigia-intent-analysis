# VIGÍA PATCH NOTES — Tanda de Seguridad P0+P1+P2
## Fecha: 2026-05-06
## Auditor: Kimi (Red Team / Forensic Systems)
## Estado: LISTO PARA GIT COMMIT

---

### 🔴 CRÍTICAS (Corregidas)

#### V06 / V11 — `apply_conflict_penalty` penalizaba al DOMINANTE
- **Archivo**: `vigia/sift/_math_utils.py`
- **Problema**: La función aplicaba el factor de ajuste al source con MAYOR z y gamma, rebajándolo artificialmente. Esto permitía a un atacante silenciar señales legítimas de memoria inundando con logs falsos.
- **Fix**: La penalización `(1 - penalty * alpha)` ahora se aplica EXCLUSIVAMENTE a los NO-dominantes. El dominante conserva su z original y se marca `dominance_stable = True`.
- **Validación**: Los tests `test_conflict_dominance_stability.py` pasan con la lógica corregida.

#### V01 / V13 — TOCTOU en todo el pipeline
- **Archivo**: `vigia/core/path_guard.py`
- **Problema**: `validate()` y `safe_open()` estaban desacoplados; `verify_no_toctou()` nunca se invocaba en producción.
- **Fix**:
  - `safe_open()` ahora integra `O_NOFOLLOW` + `fstat` en descriptor + `flock` compartido.
  - Nuevo método `safe_read()` ejecuta `validate()` → `safe_open()` → `verify_no_toctou()` en un solo flujo atómico.
  - Eliminado `os.access()` (TOCTOU clásico); ahora se usa `fstat` sobre descriptor abierto.

#### V03 — Falsa protección contra symlinks
- **Archivo**: `vigia/core/path_guard.py`
- **Problema**: `Path.resolve()` SIGUE los symlinks, por lo que `p.is_symlink()` nunca se activaba.
- **Fix**: Se reemplazó `resolve()` por `absolute()` + verificación explícita de symlinks en TODOS los componentes de la ruta con `lstat()`.

#### V18 — OverflowError en conversión `float → Fraction`
- **Archivos**: `_math_utils.py`, `abductive_reasoner.py`, `adversarial_robustness.py`
- **Problema**: `Fraction(int(round(z * 100)), 100)` explota con `OverflowError` si `z` es `1e308` o `inf`.
- **Fix**: Nueva función `clamp_float_to_fraction()` que:
  - Clampea a rango `[0, 10]` por defecto.
  - Detecta `NaN` e `inf`.
  - Usa `limit_denominator(10**9)` para evitar números astronómicos.

#### V24 — Suplantación de binarios externos vía PATH
- **Archivos**: `memory_forensics.py`, `registry_timeline_reconstructor.py`
- **Problema**: `vol` y `rip.pl` se invocan sin ruta absoluta; un atacante puede envenenar PATH.
- **Fix**: Nuevo método `_validate_binary()` que exige ruta absoluta o resuelve via `shutil.which()` con `FileNotFoundError` si no se encuentra.

---

### 🟠 ALTAS (Corregidas)

#### V07 — XML Billion Laughs / XXE
- **Archivo**: `event_log_correlator.py`
- **Fix**: Importa `defusedxml.ElementTree` con guard. Si `defusedxml` no está
  instalado, NO hay fallback a `xml.etree` (decisión deliberada anti-XXE):
  los artefactos XML/EVTX quedan marcados `UNANALYZED_ARTIFACT` y el caso
  degrada honestamente a ABSTAIN. (Nota: una versión anterior de esta entrada
  describía un fallback `ET.fromstring(..., forbid_dtd=True)` que no existe
  en el código vivo.)

#### V19 — DoS por `Fraction` gigante en IOC Manager
- **Archivo**: `ioc_manager.py`
- **Fix**: Nueva función `_safe_fraction()` que valida rango `[0,1]` y usa `limit_denominator(1000)`.

#### V08 — `_sqrt_fraction` inseguro para enteros grandes
- **Archivo**: `_math_utils.py`
- **Problema**: `int(x.numerator ** 0.5)` falla con `OverflowError` si el numerador > 2**53.
- **Fix**: Reimplementado con método de Newton puro sobre `Fraction` (50 iteraciones, sin `float()` intermedio).

---

### 🟡 MEDIAS (Corregidas)

#### V15 — `_parse_iso_timestamp` falla silenciosamente con epoch 0
- **Archivo**: `_math_utils.py`
- **Fix**: Ahora lanza `ValueError` en vez de devolver `0`. Valida rango 2000–2100.

#### V16 / V20 / V26 — CCS manipulable vía entropía causal
- **Archivo**: `signal_mapper.py`
- **Fix**:
  - Entropía máxima ahora se calcula sobre causas reales observadas (no valor fijo 4.7).
  - Factor de entropía acotado a `max(1 - entropy, 0.5)` para evitar que fuerce ABSTAIN arbitrariamente.
  - Señales raíz ampliadas a TODOS los motores SIFT.

#### V14 — `safe_open` sin validación de archivo regular
- **Archivo**: `path_guard.py`
- **Fix**: Verificación `stat.S_ISREG()` antes de abrir; rechaza FIFOs, devices, etc.

#### V25 — Umbral fijo de 5 archivos para timestomping masivo
- **Archivo**: `disk_forensics.py`
- **Fix**: Umbral reducido de `>= 5` a `>= 3` para evadir lotes de 4.

#### V27 — Umbral de entropía de beaconing hardcodeado a 3.5 bits
- **Archivo**: `network_forensics.py`
- **Fix**: Reemplazado por score compuesto dinámico:
  - Entropía relativa al máximo teórico para `n` muestras.
  - CV + periodicidad + entropía + Mann-Kendall ponderados.
  - Umbral final: `beacon_score >= 0.7`.

---

### 🟢 BAJAS / INFORMATIVAS (Corregidas o documentadas)

#### V09 / V22 — Colisión de entropía por falta de separador
- **Archivo**: `_math_utils.py`
- **Fix**: `_entropy_shannon()` ahora acepta `List[Any]` y calcula directamente sobre valores. Para strings usa conteo de caracteres individual (no serialización insegura).

#### V12 — Convergencia insuficiente de `_log_rational`
- **Archivo**: `_math_utils.py`
- **Fix**: Aumentado de 20 a 40 términos Taylor + clamping de entrada a rango `[1e-50, 1e50]`.

#### V28 — Bucle de normalización en logaritmo sin límite
- **Archivo**: `_math_utils.py`
- **Fix**: El clamping anterior previene iteraciones millonarias.

#### V23 — Motores abductivos duplicados
- **Nota**: `abductive_reasoner_v2.py` está disponible pero NO conectado al orquestador. Se mantiene para migración futura.

---

## Instrucciones para Git

```bash
# 1. Reemplazar archivos en tu repo
cp /mnt/agents/output/vigia_patched/*.py /ruta/a/tu/repo/vigia/

# 2. Revisar diff
git diff

# 3. Commit limpio
git add -A
git commit -m "SECURITY: P0+P1+P2 patches — TOCTOU, anti-silencing, float overflow, XML hardening, PATH validation"

# 4. Tag para la hackathon
git tag -a v1.1-security -m "Tanda de seguridad post-auditoría Kimi"
```

## Dependencias nuevas recomendadas

```bash
pip install defusedxml  # V07 — Protección XML
```

---
*Generado por Kimi para el Colectivo VIGÍA — SANS Hackathon 2026*


---

## Tanda Funcional P3 — 2026-05-06 (segunda pasada)

### 🔧 Completitud funcional

#### `_entropy_shannon` homogeneizado
- **Archivos**: `network_forensics.py`, `metabolic_profiler.py`, `behavioral_fingerprint.py`, `signal_mapper.py`
- **Cambio**: Todos los callers ahora pasan `List[Any]` en lugar de strings concatenados. Elimina colisiones (ej. `[12,34]` vs `[123,4]`).

#### `disk_forensics.py` — timestamp real
- **Cambio**: `now = int(time.time())` reemplaza el epoch fijo `1715000000`.

#### `unified_timeline_engine.py` — robustez ante timestamps inválidos
- **Cambio**: `_extract_timestamp()` ahora captura `ValueError` y devuelve `0` sin detener el pipeline.

#### Stubs transparentes
- **Archivos**: `usb_device_tracker.py`, `browser_forensics.py`, `shellbag_analyzer.py`, `amcache_shimcache.py`, `prefetch_analyzer.py`
- **Cambio**: Metadatos incluyen `"stub": True` cuando el análisis es simulado.

#### `defusedxml` obligatorio
- **Archivo**: `event_log_correlator.py`
- **Cambio**: `ImportError` explícito si no está instalado. Protección XXE garantizada.

#### AbductiveReasonerV2 integrado
- **Archivo**: `abductive_reasoner.py` (nuevo bridge)
- **Cambio**: Wrapper que expone API v1 (`reason(signals)`) pero ejecuta motor v2 internamente (CCS, veto, veredicto Daubert). El orquestador no requiere cambios de API.

---

## Dependencias obligatorias

```bash
pip install defusedxml>=0.7.1
```

## Checklist pre-commit

- [ ] `_entropy_shannon` recibe listas en todos los módulos
- [ ] `pytest` pasa sin regresiones
- [ ] `defusedxml` instalado
- [ ] Stubs marcados con `"stub": True`
- [ ] `AbductiveReasonerV2` ejecuta via bridge
