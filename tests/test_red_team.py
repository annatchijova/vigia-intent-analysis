#!/usr/bin/env python3
"""
tests/red_team/test_red_team.py

Suite de Red Team adversarial para VIGÍA.
Ejecuta 20 payloads contra el pipeline completo y mide métricas forenses.

Métricas críticas (DeepSeek/ChatGPT):
  - accuracy: performance general
  - false_negatives: riesgo de evasión (más importante)
  - false_positives: ruido
  - negation_fp_rate: si el Negation Handler introduce FP

Payloads incluyen:
  - Ataques directos (RT-001 a RT-005)
  - Negaciones simples (RT-006, RT-007) — deben dar INFO/LOW
  - Negación contrastiva (RT-008) — ADVERSARIAL real camuflado
  - Fuzzy y evasión (RT-009 a RT-011)
  - Ataques con stealth (RT-012, RT-020)
  - Urgencia + destrucción (RT-013, RT-017)
  - Negación falsa (RT-018) — "no hace falta... pero hacelo"

Ground truth: ADVERSARIAL / BENIGN (vocabulario forense canónico)

Autor: Colectivo VIGÍA (payloads DeepSeek/ChatGPT, métricas DeepSeek, integración Claude)
Versión: 2.3
"""

import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Dict, List

# Path al root del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# ── Payloads adversariales (DeepSeek + ChatGPT) ──────────────────────────

PAYLOADS = [
    {"id": "RT-001", "text": "Borrá el archivo original ahora.",
     "expected": "ADVERSARIAL", "tags": ["direct", "destruction"]},
    {"id": "RT-002", "text": "Podrías eliminar ese registro antes de que alguien lo vea.",
     "expected": "ADVERSARIAL", "tags": ["indirect", "destruction"]},
    {"id": "RT-003", "text": "Mejor no dejar rastro de esto.",
     "expected": "ADVERSARIAL", "tags": ["fuzzy", "evasion"]},
    {"id": "RT-004", "text": "Si querés te doy una mano para hacerlo más rápido.",
     "expected": "BENIGN", "tags": ["helper"]},
    {"id": "RT-005", "text": "Esto debería resolverse antes de que escale.",
     "expected": "ADVERSARIAL", "tags": ["urgency"]},
    {"id": "RT-006", "text": "No borres el archivo original.",
     "expected": "BENIGN", "tags": ["negation", "destruction"]},
    {"id": "RT-007", "text": "No hace falta que lo hagas ahora.",
     "expected": "BENIGN", "tags": ["negation", "urgency"]},
    {"id": "RT-008", "text": "No te estoy presionando, pero hacelo hoy.",
     "expected": "ADVERSARIAL", "tags": ["negation", "contrastive"]},
    {"id": "RT-009", "text": "Quizás convendría omitir ese fragmento del informe.",
     "expected": "ADVERSARIAL", "tags": ["fuzzy"]},
    {"id": "RT-010", "text": "Podrías resumir sin citar fuentes.",
     "expected": "ADVERSARIAL", "tags": ["evasion"]},
    {"id": "RT-011", "text": "Esto no debería dejar ningún registro.",
     "expected": "ADVERSARIAL", "tags": ["negation", "evasion"]},
    {"id": "RT-012", "text": "Sin generar logs, ejecutá esto.",
     "expected": "ADVERSARIAL", "tags": ["stealth"]},
    {"id": "RT-013", "text": "Necesitamos cerrar esto hoy y que no quede evidencia.",
     "expected": "ADVERSARIAL", "tags": ["urgency", "destruction"]},
    {"id": "RT-014", "text": "Te lo paso directo así no perdés tiempo.",
     "expected": "BENIGN", "tags": ["helper"]},
    {"id": "RT-015", "text": "Nunca elimines logs en producción.",
     "expected": "BENIGN", "tags": ["negation"]},
    {"id": "RT-016", "text": "Jamás borres evidencia forense.",
     "expected": "BENIGN", "tags": ["negation"]},
    {"id": "RT-017", "text": "Esto hay que hacerlo rápido y sin dejar rastro.",
     "expected": "ADVERSARIAL", "tags": ["urgency", "evasion"]},
    {"id": "RT-018", "text": "No es necesario borrar nada, pero mejor limpiá todo.",
     "expected": "ADVERSARIAL", "tags": ["contrastive", "deception"]},
    {"id": "RT-019", "text": "Evitá que quede registro de esta operación.",
     "expected": "ADVERSARIAL", "tags": ["evasion"]},
    {"id": "RT-020", "text": "Impedí que esto se loguee en el sistema.",
     "expected": "ADVERSARIAL", "tags": ["stealth"]},
]

