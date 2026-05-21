# VIGÍA Integration Plan — SANS Hackathon 2026
## Deadline: 15 de junio | Entrega: GitHub Open Source

---

## VISIÓN GENERAL

Objetivo: Transformar VIGÍA de "herramienta forense" a **"motor de intención admisible bajo Daubert"** que:
1. Produce hipótesis de intención deterministas
2. Mapea a MITRE ATT&CK + PICERL de Rob T. Lee
3. Funciona con Claude Code + Ollama (sin dependencias estatales)
4. Es auditable por cualquier perito

---

## FASE 1: LAZY ABSTRACTION + VISIBLE VARIABLES (Semanas 1-2)

**Objetivo**: Implementar el principio de Vizel sin CHC solver completo.

### Hito 1.1: `VisibleVariablesEngine` — Selección Inteligente de Estado
**Archivo**: `vigia/engine/visible_variables.py` (NUEVO)
**Entrada**: `ForensicBundle` completo
**Salida**: Subconjunto de variables "visibles" en cada fase de IR

```python
class VisibleVariablesEngine:
    """
    Mapea fases de IR (acceso, persistencia, exfiltración) a sets de variables relevantes.
    
    Principio Vizel: No todas las variables son visibles en cada time frame.
    En IR: No todo el sistema es relevante en cada fase.
    
    Fases:
      - Acceso Inicial:      firewall logs, proxy, border sensors
      - Establecimiento:     registry, AD, scheduled tasks
      - Movimiento Lateral:  network flows, authentication logs
      - Persistencia:        cron, services, boot mechanisms
      - Exfiltración:        egress traffic, data exfiltration markers
      - Cobertura:           log deletion, artifact overwrite
    
    Para cada fase: define qué tipos de signos (Peirce) son "visibles".
    Ignora ruido que no es relevante en esa etapa.
    """
    
    def infer_phase(bundle: ForensicBundle) -> IRPhase:
        """Detecta automáticamente qué fase estamos observando."""
        pass
    
    def visible_variables(phase: IRPhase) -> Set[str]:
        """Retorna qué campos del bundle son relevantes en esta fase."""
        pass
    
    def focus_analysis(bundle: ForensicBundle) -> FocusedBundle:
        """Filtra el bundle dejando solo variables visibles."""
        pass
```

**Justificación Daubert**:
- Determinístico: Mapeo fase → variables es una tabla (no ML)
- Documentado: Cada variable visible tiene justificación NIST/SANS
- Reproducible: Mismo bundle → mismo foco siempre
- Falsable: Si detectamos variable Y en fase X pero Y no está visible en X → hipótesis de fase es incorrecta

**Dependencias**: 0 (puro Python stdlib)
**Riesgo**: Baja. Es un pre-filtro, no toca lógica de inferencia.

---

### Hito 1.2: Mapeo a Fases PICERL
**Archivo**: `vigia/forensics/picerl_mapping.py` (NUEVO)
**Propósito**: Conectar VIGÍA con el framework de Rob T. Lee

```python
class PICERLMapper:
    """
    PICERL: Preparar → Identificar → Contener → Erradicar → Recuperar → Aprender
    
    VIGÍA añade una dimensión transversal: INTENCIÓN
    
    En cada fase PICERL, VIGÍA responde:
      - Preparación:  "¿Qué intenciones anticipamos según threat intel?"
      - Identificación: "¿Qué intención infiere el conjunto de artefactos?"
      - Contención:    "¿Qué tipo de contención es apropiada para esta intención?"
      - Erradicación:  "¿Qué intención queremos eliminar?"
      - Recuperación:  "¿Cómo validamos que la intención está neutralizada?"
      - Lecciones:     "¿Qué aprendimos sobre la intención de este atacante?"
    
    Output: Reporte PICERL-I que mapea cada fase a hipótesis de intención VIGÍA.
    """
    
    def map_bundle_to_picerl_phase(
        bundle: ForensicBundle,
        threat_intel: Dict
    ) -> PICERLPhase:
        """Mapea el bundle al punto donde estamos en la cadena PICERL."""
        pass
    
    def infer_intent_by_phase(
        phase: PICERLPhase,
        bundle: ForensicBundle
    ) -> IntentHypothesis:
        """Para cada fase, produce una hipótesis de intención."""
        pass
    
    def generate_picerl_i_report(
        phases: List[PICERLPhase],
        hypotheses: List[IntentHypothesis]
    ) -> str:
        """Genera reporte en forma que Rob T. Lee lo entienda."""
        pass
```

