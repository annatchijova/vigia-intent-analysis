# vigia/cli.py — Evidence Bundle Verifier (directory-based manifest format)
#
# B-120 (2026-07-14): this is the `vigia` entry point registered in
# pyproject.toml. It verifies directory-based bundles (manifest.json +
# ledger.json), NOT the sealed ForensicBundle JSON produced by the pipeline.
#
# WHAT THIS VERIFIES:
#   - File integrity: SHA-256 of each file vs manifest.json declarations
#   - Ledger chain: prev_hash -> hash chain continuity (legacy schema,
#     NO HMAC — see warning in verify_ledger)
#   - Consistency: required files present in manifest
#
# WHAT THIS DOES NOT VERIFY:
#   - PKI signatures (not implemented — returns FAIL, not a false PASS)
#   - RFC 3161 timestamps (not implemented — returns FAIL, not a false PASS)
#   - HMAC-protected tool execution chains (use verify_tool_log.py)
#   - Sealed ForensicBundle integrity (use forensics/verify_ebs_v1.py)

import argparse
import json
import hashlib
import os
import sys
from typing import Dict, List

# ------------------------------------------------------------------
# Utils
# ------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: str) -> Dict:
    with open(path, "r") as f:
        return json.load(f)


# ------------------------------------------------------------------
# Manifest Verification
# ------------------------------------------------------------------

def verify_manifest(bundle_path: str) -> Dict:
    manifest_path = os.path.join(bundle_path, "manifest.json")
    manifest = load_json(manifest_path)
    
    results = []
    
    for entry in manifest.get("files", []):
        file_path = os.path.join(bundle_path, entry["name"])
        
        if not os.path.exists(file_path):
            results.append((entry["name"], False, "missing"))
            continue
        
        computed = sha256_file(file_path)
        expected = entry["sha256"]
        
        if computed == expected:
            results.append((entry["name"], True, "ok"))
        else:
            results.append((entry["name"], False, "hash mismatch"))
    
    return {
        "status": all(r[1] for r in results),
        "details": results
    }


# ------------------------------------------------------------------
# Ledger Verification (hash chain)
# ------------------------------------------------------------------

def verify_ledger(bundle_path: str) -> Dict:
    """Verify ledger hash chain (legacy schema, NO HMAC).

    WARNING: this verifies internal chain consistency only (prev_hash ->
    hash linkage). It does NOT use HMAC, so an attacker with write access
    can rewrite and recompute the entire chain undetected. For bundles
    produced by the current pipeline, use verify_tool_log.py (chain v2
    with HMAC) instead.
    """
    ledger_path = os.path.join(bundle_path, "ledger.json")

    if not os.path.exists(ledger_path):
        return {"status": False, "error": "ledger missing"}

    ledger = load_json(ledger_path)
    prev_hash = "0" * 64

    for i, entry in enumerate(ledger):
        data = {
            "timestamp": entry["timestamp"],
            "event": entry["event"],
            "prev_hash": entry["prev_hash"]
        }

        serialized = json.dumps(data, sort_keys=True)
        computed = hashlib.sha256(serialized.encode()).hexdigest()

        if entry["prev_hash"] != prev_hash:
            return {"status": False, "error": f"broken chain at {i}"}

        if entry["hash"] != computed:
            return {"status": False, "error": f"invalid hash at {i}"}

        prev_hash = entry["hash"]

    return {
        "status": True,
        "warning": (
            "Legacy schema (SHA-256 chain without HMAC). An attacker with "
            "write access can rewrite and recompute this chain undetected. "
            "For new bundles use verify_tool_log.py (chain v2 with HMAC)."
        ),
    }


# ------------------------------------------------------------------
# Signature Verification (stub - external tool)
# ------------------------------------------------------------------

def verify_signature(bundle_path: str) -> Dict:
    # B-120: NOT IMPLEMENTED. Previously returned status=True unconditionally,
    # giving a false PASS to any bundle regardless of signature validity.
    return {
        "status": False,
        "note": (
            "NOT IMPLEMENTED — requires external PKI tool "
            "(OpenSSL / DSS / PyKCS11). This check does not verify "
            "anything; do not treat as PASS."
        ),
    }


# ------------------------------------------------------------------
# Timestamp Verification (stub)
# ------------------------------------------------------------------

def verify_timestamp(bundle_path: str) -> Dict:
    # B-120: NOT IMPLEMENTED. Previously returned status=True unconditionally.
    return {
        "status": False,
        "note": (
            "NOT IMPLEMENTED — requires RFC 3161 verification. "
            "This check does not verify anything; do not treat as PASS."
        ),
    }


# ------------------------------------------------------------------
# Consistency checks
# ------------------------------------------------------------------

def verify_consistency(bundle_path: str) -> Dict:
    manifest = load_json(os.path.join(bundle_path, "manifest.json"))
    
    required_files = [
        "report.pdf",
        "ledger.json",
        "metrics.json"
    ]
    
    missing = []
    for f in required_files:
        if not any(entry["name"] == f for entry in manifest["files"]):
            missing.append(f)
    
    return {
        "status": len(missing) == 0,
        "missing": missing
    }


# ------------------------------------------------------------------
# Main verification
# ------------------------------------------------------------------

def verify_bundle(bundle_path: str) -> Dict:
    results = {}
    
    results["manifest"] = verify_manifest(bundle_path)
    results["ledger"] = verify_ledger(bundle_path)
    results["signature"] = verify_signature(bundle_path)
    results["timestamp"] = verify_timestamp(bundle_path)
    results["consistency"] = verify_consistency(bundle_path)
    
    overall = all(
        r.get("status", False)
        for r in results.values()
    )
    
    return {
        "overall_status": overall,
        "checks": results
    }


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evidence Bundle Verifier")
    parser.add_argument("bundle", help="Path to evidence bundle")
    args = parser.parse_args()
    
    if not os.path.exists(args.bundle):
        print("[ERROR] Bundle path does not exist")
        sys.exit(1)
    
    result = verify_bundle(args.bundle)
    
    print("\n=== VERIFICATION RESULT ===")
    print(f"Overall: {'VALID' if result['overall_status'] else 'INVALID'}\n")
    
    for name, res in result["checks"].items():
        print(f"[{name.upper()}] -> {res.get('status')}")
        if "error" in res:
            print(f"   error: {res['error']}")
    
    print()
    
    if not result["overall_status"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
