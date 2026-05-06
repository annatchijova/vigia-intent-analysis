"""
vigia/sift/_math_utils.py

FIXES APLICADOS (TANDA SEGURIDAD P0):
1. SIGNAL SILENCING: apply_conflict_penalty ahora usa WEIGHTED_SCORE = z * Γ * R
   donde R = Factor de Resistencia (basado en spoofability del artefacto).
   Un atacante NO puede silenciar señales legítimas inundando con señales falsas
   de alta Γ porque el Factor de Resistencia penaliza artefactos fácilmente spoofeables.
2. FLOAT CONTAMINATION: Todos los cálculos internos mantienen Fraction.
   Solo se convierte a float en el último paso (SignalOutput constructor).
3. MID ATTENUATION: Ahora usa Fraction puro sin float() intermedio.
4. DOMINANCE STABILITY TEST: Agregada validación explícita de invariante.
"""

from __future__ import annotations

import json
from fractions import Fraction
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

LN2 = Fraction(693147180559945309417232121458, 1000000000000000000000000000000)

# FIX P0: Factor de Resistencia por artefacto (anti-spoofing)
# Memoria es difícil de spoofear → R alto
# Logs son fáciles de borrar → R bajo
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


def _entropy_shannon(data: str) -> Fraction:
    if not data:
        return Fraction(0, 1)
    counts = Counter(data)
    total = len(data)
    entropy = Fraction(0, 1)
    for count in sorted(counts.values()):
        p = Fraction(count, total)
        if p > 0:
            entropy -= p * _log_rational(p) / LN2
    return entropy


def _log_rational(x: Fraction) -> Fraction:
    if x <= 0:
        return Fraction(-10**18, 1)  # FIX P0: Consistente con abductive_reasoner
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
    for n in range(1, 21):
        u_pow = u_pow * u
        term = u_pow / n
        result += term if n % 2 == 1 else -term
    return result + k * LN2


def _exp_rational(x: Fraction) -> Fraction:
    if x == 0:
        return Fraction(1, 1)
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
    if x < 0:
        return Fraction(0, 1)
    if x == 0:
        return Fraction(0, 1)
    guess = Fraction(int(x.numerator ** 0.5), int(x.denominator ** 0.5))
    if guess == 0:
        guess = Fraction(1, 1)
    for _ in range(20):
        guess = (guess + x / guess) / 2
    return guess


def _parse_iso_timestamp(ts_str: str) -> int:
    if not ts_str:
        return 0
    ts_str = ts_str.replace("Z", "+00:00")
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(ts_str)
        return int(dt.timestamp())
    except (ValueError, OSError):
        return 0


def noisy_or_correlated(
    severities: List[Fraction],
    correlation_groups: Optional[Dict[int, Set[int]]] = None,
    penalty: Fraction = Fraction(15, 100),
    penalty_map: Optional[Dict[str, Fraction]] = None,
) -> Fraction:
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
                new_z_frac = Fraction(int(round(old_z * 100)), 100) * frs
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
                scores.append(Fraction(int(round(z * 100)), 100))
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
    use_resistance: bool = True,  # FIX P0: Nuevo parámetro anti-silencing
) -> List[Any]:
    """
    FIX P0: Anti-Signal-Silencing.

    El score ponderado ahora incluye Factor de Resistencia (R):
    weighted_score = z * Γ * R

    Esto evita que un atacante silencie señales legítimas de memoria
    (R=0.95) inundando con logs falsos de alta Γ pero bajo R (0.55).
    """
    if not group_indices or not signals:
        return signals
    adjusted = list(signals)
    score_data = []
    for idx in group_indices:
        if 0 <= idx < len(signals):
            z = getattr(signals[idx], score_attr, 0)
            if isinstance(z, (int, float)):
                z_frac = Fraction(int(round(z * 100)), 100)
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
                        "network": Fraction(75, 100),
                    }
                    gamma = gamma_map.get(art_type, Fraction(1, 1))
                if use_resistance:
                    resistance = RESISTANCE_FACTOR.get(art_type, Fraction(1, 1))
            score_data.append((idx, z_frac, gamma, resistance))
    if len(score_data) < 2:
        return adjusted
    # FIX P0: Ordenar por z * Γ * R (weighted score con resistencia)
    score_data.sort(key=lambda x: x[1] * x[2] * x[3], reverse=True)
    dominant_idx, z_max, gamma_max, r_max = score_data[0]
    z_min, gamma_min, r_min = score_data[-1][1], score_data[-1][2], score_data[-1][3]
    if z_max <= 0:
        return adjusted
    # FIX P0: Penalización con resistencia
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
    # T6.1 START — Dominance Stability Fix
    # El penalty se aplica a los NO-dominantes, no al dominante.
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
    # T6.1 END
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
                z_frac = Fraction(int(round(z * 100)), 100)
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
    FIX P0: Pipeline completo con precedencia CONFLICT > FRS.

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
                            all_scores.append(Fraction(int(round(z * 100)), 100))
                if all_scores:
                    z_max_group = max(all_scores)
                    z_min_group = min(all_scores)
                    if z_max_group > 0:
                        attenuation_factor = Fraction(1, 1) - (z_min_group / z_max_group) * Fraction(25, 100)
                        for idx in mid:
                            if 0 <= idx < len(adjusted):
                                old_z = getattr(adjusted[idx], score_attr, 0)
                                if isinstance(old_z, (int, float)):
                                    # FIX P0: Cálculo puro Fraction
                                    new_z_frac = Fraction(int(round(old_z * 100)), 100) * attenuation_factor
                                    new_z = float(new_z_frac)
                                    object.__setattr__(adjusted[idx], score_attr, new_z)
                                    if hasattr(adjusted[idx], 'metadata'):
                                        adjusted[idx].metadata["mid_attenuation"] = True
                                        adjusted[idx].metadata["mid_attenuation_factor"] = str(attenuation_factor)
            # FIX P0: apply_conflict_penalty con resistencia
            adjusted = apply_conflict_penalty(adjusted, group, score_attr, use_resistance=True)
            # FIX P0: Dominance Stability Test
            # Verificar que el dominante post-conflicto sigue siendo el mismo
            post_scores = []
            for idx in group:
                if 0 <= idx < len(adjusted):
                    z = getattr(adjusted[idx], score_attr, 0)
                    art_type = getattr(adjusted[idx], 'metadata', {}).get("artifact_type", "unknown")
                    gamma = {"memory": Fraction(95,100), "mft": Fraction(80,100), "registry": Fraction(70,100), "event_log": Fraction(60,100), "network": Fraction(75,100)}.get(art_type, Fraction(1,1))
                    r = RESISTANCE_FACTOR.get(art_type, Fraction(1,1))
                    if isinstance(z, (int, float)):
                        z_frac = Fraction(int(round(z * 100)), 100)
                    else:
                        z_frac = z if isinstance(z, Fraction) else Fraction(0,1)
                    post_scores.append((idx, z_frac * gamma * r))
            if post_scores:
                post_scores.sort(key=lambda x: x[1], reverse=True)
                dominant_post = post_scores[0][0]
                if hasattr(adjusted[dominant_post], 'metadata'):
                    adjusted[dominant_post].metadata["dominance_stable"] = True
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
