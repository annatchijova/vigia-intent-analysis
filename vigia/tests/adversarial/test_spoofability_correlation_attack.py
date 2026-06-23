# vigia/tests/adversarial/test_spoofability_correlation_attack.py
#
# Test P0/P1 — Spoofability Correlation Attack ("inverse credibility anchor")
# =============================================================================
# Source: advanced test coverage audit, gap T-5.
# Grounded directly in vigia/tools/caie.py — CONFIRM against LaBestia before
# merging if caie.py has changed since this was written.
#
# Hypothesis under test (T-5):
#   Artifact A (memory_process, intrinsic spoofability 0.15) claims a process
#   is legitimate.
#   Artifact B (log_entry, intrinsic spoofability 0.85) claims that same
#   process connected to a known C2 IP.
#   Does the spoofability differential (adjusted_score = raw_score ×
#   (1 - effective_spoofability) × weight × base_trust) let VIGIA discard B,
#   and with it, the real attack?
#
# Reading of caie.py:
#   There is a structural Golden Rule — fracture_type "LOG_VS_MEMORY" —
#   designed exactly for this scenario: "the fracture itself is evidence of
#   fabrication". When it fires, it forces structural_verdict=MALICE, which
#   DOMINATES the probabilistic composite (see _STRUCTURAL_MALICE_TYPES and
#   the rank-based max() at the end of evaluate()).
#
#   BUT the rule only fires if:
#     log_verdicts  = {a.metadata.get("verdict") for a in logs} - {None, "NOISE"}
#     tech_verdicts = {a.metadata.get("verdict") for a in technical}
#     if log_verdicts and "NOISE" in tech_verdicts and len(tech_verdicts) == 1: ...
#
#   I.e. it requires every artifact to carry an explicit metadata["verdict"]
#   field with exact values. If artifacts are built without that field (raw
#   Artifact() construction, or any upstream tool that doesn't emit it for
#   "clean" findings), tech_verdicts contains {None} instead of {"NOISE"},
#   the rule does NOT fire, and the case falls through to the pure
#   probabilistic Noisy-OR — where the log's 0.85 spoofability CAN suppress
#   its contribution enough that the final verdict never clears NOISE.
#
# This file exercises BOTH paths with the SAME raw_score and narrative,
# varying only the presence of metadata["verdict"].
#
# Run:
#   pytest vigia/tests/adversarial/test_spoofability_correlation_attack.py -v
#
# If test_red_team_anchor_bypass fails: T-5 is empirically confirmed as an
# exploitable gap, not just a theoretical hypothesis. That is a Daubert-
# relevant finding for KNOWN_LIMITATIONS.md, not a bug to hide.

import json
from pathlib import Path
from typing import Dict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vigia.tools.caie import CrossArtifactIncongruenceEngine, Artifact


def _acq_strong() -> dict:
    """
    Full forensic acquisition metadata (NIST SP 800-86 / RFC 3227).
    Guarantees acquisition_assurance = STRONG (9/10) on both artifacts, so
    the comparison between scenario A and B is not contaminated by
    base_trust degradation from missing chain-of-custody fields — the only
    variable that changes between scenarios is metadata["verdict"].
    """
    return {
        "acquisition_tool": "volatility3",
        "acquisition_hash": "sha256:" + "a" * 64,
        "acquisition_timestamp": "2026-06-20T03:00:00Z",
        "examiner_id": "vigia_test_harness",
        "write_blocker_used": True,
    }


