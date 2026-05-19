# VIGÍA — Análisis de Intencionalidad para SIFT Workstation

> *"La mentira tiene un costo computacional. VIGÍA lo cobra."*

**SANS FIND EVIL Hackathon 2026** | Autora: Anna Tchijova | Colectivo: VIGÍA AI Collective | Licencia: MIT

---

## El Cambio de Paradigma: de IoC a IoI

Los sistemas DFIR actuales — EDR, SIEM, SOAR — responden: **"¿Qué pasó?"**

VIGÍA responde: **"¿Por qué pasó, y quién se beneficia de esa interpretación?"**

Este cambio — de **Indicador de Compromiso (IoC)** a **Indicador de Intención (IoI)** — es la innovación central del proyecto. Los atacantes sofisticados pueden fabricar o suprimir evidencia técnica. No pueden eliminar las fracturas semióticas que produce la fabricación deliberada.

---

## Descripción General

VIGÍA es un puente de integración analítica para la SIFT Workstation. Opera sobre los mismos artefactos ya procesados por SIFT y agrega una capa de análisis de intencionalidad basada en:

- **Semiótica Peirciana**: razonamiento abductivo (Firstness → Secondness → Thirdness) como motor de inferencia central
- **Silencio Significativo (Eco)**: la ausencia de evidencia esperada es evidencia
- **Máximas de Grice**: violaciones conversacionales en artefactos digitales como señal forense
- **Patrones Carnegie**: taxonomía de manipulación aplicada a texto libre
- **Navaja de Ockham**: selección de hipótesis por economía explicativa

El sistema produce un `ForensicBundle` sellado con SHA-256 — determinista, bit a bit reproducible, auditable sin acceso al runtime — compatible con los estándares de admisibilidad Daubert.

---

## Arquitectura

```
EVIDENCIA (logs, imágenes de disco, memoria, red)
         │
         ▼
    SIFT WORKSTATION (extracción forense)
         │
         ▼
    SERVIDOR MCP VIGÍA
    │
    │  CAPA 0: ebs_v1.py          — Contratos de datos (inmutable)
    │  CAPA 1: señales externas   — Herramientas forenses SIFT
    │  CAPA 2: likelihood_engine  — KDE + Ledoit-Wolf
    │          graph_stability    — Bootstrap stability selection
    │  CAPA 3: risk_bounded_layer — r=(1-P)·(1+λD)·(1+γ(1-S))
    │  CAPA 4: audit_action       — Diff/Optimizer/PolicyEngine
    │  CAPA 5: verify_ebs_v1.py   — Verificación stdlib puro
    │
    └─ SIFT BRIDGE (21+ herramientas MCP)
         │
         ▼
    PEIRCE PLANNER (Ollama / Claude Code)
    — SOLO narrativa — fuera del loop de decisión matemática —
```

### Regla de Oro

El LLM queda **fuera del loop de decisión matemática**. Su única función es traducir el `ForensicBundle` sellado a narrativa humana. La decisión ya está cerrada cuando el LLM entra. Esto no es negociable — es un requisito de admisibilidad Daubert.

---

## Características Principales

### Pipeline EBS v1 — Determinismo Forense

- `ForensicBundle` sin método `seal()` — el sellado es externo (un motor comprometido no puede sellar su propia mentira)
- `verify_ebs_v1.py` usa únicamente stdlib Python (confirmado por inspección AST)
- `json.dumps` con `sort_keys=True` en todo el pipeline
- `_round_floats()` antes de todo hashing para determinismo cross-OS
- Aritmética con `decimal.Decimal` en paths críticos

### Motor Abductivo — 33 Hipótesis en 13 Fases IR

Cubre el ciclo de vida completo del incidente según MITRE ATT&CK Enterprise v14.1:
- Reconocimiento, Acceso Inicial, Ejecución, Persistencia
- Escalada de Privilegios, Evasión de Defensa, Acceso a Credenciales
- Movimiento Lateral, Recolección, C2, Exfiltración, Impacto

Hipótesis especiales: `H_SE_001` (False Security Theater — Paradoja de Jevons), `H_IM_003` (False Flag Operation)

### Cinco Clusters de Intención Semántica

| ID | Nombre | Rationale del Atacante |
|----|--------|------------------------|
| IC_01 | STEALTH | Operar sin detección |
| IC_02 | PERSISTENCE | Mantener acceso |
| IC_03 | EXFILTRATION | Extraer valor |
| IC_04 | DISRUPTION | Destruir o interrumpir |
| IC_05 | ESCALATION | Ampliar capacidad |

### CAIE — Cross-Artifact Incongruence Engine

8 reglas de fractura forense: MEMORY_VS_DISK, LOG_VS_MEMORY, TEMPORAL_PARADOX, CULTURAL_MARKER_MISMATCH, PERFECTION_ANOMALY, SILENCE_PATTERN, DOCUMENT_FORGERY, MULTI_TENANT_ISOLATION_BREACH

