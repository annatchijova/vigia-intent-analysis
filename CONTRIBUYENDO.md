# CONTRIBUYENDO A VIGÍA

**Repositorio:** `https://github.com/annatchijova/vigia-intent-analysis`  
**Autora:** Anna Tchijova  
**Última actualización:** junio de 2026

---

## Cumplimiento del Protocolo P2 — Lectura obligatoria para forks

El núcleo matemático de VIGÍA opera bajo el **Protocolo P2**, la especificación
determinista de entropía que rige todas las afirmaciones de reproducibilidad de
scoring. Si estás haciendo un fork de este repositorio, portando el kernel de
entropía a otro lenguaje, o construyendo una herramienta que reclame compatibilidad
con VIGÍA, **debés leer P2 antes de escribir una sola línea de código de scoring**.

La especificación completa está en `docs/protocols/P2/SPEC.md`. Los vectores
canónicos están en `canonical_vectors_p2.json`, acompañados de
`canonical_vectors_p2.sha256`. El SHA-256 del archivo de vectores es normativo:
cualquier modificación — incluyendo espacios en blanco — invalida la huella digital
y el reclamo de compatibilidad.

### Qué rige P2

P2 define el contrato de reproducibilidad para: entropía de Shannon, entropía
normalizada, tasa de entropía, entropía condicional de Markov de orden k, complejidad
de Lempel-Ziv (variante LZ76), entropía de permutación, codificación de pares,
umbrales de abstención, y rechazo adversarial (NaN, Inf, denormales).

P2 **no** define: interpretación semántica de evidencia, atribución de autoría,
inferencia de intención, admisibilidad legal, ni afirmaciones ontológicas sobre
"autenticidad". Estos están explícitamente fuera del alcance y documentados como tal
en la sección de no-objetivos de la especificación.

### Niveles de cumplimiento

| Nivel | Para quién es | Afirmación permitida |
|-------|---------------|----------------------|
| **Strict** | Auditoría forense, procedimientos legales | `VIGÍA-compatible P2 (strict)` |
| **Reference** | DFIR de producción, investigación, multiplataforma | `VIGÍA-compatible P2` |
| **Accelerated** | Tiempo real, embebido, alto volumen | `VIGÍA-accelerated` — **no puede reclamar compatibilidad P2** |

El cumplimiento Strict requiere Python puro, reducción secuencial, y canonicalización
`Decimal.quantize()` HALF_EVEN. El cumplimiento Reference permite NumPy/CuPy con
acumuladores float64. Accelerated permite float32 pero pierde el reclamo de
compatibilidad por completo — esto es no negociable y está documentado en la sección
de niveles de cumplimiento de la especificación.

### La cláusula de revocación

P2 §3 contiene una cláusula de revocación que aplica a forks y obras derivadas.
Si tu documentación, etiquetas de UI, salida de CLI, nombres de campos de API, o
cualquier material dirigido al usuario usa alguna de las siguientes frases, perdés
automáticamente el derecho a reclamar compatibilidad P2, independientemente de si
tus vectores pasan:

- `"AI detector"` / `"bot detector"` / `"human-vs-machine classifier"`
- `"authenticity score"` / `"deception score"` / `"intent score"` / `"humanity index"`

Estas son afirmaciones ontológicas que las mediciones matemáticas de P2 no pueden
sostener. Una secuencia de alta entropía no es "más humana". Una secuencia de baja
entropía no es "más sintética". Si tu herramienta necesita hacer esas afirmaciones,
necesita una capa de decisión validada independientemente por encima de P2, y no
puede usar la marca de compatibilidad de VIGÍA para hacerlo.

### Brechas adversariales conocidas

P2 documenta 10 brechas conocidas (GAP-01 a GAP-10) — escenarios adversariales
que todavía no están cubiertos por vectores canónicos. Estos incluyen ataques de
inflación de entropía, explosión simbólica vía perturbaciones de punto flotante
sub-ULP, deriva de calibración, y aliasing de período LZ en secuencias cortas. Leé
§14 de la especificación antes de reclamar propiedades de robustez. Estas brechas son
de solo adición: una vez asignado, un identificador GAP-NN nunca se reutiliza.

### Estado de P2

P2 está actualmente en **borrador pre-freeze**. La fecha objetivo de freeze fue
2026-06-15, alineada con el envío al SANS FIND EVIL Hackathon. El freeze requiere
validación empírica de los umbrales de abstención (actualmente heurísticos),
verificación entre backends en 3+ runtimes, y testing formal de cadena de custodia.
Hasta el freeze, los umbrales son orientativos. Cualquier despliegue en producción
debe documentar la procedencia de los umbrales.

P1 está congelado e inmutable. P2 depende de P1. Los validadores deben pasar P1
primero.

### Hoja de ruta P3

P2 es infraestructura, no un sistema forense. Las siguientes capacidades están
explícitamente diferidas a P3: estándar formal de discretización, fusión y ponderación
de scores, propagación de incertidumbre, protocolo de calibración, y cierre de
inferencia Peirciana. P2 mide. P3 razonará.

