# vigia/llm/hallucination_guard.py
#
# Hallucination Guard — Narrative Verification Layer
# =============================================================================
# Design: Anna Tchijova + Claude (Anthropic) + ChatGPT + Kimi (Moonshot)
#         2026-06-26
#
# Philosophy:
#   The LLM is outside the verdict path. But the LLM *narrates* the verdict.
#   If the narration invents facts the motor never computed, the forensic
#   record is contaminated even though the verdict is correct.
#
#   This module enforces: the narrative cannot amplify the evidence; it can
#   only express facts that already exist in the deterministic state.
#
# Architecture (Opción B — motor not modified):
#   Motor result dict
#       ↓
#   extract_authorized_facts()  ← B: separate function, not part of evaluate()
#       ↓
#   frozenset[AuthorizedFact]   ← explicit authorized set, no dict traversal
#       ↓
#   HallucinationGuard.check(narration)
#       ↓
#   GuardResult (safe_narration + audit trail)
#
# Key design decisions:
#   - No float anywhere — numeric comparison uses Decimal with localcontext
#   - No flatten_dict — only known field paths from evaluate() output
#   - match_strategy is explicit per fact ("exact" | "numeric")
#   - Three-valued match: True=verified, False=hallucinated, None=unverifiable
#   - field_path is for traceability only, not for matching
#
# Kimi audit (2026-06-26) findings addressed:
#   - P0: No quantize() — uses Decimal(a)==Decimal(b) with localcontext
#   - P0: No str.replace() for redaction — uses char-index reconstruction
#   - P1: Three-valued match distinguishes hallucinated from unverifiable
#   - P1: match_strategy field makes the two matchers explicit
#   - P2: z-scores not in evaluate() output — removed from fact types
#   - P2: process names not in evaluate() output — removed from fact types
#   - P3: _NUMERIC_CTX not a module-level mutable — constructed inline
#
# Run:
#   python3 vigia/llm/hallucination_guard.py  (runs __main__ test)

from __future__ import annotations

import decimal
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, List, Optional

logger = logging.getLogger("vigia.hallucination_guard")


# ---------------------------------------------------------------------------
# AuthorizedFact — the unit of ground truth
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AuthorizedFact:
    """
    A single fact authorized by the deterministic motor.

    Invariants:
    - value is ALWAYS a str — Decimal/Fraction serialized via str()
    - value is NEVER a float
    - match_strategy determines how claim_value is compared to value

    field_path is for traceability only (appears in GuardResult for
    debugging). It does not participate in matching.
    """
    fact_type: str        # "verdict" | "score" | "fracture_type" |
                          # "severity" | "hash" | "mitre_ttp" | "golden_rules"
    field_path: str       # e.g. "verdict", "fractures[0].type" — traceability
    value: str            # canonical str — no floats ever
    match_strategy: str   # "exact" | "numeric"


