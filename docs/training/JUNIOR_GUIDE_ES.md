# Cómo leer un veredicto VIGÍA siendo analista SOC

Esta guía es para un analista que tiene un bundle de VIGÍA adelante por primera
vez. Explica qué es el veredicto, qué no es, y qué te muestra un reporte junior
(`*_report_junior_<lang>.md`), sección por sección. Versión en inglés:
[`JUNIOR_GUIDE.md`](./JUNIOR_GUIDE.md).

---

## 1. Qué estás mirando

VIGÍA no te dice *qué pasó*. Eso lo hace cualquier herramienta forense. Responde
una pregunta más angosta: **¿la evidencia muestra conducta deliberada, y cuánta?**
La respuesta es un solo token en una escala de cinco peldaños, sellado con un hash
antes de que ninguna persona ni modelo de lenguaje escriba una oración sobre él.

Existen tres tipos de bundle, y la cabecera del reporte dice cuál tenés:

| Familia (como se imprime) | Sale de | Campo del veredicto |
|---|---|---|
| `agent_audit` | `python3 vigia_agent.py` (Modo 1, sin LLM) | `agent_verdict` |
| `ebs_v1` | el pipeline sellado (`vigia/core/bundle_builder.py`) | `decision_trace.decision`, a veces también `caie_analysis.verdict` |
| `mcp_investigation` | una investigación en Claude Code / MCP (Modo 2) | `overall_verdict` o `final_verdict` |

El reporte junior es un **visor**. Copia los valores sellados carácter por carácter
y agrega explicación alrededor. No puede sumar evidencia, y si alguna vez difiere del
bundle, gana el bundle.

## 2. La escala

| Veredicto | Significa | No significa |
|---|---|---|
| `NOISE` | todo lo observado tiene una explicación normal e inocente | inocencia; los artefactos que nunca se recolectaron no están cubiertos |
| `SUSPICION` | una anomalía estructural real, sin señal de ocultamiento ni coordinación | atribución; puede existir una causa inocente que no se probó |
| `INTENT` | decisiones deliberadas produjeron este resultado (dos fuentes, refutación superada) | culpabilidad; es una inferencia sobre los artefactos analizados |
| `MALICE` | el actor esconde que está escondiendo (antiforense) | un hallazgo legal, una identificación ni una afirmación sobre el daño |
| `ABSTAIN` | no hay evidencia suficiente para clasificar | benigno; significa indeciso, y el reporte lista lo que falta |

`ERROR` no es un peldaño. Es la etiqueta de salida de una corrida que no terminó.

**El Modo 1 no tiene peldaño INTENT.** Un bundle de agente que dice `SUSPICION`
puede estar donde una investigación de Modo 2 diría `INTENT`: el pipeline
determinista tapa los casos límite en `SUSPICION` (ver `CLAUDE.md`, Verdict Scale).
Leé la narrativa sellada antes de decidir qué tan urgente es una `SUSPICION`.

## 3. Qué hacer en cada peldaño

Son pasos SOC genéricos; tu runbook manda.

- **NOISE**: cerrá o bajá la prioridad, guardá el bundle con el ticket, anotá el
  comportamiento normal que explicó la anomalía.
- **SUSPICION**: dejá el caso abierto, no bloquees todavía, buscá una segunda fuente
  independiente (otro host, log o sensor), pedí revisión senior antes de escalar.
- **INTENT**: escalá a respuesta a incidentes, preservá los originales en sólo
  lectura, empezá a dimensionar qué más pudo tocar el mismo actor.
- **MALICE**: escalá ahora, preservá todo (incluido lo que pudo haberse borrado), y
  dejá las decisiones de contención a IR y a la dirección.
- **ABSTAIN**: no cierres como benigno. Leé la sección de huecos, recolectá lo que
  nombra, volvé a correr, comparé los dos bundles.

## 4. Dos veredictos que no coinciden

Un bundle EBS v1 puede llevar dos campos con veredicto: la decisión sellada del
pipeline y el veredicto forense del módulo CAIE. Cuando difieren, el reporte muestra
**ambos** y un aviso; nunca elige uno. El ejemplo
`examples/VIGIA-REAL-SRL-DMZ-FTP_bundle_report_expert_en.md` muestra `ABSTAIN` al
lado de `MALICE`. No es un bug del reporte: el bundle selló ambos, y la nota del
perito (`r3_calibration_note`) explica por qué. No actúes sobre el más severo sólo
porque es más severo.

## 5. Recorrido por un reporte junior

Abrí `examples/VIGIA-KIWI-006_bundle_report_junior_es.md` (Modo 2, español) o
`examples/FF-GENUINE-001_agent_bundle_report_junior_en.md` (Modo 1, inglés) y seguí
las secciones numeradas:

1. **El veredicto.** Cada campo con veredicto, tal cual, con su nombre de campo. En
   un bundle de agente también ves `best_hypothesis`: es la etiqueta de la hipótesis
   ganadora, no un veredicto.
2. **Qué significa.** La tabla de la escala con el peldaño de este bundle marcado.
3. **Qué hacer ahora.** Los pasos genéricos de arriba para este peldaño.
4. **Qué NO concluir.** Las sobreinterpretaciones que meten en problemas a los
   analistas.
5. **Hallazgos.** Modo 2: cada hallazgo con sus tres capas peirceanas. Firstness es
   la observación cruda, Secondness es cómo choca con lo normal, Thirdness es el
   patrón deliberado que la produciría. La explicación benigna más fuerte
   (`devil_advocate`) está justo debajo, y cualquier veredicto candidato que un gate
   rechazó se lista después de los hallazgos. Modo 1: una tabla de señales con
   fracciones exactas y la narrativa sellada del propio pipeline.
6. **MITRE ATT&CK.** Ids de técnica encontrados en el bundle con el nombre y la
   descripción de MITRE (en inglés, nunca traducidos) y un enlace.
7. **Ciclo SANS.** Dónde cae un veredicto sellado (Identificación) y por qué la
   contención es una decisión humana.
8. **Huecos.** Lo que el bundle no dice. Que falte significa que no quedó
   registrado, no que no exista.
9. **Glosario.** Cada token sellado usado arriba, explicado.
10. **Cómo verificar.** El único comando que chequea la integridad de esta familia.

## 6. Tres hábitos

- **Citá, no parafrasees.** Cuando escribas el ticket, copiá el token del veredicto y
  el SHA-256 de origen de la cabecera del reporte. Cualquiera puede regenerar el
  reporte y chequear tu cita.
- **Los números son fracciones.** `19/20` es exacto. No es "95%": el pipeline usa
  aritmética exacta para que dos máquinas den el mismo resultado, y el reporte lo
  conserva.
- **El idioma es evidencia.** El texto citado conserva el idioma en que fue sellado.
  Una narrativa en español dentro de un reporte en inglés es el registro, no un
  defecto de presentación.

## 7. Para seguir

- `KNOWN_LIMITATIONS.md`: lo que el sistema no puede ver (L-001 en adelante). L-074
  cubre estos reportes.
- `docs/EXECUTION_MODES.md`: por qué existen las tres familias de bundle.
- [`EXPERT_GUIDE_ES.md`](./EXPERT_GUIDE_ES.md): verificación, familias de hashes,
  gates Daubert.