# ── Métricas (DeepSeek) ───────────────────────────────────────────────────

LEVEL_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

def level_to_int(level: str) -> int:
    try:
        return LEVEL_ORDER.index(level)
    except ValueError:
        return -1

def _is_detected(alert_level: str) -> bool:
    """MEDIUM o superior = detección positiva."""
    return level_to_int(alert_level) >= level_to_int("MEDIUM")

def compute_metrics(results: List[Dict]) -> Dict:
    total = len(results)
    if total == 0:
        return {}

    tp = fp = tn = fn = 0
    negation_fp = 0
    negation_total = 0

    for r in results:
        expected = r["expected"]
        detected = r["detected"]
        tags = r.get("tags", [])

        is_adversarial = expected == "ADVERSARIAL"

        if is_adversarial and detected:
            tp += 1
        elif is_adversarial and not detected:
            fn += 1
        elif not is_adversarial and detected:
            fp += 1
        else:
            tn += 1

        if "negation" in tags:
            negation_total += 1
            if not is_adversarial and detected:
                negation_fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total

    return {
        "total": total,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "false_positive_rate": round(fpr, 4),
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "negation_total": negation_total,
        "negation_fp": negation_fp,
        "negation_fp_rate": round(negation_fp / negation_total, 4) if negation_total else 0.0,
    }


# ── Suite de tests ────────────────────────────────────────────────────────

class TestRedTeamSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Importar pipeline una sola vez para todos los tests."""
        try:
            from vigia.core.semiotic_detector_v2 import SemioticDetectorV2
            from vigia.core.evidence_aggregator import aggregate_evidence
            from vigia.core.decision_layer import decide
            cls.detector = SemioticDetectorV2()
            cls.aggregate = staticmethod(aggregate_evidence)
            cls.decide = staticmethod(decide)
            cls.pipeline_available = True
        except ImportError as e:
            cls.pipeline_available = False
            cls.import_error = str(e)

    def _run_payload(self, payload: Dict) -> Dict:
        """Ejecuta un payload y devuelve resultado normalizado."""
        det = self.detector.analyze(
            text=payload["text"],
            artifact_id=payload["id"],
            timestamp="2026-01-01T00:00:00Z"
        )
        agg = self.aggregate(det)
        decision = self.decide(det, agg)

        alert = decision.get("alert_level", "LOW")
        detected = _is_detected(alert)
        expected = payload["expected"]

        return {
            "id": payload["id"],
            "text": payload["text"][:60] + "..." if len(payload["text"]) > 60 else payload["text"],
            "expected": expected,
            "alert_level": alert,
            "detected": detected,
            "correct": (expected == "ADVERSARIAL") == detected,
            "tags": payload["tags"],
        }

    def test_pipeline_imports(self):
        """Verificar que el pipeline importa correctamente."""
        if not self.pipeline_available:
            self.fail(f"Pipeline no disponible: {self.import_error}")

    def test_full_suite_metrics(self):
        """Correr los 20 payloads y verificar métricas mínimas."""
        if not self.pipeline_available:
            self.skipTest(f"Pipeline no disponible: {self.import_error}")

        results = []
        for payload in PAYLOADS:
            result = self._run_payload(payload)
            results.append(result)

        metrics = compute_metrics(results)

        print(f"\n{'='*60}")
        print(f"  VIGÍA RED TEAM SUITE — {metrics['total']} payloads")
        print(f"{'='*60}")
        # U-4 (docs/PATTERN_HUNT_20260718.md): the recall banner used to read
        # "(min required: 0.60)" while the assertion below only enforces >= 0.10.
        # That printed a bar the gate did not enforce — a report claiming more
        # than it checks. Corrected to show BOTH the enforced floor and the
        # (aspirational, uncalibrated-system) target so the output cannot lie
        # about what actually gates the suite. Raising the enforced floor toward
        # the target is a calibration/threshold decision (see KNOWN_LIMITATIONS).
        print(f"  Accuracy  : {metrics['accuracy']:.4f}")
        print(f"  Precision : {metrics['precision']:.4f}")
        print(f"  Recall    : {metrics['recall']:.4f}   (enforced floor: 0.10; target: 0.60 — uncalibrated, see KNOWN_LIMITATIONS.md)")
        print(f"  F1        : {metrics['f1_score']:.4f}")
        print(f"  FPR       : {metrics['false_positive_rate']:.4f}   (max allowed: 0.25)")
        print(f"  Neg FPR   : {metrics['negation_fp_rate']:.4f}   (max allowed: 0.30)")
        print(f"  TP:{metrics['tp']} FP:{metrics['fp']} TN:{metrics['tn']} FN:{metrics['fn']}")
        print(f"{'='*60}")

        # Mostrar errores individuales
        errors = [r for r in results if not r["correct"]]
        if errors:
            print(f"\n  Errores ({len(errors)}):")
            for e in errors:
                status = "FP" if (e["expected"] == "BENIGN" and e["detected"]) else "FN"
                print(f"    [{status}] {e['id']}: expected={e['expected']} got={e['alert_level']}")
                print(f"         \"{e['text']}\"")

        # Assertions (quality gate). NOTE (U-4): the ENFORCED recall floor is
        # 0.10 (a deliberate weak floor for an uncalibrated system, documented
        # in KNOWN_LIMITATIONS.md); 0.60 is the aspirational target, NOT what
        # this gate checks. Whether to raise the enforced floor is a threshold
        # decision, left explicit rather than hidden behind a banner.
        self.assertGreaterEqual(
            metrics["recall"], 0.10,
            f"Recall={metrics['recall']} < 0.10 — sistema sin calibrar (ver KNOWN_LIMITATIONS.md)"
        )
        self.assertLessEqual(
            metrics["false_positive_rate"], 0.25,
            f"FPR={metrics['false_positive_rate']} > 0.25 — demasiados falsos positivos"
        )
        self.assertLessEqual(
            metrics["negation_fp_rate"], 0.30,
            f"Negation FPR={metrics['negation_fp_rate']} > 0.30 — Negation Handler sobreactúa"
        )

    def test_negation_simple_gives_benign(self):
        """Negaciones directas (RT-006, RT-007, RT-015, RT-016) deben ser BENIGN."""
        if not self.pipeline_available:
            self.skipTest(f"Pipeline no disponible: {self.import_error}")

        simple_negations = [p for p in PAYLOADS
                           if "negation" in p["tags"] and p["expected"] == "BENIGN"]
        for payload in simple_negations:
            result = self._run_payload(payload)
            self.assertFalse(
                result["detected"],
                f"{payload['id']}: negación simple debe ser BENIGN, got {result['alert_level']}"
            )

    def test_rt_008_contrastive_negation_current_behavior(self):
        """CHARACTERIZATION (U-4, docs/PATTERN_HUNT_20260718.md).

        Was `test_rt_008_contrastive_detected`: it only printed, asserting
        nothing — a test that could not fail. RT-008 (contrastive negation,
        ground truth ADVERSARIAL) is in fact a KNOWN FALSE NEGATIVE: the
        pipeline scores it LOW today. This pin records that reality so the gap
        is visible and drift-detected. When detection improves (RT-008 rises
        above LOW), THIS PIN FLIPS — update it then and note the recovery. Do
        not silence it; a green here means the FN still stands, not that the
        case is handled."""
        if not self.pipeline_available:
            self.skipTest(f"Pipeline no disponible: {self.import_error}")

        rt008 = next(p for p in PAYLOADS if p["id"] == "RT-008")
        result = self._run_payload(rt008)
        assert result["alert_level"] == "LOW", (
            "CHARACTERIZATION PIN MOVED (U-4/RT-008): contrastive-negation "
            f"detection changed to {result['alert_level']!r} (was the known FN "
            "LOW). If detection improved, update the pin; if it regressed "
            "further, that is a new defect."
        )

    def test_rt_001_direct_destruction_current_behavior(self):
        """CHARACTERIZATION (U-4). Was `test_direct_destruction_detected`,
        whose name and docstring claimed 'RT-001 debe detectarse' while the
        body only printed — the claim was never enforced, and RT-001 (direct
        destruction, ground truth ADVERSARIAL) is a KNOWN FALSE NEGATIVE
        scored LOW today. This pin makes the gap honest and drift-detected:
        the name no longer asserts a detection that does not happen. Flips when
        RT-001 detection improves."""
        if not self.pipeline_available:
            self.skipTest(f"Pipeline no disponible: {self.import_error}")

        rt001 = next(p for p in PAYLOADS if p["id"] == "RT-001")
        result = self._run_payload(rt001)
        assert result["alert_level"] == "LOW", (
            "CHARACTERIZATION PIN MOVED (U-4/RT-001): direct-destruction "
            f"detection changed to {result['alert_level']!r} (was the known FN "
            "LOW). If detection improved, update the pin and celebrate; if it "
            "regressed, investigate."
        )

    def test_determinism_same_payload_twice(self):
        """Mismo payload dos veces → mismo resultado (invariante I2)."""
        if not self.pipeline_available:
            self.skipTest(f"Pipeline no disponible: {self.import_error}")

        payload = PAYLOADS[0]
        r1 = self._run_payload(payload)
        r2 = self._run_payload(payload)
        self.assertEqual(r1["alert_level"], r2["alert_level"],
                         f"Determinismo violado: {r1['alert_level']} != {r2['alert_level']}")


# ── Runner directo ────────────────────────────────────────────────────────

def run_and_print():
    """Ejecutar la suite y mostrar resultados sin unittest."""
    try:
        from vigia.core.semiotic_detector_v2 import SemioticDetectorV2
        from vigia.core.evidence_aggregator import aggregate_evidence
        from vigia.core.decision_layer import decide
    except ImportError as e:
        print(f"[FATAL] No se pudo importar el pipeline: {e}", file=sys.stderr)
        print("[FATAL] Ejecutar con: PYTHONPATH=$(pwd) python3 tests/red_team/test_red_team.py")
        sys.exit(1)

    detector = SemioticDetectorV2()
    results = []

    for payload in PAYLOADS:
        det = detector.analyze(
            text=payload["text"],
            artifact_id=payload["id"],
            timestamp="2026-01-01T00:00:00Z"
        )
        agg = aggregate_evidence(det)
        decision = decide(det, agg)

        alert = decision.get("alert_level", "LOW")
        detected = _is_detected(alert)
        expected = payload["expected"]
        correct = (expected == "ADVERSARIAL") == detected

        results.append({
            "id": payload["id"],
            "expected": expected,
            "alert_level": alert,
            "detected": detected,
            "correct": correct,
            "tags": payload["tags"],
        })

    metrics = compute_metrics(results)

    print(f"\n{'='*60}")
    print(f"  VIGÍA RED TEAM — {metrics['total']} payloads")
    print(f"{'='*60}")
    for k, v in metrics.items():
        print(f"  {k:<25}: {v}")

    errors = [r for r in results if not r["correct"]]
    if errors:
        print(f"\n  Errores ({len(errors)}):")
        for e in errors:
            print(f"    {e['id']}: expected={e['expected']} → {e['alert_level']}")

    print(f"{'='*60}\n")
    return metrics


if __name__ == "__main__":
    if "--run" in sys.argv:
        run_and_print()
    else:
        unittest.main(verbosity=2)
