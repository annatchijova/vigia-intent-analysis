"""
vigia/core/explainable_governance.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. ANTI-RECON: Las "Limitaciones Conocidas" ahora son GENÉRICAS.
   NO enumeramos ataques específicos que el sistema "no detecta".
   En su lugar, usamos categorías abstractas que no dan receta al atacante.
2. Daubert Compliance Statement ahora incluye advertencia de que
   las limitaciones son propiedad intelectual del sistema y no públicas.
3. Se eliminó la sección detallada de "Zero-trace attacks" como categoría
   explícita. Ahora es "Limitaciones de alcance de artefactos".
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from html import escape


class ExplanationEngine:
    TEMPLATES = {
        "ACCEPT": {
            "header": "## ✅ ANÁLISIS FORENSE: ACEPTADO",
            "interpretation": "El contenido presenta características consistentes con autoría humana legítima.",
        },
        "REJECT": {
            "header": "## ❌ ANÁLISIS FORENSE: RECHAZADO",
            "interpretation": "El contenido presenta patrones anómalos consistentes con generación automatizada o manipulación.",
        },
        "ABSTAIN": {
            "header": "## ⚠️ ANÁLISIS FORENSE: ABSTENCIÓN",
            "interpretation": "El caso requiere validación humana experta debido a evidencia insuficiente o contradictoria.",
        },
        "ABSTAIN_CONTRADICTION": {
            "header": "## ⚠️ ANÁLISIS FORENSE: ABSTENCIÓN POR CONTRADICCIÓN ABDUCTIVA",
            "interpretation": "Se identifican múltiples patrones mutuamente incompatibles activos simultáneamente.",
        },
    }

    REASON_CODES = {
        "ABSTAIN_DRIFT": "Deriva estadística detectada",
        "ABSTAIN_INSTABILITY": "Inestabilidad en grafo de evidencia",
        "ABSTAIN_INTENTION": "Inconsistencia entre intención inferida y evidencia física",
        "ABSTAIN_ZONE": "Riesgo en zona de decisión ambigua",
        "ABSTAIN_CONTRADICTION": "Contradicción abductiva: patrones incompatibles coexisten",
    }

    CONTRADICTION_TYPES = {
        "EVIDENCIAL": "Artefactos incompatibles entre sí",
        "TEMPORAL": "Cronología imposible",
        "OPERATIONAL": "TTPs incompatibles",
        "ADVERSARIAL": "Señales de manipulación o fabricación",
    }

    def __init__(self, bundle: Dict[str, Any]):
        self.bundle = bundle
        self.decision = bundle.get("decision_trace", {})
        self.graph = bundle.get("evidence_graph", {})
        self.policy = bundle.get("policy_spec", {})

    def generate_explanation(self) -> str:
        sections = [
            self._header(), self._summary(), self._evidence_table(),
            self._conflict_narrative(),
            self._ontological_summary(),
            self._risk_decomposition(), self._graph_metrics(),
            self._interventions(), self._daubert_compliance(),
            self._limitations(), self._footer(),
        ]
        return "\n\n".join(s for s in sections if s)

    def to_html(self) -> str:
        md = self.generate_explanation()
        lines = md.split("\n")
        html_lines = ["<div style='font-family:monospace;color:#00ff41;background:#0a0e27;padding:20px;'>"]
        in_table = False
        for raw_line in lines:
            line = escape(raw_line.strip())
            if line.startswith("## "):
                html_lines.append("<h2 style='color:#00ff41;text-shadow:0 0 5px #00ff41;'>" + line[3:] + "</h2>")
            elif line.startswith("### "):
                html_lines.append("<h3 style='color:#00ff41;'>" + line[4:] + "</h3>")
            elif line.startswith("| "):
                if not in_table:
                    html_lines.append("<table border='1' style='border-collapse:collapse;color:#00ff41;'>")
                    in_table = True
                cells = [c.strip() for c in line.split("|")[1:-1]]
                html_lines.append("<tr>" + "".join("<td style='padding:5px;border:1px solid #00ff41;'>" + c + "</td>" for c in cells) + "</tr>")
            elif in_table and not line.startswith("| "):
                html_lines.append("</table>")
                in_table = False
                html_lines.append("<p>" + line + "</p>")
            elif line.startswith("- "):
                html_lines.append("<li>" + line[2:] + "</li>")
            elif line:
                html_lines.append("<p>" + line + "</p>")
        if in_table:
            html_lines.append("</table>")
        html_lines.append("</div>")
        return "\n".join(html_lines)

    def _header(self) -> str:
        d = self.decision.get("decision", "UNKNOWN")
        reason = self.decision.get("reason", "")
        if "CONTRADICTION" in str(reason).upper():
            d = "ABSTAIN_CONTRADICTION"
        t = self.TEMPLATES.get(d, self.TEMPLATES["ABSTAIN"])
        return "# " + t["header"] + "\n\n**Bundle ID:** `" + escape(str(self.bundle.get("bundle_id","N/A"))) + "`  \n**Timestamp:** " + escape(str(self.bundle.get("timestamp","N/A")))

    def _summary(self) -> str:
        d = self.decision.get("decision", "ABSTAIN")
        reason = self.decision.get("reason", "")
        if "CONTRADICTION" in str(reason).upper():
            d = "ABSTAIN_CONTRADICTION"
        t = self.TEMPLATES.get(d, self.TEMPLATES["ABSTAIN"])
        posterior = self.decision.get("posterior", 0.0)
        risk = self.decision.get("risk", 0.0)
        contradiction_type = self.decision.get("contradiction_type")
        lines = [
            "## Resumen Ejecutivo", "", "**Decisión:** " + escape(str(d)),
            "**Posterior:** " + str(round(posterior * 100, 2)) + "%",
            "**Riesgo:** " + str(round(risk, 4)),
            "", "### Interpretación", "", t["interpretation"],
        ]
        if d == "ABSTAIN_CONTRADICTION":
            near_misses = self.decision.get("near_misses", [])
            pivot_signals = self.decision.get("pivot_signals", [])
            lines.extend(["", "### Detalle de la contradicción", "", "Se identifican múltiples patrones mutuamente incompatibles:", ""])
            for nm in near_misses[:3]:
                lines.append("- **Patrón A:** " + escape(str(nm.get("pattern","?"))) + " → soportado por señales " + escape(str(nm.get("signals","[]"))))
            for pv in pivot_signals[:3]:
                lines.append("- **Patrón B:** " + escape(str(pv.get("pattern","?"))) + " → soportado por señales " + escape(str(pv.get("signals","[]"))))
            lines.extend(["", "Ambos patrones no pueden ser verdaderos simultáneamente.", "", "**Conclusión:** El sistema no puede resolver la contradicción."])
            if contradiction_type and contradiction_type in self.CONTRADICTION_TYPES:
                desc = self.CONTRADICTION_TYPES[contradiction_type]
                lines.extend(["", "**Tipo de contradicción:** " + escape(contradiction_type) + " — " + escape(desc), "", "Esta tipificación permite priorizar la investigación forense."])
        return "\n".join(lines)

    def _evidence_table(self) -> str:
        nodes = self.graph.get("nodes", [])
        if not nodes:
            return ""
        sorted_nodes = sorted(nodes, key=lambda x: x.get("z_score", 0), reverse=True)
        lines = [
            "## Análisis de Evidencias", "",
            "| Herramienta | Z-Score | Confianza | Valor |",
            "|-------------|---------|-----------|-------|",
        ]
        for node in sorted_nodes[:10]:
            tool = escape(str(node.get("tool_name", "UNKNOWN")))
            z = node.get("z_score", 0.0)
            c = node.get("confidence", 0.0)
            v = node.get("value", 0.0)
            emoji = "🔴" if z > 2.8 else "🟡" if z > 1.96 else "🟢"
            lines.append("| " + emoji + " " + tool + " | " + str(round(z, 2)) + " | " + str(round(c, 2)) + " | " + str(round(v, 4)) + " |")
        return "\n".join(lines)

    def _conflict_narrative(self) -> str:
        nodes = self.graph.get("nodes", [])
        conflict_signals = [
            n for n in nodes
            if n.get("metadata", {}).get("conflict") == True
        ]
        if not conflict_signals:
            return ""
        def dominance_key(node):
            z = node.get("z_score", 0.0)
            gamma_str = node.get("metadata", {}).get("gamma_type", "unknown")
            gamma_map = {
                "memory": 0.95, "mft": 0.80, "registry": 0.70,
                "event_log": 0.60, "network": 0.75,
            }
            gamma = gamma_map.get(gamma_str, 1.0)
            return z * gamma
        conflict_signals.sort(key=dominance_key, reverse=True)
        dominant = conflict_signals[0]
        dom_tool = escape(str(dominant.get("tool_name", "UNKNOWN")))
        dom_z = dominant.get("z_score", 0.0)
        dom_gamma = dominant.get("metadata", {}).get("gamma_type", "unknown")
        sources = dominant.get("metadata", {}).get("conflict_sources", [])
        z_before = dominant.get("metadata", {}).get("z_before_conflict", "N/A")
        z_after = dominant.get("metadata", {}).get("z_after_conflict", "N/A")
        penalty = dominant.get("metadata", {}).get("conflict_penalty", "N/A")
        lines = [
            "## Evaluación de Consistencia Inter-Artefacto",
            "",
            "Se detectaron inconsistencias entre múltiples fuentes de evidencia asociadas a la misma entidad operacional.",
            "",
            f"- **Fuentes en conflicto:** {escape(str(sorted(set(sources))))}",
            f"- **Señal dominante:** {dom_tool} (z={dom_z}, Γ={dom_gamma})",
            f"- **Penalización de coherencia:** {escape(str(penalty))}",
            f"- **z antes del conflicto:** {escape(str(z_before))}",
            f"- **z después del conflicto:** {escape(str(z_after))}",
            "",
            "### Interpretación técnica",
            "",
            "La evidencia presenta divergencia semántica. Se prioriza la fuente con mayor resistencia a la manipulación (Γ), mientras que la inconsistencia reduce la certeza global del análisis.",
            "",
            "### Impacto en el veredicto",
            "",
            "El score fue ajustado mediante penalización de coherencia, sin descartar la señal dominante.",
            "",
        ]
        if sources:
            has_memory = any("memory" in s for s in sources)
            has_logs = any("event" in s for s in sources)
            if has_memory and has_logs:
                lines.extend([
                    "> **Clasificación:** SILENCE_CONTRADICTION",
                    ">",
                    "> La evidencia de memoria confirma actividad maliciosa, pero los logs no registran trazas correspondientes. Esto sugiere evasión de telemetría o borrado selectivo de logs (Event ID 1102/104).",
                ])
            else:
                lines.extend([
                    "> **Clasificación:** EVIDENCIAL_CONTRADICTION",
                    ">",
                    "> Las fuentes de evidencia presentan interpretaciones divergentes del mismo fenómeno operacional.",
                ])
        return "\n".join(lines)

    def _ontological_summary(self) -> str:
        ranked = self.graph.get("ranked_hypotheses", [])
        if not ranked:
            return ""
        techniques = [h for h in ranked if h.get("level") == "TECHNIQUE" or h.get("ontological_level") == "TECHNIQUE"]
        tactics = [h for h in ranked if h.get("level") == "TACTIC" or h.get("ontological_level") == "TACTIC"]
        objectives = [h for h in ranked if h.get("level") == "OBJECTIVE" or h.get("ontological_level") == "OBJECTIVE"]
        top_technique = techniques[0] if techniques else None
        top_tactic = tactics[0] if tactics else None
        top_objective = objectives[0] if objectives else None
        lines = [
            "## Hipótesis por Nivel Ontológico", "",
            "- **Técnicas:** " + str(len(techniques)) + " (mecanismos observables)",
            "- **Tácticas:** " + str(len(tactics)) + " (comportamientos)",
            "- **Objetivos:** " + str(len(objectives)) + " (fines últimos)",
            "", "### Top por nivel",
        ]
        if top_technique:
            name = escape(str(top_technique.get("name", "N/A")))
            post = top_technique.get("posterior", "N/A")
            lines.append("- **Top Técnica:** " + name + " (posterior: " + str(post) + ")")
        if top_tactic:
            name = escape(str(top_tactic.get("name", "N/A")))
            post = top_tactic.get("posterior", "N/A")
            lines.append("- **Top Táctica:** " + name + " (posterior: " + str(post) + ")")
        if top_objective:
            name = escape(str(top_objective.get("name", "N/A")))
            post = top_objective.get("posterior", "N/A")
            lines.append("- **Top Objetivo:** " + name + " (posterior: " + str(post) + ")")
        lines.extend([
            "",
            "> **Nota:** Estos niveles no compiten directamente. Una técnica (MEMORY_INJECTION)",
            "> puede servir a una táctica (LATERAL_MOVEMENT) que a su vez sirve a un",
            "> objetivo (DATA_EXFILTRATION).",
            "",
            "> **Advertencia:** El ranking global no implica competencia directa entre",
            "> niveles ontológicos distintos.",
        ])
        if top_technique and top_tactic and top_objective:
            lines.extend([
                "",
                "### Cadena Causal Inferida",
                "",
                "1. **Técnica detectada:** " + escape(str(top_technique.get("name","?"))) + " (Nivel Mecanismo)",
                "2. **Táctica habilitada:** " + escape(str(top_tactic.get("name","?"))) + " (Nivel Intención)",
                "3. **Objetivo inferido:** " + escape(str(top_objective.get("name","?"))) + " (Nivel Finalidad)",
            ])
        return "\n".join(lines)

    def _risk_decomposition(self) -> str:
        risk = self.decision.get("risk", 0.0)
        posterior = self.decision.get("posterior", 0.0)
        return "\n".join([
            "## Descomposición del Riesgo", "",
            "**Fórmula:** r = (1-P) · (1+λD) · (1+γ(1-S)) · (1+ω(1-I))", "",
            "- **Posterior (P):** " + str(round(posterior, 4)),
            "- **Incertidumbre base:** " + str(round(1-posterior, 4)),
            "- **Riesgo total:** " + str(round(risk, 4)),
        ])

    def _graph_metrics(self) -> str:
        edges = self.graph.get("edges", [])
        nodes = self.graph.get("nodes", [])
        stability = self.graph.get("graph_stability", 0.0)
        return "\n".join([
            "## Métricas del Grafo", "",
            "- **Nodos:** " + str(len(nodes)),
            "- **Aristas:** " + str(len(edges)),
            "- **Estabilidad global:** " + str(round(stability, 2)),
        ])

    def _interventions(self) -> str:
        if self.decision.get("decision") != "ABSTAIN":
            return ""
        actions = self.bundle.get("actions", [])
        lines = ["## Recomendaciones de Intervención", ""]
        if not actions:
            lines.extend(["1. Validación manual experta", "2. Solicitar evidencia adicional", "3. Re-ejecutar con capacidades completas"])
        else:
            for i, action in enumerate(actions[:5], 1):
                lines.append(str(i) + ". " + escape(str(action.get("description", "Sin descripción"))))
        return "\n".join(lines)

    def _daubert_compliance(self) -> str:
        return "\n".join([
            "## Daubert Compliance Statement", "",
            "### 1. Testability (Falsabilidad)",
            "Este análisis es completamente reproducible ejecutando el mismo pipeline sobre el mismo input. "
            "La cadena de custodia utiliza hashing criptográfico (SHA256) y los identificadores de evento son funciones puras del contenido. "
            "No hay fuentes de entropía del reloj del sistema en la lógica de decisión.", "",
            "### 2. Known Error Rate",
            "El sistema reporta explícitamente:",
            "- Incertidumbre: posterior probability con aritmética racional (Fraction).",
            "- Estabilidad: verdict_stability derivado del grafo de evidencia.",
            "- Señales contradictorias: near_misses y pivot_signals cuando hay contradicción abductiva.",
            "- Tasa de fallo del pipeline: monitoreada por PipelineHealthMonitor (umbral heurístico configurable).", "",
            "### 3. Standards",
            "El análisis sigue principios consistentes con:",
            "- Cadena de custodia digital (hashing, inmutabilidad, linked list verificable).",
            "- Razonamiento abductivo formal (Peirce: Firstness / Secondness / Thirdness).",
            "- Detección de evasión adversarial (threshold clustering, coordinated evasion, asymmetric evasion).", "",
            "### 4. General Acceptance",
            "**Técnicas aceptadas utilizadas:**",
            "- Hashing criptográfico (SHA-256)",
            "- Análisis temporal de artefactos",
            "- Correlación de evidencias cruzadas",
            "- Cadena de custodia digital estándar", "",
            "**Síntesis novedosa:**",
            "Este sistema combina las técnicas anteriores con un marco abductivo estructurado (Peirce), "
            "que es una formalización matemática del razonamiento inferencial ya utilizado por analistas humanos expertos. "
            "La novedad reside en la *automatización determinista* del proceso, no en la metodología subyacente.", "",
            "**Advertencia:** El umbral de admisibilidad del pipeline (`DAUBERT_MAX_FAILURE_RATE`) es un parámetro heurístico configurable. "
            "El estándar Daubert exige que la tasa de error sea *conocida y documentada*, no inferior a un valor fijo arbitrario.",
        ])

    def _limitations(self) -> str:
        """
        FIX P0: Limitaciones GENÉRICAS. No damos receta al atacante.
        Las limitaciones específicas están en documentación interna (NO pública).
        """
        return "\n".join([
            "## Limitaciones Conocidas del Sistema", "",
            "Las siguientes limitaciones son inherentes al diseño y deben considerarse al interpretar resultados:", "",
            "### L1: Independencia de señales",
            "- El motor bayesiano asume independencia condicional entre herramientas. "
            "En la práctica, herramientas de la misma familia están correlacionadas. "
            "Esto puede producir sobreestimación leve de confianza cuando múltiples herramientas similares reportan activación. "
            "**Mitigación:** `EvidenceGraph` penaliza pares correlacionados (twin pairs). `noisy_or_correlated()` aplica penalización por doble conteo semántico.", "",
            "### L2: Detección de evasión adversarial",
            "- Los umbrales de detección de evasión están calibrados por razonamiento adversarial, no por dataset empírico. "
            "Un atacante sofisticado puede diseñar evasión que mantenga parámetros justo por encima de umbrales heurísticos. "
            "**Mitigación:** Umbrales configurables. Metadata incluye `thresholds_used` para trazabilidad.", "",
            "### L3: Memoria volátil",
            "- `MemoryForensicsEngine` depende de Volatility3 para parseo de dumps. "
            "Técnicas de evasión de kernel avanzadas pueden no ser detectables. "
            "**Mitigación:** El sistema reporta explícitamente cuando no encuentra anomalías, recomendando análisis complementario de disco y registro.", "",
            "### L4: Alcance de artefactos",
            "- El sistema analiza artefactos digitales estándar (memoria, disco, registro, logs, red). "
            "Ataques que operan enteramente fuera de estos artefactos o que los manipulan consistentemente "
            "pueden no dejar trazas detectables. "
            "**Mitigación:** Correlación cross-source en `UnifiedTimelineEngine` (futuro).", "",
            "### L5: Ontología jerárquica",
            "- El sistema rankea hipótesis de distintos niveles ontológicos (técnica, táctica, objetivo) "
            "en un mismo espacio de probabilidad. Esto es una limitación conocida: los niveles no compiten "
            "directamente, pero el ranking global puede sugerirlo. "
            "**Mitigación:** La sección 'Hipótesis por Nivel Ontológico' en este reporte documenta explícitamente "
            "la separación y evita interpretación errónea.", "",
            "*Estas limitaciones no invalidan el sistema; lo contextualizan para uso pericial informado.*",
            "",
            "*Nota de seguridad: Las limitaciones técnicas detalladas son propiedad intelectual del sistema "
            "y se comparten bajo NDA con auditores autorizados únicamente.*",
        ])

    def _footer(self) -> str:
        return "\n".join([
            "---",
            "## Verificación",
            "**Bundle Hash:** `" + escape(str(self.bundle.get("bundle_hash","N/A"))) + "`", "",
            "Para verificar: `python forensics/verify_ebs_v1.py <bundle.json>`", "",
            "*VIGÍA Forensic Intelligence Engine v3.0*",
        ])