**Entrada**: Datos del incidente + threat intel + timeline PICERL
**Salida**: Reporte que dice: "Basándose en la Identificación (PICERL fase 2), VIGÍA infiere que la intención es X con confianza Y"

**Justificación Daubert**:
- Conecta con metodología ya aceptada (PICERL de SANS)
- Separa el modelo de VIGÍA de la metodología operativa
- Reproducible: mismo input → mismo mapeo

**Riesgo**: Conceptual bajo, pero si Rob T. Lee ve que no entendemos PICERL, game over.

---

### Hito 1.3: Verificación Determinista — Herramienta "Nivel 1" (等保2.0)
**Archivo**: `vigia/governance/trust_levels.py` (NUEVO)

```python
class TrustLevelVerifier:
    """
    Implementa los 4 niveles de 等保2.0 (Verificación Confiable).
    Sin hardware real, pero con abstracción funcional.
    
    Nivel 1: Verificación básica en boot + alarma
    Nivel 2: + Auditoría centralizada en Security Management Center
    Nivel 3: + Verificación dinámica en puntos clave de ejecución
    Nivel 4: + Correlación dinámica en tiempo real (Peirce Terceridad)
    
    Uso: El usuario elige el nivel según criticidad del entorno.
    """
    
    def verify_level_1(bundle: ForensicBundle) -> VerificationResult:
        """Hash HMAC de boot + timestamp. Detección simple."""
        pass
    
    def verify_level_2(bundle: ForensicBundle, audit_center: AuditCenter) -> VerificationResult:
        """Level 1 + registros de auditoría centralizados."""
        pass
    
    def verify_level_3(bundle: ForensicBundle, checkpoints: List[ExecutionPoint]) -> VerificationResult:
        """Level 2 + verificación en puntos clave de ejecución."""
        pass
    
    def verify_level_4(
        bundle: ForensicBundle,
        correlation_engine: DynamicCorrelationEngine
    ) -> VerificationResult:
        """Level 3 + correlación dinámica de eventos (Peirce Terceridad)."""
        pass
```

**Justificación Daubert**:
- Explícito: El usuario sabe qué nivel está usando
- Progresivo: No obliga nivel 4 si nivel 2 es suficiente
- Documentable: "Caso X fue verificado bajo Nivel 2 (等保2.0)"

**Riesgo**: Muy bajo. Es arquitectura, no lógica de inferencia.

---

## FASE 2: MOTOR DE INTENCIÓN ABDUCTIVO (Semanas 2-3)

**Objetivo**: Implementar la "Idea 1" de Kimi en forma que funcione sin CHC solver.

### Hito 2.1: `AbductiveIntentEngine` — Hipótesis de Hábito

**Archivo**: `vigia/engine/abductive_intent.py` (NUEVO)

