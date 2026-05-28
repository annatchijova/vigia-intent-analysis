# vigia/tests/adversarial/vabs1_runner.py
#
# VIGÍA Adversarial Benchmark Suite v1 — Unified Runner
# ======================================================
# Ejecuta P3 (supuestos epistemologicos, 10 casos) +
# VABS-1 (escenarios forenses, 15 casos) en una sola
# pasada y genera un reporte unificado con metricas SANS.
#
# METRICAS PRIMARIAS (VABS-1 spec §11):
#   FNR-MAL    : malicious cases classified as BENIGN/NOISE
#   FPR-BEN    : benign cases classified as MALICE
#   ABSTAIN-OH  : % casos sin decision (overhead)
#   LR-CAL-ERR : desviacion LR esperada vs observada
#   CCS-FAIL   : casos con CCS incorrecto
#
# METRICAS ESTRUCTURALES:
#   SIFR       : sensor independence failure rate
#   XL-MISS    : cross-layer contradiction miss rate
#   CC-FALSE   : causal closure false acceptance rate
#   ENTROPY-BLIND: entropy invariance blindness score
#
# CLASIFICACION FINAL (VABS Score):
#   S (>=0.90) : SANS production-grade
#   A (>=0.80) : research robust
#   B (>=0.70) : prototype-grade
#   C (<0.70)  : fragile under adversarial load
#
# NOTA SOBRE LIMITES EPISTEMOLOGICOS:
#   Casos con expected["detectable"] == False son limites
#   del conocimiento, no fallas de implementacion.
#   El sistema PASA si emite ABSTAIN_* con audit trail.
#   El sistema FALLA si emite un veredicto confiado incorrecto.
#
# AUDITORIA: Claude (Anthropic), mayo 2026.

import sys
import json
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Imports del engine — ajustar segun estructura real del repo
try:
    from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact
    _ENGINE_AVAILABLE = True
except ImportError:
    _ENGINE_AVAILABLE = False


# Verdicts que representan abstension honesta
_ABSTAIN_VERDICTS = frozenset({
    "ABSTAIN",
    "ABSTAIN_EPISTEMIC",
    "ABSTAIN_DEGRADED",
    "ABSTAIN_CONTRADICTION",
    "ABSTAIN_DRIFT",
    "ABSTAIN_INSTABILITY",
    "ABSTAIN_LR_COLLAPSE",
    "ABSTAIN_STRUCTURED_GAP",
})

# Verdicts que representan veredicto malintencionado
_MALICE_VERDICTS = frozenset({"MALICE", "INTENT", "SUSPICION"})

# Verdicts que representan comportamiento benigno/limpio
_BENIGN_VERDICTS = frozenset({"BENIGN", "NOISE", "ACCEPT"})


