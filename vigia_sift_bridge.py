# Shim de compatibilidad para tests
from vigia.tools.vigia_sift_bridge import (
    _sanitize_grep_pattern,
    calculate_shannon_entropy,
    detect_human_jitter,
    infer_intent,
    detect_eco_overinterpretation,
    analyze_stylometry,
    audit_grice_maxims,
    calculate_human_entropy,
    detect_habit_incongruence,
)
from vigia.security.security import _sanitize_path
