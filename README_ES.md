# VIGÍA — Agente de Investigación Forense Asistido por IA

[English](./README.md) · [Español](./README_ES.md) · [FRACTURE (la VIGÍA original)](https://github.com/annatchijova/fracture) · Autora: Anna Tchijova · Licencia: Apache 2.0

**Índice:** [Qué cambió y por qué](#qué-cambió-y-por-qué) · [Qué es la nueva VIGÍA](#qué-es-la-nueva-vigía) · [Protocolo Kassandra y Hallucination Guard](#protocolo-kassandra-y-hallucination-guard) · [Reproducilo vos misma/o](#reproducilo-vos-mismamo) · [Señal de calidad: el registro de bugs](#señal-de-calidad-el-registro-de-bugs) · [MCP, API y el ecosistema](#mcp-api-y-el-ecosistema) · [MCP Cronos](#mcp-cronos) · [Roadmap](#roadmap) · [Rigor científico](#rigor-científico) · [Para Mozilla](#para-mozilla)

---

## Qué cambió y por qué

**Esto no es un proyecto nuevo reemplazando a uno viejo. Es el mismo proyecto,
separado en dos, con dos nombres.**

El sistema que antes era VIGÍA — un motor forense determinista de
intencionalidad donde el LLM queda deliberadamente afuera del camino de
veredicto, pensado para investigadores avanzados en contextos de amenaza
crítica, nivel judicial y bajo estándar Daubert — no dejó de existir.
Mantuvo todo su código, sus más de 102.000 líneas de Python de producción,
sus 617 bundles sellados, sus 11 rondas de red-team y su compromiso de
mantenimiento activo, bajo un nombre nuevo: **FRACTURE**
([github.com/annatchijova/fracture](https://github.com/annatchijova/fracture)).
Su README original está preservado tal cual en
[`docs/README_FRACTURE_LEGACY_ES.md`](./docs/README_FRACTURE_LEGACY_ES.md)
([EN](./docs/README_FRACTURE_LEGACY_EN.md)), para que nada de ese trabajo se
pierda ni se reescriba.

**Este repositorio (`vigia-intent-analysis`) pasa a ser la nueva VIGÍA.**

Soy investigadora independiente en IA y seguridad. Apliqué a Mozilla con VIGÍA
como mi propuesta. El programa de Mozilla pide que la IA sea protagonista del
trabajo — y la VIGÍA que existía estaba diseñada sobre el principio opuesto:
el LLM nunca decide, solo narra después de que un motor determinista ya selló
el veredicto. Esa es una decisión de diseño deliberada, documentada y
estructural para una herramienta forense con pretensión de admisibilidad
Daubert, y no la voy a disimular fingiendo lo contrario.

Lo que le dije a Mozilla es cierto: VIGÍA existe, y la estoy reescribiendo
para que la IA sea protagonista real de toda la investigación — no para
pegarle una etiqueta al motor viejo. Esa reescritura es lo que este
repositorio es ahora, y es para lo que es la financiación. El relato completo
y detallado de esta decisión —el ecosistema en el que se inserta, las
restricciones de honestidad que me puse, y en qué difieren exactamente los dos
sistemas— está en [`docs/MOZILLA_PROPOSAL_EN.md`](./docs/MOZILLA_PROPOSAL_EN.md).

---

## Qué es la nueva VIGÍA

Un agente de investigación forense asistido por IA, de punta a punta —
pensado para peritos, gente de ciberseguridad e investigadores DFIR que
quieren un agente que acompañe todo el proceso, no una caja negra que solo
responde "qué pasó". Donde FRACTURE excluye al LLM de la decisión por diseño,
la nueva VIGÍA lo pone a trabajar en la investigación misma: proponiendo
hipótesis, conduciendo el uso de herramientas y narrando hallazgos — mientras
los mecanismos de integridad descriptos abajo (Kassandra, el hallucination
guard) mantienen esa narración honesta y evitan que evidencia adversarial la
manipule.

Esto es una reescritura activa, no un producto terminado. Las secciones de
abajo distinguen claramente qué ya corre hoy y qué es dirección, no entrega.

---

## Protocolo Kassandra y Hallucination Guard

Dos mecanismos de integridad que ya existen en este código, heredados de
FRACTURE y centrales para que una VIGÍA con IA protagonista siga siendo
confiable. Cada uno atribuido acá al archivo que realmente lo implementa:

**Protocolo Kassandra** — [`vigia/vigia_sift_bridge.py`](https://github.com/annatchijova/vigia-intent-analysis/blob/main/vigia/vigia_sift_bridge.py)
(`_derive_session_nonce`, `_generate_active_tripwire`, `_process_llm_verdict`).
Es un *semantic tripwire* que hice porque VIGÍA es open source, así que tengo
que asumir que un atacante puede leer todo el código y preparar evidencia
específicamente para manipular la capa LLM. La idea es que el mecanismo sea
público, pero el valor concreto que protege cada sesión no lo sea. Cuando
empieza el análisis, VIGÍA toma el SHA-256 de la evidencia y, usando un
`KASSANDRA_SALT` secreto, deriva por HMAC-SHA256 un nonce de sesión. Con ese
nonce genera delimitadores dinámicos para la evidencia y un identificador
secreto tipo `PROTOCOLO_KASSANDRA_<hash_dinámico>`: un canario semántico que
el LLM conoce para esa sesión, pero que la evidencia analizada no debería
conocer. Si la evidencia intenta mencionarlo, reproducirlo o hacerse pasar por
una instrucción legítima que lo contiene, es señal de que algo está cruzando
la frontera datos→instrucciones. VIGÍA no confía simplemente en que el LLM
diga "detecté Kassandra": verifica externamente que devuelva el `tripwire_id`
correcto y cumpla el contrato esperado. Si inventa otro ID o responde de
forma inconsistente, queda registrado como `KASSANDRA_PROTOCOL_VIOLATION` /
`INTEGRITY_UNKNOWN`.

Kassandra no demuestra que exista un atacante, ni convierte automáticamente
una anomalía en una conclusión forense — es una defensa de integridad
semántica del canal hacia el LLM, principalmente contra prompt injection y
manipulación de evidencia. Y tiene una limitación deliberadamente explícita:
si no configurás un `KASSANDRA_SALT` secreto, el fallback es un salt público
(`VIGIA_FALLBACK_SALT_NO_PRODUCTION`) — un atacante que conoce la evidencia
puede precomputar los valores, y VIGÍA solo registra un warning
(`KASSANDRA_SALT_MISSING`). Para entornos donde esa garantía importa,
`VIGIA_ENFORCE_KASSANDRA_SALT=true` hace **fail-closed**: VIGÍA directamente
no arranca sin un salt secreto configurado.

**Hallucination Guard** — [`vigia/llm/hallucination_guard.py`](https://github.com/annatchijova/vigia-intent-analysis/blob/main/vigia/llm/hallucination_guard.py).
Un mecanismo distinto: verifica la narración del LLM —veredicto, score, tipo
de fractura, TTPs de MITRE, hashes— contra un conjunto de `AuthorizedFact`
extraído directamente de la salida del motor determinista, comparando con
`Decimal`/`Fraction`, nunca floats, y redacta cualquier afirmación del modelo
que no esté respaldada por ese conjunto autorizado. Kassandra defiende la
frontera evidencia→LLM; el hallucination guard defiende la frontera
LLM→reporte. Juntos son la razón por la que me siento cómoda dejando que el
LLM sea protagonista acá, en vez de excluirlo por completo como hace
FRACTURE.

Esto no es una afirmación terminada y auditada de que la arquitectura nueva
es segura — es temprano, está en rediseño activo (ver [Roadmap](#roadmap)), y
no lo voy a disimular para una postulación a una beca.

---

## Reproducilo vos misma/o

No le pido a nadie que crea las cifras por fe. El núcleo determinista que este
repositorio heredó de FRACTURE sigue acá y sigue siendo verificable — y quiero
ser precisa sobre a qué modo le corresponde cada número, porque mezclarlos es
en sí mismo una forma de overclaim:

- **Agente solo Python, 0 llamadas a LLM (Dominio B)** — **158/162 (97,5%)**
  ciego a etiquetas en el corpus de detección; **187/199 (94,0%)** en el
  corpus mixto (incluyendo 16 casos adversariales BREAK, 7 KIWI, 3 falsos
  negativos, 5 falsos positivos). Esto es el scorer determinista corriendo
  solo, sin la capa de razonamiento del agente.
- **Claude Code / MCP, investigación asistida por LLM (Dominio A)** — **100%
  de veredictos correctos en toda investigación corrida hasta la fecha**,
  evaluado por caso, no como cifra agregada de corpus. Este es el modo sobre
  el que realmente se construye la reescritura con IA protagonista. Si la
  señal de un caso cae en algo que VIGÍA no contempla, la arquitectura está
  diseñada para degradar a `ABSTAIN` en vez de adivinar — y eso, sin
  confirmar, podría más adelante resultar un falso negativo. Todavía no
  encontramos un caso así. Eso no es una garantía de que no exista; es una
  afirmación honesta de lo que se chequeó hasta ahora y lo que no.
- Metodología completa y desglose por dominio en
  [`docs/ACCURACY_ES.md`](./docs/ACCURACY_ES.md).
- Casos reales de **Digital Corpora** (M57-Jean, Nitroba, Lone Wolf, Tuck
  2019) y datasets NPS, documentados en
  [`docs/digital_corpora_complete_report.md`](./docs/digital_corpora_complete_report.md).
- El corpus adversarial propio de VIGÍA —los casos BREAK, KIWI, de falso
  positivo y falso negativo construidos específicamente para intentar romper
  el sistema— vive hoy en este repositorio bajo `data/cases/` y se está
  consolidando en su propia carpeta de nivel superior, `CORPUS-CASES/`, para
  que sea fácil de encontrar y correr de forma independiente del resto.
- Elegí cualquier caso sellado y verificalo bit a bit, de forma independiente
  del código de VIGÍA:
  ```bash
  python3 forensics/verify_ebs_v1.py results/<caso>_bundle.json --verbose
  python3 show_4_hashes.py results/<caso>_bundle.json
  ```
  `show_4_hashes.py` imprime los cuatro hashes forenses (grafo, bundle,
  cadena HMAC, re-verificación independiente EBS) de un caso sellado.
  Deliberadamente no cito acá un resultado específico de "N hashes
  coinciden, uno no" hasta volver a verificar esa afirmación exacta con una
  corrida fresca — ver [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md) para
  lo confirmado versus lo que todavía se está chequeando. Reportá cualquier
  cosa que no reproduzca.

---

## Señal de calidad: el registro de bugs

No borro mis propios bugs. El historial completo —11 rondas de red-team,
violaciones de invariantes encontradas y corregidas— está en
[`BUGS_HISTORICO.md`](./BUGS_HISTORICO.md). Algunos de los más retorcidos,
para que esto no se lea como una afirmación sin respaldo:

- **[B-150](./BUGS_HISTORICO.md)** — `_parse_iso_timestamp` interpretaba
  silenciosamente timestamps sin timezone en la *timezone local de la máquina
  que corría el análisis*: la misma evidencia podía producir un veredicto y
  un hash distintos según la configuración de reloj del sistema operativo de
  cada perito.
- **[B-239](./BUGS_HISTORICO.md)** — `bool` es subclase de `int` en Python.
  Dos copias paralelas del mismo predicado `Fraction` discreparon porque una
  aceptaba booleanos como entrada numérica válida y la otra no.
- **[B-218](./BUGS_HISTORICO.md)** — el bundle sellado registraba
  `epsilon_used = epsilon_accept` incluso en casos donde la decisión real fue
  REJECT vía `epsilon_reject` — el parámetro auditado no era el que realmente
  decidió el caso.
- **[B-215](./BUGS_HISTORICO.md)** — `evidence_graph` nunca se poblaba en los
  bundles de `run_full`, así que `graph_hash` era idéntico en *todos* los
  casos: un ancla de integridad criptográfica que parecía real y no cargaba
  ninguna información.
- **[B-234](./BUGS_HISTORICO.md)** — nada verificaba que un reasoning trace
  estuviera realmente ligado al bundle sellado que decía acompañar — dos
  artefactos presentados como vinculados, sin ningún chequeo que lo exigiera.

Los cinco están marcados `RESOLVED` en el registro — el punto no es que los
bugs existieran, es que están documentados en vez de desaparecer en
silencio.

---

## MCP, API y el ecosistema

VIGÍA ya es usable vía MCP (`launch_vigia_mcp.sh`, 22 herramientas forenses —
ver [`CLAUDE.md`](./CLAUDE.md)) y vía un wrapper FastAPI. Ambos están en
rediseño activo para el enfoque de IA protagonista descripto arriba. La
dirección de la que me inspiro: el diseño de orquestación multiagente y
telemetría de [annaconda](https://github.com/annatchijova/annaconda) y
[zaynor](https://github.com/annatchijova/zaynor), y el ecosistema más amplio
de [krakadyl](https://github.com/annatchijova/krakadyl) — hacia ahí quiero que
converja la arquitectura de agentes de la nueva VIGÍA, no donde está hoy.

Si el motor determinista del Modo 1 sigue siendo accesible directamente desde
este repositorio, o pasa a vivir enteramente bajo FRACTURE, es una decisión de
diseño que todavía estoy pensando — la dejo anotada acá en vez de decidirla
prematuramente.

---

## MCP Cronos

[Cronos](https://github.com/annatchijova/cronos) es un servidor MCP aparte
que construí como grabador de caja negra para agentes: captura llamadas a
herramientas, memorias recuperadas, hipótesis consideradas y descartadas,
evidencia y decisiones a medida que ocurren, y sella el trace resultante en
una cadena de hashes SHA-256. Ya corre junto a las investigaciones de VIGÍA
en Claude Code hoy — este repositorio trae decenas de archivos
`cronos_*.md` de sesiones pasadas como prueba, no como promesa.

Importa más ahora, no menos, a medida que la IA pasa a ser protagonista en
vez de narradora llamada una sola vez al final. Un veredicto sellado te dice
*qué* se decidió; no dice nada sobre el camino que el agente recorrió
realmente para llegar ahí —qué hipótesis planteó y descartó, qué llamadas a
herramientas hizo y en qué orden, dónde cambió de postura—. Cronos es el
registro independiente y a prueba de alteración de ese camino, mantenido
separado del veredicto de la misma forma en que Kassandra y el hallucination
guard se mantienen separados de la narración del LLM: ninguno de los tres
confía en que el agente resuma honestamente lo que hizo.

---

## Roadmap

Explícitamente trabajo futuro, no entregado:

- UI adaptada a una audiencia más amplia, incluyendo personas
  neurodivergentes — todavía no construida.
- Superficie MCP/API rediseñada alineada con el modelo multiagente y de
  telemetría de annaconda/zaynor/krakadyl mencionado arriba.
- Reestructuración de carpetas y repositorios para reflejar con claridad la
  separación VIGÍA/FRACTURE (planificado aparte de esta tanda de
  documentación).

---

## Rigor científico

Separarse en dos nombres no significa separarse del estándar. Tanto **VIGÍA**
como **FRACTURE** son packages de GitHub propiamente dichos, bajo la misma
licencia Apache 2.0, con sus propias suites de test y registros de bugs.
También estoy formalizando (por ahora en español, versión en inglés en
camino) una investigación en curso sobre reward hacking como fenómeno
sociotécnico en agentes LLM en
[reward-hacking-social](https://github.com/annatchijova/reward-hacking-social) —
técnicas de mitigación que ya probé de forma informal y que ahora quiero
validar formalmente. La nombro acá a propósito, no como una proeza
incoherente para un proyecto que está a punto de darle más margen a un LLM:
es justo lo contrario, un intento de reducir ese riesgo antes de apoyarme
más en el modelo. Ya tengo hipótesis de trabajo para orquestar varios
agentes de forma que el error se reduzca en vez de acumularse, y eso es
parte de lo que informa cuánto margen le da la arquitectura nueva de VIGÍA
al modelo, y dónde se ubican ahí Kassandra, el hallucination guard y Cronos.

---

## Para Mozilla

Envié la postulación a Mozilla describiendo a VIGÍA tal como existía en ese
momento, y me comprometí a reescribirla para que la IA fuera protagonista del
trabajo — este repositorio, a partir de esta tanda de documentación, es esa
reescritura en curso, y la financiación es lo que hace posible terminarla. El
relato completo, sin recortar —el ecosistema en el que se inserta, qué está
confirmado versus en verificación, y la diferencia honesta entre VIGÍA y
FRACTURE— está en [`docs/MOZILLA_PROPOSAL_EN.md`](./docs/MOZILLA_PROPOSAL_EN.md).

---

## Licencia

Apache 2.0 — ver [`LICENSE`](./LICENSE).
Copyright (c) 2026 Anna Tchijova y el Colectivo IA de VIGÍA.
