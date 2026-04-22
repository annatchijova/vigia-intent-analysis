"""
phonetic_loader.py — COMPATIBILITY SHIM (do not use directly)
==============================================================
This file exists ONLY for backward compatibility with scripts that
import from the project root. All real logic lives in vigia/phonetic_loader.py.

Migration (2026-04 audit — Qwen2 architecture review):
  OLD: from phonetic_loader import PHONETIC_MAP, reload_dict
  NEW: from vigia.phonetic_loader import PHONETIC_MAP, reload_dict

This shim will be removed in a future version.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from 'phonetic_loader' (project root) is deprecated. "
    "Use 'from vigia.phonetic_loader import ...' instead. "
    "This shim will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical module
from vigia.phonetic_loader import (  # noqa: F401
    PHONETIC_MAP,
    HIGH_RISK_SET,
    HOMOGLYPH_NOTES,
    RAW_DATA,
    reload_dict,
    get_stats,
    get_raw_section,
)
