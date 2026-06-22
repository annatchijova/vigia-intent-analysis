# VIGIA — Informe de Síntesis de Investigación (AI Collective)

<!-- Generado por: Kimi K2 Agent Swarm (Moonshot AI) -->
<!-- Corrección y verificación contra repositorio en vivo: Claude (Anthropic), Colectivo VIGIA AI -->
<!-- Corrección 2026-06-22: separación de métrica modo agente (vigia_agent.py) vs modo Python (run_all_cases.py / pipeline determinista). Ver §7.1.4 y §9.3.2 (CZ-01, resuelto). -->
<!-- English version: VIGIA_RESEARCH_REPORT_EN.md -->

---

## 1. Introducción: VIGIA y la Nueva Frontera del Análisis de Intencionalidad Forense

### 1.1 El Problema: Limitaciones del DFIR Tradicional

El 22 de febrero de 2026, Rob T. Lee, Chief AI Officer del SANS Institute, pronunció dos palabras ante su laptop en la RSAC: *find evil*. Catorce minutos y veintisiete segundos después, un agente autónomo construido sobre SIFT Workstation había completado un análisis forense de disco C: que, según respondedores de incidentes, suele llevar una semana o más [^42^]. Esa demostración no fue solo una proeza técnica — fue un diagnóstico brutal de una profesión en crisis.

El **DFIR** (*Digital Forensics and Incident Response*, Forense Digital y Respuesta a Incidentes) tradicional ha operado durante décadas bajo un paradigma insuficiente: pregunta *qué* ocurrió, pero rara vez *por qué* la evidencia se ve como se ve. Cuando un analista examina logs o procesos en memoria, interpreta artefactos sin interrogar las decisiones deliberadas que los produjeron. Esa omisión no es académica — es estructuralmente explotable.

La crisis se manifiesta en cifras contundentes. El *Global Threat Report 2026* de CrowdStrike revela que el **82% de las detecciones en 2025 fueron *malware-free*** — ataques que operaron exclusivamente mediante técnicas **LotL** (*Living Off the Land*, uso de herramientas legítimas del sistema para fines maliciosos) [^838^]. El *Picus Blue Report 2025* confirma que las organizaciones detectan apenas **1 de cada 7 ataques simulados** (~14%) [^810^]. El tiempo de *breakout* — entre infiltración y movimiento lateral — se ha reducido a **29 minutos**, con un récord de 27 segundos [^836^].

Detrás de estos números yace la **crisis de confianza en los EDR** (*Endpoint Detection and Response*, sistemas de detección y respuesta en endpoints). Los EDR comerciales operan como **cajas negras** — modelos de aprendizaje automático opacos, umbrales flotantes no deterministas, e incapacidad para explicar sus clasificaciones — lo que los hace vulnerables a evasión y exclusión judicial [^769^]. Un estudio en DEF CON 32 demostró que el **94% de las soluciones EDR analizadas carecen de *hooks* en la capa por encima de NTDLL**, dejando una brecha arquitectónica sistémica [^821^]. La evasión de EDR se ha convertido en **commodity**: herramientas como AuKill y EDRKillShifter se venden por **$300** en foros subterráneos [^782^], mientras que LACUNA Chain demostró en junio de 2026 un *bypass* completo de detección basada en *call-stack* [^799^].

Las técnicas **anti-forenses** han evolucionado desde el borrado de logs hacia la fabricación sofisticada de artefactos. Grupos **APT** (*Advanced Persistent Threat*) como Lazarus y Sandworm no solo ocultan evidencia — la plantan para engañar [^822^][^783^]. El caso **Olympic Destroyer** (2018) encapsula esta realidad: atacantes rusos imitaron tan convincentemente las TTPs (*Tactics, Techniques, and Procedures*) de Lazarus que los investigadores atribuyeron inicialmente el ataque a Corea del Norte [^783^]. Cuando la evidencia misma miente, preguntar solo *qué* pasado ya no basta.

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Detecciones *malware-free* (2025) | 82% | CrowdStrike GTR 2026 [^838^] |
| Ataques simulados no detectados | ~86% (6/7) | Picus Blue Report 2025 [^810^] |
| Tiempo de *breakout* promedio | 29 minutos | CrowdStrike GTR 2026 [^836^] |
| Precio mínimo de *EDR killer* | $300 USD | Foros underground [^782^] |
| EDR con ciegos NTDLL | 94% | DEF CON 32 [^821^] |
| Ataques con IA habilitados (YoY) | +89% | CrowdStrike GTR 2026 [^835^] |

### 1.2 VIGIA: Visión y Propuesta de Valor

**VIGIA** (*Virtual Intent-Guided Inference Analyzer*) es un motor de inferencia abductiva determinista que evalúa las **fracturas lógicas en la mentira**. Su principio fundacional: *Hoy, mentir en un log o falsificar un ataque es gratis. VIGIA cobra ese precio evaluando las fracturas lógicas en la mentira* [^853^].

La distinción arquitectónica clave es el **aislamiento del LLM** del pipeline de veredicto: *los veredictos se sellan antes de que cualquier LLM* (*Large Language Model*, modelo de lenguaje grande) *vea la evidencia*. El motor opera con aritmetica entera exclusiva usando `fractions.Fraction` y SHA-256 para integridad; los LLMs participan únicamente en narrativa post-veredicto. Este diseño responde a una lección empírica: el caso **BREAK-012** documentó cómo un LLM alteró incorrectamente un veredicto de BENIGNO a MALICIA al acceder a datos antes del sellado [^854^].

VIGIA mide **spoofability** — qué tan fácil es falsificar cada tipo de evidencia. La geolocalización por IP tiene *spoofability* 0.90 (fácilmente falsificable); un proceso en memoria tiene 0.15 (estructuralmente irrefutable) [^853^]. La filosofía operativa se resume así: **hacer la decepción computacionalmente costosa para el atacante** [^853^]. Los *Indicadores de Intención* (**IoI**, *Indicators of Intent*) reemplazan a los tradicionales *Indicadores de Compromiso* (**IoC**, *Indicators of Compromise*).

| Dimensión | DFIR Tradicional | VIGIA |
|-----------|-----------------|-------|
| **Pregunta central** | ¿Qué ocurrió? | ¿Por qué la evidencia se ve así? ¿Quién se beneficia? |
| **Unidad de análisis** | IoC (hash, IP, firma) | IoI (inconsistencia intencional, fractura narrativa) |
| **Detección de LotL** | Limitada — requiere firmas de comportamiento | Nativa — "procesos conocidos haciendo cosas desconocidas" [^853^] |
| **Resistencia a *false flags*** | Baja — correlaciona artefactos aislados | Alta — CAIE detecta incongruencias cross-artifact [^853^] |
| **Determinismo** | No garantizado | Garantizado bit-a-bit — `fractions.Fraction` + SHA-256 [^853^] |
| **Transparencia** | EDRs de caja negra, algoritmos propietarios | Código abierto Apache 2.0, verificador con stdlib únicamente |
| **Modo offline** | Funcionalidad reducida | Modo 0 tokens — operación completa sin LLM ni internet [^225^] |
| **Filosofía ante incertidumbre** | Forzar clasificación binaria | ABSTAIN como veredicto válido y epistemológicamente correcto [^854^] |

### 1.3 Contexto del Desarrollo

VIGIA fue construido para el **SANS FIND EVIL Hackathon 2026**, el primer hackathon de agentes autónomos DFIR, con 4,178+ participantes y $22,000 USD en premios [^40^][^41^]. El desafío: transformar **Protocol SIFT** — la iniciativa de Rob T. Lee para conectar LLMs con 500+ herramientas forenses mediante **MCP** (*Model Context Protocol*) de Anthropic [^55^] — en un agente DFIR autónomo capaz de pensar como un analista senior y auto-corrigirse [^41^].

El proyecto fue dirigido por **Anna Tchijova**, cocinera profesional de origen ruso residente en Argentina sin formación formal en IT, quien orquestó un **AI Collective** de 7 LLMs con roles especializados: Claude (integración), Gemini (marco teórico IoI), Kimi (sistemas forenses), DeepSeek (auditoría de seguridad), Qwen (hardening), Grok (arquitectura de *scoring*) y ChatGPT (red team adversarial) [^222^][^225^]. El desarrollo siguió ciclos de debate, escritura de código y auditoría competitiva entre modelos [^225^].

El presente informe investiga el repositorio *vigia-intent-analysis* sintetizando hallazgos de 10 dimensiones independientes, 250+ búsquedas web, análisis de código fuente y revisión de literatura académica en filosofía de la ciencia, semiótica, inteligencia artificial, forense digital y derecho.

> *Caso de ejemplo — CAN-031: Weaponized Incompetence.* Un actor ejecuta PowerShell para eliminar *shadow copies* y desactivar el firewall con cero errores de sintaxis. Sesenta y tres segundos después, genera un ticket de IT: "mi pantalla parpadeó, soy inútil con computadoras". El investigador tradicional ve incompetencia accidental. VIGIA detecta la fractura: la ausencia de errores en comandos destructivos contradice la narrativa de incompetencia, y el *timing* de 63 segundos es estadísticamente anómalo. El **CAIE** (*Cross-Artifact Incongruence Engine*, motor de incongruencia cross-artefacto) computa la discrepancia entre comportamiento técnico perfecto y narrativa fingida, elevando el veredicto a MALICIA [^853^].

Este informe examina cómo VIGIA transforma la forense digital de disciplina de catalogación a inferencia intencional determinista — y por qué esa transición es obligatoria en un panorama donde el 82% de las amenazas no dejan rastro de malware y los *EDR killers* cuestan menos que una entrada de cine.
## 2. Fundamentos Teoricos: Del Razonamiento Abductivo de Peirce a la Semiotica Forense

### 2.1 Charles Sanders Peirce y las Tres Categorias Ontologicas

#### 2.1.1 Firstness, Secondness, Thirdness Aplicadas a Evidencia Digital

Charles Sanders Peirce (1839–1914) construyo su sistema filosofico sobre tres categorias fenomenologicas irreductibles entre si: Firstness, Secondness y Thirdness. Este armazon ontologico sostiene toda su semiotica y su logica del descubrimiento cientifico [^1^], y constituye el fundamento sobre el cual VIGIA erige su arquitectura de inferencia —no como metafora, sino como estructura de datos ejecutable [^2^].

Firstness designa la cualidad pura, la inmediatez no mediada. Peirce la define como aquello cuyo ser "is simply in itself... a kind of unmediated meditative state without unity and without parts, it just 'is'" [^3^]. Relacionalmente, equivale a predicados monadicos —propiedades que un ente posee sin referencia a otro [^4^]. En forense digital, Firstness se manifiesta en el dato bruto: un timestamp, un hash, una entrada de registro. Son *qualia* digitales que existen como mera presencia antes de cualquier interpretacion.

Secondness es la categoria del hecho, la existencia, la resistencia: "the knock on the door which interrupts the musical reverie; it is the unexpected rear-end collision" [^5^]. Relacionalmente, corresponde a predicados diadicos que exigen dos correlatos: accion-reaccion, causa-efecto [^4^]. En evidencia digital, Secondness emerge cuando dos artefactos entran en relacion —un timestamp contradice a otro, un registro de proceso es inconsistente con un log de red, la memoria volatile refuta la narrativa del almacenamiento persistente.

Thirdness es la categoria de la ley, el habito, la mediacion. Peirce la ilustra: "Tycho Brahe's recorded observations of the positions of the planet Mars at given times are seconds. Kepler's laws, worked out to unify that body of data, are thirds" [^6^]. Relacionalmente, requiere predicados triadicos —sujeto, objeto, interpretante— en un acto de semiosis [^4^]. En forense digital, Thirdness corresponde a la hipotesis explicativa que unifica artefactos incongruentes: la atribucion de intencionalidad, la reconstruccion de la cadena de ataque.

Peirce sostuvo la irreductibilidad estricta de Thirdness: "I will sketch a proof that the idea of meaning is irreducible to those of quality and reaction... a triadic relation is inexpressible by means of dyadic relations alone" [^7^]. Esta tesis tiene consecuencias directas para la arquitectura de sistemas de inferencia: una hipotesis explicativa no puede reducirse a la suma de datos mas sus correlaciones, justificando la existencia de un motor de abduccion como componente independiente.

**Diagrama 2.1: Jerarquia Ontologica Peirce–VIGIA (descripcion textual)**

El diagrama representa una piramide de tres niveles con flechas de inclusion que indican irreductibilidad. En la base (Nivel 1), Firstness se representa como nodos aislados hexagonales etiquetados *Artifact* (timestamp, hash, registry entry). En el nivel intermedio (Nivel 2), Secondness aparece como flechas diadicas etiquetadas *CAIE* que conectan pares de nodos del nivel inferior —por ejemplo, *timestamp_A* con *timestamp_B* bajo la etiqueta *TEMPORAL_CAUSALITY_VIOLATION*. En la cuspide (Nivel 3), Thirdness se materializa como una elipse *AbductiveHypothesis* que agrupa flechas del nivel 2 bajo una narrativa unificadora (por ejemplo: *log_fabrication*). Flechas punteadas descendentes desde Thirdness indican que la hipotesis genera predicciones testables via el campo *what_would_falsify*. Barras diagonales etiquetadas "irreducible" bloquean la reduccion de Nivel 3 a Nivel 2+1, materializando la tesis peirceana sobre la irreductibilidad de la triadicidad.

#### 2.1.2 La Triada Inferencial: Abduccion, Deduccion, Induccion en Investigacion Forense

Peirce articulo que la investigacion cientifica completa requiere tres inferencias mutuamente irreductibles. La abduccion adopta la hipotesis explicativa ante hechos sorprendentes; la deduccion deriva sus consecuencias observables; la induccion las somete a prueba empirica [^8^]. El investigador forense reproduce este ciclo: observa un artefacto anomalo, formula un escenario de ataque, predice que evidencia corroboraria ese escenario, y verifica esas predicciones contra el corpus disponible [^9^].

