#!/usr/bin/env python3
"""
vigia_prepare_evidence.py — Forensic evidence preparation helper for VIGÍA.

This is a STANDALONE utility. It is deliberately NOT part of the forensic
analysis engine:

  * It does not import vigia_agent.py or any SIFT / CAIE / scorer module.
  * vigia_agent.py does not import this file.
  * A bug in image-format detection here can never contaminate the
    Fraction-pure verdict path.

Responsibility split:
  * VIGÍA Agent          → reasons about already-extracted evidence.
  * This helper          → prepares a forensic image so the agent can read it.

What it does (read-only, never executes anything privileged):
  1. Detects the image format (today: EWF / .E01; designed to extend).
  2. Displays acquisition metadata via `ewfinfo` so the examiner can confirm
     they are looking at the right image before mounting anything.
  3. Mounts the EWF container read-only with `ewfmount` IF that is possible
     without elevated privileges. If it is not, it prints the exact command
     for the examiner to run and asks them to re-invoke with --already-mounted.
  4. Runs `mmls` (unprivileged) on the raw `ewf1` device, parses the partition
     table, and identifies the most likely evidence partition.
  5. Computes the byte offset using the sector size REPORTED by mmls (it does
     not assume 512).
  6. Prints the exact `sudo mount` command for the examiner to run with their
     own eyes — this tool never elevates privileges itself.
  7. Prints the follow-up vigia_agent.py invocation.

Design constraints (intentional):
  * Non-interactive: no input() prompts, no clipboard, no Y/n questions.
  * Standard library only (subprocess, shutil, argparse, etc.).
  * Fail loud: missing tools or unparsable output produce a clear error, never
    a silent best-effort guess.
  * If this script mounts anything itself, it ALWAYS unmounts on exit.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# ──────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────

# External tools this helper depends on.
_TOOL_EWFINFO = "ewfinfo"
_TOOL_EWFMOUNT = "ewfmount"
_TOOL_MMLS = "mmls"
_TOOL_FUSERMOUNT = "fusermount"

# Partition descriptions that are NOT the primary evidence filesystem.
# Matched case-insensitively as substrings against the mmls description column.
_EXCLUDED_PARTITION_KEYWORDS = (
    "unallocated",
    "meta",
    "primary table",
    "gpt header",
    "safety table",
    "efi system partition",
    "efi",
    "recovery",
    "microsoft reserved",
    "extended",
)

# Default sector size, used only if mmls does not report one (it normally does).
_DEFAULT_SECTOR_BYTES = 512


# ──────────────────────────────────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────────────────────────────────

@dataclass
class Partition:
    """A single row from the mmls partition table."""
    index: int
    slot: str
    start_sector: int
    end_sector: int
    length_sectors: int
    description: str

    def is_excluded(self) -> bool:
        desc = self.description.lower()
        return any(kw in desc for kw in _EXCLUDED_PARTITION_KEYWORDS)


# ──────────────────────────────────────────────────────────────────────────
# Tool availability
# ──────────────────────────────────────────────────────────────────────────

def _require_tool(name: str) -> str:
    """Return the resolved path to a tool, or raise with an install hint."""
    path = shutil.which(name)
    if path is None:
        raise RuntimeError(
            f"Required tool '{name}' not found in PATH.\n"
            f"  Install with: sudo apt install libewf-tools sleuthkit"
        )
    return path


# ──────────────────────────────────────────────────────────────────────────
# Image format detection (extensible)
# ──────────────────────────────────────────────────────────────────────────

def detect_image_format(image_path: Path) -> str:
    """
    Identify the forensic image format.

    Today only EWF (.E01) is supported. This function is intentionally
    isolated so future formats (VMDK, AFF4, QCOW2, VHDX, raw dd, ...) can be
    added here without touching the rest of the tool — and so an unsupported
    format fails loudly rather than being mishandled downstream.
    """
    suffix = image_path.suffix.lower()
    if suffix in (".e01", ".ewf"):
        return "ewf"
    # First segment of a multi-part EWF set is sometimes .E01 with later
    # segments .E02, .E03, ...; only the first segment is passed here.
    raise RuntimeError(
        f"Unsupported image format: '{suffix or '(no extension)'}'.\n"
        f"  This helper currently supports EWF images (.E01).\n"
        f"  For other formats, mount manually and point vigia_agent.py at the "
        f"mounted filesystem."
    )


# ──────────────────────────────────────────────────────────────────────────
# ewfinfo — acquisition metadata (informational)
# ──────────────────────────────────────────────────────────────────────────

def show_acquisition_metadata(image_path: Path) -> None:
    """Run ewfinfo and echo its output so the examiner can confirm the image."""
    ewfinfo = _require_tool(_TOOL_EWFINFO)
    print("── Acquisition metadata (ewfinfo) ─────────────────────────────")
    try:
        proc = subprocess.run(
            [ewfinfo, str(image_path)],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        print("  (ewfinfo timed out after 60s — skipping metadata display)")
        return
    if proc.returncode != 0:
        # Informational step: report but do not abort the whole run.
        print(f"  (ewfinfo exited {proc.returncode}; stderr below)")
        if proc.stderr.strip():
            print("  " + proc.stderr.strip().replace("\n", "\n  "))
        return
    print(proc.stdout.rstrip())
    print("───────────────────────────────────────────────────────────────")


# ──────────────────────────────────────────────────────────────────────────
# ewfmount — try unprivileged; fall back to instructions
# ──────────────────────────────────────────────────────────────────────────

def try_ewfmount(image_path: Path, mount_dir: Path,
                 timeout_s: int = 120) -> bool:
    """
    Attempt to mount the EWF container without elevated privileges.

    Returns True if the ewf1 device is available under mount_dir afterwards,
    False otherwise (e.g. ewfmount requires sudo on this system). Never raises
    on a permission failure — that is an expected outcome we handle by falling
    back to printed instructions.

    Note: ewfmount creates a FUSE filesystem and returns quickly; it does NOT
    read the whole image up front (reads are lazy/on-demand). The timeout
    exists for pathological cases (very slow or networked storage), not image
    size, and is configurable via --mount-timeout.
    """
    ewfmount = _require_tool(_TOOL_EWFMOUNT)
    try:
        proc = subprocess.run(
            [ewfmount, str(image_path), str(mount_dir)],
            capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        print(f"  (ewfmount timed out after {timeout_s}s; "
              f"raise it with --mount-timeout if storage is slow)")
        return False
    ewf1 = mount_dir / "ewf1"
    if proc.returncode == 0 and ewf1.exists():
        return True
    # Did not work unprivileged — surface why, for transparency.
    if proc.stderr.strip():
        first_line = proc.stderr.strip().splitlines()[0]
        print(f"  (ewfmount could not run unprivileged: {first_line})")
    return False


def unmount_ewf(mount_dir: Path) -> None:
    """Unmount a FUSE mount created by this script. Best-effort, never raises."""
    fusermount = shutil.which(_TOOL_FUSERMOUNT)
    if fusermount is not None:
        subprocess.run(
            [fusermount, "-u", str(mount_dir)],
            capture_output=True, text=True,
        )


def print_manual_ewfmount_instructions(image_path: Path, case_name: str) -> None:
    """When ewfmount needs sudo, tell the examiner exactly what to run."""
    mp = f"/mnt/vigia_{case_name}_ewf"
    print()
    print("ewfmount requires elevated privileges on this system.")
    print("Run these commands yourself, then re-invoke this helper:")
    print()
    print(f"  sudo mkdir -p {mp}")
    print(f"  sudo ewfmount {image_path} {mp}")
    print()
    print("Then:")
    print(f"  python3 vigia_prepare_evidence.py {image_path} "
          f"--already-mounted {mp}")
    print()
    print("(The helper will read the partition table and compute the mount "
          "offset for you — it still will not execute anything privileged.)")


# ──────────────────────────────────────────────────────────────────────────
# mmls — parse the partition table
# ──────────────────────────────────────────────────────────────────────────

# Matches a partition row, e.g.:
#   002:  000:000   0000002048   0001023999   0001021952   NTFS / exFAT (0x07)
# Index width is not fixed: mmls widens it for tables with many partitions
# (GPT can hold 128+). \d{2,} covers 2-digit and wider indices.
_MMLS_ROW_RE = re.compile(
    r"^(?P<index>\d{2,}):\s+"
    r"(?P<slot>\S+)\s+"
    r"(?P<start>\d+)\s+"
    r"(?P<end>\d+)\s+"
    r"(?P<length>\d+)\s+"
    r"(?P<description>.+?)\s*$"
)

# Matches the sector-size declaration, e.g. "Units are in 512-byte sectors".
_MMLS_SECTOR_RE = re.compile(r"Units are in (?P<bytes>\d+)-byte sectors")


def run_mmls(ewf1_path: Path) -> str:
    """Run mmls (unprivileged) on the raw device and return stdout.

    LC_ALL=C forces English, locale-independent output so the sector-size
    line ("Units are in N-byte sectors") is parseable regardless of the
    examiner's system locale. Without this, a localised mmls would silently
    fall through to the default sector size and could yield a wrong offset.
    """
    mmls = _require_tool(_TOOL_MMLS)
    env = dict(os.environ, LC_ALL="C", LANG="C")
    try:
        proc = subprocess.run(
            [mmls, str(ewf1_path)],
            capture_output=True, text=True, timeout=120, env=env,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("mmls timed out after 120s.")
    if proc.returncode != 0:
        msg = proc.stderr.strip() or f"mmls exited {proc.returncode}"
        raise RuntimeError(
            f"mmls failed on {ewf1_path}: {msg}\n"
            f"  The image may use a partitioning scheme mmls does not "
            f"recognise, or may be a single unpartitioned volume."
        )
    return proc.stdout


def parse_mmls(output: str) -> tuple[List[Partition], int]:
    """
    Parse mmls output into a list of Partition rows and the sector size.

    Raises if no partition rows are found (fail loud — do not return an empty
    result that looks like success).
    """
    sector_bytes = _DEFAULT_SECTOR_BYTES
    sector_reported = False
    partitions: List[Partition] = []

    for line in output.splitlines():
        m_sector = _MMLS_SECTOR_RE.search(line)
        if m_sector:
            sector_bytes = int(m_sector.group("bytes"))
            sector_reported = True
            continue
        m_row = _MMLS_ROW_RE.match(line)
        if m_row:
            partitions.append(Partition(
                index=int(m_row.group("index")),
                slot=m_row.group("slot"),
                start_sector=int(m_row.group("start")),
                end_sector=int(m_row.group("end")),
                length_sectors=int(m_row.group("length")),
                description=m_row.group("description").strip(),
            ))

    if not partitions:
        raise RuntimeError(
            "mmls produced no recognisable partition rows.\n"
            "  The volume may be unpartitioned (a single filesystem). In that "
            "case mount the ewf1 device directly with offset=0."
        )
    if not sector_reported:
        print("  (warning: mmls did not report a sector size; "
              f"assuming {_DEFAULT_SECTOR_BYTES} bytes)")
    return partitions, sector_bytes


# ──────────────────────────────────────────────────────────────────────────
# Partition selection heuristic
# ──────────────────────────────────────────────────────────────────────────

def select_partition(partitions: List[Partition]) -> Optional[Partition]:
    """
    Recommend the most likely evidence partition: the largest one whose
    description is not in the exclusion set.

    Returns None when the choice is ambiguous (the two largest candidates are
    within 20% of each other in size) or when no candidate qualifies. In those
    cases the caller lists everything and recommends nothing — better to make
    the examiner choose than to silently pick wrong.
    """
    candidates = [p for p in partitions if not p.is_excluded()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.length_sectors, reverse=True)
    if len(candidates) >= 2:
        largest = candidates[0].length_sectors
        runner_up = candidates[1].length_sectors
        if largest > 0 and (runner_up / largest) > 0.80:
            # Two comparably-sized candidates → ambiguous, do not guess.
            return None
    return candidates[0]


def print_partition_table(partitions: List[Partition],
                          recommended: Optional[Partition],
                          sector_bytes: int) -> None:
    print()
    print(f"── Partition table (sector size: {sector_bytes} bytes) ─────────")
    print(f"  {'idx':>3}  {'start':>12}  {'length':>12}  description")
    for p in partitions:
        marker = "  <- recommended" if (recommended is not None
                                        and p.index == recommended.index) else ""
        print(f"  {p.index:>3}  {p.start_sector:>12}  "
              f"{p.length_sectors:>12}  {p.description}{marker}")
    print("───────────────────────────────────────────────────────────────")


# ──────────────────────────────────────────────────────────────────────────
# Output: the mount command and next step
# ──────────────────────────────────────────────────────────────────────────

def print_mount_command(ewf1_path: Path,
                        partition: Partition,
                        sector_bytes: int,
                        case_name: str) -> None:
    offset_bytes = partition.start_sector * sector_bytes
    fs_mount = f"/mnt/vigia_{case_name}_fs"
    print()
    print("Recommended mount command (run it yourself — this helper will not):")
    print()
    print(f"  sudo mkdir -p {fs_mount}")
    print(f"  sudo mount -o ro,noexec,nosuid,nodev,offset={offset_bytes} "
          f"{ewf1_path} {fs_mount}")
    print()
    print(f"  # partition {partition.index}: {partition.description}")
    print(f"  # offset = {partition.start_sector} sectors "
          f"× {sector_bytes} bytes = {offset_bytes} bytes")
    print()
    print("Then analyse with VIGÍA:")
    print()
    print(f"  python3 vigia_agent.py --evidence {fs_mount} "
          f"--case-id <YOUR_CASE_ID>")
    print()


def print_ambiguous_guidance(ewf1_path: Path, sector_bytes: int) -> None:
    print()
    print("No single partition could be recommended unambiguously.")
    print("Pick the evidence partition from the table above, then mount it:")
    print()
    print(f"  sudo mkdir -p /mnt/vigia_case_fs")
    print(f"  sudo mount -o ro,noexec,nosuid,nodev,"
          f"offset=$((<START_SECTOR> * {sector_bytes})) "
          f"{ewf1_path} /mnt/vigia_case_fs")
    print()
    print("  # replace <START_SECTOR> with the 'start' value of your chosen "
          "partition")
    print()


# ──────────────────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────────────────

def derive_case_name(image_path: Path) -> str:
    """Build a filesystem-safe slug from the image filename stem.

    Uses a denylist (replace anything that is not a Unicode word char or
    hyphen) rather than an ASCII allowlist, so non-Latin names — e.g. Cyrillic
    case names — are preserved instead of being wiped to the fallback. \\w under
    Python 3 re is Unicode-aware and matches letters from any script plus
    digits and underscore; none of those are shell metacharacters, so the slug
    remains safe to embed in the printed mount path.
    """
    stem = image_path.stem
    slug = re.sub(r"[^\w-]+", "_", stem, flags=re.UNICODE).strip("_")
    return slug or "case"


def analyse_mounted_device(ewf1_path: Path, case_name: str) -> int:
    """Run mmls on an available ewf1 device and print mount guidance."""
    if not ewf1_path.exists():
        raise RuntimeError(
            f"Expected raw device not found: {ewf1_path}\n"
            f"  Is the EWF container actually mounted at its parent directory?"
        )
    output = run_mmls(ewf1_path)
    partitions, sector_bytes = parse_mmls(output)
    recommended = select_partition(partitions)
    print_partition_table(partitions, recommended, sector_bytes)
    if recommended is None:
        print_ambiguous_guidance(ewf1_path, sector_bytes)
    else:
        print_mount_command(ewf1_path, recommended, sector_bytes, case_name)
    return 0


def run(image_arg: str, already_mounted: Optional[str],
        mount_timeout: int = 120) -> int:
    image_path = Path(image_arg).expanduser().resolve()

    # --already-mounted: the examiner ran ewfmount themselves; just analyse.
    if already_mounted is not None:
        mount_dir = Path(already_mounted).expanduser().resolve()
        case_name = derive_case_name(image_path)
        show_acquisition_metadata(image_path)
        return analyse_mounted_device(mount_dir / "ewf1", case_name)

    if not image_path.is_file():
        raise RuntimeError(f"Image file not found: {image_path}")

    image_format = detect_image_format(image_path)
    if image_format != "ewf":  # defensive; detect_image_format already guards
        raise RuntimeError(f"Unhandled format '{image_format}'.")

    case_name = derive_case_name(image_path)
    show_acquisition_metadata(image_path)

    # Try to mount the EWF container unprivileged. Clean up no matter what.
    tmp_mount = Path(tempfile.mkdtemp(prefix=f"vigia_{case_name}_ewf_"))
    mounted_by_us = False
    try:
        mounted_by_us = try_ewfmount(image_path, tmp_mount, mount_timeout)
        if not mounted_by_us:
            print_manual_ewfmount_instructions(image_path, case_name)
            return 0
        return analyse_mounted_device(tmp_mount / "ewf1", case_name)
    finally:
        if mounted_by_us:
            unmount_ewf(tmp_mount)
        try:
            tmp_mount.rmdir()
        except OSError:
            pass  # not empty / already gone — leave it, do not mask the result


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="vigia_prepare_evidence.py",
        description="Prepare a forensic image for analysis by VIGÍA. "
                    "Read-only; never executes privileged commands.",
    )
    parser.add_argument(
        "image",
        help="Path to the forensic image (currently: EWF / .E01).",
    )
    parser.add_argument(
        "--already-mounted",
        metavar="DIR",
        default=None,
        help="Directory where you already mounted the EWF container with "
             "ewfmount (it should contain an 'ewf1' file). Use this if "
             "ewfmount required sudo on your system.",
    )
    parser.add_argument(
        "--mount-timeout",
        metavar="SECONDS",
        type=int,
        default=120,
        help="Timeout for the ewfmount attempt (default: 120). Raise it only "
             "if evidence sits on slow or networked storage; image size alone "
             "does not require a higher value (FUSE reads are lazy).",
    )
    args = parser.parse_args()

    try:
        return run(args.image, args.already_mounted, args.mount_timeout)
    except RuntimeError as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[ABORTED]", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
