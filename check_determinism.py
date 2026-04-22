#!/usr/bin/env python3
"""
check_determinism.py — VIGIA Determinism Verification Script
=============================================================
Runs the same analysis N times on the same evidence file and compares
the SHA-256 hashes of the generated reports. If hashes diverge, the
system alerts about non-determinism in the model or analysis pipeline.

This is critical for forensic admissibility: the same evidence must
produce the same findings regardless of when the analysis is run.

Usage:
    python3 check_determinism.py [evidence_file] [--runs N] [--tool TOOL]

    evidence_file : path to the file to analyze (default: uses test fixture)
    --runs N      : number of analysis runs (default: 3, max: 10)
    --tool TOOL   : MCP tool to test (default: calculate_shannon_entropy)

Exit codes:
    0 — All runs produced identical results (deterministic)
    1 — Non-determinism detected (hashes differ between runs)
    2 — Error (file not found, tool failure, etc.)

For SANS hackathon:
    make check-determinism
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from pathlib import Path

# ── Resolve imports ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _hash_result(result: dict | list | str) -> str:
    """
    Produce a deterministic SHA-256 hash of a tool result.

    Strips fields that are expected to vary between runs:
    timestamp, process_id, investigation_id, _hmac, _prev_hmac.
    """
    VOLATILE_KEYS = {
        "timestamp", "process_id", "investigation_id",
        "_hmac", "_prev_hmac", "timestamp_read",
    }

    def _strip_volatile(obj):
        if isinstance(obj, dict):
            return {
                k: _strip_volatile(v)
                for k, v in sorted(obj.items())
                if k not in VOLATILE_KEYS
            }
        if isinstance(obj, list):
            return [_strip_volatile(item) for item in obj]
        return obj

    cleaned = _strip_volatile(result)
    canonical = json.dumps(cleaned, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def _run_tool(tool_name: str, kwargs: dict) -> dict:
    """
    Import and execute a VIGIA tool by name.
    Returns the tool's result dict.
    """
    # Map tool names to their module locations
    TOOL_MAP = {
        "calculate_shannon_entropy": (
            "vigia_sift_bridge", "calculate_shannon_entropy"
        ),
        "generate_forensic_hash": (
            "vigia_sift_bridge", "generate_forensic_hash"
        ),
        "audit_document_integrity": (
            "vigia.tools.document_integrity", "audit_document_integrity"
        ),
        "analyze_image_layers": (
            "vigia.tools.document_integrity", "analyze_image_layers"
        ),
        "detect_document_geometry": (
            "vigia.tools.document_integrity", "detect_document_geometry"
        ),
        "vision_intent_audit": (
            "vigia.tools.vision_audit", "vision_intent_audit"
        ),
    }

    if tool_name not in TOOL_MAP:
        return {"error": f"Unknown tool: {tool_name}. Available: {list(TOOL_MAP.keys())}"}

    module_path, func_name = TOOL_MAP[tool_name]

    try:
        import importlib
        mod = importlib.import_module(module_path)
        func = getattr(mod, func_name)
    except (ImportError, AttributeError) as exc:
        return {"error": f"Cannot import {module_path}.{func_name}: {exc}"}

    try:
        result = await func(**kwargs)
        return result
    except Exception as exc:
        return {"error": f"Tool execution failed: {exc}"}


def _create_test_fixture() -> str:
    """
    Create a minimal test file for determinism checking when no
    evidence file is provided.
    """
    import tempfile
    content = (
        "This is a VIGIA determinism test fixture.\n"
        "It contains predictable content for hash comparison.\n"
        "The quick brown fox jumps over the lazy dog.\n"
        "Timestamp: FIXED — do not modify.\n"
        "Case ID: DETERMINISM-CHECK-001\n"
    ) * 10  # Repeat for enough entropy

    fd, path = tempfile.mkstemp(prefix="vigia_determinism_", suffix=".txt")
    os.write(fd, content.encode("utf-8"))
    os.close(fd)
    return path


def _build_kwargs(tool_name: str, evidence_path: str) -> dict:
    """Build appropriate kwargs for each tool."""
    if tool_name == "calculate_shannon_entropy":
        with open(evidence_path, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
        return {"data": data}
    elif tool_name == "generate_forensic_hash":
        return {"file_path": evidence_path}
    elif tool_name in ("audit_document_integrity", "detect_document_geometry"):
        return {"file_path": evidence_path}
    elif tool_name == "analyze_image_layers":
        return {"file_path": evidence_path}
    elif tool_name == "vision_intent_audit":
        return {"image_path": evidence_path}
    return {"path": evidence_path}


async def check_determinism(
    evidence_path: str,
    tool_name: str = "calculate_shannon_entropy",
    num_runs: int = 3,
    verbose: bool = True,
) -> dict:
    """
    Run the same tool N times on the same evidence and compare results.

    Returns:
        {
            "deterministic": bool,
            "runs": int,
            "hashes": [str, ...],
            "unique_hashes": int,
            "tool": str,
            "evidence_path": str,
            "results": [dict, ...],  # only if verbose
        }
    """
    if not os.path.exists(evidence_path):
        return {"error": f"Evidence file not found: {evidence_path}"}

    kwargs = _build_kwargs(tool_name, evidence_path)
    hashes = []
    results = []
    timings = []

    for run_num in range(1, num_runs + 1):
        t0 = time.monotonic()
        result = await _run_tool(tool_name, kwargs)
        elapsed = time.monotonic() - t0
        timings.append(elapsed)

        if isinstance(result, dict) and result.get("error"):
            return {
                "error": f"Run {run_num} failed: {result['error']}",
                "run": run_num,
                "tool": tool_name,
            }

        h = _hash_result(result)
        hashes.append(h)
        results.append(result)

        if verbose:
            print(
                f"  Run {run_num}/{num_runs}: hash={h[:16]}... "
                f"({elapsed:.3f}s)",
                file=sys.stderr,
            )

    unique = len(set(hashes))
    deterministic = unique == 1

    report = {
        "deterministic": deterministic,
        "runs": num_runs,
        "hashes": hashes,
        "unique_hashes": unique,
        "tool": tool_name,
        "evidence_path": evidence_path,
        "evidence_sha256": hashlib.sha256(
            open(evidence_path, "rb").read()
        ).hexdigest(),
        "timings_seconds": [round(t, 4) for t in timings],
    }

    if not deterministic:
        report["alert"] = (
            "NON-DETERMINISM DETECTED. "
            f"The tool '{tool_name}' produced {unique} different results "
            f"from {num_runs} identical runs. "
            "This compromises forensic reproducibility. "
            "Possible causes: floating-point instability, random seeds, "
            "timestamp leakage in results, or LLM temperature > 0."
        )
        # Show which runs diverged
        divergences = []
        baseline = hashes[0]
        for i, h in enumerate(hashes[1:], 2):
            if h != baseline:
                divergences.append({"run": i, "hash": h, "baseline_hash": baseline})
        report["divergences"] = divergences

    if verbose:
        report["results_preview"] = [
            {k: v for k, v in r.items() if k not in ("raw_response",)}
            if isinstance(r, dict) else r
            for r in results
        ]

    return report


def main():
    parser = argparse.ArgumentParser(
        description="VIGIA Determinism Verification",
        epilog="Exit code 0 = deterministic, 1 = non-deterministic, 2 = error",
    )
    parser.add_argument(
        "evidence_file",
        nargs="?",
        default=None,
        help="Path to evidence file (uses test fixture if not provided)",
    )
    parser.add_argument(
        "--runs", "-n",
        type=int,
        default=3,
        help="Number of analysis runs (default: 3, max: 10)",
    )
    parser.add_argument(
        "--tool", "-t",
        default="calculate_shannon_entropy",
        help="MCP tool to test (default: calculate_shannon_entropy)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write JSON report to file (default: stdout)",
    )

    args = parser.parse_args()

    # Validate runs
    num_runs = max(2, min(args.runs, 10))

    # Resolve evidence file
    cleanup_fixture = False
    if args.evidence_file:
        evidence_path = args.evidence_file
        if not os.path.exists(evidence_path):
            print(f"[ERROR] Evidence file not found: {evidence_path}", file=sys.stderr)
            sys.exit(2)
    else:
        evidence_path = _create_test_fixture()
        cleanup_fixture = True
        if not args.quiet:
            print(
                f"[VIGIA] No evidence file specified. Using test fixture: {evidence_path}",
                file=sys.stderr,
            )

    if not args.quiet:
        print(
            f"[VIGIA] Determinism check: tool={args.tool}, "
            f"runs={num_runs}, evidence={evidence_path}",
            file=sys.stderr,
        )

    try:
        report = asyncio.run(
            check_determinism(
                evidence_path=evidence_path,
                tool_name=args.tool,
                num_runs=num_runs,
                verbose=not args.quiet,
            )
        )
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(2)
    finally:
        if cleanup_fixture and os.path.exists(evidence_path):
            os.unlink(evidence_path)

    # Output report
    report_json = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_json + "\n")
        if not args.quiet:
            print(f"[VIGIA] Report written to {args.output}", file=sys.stderr)
    else:
        print(report_json)

    # Exit code
    if "error" in report:
        print(f"\n[ERROR] {report['error']}", file=sys.stderr)
        sys.exit(2)
    elif report["deterministic"]:
        if not args.quiet:
            print(
                f"\n[VIGIA] DETERMINISTIC: {num_runs} runs produced identical results.",
                file=sys.stderr,
            )
        sys.exit(0)
    else:
        print(
            f"\n[VIGIA] NON-DETERMINISM DETECTED: "
            f"{report['unique_hashes']} unique results from {num_runs} runs.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
