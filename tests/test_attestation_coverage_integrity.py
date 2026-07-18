"""
Attestation integrity (2026-07-17) — the engine attestation must not silently
reduce its own coverage.

Finding surfaced by Forge (software). Two defects, same family:
  - vigia/pipeline/pipeline.py::_compute_attestation was a dead-duplicate that
    walked ONLY vigia/pipeline/ (missing the scoring core: vigia/tools/caie.py,
    vigia/core/, ...) and captured no dependency versions — an incomplete
    attestation presented as complete (live path).
  - vigia/core/bundle_builder.py::compute_engine_attestation (the complete impl,
    previously dead/unused) swallowed per-file OSError with `pass`, letting an
    in-scope source/dep silently drop out of the hash so two different engine
    states could attest identically, and returned "" on any error silently.

Fix: the live path delegates to the single shared implementation, and unreadable
in-scope files perturb the hash (fold a deterministic marker) instead of
vanishing. Determinism (Daubert bit-for-bit) is preserved.
"""

import builtins
import hashlib
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from vigia.core.bundle_builder import BundleBuilder  # noqa: E402
from vigia.pipeline.pipeline import VigiaPipeline     # noqa: E402

logging.disable(logging.CRITICAL)

_HEX64 = 64


def test_attestation_is_deterministic_bit_for_bit():
    a1 = BundleBuilder.compute_engine_attestation()
    a2 = BundleBuilder.compute_engine_attestation()
    assert a1 == a2
    assert len(a1) == _HEX64
    int(a1, 16)  # valid hex


def test_attestation_covers_more_than_the_pipeline_package():
    """The old live body hashed only vigia/pipeline/. The shared impl covers the
    whole vigia/ tree (incl. the scoring core) + dep manifests, so the two
    hashes must differ — proof the coverage hole is closed."""
    full = BundleBuilder.compute_engine_attestation()
    here = REPO / "vigia" / "pipeline"
    src = []
    for root, _, files in os.walk(here):
        for fn in sorted(files):
            if fn.endswith(".py"):
                try:
                    src.append((Path(root) / fn).read_bytes())
                except OSError:
                    pass
    pipeline_only = hashlib.sha256(b"".join(src)).hexdigest()
    assert full != pipeline_only
    # And caie.py is actually inside the attested tree.
    assert (REPO / "vigia" / "tools" / "caie.py").is_file()


def test_pipeline_attestation_delegates_to_shared_impl():
    """The live _compute_attestation body ignores self and delegates, so calling
    it unbound must return exactly the shared implementation's hash."""
    delegated = VigiaPipeline._compute_attestation(None)
    assert delegated == BundleBuilder.compute_engine_attestation()


def test_unreadable_source_perturbs_hash_not_silently_dropped(monkeypatch):
    d = tempfile.mkdtemp()
    try:
        (Path(d) / "a.py").write_text("print(1)")
        bad = Path(d) / "b.py"
        bad.write_text("print(2)")

        readable = BundleBuilder.compute_engine_attestation(source_dirs=[d], dep_files=[])

        # 2026-07-18: the read failure is INJECTED instead of chmod(bad, 0).
        # Running as root (CI containers, remote runners) chmod 000 does not
        # block reads, so the permission-based simulation degenerated into
        # unreadable == readable and this test failed for environment reasons,
        # not product reasons. Patching open() reproduces the exact failure
        # mode the impl guards (OSError at open) in every environment.
        real_open = builtins.open
        bad_str = str(bad)

        def failing_open(file, *args, **kwargs):
            if isinstance(file, (str, os.PathLike)) and os.fspath(file) == bad_str:
                raise PermissionError(13, "simulated unreadable source", bad_str)
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", failing_open)
        try:
            unreadable = BundleBuilder.compute_engine_attestation(source_dirs=[d], dep_files=[])
        finally:
            monkeypatch.undo()
        bad.unlink()
        absent = BundleBuilder.compute_engine_attestation(source_dirs=[d], dep_files=[])

        # An unreadable in-scope file must change the attestation (not vanish),
        # and must be distinct from the file never having existed.
        assert unreadable != readable
        assert unreadable != absent
        assert unreadable and len(unreadable) == _HEX64
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_total_failure_returns_empty_not_a_fake_hash():
    """A hard failure yields "" (R4 unreachable = honest 'unattested'), never a
    plausible-looking hash. Passing a non-iterable source_dirs forces the outer
    except path."""
    result = BundleBuilder.compute_engine_attestation(source_dirs=123)  # type: ignore[arg-type]
    assert result == ""


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