def extract_authorized_facts(result: dict) -> frozenset:
    """
    Extract authorized facts from evaluate() output dict.

    Only uses known field paths from the real evaluate() output structure
    (confirmed against live output 2026-06-26). No dict flattening.
    No assumptions about unknown fields.

    Field paths covered:
      - result["verdict"]
      - result["structural_verdict"]
      - result["probabilistic_verdict"]
      - result["composite_score"]          ← str since L-021 Phase 1
      - result["probabilistic_score"]      ← str since L-021 Phase 1
      - result["fractures"][i]["type"]
      - result["fractures"][i]["severity"] ← str since L-021 Phase 1
      - result["fractures"][i]["mitre_ttp"]
      - result["raw_scores"][i]["adjusted"]  ← str since L-021 Phase 1
      - result["raw_scores"][i]["raw_score"] ← str since L-021 Phase 1
      - result["golden_rules_triggered"]
      - result["_operation_hmac"]
    """
    facts: set[AuthorizedFact] = set()

    # Verdicts — exact match
    for key in ("verdict", "structural_verdict", "probabilistic_verdict"):
        v = result.get(key)
        if v and isinstance(v, str):
            facts.add(AuthorizedFact(
                fact_type="verdict",
                field_path=key,
                value=v.strip().upper(),
                match_strategy="exact",
            ))

    # Scores — numeric match (str from L-021 boundary)
    for key in ("composite_score", "probabilistic_score"):
        v = result.get(key)
        if v is not None:
            facts.add(AuthorizedFact(
                fact_type="score",
                field_path=key,
                value=str(v),
                match_strategy="numeric",
            ))

    # Fractures
    for i, f in enumerate(result.get("fractures", [])):
        if ftype := f.get("type"):
            facts.add(AuthorizedFact(
                fact_type="fracture_type",
                field_path=f"fractures[{i}].type",
                value=str(ftype).upper(),
                match_strategy="exact",
            ))
        if sev := f.get("severity"):
            facts.add(AuthorizedFact(
                fact_type="severity",
                field_path=f"fractures[{i}].severity",
                value=str(sev),
                match_strategy="numeric",
            ))
        if ttp := f.get("mitre_ttp"):
            facts.add(AuthorizedFact(
                fact_type="mitre_ttp",
                field_path=f"fractures[{i}].mitre_ttp",
                value=str(ttp).upper(),
                match_strategy="exact",
            ))

    # Raw scores
    for i, rs in enumerate(result.get("raw_scores", [])):
        for subkey in ("adjusted", "raw_score"):
            v = rs.get(subkey)
            if v is not None:
                facts.add(AuthorizedFact(
                    fact_type="score",
                    field_path=f"raw_scores[{i}].{subkey}",
                    value=str(v),
                    match_strategy="numeric",
                ))

    # Golden rules count — exact (it's an int, serialized as str)
    gr = result.get("golden_rules_triggered")
    if gr is not None:
        facts.add(AuthorizedFact(
            fact_type="golden_rules",
            field_path="golden_rules_triggered",
            value=str(gr),
            match_strategy="exact",
        ))

    # HMAC hash — exact, case-insensitive
    hmac = result.get("_operation_hmac")
    if hmac and isinstance(hmac, str):
        facts.add(AuthorizedFact(
            fact_type="hash",
            field_path="_operation_hmac",
            value=hmac.lower(),
            match_strategy="exact",
        ))

    return frozenset(facts)


# ---------------------------------------------------------------------------
# Matcher
# ---------------------------------------------------------------------------

def match_fact(
    claim_type: str,
    claim_value: str,
    facts: frozenset,
) -> tuple[Optional[bool], str]:
    """
    Match a claim against the authorized fact set.

    Returns:
        (True,  field_path) — claim verified against a known fact
        (False, "")         — candidates exist but none matched (hallucinated)
        (None,  "")         — no facts of this type in motor output (unverifiable)

    The three-valued return distinguishes hallucinated (False) from unverifiable
    (None). GuardResult.claims_hallucinated counts False; claims_unverifiable
    counts None. Only False counts against the LLM.
    """
    candidates = [f for f in facts if f.fact_type == claim_type]

    if not candidates:
        return None, ""

    for fact in candidates:
        if fact.match_strategy == "exact":
            # Verdicts and fracture types: upper() only (no strip — motor
            # guarantees no whitespace in canonical values since L-021).
            # Hashes: lower() only.
            if claim_type == "hash":
                if claim_value.lower() == fact.value:
                    return True, fact.field_path
            else:
                if claim_value.strip().upper() == fact.value:
                    return True, fact.field_path

        elif fact.match_strategy == "numeric":
            # Decimal comparison with fixed context — no quantize, no float.
            # localcontext is constructed inline to prevent context mutation
            # from other modules affecting this comparison.
            try:
                ctx = decimal.Context(prec=28, rounding=decimal.ROUND_HALF_EVEN)
                with decimal.localcontext(ctx):
                    if decimal.Decimal(claim_value) == decimal.Decimal(fact.value):
                        return True, fact.field_path
            except decimal.InvalidOperation:
                continue

    return False, ""


# ---------------------------------------------------------------------------
# Claim extraction from LLM narrative
# ---------------------------------------------------------------------------

@dataclass
class NarrativeClaim:
    """A claim extracted from LLM narrative text."""
    text: str               # the matched fragment
    claim_type: str         # maps to AuthorizedFact.fact_type
    extracted_value: str    # what the LLM claims
    start: int              # char index in narrative — for index-based redaction
    end: int
    verified: Optional[bool] = None  # True/False/None — three-valued
    ground_truth_path: str = ""      # field_path of matching fact if verified