| Fase Inferencial | Definicion Peirce | Implementacion Forense | Funcion en VIGIA |
|---|---|---|---|
| **Abduccion** | Sugerencia de hipotesis que explica lo observado [^8^] | Generacion de hipotesis explicativas a partir de artefactos anomalos | `AbductiveIntentEngine.infer()` — produce hipotesis con artefactos requeridos y asumidos |
| **Deduccion** | Trazado de consecuencias experienciales probables [^8^] | Especificacion de condiciones de falsificacion | Campo `what_would_falsify` — prediccion de datos que invalidarian la hipotesis |
| **Induccion** | Prueba experimental de la hipotesis [^8^] | Evaluacion empirica via scoring entero y falsificacion activa | Motor de scoring + Devil's Advocate — verificacion inductiva contra la evidencia |

La tabla sintetiza la triada inferencial peirceana con su implementacion en VIGIA. El campo `what_would_falsify` provee el mecanismo deductivo para descartar alternativas; el *Devil's Advocate* cierra el ciclo mediante contra-argumentos que pueden reiniciar la abduccion. Esta integridad triadica es epistemologicamente critica: un sistema que solo genera hipotesis sin especificar condiciones de falsificacion carece de rigor cientifico; uno que solo prueba sin generar hipotesis nuevas es puramente confirmatorio.

### 2.3 Lorenzo Magnani y la Cognicion Abductiva

#### 2.3.1 Abduccion Teorica vs. Manipulativa en el Marco de Magnani

Lorenzo Magnani (Universita di Pavia) desarrollo la extension sistematica mas citada de la abduccion peirceana contemporanea. Su monografia *Abductive Cognition* (2009), con 757 citas en Google Scholar, constituye el puente teorico entre semiotica clasica y arquitecturas computacionales [^10^].

Magnani distingue dos formas fundamentales. La abduccion teorica tiene como objetivo "selecting and creating a set of hypotheses that are able to dispense good (preferred) explanations of data" [^11^], subdividiendose en sentencial (proposicional) y model-based (representaciones internas no sentenciales). La abduccion manipulativa captura "the role of action in many interesting situations: action provides otherwise unavailable information that enables the agent to solve problems by starting and performing a suitable abductive process" [^11^]. En terminos magnanianos: "Manipulative abduction happens when we are thinking through doing and not only, in a pragmatic sense, about doing" [^12^]. Un concepto clave es el mediador epistemico: objetos externos —diagramas, instrumentos, estructuras de datos computacionales— que al ser manipulados activamente revelan propiedades inaccesibles para la abduccion puramente teorica [^11^].

#### 2.3.2 "Inference to the Best Explanation" de Harman y Lipton como Fundamento

La formulacion contemporanea de la abduccion como *Inference to the Best Explanation* (IBE) proviene de Gilbert Harman (1965): la inferencia "from the fact that a certain hypothesis would explain the evidence, to the truth of that hypothesis" [^13^]. Peter Lipton desarrollo esta teoria en *Inference to the Best Explanation* (1991; 2da ed. 2004), introduciendo la distincion entre *loveliest explanation* —la que provee mayor comprension— y *likeliest explanation* —la mas probable [^14^]. Lipton argumento que "the explanation that would, if true, provide the deepest understanding is the explanation that is likeliest to be true" [^14^], identificando las "virtudes explicativas" que caracterizan a la mejor explicacion: mecanismo, precision, alcance, simplicidad, fertilidad y unificacion [^15^].

La objecion mas citada contra IBE proviene de Bas van Fraassen: la inferencia solo concluye que una hipotesis es "la mejor de un mal lote" (*best of a bad lot*), no que sea verdadera [^16^]. Lipton respondio que IBE solo recomienda la hipotesis ganadora si es "suficientemente buena" [^17^]; Schupbach (2014) considero la objecion "misguided" por confundir el proposito de la inferencia [^18^]. VIGIA responde computacionalmente via el campo `what_would_falsify`, que establece un criterio de suficiencia independiente de la comparacion con alternativas, y via el *Devil's Advocate*, que explora activamente el espacio de hipotesis no formuladas.

### 2.4 Aplicacion a VIGIA: Semiotica Computacional

#### 2.4.1 Materializacion de Peirce en Clases Python

VIGIA implementa las tres categorias ontologicas peirceanas como estructuras de datos con correspondencia filosofica explicita. `Artifact` materializa Firstness —dato forense bruto sin interpretacion. CAIE (*Cross-Artifact Incongruence Engine*) implementa Secondness —relaciones diadicas entre artefactos que detectan incongruencias. `AbductiveHypothesis` concreta Thirdness —narrativa explicativa que unifica artefactos mediante atribucion de intencionalidad [^19^]. El motor de scoring implementa IBE de manera determinista: `scored.sort(key=lambda h: (h.cost, -h.coverage_score))` selecciona la hipotesis con menor costo (menos supuestos no observados, navaja de Ockham operacionalizada) y mayor cobertura (mas datos explicados) [^20^]. La distincion magnaniana tambien tiene correlato arquitectonico: el motor `_score_hypothesis()` opera sentencialmente; las clases `AbductiveHypothesis` contienen modelos internos (model-based); el *Devil's Advocate* y CAIE implementan abduccion manipulativa al transformar activamente la estructura de hipotesis durante la inferencia [^21^].

#### 2.4.2 Grice Maxims Aplicados a Evidencia Forense

H. Paul Grice (1975) propuso el Principio Cooperativo con cuatro maximas: Cantidad (aporta la informacion requerida), Calidad (no digas lo falso), Relacion (se relevante) y Modo (evita oscuridad) [^22^]. Hobbs establecio la conexion con la abduccion: "an implicature can be viewed as an abductive move for the sake of achieving the best interpretation" [^23^]. En forense digital, la violacion de Cantidad se manifiesta en logs excesivamente detallados (*staging*) o con informacion insuficiente (*tampering*). La violacion de Calidad emerge cuando timestamps se contradicen mutuamente o registros carecen de corroboracion. VIGIA detecta estas violaciones operacionalmente: el `coverage_score` mide Cantidad; CAIE detecta inconsistencias (Calidad); el pattern-matching mide Relacion; y la deteccion de *excessive digital perfection* identifica evidencia sospechosamente ordenada (Modo) [^24^].

#### 2.4.3 La Semiotica Forense como Disciplina Emergente

La convergencia entre semiotica y forense digital consolida una disciplina academica interdisciplinaria. Leone analizo los artefactos forenses como signos triadicos peirceanos con dimension iconica, indexical y simbolica [^25^]. Danesi sistematizo la semiotica forense argumentando que "semiotics and crime detection are 'two sides of the same cognitive (inference-based) coin'... clues are signs that require interpretation" [^26^]. Crispino propone reformar la ciencia forense desde sus fundamentos: "a trace is not merely a tangible object; it is a sign that requires recognition and interpretation... Peirce's semiotics enhances this quantitative methodology by incorporating the examination of meanings and contexts into the evaluation of the probative value of forensic evidence" [^27^], enfatizando que "all inferences are interpretive... without incorporating the human element, technical quality alone is inadequate" [^28^]. Sorensen, Thellefsen y Thellefsen han analizado las pistas como informacion y el "semiotic gap" en procesos investigativos [^29^]. VIGIA se situa en este contexto como la primera implementacion computacional a escala de estos principios: cada `Artifact` es un signo peirceano, cada `AbductiveHypothesis` es un interpretante, y el motor completo constituye una maquina de semiosis forense que opera bajo principios semioticos explicitos en lugar de heuristicas ad-hoc.
## 3. Arquitectura Tecnica y Motor de Inferencia

### 3.1 Estructura del Sistema

#### 3.1.1 Organizacion Modular

VIGIA se organiza en seis modulos funcionales que reflejan una separacion de responsabilidades alineada con el ciclo de respuesta a incidentes: `engine/` aloja el nucleo inferencial; `vigia/` contiene los componentes de analisis de intencion, incluyendo `abductive_intent_engine.py` (~1.133 lineas) y `core/decision_layer.py`; `forensics/` gestiona la adquisicion y preservacion de evidencia; `evidence/` implementa la cadena de custodia HMAC-SHA256; `models/` define las estructuras de datos inmutables (EBS v1); y `governance/` especifica el Protocolo P2 de determinismo. Esta particion no es meramente cosmética: el modulo `models/` opera bajo la regla absoluta "This module contains DATA ONLY" [^1^], eliminando toda logica de negocio de la capa inmutable y garantizando que los bundles de evidencia sean interpretables sin ejecutar codigo de produccion.

#### 3.1.2 Componentes Principales

Los cuatro componentes que constituyen el pipeline critico son: *AbductiveIntentEngine* (motor de generacion y seleccion de hipotesis), *CAIE* (*Cross-Artifact Incongruence Engine*, detector de fracturas forenses), *Devil's Advocate* (generador determinista de falsificaciones abductivas), y *DecisionLayer* (capa de arbitraje de veredictos). La relacion entre ellos sigue un flujo estrictamente secuencial: el motor propone, CAIE verifica la coherencia entre fuentes, el Devil's Advocate intenta refutar, y la capa de decision emite el veredicto final. A continuacion se comparan sus funciones, fundamentos teoricos y archivos fuente.

| Componente | Funcion Principal | Fundamento Teorico | Archivo Fuente | Lineas (aprox.) |
|---|---|---|---|---|
| AbductiveIntentEngine | Generar y seleccionar hipotesis por costo/cobertura | Semiotica de Peirce + Ockham's Razor | `abductive_intent_engine.py` | ~1.133 |
| CAIE | Detectar fracturas entre artefactos cruzados | Teoria de la informacion + Golden Forensic Rules | `tools/caie.py` | ~1.800 |
| Devil's Advocate (R7) | Componer falsificaciones abductivas deterministas | Eco's Razor (falsificacion abductiva) | `core/devil_advocate_gen.py` | ~200 |
| DecisionLayer | Arbitraje de 4-8 estados con umbrales en Fraction | Inferencia contrastiva (Lipton) + Criterio Daubert | `core/decision_layer.py` | ~300 |

La asimetria en el tamano de los modulos es significativa. CAIE, con ~1.800 lineas, es el componente mas extenso porque debe evaluar 17 perfiles de evidencia y 9 reglas de fractura contra cada hipotesis candidata. Por el contrario, el Devil's Advocate (~200 lineas) opera bajo la restriccion deliberada de "No LLM on this path" [^2^], delegando la complejidad narrativa a la capa posterior. Esta distribucion refleja un principio de diseño central: el determinismo se logra mediante la contencion, no la expansion.

#### 3.1.3 Flujo del Pipeline

El pipeline completo se describe como una secuencia de cinco etapas. Primero, los artefactos forenses se encapsulan como instancias de `Artifact`, cada uno con un identificador ("A001", "A002"), una categoria (`VariableCategory`: temporal, process, network, persistence, auth, data, evasion, ioc) y un valor observado. Segundo, `AbductiveIntentEngine.infer()` carga los templates de hipotesis correspondientes a la fase MITRE detectada y calcula el costo Ockham y la cobertura para cada candidata. Tercero, CAIE evalua las fracturas entre los artefactos que soportan la hipotesis lider aplicando las *Golden Forensic Rules* y ajusta los scores mediante la formula `adjusted_score = raw_score * (1 - spoofability) * weight` [^3^]. Cuarto, el Devil's Advocate genera una narrativa de falsificacion basada en las senales faltantes del *CasePatternLibrary*. Quinto, `RiskBoundedDecisionLayer` clasifica el resultado en uno de cuatro niveles (LOW, MEDIUM, HIGH, CRITICAL) utilizando umbrales definidos como fracciones exactas de Python: `Fraction(15, 100)`, `Fraction(30, 100)`, `Fraction(60, 100)` [^4^].

### 3.2 El Motor Abductivo: AbductiveIntentEngine

#### 3.2.1 Ockham's Razor Operacionalizado

El motor implementa la abduccion peirceana como un proceso computacional de tres fases fenomenologicas: *Primeridad* (el dato bruto observado, materializado en la clase `Artifact`), *Segundidad* (las correlaciones entre artefactos, evaluadas por CAIE), y *Terceridad* (la ley o habito explicativo, instanciada en `AbductiveHypothesis`) [^5^]. La seleccion de la hipotesis ganadora opera bajo el principio de Ockham's Razor traducido a una metrica computable: el *costo* se define como el numero de supuestos no observados (`len(missing_required) + len(assumed_artifacts)`), y la *cobertura* como el porcentaje entero de artefactos requeridos que efectivamente se observaron (`(len(observed_required) * 100) // len(required_artifacts)`) [^6^].

El algoritmo de ordenacion es determinista y utiliza una tupla lexicografica: `scored.sort(key=lambda h: (h.cost, -h.coverage_score))` [^7^]. Esta linea encapsula la logica completa del motor: primero minimizar el costo (supuestos no observados), y en caso de empate, maximizar la cobertura (datos explicados). La ausencia de punto flotante no es accidental. El comentario en el docstring declara: "Costo Ockham = conteo entero (no float). Cobertura = porcentaje entero (no float)" [^8^]. Esta decision de diseño elimina la deriva numerica que afecta a los sistemas basados en aritmetica de coma flotante IEEE-754, cuyas limitaciones quedaron expuestas en incidentes como el Pentium FDIV ($475 millones), el misil Patriot (28 fallecidos) y el cohete Ariane 5 ($370 millones).

#### 3.2.2 Las 32 Plantillas de Hipotesis en 11 Fases MITRE ATT&CK

El motor dispone de 32 templates de hipotesis distribuidas en 11 fases del framework MITRE ATT&CK. Cada template define los artefactos requeridos, los artefactos asumidos (que incrementan el costo si no se observan), el tipo de intencion, y un criterio de falsificacion explícito (`what_would_falsify`), este ultimo critico para la admisibilidad bajo el criterio Daubert de testabilidad. La distribucion no es uniforme: las fases de mayor prevalencia en incidentes reales (PERSISTENCE, DEFENSE_EVASION, CREDENTIAL_ACCESS) reciben 3 templates cada una, mientras que LATERAL_MOVEMENT y EXFILTRATION disponen de 1 cada una, reflejando la naturaleza transversal de estas tecnicas. Las fases DISCOVERY y CLEANUP no cuentan con templates propios; la primera es inherentemente transversal a todas las demas, y la segunda es post-incidente.

