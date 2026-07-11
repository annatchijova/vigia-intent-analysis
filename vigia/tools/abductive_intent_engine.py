"""Re-export shim (L-052 consolidation).

The canonical AbductiveIntentEngine lives in
vigia/inference/abductive_intent_engine.py (self-labeled "canonico" and the
only copy with a production import path — vigia/pipeline/pipeline.py's
defensive Thirdness import).

This file used to hold a DIVERGENT full copy (distinct md5; differences in
hypothesis IDs, Daubert annotations, and import style) with no production
invocation path — only __main__ manual-test blocks. For an engine that
claims Daubert-grade determinism, which copy gets loaded must not depend on
import spelling (KNOWN_LIMITATIONS.md L-052), so the copies were replaced by
this alias. The pre-consolidation content is preserved in git history
(tag restore-pre-audit-2026-07-10 and earlier).
"""
from vigia.inference.abductive_intent_engine import *  # noqa: F401,F403
from vigia.inference.abductive_intent_engine import (  # noqa: F401
    AbductiveIntentEngine,
    AbductiveHypothesis,
    AbductiveResult,
    Artifact,
    HYPOTHESIS_TEMPLATES,
)
