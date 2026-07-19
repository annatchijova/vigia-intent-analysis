"""
tests/test_b150_naive_timestamp_utc.py
======================================
B-150 — _parse_iso_timestamp must interpret a timezone-NAIVE ISO string as UTC
(explicitly, with disclosure), not in the host's local timezone. dt.timestamp()
on a naive datetime applies the process-local TZ, so the same case would seal a
different epoch on a UTC host vs an America/New_York host — a determinism leak
(§5.2). This mirrors the CAIE TCV_TIMESTAMP_NAIVE_ASSUMED_UTC assume-UTC-and-log
pattern already used in the verdict path.

Red-first: under a non-UTC TZ, the naive parse diverges from the UTC parse
before the fix (host-local interpretation); after the fix they are equal.
"""
from __future__ import annotations

import os
import time

import pytest

from vigia.sift._math_utils import _parse_iso_timestamp


def _set_tz(tz: str):
    old = os.environ.get("TZ")
    os.environ["TZ"] = tz
    time.tzset()
    return old


def _restore_tz(old):
    if old is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = old
    time.tzset()


def test_naive_timestamp_assumed_utc_under_non_utc_host_tz():
    # Instant-based reference: the aware (Z) form is TZ-independent by construction.
    expected_utc = _parse_iso_timestamp("2026-07-19T10:00:00Z")
    old = _set_tz("America/New_York")  # UTC-4 in July (EDT)
    try:
        # Sanity: confirm the host TZ actually shifted (else the test is vacuous).
        assert time.localtime().tm_gmtoff != 0, "TZ did not take effect; test vacuous"
        naive = _parse_iso_timestamp("2026-07-19T10:00:00")  # no offset
        assert naive == expected_utc, (
            f"naive timestamp interpreted in host-local TZ (determinism leak): "
            f"got {naive}, expected UTC {expected_utc} (delta {naive - expected_utc}s)"
        )
    finally:
        _restore_tz(old)


def test_naive_and_aware_agree_on_utc_host():
    # Regression: on a UTC host, naive and Z forms must remain equal (unchanged).
    old = _set_tz("UTC")
    try:
        assert _parse_iso_timestamp("2026-07-19T10:00:00") == \
               _parse_iso_timestamp("2026-07-19T10:00:00Z")
    finally:
        _restore_tz(old)


def test_aware_offset_still_instant_correct():
    # An explicit offset must still be honored (not overridden by the assume-UTC).
    assert _parse_iso_timestamp("2026-07-19T06:00:00-04:00") == \
           _parse_iso_timestamp("2026-07-19T10:00:00Z")