#### 3.2.3 Scoring con Enteros: Aritmetica Fraction para Determinismo Absoluto

La garantia de determinismo bit-a-bit se materializa en tres mecanismos interconectados. El motor abductivo utiliza aritmetica entera exclusiva para todos los calculos de scoring. Los umbrales de la capa de decision emplean `fractions.Fraction`, que representa racionales exactos sin perdida de precision: `HIGH_CONFIDENCE_THRESHOLD = Fraction(4, 5)` (80 %) y `MEDIUM_CONFIDENCE_THRESHOLD = Fraction(3, 5)` (60 %) [^9^]. CAIE, que opera en un dominio donde se requieren decimales, utiliza `decimal.Decimal` con precision fija: `getcontext().prec = 28` y redondeo `ROUND_HALF_EVEN` [^10^]. El resultado de cada inferencia incluye un hash SHA-256 reproducible: `result_hash = hashlib.sha256(json.dumps(result_dict, sort_keys=True).encode()).hexdigest()` [^11^]. Mismo input, misma hipotesis ganadora, mismo hash en cualquier maquina.

### 3.3 Cross-Artifact Incongruence Engine (CAIE)

#### 3.3.1 Nueve Reglas de Fractura Forense (Golden Forensic Rules)

CAIE es el modulo de mayor extension (~1.800 lineas) y funcion mas compleja del sistema. Disenado por Kimi (Moonshot AI) e implementado por Claude (Anthropic), detecta fracturas logicas entre fuentes de evidencia mediante 9 reglas con severidades documentadas. La regla `TEMPORAL_CAUSALITY_VIOLATION` recibe la maxima severidad (1.0) porque un efecto anterior a su causa invalida secuencialmente toda la cadena de inferencia. Las reglas `LOG_VS_MEMORY` (0.9) y `DOCUMENT_FORGERY` (0.9) identifican las contradicciones mas frecuentes en casos de anti-forense, mientras que `TIMESTAMP_PRECISION_ANOMALY` (0.95) detecta especificamente la firma de herramientas de *timestomping* como la suite Metasploit [^12^].

#### 3.3.2 Tabla de Spoofability de 17 Tipos de Evidencia

CAIE asigna a cada tipo de evidencia un coeficiente de *spoofability* (probabilidad de ser falsificado convincentemente) y un peso que refleja su valor probatorio. La matriz cubre un rango de 0.05 (evidencia criptograficamente anclada) a 0.90 (metadatos de red trivialmente modificables).

| Tipo de Evidencia | Spoofability | Peso | Razon del Valor |
|---|---|---|---|
| ip_geolocation | 0.90 | 0.15 | VPN/proxy anonimizan origen sin traza local |
| cultural_marker | 0.90 | 0.15 | Lenguaje y keyboard layout son seleccionables |
| log_entry | 0.85 | 0.15 | Syslog/eventlog escribible por administrador |
| user_agent | 0.85 | 0.15 | Header HTTP modificable en cualquier request |
| file_timestamp | 0.70 | 0.20 | Comando `touch` o APIs de sistema alteran mtime/atime |
| registry_key | 0.55 | 0.20 | Windows Registry escribible con privilegios elevados |
| file_hash | 0.50 | 0.25 | SHA-256 verifica contenido pero no contexto |
| prefetch | 0.25 | 0.28 | Superfetch gestionado por el OS; requiere compromiso previo |
| usn_journal | 0.20 | 0.30 | NTFS USN journal accesible solo a nivel kernel |
| memory_process | 0.15 | 0.30 | Memoria volatil requiere compromiso en ejecucion |
| lsass_session | 0.15 | 0.30 | Credenciales derivadas criptograficamente |
| kernel_structure | 0.10 | 0.35 | EPROCESS/ETHREAD en espacio de direcciones kernel |
| digital_signature | 0.10 | 0.40 | PKI requiere compromiso de clave privada de CA |
| timestamp_precision | 0.05 | 0.40 | Precision sub-segundo como firma de herramienta |
| hmac_audit_log | 0.05 | 0.40 | Log encadenado con HMAC; requiere clave de integridad |
| hardware_serial | 0.05 | 0.40 | Numeros de serie requieren acceso fisico al dispositivo |
| mft_entry | 0.05 | 0.42 | Numero de entrada MFT asignado por driver NTFS |
| cryptographic_hash | 0.05 | 0.45 | Hash con base de datos known-good; colision computacionalmente infactible |

La tabla revela una jerarquia de confianza forense que no coincide con la jerarquia de recoleccion tradicional. Los investigadores suelen priorizar logs de eventos por su volumen y accesibilidad, pero estos tienen una spoofability de 0.85, apenas superior a los metadatos de red. Por el contrario, las estructuras de kernel (`kernel_structure`, 0.10) y los registros MFT (`mft_entry`, 0.05) ofrecen confianza sustancialmente mayor aunque su extraccion requiere herramientas especializadas. CAIE opera como un optimizador de recoleccion implicito: al ajustar los scores mediante `(1 - spoofability)`, penaliza las hipotesis soportadas principalmente por evidencia de bajo costo de falsificacion [^13^].

#### 3.3.3 Modelo Noisy-OR y Infinity Guard contra Score Poisoning

CAIE implementa dos mecanismos de proteccion contra manipulacion adversarial del scoring. El modelo *Noisy-OR* previene los *flood attacks* donde una unica herramienta genera multiples alertas para dominar el veredicto: `group_score = 1 - prod(1 - score_i)` dentro de cada grupo de evidencia dependiente, y `composite = 1 - prod(1 - group_j)` entre grupos independientes [^14^]. Este modelo satura el score agregado conforme crece el numero de alertas correlacionadas, evitando que 100 alertas de la misma fuente produzcan un veredicto distorsionado. Complementariamente, el *Infinity Guard* protege contra *score poisoning*: todo valor numerico pasa por `math.isfinite()` antes de ser incorporado al calculo. Si un atacante inyecta `float('inf')`, `float('-inf')` o `float('nan')`, el artefacto se anula y el sistema dispara una alerta `FORENSIC_POISONING_ATTEMPT` [^15^].

### 3.4 Devil's Advocate y el Sistema de Validacion

#### 3.4.1 Generacion Determinista de Falsificaciones Abductivas (R7)

El Devil's Advocate (regla R7) implementa la *Navaja de Eco* (Eco's Razor): la falsificacion abductiva como contrapeso sistematico a la generacion de hipotesis. Aprobado por voto del Colectivo VIGIA el 19 de junio de 2026, su diseno excluye deliberadamente a los LLMs del camino critico [^16^]. El compositor `compose_devil_advocate_struct()` opera en cinco pasos: (1) recibe `pattern_signal_metadata` del *CasePatternLibrary*; (2) extrae las senales faltantes y los scores de coincidencia por patron; (3) ordena los patrones por score descendente y selecciona los *top-k* (k=3 por defecto) para preservar la diversidad contrafactual; (4) calcula `gap_strength = len(missing_signals) * pattern_score` para cada patron; (5) genera una narrativa de falsificacion que explica explicitamente que senales faltan y por que la hipotesis principal podria ser incorrecta [^17^].

El campo `devil_advocate_source` documenta la procedencia de cada falsificacion en tres categorias mutuamente excluyentes: `deterministic_missing_signals` (patrones coincidieron con gaps identificados), `deterministic_no_pattern_data_available` (el *CasePatternLibrary* no ejecuto en este path), y `deterministic_no_pattern_matched` (ningun patron coincide con la evidencia) [^18^]. Esta taxonomia permite auditar la cobertura del Devil's Advocate por caso.

El sistema tiene una limitacion documentada (L-025): en el path standalone (`vigia_scorer.py`), el campo `devil_advocate` solo se popula cuando un curador humano lo escribe manualmente en el JSON del caso antes de construir el corpus. Ningun componente del pipeline autonomo genera este campo en tiempo de investigacion para ese path [^19^]. La limitacion no afecta al modo agente completo (`vigia_agent.py` + `sift_orchestrator.py`), donde el Devil's Advocate opera con datos del *CasePatternLibrary*.

#### 3.4.2 Escala de Intencionalidad: NOISE/SUSPICION/INTENT/MALICE

