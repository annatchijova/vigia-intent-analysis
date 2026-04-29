#!/usr/bin/env python3
"""
vigia/core/pattern_detector.py

Detector determinista de patrones semióticos adversariales.
NO usa ML. NO usa estadística. Solo regex + lógica abductiva.

Basado en corpus de 110+ casos forenses (sintéticos + datasets reales).
Schema: v1.0 | Standard: SANS_FIND_EVIL_2026
"""

import re
import sqlite3
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class PatternMatch:
    pattern_name: str
    category: str
    peirce_layer: str
    weight: float
    confidence_boost: float
    matched_text: str
    description: str
    case_origin: str


class SemioticPatternDetector:
    """
    Detector de fricciones semióticas en artefactos textuales.

    Uso:
        detector = SemioticPatternDetector("vigia/tools/forensic_patterns.sqlite")
        matches = detector.analyze_text("soy un desastre, rompí el proxy...")
        # Devuelve: [PatternMatch(CARNEGIE_WEAPONIZED_INCOMPETENCE, ...)]
    """

    def __init__(self, db_path: str = "vigia/tools/forensic_patterns.sqlite"):
        self.db_path = db_path
        self._patterns: List[Dict[str, Any]] = []
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Carga patrones en memoria para determinismo."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT pattern_name, category, pattern_regex, weight, 
                   description, case_origin, peirce_layer, confidence_boost
            FROM nlp_patterns
            ORDER BY weight DESC
        """).fetchall()
        conn.close()

        for row in rows:
            try:
                compiled = re.compile(row["pattern_regex"], re.IGNORECASE)
                self._patterns.append({
                    "name": row["pattern_name"],
                    "category": row["category"],
                    "regex": compiled,
                    "weight": row["weight"],
                    "description": row["description"],
                    "origin": row["case_origin"],
                    "layer": row["peirce_layer"],
                    "boost": row["confidence_boost"],
                })
            except re.error as e:
                # Patrón inválido: loggear pero no fallar
                print(f"[WARN] Regex inválido en {row['pattern_name']}: {e}")

    def analyze_text(self, text: str, context: Optional[str] = None) -> List[PatternMatch]:
        """
        Analiza texto buscando patrones semióticos.

        Args:
            text: El artefacto textual a analizar
            context: Contexto adicional (tipo de artefacto, fase IR)

        Returns:
            Lista de coincidencias ordenadas por peso descendente
        """
        matches = []
        text_lower = text.lower()

        for pat in self._patterns:
            match = pat["regex"].search(text)
            if match:
                # Extraer texto coincidente (contexto)
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                matched_text = text[start:end]

                matches.append(PatternMatch(
                    pattern_name=pat["name"],
                    category=pat["category"],
                    peirce_layer=pat["layer"],
                    weight=pat["weight"],
                    confidence_boost=pat["boost"],
                    matched_text=matched_text,
                    description=pat["description"],
                    case_origin=pat["origin"],
                ))

        # Ordenar por peso descendente
        matches.sort(key=lambda m: m.weight, reverse=True)
        return matches

    def analyze_artifact(self, artifact_content: str, artifact_type: str) -> Dict[str, Any]:
        """
        Análisis completo de un artefacto con scoring.

        Returns:
            {
                "matches": [...],
                "dominant_category": "ECO",
                "max_weight": 0.95,
                "confidence_adjustment": 0.15,
                "peirce_layers": ["FIRSTNESS", "SECONDNESS"],
                "summary": "3 patrones detectados: ECO_KEYBOARD_SLIP..."
            }
        """
        matches = self.analyze_text(artifact_content)

        if not matches:
            return {
                "matches": [],
                "dominant_category": None,
                "max_weight": 0.0,
                "confidence_adjustment": 0.0,
                "peirce_layers": [],
                "summary": "Sin patrones detectados",
            }

        # Calcular categoría dominante
        cat_weights: Dict[str, float] = {}
        for m in matches:
            cat_weights[m.category] = cat_weights.get(m.category, 0) + m.weight

        dominant = max(cat_weights, key=cat_weights.get)
        max_weight = max(m.weight for m in matches)

        # Ajuste de confianza: suma de boosts, capado en 0.20
        total_boost = sum(m.confidence_boost for m in matches)
        adjustment = min(total_boost, 0.20)

        layers = list(set(m.peirce_layer for m in matches))

        summary = f"{len(matches)} patrones detectados: " + ", ".join(
            f"{m.pattern_name}({m.weight:.2f})" for m in matches[:3]
        )

        return {
            "matches": [self._match_to_dict(m) for m in matches],
            "dominant_category": dominant,
            "max_weight": max_weight,
            "confidence_adjustment": adjustment,
            "peirce_layers": layers,
            "summary": summary,
        }

    def _match_to_dict(self, match: PatternMatch) -> Dict[str, Any]:
        return {
            "pattern_name": match.pattern_name,
            "category": match.category,
            "peirce_layer": match.peirce_layer,
            "weight": match.weight,
            "confidence_boost": match.confidence_boost,
            "matched_text": match.matched_text,
            "description": match.description,
            "case_origin": match.case_origin,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas del detector."""
        return {
            "total_patterns": len(self._patterns),
            "categories": list(set(p["category"] for p in self._patterns)),
            "max_weight": max(p["weight"] for p in self._patterns) if self._patterns else 0,
            "db_path": self.db_path,
        }


# ── Función de conveniencia para el pipeline ───────────────────────────────

def detect_semiotic_frictions(artifact_content: str, artifact_type: str = "text") -> Dict[str, Any]:
    """
    API de alto nivel para el pipeline VIGÍA.
    Detecta fricciones semióticas en un artefacto y devuelve
    ajustes para el RiskBoundedDecisionLayer.
    """
    detector = SemioticPatternDetector()
    result = detector.analyze_artifact(artifact_content, artifact_type)

    # Si hay colisión semiótica (meta-ataque), elevar inmediatamente
    if any(m.pattern_name == "ECO_SEMIOTIC_COLLISION" for m in result.get("matches", [])):
        result["alert_level"] = "CRITICAL"
        result["confidence_adjustment"] = 0.25  # Override del cap

    return result
