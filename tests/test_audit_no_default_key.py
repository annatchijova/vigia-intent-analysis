"""
tests/test_audit_no_default_key.py
==================================
Red-team audit — Finding H-08: default HMAC key fallback.

Automates the `grep default_key` as a permanent guard. If `verify_level_1`
(or any other path) uses `b"default_key"` as a fallback when trusted_root is
None, the integrity anchor is forgeable by anyone who knows the constant.

This test is NOT xfail: it is a hard assertion. If you already fixed it, it
passes. If it reappears in any refactor, it fails immediately.

Does not import modules: it scans the source code, so it runs in any
environment without depending on PYTHONPATH.
"""
from __future__ import annotations

import pathlib

import pytest

# Forbidden literal. Kept as bytes to avoid self-triggering the match from the
# test's own source text (we construct it in parts).
_FORBIDDEN = b"default" + b"_key"


def _repo_root() -> pathlib.Path:
    """Walk up from this file until we find the repo root (vigia/ folder)."""
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "vigia").is_dir() or (parent / "vigia_scorer.py").exists():
            return parent
    # Fallback: two levels up from tests/
    return here.parent.parent


def _trust_level_sources() -> list[pathlib.Path]:
    root = _repo_root()
    matches = list(root.rglob("trust_levels*.py"))
    return [p for p in matches if "__pycache__" not in str(p)]


def test_trust_level_files_exist():
    files = _trust_level_sources()
    if not files:
        pytest.skip("No trust_levels*.py found under the repo root.")
    assert files, "Expected at least one trust_levels module."


@pytest.mark.parametrize("path", _trust_level_sources(), ids=lambda p: p.name)
def test_no_default_hmac_key_fallback(path: pathlib.Path):
    data = path.read_bytes()
    assert _FORBIDDEN not in data, (
        f"{path} contains a default HMAC key fallback "
        f"({_FORBIDDEN.decode()!r}). Replace with "
        f'raise RuntimeError("Trusted root required") — an HMAC with a '
        f"publicly known key is not an integrity anchor."
    )