```python
class AbductiveIntentEngine:
    """
    Motor abductivo (no deductivo, no inductivo).
    
    Entrada: Secuencia de artefactos forenses = cadena de signos (Peirce)
    Salida: Hábito (habit) = hipótesis más simple sobre la intención del atacante
    
    Mecanismo:
      1. Cada artefacto es un signo peirceano:
         - Primeridad: dato bruto (hash, timestamp)
         - Segundidad: reacción observada (el ataque contra el artefacto)
         - Terceridad: intención propuesta (el hábito que explica por qué)
      
      2. Cadena de signos: sig_1 → sig_2 → sig_3 → ...
         Cada signo refina la interpretación anterior.
      
      3. Hábito propuesto: "Si esta secuencia ocurriera 1000 veces, ¿cuál sería
         la ley regular que la gobernaría?"
      
      4. Verificación: Comparar la hipótesis contra dataset histórico.
         ¿Ocurren patrones similares en ataques conocidos?
         ¿Es la hipótesis "simple" o requiere muchas excepciones?
    
    Output: IntentHypothesis con falsabilidad explícita.
    """
    
    def infer_habit(
        artifacts: List[ForensicArtifact],
        historical_dataset: Optional[Dict] = None
    ) -> IntentHypothesis:
        """
        Propone el hábito más simple que explique la secuencia.
        
        Usa Ockham's Razor:
          - Persistencia vs. Exfiltración vs. Lateral Movement vs. Sabotaje
          - Cada hipótesis tiene un "costo" (número de excepciones/supuestos)
          - La hipótesis con menor costo es la propuesta
        
        Returns:
            IntentHypothesis con campos:
              - habit_name: "Persistencia vía AD Golden Ticket"
              - confidence: 0.92
              - supporting_artifacts: [arc_id, arc_id, ...]
              - contradicting_artifacts: []
              - what_would_falsify: "Si encontramos Kerberos TGT en DC..."
              - reference_cis: ["CIS 5.4.1", ...]
        """
        pass
    
    def rank_hypotheses(
        candidates: List[IntentHypothesis],
        weighting: str = "simplicity"
    ) -> List[Tuple[IntentHypothesis, float]]:
        """
        Ordena hipótesis por probabilidad usando:
          - simplicity: menos supuestos = más probable
          - historical_frequency: ¿qué tan común es este patrón?
          - evidence_density: ratio de artefactos que soportan la hipótesis
        """
        pass
```

**Justificación Daubert**:
- Explícito: El "hábito" se declara en lenguaje natural
- Falsable: Campo `what_would_falsify` es fundamental
- Reproducible: Ockham's Razor es una regla matemática
- Sin cajanegra: No usa redes neuronales

**Riesgo**: CRÍTICO. Necesitamos una librería de patrones de "intención conocida" que sea sólida.

**Solución rápida**: Usar MITRE ATT&CK como fuente de verdad para patrones de intención.

---

### Hito 2.2: Mapeo MITRE ATT&CK ↔ Intención

**Archivo**: `vigia/forensics/mitre_intent_mapping.py` (ACTUALIZAR)

MITRE ATT&CK ya agrupa técnicas por **tácticas** (goals):
- Reconnaissance
- Resource Development
- Initial Access
- Execution
- Persistence
- Privilege Escalation
- Defense Evasion
- Credential Access
- Discovery
- Lateral Movement
- Collection
- Command and Control
- Exfiltration
- Impact
- Resource Hijacking

Cada táctica = un tipo de "hábito" o intención observable.

```python
class MITREIntentClassifier:
    """
    Clasifica intención basándose en cuál táctica MITRE está ocurriendo.
    
    Heurística simple pero poderosa:
      - Si observamos técnicas de "Persistence" → intención = mantenimiento de acceso
      - Si observamos "Exfiltration" → intención = robo de datos
      - Si observamos "Defense Evasion" + "Credential Access" → intención = lateral
      
    Ventaja: Rob T. Lee conoce MITRE ATT&CK al dedillo.
    """
    
    def artifacts_to_mitre_tactics(
        artifacts: List[ForensicArtifact]
    ) -> Dict[str, float]:  # tactic_name -> confidence
        """Mapea artefactos a tácticas MITRE."""
        pass
    
    def tactics_to_intent(tactics: Dict[str, float]) -> IntentHypothesis:
        """Convierte distribución de tácticas en hipótesis de intención."""
        pass
```

---

## FASE 3: DOCUMENTACIÓN PARA DAUBERT + PITCH (Semana 3)

### Hito 3.1: Actualización `DAUBERT_JUDICIAL.md`

Agregar secciones:
1. **Lazy Abstraction**: Explicar por qué "variables visibles" = reducción de falsos positivos
2. **Niveles de Confianza**: Tabla 等保2.0 con equivalentes forenses
3. **Abductive Intent Engine**: Explicar diferencia entre ML (inducción) y nuestro motor (abducción)
4. **PICERL-I Mapping**: Cómo VIGÍA se integra con SANS framework

### Hito 3.2: Génesis de VIGIA_STORY.md (Para Anna)

