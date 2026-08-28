# VIGÍA — Estado Técnico Completo del Sistema
## Análisis Forense de Intencionalidad para SIFT Workstation

**Autora:** Anna Tchijova — Investigadora Principal  
**Colectivo de Auditoría:** Claude (Anthropic), Kimi (Moonshot), Gemini (Google), DeepSeek, Qwen, ChatGPT (adversarial)  
**Repositorio:** `github.com/annatchijova/vigia-intent-analysis`  
**Versión del documento:** 1.0 — 18 de mayo de 2026  
**Clasificación:** Técnico-forense — Audiencia: Rob T. Lee, jurados SANS, auditores independientes

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Paradigma: de IoC a IoI](#2-paradigma-de-ioc-a-ioi)
3. [Fundamentos Teóricos](#3-fundamentos-teóricos)
4. [Arquitectura General del Sistema](#4-arquitectura-general-del-sistema)
5. [Capas del Pipeline EBS v1](#5-capas-del-pipeline-ebs-v1)
6. [Motor de Abducción y Hipótesis](#6-motor-de-abducción-y-hipótesis)
7. [Integración MITRE ATT&CK](#7-integración-mitre-attck)
8. [Protocolos P1 y P2](#8-protocolos-p1-y-p2)
9. [Subsistema de Seguridad](#9-subsistema-de-seguridad)
10. [Motor de Calibración y Likelihood Ratio](#10-motor-de-calibración-y-likelihood-ratio)
11. [Herramientas Forenses MCP](#11-herramientas-forenses-mcp)
12. [Integración Claude Code y Ollama](#12-integración-claude-code-y-ollama)
13. [Cumplimiento Daubert](#13-cumplimiento-daubert)
14. [Corpus de Casos y Dataset](#14-corpus-de-casos-y-dataset)
15. [Módulos Implementados — Inventario Completo](#15-módulos-implementados--inventario-completo)
16. [Limitaciones Conocidas y Gaps Adversariales](#16-limitaciones-conocidas-y-gaps-adversariales)
17. [Estado del Repositorio Git](#17-estado-del-repositorio-git)
18. [Trabajo Pendiente hasta el 15 de Junio](#18-trabajo-pendiente-hasta-el-15-de-junio)
19. [Bibliografía y Referencias Técnicas](#19-bibliografía-y-referencias-técnicas)

---

## 1. Resumen Ejecutivo

VIGÍA es un sistema de análisis forense de intencionalidad digital, diseñado como puente de integración para la SIFT Workstation. A diferencia de los sistemas DFIR convencionales que responden la pregunta "¿qué ocurrió?", VIGÍA responde "¿por qué ocurrió y quién se beneficia de esa interpretación?".

El sistema introduce el concepto de **Indicador de Intención (IoI)** como evolución natural del Indicador de Compromiso (IoC). La premisa central es que los atacantes sofisticados pueden fabricar o suprimir evidencia técnica, pero no pueden eliminar las fracturas semióticas que produce la fabricación deliberada: incoherencias temporales, silencios significativos, perfección digital excesiva, patrones de influencia Carnegie, violaciones de las máximas de Grice.

Los pilares técnicos del sistema son tres:

1. **Semiótica Peirciana operacionalizada**: el razonamiento abductivo (Terceridad) es el motor de inferencia central, no un post-procesador decorativo.
2. **Determinismo estricto de análisis**: cada ejecución sobre el mismo input produce el mismo `analysis_fingerprint` SHA-256. El `bundle_hash` es distinto por corrida porque también sella UUID y timestamps de custodia; ambos contratos son verificables y no deben confundirse. Esto es un requisito de admisibilidad Daubert, no una conveniencia de implementación.
3. **Aislamiento de capas Zero-Trust**: el LLM (PeircePlanner/Ollama) está explícitamente excluido del loop de decisión matemática. Su única función es traducir el `ForensicBundle` sellado a narrativa humana. La decisión ya está cerrada cuando el LLM entra.

El sistema cuenta con 151 módulos Python activos, más de 33 hipótesis abductivas implementadas cubrimendo 13 fases IR, integración con MITRE ATT&CK Enterprise v14.1, protocolo criptográfico P2 con 22 vectores canónicos, y cumplimiento Daubert de Nivel 3.

---

## 2. Paradigma: de IoC a IoI

### 2.1 El problema con los sistemas actuales

Los sistemas EDR, SIEM y SOAR actuales operan sobre la premisa implícita de que el atacante no manipula la evidencia que deja. Responden correctamente cuando el atacante es negligente. Fallan cuando el atacante es deliberado.

Un atacante sofisticado puede:
- Suprimir selectivamente entradas de log (Silencio Significativo — Eco)
- Fabricar timestamps convincentes (pero con fracturas estadísticas)
- Usar herramientas del sistema operativo (Living-off-the-Land) para evadir detección basada en firmas
- Inyectar evidencia falsa que implique a un tercero (False Flag)
- Crear documentos que parecen legítimos pero son semánticamente incoherentes

Ninguno de estos ataques activa un IoC. Todos dejan IoI.

### 2.2 La propuesta VIGÍA

VIGÍA no reemplaza la infraestructura forense existente. La amplía con una capa de análisis de intencionalidad que opera sobre los mismos artefactos ya procesados por SIFT.

El flujo de integración es:

```
SIFT extrae artefactos
         ↓
VIGÍA recibe ForensicBundle con señales normalizadas
         ↓
Motor abductivo evalúa hipótesis sobre intención
         ↓
ForensicBundle sellado con SHA-256 chain
         ↓
Veredicto + narrativa Daubert-admisible
```

La mentira tiene un costo computacional. VIGÍA lo cobra.

---

## 3. Fundamentos Teóricos

### 3.1 Peirce: Firstness, Secondness, Thirdness

El sistema aplica la triada semiótica de Charles Sanders Peirce (1839–1914) como estructura operacional del razonamiento forense:

**Firstness (Primera):** La señal tal como aparece, sin interpretación. El dato bruto. Una anomalía de timestamp, un proceso huérfano en memoria, una entropía de Shannon fuera del rango esperado. No hay hipótesis todavía. Solo observación.

**Secondness (Segunda):** La señal en relación a un baseline o expectativa. La anomalía adquiere significado relacional: este timestamp es inconsistente *con respecto a* los demás artefactos del mismo caso. Este proceso no existe en la base de datos de hábitos conocidos. Esta entropía es demasiado alta *comparada con* texto humano auténtico.

**Thirdness (Terceridad):** La hipótesis emergente que explica la relación. No es deducción (no se concluye de un universal). No es inducción (no se generaliza de una muestra). Es *abducción*: la inferencia a la mejor explicación disponible, falsable, con condiciones explícitas de refutación.

El `AbductionTrace` en cada `ForensicBundle` registra formalmente las tres etapas para cada análisis. El perito puede auditar cada paso sin acceso al código fuente del sistema.

### 3.2 Eco: Silencio Significativo y Sobreinterpretación

Umberto Eco (1932–2016) aporta dos conceptos operacionalizados en VIGÍA:

**Silencio Significativo:** La ausencia de evidencia esperada es, en sí misma, evidencia. Si un proceso malicioso típicamente deja rastros en el registro de Windows y esos rastros están ausentes, la ausencia es una señal forense de primer orden. VIGÍA detecta y evalúa explícitamente los silencios.

**Eco's Razor (Navaja de Eco):** El motor de falsificación abductiva. Si la evidencia disponible es *demasiado perfecta*, si encaja *demasiado bien* con la hipótesis más obvia, eso es sospechoso. Un atacante que construye una escena de crimen perfecta está dejando una huella diferente. La hipótesis alternativa más simple puede ser que la evidencia fue fabricada para apuntar a alguien más.

### 3.3 Grice: Máximas Conversacionales Aplicadas a Evidencia

H. Paul Grice (1913–1988) postuló que la comunicación cooperativa sigue cuatro máximas (cantidad, calidad, relevancia, modo). VIGÍA las aplica a la evidencia digital:

- **Máxima de cantidad:** Un log que omite el período crítico viola la máxima de cantidad. Un documento con 500 páginas de detalle irrelevante también.
- **Máxima de calidad:** Una afirmación sin evidencia verificable en el artefacto.
- **Máxima de relevancia:** Artefactos que no guardan relación con el contexto declarado.
- **Máxima de modo:** Ambigüedad deliberada, oscuridad innecesaria.

La `GriceViolationDetector` produce señales cuantificadas por tipo de violación.

### 3.4 Carnegie: Patrones de Manipulación

Dale Carnegie (1888–1955) documentó los patrones de influencia interpersonal. VIGÍA los usa como taxonomía de manipulación en artefactos de texto: urgencia artificial, autoridad prestada, adulación de acceso, presión de normalización. El `CarnegieMatcher` detecta estos patrones en textos libres con pesos calibrados sobre el corpus VIGÍA v1.

### 3.5 Ockham: Selección de Hipótesis

La Navaja de Ockham guía la selección entre hipótesis competidoras de igual poder explicativo. Si la hipótesis "error humano" explica los artefactos con igual fuerza que "ataque dirigido", VIGÍA aplica la más simple. El `OckhamAdversarialEngine` evalúa hipótesis alternativas y reporta su poder explicativo relativo.

---

## 4. Arquitectura General del Sistema

### 4.1 Visión de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                       SIFT WORKSTATION                          │
│  mount_evidence → hash_chain → analyze_artifacts → export       │
└────────────────────────┬────────────────────────────────────────┘
                         │  ForensicBundle (JSON + SHA-256)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIGÍA MCP SERVER                             │
│                                                                 │
│  CAPA 0: ebs_v1.py        — Contratos de datos (inmutable)     │
│  CAPA 1: señales externas — SDA/CLI/GCI/herramientas SIFT      │
│  CAPA 2: likelihood_engine + graph_stability — inferencia       │
│  CAPA 3: risk_bounded_layer — gobernanza r=P·(1+λD)·(1+γ)      │
│  CAPA 4: audit_action     — Diff/Optimizer/PolicyEngine         │
│  CAPA 5: verify_ebs_v1.py — verificación stdlib puro           │
│                                                                 │
│  SIFT BRIDGE: vigia_sift_bridge.py (22+ tools MCP)             │
└────────────────────────┬────────────────────────────────────────┘
                         │  ForensicBundle sellado
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              PEIRCE PLANNER (Narrativa — LLM externo)           │
│  Claude Code / Ollama — SOLO traduce el bundle a narrativa      │
│  NO participa en la decisión matemática                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Principio de Aislamiento de Capas (Zero-Trust)

Cada capa tiene una dirección de dependencia estrictamente definida. Ninguna capa puede importar desde una capa superior. El diagrama de dependencias es un DAG acíclico. Esto garantiza que un componente comprometido no puede contaminar el proceso de atestación.

La regla de oro: **el LLM queda fuera del loop de decisión matemática**. Esta invariante no es negociable. Fue propuesta por el colectivo de auditoría y aceptada como requisito Daubert fundamental.

### 4.3 ForensicBundle como Unidad de Entrega

El `ForensicBundle` es el artefacto sellado que VIGÍA entrega a SIFT. Contiene:

- `evidence_graph`: grafo probabilístico de dependencias entre artefactos
- `decision_trace`: posterior / risk / decision con trazabilidad completa
- `policy_spec`: política activa verificable externamente
- `actions`: historial de intervenciones ejecutadas
- `system_state`: parámetros adaptativos en el momento del sellado
- `abduction_trace`: trazabilidad del razonamiento Peirciano
- `integrity`: hashes SHA-256 encadenados (sellado criptográfico externo)

El bundle es portable, autocontenido y auditable sin acceso al runtime.

---

## 5. Capas del Pipeline EBS v1

### 5.1 Capa 0 — Contratos de Datos (`ebs_v1.py`)

Contiene todas las estructuras de datos del sistema. Es la única capa que no importa nada de capas superiores. Implementado como dataclasses puro con fallback a Pydantic v2 si disponible.

Contratos implementados:
- `SignalOutput`: output canónico de toda herramienta forense
- `EvidenceEdge`: arista del grafo con estabilidad bootstrap (π ≥ 0.85)
- `EvidenceGraph`: grafo de dependencias emergente
- `DecisionTrace`: tríada posterior/risk/decision con veredicto
- `PolicyRule` / `PolicySpec`: política de gobernanza verificable
- `ActionRecord`: acción ejecutada con trazabilidad
- `SystemState`: parámetros adaptativos (λ, γ, ε)
- `IntegrityBlock`: hashes SHA-256 encadenados
- `AbductionTrace`: trazabilidad del razonamiento Peirciano
- `ForensicBundle`: artefacto sellado EBS v1

**Invariante crítica:** `ForensicBundle` no tiene método `seal()`. El sellado es responsabilidad exclusiva de `BundleBuilder` (proceso externo). Un motor comprometido no puede sellar su propia mentira.

### 5.2 Capa 2 — Motor de Inferencia

**`likelihood_engine.py`** — Kernel de densidad (KDE) con estimación de covarianza Ledoit-Wolf. Produce el posterior probabilístico sobre las señales normalizadas. Implementa:
- KDE multivariada con bandwidth automático
- Shrinkage de covarianza (Ledoit-Wolf) para datasets pequeños
- `_round_floats()` aplicado antes de todo hashing para determinismo cross-OS
- Aritmética con `decimal.Decimal` en paths críticos

**`graph_stability.py`** — Stability Selection vía Bootstrap (B=500). El grafo de evidencia emerge del dato, no está hardcodeado. Una arista (i,j) existe si y solo si π_ij = freq(arista en bootstrap) ≥ τ = 0.85.

Criterios de dependencia:
- Spearman ρ ≥ threshold_rho (robusto ante no-normalidad)
- Mutual Information ≥ threshold_mi (captura no-linealidad)
- Una arista requiere AMBOS criterios

Esto es estadísticamente defendible ante Daubert: "Esta dependencia aparece en X% de los mundos estadísticos posibles del dataset de calibración."

### 5.3 Capa 3 — Gobernanza y Riesgo

**`risk_bounded_layer.py`** — Función de riesgo:

```
r = (1 - P) · (1 + λ·D) · (1 + γ·(1 - S))
```

Donde:
- `P`: posterior probabilístico (LikelihoodEngine)
- `D`: drift score (divergencia del baseline)
- `S`: estabilidad del grafo de evidencia
- `λ`, `γ`: parámetros adaptativos (SelfAdaptiveRiskPolicy)

Implementa tres componentes:
- `RiskBoundedDecisionLayer`: veredicto final con threshold
- `SelfAdaptiveRiskPolicy`: ajuste dinámico de λ y γ según historial
- `PolicyStabilityController`: evita oscilaciones en la política

Los umbrales se leen desde `PolicySpec` via `from_policy_spec()`. **No existen hardcodes**.

### 5.4 Capa 4 — Auditoría y Acción

**`audit_action.py`** — Cuatro componentes:
- `EvidenceGraphDiff`: detecta divergencias entre ejecuciones
- `InterventionOptimizer`: recomienda intervenciones mínimas
- `FormalPolicyEngine`: evalúa acciones contra política
- `SafeActionExecutor`: ejecuta con registro completo

### 5.5 Capa 5 — Verificación Independiente

**`verify_ebs_v1.py`** — Verificador independiente del bundle. **Usa únicamente stdlib Python** (confirmado por inspección AST). No importa nada del runtime de producción. Esta separación es deliberada: el verificador puede validar cualquier bundle sin acceso al sistema que lo produjo.

El `BundleBuilder` no es importado por `verify_ebs_v1.py`. Implementan el mismo protocolo de hashing en forma independiente. Si difieren, el protocolo es el fallo, no los módulos.

---

## 6. Motor de Abducción y Hipótesis

### 6.1 Hipótesis Implementadas

El `AbductiveIntentEngine` implementa 33 hipótesis abductivas sobre 13 fases IR del ciclo de vida del incidente:

**RECONNAISSANCE (H_RE_001 a H_RE_003):**
- `H_RE_001`: passive_osint_gathering
- `H_RE_002`: active_scanning_pattern
- `H_RE_003`: social_engineering_recon

**RESOURCE_DEVELOPMENT:**
- `H_RD_001`: infrastructure_acquisition

**INITIAL_ACCESS (H_IA_001 a H_IA_003):**
- `H_IA_001`: phishing_document
- `H_IA_002`: credential_stuffing
- `H_IA_003`: supply_chain_compromise

**EXECUTION (H_EX_001 a H_EX_003):**
- `H_EX_001`: command_line_abuse
- `H_EX_002`: scheduled_task_abuse
- `H_EX_003`: powershell_living_off_the_land

**PERSISTENCE (H_PE_001 a H_PE_003):**
- `H_PE_001`: single_persistence
- `H_PE_002`: multi_mechanism_persistence
- `H_PE_003`: bootkit_persistence

**PRIVILEGE_ESCALATION (H_PA_001 a H_PA_002):**
- `H_PA_001`: token_manipulation
- `H_PA_002`: kernel_exploit

**DEFENSE_EVASION (H_DE_001 a H_DE_003 + H_SE_001):**
- `H_DE_001`: log_fabrication
- `H_DE_002`: timestamp_manipulation
- `H_DE_003`: anti_forensics_tools
- `H_SE_001`: **false_security_theater** (Paradoja de Jevons aplicada a seguridad)

**CREDENTIAL_ACCESS:**
- `H_CA_001`: credential_dumping
- `H_CA_002`: keylogging

**LATERAL_MOVEMENT:**
- `H_LM_001`: pass_the_hash

**COLLECTION (H_CO_001 a H_CO_003):**
- `H_CO_001`: data_staging_for_exfil
- `H_CO_002`: clipboard_and_screen_capture
- `H_CO_003`: audio_and_video_surveillance

**COMMAND_AND_CONTROL (H_C2_001 a H_C2_002):**
- `H_C2_001`: domain_fronting_beacon
- `H_C2_002`: dns_tunnel_c2

**EXFILTRATION (H_EX_001 a H_EX_002, espacio EXFIL):**
- `H_XF_001`: slow_exfil_pattern
- `H_XF_002`: cloud_exfil

**IMPACT:**
- `H_IM_001`: ransomware_pattern
- `H_IM_002`: wiper_pattern
- `H_IM_003`: false_flag_operation

### 6.2 Falsabilidad Explícita

Cada hipótesis tiene condiciones de falsabilidad documentadas. Esto es un requisito Daubert: una hipótesis forense que no puede ser refutada no es científicamente válida. El `OckhamAdversarialEngine` evalúa hipótesis alternativas para cada veredicto.

### 6.3 Cinco Clusters de Intención Semántica

El `MITREClusterer` mapea hipótesis a cinco clusters de intención:

| ID | Nombre | Rationale del Atacante |
|----|--------|------------------------|
| IC_01 | STEALTH | Operar sin detección |
| IC_02 | PERSISTENCE | Mantener acceso |
| IC_03 | EXFILTRATION | Extraer valor |
| IC_04 | DISRUPTION | Destruir o interrumpir |
| IC_05 | ESCALATION | Ampliar capacidad |

---

## 7. Integración MITRE ATT&CK

### 7.1 Master TTP Dictionary

El `mitre_mapping.py` implementa el diccionario maestro centralizado de TTPs. Todas las TTPs incluyen:
- `technique_id`: ID MITRE ATT&CK Enterprise v14.1
- `base_severity`: severidad intrínseca [0.0, 1.0]
- `spoofability_score`: facilidad de falsificación (0.0 = casi imposible, 1.0 = trivial)
- `evidence_types`: tipos de evidencia VIGÍA que mapean a esta TTP

La `spoofability_score` es un aporte original de VIGÍA al framework MITRE: evidencia de memoria (T1055 — Process Injection) tiene `spoofability=0.10` porque requiere acceso real al kernel. Evidencia de logs de red (`T1071`) tiene `spoofability=0.80` porque los logs son trivialmente falsificables.

**Esto permite que el perito pondere la credibilidad de la evidencia según su capacidad de falsificación**, no solo su tipo.

### 7.2 TTPs de Alta Relevancia Forense

Técnicas con spoofability bajo — evidencia forense más confiable:

| TTP ID | Nombre | Spoofability |
|--------|--------|-------------|
| T1055 | Process Injection (memoria) | 0.10 |
| T1547 | Boot/Logon Autostart (registro) | 0.20 |
| T1078 | Valid Accounts (autenticación) | 0.25 |
| TPM_attestation | Hardware Trust Anchor | 0.05 |

Técnicas con alta spoofability — requieren corroboración cruzada:

| TTP ID | Nombre | Spoofability |
|--------|--------|-------------|
| T1071 | Application Layer Protocol (logs de red) | 0.80 |
| T1566 | Phishing (email headers) | 0.75 |
| T1003 | OS Credential Dumping (logs de eventos) | 0.60 |

### 7.3 Exportación STIX 2.1

`mitre_mapping.py` incluye `to_stix_sdo()` que convierte artefactos VIGÍA a STIX SDOs válidos. Esto permite interoperabilidad directa con OpenCTI, MISP, y otras plataformas DFIR que consumen STIX 2.1.

### 7.4 Cobertura de Mapeo

El `MITREClustering Hito 2.2` verifica cobertura completa:
- `coverage_ratio`: fracción de hipótesis con técnica MITRE asignada
- `tables_frozen`: flag que garantiza inmutabilidad de las tablas en producción
- Todas las 33 hipótesis tienen al menos una técnica MITRE mapeada

---

## 8. Protocolos P1 y P2

### 8.1 Protocolo P1 (Congelado)

P1 responde: "¿El kernel de entropía produce los mismos resultados en todas partes?"

Propiedades:
- Entropía de Shannon determinista sobre cualquier backend
- `entropy_uniform = 0.0` (caso trivial verificado)
- `entropy_distinct = 1.0` (máxima entropía verificada)
- `entropy_shannon_seed42 = 7.782633` (valor de referencia fijo)
- Pair encoding collision-free: `token = (uint64(a) << 32) | uint64(b)`

P1 está congelado e inmutable. Cualquier cambio invalida la compatibilidad.

### 8.2 Protocolo P2 (Draft v2.8 — target freeze: 15 de junio 2026)

P2 responde: "¿El sistema es matemáticamente consistente, adversarialmente robusto y epistemológicamente honesto?"

Módulos nuevos respecto a P1:
- **Markov Order-k**: H_k = -Σ P(w) · Σ P(s|w) · log₂(P(s|w)), sin smoothing (MLE puro)
- **Lempel-Ziv LZ76**: complejidad de compresibilidad, O(n²) naive / O(n) suffix-tree
- **Permutation Entropy**: PE = -Σ p(π) · log₂(p(π)) / log₂(d!), tie-breaking por stable sort
- **Abstention Policy**: zona honesta [0.15, 0.85] con `Decimal.quantize()` HALF_EVEN
- **Chain of Custody**: bloque de discretización obligatorio para inputs no discretos

22 vectores canónicos con SHA-256: `f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`

### 8.3 Niveles de Cumplimiento P2

| Nivel | Descripción | Claim permitido |
|-------|-------------|----------------|
| Strict | Python puro, `Decimal.quantize()` HALF_EVEN, secuencial | "VIGÍA-compatible P2 (strict)" |
| Reference | NumPy/CuPy permitido, float64 acumulador, paralelo OK | "VIGÍA-compatible P2" |
| Accelerated | Cualquier backend, float32 permitido, subset P2 | "VIGÍA-accelerated" — NO puede reclamar P2 completo |

### 8.4 Garantías y No-Garantías P2

P2 **garantiza**:
- Equivalencia cuantizada determinista entre backends
- Entropía contextual (memoria Markov)
- Semántica de complejidad (compresibilidad LZ)
- Invarianza ordinal (PE bajo transformaciones monótonas)
- Rechazo adversarial (denormales, NaN, Inf, overflow)
- Honestidad en la abstención

P2 **NO garantiza**:
- Precisión absoluta (reproducibilidad ≠ verdad)
- Clasificación conductual (humano vs. bot, real vs. sintético)
- Atribución de autoría o inferencia de intención
- Certificación de admisibilidad legal
- Corrección de la discretización upstream

### 8.5 Gaps Adversariales Documentados (P2 §14)

10 gaps identificados y documentados honestamente:

| ID | Nombre | Descripción |
|----|--------|-------------|
| GAP-01 | entropy_inflation_attack | Ruido uniforme de baja tasa satura métricas |
| GAP-02 | symbolic_explosion_attack | Perturbaciones sub-ULP inflan la entropía Shannon |
| GAP-03 | calibration_drift | Degradación de umbrales con drift de distribución |
| GAP-04 | backend_divergence_under_stress | Reducciones paralelas bajo alta carga |
| GAP-05 | heterogeneous_hardware | GPU cross-vendor no validado empíricamente |
| GAP-06 | false_structure_induction | Inputs patológicos con baja LZ sin estructura real |
| GAP-07 | dataset_leakage_in_calibration | Overlap corpus calibración/deployment |
| GAP-08 | upstream_discretization_attack | Atacante controla la discretización upstream |
| GAP-09 | tie_break_exploitation | PE stable-sort explotable adversarialmente |
| GAP-10 | lz_period_aliasing | LZ76 asintótica — imprecisa para secuencias cortas |

---

## 9. Subsistema de Seguridad

### 9.1 LLMShield — Firewall de Prompt Injection

`security.py` implementa `LLMShield` con tres pasadas:
1. Texto normalizado NFKC — detecta sustitución de homoglifos Unicode
2. Texto decodificado leet — detecta ofuscación 1337
3. Texto original — captura patrones que sobreviven la normalización

25+ patrones cubriendo: instruction override, familias DAN/jailbreak (contextual — no genera falsos positivos con el nombre "Dan"), extracción de system prompt, confusión de roles, delimitadores token-stuffing.

### 9.2 Protocolo Kassandra — Tripwire Semántico

El `KassandraProtocol` implementa un tripwire criptográfico derivado deterministicamente de HMAC(KASSANDRA_SALT, session_nonce + counter):

```
session_nonce → fijado en la PRIMERA evidencia procesada
tripwire → HMAC determinista por sesión
evidencia legítima → wrapeada con <<<EVIDENCE_DATA_{nonce}>>>
inyección → nonce no coincide → KASSANDRA_TRIPWIRE_TRIGGERED
```

Esto garantiza que un proceso sustituto (BYOI) no puede reproducir la cadena sin conocer el estado interno exacto.

### 9.3 HMAC Chain — Integridad de Logs

Cada entrada del audit log contiene:
- `_prev_hmac`: HMAC de la entrada anterior ("GENESIS" para la primera)
- `_hmac`: HMAC-SHA256 del contenido de la entrada + `_prev_hmac`

Tampering con cualquier línea invalida todas las entradas subsiguientes. Verificación vía `audit_logger.verify_chain()`. Resolución de clave:
1. `VIGIA_HMAC_KEY` (variable de entorno, hex-encoded, ≥ 32 bytes)
2. `VIGIA_HMAC_KEY_FILE` (path a archivo con key bytes)
3. Clave efímera autogenerada (solo desarrollo — registra WARNING)

### 9.4 Sandbox de Subprocesos

`sandbox.py` implementa:
- Límites de memoria vía `setrlimit(RLIMIT_AS)`
- Límites de CPU vía `setrlimit(RLIMIT_CPU)`
- Truncación de output (10 MB stdout, 256 KB stderr)
- Timeout asyncio duro con kill de proceso
- Privilege drop: `_drop_privs_if_requested()` aborta con `os._exit(126)` si `setuid()` falla — nunca continúa como root

**Nota de seguridad crítica:** `subprocess` directo fue removido del bridge principal en el fix P2-11. Todas las llamadas migradas a `sandboxed_execute()`.

### 9.5 Mitigaciones TOCTOU

Implementadas en `vigia_sift_bridge.py` con comentario explícito en el código:

1. Archivos temporales creados con `tempfile.mkstemp()` — nombre único e impredecible
2. Verificación post-escritura: `os.lstat()` (no sigue symlinks) confirma que el temporal no fue convertido en symlink entre escritura y rename
3. Si se detecta symlink: `_IntegrityViolation` inmediata, operación abortada

### 9.6 Sanitización de Paths

`_sanitize_path()` en `security.py`:
- Bloqueo de null bytes
- Resolución de tildes
- Blocked prefixes configurables
- Confinamiento a `base_dir`
- `must_exist` opcional
- Validación de symlinks

### 9.7 Seguridad de Transporte MCP

`_verify_transport_security()` al arranque:
1. Session token (128-bit random) a stderr para verificación del operador
2. Verificación de stdin como pipe (transporte stdio esperado)
3. Detección de HTTP/SSE: sin `VIGIA_MCP_AUTH_TOKEN` → CRITICAL alert
4. Con `VIGIA_ENFORCE_STDIO=true`: abort en startup si transporte inseguro

VIGÍA expone 22+ herramientas forenses incluyendo operaciones de nivel root. HTTP sin autenticación es una superficie de ataque inaceptable.

### 9.8 Integridad del Modelo CLIP

Para la herramienta de visión forense:
- Verificación SHA-256 del modelo antes de cargar
- Hash sources: `VIGIA_CLIP_HASH_FILE` (JSON), env vars por modelo, hardcoded
- Modo estricto (`VIGIA_STRICT_MODEL_CHECK=true`): rechaza cargar modelos sin hash configurado
- Previene supply-chain attacks donde un modelo envenenado clasifica documentos falsos como legítimos

---

## 10. Motor de Calibración y Likelihood Ratio

### 10.1 LikelihoodRatio y Escala ENFSI

VIGÍA usa la escala de probabilidad forense estándar ENFSI (European Network of Forensic Science Institutes):

| LR | Escala ENFSI | Etiqueta |
|----|-------------|---------|
| 1–10 | Limitado | NOISE |
| 10–100 | Moderado | SUSPICION |
| 100–1000 | Moderado-Fuerte | SUSPICION_STRONG |
| 1000–10000 | Fuerte | MALICE |
| >10000 | Muy Fuerte | MALICE_STRONG |

Este es el estándar adoptado por los sistemas forenses judiciales europeos. Usar una escala no estándar podría comprometer la admisibilidad Daubert.

### 10.2 Calibración Isotónica

`lr_calibration.py` implementa calibración isotónica con:
- Regresión logística sklearn (`backend: sklearn_logistic`)
- Corpus de calibración: 105 casos (hash del corpus: `025aacafd60...`)
- Split: 80% train / 20% test, `seed=42`
- Métricas de test: `brier_score=0.0813`, `tpr_at_0.5=1.0`, `fpr_at_0.5=1.0`

**Nota de honestidad:** El corpus de calibración es actualmente sintético (bootstrap v1). Los umbrales P2 (0.15/0.85) son heurísticos pendientes de validación empírica. `calibration_metadata.json` documenta esto explícitamente.

### 10.3 KDE + Ledoit-Wolf

`likelihood_engine.py` usa KDE multivariada con estimación de covarianza Ledoit-Wolf para datasets pequeños. El shrinkage covariance evita matrices singulares con pocas muestras — problema habitual en datasets forenses donde el número de variables puede superar el número de casos.

### 10.4 `_round_floats()` — Determinismo Cross-OS

Aplicado antes de todo hashing. Problema: JSON no distingue int de float (1 vs 1.0 → strings distintos). Si el `InterventionOptimizer` produce un score como int y otro módulo lo lee como float, el `bundle_hash` cambia sin que el contenido haya cambiado — rompe la Invariante I2 del EBS v1.

La canonicalización recorre recursivamente el objeto y convierte todo float a int si `float == int(float)`, o redondea a 6 decimales si no.

---

## 11. Herramientas Forenses MCP

El SIFT Bridge registra las siguientes herramientas como endpoints MCP:

### 11.1 Herramientas de Cadena de Custodia (9 tools)

| Tool | Función |
|------|---------|
| `mount_sift_evidence` | Montaje forense con magic-byte validation, flags `noexec,nosuid,nodev,ro` |
| `generate_forensic_hash` | SHA-256 chain of custody |
| `read_evidence` | Lectura single-pass con hash inline |
| `list_files` | Perímetro del sistema de archivos |
| `search_pattern` | Búsqueda Python pura (sin grep directo) |
| `list_processes` | Detección de persistencia en memoria |
| `audit_network` | Mapeo de canales de exfiltración |
| `calculate_shannon_entropy` | Detección de payload/cifrado |
| `detect_eco_overinterpretation` | Perfección digital excesiva |

### 11.2 Herramientas de Análisis de Intencionalidad

| Tool | Función |
|------|---------|
| `calculate_human_entropy` | Entropía local en bloques — distingue texto humano de generado |
| `detect_human_jitter` | Análisis de jitter temporal — hábitos humanos vs. automatización |
| `analyze_stylometry` | Estilometría multi-vector (tasa de tipo/token, vocabulario, frecuencia) |
| `infer_intent` | Motor abductivo principal — produce AbductionTrace completo |
| `audit_grice_maxims` | Detección de violaciones de las 4 máximas conversacionales de Grice |
| `detect_habit_incongruence` | Incoherencia memoria vs. logs (Volatility: LSASS) |
| `cross_artifact_analysis` | CAIE — Cross-Artifact Incongruence Engine |
| `trust_fusion_analysis` | Fusión Bayesiana: Temporal → Provenance → Effective Trust |
| `investigate_autonomous` | Loop autónomo: plan → execute → evaluate → repeat |

### 11.3 Herramientas de Integridad Documental

| Tool | Función |
|------|---------|
| `audit_document_integrity` | PDF/DOCX: fonts, producer, coherencia género/rol |
| `analyze_image_layers` | ELA (Error Level Analysis) para detección de paste-in |
| `detect_document_geometry` | Márgenes, alineación, consistencia de folio |
| `ocr_semantic_validator` | OCR + validación semántica de campos obligatorios |
| `vision_intent_audit` | CLIP zero-shot: intencionalidad visual en imágenes |

### 11.4 CAIE — Cross-Artifact Incongruence Engine

El CAIE (`caie.py`) implementa 8 reglas de fractura forense:

1. **MEMORY_VS_DISK**: proceso en memoria sin ejecutable en disco
2. **LOG_VS_MEMORY**: log registra evento que memoria contradice
3. **TEMPORAL_PARADOX**: efecto antes de causa
4. **CULTURAL_MARKER_MISMATCH**: marcadores lingüísticos inconsistentes con el origen declarado
5. **PERFECTION_ANOMALY**: artefacto estadísticamente demasiado perfecto
6. **SILENCE_PATTERN**: ausencia de evidencia esperada
7. **DOCUMENT_FORGERY**: incoherencia multi-capa en documento
8. **MULTI_TENANT_ISOLATION_BREACH**: violación de aislamiento en entornos cloud

### 11.5 TrustFusion

`trust_fusion.py` cierra el ciclo Temporal → Provenance → Correlation:

```
effective_trust = provenance_trust × exp(-2 × max_weighted_severity)
```

Donde `max_weighted_severity` integra las violaciones temporales ponderadas por spoofability.

---

## 12. Integración Claude Code y Ollama

### 12.1 Claude Code (MCP)

Configuración en `~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-sift/vigia/vigia_sift_bridge.py"]
    }
  }
}
```

Claude Code llama a las herramientas VIGÍA vía protocolo MCP sobre stdio. El transporte stdio hereda el aislamiento de proceso del OS — solo el proceso padre (Claude Code) puede leer/escribir el stdin/stdout del servidor.

### 12.2 Ollama (Backend LLM para Narrativa)

`llm_backend.py` / `llm_backend_v2.py` implementan backend pluggable:
- Anthropic API (`claude-*`) para razonamiento de alta calidad
- Ollama (local) para operación offline en SIFT field deployments
- Fallback automático con logging

La selección del backend se configura vía `VIGIA_LLM_BACKEND` env var. El ForensicBundle ya está sellado antes de llamar al LLM. El LLM solo recibe el bundle como contexto para producir la narrativa — no puede modificar la decisión.

### 12.3 vigia_ask.sh — CLI Forense

Script de conveniencia para interrogar el sistema vía Ollama desde línea de comandos. Útil para SIFT field deployments donde no hay acceso a Claude Code.

### 12.4 FastAPI Wrapper (`vigia_api.py`)

Wrapper REST para integración con OpenWebUI. Expone:
- `POST /analyze`: recibe caso JSON, ejecuta pipeline completo, retorna veredicto + bundle_hash
- `POST /narrative`: genera narrativa vía `vigia_ask.sh` (Ollama)

---

## 13. Cumplimiento Daubert

### 13.1 Los Cuatro Criterios Daubert

La decisión *Daubert v. Merrell Dow Pharmaceuticals* (1993) estableció cuatro criterios para la admisibilidad de evidencia científica en tribunales federales de EE.UU.:

1. **Testabilidad**: ¿puede la metodología ser —y ha sido— probada?
2. **Peer review**: ¿ha sido sometida a revisión por pares?
3. **Tasa de error conocida**: ¿existe tasa de error conocida y estándares de control?
4. **Aceptación general**: ¿es generalmente aceptada en la comunidad científica relevante?

### 13.2 Implementación en VIGÍA

| Criterio | Implementación VIGÍA |
|---------|---------------------|
| Testabilidad | 22 vectores canónicos P2, verificador stdlib puro, `verify_ebs_v1.py` independiente |
| Peer review | Colectivo de 7 IAs con roles definidos, auditorías vinculantes documentadas |
| Tasa de error | `calibration_metadata.json`: brier_score, AUC, FPR/TPR documentados |
| Aceptación | MITRE ATT&CK v14.1, ENFSI scale, STIX 2.1, ISO 27037 |

### 13.3 Invariantes EBS v1 (No Negociables)

- **I1 — Determinismo**: mismo input analítico → mismo `analysis_fingerprint`; cada sello de custodia conserva su UUID/timestamps y por eso su `bundle_hash` propio
- **I2 — Integridad encadenada**: `bundle_hash` cubre TODO el contenido
- **I3 — Política verificable**: `policy_spec` es independiente del runtime
- **I4 — Acciones explícitas**: no existen efectos implícitos
- **I5 — Decisión explicable**: risk y posterior SIEMPRE presentes

### 13.4 Chain of Custody Completa

Todo el pipeline mantiene cadena de custodia:
- Hash SHA-256 del artefacto de entrada
- Hash de cada etapa de procesamiento
- Timestamp de cada operación (UTC, ISO 8601)
- `sealed_at` en el IntegrityBlock
- Log HMAC de toda la sesión

### 13.5 Amicus Curiae Narrative

El `AmicusCuriaeNarrative` genera narrativas que distinguen explícitamente entre:
- Hallazgos confirmados (con evidencia técnica directa)
- Hallazgos inferidos (abducción con condiciones de falsabilidad)
- Incertidumbres documentadas (zonas de abstención)

---

## 14. Corpus de Casos y Dataset

### 14.1 Estado Actual

El sistema trabaja con tres tipos de casos:

**Casos sintéticos VIGÍA Internal Corpus:**
- 186 casos en formato JSON (no incluidos en este análisis por volumen)
- Generados por `convert_synthetic_cases.py` y `convert_md_cases.py`
- Cubren los 5 clusters de intención y las 33 hipótesis

**Casos de breakage (BREAK_001 a BREAK_009):**
- 9 casos de estrés diseñados para explorar límites del sistema
- Documentados en `known_limitations.md`

**Casos de calibración:**
- 105 casos con split 80/20 (84 train, 21 test)
- `n_authentic: 16`, `n_fabricated: 89`

### 14.2 Limitaciones del Corpus Actual

El corpus de calibración es actualmente sintético (bootstrap v1). Esto afecta:
- Los umbrales de LR (pendientes de validación empírica)
- La confiabilidad de los `brier_score` y métricas AUC en producción real
- La calibración de la `spoofability_score` por tipo de evidencia

La calibración con corpus forense real (`fit_calibration.py` + dataset SIFT real) es una tarea pendiente crítica antes del 15 de junio.

### 14.3 Patrones NLP Calibrados

`vigia_patterns_migration.sql` documenta los patrones NLP calibrados del corpus v1:

**Patrones Carnegie:**
- `CARNEGIE_FLATTERY_APPEAL`: adulación como vector de acceso
- `CARNEGIE_NORMALIZATION_PRESSURE`: presión social para anular dudas
- `CARNEGIE_ARTIFICIAL_URGENCY`: urgencia falsa para evadir verificación
- `CARNEGIE_BORROWED_CREDIBILITY`: citar autoridad inverosímil

**Patrones Grice:**
- `GRICE_QUANTITY_FLOOD`: saturación con información irrelevante
- `GRICE_QUANTITY_STARVATION`: omisión de información crítica
- `GRICE_QUALITY_UNVERIFIABLE`: afirmación sin evidencia
- `GRICE_QUALITY_FALSE_NORMALITY`: normalización de lo anormal

---

## 15. Módulos Implementados — Inventario Completo

El proyecto cuenta con 151 módulos Python. Clasificación por función:

### 15.1 Core Pipeline (14 módulos)
`ebs.py`, `ebs_v1.py`, `pipeline.py`, `run_pipeline.py`, `run_vigia_full.py`, `bundle_builder.py`, `verify_ebs_v1.py`, `signal_contract.py`, `signal_mapper.py`, `signal_adapter.py`, `signal_quality_gate.py`, `vigia_integration_bridge.py`, `vigia_case_adapter.py`, `vigia_scorer.py`

### 15.2 Motores de Inferencia (8 módulos)
`likelihood_engine.py`, `likelihood_ratio.py`, `lr_calibration.py`, `graph_stability.py`, `risk_bounded_layer.py`, `risk_bounded_layer_v2.py`, `abductive_reasoner.py`, `abductive_reasoner_v2.py`

### 15.3 Análisis Forense (18 módulos)
`abductive_intent_engine.py`, `visible_variables.py`, `semiotic_detector.py`, `semiotic_detector_v2.py`, `forensic_technical_detector.py`, `vigia_core_forensic_technical_detector.py`, `vigia_core_semiotic_detector.py`, `pattern_detector.py`, `entropy_locality.py`, `behavioral_fingerprint.py`, `temporal_forensics.py`, `temporal_forensics_redteam.py`, `temporal_drift.py`, `cross_artifact_resonance.py`, `coherence_validator.py`, `causal_closure.py`, `trust_fusion.py`, `trust_levels.py`

### 15.4 Herramientas SIFT (12 módulos)
`sift_orchestrator.py`, `mft_timeline_analyzer.py`, `registry_timeline_reconstructor.py`, `prefetch_analyzer.py`, `memory_forensics.py`, `shellbag_analyzer.py`, `usb_device_tracker.py`, `browser_forensics.py`, `event_log_correlator.py`, `disk_forensics.py`, `amcache_shimcache.py`, `network_forensics.py`

### 15.5 Bridge y API (3 módulos)
`vigia_sift_bridge.py`, `vigia_api.py`, `cli.py`

(`vigia_sift_bridge_final.py`, `BRIDGE_PATCH_FINAL.py`, `vigia_server.py` y
`vigia_namespace_shim.py` no existen en el repositorio — confirmado por
búsqueda exhaustiva 2026-07-26; removidos de este inventario, que hasta
entonces los listaba como si existieran.)

### 15.6 Seguridad (6 módulos)
`security.py`, `sandbox.py`, `shadow_mode.py`, `path_guard.py`, `config_sentinel.py`, `normalization_layer.py`

### 15.7 MITRE ATT&CK (4 módulos)
`mitre_mapping.py`, `mitre_clustering.py`, `picerl_mapping.py`, `sans_phase.py`

### 15.8 Reportes y Documentación (8 módulos)
`forensic_reporter.py`, `report_builder.py`, `report_exporter.py`, `report_exporter_v2.py`, `narrative_auditor.py`, `dissent_report.py`, `generate_report.py`, `generate_execution_log.py`

### 15.9 Calibración y Métricas (9 módulos)
`fit_calibration.py`, `run_calibration.py`, `generate_calibration.py`, `build_calibration_dataset.py`, `calibration_metadata.json`, `lr_calibration.py`, `check_determinism.py`, `compare_runs.py`, `evaluate_detector.py`

### 15.10 Módulos de Auditoría y Gobernanza (10 módulos)
`audit_action.py`, `decision_layer.py`, `evidence_aggregator.py`, `evidence_bundle.py`, `explainable_governance.py`, `execution_logger.py`, `chain_of_custody.py`, `hypothesis_lineage.py`, `negation_handler.py`, `adversarial_silence.py`

### 15.11 Módulos Especializados (15 módulos)
`caie.py`, `quadripartite.py`, `geopolitical.py`, `geopolitical_v2.py`, `eml_symbolic.py`, `eml_gci.py`, `metabolic_profiler.py`, `resource_optimizer.py`, `document_integrity.py`, `vision_audit.py`, `vision_audit_final.py`, `pdf_dual_parser.py`, `rfc3161_chain.py`, `pki_tools.py`, `ioc_manager.py`

### 15.12 Módulos P2 y Semántica Avanzada (8 módulos)
`adversarial_robustness.py`, `adversarial_nlp.py`, `vigia_adversarial_nlp.py`, `ockham_adversarial.py`, `entanglement.py`, `vigia_entanglement.py`, `graph_stability.py`, `_math_utils.py`

### 15.13 Scripts y Utilidades (12 módulos)
`run_demo.py`, `run_case.py`, `convert_md_cases.py`, `convert_synthetic_cases.py`, `convert_break_cases.py`, `consolidate_cases.py`, `export_patterns.py`, `init_patterns_db.py`, `fix_security_init.py`, `fix_inits.py`, `top_breaking_phrases.py`, `negation_stress_test.py`

---

## 16. Limitaciones Conocidas y Gaps Adversariales

### 16.1 Limitaciones Documentadas (`known_limitations.md`)

| ID | Caso | Veredicto VIGÍA | Esperado | Tipo |
|----|------|-----------------|----------|------|
| L-001 | BREAK_006 (living-off-the-land avanzado) | SUSPICION | MALICE | Limitación real |
| L-002 | BREAK_004 (staged persistent access) | SUSPICION | MALICE | Limitación real |
| L-003 | BREAK_007 (fog of war + false flag) | SUSPICION | MALICE | Limitación real |
| L-004 | BREAK_009 (texto libre engañoso) | UNKNOWN | MALICE | Limitación real |
| L-005 | BREAK_002/005 (pentest autorizado) | UNKNOWN/SUSPICION | NOISE/UNKNOWN | Discutible |
| L-006 | BREAK_001 (inconsistencia temporal única) | MALICE | UNKNOWN | Decisión de diseño |

**L-004** es la limitación más crítica: el LLMShield filtra inyecciones directas pero no neutraliza narrativas engañosas embebidas en artefactos de texto libre. Todo artefacto de texto libre debe tratarse con trust reducido.

**L-006** es una decisión de diseño deliberada: en forense, es preferible investigar un caso que resultó benigno que ignorar uno malicioso. El hard gate `EFFECT_BEFORE_CAUSE` y la penalización por inconsistencia temporal son agresivos por diseño.

### 16.2 Problema de Sincronización Git (Crisis Activa)

El repositorio Git contiene significativamente menos archivos que el directorio de trabajo local ("paraKimi"). Existen sufijos de versión proliferados: `_v2`, `_v3`, `_P0`, `_UPDATED`, `_GIT`, `_WIRED_P0`. Algunos archivos del repo contienen código endurecido de seguridad de sesiones auditadas; algunos archivos locales pueden ser más recientes pero potencialmente con vulnerabilidades.

**Resolución requerida:** comparación archivo por archivo por fecha de modificación y contenido. Un overwrite simple en cualquier dirección no es seguro.

### 16.3 Calibración Pendiente

Los umbrales operacionales del sistema (LR thresholds, P2 abstention zone, spoofability weights) están basados en corpus sintético bootstrap. La calibración con datos reales es la tarea de mayor impacto sobre la calidad del sistema antes del deadline.

---

## 17. Estado del Repositorio Git

**Repositorio:** `github.com/annatchijova/vigia-intent-analysis` (privado)  
**Release público planificado:** 7–10 de junio de 2026  
**Estado:** push inicial realizado, workflow SSH/git establecido

**Pendiente:**
- Resolver el caos de versiones (sufijos proliferados)
- Establecer rama `main` limpia con código auditado
- Verificar que `verify_ebs_v1.py` usa solo stdlib (confirmado por AST, mantener)
- Tests de integración: 55/55 pasan en el estado actual
- CI/CD: `ci_gate.py` implementado, requiere configuración en GitHub Actions

---

## 18. Trabajo Pendiente hasta el 15 de Junio

### 18.1 Crítico (bloquea el release)

1. **Sincronización Git**: resolver el quilombo de versiones antes de cualquier desarrollo adicional
2. **Calibración con corpus real**: `fit_calibration.py` sobre datos forenses reales
3. **Freeze P2**: congelar los 22 vectores canónicos antes del 15 de junio (deadline coincide con target freeze)
4. **README final**: técnico, English-only, para audiencia SANS
5. **Release bundle**: `generate_release_bundle.py` para el release público

### 18.2 Alta Prioridad

6. **Conversión de 50 casos adicionales**: de formato MD a JSON usando `convert_md_cases.py`
7. **Actualización RFC documentation**: docs técnicos de los protocolos P1/P2
8. **Integration tests completos**: verificar 55/55 en el estado post-sync
9. **Docker image**: `docker-compose.yml` existe, validar build completo

### 18.3 Media Prioridad

10. **VIGIA_STORY.md**: Anna lo escribe, Claude puede asistir solo con edición
11. **Configuración GitHub Actions**: `ci_gate.py` → workflows YAML
12. **Documentación DAUBERT_JUDICIAL.md**: completar sección de casos de prueba

### 18.4 Tareas de Cierre

13. **Audit final del colectivo** antes del release público
14. **Verificación de no filtración de datos sensibles** en el repositorio público
15. **LICENSE y SECURITY.md** verificados y actualizados

---

## 19. Bibliografía y Referencias Técnicas

**Semiótica y Filosofía:**
- Peirce, C.S. (1868–1914). *Collected Papers*. Harvard University Press.
- Eco, U. (1990). *The Limits of Interpretation*. Indiana University Press.
- Grice, H.P. (1975). "Logic and Conversation." *Syntax and Semantics* 3.
- Carnegie, D. (1936). *How to Win Friends and Influence People*.

**Forense Digital:**
- Casey, E. (2011). *Digital Evidence and Computer Crime* (3rd ed.).
- Carrier, B. (2005). *File System Forensic Analysis*.
- SANS Institute. *DFIR Curriculum* — TCO 558.

**Marcos Forenses:**
- MITRE ATT&CK Enterprise v14.1: https://attack.mitre.org
- ENFSI Guideline for Evaluative Reporting in Forensic Science (2015)
- STIX 2.1 Specification (OASIS)
- ISO/IEC 27037:2012 — Digital Evidence Handling
- RFC 3161 — Internet X.509 PKI Timestamping

**Estándares Judiciales:**
- *Daubert v. Merrell Dow Pharmaceuticals*, 509 U.S. 579 (1993)
- *Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999)
- *Frye v. United States*, 293 F. 1013 (D.C. Cir. 1923)

**Matemáticas y Estadística:**
- Ledoit, O. & Wolf, M. (2004). "A well-conditioned estimator for large-dimensional covariance matrices."
- Bandt, C. & Pompe, B. (2002). "Permutation entropy." *Physical Review Letters*.
- Lempel, A. & Ziv, J. (1976). "On the complexity of finite sequences." *IEEE Transactions on IT*.
- Stability Selection: Meinshausen & Bühlmann (2010). *JRSS-B*.

**Implementación:**
- FastMCP: Anthropic MCP Framework
- Volatility 3: The Volatility Foundation
- Plaso / log2timeline: Google

---

*"La mentira tiene un costo computacional. VIGÍA lo cobra."*

*Documento generado: 18 de mayo de 2026. VIGÍA AI Collective.*
