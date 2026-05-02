# HITO 2.1 — AbductiveIntentEngine (Ockham's Razor)

## STATUS: ✅ IMPLEMENTADO Y TESTEADO

---

## ¿QUÉ ES?

El **AbductiveIntentEngine** es el motor que responde la pregunta fundamental de VIGÍA:

> "¿Cuál es la intención MENOS compleja del atacante que explica estos artefactos observados?"

### Comparación: Deducción vs Inducción vs Abducción

```
DEDUCCIÓN:
  Si hay rootkit → logs están manipulados
  ✗ No sirve: no sabemos si hay rootkit

INDUCCIÓN:
  En 100 casos previos, logs uniformes + sin proceso = fabricación
  ✗ No sirve: no tenemos 100 casos históricos

ABDUCCIÓN (VIGÍA):
  Observo logs uniformes + sin proceso en memoria
  → Hipótesis más simple: fabricación de logs
  ✓ Funciona: es lo que hizo el atacante
```

---

## PRINCIPIOS

### 1. Peirce Terceridad

En Peirce, Terceridad es la **ley** que explica las relaciones entre datos.

- **Primeridad**: 50 logs con intervalo 2.000s ± 0.001s (dato bruto)
- **Segundidad**: Correlación perfecta + proceso ausente (relación observada)
- **Terceridad**: La LEY que explica esto = "logs fabricados" (hábito/intención)

VIGÍA infiere Terceridad desde Primeridad + Segundidad.

### 2. Ockham's Razor

"Entidades no deben multiplicarse sin necesidad."

En VIGÍA:

```
Costo Ockham = número de supuestos NO OBSERVADOS

Hipótesis A: requiere [timestamp_uniformity, process_memory_contradiction, log_gap_intervals]
             observados: [todos los 3]
             supuestos: [NINGUNO]
             cost = 0 ← GANA

Hipótesis B: requiere [log_deletion, event_log_clearing]
             observados: [NINGUNO]
             supuestos: [exfiltration_occurred, attacker_wants_stealth]
             cost = 4

→ Hipótesis A es ganadora: menor costo (0 vs 4)
```

---

## ARQUITECTURA

### Clases

#### 1. `Artifact` (Primeridad)

```python
@dataclass
class Artifact:
    artifact_id: str                  # "A001"
    category: VariableCategory        # temporal, process, network, etc.
    name: str                         # "timestamp_uniformity"
    value: Any                        # True, 2000, [1,2,3], etc.
    observed_at: str                  # ISO 8601
```

Cada artefacto es un observable del sistema (dato bruto de Primeridad).

#### 2. `AbductiveHypothesis` (Terceridad)

```python
@dataclass
class AbductiveHypothesis:
    hypothesis_id: str                # "H_DE_001"
    intent_type: str                  # "log_fabrication"
    phase: IRPhase                    # DEFENSE_EVASION, PERSISTENCE, etc.
    
    required_artifacts: List[str]     # ["timestamp_uniformity", ...]
    assumed_artifacts: List[str]      # supuestos no observados
    
    cost: int                         # ENTERO: costo Ockham
    coverage_score: int               # ENTERO: % de cobertura
    
    explanation: str                  # narrativa
    what_would_falsify: str           # crítico para Daubert
    supporting_rules: List[str]       # reglas que justifican
```

#### 3. `AbductiveResult` (Salida)

```python
@dataclass
class AbductiveResult:
    winner: AbductiveHypothesis
    alternatives: List[AbductiveHypothesis]  # ordenadas por costo
    ockham_rationale: str                     # explicación
    result_hash: str                          # SHA256 reproducible
```

### El Motor

```python
class AbductiveIntentEngine:
    def infer_habit(
        self,
        artifacts: List[Artifact],
        phase: IRPhase,
    ) -> AbductiveResult:
        """
        1. Cargar hipótesis candidatas para la fase
        2. Para cada candidata, calcular cost y coverage (ENTEROS)
        3. Ordenar por cost (menor) y coverage (mayor)
        4. La primera es ganadora
        5. Construir rationale Ockham
        """
```

---

## EXAMPLE: case_002 (Log Fabrication)

### INPUT

