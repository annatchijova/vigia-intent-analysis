#!/usr/bin/env python3
"""
vigia/core/forensic_technical_detector.py  v2.3.5

Cambios v2.3.5:
  M4-hibrid: effective_max = max(unique_cats, n_categories//2)
    Evita doble penalizacion de evidencia concentrada (Kimi).
    1 cat fuerte → z~1.3, 3 cats → REJECT. Balance correcto.
  DoS-input: anomalias limitadas ANTES del join/regex (Kimi).
  SHADOW_COPY: keywords espanoles agregados (Kimi — consistencia interna).

Historial anterior:
  v2.3.4: C1 /etc/shadow, C2 C2_SERVER, C7 chmod, A7 wireless,
          M1 word boundaries, M2 sin re.I, M9 privilege_abuse,
          M14 hotspot sin pipe, A13 evil.exe whitespace, BUG1 command&control
"""
from __future__ import annotations

import re
import unicodedata
from fractions import Fraction
from typing import Dict, List, Tuple

# Limite de anomalias procesadas — DoS protection en INPUT (no solo output)
INPUT_ANOMALIES_LIMIT = 200

# ── Tabla de homoglifos Unicode → ASCII ──────────────────────────────
# Cubre confusables cirílicos y griegos que afectan términos del catálogo.
# Fuente: Unicode Technical Report #39 (Confusable Characters).
# Propósito: impedir evasión por sustitución de caracteres visualmente
# idénticos (ej: 'е' cirílica U+0435 en lugar de 'e' latina U+0065).
# NFC/NFKC NO resuelve esto — son caracteres distintos en cualquier forma.
_HOMOGLYPH_TABLE: Dict[str, str] = {
    # Cirílico → Latino
    "\u0430": "a",  # а CYRILLIC SMALL LETTER A
    "\u0435": "e",  # е CYRILLIC SMALL LETTER IE
    "\u043E": "o",  # о CYRILLIC SMALL LETTER O
    "\u0440": "p",  # р CYRILLIC SMALL LETTER ER
    "\u0441": "c",  # с CYRILLIC SMALL LETTER ES
    "\u0445": "x",  # х CYRILLIC SMALL LETTER HA
    "\u0443": "y",  # у CYRILLIC SMALL LETTER U
    "\u0456": "i",  # і CYRILLIC SMALL LETTER BYELORUSSIAN-UKRAINIAN I
    "\u0455": "s",  # ѕ CYRILLIC SMALL LETTER DZE
    "\u0458": "j",  # ј CYRILLIC SMALL LETTER JE
    # Griego → Latino
    "\u03B1": "a",  # α GREEK SMALL LETTER ALPHA
    "\u03BF": "o",  # ο GREEK SMALL LETTER OMICRON
    "\u03C1": "p",  # ρ GREEK SMALL LETTER RHO
    "\u03BD": "v",  # ν GREEK SMALL LETTER NU
    # Fullwidth ASCII (U+FF01–U+FF5E) → ASCII equivalente
    **{chr(0xFF01 + i): chr(0x21 + i) for i in range(94)},
}

_HOMOGLYPH_TRANS = str.maketrans(_HOMOGLYPH_TABLE)

