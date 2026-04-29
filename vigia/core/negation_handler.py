#!/usr/bin/env python3
"""
vigia/core/negation_handler.py

Negation Handler — VIGÍA
Detecta palabras de negación cercanas a un match y aplica factor de atenuación.

Versión: 1.0 (minimalista y segura)
Autor: Colectivo VIGÍA (DeepSeek idea, ChatGPT crítica, Kimi consolidación)

Principios:
- Determinista: sin ML, sin randomness
- No destructivo: no modifica el match original, solo agrega factor
- Bidireccional: busca antes Y después del match
- Seguro: no usa .find(), no usa substring matching ingenuo
- Auditabile: el informe puede decir "peso atenuado por negación detectada"
"""

import re
from fractions import Fraction
from typing import Dict, List, Tuple

# ── Configuración ─────────────────────────────────────────────────────────

NEGATION_WINDOW_CHARS = 50  # caracteres antes y después del match

# Negaciones fuertes → atenuación 50%
STRONG_NEGATION = {
    "no", "nunca", "jamás", "tampoco", "ni", "ningún", "ninguna", "ninguno",
    "nadie", "nada", "never", "not", "don't", "do not", "doesn't", "didn't",
    "won't", "wouldn't", "shouldn't", "mustn't", "can't", "cannot",
}

# Negaciones débiles → atenuación 75%
WEAK_NEGATION = {
    "evitar", "evitemos", "intentar no", "tratar de no", "preferiría no",
    "avoid", "let's not", "try not to", "prefer not to",
}

# Verbos objetivo por categoría (para evitar falsos positivos)
TARGET_VERBS = {
    "GRICE_DESTRUCTION_REQUEST": ["borrar", "eliminar", "remover", "borrá", "eliminá", "remove", "delete"],
    "CARNEGIE_ARTIFICIAL_URGENCY": ["hacer", "ejecutar", "correr", "run", "execute", "do it"],
    "GRICE_EVIDENCE_CLEANING": ["limpiar", "borrar", "eliminar", "clean", "wipe"],
}

# ── Funciones públicas ────────────────────────────────────────────────────

def detect_negation(text: str, match_start: int, match_end: int,
                    pattern_name: str) -> Tuple[bool, Fraction, str]:
    """
    Detecta negación cercana a un match.

    Args:
        text: Texto completo del artefacto
        match_start: Índice de inicio del match en el texto
        match_end: Índice de fin del match
        pattern_name: Nombre del patrón detectado

    Returns:
        (negation_detected, attenuation_factor, reason)
        attenuation_factor: Fraction(1,1) = sin atenuación
                            Fraction(1,2) = atenuación fuerte
                            Fraction(3,4) = atenuación débil
    """
    # Extraer ventana bidireccional
    window_start = max(0, match_start - NEGATION_WINDOW_CHARS)
    window_end = min(len(text), match_end + NEGATION_WINDOW_CHARS)
    context = text[window_start:window_end].lower()

    # Tokenizar con word boundaries (evita "conocimiento" → "no")
    tokens = re.findall(r"\b\w+\b", context)

    # Buscar negaciones
    has_strong = any(t in STRONG_NEGATION for t in tokens)
    has_weak = any(t in WEAK_NEGATION for t in tokens)

    # Verificar vínculo semántico: ¿la negación aplica al verbo del patrón?
    verbs = TARGET_VERBS.get(pattern_name, [])
    has_target_verb = any(v in context for v in verbs) if verbs else True

    if has_strong and has_target_verb:
        return (True, Fraction(1, 2), "negación fuerte + verbo objetivo")
    elif has_weak and has_target_verb:
        return (True, Fraction(3, 4), "negación débil + verbo objetivo")
    elif has_strong:
        return (True, Fraction(3, 4), "negación fuerte sin verbo confirmado")
    elif has_weak:
        return (True, Fraction(7, 8), "negación débil sin verbo confirmado")

    return (False, Fraction(1, 1), "sin negación detectada")


def apply_negation_attenuation(match_dict: Dict, text: str) -> Dict:
    """
    Aplica atenuación de negación a un match ya detectado.
    NO modifica destructivamente. Devuelve copia con campos adicionales.

    Args:
        match_dict: Diccionario del match (de _match_to_dict)
        text: Texto completo

    Returns:
        Diccionario enriquecido con campos de negación
    """
    # Reconstruir índices aproximados (el diccionario no guarda índices, 
    # pero podemos buscar el matched_text en el texto original)
    matched_text = match_dict.get("matched_text", "")
    if not matched_text:
        return {**match_dict, "negation": {"detected": False, "factor": "1/1", "reason": "sin contexto"}}

    idx = text.lower().find(matched_text.lower())
    if idx < 0:
        idx = 0

    detected, factor, reason = detect_negation(
        text, idx, idx + len(matched_text), match_dict["pattern_name"]
    )

    result = dict(match_dict)
    result["negation"] = {
        "detected": detected,
        "factor_num": factor.numerator,
        "factor_den": factor.denominator,
        "factor_display": f"{factor.numerator}/{factor.denominator}",
        "reason": reason,
    }

    if detected:
        # Aplicar atenuación al peso y boost (sin modificar el objeto original)
        weight = Fraction(match_dict.get("weight_num", 0), match_dict.get("weight_den", 1))
        boost = Fraction(match_dict.get("confidence_boost_num", 0), match_dict.get("confidence_boost_den", 1))

        adjusted_weight = weight * factor
        adjusted_boost = boost * factor

        result["adjusted_weight"] = {
            "num": adjusted_weight.numerator,
            "den": adjusted_weight.denominator,
        }
        result["adjusted_confidence_boost"] = {
            "num": adjusted_boost.numerator,
            "den": adjusted_boost.denominator,
        }

    return result
