# vigia/report/evidence_bundle.py

import os
import json
import hashlib
import zipfile
from typing import Dict, Any, Optional


# ---------------------------------------------------------------------------
# Hash helper
# ---------------------------------------------------------------------------

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def build_manifest(
    pdf_path: str,
    ledger_path: str,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    pdf_hash = sha256_file(pdf_path)
    ledger_hash = sha256_file(ledger_path)

    manifest = {
        "version": "v1.0",
        "artifacts": {
            "report_pdf": {
                "path": os.path.basename(pdf_path),
                "sha256": pdf_hash,
            },
            "ledger": {
                "path": os.path.basename(ledger_path),
                "sha256": ledger_hash,
            },
        },
        "binding": {
            "pdf_hash": pdf_hash,
            "ledger_hash": ledger_hash,
        },
        "metadata": metadata,
    }

    # Hash del manifest (clave)
    manifest_str = json.dumps(manifest, sort_keys=True)
    manifest["manifest_hash"] = hashlib.sha256(manifest_str.encode()).hexdigest()

    return manifest


# ---------------------------------------------------------------------------
# Firma (placeholder)
# ---------------------------------------------------------------------------

def sign_manifest(manifest_hash: str, private_key=None) -> Optional[str]:
    if private_key is None:
        return None
    return f"SIGNED({manifest_hash[:16]})"


# ---------------------------------------------------------------------------
# Builder principal
# ---------------------------------------------------------------------------

def build_evidence_bundle(
    pdf_path: str,
    ledger_dict: Dict[str, Any],
    output_dir: str,
    case_id: str,
    metadata: Dict[str, Any],
    private_key=None,
    zip_output: bool = True,
) -> Dict[str, Any]:
    """
    Genera bundle verificable:
    - PDF
    - ledger.json
    - manifest.json (con hashes)
    - firma opcional
    """

    os.makedirs(output_dir, exist_ok=True)

    # -----------------------------------------------------------------------
    # Paths
    # -----------------------------------------------------------------------

    bundle_dir = os.path.join(output_dir, f"{case_id}_bundle")
    os.makedirs(bundle_dir, exist_ok=True)

    pdf_out = os.path.join(bundle_dir, "report.pdf")
    ledger_out = os.path.join(bundle_dir, "ledger.json")
    manifest_out = os.path.join(bundle_dir, "manifest.json")
    sig_out = os.path.join(bundle_dir, "bundle.sig")

    # -----------------------------------------------------------------------
    # Copiar PDF
    # -----------------------------------------------------------------------

    with open(pdf_path, "rb") as src, open(pdf_out, "wb") as dst:
        dst.write(src.read())

    # -----------------------------------------------------------------------
    # Guardar ledger
    # -----------------------------------------------------------------------

    with open(ledger_out, "w") as f:
        json.dump(ledger_dict, f, indent=2)

    # -----------------------------------------------------------------------
    # Manifest
    # -----------------------------------------------------------------------

    manifest = build_manifest(pdf_out, ledger_out, metadata)

    with open(manifest_out, "w") as f:
        json.dump(manifest, f, indent=2)

    # -----------------------------------------------------------------------
    # Firma
    # -----------------------------------------------------------------------

    signature = sign_manifest(manifest["manifest_hash"], private_key)

    if signature:
        with open(sig_out, "w") as f:
            f.write(signature)

    # -----------------------------------------------------------------------
    # ZIP opcional
    # -----------------------------------------------------------------------

    zip_path = None
    if zip_output:
        zip_path = os.path.join(output_dir, f"{case_id}_bundle.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for fname in os.listdir(bundle_dir):
                z.write(
                    os.path.join(bundle_dir, fname),
                    arcname=fname
                )

    return {
        "bundle_dir": bundle_dir,
        "zip_path": zip_path,
        "manifest_hash": manifest["manifest_hash"],
        "pdf_hash": manifest["artifacts"]["report_pdf"]["sha256"],
        "ledger_hash": manifest["artifacts"]["ledger"]["sha256"],
        "signature": signature,
    }