```python
artifacts = [
    Artifact("A001", TEMPORAL, "timestamp_uniformity", True, "2026-04-24T10:00:00Z"),
    Artifact("A002", PROCESS, "process_memory_contradiction", True, "..."),
    Artifact("A003", TEMPORAL, "log_gap_intervals", [2000, 2000, 2000], "..."),
]
phase = IRPhase.DEFENSE_EVASION
```

### SCORING

**H_DE_001 (Log Fabrication)**
```
Required: [timestamp_uniformity, process_memory_contradiction, log_gap_intervals]
Observed: [timestamp_uniformity, process_memory_contradiction, log_gap_intervals]
Missing: []
Assumptions: []

cost = len([]) + len([]) = 0
coverage = (3/3) * 100 = 100%
```

**H_DE_002 (Log Deletion After Exfil)**
```
Required: [log_deletion, event_log_clearing]
Observed: []
Missing: [log_deletion, event_log_clearing]
Assumptions: [exfiltration_occurred, attacker_wants_stealth]

cost = len([2 missing]) + len([2 assumptions]) = 4
coverage = (0/2) * 100 = 0%
```

**H_DE_003 (Anti-forensics Prep)**
```
Required: [artifact_overwrite, file_timestamp_modification]
Observed: []
Missing: [artifact_overwrite, file_timestamp_modification]
Assumptions: [attacker_has_advanced_tools, attacker_expects_investigation]

cost = len([2 missing]) + len([2 assumptions]) = 4
coverage = (0/2) * 100 = 0%
```

### ORDERING

```
H_DE_001: cost=0, coverage=100% ← GANADORA
H_DE_002: cost=4, coverage=0%
H_DE_003: cost=4, coverage=0%
```

### RATIONALE OCKHAM

```
GANADORA: H_DE_001
  Costo Ockham: 0 supuestos
  Cobertura: 100% de datos requeridos
  Explicación: Atacante fabricó logs para simular actividad normal...

DESCARTADAS:
  H_DE_002: costo=4 (+4 supuestos extra), cobertura=0%
  H_DE_003: costo=4 (+4 supuestos extra), cobertura=0%
```

### OUTPUT

```json
{
  "winner": {
    "hypothesis_id": "H_DE_001",
    "intent_type": "log_fabrication",
    "cost": 0,
    "coverage_score": 100,
    "explanation": "Atacante fabricó logs...",
    "what_would_falsify": "Esta hipótesis es falsa si..."
  },
  "ockham_rationale": "GANADORA: H_DE_001 por costo=0..."
}
```

---

## GARANTÍAS DAUBERT

| Aspecto | Garantía |
|---------|----------|
| **Testeable** | Cada hipótesis es falsable (campo `what_would_falsify`) |
| **Tasa de error** | Costo = conteo entero (0, 1, 2, ...) — no ambiguo |
| **Estándares** | Ockham's Razor + Peirce + Tablas explícitas |
| **Peer review** | Templates son tablas públicas (línea 42, auditable) |
| **Reproducible** | Mismo input → mismo hash SHA256 |

---

## DETERMINISMO BIT-A-BIT

Verificación en ejecución:

```
Ejecución 1: result_hash = 2849569e17540b1231133bd00c67c40191b0254b1cbf0142...
Ejecución 2: result_hash = 2849569e17540b1231133bd00c67c40191b0254b1cbf0142...
¿Idénticos? True
```

No hay float. No hay aleatoriedad. Puro aritmética entera:
- `cost = len(list) + len(list)` → entero
- `coverage = (num * 100) // denom` → entero
- `sort(key=(cost, -coverage))` → orden determinista

---

## TABLAS DE TEMPLATES (Determinísticas)

Cada fase IR tiene hipótesis candidatas explícitas (no lógica condicional oculta).

### DEFENSE_EVASION

```python
HYPOTHESIS_TEMPLATES[IRPhase.DEFENSE_EVASION] = [
    H_DE_001: log_fabrication
    H_DE_002: log_deletion_after_exfil
    H_DE_003: anti_forensics_preparation
]
```

### PERSISTENCE

