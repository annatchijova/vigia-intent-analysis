"""
mount_sift_evidence magic-byte validation.

SECURITY.md has claimed since before this fix: "Magic-byte validation
before mounting (EVF/LVF for E01, script detection for raw)". No such check
ever existed in the code -- mount_sift_evidence only checked the file
EXTENSION (os.path.splitext), which is trivially spoofable: rename any
file to .e01/.dd/.img/.raw and the check passes regardless of actual
content. Mounting is a root-privileged, rate-limited-as-"sensitive"
operation (loop-mounts through ewfmount/mount), so a documented-but-
nonfunctional content check here is the same claim/mechanism mismatch
class as the removed HTTP/SSE auth-token theater.

These tests cover the new _verify_image_magic_bytes() helper directly
(cheap, no root/mount tools required) and one end-to-end check that
mount_sift_evidence rejects a spoofed .e01 before ever reaching
_sanitize_mount_point / sandboxed_execute.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

pytest.importorskip("mcp")

import vigia.vigia_sift_bridge as bridge


class TestVerifyImageMagicBytes:
    def test_valid_ewf_e01_signature_passes(self, tmp_path):
        image = tmp_path / "evidence.e01"
        image.write_bytes(b"EVF\x09\x0d\x0a\xff\x00" + b"\x00" * 100)

        assert bridge._verify_image_magic_bytes(str(image), ".e01") is None

    def test_valid_ewf2_signature_passes(self, tmp_path):
        image = tmp_path / "evidence.ewf"
        image.write_bytes(b"LVF\x09\x0d\x0a\xff\x00" + b"\x00" * 100)

        assert bridge._verify_image_magic_bytes(str(image), ".ewf") is None

    def test_e01_extension_with_wrong_content_is_rejected(self, tmp_path):
        image = tmp_path / "spoofed.e01"
        image.write_bytes(b"NOT_AN_EWF_FILE_AT_ALL" + b"\x00" * 100)

        error = bridge._verify_image_magic_bytes(str(image), ".e01")

        assert error is not None
        assert "EWF" in error

    def test_raw_image_with_arbitrary_content_passes(self, tmp_path):
        """Raw/dd images have no universal signature -- only obvious
        script/executable content is rejected."""
        image = tmp_path / "disk.raw"
        image.write_bytes(b"\x00\x01\x02\x03partition table garbage")

        assert bridge._verify_image_magic_bytes(str(image), ".raw") is None

    def test_raw_extension_shebang_script_is_rejected(self, tmp_path):
        image = tmp_path / "malicious.raw"
        image.write_bytes(b"#!/bin/sh\nrm -rf /\n")

        error = bridge._verify_image_magic_bytes(str(image), ".raw")

        assert error is not None
        assert "script" in error.lower()

    def test_dd_extension_elf_binary_is_rejected(self, tmp_path):
        image = tmp_path / "malicious.dd"
        image.write_bytes(b"\x7fELF" + b"\x00" * 100)

        error = bridge._verify_image_magic_bytes(str(image), ".dd")

        assert error is not None

    def test_img_extension_pe_binary_is_rejected(self, tmp_path):
        image = tmp_path / "malicious.img"
        image.write_bytes(b"MZ" + b"\x00" * 100)

        error = bridge._verify_image_magic_bytes(str(image), ".img")

        assert error is not None

    def test_unreadable_file_reports_error(self, tmp_path):
        missing = tmp_path / "does_not_exist.e01"

        error = bridge._verify_image_magic_bytes(str(missing), ".e01")

        assert error is not None


class TestMountRejectsSpoofedExtension:
    def test_mount_sift_evidence_rejects_spoofed_e01(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        evidence_root = tmp_path / "evidence"
        work_root = tmp_path / "work"
        mount_root = work_root / "mounted"
        evidence_root.mkdir()
        mount_root.mkdir(parents=True)
        monkeypatch.setattr(bridge, "EVIDENCE_BASE_DIR", str(evidence_root))
        monkeypatch.setattr(bridge, "WORK_BASE_DIR", str(work_root))
        monkeypatch.setattr(bridge, "_MOUNT_ROOT", str(mount_root))
        monkeypatch.setattr(bridge.os, "geteuid", lambda: 0)

        # A file that is definitely not an EWF image, wearing a .e01 extension.
        image = evidence_root / "spoofed.e01"
        image.write_bytes(b"this is not an EWF image, just renamed")

        response = asyncio.run(
            bridge.mount_sift_evidence.__wrapped__(str(image), "spoofed-target")
        )

        assert response.get("security_block") is True
        assert "EWF" in response["error"]
        # Must not have created a mount leaf -- rejected before _sanitize_mount_point.
        assert not (mount_root / "spoofed-target").exists()