Este archivo es tuyo. Estructura sugerida:
- **Origen**: "El IR occidental se queda en reacción (Segundidad). VIGÍA propone Terceridad."
- **Por qué Israel + China + Rusia importan**: "Mostramos que el determinismo existe de facto en esos estados. VIGÍA lo formaliza para auditoría."
- **Por qué Rob T. Lee**: "Propone evolución de PICERL que él nunca escribió."
- **Visión**: "SIFT + VIGÍA = IR determinista y admisible en corte."

---

## FASE 4: INTEGRACIÓN CON CLAUDE CODE + OLLAMA (Semana 3)

### Hito 4.1: CLI Mejorada

```bash
# Modo explicativo (sin ejecutar)
vigia analyze --evidence-dir /path --explain

# Modo forense nivel 1-4
vigia analyze --evidence-dir /path --trust-level 2

# Salida PICERL-I
vigia report --format picerl-i --output reporte.md

# Salida para SIFT
vigia bundle --output evidence_bundle.ebs1
```

### Hito 4.2: Compatibilidad Ollama

Si Ollama está disponible → usarlo como "narrativa post-procesador" (explícitamente declarado).
Si no → salida estructurada YAML/JSON (determinista puro).

---

## DELIVERABLES FINALES (15 junio)

### GitHub
- `vigia/engine/visible_variables.py`
- `vigia/engine/abductive_intent.py`
- `vigia/forensics/picerl_mapping.py`
- `vigia/forensics/mitre_intent_mapping.py`
- `vigia/governance/trust_levels.py`
- Actualización `DAUBERT_JUDICIAL.md`

### Documentación
- `VIGIA_STORY.md` (bilingual: es/en) — Anna escribe
- `README_SANS_HACKATHON.md` — Pitch para Rob T. Lee
- Ejemplo completo: caso_002_log_fabrication → PICERL-I → Intención

### Verificación
- `check_determinism.py` pasando 100% en los módulos nuevos
- `verify_ebs_v1.py` validando bundles generados

---

## CRÍTICA A KIMI (para evitar sorpresas)

Kimi propone:
1. ✅ **Lazy Abstraction** → Hito 1.1 (HACIBLE)
2. ❌ **Counterfactual Intent Mapping** → Demasiado complejo para 3 semanas
3. ✅ **Habit Inference from ATT&CK** → Hito 2.2 (HACIBLE)
4. ✅ **Visible Variable Forensics** → Hito 1.1 (HACIBLE)
5. ✅ **Daubert Wrapper** → Ya existe, refinar
6. ✅ **PICERL-I** → Hito 1.2 (HACIBLE)
7. ⚠️ **Active Immunity by Intent** → Demo conceptual sin implementación real
8. ❌ **Peircean Chain of Custody** → Estructura teórica, sin código nuevo

**Prioridades REALES**: 1, 3, 4, 6, 5 (en ese orden)
**Posdata**: 7 y 8 son post-hackathon.

---

## RIESGOS Y MITIGACIONES

| Riesgo | Mitigation |
|--------|------------|
| Que Rob T. Lee diga "Esto no es IR" | Énfasis explícito en PICERL mapping + comparación con NIST |
| CHC solver = demasiado complejo | Usar Ockham + MITRE como proxy |
| Nivel 2 de 等保2.0 sin TPM real | Abstracción HMAC-based, documentar como "fallback open source" |
| Anna quiere VIGIA_STORY.md y no empieza | Entregarle outline y ella va editando |
| Ollama no está disponible | Todo debe funcionar sin él |

---

## TIMELINE (Hora/Fecha)

```
Hoy (24 abr):        Plan aprobado → Inicio Hito 1.1
Sem 1 (29 abr):      Hito 1.1 + 1.2 + 1.3 funcionales
Sem 2 (6 may):       Hito 2.1 + 2.2 funcionales
Sem 2.5 (13 may):    Hito 3.1 + 3.2 + testing
Sem 3 (20 may):      Hito 4.1 + 4.2 + documentación
15 junio:            GitHub ready + Pitch escrito
```

---

## PREGUNTAS PARA ANNIA

1. ¿Ese outline para VIGIA_STORY.md suena bien?
2. ¿Qué tanto detalle técnico debe tener el Pitch para Rob? (¿Él lee código o solo conceptos?)
3. ¿Ollama es "must have" o "nice to have"?
4. ¿Querés que haga auditoría de seguridad previa antes de publicar en GitHub?