IFT_CATALOG: List[Tuple[str, str, re.Pattern, Fraction]] = [
    # IDENTITY
    ("identity", "EVIL_ALIAS",
     re.compile(r'\b(?:mr\.?\s*)?evil\b'),
     Fraction(9, 10)),
    ("identity", "SUSPICIOUS_NICK",
     re.compile(r'\b(?:mrevil|evilrulez|l33t|elite\.hacker|darkside|shadowhack)\w*\b'),
     Fraction(8, 10)),
    ("identity", "ATTACKER_ALIAS",
     re.compile(r'\balias\s+(?:de\s+)?atacante\b|\bnick(?:name)?\s+malicioso\b'),
     Fraction(8, 10)),

    # NETWORK
    ("network", "PCAP_INTERCEPT",
     re.compile(r'\bpcap\b[^\n|.;]{0,80}\b(?:terceros|interceptado|ajenos|externos|no\s*autorizados)\b'),
     Fraction(9, 10)),
    ("network", "WAR_DRIVING",
     re.compile(r'\bwar\s*driving\b|\bwardriving\b'),
     Fraction(7, 10)),
    ("network", "SNIFFER",
     re.compile(r'\b(?:sniffer|modo\s+promiscuo|promiscuous\s*mode|packet\s*capture\s+ilegal)\b'),
     Fraction(8, 10)),
    ("network", "C2_SERVER",
     re.compile(
         r'\bc2\s*server\b'
         r'|\bcommand\s*(?:and|&)\s*control\b'
         r'|\bmalicious\.com\b|\battacker\.com\b|\bevil\.com\b'
     ),
     Fraction(9, 10)),
    ("network", "CREDENTIAL_THEFT",
     re.compile(r'\bcontrase\xf1as?\s+robadas?\b|\bcredenciales?\s+(?:robadas?|exfiltradas?)\b|\bpassword\s+theft\b'),
     Fraction(9, 10)),

    # COMMUNITY / IRC
    ("community", "HACKER_CHANNEL",
     re.compile(r'#(?:elite\.?hackers?|warez|crack(?:ing)?|darknet|undernet\.?hack|evilfork)\b'),
     Fraction(10, 10)),
    ("community", "HACKER_NICK",
     re.compile(r'\bnick\s*:\s*(?:mr\.?\s*evil|mrevilrulez|mini\s*me)\b'),
     Fraction(9, 10)),
    ("community", "IRC_HACKING",
     re.compile(r'\birc\b.{0,40}#(?:elite|hacker|warez|dark|evilfork)\b'),
     Fraction(8, 10)),

    # TOOLS
    ("tools", "HACKING_TOOL",
     re.compile(r'\b(?:keylogger|mimikatz|metasploit|cobalt\s*strike|meterpreter|rootkit|netbus|sub7|darkcomet)\b'),
     Fraction(10, 10)),
    ("tools", "WIRELESS_ATTACK",
     re.compile(r'\b(?:aircrack|kismet|netstumbler)\b|\b(?:wireshark|ethereal)\b.{0,30}\bintercept\b'),
     Fraction(8, 10)),
    ("tools", "OBFUSCATION",
     re.compile(r'\bbase64\s*[|>]\s*(?:bash|sh)\b|\bpowershell\s+-enc\b|\bcertutil\s+-decode\b'),
     Fraction(9, 10)),

    # COMMANDS
    ("commands", "DESTRUCTIVE",
     re.compile(r'\brm\s+-rf\s+/\b|\bhistory\s+-c\b|\bshred\s+-u\b|\bhistcontrol\b'),
     Fraction(10, 10)),
    ("commands", "EXFIL",
     re.compile(r'\bexfil(?:trac)?\b|\bnc\s+-e\s+|\bmysqldump.{0,30}(?:attacker|evil|malicious)\b'),
     Fraction(9, 10)),
    # C1: lookbehind negativo — \b no funciona antes de /
    # A14: keywords espanoles agregados (consistencia interna del catalogo)
    ("commands", "SHADOW_COPY",
     re.compile(r'(?<!\w)/etc/shadow.{0,40}(?:rob(?:ad)?|copi(?:ad)?|copy|send|enviad?|mail|exfil|attacker|atacante)'),
     Fraction(10, 10)),
    # C7: chmod 777 seguido de cualquier path (no solo / con espacio/EOL)
    # P1-002 (Kimi 2026-05-02): /(?:\s|$) solo detectaba "chmod 777 / " — falso
    # negativo para chmod 777 /etc/shadow, chmod 777 /tmp/evil, etc.
    # Fix: /[^\s]* permite path arbitrario tras el slash.
    ("commands", "PRIVILEGE_ABUSE",
     re.compile(r'\bchmod\s+777\s+/[^\s]*|\bchown\s+root\b.{0,20}\b(?:backdoor|malware)\b'),
     Fraction(8, 10)),

    # TEMPORAL ANOMALIES
    ("temporal", "TIME_ANOMALY",
     re.compile(r'\batime\s*[<>]\s*mtime\b|\bduraci[o\u00f3]n\s+negativa\b|\btimestomping\b|\bfecha\s+(?:imposible|futura\s+fabricada)'),
     Fraction(8, 10)),
    ("temporal", "TIMESTAMP_IMPOSSIBLE",
     re.compile(r'\bcreaci[o\u00f3]n\s+posterior\s+al\s+(?:[u\u00fa]ltimo\s+)?acceso\b|\bacceso\s+antes\s+de\s+creaci[o\u00f3]n\b'),
     Fraction(9, 10)),

    # REGISTRY
    ("registry", "IFEO_HIJACK",
     re.compile(r'\bifeo\b|\bimage\s*file\s*execution\s*options\b|\bsticky\s*keys\s*hijack\b'),
     Fraction(10, 10)),
    # A13: \s* resiste whitespace invisible entre nombre y extension
    ("registry", "EVIL_EXE",
     re.compile(r'\b(?:evil|malware|payload|trojan)\s*\.exe\b'),
     Fraction(9, 10)),
    ("registry", "PERSISTENCE_ABUSE",
     re.compile(r'\brun(?:once)?\s+key\b.{0,40}(?:evil|malware|unknown|suspicious)'),
     Fraction(8, 10)),

    # EXFILTRATION SPANISH
    ("exfil_es", "EXFIL_SPANISH",
     re.compile(r'\bexfiltrar\b|\bexfiltr(?:ando|ados?)\b|\bdatos?\s+exfiltrados?\b'),
     Fraction(9, 10)),
    ("exfil_es", "PERSONAL_CLOUD_EXFIL",
     re.compile(r'\b(?:gmail|yahoo|hotmail|dropbox)\b.{0,50}(?:exfil|subid|compartid|copi)'),
     Fraction(9, 10)),
    ("exfil_es", "PERSONAL_CLOUD_EXFIL2",
     re.compile(r'\bcuenta\s+personal\b.{0,40}(?:gmail|yahoo|hotmail|dropbox)'),
     Fraction(8, 10)),

    # ANTIFORENSIC
    ("antiforensic", "ANTIFORENSIC_TOOL",
     re.compile(r'\b(?:ccleaner|eraser|bleachbit|shredder)\b'),
     Fraction(9, 10)),
    ("antiforensic", "ANTIFORENSIC_ACTION",
     re.compile(r'\banti.?forens\b|\bborrar\s+(?:logs?|registros?|huellas?)|\beliminar\s+(?:logs?|registros?|evidencia)'),
     Fraction(9, 10)),

    # CONCEALMENT
    ("concealment", "FILE_CONCEALMENT",
     re.compile(r'\bcambio\s+deliberado\s+de\s+extensi[oó]n|\bocultar\b.{0,30}(?:contenido|extensi[oó]n)'),
     Fraction(8, 10)),

    # ATTACK TOOLS / EXPLOITS (REAL-003, 008, 009)
    ("attack_tools", "EXPLOIT_TOOL",
     re.compile(r'\b(?:sqlmap|metasploit|meterpreter|mimikatz|malfind|psxview|psscan)\b'),
     Fraction(10, 10)),
    ("attack_tools", "WEBSHELL",
     re.compile(r'\b(?:webshell|c99\s*shell|c99\.php|webshells?\.zip|php\s*shell)\b'),
     Fraction(10, 10)),
    ("attack_tools", "PROCESS_HOLLOW",
     re.compile(r'\bprocess\s*hollow|\bpsxview\b|\bmalfind\b|\binjec(?:t|ci[oó]n)\s+(?:de\s+)?c[oó]digo'),
     Fraction(10, 10)),

    # MALWARE INDICATORS (REAL-003, 004, 008)
    ("malware", "MALWARE_MASQUERADE",
     re.compile(r'\b(?:masquerad|imita\s+(?:a\s+)?(?:sysinternal|vmware|adobe|microsoft)|nombre\s+(?:de\s+)?proceso\s+leg[ií]timo)'),
     Fraction(9, 10)),
    ("malware", "C2_CALLBACK",
     re.compile(r'\b(?:malware\d+\.com|callback|beacon|mutex\b.{0,20}encrypt|hardcoded?\s+(?:ip|server|servidor))\b'),
     Fraction(9, 10)),
    ("malware", "DOWNLOADER",
     re.compile(r'\b(?:urldownloadtofile|downloader|descarg[ao]\s+(?:exploit|malware|payload))\b'),
     Fraction(9, 10)),

    # EMAIL SPOOFING / PHISHING (REAL-006, 007, 010)
    ("email_attack", "EMAIL_SPOOFING",
     re.compile(r'\b(?:spoofing|spoofeado|return.path\b.{0,40}no\s+coincide|reply.to\s+cambi[oó])\b'),
     Fraction(9, 10)),
    ("email_attack", "ANON_EMAIL",
     re.compile(r'\b(?:willselfdestruct|guerrillamail|tempmail|autodestrucci[oó]n|email\s+an[oó]nimo)\b'),
     Fraction(8, 10)),
    ("email_attack", "DESTROY_EVIDENCE",
     re.compile(r'\bno\s+incluyas?\s+el\s+texto|\bdestruir\s+evidencia|\beliminar\s+(?:email|correo|mensaje)\b'),
     Fraction(9, 10)),

    # DATA THEFT / ESPIONAGE (REAL-009, 010)
    ("data_theft", "LATERAL_MOVEMENT",
     re.compile(r'\b(?:admin.?share|share\s+administrativo|movimiento\s+lateral|copia\s+masiva\s+de\s+archivos)\b'),
     Fraction(9, 10)),
    ("data_theft", "ESPIONAGE",
     re.compile(r'\b(?:espionaje\s+industrial|propiedad\s+intelectual|negociaci[oó]n.{0,20}venta|documentos?\s+confidenciales?.{0,30}(?:competidor|externo))\b'),
     Fraction(9, 10)),
    ("data_theft", "COVERING_TRACKS",
     re.compile(r'\b(?:covering\s+tracks|elimina(?:ci[oó]n|r)\s+(?:del?\s+)?script|borrar\s+huellas|prefetch\s+eliminad)\b'),
     Fraction(8, 10)),

    # CRYPTO / ENCRYPTION ABUSE (REAL-005)
    ("crypto_abuse", "ENCRYPTION_CONCEALMENT",
     re.compile(r'\b(?:aes|gpg|bitlocker)\b.{0,40}(?:ocultar|esconder|confidencial|comunicaci[oó]n\s+secreta)\b'),
     Fraction(8, 10)),

    # BRIDGE
    # TODO: migrar a SemioticDetectorV2 en v3.0
    ("bridge", "EXPLICIT_MALICE",
     re.compile(r'\bindicativo\s+de\s+(?:alias\s+de\s+)?atacante\b|\bherramienta\s+de\s+hacking\b'),
     Fraction(9, 10)),
    ("bridge", "INTERCEPT_EVIDENCE",
     re.compile(r'\btr\u00e1fico\s+interceptado\b|\bescucha\s+ilegal\b|\bintercepci[o\u00f3]n\s+de\s+comunicaciones\b'),
     Fraction(9, 10)),
    # M14: [^\n|] excluye separador de campos
    ("bridge", "HOTSPOT_ATTACK",
     re.compile(r'\bhotspot\b[^\n|]{0,40}\b(?:intercept|attack|hack|evil|victim)\b'),
     Fraction(8, 10)),
]

