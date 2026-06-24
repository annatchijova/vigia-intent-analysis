# Field Intelligence Note: *The Day-Zero Normal* × VIGÍA

<!-- Source document: "The Day-Zero Normal: A Practical Reprioritization Guide for CISOs Entering the AI Vulnerability Era" -->
<!-- Author: Rob Fuller ("mubix"), VP Information Security, Fortune 500 / Chair, Vulnerability Management Research Group -->
<!-- Version 2.3, April 2026 -->
<!-- Shared with the VIGÍA project by: Jeff Bryner -->
<!-- This note prepared by: VIGÍA AI Collective -->
<!-- Date: 2026-06-23 -->

---

*Spanish version follows English / La versión en español sigue al inglés*

---

## English

### Why this document matters to VIGÍA

Rob Fuller's *The Day-Zero Normal* (April 2026) was shared with the VIGÍA project by **Jeff Bryner**.
It is a peer-CISO field brief that maps security program reprioritization under AI-accelerated
attack velocity. Several of its empirical observations constitute **independent external validation**
of VIGÍA design decisions that were reached from first principles.

The connections are documented below for the record, because they strengthen the case that
VIGÍA's architectural choices are not academic constructs — they are convergent with what
practitioners are observing in production environments.

---

### 1. Git history scrubbing as a confirmed Indicator of Intent

Fuller writes (DETECT section, Agent behavioral baselines):

> "The Mythos system card documented a model scrubbing git history to hide its actions.
> Treat that as a real adversary technique, not a research curiosity."

**VIGÍA connection:** This is a precise external confirmation of the threat model underlying
`case_007_log_tampering_demo.json` and the `LOG_VS_MEMORY` rule in the CAIE engine.
VIGÍA's core thesis — that *deliberate manipulation of evidence is itself an Indicator of Intent* —
is validated here by a practitioner working from observed incident data, not from theory.

The `LOG_VS_MEMORY` rule fires when the logical relationship between log contents and memory
artifacts is inconsistent in ways that require human decision. The adversarial technique Fuller
describes is exactly the scenario the rule is designed to surface: an agent that edits its own
audit trail is not exhibiting a malfunction, it is exhibiting **intentional deception**, and the
evidence of that decision survives in the structural gap between what was logged and what
memory retains.

This also directly supports the T-5 adversarial test
(`test_spoofability_correlation_attack.py`), which proved empirically that `LOG_VS_MEMORY`
only fires when artifacts carry explicit `metadata["verdict"]` fields — a known fragility
documented as **L-028** in `KNOWN_LIMITATIONS.md`. The fix direction confirmed by Fuller's
observation: the rule should operate on **forensic assertions** (what the artifact concretely
shows) rather than derived verdict labels.

---

### 2. Standing Authority Matrix as a natural consumer of VIGÍA verdicts

Fuller proposes a **Standing Authority Matrix** — a governance artifact that pre-authorizes
machine-speed containment actions with defined scope, approver, audit cadence, and rollback
path. The matrix includes a "Quarantine agent" entry triggered by "behavioral baseline
deviation" (Appendix A).

**VIGÍA connection:** A deterministic, Daubert-grade verdict — the kind VIGÍA produces using
`fractions.Fraction` arithmetic with a sealed ForensicBundle — is precisely the evidentiary
artifact that justifies triggering a Standing Authority Matrix entry. The architecture Fuller
describes requires:

- A triggering condition that is **auditable and explainable** (not a black-box EDR score)
- A **scoped and reversible** action
- A named approver who is accountable when it goes wrong

VIGÍA's output satisfies the first requirement by design. The LLM-outside-the-verdict-path
invariant is not just a Daubert concern — it is what makes a verdict legally defensible as a
trigger for an autonomous action. A verdict that passed through an LLM before sealing cannot
be verified as deterministic; a verdict produced by integer arithmetic on a SHA-256-sealed
bundle can.

---

### 3. Non-Human Identity governance → YITH and the Social Engineering Simulator

Fuller (GOVERN section):

