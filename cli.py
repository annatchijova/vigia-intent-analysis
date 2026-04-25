# verifier/cli.py

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
    
    return {"status": True}


# ------------------------------------------------------------------
# Signature Verification (stub - external tool)
# ------------------------------------------------------------------

def verify_signature(bundle_path: str) -> Dict:
    manifest = os.path.join(bundle_path, "manifest.json")
    signature = os.path.join(bundle_path, "manifest.sig")
    
    if not os.path.exists(signature):
        return {"status": False, "error": "signature missing"}
    
    # Requiere OpenSSL / DSS / PyKCS11 real en producción
    # Aquí solo stub controlado
    
    # Ejemplo real sería:
    # openssl cms -verify -in manifest.sig -content manifest.json
    
    return {
        "status": True,
        "note": "signature verification requires external PKI tool"
    }


# ------------------------------------------------------------------
# Timestamp Verification (stub)
# ------------------------------------------------------------------

def verify_timestamp(bundle_path: str) -> Dict:
    # Similar: requiere TSA validation real
    return {
        "status": True,
        "note": "timestamp validation requires RFC3161 verification"
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