---

## Una nota de la autora

Quiero ser directa sobre algo antes que nada: **VIGÍA no es perfecto, y lo sé.**

Esto no es un descargo de responsabilidad escrito por presión legal. Es un principio de
diseño. Un sistema forense que no puede documentar sus propios modos de falla es
intrínsecamente poco confiable. El mismo estándar epistemológico que aplico a la
evidencia, lo aplico a este código.

Si encontrás algo mal — un bug, una inconsistencia lógica, un caso donde el scoring
produce un veredicto claramente incorrecto, un vacío de cobertura, una falla teórica
— genuinamente quiero saberlo. No me voy a poner a la defensiva. La crítica no es un
ataque al proyecto. La crítica *es* el proyecto funcionando como se pretendía.

Sé directo. El modelo de amenaza contra el que trabajo no recompensa la cortesía por
encima de la precisión.

---

## Lo que VIGÍA no cubre (y probablemente nunca cubrirá del todo)

El corpus de casos fue diseñado alrededor de un panorama de amenazas específico:
amenazas internas empresariales, intrusiones estilo APT, abuso de credenciales,
manipulación de logs, y patrones de malware residente en memoria documentados en
datasets forenses públicos (NIST, DFRWS, DEF CON DFIR CTF, Digital Corpora).

**Esto no es toda la vida humana.** La investigación forense abarca dominios que este
sistema no tocó:

- Forense de dispositivos móviles (artefactos iOS/Android)
- IoT y evidencia de sistemas embebidos
- Entornos nativos de nube (contenedores, serverless, identidad gestionada)
- Sistemas de control industrial (ICS/SCADA)
- Cadenas de redes sociales e inteligencia de fuentes abiertas (OSINT)
- Integración de control de acceso físico
- Entornos de idiomas no-inglés a nivel léxico
- Campañas APT lentas y prolongadas que abarcan múltiples años
- Casos criminales que involucran perpetradores no técnicos

El modelo de puntuación CAIE fue calibrado sobre los casos que existen en el corpus.
Si traés un tipo de caso que es estructuralmente diferente de esos — diferentes firmas
de artefactos, diferentes primitivas de ataque, diferente contexto cultural u
organizacional — los pesos pueden no reflejar tu realidad.

**Documentá tu dominio.** Si contribuís casos de un área no cubierta, lo más valioso
que podés incluir es una explicación de por qué los pesos existentes están mal para tu
dominio, no solo un parche que haga pasar el test.

---

## Sobre la cooperación

VIGÍA fue construido por un humano y siete modelos de IA trabajando juntos, lo que
significa que fue construido sobre la premisa de que ninguna perspectiva individual es
suficiente.

Ese mismo principio se extiende a los colaboradores humanos. No creo en el modelo del
genio solitario heroico del open source. Creo que una herramienta forense revisada por
un ex investigador de fuerzas del orden, un abogado defensor, un operador de red team,
y un psicólogo conductual será más confiable que una revisada solo por gente que piensa
como yo.

Si tu trasfondo es diferente al mío — si venís de DFIR, de la academia, de la práctica
legal, de una jurisdicción que no consideré — tu perspectiva tiene un valor
desproporcionado acá, precisamente porque es diferente.

Las contribuciones son bienvenidas de cualquier trasfondo. El requisito mínimo no es la
expertise: es la honestidad intelectual sobre lo que sabés y lo que no sabés.

---

## Limitaciones actuales bajo desarrollo activo

Antes de contribuir, leé [`KNOWN_LIMITATIONS.md`](./KNOWN_LIMITATIONS.md). Documenta
cada modo de falla conocido en detalle, incluyendo causas raíz e implicaciones
forenses.

Elementos clave todavía abiertos para contribución:

- **FW-008:** Conversión completa a fracciones de valores intermedios de scoring.
  Actualmente el camino de decisión del veredicto es determinista, pero algunas
  operaciones intermedias de punto flotante permanecen. La racionalización completa
  es el objetivo.
- **Expansión de dominio:** Nuevas categorías de casos, especialmente entornos forenses
  de IoT, nativos de nube, y móviles.
- **Cobertura de idiomas:** La capa de NLP opera principalmente sobre artefactos en
  inglés. Extender la cobertura de patrones a otros idiomas requiere expertise de
  dominio tanto en el idioma como en sus firmas de artefactos forenses.

---

## Proyectos futuros

VIGÍA es un proyecto en una trayectoria de investigación más amplia. Si alguno de los
siguientes te interesa, explorá la lista completa de repositorios en:

**`https://github.com/annatchijova`**

### RAVEN-MEMORY

RAVEN-MEMORY es una arquitectura de memoria adaptativa para sistemas de IA agentica,
actualmente en desarrollo como proyecto independiente. El objetivo de diseño es memoria
episódica persistente y estructurada para agentes que operan a través de sesiones largas
— el tipo de memoria que permite a un agente forense mantener contexto de caso a través
de investigaciones interrumpidas.