BASE_Z       = Fraction(4, 10)
MAX_Z        = Fraction(45, 10)
SYNERGY_STEP = Fraction(1, 4)
MAX_SYNERGY  = Fraction(2, 1)

_CONF_MAP: Dict[int, Fraction] = {
    0: Fraction(7, 10),
    1: Fraction(8, 10),
    2: Fraction(9, 10),
}
_CONF_DEFAULT = Fraction(19, 20)

TYPE_TOOL = {
    "registry": "ROI", "network_flow": "GCI", "bash_history": "CLI",
    "file_system": "ACP", "process": "SDA", "memory": "SDA",
    "log": "CLI", "auth_log": "CLI", "email": "DGPI", "browser": "GCI",
    "usb": "ACP", "prefetch": "ACP", "lnk": "ACP",
    "scheduled_task": "ROI", "service": "ROI", "user_account": "SDA",
    "crypto": "DGPI", "timeline": "GCI", "file_metadata": "ACP",
    "artifact": "ACP",
}


def _sanitize(text: str) -> str:
    """
    Normaliza texto para detección robusta.

    Pipeline:
      1. Rechazo de no-string (R2)
      2. NFC — formas compuestas canónicas
      3. Strip de caracteres de control invisible (zero-width, BiDi, soft-hyphen)
      4. Normalización de homoglifos Unicode → ASCII (_HOMOGLYPH_TABLE)
         Impide evasión por sustitución visual (cirílica/griega/fullwidth).
         NFC/NFKC NO resuelve esto — se requiere tabla explícita.
      5. Colapso de espacios múltiples
      6. casefold

    NOTA FORENSE: Esta función es para detección semántica general.
    Los patrones de ofuscación T1027 (espaciado inusual, encoding) se evalúan
    sobre el texto RAW antes de esta normalización — ver analyze().
    """
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFEFF\u00AD]", "", text)
    text = text.translate(_HOMOGLYPH_TRANS)
    text = re.sub(r'\s+', ' ', text)
    return text.casefold()


