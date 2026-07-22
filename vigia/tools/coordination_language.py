"""Candidate content-language detector for transaction coordination (L-041).

NOT WIRED to vigia_scorer.py or vigia_integration_bridge.py. This module is a
measurement-only candidate — see scripts/dryrun_coordination_language.py and
BUGS_PENDIENTES.md (B-207) for why: the corpus has exactly one case with
content-rich legacy artifacts and no known-negative examples for this content
class, far below the L-033 calibration precedent's minimum (>=20 signals,
>=3 cases per polarity, both polarities represented) before any detector is
allowed to influence raw_score.

Deliberately narrow rule (per L-041's own caution against generic
price/time/location keyword sets): flag a message ONLY when it names a
secondary confirmation channel ("confirmation will come through X", "message
me on X to confirm") AND makes a concrete delivery/handoff timing commitment
("today", "tonight", or an explicit clock time paired with a handoff verb) in
the SAME text. Requiring both conditions together — rather than either
alone — is what keeps ordinary scheduling messages ("let's meet for coffee at
5") from matching.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Optional

# Generic secondary-communication-channel names. Not "owl"-specific and not
# limited to L-041's original encrypted-app list (android_forensics.py's
# ENCRYPTED_APPS) — any named channel used to relocate a confirmation counts.
_CHANNEL_WORDS = (
    r"pidgin|signal|wickr|wire|telegram|whatsapp|kik|snapchat|imessage|"
    r"skype|discord|session|briar|email|e-?mail|text|sms|call|phone"
)

_CHANNEL_HANDOFF_RE = re.compile(
    r"\b(?:confirm(?:ation|ed)?|message me|reach (?:me|out))\b"
    r"[^.!?]{0,40}\b(?:through|via|on|by)\b[^.!?]{0,20}\b(?:" + _CHANNEL_WORDS + r")\b",
    re.IGNORECASE,
)

_TIMING_WORD_RE = re.compile(r"\b(?:today|tonight|tomorrow)\b", re.IGNORECASE)
_CLOCK_TIME_RE = re.compile(r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)?\b", re.IGNORECASE)
_HANDOFF_VERB_RE = re.compile(
    r"\b(?:deliver(?:y)?|drop[\s-]?off|bring|pick[\s-]?up|hand(?:ed)?[\s-]?over|meet)\b",
    re.IGNORECASE,
)


def _has_timing_commitment(text: str) -> Optional[str]:
    word_match = _TIMING_WORD_RE.search(text)
    if word_match and _HANDOFF_VERB_RE.search(text):
        return word_match.group(0)
    clock_match = _CLOCK_TIME_RE.search(text)
    if clock_match and _HANDOFF_VERB_RE.search(text):
        return clock_match.group(0)
    return None


def detect_coordination_handoff(text: Any) -> Optional[dict]:
    """Return a finding dict if `text` names a confirmation channel AND makes
    a delivery/handoff timing commitment; None otherwise (including for any
    non-string or empty input — this is a pure, non-throwing classifier).
    """
    if not isinstance(text, str) or not text.strip():
        return None

    channel_match = _CHANNEL_HANDOFF_RE.search(text)
    if not channel_match:
        return None

    timing_phrase = _has_timing_commitment(text)
    if timing_phrase is None:
        return None

    channel_word_match = re.search(_CHANNEL_WORDS, channel_match.group(0), re.IGNORECASE)
    return {
        "pattern": "COORDINATION_CHANNEL_HANDOFF",
        "matched_channel_word": channel_word_match.group(0).lower() if channel_word_match else None,
        "matched_timing_phrase": timing_phrase.lower(),
        "severity": Fraction(70, 100),
    }
