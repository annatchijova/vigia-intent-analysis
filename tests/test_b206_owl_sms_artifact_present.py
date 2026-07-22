"""B-206: the OWL-NEXUS5 case JSON must carry the SMS L-041 references.

The case's own legacy taxonomy had no ``sms`` entry, and the coordination SMS
that L-041 documents ("Sarah, the delivery is today 7 tonight the
confirmation will come later through pidgin", from evidence/owl-2019-nexus5-
quick/Agent Data/mmssms.db, sms._id=6/5) had never been added to
data/cases/OWL-NEXUS5-CASE.json's 20 artifacts. Fixing the semantic-extractor
gap or the historical NOISE bug could never surface this specific message
because it was simply absent from the file Mode 1 reads. This guards both
the taxonomy mapping and the artifact's presence so neither regresses.
"""

from __future__ import annotations

import json
from pathlib import Path

from vigia.pipeline.vigia_integration_bridge import _LEGACY_TYPE_TO_EVIDENCE, normalize_case_schema

REPO = Path(__file__).resolve().parent.parent
CASE_PATH = REPO / "data" / "cases" / "OWL-NEXUS5-CASE.json"


class TestLegacySmsTaxonomy:
    def test_sms_legacy_type_maps_to_canonical_sms(self):
        # "sms" already has its own CAIE evidence profile (carrier-CDR
        # correlatable, distinct spoofability from an app chat DB) — must not
        # collapse into "chat_message" or the generic "default" fallback.
        assert _LEGACY_TYPE_TO_EVIDENCE["sms"] == "sms"


class TestOwlCoordinationSmsPresent:
    def _artifacts(self) -> list:
        case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
        return case["artifacts"]

    def test_coordination_sms_present_in_case_file(self):
        arts = self._artifacts()
        sms_arts = [a for a in arts if a.get("type") == "sms"]
        assert len(sms_arts) == 2, (
            "expected the L-041 coordination SMS pair (delivery confirmation "
            f"+ reply); found {len(sms_arts)} sms artifacts"
        )
        messages = {a["content"]["message"] for a in sms_arts}
        assert (
            "Sarah, the delivery is today 7 tonight the confirmation will "
            "come later through pidgin"
        ) in messages
        assert "Thank you!" in messages

    def test_coordination_sms_survives_normalization_as_sms_evidence_type(self):
        case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
        normalized = normalize_case_schema(case)
        sms_norm = [
            a for a in normalized["artifacts"] if a.get("evidence_type") == "sms"
        ]
        assert len(sms_norm) == 2
        ids = {a["artifact_id"] for a in sms_norm}
        assert ids == {"ART-021", "ART-022"}, (
            "artifact_id must survive normalization — a '?' here means the "
            "legacy id->artifact_id preservation (B-162) regressed"
        )