# Patrones de ofuscación que requieren texto RAW (pre-sanitize).
# T1027: espaciado inusual destruido por _sanitize — evaluar sobre original.
# Se compilan una sola vez al importar el módulo.
_RAW_OBFUSCATION_PATTERNS: List[re.Pattern] = [
    re.compile(r'p[\s_\-\.]{1,3}o[\s_\-\.]{1,3}w[\s_\-\.]{1,3}e[\s_\-\.]{1,3}r[\s_\-\.]{1,3}s[\s_\-\.]{1,3}h[\s_\-\.]{1,3}e[\s_\-\.]{1,3}l[\s_\-\.]{1,3}l', re.IGNORECASE),  # powershell espaciado
    re.compile(r'c[\s_\-\.]{1,3}m[\s_\-\.]{1,3}d[\s_\-\.]{1,3}\.[\s_\-\.]{0,2}e[\s_\-\.]{1,3}x[\s_\-\.]{1,3}e', re.IGNORECASE),  # cmd.exe espaciado
    re.compile(r'm[\s_\-\.]{1,3}i[\s_\-\.]{1,3}m[\s_\-\.]{1,3}i[\s_\-\.]{1,3}k[\s_\-\.]{1,3}a[\s_\-\.]{1,3}t[\s_\-\.]{1,3}z', re.IGNORECASE),  # mimikatz espaciado
]


