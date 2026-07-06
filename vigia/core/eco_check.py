"""
vigia/core/eco_check.py — Núcleo determinista del filtro Eco (fuente única).

Umberto Eco: la conspiración perfecta no deja rastros obvios; si hay
demasiados, alguien los plantó (Malice by Distraction). Este módulo contiene
la lógica pura del detector — extraída del tool MCP
`detect_eco_overinterpretation` (vigia_sift_bridge) para que el scorer
determinista pueda consumir EXACTAMENTE el mismo criterio sin depender del
bridge asíncrono (FASE 2 / D1, docs/FASE2_EVIDENCIA_EXCULPATORIA.md §4.5):

    D1 — barra de corroboración mínima: los artefactos exculpatorios pasan
    por el filtro Eco ANTES de ser apartados del composite. Documentación
    demasiado perfecta (o que menciona vocabulario de ataque siendo
    supuestamente un memo de autorización) = señal, no refutación.

stdlib-only, sin floats en la decisión (comparación entera 2*hits > total).
"""
from __future__ import annotations

import re

__all__ = [
    "OBVIOUS_BAIT_TERMS",
    "word_search",
    "text_obvious_bait_hits",
    "eco_overinterpretation_check",
]

# Vocabulario de cebo obvio — término presente = la "evidencia" grita ataque.
# Fuente única: el tool MCP delega en esta lista (antes vivía inline en el
# bridge). Cambios acá son cambios de doctrina del filtro Eco.
OBVIOUS_BAIT_TERMS: tuple = (
    "hack", "virus", "password", "contraseña", "attack",
    "log_deleted", "malware", "backdoor", "exploit",
    "admin123", "root", "pwned", "compromised", "hacked",
    # Términos de threat intel y herramientas de ataque conocidas
    "mimikatz", "ransomware", "vssadmin", "onion", "virustotal",
    "c2", "cobalt", "metasploit", "meterpreter", "empire",
    "lsass", "credential", "dump", "exfil", "lateral",
    "threatintel", "threat intel", "known_ransomware", "known malicious",
    "public threat", "VirusTotal", "virus total",
    # IOCs de red y atribución geográfica
    "port scan", "portscan", "russian isp", "russian range",
    "known russian", "isp range", "known bad", "known malware",
    "blacklisted", "blocked ip", "tor exit",
    "command and control", "c&c", "botnet",
)


def word_search(term: str, text: str) -> bool:
    """
    Búsqueda con detección inteligente de límites de palabra.

    Gemini fix (heredado del bridge): \\b falla en términos con caracteres
    no-alfanuméricos ([ERROR], c&c, #tag) — para esos se usan límites de
    espacio/línea. Case-insensitive.
    """
    stripped = term.strip()
    if not stripped:
        return False
    has_special = bool(re.search(r"[^\w]", stripped))
    escaped = re.escape(stripped)
    if has_special:
        pattern = r"(?:^|(?<=\s))" + escaped + r"(?=\s|$)"
    else:
        pattern = r"\b" + escaped + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def text_obvious_bait_hits(text: str) -> list:
    """Términos de cebo obvio presentes en un texto (para el gate D1
    por-artefacto del scorer). Lista vacía = el texto no grita ataque."""
    lowered = text.lower()
    return [t for t in OBVIOUS_BAIT_TERMS if word_search(t, lowered)]


def eco_overinterpretation_check(evidence_list: list) -> dict:
    """
    Chequeo Eco a nivel de conjunto — la lógica original del tool MCP:
    si más de la mitad de las evidencias contienen términos de cebo obvio,
    la escena probablemente fue plantada (POSSIBLE_SCENE_STAGING).

    Determinista, sin floats en la decisión: `2*len(found) > len(list)`.
    El campo obvious_ratio se expone solo como informativo.
    """
    found = []
    for ev in evidence_list:
        hits = text_obvious_bait_hits(str(ev))
        if hits:
            found.append({"evidence": str(ev), "obvious_terms": hits})

    n = len(evidence_list)
    staged = bool(n) and (2 * len(found) > n)
    ratio = round(len(found) / n, 2) if n else 0.0

    if staged:
        return {
            "verdict": "POSSIBLE_SCENE_STAGING",
            "eco_theory": ("Attacker wants you looking here. "
                           "An overly obvious scene is deliberate distraction."),
            "suspicious_evidence": found,
            "obvious_ratio": ratio,
            "abduction": ("ABDUCTIVE HYPOTHESIS: This evidence was manufactured "
                          "or planted. The real trail is elsewhere. "
                          "Look for what is NOT there, not what is."),
            "suggested_action": ("INVERT ANALYSIS: search for significant "
                                 "silence, not obvious noise."),
        }
    return {
        "verdict": "NORMAL_DISTRIBUTION",
        "interpretation": ("Evidence distribution within expected parameters. "
                           "No staging detected."),
        "obvious_ratio": ratio,
        "suspicious_evidence": found,
    }
