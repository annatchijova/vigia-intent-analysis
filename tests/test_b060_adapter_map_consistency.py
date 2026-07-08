"""
B-060 — adapter map consistency guard (Grupo B / B6).

`vigia/core/forensic_adapter.py` routes every artifact through three parallel
maps keyed by the raw artifact type:

  * `_LAYER_MAP`     art_type -> EvidenceLayer
  * `_ONTOLOGY_MAP`  art_type -> OntologicalLevel
  * `_EVIDENCE_MAP`  art_type -> canonical evidence_type

All three `.get(art_type, DEFAULT)` with a SILENT default (DISK_MFT /
TECHNIQUE / identity). The B-060 defect class: a new type added to one map
but forgotten in another falls through to that silent default with no
signal — a mapping the maintainer never decided. AUDITORIA_MOBILE_WHITELIST
§4 proposed either a single unified `ARTIFACT_TYPE_REGISTRY` or a consistency
test; this is the zero-verdict-risk consistency test.

Contract (see `check_adapter_map_consistency`):
  1. `_LAYER_MAP` and `_ONTOLOGY_MAP` MUST share the exact same key set — they
     are both keyed by the raw art_type category and must move in lockstep.
  2. Every `_LAYER_MAP`/`_ONTOLOGY_MAP` key MUST also be a key of
     `_EVIDENCE_MAP` (a categorized art_type always has an explicit evidence
     mapping, never the identity fallback).
  3. `_EVIDENCE_MAP` MAY legitimately be a superset — the extra keys are
     already-canonical evidence types (identity-mapped, value == key), which
     arrive pre-typed and need no layer/ontology categorization.

Red-first: `check_adapter_map_consistency` did not exist before this fix, so
the import failed. The `test_checker_detects_*` cases are the teeth — they
prove the guard actually catches an injected inconsistency, not just that the
current maps happen to agree.
"""
from __future__ import annotations

import pytest

from vigia.core import forensic_adapter as FA
from vigia.core.forensic_adapter import check_adapter_map_consistency


def test_real_maps_are_consistent():
    """The shipped maps must satisfy the contract — regression guard."""
    violations = check_adapter_map_consistency(
        FA._LAYER_MAP, FA._ONTOLOGY_MAP, FA._EVIDENCE_MAP
    )
    assert violations == [], (
        "forensic_adapter maps diverged — a type is categorized in one map "
        "but silently defaulted in another:\n  " + "\n  ".join(violations)
    )


def test_layer_and_ontology_keys_are_lockstep():
    assert set(FA._LAYER_MAP) == set(FA._ONTOLOGY_MAP)


def test_layer_keys_are_subset_of_evidence():
    assert set(FA._LAYER_MAP) <= set(FA._EVIDENCE_MAP)


def test_evidence_only_keys_are_identity_mapped():
    """The keys EVIDENCE has beyond LAYER/ONTOLOGY are canonical types
    (value == key): they need no layer/ontology categorization."""
    evidence_only = set(FA._EVIDENCE_MAP) - set(FA._LAYER_MAP)
    non_identity = {
        k: FA._EVIDENCE_MAP[k] for k in evidence_only if FA._EVIDENCE_MAP[k] != k
    }
    assert non_identity == {}, (
        "EVIDENCE-only keys that are NOT identity-mapped would be raw "
        f"art_types missing from LAYER/ONTOLOGY: {non_identity}"
    )


def test_checker_detects_layer_ontology_divergence():
    """Teeth: a type in LAYER but missing from ONTOLOGY must be flagged."""
    layer = dict(FA._LAYER_MAP)
    ontology = dict(FA._ONTOLOGY_MAP)
    layer["brand_new_type"] = next(iter(FA._LAYER_MAP.values()))
    # deliberately NOT added to ontology
    violations = check_adapter_map_consistency(layer, ontology, FA._EVIDENCE_MAP)
    assert any("brand_new_type" in v for v in violations)


def test_checker_detects_missing_evidence_mapping():
    """Teeth: a categorized type absent from EVIDENCE must be flagged."""
    layer = dict(FA._LAYER_MAP)
    ontology = dict(FA._ONTOLOGY_MAP)
    val_layer = next(iter(FA._LAYER_MAP.values()))
    val_ont = next(iter(FA._ONTOLOGY_MAP.values()))
    layer["orphan_type"] = val_layer
    ontology["orphan_type"] = val_ont
    # present in LAYER+ONTOLOGY but NOT in EVIDENCE -> silent identity fallback
    violations = check_adapter_map_consistency(layer, ontology, FA._EVIDENCE_MAP)
    assert any("orphan_type" in v for v in violations)
