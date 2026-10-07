# VIGÍA — README Técnico
## Motor determinista de análisis forense de intencionalidad para SIFT Workstation

[README (ES)](../README_ES.md) · [README (EN)](../README.md) · [Technical README (EN)](./VIGIA_TECHNICAL_STATE_EN.md) · [Índice de documentación académica](./academic/ACADEMIC_DOCS_MASTER_INDEX.md)

**Autora e investigadora principal:** Anna Tchijova
**Colectivo de auditoría:** Claude (Anthropic), Kimi (Moonshot), Gemini (Google), DeepSeek, Qwen, ChatGPT (red team adversarial)
**Repositorio:** `github.com/annatchijova/vigia-intent-analysis` · **Licencia:** Apache 2.0
**Versión del documento:** 2.0 — 7 de octubre de 2026 (reemplaza al dossier v1.0 del 18 de mayo de 2026)
**Audiencia:** auditores, peritos y revisores independientes

> Todas las cifras de este documento se midieron sobre el árbol del repositorio
> en la fecha indicada y llevan su fuente o el comando que permite reproducirlas
> (ver [§2.4](#24-cómo-reproducir-las-mediciones)). Donde una cifra proviene de
> un registro histórico y no de una medición nueva, se dice explícitamente.

---

## Índice

1. [Qué es VIGÍA](#1-qué-es-vigía)
2. [Magnitud del trabajo](#2-magnitud-del-trabajo)
3. [Documentación académica: 193 módulos en 4 idiomas](#3-documentación-académica-193-módulos-en-4-idiomas)
4. [Estado actual del proyecto](#4-estado-actual-del-proyecto)
5. [Fundamentos teóricos](#5-fundamentos-teóricos)
6. [Arquitectura](#6-arquitectura)
7. [Motor de puntuación y veredicto (Modo 1)](#7-motor-de-puntuación-y-veredicto-modo-1)
8. [Sellado, cadena de custodia y verificación independiente](#8-sellado-cadena-de-custodia-y-verificación-independiente)
9. [Motor abductivo e hipótesis](#9-motor-abductivo-e-hipótesis)
10. [Integración MITRE ATT&CK](#10-integración-mitre-attck)
11. [Protocolos P1 y P2](#11-protocolos-p1-y-p2)
12. [Subsistema de seguridad](#12-subsistema-de-seguridad)
13. [Likelihood ratio y calibración](#13-likelihood-ratio-y-calibración)
14. [Herramientas MCP (Modo 2)](#14-herramientas-mcp-modo-2)
15. [Modos de despliegue, LLM y API](#15-modos-de-despliegue-llm-y-api)
16. [Verificación del propio sistema: tests, mutation testing y red team](#16-verificación-del-propio-sistema-tests-mutation-testing-y-red-team)
17. [Corpus de casos y evaluación](#17-corpus-de-casos-y-evaluación)
18. [Cumplimiento Daubert](#18-cumplimiento-daubert)
19. [Limitaciones conocidas y trabajo abierto](#19-limitaciones-conocidas-y-trabajo-abierto)
20. [Bibliografía y referencias técnicas](#20-bibliografía-y-referencias-técnicas)

---

## 1. Qué es VIGÍA

VIGÍA es un motor de análisis forense de **intencionalidad** diseñado como puente
de integración para la SANS SIFT Workstation. Los sistemas DFIR convencionales
(EDR, SIEM, SOAR) responden "¿qué pasó?". VIGÍA responde "¿por qué pasó, qué
decisiones deliberadas revela ese camino, y quién se beneficia de esa
interpretación?".

El sistema introduce el **Indicador de Intención (IoI)** como complemento del
Indicador de Compromiso (IoC). Un atacante puede fabricar o suprimir evidencia
técnica; lo que no puede eliminar son las fracturas semióticas que produce la
fabricación deliberada: incoherencias temporales, silencios significativos,
perfección digital excesiva, patrones de influencia de Carnegie y violaciones de
las máximas de Grice.

Tres pilares técnicos lo sostienen:

1. **Semiótica peirciana operacionalizada.** El razonamiento abductivo
   (Terceridad) es parte del motor de inferencia, no un post-procesador
   decorativo.
2. **Determinismo estricto.** La puntuación usa `fractions.Fraction` y
   `decimal.Decimal` con `prec=28` y `ROUND_HALF_EVEN`. El mismo input analítico
   produce el mismo `analysis_fingerprint`; el `bundle_hash` cambia por corrida
   porque además sella UUID y timestamps de custodia. Son dos contratos
   distintos y verificables, y no deben confundirse.
3. **El LLM queda fuera del loop de decisión.** Todo veredicto sellado, en todos
   los modos, lo produce y lo aprueba el motor Python determinista. Un LLM puede
   proponer y narrar; no decide, no puede saltear la compuerta de corroboración
   Daubert y no puede modificar un bundle sellado.

---

## 2. Magnitud del trabajo

VIGÍA no es un prototipo de un solo archivo. Es un sistema de **más de 102.000
líneas de Python de producción** respaldado por **más de 540.000 líneas de JSON y
Markdown** entre casos, evidencia, bundles sellados, resultados y documentación.
En total, el repositorio versiona **más de 713.000 líneas de texto**.

### 2.1 Código Python

| Ámbito | Archivos | Líneas físicas | Líneas no vacías |
|--------|---------:|---------------:|-----------------:|
| **Código de producción** (todo lo que no es test) | 273 | **108.805** | 94.852 |
| Suites de tests (`tests/`, `vigia/tests/`, `test_*.py`) | 280 | 46.931 | 38.967 |
| `attic/` (código archivado) | 3 | 403 | 338 |
| **Total Python** | **556** | **156.139** | **134.157** |

Distribución del código de producción por paquete (líneas físicas):

| Paquete | Archivos | Líneas | Contenido |
|---------|---------:|-------:|-----------|
| `vigia/tools/` | 33 | 19.943 | CAIE, NLP adversarial, MITRE, integridad documental, visión |
| `vigia/core/` | 53 | 18.369 | Scorer, contratos EBS v1, sellado, cadena de log, calibración, kernel epistémico |
| `vigia/` (raíz del paquete) | 14 | 6.358 | Bridge MCP (`vigia_sift_bridge.py`), API, CLI, `collapse_decision.py` |
| Raíz del repositorio | 21 | 11.781 | `vigia_scorer.py`, `vigia_agent.py`, `sift_orchestrator.py`, verificadores |
| `scripts/` | 45 | 10.507 | Conversión de casos, corridas de corpus, auditorías |
| `vigia/sift/` | 25 | 10.278 | MFT, prefetch, registry, shellbags, memoria, red, navegadores, móviles |
| `vigia/forensics/` | 9 | 6.073 | PDF, PKI, RFC 3161, cadena de custodia |
| `vigia/inference/` | 11 | 4.665 | Motor abductivo canónico, fingerprint conductual |
| `vigia/pipeline/` | 7 | 3.983 | Pipeline, bundle, reportes |
| `vigia/security/` | 5 | 2.549 | `LLMShield`, sandbox, saneamiento de rutas |
| `vigia/scripts/`, `vigia/abduction/`, `vigia/action/`, `vigia/ui/`, `forensics/` y otros | 50 | 14.299 | Planificación, mitigación, web UI offline, verificador EBS v1 |

### 2.2 Casos, evidencia, resultados y documentación

| Tipo | Archivos | Líneas | Dónde vive |
|------|---------:|-------:|------------|
| **JSON** — casos, evidencia, bundles sellados, datasets | 1.222 | **362.744** | `results/` (749 archivos, 228.965 líneas), `data/` (279 archivos, 86.510 líneas), `blind_cases_for_mcp/`, `cases/`, `evidence/`, `scripts/`, `vigia/` |
| **Markdown** — documentación, reportes, amicus curiae | 689 | **180.084** | `docs/` (329 archivos, 73.612 líneas), `docs_merged/` (193 fuentes académicas, 42.236 líneas), raíz (32.605 líneas: bugs, limitaciones, instalación), `results/`, `evidence/`, `cronos/` |
| HTML, SQL, YAML, JavaScript, shell y otros textos | — | 14.730 | Sitios de documentación, esquemas, workflows de CI |
| Sidecars `.sha256` de bundles sellados | 631 | — | Junto a cada bundle en `results/`, `cases/`, `audits/` |
| **Subtotal JSON + Markdown + otros** | | **557.558** | |

### 2.3 Lo que hay detrás de las líneas

- **617 bundles forenses sellados** (`*_bundle.json`) en `results/`, cada uno
  verificable sin el código de VIGÍA (ver [§8](#8-sellado-cadena-de-custodia-y-verificación-independiente)).
- **2.066 funciones de test en 255 archivos de test**. La última medición
  completa registrada (B-227, 2026-08-12) dio **2.237 passed, 0 failed** con el
  entorno MCP completo.
- **223 bugs documentados** con causa raíz, fix y verificación, con numeración
  hasta B-241: 214 entradas resueltas en
  [`BUGS_HISTORICO.md`](../BUGS_HISTORICO.md) y 9 abiertas en
  [`BUGS_PENDIENTES.md`](../BUGS_PENDIENTES.md), ambos en ES y EN.
- **70 limitaciones documentadas**, numeradas de L-001 a L-073, en
  [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md), incluidas las abiertas: se
  marcan, no se borran.
- **11 rondas de red team** propias (`docs/REDTEAM_ROUND2` a `ROUND12`), más
  auditorías abductivas, de cobertura, de seguridad del veredicto sellado y
  censos de punto flotante en `docs/AUDITORIA_*` y `docs/AUDIT_*`.
- **Mutation testing semanal** del camino del veredicto (ver [§16](#16-verificación-del-propio-sistema-tests-mutation-testing-y-red-team)).
- **193 módulos documentados académicamente en 4 idiomas** (ver [§3](#3-documentación-académica-193-módulos-en-4-idiomas)).

### 2.4 Cómo reproducir las mediciones

Las cifras de §2 cuentan **solo archivos versionados en git** (`git ls-files`),
así que no dependen de lo que haya suelto en una máquina local, y excluyen
archivos binarios (imágenes, modelos, bases SQLite). "Líneas físicas" equivale a
`wc -l`. Las cifras de Markdown se mueven levemente con cada edición de la
documentación, incluida la de este mismo archivo; las de esta versión se tomaron
sobre el árbol que la contiene. Un archivo es "test" si su ruta contiene un directorio
`tests` o su nombre empieza con `test_`.

```bash
# Líneas por tipo de archivo
for e in py json md; do
  printf '%s: ' "$e"; git ls-files -z "*.$e" | xargs -0 cat | wc -l
done

# Python de producción (excluye tests y attic/)
git ls-files '*.py' | grep -v -E '(^|/)tests/|(^|/)test_|^attic/' | tr '\n' '\0' | xargs -0 cat | wc -l

# Total de líneas de texto versionadas
git ls-files -z | xargs -0 grep -Il '' 2>/dev/null | tr '\n' '\0' | xargs -0 cat | wc -l
```

---

## 3. Documentación académica: 193 módulos en 4 idiomas

La documentación de referencia de cada módulo vive en el
**[Índice Maestro de Documentación Académica](./academic/ACADEMIC_DOCS_MASTER_INDEX.md)**,
que cubre el corpus de **193 módulos** en **cuatro idiomas: inglés, español,
ruso y chino**. El índice tiene una versión por idioma:

| Idioma | Índice |
|--------|--------|
| Español | [`ACADEMIC_DOCS_MASTER_INDEX.md`](./academic/ACADEMIC_DOCS_MASTER_INDEX.md) |
| English | [`ACADEMIC_DOCS_MASTER_INDEX_EN.md`](./academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md) |
| Русский | [`ACADEMIC_DOCS_MASTER_INDEX_RU.md`](./academic/ACADEMIC_DOCS_MASTER_INDEX_RU.md) |
| 中文 | [`ACADEMIC_DOCS_MASTER_INDEX_ZH.md`](./academic/ACADEMIC_DOCS_MASTER_INDEX_ZH.md) |

Cada documento académico explica el módulo en los cuatro idiomas con la misma
estructura: qué es el módulo, conceptos clave, glosario técnico, una nota
científica que lo vincula con la semiótica de Peirce, Eco y Grice, y los
procedimientos de uso. Sumados, los documentos académicos tienen **36.855
líneas**; sus 193 fuentes de generación se conservan en `docs_merged/` (42.236
líneas). Junto al índice están los informes de síntesis de investigación
[`VIGIA_RESEARCH_REPORT.md`](./academic/VIGIA_RESEARCH_REPORT.md) (ES) y
[`VIGIA_RESEARCH_REPORT_EN.md`](./academic/VIGIA_RESEARCH_REPORT_EN.md) (EN).

Organización por área:

| Carpeta | Documentos | Contenido |
|---------|-----------:|-----------|
| `core/` | 38 | Pipeline central, semiótica, señales, calibración |
| `tools/` | 22 | CAIE, NLP adversarial, MITRE, patrones, EML |
| `sift/` | 9 | MFT, prefetch, shellbags, registry, red, navegador, memoria |
| `forensics/` | 5 | PDF, PKI, RFC 3161, visión, cadena de custodia |
| `inference/` | 5 | Razonamiento abductivo, fingerprint conductual |
| `pipeline/` | 4 | Bundle, reporte, bridge SIFT, registro de evidencia |
| `security/` | 4 | Sandbox, seguridad forense, hardening |
| `governance/` | 2 | Niveles de confianza, capa de riesgo |
| `specialized/` | 2 | Módulos especializados menores |
| `root/` | 13 | API, CLI, configuración, núcleo |
| `scripts/` | 10 | Utilidades de ejecución, conversión y análisis |
| `unclassified/` | 78 | Módulos cuya ruta Python no se resolvió al generar (navegables desde la sección 12 del índice) |

**Trazabilidad del conteo.** El manifiesto de generación
[`_reorganization_manifest.json`](./academic/_reorganization_manifest.json)
registra **193 módulos procesados, 0 errores**. En disco hay hoy 192 documentos:
el de `vigia/tools/vigia_planner_GIT.py` figura en el manifiesto pero su archivo
no está en `tools/`. De los 192 presentes, 190 contienen las cuatro lenguas
completas y 2 (`unclassified/673c2ea3`, `unclassified/0c4cec60`) están
parciales. La documentación académica se generó con la Batch API de Moonshot
(Kimi K2.6) y la auditó el colectivo VIGÍA; es documentación de módulos, no
forma parte del camino del veredicto. Para refrescar la columna de idiomas del
índice: `python3 docs/academic/refresh_index_status.py`.

---

## 4. Estado actual del proyecto

Estado al 7 de octubre de 2026.

| Aspecto | Estado | Fuente |
|---------|--------|--------|
| Suite de tests | 2.237 passed / 0 failed con `mcp` 1.29.0; 2.127 passed / 0 failed en el entorno mínimo de CI | [`BUGS_HISTORICO.md`](../BUGS_HISTORICO.md) B-227 |
| Corpus de detección (Modo 1, agente sobre JSON, ciego a etiqueta, 0 llamadas a LLM) | **158/162 (97,5 %)** | [`ACCURACY_ES.md`](./ACCURACY_ES.md) |
| Corpus mixto (incluye 31 casos adversariales diseñados para romper el sistema) | 187/199 (94,0 %) | [`ACCURACY_ES.md`](./ACCURACY_ES.md) |
| Evidencia raw real (Dominio C) | 43 fuentes de evidencia raw con bundles sellados | [`ACCURACY_ES.md`](./ACCURACY_ES.md), [`RAW_CASES_LOG_ES.md`](./RAW_CASES_LOG_ES.md) |
| Registro de bugs | 223 entradas, numeración hasta B-241; 9 abiertas | [`BUGS_PENDIENTES.md`](../BUGS_PENDIENTES.md) |
| Limitaciones documentadas | 70 entradas, L-001 a L-073 | [`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md) |
| CI | 4 workflows: `pytest.yml`, `vigia-forensic-ci.yml`, `mutation.yml` (semanal), `docker-publish.yml` | `.github/workflows/` |

Los números del corpus **no** son "la precisión de Claude": los produce el motor
Python determinista. El 97,5 % aplica solo al subconjunto de detección; no
representa evidencia raw ni el rendimiento de todos los modos. La metodología
completa, el mecanismo del gate y el desglose por dominios están en
[`ACCURACY_ES.md`](./ACCURACY_ES.md).

---

## 5. Fundamentos teóricos

### 5.1 Peirce: Primeridad, Segundidad, Terceridad

La tríada semiótica de Charles Sanders Peirce (1839–1914) es la estructura
operacional del razonamiento forense:

- **Primeridad:** la señal tal como aparece, sin interpretación. Una anomalía de
  timestamp, un proceso huérfano en memoria, una entropía de Shannon fuera de
  rango.
- **Segundidad:** la señal en relación con un baseline. El timestamp es
  inconsistente *respecto de* los demás artefactos del caso; la entropía es
  demasiado alta *comparada con* texto humano auténtico.
- **Terceridad:** la hipótesis que explica la relación. No es deducción ni
  inducción: es *abducción*, la inferencia a la mejor explicación disponible,
  falsable y con condiciones explícitas de refutación.

El `AbductionTrace` de cada `ForensicBundle` registra las tres etapas. El perito
puede auditar cada paso sin acceso al código fuente.

### 5.2 Eco: silencio significativo y sobreinterpretación

- **Silencio significativo:** la ausencia de evidencia esperada es evidencia. Si
  un tipo de actividad deja rastros característicos y esos rastros faltan, la
  ausencia es una señal de primer orden.
- **Navaja de Eco:** si la evidencia es *demasiado perfecta* y encaja *demasiado
  bien* con la hipótesis obvia, eso es sospechoso. La herramienta
  `detect_eco_overinterpretation` lo operacionaliza.

### 5.3 Grice: máximas conversacionales aplicadas a evidencia

H. Paul Grice (1913–1988) postuló cuatro máximas de la comunicación cooperativa
(cantidad, calidad, relación, modo). El texto engañoso viola sistemáticamente al
menos una. `audit_grice_maxims` (v3.2, B-126) es un detector bilingüe EN+ES
basado en fenómenos con cuatro rasgos: imposibilidad fáctica, asimetría de
cantidad, retención de evidencia e ignorancia fundamental.

### 5.4 Carnegie: patrones de manipulación

Dale Carnegie (1888–1955) documentó patrones de influencia interpersonal. VIGÍA
los usa como taxonomía de manipulación: urgencia artificial, autoridad prestada,
adulación como vector de acceso, presión de normalización. Los patrones
calibrados están en `vigia_patterns_migration.sql`
(`CARNEGIE_ARTIFICIAL_URGENCY`, `CARNEGIE_BORROWED_CREDIBILITY`,
`GRICE_QUANTITY_STARVATION`, entre otros).

### 5.5 Ockham: selección de hipótesis

Entre hipótesis de igual poder explicativo, gana la más simple. Si "error
humano" explica los artefactos tan bien como "ataque dirigido", VIGÍA no emite
el veredicto más grave. `vigia/core/ockham_adversarial.py` evalúa hipótesis
alternativas y penaliza las que necesitan supuestos extra.

---

## 6. Arquitectura

### 6.1 Visión de alto nivel

```
┌──────────────────────────────────────────────────────────────────┐
│                        SIFT WORKSTATION                          │
│  adquisición → montaje read-only → extracción de artefactos      │
└────────────────────────┬─────────────────────────────────────────┘
                         │  evidencia raw o caso JSON
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│               NÚCLEO DETERMINISTA (Modo 1, 0 tokens)             │
│                                                                  │
│  vigia_agent.py ─► señales (SIFT, NLP, CAIE, TrustFusion)        │
│                ─► vigia_scorer.py (Fraction / Decimal prec=28)   │
│                ─► compuerta de corroboración Daubert             │
│                ─► BundleBuilder.seal() → ForensicBundle sellado  │
│                                                                  │
│  Verificación independiente: forensics/verify_ebs_v1.py,         │
│  verify_tool_log.py (solo stdlib)                                │
└────────────────────────┬─────────────────────────────────────────┘
                         │  bundle sellado (inmutable)
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│         CAPA NARRATIVA (Modos 2, 3, 5 — LLM opcional)            │
│  Claude Code + MCP (Vigia_Sift_Bridge) / Ollama / OpenWebUI      │
│  Narra y propone; NO modifica el bundle ni el veredicto          │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 Aislamiento de capas

Cada capa tiene una dirección de dependencia definida. Los contratos de datos
(`vigia/core/ebs_v1.py`) no importan nada de capas superiores. El kernel
epistémico (`vigia/core/ontology.py`, `vigia/core/reasoning/abduction.py`)
genera hipótesis pero no emite veredicto, score ni salida sellada: nada del
pipeline de puntuación lo importa y un test de regresión lo hace cumplir (ver
[`EPISTEMIC_KERNEL.md`](./EPISTEMIC_KERNEL.md)).

La regla de oro: **el LLM queda fuera del loop de decisión matemática.** Fue
propuesta por el colectivo de auditoría y aceptada como requisito Daubert.

### 6.3 ForensicBundle como unidad de entrega

El `ForensicBundle` es el artefacto sellado que VIGÍA entrega. Contiene, entre
otros: el grafo de evidencia, la traza de decisión (posterior, riesgo,
veredicto), la política activa, el estado del sistema al sellar, la traza
abductiva, la atestación de configuración y el bloque de integridad con los
hashes encadenados. Es portable, autocontenido y auditable sin el runtime.

**Invariante crítica:** `ForensicBundle` no tiene método `seal()`. El sellado
es responsabilidad exclusiva de `BundleBuilder`. Un motor comprometido no puede
sellar su propia mentira.

---

## 7. Motor de puntuación y veredicto (Modo 1)

### 7.1 Pipeline

`vigia_scorer.py` implementa el pipeline
**TrustFusion → CorrelationDecay → CAIE → Decision → Quadripartite**. Corre
standalone, sin instalar el paquete `vigia`, y cae a parámetros conservadores
si falta algún módulo. `vigia_agent.py` es el agente autónomo de extremo a
extremo que lo invoca y sella el resultado.

```bash
python3 vigia_agent.py --evidence /ruta/a/evidencia --case-id CASO-001
```

Códigos de salida: `0` = sin mal, `1` = MALICE, `2` = error,
`3` = intención/sospecha.

> `scripts/run_case.py` **no** es el núcleo determinista: solo invoca la capa
> narrativa LLM y no emite un veredicto sellado.

### 7.2 Aritmética exacta

El camino crítico usa `fractions.Fraction` y `decimal.Decimal` con `prec=28` y
`ROUND_HALF_EVEN`, lo que elimina la variación por mantisa de punto flotante
entre plataformas. Un valor float en la puntuación intermedia es una violación
de determinismo. El censo de floats está en
[`AUDIT_P0001_FLOAT_CENSUS.md`](./AUDIT_P0001_FLOAT_CENSUS.md); el residuo
latente conocido es L-073 (una comparación de umbral float contra `Fraction`
con incidencia cero en el corpus).

### 7.3 Escala de veredictos

| Veredicto | Significado | Exigencia |
|-----------|-------------|-----------|
| `NOISE` | Explicado por configuración, error de software o comportamiento normal | Una fuente |
| `SUSPICION` | Anomalía estructural sin evidencia de ocultamiento deliberado | Una fuente con desvío de baseline documentado |
| `INTENT` | Evidencia de decisiones deliberadas | Dos fuentes independientes + protocolo de refutación |
| `MALICE` | Ocultamiento activo de la intención | Dos fuentes + refutación + `devil_advocate` poblado |
| `ABSTAIN` | Evidencia insuficiente | Brecha documentada como limitación |

El motor del Modo 1 **no tiene escalón INTENT**: los casos limítrofes se acotan
a SUSPICION. El Modo 2 sí puede emitir INTENT cuando se cumplen el protocolo de
refutación y la corroboración de dos fuentes.

### 7.4 Compuerta de corroboración Daubert

La compuerta rechaza candidatos sin respaldo **antes** de sellar: si una clase
de evidencia tiene menos de dos artefactos, el candidato se acota a SUSPICION.
La autocorrección ocurre pre-emisión: ningún veredicto incorrecto llega al
bundle, y el LLM no puede saltear la compuerta. `vigia/collapse_decision.py`
contiene la lógica de colapso del veredicto; es uno de los módulos bajo
mutation testing semanal.

### 7.5 CAIE — Cross-Artifact Incongruence Engine

El CAIE pondera más la evidencia difícil de falsificar y detecta fracturas entre
artefactos:

1. **MEMORY_VS_DISK:** proceso en memoria sin ejecutable en disco.
2. **LOG_VS_MEMORY:** el log registra algo que la memoria contradice.
3. **TEMPORAL_PARADOX:** efecto antes que causa.
4. **CULTURAL_MARKER_MISMATCH:** marcadores lingüísticos inconsistentes con el origen declarado.
5. **PERFECTION_ANOMALY:** artefacto estadísticamente demasiado perfecto.
6. **SILENCE_PATTERN:** ausencia de evidencia esperada.
7. **DOCUMENT_FORGERY:** incoherencia multicapa en un documento.
8. **MULTI_TENANT_ISOLATION_BREACH:** violación de aislamiento en entornos cloud.

### 7.6 TrustFusion

`vigia/core/trust_fusion.py` cierra el ciclo temporal → procedencia →
correlación:

```
effective_trust = provenance_trust × exp(-2 × max_weighted_severity)
```

donde `max_weighted_severity` integra las violaciones temporales ponderadas por
spoofability.

---

## 8. Sellado, cadena de custodia y verificación independiente

### 8.1 Los cuatro hashes

| Hash | Qué cubre |
|------|-----------|
| H1 — `graph_hash` | SHA-256 del grafo de evidencia (artefactos + señales) |
| H2 — `bundle_hash` | SHA-256 del bundle sellado completo (cubre H1, decisión y metadatos) |
| H3 — cadena HMAC de auditoría | HMAC-SHA256 encadenado del log de la sesión |
| H4 — verificación EBS | Verificación independiente de H2 con `verify_ebs_v1.py` |

`python3 show_4_hashes.py <caso.json>` los muestra explícitamente.

### 8.2 Cadena del log de herramientas (v2)

Cada llamada a herramienta queda en `tool_execution_log`, generado con
`vigia.core.tool_log_chain.ToolExecutionLogChain`. En la versión 2, cada
`entry_hash` cubre la entrada **completa** más `seq` y `prev_hash`; con
`VIGIA_HMAC_KEY` presente se agrega `entry_hmac`. Modificar cualquier campo de
cualquier entrada rompe la cadena (en v1 solo se protegía `result_summary`).

Para detectar el truncado de la cola, la punta de la cadena
(`chain_tip_sha256` y `chain_tip_hmac`) se pasa **a través del sello**
(`BundleBuilder.seal(bundle, tool_log_tip=...)`), de modo que queda cubierta por
`bundle_hash`. Ver [`REDTEAM_ROUND6_PERIMETER.md`](./REDTEAM_ROUND6_PERIMETER.md).

### 8.3 Verificadores independientes

- **`forensics/verify_ebs_v1.py`** verifica bundles EBS v1 usando solo la
  biblioteca estándar de Python (confirmado por inspección AST). No importa
  `BundleBuilder`: implementa el mismo protocolo de forma independiente, así que
  si difieren, el fallo es del protocolo y no de un módulo.
- **`verify_tool_log.py`** verifica la cadena del log (v1 legada y v2), incluida
  la punta sellada; acepta clave HMAC por `--hmac-key-hex`, `--hmac-key-file` o
  variable de entorno.

```bash
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
python3 verify_tool_log.py <bundle.json>
```

### 8.4 Estado operativo fuera de la evidencia

La evidencia es de solo lectura. El estado operativo (montajes, cuarentena,
honey tokens, logs JSONL, bases SQLite forense y de cadena) va a
`VIGIA_WORK_DIR` y sus variables derivadas, que nunca pueden apuntar dentro de
`VIGIA_EVIDENCE_DIR`. Ver [`CLAUDE.md`](../CLAUDE.md) e
[`INSTALL_ES.md`](../INSTALL_ES.md).

---

## 9. Motor abductivo e hipótesis

### 9.1 Hipótesis implementadas

El motor canónico es `vigia/inference/abductive_intent_engine.py`
(`vigia/core/abductive_intent_engine.py` y `vigia/abductive_intent_engine.py`
son alias de re-exportación desde la consolidación L-052). Implementa **32
hipótesis abductivas sobre 12 fases** del ciclo de vida del incidente:

| Fase | Hipótesis |
|------|-----------|
| Reconnaissance | `H_RE_001` targeted_reconnaissance · `H_RE_002` osint_gathering · `H_RE_003` opportunistic_scanning |
| Initial Access | `H_IA_001` spearphishing_execution · `H_IA_002` exploitation_public_facing · `H_IA_003` supply_chain_compromise |
| Execution | `H_EX_001` command_line_abuse · `H_EX_002` scheduled_task_abuse · `H_EX_003` powershell_living_off_the_land |
| Persistence | `H_PE_001` single_persistence · `H_PE_002` multi_mechanism_persistence · `H_PE_003` redundant_persistence |
| Privilege Escalation | `H_PE_004` token_impersonation · `H_PE_005` exploit_vulnerability · `H_PE_006` kerberoasting |
| Defense Evasion | `H_DE_001` log_fabrication · `H_DE_002` log_deletion_after_exfil · `H_DE_003` anti_forensics_preparation |
| Credential Access | `H_CA_001` credential_dumping · `H_CA_002` brute_force · `H_CA_003` keylogger_deployment |
| Lateral Movement | `H_LM_001` pass_the_hash |
| Collection | `H_CO_001` data_staging_for_exfil · `H_CO_002` clipboard_and_screen_capture · `H_CO_003` audio_and_video_surveillance |
| Command and Control | `H_C2_001` domain_fronting_beacon · `H_C2_002` dns_tunnel_c2 · `H_C2_003` dead_drop_resolver |
| Exfiltration | `H_XF_001` bulk_data_exfiltration |
| Impact | `H_IM_001` ransomware_deployment · `H_IM_002` wiper_destruction · `H_IM_003` defacement_and_humiliation |

### 9.2 Falsabilidad explícita

Cada hipótesis tiene condiciones de refutación documentadas. Una hipótesis
forense que no puede refutarse no es científicamente válida.

### 9.3 Cinco clusters de intención

`MITREClusterer` (`vigia/tools/mitre_clustering.py`) agrupa las hipótesis en
cinco clusters de intención del atacante:

| `cluster_id` | Nombre en el código | Racional del atacante |
|--------------|---------------------|-----------------------|
| `STEALTH` | Invisibilidad y Ocultamiento | Operar sin ser detectado |
| `PERSISTENCE` | Arraigo y Control Duradero | Poder volver por cualquier vector |
| `EXFILTRATION` | Robo de Datos | Sacar información sin que se note |
| `DISRUPTION` | Sabotaje y Daño | Causar el máximo daño visible |
| `ESCALATION` | Elevación de Privilegios | Ampliar capacidad |

---

## 10. Integración MITRE ATT&CK

### 10.1 Diccionario maestro de TTPs

`vigia/tools/mitre_mapping.py` define `MASTER_TTP_DICTIONARY` con **27 técnicas**
de MITRE ATT&CK Enterprise. Cada una lleva `technique_id`, `base_severity`,
`spoofability_score` (0,0 = casi imposible de falsificar, 1,0 = trivial) y los
tipos de evidencia VIGÍA que la activan.

La `spoofability_score` es un aporte propio de VIGÍA: permite que el perito
pondere la credibilidad de la evidencia según cuán fácil es falsificarla, no
solo según su tipo.

### 10.2 Ejemplos de spoofability (valores del código)

| TTP | Nombre | Spoofability |
|-----|--------|-------------:|
| T1553.006 | Subvert Trust Controls: Code Signing Policy Modification | 0,05 |
| T1055 | Process Injection | 0,10 |
| T1611 | Escape to Host | 0,15 |
| T1006 | Direct Volume Access | 0,20 |
| T1059 | Command and Scripting Interpreter | 0,45 |
| T1070.001 | Indicator Removal: Clear Windows Event Logs | 0,50 |
| T1566 | Phishing | 0,60 |
| T1070.006 | Indicator Removal: Timestomp | 0,70 |
| T1586 | Compromise Accounts | 0,85 |
| T1585.001 | Establish Accounts: Social Media Accounts | 0,90 |

### 10.3 Exportación STIX 2.1

`to_stix_sdo()` y `to_stix_indicator()` convierten artefactos VIGÍA en objetos
STIX 2.1, para interoperar con OpenCTI, MISP y otras plataformas que consumen
STIX.

---

## 11. Protocolos P1 y P2

### 11.1 P1 (congelado)

P1 responde: "¿el kernel de entropía produce los mismos resultados en todas
partes?". Entropía de Shannon determinista en cualquier backend, valores de
referencia fijos (`entropy_uniform = 0.0`, `entropy_distinct = 1.0`,
`entropy_shannon_seed42 = 7.782633`) y codificación de pares sin colisiones
(`token = (uint64(a) << 32) | uint64(b)`). P1 es inmutable.

### 11.2 P2

P2 responde: "¿el sistema es matemáticamente consistente, adversarialmente
robusto y epistemológicamente honesto?". Agrega entropía de Markov de orden k
(MLE puro), complejidad Lempel-Ziv LZ76, entropía de permutación, política de
abstención con zona honesta [0,15, 0,85] cuantizada con `Decimal` HALF_EVEN, y
bloque obligatorio de discretización para la cadena de custodia.

Los 22 vectores canónicos están sellados con SHA-256
`f7276a524a46149a2811d52f9e5072d2a281df227f9d46d084a651d6420cf4ce`
([`protocols/P2/canonical_vectors_p2_sha256.txt`](./protocols/P2/canonical_vectors_p2_sha256.txt)).
Checklist y builds oficiales: [`docs/protocols/P2/`](./protocols/P2/). RFCs
técnicos: [`docs/rfcs/`](./rfcs/).

| Nivel | Descripción | Claim permitido |
|-------|-------------|-----------------|
| Strict | Python puro, `Decimal` HALF_EVEN, secuencial | "VIGÍA-compatible P2 (strict)" |
| Reference | NumPy/CuPy, acumulador float64, paralelo | "VIGÍA-compatible P2" |
| Accelerated | Cualquier backend, float32, subconjunto P2 | "VIGÍA-accelerated" (no puede reclamar P2 completo) |

**P2 garantiza:** equivalencia cuantizada determinista entre backends, entropía
contextual, semántica de complejidad, invariancia ordinal, rechazo adversarial
(denormales, NaN, Inf, overflow) y honestidad en la abstención.

**P2 no garantiza:** precisión absoluta (reproducibilidad no es verdad),
clasificación conductual, atribución de autoría, certificación de admisibilidad
legal ni corrección de la discretización upstream.

### 11.3 Brechas adversariales documentadas de P2

| ID | Nombre | Descripción |
|----|--------|-------------|
| GAP-01 | entropy_inflation_attack | Ruido uniforme de baja tasa satura métricas |
| GAP-02 | symbolic_explosion_attack | Perturbaciones sub-ULP inflan Shannon |
| GAP-03 | calibration_drift | Degradación de umbrales con drift de distribución |
| GAP-04 | backend_divergence_under_stress | Reducciones paralelas bajo carga |
| GAP-05 | heterogeneous_hardware | GPU entre fabricantes no validada empíricamente |
| GAP-06 | false_structure_induction | Inputs patológicos con LZ baja sin estructura real |
| GAP-07 | dataset_leakage_in_calibration | Solapamiento corpus de calibración / despliegue |
| GAP-08 | upstream_discretization_attack | El atacante controla la discretización upstream |
| GAP-09 | tie_break_exploitation | El stable sort de PE es explotable |
| GAP-10 | lz_period_aliasing | LZ76 asintótica, imprecisa en secuencias cortas |

---

## 12. Subsistema de seguridad

### 12.1 LLMShield

`LLMShield` (`vigia/security/security.py`) filtra prompt injection en tres
pasadas: texto normalizado NFKC (homoglifos Unicode), texto decodificado leet y
texto original. Cubre instruction override, familias DAN/jailbreak (de forma
contextual, sin falsos positivos con el nombre "Dan"), extracción de system
prompt, confusión de roles y delimitadores de token-stuffing.

**Límite conocido:** filtra inyecciones directas, pero no neutraliza narrativas
engañosas en texto libre. Todo artefacto de texto libre se trata con confianza
reducida (ver `KNOWN_LIMITATIONS.md`).

### 12.2 Nonce de sesión y tripwire

El nonce criptográfico de sesión se deriva de la primera evidencia procesada:
`nonce = HMAC-SHA256(KASSANDRA_SALT, evidence_seed)[:16]`. No puede cambiarse,
rotarse ni ser provisto por el usuario; un intento de redefinirlo es en sí una
señal de MALICE. La evidencia legítima se envuelve con delimitadores ligados al
nonce, así que una inyección que no lo conoce no puede imitarlos.

### 12.3 Cadena HMAC de logs

Cada entrada del log de auditoría lleva el HMAC de la anterior; alterar una
línea invalida todas las siguientes. Resolución de clave:
`VIGIA_HMAC_KEY` → `VIGIA_HMAC_KEY_FILE` → clave efímera (solo desarrollo, con
WARNING). `SecurityAudit` escribe en `VIGIA_LOG_DIR`, nunca dentro de la
evidencia (B-135).

### 12.4 Sandbox de subprocesos

`vigia/security/sandbox.py` (con `vigia/sandbox.py` como shim de compatibilidad) impone límites de memoria (`RLIMIT_AS`) y CPU
(`RLIMIT_CPU`), trunca la salida (10 MB stdout, 256 KB stderr), aplica timeout
duro con kill y hace privilege drop que aborta con `os._exit(126)` si
`setuid()` falla: nunca continúa como root. El bridge no llama a `subprocess`
directamente; todo pasa por `sandboxed_execute()`. El JobRunner de la web UI
termina el árbol de procesos completo, no solo el pid (B-240).

### 12.5 TOCTOU y saneamiento de rutas

Los temporales se crean con `tempfile.mkstemp()`; después de escribir, `os.lstat()`
confirma que no fueron reemplazados por un symlink antes del rename. Si lo
fueron, la operación aborta con `_IntegrityViolation`. `_sanitize_path()`
bloquea null bytes, resuelve tildes, aplica prefijos bloqueados, confina a
`base_dir` y valida symlinks.

### 12.6 Transporte MCP

`_verify_transport_security()` al arrancar: token de sesión de 128 bits a
stderr, verificación de stdin como pipe, alerta CRITICAL si hay HTTP/SSE sin
`VIGIA_MCP_AUTH_TOKEN`, y aborto si `VIGIA_ENFORCE_STDIO=true` y el transporte
es inseguro.

### 12.7 Integridad del modelo CLIP

Antes de cargar el modelo de visión se verifica su SHA-256. Con
`VIGIA_STRICT_MODEL_CHECK=true` se rechazan modelos sin hash configurado, para
evitar ataques de cadena de suministro con modelos envenenados.

---

## 13. Likelihood ratio y calibración

### 13.1 Escala ENFSI

`vigia/core/enfsi.py` es la única fuente de verdad de la escala verbal ENFSI
(unificada en B-059 para que el mismo LR no reciba etiquetas distintas en
distintos módulos):

| Likelihood ratio | Etiqueta |
|------------------|----------|
| 0 o NaN | inconclusive |
| < 1 | supports_H0 (la evidencia favorece autenticidad) |
| 1 ≤ LR < 2 | weak |
| 2 ≤ LR < 10 | limited |
| 10 ≤ LR < 100 | moderate |
| 100 ≤ LR < 1.000 | moderately strong |
| 1.000 ≤ LR < 10.000 | strong |
| ≥ 10.000 | very strong |

La etiqueta ENFSI describe la fuerza del LR; el veredicto lo decide el scorer
con su compuerta de corroboración.

### 13.2 Calibración

`vigia/core/lr_calibration.py` calibra con regresión logística (sklearn),
regresión isotónica si la logística no converge, o Platt scaling manual sin
sklearn. Metadatos vigentes (`models/calibration_metadata.json`, 2026-06-24):

| Parámetro | Valor |
|-----------|-------|
| Backend | `sklearn_logistic` |
| Corpus | 78 casos (hash `52d6dc6c…`) |
| Split | 80/20, `seed=42` (61 train / 14 eval) |
| Brier score (eval) | 0,1491 |
| TPR / FPR en 0,5 | 0,80 / 0,25 |

**Nota de honestidad:** el conjunto de evaluación es chico (14 casos) y los
umbrales de abstención de P2 (0,15/0,85) siguen siendo heurísticos. Las
métricas de calibración no deben leerse como tasa de error de producción.

---

## 14. Herramientas MCP (Modo 2)

El servidor `Vigia_Sift_Bridge` (`vigia/vigia_sift_bridge.py`) expone **22
herramientas base**, siempre registradas, y hasta **10 herramientas de
enriquecimiento** que se registran si su módulo carga y su flag lo permite.

### 14.1 Herramientas base

| Fase | Herramientas |
|------|--------------|
| Preservación de evidencia | `generate_forensic_hash`, `mount_sift_evidence`, `list_files`, `read_evidence` |
| Adquisición de señales | `calculate_shannon_entropy`, `search_pattern`, `audit_image_metadata`, `detect_habit_incongruence`, `audit_network`, `list_processes` |
| Análisis de intencionalidad | `infer_intent`, `detect_eco_overinterpretation`, `audit_grice_maxims`, `analyze_stylometry`, `calculate_human_entropy`, `detect_human_jitter` |
| Validación y autocorrección | `validate_and_correct_analysis`, `reason_with_llm` |
| Contramedidas | `activate_honey_token`, `deactivate_honey_token` |
| Utilidades | `reload_phonetic_dict`, `get_phonetic_dict_stats` |

### 14.2 Herramientas de enriquecimiento (registro dinámico)

| Herramienta | Módulo | Flag |
|-------------|--------|------|
| `audit_document_integrity`, `analyze_image_layers`, `detect_document_geometry`, `ocr_semantic_validator` | `vigia.tools.document_integrity` | siempre (si el módulo está) |
| `vision_intent_audit` | `vigia.tools.vision_audit` | siempre; requiere GPU y modelo CLIP (B-114) |
| `cross_artifact_analysis` | `vigia.tools.caie` | `VIGIA_CAIE_ENABLED` |
| `trust_fusion_analysis` | `vigia.core.trust_fusion` | `VIGIA_TRUST_FUSION_ENABLED` |
| `compare_paired_bundles` | `vigia.tools.paired_review` | `VIGIA_PAIRED_REVIEW_ENABLED` (sin autoridad sobre el veredicto) |
| `analyze_document_register` | `vigia.tools.adversarial_nlp` | `VIGIA_NLP_ENABLED` |
| `analyze_document_entanglement` | `vigia.tools.entanglement` | `VIGIA_ENTANGLEMENT_ENABLED` |

El playbook completo de investigación (fases, protocolo peirciano, protocolo
obligatorio de refutación, formato de reporte) está en
[`CLAUDE.md`](../CLAUDE.md).

---

## 15. Modos de despliegue, LLM y API

| Modo | Descripción | LLM |
|------|-------------|-----|
| **1 — Fallback Python** | Núcleo forense principal y evaluado. Pipeline completo, 0 tokens, sin internet | No |
| **2 — Claude Code + MCP** | Investigación peirciana interactiva con las herramientas de §14 | Sí |
| **3 — Ollama** | LLM local (`hermes3:8b`, `deepseek-r1:8b`, `gemma3:27b`); nada sale de la máquina | Sí |
| **4 — Agente batch autónomo** | Procesamiento de corpus con loop de autocorrección | Opcional |
| **5 — OpenWebUI (experimental)** | Servidor MCP vía interfaz web | Sí |

Los Modos 2–5 reutilizan las herramientas deterministas pero tienen contratos de
investigación y reporte separados: un reporte de Modo 2 nunca muta un bundle
sellado de Modo 1. Si ambos difieren, se conservan los dos con sus notas de
alcance. Mapa completo: [`EXECUTION_MODES.md`](./EXECUTION_MODES.md).

**Backend LLM.** `VIGIA_LLM_BACKEND` selecciona Anthropic API u Ollama. Sin
backend disponible, `reason_with_llm` devuelve error y las herramientas
deterministas siguen operativas: es una limitación documentada, no una falla.

**API REST (`vigia_api.py`).** Expone `POST /analyze/path`, `POST /analyze/json`
y endpoints compatibles con OpenAI (`GET /v1/models`,
`POST /v1/chat/completions`). Devuelve el veredicto del scorer determinista y
sella ese mismo payload. Como su score compuesto no es un posterior EBS
calibrado, la envoltura EBS registra `ABSTAIN` con
`STANDALONE_SCORER_UNCALIBRATED_EBS_RISK` mientras `caie_analysis` conserva el
veredicto forense; la API expone ambos para que un sello válido nunca se
presente como prueba de otra decisión. El JSON entrante se limita a 1 MiB y
1.024 artefactos; las rutas inválidas responden `404` opaco y un caso rechazado
solo por tamaño responde `422`.

**Web UI offline.** `./launch_vigia_ui.sh` levanta en `http://127.0.0.1:8010`
un navegador de bundles, un panel de verificación y un lanzador del Modo 1
(`vigia/ui/`). Ver [`INSTALL_ES.md`](../INSTALL_ES.md) §11b.

---

## 16. Verificación del propio sistema: tests, mutation testing y red team

### 16.1 Suite de regresión

La suite está organizada por modelo de amenaza: unitarios, integración, CAIE,
red team / anti-evasión, compuertas de auditoría, caracterización y casos reales.
Muchos tests llevan el número del bug que fijan (`test_b116_*`, `test_b201_*`),
de modo que cada corrección queda anclada.

```bash
PYTHONPATH=$(pwd) python3 -m pytest tests/ vigia/tests/ -v --tb=short --ignore=tests/integration
bash run_all_tests.sh
```

### 16.2 Mutation testing

La cobertura de líneas responde "¿se ejecutó esta línea?", no "¿algo notaría
si estuviera mal?". Eso último lo mide el mutation testing, que corre cada
semana (`.github/workflows/mutation.yml`, un job por módulo). La primera línea
de base encontró `vigia/collapse_decision.py` con 77,94 % de cobertura de
líneas pero 13,8 % de mutation score: el umbral de MALICE podía moverse a un
valor inalcanzable sin que fallara ningún test. Operación y diagnóstico:
[`MUTATION_RUNBOOK_ES.md`](./MUTATION_RUNBOOK_ES.md); método y alcance:
[`MUTATION_TESTING_ES.md`](./MUTATION_TESTING_ES.md); puntajes medidos:
[`MUTATION_BASELINE_ES.md`](./MUTATION_BASELINE_ES.md).

### 16.3 Red team y auditorías

| Ronda | Tema |
|-------|------|
| [Ronda 2](./REDTEAM_ROUND2_MONOTONICITY.md) | Monotonicidad del veredicto |
| [Ronda 3](./REDTEAM_ROUND3_EMERGENT.md) | Comportamiento emergente |
| [Ronda 4](./REDTEAM_ROUND4_BOUNDARIES.md) | Fronteras |
| [Ronda 5](./REDTEAM_ROUND5_DOWNGRADE.md) | Ataques de degradación |
| [Ronda 6](./REDTEAM_ROUND6_PERIMETER.md) | Perímetro del sello |
| [Ronda 7](./REDTEAM_ROUND7_PAIRING.md) | Emparejamiento de bundles |
| [Ronda 8](./REDTEAM_ROUND8_UI.md) | Web UI |
| [Ronda 9](./REDTEAM_ROUND9_EXPOSURE.md) | Exposición |
| [Ronda 10](./REDTEAM_ROUND10_RENDER_TYPES.md) | Tipos de render |
| [Ronda 11](./REDTEAM_ROUND11_PROCESS_TREE.md) | Árbol de procesos |
| [Ronda 12](./REDTEAM_ROUND12_SELF_AUDIT.md) | Autoauditoría |

Además, `docs/` conserva auditorías abductivas, de cobertura del motor, de
falsos negativos, de seguridad del veredicto sellado
([`AUDIT_SEALED_VERDICT_SECURITY.md`](./AUDIT_SEALED_VERDICT_SECURITY.md)),
auditorías externas (Codex, DeepSeek, Kimi) y registros de diseño. Se preservan
como historia del proyecto.

---

## 17. Corpus de casos y evaluación

VIGÍA se evalúa en tres dominios que **no se suman** entre sí:

- **Dominio A — Claude Code / MCP.** Investigación asistida por LLM con el mismo
  sello determinista; se evalúa caso por caso sobre evidencia raw real, no como
  cifra de corpus.
- **Dominio B — Agente sobre JSON, solo Python, 0 llamadas a LLM.**
  158/162 (97,5 %) ciego a etiqueta en el corpus de detección; 187/199 (94,0 %)
  en el corpus mixto, que incluye 31 casos adversariales (16 BREAK, 7 KIWI, 3 FN,
  5 FP) diseñados para romper el sistema. Esos 31 miden resistencia y límites
  documentados, no precisión de detección.
- **Dominio C — Agente sobre evidencia raw, solo Python, 0 llamadas a LLM.**
  43 fuentes de evidencia raw de corpus públicos con bundles sellados: SRL 2018
  (22 imágenes de memoria), MUS2019/Narcos (13 dumps), M57, NPS 2010/2014,
  Magnet CTF, Tuck 2019 macOS, Vanko, entre otras.

```bash
python3 run_all_agent.py --timeout 90   # corpus completo, ciego a etiqueta
```

Catálogos: [`RAW_CASES_LOG_ES.md`](./RAW_CASES_LOG_ES.md),
[`readme_benign_cases.md`](./readme_benign_cases.md),
[`digital_corpora_complete_report.md`](./digital_corpora_complete_report.md),
[`nist_cfreds_full_report.md`](./nist_cfreds_full_report.md). Correcciones del
corpus: [`CORPUS_CORRECTIONS.md`](./CORPUS_CORRECTIONS.md).

---

## 18. Cumplimiento Daubert

### 18.1 Criterios

*Daubert v. Merrell Dow Pharmaceuticals* (1993) fijó cuatro criterios de
admisibilidad de evidencia científica: testabilidad, revisión por pares, tasa de
error conocida y aceptación general.

| Criterio | Implementación en VIGÍA |
|----------|-------------------------|
| Testabilidad | Verificadores stdlib independientes, 22 vectores canónicos P2, suite de regresión y mutation testing |
| Revisión por pares | Colectivo de auditoría multi-IA con roles definidos, 11 rondas de red team, auditorías externas documentadas |
| Tasa de error | Métricas por dominio en `ACCURACY_ES.md`; calibración en `models/calibration_metadata.json`; fallos conocidos en `KNOWN_LIMITATIONS.md` |
| Aceptación general | MITRE ATT&CK, escala ENFSI, STIX 2.1, ISO/IEC 27037, RFC 3161 |

Fundamento completo: [`DAUBERT_JUDICIAL_ES.md`](./DAUBERT_JUDICIAL_ES.md).

### 18.2 Invariantes EBS v1

- **I1 — Determinismo:** mismo input analítico → mismo `analysis_fingerprint`.
- **I2 — Integridad encadenada:** `bundle_hash` cubre todo el contenido sellado.
- **I3 — Política verificable:** `policy_spec` es independiente del runtime.
- **I4 — Acciones explícitas:** no hay efectos implícitos.
- **I5 — Decisión explicable:** riesgo y posterior siempre presentes.

### 18.3 Protocolo obligatorio de refutación

Antes de cualquier veredicto INTENT o MALICE: formular la hipótesis de
incompetencia benigna más fuerte, contrastarla contra toda la evidencia, y
poblar el campo `devil_advocate` con la mejor defensa posible. Bajar de MALICE a
SUSPICION por refutación exitosa es el sistema funcionando bien, no una falla.

### 18.4 Amicus curiae

Las narrativas amicus curiae distinguen hallazgos confirmados (evidencia técnica
directa), hallazgos inferidos (abducción con condiciones de refutación) e
incertidumbres documentadas (zonas de abstención). Hay ejemplos sellados en
`results/` y `evidence/`.

---

## 19. Limitaciones conocidas y trabajo abierto

### 19.1 Limitaciones

[`KNOWN_LIMITATIONS.md`](../KNOWN_LIMITATIONS.md) documenta 70 limitaciones (L-001 a L-073) con su
estado (abierta, mitigada, resuelta). Es lectura obligatoria para el alcance
Daubert. Ejemplos de limitaciones abiertas recientes:

- **L-071:** la compuerta cross-domain cuenta presencia de dominio, no masa: un
  artefacto casi nulo puede pivotear SUSPICION→MALICE.
- **L-072:** una etiqueta declarada de `semantic_role` puede neutralizar MALICE.
- **L-073:** una comparación de umbral float contra `Fraction` en un punto
  exacto de la grilla otorga el escalón superior (latente, incidencia cero en el
  corpus).

### 19.2 Trabajo abierto

La fuente de verdad es [`BUGS_PENDIENTES.md`](../BUGS_PENDIENTES.md)
([EN](../BUGS_PENDIENTES_EN.md)). Ítems abiertos al 7 de octubre de 2026:

| Bug | Tema |
|-----|------|
| B-010 | Migración de `forensic_technical_detector.py` a `SemioticDetectorV2` (premisa refutada por medición, espera cierre formal) |
| B-111 | Modo 3 (Ollama) no confiable en evidencia testimonial densa (estocástico) |
| B-112, B-113 | Candidatos de catálogo CAIE: auto-incriminación y rechazo institucional |
| B-116 | `signal_quality_gate.py` diseñado y probado, no cableado al scorer |
| B-123, B-124 | Compuertas de cierre causal y de gobernanza diseñadas y probadas, no cableadas |
| B-129 | PeircePlanner acotado: fase 2 pendiente |
| B-162 | Adaptador legado: reparación parcial |

Las tablas de roadmap de [`WHAT_IS_NEXT.md`](./WHAT_IS_NEXT.md) son históricas.

---

## 20. Bibliografía y referencias técnicas

**Semiótica y filosofía**
- Peirce, C. S. (1931–1958). *Collected Papers*. Harvard University Press.
- Eco, U. (1990). *The Limits of Interpretation*. Indiana University Press.
- Grice, H. P. (1975). "Logic and Conversation". *Syntax and Semantics* 3.
- Carnegie, D. (1936). *How to Win Friends and Influence People*.

**Forense digital**
- Casey, E. (2011). *Digital Evidence and Computer Crime* (3.ª ed.).
- Carrier, B. (2005). *File System Forensic Analysis*.

**Marcos forenses**
- MITRE ATT&CK Enterprise: https://attack.mitre.org
- ENFSI Guideline for Evaluative Reporting in Forensic Science (2015).
- OASIS STIX 2.1 Specification.
- ISO/IEC 27037:2012 — Digital Evidence Handling.
- RFC 3161 — Internet X.509 PKI Time-Stamp Protocol.

**Estándares judiciales**
- *Daubert v. Merrell Dow Pharmaceuticals*, 509 U.S. 579 (1993).
- *Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999).
- *Frye v. United States*, 293 F. 1013 (D.C. Cir. 1923).

**Matemática y estadística**
- Ledoit, O. y Wolf, M. (2004). "A well-conditioned estimator for large-dimensional covariance matrices".
- Bandt, C. y Pompe, B. (2002). "Permutation entropy". *Physical Review Letters*.
- Lempel, A. y Ziv, J. (1976). "On the complexity of finite sequences". *IEEE Transactions on Information Theory*.
- Meinshausen, N. y Bühlmann, P. (2010). "Stability selection". *JRSS-B*.

**Implementación**
- FastMCP / Model Context Protocol.
- Volatility 3 — The Volatility Foundation.
- Plaso / log2timeline.

---

*"Si un sistema afirma MALICE sin poder explicarlo con matemática exacta, no es
forense: es adivinación."* — VIGÍA

*Historial: v1.0 (2026-05-18) dossier técnico original, preservado en el
historial de git; v2.0 (2026-10-07) reescritura con cifras medidas sobre el
repositorio.*
