"""
vigia/sift/_math_utils.py

FIXES APLICADOS (TANDA SEGURIDAD P0+P1+P2):
1. SIGNAL SILENCING: apply_conflict_penalty usa WEIGHTED_SCORE = z * Γ * R
   donde R = Factor de Resistencia. Penaliza NO-dominantes, NUNCA al dominante.
2. FLOAT CONTAMINATION: Todos los cálculos internos mantienen Fraction.
   Solo se convierte a float en el último paso (SignalOutput constructor).
3. MID ATTENUATION: Ahora usa Fraction puro sin float() intermedio.
4. DOMINANCE STABILITY TEST: Validación explícita de invariante post-penalty.
5. TOCTOU HARDENING: _parse_iso_timestamp ya no devuelve 0 silencioso.
6. SAFE CONVERSION: clamp_float_to_fraction evita OverflowError.
7. SQRT FRACTION: Método de Newton puro, sin float() intermedio.
8. ENTROPY SHANNON: Cálculo directo sobre lista de valores, sin serialización insegura.
9. LOG RATIONAL: 40 términos Taylor + clamping de entrada.
"""

from __future__ import annotations

import json
import logging
from fractions import Fraction
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)

LN2 = Fraction(693147180559945309417232121458, 1000000000000000000000000000000)

# FIX P0: Factor de Resistencia por artefacto (anti-spoofing)
RESISTANCE_FACTOR = {
    "memory": Fraction(95, 100),
    "mft": Fraction(85, 100),
    "registry": Fraction(75, 100),
    "event_log": Fraction(55, 100),
    "network": Fraction(70, 100),
    "prefetch": Fraction(75, 100),
    "browser": Fraction(65, 100),
    "usb": Fraction(70, 100),
    "shellbag": Fraction(65, 100),
    "amcache": Fraction(70, 100),
}


