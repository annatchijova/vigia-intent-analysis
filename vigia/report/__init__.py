"""Audience-tailored presentations of a sealed VIGÍA verdict.

Two audiences (``junior`` SOC analyst, ``expert`` forensic examiner), two
languages (``en``, ``es``), one rule: this package is a **viewer**. It reads a
sealed bundle and writes Markdown *beside* it. It never computes, restates,
reconciles, rounds or translates a sealed value. Verdict values, schema names
and bundle field names appear verbatim; only the explanation around them is
localized (same rule as the web UI chrome, ``vigia/ui/static/i18n.js``).

Position in the architecture
----------------------------
* Strictly downstream of the sealed verdict path. Nothing under
  ``vigia_scorer.py``, ``vigia/tools/caie.py``, ``vigia/core/decision_layer.py``
  or any other sealed module imports this package; a regression test enforces
  the arrow's direction (``tests/test_report_not_in_verdict_path.py``).
* Deterministic and stdlib-only: same bundle bytes -> same report bytes, in any
  process, under any ``PYTHONHASHSEED``. No generation timestamp is written.
* Outputs are sibling files (``<stem>_report_<audience>_<lang>.md``). All three
  bundle families hash their entire payload, so a presentation can never live
  inside the seal without changing it. Precedent: ``<stem>_reasoning_trace.json``.
* ``VIGIA_AUDIENCE_REPORTS_ENABLED`` (default ``true``) is a kill switch for the
  ``vigia_agent.py`` hook only. It is deliberately **not** registered in
  ``vigia/core/config_sentinel.py``: that map feeds a sealed integrity report,
  and a presentation flag must not be able to move it.
"""

from __future__ import annotations

REPORT_VERSION = "1.0"
AUDIENCES: tuple[str, ...] = ("junior", "expert")
LANGS: tuple[str, ...] = ("en", "es")

__all__ = ["REPORT_VERSION", "AUDIENCES", "LANGS"]
