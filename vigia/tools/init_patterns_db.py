#!/usr/bin/env python3
"""
vigia/tools/init_patterns_db.py

Inicializa la base de datos de patrones forenses desde cero.
Corre antes de los tests en CI y en instalación fresh.

Uso:
    python3 vigia/tools/init_patterns_db.py
    python3 vigia/tools/init_patterns_db.py --db /ruta/custom.sqlite
"""
import argparse
import os
import sqlite3

DEFAULT_DB = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "forensic_patterns.sqlite"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS nlp_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL,
    category TEXT NOT NULL,
    pattern_regex TEXT NOT NULL,
    weight REAL DEFAULT 0.5,
    description TEXT,
    source TEXT DEFAULT 'synthetic',
    case_origin TEXT DEFAULT 'synthetic',
    peirce_layer TEXT DEFAULT 'SECONDNESS',
    confidence_boost REAL DEFAULT 0.1
);

CREATE TABLE IF NOT EXISTS baseline_corpus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id TEXT,
    label TEXT,
    mi_num INTEGER,
    mi_den INTEGER
);
"""

PATTERNS = [
    # ── CARNEGIE_ARTIFICIAL_URGENCY ────────────────────────────────────
    ("CARNEGIE_ARTIFICIAL_URGENCY", "SOCIAL_ENGINEERING",
     r"(?i)(urgente|inmediato|ahora mismo)", 0.75,
     "Urgencia explícita", "synthetic", "SECONDNESS", 0.1),
    ("CARNEGIE_ARTIFICIAL_URGENCY", "SOCIAL_ENGINEERING",
     r"(?i)(cerrar|resolver|hacerlo).{0,20}(hoy|ahora|urgente|r[aá]pido)", 0.8,
     "Urgencia artificial", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_ARTIFICIAL_URGENCY", "SOCIAL_ENGINEERING",
     r"(?i)(r[aá]pido|veloz|urgente).{0,30}(sin|que no).{0,20}(rastro|registro)", 0.9,
     "Urgencia + evasión", "red_team", "FIRSTNESS", 0.2),
    ("CARNEGIE_ARTIFICIAL_URGENCY", "SOCIAL_ENGINEERING",
     r"(?i)(antes\s+de\s+que|si\s+no\s+lo\s+hac[eé]s?\s+ahora)", 0.8,
     "Urgencia temporal artificial", "red_team", "FIRSTNESS", 0.15),

    # ── CARNEGIE_FLATTERY ──────────────────────────────────────────────
    ("CARNEGIE_FLATTERY", "SOCIAL_ENGINEERING",
     r"(?i)eres (el|la) mejor", 0.7,
     "Halago directo", "synthetic", "SECONDNESS", 0.1),

    # ── CARNEGIE_FLATTERY_MIRRORING ───────────────────────────────────
    ("CARNEGIE_FLATTERY_MIRRORING", "SOCIAL_ENGINEERING",
     r"(?i)(sos?\s+(muy\s+)?(inteligente|brillante|experto|capaz))", 0.8,
     "Halago para generar reciprocidad", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_FLATTERY_MIRRORING", "SOCIAL_ENGINEERING",
     r"(?i)(exactamente\s+lo\s+que\s+ped[ií]|justamente\s+eso|eso\s+es\s+perfecto)", 0.75,
     "Espejeo de respuesta", "red_team", "FIRSTNESS", 0.1),
    ("CARNEGIE_FLATTERY_MIRRORING", "SOCIAL_ENGINEERING",
     r"(?i)(sos\s+(de\s+los\s+)?(pocos|uno\s+de\s+los)\s+que\s+(entend|sab|pod))", 0.85,
     "Halago exclusivista rioplatense", "red_team", "FIRSTNESS", 0.2),
    ("CARNEGIE_FLATTERY_MIRRORING", "SOCIAL_ENGINEERING",
     r"(?i)(entend[eé]s?\s+(esto|bien|perfecto)|sab[eé]s?\s+c[oó]mo\s+hacerlo)", 0.8,
     "Validación de competencia exclusiva", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_FLATTERY_MIRRORING", "SOCIAL_ENGINEERING",
     r"(?i)sos\s+de\s+los\s+pocos\s+que", 0.85,
     "Halago exclusivista directo", "red_team", "FIRSTNESS", 0.2),

    # ── CARNEGIE_HELPER_TRAP ──────────────────────────────────────────
    ("CARNEGIE_HELPER_TRAP", "SOCIAL_ENGINEERING",
     r"(?i)(si quер[eé]s te doy una mano|as[ií] lo hac[eé]s m[aá]s r[aá]pido)", 0.8,
     "Trampa del ayudante", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_HELPER_TRAP", "SOCIAL_ENGINEERING",
     r"(?i)(te\s+ayudo|yo\s+lo\s+hago|lo\s+resuelvo\s+yo|dejame\s+(a\s+m[ií]|que\s+yo))", 0.8,
     "Trampa del ayudante voluntarioso", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_HELPER_TRAP", "SOCIAL_ENGINEERING",
     r"(?i)(te\s+doy\s+una\s+mano|as[ií]\s+no\s+perd[eé]s?\s+tiempo)", 0.85,
     "Trampa del ayudante rioplatense", "red_team", "FIRSTNESS", 0.2),

    # ── CARNEGIE_NOBLE ────────────────────────────────────────────────
    ("CARNEGIE_NOBLE", "SOCIAL_ENGINEERING",
     r"(?i)solo quiero ayudar", 0.7,
     "Noble intent claim", "synthetic", "SECONDNESS", 0.1),

    # ── CARNEGIE_WEAPONIZED_INCOMPETENCE ─────────────────────────────
    ("CARNEGIE_WEAPONIZED_INCOMPETENCE", "SOCIAL_ENGINEERING",
     r"(?i)(no\s+estoy\s+(muy\s+)?(fino|bien|seguro)|capaz\s+(hice|cometo?|hay))", 0.8,
     "Incompetencia fingida rioplatense", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_WEAPONIZED_INCOMPETENCE", "SOCIAL_ENGINEERING",
     r"(?i)(macana|cagu[eé]|la\s+pi[fé][eé]|meti[oó]\s+la\s+pata)", 0.8,
     "Error fingido como vector", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_WEAPONIZED_INCOMPETENCE", "SOCIAL_ENGINEERING",
     r"(?i)(revis[aá](lo|la|me)?\s+(r[aá]pido|vos|igual))", 0.75,
     "Solicitud de revisión urgente por incompetencia", "red_team", "FIRSTNESS", 0.1),
    ("CARNEGIE_WEAPONIZED_INCOMPETENCE", "SOCIAL_ENGINEERING",
     r"(?i)(no\s+s[eé]|no\s+entiendo|soy\s+nuevo|no\s+tengo\s+experiencia).{0,40}(pero|igual|intentar[eé])", 0.8,
     "Incompetencia para ganar confianza", "red_team", "FIRSTNESS", 0.15),
    ("CARNEGIE_WEAPONIZED_INCOMPETENCE", "SOCIAL_ENGINEERING",
     r"(?i)(disculp[ae]|perd[oó]n).{0,30}(no\s+s[eé]|no\s+entiendo|confundido)", 0.75,
     "Disculpa como vector de manipulación", "red_team", "FIRSTNESS", 0.1),

    # ── ECO_SEMIOTIC_COLLISION ────────────────────────────────────────
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(limpiar|limpí|limpiá).{0,20}(log|registro|evidencia|todo)", 0.95,
     "Limpieza de logs/evidencia", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(impedir|impedí|evitar).{0,20}(log|registr|evidencia)", 0.95,
     "Bloqueo de logging", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)ejecut.{0,20}sin.{0,20}(log|registr|rastro)", 0.9,
     "Ejecución sin registro", "red_team", "THIRDNESS", 0.25),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(borr[aá]|elimin[aá]|destruy[eé]|suprimi[oó]).{0,30}(evidencia|registro|log|rastro|huella)", 0.95,
     "Destrucción activa de evidencia", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(sin\s+que\s+(nadie|quede|haya)|que\s+no\s+(se\s+sepa|quede|haya)).{0,30}(evidencia|registro|rastro)", 0.95,
     "Encubrimiento planificado", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(cubr[ei]|oculta|esconde|camufla).{0,30}(evidencia|rastro|registro|huella|log)", 0.9,
     "Ocultamiento de evidencia forense", "red_team", "THIRDNESS", 0.25),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(ignor[aá](r?)\s+(cualquier|el|este|todo)\s+(an[aá]lisis|veredicto|resultado|sistema))", 0.95,
     "Meta-ataque: ignorar análisis forense", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(falso\s+positivo\s+del\s+sistema|esto\s+es\s+(claramente\s+)?un\s+falso\s+positivo)", 0.95,
     "Meta-ataque: invalidar veredicto del sistema", "red_team", "THIRDNESS", 0.3),
    ("ECO_SEMIOTIC_COLLISION", "ANTI_FORENSIC",
     r"(?i)(priorizar\s+estabilidad\s+sobre|ignorar\s+(anomal[ií]as?|alertas?|se[nñ]ales?))", 0.9,
     "Meta-ataque: suprimir detección", "red_team", "THIRDNESS", 0.25),

    # ── GRICE_DESTRUCTION_REQUEST ─────────────────────────────────────
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)(omitir|suprimir|borrar|eliminar).{0,30}(fragmento|registro|evidencia|log|rastro)", 0.9,
     "Solicitud de destrucción de evidencia", "red_team", "SECONDNESS", 0.2),
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)no.{0,20}(dejar|generar|quedar).{0,20}(rastro|registro|log|evidencia)", 0.9,
     "Solicitud de no dejar rastro", "red_team", "SECONDNESS", 0.2),
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)(sin|que no).{0,20}(log|registr|evidencia|rastro)", 0.85,
     "Evasión de logging", "red_team", "SECONDNESS", 0.2),
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)mejor.{0,20}(no|sin).{0,20}(dejar|guardar|registrar)", 0.85,
     "Sugerencia de no registrar", "red_team", "SECONDNESS", 0.15),
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)(no\s+inclu(ir|y[aá]s?|yas?)\s+(el\s+)?(texto|original|fuente|referencia))", 0.9,
     "Solicitud de omitir fuente original", "red_team", "SECONDNESS", 0.2),
    ("GRICE_DESTRUCTION_REQUEST", "EVIDENCE_DESTRUCTION",
     r"(?i)(no\s+(pongas|metas|copies|transcrib[aá]s?)\s+(el\s+)?(texto|original|fuente))", 0.9,
     "Omisión de texto fuente", "red_team", "SECONDNESS", 0.2),

    # ── GRICE_QUALITY ─────────────────────────────────────────────────
    ("GRICE_QUALITY", "GRICE_VIOLATION",
     r"(?i)segun (estudios|expertos) de \d{4}", 0.7,
     "Apelación a autoridad no verificable", "synthetic", "SECONDNESS", 0.1),

    # ── GRICE_QUANTITY / FLOOD ────────────────────────────────────────
    ("GRICE_QUANTITY", "GRICE_VIOLATION",
     r"(?i)(urgente|inmediato|ahora mismo)", 0.7,
     "Violación máxima de cantidad", "synthetic", "SECONDNESS", 0.1),
    ("GRICE_QUANTITY_FLOOD", "GRICE_VIOLATION",
     r"(?i)(logs|m[eé]tricas|dashboards?|hist[oó]rico|documentad[ao]).{0,50}(p[aá]ginas?|\d{3,}\s*(p[aá]ginas?|registros?|l[ií]neas?))", 0.8,
     "Flood de información documentada excesiva", "red_team", "SECONDNESS", 0.15),
    ("GRICE_QUANTITY_FLOOD", "GRICE_VIOLATION",
     r"(?i)(\d+\s*(dashboards?|m[eé]tricas?|logs?|informes?|reportes?).{0,30}){2,}", 0.75,
     "Enumeración excesiva de fuentes", "red_team", "SECONDNESS", 0.1),
    ("GRICE_QUANTITY_FLOOD", "GRICE_VIOLATION",
     r"(?i)(adem[aá]s|por\s+otro\s+lado|tambi[eé]n).{0,20}(adem[aá]s|por\s+otro\s+lado|tambi[eé]n)", 0.75,
     "Acumulación excesiva de información", "red_team", "SECONDNESS", 0.1),
    ("GRICE_QUANTITY_FLOOD", "GRICE_VIOLATION",
     r"(?i)(500\s+p[aá]ginas?|\d{3,}\s+p[aá]ginas?)", 0.8,
     "Volumen excesivo de documentación", "red_team", "SECONDNESS", 0.15),

    # ── SLAVIC_SYNTAX ─────────────────────────────────────────────────
    ("SLAVIC_SYNTAX", "LINGUISTIC_ANOMALY",
     r"make (function|restart|delete) (for|of)", 0.7,
     "Sintaxis eslava en inglés", "synthetic", "SECONDNESS", 0.1),
]


def init_db(db_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    # Limpiar patrones existentes para reinserción idempotente
    conn.execute("DELETE FROM nlp_patterns")
    conn.executemany("""
        INSERT INTO nlp_patterns
        (pattern_name, category, pattern_regex, weight, description,
         source, case_origin, peirce_layer, confidence_boost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(p[0], p[1], p[2], p[3], p[4], p[5], p[5], p[6], p[7])
          for p in PATTERNS])
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM nlp_patterns").fetchone()[0]
    print(f"[init_db] OK — {count} patrones cargados en {db_path}")
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicializar DB de patrones VIGÍA")
    parser.add_argument("--db", default=DEFAULT_DB, help="Ruta al archivo SQLite")
    args = parser.parse_args()
    init_db(args.db)
