"""B-164/B-173 — MCP image mounting must have reachable, confined roots.

``mount_sift_evidence`` used the evidence-root sanitizer for *both* its
source image and its target, then separately required the target to be under
``/mnt/analysis``.  Unless the evidence root itself was ``/mnt/analysis``, no
request could reach the privilege check or the mount operation.

The repaired contract keeps the image in the immutable evidence root and
creates a private leaf beneath a distinct operational mount root. That makes
the mounted filesystem available to normal evidence-reading tools without
giving the MCP caller an arbitrary privileged mount path or mutating evidence.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

pytest.importorskip("mcp.server.fastmcp")

import vigia.vigia_sift_bridge as bridge


def _isolated_mount_roots(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    evidence_root = tmp_path / "evidence"
    work_root = tmp_path / "work"
    mount_root = work_root / "mounted"
    evidence_root.mkdir()
    mount_root.mkdir(parents=True)
    monkeypatch.setattr(bridge, "EVIDENCE_BASE_DIR", str(evidence_root))
    monkeypatch.setattr(bridge, "WORK_BASE_DIR", str(work_root))
    monkeypatch.setattr(bridge, "_MOUNT_ROOT", str(mount_root))
    return evidence_root, mount_root


def test_b164_creates_a_private_mount_leaf_outside_evidence(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The target is both reachable and readable through evidence tools."""
    _evidence_root, mount_root = _isolated_mount_roots(monkeypatch, tmp_path)

    target = bridge._sanitize_mount_point("nexus5")

    assert target == str(mount_root / "nexus5")
    assert Path(target).is_dir()
    # Later MCP readers accept the controlled mount root as a read-only source.
    assert bridge._sanitize_path_local(target) == target


@pytest.mark.parametrize(
    "untrusted_target",
    ["", ".", "..", "../escape", "/mnt/analysis", "nested/escape", "bad\x00leaf"],
)
def test_b164_rejects_untrusted_or_ambiguous_mount_targets(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, untrusted_target: str
) -> None:
    _isolated_mount_roots(monkeypatch, tmp_path)

    with pytest.raises(ValueError, match="mount_point"):
        bridge._sanitize_mount_point(untrusted_target)


@pytest.mark.parametrize("kind", ["regular_file", "symlink"])
def test_b164_rejects_an_existing_non_directory_mount_leaf(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, kind: str
) -> None:
    _evidence_root, mount_root = _isolated_mount_roots(monkeypatch, tmp_path)
    candidate = mount_root / "nexus5"
    if kind == "regular_file":
        candidate.write_text("not a mount point", encoding="utf-8")
    else:
        safe_directory = mount_root / "other"
        safe_directory.mkdir()
        candidate.symlink_to(safe_directory, target_is_directory=True)

    with pytest.raises(ValueError, match="mount_point"):
        bridge._sanitize_mount_point("nexus5")


def test_b164_reaches_the_privilege_gate_instead_of_an_impossible_path_gate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A valid request now reaches the real privilege boundary before mounting."""
    evidence_root, _mount_root = _isolated_mount_roots(monkeypatch, tmp_path)
    image = evidence_root / "nexus5.raw"
    image.write_bytes(b"not mounted during this unit test")
    monkeypatch.setattr(bridge.os, "geteuid", lambda: 1000)

    response = asyncio.run(
        bridge.mount_sift_evidence.__wrapped__(str(image), "nexus5")
    )

    assert response == {
        "error": "Root privileges required for mounting images. Re-run as root or via sudo."
    }
