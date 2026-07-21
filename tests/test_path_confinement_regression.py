"""Regression coverage for forensic input-path confinement.

These tests use only pytest-owned temporary fixtures.  They exercise the
boundary before any evidence parser or external forensic binary is invoked.
"""

from __future__ import annotations

import importlib

import pytest

from vigia.core.path_guard import PathGuard


def test_path_guard_rejects_sibling_with_allowed_prefix(tmp_path):
    allowed_root = tmp_path / "vigia"
    allowed_root.mkdir()
    sibling = tmp_path / "vigia-neighbor"
    sibling.mkdir()
    outside = sibling / "outside.bin"
    outside.write_bytes(b"outside")

    guard = PathGuard(allowed_base_paths=[allowed_root])

    result = guard.validate(str(outside))

    assert not result.valid
    assert result.reason == "OUTSIDE_ALLOWLIST"
    with pytest.raises(PermissionError, match="OUTSIDE_ALLOWLIST"):
        guard.safe_read(str(outside))


def test_path_guard_rejects_raw_parent_traversal_even_if_it_lands_on_a_file(tmp_path):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_root = tmp_path / "outside"
    outside_root.mkdir()
    outside = outside_root / "fixture.bin"
    outside.write_bytes(b"outside")
    traversal = allowed_root / ".." / outside_root.name / outside.name

    result = PathGuard(allowed_base_paths=[allowed_root]).validate(str(traversal))

    assert not result.valid
    assert result.reason == "PATH_TRAVERSAL"


def test_path_guard_still_reads_regular_descendant_inside_allowed_root(tmp_path):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    artifact = allowed_root / "artifact.bin"
    artifact.write_bytes(b"trusted-fixture")

    guard = PathGuard(allowed_base_paths=[allowed_root])

    assert guard.validate(str(artifact)).valid
    assert guard.safe_read(str(artifact)) == b"trusted-fixture"


@pytest.mark.parametrize(
    ("module_name", "interface_name"),
    [
        ("vigia.sift.memory_forensics", "Volatility3Interface"),
        ("vigia.sift.registry_timeline_reconstructor", "RegRipperInterface"),
    ],
)
def test_engine_validators_reject_existing_file_outside_configured_allowlist(
    tmp_path, monkeypatch, module_name, interface_name
):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"outside")
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, "ALLOWED_BASE_PATHS", [allowed_root])
    interface = getattr(module, interface_name)

    with pytest.raises(PermissionError, match="outside configured allowlist"):
        interface._validate_path(str(outside))


@pytest.mark.parametrize(
    ("module_name", "interface_name"),
    [
        ("vigia.sift.memory_forensics", "Volatility3Interface"),
        ("vigia.sift.registry_timeline_reconstructor", "RegRipperInterface"),
    ],
)
def test_engine_validators_accept_regular_file_inside_configured_allowlist(
    tmp_path, monkeypatch, module_name, interface_name
):
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    artifact = allowed_root / "artifact.bin"
    artifact.write_bytes(b"fixture")
    module = importlib.import_module(module_name)
    monkeypatch.setattr(module, "ALLOWED_BASE_PATHS", [allowed_root])
    interface = getattr(module, interface_name)

    assert interface._validate_path(str(artifact)) == artifact.resolve()
