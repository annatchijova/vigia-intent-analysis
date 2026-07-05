"""
tests/test_entanglement_groundtruth.py
======================================
Ground-truth tests for vigia/core/entanglement.py (was 0% covered).

entanglement.py detects "forgery factories": batches of documents that look
distinct but share a common production matrix. Its two mathematically exact
primitives are ideal ground-truth targets:

  * NGramFingerprint.jaccard_similarity — set-theoretic Jaccard index over
    char-bigram / word-trigram / sentence-hash sets, plus a fixed-weight
    composite (0.2*char + 0.5*word + 0.3*sentence). Jaccard has one correct
    value per input pair, so a regression cannot hide behind "looks plausible".
  * EntanglementReport.to_caie_fractures — deterministic fracture severities
    with documented caps and MITRE TTP tags.

Most tests here PASS and pin the correct behavior. One class
(TestIdenticalDocumentCollapse) currently FAILS on purpose: it documents a real
chain-of-custody defect found while writing these tests, where two byte-identical
documents in a batch are silently collapsed to a single analyzed unit while the
report still claims document_count == 2. It is left failing — not xfail'd — so the
defect stays visible until fixed. See its docstring for the full analysis.
"""
from __future__ import annotations

import uuid

import pytest

from vigia.core.entanglement import (
    NGramFingerprint,
    PhysicalKeySignature,
    ForcedVarietyProfile,
    EntanglementReport,
    EntanglementEngine,
    PHYSICAL_KEY_MIN_DOCS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fp(char=(), word=(), sent=(), doc_hash="h"):
    """Build an NGramFingerprint from plain iterables of set members."""
    return NGramFingerprint(
        doc_hash=doc_hash,
        char_bigrams=frozenset(char),
        word_trigrams=frozenset(word),
        sentence_hashes=frozenset(sent),
    )


def _write(dirpath, name, text):
    p = dirpath / name
    p.write_text(text, encoding="utf-8")
    return str(p)


# ---------------------------------------------------------------------------
# NGramFingerprint.jaccard_similarity — set-theoretic Jaccard, closed form
# ---------------------------------------------------------------------------

class TestNGramJaccardGroundTruth:
    def test_identical_fingerprint_is_all_ones(self):
        # J(A, A) = |A & A| / |A | A| = |A| / |A| = 1 for every non-empty set.
        fp = _fp(char={"ab", "bc"}, word={"x_y_z"}, sent={"s1"})
        sims = fp.jaccard_similarity(fp)
        assert sims["char_bigram"] == 1.0
        assert sims["word_trigram"] == 1.0
        assert sims["sentence"] == 1.0
        assert sims["composite"] == 1.0

    def test_disjoint_fingerprints_are_all_zero(self):
        # Disjoint sets: intersection empty -> Jaccard 0 on every channel.
        a = _fp(char={"ab", "bc"}, word={"x_y_z"}, sent={"s1"})
        b = _fp(char={"pq", "qr"}, word={"m_n_o"}, sent={"s2"})
        sims = a.jaccard_similarity(b)
        assert sims["char_bigram"] == 0.0
        assert sims["word_trigram"] == 0.0
        assert sims["sentence"] == 0.0
        assert sims["composite"] == 0.0

    def test_partial_char_overlap_is_one_third(self):
        # {ab,bc} vs {bc,cd}: intersection {bc} (1), union {ab,bc,cd} (3) -> 1/3.
        a = _fp(char={"ab", "bc"})
        b = _fp(char={"bc", "cd"})
        sims = a.jaccard_similarity(b)
        assert sims["char_bigram"] == pytest.approx(1 / 3, abs=1e-4)
        # char-only overlap, weighted 0.2 in composite: (1/3)*0.2 = 0.0667.
        assert sims["composite"] == pytest.approx((1 / 3) * 0.2, abs=1e-4)

    def test_partial_word_overlap_is_one_half(self):
        # {t1,t2,t3} vs {t2,t3,t4}: intersection 2, union 4 -> 0.5.
        a = _fp(word={"t1", "t2", "t3"})
        b = _fp(word={"t2", "t3", "t4"})
        sims = a.jaccard_similarity(b)
        assert sims["word_trigram"] == pytest.approx(0.5, abs=1e-4)
        # word channel weighted 0.5: 0.5 * 0.5 = 0.25.
        assert sims["composite"] == pytest.approx(0.25, abs=1e-4)

    def test_two_empty_fingerprints_are_zero_not_nan(self):
        # Guard clause: union size 0 must return 0.0, never a ZeroDivisionError / NaN.
        e = _fp()
        sims = e.jaccard_similarity(e)
        assert sims["char_bigram"] == 0.0
        assert sims["word_trigram"] == 0.0
        assert sims["sentence"] == 0.0
        assert sims["composite"] == 0.0

    def test_composite_weights_sum_to_one(self):
        # Each channel identical in isolation contributes exactly its weight.
        char_only = _fp(char={"ab"})
        assert char_only.jaccard_similarity(char_only)["composite"] == pytest.approx(0.2, abs=1e-4)
        word_only = _fp(word={"x_y_z"})
        assert word_only.jaccard_similarity(word_only)["composite"] == pytest.approx(0.5, abs=1e-4)
        sent_only = _fp(sent={"s1"})
        assert sent_only.jaccard_similarity(sent_only)["composite"] == pytest.approx(0.3, abs=1e-4)

    def test_symmetry(self):
        # Jaccard is symmetric: J(A,B) == J(B,A) on every channel.
        a = _fp(char={"ab", "bc", "cd"}, word={"t1", "t2"}, sent={"s1"})
        b = _fp(char={"bc", "cd", "de"}, word={"t2", "t3"}, sent={"s2"})
        assert a.jaccard_similarity(b) == b.jaccard_similarity(a)

    def test_results_rounded_to_four_decimals(self):
        # Module rounds each channel to 4 decimals; 1/3 -> 0.3333.
        a = _fp(char={"ab", "bc"})
        b = _fp(char={"bc", "cd"})
        assert a.jaccard_similarity(b)["char_bigram"] == 0.3333


# ---------------------------------------------------------------------------
# PhysicalKeySignature — doc_count and factory threshold (>= 3 docs)
# ---------------------------------------------------------------------------

class TestPhysicalKeySignature:
    def test_doc_count_matches_affected_docs(self):
        sig = PhysicalKeySignature("pat", "ctx", ["d1", "d2"], {})
        assert sig.doc_count == 2

    def test_below_threshold_is_not_factory(self):
        # Two docs < PHYSICAL_KEY_MIN_DOCS (3) -> not a factory signature.
        sig = PhysicalKeySignature("pat", "ctx", ["d1", "d2"], {})
        assert sig.is_factory_signature is False

    def test_at_threshold_is_factory(self):
        assert PHYSICAL_KEY_MIN_DOCS == 3
        sig = PhysicalKeySignature("pat", "ctx", ["d1", "d2", "d3"], {})
        assert sig.doc_count == 3
        assert sig.is_factory_signature is True


# ---------------------------------------------------------------------------
# EntanglementReport.to_caie_fractures — deterministic fracture emission
# ---------------------------------------------------------------------------

def _report(**over):
    base = dict(
        batch_id="B",
        document_count=2,
        entanglement_matrix={},
        identical_sequences=[],
        physical_key_signatures=[],
        forced_variety_anomalies=[],
        is_factory_production=False,
        estimated_operator_count=1,
        confidence=0.0,
    )
    base.update(over)
    return EntanglementReport(**base)


class TestToCaieFractures:
    def test_clean_report_emits_no_fractures(self):
        assert _report().to_caie_fractures() == []

    def test_factory_fracture_uses_confidence_as_severity(self):
        r = _report(is_factory_production=True, confidence=0.8, estimated_operator_count=3)
        fr = [f for f in r.to_caie_fractures() if f["type"] == "FACTORY_PRODUCTION_DETECTED"]
        assert len(fr) == 1
        assert fr[0]["severity"] == 0.8
        assert fr[0]["estimated_operators"] == 3
        assert fr[0]["mitre_ttp"] == "T1585"

    def test_identical_sequence_severity_scales_and_caps(self):
        # severity = min(0.95, n * 0.2).
        r1 = _report(identical_sequences=[{"hash": "a"}])
        f1 = [f for f in r1.to_caie_fractures() if f["type"] == "IDENTICAL_SEQUENCES_CROSS_DOCUMENT"][0]
        assert f1["severity"] == pytest.approx(0.2)
        assert f1["count"] == 1
        assert f1["mitre_ttp"] == "T1036.005"
        # 6 sequences would be 1.2 -> capped at 0.95.
        r6 = _report(identical_sequences=[{"hash": str(i)} for i in range(6)])
        f6 = [f for f in r6.to_caie_fractures() if f["type"] == "IDENTICAL_SEQUENCES_CROSS_DOCUMENT"][0]
        assert f6["severity"] == 0.95

    def test_physical_key_fracture_counts_only_factory_signatures(self):
        weak = PhysicalKeySignature("p", "c", ["d1", "d2"], {})          # doc_count 2, not factory
        strong = PhysicalKeySignature("p", "c", ["d1", "d2", "d3"], {})  # doc_count 3, factory
        # Only the weak signature present -> no PHYSICAL_KEY fracture at all.
        r_weak = _report(physical_key_signatures=[weak])
        assert not any(f["type"] == "PHYSICAL_KEY_SIGNATURE_MATCH" for f in r_weak.to_caie_fractures())
        # One strong signature -> severity min(0.90, 1 * 0.3) = 0.3.
        r_strong = _report(physical_key_signatures=[weak, strong])
        fr = [f for f in r_strong.to_caie_fractures() if f["type"] == "PHYSICAL_KEY_SIGNATURE_MATCH"]
        assert len(fr) == 1
        assert fr[0]["severity"] == pytest.approx(0.3)
        assert fr[0]["signatures_found"] == 1
        assert fr[0]["mitre_ttp"] == "T1585.001"

    def test_physical_key_severity_caps_at_090(self):
        strong = [PhysicalKeySignature("p", "c", ["a", "b", "c"], {}) for _ in range(4)]
        r = _report(physical_key_signatures=strong)
        fr = [f for f in r.to_caie_fractures() if f["type"] == "PHYSICAL_KEY_SIGNATURE_MATCH"][0]
        # 4 * 0.3 = 1.2 -> capped 0.90.
        assert fr["severity"] == 0.90


# ---------------------------------------------------------------------------
# EntanglementEngine.analyze_batch — end-to-end on real text files
# ---------------------------------------------------------------------------

class TestEngineAnalyzeBatch:
    def test_single_document_has_empty_matrix(self, tmp_path):
        # One document -> no pairs -> empty entanglement matrix, no factory.
        p = _write(tmp_path, "solo.txt", "The quick brown fox jumps over the lazy dog. " * 20)
        r = EntanglementEngine().analyze_batch([p], batch_id="SOLO-" + uuid.uuid4().hex[:8])
        assert r.document_count == 1
        assert r.entanglement_matrix == {}
        assert r.is_factory_production is False
        assert r.confidence == 0.0

    def test_two_unrelated_documents_are_not_factory(self, tmp_path):
        # Distinct topics -> low composite similarity, not flagged as a factory.
        p1 = _write(tmp_path, "u1.txt", "The quick brown fox jumps over the lazy dog. " * 20)
        p2 = _write(tmp_path, "u2.txt", "Mountains rivers valleys glaciers and open skies everywhere. " * 20)
        r = EntanglementEngine().analyze_batch([p1, p2], batch_id="UNREL-" + uuid.uuid4().hex[:8])
        # Two distinct hashes -> matrix stores both directions (2 entries).
        assert len(r.entanglement_matrix) == 2
        for sims in r.entanglement_matrix.values():
            assert sims["composite"] < 0.15  # below ENTANGLEMENT_THRESHOLD
        assert r.is_factory_production is False

    def test_matrix_composite_matches_jaccard_of_fingerprints(self, tmp_path):
        # The matrix value for a pair must equal the direct jaccard_similarity
        # of the two fingerprints (no hidden transform in the aggregation path).
        p1 = _write(tmp_path, "m1.txt", "Alpha beta gamma delta epsilon zeta eta theta iota. " * 10)
        p2 = _write(tmp_path, "m2.txt", "Mu nu xi omicron pi rho sigma tau upsilon phi. " * 10)
        eng = EntanglementEngine()
        # Recompute the two fingerprints the same way the engine does.
        _, _, fp1, _ = eng._process_document(p1)
        _, _, fp2, _ = eng._process_document(p2)
        expected = fp1.jaccard_similarity(fp2)
        r = eng.analyze_batch([p1, p2], batch_id="MATCH-" + uuid.uuid4().hex[:8])
        key = (fp1.doc_hash, fp2.doc_hash)
        assert key in r.entanglement_matrix
        assert r.entanglement_matrix[key] == expected

    def test_shared_block_detected_as_identical_sequence(self, tmp_path):
        # Two DISTINCT documents (different tails -> different hashes) that share a
        # long verbatim block must surface as a cross-document identical sequence.
        shared = " ".join(
            "alpha beta gamma delta epsilon zeta eta theta" for _ in range(8)
        )
        p1 = _write(tmp_path, "s1.txt", shared + " unique tail one two three four five six seven")
        p2 = _write(tmp_path, "s2.txt", shared + " different close nine ten eleven twelve thirteen")
        r = EntanglementEngine().analyze_batch([p1, p2], batch_id="SHARE-" + uuid.uuid4().hex[:8])
        assert len(r.identical_sequences) >= 1
        seq = r.identical_sequences[0]
        assert seq["length"] == 30
        # The shared sequence must span exactly the two distinct documents.
        assert len(set(seq["documents"])) == 2

    def test_query_cross_linked_unknown_hash_is_empty(self, tmp_path):
        # No factory link recorded for a random hash -> empty result, no error.
        assert EntanglementEngine().query_cross_linked("deadbeefdeadbeef") == []


# ---------------------------------------------------------------------------
# REGRESSION GUARD — BUG-ENT-001, fixed with keep-both semantics (see docstring)
# ---------------------------------------------------------------------------

class TestIdenticalDocumentCollapse:
    """
    BUG-ENT-001 (FIXED, keep-both) — byte-identical documents collapsed,
    breaking document accounting. This class is now the regression guard.

    analyze_batch() keyed its per-document state (fingerprints, texts,
    errors_by_doc) by `doc_hash = sha256(text)[:16]`. Two byte-identical inputs
    therefore shared one key and silently overwrote each other in those dicts,
    while `document_count` was set from `len(document_paths)` (== 2). The result:

      * entanglement_matrix is EMPTY (only one fingerprint key survives, so
        _calc_entanglement_matrix produces no pairs);
      * is_factory_production is False with confidence 0.0;
      * _persist_entanglement writes ONE row for a report that claims two docs.

    This is a false negative on the module's strongest possible signal — a forgery
    factory that emits a template verbatim twice is exactly what this engine is
    built to catch — and, more concretely, an internal accounting contradiction:
    a forensic report states document_count == 2 while only one document is
    actually analyzed and persisted. Under any interpretation this is wrong: if
    de-duplication were intended, document_count should be 1; if not, the second
    document must contribute a distinct analyzed unit. It cannot be both.

    Fix applied (keep-both semantics, maintainer decision D2): a duplicate
    content hash gets an ordinal in-memory suffix ("hash#2") so the second
    document survives as a distinct analyzed unit, while the PERSISTED doc_hash
    column keeps the pure content hash taken from fingerprint.doc_hash — two
    byte-identical documents produce two rows with the same content hash, which
    is the forensic truth. "#" is outside the hex alphabet, so a suffixed id
    can never collide with a real hash; suffix order follows input order, so
    the result stays deterministic.

    These tests now pin the keep-both contract: full accounting (rows ==
    document_count), the identical pair visible in the matrix at composite 1.0,
    factory detection firing on a verbatim duplicate, and the DB column staying
    a pure content hash.
    """

    def test_identical_documents_are_accounted_for(self, tmp_path):
        text = "The quick brown fox jumps over the lazy dog. " * 20
        p1 = _write(tmp_path, "id1.txt", text)
        p2 = _write(tmp_path, "id2.txt", text)  # byte-identical
        batch_id = "COLLAPSE-" + uuid.uuid4().hex[:8]

        eng = EntanglementEngine()
        report = eng.analyze_batch([p1, p2], batch_id=batch_id)

        # The report claims two documents...
        assert report.document_count == 2

        # ...so exactly two documents must have been analyzed and persisted.
        with eng.db.connection() as conn:
            rows = conn.execute(
                "SELECT doc_hash FROM entanglement_analysis WHERE batch_id = ?",
                (batch_id,),
            ).fetchall()
        hashes = [dict(r)["doc_hash"] for r in rows]
        assert len(hashes) == report.document_count, (
            f"document_count={report.document_count} but only {len(hashes)} "
            f"row(s) persisted: byte-identical documents collapse on doc_hash, "
            f"so the second document is silently dropped (BUG-ENT-001)."
        )

        # DB contract: the persisted doc_hash is the pure content hash (16 hex
        # chars, never an in-memory suffixed id), identical for identical docs.
        assert all(len(h) == 16 and "#" not in h for h in hashes)
        assert hashes[0] == hashes[1]

    def test_identical_pair_is_detected_as_entangled(self, tmp_path):
        # Keep-both semantics: a verbatim duplicate is the strongest possible
        # entanglement signal and must be DETECTED, not collapsed away.
        text = "The quick brown fox jumps over the lazy dog. " * 20
        p1 = _write(tmp_path, "dup1.txt", text)
        p2 = _write(tmp_path, "dup2.txt", text)

        report = EntanglementEngine().analyze_batch(
            [p1, p2], batch_id="KEEPBOTH-" + uuid.uuid4().hex[:8]
        )

        # The pair appears in the matrix with a perfect composite score.
        assert report.entanglement_matrix, "identical pair missing from matrix"
        assert all(
            sims["composite"] == pytest.approx(1.0)
            for sims in report.entanglement_matrix.values()
        )
        # Verbatim shared sequences span both analyzed units.
        assert report.identical_sequences
        # A verbatim duplicate batch is factory production by definition.
        assert report.is_factory_production is True
