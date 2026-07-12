# GATE RECORD — Invariante 4: acumuladores exactos (Fraction) — 2026-07-12

Registro de aceptación del fix de determinismo del path de decisión, para
coordinar su porteo a la rama de implementación ANTES de M1. Este documento es
el "record firmado": todos los identificadores criptográficos y de git
necesarios para verificar el estado exacto que pasó el gate.

---

## ⚠️ AVISO DE COORDINACIÓN — leer antes de tocar la otra rama

**M1, M3, M2 y el lint semántico YA ESTÁN implementados, medidos y pusheados
en ESTA rama** (`claude/fossil-hunt-daubert-o85ou4`), por esta misma sesión:

| Etapa | Commit | Medición |
|---|---|---|
| M1 — TCV solo campos estructurados | `b3cb632` | 160→155 (el −5 de D-1) |
| M3 — paridad scorer↔CAIE | `3fe53ea` | 155→155 |
| M2 — discriminadores marker_class | `d91f31b` | 155→153 |
| Lint semántico + triage | `dbdb822` | 153 |
| D-5 retipado CAN-024 | `723efe8` | — |
| **Invariante 4 (este record)** | `3170616` | **bit-idéntico, 0 cambios** |
| Re-puntuación CAN-008/047 | `ff74092` | 153→155 |

Si la "otra sesión" arranca M1 desde main, **duplica trabajo ya hecho y va a
divergir**. Opciones limpias, en orden de preferencia:

1. **La rama de implementación ES esta rama** (o mergea esta rama completa):
   todo el orden M1→M3→M2→lint ya está, con Fraction e2e verificado encima.
2. **Cherry-pick solo del fix Fraction** (`3170616`) a una rama pre-M1: el
   commit toca únicamente el bloque de acumuladores de `vigia_scorer.py` (más
   test + gate script, archivos nuevos) — no colisiona con M1 (caie.py Rule 6)
   ni con M2 (caie.py Rule 1); roza el contexto de M3 (frozensets, ~40 líneas
   arriba) pero no sus líneas. **El gate es relativo al estado**: tras el
   cherry-pick hay que RE-CORRER el gate en esa rama (instrucciones abajo) —
   la bit-identidad se verifica en su propio contexto, no se hereda de este
   record.

## Qué es el fix

`vigia_scorer.py`, bloque de acumuladores de fracturas (commit `3170616`):
`fracture_malice_boost`/`fracture_credibility_penalty` acumulaban con float
`+=`, haciendo que el valor dependiera del ORDEN DE EMISIÓN de las fracturas.
Reproducción construida sobre el motor real: **2 flips de veredicto sellado**
(UNKNOWN↔SUSPICION en un cliff de redondeo de 5e-5) por puro orden de emisión.
Cualquier refactor de CAIE que reordene reglas (M1/M2 ya tocan el flujo) podía
cambiar veredictos sellados.

Fix quirúrgico: cada término conserva SU MISMO valor float de siempre (una
multiplicación sola no tiene orden); los términos se elevan exactos a
`Fraction` y se suman exactos (la suma exacta es asociativa y conmutativa);
una sola conversión a float en el cap. Semántica de caps preservada bit a bit
(suma CAIE → cap 0.5 → términos SU → re-cap).

## Evidencia del gate

**Gate 1 — bit-identidad de corpus (el criterio de aceptación acordado):**

```
Herramienta : scripts/experiments/fraction_gate.py (commiteada, portable)
Corpus      : 193 casos (find_cases(CASES_DIRS), doctrina del snapshot)
Campos      : verdict, repr(score), repr(fracture_malice_boost),
              repr(fracture_credibility_penalty), reason — repr COMPLETO,
              un drift de 1 ulp falla el gate
ANTES  (HEAD c343321) sha256: a5812d8c141318b082215b755e4d64ebc35404aa24e36634eff4c7cbfc42833a
DESPUÉS (fix aplicado) sha256: a5812d8c141318b082215b755e4d64ebc35404aa24e36634eff4c7cbfc42833a
Resultado   : GATE PASS — snapshots BYTE-IDÉNTICOS (mismo sha256).
              0 cambios de veredicto, 0 cambios de score a precisión float
              completa, en 193/193 casos.
```

