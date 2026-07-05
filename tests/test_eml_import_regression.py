"""
tests/test_eml_import_regression.py
===================================
Import-time regression for the email-forensics modules (was 0% covered).

BUG-EML-001 (FIXED) — three modules imported SignalBuilder from the wrong
module and therefore failed to load at all:

    vigia/tools/eml_symbolic.py:41   from vigia.core.signal_contract import SignalBuilder
    vigia/tools/eml_gci.py:39        from vigia.core.signal_contract import SignalBuilder
    vigia/tools/signal_adapter.py:37 from vigia.core.signal_contract import SignalBuilder

SignalBuilder is not defined in vigia/core/signal_contract.py (that file only
re-exports data models from ebs_v1). It lives in vigia/tools/signal_contract.py
(class SignalBuilder, with from_raw() and from_z_score()). Every import of any
of the three raised:

    ImportError: cannot import name 'SignalBuilder' from 'vigia.core.signal_contract'

No runtime shim injects SignalBuilder into vigia.core.signal_contract anywhere
in the tree, and no test imported these modules — which is exactly why the
breakage sat undetected at 0% coverage. eml_gci is also the downstream consumer
of entropy_kernel (see BUG-ENTROPY-001), so this import wall doubled that
path's invisibility.

Fix applied: the three imports now point at vigia.tools.signal_contract, which
keeps the documented layering (core = layer-0 data, tools = logic) instead of
re-exporting logic from core. Staged verification after the fix: all three
modules import cleanly (no further latent errors surfaced behind the import
wall), and a static check confirmed all 12 SignalBuilder call sites use only
kwargs present in the real from_raw / from_z_score signatures.

This test is now the regression guard: all three modules must stay importable.
"""
from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "vigia.tools.eml_symbolic",
        "vigia.tools.eml_gci",
        # Third victim of the same wrong import path, found while measuring
        # the blast radius for the fix (signal_adapter.py:37).
        "vigia.tools.signal_adapter",
    ],
)
def test_email_forensic_module_imports(module_name):
    # importlib keeps the ImportError inside the test body, so a broken import
    # surfaces as a clean test FAILURE rather than a collection-time error.
    importlib.import_module(module_name)
