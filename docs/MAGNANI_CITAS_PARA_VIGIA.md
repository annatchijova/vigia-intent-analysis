# CITAS TEXTUALES CLAVE DE MAGNANI (2009) PARA VIGÍA

> **Fuente:** Magnani, L. (2009). *Abductive Cognition: The Epistemological and Eco-Cognitive Dimensions of Hypothetical Reasoning*. Cognitive Systems Monographs, Vol. 3. Springer-Verlag Berlin Heidelberg.  
> **DOI:** 10.1007/978-3-642-03631-6  
> **ISBN:** 978-3-642-03630-9 (hardcover) / 978-3-642-03631-6 (ebook)  
> **ISSN:** 1867-4925

---

## 📌 CITA 1 — DEFINICIÓN DE ABDUCCIÓN MANIPULATIVA

> "Manipulative abduction happens when we are thinking through doing and not only, in a pragmatic sense, about doing."
> — Magnani, L. (2009). *Abductive Cognition*, Springer, **p. 60** (sección 1.6)

**Traducción:** "La abducción manipulativa ocurre cuando pensamos a través del hacer y no solo, en sentido pragmático, sobre el hacer."

**Aplicación a VIGÍA:** Los detectores técnicos (`shellbag_analyzer.py`, `prefetch_analyzer.py`, etc.) no "leen" pasivamente los artefactos digitales — los **MANIPULAN**: parsean estructuras binarias, reconstruyen timelines, correlacionan datos. Eso es abducción manipulativa.

---

## 📌 CITA 2 — MEDIADORES EPISTÉMICOS

> "Many external things, usually inert from the epistemological point of view, can be transformed into what I call epistemic mediators."
> — Magnani, L. (2004/2009). *Abductive Cognition*, p. 221 (reafirmado en 2009)

**Traducción:** "Muchas cosas externas, normalmente inertes desde el punto de vista epistemológico, pueden transformarse en lo que llamo mediadores epistémicos."

**Aplicación a VIGÍA:** Un registro SAM, una entrada de prefetch, un shellbag — son "inertes" epistemológicamente hasta que el detector los manipula. El parseo los convierte en **mediadores epistémicos** que generan hipótesis.

---

## 📌 CITA 3 — ACCIÓN COMO GENERADORA DE INFORMACIÓN

> "Action provides otherwise unavailable information that enables the agent to solve problems by starting and performing a suitable abductive process of generation or selection of hypotheses."
> — Magnani, L. (2009). **p. 220**

**Traducción:** "La acción provee información de otro modo no disponible que permite al agente resolver problemas iniciando y realizando un proceso abductivo adecuado de generación o selección de hipótesis."

**Aplicación a VIGÍA:** El "parseo" es la acción. Sin parsear el binario crudo, la información está inaccesible. La acción de parsing genera hipótesis que de otro modo no existirían.

---

## 📌 CITA 4 — ABDUCCIÓN TEÓRICA vs MANIPULATIVA (LA DISTINCIÓN CLAVE)

> "What I call theoretical abduction certainly illustrates much of what is important in creative abductive reasoning, in humans and in computational programs, especially the objective of selecting and creating a set of hypotheses (diagnoses, causes, hypotheses) that are able to dispense good (preferred) explanations of data (observations), but fails to account for many cases of explanations occurring in science and in everyday reasoning when the exploitation of environment is crucial. It fails to account for those cases in which there is a kind of 'discovering through doing', cases in which new and still unexpressed information is codified by means of manipulations of some external objects (epistemic mediators)."
> — Magnani, L. (2009). **p. 11-12**

**Traducción:** "Lo que llamo abducción teórica ciertamente ilustra mucho de lo que es importante en el razonamiento abductivo creativo, en humanos y en programas computacionales, especialmente el objetivo de seleccionar y crear un conjunto de hipótesis (diagnósticos, causas, hipótesis) capaces de proporcionar buenas (preferidas) explicaciones de datos (observaciones), pero falla en dar cuenta de muchos casos de explicaciones que ocurren en la ciencia y en el razonamiento cotidiano cuando la explotación del entorno es crucial. Falla en dar cuenta de aquellos casos en los que hay una especie de 'descubrir a través del hacer', casos en los que información nueva y aún no expresada se codifica mediante manipulaciones de algunos objetos externos (mediadores epistémicos)."

**Aplicación a VIGÍA:** El motor abductivo (`abductive_reasoner.py`) hace abducción **TEÓRICA** (sentencial/model-based). Los detectores técnicos hacen abducción **MANIPULATIVA**. VIGÍA necesita **AMBAS**.

---

## 📌 CITA 5 — LA DISTINCIÓN ON-LINE / OFF-LINE

> "The epistemological distinction... between theoretical and manipulative abduction is certainly based on the possibility of separating the two aspects in real cognitive processes, resorting to the differentiation between off-line (theoretical, when only inner aspects are at stake) and on-line (manipulative, where the interplay between internal and external aspects is fundamental)."
> — Magnani, L. (2009). **p. 12**

**Traducción:** "La distinción epistemológica... entre abducción teórica y manipulativa se basa ciertamente en la posibilidad de separar los dos aspectos en procesos cognitivos reales, recurriendo a la diferenciación entre off-line (teórica, cuando solo están en juego aspectos internos) y on-line (manipulativa, donde el interplay entre aspectos internos y externos es fundamental)."

**Aplicación a VIGÍA:**
- **OFF-LINE:** `abductive_reasoner.py`, `likelihood_ratio.py`, `trust_fusion.py` (procesamiento interno de hipótesis)
- **ON-LINE:** `shellbag_analyzer.py`, `prefetch_analyzer.py` (interacción con artefactos externos)

