"""
Test R3-5 — chain_tip_sha256: anchoring the tool_execution_log tail.

Surprise / expectation violated: the v2 tool_execution_log chain (R3-2/A1/A2)
already makes every field of every entry tamper-evident, and prev_hash
linkage already catches an entry deleted, inserted, or reordered in the
MIDDLE of the log (seq_discontinuities + broken_links, exercised in
test_hash_chain_hardening.py::test_deleted_middle_link). But deleting the
LAST N entries of an otherwise-untouched chain leaves it internally
consistent: there is nothing after seq=N to notice N is gone. This is the
same structural gap ChainOfCustody already solved for the sqlite ledger via
checkpoint() (A5/A6 in test_hash_chain_hardening.py) — but the single-bundle
tool_execution_log had no equivalent anchor.

Fix: the producer records chain_tip_sha256 (the entry_hash of the last
entry) as a bundle-level field, sibling to tool_execution_log — outside the
array an attacker would truncate. The verifier recomputes the tip from the
log it is handed and compares it against the declared chain_tip_sha256; a
mismatch means entries were removed or appended after the tip was recorded.

Honest limit (documented, not silently overclaimed — red-team-auditing
epistemic ladder): chain_tip_sha256 alone is a plain SHA-256, recomputable by
any attacker with write access to the bundle, exactly like the per-entry
entry_hash in A3. An attacker who truncates the tail AND rewrites
chain_tip_sha256 to match is invisible under hash-only verification — same
documented limit as test_a5_without_checkpoint_truncation_is_invisible. The
keyed sibling, chain_tip_hmac = HMAC(VIGIA_HMAC_KEY, chain_tip_sha256), closes
that gap the same way entry_hmac closes it for A3: recomputable only by
someone holding the key.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from vigia.core.hash_chain import GENESIS_HASH, build_link, compute_entry_hmac, verify_chain
from vigia.core.tool_log_chain import ToolExecutionLogChain, verify_bundle_tool_log, verify_tool_execution_log

REPO_ROOT = Path(__file__).resolve().parent.parent

KEY = b"k" * 32
OTHER_KEY = b"x" * 32


def _build_chain(n: int, hmac_key=None):
    links = []
    prev = GENESIS_HASH
    for seq in range(1, n + 1):
        link = build_link(seq, prev, {"data": f"evento-{seq}"}, hmac_key=hmac_key)
        links.append(link)
        prev = link.entry_hash
    return links


def _v2_log(n: int = 5, hmac_key=KEY):
    chain = ToolExecutionLogChain(mode="claude_code", hmac_key=hmac_key, use_env_key=False)
    log = [
        chain.append(
            tool=f"tool_{i}", target=f"/evidence/art_{i}",
            result_summary=f"resultado {i}", arguments={"i": i},
        )
        for i in range(1, n + 1)
    ]
    return chain, log


class TestPrimitiveExpectedTip:
    def test_tip_matches_is_valid(self):
        links = _build_chain(5)
        r = verify_chain(links, expected_tip=links[-1].entry_hash)
        assert r.valid
        assert r.tip_checked and not r.tip_mismatch

    def test_tail_truncation_detected_via_expected_tip(self):
        links = _build_chain(5)
        tip = links[-1].entry_hash          # tip recorded BEFORE the attack
        truncated = links[:3]               # attacker deletes the last 2 entries
        r = verify_chain(truncated, expected_tip=tip)
        assert not r.valid
        assert r.tip_checked and r.tip_mismatch
        assert r.actual_tip == truncated[-1].entry_hash
        assert r.expected_tip == tip

    def test_tail_append_detected_via_expected_tip(self):
        links = _build_chain(3)
        tip = links[-1].entry_hash          # tip recorded BEFORE the attack
        extra = build_link(4, tip, {"data": "evento-4-INYECTADO"})
        r = verify_chain(links + [extra], expected_tip=tip)
        assert not r.valid and r.tip_mismatch

    def test_no_expected_tip_means_no_tip_check(self):
        links = _build_chain(5)
        truncated = links[:3]
        r = verify_chain(truncated)          # backward compat: nobody asked
        assert r.valid                      # internally-consistent prefix
        assert not r.tip_checked

    def test_empty_chain_tip_is_genesis(self):
        r = verify_chain([], expected_tip=GENESIS_HASH)
        assert r.valid and r.tip_checked and not r.tip_mismatch

    def test_tip_hmac_matches_is_valid(self):
        links = _build_chain(4, hmac_key=KEY)
        tip = links[-1].entry_hash
        tip_hmac = compute_entry_hmac(KEY, tip)
        r = verify_chain(links, hmac_key=KEY, expected_tip=tip, expected_tip_hmac=tip_hmac)
        assert r.valid and r.tip_hmac_checked and not r.tip_hmac_mismatch

    def test_a8_tip_recompute_without_key_still_invisible(self):
        """Documented limit (parallels test_a5_without_checkpoint_...): a bare
        SHA-256 chain_tip_sha256, rewritten consistently by the attacker after
        truncation, is NOT detectable without a keyed anchor."""
        links = _build_chain(5, hmac_key=KEY)
        truncated = links[:3]
        forged_tip = truncated[-1].entry_hash   # attacker recomputes the tip too
        r = verify_chain(truncated, expected_tip=forged_tip)
        assert r.valid   # hash-only: the forged tip is self-consistent

        # But the attacker cannot forge chain_tip_hmac without the key.
        stale_tip_hmac = compute_entry_hmac(KEY, links[-1].entry_hash)  # from before the attack
        r_keyed = verify_chain(
            truncated, hmac_key=KEY, expected_tip=forged_tip, expected_tip_hmac=stale_tip_hmac,
        )
        assert not r_keyed.valid and r_keyed.tip_hmac_mismatch


class TestToolLogChainTip:
    def test_bundle_fields_exposes_tip_and_hmac(self):
        chain, log = _v2_log(hmac_key=KEY)
        fields = chain.bundle_fields()
        assert fields["chain_tip_sha256"] == chain.tip_hash == log[-1]["entry_hash"]
        assert fields["chain_tip_hmac"] == compute_entry_hmac(KEY, chain.tip_hash)

    def test_bundle_fields_no_hmac_without_key(self):
        chain, _ = _v2_log(hmac_key=None)
        fields = chain.bundle_fields()
        assert fields["chain_tip_sha256"]
        assert "chain_tip_hmac" not in fields

    def test_verify_bundle_tool_log_tip_matches(self):
        chain, log = _v2_log(hmac_key=None)
        bundle = {"tool_execution_log": log, **chain.bundle_fields()}
        report = verify_bundle_tool_log(bundle)
        assert report["valid"]
        assert report["tip_checked"] and not report["tip_mismatch"]

    def test_verify_bundle_tool_log_detects_tail_truncation(self):
        chain, log = _v2_log(n=5, hmac_key=None)
        bundle = {"tool_execution_log": log, **chain.bundle_fields()}
        # Attacker deletes the last two entries but leaves chain_tip_sha256
        # stale (does not know / does not bother to update it).
        bundle["tool_execution_log"] = log[:3]
        report = verify_bundle_tool_log(bundle)
        assert not report["valid"]
        assert report["tip_mismatch"]

    def test_verify_bundle_tool_log_no_tip_is_backward_compatible(self):
        chain, log = _v2_log(hmac_key=None)
        bundle = {"tool_execution_log": log}  # older bundle, no chain_tip_sha256
        report = verify_bundle_tool_log(bundle)
        assert report["valid"]
        assert not report["tip_checked"]
        assert "chain_tip_caveat" in report

    def test_verify_tool_execution_log_expected_tip_threaded(self):
        chain, log = _v2_log(n=4, hmac_key=None)
        tip = chain.tip_hash
        r = verify_tool_execution_log(log, expected_tip=tip)
        assert r.valid and r.tip_checked

        truncated = log[:2]
        r2 = verify_tool_execution_log(truncated, expected_tip=tip)
        assert not r2.valid and r2.tip_mismatch

    def test_v1_legacy_bundle_ignores_tip_check(self):
        # v1 bundles predate chain_tip_sha256; even if present it must not be
        # applied under the v1 legacy verification path.
        import hashlib
        log = []
        prev_summary = None
        for seq in range(1, 3):
            log.append({
                "seq": seq, "timestamp": f"2026-07-02T00:0{seq}:00+00:00",
                "mode": "claude_code", "tool": f"tool_{seq}", "target": f"art_{seq}",
                "result_summary": f"resultado {seq}", "input_hash": "ab" * 32,
                "prev_hash": ("GENESIS" if seq == 1
                              else hashlib.sha256(prev_summary.encode()).hexdigest()),
            })
            prev_summary = f"resultado {seq}"
        bundle = {"tool_execution_log": log, "chain_tip_sha256": "deadbeef" * 8}
        report = verify_bundle_tool_log(bundle)
        assert report["chain_version"] == "1"
        assert report["valid"]  # v1 caveat path, unaffected by the v2-only tip field


class TestFullTruncationAttackEndToEnd:
    """A8 (extends A1-A7 in test_hash_chain_hardening.py): tail truncation of a
    single-bundle tool_execution_log, closed by chain_tip_sha256."""

    def test_a8_caught_when_attacker_forgets_the_tip(self):
        chain, log = _v2_log(n=6, hmac_key=None)
        bundle = {"tool_execution_log": copy.deepcopy(log), **chain.bundle_fields()}
        bundle["tool_execution_log"] = bundle["tool_execution_log"][:4]
        assert not verify_bundle_tool_log(bundle)["valid"]

    def test_a8_middle_deletion_still_caught_without_tip(self):
        # Sanity: R3-5 does not replace existing middle-deletion detection.
        chain, log = _v2_log(n=5, hmac_key=None)
        del log[2]
        r = verify_tool_execution_log(log)
        assert not r.valid


class TestStandaloneVerifierCLI:
    """verify_tool_log.py is a stdlib-only third-party verifier (no vigia
    import) — it must implement the same chain_tip_sha256 check as the
    library copy, exercised here via subprocess like the R3-2 CLI tests."""

    def _bundle_path(self, tmp_path, bundle):
        path = tmp_path / "bundle.json"
        path.write_text(json.dumps(bundle))
        return path

    def _run(self, path):
        return subprocess.run(
            [sys.executable, "verify_tool_log.py", str(path)],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )

    def test_cli_verifies_when_tip_matches(self, tmp_path):
        chain, log = _v2_log(n=4, hmac_key=None)
        bundle = {"tool_execution_log": log, **chain.bundle_fields()}
        r = self._run(self._bundle_path(tmp_path, bundle))
        assert r.returncode == 0, r.stdout
        assert "CHAIN VERIFIED" in r.stdout
        assert "chain_tip_sha256" in r.stdout

    def test_cli_fails_on_tail_truncation(self, tmp_path):
        chain, log = _v2_log(n=5, hmac_key=None)
        bundle = {"tool_execution_log": log[:3], **chain.bundle_fields()}
        r = self._run(self._bundle_path(tmp_path, bundle))
        assert r.returncode == 1, r.stdout
        assert "CHAIN BROKEN" in r.stdout
        assert "chain_tip_sha256" in r.stdout

    def test_cli_notes_absence_of_tip(self, tmp_path):
        chain, log = _v2_log(n=3, hmac_key=None)
        bundle = {"tool_execution_log": log}
        r = self._run(self._bundle_path(tmp_path, bundle))
        assert r.returncode == 0, r.stdout
        assert "Sin chain_tip_sha256" in r.stdout

    def test_cli_keyed_tip_hmac(self, tmp_path):
        chain, log = _v2_log(n=3, hmac_key=KEY)
        bundle = {"tool_execution_log": log, **chain.bundle_fields()}
        path = self._bundle_path(tmp_path, bundle)
        r = subprocess.run(
            [sys.executable, "verify_tool_log.py", str(path),
             "--hmac-key-hex", KEY.hex()],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert r.returncode == 0, r.stdout
        assert "chain_tip_hmac" in r.stdout
