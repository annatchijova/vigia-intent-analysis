# vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py
#
# Test P1 — T-1: documented detector blind spot in detect_human_jitter's scalar thresholds
# =============================================================================
# Origin: coverage audit gap T-1 ("RNG sesgado para evadir jitter").
#
# Confirmed live bridge: vigia/vigia_sift_bridge.py — this is the ONLY
# bridge file. launch_vigia_mcp.sh launches it directly (lines 7-8):
#   exec .venv/bin/python3 vigia/vigia_sift_bridge.py "$@"
# A comment at the top of that file claims a separate
# "vigia_sift_bridge_final.py" is the real Active MCP bridge — that file
# does not exist anywhere in the repo. The comment is stale; ignore it.
#
# detect_human_jitter() decides "human vs automation" using exactly four
# scalar checks on the interval sequence between timestamps:
#   1. PROGRAMMED_DELAY_DETECTED: variance < 0.1 and len(intervals) > 3
#   2. NON_HUMAN_PRECISION:       cv < 0.05  and len(intervals) > 5
#   3. IMPOSSIBLE_TYPING_SPEED:   only checked if message_lengths is given
#   4. ABSENCE_OF_HUMAN_PAUSES:   no interval > 10s, len(intervals) > 10,
#                                 average interval < 5s
# score_raw sums whichever fire; verdict is NOISE if score < 40.
#
# The coverage audit's hypothesis was that an attacker needs a biased PRNG
# (Xorshift1024*, small-modulus LCG) to dodge these thresholds. Empirically,
# no PRNG is required at all — not even a real random number. A fully
# deterministic, byte-for-byte reproducible sequence (N-1 identical
# intervals plus ONE inserted pause above 10s) clears all four checks at
# once:
#   - the single outlier alone provides enough variance/cv to clear rules
#     1 and 2 (which fire on LOW variance/cv — too regular)
#   - that same outlier is itself a "long pause", so rule 4 (which fires
#     on the ABSENCE of any pause) never engages
# Nothing about this sequence is irregular in the way a human is irregular
# — it is exactly two repeated values. The detector cannot tell the
# difference because it only ever inspects aggregate variance/cv/pause-
# count, never whether the sequence itself is reproducible.
#
# This is NOT xfail. If it ever fails, that means the detector started
# resisting this exact construction — which would be good news, not a
# regression.
#
# Run: pytest vigia/tests/adversarial/test_human_jitter_deterministic_bypass.py -v

import asyncio
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from vigia.vigia_sift_bridge import detect_human_jitter  # noqa: E402


def _run(coro):
    return asyncio.run(coro)


def _build_timestamps(intervals, base=1_700_000_000.0):
    timestamps = [base]
    for iv in intervals:
        timestamps.append(timestamps[-1] + iv)
    return timestamps


def test_constant_intervals_with_one_inserted_pause_passes_as_noise():
    """
    15 identical 2.0s intervals + 1 inserted 12.0s "fake thinking pause".
    16 intervals total — every length-gate (>3, >5, >10) is satisfied, so
    all four rules are genuinely in play, not skipped on a technicality.

    This sequence is fully deterministic: running it twice produces
    byte-identical timestamps. There is no randomness anywhere in its
    construction. It is the textbook definition of a scripted action
    sequence with one inserted decoy pause — yet it clears every check.
    """
    intervals = [2.0] * 15 + [12.0]
    timestamps = _build_timestamps(intervals)

    avg = sum(intervals) / len(intervals)
    variance = sum((x - avg) ** 2 for x in intervals) / len(intervals)
    cv = math.sqrt(variance) / avg

    # Confirm the construction actually clears rules 1 and 2 by design,
    # not by accident — and that rule 4's length gate is genuinely active.
    assert len(intervals) > 10, "Need len>10 for rule 4's gate to be live."
    assert variance >= 0.1, "Construction error: should clear rule 1's floor."
    assert cv >= 0.05, "Construction error: should clear rule 2's floor."
    assert avg < 5, "Construction error: rule 4 needs avg<5 to be live."

    result = _run(detect_human_jitter(timestamps=timestamps))

    assert "error" not in result, f"Unexpected error: {result.get('error')}"

    assert result["verdict"] == "NOISE", (
        f"Expected a fully deterministic, zero-entropy interval sequence "
        f"(15x identical + 1 decoy pause) to be flagged as automation, but "
        f"detect_human_jitter returned verdict={result['verdict']!r} "
        f"(score_raw={result.get('score_raw')}, "
        f"signals={result.get('signals')}). The detector only checks "
        f"aggregate variance/coefficient_of_variation/pause-count — it "
        f"never checks whether the underlying sequence is reproducible."
    )
    assert result["score_raw"] == 0.0, (
        f"Expected score_raw=0.0 (no rule fires), got "
        f"{result.get('score_raw')} with signals={result.get('signals')}"
    )
    assert result["probability_automation"] == 0.0


def test_two_independent_calls_on_identical_input_agree():
    """
    Same deterministic sequence, called twice with fresh timestamp lists.
    Documents explicitly that detect_human_jitter has no cross-call
    memory: a human never produces the exact same interval sequence
    twice, but the function can't catch that by design — it only ever
    sees one call's worth of data. This is a known, accepted limitation
    of the function's scope, not a new finding — recorded here so it
    doesn't get rediscovered as if it were new.
    """
    intervals = [2.0] * 15 + [12.0]

    r1 = _run(detect_human_jitter(timestamps=_build_timestamps(intervals)))
    r2 = _run(detect_human_jitter(timestamps=_build_timestamps(intervals)))

    assert r1["verdict"] == r2["verdict"] == "NOISE"
    assert r1["score_raw"] == r2["score_raw"] == 0.0


if __name__ == "__main__":
    intervals = [2.0] * 15 + [12.0]
    ts = _build_timestamps(intervals)
    res = _run(detect_human_jitter(timestamps=ts))
    print("verdict:", res.get("verdict"))
    print("score_raw:", res.get("score_raw"))
    print("variance:", res.get("variance"))
    print("coefficient_of_variation:", res.get("coefficient_of_variation"))
    print("signals:", res.get("signals"))