---

## 📌 CITA 6 — MODELO ST (SELECT AND TEST)

> "The ST-model... describes the different roles played by such basic inference types in developing various kinds of medical reasoning (diagnosis, therapy planning, monitoring) but can be extended and regarded also as an illustration of scientific theory change. The model is consistent with the Peircean view about the various stages of scientific inquiry in terms of 'hypothesis' generation, deduction (prediction), and induction."
> — Magnani, L. (2009). **p. 9-10**, Figura 1.3

**Aplicación a VIGÍA:** El pipeline de VIGÍA **ES** el ST-model:
1. **ABDUCCIÓN:** generar hipótesis (`abductive_reasoner.py`)
2. **DEDUCCIÓN:** predecir consecuencias (`likelihood_ratio.py`)
3. **INDUCCIÓN:** evaluar contra datos observados (`trust_fusion.py`)

---

## 📌 CITA 7 — ABDUCCIÓN COMO PRESERVACIÓN DE IGNORANCIA

> "Abduction does not have to be considered a 'solution' of an ignorance problem, but rather a response to it, in which the agent reaches presumptive attainment rather than actual attainment."
> — Gabbay & Woods (citado por Magnani, 2009, **p. 11**)

**Aplicación a VIGÍA:** El veredicto `UNKNOWN` no es un fallo — es una **"preservación de ignorancia"** honesta. VIGÍA no afirma `MALICE` cuando no puede alcanzar "actual attainment" de la verdad.

---

## 📌 CITA 8 — LA CREATIVIDAD NO ES IRRACIONAL

> "Creativity and discovery are no longer seen as mysterious irrational processes, but, thanks to constructive accounts, they are viewed as complex relationships among different inferential steps that can be clearly analyzed and identified."
> — Magnani, L. (2009). **p. 2**

**Aplicación a VIGÍA:** VIGÍA es una **"constructive account"** de la abducción forense. No es magia, no es ML, es un pipeline de pasos inferenciales claramente analizables.

---

## 📌 CITA 9 — ABDUCCIÓN SENTENCIAL (PARA RESOLVE)

> "Sentential abduction can be rendered in different ways. For example, in the syllogistic framework we have just described abduction is considered like something propositional and as a type of fallacious reasoning. If we want to model abduction in a computational logic-based system, the fundamental operation is search."
> — Magnani, L. (2009). **p. 23** (sección 1.4)

**Aplicación a VIGÍA:** La función `resolve(ccs, risk, epsilon)` es una operación de **búsqueda** en el espacio de hipótesis — exactamente lo que Magnani describe como "sentential abduction".

---

## 📌 CITA 10 — MODELO-BASED ABDUCTION (PARA LIKELIHOOD RATIO)

> "Model-based reasoning is used to indicate the construction and manipulation of various kinds of representations, not mainly sentential and/or formal, but mental (visual imagistic, analogical, etc.) and/or related to external mediators."
> — Magnani, L. (2009). **p. 38** (sección 1.5.2)

**Aplicación a VIGÍA:** El scoring por fracciones en `likelihood_ratio.py` es una forma de **model-based abduction**: opera sobre modelos numéricos internos (no sobre datos crudos), calculando preferencias entre hipótesis explicativas.

---

## MAPA DE SECCIONES DEL LIBRO A COMPONENTES DE VIGÍA

| Sección del libro | Componente VIGÍA | Justificación |
|---|---|---|
| 1.1 Computational Modeling as Pragmatic Rule | Arquitectura general | Claridad computacional del código Python |
| 1.2 Computational Modeling and Scientific Discovery | Pipeline completo | El "computational turn" de VIGÍA |
| 1.3 What Is Abduction? (ST-Model) | `abductive_reasoner.py` → `likelihood_ratio.py` → `trust_fusion.py` | Ciclo abducción-deducción-inducción |
| 1.4 Sentential Abduction | `resolve(ccs, risk, epsilon)` | Búsqueda y selección de hipótesis |
| 1.5 Model-Based Creative Abduction | `likelihood_ratio.py` | Modelos numéricos internos |
| **1.6 Manipulative Abduction** | **Detectores técnicos forenses** | **THE BIG ONE — pensar a través del hacer** |
| 1.7 Mirroring Hidden Properties | Visualización de datos | Timelines, diagramas forenses |
| Cap. 2 Non-Explanatory Abduction | Veredicto `UNKNOWN` | Preservación de ignorancia |
| Cap. 3 Semiotic Brains | Arquitectura híbrida | Sistema humano + artefacto + entorno |
| Cap. 6 Affordances & Cognitive Niches | Reglas de detección nuevas | Creación de nuevas affordances |

---

## REFERENCIA BIBLIOGRÁFICA COMPLETA (BibTeX)

```bibtex
@book{magnani2009abductive,
  author    = {Magnani, Lorenzo},
  title     = {Abductive Cognition: The Epistemological and Eco-Cognitive Dimensions of Hypothetical Reasoning},
  series    = {Cognitive Systems Monographs},
  volume    = {3},
  publisher = {Springer-Verlag},
  address   = {Berlin Heidelberg},
  year      = {2009},
  doi       = {10.1007/978-3-642-03631-6},
  isbn      = {978-3-642-03630-9},
  issn      = {1867-4925}
}
```

---

*Documento extraído del PDF "L_Magnani_2009_Abductive_Cognition_The_E.pdf"*
*Para integración en README/paper de VIGÍA — POST-HACKATHON*
