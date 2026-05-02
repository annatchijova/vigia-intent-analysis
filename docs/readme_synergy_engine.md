# VIGÍA Synergy Engine v2.0

## Qué es

Mejora del **SemioticPatternDetector** que resuelve las debilidades
identificadas por ChatGPT:

1. **Sinergia de patrones** — detección composicional (no independiente)
2. **Fuzzy matching determinista** — resiliencia a paráfrasis sin floats
3. **Memoria temporal** — sliding window de sesión con secuencias de ataque
4. **Forensic Signal Vector** — features cuantificados para RiskBoundedDecisionLayer

---

## Archivos generados

| Archivo | Propósito |
|---------|-----------|
| `synergy_matrix.json` | 8 reglas de sinergia con multiplicadores racionales |
| `fuzzy_config.json` | 5 patrones expandidos con variantes semánticas |
| `session_memory_config.json` | Configuración de sliding window y secuencias |
| `fsv_schema.json` | Schema del Forensic Signal Vector |
| `semiotic_detector_v2.py` | **Integrador completo** — lo que Claude debe implementar |

---

## Determinismo garantizado

- ✅ Sinergia: multiplicadores como fracciones (num/den)
- ✅ Fuzzy: n-grams con umbral racional 13/20
- ✅ Memoria: sliding window fijo de 10 entradas
- ✅ FSV: aritmética racional, no floating point
- ✅ Todo `sort_keys=True`, hashes SHA-256

---

## Reglas de sinergia

| ID | Patrones | Multiplicador | Cap bonus | MITRE |
|----|----------|---------------|-----------|-------|
| SYN-001 | HELPER_TRAP + QUANTITY_STARVATION | 5/4 = 1.25 | 1/20 = 0.05 | T1567 |
| SYN-002 | URGENCY + DEFENSIVE_EVASION | 13/10 = 1.30 | 3/50 = 0.06 | T1204 |
| SYN-003 | KEYBOARD_SLIP + MANNER_AMBIGUITY | 6/5 = 1.20 | 1/25 = 0.04 | T1585 |
| SYN-004 | FLATTERY + HELPER + URGENCY | 3/2 = 1.50 | 1/10 = 0.10 | T1566 |
| SYN-005 | UNVERIFIABLE + BORROWED_CRED | 7/5 = 1.40 | 1/20 = 0.05 | T1589 |
| SYN-006 | SYNTHETIC_JITTER + INHUMAN_PERF | 5/4 = 1.25 | 1/20 = 0.05 | T1071 |
| SYN-007 | PREEMPTIVE_CONF + EVIDENCE_CLEAN | 8/5 = 1.60 | 3/50 = 0.06 | T1070 |
| SYN-008 | FALSE_AMATEUR + ANACHRONISM_TOOL | 9/5 = 1.80 | 1/10 = 0.10 | T1055 |

---

## Secuencias temporales detectadas

| ID | Fases | Bonus | MITRE |
|----|-------|-------|-------|
| SEQ-SOCIAL-ENGINEERING | FLATTERY→HELPER→URGENCY→EVASION→EXFILTRATION | 3/20 = 0.15 | T1566 |
| SEQ-INSIDER-SETUP | CONFESSION→CLEANING→NORMALIZATION→PERSISTENCE | 1/10 = 0.10 | T1078 |
| SEQ-OPSEC-FAILURE | PHYSICAL_SLIP→CORRECTION→COVER→REPETITION | 1/5 = 0.20 | T1585 |

---

## Evasión que ahora detectamos

| Texto de evasión | Patrón base | Variante fuzzy detectada |
|---|---|---|
| "quizás convendría omitir ese fragmento" | GRICE_DESTRUCTION_REQUEST | ✅ |
| "si querés te doy una mano" | CARNEGIE_HELPER_TRAP | ✅ |
| "esto debería resolverse antes de que escale" | CARNEGIE_ARTIFICIAL_URGENCY | ✅ |
| "sos de los pocos que entienden esto" | CARNEGIE_FLATTERY_MIRRORING | ✅ (regex) |
| "mejor no dejar rastro de esto" | GRICE_DESTRUCTION_REQUEST | ✅ |

---

## Próximo paso

Claude debe integrar `semiotic_detector_v2.py` en `adversarial_nlp.py`,
reemplazando el detector v1.0. El API es compatible:

```python
from vigia.core.semiotic_detector_v2 import analyze_artifact

result = analyze_artifact(
    text="soy un desastre, ghbdtn, no incluyas el texto",
    artifact_id="ART-001",
    timestamp="2024-01-01T09:00:00"
)
# result ahora incluye: matches, synergy, sequences, fsv, confidence_adjustment
```

---

*Generado: 2026-04-28T07:17:43.082720+00:00*
*Schema: v2.0 | Standard: SANS_FIND_EVIL_2026*
*Mejoras: ChatGPT red team → Kimi implementación determinista*