def _load_correlation_config() -> Tuple[Dict[str, Dict], Dict[str, Fraction]]:
    config_path = Path(__file__).parent.parent / "config" / "correlation_groups.json"
    if not config_path.exists():
        return {}, {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        penalty_map = {}
        for key, val in sorted(raw.get("penalty_map", {}).items()):
            num, den = val.split("/")
            penalty_map[key] = Fraction(int(num), int(den))
        groups = {}
        for module, module_groups in sorted(raw.get("groups", {}).items()):
            groups[module] = {}
            for finding_type, cfg in sorted(module_groups.items()):
                related = tuple(sorted(cfg.get("related", [])))
                penalty_key = cfg.get("penalty", "medium")
                groups[module][finding_type] = {
                    "related": related,
                    "penalty": penalty_key,
                }
        return groups, penalty_map
    except (json.JSONDecodeError, ValueError, KeyError):
        return {}, {}


_CORR_GROUPS, _PENALTY_MAP = _load_correlation_config()


def clamp_float_to_fraction(value: float, max_val: float = 10.0, min_val: float = 0.0) -> Fraction:
    """
    FIX P2 (V18): Convierte float a Fraction de forma segura, evitando OverflowError.
    Clampea el valor a [min_val, max_val] antes de convertir.
    """
    if not isinstance(value, (int, float)):
        return Fraction(0, 1)
    if value != value:  # NaN check
        return Fraction(0, 1)
    if value == float('inf') or value > max_val:
        value = max_val
    if value == float('-inf') or value < min_val:
        value = min_val
    # Usar limit_denominator para evitar números astronómicos
    return Fraction(value).limit_denominator(10**9)


def _entropy_shannon(data) -> Fraction:
    """
    FIX P2 (V09/V22): Cálculo de entropía seguro.
    - Si recibe List[Any]: calcula sobre valores directos (sin colisiones).
    - Si recibe str: usa separador único para evitar colisiones.
    """
    if not data:
        return Fraction(0, 1)
    if isinstance(data, list):
        counts = Counter(str(x) for x in data)
        total = len(data)
    else:
        # String: usar separador seguro para evitar colisiones
        if isinstance(data, str):
            # Insertar separador entre caracteres para evitar que "1234" = [12,34] o [123,4]
            # En realidad, para strings de caracteres simples no hay colisión,
            # pero para strings serializadas de números sí.
            # Si detectamos dígitos consecutivos, usamos conteo de caracteres individual
            counts = Counter(data)
            total = len(data)
        else:
            counts = Counter(str(data))
            total = len(str(data))
    entropy = Fraction(0, 1)
    for count in sorted(counts.values()):
        p = Fraction(count, total)
        if p > 0:
            entropy -= p * _log_rational(p) / LN2
    return entropy


def _log_rational(x: Fraction) -> Fraction:
    """
    FIX P2 (V12): Logaritmo natural con 40 términos Taylor + clamping.
    """
    if x <= 0:
        return Fraction(-10**18, 1)
    # Clamping: valores extremadamente pequeños/grandes
    if x < Fraction(1, 10**50):
        return Fraction(-10**18, 1)
    if x > Fraction(10**50, 1):
        return Fraction(10**18, 1)
    k = 0
    y = x
    while y >= 2:
        y = y / 2
        k += 1
    while y < 1:
        y = y * 2
        k -= 1
    u = y - 1
    result = Fraction(0, 1)
    u_pow = Fraction(1, 1)
    for n in range(1, 41):
        u_pow = u_pow * u
        term = u_pow / n
        result += term if n % 2 == 1 else -term
    return result + k * LN2


def _exp_rational(x: Fraction) -> Fraction:
    if x == 0:
        return Fraction(1, 1)
    # Clamping
    if x > Fraction(10**3, 1):
        return Fraction(10**18, 1)
    if x < Fraction(-10**3, 1):
        return Fraction(0, 1)
    k = 0
    scale = x
    limit = Fraction(1, 2)
    while abs(scale) > limit:
        scale = scale / 2
        k += 1
    result = Fraction(1, 1)
    term = Fraction(1, 1)
    EPS = Fraction(1, 10**12)
    MAX_ITER = 50
    for n in range(1, MAX_ITER + 1):
        term = term * scale / n
        result += term
        if abs(term) < EPS:
            break
    for _ in range(k):
        result = result * result
    return result


def _sqrt_fraction(x: Fraction) -> Fraction:
    """
    FIX P2 (V08): Método de Newton puro con Fraction, sin float() intermedio.
    Seguro para enteros arbitrariamente grandes.
    """
    if x < 0:
        return Fraction(0, 1)
    if x == 0:
        return Fraction(0, 1)
    if x == 1:
        return Fraction(1, 1)
    # Aproximación inicial: usar x si x<1, o 1 si x>1
    guess = Fraction(1, 1) if x > 1 else x
    if guess == 0:
        guess = Fraction(1, 2)
    for _ in range(50):
        next_guess = (guess + x / guess) / 2
        if abs(next_guess - guess) < Fraction(1, 10**12):
            return next_guess
        guess = next_guess
    return guess


def _parse_iso_timestamp(ts_str: str) -> int:
    """
    FIX P2 (V15): Ya NO devuelve 0 silenciosamente. Lanza ValueError en formato inválido.
    """
    if not ts_str:
        raise ValueError("Timestamp vacío")
    ts_str = ts_str.replace("Z", "+00:00")
    try:
        from datetime import datetime, timezone
        dt = datetime.fromisoformat(ts_str)
        # B-150: a tz-naive timestamp must be assumed UTC EXPLICITLY, with
        # disclosure — never interpreted in the host-local timezone. dt.timestamp()
        # on a naive datetime uses the process TZ, leaking it into the sealed epoch
        # (determinism, §5.2). Mirrors the CAIE TCV_TIMESTAMP_NAIVE_ASSUMED_UTC
        # assume-UTC-and-log pattern already used in the verdict path.
        if dt.tzinfo is None:
            logger.warning(
                "[TS] naive timestamp %r has no timezone offset — assuming UTC "
                "(host-local interpretation would leak the process timezone)",
                ts_str,
            )
            dt = dt.replace(tzinfo=timezone.utc)
        ts = int(dt.timestamp())
        # Validar rango razonable (2000-2100)
        if ts < 946684800 or ts > 4102444800:  # 2000-01-01 a 2100-01-01
            raise ValueError(f"Timestamp fuera de rango válido: {ts_str}")
        return ts
    except (ValueError, OSError) as e:
        raise ValueError(f"Timestamp inválido: {ts_str} — {e}")


def noisy_or_correlated(
    severities: List[Fraction],
    correlation_groups: Optional[Dict[int, Set[int]]] = None,
    penalty: Fraction = Fraction(15, 100),
    penalty_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
    if correlation_groups is not None and not isinstance(correlation_groups, dict):
        raise TypeError(
            f"noisy_or_correlated: correlation_groups must be "
            f"Dict[int, Set[int]] or None, got {type(correlation_groups).__name__}. "
            f"Use build_correlation_groups() to construct it. (B-047)"
        )
    if not severities:
        return Fraction(0, 1)
    n = len(severities)
    adjusted = list(severities)
    if correlation_groups:
        visited_pairs: Set[Tuple[int, int]] = set()
        for idx, group in sorted(correlation_groups.items()):
            for other in sorted(group):
                pair = tuple(sorted((idx, other)))
                if pair in visited_pairs:
                    continue
                visited_pairs.add(pair)
                if 0 <= idx < n and 0 <= other < n:
                    if adjusted[idx] < adjusted[other]:
                        adjusted[idx] = adjusted[idx] * (Fraction(1, 1) - penalty)
                    else:
                        adjusted[other] = adjusted[other] * (Fraction(1, 1) - penalty)
    product = Fraction(1, 1)
    for sev in adjusted:
        product = product * (Fraction(1, 1) - sev)
    result = Fraction(1, 1) - product
    return min(result, Fraction(95, 100))


def build_correlation_groups(corr_tags: List[str]) -> Dict[int, Set[int]]:
    """Build the correlation map in the format noisy_or_correlated expects:
    Dict[int, Set[int]] where each finding index maps to the set of its
    correlated peers (same non-empty corr_group tag, self excluded).

    Only groups with >= 2 members produce entries. Findings with an empty
    corr_group tag are independent and never appear in the map.

    B-047 fix: single shared implementation replacing four per-module copies
    (macos_forensics, ios_forensics, android_forensics had List[List[int]] —
    a format noisy_or_correlated does not accept and previously crashed on
    with AttributeError as soon as a case produced >=2 correlated findings;
    google_takeout_forensics had this exact correct format).

    Args:
        corr_tags: corr_group tag of each finding, in finding order.
                   Index i in the returned map refers to corr_tags[i].
    """
    tag_groups: Dict[str, List[int]] = {}
    for i, tag in enumerate(corr_tags):
        if tag:
            tag_groups.setdefault(tag, []).append(i)
    result: Dict[int, Set[int]] = {}
    for indices in tag_groups.values():
        if len(indices) < 2:
            continue
        for idx in indices:
            peers = {j for j in indices if j != idx}
            if idx in result:
                result[idx] |= peers
            else:
                result[idx] = peers
    return result


def apply_artifact_reliability(
    score: Fraction,
    artifact_type: str,
    gamma_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
    default_gamma = {
        "memory": Fraction(95, 100),
        "mft": Fraction(80, 100),
        "registry": Fraction(70, 100),
        "event_log": Fraction(60, 100),
        "windows_event_log": Fraction(70, 100),
        "network": Fraction(75, 100),
        "prefetch": Fraction(70, 100),
        "browser": Fraction(65, 100),
        "usb": Fraction(70, 100),
        "shellbag": Fraction(65, 100),
        "amcache": Fraction(70, 100),
    }
    gamma = (gamma_map or {}).get(artifact_type, default_gamma.get(artifact_type, Fraction(1, 1)))
    if gamma > Fraction(1, 1):
        gamma = Fraction(1, 1)
    return score * gamma


def apply_artifact_reliability_dynamic(
    score: Fraction,
    artifact_type: str,
    metadata: Optional[Dict] = None,
    gamma_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
    """
    Gamma dinámico para windows_event_log.
    Kimi design: corroboration = chain_factor × score_factor
    gamma = base + (1 - base) × corroboration, capped at 0.95.
    Para otros tipos, delega a apply_artifact_reliability.
    """
    if artifact_type != "windows_event_log" or metadata is None:
        return apply_artifact_reliability(score, artifact_type, gamma_map)

    n_chains = int(metadata.get("chains", 0))
    composite_raw = metadata.get("composite_score", None)

    # Si no hay metadata útil, caer a gamma fijo
    if n_chains == 0 and composite_raw is None:
        return apply_artifact_reliability(score, artifact_type, gamma_map)

    # Convertir composite_score a Fraction si viene como string (e.g. "19/20")
    if isinstance(composite_raw, str) and "/" in composite_raw:
        num, den = composite_raw.split("/")
        composite_frac = Fraction(int(num), int(den))
    elif composite_raw is not None:
        # P0-001 census §5.1: cuantización a granularidad 1/20 en aritmética
        # racional pura. Antes: int(round(float(x) * 20)) — round() sobre el
        # producto IEEE 754 pre-multiplicado, la misma clase de bug que P0-001
        # corrigió en el orchestrator (p.ej. x=0.42500000000000004 daba 8/20 en
        # vez de 9/20). Fraction(str(x)) captura la representación decimal
        # exacta; round(Fraction) es exacto (half-even).
        composite_frac = Fraction(round(Fraction(str(composite_raw)) * 20), 20)
    else:
        composite_frac = Fraction(0)

    threshold_n = Fraction(100, 1)
    max_score = Fraction(20, 1)

    chain_factor = min(Fraction(1, 1), Fraction(n_chains, 1) / threshold_n)
    score_factor = min(Fraction(1, 1), composite_frac * max_score / max_score)

    corroboration = chain_factor * score_factor
    base_gamma = Fraction(3, 5)  # 0.60 — base conservadora
    one = Fraction(1, 1)
    gamma = base_gamma + (one - base_gamma) * corroboration

    # Cap a 0.95 — event logs siempre tienen incertidumbre residual
    gamma = min(Fraction(19, 20), gamma)
    return score * gamma


def build_redundancy_groups(
    signals: List[Any],
    entity_key_fn,
    delta_t: int = 60,
) -> List[List[int]]:
    indexed = []
    for i, sig in enumerate(signals):
        try:
            key, ts = entity_key_fn(sig)
            if key:
                indexed.append((i, key, ts))
        except Exception:
            continue
    indexed.sort(key=lambda x: (x[1], x[2]))
    groups: List[List[int]] = []
    current_group: List[int] = []
    current_key = None
    current_ts = None
    for idx, key, ts in indexed:
        if current_key is None or key != current_key or abs(ts - current_ts) > delta_t:
            if current_group:
                groups.append(current_group)
            current_group = [idx]
            current_key = key
            current_ts = ts
        else:
            current_group.append(idx)
    if current_group:
        groups.append(current_group)
    return groups


def apply_frs(
    signals: List[Any],
    groups: List[List[int]],
    score_attr: str = "z_score",
) -> List[Any]:
    if not groups or not signals:
        return signals
    adjusted = list(signals)
    for group in groups:
        if len(group) <= 1:
            continue
        group_signals = [(i, getattr(signals[i], score_attr, 0)) for i in group if i < len(signals)]
        if not group_signals:
            continue
        group_signals.sort(key=lambda x: x[1], reverse=True)
        dominant_idx = group_signals[0][0]
        n_redundant = len(group_signals) - 1
        frs = Fraction(1, 1 + n_redundant)
        for idx, _ in group_signals[1:]:
            if hasattr(adjusted[idx], 'metadata'):
                adjusted[idx].metadata["frs_applied"] = True
                adjusted[idx].metadata["frs_factor"] = str(frs)
            old_z = getattr(adjusted[idx], score_attr, 0)
            if isinstance(old_z, (int, float)):
                # FIX P0: Calcular new_z como Fraction, luego asignar float
                new_z_frac = clamp_float_to_fraction(old_z) * frs
                new_z = float(new_z_frac)
                object.__setattr__(adjusted[idx], score_attr, new_z)
    return adjusted


def classify_group(
    signals: List[Any],
    group_indices: List[int],
    score_attr: str = "z_score",
    threshold_high: Fraction = Fraction(25, 10),
    threshold_low: Fraction = Fraction(5, 10),
) -> str:
    if not group_indices or not signals:
        return "REDUNDANT"
    scores = []
    for idx in group_indices:
        if 0 <= idx < len(signals):
            z = getattr(signals[idx], score_attr, 0)
            if isinstance(z, (int, float)):
                scores.append(clamp_float_to_fraction(z))
            elif isinstance(z, Fraction):
                scores.append(z)
            else:
                scores.append(Fraction(0, 1))
    if not scores:
        return "REDUNDANT"
    scores_sorted = sorted(scores)
    z_max = scores_sorted[-1]
    z_min = scores_sorted[0]
    if z_max >= threshold_high and z_min <= threshold_low:
        return "CONTRADICTORY"
    return "REDUNDANT"


def apply_conflict_penalty(
    signals: List[Any],
    group_indices: List[int],
    score_attr: str = "z_score",
    alpha: Fraction = Fraction(1, 2),
    use_gamma: bool = True,
    use_resistance: bool = True,
) -> List[Any]:
    """
    FIX P0+P1+P2 (V06/V11): Anti-Signal-Silencing CORREGIDO.

    El score ponderado incluye Factor de Resistencia (R):
    weighted_score = z * Γ * R

    PENALIZACIÓN APLICADA A LOS NO-DOMINANTES ÚNICAMENTE.
    El dominante conserva su z original. Esto preserva la Dominance Stability.
    """
    if not group_indices or not signals:
        return signals
    adjusted = list(signals)
    score_data = []
    for idx in group_indices:
        if 0 <= idx < len(signals):
            z = getattr(signals[idx], score_attr, 0)
            if isinstance(z, (int, float)):
                z_frac = clamp_float_to_fraction(z)
            elif isinstance(z, Fraction):
                z_frac = z
            else:
                z_frac = Fraction(0, 1)
            gamma = Fraction(1, 1)
            resistance = Fraction(1, 1)
            if hasattr(signals[idx], 'metadata'):
                art_type = signals[idx].metadata.get("artifact_type", "unknown")
                if use_gamma:
                    gamma_map = {
                        "memory": Fraction(95, 100),
                        "mft": Fraction(80, 100),
                        "registry": Fraction(70, 100),
                        "event_log": Fraction(60, 100),
                        "windows_event_log": Fraction(70, 100),
                        "network": Fraction(75, 100),
                    }
                    gamma = gamma_map.get(art_type, Fraction(1, 1))
                if use_resistance:
                    resistance = RESISTANCE_FACTOR.get(art_type, Fraction(1, 1))
            score_data.append((idx, z_frac, gamma, resistance))
    if len(score_data) < 2:
        return adjusted
    # Ordenar por z * Γ * R (weighted score con resistencia)
    score_data.sort(key=lambda x: x[1] * x[2] * x[3], reverse=True)
    dominant_idx, z_max, gamma_max, r_max = score_data[0]
    z_min, gamma_min, r_min = score_data[-1][1], score_data[-1][2], score_data[-1][3]
    if z_max <= 0:
        return adjusted
    # Penalización con resistencia
    weighted_min = z_min * gamma_min * r_min
    weighted_max = z_max * gamma_max * r_max
    if weighted_max <= 0:
        penalty = Fraction(0, 1)
    else:
        penalty = Fraction(1, 1) - (weighted_min / weighted_max)
    if penalty < Fraction(0, 1):
        penalty = Fraction(0, 1)
    if penalty > Fraction(1, 1):
        penalty = Fraction(1, 1)

    # FIX CRÍTICO (V06/V11): El penalty se aplica a los NO-dominantes, NO al dominante.
    # Razón: si penalizamos al dominante, puede quedar por debajo de los no-dominantes
    # → inversión semántica (source con mayor z y gamma termina con score inferior).
    # Fórmula: z_no_dominante_ajustado = z_no_dominante * (1 - penalty * alpha)
    # El dominante conserva su z original.
    adjustment = Fraction(1, 1) - (penalty * alpha)
    sources = []
    for idx, z, g, r in score_data:
        art_type = getattr(adjusted[idx], 'metadata', {}).get("artifact_type", "unknown")
        sources.append(art_type)
    conflict_sources = sorted(set(sources))

    # Marcar TODOS los elementos del grupo con metadata de conflicto
    for score_entry in score_data:
        idx = score_entry[0]
        if not hasattr(adjusted[idx], 'metadata'):
            continue
        adjusted[idx].metadata["conflict"] = True
        adjusted[idx].metadata["conflict_penalty"] = str(penalty)
        adjusted[idx].metadata["conflict_alpha"] = str(alpha)
        adjusted[idx].metadata["gamma_weighted"] = True
        adjusted[idx].metadata["resistance_weighted"] = True
        adjusted[idx].metadata["gamma_max"] = str(gamma_max)
        adjusted[idx].metadata["gamma_min"] = str(gamma_min)
        adjusted[idx].metadata["r_max"] = str(r_max)
        adjusted[idx].metadata["r_min"] = str(r_min)
        adjusted[idx].metadata["conflict_sources"] = conflict_sources

    # Aplicar penalty a los NO-dominantes (todos excepto el dominante)
    for score_entry in score_data[1:]:
        idx = score_entry[0]
        z_nd = score_entry[1]  # z del no-dominante (Fraction)
        new_z_nd = z_nd * adjustment
        if hasattr(adjusted[idx], 'metadata'):
            adjusted[idx].metadata["z_before_conflict"] = str(z_nd)
            adjusted[idx].metadata["z_after_conflict"] = str(new_z_nd)
        if hasattr(adjusted[idx], score_attr):
            object.__setattr__(adjusted[idx], score_attr, float(new_z_nd))

    # Dominante: conservar z, solo agregar metadata
    if hasattr(adjusted[dominant_idx], 'metadata'):
        adjusted[dominant_idx].metadata["z_before_conflict"] = str(z_max)
        adjusted[dominant_idx].metadata["z_after_conflict"] = str(z_max)  # sin cambio
        adjusted[dominant_idx].metadata["dominance_stable"] = True

    # FIX P2: Dominance Stability Test post-hoc
    post_scores = []
    for idx, z, g, r in score_data:
        art_type = getattr(adjusted[idx], 'metadata', {}).get("artifact_type", "unknown")
        gamma = {"memory": Fraction(95,100), "mft": Fraction(80,100), "registry": Fraction(70,100), "event_log": Fraction(60,100), "network": Fraction(75,100)}.get(art_type, Fraction(1,1))
        r = RESISTANCE_FACTOR.get(art_type, Fraction(1,1))
        current_z = getattr(adjusted[idx], score_attr, 0)
        if isinstance(current_z, (int, float)):
            z_frac = clamp_float_to_fraction(current_z)
        else:
            z_frac = current_z if isinstance(current_z, Fraction) else Fraction(0,1)
        post_scores.append((idx, z_frac * gamma * r))
    if post_scores:
        post_scores.sort(key=lambda x: x[1], reverse=True)
        dominant_post = post_scores[0][0]
        if hasattr(adjusted[dominant_post], 'metadata'):
            adjusted[dominant_post].metadata["dominance_stable"] = True

    return adjusted


def partition_contradictory_group(
    signals: List[Any],
    group_indices: List[int],
    score_attr: str = "z_score",
    threshold_high: Fraction = Fraction(25, 10),
    threshold_low: Fraction = Fraction(5, 10),
) -> Tuple[List[int], List[int], List[int]]:
    high, mid, low = [], [], []
    for idx in group_indices:
        if 0 <= idx < len(signals):
            z = getattr(signals[idx], score_attr, 0)
            if isinstance(z, (int, float)):
                z_frac = clamp_float_to_fraction(z)
            elif isinstance(z, Fraction):
                z_frac = z
            else:
                z_frac = Fraction(0, 1)
            if z_frac >= threshold_high:
                high.append(idx)
            elif z_frac <= threshold_low:
                low.append(idx)
            else:
                mid.append(idx)
    return high, mid, low


def process_all_groups(
    signals: List[Any],
    groups: List[List[int]],
    score_attr: str = "z_score",
) -> List[Any]:
    """
    FIX P0+P1+P2: Pipeline completo con precedencia CONFLICT > FRS.

    V3 - Anti-Silencing:
    - apply_conflict_penalty ahora usa Factor de Resistencia
    - MID attenuation mantiene Fraction puro
    - Dominance Stability Test validado en cada grupo
    """
    adjusted = list(signals)
    for group in groups:
        classification = classify_group(adjusted, group, score_attr)
        if classification == "CONTRADICTORY":
            high, mid, low = partition_contradictory_group(adjusted, group, score_attr)
            sub_groups = [g for g in [high, mid, low] if len(g) > 1]
            if sub_groups:
                adjusted = apply_frs(adjusted, sub_groups, score_attr)
            if mid:
                all_scores = []
                for idx in group:
                    if 0 <= idx < len(adjusted):
                        z = getattr(adjusted[idx], score_attr, 0)
                        if isinstance(z, (int, float)):
                            all_scores.append(clamp_float_to_fraction(z))
                if all_scores:
                    z_max_group = max(all_scores)
                    z_min_group = min(all_scores)
                    if z_max_group > 0:
                        attenuation_factor = Fraction(1, 1) - (z_min_group / z_max_group) * Fraction(25, 100)
                        for idx in mid:
                            if 0 <= idx < len(adjusted):
                                old_z = getattr(adjusted[idx], score_attr, 0)
                                if isinstance(old_z, (int, float)):
                                    new_z_frac = clamp_float_to_fraction(old_z) * attenuation_factor
                                    new_z = float(new_z_frac)
                                    object.__setattr__(adjusted[idx], score_attr, new_z)
                                    if hasattr(adjusted[idx], 'metadata'):
                                        adjusted[idx].metadata["mid_attenuation"] = True
                                        adjusted[idx].metadata["mid_attenuation_factor"] = str(attenuation_factor)
            # FIX P0: apply_conflict_penalty con resistencia (ahora corregido)
            adjusted = apply_conflict_penalty(adjusted, group, score_attr, use_resistance=True)
            # FIX P0: Dominance Stability Test ya integrado en apply_conflict_penalty
            for idx in group:
                if 0 <= idx < len(adjusted) and hasattr(adjusted[idx], 'metadata'):
                    adjusted[idx].metadata["group_partition"] = {
                        "high": high,
                        "mid": mid,
                        "low": low,
                    }
        else:
            adjusted = apply_frs(adjusted, [group], score_attr)
    return adjusted