class SpoofabilityCorrelationAttackTest:
    """
    T-5: can an attacker use a structurally irrefutable artifact (memory,
    low spoofability) as an innocence "anchor" to neutralize a trivially
    forgeable artifact (log, high spoofability) that carries the actual
    evidence of compromise (connection to a C2 IP)?
    """

    # ── Base artifact construction (shared by both scenarios) ─────────────

    def _memory_artifact(self, with_verdict: bool) -> Artifact:
        """
        Volatility on the process: normal memory behavior, no hooks, no
        injection. raw_score is deliberately low — this is the EXCULPATORY
        artifact, structurally hard to forge.
        """
        meta = _acq_strong()
        meta.update({"pid": 4521, "process_name": "svchost.exe"})
        if with_verdict:
            meta["verdict"] = "NOISE"
        return Artifact(
            source_tool="volatility3",
            evidence_type="memory_process",
            raw_score=0.10,
            description="svchost.exe process shows no hooks or injection in memory",
            metadata=meta,
        )

    def _malicious_log_artifact(self, with_verdict: bool) -> Artifact:
        """
        SIEM/firewall log: the SAME pid connected to a known C2 IP.
        raw_score is high — this is the REAL evidence of the attack, in the
        artifact that is easiest to forge (or, in this case, easiest to
        SILENTLY DISCOUNT if nobody attaches an explicit verdict to it).
        """
        meta = _acq_strong()
        meta.update({"pid": 4521, "dst_ip": "203.0.113.77", "dst_port": 443})
        if with_verdict:
            meta["verdict"] = "MALICE"
        return Artifact(
            source_tool="siem_export",
            evidence_type="log_entry",
            raw_score=0.95,
            description="svchost.exe (pid 4521) connected to known C2 IP 203.0.113.77:443",
            metadata=meta,
        )

    # ── Scenario A: metadata["verdict"] convention is followed ────────────

    def test_metadata_convention_present_triggers_golden_rule(self) -> Dict:
        """
        If both artifacts carry explicit metadata['verdict'] consistent with
        what the real upstream tool would produce (log says MALICE, memory
        says NOISE), the LOG_VS_MEMORY Golden Rule must fire and force
        MALICE, regardless of how much the probabilistic Noisy-OR depresses
        the log's contribution. This is the designed defense working as
        documented in the code.
        """
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        engine.add_artifact(self._memory_artifact(with_verdict=True))
        engine.add_artifact(self._malicious_log_artifact(with_verdict=True))
        res = engine.evaluate()

        fracture_types = [f.get("type") if isinstance(f, dict) else getattr(f, "fracture_type", None)
                           for f in res.get("fractures", [])]
        has_log_vs_memory = "LOG_VS_MEMORY" in fracture_types
        verdict = res.get("verdict")

        passed = has_log_vs_memory and verdict == "MALICE"

        return {
            "test": "metadata_convention_present",
            "fracture_types": fracture_types,
            "has_log_vs_memory": has_log_vs_memory,
            "composite_score": res.get("composite_score", res.get("probabilistic_score")),
            "verdict": verdict,
            "status": "PASS" if passed else "FAIL",
            "detail": (
                "With explicit metadata['verdict'], LOG_VS_MEMORY must fire "
                "and force MALICE despite the log's high spoofability."
            ),
        }

    # ── Scenario B: the real attack — no explicit metadata['verdict'] ─────

    def test_red_team_anchor_bypass(self) -> Dict:
        """
        SAME raw_score, SAME narrative, SAME C2 evidence — the only
        difference is that neither artifact carries metadata['verdict'].
        This is exactly how artifacts are built across much of the real
        pipeline (tools that don't emit an explicit 'verdict' field for
        negative findings, or direct Artifact() ingestion).

        If this rule doesn't fire, the case falls to pure Noisy-OR, where
        spoofability=0.85 on the log can depress its adjusted_score enough
        that the final verdict collapses to NOISE — despite containing a
        high-severity IoC (connection to a known C2).

        This is NOT xfail: it is a hard assertion. If it passes, T-5 is not
        exploitable under the current configuration. If it fails, T-5 is
        confirmed and must be documented in KNOWN_LIMITATIONS.md as a real
        finding, not a hypothesis.
        """
        engine = CrossArtifactIncongruenceEngine()
        engine.reset()
        engine.add_artifact(self._memory_artifact(with_verdict=False))
        engine.add_artifact(self._malicious_log_artifact(with_verdict=False))
        res = engine.evaluate()

        fracture_types = [f.get("type") if isinstance(f, dict) else getattr(f, "fracture_type", None)
                           for f in res.get("fractures", [])]
        has_log_vs_memory = "LOG_VS_MEMORY" in fracture_types
        verdict = res.get("verdict")
        composite = res.get("composite_score", res.get("probabilistic_score"))

        # Minimum defensible bar: a high-severity IoC (confirmed connection
        # to a known C2) should never collapse to NOISE, whether or not a
        # competing exculpatory artifact is present. NOISE means "nothing to
        # see here", which is forensically and narratively false in this case.
        passed = verdict != "NOISE"

        return {
            "test": "red_team_anchor_bypass",
            "fracture_types": fracture_types,
            "has_log_vs_memory": has_log_vs_memory,
            "composite_score": composite,
            "verdict": verdict,
            "status": "PASS" if passed else "FAIL_T5_CONFIRMED",
            "detail": (
                "Without metadata['verdict'], LOG_VS_MEMORY does not fire. "
                "The C2 IoC should not degrade to NOISE on spoofability alone."
            ),
        }

    # ── Orchestration ───────────────────────────────────────────────────────

    def run_all(self):
        self.results = [
            self.test_metadata_convention_present_triggers_golden_rule(),
            self.test_red_team_anchor_bypass(),
        ]
        return self.results

    def summary(self) -> Dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        return {
            "suite": "Spoofability_Correlation_Attack_T5",
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "status": "PASS" if passed == total else "FAIL",
            "details": self.results,
        }

    def save(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.summary(), f, indent=2, ensure_ascii=False, sort_keys=True)
        print(f"Report saved to {path}")


