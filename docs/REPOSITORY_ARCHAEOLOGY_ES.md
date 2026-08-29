# Arqueología del Repositorio — Cómo llegó a existir VIGÍA

> [English version](./REPOSITORY_ARCHAEOLOGY.md) ·
> Dossier HTML acompañante: [`repository_archaeology.html`](./repository_archaeology.html)

**Fecha:** 2026-08-29
**Alcance:** el repositorio completo en `claude/archaeologist-architecture-analysis-r48jxg`
(HEAD desciende de `4c406ea`, el merge del PR #22).
**Pregunta que responde:** no *qué hace el sistema* — eso lo cubren los docs de
estado técnico — sino *cómo llegó a tener esta forma*: qué hechos
arquitectónicos son deliberados, cuáles son accidente histórico, qué
invariantes existen solo en los tests, qué APIs se diseñaron alrededor de
restricciones que ya no existen, y qué conserva el código que nadie podría
reconstruir a partir de la documentación sola.

**Método.** Cada afirmación lleva etiqueta:

- **[OBS]** — leída directamente de un archivo/línea citado, un commit o la
  salida de un comando.
- **[INF]** — inferencia a partir de observaciones cruzadas; se nombra la
  evidencia discriminante.

Se corrieron tres barridos de excavación en paralelo (ruta del veredicto e
invariantes; abstracciones redundantes y fósiles; narrativa histórica desde los
documentos), y las afirmaciones de mayor impacto de cada barrido se
re-verificaron de forma independiente contra los archivos vivos antes de
incluirlas. Donde una afirmación no pudo discriminarse, se preservan ambas
hipótesis — según la doctrina del propio proyecto de que una hipótesis refutada
o indecidible es un resultado, no un fracaso
(`docs/ENGINEERING_DISCIPLINE.md` §1.3).

Una nota metodológica: este repositorio documenta sus propios fósiles mejor de
lo que la mayoría de los repositorios documenta su código vivo.
`attic/README.md`, `docs/FOSSIL_HUNT_20260711.md`,
`docs/CALIBRATION_ARCHAEOLOGY_20260723.md`, `docs/B123_EXCAVATION_20260723.md`
y el registro de bugs de 11.000 líneas son fuentes primarias escritas por el
proyecto sobre sí mismo. Este informe las contrasta con el código en lugar de
repetirlas.

---

## 1. Historia de formación: los estratos

### 1.1 Tres reinicios de git — la historia es más joven que el proyecto

**[OBS]** La historia git de este repositorio contiene 125 commits entre
2026-07-21 y 2026-08-28, con **tres commits raíz independientes**
(`6e5eb7f`, `ccd3e33`, `69da100`), cada uno un snapshot completo de ~3.000
archivos (3034 / 3039 / 3046 respectivamente), unidos por merges ordinarios
(PR #11, `Merge remote-tracking branch 'origin/main'`).

**[OBS]** Los documentos citan commits que acá no existen. De 85 cadenas de
siete dígitos hexadecimales citadas como commits en `docs/*.md` y
`BUGS_HISTORICO.md`, **77 no resuelven a nada en este repositorio** — p. ej.
`BUGS_HISTORICO.md:4085` cita los commits de fix `03f6c10`, `22f6edc`,
`b981803`, `e0e7be0` fechados 2026-07-07, dos semanas antes del primer commit
de este repo.

**[OBS]** El propio proyecto registra un horizonte aún anterior:
`docs/FOSSIL_HUNT_20260711.md:307` — "El historial git empieza en el import
squasheado `dbba7ca` (2026-07-05)" — un commit ausente acá también. Y
`BUGS_HISTORICO.md` (B-145) registra que la historia fina solo fue recuperable
"tras des-shallowear el clon".

**[INF]** Hubo entonces al menos tres horizontes de historia: un repo de
trabajo cuyos commits sobreviven solo como hashes huérfanos en el registro; un
import squasheado el 2026-07-05 (`dbba7ca`); y el import a GitHub del
2026-07-21, ensamblado a su vez desde tres snapshots paralelos de árbol
completo. El desarrollo corrió en simultáneo en la máquina de la mantenedora
(`/home/labestiadevigia/vigia-repo`, ruta todavía hardcodeada en
`launch_vigia_mcp.sh:2` y `scripts/clean_thinking_artifacts.py:15`) y en
sesiones de agente remotas que partían cada una de un snapshot subido sin
ancestro común. La consecuencia para cualquier arqueólogo futuro: **la
cronología verdadera del proyecto es el registro de bugs, no git** — el primer
commit de GitHub ya referencia B-171..B-205.

Dos hipótesis sobre los reinicios se discriminan en §10 (P5).

### 1.2 Línea de tiempo de las eras

Todas las fechas son 2026. Fuentes: fechas embebidas en archivos, el campo
`Detectado en` del registro de bugs, la tabla de auditorías de `SECURITY.md` y
git.

| Período | Era | Evidencia clave |
|---|---|---|
| 22 feb | Escena de origen: RSAC, la demo "find evil" de Rob T. Lee; Protocol SIFT | `docs/academic/VIGIA_RESEARCH_REPORT.md:14` |
| 24 abr | Artefacto fechado más antiguo: "Hito 1 COMPLETADO" | `docs/hito_1_estado.md:3` |
| 28 abr | Se genera la DB de patrones ("Standard: SANS_FIND_EVIL_2026", "110+ forensic cases") | `vigia_patterns_migration.sql:2-4` |
| abr | Cuatro rondas de auditoría de seguridad (DeepSeek 16 fixes; el CAIE nace en la ronda 3 de Kimi) | `SECURITY.md:305-308` |
| abr–may | Ola de calibración 1: pista de LR empírico con KDE + Ledoit-Wolf — nunca cableada | `docs/CALIBRATION_ARCHAEOLOGY_20260723.md:73-78` |
| 2 may | **La encarnación anterior**: motor de recomendaciones v3.1, vocabulario de contención Kubernetes | `vigia_recommendation_engine_v3.1_SAFE.sql:20-23` (§5.3) |
| 18 may | Dossier técnico v1.0; el filtro por substring del TCV se amplía con un comentario que admite que no es reproducible bajo Daubert | `docs/FOSSIL_HUNT_20260711.md:79` |
| ~14 jun | **Cierra la entrega de SANS FIND EVIL 2026** — [INF] de "2026-06-28, día 14 post-hackathon" | `BUGS_HISTORICO.md:2186` |
| 23–27 jun | Barrido post-hackathon de crashes: B-001..B-018 (UnboundLocalError, plomería de imports, dependencias faltantes) | `BUGS_HISTORICO.md` |
| 28 jun | Sesión de Epistemic State Fuzzing: B-019..B-030 (ABSTAIN colapsando a NOISE, contradicciones de estado de veredicto) | `BUGS_HISTORICO.md:2186-2320` |
| 3–11 jul | Era de doctrina: gates de corroboración, monotonicidad, el descubrimiento del label leak y la reconstrucción de la métrica (B-075) | `docs/ACCURACY.md:67-77` |
| 5 jul | Import squasheado `dbba7ca` — primer reinicio de historia | `docs/FOSSIL_HUNT_20260711.md:307` |
| 10 jul | Se sella la doctrina del techo SUSPICION L-067 "collective + Anna's signature" | `KNOWN_LIMITATIONS.md:2187` |
| 11–14 jul | Cacerías de fósiles I/II; auditoría de arqueología de módulos (B-117 veredictos invertidos; −5.491 líneas) | `docs/FOSSIL_HUNT_20260711*.md`, `SECURITY.md:311` |
| 12 jul | Gate de acumuladores Fraction: dos flips de veredicto sellado por orden de emisión de floats, corregido bajo un gate de identidad byte a byte sobre el corpus | `docs/FRACTION_GATE_RECORD_20260712.md:41-72` |
| 13 jul | Ollama degradado tras el experimento ciego (B-111, N=2, salida estocástica) | `BUGS_PENDIENTES.md:79-135` |
| 21 jul | **Import a GitHub (segundo reinicio visible)**; la auditoría de Codex aterriza B-153..B-205 en un día | `git log`; `docs/CODEX_AUDIT_2026-07-21.md` |
| 23 jul | Día de triple arqueología: arqueología de calibración, excavación B-123, auditoría externa zone38; el centinela de paridad ES/EN se promueve a guarda dura | tres docs; `tests/test_registry_integrity.py:146-160` |
| 25 jul | El registro de bugs se parte en HISTORICO/PENDIENTES; auditoría epistemológica "Ronda 2" | `BUGS_HISTORICO.md:1-12` |
| 31 jul | Se integra el kernel epistémico (arquitectura de Kimi, revisión de ChatGPT, integración de Claude) — deliberadamente fuera de la ruta del veredicto | `docs/EPISTEMIC_KERNEL.md` |
| 1 ago | Infraestructura de mutation testing; línea base 40,8% sobre 3 módulos; el único cluster de mensajes de commit en español | `docs/MUTATION_BASELINE.md`; git log |
| 9 ago | Vuelve DeepSeek: 3 de 5 hallazgos refutados; el scorer queda sin modificar "per its own delicacy" | `docs/DEEPSEEK_AUDIT_20260809.md` |
| 12 ago | B-227: la suite completa corrió **cero tests** en el entorno mínimo documentado | `BUGS_HISTORICO.md:10524` |
| 15 ago | Se retira el prefijo de commit `POST HACKATHON` | `docs/ENGINEERING_DISCIPLINE.md:21-23` |
| 27–28 ago | Consolidación de docs; **web UI** (PR #22) — la primera GUI, de una autora que dejó registrado que "una app es un vector más de ataque" | git log; `docs/academic/VIGIA_RESEARCH_REPORT.md:592` |

**[OBS]** El carácter de los bugs cambia a través de los estratos, y esa es la
señal más clara de la maduración del proyecto: las entradas tempranas son
crashes (`UnboundLocalError`, imports rotos); las tardías son *epistémicas* —
un log sellado que fabrica la fórmula que dice haber usado (B-223), un loop de
auto-corrección estructuralmente inerte (B-224), un campo JSON que tenía
autoridad de veredicto en silencio (B-225), una suite de tests que no corría
nada (B-227). El modo de falla que el proyecto llegó a temer no era romperse —
era **aparentar funcionar**.

### 1.3 Quién lo construyó

**[OBS]** `AUTHORS.md` documenta un proceso de formación inusual: una
investigadora principal humana (Anna Tchijova — según
`docs/academic/VIGIA_RESEARCH_REPORT.md:592`, cocinera profesional sin
formación formal en IT, trabajando desde Argentina) dirigiendo un "Colectivo
IA VIGÍA" de siete LLMs distintos con roles nombrados y subsistemas
atribuidos: Claude (integración, puente MCP), Gemini (el marco IoI), Kimi
(CAIE y el kernel epistémico), DeepSeek (auditoría de seguridad), Qwen
(determinismo de floats, hardening de contenedores), Grok (matemática del
scorer), ChatGPT (revisión adversarial). **[OBS]** Un octavo modelo, Codex,
escribió la tanda de auditoría más grande del registro (B-153..B-205,
2026-07-21) y no figura en `AUTHORS.md` — [INF] una llegada tardía nunca
retro-agregada.

Esta autoría políglota explica hechos estructurales que de otro modo
parecerían descuido: gemelos divergentes de la misma función, dos esquemas de
sellado nunca reconciliados, y una cultura de auditoría en la que el hallazgo
de cada modelo se trata como "una afirmación, no un hecho" hasta verificarlo
contra el archivo vivo (`docs/ENGINEERING_DISCIPLINE.md` §4.1, §6).

---

## 2. Lo que es deliberado

Estas decisiones tienen justificación escrita contemporánea, mecanismos de
enforcement y, en varios casos, gates de aceptación medidos. Son diseño, no
accidente.

### 2.1 El LLM está fuera de la ruta de decisión — y el enforcement es real

**[OBS]** El Modo 1 no contiene ninguna llamada a un LLM. `vigia_scorer.py`
tiene cero ocurrencias de `llm`/`anthropic`/`ollama`; las únicas ocurrencias
en `sift_orchestrator.py` y `vigia_agent.py` son *aserciones negativas* ("el
LLM no puede anular este gate", `sift_orchestrator.py:476`; "Narrative: 100%
deterministic — no LLMs in core analysis", `vigia_agent.py:2155`).

**[OBS]** Donde salidas adyacentes al LLM amenazaron con filtrar autoridad de
vuelta, el proyecto cerró el canal con sellos de procedencia en lugar de
confianza: el fix B-225 (`vigia_scorer.py:1590-1617`) escala por un veredicto
Grice solo cuando `grice_source == "live_grice"` — sellado *después* de correr
el auditor vivo (`sift_orchestrator.py:1176-1186`) — y enruta toda afirmación
declarada sin verificar a una puerta de autoridad que fuerza ABSTAIN en lugar
de ignorarla. La capa narrativa tiene su propia guardia:
`vigia/llm/hallucination_guard.py:9-14` ("the narrative cannot amplify the
evidence") y los detectores `ROLE_OVERRIDE`/`VERDICT_COERCION` del auditor
narrativo C3 (B-124).

**[OBS]** La frase **"zero verdict authority"** se repite textual en al menos
cinco módulos independientes (`vigia/tools/paired_review.py:9`,
`vigia/core/case_linkage.py:25`, `vigia/vigia_sift_bridge.py:3540`,
`vigia/core/signal_quality_shadow.py`,
`vigia/pipeline/vigia_integration_bridge.py:390`) — un principio
arquitectónico que se volvió modismo de la casa.

**[INF]** Deliberado — pero ver §10 (P1) para la historia de origen por capas:
el principio, la economía y el enforcement tienen tres cumpleaños distintos.

### 2.2 Sellado externo: un motor no debe poder sellar su propia mentira

**[OBS]** `vigia/core/ebs_v1.py:20-36`: "**ABSOLUTE RULE: This module contains
DATA ONLY** … A bundle that hashes itself allows a compromised engine to seal
its own lie." Espejado en `vigia/core/bundle_builder.py:12-16`. El verificador
de terceros está deliberadamente fuera del paquete y es stdlib puro:
`forensics/verify_ebs_v1.py:7-12` — "GARANTIA DE INDEPENDENCIA TOTAL … Si el
verificador necesita importar el codigo de produccion, el sistema no es
auditable por terceros."

### 2.3 El log tamper-evident evolucionó contra una taxonomía de ataques enumerada

**[OBS]** `vigia/core/tool_log_chain.py:8-14` documenta la debilidad de v1 en
el propio módulo ("solo `result_summary` está protegido … NO usar para
escribir"), y `tests/test_hash_chain_hardening.py:1-24` nombra siete ataques
concretos (A1..A7) que "ANTES del hardening pasaban en silencio" — edición de
campos, edición de la última entrada, recomputación de la cadena sin clave,
hashes de bundle fabricados, truncamiento de cola, alteración de checkpoints.
El residual de v2 (borrar las últimas N entradas deja la cadena internamente
consistente) se encontró después, se reprodujo y se cerró con un ancla de
punta a nivel bundle (`tests/test_r3_5_chain_tip_truncation.py:1-30`;
`docs/REDTEAM_ROUND3_EMERGENT.md:338-345`). La verificación emite *caveats*
legibles por máquina para cadenas legacy o sin ancla en lugar de pasar en
silencio (`tool_log_chain.py:284-297`).

### 2.4 El techo SUSPICION es doctrina sellada, aplicada recién tras medición

**[OBS]** Tres mecanismos distintos que suelen confundirse:

1. El vocabulario del scorer simplemente no tiene peldaño INTENT — la cadena
   `INTENT` no aparece en `vigia_scorer.py`. Por encima del umbral de MALICE
   sin rama de corroboración abierta, el veredicto cae a SUSPICION
   (`vigia_scorer.py:1534-1543`, el gate anti-drowning B-068).
2. El gate de corroboración Daubert rechaza candidatos de fuente única
   *pre-emisión* (`CLAUDE.md:555-562`).
3. L-067, el techo doctrinal para evidencia confinada a un solo canal de
   fabricación: "Whoever controls the disk controls all of those sources at
   once" (`KNOWN_LIMITATIONS.md:2201-2207`) — sellado el 2026-07-10 con la
   firma de la mantenedora, y aplicado recién tras un gate medido: "0 flips
   across 291 bundles, corpus 167/199 identical, byte-identical runner
   output."

**[OBS]** El techo solo capea hacia abajo — "nunca eleva un ABSTAIN/NOISE"
(`vigia_agent.py:226-229`). La misma disciplina aparece en la historia de
B-097: la regla de recuperación pre-registrada se midió, expuso 3 casos, y
**no se aplicó** (fail-closed) hasta que existió una validación de triple
fuente (`vigia_agent.py:236-247`).

### 2.5 Retención de proveniencia en lugar de borrado

**[OBS]** `attic/README.md` define un protocolo de retiro: los archivos se
mueven solo tras verificación de cero referencias, conservan su layout
original y llevan justificación por archivo más — inusual — una lista de
NO-movidos con motivos. Las cacerías de fósiles se rotulan "cacería y
diagnóstico. NO contiene fixes" y abren con un tag de restauración. El
registro de bugs es append-only ("los bugs resueltos no se eliminan, solo se
archivan", `BUGS_HISTORICO.md:1-12`) y se ofrece explícitamente como lectura
de red team. **[INF]** Varios fósiles sobreviven *porque* un documento de
auditoría o un test los cita como evidencia — borrarlos rompería un audit
trail, no un build (ver §9).

### 2.6 Degradación honesta como postura de todo el sistema

**[OBS]** Patrones recurrentes y aplicados: ABSTAIN cuando la proveniencia
colapsa, en lugar de un NOISE confiado (`vigia_scorer.py:1401-1414`, "un
veredicto inadmisible no puede presentarse como NOISE confiado"); ABSTAIN ⊥
`is_conclusive=True` (B-027, `vigia_agent.py:1483-1496`); todo lo no
calibrado cableado en modo SHADOW/WARN con "cero autoridad de veredicto"
(`vigia/core/signal_quality_shadow.py`, B-116); la ausencia de
`baselines_institucionales.yaml` *degrada* el nivel del bundle con un warning
en lugar de fallar o fingir (`vigia/pipeline/vigia_integration_bridge.py:937`).

---

## 3. Lo que es accidente histórico

### 3.1 La migración flat→package nunca se terminó — en ninguna dirección

**[OBS]** Los directorios de raíz `engine/`, `governance/`, `models/` y parte
de `forensics/` son shims de una línea `from vigia.core.X import *`; en
simultáneo, `vigia/core/vigia_scorer.py` re-exporta *hacia afuera* al
`vigia_scorer.py` de raíz, y `vigia/tools/vigia_entanglement.py` /
`vigia_adversarial_nlp.py` son shims "COMPATIBILITY STUB" para módulos que
asumían el otro layout. **[OBS]** Los módulos canónicos todavía llevan su ruta
pre-mudanza en sus propios docstrings — `vigia/core/resource_optimizer.py:2`
dice `vigia/engine/resource_optimizer.py`, un directorio que **nunca
existió**. **[INF]** La migración corrió módulo a módulo en ambas
direcciones, nunca se completó, y el estado intermedio se congeló porque
ahora hay tests que dependen de él: CI corre
`tests/integration/test_ebs_v1_integration.py` directamente (40+ imports de
los nombres flat, `.github/workflows/vigia-forensic-ci.yml:55`) mientras la
suite pytest lo excluye.

**[OBS]** La jerarquía duplicada causó un bug real de producción:
`vigia/forensics/` ensombrece al `forensics/` de raíz en `sys.path` según el
orden de import (B-097), corregido con un workaround de importlib por ruta
absoluta y un test de regresión que recrea el shadow a propósito
(`vigia/pipeline/pipeline.py:60-100`;
`tests/test_pipeline_verify_import_shadowing.py:40`). Y el healthcheck de
Docker todavía importa el layout flat: `Dockerfile:83` ejecuta
`from ebs_v1 import EvidenceBundle` — un módulo que ya no existe en la raíz y
un nombre de clase (`EvidenceBundle`) que no existe en ningún lado del árbol.
**[INF]** El healthcheck del contenedor viene fallando desde la migración;
nadie lo notó porque nada lo consume.

### 3.2 Exit codes numerados por cronología, no por severidad

**[OBS]** `vigia_agent.py:100-105`: `0=NOISE, 1=MALICE, 2=ERROR, 3=INTENT,
4=ABSTAIN, 5=SUSPICION`. La banda 0/1/2 es la tríada Unix clásica para una
herramienta cuyo hackathon se llamaba literalmente FIND EVIL ("0=no evil,
1=evil, 2=error"); 3, 4 y 5 se fueron agregando a medida que los veredictos
entraban al vocabulario — B-097 le dio a SUSPICION el código *nuevo* 5 porque
"INTENT conserva el 3 (contrato histórico)" (`vigia_agent.py:93-102`). El
orden de severidad y el orden numérico divergieron para siempre, y
`README.md:57` todavía documenta solo los códigos 0–3.

### 3.3 Un límite de dependencia sostenido por accidente durante meses

**[OBS]** `requirements.txt` (comentario B-227): el puente MCP hace
`from mcp.server.fastmcp import FastMCP`, que `mcp` 2.0 eliminó. "Until this
bound was declared, the only thing holding the line was `fastmcp`'s own
transitive `mcp<2`, which is an accident: **no module in this repo imports
`fastmcp`**, so a cleanup dropping it would have broken the MCP surface
silently." Hoy lo fija `tests/test_mcp_dependency_contract.py`.

### 3.4 Gemelos divergentes que se separaron

- **[OBS]** `phonetic_dict.json` existe en la raíz y en `data/` **con
  contenido distinto** (md5 diferentes). El loader consolidador
  (`vigia/phonetic_loader.py:22-38`) documenta la historia de las dos rutas,
  pero su ruta de prioridad 2 (`vigia/data/phonetic_dict.json`) no existe, y
  `vigia/tools/document_integrity.py:54` todavía hardcodea esa ruta faltante.
  [INF] La consolidación se escribió; un lector nunca se migró; las copias
  divergieron desde entonces.
- **[OBS]** `initial_templates.sql` e `initial_templates_v2.sql` son
  **byte-idénticos** (mismo md5) — un copiar-y-renombrar nunca reconciliado.
- **[OBS]** `_sanitize_grep_pattern` existe dos veces con cuerpos distintos —
  `vigia/vigia_sift_bridge.py:174` vs `vigia/security/sandbox.py:353` — "dos
  validadores de seguridad con semánticas divergentes para la misma
  superficie" (`docs/AUDITORIA_FUGA_INDIRECTA.md:170`). Ambos vivos.

### 3.5 Directorios de salida de tres convenciones

**[OBS]** `results/` (1.437 archivos, vivo), `vigia/results/` (salidas de
sesiones de agente, vivo), y `resultados/` — cuatro archivos de un solo caso,
referenciados por ningún código, [INF] un snapshot anterior a la convención
de nombres en inglés. `vigia/ui/normalizer.py:3` concede que el corpus
contiene "three [schema generations]". Análogamente, `docs_merged/` (193
archivos con nombre de hash) es el insumo de staging superado de una
reorganización documental cuyo manifiesto está commiteado
(`docs/academic/_reorganization_manifest.json`); un limpiador huérfano todavía
lo apunta con una ruta absoluta de la máquina de la autora.

### 3.6 La ceremonia del `prec=28`

**[OBS]** `vigia/tools/caie.py:120`: "prec=28 matches the Directiva 4
requirement." Ningún documento llamado "Directiva 4" sobrevive en el
repositorio (el rastro de comentarios dice "Qwen P0 + Red Team P0_CRITICO
Directiva 4", `caie.py:103`) — y **28 es la precisión por defecto de
`decimal` en Python**: el requisito manda lo que el lenguaje hace de todos
modos. Mientras tanto, el `_dround` propio del scorer
(`vigia_scorer.py:174-182`) configura el contexto Decimal y después usa el
`round()` nativo sobre floats, salteándolo. **[INF]** El comentario preserva
una autoridad desaparecida; el mecanismo que manda está parcialmente sin
usar. Es el fósil más puro del código: la ceremonia sobrevivió a su
legislador y a su ley.

### 3.7 Colisiones de registro por sesiones paralelas

**[OBS]** B-206/207/208 tuvieron que renumerarse a B-211/212/213 (commit
`c5fec4f`); L-051 colisionó y pasó a ser L-067, con la cicatriz de
renumeración documentada en el lugar (`KNOWN_LIMITATIONS.md:2192-2198`);
B-031..B-044 son retro-agregados ("[entrada retrospectiva 2026-07-23]") y
B-057 es un ID genuinamente desaparecido con cero referencias. **[INF]**
Sesiones de IA paralelas asignaban IDs sin verse entre sí — el registro es
fuente secundaria para la era pre-julio, reconciliada a posteriori.

---

## 4. Invariantes que existen solo en los tests

Reglas estructurales que un contribuidor descubre por un CI rojo, no por
ningún documento en prosa.

| Invariante | Aplicada por | ¿Documentada en prosa? |
|---|---|---|
| Los registros de bugs ES y EN deben contener el conjunto B-* idéntico, y la partición del 2026-07-25 debe seguir siendo verdadera | `tests/test_registry_integrity.py:143,173,190` | No — el docstring del test es la única declaración ("Un registro espejo que diverge en contenido deja de ser espejo") |
| Los dos wrappers FastAPI (`vigia_api`, `vigia.vigia_api`) deben exponer protocolo y fronteras idénticos | `tests/test_b168_api_contract_parity.py` + 4 hermanos | Solo en los tests ("A caller must not get a weaker protocol … merely by choosing the package import path") |
| La pipeline de scoring no debe importar el kernel epistémico | `tests/test_epistemic_kernel.py:443-464` (un `git grep` dentro de un test) | Sí (`CLAUDE.md`, `docs/EPISTEMIC_KERNEL.md`) — el caso raro donde prosa y test coinciden |
| `mcp<2` y el set de dependencias de CI deben coincidir con lo que el código importa | `tests/test_mcp_dependency_contract.py`, `tests/test_requirements_ci_contract.py` | Solo como comentarios dentro de los archivos de requirements |
| Toda copia alcanzable del canonicalizador — incluidos los verificadores stdlib cargados *por ruta de archivo* — debe codificar idéntico | `tests/test_canonicalize_lockstep.py:1-26` | No ("a divergence between verifier copies is a court-facing contradiction") |
| El paso DECISION de la traza de razonamiento debe igualar el veredicto sellado, y construir la traza debe dejar `bundle_digest` byte-idéntico | `tests/test_reasoning_trace_bundle_gate.py:9-16` | Solo docstring del módulo |
| El determinismo se afirma como igualdad **entre corridas**, nunca contra un score hardcodeado | `tests/test_determinism_sealed_verdict.py:16-23` | No — y es posiblemente la doctrina de testing más profunda del proyecto |
| Fronteras de decisión y cadenas centinela fijadas en el punto de corte exacto | `tests/test_collapse_decision_boundaries.py` | Sí — `CLAUDE.md:444-450` cita el resultado de mutación que lo motivó (77,94% cobertura, 13,8% mutation score) |
| La documentación de auto-corrección debe decir la verdad sobre su propia dormancia | `tests/test_b224_self_correction_docs_are_honest.py` | El test *es* el mecanismo de honestidad documental |
| Un flag de enriquecimiento sin setear no debe reportar un módulo huérfano como integridad activa | `tests/test_config_sentinel_orphaned_module_env_map.py:6-27` | No — "a sealed integrity report that would lie about its own subject" |

**[INF]** El patrón: tras quemarse dos veces con deriva de registros y una vez
con una suite que corría nada en silencio (B-227), el proyecto convirtió
promesas documentales en contratos ejecutables. Los tests son la constitución;
la prosa es comentario.

---

## 5. APIs diseñadas alrededor de restricciones que ya no existen

### 5.1 El modo primario de 0 tokens

**[OBS]** `docs/academic/VIGIA_RESEARCH_REPORT.md:592` cita a la autora: "como
no tenía dinero para Claude Code, casi todo VIGIA fue construido para modo
fallback o Ollama" — la restricción económica que hizo del Modo 1
determinista y sin LLM el *modo primario evaluado*. La restricción se
formalizó después como limitación L-055 ("API and subscription are separate
authentication products … Ollama fills that role"). Ver §10 (P1) para cómo
este origen de escasez convive con la justificación Daubert.

### 5.2 Fósiles de reglas del hackathon todavía vigentes

**[OBS]** `CLAUDE.md:530-538` todavía exige un bloque de uso de tokens en cada
informe "required for audit trail completeness under **SANS submission
rules**" — de una competencia que cerró en junio. `KNOWN_LIMITATIONS.md`
define el tag de estado `[FIX DESIGNED]` como "Application is deferred
**post-hackathon**" — un artefacto de la ventana de freeze convertido en
vocabulario permanente. El prefijo de commit `POST HACKATHON` sobrevivió dos
meses al evento antes de retirarse (2026-08-15). Los exit codes 0/1/2
codifican el nombre del propio hackathon ("0=no evil, 1=evil").

### 5.3 La encarnación Kubernetes

**[OBS]** `vigia_recommendation_engine_v3.1_SAFE.sql` (2026-05-02) crea las
tablas `recommendation_policies`/`recommendation_ledger` cuyo vocabulario de
acciones es respuesta a incidentes en Kubernetes — `ISOLATE_POD`,
`QUARANTINE_NAMESPACE`, `REVOKE_SA_TOKEN` — con una firma humana
`operator_hmac_signature` obligatoria, y un vocabulario de veredictos
(`REJECT`/`ABSTAIN`/`ESCALATE`) que no coincide con nada del motor actual. Su
gemelo Python sobrevive en `vigia/inference/recommendation_engine_v3.1.py` —
un nombre de archivo con un punto, que **no puede importarse como módulo
Python**; cero importadores. El sufijo `_SAFE` marca remoción de peligros
(sin triggers auto-ejecutables, sin bypass de firma). **[INF]** VIGÍA fue,
durante al menos una iteración de mayo 2026, un recomendador de contención
automática para un cluster K8s; el `RiskBoundedDecisionLayer` que consumía es
el único componente que sobrevivió al pivot — y el que B-117 después atrapó
emitiendo veredictos invertidos.

### 5.4 La era Ollama-primario

**[OBS]** `docs/DAUBERT_JUDICIAL.md:15-17` argumenta determinismo forzado vía
"fixed seed for Ollama (42)" — el caso de determinismo se escribió
originalmente para un despliegue de LLM local. El Modo 3 fue degradado a
no-primario sobre la base de un experimento ciego de dos corridas en el que
`hermes3:8b` alucinó campos de schema y devolvió JSON truncado (B-111,
`BUGS_PENDIENTES.md:79-135`; "El comportamiento es estocástico, no
determinista").

### 5.5 Fósiles de entorno

**[OBS]** `README.md:42` instala con `--break-system-packages` (la realidad
Ubuntu/PEP-668 de la SIFT Workstation); `launch_vigia_mcp.sh` hardcodea cada
ruta a `/home/labestiadevigia/` y no corre en ninguna otra máquina sin
editarlo; `CLAUDE.md` limita las investigaciones a 40 llamadas de
herramientas y tuvo que corregir su conteo de herramientas de un 21 
desactualizado a 22 (commit `266fd03`).

---

## 6. Abstracciones redundantes

| Abstracción | Duplicado de | Estado | Por qué persiste |
|---|---|---|---|
| Shims `engine/`, `governance/`, `models/`, `forensics/*` | `vigia/core/*` | Vivos solo para un test de integración legacy que CI corre directo | Media-migración congelada (§3.1) |
| `caie_legacy_root.py` (1.884 líneas) | `vigia/tools/caie.py` (3.469 líneas) | Muerto — cero importadores, excluido de la atestación del motor *en dos lugares con comentarios idénticos* (`vigia/core/bundle_builder.py:463`, `vigia/pipeline/pipeline.py:1399`) | Proveniencia: preserva el bug B-001 original en `caie_legacy_root.py:1464`, citado por el registro (§10, P7) |
| `vigia_api.py` vs `vigia/vigia_api.py` | entre sí | Ambos vivos; cinco tests de paridad vigilan la copia | Accidente promovido a contrato (§10, P6) |
| `sift_orchestrator.py` de raíz (88 KB, "shim de compatibilidad") | `vigia/sift/sift_orchestrator.py` (el rico) | Ambos vivos; el shim está en la ruta del Modo 1 | Dos generaciones de orquestador, confirmadas distintas por diff el 2026-06-19 (`docs/EXECUTION_MODES.md`) |
| Schema de bundle del agente vs bundles sellados EBS v1 | dos familias de sellado | Ambas vivas, "never reconciled into one schema, and probably won't be short-term" | Admitido abiertamente (`docs/EXECUTION_MODES.md:72-76`) |
| `vigia/core/vigia_scorer.py` | `vigia_scorer.py` de raíz | Re-export congelado después de que la copia divergiera con un `NameError` latente (B-055) | "Se congela como re-export para que NO pueda volver a divergir" |
| `vigia/abductive_intent_engine.py` + `vigia/tools/abductive_intent_engine.py` | un shim, duplicado | Ambos vivos | El shim de consolidación L-052 fue a su vez copiado en dos ubicaciones |
| `initial_templates.sql` / `_v2.sql` | byte-idénticos | Muertos ×2 | Nada carga ningún SQL de raíz |

**[OBS]** El censo del propio repo contó **144 nombres definidos en más de un
archivo con cuerpos distintos** (`docs/AUDITORIA_FUGA_INDIRECTA.md:166`). La
mayoría se resolvió; los dos nombrados como divergencias aún vivas
(`_sanitize_grep_pattern`, `to_caie_fracture`) siguen así.

---

## 7. API de facto — comportamiento del que se depende sin haberse prometido

Instancias de la ley de Hyrum, cada una con evidencia de consumo real:

1. **Exit codes 4 y 5.** `EXIT_ABSTAIN=4` y `EXIT_SUSPICION=5` existen y hay
   wrappers que dependen de ellos, pero `README.md:57` documenta solo 0–3.
2. **`gate_verdict`.** La pipeline anota que su único consumidor en el repo es
   `show_4_hashes.py` "(demo)" (`vigia/pipeline/pipeline.py:882`) — pero la
   salida de esa demo está citada en artefactos judiciales entregados
   (`results/real/VIGIA-REAL-008_amicus_curiae.md:46`). Un script de demo se
   volvió interfaz de reporte de facto.
3. **Campos del JSON de caso como entradas encubiertas.** Hasta B-225, un
   archivo de caso podía *declarar* `grice_verdict` y adquirir autoridad de
   veredicto — un campo de salida funcionando como API de entrada no
   documentada. El fix (sellos de procedencia + puerta de autoridad) es en
   efecto una deprecación formal de esa API accidental, hecha fail-closed: la
   declaración ahora fuerza ABSTAIN en lugar de ignorarse
   (`vigia_scorer.py:1601-1604`). L-072 registra que `semantic_role` sigue
   siendo una instancia abierta de la misma clase.
4. **`results/` quedó sellado bajo la cadena v1 para siempre.** Todos los
   bundles de `results/` se sellaron bajo la cadena de log v1, más débil
   (`vigia/core/canonicalize.py:57-59`); el archivo histórico solo es
   verificable al estándar v1. Declarado en comentarios de código; ausente de
   todo documento de cara al operador.
5. **`blind_cases_for_mcp/`** — generado una vez por un script hoy huérfano,
   luego registrado como raíz de evidencia de primera clase
   (`vigia/ui/evidence_paths.py:27`, ambas guías de instalación). El corpus
   sobrevivió a su generador.
6. **El Modo 1 puede sellar INTENT.** `CLAUDE.md:320-322` dice que el motor
   del Modo 1 no tiene peldaño INTENT — cierto para `vigia_scorer.py`. Pero
   el override L-036 de la capa agente fabrica `INTENT_DETECTED` cuando
   señales primarias superan z>3 sobre una hipótesis indeterminada
   (`vigia_agent.py:1072`), y `classify_agent_verdict` lo sella como INTENT
   con exit code 3. Hay bundles del corpus que lo llevan; hay tests que lo
   fijan (`tests/test_b058_abstain_classification.py:74`). La superficie de
   veredictos de facto es más ancha que la documentada.

---

## 8. Requisitos codificados solo en tests

Más allá de la tabla de invariantes de §4, tres archivos de test merecen nota
arqueológica:

- **`tests/test_collapse_decision_boundaries.py`** fija cadenas centinela
  exactas (`"sensor_independence"`), puntos de corte exactos de umbrales y el
  texto exacto de los mensajes de `explain()` — requisitos que no existen en
  ningún otro lado. Su docstring registra el origen: el mutation testing
  demostró que el umbral de MALICE "podía moverse a un valor inalcanzable sin
  que nada fallara". También anota con honestidad un olor de diseño que
  deliberadamente no corrigió (`explain()` recalcula su motivo independiente
  de `resolve()`).
- **`tests/test_b097_motor_suspicion_verdict.py`** codifica un requisito de
  *proceso*: sus tests "eran sentinelas `xfail(strict=True)` mientras estuvo
  NO APLICADO" — tests como mecanismo de pre-registro de un fix a la espera
  de su gate de aceptación.
- **`tests/test_b224_self_correction_docs_are_honest.py`** testea la
  *documentación*, no el código — el requisito de que los docs de VIGÍA no
  sobre-reclamen su capacidad de auto-corrección es él mismo ejecutable.

**[OBS]** Un falsificador declarado sigue sin implementar:
`docs/ENGINEERING_DISCIPLINE.md:209-211` declara el test propio de la
arquitectura — "swapping the narrator backend (Ollama ↔ hosted API) must
change only the wording — never the verdict" — y ningún test del árbol hace
ese swap. [INF] El falsificador insignia de la doctrina es, al momento de
esta excavación, prosa.

---

## 9. Sobrevivientes de refactors y por qué persisten

Sobrevivientes cuya razón de existencia ya no es evidente desde el código:

- **`apply_b047*.py`, `apply_b048.py`** — scripts de parche quirúrgico, ya
  aplicados, muertos como ejecutables. Estructurales como *documentación*: un
  test vivo requiere su efecto ("Requiere el guard aplicado
  (apply_b047_mathutils.py)", `vigia/tests/test_b047_correlation_groups.py:231`)
  y los docs de diseño citan sus anchors.
- **`scratchpad/q2_induction.py`** — el único archivo commiteado de un
  directorio explícitamente efímero, conservado porque una auditoría de
  seguridad sellada lo cita como su ancla de reproducibilidad
  (`docs/AUDIT_SEALED_VERDICT_SECURITY.md:6`).
- **`coverage_baseline_20260622.txt`** — una transcripción cruda de pytest de
  la máquina de la autora; cero referencias. Se volvió un índice accidental
  de módulos borrados (lista `vigia/pipeline/report_exporter.py`, ya
  eliminado) y un marcador de crecimiento: 169 tests colectados entonces,
  2.176+ pasando hoy.
- **`scripts/pre_release_check.py`** — contiene `BANNED_FILENAMES`, **un dict
  vacío cuyo contenido entero es un comentario** que explica por qué está
  vacío (la v2 baneada se borró; la v1 es canónica). Varias entradas de
  `BANNED_MODULES` sobrevivieron a sus objetivos; una (`ebs`) banea un módulo
  que todavía existe. El script de enforcement no lo invoca nada. Un registro
  de prohibiciones como puro sedimento.
- **`vigia/core/risk_bounded_layer.py:35-39`** — el docstring preserva el
  reporte de bug de un archivo *borrado* (la v2 huérfana que documentaba el
  fix P0-001 pero "nunca se cableó"). El sobreviviente carga el epitafio de
  su gemelo muerto.
- **`docs/VIGIA_THEME_SONG.md:26`** — todavía canta "Ledoit-Wolf and KDE
  quantifying the risk": maquinaria que la arqueología de calibración del
  2026-07-23 demostró que nunca estuvo en la ruta de decisión. La canción es
  la última referencia activa a la ola de calibración retirada.
- **`CollapseDecisionLayer`** — el módulo mejor testeado del repo (fronteras
  fijadas tras la línea base de mutación) solo es alcanzable vía
  `evaluate()`, que el scorer del Modo 1 nunca llama (`_vigia_score` llama a
  `detect_fractures()` directo, `vigia_scorer.py:832-869`). Su campo de
  contexto `independent_sources` lo puebla el CAIE y no lo lee nadie. [INF]
  Una capa de veredicto que migró fuera de la ruta del veredicto mientras su
  suite de tests — y su cita en `CLAUDE.md` como ejemplar de la ruta del
  veredicto — se quedaron.

---

## 10. Hipótesis históricas en competencia

Para cada patrón significativo: al menos dos explicaciones rivales, la
evidencia que discrimina, y un veredicto con el vocabulario de confianza del
propio proyecto. Siguiendo el método de la casa: no se asumió correcta la
explicación más obvia.

### P1 — ¿Por qué el LLM está fuera del loop de decisión?

- **H-A (doctrina primero):** diseñado desde primeros principios para
  admisibilidad Daubert.
- **H-B (escasez primero):** la falta de presupuesto de API forzó un build
  sin LLM; la necesidad se elevó después a principio.
- **H-C (guiado por incidentes):** la frontera se endureció respondiendo a
  fugas de autoridad concretas.

**Evidencia discriminante.** H-B tiene atestación directa: "como no tenía
dinero para Claude Code, casi todo VIGIA fue construido para modo fallback o
Ollama" (`VIGIA_RESEARCH_REPORT.md:592`). H-A tiene los documentos teóricos
tempranos y la arquitectura de la era de abril. H-C tiene el registro: los
mecanismos de enforcement son todos posteriores al principio — B-225 (agosto)
cerró un campo JSON con autoridad de veredicto, B-124 (julio) agregó
detección de coerción, el escaneo confused-deputy aterrizó en julio
(`e0033f5`), y el falsificador declarado de swap de backend sigue sin
implementar (§8).

**Veredicto: las tres, en capas distintas — CONFIRMADO.** El *principio* es
temprano y genuino; la *primacía del modo 0 tokens* es de origen económico por
palabras de la propia autora; el *enforcement* se acumuló incidente a
incidente durante dos meses después de declarado el principio. Los docs de
arquitectura narran el resultado como si hubiera nacido entero; el registro
muestra que se ganó.

### P2 — ¿Por qué determinismo de aritmética exacta?

- **H-A:** requisito de diseño del día uno ("zero floating-point in the
  critical path", `README.md:78`).
- **H-B:** propiedad retro-instalada tras incidentes concretos de
  no-determinismo, nunca lograda del todo, cuya documentación sobre-reclama.

**Evidencia discriminante.** Para H-B: la purga de floats es una campaña de
dos meses a través del registro (B-007/8/9, B-024, B-042/43, B-083,
B-104/105, L-021 en fases); el incidente decisivo está fechado y
cuantificado — el orden de acumulación de floats dio vuelta dos veredictos
sellados en un cliff de redondeo de 5e-5
(`docs/FRACTION_GATE_RECORD_20260712.md:41-47`); y el scorer vivo *hoy*
redondea con el `round()` nativo sobre floats (`vigia_scorer.py:174-182`),
directamente debajo de un comentario que explica por qué se introdujo
Decimal. L-073 — el único documento que enuncia la invariante real — la
formula correctamente: reproducibilidad exacta en la frontera y estable entre
plataformas, **no** pureza sin floats. Para H-A: solo las afirmaciones
aspiracionales mismas.

**Veredicto: H-B — CONFIRMADO.** El determinismo que efectivamente vale
(byte-idéntico entre corridas y plataformas) se ganó tarde, incrementalmente
y contra la corriente del propio código; la afirmación más fuerte del README
es falsa tal como está escrita y la contradice el propio L-073 del proyecto.

### P3 — ¿Por qué el Modo 1 se detiene en SUSPICION?

- **H-A (doctrina epistémica):** la independencia de fuentes no puede
  certificarla un motor sin supervisión; "whoever controls the disk controls
  all of those sources at once" (L-067).
- **H-B (artefacto de calibración):** el techo cayó del tuning de accuracy —
  el gate anti-drowning B-068 que impidió que el volumen del mismo dominio
  comprara MALICE — y se racionalizó después.

**Evidencia discriminante.** Para H-A: L-067 es doctrina sellada con la firma
de la mantenedora (2026-07-10) y un argumento filosófico anterior a su
enforcement; el enforcement esperó a un gate medido de 0 flips — doctrina
primero, cableado después. Para H-B: las ramas de corroboración
(`vigia_scorer.py:1454-1471`) se agregaron dentro de la recuperación de
accuracy R4-3/B-068, y los umbrales se recalibraron en la misma era (B-076).
Crucial: el scorer nunca tuvo un peldaño INTENT que remover — el "cap" es una
metáfora documental — mientras la capa agente encima acuña INTENT vía L-036
(`vigia_agent.py:1072`), así que el techo ni siquiera es hermético.

**Veredicto: co-evolución — CONFIRMADO para la doctrina, con una fuga
documentada.** La doctrina es real y se aplicó con disciplina inusual
(fail-closed hasta medir), pero cristalizó *durante* la campaña de
recuperación de accuracy, no antes, y la superficie de veredictos sellados
contradice el atajo "no INTENT". La formulación honesta es la de L-067, no la
de `CLAUDE.md:320`.

### P4 — ¿Por qué todo es bilingüe ES/EN?

- **H-A (mercado):** diseñado para sistemas judiciales hispanohablantes.
- **H-B (biografía + entrega):** la mantenedora trabaja en español
  rioplatense; el hackathon y el repo público exigían inglés; un test de
  paridad después convirtió la duplicación en ley.

**Evidencia discriminante.** Para H-B: la propia regla del acuerdo de trabajo
("Conversation with the maintainer is in Rioplatense Spanish … Everything
committed … is in English", `docs/ENGINEERING_DISCIPLINE.md:17-19`) —
imperfectamente aplicada, ya que el registro y la mitad de `docs/` están en
español; el centinela de paridad se promovió a guarda dura recién después de
detectar deriva dos veces (`tests/test_registry_integrity.py:146-160`); el
registro en inglés tuvo que retro-completarse en bloque (commit raíz
`69da100`, "201 = 201"). Para H-A: el *sustrato de detección* es
genuinamente bilingüe por diseño — regexes de engaño en español en la DB de
patrones, el detector de Grice "bilingual EN+ES", neutralidad cultural
"calibrated for Rioplatense Spanish" (`SECURITY.md:300`).

**Veredicto: H-B para la duplicación documental, H-A para el detector —
CONFIRMADO.** Dos bilingüismos distintos con dos causas distintas que
parecen una sola política.

### P5 — ¿Por qué la historia git empieza el 2026-07-21 con tres raíces?

- **H-A (limpieza deliberada):** historia removida a propósito.
- **H-B (artefacto de workflow):** líneas de desarrollo paralelas (máquina
  local + sesiones de agente remotas sembradas desde snapshots) fusionadas
  sin ancestro común.

**Evidencia discriminante.** Para H-B: las tres raíces son snapshots de árbol
completo casi idénticos que difieren en un puñado de archivos; las reglas de
la casa *prohíben* reescribir historia en sesiones de agente
(`docs/ENGINEERING_DISCIPLINE.md` §2); los hashes huérfanos quedaron en los
documentos (una limpieza habría removido el propio audit trail del proyecto,
que el proyecto trata como sagrado); y el proyecto *se queja* de sus propios
reinicios — la cacería de fósiles llama obstáculo al import squasheado, y
B-145 registra haber tenido que des-shallowear un clon para recuperar
historia. Para H-A: nada — ni motivo, ni limpieza de referencias.

**Veredicto: H-B — CONFIRMADO.** Los reinicios fueron eventos de tooling que
el propio proyecto vivió como pérdidas. Nota al pie irónica: la literatura
del modelo de amenazas del proyecto trata el scrubbing de historia git como
Indicador de Intencionalidad (`docs/DAY_ZERO_NORMAL_VIGIA_NOTES.md`); sus
propios huecos de historia son el gemelo benigno de esa señal — una lección
objetiva de su propio Protocolo de Refutación.

### P6 — ¿Por qué sobreviven dos copias del wrapper FastAPI con cinco tests de paridad?

- **H-A (redundancia deliberada):** dos rutas de import como contrato público
  soportado.
- **H-B (accidente congelado):** un duplicado sin resolver cuyo riesgo de
  borrado, bajo las doctrinas de "no unrequested improvement" y parche
  quirúrgico, superaba su costo de mantenimiento — así que se lo cercó con
  tests en lugar de resolverlo.

**Evidencia discriminante.** Los tests de paridad presentan ambas rutas como
"supported" (lenguaje H-A) — pero los gemelos todavía *difieren*: la copia de
raíz lleva dos mejoras de seguridad que a la del paquete le faltan, incluido
el fix del oráculo de 404 (`vigia_api.py:195-196`), que una paridad de
contrato verdadera habría propagado. La generación más nueva de UI se niega
explícitamente a tocarlos (`vigia/ui/server.py:3-5`). Un contrato deliberado
de dos rutas tendría una fuente y un shim de re-export — el patrón que este
mismo repo usa en otros lados (`vigia/core/vigia_scorer.py`).

**Veredicto: H-B — CONFIRMADO POR INDUCCIÓN.** La duplicación es un accidente
promovido a invariante custodiada por tests; la deriva de comportamiento
sobreviviente es el discriminador.

### P7 — ¿Por qué `caie_legacy_root.py` sigue en la raíz del repositorio?

- **H-A (compatibilidad Hyrum):** algo podría importarlo todavía.
- **H-B (proveniencia):** el registro histórico lo cita, y borrarlo dejaría
  huérfano el audit trail.

**Evidencia discriminante.** Contra H-A: cero importadores (verificado por
grep por la propia auditoría del proyecto,
`docs/AUDITORIA_FUGA_INDIRECTA.md:166`); el único fallback de import latente
nombra `caie` plano, no este archivo. Para H-B: el registro cita
`caie_legacy_root.py:1464` como el sitio del bug B-001 original — el archivo
*preserva el bug* como evidencia; la atestación del motor lo excluye
deliberadamente en dos lugares con comentarios idénticos; y la config de
mutación lo copia solo para que los tests que lo referencian importen limpio.

**Veredicto: H-B — CONFIRMADO.** Es una pieza de museo con número de
catálogo, no un shim de compatibilidad.

### P8 — ¿Por qué cinco modos de despliegue y cinco generaciones de entry points?

- **H-A (diseño de producto):** niveles de despliegue deliberados.
- **H-B (acreción):** los entry points se acumularon bajo presión de deadline
  y autoría multi-modelo, y se catalogaron después.

**Evidencia discriminante.** El proyecto se responde solo:
`docs/EXECUTION_MODES.md:1-8` — "built by one person … with a multi-AI
collective … under a tight deadline. As a result it has more than one way to
run an analysis and seal a result, and they don't all produce the same kind
of output. This document exists so nobody else has to reverse-engineer that
the hard way" — y `:72-76`: "We're not hiding the duplication — a project
that's honest about how it grew is more useful to learn from than one that
pretends it arrived fully formed." La evidencia física coincide: dos esquemas
de sellado sin reconciliar, un healthcheck de Docker roto desde la migración
de layout, un launcher hardcodeado al home de la autora.

**Veredicto: H-B — CONFIRMADO, por confesión.** La tabla de cinco modos del
README es taxonomía descriptiva, no intención de diseño.

---

## 11. Hallazgos no accionados

Divergencias doc/código y peligros que esta excavación sacó a la superficie,
reportados según la regla de la casa (los hallazgos son afirmaciones para la
mantenedora, no parches silenciosos):

1. **Sobre-reclamo de floats en `README.md:78` / Invariante 4 de `CLAUDE.md`**
   — "zero floating-point in the critical path" es falso tal como está
   escrito; `vigia_scorer._dround` devuelve floats vía el `round()` nativo.
   L-073 enuncia la invariante correcta. El README debería decir lo que dice
   L-073.
2. **Redacción de INTENT en `CLAUDE.md:320`** — cierta para el motor,
   engañosa para la superficie sellada (L-036 acuña INTENT en la capa agente
   con exit code 3).
3. **Exit codes en `README.md:57`** — documenta 0–3; faltan el 4 (ABSTAIN) y
   el 5 (SUSPICION, B-097).
4. **`KNOWN_LIMITATIONS.md:2222` desactualizado** — todavía dice que
   SUSPICION comparte `EXIT_INTENT`; B-097 le dio el código 5.
5. **Healthcheck de `Dockerfile:83`** — importa un módulo y una clase
   inexistentes; falla desde la migración flat→package.
6. **`vigia/tools/document_integrity.py:54`** — lee
   `vigia/data/phonetic_dict.json`, que no existe; las copias de raíz y de
   `data/` del diccionario tienen contenido divergente.
7. **`KNOWN_LIMITATIONS.md:1158`** — cita `vigia/tools/caie_legacy_root.py`,
   una ruta que no existe (el archivo está en la raíz del repo).
8. **Cero git tags en el remoto** pese a que `docs/ENGINEERING_DISCIPLINE.md`
   §2 manda tags de restauración pre-sesión — o no se practica, o son solo
   locales (indiscriminable desde este clon; git no pushea tags por defecto).
9. **Falsificador insignia sin implementar** — el test de swap de backend del
   narrador declarado en `docs/ENGINEERING_DISCIPLINE.md:209-211` no tiene
   implementación.
10. **Candidatos a limpieza con cero referencias** (cada uno necesita su
    propio experimento discriminante antes de borrarse, según la doctrina de
    fósiles): `initial_templates_v2.sql` (gemelo byte-idéntico),
    `vigia/inference/recommendation_engine_v3.1.py` (nombre no importable) +
    su SQL, `resultados/`, `coverage_baseline_20260622.txt`,
    `tools/vigia_prepare_evidence.py`, `c3_pattern_compare.py`,
    `c3_role_verdict_probe.py`, `convert_mans_to_ebs.py`,
    `vigia/core/geopolitical_v2.py`.

---

## 12. Limitaciones de esta excavación

- El registro pre-abril 2026 es fino: el origen en RSAC y los primeros
  debates de diseño sobreviven solo en el informe de investigación
  retrospectivo.
- Toda la cronología anterior al 2026-07-21 descansa en los documentos del
  propio proyecto, que §3.7 muestra parcialmente retro-completados; las
  fechas del registro son fechas de fuente secundaria.
- Los tres reportes de barrido se verificaron por muestreo contra archivos
  vivos en sus afirmaciones de mayor impacto (redondeo float, override
  INTENT, test de paridad, healthcheck, gemelos SQL, hashes huérfanos,
  "Directiva 4"), no re-verificados línea por línea en su totalidad.
- No se ejecutó código; los estados "muerto" descansan en análisis de
  referencias (grep, imports, configs de CI) más las propias auditorías de
  cero referencias del proyecto — el mismo estándar que usa
  `attic/README.md`, con la misma salvedad de que reflexión o consumidores
  externos no pueden excluirse del todo desde un solo repo.
- La pregunta de los git tags (§11.8) es genuinamente indiscriminable desde
  un clon.

---

*Preparado como excavación de solo lectura en la rama
`claude/archaeologist-architecture-analysis-r48jxg`. No se modificó código de
producto. Método: abducción de hipótesis rivales con consulta de índices antes
de concluir — la propia disciplina del repositorio, aplicada al repositorio
mismo.*
