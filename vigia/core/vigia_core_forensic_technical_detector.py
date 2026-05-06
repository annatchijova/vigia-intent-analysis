#!/usr/bin/env python3
"""
vigia/core/forensic_technical_detector.py
 
Detector forense técnico determinístico — complementa SemioticDetectorV2.
Detecta TTPs explícitos en texto de artefactos forenses.
 
Invariantes:
- I2: mismo input → mismo output siempre
- I7: toda lógica usa Fraction — sin floats internos
- I9: toda detección trazable a regex explícita
- Sin ML, sin sklearn, sin dependencias externas
"""
from __future__ import annotations
 
import re
import unicodedata
from fractions import Fraction
from typing import Dict, List, Tuple
 
# ── Catálogo de indicadores forenses técnicos ─────────────────────────────
# (category, indicator_id, compiled_regex, weight: Fraction, z_contribution: Fraction)
 
IFT_CATALOG: List[Tuple[str, str, re.Pattern, Fraction, Fraction]] = [
    # IDENTITY
    ("identity", "EVIL_ALIAS",
     re.compile(r'\b(?:mr\.7\s*)?evil\b', re.I),
     Fraction(9, 10), Fraction(32, 10)),
    ("identity", "SUSPICIOUS_NICK",
     re.compile(r'\b(?:mrevil|evilrulez|l33t|elite\.hacker|darkside|shadowhack)\w*\b', re.I),
     Fraction(8, 10), Fraction(24, 10)),
    ("identity", "ATTACKER_ALIAS",
     re.compile(r'\balias\s+(?:de\s+)?atacante\b|\bnick(?:name)?\s+malicioso\b', re.I),
     Fraction(8, 10), Fraction(28, 10)),
 
    # NETWORK
    ("network", "PCAP_INTERCEPT",
     re.compile(r'\bpcap\b.{0,60}?\b(?:terceros|interceptado|ajenos|externos|no\s*autorizados)\b', re.I),
     Fraction(9, 10), Fraction(34, 10)),
    ("network", "WAR_DRIVING",
     re.compile(r'\bwar\s*driving\b|\bwardriving\b|\bwifi.{0,20}intercept', re.I),
     Fraction(7, 10), Fraction(22, 10)),
    ("network", "SNIFFER",
     re.compile(r'\b(?:sniffer|modo\s+promiscuo|promiscuous\s*mode|packet\s*capture\s+ilegal)\b', re.I),
     Fraction(8, 10), Fraction(30, 10)),
    ("network", "C2_TRAFFIC",
     re.compile(r'\bc2\b|\bcommand.{0,10}control\b|\bmalicious\.com\b|\battacker\.com\b|\bevil\.com\b', re.I),
     Fraction(9, 10), Fraction(36, 10)),
    ("network", "CREDENTIAL_THEFT",
     re.compile(r'\bcontraseñas?\s+robadas?\b|\bcredenciales?\s+(?:robadas?|exfiltradas?)\b|\bpassword\s+theft\b', re.I),
     Fraction(9, 10), Fraction(34, 10)),
 
    # COMMUNITY / IRC
    ("community", "HACKER_CHANNEL",
     re.compile(r'#(?:elite\.?hackers?|warez|crack(?:ing)?|darknet|undernet\.?hack|evilfork)', re.I),
     Fraction(10, 10), Fraction(40, 10)),
    ("community", "HACKER_NICK",
     re.compile(r'\bnick\s*:?\s*(?:mr\.?\s*evil|mrevilrulez|mini\s*me)\b', re.I),
     Fraction(9, 10), Fraction(32, 10)),
    ("community", "IRC_HACKING",
     re.compile(r'\birc\b.{0,40}(?:hacking|warez|elite|dark)', re.I),
     Fraction(8, 10), Fraction(28, 10)),
 
    # TOOLS
    ("tools", "HACKING_TOOL",
     re.compile(r'\b(?:keylogger|mimikatz|metasploit|cobalt\s*strike|meterpreter|rootkit|netbus|sub7|darkcomet)\b', re.I),
     Fraction(10, 10), Fraction(42, 10)),
    ("tools", "WIRELESS_ATTACK",
     re.compile(r'\b(?:aircrack|kismet|wireshark.{0,20}intercept|ethereal.{0,20}intercept|netstumbler)\b', re.I),
     Fraction(8, 10), Fraction(30, 10)),
    ("tools", "OBFUSCATION",
     re.compile(r'\bbase64\s*[|> ]\s*(?:bash|sh)\b|\bpowershell\s+-enc\b|\bcertutil\s+-decode\b', re.I),
     Fraction(9, 10), Fraction(36, 10)),
    ("tools", "RAT_TOOL",
     re.compile(r'\b(?:rat\s+(?:tool|cliente?)|remote\s+access\s+trojan|troyano\s+acceso\s+remoto)\b', re.I),
     Fraction(9, 10), Fraction(34, 10)),
 
    # COMMANDS
    ("commands", "DESTRUCTIVE",
     re.compile(r'\brm\s+-rf\s+/\b|\bhistory\s+-c\b|\bshred\s+-u\b|\bhistcontrol\b', re.I),
     Fraction(10, 10), Fraction(45, 10)),
    ("commands", "EXFIL",
     re.compile(r'\bexfil(?:trac)?\b|\bnc\s+-e\s+|\bmysqldump.{0,30}(?:attacker|evil|malicious)\b', re.I),
     Fraction(9, 10), Fraction(38, 10)),
    ("commands", "SHADOW_COPY",
     re.compile(r'\b/etc/shadow\b.{0,30}(?:rob|copy|send|mail|exfil|attacker)', re.I),
     Fraction(10, 10), Fraction(40, 10)),
    ("commands", "PRIVILEGE_ABUSE",
     re.compile(r'\bchmod\s+777\s+/\b|\bchown\s+root\b.{0,20}(?:backdoor|malware)', re.I),
     Fraction(8, 10), Fraction(30, 10)),
 
    # TEMPORAL ANOMALIES
    ("temporal", "TIME_ANOMALY",
     re.compile(r'\batime\s*[<> ]\s*mtime\b|\bduraci[oó]n\s+negativa\b|\btimestomping\b|\bfecha\s+(?:imposible|futura\s+fabricada)', re.I),
     Fraction(8, 10), Fraction(30, 10)),
    ("temporal", "TIMESTAMP_IMPOSSIBLE",
     re.compile(r'\bcreaci[oó]n\s+posterior\s+al\s+(?:[uú]ltimo\s+)?acceso\b|\bacceso\s+antes\s+de\s+creaci[oó]n\b', re.I),
     Fraction(9, 10), Fraction(34, 10)),
 
    # REGISTRY
    ("registry", "IFEO_HIJACK",
     re.compile(r'\bifeo\b|\bimage\s*file\s*execution\s*options\b|\bsticky\s*keys\s*hijack\b', re.I),
     Fraction(10, 10), Fraction(44, 10)),
    ("registry", "EVIL_EXE",
     re.compile(r'\b(?:evil|malware|payload|trojan)\.exe\b', re.I),
     Fraction(9, 10), Fraction(36, 10)),
    ("registry", "PERSISTENCE_ABUSE",
     re.compile(r'\brun(?:once)?\s+key\b.{0,40}(?:evil|malware|unknown|suspicious)', re.I),
     Fraction(8, 10), Fraction(28, 10)),
 
    # FORENSIC EXPLICIT
    ("forensic", "EXPLICIT_MALICE",
     re.compile(r'\bindicativo\s+de\s+(?:alias\s+de\s+)?atacante\b|\bherramienta\s+de\s+hacking\b|\bataque\s+(?:confirmado|detectado)\b', re.I),
     Fraction(9, 10), Fraction(36, 10)),
    ("forensic", "INTERCEPT_EVIDENCE",
     re.compile(r'\btráfico\s+interceptado\b|\bescucha\s+ilegal\b|\bintercepci[oó]n\s+de\s+comunicaciones\b', re.I),
     Fraction(9, 10), Fraction(34, 10)),
    ("forensic", "HOTSPOT_ATTACK",
     re.compile(r'\bhotspot\b.{0,40}(?:intercept|attack|hack|evil|victim)', re.I),
     Fraction(8, 10), Fraction(28, 10)),
]
 