**Gate 2 — el hazard desaparece:**

```
Repro construida (motor real, orden de emisión de fracturas permutado):
  ANTES del fix : REAL-ENGINE FLIPS: 2  (UNKNOWN<->SUSPICION, 0.0999 vs 0.1000)
  DESPUÉS       : REAL-ENGINE FLIPS: 0  (re-corrido, mismo script)
```

**Gate 3 — regresión permanente:**
`tests/test_invariant4_fraction_accumulators.py` — 9 tests: invariancia por
permutación (boost y penalty, incluidas tripletas de floats adversariales),
bit-compat legacy para 1–2 términos, cap en exactamente 0.5, semántica
SU-después-del-cap. Suite completa: **1218 passed / 37 xfailed** (21 fallos
e2e pre-existentes de entorno, verificados idénticos en el tag pre-sesión).

**Identificadores firmados:**

```
Commit del fix            : 3170616bda476d6fa92015667676a88e5af2902b
Blob vigia_scorer.py (fix): 02f839927f3962ec93b822d012ab80c0dbc03f4c
Estado base del gate      : c343321 (rama claude/fossil-hunt-daubert-o85ou4)
HEAD al escribir el record: ff7409295310fcf8c7b0d00ff6988293346ed81c
Snapshots del gate sha256 : a5812d8c141318b082215b755e4d64ebc35404aa24e36634eff4c7cbfc42833a (ambos)
```

(No hay VIGIA_HMAC_KEY en este entorno: la cadena de firma es git + los
sha256 de arriba. Con clave, firmar este archivo con HMAC al archivarlo.)

## Cómo re-correr el gate en la rama de implementación (obligatorio al portear)

```bash
# en la rama destino, ANTES de aplicar el cherry-pick:
python3 scripts/experiments/fraction_gate.py snapshot /tmp/gate_before.json
git cherry-pick 3170616
python3 scripts/experiments/fraction_gate.py snapshot /tmp/gate_after.json
python3 scripts/experiments/fraction_gate.py compare /tmp/gate_before.json /tmp/gate_after.json
# exit 0 + "GATE PASS" o el cherry-pick no se acepta
PYTHONPATH=. python3 -m pytest tests/test_invariant4_fraction_accumulators.py -q --no-cov
```

Nota: si la rama destino no tiene `scripts/experiments/fraction_gate.py`,
cherry-pickear primero (viene dentro de `3170616`), o copiar el archivo — es
autocontenido y solo-lectura.

## También en esta entrega (segunda mitad del encargo)

Re-puntuación aprobada aplicada (`ff74092`), medida en aislamiento antes y
verificada desde disco después:

- **CAN-008**: retipado D-5 + rúbrica (rootkit SSDT 0.05→0.90) →
  **MALICE 0.4359**, rama cross-domain, **cero fracturas, boost 0** —
  veredicto por masa de composite limpia.
- **CAN-047**: retipado D-5 + rúbrica (RWX 0.07→0.88, parent 0.07→0.80) →
  **MALICE 0.4233**, ídem.
- **CAN-046**: intacto — SUSPICION honesto (la banda defendible de la rúbrica
  no alcanza MALICE; contraejemplo benigno en corpus LINUX-005). Pendiente
  solo la decisión de reetiqueta (criterio CAN-026).
- Corpus: **153 → 155**, exactamente los 2 casos previstos, nada más se movió.
- `KNOWN_PENDING` actualizado: case_090/case_026 pasan de "pendiente
  re-puntuación" a la razón real remanente (divergencia de modos D-G: el motor
  sella MALICE, la capa CAIE-tool sigue NOISE por escala de fusión — ya no es
  un problema de datos).

## Follow-ups anotados (no incluidos en este fix, deliberadamente)

Del audit de determinismo (dossier D-E), quedan fuera de este cambio para no
ensanchar el diff gateado: `0.7**k` (libm pow) en el decay R4-3 → tabla
Fraction; crash por severity string/None en el hard gate (rutear por
`_sev_float`); reasociación de `math.prod` en cadenas Noisy-OR (hazard solo
ante refactor). Cada uno es un cambio chico con su propio gate bit-idéntico.