# Regexes for claim extraction from LLM narrative text.
# Deliberately conservative — prefer false negatives over false positives.
# A missed claim is not verified (neutral). A false claim match would be worse.
_VERDICT_RE = re.compile(
    r"\b(MALICE|BENIGN|NOISE|SUSPICION|INCONCLUSIVE)\b",
    re.IGNORECASE,
)
_SCORE_RE = re.compile(
    r"(?:score|composite|posterior|confidence)[:\s]+([0-9]+\.[0-9]+)",
    re.IGNORECASE,
)
_SEVERITY_RE = re.compile(
    r"(?:severity)[:\s]+([0-9]+\.[0-9]+)",
    re.IGNORECASE,
)
_FRACTURE_TYPE_RE = re.compile(
    r"\b(LOG_VS_MEMORY|MEMORY_VS_DISK|TIMELINE_PARADOX|EFFECT_BEFORE_CAUSE|"
    r"NARRATIVE_POISONING_DETECTED|TEMPORAL_IMPOSSIBILITY|"
    r"CROSS_TOOL_CONTRADICTION|FALSE_FLAG_PATTERN)\b",
    re.IGNORECASE,
)
_MITRE_RE = re.compile(r"\b(T\d{4}(?:\.\d{3})?)\b")
_SHA256_RE = re.compile(r"\b([0-9a-f]{64})\b", re.IGNORECASE)


def extract_claims(narration: str) -> list[NarrativeClaim]:
    """
    Extract verifiable claims from LLM narrative text.

    Returns NarrativeClaim objects with char-level start/end positions
    for index-based redaction (no str.replace).
    """
    claims: list[NarrativeClaim] = []

    for m in _VERDICT_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0),
            claim_type="verdict",
            extracted_value=m.group(1).upper(),
            start=m.start(), end=m.end(),
        ))

    for m in _SCORE_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0),
            claim_type="score",
            extracted_value=m.group(1),
            start=m.start(), end=m.end(),
        ))

    for m in _SEVERITY_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0),
            claim_type="severity",
            extracted_value=m.group(1),
            start=m.start(), end=m.end(),
        ))

    for m in _FRACTURE_TYPE_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0),
            claim_type="fracture_type",
            extracted_value=m.group(1).upper(),
            start=m.start(), end=m.end(),
        ))

    for m in _MITRE_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0),
            claim_type="mitre_ttp",
            extracted_value=m.group(1).upper(),
            start=m.start(), end=m.end(),
        ))

    for m in _SHA256_RE.finditer(narration):
        claims.append(NarrativeClaim(
            text=m.group(0)[:16] + "...",
            claim_type="hash",
            extracted_value=m.group(1).lower(),
            start=m.start(), end=m.end(),
        ))

    return claims


# ---------------------------------------------------------------------------
# Guard result
# ---------------------------------------------------------------------------

@dataclass
class GuardResult:
    original_narration: str
    safe_narration: str         # hallucinated claims redacted
    claims_total: int = 0
    claims_verified: int = 0
    claims_hallucinated: int = 0
    claims_unverifiable: int = 0
    hallucination_rate: Fraction = Fraction(0)
    suspicious: bool = False
    audit_sha256: str = ""
    hallucinated_claims: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "claims_total": self.claims_total,
            "claims_verified": self.claims_verified,
            "claims_hallucinated": self.claims_hallucinated,
            "claims_unverifiable": self.claims_unverifiable,
            "hallucination_rate": str(self.hallucination_rate),
            "suspicious": self.suspicious,
            "audit_sha256": self.audit_sha256,
            "hallucinated_claims": [
                {
                    "text": c.text,
                    "type": c.claim_type,
                    "llm_said": c.extracted_value,
                    "ground_truth_path": c.ground_truth_path,
                }
                for c in self.hallucinated_claims
            ],
        }


# ---------------------------------------------------------------------------
# HallucinationGuard
# ---------------------------------------------------------------------------

