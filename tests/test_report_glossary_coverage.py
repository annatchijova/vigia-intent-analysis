"""vigia.report.glossary and vigia.report.picerl — coverage and lockstep.

* Every verdict value, schema name, custody field name and Peircean / status /
  confidence enum the renderers can emit has a glossary entry with non-empty,
  non-identical EN and ES explanations.
* PICERL labels reproduced in ``vigia/report/picerl.py`` (kept import-free on
  purpose) match ``vigia.sift.sans_phase.SANSPhase.label`` exactly.
* ``GlossaryCollector`` renders only the terms that were marked, sorted.
"""
from __future__ import annotations

import re

from vigia.report import picerl
from vigia.report.glossary import GLOSSARY, GlossaryCollector, is_term

REQUIRED_TERMS = {
    # verdict scale + exit label
    "NOISE", "SUSPICION", "INTENT", "MALICE", "ABSTAIN", "ERROR",
    # families
    "ebs_v1", "agent_audit", "mcp_investigation", "unknown",
    # Peirce, status, confidence
    "Firstness", "Secondness", "Thirdness",
    "CONFIRMED", "INFERRED", "REFUTED", "HIGH", "MEDIUM", "LOW",
    # custody fields emitted by adapter.custody_fields
    "bundle_hash", "analysis_fingerprint", "graph_hash", "decision_hash", "policy_hash",
    "engine_attestation_hash", "ecl_hash", "sealed_at",
    "evidence_sha256", "runtime_fingerprint", "analysis_timestamp",
    "bundle_sha256", "primary_evidence_sha256", "evidence_hash", "chain_tip_sha256",
    "timestamp_sealed",
    # process records and gates
    "audit_trail", "tool_execution_log", "chain_version", "refutation_gate_log",
    "devil_advocate", "sans_compliance", "sans_phase", "agent_verdict", "best_hypothesis",
    # frameworks
    "PICERL", "Daubert", "Carnegie", "CAIE", "MITRE ATT&CK", "Fraction",
}

_EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")


def test_required_terms_present():
    missing = sorted(REQUIRED_TERMS - set(GLOSSARY))
    assert not missing, f"glossary lacks: {missing}"


def test_every_entry_bilingual_and_distinct():
    for term, entry in GLOSSARY.items():
        assert entry.term == term
        assert entry.en.strip() and entry.es.strip(), term
        assert entry.en != entry.es, f"{term}: EN and ES explanations are identical"
        assert not _EMOJI.search(entry.en + entry.es), term
        for ref in entry.see_also:
            assert ref in GLOSSARY, f"{term} see_also -> undefined {ref}"


def test_verdict_tokens_never_translated_in_es_explanations():
    for bad in ("RUIDO", "SOSPECHA", "MALICIA", "ABSTENCIÓN"):
        for term, entry in GLOSSARY.items():
            assert bad not in entry.es, f"{term}: translated sealed token in ES"


def test_collector_renders_only_marked_terms_sorted():
    c = GlossaryCollector()
    c.mark("Thirdness", "NOISE", "not_a_term", "Firstness")
    c.mark_verdict("MALICE")
    c.mark_verdict("MALICIOUS_INTENT_DETECTED")   # hypothesis label, not on the scale
    assert c.used() == ["Firstness", "MALICE", "NOISE", "Thirdness"]
    rows_en = c.rows("en")
    rows_es = c.rows("es")
    assert [r[0] for r in rows_en] == c.used()
    assert rows_en[1][1] == GLOSSARY["MALICE"].en + " (`devil_advocate`)"
    assert rows_es[1][1].startswith(GLOSSARY["MALICE"].es)
    assert is_term("Daubert") and not is_term("daubert")


def test_picerl_labels_match_sans_phase_enum():
    from vigia.sift.sans_phase import SANSPhase

    expected = [(p.name.lower(), p.label) for p in SANSPhase]
    assert list(picerl.PHASES) == expected


def test_picerl_rows_localized_in_both_languages():
    en = picerl.phase_rows("en")
    es = picerl.phase_rows("es")
    assert [r[0] for r in en] == [r[0] for r in es] == [p[1] for p in picerl.PHASES]
    assert all(r[1] for r in en) and all(r[1] for r in es)
    assert [r[1] for r in en] != [r[1] for r in es]