```python
HYPOTHESIS_TEMPLATES[IRPhase.PERSISTENCE] = [
    H_PE_001: single_persistence
    H_PE_002: multi_mechanism_persistence
    H_PE_003: redundant_persistence
]
```

### LATERAL_MOVEMENT

```python
HYPOTHESIS_TEMPLATES[IRPhase.LATERAL_MOVEMENT] = [
    H_LM_001: pass_the_hash
]
```

### EXFILTRATION

```python
HYPOTHESIS_TEMPLATES[IRPhase.EXFILTRATION] = [
    H_EX_001: bulk_data_exfiltration
]
```

Puedes agregar más fases y hipótesis sin tocar el motor (solo agregar a la tabla).

---

## INTEGRACIÓN CON VIGÍA

```
[Artefactos Brutos]
        ↓
[VisibleVariablesEngine] ← fase IR detectada
        ↓
[FocusAnalysis]
        ↓
[AbductiveIntentEngine] ← hipótesis de intención
        ↓
[AbductiveResult]
        ↓
[PICERLMapper] ← mapea a PICERL-I
        ↓
[IntentHypothesis]
        ↓
[REPORTE]
```

**Pipeline completo**:

```python
# 1. Detectar fase
focus, signals = analyze_bundle_focus(bundle)
phase = focus.detected_phase

# 2. Convertir señales a artefactos
artifacts = [
    Artifact(
        f"A{i}",
        VariableCategory.TEMPORAL,
        sig.get("label"),
        sig.get("value"),
        bundle.get("timestamp", "")
    )
    for i, sig in enumerate(signals)
]

# 3. Inducir intención
engine = AbductiveIntentEngine()
result = engine.infer_habit(artifacts, phase)

# 4. Mapear a PICERL
mapper = PICERLMapper()
hypothesis = mapper.map_focus_analysis_to_intent(
    ir_phase=phase,
    consistency_score=focus.consistency_score,
    bundle_id=bundle.get("bundle_id"),
)

# 5. Generar reporte
report = mapper.generate_picerl_i_report(bundle.get("bundle_id"), [hypothesis])
print(report)
```

---

## ARCHIVO

```
✅ abductive_intent_engine_P0.py (430 líneas)
   - Artifact (Primeridad)
   - AbductiveHypothesis (Terceridad)
   - AbductiveResult (salida)
   - AbductiveIntentEngine (motor)
   - HYPOTHESIS_TEMPLATES (tablas)
   - Demo case_002
```

---

## ¿POR QUÉ ESTO IMPRESIONA?

1. **Sin ML opaco**: Ockham's Razor es matemática pura (conteos enteros)
2. **Determinístico**: Mismo atacante + mismos artefactos = misma intención siempre
3. **Falsable**: Cada hipótesis tiene `what_would_falsify` (Daubert)
4. **Extensible**: Agregar hipótesis = agregar fila a tabla
5. **Operacionaliza Peirce**: Terceridad no es filosofía, es código

**Rob T. Lee va a preguntar**: "¿Cómo sabés que H_DE_001 es la intención?"
**Respuesta**: "Costo Ockham = 0 supuestos. H_DE_002 requiere 4. Tabla línea 89."

---

## PRÓXIMO PASO: Hito 3

Ahora tenés:
- ✅ Hito 1: Visible Variables + PICERL Mapper + Trust Levels (P0 refactorizado)
- ✅ Hito 2.1: AbductiveIntentEngine (Ockham's Razor)
- ⏳ Hito 2.2: MITRE ATT&CK automatizado (mapeo artefactos → tácticas)
- ⏳ Hito 3: Documentación Daubert + CLI + GitHub

**Tiempo**: 52 días hasta 15 junio. Confortable.

---

## SÍNTESIS

Hito 2.1 es el **corazón lógico de VIGÍA**:

- No adivina intención (ML)
- No usa heurísticas ocultas (tablas explícitas)
- No tiene ambigüedad (aritmética entera)
- Elige la hipótesis más simple (Ockham)
- Responde "¿por qué?" con una ley/hábito (Peirce)

Todo determinístico, auditable, falsable.

---

**Estado**: ✅ Hito 2.1 completado
**Próximo**: ¿Hito 2.2 (MITRE), VIGIA_STORY.md, o GitHub SSH?