### Protocolo P2 — Semántica Forense Avanzada

22 vectores canónicos verificables: SHA-256 `f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`

Implementa: Markov Order-k, Lempel-Ziv LZ76, Permutation Entropy, Abstention Policy honesta

### Seguridad Paranoica

- **LLMShield**: firewall de prompt injection, 3 pasadas (NFKC + leet + original), 25+ patrones
- **Protocolo Kassandra**: tripwire semántico criptográfico determinista por sesión
- **HMAC Chain**: cadena de auditoría inmutable — tampering invalida todas las entradas subsiguientes
- **Sandbox de subprocesos**: límites RLIMIT_AS/RLIMIT_CPU, privilege drop
- **Mitigaciones TOCTOU**: `mkstemp()` + verificación post-escritura `lstat()`
- **Seguridad de transporte MCP**: session token, verificación stdin, bloqueo HTTP sin auth

---

## Instalación

### Requisitos

- Python 3.10+
- SIFT Workstation (recomendado)
- Claude Code o Ollama (para narrativa — opcional para el pipeline matemático)

### Instalación Rápida

```bash
git clone https://github.com/annatchijova/vigia-intent-analysis
cd vigia-intent-analysis
pip install -r requirements.txt --break-system-packages
```

### Verificar Integridad del Sistema

```bash
# Verificar vectores canónicos P2
sha256sum docs/protocols/P2/canonical_vectors_p2.json
# Esperado: f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce

# Verificar que verify_ebs_v1.py usa solo stdlib
python3 -c "
import ast, sys
tree = ast.parse(open('vigia/forensics/verify_ebs_v1.py').read())
imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
print('Imports encontrados:', len(imports))
"

# Ejecutar tests de integración
PYTHONPATH=$(pwd) python3 -m pytest tests/ -v
```

### Configuración de Variables de Entorno

```bash
# Obligatorio para producción
export VIGIA_HMAC_KEY="<hex-encoded-key-32-bytes-mínimo>"
export VIGIA_EVIDENCE_DIR="/var/log/vigia"

# Backend LLM (para narrativa — no afecta la decisión matemática)
export VIGIA_LLM_BACKEND="ollama"  # o "anthropic"
export OLLAMA_MODEL="llama3.1:8b"

# Seguridad de transporte
export VIGIA_ENFORCE_STDIO="true"

# Opcionales
export VIGIA_STRICT_MODEL_CHECK="true"   # CLIP model integrity
export VIGIA_CAIE_ENABLED="true"
export VIGIA_TRUST_FUSION_ENABLED="true"
```

### Docker

```bash
docker-compose up vigia-mcp
```

---

## Uso con Claude Code

`~/.claude/claude.json`:

```json
{
  "mcpServers": {
    "vigia_sift": {
      "command": "python3",
      "args": ["/path/to/vigia-intent-analysis/vigia_sift_bridge_final.py"]
    }
  }
}
```

Luego en Claude Code:

```
Analizá la evidencia en /evidence/caso_001/ y determiná si existe intención
maliciosa. Usá las herramientas VIGÍA para calcular entropía, detectar
incoherencias de artefactos cruzados, y generá una narrativa forense
que explique el PROPÓSITO de cada hallazgo.
```

---

## Uso con Ollama

```bash
# Iniciar servidor MCP
python3 vigia_sift_bridge_final.py

# Interrogar en otra terminal
./vigia_ask.sh "Analizá estos artefactos y determiná intención"

# O vía API REST
python3 vigia_api.py
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d @mi_caso.json
```

---

## Ejemplos de Investigación

### Investigación Autónoma (un solo comando)

```
Analizá la evidencia en /evidence/caso_001/ y determiná si existe
intención maliciosa. Usá las herramientas VIGÍA para detectar anomalías
de hábitos en memoria y generá una narrativa forense.
```

### Detección de Falsa Bandera

```
Montá la imagen en /evidence/servidor.E01. Los logs dicen que hubo un
login RDP ruso a las 03:00 UTC. Compará contra memoria para determinar
si el login realmente ocurrió o si fue fabricado.
```

### Análisis de Integridad Documental

```
Auditá el documento en /evidence/contrato.pdf. Verificá coherencia
tipográfica, consistencia de márgenes, y validá los campos obligatorios.
```

---

## Flujo de Investigación

```
SOSPECHA INICIAL
      │
      ├─ Evidencia demasiado perfecta? → detect_eco_overinterpretation
      │                                   → ir a memoria PRIMERO (saltear logs)
      │
      ├─ Es humano?                    → calculate_human_entropy
      │                                   detect_human_jitter
      │
      ├─ Es una sola identidad?        → analyze_stylometry
      │
      ├─ Qué quiere?                   → infer_intent
      │                                   audit_grice_maxims
      │
      ├─ Memoria consistente?          → detect_habit_incongruence
      │                                   (Volatility: LSASS vs logs)
      │
      ├─ Artefactos consistentes?      → cross_artifact_analysis (CAIE)
      │
      └─ Confianza integrada?          → trust_fusion_analysis
                                          → ForensicBundle sellado → SIFT
```