VIGIA define una escala de intencionalidad operacionalizada con cuatro niveles. Cada nivel requiere un conjunto estrictamente creciente de condiciones: NOISE (patrones aleatorios sin correlacion estructural), SUSPICION (anomalias que requieren explicacion), INTENT (anomalias con explicacion abductiva de costo minimico), y MALICE (INTENT + Devil's Advocate superado + confirmacion de fracturas CAIE). El *CollapseDecisionLayer* implementa una politica agresiva: cualquier ruptura de `sensor_independence` fuerza el veredicto a INCONCLUSIVE, priorizando la integridad epistemica sobre la cobertura [^20^].

#### 3.4.3 Sistema de Cuatro Estados con Umbrales en Fraction

El `RiskBoundedDecisionLayer` define cuatro niveles de alerta con umbrales en fracciones exactas, eliminando toda ambiguedad en los limites de decision.

| Nivel | Umbral (Fraction) | Valor Decimal | Veredicto Emitido | Condicion de Override |
|---|---|---|---|---|
| LOW | `< 15/100` | < 0.15 | NO_SEMIOTIC_ANOMALY_DETECTED | Ninguna |
| MEDIUM | `[15/100, 30/100)` | [0.15, 0.30) | ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED | Ninguna |
| HIGH | `[30/100, 60/100)` | [0.30, 0.60) | ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED | Ninguna |
| CRITICAL | `>= 60/100` | >= 0.60 | ADVERSARIAL_SEMIOTIC_PATTERN_DETECTED | ECO_SEMIOTIC_COLLISION fuerza CRITICAL |

La eleccion de `Fraction` sobre `float` es funcional, no estilistica. Los umbrales en punto flotante binario no pueden representar exactamente fracciones como 15/100 (0.15 = 0.001001100110011... en binario), lo que introduce variabilidad cross-platform. `Fraction(15, 100)` es exactamente 3/20 en cualquier arquitectura [^21^]. El override `ECO_SEMIOTIC_COLLISION` permite que la capa de decision eleve automaticamente a CRITICAL cuando el Devil's Advocate detecta una collision semiotica: la coexistencia de patrones mutuamente excluyentes que ninguna hipotesis unica puede explicar, serialando con alta probabilidad una operacion de *false flag* o anti-forense avanzada.

Para veredictos de mayor granularidad, el `QuadripartiteClassifier` expande el sistema a 8 estados con dos umbrales adicionales: `Fraction(4, 5)` (80 %, confianza alta) y `Fraction(3, 5)` (60 %, confianza media). Los estados `ABSTAIN_CONTRADICTION`, `ABSTAIN_INSUFFICIENT` y `ABSTAIN_DEGRADED` formalizan la abstencion como veredicto valido, no como fallo del sistema. Como indica el metadata de calibracion: "ABSTAIN en casos VIGIA-REAL es epistemologicamente correcto: los artefactos legacy tienen solo 2 anomalias... sin evidencia suficiente, ABSTAIN es la respuesta honesta y Daubert-defensible" [^22^]. En un campo que tradicionalmente premia la confianza sobre la honestidad, esta arquitectura de abstencion constituye una inversion epistemologica significativa.
## 4. Indicadores de Intento: Mas Alla de los IOCs Tradicionales

La forense digital ha operado durante decadas bajo un paradigma reactivo: el analista encuentra un hash malicioso, una IP sospechosa o un dominio fraudulento y busca coincidencias en sistemas comprometidos. Este modelo, basado en *Indicators of Compromise* (IOCs), responde a una pregunta fundamental: **"que paso?** Sin embargo, el panorama de amenazas de 2025-2026 ha erosionado la eficacia de este enfoque. El 82% de las detecciones reportadas por CrowdStrike en 2025 fueron *malware-free* — es decir, no dejaron artefactos estaticos detectables [^838^]. Las herramientas de evasion de EDR se venden en foros subterraneos por tan solo $300 [^782^], y el *breakout time* promedio se ha reducido a 29 minutos [^836^]. En este contexto, detectar *que* ocurrio ya no es suficiente: es necesario inferir *por que* ocurrio y *quien se beneficia* de que el investigador adopte una interpretacion particular.

VIGIA aborda esta brecha mediante un marco de *Indicators of Intent* (IoIs) que representa un salto epistemologico en el campo del DFIR (*Digital Forensics and Incident Response*): la transicion de detectar artefactos tecnicos a detectar intencionalidad deliberada [^3^].

### 4.1 La Jerarquia de Indicadores: De los IOCs a los IoIs

El ecosistema de ciberseguridad ha evolucionado a traves de tres generaciones de indicadores, cada una representando un nivel superior de abstraccion e interpretacion. La tabla siguiente sintetiza esta jerarquia:

| Dimension | IOC (Indicator of Compromise) | IOA (Indicator of Attack) | IoI (Indicator of Intent) |
|-----------|------------------------------|---------------------------|---------------------------|
| **Enfoque** | Evidencia despues del ataque | Comportamiento durante el ataque | Intencionalidad detras del comportamiento |
| **Temporalidad** | Reactivo | Proactivo | Interpretativo-abductivo |
| **Naturaleza** | Estatico (hashes, IPs, dominios) | Dinamico (TTPs) | Semiotico (signos de deliberacion) |
| **Pregunta central** | "Que paso?" | "Como lo hicieron?" | "Quien se beneficia de esta interpretacion?" |
| **Base de deteccion** | Firmas conocidas | Tacticas, tecnicas y procedimientos | Fracturas en la coherencia comunicativa |
| **Fundamento teorico** | Coincidencia de patrones | MITRE ATT&CK + ML | Semiotica Peirceana + pragmatica de Grice |
| **Operacion en VIGIA** | Input de primeridad | Template de hipotesis | Motor abductivo + CAIE |

*Fuentes: CrowdStrike [^8^]; SISA [^366^]; Forsythe [^7^]; VIGIA [^3^]*

La distincion no es meramente tecnica — es epistemologica. Mientras los IOCs operan en el nivel de *Secondness* peirceano (correlacion entre artefactos observados), los IoIs operan en el nivel de *Thirdness*: la ley o habito inferido que explica un patron deliberado [^3^]. CrowdStrike introdujo los *Indicators of Attack* (IOAs) en 2012 para detectar comportamiento en tiempo real [^8^]. SISA propuso en 2022 los *Indicators of Behavior* (IoB) como "particulas comportamentales que determinan el contexto y la intencion de una amenaza" [^366^]. VIGIA completa esta escalera: los IoIs analizan no el comportamiento, sino la intencionalidad que lo motiva.

Este salto responde al principio juridico latino *Cui bono?* ("A quien beneficia?"), operacionalizado mediante inferencia a la mejor explicacion [^418^][^30^]. La pregunta que formula VIGIA ante cada evidencia no es solo "que paso aqui?", sino "quien gana si el investigador cree que esto fue un error?" [^3^].

### 4.2 Los Cinco Indicators of Intent de VIGIA

VIGIA define cinco IoIs fundamentados en pragmatica linguistica, semiotica y ciencia forense. Cada uno detecta un patron especifico de manipulacion intencional.

**Weaponized Incompetence (Incompetencia Weaponizada).** Este IoI detecta cuando un actor deliberadamente finge incompetencia tecnica para ocultar actividad maliciosa. El caso **CAN-031** documenta el patron con precision: PowerShell ejecuta comandos perfectos para eliminar *shadow copies* y desactivar el firewall — cero errores de sintaxis — y 63 segundos despues el mismo usuario genera un ticket de IT quejandose de que "mi pantalla parpadeo, soy inutil con computadoras" [^853^]. La ausencia de errores en comandos destructivos contradice la narrativa de incompetencia. La deteccion se fundamenta en la violacion de las maximas de Calidad y Cantidad de Grice [^9^][^21^] y en la *Information Manipulation Theory 2* de McCornack: las mentiras se construyen a partir de verdades manipuladas para inducir una conclusion falsa [^24^].

**Excessive Digital Perfection (Perfeccion Digital Excesiva).** Los sistemas informaticos reales son inherentemente ruidosos: producen errores menores, timestamps con variabilidad, logs duplicados y eventos de depuracion. Un artefacto "demasiado limpio" — sin estas imperfecciones naturales — es una senal de intervencion deliberada. El caso **CAN-018** encapsula este principio: 847 comandos ejecutados a exactamente 300.000 segundos de intervalo, cero errores, cero reintentos, entropia temporal de 0.00 bits [^853^]. Tal perfeccion es estadisticamente imposible en un sistema operativo real. Técnicamente, este IoI conecta con la categoria de anti-forenses *trail obfuscation* (ofuscacion de rastro) documentada por Rogers y Conlan [^118^][^444^]. La regla **DOCUMENT_FORGERY** del CAIE de VIGIA se activa con severidad 0.9 cuando detecta esta anomalia [^26^].

**Significant Silences (Silencios Significativos).** La ausencia de artefactos que deberian estar presentes puede ser tan reveladora como su presencia. Se trata de *evidencia cuya ausencia es evidencia de intencionalidad*. William C. Thompson et al. demostraron formalmente, mediante inferencia bayesiana, que la ausencia de evidencia SI constituye evidencia de ausencia cuando se cumplen tres condiciones: se busco adecuadamente, la evidencia deberia estar presente segun el contexto, y la ausencia favorece una hipotesis sobre otra [^449^]. VIGIA detecta silencios significativos mediante la regla **USN_JOURNAL_GAP** del CAIE, que identifica vacios en el USN Journal de NTFS — un artefacto de sistema que rara vez presenta gaps naturales [^26^]. En terminos de pragmatica de Grice, un silencio significativo viola la maxima de Cantidad: "Haz tu contribucion tan informativa como se requiera" [^9^].

**Impossible Timing (Tiempo Imposible).** Este IoI detecta inconsistencias temporales que no pueden ocurrir naturalmente: un efecto antes de su causa, timestamps con precision imposible para el sistema, o secuencias que violan las leyes fisicas de la computacion. El *timestomping* — manipulacion de timestamps — es la tecnica anti-forense mas documentada, utilizada por decenas de grupos APT incluyendo Lazarus, APT28 y APT29 [^768^]. VIGIA implementa la regla **TEMPORAL_CAUSALITY_VIOLATION** con severidad maxima (1.0), que detecta directamente un "efecto antes de causa" [^26^]. La regla **TIMESTAMP_PRECISION_ANOMALY** (severidad 0.95) identifica sub-segundos truncados a ceros, una firma caracteristica de timestomping [^26^]. El modelo TER (*Timeline based Event Reconstruction*, 2025) proporciona el fundamento teorico para esta deteccion [^417^][^393^].

**Narrative Fractures (Fracturas Narrativas).** Cuando multiples artefactos deberian contar la misma historia pero no lo hacen, se produce una fractura narrativa. Brookman et al. (2020) demostraron que las narrativas forenses integran personaje, motivo, intencion y cronologia; cuando los artefactos proporcionan versiones contradictorias de estos elementos, la narrativa se fractura [^419^]. El **CAIE** (*Cross-Artifact Incongruence Engine*) de VIGIA detecta estas fracturas mediante nueve reglas especificas [^26^]. La regla **LOG_VS_MEMORY** (0.9) detecta cuando "los logs dicen X, pero la memoria dice que no ocurrio". La regla **NETWORK_VS_HOST** (0.8) activa cuando el firewall registra trafico pero el host no tiene *sockets* abiertos. La regla **FALSE_FLAG_PATTERN** (0.8) identifica "marcadores culturales altos + cero corroboracion tecnica" — el patron clasico de una bandera falsa [^26^]. Cada fractura incrementa el costo computacional de mantener una mentira coherente, haciendo la decepcion progresivamente mas cara para el atacante.

### 4.3 Deteccion de Artefactos Fabricados y *False Flags*

Los *false flags* — actos deliberados de engano donde los actores de amenaza disfrazan su identidad — representan una de las aplicaciones mas exigentes de los IoIs. Los casos documentados incluyen *Olympic Destroyer* (2018), donde Russia atribuyo el ataque a Corea del Norte [^783^], y el *DNC Hack* (2016), donde operadores GRU se hicieron pasar por un hacker rumano solitario [^783^].

VIGIA incluye casos especificos de *false flag* en su corpus de evaluacion: 3 de 3 *false flags* genuinos fueron detectados correctamente [^853^]. El mecanismo de deteccion opera mediante el CAIE buscando incongruencias entre artefactos que deberian corroborarse pero no lo hacen. Cuando un atacante copia las TTPs de un grupo conocido pero comete errores que ese grupo no cometeria — o cuando planta marcadores culturales sin respaldo tecnico — el sistema detecta la fractura. El caso **L-019** (*false flag* de atribucion cultural) fue resuelto correctamente, demostrando que la abduccion adversarial, conceptualizada por Forsythe como "esfuerzos semioticos para inducir a error las abducciones del adversario" [^7^], puede operacionalizarse computacionalmente.

La relevancia de esta capacidad crece con la sofisticacion de los actores de amenaza. Cuando el 82% de las detecciones son *malware-free* [^838^] y las tecnicas *living-off-the-land* aparecen en el 84% de ataques de alta severidad [^761^], la unica senal remanente suele ser la inconsistencia intencional — la marca que el atacante no puede eliminar sin dejar otra marca. VIGIA cuantifica esta fractura: la formula de scoring ajustado del CAIE, $adjusted\_score = raw\_score \times (1 - spoofability) \times weight$, penaliza matematicamente los artefactos de alta falsificabilidad, revelando las fracturas que indican manipulacion deliberada [^26^]. Este mecanismo transforma la economia de la decepcion digital: mientrastradicionalmente mentir en un log o fabricar un ataque es computacionalmente barato, VIGIA incrementa el costo de la mentira al exigir coherencia perfecta en multiples capas de evidencia simultaneamente. El atacante que puede falsear un log (facil) debe ahora falsear tambien la memoria (dificil), los timestamps (muy dificil) y las correlaciones cross-artifact (casi imposible). Los IoIs de VIGIA no reemplazan a los IOCs e IOAs: los complementan, proporcionando una capa de interpretacion que pregunta, ante cada artefacto, si la historia que cuenta es la que realmente ocurrio — o la que alguien quiere que el investigador crea.
## 5. Seguridad, Aislamiento de LLMs y Cadena de Custodia

### 5.1 Arquitectura de Aislamiento: LLMs Fuera del Path de Veredicto

#### 5.1.1 Principio fundamental: veredicto sellado antes de que LLM vea evidencia

La arquitectura de seguridad de VIGIA se construye sobre una premisa no negociable: el veredicto forense se computa y se sella criptográficamente antes de que cualquier modelo de lenguaje (LLM, *Large Language Model*) tenga acceso a la evidencia. Este principio responde a una vulnerabilidad estructural documentada en sistemas de IA aplicados a forense: los LLMs, incluso operando con parámetros deterministas, exhiben varianza residual suficiente para alterar interpretaciones en contextos de alta incertidumbre. El caso BREAK-012 del corpus VIGIA demuestra esta fragilidad: el modelo Claude cambió un veredicto de BENIGN a MALICE de manera incorrecta, un evento clasificado como alucinación del modelo [^263^].

VIGIA implementa una separación arquitectónica estricta entre el motor de inferencia determinista y los LLMs narrativos. El flujo de datos sigue una topología unidireccional: la evidencia cruda ingresa al motor determinista (Capas 0–3), que produce un bundle sellado (EBS v1); únicamente después del sellado, el bundle —ya inmutable— puede transferirse al pipeline narrativo para generación de informes. El LLM nunca participa en el cálculo del *z-score*, en la construcción del grafo de evidencia ni en la decisión ACCEPT/REJECT/ABSTAIN [^295^].

#### 5.1.2 BundleBuilder como proceso externo: motor comprometido no puede sellar su propia mentira

El sellado criptográfico no reside en el motor de inferencia sino en `bundle_builder.py`, un proceso externo de atestación. Esta decisión de diseño, auditada por Gemini y DeepSeek, responde a un argumento de seguridad fundamental: *un bundle que se hashea a sí mismo permite que un motor comprometido selle su propia mentira* [^324^]. Al externalizar el sellado, VIGIA garantiza que ni una modificación maliciosa del motor ni una inyección en runtime puedan producir un bundle aparentemente válido sin que el verificador independiente lo detecte.

La arquitectura completa se organiza en cinco capas de seguridad que operan de manera acumulativa:

| Capa | Componente | Función de seguridad | Primitiva criptográfica |
|------|-----------|----------------------|------------------------|
| 0 — Datos inmutables | EBS v1 (`ebs_v1.py`) | Especificación pura de datos; sin lógica de negocio, sin referencias a LLMs | Ninguna (datos crudos) |
| 1 — Integridad encadenada | BundleBuilder (`bundle_builder.py`) | Atestación externa; protocolo de 5 pasos de hashing | SHA-256 encadenado |
| 2 — Verificación independiente | `verify_ebs_v1.py` | Auditoría por terceros sin dependencias de producción | SHA-256 (stdlib only) |
| 3 — Custodia forense | HMAC Audit Logger | Registro secuencial con forward integrity | HMAC-SHA256 encadenado |
| 4 — Gobernanza runtime | ConfigSentinel + Sandbox | Detección de degradación; contención de procesos | HMAC-SHA256 + `setrlimit` |

Cada capa compensa debilidades potenciales de las demás. La Capa 0 garantiza que los datos sean interpretables sin código de producción; la Capa 1 asegura que el motor no pueda autovalidar manipulaciones; la Capa 2 permite que cualquier tercero con Python 3.6+ verifique un bundle; la Capa 3 crea un *ratchet* criptográfico donde la alteración de cualquier entrada invalida toda la cadena subsiguiente; y la Capa 4 protege contra la degradación silenciosa de módulos críticos y la escalada de privilegios en tiempo de ejecución [^295^] [^324^] [^316^].

### 5.2 Evidence Bundle Standard v1 (EBS v1)

#### 5.2.1 Capa 0 de datos pura e inmutable: sin lógica de negocio, sin referencias a LLMs

El Evidence Bundle Standard v1 constituye la especificación de datos forenses de VIGIA, implementada en `ebs_v1.py` (801 líneas, 29.1 KB) [^295^]. La regla absoluta que gobierna este módulo está documentada explícitamente en el código fuente: *"ABSOLUTE RULE: This module contains DATA ONLY. No business logic. No hashing. No sealing. No references to LLMs, Ollama, or narrative backends"*. Esta separación no es meramente organizativa — es una garantía de que el formato de evidencia permanece interpretable independientemente del sistema que lo produjo o del modelo de lenguaje que posteriormente lo narre.

El contenedor principal, `ForensicBundle`, agrupa seis componentes: `EvidenceGraph` (grafo de dependencias entre artefactos), `DecisionTrace` (traza de la decisión con *posterior*, *risk* y *log-likelihood ratio*), `PolicySpec` (especificación de política independiente del runtime), lista de acciones sugeridas, estado del sistema, y traza de abducción (`AbductionTrace`). Ninguno de estos componentes ejecuta código ni invoca funciones de hashing; el campo `integrity` de tipo `IntegrityBlock` se asigna exclusivamente desde el proceso externo `BundleBuilder` [^295^].

#### 5.2.2 Invariantes I1–I5: determinismo, integridad encadenada, política verificable

El estándar define cinco invariantes que todo bundle válido debe satisfacer. I1 (*Determinism*) establece que la misma entrada produce idéntico bundle bit-a-bit, independientemente de la arquitectura de hardware o la versión del intérprete Python. I2 (*Chained integrity*) exige que el `bundle_hash` cubra el contenido completo del payload. I3 (*Verifiable policy*) garantiza que la política de decisión sea independiente del runtime donde se ejecute el análisis. I4 (*Explicit actions*) prohíbe efectos secundarios implícitos: toda acción sugerida debe estar declarada explícitamente. I5 (*Explainable decision*) obliga a que los campos `risk` y `posterior` estén siempre presentes en la traza de decisión [^295^].

La satisfacción de estas invariantes habilita una propiedad forense crítica: la reproducibilidad intersubjetiva. Cualquier analista, en cualquier máquina, puede reconstruir el razonamiento que condujo al veredicto a partir del bundle únicamente, sin acceso al sistema que lo generó.

#### 5.2.3 Verificador independiente: solo stdlib Python, cero imports de producción

El archivo `verify_ebs_v1.py` (309 líneas) implementa el verificador independiente del estándar. Su garantía de independencia es total: utiliza exclusivamente la biblioteca estándar de Python, sin importar ninguna clase del código de producción de VIGIA [^316^]. Las constantes del estándar —versión soportada, nombres de campos requeridos, umbrales de validación— están copiadas deliberadamente en el verificador en lugar de importarse desde `ebs_v1.py`. Como señala la documentación del módulo: *"Si el verificador necesita importar el código de producción, el sistema no es auditable por terceros — viola el principio de independencia forense"* [^316^].

El verificador implementa seis reglas de validación con tres niveles de severidad (ERROR, WARNING, CRITICAL) y cuatro niveles de conformidad, desde Level 0 (*Non-compliant*) hasta Level 3 (*Fully compliant EBS v1*). La regla R6 (*Devil's Advocate*) es la única clasificada como CRITICAL: un veredicto MALICE o INTENT sin pasar por la validación del *devil's advocate* dispara fallo inmediato de verificación [^316^].

### 5.3 Cadena de Custodia Criptográfica

#### 5.3.1 HMAC-SHA256 encadenada con forward integrity

El sistema de cadena de custodia implementa un esquema de *forward integrity* mediante HMAC-SHA256 encadenado. Cada entrada del registro de auditoría contiene dos campos criptográficos: `_prev_hmac`, que almacena el HMAC de la entrada anterior (o la cadena "GENESIS" para la primera), y `_hmac`, que computa el HMAC-SHA256 del contenido de la entrada concatenado con `_prev_hmac` [^263^]. Esta estructura crea una propiedad de seguridad robusta: la alteración de cualquier línea invalida todas las entradas subsiguientes, ya que cada `_hmac` depende criptográficamente del anterior. La verificación de la cadena completa se realiza mediante `audit_logger.verify_chain()`, que recorre secuencialmente el registro validando cada enlace [^263^].

La resolución de la clave HMAC sigue una jerarquía de tres fuentes: variable de entorno `VIGIA_HMAC_KEY` (hex-encoded, mínimo 32 bytes), archivo externo vía `VIGIA_HMAC_KEY_FILE`, o generación efímera automática — esta última únicamente en entornos de desarrollo, registrada como WARNING en el log. La clave efímera presenta una limitación conocida: al reiniciar el proceso, la clave se pierde y la cadena previa no es verificable [^263^].

#### 5.3.2 Protocolo de 5 pasos: graph_hash → policy_hash → decision_hash → bundle_hash

El protocolo de hashing del BundleBuilder opera en cinco pasos secuenciales que acumulan integridad criptográfica desde los componentes individuales hacia el bundle completo [^324^]:

Paso 1: *graph_hash* = SHA-256 del grafo de evidencia **sin** el campo `graph_hash`.

Paso 2: *policy_hash* = SHA-256 de la especificación de política **sin** el campo `created_at` (garantizando reproducibilidad temporal).

Paso 3: *decision_hash* = SHA-256 de la traza de decisión completa.

Paso 4: El grafo se actualiza con `graph_hash` asignado → `graph_dict_final`.

Paso 5: *bundle_hash* = SHA-256 de la concatenación canónica de `bundle_id`, `version`, `timestamp`, `graph_dict_final`, `decision_trace`, `policy_spec`, `actions` y `system_state`.

La canonicalización estricta (designada H22 en la documentación interna) resuelve un problema de determinismo cross-platform: JSON no distingue `int(1)` de `float(1.0)`. La función `_canonicalize()` transforma tipos de manera unívoca — `float` a cadena con 8 decimales fijos, `int` a cadena con sufijo `:int`, `bool` a `"true"`/`"false"` en minúsculas, `None` a `"null"`, y diccionarios con claves ordenadas lexicográficamente — garantizando que el hash del bundle sea idéntico en cualquier plataforma [^324^].

#### 5.3.3 Witness Mode con co-firma humana (DUAL_CUSTODY/UNSIGNED/HARD_FAIL)

Para veredictos críticos (MALICE o INTENT), VIGIA implementa el *Witness Mode*: una co-firma HMAC-SHA256 con la clave del operador humano (`VIGIA_HUMAN_OPERATOR_KEY`), creando un esquema de *dual custody* donde una clave deriva de la cadena HMAC del audit log y la otra pertenece al analista calificado [^263^]. El sistema opera en tres modos mutuamente excluyentes:

En modo `DUAL_CUSTODY`, la clave del operador está presente y el reporte se co-firma; el veredicto alcanza estado *Daubert-admissible*. En modo `UNSIGNED`, la clave está ausente pero el sistema genera un *soft warning*; el bundle es usable pero carece de certificación humana. En modo `HARD_FAIL`, activado cuando `VIGIA_FORENSIC_STRICT=true` y la clave del operador está ausente, el veredicto se invalida y la investigación aborta, registrando el evento `WITNESS_HARD_FAIL` a nivel CRITICAL en el audit log. La clave del operador debe tener al menos 32 caracteres; claves débiles también son rechazadas en modo estricto [^263^].

### 5.4 Sandbox y Gobernanza

#### 5.4.1 Sandbox con setrlimit y drop de privilegios

El módulo `vigia/security/sandbox.py` (~400 líneas) implementa contención de procesos mediante el wrapper `sandboxed_execute()`, que invoca `asyncio.create_subprocess_exec` con restricciones POSIX impuestas vía `setrlimit` [^305^]. Los límites por defecto son: 512 MB de memoria virtual (`RLIMIT_AS`), 30 segundos de tiempo CPU (`RLIMIT_CPU`), cero core dumps (`RLIMIT_CORE = (0, 0)`), 50 MB de tamaño de archivo (`RLIMIT_FSIZE`), 1,024 archivos abiertos (`RLIMIT_NOFILE`), 64 MB de stack (`RLIMIT_STACK`) y 64 procesos (`RLIMIT_NPROC`) [^305^].

El sistema implementa *drop* de privilegios condicional: si la variable `VIGIA_DROP_PRIVS_UID` está definida y el proceso corre como root, transfiere al UID especificado antes de ejecutar el subprocesso. Si `setuid()` falla, el proceso aborta con `os._exit(126)` — nunca continúa con privilegios elevados [^305^]. En entornos Windows, el comportamiento es *fail-safe*: si `VIGIA_ENFORCE_POSIX_SANDBOX=true` en plataforma no-POSIX, el sistema aborta en el arranque; sin enforcement, aplica timeout agresivo de 5 segundos.

#### 5.4.2 ConfigSentinel: detección de degradación de módulos críticos

`config_sentinel.py` (~240 líneas) opera como guardian de integridad del sistema en tiempo de ejecución. Monitorea un conjunto de módulos críticos —CAIE (*Cross-Artifact Incongruence Engine*), TrustFusion, OckhamAdversarial y SignalRouter— y detecta tres patrones de degradación: desactivación de módulos críticos durante el arranque, cambios de configuración en runtime (*tampering*), y degradación silenciosa inducida por variables de entorno [^298^].

El flujo de operación consta de tres fases: `initialize()` captura un *snapshot* criptográfico de la configuración antes del análisis; `checkpoint()` verifica cambios respecto al baseline entre fases del pipeline; y `finalize()` cierra el *trail* de auditoría. Cada evento de degradación se sella con HMAC-SHA256 usando la clave secreta del monitor. Si un módulo crítico se desactiva durante el análisis, el sistema dispara `ConfigurationTamperedException`, interrumpiendo el pipeline [^298^].

La arquitectura de seguridad de VIGIA ha sido auditada en múltiples rondas por Kimi (Moonshot), Gemini (Google) y DeepSeek, con 16+ correcciones de seguridad documentadas en el repositorio, incluyendo vulnerabilidades de transporte MCP (V-002), limitación de tasa (V-003), validación de symlinks (V-004) y sanitización de señales antes de ingesta a LLM [^263^]. Esta multi-auditoría, combinada con el código abierto bajo licencia Apache 2.0, constituye una ventaja estructural frente a herramientas forenses de caja negra cuya evidencia ha sido excluida de tribunales por falta de transparencia [^245^].
## 6. Determinismo Computacional y Cumplimiento del Estándar Daubert

### 6.1 El Problema del Punto Flotante en Forense

#### 6.1.1 No-asociatividad y no-determinismo de cálculos en paralelo

La aritmética de punto flotante conforme al estándar IEEE-754 posee una propiedad que la descalifica para aplicaciones forenses legales: **no es asociativa**. En otras palabras, $(a + b) + c$ no necesariamente equivale a $a + (b + c)$ [^611^]. En computación paralela —incluyendo cómputo en GPU— el orden de evaluación depende del planificador de hilos (*thread scheduler*), que es inherentemente no-determinista. Un estudio de 2024 demostró que la variabilidad por no-asociatividad en operaciones paralelas en GPU alcanza los umbrales de tolerancia de simulación molecular de alta precisión [^683^]. Lawrence Livermore National Laboratory documentó diferencias de un orden de magnitud en errores de redondeo entre distintas operaciones de reducción en aceleradores [^681^]. NVIDIA clasifica el determinismo de sus GPUs en tres niveles: *not-guaranteed*, *run-to-run* e idéntico *gpu-to-gpu* —este último con una penalización de rendimiento del 20-30% [^679^]. En forense, un bit que cambia en el bit 52 de la mantisa puede alterar un veredicto de SUSPICION a MALICE, invalidar el hash SHA-256 de un bundle o producir conclusiones distintas en máquinas diferentes.

#### 6.1.2 Casos históricos: Intel Pentium FDIV ($475M), Patriot Missile (28 muertos), Ariane 5 ($370M)

La literatura documenta tres desastres paradigmáticos causados por errores de representación numérica. El **bug FDIV del Intel Pentium (1994)** —cinco entradas faltantes en una tabla de 1,066— producía divisiones incorrectas con probabilidad de 1 en 9 mil millones, costando a Intel $475 millones en reemplazos, más demandas colectivas e investigación de la SEC [^695^] [^696^] [^697^]. El **fallo del Patriot Missile (1991)** fue más trágico: el valor 0.1 segundos —no terminable en binario— se truncó a 24 bits; tras 100 horas, el error acumulado alcanzó ~0.34 segundos, suficiente para que un Scud a 1,676 m/s recorriera ~570 metros fuera del *range gate*, matando a 28 soldados en Dhahran [^705^] [^709^] [^710^] [^711^]. El **vuelo 501 del Ariane 5 (1996)** se autodestruyó cuando la velocidad horizontal superó 32,767 —máximo de int16— durante una conversión de float64 a entero, destruyendo $370 millones más una carga de $500 millones [^708^] [^713^] [^715^] [^716^] [^719^]. Tres mecanismos distintos —tabla de hardware, acumulación de redondeo, overflow de tipo— convergen en una misma lección: un sistema que no controla su aritmética numérica no puede garantizar la integridad de sus conclusiones.

### 6.2 Aritmética Exacta en VIGIA

#### 6.2.1 Python `fractions.Fraction` para umbrales de decisión

VIGIA evita completamente el punto flotante IEEE-754 en su capa de decisión. Los umbrales que separan los cuatro niveles de veredicto se definen mediante `fractions.Fraction`, que representa números racionales exactos como pares (numerador, denominador) de enteros de precisión ilimitada [^152^]. En `vigia_scorer.py`:

```python
elif final_score > Fraction(3, 4):     # exactamente 0.75
    verdict = "MALICE"
elif final_score > Fraction(11, 20):  # exactamente 0.55
    verdict = "SUSPICION"
elif final_score > Fraction(1, 4):    # exactamente 0.25
    verdict = "UNKNOWN"
```

Con `float(0.75)`, un score de `0.7500000000000001` —producto de errores de redondeo acumulados— cruzaría incorrectamente el umbral. Con `Fraction(3, 4)`, ese escenario es matemáticamente imposible.

#### 6.2.2 `decimal.Decimal(prec=28)` para cómputo intermedio

Para cómputo intermedio —sumas acumulativas, normalizaciones— VIGIA emplea `decimal.Decimal` con precisión fija de 28 dígitos y redondeo `ROUND_HALF_EVEN`, eliminando la divergencia del bit 52 que `round()` nativo produce entre arquitecturas x86-64 y ARM64 [^152^]. Las funciones `_dround()` y `_dsum()` actúan como "escudos de matemática finita": ante valores `inf`, `-inf` o `NaN`, retornan 0.0, previniendo que artefactos corruptos propaguen toxicidad al veredicto.

#### 6.2.3 Garantía: "same input → same SHA-256 bundle hash on any machine, any run"

La arquitectura opera en tres capas: `fractions.Fraction` para umbrales exactos, `decimal.Decimal` para cómputo de precisión controlada, y `SHA-256` para sellado criptográfico. Cada `ForensicRecord` genera su hash mediante `json.dumps(sort_keys=True, ensure_ascii=False)` seguido de SHA-256, garantizando serialización determinista. El sistema es *stateless* por diseño: no hay semillas aleatorias, no hay llamadas de red, no hay timestamps en el hash de decisión. Esta garantía de reproducibilidad bit-exact es condición necesaria que NIST SP 800-86 define para la admisibilidad de evidencia electrónica: resultados *repeatable* y *reproducible* [^680^].

| Propiedad | `float` (IEEE-754) | `fractions.Fraction` | Implicación forense |
|---|---|---|---|
| Representación | 53 bits de mantisa (aproximada) | Par (num, den) de enteros ilimitados (exacta) | `0.1 + 0.2 == 0.3` es `False` con `float`; `True` con `Fraction` |
| Asociatividad | No: $(a+b)+c \neq a+(b+c)$ | Sí | `Fraction` produce el mismo resultado independientemente del orden de evaluación |
| Hash cross-platform | No garantizado | Garantizado | `Fraction` produce el mismo hash en x86-64, ARM64 o cualquier plataforma |
| Serialización | `repr()` puede variar entre plataformas | `repr()` siempre exacto | `Fraction` es reproducible al deserializar |
| Penalización de rendimiento | ~1 ciclo CPU | ~50-500× más lento | Aceptable para scoring forense (decenas de artefactos, no millones de operaciones) |
| Determinismo en GPU paralelo | No (no-asociatividad del planificador) | Sí | `Fraction` elimina la fuente de no-determinismo en cómputo paralelo |

### 6.3 Cumplimiento del Estándar Daubert

#### 6.3.1 Los 5 factores Daubert y cómo VIGIA los cumple

El estándar *Daubert v. Merrell Dow Pharmaceuticals, Inc.*, 509 U.S. 579 (1993), impone al juez la obligación de *gatekeeping*: asegurar que el testimonio experto "repose sobre un fundamento confiable y sea relevante" [^145^] [^161^]. La Corte formuló cinco factores indicativos, extendidos por *Kumho Tire Co. v. Carmichael*, 526 U.S. 137 (1999), a **todo** testimonio experto [^162^].

| Factor Daubert | Requisito | Implementación VIGIA | Evidencia verificable |
|---|---|---|---|
| 1. Testabilidad (falsabilidad) | El método puede probarse empíricamente | `VIGIA_FORENSIC_LOCK=true`; `fractions.Fraction`; seed fijo | `make check-determinism` ejecuta $N$ veces y compara hashes SHA-256 |
| 2. Revisión por pares | Método sometido a revisión y publicación | Código abierto Apache 2.0 en GitHub público | Cualquier experto puede auditar el código; verificador `verify_ebs_v1.py` usa stdlib únicamente [^184^] |
| 3. Tasa de error conocida | Tasa de error documentada | Escala de 4 niveles; campo `what_would_falsify_this` | Métricas FPR, FNR-MAL, TTP Coverage; 55/55 tests EBS v1 |
| 4. Estándares y controles | Estándares que controlan la operación | Protocolo P2; ISO 27037:2012; NIST SP 800-86 | `_dround()` con precisión fija; cadena HMAC-SHA256 |
| 5. Aceptación general | Aceptación en la comunidad relevante | SANS FIND EVIL 2026; STIX 2.1; MITRE ATT&CK | Formatos de intercambio ampliamente aceptados |

Un método no-determinista **no puede** tener una tasa de error conocida porque sus resultados varían entre ejecuciones [^589^]. Si un score cambia entre máquinas por diferencias de punto flotante, el sistema no es *repeatable*, su tasa de error es incalculable, y es inadmisible bajo Daubert. VIGIA resuelve este problema en su raíz aritmética.

#### 6.3.2 FRE 702 (2023 amendment): nuevo requisito "más probable que no"

La enmienda a la Regla 702, efectiva el 1 de diciembre de 2023, introduce dos cambios fundamentales [^143^] [^147^]. Primero, el proponente debe demostrar por preponderancia ("más probable que no") que el testimonio cumple **todos** los requisitos; antes, muchos tribunales trataban la metodología como de "peso" para el jurado, no de admisibilidad [^591^]. Segundo, la opinión del experto debe reflejar "una aplicación confiable de los principios y métodos a los hechos del caso". El Comité Asesor instruyó que los forenses "deben evitar afirmaciones de certeza absoluta" [^147^]. VIGIA cumple esto mediante su sistema de 4 niveles que evita veredictos binarios absolutos, y el campo `what_would_falsify_this` que documenta las condiciones de falsabilidad de cada conclusión.

#### 6.3.3 FRE 902(13)/(14): auto-autenticación de evidencia digital

Las enmiendas de 2017 crearon mecanismos de auto-autenticación electrónica [^180^] [^182^]. La Regla 902(14) permite que datos de dispositivos electrónicos se autentiquen mediante un "proceso de identificación digital" —típicamente valores de hash— sin testimonio presencial. El Federal Judicial Center señala que "valores de hash idénticos para el original y la copia atestiguan confiablemente que son duplicados exactos" [^182^]. VIGIA implementa SHA-256 atómico durante lectura (`O_NOFOLLOW` + `os.fstat(fd)`), HMAC-SHA256 encadenado con `_prev_hmac`, montaje read-only Docker, y WORM con `chattr +i`, cumpliendo simultáneamente ISO/IEC 27037:2012 [^707^].

#### 6.3.4 El caso Cybercheck: por qué las cajas negras fracasan en tribunales

El contraste más ilustrativo lo proporciona **Cybercheck**, software de IA que afirma identificar perpetradores con "90% de precisión" [^597^]. Su creador, Adam Mosher, rehusó explicar cómo funciona; bajo juramento testificó que Cybercheck **no retiene registros** de dónde obtiene datos ni cómo calcula sus tasas de precisión [^597^]. Jueces en Colorado declararon su evidencia inadmisible; en abril de 2024, abogados en Ohio acusaron a Mosher de perjurio [^197^]. El reconocimiento facial fue excluido en 2025 por "fallas de confiabilidad y transparencia" [^197^]; en *Commonwealth v. Arrington*, 226 N.E.3d 851 (Mass. 2024), la Corte excluyó datos de iPhones porque el algoritmo era "propietario y celosamente guardado por Apple" [^613^] [^648^]. La lección es unívoca: **el acceso al algoritmo es fundamental para la admisibilidad**. VIGIA elimina este obstáculo por diseño —su código abierto permite que cualquier contraexperto examine y verifique cada línea. Como argumentó Brian Carrier, las herramientas forenses de código abierto tienen "aceptación implícita de la comunidad por virtud de su continuo desarrollo y uso", lo que ha llevado a denominar a la forense de código abierto **"el estándar digital Daubert"** [^184^].
## 7. Evaluacion Empirica y Casos Reales

La validacion de un sistema forense exige confrontacion con datasets publicos, *ground truth* verificable, y escenarios que ejerciten cada capa del motor de inferencia. VIGIA ha sido sometido a tres capas de evaluacion — corpus real, corpus canonico, y tests estructurales — sobre un total de 125 casos y 55 tests automatizados. Este capitulo documenta los resultados cuantitativos, la metodologia de evaluacion, y tres casos que ilustran como opera el sistema cuando la intencionalidad se oculta tras tecnicas anti-forenses sofisticadas.

### 7.1 Datasets y Metodologia de Evaluacion

#### 7.1.1 Datasets Publicos Verificados

VIGIA utiliza seis fuentes de datasets forenses reconocidos internacionalmente: NIST CFReDS (*Computer Forensic Reference Data Sets*), desarrollados por el IT Laboratory del National Institute of Standards and Technology [^76^][^523^]; los DFRWS Forensic Challenges, organizados anualmente desde 2005 con soluciones publicadas [^542^]; Digital Corpora, mantenido por Simson Garfinkel, con escenarios como Nitroba University y M57-Patents [^554^][^84^]; el curso SANS FOR508 (Stark Research Labs 2018) [^548^][^549^]; datasets de Ali Hadi; y el Cridex Banking Trojan del Volatility Project. Todos cumplen tres criterios: *ground truth* publicamente verificable, multiples categorias de artefactos (disco, memoria, red), y reconocimiento en la comunidad DFIR como referencia para evaluacion de herramientas.

#### 7.1.2 Corpus Canonico VIGIA-CAN

El corpus canonico comprende 52 casos sinteticos con *ground truth* conocido, que cubren patrones documentados en la literatura anti-forense: *weaponized incompetence*, *process hollowing*, *log ventriloquism*, persistencia fantasma, y false flags culturales. Cada caso se ejecuta mediante `tests/run_all_cases.py` (pipeline Python determinista, vía `run_vigia_case.py` — no el agente autónomo), produciendo un `ForensicBundle` sellado con SHA-256 y cadena HMAC. Resultado: 52/52 correctos (100%) en **modo Python**.

> **Corrección 2026-06-22:** la version original de este informe atribuia este resultado a "modo agente". Verificación contra el repositorio en vivo confirmó que `run_all_cases.py` invoca `run_vigia_case.py` (scorer determinista), sin tocar `vigia_agent.py`. La métrica real de modo agente autónomo se documenta en §7.1.4.

#### 7.1.3 Corpus Real

El corpus real comprende 18 casos de datasets publicos procesados con el pipeline completo. La Tabla 7.1 resume los resultados por fuente.

**Tabla 7.1 — Resultados de Evaluacion por Dataset (Corpus Real + Canonico)**

| Fuente | Casos | Correctos | Precision | Modo |
|--------|-------|-----------|-----------|------|
| NIST CFReDS (Mr. Evil, Data Leakage) | 2 | 2 | 100% | Python |
| Ali Hadi (Web Server, SysInternals, Encrypt) | 3 | 3 | 100% | Python |
| Digital Corpora (M57-Jean, Nitroba) | 2 | 2 | 100% | Python |
| Volatility Project (Cridex Trojan) | 1 | 1 | 100% | Python |
| DFRWS 2008/2011 (Linux, Android) | 2 | 2 | 100% | Python |
| SANS FOR508 / Stark Research Labs 2018 | 5 | 5 | 100% | Python |
| DEF CON DFIR CTF | 1 | 1 | 100% | Python |
| SANS SRL-2018 (DC Memory) | 1 | 1 (ABSTAIN) | 100% | Python |
| **Subtotal Corpus Real** | **18** | **18** | **100%** | Python |
| **Corpus Canonico VIGIA-CAN** | **52** | **52** | **100%** | Python |
| **Tests EBS v1** | **55** | **55** | **100%** | stdlib |
| **Total Empirico (modo Python)** | **125** | **125** | **100%** | Python / stdlib |

> **Corrección 2026-06-22:** la columna "Modo" decía "Agente" en la version original. Estos 70 casos (18 reales + 52 canonicos) corren via `run_all_cases.py` → `run_vigia_case.py`, el pipeline Python determinista — no `vigia_agent.py`. Esto NO es la metrica de produccion del agente autonomo; ver §7.1.4.

La precision del 100% en modo Python debe interpretarse con cautela: la muestra de 70 casos (18 reales + 52 canonicos) es selectiva y potencialmente sesgada, y no es la metrica de produccion del agente autonomo. La evaluacion en benchmarks independientes como DFIR-Metric [^513^] constituye trabajo pendiente.

#### 7.1.4 Métrica del Agente Autónomo (`vigia_agent.py`) — la cifra de producción real

La suite de regresión completa, ejecutada mediante `run_all_agent.py` contra `vigia_agent.py` (modo agente autónomo, no el scorer Python aislado), cubre 136 casos repartidos en tres dominios de evaluación:

| Dominio | Casos | Correctos | Precisión | Detalle |
|---|---|---|---|---|
| **Dominio A** (núcleo determinista) | 118 | 118 | **100%** | Falsos positivos, falsos negativos, false flag, corpus de demo |
| **Dominio B** (frontera epistémica) | 2 | 0 | 0% | VIGIA-AMB-001/002 — NOISE en lugar de ABSTAIN (L-012, límite de diseño documentado) |
| **Dominio C** (resto de la suite) | 16 | 16 | 100% | — |
| **Total A+B+C (modo agente)** | **136** | **134** | **98.5%** | Reproducible: `python3 run_all_agent.py --timeout 90` |

El único fallo del modo agente son los dos casos de ambigüedad irreducible (VIGIA-AMB-001, VIGIA-AMB-002), donde el diseño correcto es ABSTAIN y el sistema emite NOISE — un límite de frontera epistémica documentado como L-012 en `KNOWN_LIMITATIONS.md`, no un error de conteo ni una falla de cobertura. **Dominio A (118/118, 100%) es la única cifra que constituye el claim de precisión del sistema**; el 134/136 es la cifra de producción honesta que incluye los casos límite de Dominio B.

### 7.2 Resultados Cuantitativos

#### 7.2.1 Tests EBS v1

El framework *Evidence-Based Security v1* define 55 tests que verifican validacion de esquema `ForensicBundle`, integridad del sellado de 4 hashes (H1-H4), consistencia del *Cross-Artifact Incongruence Engine* (CAIE), y completitud de la cadena de custodia digital. El verificador `verify_ebs_v1.py` usa exclusivamente la biblioteca estandar de Python (cero dependencias de produccion), permitiendo auditoria por terceros. El logro de 55/55 (commit `51a8d13`) requirio correccion de la tupla en `likelihood_engine`, unificacion de `verify_hash`, y resolucion de symlinks.

#### 7.2.2 Brier Score del LRCalibrator

El sistema de calibracion probabilistica alcanza un *Brier Score* de 0.0813 sobre 105 casos, con particion 80/20 (84 entrenamiento, 21 test) y semilla 42 para reproducibilidad [^515^]. El Brier Score mide la calidad de las probabilidades predichas en el rango [0, 1], donde 0 indica prediccion perfecta; un valor <0.1 se considera altamente calibrado en aplicaciones meteorologicas y de riesgo. Sin embargo, los metadatos revelan un FPR al umbral 0.5 de 1.0 (100%), explicable parcialmente por el desbalance del conjunto de test (solo 3 de 21 casos son autenticos). La distincion entre calibracion y discriminacion es tecnica pero critica: un modelo puede estar bien calibrado (predicciones confiables en probabilidad) pero tener poder discriminativo limitado si el umbral operativo no se ajusta a la distribucion real de clases.

#### 7.2.3 Tests Adversariales

La suite *Red Team* (`test_red_team.py`, 352 lineas) contiene 20 payloads adversariales disenados por DeepSeek y ChatGPT. El sistema manejo correctamente 14 de 16 payloads evaluados (87.5%), detectando destruccion directa, evasion difusa, y negacion contrastiva, mientras preservaba la correcta clasificacion de instrucciones benignas con negacion. Complementariamente, el modulo *Temporal Forensics Red Team* (`temporal_forensics_redteam.py`, 878 lineas) detecta anacronismos linguisticos mediante un diccionario temporal con marcas como "whatsapp" (2009), "bitcoin" (2009), y "chatgpt" (2022).

### 7.3 Casos Destacados

Los tres casos siguientes fueron seleccionados porque ejercitan tres vectores de engano distintos: la simulacion de incompetencia tecnica, la suplantacion de identidad en logs, y la explotacion de infraestructura compartida para anonimato. Cada caso incluye bundle forense con cadena HMAC verificable y sidecar SHA-256.

#### 7.3.1 CAN-031: Weaponized Incompetence

El caso VIGIA-CAN-031 modela un *insider threat* que ejecuta comandos PowerShell para eliminar *shadow copies* (`vssadmin delete shadows /all /quiet`) y desactivar el firewall, luego abre un ticket de IT reportando "my screen went blank" [^270^]. El patron — *weaponized incompetence* — explota una asimetria cognitiva: IT interpreta el ticket como incidente tecnico comun, mientras que el analista forense, al correlacionar el timestamp del ticket con los logs de ejecucion, detecta una congruencia sospechosa.

El bundle (273 lineas, SHA-256: `f44ede5c...`) documenta 5 iteraciones de pipeline. El motor CAIE detecta una fractura entre los artefactos de ejecucion (PowerShell con privilegios elevados) y la narrativa del ticket (usuario pasivo y confundido). La incongruencia eleva el score hasta el umbral MALICE. Este caso demuestra como VIGIA opera sobre la pregunta epistemica: *quien se beneficia de que el investigador crea esta interpretacion?*

#### 7.3.2 CAN-038: The Ventriloquist

El caso VIGIA-CAN-038 modela *log ventriloquism*: el atacante inyecta entradas de log falsas que aparentan provenir de usuarios legitimos, explotando la confianza en timestamps y nombres de cuenta. El bundle (273 lineas, SHA-256: `6b3e9f73...`) documenta el mismo pipeline de 5 iteraciones.

El atacante utiliza credenciales comprometidas para crear logs que atribuyen acciones maliciosas a un usuario inocente. CAIE aplica la regla `TEMPORAL_CAUSALITY_VIOLATION` (severidad 1.0) cuando detecta que la secuencia de acciones implicaria un patron fisicamente imposible: autenticacion desde dos ubicaciones geograficas distantes en un intervalo incompatible con la velocidad de desplazamiento. La combinacion de esta fractura con el analisis de *spoofability* — logs (alto: 0.85) versus memoria (bajo: 0.15) — produce un veredicto de MALICE con confianza calculada via aritmetica de fracciones exactas.

#### 7.3.3 REAL-007: Nitroba University Harassment

El caso VIGIA-REAL-007 proviene del dataset Nitroba University Harassment Scenario de Digital Corpora [^554^][^84^], uno de los escenarios forenses mas citados en la literatura academica. En 2008, la profesora Lily Tuckrige recibio correos amenazantes desde la IP 140.247.62.34 (dormitorio G24). Tres estudiantes compartian la habitacion: Alice, Barbara, y Candice. Barbara habia instalado un router Wi-Fi sin contrasena, abriendo un vector de acceso anonimo. La universidad coloco un sniffer en el puerto Ethernet y capturo el trafico en NITROBA.PCAP.

El analisis canonico del PCAP revela: IP interna 192.168.15.4, MAC 00:17:f2:e2:c0:ce (dispositivo Apple), uso de willselfdestruct.com para mensajes anonimos, y una sesion Gmail que expone el cookie `jcoach@gmail.com` perteneciente a Johnny Coach, estudiante de Chemistry 109 [^532^][^124^][^125^].

El bundle de VIGIA (249 lineas, SHA-256: `56a768cc...`) procesa la evidencia correlacionando logs de red, artefactos HTTP, y metadata de email. CAIE detecta que la evidencia de red (192.168.15.4) y la de aplicacion (cookie Gmail de jcoach@gmail.com) apuntan consistentemente al mismo actor, eliminando la hipotesis de acceso no autorizado al router abierto. El veredicto es MALICE. Este caso demuestra la capacidad de VIGIA para atribuir intencionalidad donde el atacante explota la ambiguedad de infraestructura compartida.

### 7.4 Limitaciones Conocidas

El documento KNOWN_LIMITATIONS.md registra 27+ limitaciones, de las cuales dos afectan directamente la interpretacion de los resultados empiricos.

**L-025 — Devil's Advocate sin Generador Autonomo.** El campo `devil_advocate` solo se completa con curacion humana; ningun componente del pipeline autonomo lo genera en tiempo real. Para los 70 casos del corpus, esto no afecta los resultados porque los bundles incluyen curacion manual; en despliegue autonomo sin supervision, el sistema carece de la capa de refutacion automatica.

**L-026 — Muestra Empirica Limitada.** Los 70 casos evaluados representan un volumen insuficiente para sostener claims de precision al 100% en el espacio completo de amenazas. Ninguno proviene de benchmarks independientes (DFIR-Metric [^513^], AutoDFBench [^688^]); todos los corpus canonicos fueron disenados por el equipo de VIGIA, con riesgo de *overfitting*. La precision reportada debe entenderse como resultado preliminar, no garantia operativa. La declaracion del equipo — *"Si la comunidad aporta falsos positivos y falsos negativos, voy a estar contenta: significa que puedo seguir mejorando"* — constituye una postura epistemologicamente honesta que fortalece la credibilidad del sistema.
## 8. Ecosistema, Integracion y Modelo de Desarrollo

### 8.1 Integracion con SIFT Workstation via Protocol SIFT

#### 8.1.1 Model Context Protocol (MCP) de Anthropic como capa de conexion

La integracion de VIGIA con el ecosistema forense se articula a traves del **Model Context Protocol (MCP)**, un protocolo abierto anunciado por Anthropic en noviembre de 2024 y donado a la Agentic AI Foundation (AAIF) bajo la Linux Foundation en diciembre de 2025 [^467^]. Creado por David Soria Parra y Justin Spahr-Summers, MCP resuelve el problema de integracion "NxM" mediante una interfaz estandarizada sobre JSON-RPC 2.0 que conecta aplicaciones LLM con fuentes de datos externas [^462^] [^55^]. La arquitectura consta de tres componentes —Host (aplicacion LLM), Client (conector MCP) y Server (herramienta expuesta)— que permiten que herramientas como Volatility3 o Plaso se invoquen directamente desde un agente de lenguaje sin que el analista escriba comandos [^505^].

#### 8.1.2 Protocol SIFT: demo de "find evil" en 14 minutos 27 segundos

**Protocol SIFT** fue introducido por Rob T. Lee (SANS Institute) en enero de 2026, motivado por dos decadas de observacion: los analistas DFIR habian sido entrenados para ser "estenografos de linea de comandos en lugar de investigadores" [^55^]. El catalizador fue el reporte GTG-1002 de Anthropic (noviembre 2025), que documento una operacion de ciberespionaje estatal con Claude Code + MCP alcanzando 80-90% de ejecucion autonoma [^40^].

La demostracion decisiva ocurrio en RSAC 2026: el comando **"find evil"** produjo un analisis forense completo de una unidad C: en **14 minutos y 27 segundos**, trabajo que manualmente puede tardar una semana [^42^]. El agente identifico el actor de amenaza, cadena de ataque completa, persistencia, inyeccion de codigo, infraestructura C2 y arbol de procesos maliciosos. Protocol SIFT implementa ademas el mecanismo de auto-correccion "Ralph Wiggum Loop", donde el LLM lee errores de herramientas, ajusta hipotesis y reintenta hasta exito o bloqueo explicito [^55^].

#### 8.1.3 Ecosistema MCP forense: Valhuntir y volatility3-mcp

El ecosistema de servidores MCP forenses crece rapidamente. Cuatro implementaciones de volatility3-mcp coexisten —Kirandawadi (FastMCP + YARA), bornpresident (Claude Desktop), gaffx (FastAPI) y raviesheth2608 (background jobs)— [^495^] [^486^] [^489^] [^492^]. La plataforma mas ambiciosa es **Valhuntir** (AppliedIR), que expone 73-100 herramientas MCP a traves de 11 paquetes [^473^]:

| Paquete MCP | Herramientas | Funcion Principal |
|---|---|---|
| **forensic-mcp** | 23 | Hallazgos, timeline, evidencia, disciplina forense |
| **case-mcp** | 15 | Ciclo de vida del caso, gestion de evidencia, auditoria |
| **sift-mcp** | 5 | Ejecucion de herramientas forenses Linux |
| **forensic-rag** | 3 | Busqueda semantica sobre 22,000+ registros forenses |
| **windows-triage** | 13 | Validacion de baseline offline (2.6M registros known-good) |
| **opencti** | 8 | Inteligencia de amenazas desde OpenCTI |
| **report-mcp** | 6 | Generacion de reportes con 6 perfiles |
| **opensearch-mcp** (opcional) | 17 | Indexacion y query de evidencia a escala |
| **sift-gateway** | — | Gateway HTTP agregando todos los MCPs |
| **case-dashboard** | — | Portal del examinador (UI web) |
| **forensic-knowledge** | — | Paquete YAML de conocimiento forense compartido |

Valhuntir refuerza la disciplina forense mediante un paquete de conocimiento que enriquece respuestas con advertencias de herramientas, busqueda semantica sobre fuentes como MITRE ATT&CK y Sigma, y un Examiner Portal donde cada hallazgo requiere aprobacion o rechazo humano explicito [^479^]. Los controles de seguridad incluyen sandbox Bubblewrap a nivel kernel, 41 reglas de denegacion para archivos de caso, y firmas criptograficas PBKDF2 [^473^].

### 8.2 AI Collective: Un Nuevo Modelo de Desarrollo

#### 8.2.1 7 LLMs con roles especializados

VIGIA fue desarrollado mediante un **AI Collective** de siete LLMs con roles diferenciados, dirigido por Anna Tchijova bajo el paradigma **human-as-orchestrator**: el humano comunica requisitos y valida, los LLMs ejecutan [^880^].

| Miembro | Rol en el Collective | Contribuciones Principales |
|---|---|---|
| **Claude** (Anthropic) | Systems Integration Engineer | Integracion de modulos, hardening, puente MCP, herramientas forenses [^222^] |
| **Gemini** (Google) | Chief Tactical Officer & PsyWar Analyst | Marco teorico IoI, semiotica Peirceana a heuristicas forenses [^222^] |
| **Kimi** (Moonshot AI) | Forensic Systems Specialist | Volatility integration, CrossArtifactIncongruenceEngine, diseno P2 [^222^] |
| **DeepSeek** (DeepSeek AI) | Security Auditor & Critical Reviewer | Vulnerabilidades, hardening, fixes TOCTOU, parches P0 [^222^] |
| **Qwen** (Alibaba) | Security & Forensic Pipeline Auditor | Hardening de contenedores, determinismo de float, hash chain [^222^] |
| **Grok** (xAI) | Epistemic Integrity & Scoring Architect | Analisis scorer P2, spoofabilidad, credibility_modifier [^222^] |
| **ChatGPT** (OpenAI) | Adversarial Red Team & Epistemological Validator | Stress testing P2, casos edge [^222^] |

El proceso operaba con competencia sana: Kimi como "el implacable" cazador de bugs, ChatGPT como "el insoportable" que senalaba todo lo faltante, y Claude protestando cuando recibia archivos con bugs repetidos [^225^]. El ciclo seguia tres fases: debate de ideas, escritura de codigo, y auditoria cruzada [^225^].

#### 8.2.2 Anna Tchijova como orquestadora humana

**Anna Tchijova**, cocinera profesional de origen ruso residente en Argentina sin formacion IT formal, ocupo el rol de Creator, Principal Investigator y Architect de VIGIA [^225^] [^777^]. Concibio el paradigma IoC $\rightarrow$ IoI, diseno el marco teorico integrando Peirce, Grice, Carnegie y Eco, y mantuvo veto sobre propuestas que violaran principios Daubert [^222^]. El desarrollo se realizo con recursos minimos —"como no tenia dinero para Claude Code, casi todo VIGIA fue construido para modo fallback o Ollama"— lo que motivo decisiones como el modo 0 tokens y la ausencia de UI grafica ("una app es un vector mas de ataque") [^225^]. Tchijova establecio un principio etico de atribucion: cada IA figura como autora formal porque "realmente aportaron" [^225^].

#### 8.2.3 Claude Code como co-autor GitHub con commits directos

El historial de commits de vigia-intent-analysis registra a Claude como co-autor explicito mediante `Co-Authored-By: Claude <noreply@anthropic.com>` en correcciones documentales, actualizaciones de especificaciones y fixes de licencia [^747^] [^748^]. VIGIA se inserta en una tendencia de mayor alcance: SemiAnalysis (febrero 2026) reporta que Claude Code autoria ~4% de los commits publicos de GitHub (~135,000/dia), con crecimiento de 42,896x en 13 meses y proyeccion de 20%+ para finales de 2026 [^880^] [^877^].

### 8.3 Gobernanza y Roadmap

#### 8.3.1 Protocolo P2: especificacion determinista de 658 lineas con 22 vectores canonicos

El **Protocolo P2** rige la reproducibilidad de scoring en VIGIA con tres niveles de compliance: *Strict* (auditoria forense), *Reference* (DFIR de produccion) y *Accelerated* (tiempo real, sin claim de compatibilidad P2) [^223^]. La version 2.8-Draft (mayo 2026) define invarianza monotonica y temporal, resistencia adversarial contra denormales y fuzzing, abstencion formalizada, cadena de custodia y canonicalizacion `Decimal.quantize()` HALF_EVEN [^871^].

#### 8.3.2 Licencia Apache 2.0 y clausula de revocacion P2 para forks

VIGIA opera bajo **Apache 2.0** con un sistema de gobernanza de dos capas: la licencia legal permite forks libremente, pero P2 revoca retroactivamente el derecho a reclamar compatibilidad si el derivado usa terminologia prohibida —"AI detector", "authenticity score", "humanity index"— en cualquier material orientado al usuario [^223^] [^871^]. Las frases permitidas son neutras epistemologicamente: "distributional variability measure", "compressibility estimate". Esta clausula es no negociable e independiente del paso de vectores tecnicos [^871^].

#### 8.3.3 Estado P2 frozen y direcciones futuras

El archivo `WHAT_IS_NEXT.md` define tres lineas de investigacion post-hackathon: la abduccion como accion embodied (Magnani), la formalizacion logica de generacion versus seleccion de hipotesis (Aliseda), y la implementacion computacional multi-hipotesis (Nishida) [^228^]. Las decisiones tecnicas se toman por consenso multi-IA con auditoria comunitaria; los mantenedores formales son el AI Collective completo y los commits requieren firma forense [^871^].

VIGIA demuestra que la convergencia DFIR-IA no requiere un equipo tradicional ni presupuestos millonarios. Requiere un orquestador humano con vision clara de que propiedades formales exigir, un colectivo de LLMs con roles diferenciados, y una especificacion tecnica que defina condiciones de compatibilidad con precision suficiente para sustentar claims legales. El ecosistema MCP forense —con Valhuntir, volatility3-mcp y las extensiones del hackathon FIND EVIL! (4,178+ participantes) [^40^]— indica que este modelo de integracion se consolidara como estandar de la industria en el horizonte 2026-2028.
## 9. Conclusiones e Implicaciones Estratégicas

La investigación multi-dimensional de VIGIA —ocho capítulos, 272+ búsquedas web, análisis de código fuente directo y revisión de literatura académica en filosofía de la ciencia, semiótica e inteligencia artificial— converge en un hallazgo central: VIGIA no es meramente una herramienta forense, sino un proto-tipo de cómo la filosofía, la ingeniería de software y el derecho pueden converger para resolver problemas que ninguna disciplina podría abordar sola. Este capítulo sintetiza los insights cruzados, articula sus implicaciones para el campo DFIR (*Digital Forensics and Incident Response*), documenta honestamente las limitaciones identificadas y formula recomendaciones accionables para tres audiencias.

### 9.1 Insights Cruzados de la Investigación

El documento de verificación cruzada confirma 65 hallazgos con calificación global de confianza ALTA: 26.5% *High Confidence* (≥2 dimensiones), 41.2% *Medium Confidence* (fuente autoritativa), y 10.3% en *Conflict Zones* (inconsistencias documentadas) [^853^]. Sobre esta base, cuatro insights estructurales definen el significado de VIGIA.

#### 9.1.1 La paradoja de la transparencia total: conocimiento del atacante como ventaja defensiva

VIGIA convierte la transparencia extrema —código abierto Apache 2.0, determinismo bit-a-bit, verificador con stdlib únicamente— de una vulnerabilidad potencial en una ventaja asimétrica. El atacante puede conocer exactamente cómo opera CAIE, pero el costo de fabricar evidencia que sobreviva a todas las capas de verificación (CAIE → scoring → spoofability → Devil's Advocate) se vuelve prohibitivo [^853^]. La paradoja es que al eliminar la seguridad por oscuridad, el atacante pierde la asimetría de información que explotar. La única vía para engañar a VIGIA es fabricar evidencia perfectamente consistente en múltiples capas —un salto cualitativo que aumenta el costo de los ataques en órdenes de magnitud. Como señala el caso Cybercheck: herramientas de caja negra son excluidas de tribunales por falta de transparencia; VIGIA elimina este obstáculo por diseño [^184^].

#### 9.1.2 La filosofía como stack tecnológico: Peirce → clases Python

VIGIA constituye el primer sistema de software que implementa la semiótica peirceana como **arquitectura de datos ejecutable**, no como metáfora. Las tres categorías fenomenológicas de Peirce (Firstness, Secondness, Thirdness) se materializan en `Artifact`, `CAIE` y `AbductiveHypothesis` [^19^]. La distinción magnaniana entre abducción teórica y manipulativa justifica el Devil's Advocate [^21^]. Las máximas de Grice operan como reglas de detección: violación de Calidad → *weaponized incompetence*; violación de Cantidad → *significant silences*; violación de Modo → *excessive digital perfection* [^24^]. La mayoría de los sistemas aplican filosofía post-hoc; VIGIA la usa como blueprint arquitectónico. Este salto legitima la filosofía de la ciencia como disciplina de ingeniería aplicable.

#### 9.1.3 Democratización asimétrica: ofensa $300, defensa por cocinera + 7 LLMs

El ataque y la defensa se democratizan mediante IA de forma asimétrica. La ofensa lo hace hacia abajo: *EDR killers* a $300 [^782^], *breakout time* de 29 minutos [^836^], 82% de detecciones *malware-free* [^838^]. La defensa lo hace hacia arriba: Anna Tchijova, cocinera sin formación IT, construyó un sistema forense de grado Daubert con 7 LLMs [^222^][^225^]. La asimetría estructural favorece a la defensa porque el determinismo bit-a-bit es inherentemente democrático: cualquiera puede verificarlo sin hardware especial. VIGIA sugiere que la democratización IA cambia las reglas cuando la herramienta defensiva es transparente y verificable.

#### 9.1.4 El costo de la mentira como nueva métrica en DFIR

VIGIA introduce una nueva métrica: el **costo computacional de fabricar evidencia convincente**. Tradicionalmente DFIR mide detección versus evasión; VIGIA pregunta: *¿cuánto le cuesta al atacante producir una mentira que parezca verdad?* La respuesta se deriva del motor abductivo, CAIE y la tabla de spoofability de 17 tipos de evidencia —desde IP geolocation (0.90, trivial de falsificar) hasta memory process (0.15, estructuralmente irrefutable) [^853^]. Un atacante que falsea un log (fácil) debe ahora falsear también la memoria (difícil), los timestamps (muy difícil) y las correlaciones cross-artifact (casi imposible). Cada capa multiplica el costo de la mentira.

**Tabla 9.1 — Insights Principales de la Investigación VIGIA**

| Insight | Fundamento | Implicación Estratégica |
|---------|-----------|------------------------|
| Paradoja de la transparencia total | Código abierto + determinismo desplazan la competencia del "ocultamiento" al "costo de la mentira" | Herramientas deterministas tienen ventaja estructural sobre cajas negras [^853^][^184^] |
| Filosofía como stack tecnológico | Peirce → `Artifact`/`CAIE`/`AbductiveHypothesis`; Grice → reglas de detección | La filosofía de la ciencia se legitima como ingeniería de software [^19^][^21^] |
| Democratización asimétrica | Ofensa: $300/EDR killer; Defensa: cocinera + 7 LLMs + determinismo | La barrera de entrada para defensa forense de alta calidad se desploma [^782^][^222^] |
| Costo de la mentira como métrica | Spoofability 0.05–0.90 multiplicada por 9 reglas CAIE | El ROI de forense avanzada se mide en costo impuesto al atacante [^853^][^26^] |

La tabla revela un patrón transversal: cada insight implica una **inversión de una relación asimétrica** tradicional —transparencia de debilidad a fortaleza, filosofía de reflexión a ingeniería, escasez de recursos a ventaja arquitectónica, detección pasiva a optimización adversarial.

### 9.2 Implicaciones para el Campo DFIR

#### 9.2.1 Convergencia DFIR-IA inevitable: MCP + SIFT + benchmarks emergentes

MCP (*Model Context Protocol*) se consolida como protocolo de comunicación entre analistas e IA, conectando LLMs con 500+ herramientas forenses [^55^]. Protocol SIFT demostró en RSAC 2026 que un agente autónomo completa un análisis forense de disco C: en 14 minutos 27 segundos —trabajo que manualmente toma una semana [^42^]. Los benchmarks emergentes (DFIR-Metric con 1,350 ítems [^513^], AutoDFBench con 10,968 escenarios [^688^]) confirman la convergencia. La pregunta no es *si* todo analista usará herramientas IA-asistidas, sino *cómo*. VIGIA ofrece un modelo: LLMs para orquestación y narrativa, motores formales para veredicto.

#### 9.2.2 El marco legal como blueprint de arquitectura: Daubert como especificación funcional

VIGIA invierte la relación derecho-tecnología: utilizó Daubert, FRE 702 e ISO 27037 como **especificaciones funcionales de arquitectura** [^145^][^707^]. La testabilidad exige `fractions.Fraction`; la revisión por pares exige código abierto; la tasa de error conocida exige aritmética determinista. Este modelo de *legal-first engineering* podría extenderse a software médico (FDA), financiero (SEC) y de votación (EAC).

#### 9.2.3 Semiótica forense como disciplina emergente con VIGIA como primera implementación

Crispino (*Towards a Forensic Semiotics*, 2024), Danesi (2023) y Leone (2021) definen la semiótica forense como el estudio de signos digitales como evidencia [^27^][^26^][^25^]. VIGIA la materializa computacionalmente: cada `Artifact` es un signo peirceano, cada `AbductiveHypothesis` un interpretante. Esto crea un ciclo de retroalimentación donde la herramienta valida la disciplina y la disciplina legitima la herramienta. En 5–10 años, la validación judicial de IoIs como metodología admisible bajo Daubert sería un hito disciplinario.

### 9.3 Limitaciones y Áreas de Mejora

#### 9.3.1 Muestra empírica limitada: necesidad de corpus más amplio

Los 70 casos evaluados (18 reales + 52 canónicos) en modo Python son insuficientes para sostener claims de precisión al 100% por sí solos. Ningún caso proviene de benchmarks independientes; todos los corpus canónicos fueron diseñados por el equipo VIGIA, con riesgo de *overfitting* [^513^][^688^]. La cifra de producción más representativa —134/136 (98.5%) en modo agente autónomo, sobre 136 casos de Dominio A+B+C— se documenta en §7.1.4 y está sujeta a la misma cautela metodológica: corpus diseñado internamente, sin validación contra benchmarks externos como DFIR-Metric o AutoDFBench.

#### 9.3.2 Inconsistencias numéricas documentadas (CZ-01, CZ-07)

El verificador cruzado identificó dos conflict zones. **CZ-01** (RESUELTO, 2026-06-22): la discrepancia entre 10 casos diseñados por Tchijova, 18 documentados en Dim06 y 136 reportados para métricas del agente [^853^] no era un error de conteo, sino la conflación de dos metodologías de evaluación distintas y no superpuestas: (a) el corpus de 125 casos (70 empíricos + 55 tests EBS v1) corrido en **modo Python** vía `run_all_cases.py`/`verify_ebs_v1.py`, y (b) la suite de regresión completa de **136 casos** (Dominio A+B+C) corrida en **modo agente autónomo** vía `run_all_agent.py` → `vigia_agent.py`, con resultado 134/136 (98.5%), documentado en §7.1.4. Una vez separadas correctamente ambas metodologías, no queda inconsistencia numérica: son dos mediciones legítimas con alcance distinto, no el mismo conjunto contado dos veces. **CZ-07**: el Brier Score de 0.0813 (excelente calibración) coexiste con FPR@0.5 = 1.0 [^515^]. El modelo puede estar bien calibrado pero tener poder discriminativo limitado. Esta inconsistencia (no relacionada con CZ-01) requiere investigación antes del uso en contextos legales.

#### 9.3.3 El FPR en calibración: requiere investigación adicional

El FPR@0.5 = 1.0 sugiere que el calibrador asigna probabilidades >0.5 a todos los casos, incluyendo benignos. Se requiere análisis de curvas ROC y evaluación en datasets balanceados antes de considerar el sistema forensemente validado.

### 9.4 Recomendaciones

#### 9.4.1 Para profesionales de DFIR: evaluar VIGIA como capa de intencionalidad

Los respondedores de incidentes deberían evaluar VIGIA como **capa de intencionalidad** complementaria a sus herramientas EDR existentes. Los 5 IoIs pueden operar sobre artefactos ya recolectados, proporcionando interpretación que pregunta *por qué* la evidencia se ve así. El modo 0 tokens [^225^] lo hace viable para entornos aislados donde herramientas basadas en nube son inutilizables. La prioridad inmediata es validar los IoIs contra datasets internos con *ground truth* conocido.

#### 9.4.2 Para desarrolladores: adoptar aritmética exacta en herramientas forenses

Los ingenieros deberían documentar todas las operaciones de punto flotante y justificar su necesidad. Los casos Pentium FDIV ($475M), Patriot Missile (28 muertos) y Ariane 5 ($370M) demuestran que errores de representación numérica tienen consecuencias graves [^695^][^705^][^708^]. VIGIA demuestra que el determinismo absoluto es alcanzable con `fractions.Fraction` para umbrales y `decimal.Decimal` para cómputo intermedio [^152^]. Los abogados defensores pueden argumentar Daubert contra herramientas que produzcan resultados diferentes en x86 versus ARM.

#### 9.4.3 Para legisladores: considerar el determinismo computacional como requisito legal

Los responsables de políticas deberían considerar el **determinismo computacional** como factor explícito en estándares de admisibilidad. La enmienda FRE 702 (2023) requiere que el proponente demuestre confiabilidad [^143^]; un método que produce resultados distintos en dos máquinas no puede ser confiable en sentido legal. La recomendación es incorporar *repeatability* bit-exact —demostrable mediante hash SHA-256 reproducible— como factor Daubert para herramientas forenses computacionales [^680^].

La investigación concluye con una pregunta abierta: si una cocinera sin formación IT, orquestando 7 LLMs con recursos mínimos, puede construir un sistema forense de grado Daubert en meses —*¿qué más es posible cuando la filosofía de la ciencia se convierte en especificación de arquitectura, el determinismo en requisito legal, y la transparencia en ventaja estratégica?* VIGIA no responde esta pregunta. La hace inevitable.
