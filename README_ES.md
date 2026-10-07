# VIGÍA — Motor de Análisis de Intencionalidad para SIFT Workstation

[English](./README.md) · [Español](./README_ES.md) · [README técnico](./docs/VIGIA_ESTADO_TECNICO_ES.md) · [Technical README (EN)](./docs/VIGIA_TECHNICAL_STATE_EN.md) · Autora: Anna Tchijova · Licencia: Apache 2.0

**Índice:** [Qué hace VIGÍA](#de-ioc-a-ioi) · [Inicio rápido](#inicio-rápido) · [Precisión y evaluación](#precisión-y-evaluación) · [Documentación](#documentación) · [Otros proyectos DFIR](#otros-proyectos-dfir)

> *"Hacer que el engaño sea computacionalmente caro para el atacante."*
> Hoy, mentir en un log o falsificar un ataque es gratis. VIGÍA le pone precio
> cuantificando las fracturas lógicas de la mentira.

**VIGÍA no es un detector. Es un motor de inferencia determinista que cuantifica
la fractura entre lo que la evidencia dice y lo que la evidencia debería decir.**
Si un sistema afirma MALICE sin poder explicar por qué con matemática exacta, no es
forense — es adivinación.

---

## De IoC a IoI

Los sistemas DFIR actuales — EDR, SIEM, SOAR — responden **"¿Qué pasó?"**
VIGÍA responde **"¿Por qué pasó, y quién se beneficia de esa interpretación?"**

| DFIR tradicional | VIGÍA |
|------------------|-------|
| IoC (Indicador de Compromiso) | IoI (Indicador de Intención) |
| ML opaco con "87% de confianza" | Aritmética exacta con `Fraction` y `audit_hash` |
| El LLM emite el veredicto | El LLM narra *después* de sellar el veredicto |
| Un hash por reporte | 4 hashes separados + cadena HMAC |
| Ignora el silencio | Detecta la ausencia de evidencia esperada |

Un atacante puede fabricar o suprimir evidencia técnica (IoC). No puede eliminar las
**fracturas semióticas** que produce la fabricación deliberada: incoherencias
temporales, silencios significativos (Eco), perfección digital excesiva, patrones de
manipulación de Carnegie y violaciones de las máximas de Grice.

### La magnitud del trabajo

| | |
|---|---|
| **Python de producción** | más de **102.000 líneas** (108.805 en 273 archivos, sin contar tests) |
| **Tests** | 46.931 líneas más; 2.066 funciones de test en 255 archivos |
| **JSON y Markdown** (casos, evidencia, bundles sellados, documentación) | más de **540.000 líneas** |
| **Total versionado** | más de **713.000 líneas** de texto |
| **Bundles forenses sellados** | 617, verificables sin el código de VIGÍA |
| **Documentación académica** | **193 módulos en 4 idiomas** (EN / ES / RU / ZH) |

El código pasó por 11 rondas propias de red team y auditorías externas. Los
hallazgos de cada ronda —violaciones de invariantes, fracturas epistemológicas y
arquitectónicas, roturas de frontera y de perímetro— se conservan como historia, no
se borran: el registro completo está en
[`BUGS_HISTORICO.md`](./BUGS_HISTORICO.md) (resueltos) y
[`BUGS_PENDIENTES.md`](./BUGS_PENDIENTES.md) (abiertos), con los informes de cada
ronda desde la [Ronda 2](./docs/REDTEAM_ROUND2_MONOTONICITY.md) hasta la
[Ronda 12](./docs/REDTEAM_ROUND12_SELF_AUDIT.md) en `docs/`. El mutation testing
semanal cubre el camino del veredicto. La documentación de cada módulo está en el
[índice de documentación académica](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX.md),
que cubre los 193 módulos en inglés, español, ruso y chino. El desglose de cada
cifra y los comandos para reproducirlas están en el
[README técnico](./docs/VIGIA_ESTADO_TECNICO_ES.md#2-magnitud-del-trabajo).

---

## Inicio Rápido

El Modo 1 (fallback Python) produce un veredicto sellado y verificable
criptográficamente con cero intervención humana, cero tokens y sin internet.

```bash
pip install -r requirements.txt --break-system-packages
export VIGIA_EVIDENCE_DIR="/ruta/a/evidencia/de/solo-lectura"   # requerido

# Investigación autónoma de extremo a extremo
python3 vigia_agent.py --evidence data/cases/converted/VIGIA-REAL-VANKO.json \
  --case-id VIGIA-REAL-VANKO --output results/vanko_bundle.json

# Verificar un bundle sellado de forma independiente (solo stdlib, sin código VIGÍA)
python3 forensics/verify_ebs_v1.py results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json --verbose
```

Un panel web local, totalmente offline (navegador de bundles, panel de
verificación, lanzador Modo 1) está disponible con `./launch_vigia_ui.sh` →
`http://127.0.0.1:8010` — ver INSTALL_ES.md §11b.

Códigos de salida: `0` = sin mal, `1` = MALICE, `2` = error, `3` = intención/sospecha.
Instalación completa: [`INSTALL_ES.md`](./INSTALL_ES.md) ([EN](./INSTALL.md)) ·
Referencia de comandos: [`vigia_commands_en.html`](https://annatchijova.github.io/vigia/vigia_commands_en.html) ·
VIGÍA (modelo matemático): [`vigia.html`](https://annatchijova.github.io/vigia/vigia.html) ·
Simulador: [`simulador.html`](https://annatchijova.github.io/vigia/simulador.html).

---

## Arquitectura — Aislamiento del LLM

```mermaid
graph LR
    A[EVIDENCIA] --> B[MOTOR MATEMÁTICO]
    B --> C[ForensicBundle sellado]
    C --> D[NARRADOR LLM]
    D --> E[Reporte judicial]
    F[EL LLM NO PUEDE] -.->|modificar| B
    F -.->|alterar veredicto| C
```

El LLM nunca toca el pipeline de puntuación. Recibe un bundle sellado y
criptográficamente comprometido, y produce una narrativa. El veredicto es
determinista y reproducible sin el LLM — un requisito de diseño para la potencial
admisibilidad Daubert. El motor usa `fractions.Fraction` (cero punto flotante en el
camino crítico), el CAIE pondera más la evidencia difícil de falsificar, y la
compuerta de corroboración Daubert rechaza candidatos infundados *antes* de sellar el
veredicto. `ABSTAIN` es un veredicto válido y matemáticamente justificado.

---

## Modos de Despliegue

El Modo 1 es el núcleo forense principal evaluado; los Modos 2–5 reutilizan las
herramientas deterministas locales pero tienen contratos de investigación y reporte
separadamente delimitados (un reporte de Modo 2 nunca muta un bundle sellado de Modo
1). Ver [`EXECUTION_MODES.md`](./docs/EXECUTION_MODES.md) y el playbook de Claude Code
[`CLAUDE.md`](./CLAUDE.md).

| Modo | Descripción | LLM |
|------|-------------|-----|
| **1 — Fallback Python** | Pipeline completo, 0 tokens, sin internet. `< 50ms` promedio. | No |
| **2 — Claude Code + MCP** | 22 herramientas forenses; investigación Peirciana interactiva. | Sí |
| **3 — Ollama** | LLM local; nada sale de la máquina. | Sí |
| **4 — Agente batch autónomo** | Procesamiento de corpus con loop de auto-corrección. | Opcional |
| **5 — OpenWebUI (experimental)** | Servidor MCP vía interfaz web. | Sí |

---

## Precisión y evaluación

**Todo veredicto sellado, en todos los modos, lo produce y lo aprueba el motor
Python determinístico (`vigia_scorer.py`) — el LLM puede proponer, no decide ni
puede saltear el gate.** Ninguno de los números de abajo es "la precisión de
Claude"; ver [`docs/ACCURACY_ES.md`](./docs/ACCURACY_ES.md)
([EN](./docs/ACCURACY.md)) para la metodología completa, el mecanismo del gate
y el desglose por dominios, y
[`CLAUDE.md` — Refutation Protocol](./CLAUDE.md#refutation-protocol-documentation-requirement)
para el ejemplo concreto del gate rechazando un veredicto candidato del LLM.

- **Agente sobre JSON (Dominio B), solo Python, 0 llamadas a LLM** — **158/162
  (97,5%)**, ciego a las etiquetas, en el *corpus de detección*. El **187/199
  (94,0%)** es el agregado del corpus mixto. Incluye 31 casos adversariales diseñados
  para romper el sistema: **16 BREAK**, **7 KIWI**, **3 de falsos negativos (FN)** y
  **5 de falsos positivos (FP)**. Esos resultados miden resistencia y límites
  documentados, no la precisión de detección ordinaria. El 97,5% corresponde solo al
  subconjunto de detección; no representa evidencia raw ni el rendimiento de todos
  los modos.
- **Claude Code / MCP (Dominio A), investigación asistida por LLM, mismo
  sello determinístico** — evaluado por caso sobre evidencia raw real, no es
  una cifra de corpus.
- **Agente sobre evidencia raw (Dominio C), solo Python, 0 llamadas a LLM** —
  43 fuentes de evidencia raw con bundles sellados en `results/`.

Modos de fallo conocidos — incluyendo cifras pre-fix obsoletas que están
marcadas, no borradas: [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md).

```bash
python3 -m pytest tests/ -v          # suite de regresión del núcleo determinista
python3 run_all_agent.py --timeout 90  # corpus completo, ciego a etiqueta
```

---

## Documentación

La documentación de referencia está en el
[índice de documentación académica de VIGÍA](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX.md):
193 módulos documentados en 4 idiomas (EN / ES / RU / ZH), con índices en
[inglés](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_EN.md),
[ruso](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_RU.md) y
[chino](./docs/academic/ACADEMIC_DOCS_MASTER_INDEX_ZH.md).

### Mapa del repositorio

```text
vigia-repo/
├── vigia/          # módulos de análisis forense e integraciones
├── forensics/      # verificación de bundles y utilidades forenses
├── docs/           # metodología, arquitectura, auditorías e índices
├── data/cases/     # casos de entrada y corpus de evaluación
├── results/        # bundles, informes y resultados generados
└── tests/          # suites de regresión y pruebas adversariales
```

**Inicio y uso**
- [`INSTALL_ES.md`](./INSTALL_ES.md) · [`INSTALL.md`](./INSTALL.md) — instalación y setup
- [`docs/QUICK_START.md`](./docs/QUICK_START.md) — guía rápida de integración
- [`EXECUTION_MODES.md`](./docs/EXECUTION_MODES.md) — mapa de todas las formas de correr un análisis
- [`CLAUDE.md`](./CLAUDE.md) — playbook de investigación Claude Code / MCP (22 herramientas)
- [Referencia de comandos](https://annatchijova.github.io/vigia/vigia_commands_en.html) — todos los modos con ejemplos copy-paste

**Casos y ejemplos**
- [`docs/PROMPTS_REALCASES_CLAUDE.md`](./docs/PROMPTS_REALCASES_CLAUDE.md) — prompts copy-paste para correr investigaciones completas
- [`RAW_CASES_LOG_ES.md`](./docs/RAW_CASES_LOG_ES.md) · [EN](./docs/RAW_CASES_LOG.md) — catálogo por caso de evidencia raw
- [`docs/readme_benign_cases.md`](./docs/readme_benign_cases.md) — casos benignos / de uso autorizado
- [`docs/digital_corpora_complete_report.md`](./docs/digital_corpora_complete_report.md) · [`docs/nist_cfreds_full_report.md`](./docs/nist_cfreds_full_report.md) — reportes completos de corpus real
- [`results/`](./results/) — ForensicBundles sellados, amicus curiae y sidecars SHA-256

**Precisión, validación y cumplimiento**
- [`docs/ACCURACY_ES.md`](./docs/ACCURACY_ES.md) · [EN](./docs/ACCURACY.md) — metodología y métricas del corpus
- [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) — limitaciones documentadas (transparencia Daubert)
- [`DAUBERT_JUDICIAL_ES.md`](./docs/DAUBERT_JUDICIAL_ES.md) · [EN](./docs/DAUBERT_JUDICIAL.md) — fundamento de admisibilidad Daubert
- [`docs/MUTATION_RUNBOOK_ES.md`](./docs/MUTATION_RUNBOOK_ES.md) · [EN](./docs/MUTATION_RUNBOOK.md) — guía de mutation testing

**Teoría y metodología**
- [`docs/vigia_paper_methodology.md`](./docs/vigia_paper_methodology.md) — el paper formal de metodología
- [`docs/EPISTEMIC_KERNEL.md`](./docs/EPISTEMIC_KERNEL.md) — el kernel epistémico (generación de hipótesis)
- [`docs/skills/abductive-engineering/SKILL.md`](./docs/skills/abductive-engineering/SKILL.md) — razonamiento abductivo como skill reutilizable

**Arquitectura y estado técnico**
- [`VIGIA_ESTADO_TECNICO_ES.md`](./docs/VIGIA_ESTADO_TECNICO_ES.md) · [EN](./docs/VIGIA_TECHNICAL_STATE_EN.md) — README técnico: magnitud medida, arquitectura y estado actual
- [`docs/diagrama_pipeline.md`](./docs/diagrama_pipeline.md) — diagrama del pipeline
- [Diagramas de arquitectura](https://annatchijova.github.io/vigia/vigia_diagrams.html) · [VIGÍA (modelo matemático)](https://annatchijova.github.io/vigia/vigia.html) · [Simulador](https://annatchijova.github.io/vigia/simulador.html) · [Video demo](https://www.youtube.com/watch?v=NOquYzUwMkg)

**Desarrollo y proyecto**
- [`CONTRIBUYENDO.md`](./CONTRIBUYENDO.md) · [`CONTRIBUTING.md`](./CONTRIBUTING.md) — guía de contribución
- [`docs/ENGINEERING_DISCIPLINE.md`](./docs/ENGINEERING_DISCIPLINE.md) — disciplina de ingeniería para agentes que trabajan sobre el código
- [`SECURITY.md`](./SECURITY.md) — política de seguridad y hardening
- [`BUGS_PENDIENTES.md`](./BUGS_PENDIENTES.md) ([EN](./BUGS_PENDIENTES_EN.md)) · [`BUGS_HISTORICO.md`](./BUGS_HISTORICO.md) ([EN](./BUGS_HISTORICO_EN.md)) — registro de bugs (abiertos / resueltos)
- [`AUTHORS.md`](./AUTHORS.md) · [`docs/VIGIA_THEME_SONG.md`](./docs/VIGIA_THEME_SONG.md) — créditos y canción tema

> `docs/` también contiene el rastro completo de auditorías internas, red-team y
> registros de diseño (`AUDITORIA_*`, `REDTEAM_ROUND*`, `FASE*`, `B0*`), preservados
> como historia del proyecto.

## Otros proyectos DFIR

También recomiendo visitar [Velo](https://github.com/annatchijova/velo),
[Zaynor](https://github.com/annatchijova/zaynor) y
[Annaconda](https://github.com/annatchijova/annaconda), otros proyectos DFIR de la
misma autora. Hay más trabajo DFIR en curso, además de repositorios separados de red
team y blue team que están en construcción.

---

## Fundamento Teórico

VIGÍA se apoya en la semiótica abductiva de Charles S. Peirce (Primeridad /
Segundidad / Terceridad), el principio cooperativo de H. Paul Grice, la taxonomía de
manipulación de Dale Carnegie, y la teoría del silencio significativo y la
sobreinterpretación de Umberto Eco.

---

## Licencia

Apache 2.0 — ver [`LICENSE`](./LICENSE).
Copyright (c) 2026 Anna Tchijova y el Colectivo IA de VIGÍA.

*"La pregunta no es qué pasó, sino por qué alguien hizo que pasara —
y quién se beneficia de esa interpretación."* — VIGÍA