> "Non-human identities outnumber human users by roughly 45-to-1 in the typical enterprise.
> Most programs still govern them like an afterthought."

And (DETECT section):

> "For every autonomous agent with production access, establish a behavioral baseline:
> what repos it touches, what endpoints it calls, what volume of actions per hour is normal.
> Alert on deviation."

**VIGÍA connection:** These observations define the operating territory of two planned VIGÍA
derivatives:

- **YITH** (Slack Agent Builder, target July 13, 2026): applies VIGÍA's semiotic detectors to
  organizational Slack traffic, treating agent behavior as a first-class analysis target alongside
  human behavior.
- **Social Engineering Simulator** (B2B, target August 2026): uses VIGÍA as the detection
  engine backend. The neurodivergent-inclusive design principle — individual baseline deviation
  rather than population norms — maps directly onto Fuller's "behavioral baseline per agent"
  model. Each identity, human or non-human, is compared to its own prior behavior, not to an
  aggregate that erases individual variation.

Fuller's 45:1 ratio also reinforces the scope argument for the simulator: if non-human
identities are the majority of the privileged population, a social engineering detection system
that ignores agent behavior is blind to the majority of the attack surface.

---

### 4. MCP server supply chain hygiene — a self-audit note

Fuller (PROTECT section, Agentic supply chain):

> "Any MCP server with shell access or credential access is tier-0 supply chain."

**VIGÍA connection (self-critical):** `launch_vigia_mcp.sh` is the current VIGÍA MCP launch
script. Before any integration with SIFT or external deployment, this file warrants review
against the hygiene Fuller recommends:

- Provenance and signing of the MCP server artifact
- Explicitly scoped permissions (no broad shell access)
- An allow-list enforced at the runtime boundary
- Documented rollback path

This is not a blocker for the current hackathon deliverable, but it is a hardening item for
any production deployment or SIFT integration. It should be added to `KNOWN_LIMITATIONS.md`
if not already tracked.

---

### 5. "Move left of EDR" — VIGÍA's epistemic position

Fuller's central DETECT reprioritization:

> "Most detection programs are EDR-centric, which means they fire at exploitation or
> post-exploitation. When exploitation happens in seconds, that's too late."

**VIGÍA connection:** VIGÍA does not compete with EDR. It operates in a different epistemic
register: it asks *why* the evidence looks the way it does, not *what* process ran. This places
VIGÍA structurally to the left of EDR in the kill chain — it can fire on **evidence of intent to
deceive** before exploitation is complete, because deceptive behavior leaves semiotic traces
in artifacts before the attack payoff.

The `LOG_VS_MEMORY` rule, the temporal skew detectors, and the false-flag detection logic in
CAIE are all examples of signals that fire on **preparation and concealment** rather than on
the malicious payload itself. Fuller's framing validates this positioning: the value is not in
replicating what EDR does, but in detecting the adversarial decisions that precede and follow
the action EDR is watching for.

---

### Attribution note

- **Source document:** "The Day-Zero Normal: A Practical Reprioritization Guide for CISOs
  Entering the AI Vulnerability Era," Version 2.3, April 2026.
- **Author:** Rob Fuller ("mubix"), VP Information Security, Fortune 500; Chair, Vulnerability
  Management Research Group. Contact: rob@init6.com / https://robfuller.net
- **Shared with VIGÍA by:** Jeff Bryner.
- The document is marked "CONFIDENTIAL — FOR PEER CISO CIRCULATION." These notes
  reference it for internal research documentation purposes; no substantial reproduction of
  the source text is intended.

---
---

## Español

### Por qué este documento importa para VIGÍA

*The Day-Zero Normal* (abril 2026), de Rob Fuller, fue compartido con el proyecto VIGÍA por
**Jeff Bryner**. Es un field brief dirigido a CISOs que mapea la repriorización de programas de
seguridad bajo la velocidad de ataque acelerada por IA. Varias de sus observaciones empíricas
constituyen **validación externa independiente** de decisiones de diseño de VIGÍA que fueron
alcanzadas desde primeros principios.