class HallucinationGuard:
    """
    Verifies LLM narrative against the deterministic motor output.

    Usage:
        facts = extract_authorized_facts(pipeline_result)
        guard = HallucinationGuard(facts)
        result = guard.check(llm_narration)
        if result.suspicious:
            use result.safe_narration instead of llm_narration
    """

    def __init__(
        self,
        authorized_facts: frozenset,
        hallucination_threshold: Fraction = Fraction(1, 5),
        redact_marker: str = "[CLAIM NOT VERIFIED]",
    ):
        self.facts = authorized_facts
        self.threshold = hallucination_threshold
        self.redact_marker = redact_marker

    def check(self, narration: str) -> GuardResult:
        claims = extract_claims(narration)

        for claim in claims:
            matched, path = match_fact(claim.claim_type, claim.extracted_value,
                                       self.facts)
            claim.verified = matched
            claim.ground_truth_path = path

        total = len(claims)
        verified = sum(1 for c in claims if c.verified is True)
        hallucinated = sum(1 for c in claims if c.verified is False)
        unverifiable = sum(1 for c in claims if c.verified is None)
        hallucinated_claims = [c for c in claims if c.verified is False]

        # Hallucination rate counts only verified+hallucinated in denominator.
        # Unverifiable claims are excluded — cannot count as evidence against LLM.
        verifiable_total = verified + hallucinated
        rate = Fraction(hallucinated, verifiable_total) if verifiable_total > 0 \
               else Fraction(0)

        suspicious = rate > self.threshold

        # Index-based redaction — no str.replace().
        # Sort hallucinated claims by start position descending to preserve
        # indices when replacing from end to start.
        safe = narration
        if hallucinated_claims:
            # Build list of (start, end, replacement) sorted by start desc
            intervals = sorted(
                [(c.start, c.end) for c in hallucinated_claims],
                key=lambda x: x[0],
                reverse=True,
            )
            # Merge overlapping intervals
            merged = []
            for start, end in intervals:
                if merged and start < merged[-1][1]:
                    merged[-1] = (min(start, merged[-1][0]),
                                  max(end, merged[-1][1]))
                else:
                    merged.append([start, end])
            # Apply replacements from end to start (preserves indices)
            for start, end in merged:
                safe = safe[:start] + self.redact_marker + safe[end:]

        # Seal
        payload = {
            "claims_total": total,
            "claims_hallucinated": hallucinated,
            "hallucination_rate": str(rate),
            "suspicious": suspicious,
        }
        sha = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        if suspicious:
            logger.warning(
                "[HALLUCINATION_GUARD] Suspicious narrative: "
                "%d/%d verifiable claims not in motor output. "
                "Rate: %s. SHA256: %s",
                hallucinated, verifiable_total, rate, sha,
            )
        elif hallucinated > 0:
            logger.warning(
                "[HALLUCINATION_GUARD] %d claim(s) not verified "
                "(below threshold %s). Rate: %s.",
                hallucinated, self.threshold, rate,
            )
        else:
            logger.info(
                "[HALLUCINATION_GUARD] Narrative verified. "
                "%d/%d claims confirmed. SHA256: %s",
                verified, total, sha,
            )

        return GuardResult(
            original_narration=narration,
            safe_narration=safe,
            claims_total=total,
            claims_verified=verified,
            claims_hallucinated=hallucinated,
            claims_unverifiable=unverifiable,
            hallucination_rate=rate,
            suspicious=suspicious,
            audit_sha256=sha,
            hallucinated_claims=hallucinated_claims,
        )


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    # Simulate evaluate() output (L-021: scores are str)
    fake_result = {
        "verdict": "MALICE",
        "structural_verdict": "MALICE",
        "probabilistic_verdict": "NOISE",
        "composite_score": "0.0164",
        "probabilistic_score": "0.0164",
        "fractures": [
            {
                "type": "LOG_VS_MEMORY",
                "severity": "0.7500",
                "mitre_ttp": "T1070.001",
                "artifact_a": "log",
                "artifact_b": "memory",
                "interpretation": "...",
                "spoofability_delta": "0.7000",
                "is_golden_rule": False,
                "is_structural": True,
            }
        ],
        "raw_scores": [
            {"tool": "log", "type": "log_entry",
             "raw_score": "0.9000", "adjusted": "0.0500"},
        ],
        "golden_rules_triggered": 0,
        "_operation_hmac": "a" * 64,
    }

    facts = extract_authorized_facts(fake_result)
    print(f"Authorized facts: {len(facts)}")
    for f in sorted(facts, key=lambda x: x.field_path):
        print(f"  {f.fact_type:<16} {f.field_path:<35} = {f.value!r} [{f.match_strategy}]")

    guard = HallucinationGuard(facts, hallucination_threshold=Fraction(1, 5))

    # Narration with one hallucinated score (7.99 not in facts)
    narration = (
        "The analysis determined a verdict of MALICE. "
        "The composite score: 7.99 indicates extreme deviation. "
        "Fracture type LOG_VS_MEMORY was detected with severity: 0.7500. "
        "MITRE technique T1070.001 was identified."
    )

    result = guard.check(narration)
    print(f"\nTotal: {result.claims_total}, "
          f"Verified: {result.claims_verified}, "
          f"Hallucinated: {result.claims_hallucinated}, "
          f"Unverifiable: {result.claims_unverifiable}")
    print(f"Rate: {result.hallucination_rate}, Suspicious: {result.suspicious}")
    print(f"\nSafe narration:\n{result.safe_narration}")
