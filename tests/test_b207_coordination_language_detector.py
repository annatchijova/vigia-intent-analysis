"""B-207: candidate transaction-coordination-language detector.

NOT wired to the scorer (see BUGS_PENDIENTES.md B-207) — the corpus has
exactly one case with content-rich legacy artifacts (OWL-NEXUS5-CASE,
B-206) and zero known-negative examples for this content class, far below
the L-033 calibration precedent's minimum (>=20 signals, >=3 cases per
polarity) before any detector is allowed to influence raw_score. These are
pure unit tests of the standalone classifier only.
"""

from __future__ import annotations

from vigia.tools.coordination_language import detect_coordination_handoff

# The real B-206 message (evidence/owl-2019-nexus5-quick/Agent Data/mmssms.db,
# sms._id=6) — the true positive this detector exists to catch.
OWL_SMS = (
    "Sarah, the delivery is today 7 tonight the confirmation "
    "will come later through pidgin"
)

# Hand-built benign scheduling messages — ordinary coordination that must
# NOT match, since the corpus has no real negatives for this content class.
BENIGN_MESSAGES = [
    "let's meet for coffee at 5 tomorrow",
    "see you tonight for dinner, can't wait!",
    "I'll text you when I land",
    "call me when you're free later today",
    "running late, will message you on whatsapp when I'm close",
    "confirmation email for your flight arrives in 24 hours",
    "reminder: dentist appointment today at 3pm",
    "happy birthday! let's celebrate this weekend",
    "meeting moved to tomorrow morning, sorry for the short notice",
    "thanks for the delivery, it arrived safely",
]


class TestTruePositive:
    def test_owl_sms_matches(self):
        finding = detect_coordination_handoff(OWL_SMS)
        assert finding is not None
        assert finding["pattern"] == "COORDINATION_CHANNEL_HANDOFF"
        assert finding["matched_channel_word"] == "pidgin"
        assert finding["matched_timing_phrase"] in ("today", "tonight")

    def test_reply_alone_does_not_match(self):
        # The "Thank you!" reply (ART-022) has neither channel nor timing —
        # must not match on its own.
        assert detect_coordination_handoff("Thank you!") is None


class TestBenignNegatives:
    def test_ordinary_scheduling_messages_do_not_match(self):
        false_positives = [
            msg for msg in BENIGN_MESSAGES if detect_coordination_handoff(msg) is not None
        ]
        assert false_positives == [], (
            f"detector flagged ordinary scheduling text as coordination handoff: {false_positives}"
        )

    def test_channel_word_alone_without_timing_does_not_match(self):
        assert detect_coordination_handoff(
            "I'll confirm via signal, no rush"
        ) is None

    def test_timing_alone_without_channel_does_not_match(self):
        assert detect_coordination_handoff(
            "the delivery is today at 7"
        ) is None


class TestDegenerateInput:
    def test_none_does_not_crash(self):
        assert detect_coordination_handoff(None) is None

    def test_empty_string_does_not_crash(self):
        assert detect_coordination_handoff("") is None

    def test_non_string_does_not_crash(self):
        for bad in (123, [], {}, True):
            assert detect_coordination_handoff(bad) is None
