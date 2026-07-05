"""
tests/test_eml_import_regression.py
===================================
Import-time regression for the email-forensics modules (was 0% covered).

BUG-EML-001 — both e-mail forensic modules import SignalBuilder from the wrong
module and therefore fail to load at all:

    vigia/tools/eml_symbolic.py:41  from vigia.core.signal_contract import SignalBuilder
    vigia/tools/eml_gci.py:39       from vigia.core.signal_contract import SignalBuilder

SignalBuilder is not defined in vigia/core/signal_contract.py (that file only
re-exports data models from ebs_v1). It lives in vigia/tools/signal_contract.py
(class SignalBuilder, with from_raw() and from_z_score()). So every import of
either module raises:

    ImportError: cannot import name 'SignalBuilder' from 'vigia.core.signal_contract'

Confirmation: CONFIRMED. Verified against the live files; no runtime shim
injects SignalBuilder into vigia.core.signal_contract anywhere in the tree, and
no existing test imports these modules — which is exactly why the breakage sat
undetected and the modules show 0% coverage. eml_gci is also the downstream
consumer of entropy_kernel (see BUG-ENTROPY-001), so this import wall is part
of why that path was never exercised.

Suggested fix: change both imports to
    from vigia.tools.signal_contract import SignalBuilder

These tests are left FAILING on purpose so the breakage stays visible until the
import path is corrected.
"""
from __future__ import annotations

import importlib

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "vigia.tools.eml_symbolic",
        "vigia.tools.eml_gci",
    ],
)
def test_email_forensic_module_imports(module_name):
    # importlib keeps the ImportError inside the test body, so a broken import
    # surfaces as a clean test FAILURE rather than a collection-time error.
    importlib.import_module(module_name)