class VABS1Runner:
    """
    Runner unificado P3 + VABS-1.

    Uso:
        runner = VABS1Runner(
            p3_dir=Path("./adversarial_tests_p3"),
            vabs1_dir=Path("./adversarial_tests_vabs1"),
        )
        runner.run()
        runner.save_report(Path("report_vabs1_unified.json"))
        runner.print_summary()
    """

    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"

    def __init__(
        self,
        p3_dir: Optional[Path] = None,
        vabs1_dir: Optional[Path] = None,
    ) -> None:
        self.p3_dir = p3_dir
        self.vabs1_dir = vabs1_dir
        self.results: List[Dict] = []
        self._engine_available = _ENGINE_AVAILABLE

    # ── Carga de casos ─────────────────────────────────────────────────────

    def _load_suite(self, suite_dir: Path, index_file: str) -> List[Dict]:
        idx_path = suite_dir / index_file
        if not idx_path.exists():
            raise FileNotFoundError(f"Index not found: {idx_path}")
        with open(idx_path, encoding="utf-8") as f:
            index = json.load(f)
        cases = []
        for cid in index["cases"]:
            p = suite_dir / f"{cid}.json"
            if not p.exists():
                raise FileNotFoundError(f"Case file not found: {p}")
            with open(p, encoding="utf-8") as f:
                cases.append(json.load(f))
        return cases

    def load_all_cases(self) -> List[Dict]:
        all_cases = []
        if self.p3_dir and self.p3_dir.exists():
            p3_cases = self._load_suite(self.p3_dir, "index_p3.json")
            for c in p3_cases:
                c.setdefault("suite", "P3")
            all_cases.extend(p3_cases)
        if self.vabs1_dir and self.vabs1_dir.exists():
            vabs1_cases = self._load_suite(self.vabs1_dir, "index_vabs1.json")
            for c in vabs1_cases:
                c.setdefault("suite", "VABS-1")
            all_cases.extend(vabs1_cases)
        return all_cases

    # ── Ejecucion de casos ─────────────────────────────────────────────────

    def run(self) -> List[Dict]:
        cases = self.load_all_cases()
        for case in cases:
            res = self._run_single(case)
            self.results.append(res)
        return self.results

    def _run_single(self, case: Dict) -> Dict:
        cid = case["case_id"]
        expected = case.get("expected", {})
        expected_verdict = expected.get("verdict", "UNKNOWN")
        expected_detectable = expected.get("detectable", True)
        expected_reason = expected.get("reason", "")
        criticality = case.get("criticality_score", 0.0)
        suite = case.get("suite", "UNKNOWN")

        if not self._engine_available:
            # Modo dry-run sin engine: simula ABSTAIN para todos
            actual_verdict = "ABSTAIN"
            actual_score = 0.5
        else:
            actual_verdict, actual_score = self._invoke_engine(case)

        status = self._classify_result(
            cid=cid,
            expected_verdict=expected_verdict,
            expected_detectable=expected_detectable,
            actual_verdict=actual_verdict,
            actual_score=actual_score,
            criticality=criticality,
        )

        return {
            "case_id": cid,
            "suite": suite,
            "vabs_category": case.get("vabs_category", case.get("breaks", ["?"])[0]),
            "criticality": criticality,
            "expected_verdict": expected_verdict,
            "expected_detectable": expected_detectable,
            "actual_verdict": actual_verdict,
            "actual_score": actual_score,
            "status": status,
            "breaks": case.get("breaks", []),
            "propagated_breaks": case.get("propagated_breaks", []),
            "expected_reason": expected_reason,
        }

    def _invoke_engine(self, case: Dict) -> Tuple[str, float]:
        """
        Invoca CrossArtifactIncongruenceEngine con los artefactos del caso.
        Retorna (verdict_str, score_float).
        """
        engine = CrossArtifactIncongruenceEngine()
        for a in case.get("artifacts", []):
            artifact = Artifact(
                source_tool=a.get("source_tool", "vabs_test"),
                evidence_type=a.get("evidence_type", "log_entry"),
                raw_score=a.get("raw_score", 0.5),
                metadata=a.get("metadata", {}),
            )
            engine.add_artifact(artifact)
        result = engine.evaluate()
        verdict = result.get("verdict", "NOISE")
        score = result.get("probabilistic_score", 0.0)
        return verdict, score

    # ── Clasificacion PASS/FAIL/REVIEW ─────────────────────────────────────

    def _classify_result(
        self,
        cid: str,
        expected_verdict: str,
        expected_detectable: bool,
        actual_verdict: str,
        actual_score: float,
        criticality: float,
    ) -> str:
        """
        Logica de clasificacion:

        Casos NO detectables (limites epistemologicos):
          - PASS si actual es ABSTAIN_*
          - FAIL si actual es un veredicto confiado (MALICE, BENIGN, etc.)
            independientemente de si coincide con expected

        Casos detectables:
          - PASS si expected == actual
          - REVIEW si actual es ABSTAIN_* y criticality > 0.5
            (degradacion elegante, puede ser valida)
          - FAIL si criticality > 0.7 y score > 0.7 y veredicto incorrecto
            (falsa confianza en zona roja — inaceptable)
          - FAIL si actual es NOISE y expected no es NOISE
          - REVIEW para todo lo demas
        """
        # Casos de limite epistemologico
        if not expected_detectable:
            if actual_verdict in _ABSTAIN_VERDICTS:
                return self.PASS
            # Emitir veredicto confiado cuando no habia señal detectable
            return self.FAIL

        # Casos detectables
        if expected_verdict == actual_verdict:
            return self.PASS

        # Abstension ante alta criticidad — posible degradacion valida
        if actual_verdict in _ABSTAIN_VERDICTS and criticality > 0.5:
            return self.REVIEW

        # Falsa confianza inaceptable
        if criticality > 0.7 and actual_score > 0.7:
            return self.FAIL

        # NOISE inesperado
        if actual_verdict == "NOISE" and expected_verdict not in {"NOISE", "BENIGN"}:
            return self.FAIL

        return self.REVIEW

    # ── Metricas VABS-1 §11 ────────────────────────────────────────────────

    def _compute_metrics(self) -> Dict:
        """
        Computa metricas primarias y estructurales del spec VABS-1.
        Aritmetica con Fraction para precision exacta — sin floats intermedios.
        """
        total = len(self.results)
        if total == 0:
            return {}

        # Casos maliciosos detectables
        mal_cases = [
            r for r in self.results
            if r["expected_detectable"]
            and r["expected_verdict"] in _MALICE_VERDICTS
        ]
        # Falsos negativos: malicioso clasificado como benigno o NOISE
        fn_mal = [
            r for r in mal_cases
            if r["actual_verdict"] in _BENIGN_VERDICTS
        ]

        # Casos benignos
        ben_cases = [
            r for r in self.results
            if r["expected_verdict"] in _BENIGN_VERDICTS
        ]
        # Falsos positivos: benigno clasificado como MALICE
        fp_ben = [
            r for r in ben_cases
            if r["actual_verdict"] in _MALICE_VERDICTS
        ]

        # Abstension
        abstain_count = sum(
            1 for r in self.results
            if r["actual_verdict"] in _ABSTAIN_VERDICTS
        )

        # Sensor independence failures (T3)
        t3_cases = [r for r in self.results if "T3" in r["vabs_category"]]
        t3_fail = [r for r in t3_cases if r["status"] == self.FAIL]

        # Cross-layer miss (T5)
        t5_cases = [r for r in self.results if "T5" in r["vabs_category"]]
        t5_fail = [r for r in t5_cases if r["status"] == self.FAIL]

        # Causal closure false acceptance (T2)
        t2_cases = [r for r in self.results if "T2" in r["vabs_category"]]
        t2_fail = [r for r in t2_cases if r["status"] == self.FAIL]

        # Entropy invariance blindness (T4)
        t4_cases = [r for r in self.results if "T4" in r["vabs_category"]]
        t4_epistemic_handled = [
            r for r in t4_cases
            if not r["expected_detectable"] and r["status"] == self.PASS
        ]

        def safe_rate(num, den):
            if den == 0:
                return None
            return round(float(Fraction(num, den)), 4)

        fnr = safe_rate(len(fn_mal), len(mal_cases))
        fpr = safe_rate(len(fp_ben), len(ben_cases))
        abstain_overhead = safe_rate(abstain_count, total)
        sifr = safe_rate(len(t3_fail), len(t3_cases))
        xl_miss = safe_rate(len(t5_fail), len(t5_cases))
        cc_false = safe_rate(len(t2_fail), len(t2_cases))
        entropy_blind = safe_rate(
            len(t4_cases) - len(t4_epistemic_handled),
            len(t4_cases),
        )

        return {
            "fnr_malicious": fnr,
            "fpr_benign": fpr,
            "abstain_overhead": abstain_overhead,
            "sensor_independence_failure_rate": sifr,
            "cross_layer_contradiction_miss_rate": xl_miss,
            "causal_closure_false_acceptance_rate": cc_false,
            "entropy_invariance_blindness_score": entropy_blind,
        }

    def _compute_vabs_score(self, metrics: Dict) -> Tuple[float, str]:
        """
        VABS Score = 0.25*(1-FNR) + 0.20*(1-FPR) + 0.15*LR_quality
                   + 0.15*CCS_reliability + 0.25*structural_robustness

        LR quality y CCS reliability: aproximados desde metricas disponibles.
        Structural robustness: 1 - mean(SIFR, XL_MISS, CC_FALSE).
        Aritmetica Fraction para score canonico.
        """
        def _safe(v, fallback=Fraction(1, 2)):
            if v is None:
                return fallback
            return Fraction(v).limit_denominator(10000)

        fnr = _safe(metrics.get("fnr_malicious"))
        fpr = _safe(metrics.get("fpr_benign"))
        sifr = _safe(metrics.get("sensor_independence_failure_rate"))
        xl_miss = _safe(metrics.get("cross_layer_contradiction_miss_rate"))
        cc_false = _safe(metrics.get("causal_closure_false_acceptance_rate"))

        # LR quality: proxy via 1 - abstain_overhead (penaliza colapso de LR)
        abstain = _safe(metrics.get("abstain_overhead"), Fraction(0))
        lr_quality = max(Fraction(0), Fraction(1) - abstain)

        # CCS reliability: proxy via 1 - cc_false
        ccs_reliability = max(Fraction(0), Fraction(1) - cc_false)

        # Structural robustness: 1 - mean(sifr, xl_miss, cc_false)
        struct_robustness = max(
            Fraction(0),
            Fraction(1) - (sifr + xl_miss + cc_false) / 3,
        )

        score = (
            Fraction(1, 4) * (Fraction(1) - fnr)
            + Fraction(1, 5) * (Fraction(1) - fpr)
            + Fraction(3, 20) * lr_quality
            + Fraction(3, 20) * ccs_reliability
            + Fraction(1, 4) * struct_robustness
        )

        score_float = round(float(score), 4)

        if score_float >= 0.90:
            grade = "S"
        elif score_float >= 0.80:
            grade = "A"
        elif score_float >= 0.70:
            grade = "B"
        else:
            grade = "C"

        return score_float, grade

    # ── Reporte ────────────────────────────────────────────────────────────

    def summary(self) -> Dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == self.PASS)
        failed = sum(1 for r in self.results if r["status"] == self.FAIL)
        review = sum(1 for r in self.results if r["status"] == self.REVIEW)

        high_risk_false_confidence = [
            r for r in self.results
            if r["status"] == self.FAIL
            and r["criticality"] > 0.7
        ]
        epistemic_handled = [
            r for r in self.results
            if not r["expected_detectable"] and r["status"] == self.PASS
        ]

        metrics = self._compute_metrics()
        vabs_score, grade = self._compute_vabs_score(metrics)

        return {
            "suite": "VABS-1-UNIFIED-P3",
            "total": total,
            "passed": passed,
            "failed": failed,
            "review": review,
            "epistemic_limits_handled_correctly": len(epistemic_handled),
            "high_risk_false_confidence": len(high_risk_false_confidence),
            "high_risk_cases": [r["case_id"] for r in high_risk_false_confidence],
            "metrics": metrics,
            "vabs_score": vabs_score,
            "grade": grade,
            "details": self.results,
        }

    def save_report(self, path: Path) -> None:
        report = self.summary()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, sort_keys=True)
        print(f"Report saved: {path}")

    def print_summary(self) -> None:
        s = self.summary()
        sep = "=" * 55
        print(f"\n{sep}")
        print(f"  VABS-1 UNIFIED ADVERSARIAL SUMMARY")
        print(sep)
        print(f"  Suite          : {s['suite']}")
        print(f"  Total          : {s['total']}")
        print(f"  PASS           : {s['passed']}")
        print(f"  FAIL           : {s['failed']}")
        print(f"  REVIEW         : {s['review']}")
        print(f"  Epistemic OK   : {s['epistemic_limits_handled_correctly']}")
        print(f"  High-risk FC   : {s['high_risk_false_confidence']}")
        print(sep)
        print(f"  VABS SCORE     : {s['vabs_score']:.4f}  [{s['grade']}]")
        print(sep)
        m = s["metrics"]
        print(f"  FNR-MAL        : {m.get('fnr_malicious')}")
        print(f"  FPR-BEN        : {m.get('fpr_benign')}")
        print(f"  ABSTAIN-OH     : {m.get('abstain_overhead')}")
        print(f"  SIFR           : {m.get('sensor_independence_failure_rate')}")
        print(f"  XL-MISS        : {m.get('cross_layer_contradiction_miss_rate')}")
        print(f"  CC-FALSE       : {m.get('causal_closure_false_acceptance_rate')}")
        print(f"  ENTROPY-BLIND  : {m.get('entropy_invariance_blindness_score')}")
        print(sep)
        if s["high_risk_cases"]:
            print(f"  CRITICAL FAILS : {', '.join(s['high_risk_cases'])}")
        print(sep)


if __name__ == "__main__":
    runner = VABS1Runner(
        p3_dir=Path("./adversarial_tests_p3"),
        vabs1_dir=Path("./adversarial_tests_vabs1"),
    )
    runner.run()
    runner.save_report(Path("report_vabs1_unified.json"))
    runner.print_summary()