El camino de integración planificado es VIGÍA → RAVEN-MEMORY como el backend de
memoria para el pipeline agentico. Actualmente el agente de VIGÍA (`vigia_agent.py`)
opera sin estado entre casos. RAVEN-MEMORY permitiría al sistema rastrear linaje de
hipótesis, acumular evidencia contextual a través de sesiones, y mantener un log de
investigación auditable que es en sí mismo un artefacto forense.

Esta integración no está prometida en ninguna línea de tiempo. Depende de que
RAVEN-MEMORY alcance estabilidad de producción. Pero es la dirección hacia la que estoy
construyendo, y las contribuciones al diseño de la interfaz de memoria en VIGÍA son
bienvenidas con ese futuro en mente.

### Otros proyectos activos

- **MUTANTE:** Red teaming adversarial de LLM vía mutación evolutiva de prompts.
  Relevante para el pipeline de testing de robustez adversarial de VIGÍA.
- **STYLOMETRY-CI:** Puerta de identidad forense para pipelines de GitLab CI/CD.
  Ortogonal a VIGÍA pero comparte la base teórica de fingerprinting conductual.
- **WormGame:** Algoritmo de optimización basado en el conectoma de C. elegans. Mapas
  de distribución de soluciones bimodales a estados conductuales documentados.
  Designado para un contexto futuro de computación bio-inspirada/ML — no integrado con
  VIGÍA.

---

## Cómo contribuir

### Reportando issues

Abrí un issue en GitHub. Incluí:

- Versión de VIGÍA o hash de commit
- La entrada específica (case JSON, path de evidencia, o comando) que dispara el issue
- Salida observada vs. salida esperada
- Si es un issue de correctitud (veredicto equivocado), un issue de determinismo
  (salida inconsistente en entrada idéntica), o un issue de usabilidad

Para vulnerabilidades de seguridad, leé [`SECURITY.md`](./SECURITY.md) primero.

### Enviando contribuciones de casos

Los casos nuevos deben seguir el esquema canónico de casos. Mirá
[`data/cases/`](./data/cases/) para ejemplos y la definición de esquema en
[`fsv_schema.json`](./fsv_schema.json).

Cada caso enviado debe incluir:

- Un campo `ground_truth` con el veredicto esperado
- Un campo `rationale` explicando por qué ese veredicto es correcto
- Un campo `domain` identificando el dominio forense
- Un campo `source` documentando de dónde origina el patrón de evidencia (dataset
  público, construcción sintética, caso real sanitizado, etc.)
- Si es sintético: una declaración explícita de que es sintético

Los casos que devuelven ABSTAIN no son fallas. No envíes casos diseñados para "romper"
el sistema y luego clasificarlos como déficits de precisión. Leé el marco de precisión
en [`README.md`](./README.md#accuracy--evidence-dataset) antes de abrir issues sobre
conteos de veredictos.

### Contribuciones de código

1. Hacé fork del repositorio
2. Creá una branch con un nombre descriptivo
3. Corré el test suite completo antes de enviar: `pytest tests/ -v`
4. Cero regresiones son aceptables. Si tu parche introduce una regresión, explicá por
   qué en la descripción del PR y cuál es el tradeoff
5. Todo código nuevo que toque el pipeline de scoring debe incluir un test de
   determinismo — entrada idéntica debe producir salida idéntica a través de plataformas
6. Si tu contribución modifica la lógica de veredictos, incluí una actualización
   correspondiente a `KNOWN_LIMITATIONS.md` si resuelve una limitación documentada, o
   una entrada nueva si introduce una

### Contribuciones de documentación

El codebase contiene comentarios en español. Las traducciones al inglés son bienvenidas
y necesitadas, particularmente en `caie.py`, `vigia_scorer.py`, y los módulos de
scoring. Mantené la precisión técnica — no simplifiqués la terminología para hacer la
traducción más fácil.

---

## Lo que no voy a mergear

- Cualquier cosa que introduzca operaciones de punto flotante en el camino de decisión
  del veredicto sin una justificación documentada y una prueba de determinismo
- Cualquier cosa que permita al backend de LLM influir en el scoring o los veredictos
- Utilidades de fabricación de evidencia — herramientas diseñadas para generar
  artefactos forenses falsos plausibles para testing de evasión están fuera del alcance
  de este repositorio
- Parches que "arreglen" veredictos ABSTAIN en casos epistémicamente ambiguos forzando
  un veredicto MALICE o SUSPICION

---

## Licencia

Todas las contribuciones son aceptadas bajo la licencia Apache 2.0 del proyecto. Al
enviar un pull request, confirmás que tenés el derecho de licenciar tu contribución
bajo estos términos.

---

*"Un sistema que no puede ser criticado no puede ser confiado."*

*— Anna Tchijova, Proyecto VIGÍA*