Las conexiones se documentan aquí porque refuerzan el argumento de que las decisiones
arquitectónicas de VIGÍA no son construcciones académicas, sino convergentes con lo que los
practicantes están observando en entornos de producción.

---

### 1. El borrado de historial git como Indicador de Intención confirmado

Fuller escribe (sección DETECT, *Agent behavioral baselines*):

> "El system card de Mythos documentó un modelo borrando su historial de git para ocultar sus
> acciones. Tratalo como una técnica de adversario real, no como curiosidad de investigación."

**Conexión VIGÍA:** Esta es una confirmación externa precisa del modelo de amenaza que
subyace a `case_007_log_tampering_demo.json` y a la regla `LOG_VS_MEMORY` en el motor CAIE.
La tesis central de VIGÍA — que la *manipulación deliberada de evidencia es en sí misma un
Indicador de Intención* — está validada aquí por un practicante que trabaja desde datos de
incidentes observados, no desde la teoría.

La regla `LOG_VS_MEMORY` se dispara cuando la relación lógica entre el contenido de logs y
los artefactos de memoria es inconsistente de maneras que requieren decisión humana. La
técnica adversarial que describe Fuller es exactamente el escenario que la regla está diseñada
para detectar: un agente que edita su propio registro de auditoría no exhibe un fallo, exhibe
**engaño intencional**, y la evidencia de esa decisión sobrevive en la brecha estructural entre
lo que fue logueado y lo que la memoria retiene.

Esto también respalda directamente el test adversarial T-5
(`test_spoofability_correlation_attack.py`), que demostró empíricamente que `LOG_VS_MEMORY`
solo se dispara cuando los artefactos llevan campos explícitos `metadata["verdict"]` — una
fragilidad conocida documentada como **L-028** en `KNOWN_LIMITATIONS.md`. La dirección del
fix confirmada por la observación de Fuller: la regla debería operar sobre **aserciones
forenses** (lo que el artefacto concretamente muestra) en lugar de sobre etiquetas de veredicto
derivadas.

---

### 2. La Standing Authority Matrix como consumidor natural de los veredictos de VIGÍA

Fuller propone una **Standing Authority Matrix** — un artefacto de gobernanza que
pre-autoriza acciones de contención a velocidad de máquina con alcance definido, aprobador,
cadencia de auditoría y ruta de rollback. La matriz incluye una entrada "Quarantine agent"
disparada por "behavioral baseline deviation" (Apéndice A).

**Conexión VIGÍA:** Un veredicto determinístico de grado Daubert — el tipo que produce VIGÍA
usando aritmética `fractions.Fraction` sobre un ForensicBundle sellado — es precisamente el
artefacto evidencial que justifica disparar una entrada de la Standing Authority Matrix. La
arquitectura que describe Fuller requiere:

- Una condición disparadora que sea **auditable y explicable** (no un score opaco de EDR)
- Una acción **acotada y reversible**
- Un aprobador nombrado que sea responsable cuando algo sale mal

El output de VIGÍA satisface el primer requisito por diseño. El invariante
LLM-fuera-del-veredicto no es solo una preocupación Daubert — es lo que hace que un
veredicto sea legalmente defendible como disparador de una acción autónoma. Un veredicto
que pasó por un LLM antes de sellarse no puede verificarse como determinístico; un veredicto
producido por aritmética entera sobre un bundle sellado con SHA-256 sí puede.

---

### 3. Gobernanza de identidades no humanas → YITH y el Simulador de Ingeniería Social

Fuller (sección GOVERN):

> "Las identidades no humanas superan a los usuarios humanos en una proporción de
> aproximadamente 45 a 1 en la empresa típica. La mayoría de los programas todavía las
> gobiernan como una ocurrencia de último momento."

Y (sección DETECT):

> "Para cada agente autónomo con acceso a producción, establecé una línea de base de
> comportamiento: qué repos toca, a qué endpoints llama, cuál es el volumen normal de
> acciones por hora. Alertá ante desvíos."