---

## Herramientas MCP Disponibles

### Cadena de Custodia (9)
`mount_sift_evidence`, `generate_forensic_hash`, `read_evidence`, `list_files`, `search_pattern`, `list_processes`, `audit_network`, `calculate_shannon_entropy`, `detect_eco_overinterpretation`

### Análisis de Intencionalidad (9)
`calculate_human_entropy`, `detect_human_jitter`, `analyze_stylometry`, `infer_intent`, `audit_grice_maxims`, `detect_habit_incongruence`, `cross_artifact_analysis`, `trust_fusion_analysis`, `investigate_autonomous`

### Integridad Documental (5)
`audit_document_integrity`, `analyze_image_layers`, `detect_document_geometry`, `ocr_semantic_validator`, `vision_intent_audit`

---

## Cumplimiento Daubert

VIGÍA implementa Nivel 3 de cumplimiento Daubert:

| Criterio | Implementación |
|---------|---------------|
| Testabilidad | 22 vectores canónicos P2 verificables por terceros |
| Revisión de pares | Colectivo de 7 IAs con auditorías vinculantes documentadas |
| Tasa de error conocida | `calibration_metadata.json` con brier_score, AUC, FPR/TPR |
| Aceptación general | MITRE ATT&CK v14.1, escala ENFSI, STIX 2.1, ISO 27037 |

Invariantes no negociables (EBS v1):
- I1 — Determinismo: mismo input → mismo bundle
- I2 — Integridad encadenada: bundle_hash cubre TODO
- I3 — Política verificable: independiente del runtime
- I4 — Acciones explícitas: sin efectos implícitos
- I5 — Decisión explicable: risk y posterior siempre presentes

---

## Limitaciones Conocidas

El corpus de calibración es actualmente sintético (bootstrap v1). Los umbrales operacionales están pendientes de validación con datos forenses reales. Ver `known_limitations.md` para el inventario completo de casos límite y decisiones de diseño.

Limitación crítica (L-004): el `LLMShield` filtra inyecciones directas pero no neutraliza narrativas engañosas embebidas en texto libre. Todo artefacto de texto libre debe tratarse con trust reducido manualmente.

---

## Estructura del Repositorio

```
vigia-intent-analysis/
├── vigia/
│   ├── core/           — Pipeline EBS v1 (capas 0-4)
│   ├── forensics/      — verify_ebs_v1.py, bundle_builder.py
│   ├── tools/          — Herramientas MCP (CAIE, MITRE, documento, visión)
│   ├── engine/         — LikelihoodEngine, GraphStability
│   ├── governance/     — RiskBoundedLayer, PolicyEngine
│   └── security.py     — LLMShield, HMAC Chain, sandbox
├── vigia_sift_bridge_final.py  — Servidor MCP principal
├── pipeline.py                  — Orquestador del pipeline
├── verify_ebs_v1.py             — Verificador independiente (stdlib puro)
├── docs/
│   └── protocols/
│       ├── P1/         — Protocolo P1 (congelado)
│       └── P2/         — Protocolo P2 (v2.8 draft)
├── tests/              — 55+ tests de integración
├── cases/              — 186 casos en formato JSON
└── docker-compose.yml
```

---

## Dependencias Principales

| Paquete | Propósito |
|---------|-----------|
| `fastmcp` / `mcp` | Framework servidor MCP |
| `anthropic` | API Claude para razonamiento |
| `sklearn` | Calibración (GridSearchCV, Ledoit-Wolf) |
| `psutil` | Monitoreo de procesos |
| `Pillow` | Extracción de metadatos EXIF, ELA |
| `volatility3` | Forense de memoria (SIFT) |
| `plaso` | Análisis de timeline (SIFT) |

---

## Cita Académica

```bibtex
@software{vigia2026,
  author  = {Tchijova, Anna and VIGÍA AI Collective},
  title   = {VIGÍA: Intentionality Analysis Bridge for SIFT Workstation},
  year    = {2026},
  url     = {https://github.com/annatchijova/vigia-intent-analysis},
  version = {2.1.0},
  note    = {SANS FIND EVIL Hackathon 2026}
}
```

---

## Licencia y Ética

MIT License.

Todos los contribuyentes del proyecto acuerdan:
1. **No maleficencia**: VIGÍA no será usado para fabricar evidencia
2. **Transparencia**: todas las hipótesis abductivas incluyen condiciones de falsabilidad
3. **Integridad judicial**: las narrativas Amicus distinguen claramente hallazgos confirmados de inferidos

*"Construimos herramientas para encontrar la verdad, no para construir narrativas."*

---

*SANS FIND EVIL Hackathon 2026. Si VIGÍA gana, se integra a SIFT.*