# ── Constantes de scoring ────────────────────────────────────────────────
BASE_Z      = Fraction(4, 10)
MAX_Z       = Fraction(45, 10)
SYNERGY_STEP = Fraction(1, 4)
MAX_SYNERGY  = Fraction(2, 1)
 
# ── Tipo de artefacto → tool_name ────────────────────────────────────────
TYPE_TOOL = {
    "registry":       "ROI",
    "network_flow":   "GCI",
    "bash_history":   "CLI",
    "file_system":    "ACP",
    "process":        "SDA",
    "memory":         "SDA",
    "log":            "CLI",
    "auth_log":       "CLI",
    "email":          "DGPI",
    "browser":        "GCI",
    "usb":            "ACP",
    "prefetch":       "ACP",
    "lnk":            "ACP",
    "scheduled_task": "ROI",
    "service":        "ROI",
    "user_account":   "SDA",
    "crypto":         "DGPI",
    "timeline":       "GCI",
    "file_metadata":  "ACP",
}
 
 
def _sanitize(text: str) -> str:
    """Normaliza unicode y casefold — determinista."""
    text = unicodedata.normalize("NFC", str(text))
    text = re.sub(
        r"[\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFEFF\u00AD]", "", text
    )
    return text.casefold()
 
 
class ForensicTechnicalDetector:
    """
    Detector determinístico de indicadores forenses técnicos (TTPs).
    Complementa SemioticDetectorV2 — detecta evidencia técnica explícita.
    """
 
    def __init__(self) -> None:
        self._catalog = IFT_CATALOG
        # Precalcular max weight por categoría para normalización
        self._category_max_weights: Dict[str, Fraction] = {}
        for cat, _, _, weight, _ in self._catalog:
            if cat not in self._category_max_weights or weight > self._category_max_weights[cat]:
                self._category_max_weights[cat] = weight
        self._max_possible = sum(self._category_max_weights.values())
 
    def analyze(self, artifact: dict) -> dict:
        """
        Analiza un artefacto forense y retorna z_score técnico.
 
        Returns dict con:
            z_score: float (display only — I7)
            confidence: float (display only — I7)
            matched_categories: list[str]
            matched_indicators: list[str]
            _z_num, _z_den: numerador/denominador Fraction
            _conf_num, _conf_den: numerador/denominador Fraction
            tool_prefix: str
        """
        content   = _sanitize(artifact.get("content", ""))
        anomalies = artifact.get("forensic_anomalies", [])
        anom_text = _sanitize(" | ".join(str(a) for a in anomalies))
        full_text = content + " | " + anom_text
 
        art_type  = artifact.get("type", "unknown")
        tool_prefix = TYPE_TOOL.get(art_type, art_type.upper()[:6])
 
        # Detectar indicadores — máximo weight por categoría
        cat_max: Dict[str, Fraction] = {}
        matched_indicators: List[str] = []
 
        for cat, ind_id, pattern, weight, _ in self._catalog:
            if pattern.search(full_text):
                matched_indicators.append(ind_id)
                if cat not in cat_max or weight > cat_max[cat]:
                    cat_max[cat] = weight
 
        # Sin matches → benigno
        if not cat_max:
            z_f    = BASE_Z
            conf_f = Fraction(1, 2)
            return {
                "_z_num": z_f.numerator, "_z_den": z_f.denominator,
                "_conf_num": conf_f.numerator, "_conf_den": conf_f.denominator,
                "z_score": float(z_f),
                "confidence": float(conf_f),
                "matched_categories": [],
                "matched_indicators": [],
                "tool_prefix": tool_prefix,
            }
 
        total_weight  = sum(cat_max.values())
        unique_cats   = len(cat_max)
 
        # Sinergia entre categorías
        synergy = Fraction(1, 1) + (unique_cats - 1) * SYNERGY_STEP
        if synergy > MAX_SYNERGY:
            synergy = MAX_SYNERGY
 
        # Normalizar
        ratio = (total_weight * synergy) / self._max_possible
        if ratio > Fraction(1, 1):
            ratio = Fraction(1, 1)
 
        # z_score final
        z_f = BASE_Z + ratio * (MAX_Z - BASE_Z)
 
        # Confidence
        conf_f = Fraction(1, 2) + Fraction(unique_cats, 10) + ratio * Fraction(2, 10)
        if conf_f > Fraction(19, 20):
            conf_f = Fraction(19, 20)
 
        return {
            "_z_num": z_f.numerator, "_z_den": z_f.denominator,
            "_conf_num": conf_f.numerator, "_conf_den": conf_f.denominator,
            "z_score": float(z_f),
            "confidence": float(conf_f),
            "matched_categories": sorted(cat_max.keys()),
            "matched_indicators": matched_indicators,
            "tool_prefix": tool_prefix,
        }
