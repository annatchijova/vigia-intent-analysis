"""``mcp`` may be absent, but it may not be present-and-wrong silently.

The suite guards every module that imports ``vigia/vigia_sift_bridge.py`` with
``pytest.importorskip("mcp.server.fastmcp")``.  That guard is deliberately
aimed at the submodule the bridge actually imports (``vigia_sift_bridge.py``
line 49: ``from mcp.server.fastmcp import FastMCP``) rather than at the
top-level ``mcp`` distribution, because the two states are not the same
failure and must not produce the same outcome:

* ``mcp`` **absent** -- the expected state of a minimal CI environment
  (KNOWN_LIMITATIONS.md L-045).  Every bridge module skips, the rest of the
  suite runs, nothing is reported as broken.  This is honest degradation.

* ``mcp`` **present but incompatible** -- the distribution installs, so a
  guard on the bare name ``mcp`` would pass, and then the bridge import blows
  up at collection time and takes the whole pytest session down with it
  (B-227).  Aiming the guard at the submodule turns that into a skip too --
  which keeps the suite alive but would now hide a genuinely broken install
  behind a wall of green skips.

This module is the piece that stops the second state from being silent.  The
guards keep the session running; this test fails, loudly and specifically,
when the dependency is installed at a version the bridge cannot use.

Concrete instance this was written against: ``mcp`` 2.0.0 removed the
``mcp.server.fastmcp`` subpackage entirely (verified 2026-08-12 against the
published wheel -- ``mcp.server`` still ships ``lowlevel``, ``session``,
``stdio``, ``streamable_http`` and others, but no ``fastmcp``).  The bridge
cannot import under it, so Modes 2 and 5 cannot start.

The declared pins are what currently prevent that: ``requirements.txt`` and
``pyproject.toml`` bound ``mcp`` below 2.  Before they were bounded, the only
thing holding the line was a *transitive accident* -- ``fastmcp``, which no
module in this repository imports, happens to depend on ``mcp<2``.  A cleanup
that dropped ``fastmcp`` as vestigial, or a ``fastmcp`` release relaxing that
bound, would have silently broken the MCP surface with nothing in the repo
objecting.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
BRIDGE = REPO / "vigia" / "vigia_sift_bridge.py"

# The import the bridge actually performs. Kept as data so the test fails if
# the bridge ever moves to a different entry point without this being updated.
REQUIRED_SUBMODULE = "mcp.server.fastmcp"
REQUIRED_SYMBOL = "FastMCP"


def _spec_exists(name: str) -> bool:
    """``find_spec`` does not only return ``None`` for a missing module.

    For a dotted name it imports the parent package first and propagates
    ``ModuleNotFoundError`` when that parent is absent, and any finder on
    ``sys.meta_path`` may raise. Both mean "not importable here", which is the
    only question this module asks.
    """
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _mcp_is_installed() -> bool:
    return _spec_exists("mcp")


def test_bridge_still_imports_the_submodule_this_contract_pins() -> None:
    """Anchors the contract to the live source, not to a remembered line."""
    source = BRIDGE.read_text(encoding="utf-8")
    expected = f"from {REQUIRED_SUBMODULE} import {REQUIRED_SYMBOL}"

    assert expected in source, (
        f"{BRIDGE.name} no longer contains {expected!r}. If the bridge moved to "
        f"a different MCP entry point, update REQUIRED_SUBMODULE here and the "
        f"pytest.importorskip target in every module that imports the bridge -- "
        f"otherwise those guards now skip on the wrong condition."
    )


@pytest.mark.skipif(
    not _mcp_is_installed(),
    reason="mcp absent: the allowlisted L-045 state, checked by "
           "test_minimal_ci_collects_without_errors.py instead",
)
def test_installed_mcp_provides_what_the_bridge_imports() -> None:
    """Present-but-incompatible must fail here rather than skip everywhere."""
    assert _spec_exists(REQUIRED_SUBMODULE), (
        f"`mcp` is installed but does not provide `{REQUIRED_SUBMODULE}`. The "
        f"bridge cannot import, so Modes 2 and 5 cannot start and every bridge "
        f"test is skipping rather than running. mcp 2.0.0 removed this "
        f"subpackage: install a version below 2, as requirements.txt and "
        f"pyproject.toml declare."
    )

    from mcp.server.fastmcp import FastMCP  # noqa: F401


@pytest.mark.parametrize(
    "manifest, pattern",
    [
        ("requirements.txt", r"^\s*mcp\s*(?P<spec>[<>=!,\s\d.]+)$"),
        ("pyproject.toml", r'"mcp(?P<spec>[<>=!,\s\d.]+)"'),
    ],
)
def test_manifests_bound_mcp_below_the_breaking_major(manifest: str, pattern: str) -> None:
    """The upper bound must be declared, not inherited from ``fastmcp``."""
    text = (REPO / manifest).read_text(encoding="utf-8")
    matches = [
        m.group("spec") for m in re.finditer(pattern, text, flags=re.MULTILINE)
    ]

    assert matches, f"no `mcp` requirement found in {manifest}"
    for spec in matches:
        assert "<2" in spec.replace(" ", ""), (
            f"{manifest} declares `mcp{spec.strip()}`, which admits mcp 2.x. "
            f"That release removed `{REQUIRED_SUBMODULE}` and the bridge cannot "
            f"import under it. The bound must be declared here, not left to "
            f"`fastmcp`'s transitive constraint -- nothing in this repository "
            f"imports `fastmcp`, so that constraint can disappear in a cleanup."
        )