# ── pytest entrypoints ──────────────────────────────────────────────────────

def test_metadata_convention_present_triggers_golden_rule():
    """The LOG_VS_MEMORY defense works when the metadata convention is followed."""
    t = SpoofabilityCorrelationAttackTest()
    r = t.test_metadata_convention_present_triggers_golden_rule()
    assert r["status"] == "PASS", (
        f"LOG_VS_MEMORY did not force MALICE with explicit metadata['verdict']. "
        f"fractures={r['fracture_types']} verdict={r['verdict']}"
    )


def test_red_team_anchor_bypass():
    """
    T-5 — hard assertion, not xfail. See
    SpoofabilityCorrelationAttackTest.test_red_team_anchor_bypass docstring
    for the full reasoning.
    """
    t = SpoofabilityCorrelationAttackTest()
    r = t.test_red_team_anchor_bypass()
    assert r["status"] == "PASS", (
        f"T-5 CONFIRMED: the C2 IoC (raw_score=0.95, log_entry) collapsed to "
        f"verdict={r['verdict']} (composite={r['composite_score']}) when "
        f"competing with a low-spoofability exculpatory artifact lacking "
        f"explicit metadata['verdict']. fractures detected: {r['fracture_types']}. "
        f"This confirms the 'inverse credibility anchor' hypothesis from the "
        f"coverage audit (gap T-5)."
    )


# ── Standalone entrypoint ───────────────────────────────────────────────────

if __name__ == "__main__":
    t = SpoofabilityCorrelationAttackTest()
    t.run_all()
    s = t.summary()
    sep = "=" * 60
    print(f"\n{sep}")
    print("SPOOFABILITY CORRELATION ATTACK — T-5 DIAGNOSTIC")
    print(sep)
    for d in s["details"]:
        print(f"  [{d['status']}] {d['test']}")
        print(f"      verdict={d['verdict']}  composite={d['composite_score']}")
        print(f"      fractures={d['fracture_types']}")
    print(sep)
    print(f"Total: {s['total']}  PASS: {s['passed']}  FAIL: {s['failed']}")
    print(sep)
    t.save(Path("report_spoofability_correlation_attack.json"))
