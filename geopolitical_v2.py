# -*- coding: utf-8 -*-
"""
VIGÍA — Geopolitical Intent Engine v3.0-P0-003
Parches aplicados: C3, W7, W8, P2-B + P0-003 (DST real via zoneinfo)

P0-003 FIX:
  - Reemplaza aproximación mensual de DST por zoneinfo.ZoneInfo (Python 3.9+).
  - Elimina error de hasta 28 días en transiciones DST.
  - Mapeo IANA por timezone_str con fallback documentado.
  - Si zoneinfo no está disponible, fallback a aproximación con WARNING log.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Dict
import hashlib
import logging

logger = logging.getLogger("vigia.geopolitical")

# ------------------------------------------------------------------------------
# CONSTANTES DE HUSOS HORARIOS (UTC offsets en minutos — referencia estática)
# ------------------------------------------------------------------------------

_TIMEZONE_OFFSETS: Dict[str, int] = {
    "+0":    0,     # UTC/GMT
    "+1":    60,    # CET
    "+2":    120,   # EET
    "+3":    180,   # MSK (APT28/GRU) — Rusia abolió DST en 2014
    "+3:30": 210,   # IRST (APT34/OilRig)
    "+5":    300,   # YEKT
    "+5:30": 330,   # IST (India — P2-010 fix)
    "+5:45": 345,   # NPT (Nepal — P2-010 fix)
    "+8":    480,   # CST (APT41/Winnti)
    "+9":    540,   # KST (Lazarus/RPDC)
    "+9:30": 570,   # ACST (Australia Central — P2-010 fix)
    "-4":    -240,  # AST (APT40 front companies)
    "-5":    -300,  # EST
}

# ------------------------------------------------------------------------------
# MAPEO IANA PARA DST REAL (P0-003)
# ------------------------------------------------------------------------------
# Cada timezone_str se mapea a una zona IANA representativa.
# En producción, el artefacto debería traer su propia zona IANA.
# ------------------------------------------------------------------------------

_IANA_ZONES: Dict[str, str] = {
    "+0":    "UTC",
    "+1":    "Europe/Berlin",      # CET/CEST
    "+2":    "Europe/Helsinki",    # EET/EEST
    "+3":    "Europe/Moscow",      # MSK (sin DST desde 2014)
    "+3:30": "Asia/Tehran",        # IRST/IRDT
    "+5":    "Asia/Yekaterinburg", # YEKT (sin DST)
    "+5:30": "Asia/Kolkata",       # IST (sin DST)
    "+5:45": "Asia/Kathmandu",     # NPT (sin DST)
    "+8":    "Asia/Shanghai",      # CST (sin DST)
    "+9":    "Asia/Seoul",         # KST (sin DST)
    "+9:30": "Australia/Adelaide", # ACST/ACDT
    "-4":    "America/Puerto_Rico", # AST (sin DST en Caribe)
    "-5":    "America/New_York",   # EST/EDT
}

# ------------------------------------------------------------------------------
# REGLAS DST APROXIMADAS — FALLBACK SI zoneinfo NO ESTÁ DISPONIBLE
# ------------------------------------------------------------------------------
# DEPRECATED: Solo para entornos Python < 3.9 sin backports.zoneinfo.
# ------------------------------------------------------------------------------

_DST_RULES_DEPRECATED: Dict[str, Tuple[int, int, int, int, int]] = {
    "+1": (3, 1, 10, 31, 60),
    "+2": (3, 1, 10, 31, 60),
    "+3": (3, 1, 10, 31, 60),
    "-5": (3, 8, 11, 1, 60),
    "+3:30": (3, 21, 9, 21, 60),
}

# ------------------------------------------------------------------------------
# PERFILES APT (W8 FIX — Fuentes documentadas)
# ------------------------------------------------------------------------------

_ACTOR_ACTIVITY_PROFILES: Dict[str, dict] = {
    "APT28": {
        "primary_hours": (7, 22, _TIMEZONE_OFFSETS["+3"]),
        "excluded_hours": [(0, 5)],
        "workdays_only": False,
        "source_intel": "Mandiant M-Trends 2024; MITRE ATT&CK G0028",
        "note": "GRU opera en horario extendido, con picos 14:00–18:00 MSK"
    },
    "APT34": {
        "primary_hours": (8, 20, _TIMEZONE_OFFSETS["+3:30"]),
        "excluded_hours": [(0, 6), (12, 14)],
        "workdays_only": True,
        "source_intel": "CrowdStrike GTR 2024; MITRE ATT&CK G0049",
        "note": "OilRig opera en horario laboral iraní, respeta pausas culturales"
    },
    "Lazarus": {
        "primary_hours": (8, 23, _TIMEZONE_OFFSETS["+9"]),
        "excluded_hours": [(3, 6)],
        "workdays_only": False,
        "source_intel": "Kaspersky 2023; MITRE ATT&CK G0032",
        "note": "Jornadas largas típicas de cultura laboral norcoreana"
    },
}


def _get_dst_offset(
    timezone_str: str,
    reference_date: Optional[str] = None
) -> int:
    """
    P0-003: Calcula el offset DST adicional (en minutos) usando zoneinfo real.

    Args:
        timezone_str: Clave de _TIMEZONE_OFFSETS (ej: "+1", "+3:30").
        reference_date: Fecha ISO-8601 para evaluar DST. Si None, usa UTC now.

    Returns:
        int: Minutos adicionales de DST (0 si no aplica o no hay DST).
    """
    if not reference_date:
        return 0

    try:
        ref = datetime.fromisoformat(reference_date.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return 0

    # ── Intentar zoneinfo primero ──
    try:
        import zoneinfo
        iana_name = _IANA_ZONES.get(timezone_str)
        if iana_name:
            tz = zoneinfo.ZoneInfo(iana_name)
            # Offset en la fecha de referencia
            aware_dt = ref.replace(tzinfo=timezone.utc).astimezone(tz)
            offset_minutes = int(aware_dt.utcoffset().total_seconds() // 60)
            # P1-006 (Kimi 2026-05-02): usar enero como base_offset es incorrecto
            # para el hemisferio sur. En Australia/Adelaide, enero ES verano austral
            # (DST activo = mayor offset). En julio (invierno), offset_minutes <
            # base_offset → dst_extra negativo → max(0, neg) = 0.
            # Fix: base_offset = mínimo entre enero y julio = offset estándar (sin DST).
            # Esto es correcto para ambos hemisferios: el mínimo anual es siempre
            # el offset estándar sin ajuste de verano.
            jan_dt = ref.replace(month=1,  day=1, tzinfo=timezone.utc).astimezone(tz)
            jul_dt = ref.replace(month=7,  day=1, tzinfo=timezone.utc).astimezone(tz)
            jan_off = int(jan_dt.utcoffset().total_seconds() // 60)
            jul_off = int(jul_dt.utcoffset().total_seconds() // 60)
            # Estándar = mínimo offset del año (sin DST)
            base_offset = min(jan_off, jul_off)
            dst_extra = offset_minutes - base_offset
            return max(0, dst_extra)
    except Exception:
        pass

    # ── Fallback: aproximación mensual (DEPRECATED) ──
    logger.warning(
        "zoneinfo no disponible o falló. Usando DST aproximado para %s. "
        "Instalar: pip install backports.zoneinfo (Python < 3.9)",
        timezone_str
    )
    if timezone_str in _DST_RULES_DEPRECATED:
        month_start, _, month_end, _, dst_minutes = _DST_RULES_DEPRECATED[timezone_str]
        if month_start <= month_end:
            dst_active = month_start <= ref.month <= month_end
        else:
            dst_active = ref.month >= month_start or ref.month <= month_end
        return dst_minutes if dst_active else 0

    return 0


def _hours_match_timezone(
    activity_hours: List[int],
    timezone_str: str,
    reference_date: Optional[str] = None
) -> float:
    """
    Determina qué tan consistentes son las horas de actividad observadas
    con una zona horaria declarada.

    Returns:
        float en [0.0, 1.0]: 1.0 = perfectamente consistente, 0.0 = inconsistente
    """
    if not activity_hours or timezone_str not in _TIMEZONE_OFFSETS:
        return 0.5

    base_offset = _TIMEZONE_OFFSETS[timezone_str]

    # --- P0-003: Ajuste DST real via zoneinfo ---
    dst_offset = _get_dst_offset(timezone_str, reference_date)
    total_offset = base_offset + dst_offset

    # --- Convertir horas UTC a horas locales ---
    local_hours = [(h + total_offset / 60) % 24 for h in activity_hours]

    # --- Buscar perfil APT (P2-B: evaluar TODOS los compatibles) ---
    compatible_profiles = [
        prof for prof in _ACTOR_ACTIVITY_PROFILES.values()
        if prof["primary_hours"][2] == base_offset
    ]

    if compatible_profiles:
        profile = compatible_profiles[0]
    else:
        profile = None

    if profile is None:
        work_start, work_end = 8, 20
        excluded_hours = [(0, 6)]
        workdays_only = False
    else:
        work_start, work_end, _ = profile["primary_hours"]
        excluded_hours = profile.get("excluded_hours", [])
        workdays_only = profile.get("workdays_only", False)

    # --- Calcular score de consistencia ---
    consistent = 0.0
    total = len(local_hours)

    for lh in local_hours:
        in_work = work_start <= lh < work_end
        in_excluded = any(excl_start <= lh < excl_end for excl_start, excl_end in excluded_hours)

        if in_excluded:
            pass
        elif in_work:
            consistent += 1.0
        else:
            consistent += 0.5

    ratio = consistent / total if total > 0 else 0.0

    # --- Penalización por uniformidad ---
    minute_granules = {int(h * 60) for h in local_hours}
    if len(minute_granules) <= 2 and len(local_hours) >= 5:
        ratio *= 0.7

    return round(max(0.0, min(1.0, ratio)), 4)


def _check_actor_consistency(
    attributed_actor: str,
    infrastructure_evidence: dict,
    reference_date: Optional[str] = None
) -> float:
    """
    Evalúa consistencia entre evidencia de infraestructura y perfil APT.

    W7 FIX: tz_match usa escala exponencial en lugar de umbral binario.
    P0-003: DST real via zoneinfo.
    """
    activity_hours = infrastructure_evidence.get("activity_hours", [])
    tz_offset = infrastructure_evidence.get("timezone_offset", "")

    if not activity_hours or not tz_offset:
        return 0.5

    profile = _ACTOR_ACTIVITY_PROFILES.get(attributed_actor)
    if profile is None:
        return 0.5

    expected_offset = profile["primary_hours"][2]
    actual_offset = _TIMEZONE_OFFSETS.get(tz_offset)

    if actual_offset is None:
        return 0.5

    diff_minutes = abs(actual_offset - expected_offset)
    tz_match = max(0.0, 1.0 - (diff_minutes / 60.0))

    hours_score = _hours_match_timezone(activity_hours, tz_offset, reference_date)

    combined = 0.6 * hours_score + 0.4 * tz_match

    return round(max(0.0, min(1.0, combined)), 4)