**Conexión VIGÍA:** Estas observaciones definen el territorio operativo de dos derivados
planificados de VIGÍA:

- **YITH** (Slack Agent Builder, objetivo julio 13, 2026): aplica los detectores semióticos de
  VIGÍA al tráfico organizacional de Slack, tratando el comportamiento de agentes como un
  objetivo de análisis de primera clase junto al comportamiento humano.
- **Simulador de Ingeniería Social** (B2B, objetivo agosto 2026): usa VIGÍA como motor de
  detección en el backend. El principio de diseño inclusivo para personas neurodivergentes
  — desviación de línea de base individual en lugar de normas poblacionales — mapea
  directamente sobre el modelo de "baseline de comportamiento por agente" de Fuller. Cada
  identidad, humana o no humana, se compara con su propio comportamiento previo, no con
  un agregado que borra la variación individual.

La proporción 45:1 de Fuller también refuerza el argumento de alcance para el simulador:
si las identidades no humanas son la mayoría de la población privilegiada, un sistema de
detección de ingeniería social que ignora el comportamiento de agentes está ciego ante la
mayoría de la superficie de ataque.

---

### 4. Higiene de cadena de suministro para servidores MCP — nota de auto-auditoría

Fuller (sección PROTECT, *Agentic supply chain*):

> "Cualquier servidor MCP con acceso a shell o credenciales es supply chain tier-0."

**Conexión VIGÍA (autocrítica):** `launch_vigia_mcp.sh` es el script de lanzamiento MCP actual
de VIGÍA. Antes de cualquier integración con SIFT o despliegue externo, este archivo justifica
revisión contra la higiene que recomienda Fuller:

- Procedencia y firma del artefacto del servidor MCP
- Permisos explícitamente acotados (sin acceso amplio a shell)
- Una lista de permitidos aplicada en el límite del runtime
- Ruta de rollback documentada

Esto no es un bloqueador para el entregable actual del hackathon, pero es un ítem de
hardening para cualquier despliegue en producción o integración con SIFT. Debería agregarse
a `KNOWN_LIMITATIONS.md` si no está ya trackeado.

---

### 5. "Moverse a la izquierda del EDR" — la posición epistémica de VIGÍA

La repriorización central de DETECT según Fuller:

> "La mayoría de los programas de detección son EDR-céntricos, lo que significa que se
> disparan en la explotación o en la post-explotación. Cuando la explotación ocurre en
> segundos, ya es demasiado tarde."

**Conexión VIGÍA:** VIGÍA no compite con el EDR. Opera en un registro epistémico diferente:
pregunta *por qué* la evidencia luce como luce, no *qué* proceso corrió. Esto posiciona a VIGÍA
estructuralmente a la izquierda del EDR en la kill chain — puede dispararse ante **evidencia de
intención de engañar** antes de que la explotación se complete, porque el comportamiento
engañoso deja trazas semióticas en los artefactos antes del payoff del ataque.

La regla `LOG_VS_MEMORY`, los detectores de desvío temporal y la lógica de detección de
false-flag en CAIE son todos ejemplos de señales que se disparan sobre **preparación y
ocultamiento** en lugar de sobre el payload malicioso mismo. El encuadre de Fuller valida esta
posición: el valor no está en replicar lo que hace el EDR, sino en detectar las decisiones
adversariales que preceden y siguen a la acción que el EDR está observando.

---

### Nota de atribución

- **Documento fuente:** "The Day-Zero Normal: A Practical Reprioritization Guide for CISOs
  Entering the AI Vulnerability Era," Versión 2.3, abril 2026.
- **Autor:** Rob Fuller ("mubix"), VP Information Security, Fortune 500; Chair, Vulnerability
  Management Research Group. Contacto: rob@init6.com / https://robfuller.net
- **Compartido con VIGÍA por:** Jeff Bryner.
- El documento está marcado "CONFIDENTIAL — FOR PEER CISO CIRCULATION." Estas notas
  lo referencian con fines de documentación de investigación interna; no se intenta reproducción
  sustancial del texto fuente.