class ForensicTechnicalDetector:

    def __init__(self) -> None:
        self._catalog = IFT_CATALOG
        self._n_categories = len(set(cat for cat, _, _, _ in self._catalog))
        # M4-hibrid: effective_max = max(unique_cats, floor)
        # floor=2: 1 categoria fuerte (ej: Mimikatz peso 1.0) → z=2.45 → ABSTAIN
        #   Fuerza revision humana sin condena automatica por fuente unica.
        #   Daubert: "sin convergencia de fuentes independientes no hay condena"
        #   floor=1 llevaría Mimikatz a z=4.5 → REJECT, con FPR alto para
        #   herramientas legítimas de forensics (wireshark, volatility, etc.)
        # 3 categorias convergentes → z=4.5 → REJECT. Balance correcto.
        self._m4_floor = 2
        self._max_weight_categories = set(
            cat for cat, _, _, w in self._catalog if w == Fraction(10, 10)
        )
        self._max_possible_global = Fraction(self._n_categories, 1)

    def analyze(self, artifact: dict) -> dict:
        # B13: content=None → _sanitize(str(None))="none" poluciona full_text
        raw_content = artifact.get("content")
        content = _sanitize(raw_content) if raw_content is not None else ""
        # DoS protection en INPUT — ordenar por severidad ANTES de truncar.
        # P1-001 (Kimi 2026-05-02): truncar crudo permite a un atacante inyectar
        # 200 anomalías leves para sepultar evidencia CRITICAL en posición 201+.
        # Copiado de la lógica A1 del vigia_case_adapter.
        raw_anomalies = artifact.get("forensic_anomalies") or []
        if len(raw_anomalies) > INPUT_ANOMALIES_LIMIT:
            def _det_severity_key(a) -> float:
                if isinstance(a, dict):
                    return -float(a.get("severity", a.get("z_score", a.get("score", 0.0))))
                return 0.0
            raw_anomalies = sorted(raw_anomalies, key=_det_severity_key)[:INPUT_ANOMALIES_LIMIT]
        anom_text = _sanitize(" | ".join(str(a) for a in raw_anomalies))
        full_text = content + " | " + anom_text

        # B1-T1027: preservar texto RAW (pre-sanitize) para patrones de
        # ofuscación que dependen de espaciado inusual. _sanitize colapsa
        # espacios y destruiría la firma antes de que el regex la vea.
        raw_for_obfusc = (raw_content or "") + " | " + " | ".join(str(a) for a in raw_anomalies)
        raw_for_obfusc = raw_for_obfusc.casefold()  # solo casefold, sin colapso de espacios

        art_type    = artifact.get("type") or "unknown"  # R1: None-safe, consistente con adapter
        tool_prefix = TYPE_TOOL.get(art_type, art_type.upper()[:6])

        cat_max: Dict[str, Fraction] = {}
        matched_indicators: List[str] = []

        for cat, ind_id, pattern, weight in self._catalog:
            if pattern.search(full_text):
                matched_indicators.append(ind_id)
                if cat not in cat_max or weight > cat_max[cat]:
                    cat_max[cat] = weight

        # B1-T1027: evaluar patrones de ofuscación sobre texto RAW.
        # full_text tiene espacios colapsados — estas firmas requieren el original.
        for i, raw_pat in enumerate(_RAW_OBFUSCATION_PATTERNS):
            if raw_pat.search(raw_for_obfusc):
                ind_id = f"OBFUSCATION_SPACING_{i}"
                matched_indicators.append(ind_id)
                if "commands" not in cat_max or Fraction(9, 10) > cat_max["commands"]:
                    cat_max["commands"] = Fraction(9, 10)

        if not cat_max:
            return self._build(BASE_Z, Fraction(7, 10), [], [], tool_prefix)

        total_weight = sum(cat_max.values())
        unique_cats  = len(cat_max)

        synergy = Fraction(1, 1) + (unique_cats - 1) * SYNERGY_STEP
        if synergy > MAX_SYNERGY:
            synergy = MAX_SYNERGY

        # M4-hibrid: effective_max = max(unique_cats, floor)
        effective_max = Fraction(max(unique_cats, self._m4_floor), 1)
        ratio = (total_weight * synergy) / effective_max
        if ratio > Fraction(1, 1):
            ratio = Fraction(1, 1)

        z_f    = BASE_Z + ratio * (MAX_Z - BASE_Z)
        conf_f = _CONF_MAP.get(unique_cats, _CONF_DEFAULT)

        return self._build(z_f, conf_f, sorted(cat_max.keys()),
                           sorted(matched_indicators), tool_prefix)

    def _build(self, z: Fraction, conf: Fraction,
               cats: List[str], inds: List[str], tool: str) -> dict:
        return {
            "_z_num": z.numerator, "_z_den": z.denominator,
            "_conf_num": conf.numerator, "_conf_den": conf.denominator,
            "z_score": float(z), "confidence": float(conf),
            "matched_categories": cats,
            "matched_indicators": inds,
            "tool_prefix": tool,
        }
