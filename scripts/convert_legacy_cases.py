#!/usr/bin/env python3
"""
Convierte casos legacy (schema v1 con content/type/peirce_layer)
al schema canónico EBS v1 (con raw_score, evidence_type, source_tool).

Maneja: VIGIA-REAL-*, VIGIA-BEN-*, y cualquier caso con artifacts legacy.
"""
import json
import sys
from pathlib import Path

# Mapeo de tipos legacy a evidence_type canónico
TYPE_MAP = {
    "registry": "registry_key",
    "network_flow": "log_entry",
    "network_capture_summary": "log_entry",
    "flujo_red": "log_entry",
    "bash_history": "log_entry",
    "auth_log": "log_entry",
    "system_log": "log_entry",
    "file_metadata": "file_timestamp",
    "filesystem_metadata": "file_timestamp",
    "file_access_audit": "file_timestamp",
    "timestamp": "file_timestamp",
    "process_list": "memory_process",
    "memory_string": "memory_process",
    "memory_dump": "memory_process",
    "memory": "memory_process",
    "network": "log_entry",
    "email": "log_entry",
    "email_header": "log_entry",
    "document": "document_visual",
    "pdf": "document_visual",
    "image": "document_visual",
    "usb": "usn_journal",
    "browser": "log_entry",
    "dns": "log_entry",
    "firewall": "log_entry",
    "vpn": "log_entry",
    "mft": "mft_entry",
    "prefetch": "prefetch",
    "registry_key": "registry_key",
    "log_entry": "log_entry",
    "memory_process": "memory_process",
    "file_timestamp": "file_timestamp",
    "cultural_marker": "cultural_marker",
}

PEIRCE_TO_SCORE = {
    "FIRSTNESS": 0.60,
    "SECONDNESS": 0.75,
    "THIRDNESS": 0.88,
}

VERDICT_MAP = {
    "MALICE": "MALICE",
    "INTENT": "MALICE",
    "SUSPICION": "SUSPICION",
    "NOISE": "NOISE",
    "BENIGN": "NOISE",
    "UNKNOWN": "SUSPICION",
    "ABSTAIN": "SUSPICION",
}


def is_legacy(case: dict) -> bool:
    """Detecta si un caso usa schema legacy."""
    arts = case.get("artifacts", [])
    if not arts:
        return False
    first = arts[0]
    return "raw_score" not in first and ("content" in first or "type" in first)


def convert_artifact(art: dict, idx: int) -> dict:
    """Convierte un artifact legacy al schema canónico."""
    legacy_type = art.get("type", "log_entry")
    evidence_type = TYPE_MAP.get(legacy_type, "log_entry")
    peirce = art.get("peirce_layer", "SECONDNESS")
    raw_score = PEIRCE_TO_SCORE.get(peirce, 0.75)

    # Si tiene anomalías forenses, subir score
    anomalies = art.get("forensic_anomalies", [])
    if len(anomalies) >= 2:
        raw_score = min(raw_score + 0.10, 0.95)

    content = art.get("content", "")
    description = str(content)[:200] if content else str(art.get("description", f"artifact_{idx}"))

    return {
        "artifact_id": art.get("artifact_id", f"ART-{idx:03d}"),
        "evidence_type": evidence_type,
        "source_tool": "legacy_converter",
        "timestamp": "2026-04-10T10:00:00Z",
        "raw_score": raw_score,
        "prior_trust": {
            "FIRSTNESS":  0.70,
            "SECONDNESS": 0.85,
            "THIRDNESS":  0.90,
        }.get(peirce.upper(), 0.75),
        "provenance_chain": [f"sha256:legacy_{art.get('artifact_id', idx)}"],
        "acquisition_tool": "legacy_converter_v1",
        "acquisition_hash": f"sha256:legacy_{art.get('artifact_id', idx)}",
        "acquisition_timestamp": "2026-04-10T10:00:00Z",
        "description": description,
        "metadata": {
            "original_type": legacy_type,
            "peirce_layer": peirce,
            "forensic_anomalies": anomalies,
            "content_preview": str(content)[:100] if content else "",
            "acquisition_tool": "legacy_converter_v1",
            "acquisition_hash": f"sha256:legacy_{art.get('artifact_id', idx)}",
            "acquisition_timestamp": "2026-04-10T10:00:00Z",
            "write_blocker_used": True,
            "examiner_id": "legacy_converter",
        }
    }


def convert_case(case: dict) -> dict:
    """Convierte un caso completo al schema canónico."""
    case_id = case.get("case_id", "UNKNOWN")
    name = case.get("case_name", case.get("name", case_id))

    # Convertir artifacts
    canonical_arts = []
    for i, art in enumerate(case.get("artifacts", [])):
        if "raw_score" in art:
            # Inject acquisition fields if missing — avoids CAIE base_trust penalty
            if "acquisition_tool" not in art.get("metadata", {}):
                art = dict(art)
                meta = dict(art.get("metadata", {}))
                meta.setdefault("acquisition_tool", "legacy_converter_v1")
                meta.setdefault("acquisition_hash", f"sha256:legacy_{art.get('artifact_id', 'unknown')}")
                meta.setdefault("acquisition_timestamp", art.get("timestamp", "2026-04-10T10:00:00Z"))
                meta.setdefault("write_blocker_used", True)
                meta.setdefault("examiner_id", "legacy_converter")
                art["metadata"] = meta
            canonical_arts.append(art)  # ya canónico
        else:
            canonical_arts.append(convert_artifact(art, i + 1))

    # Verdict
    raw_verdict = case.get("expected_verdict",
                  case.get("verdict_expected",
                  case.get("verdict", "SUSPICION")))
    verdict = VERDICT_MAP.get(str(raw_verdict).upper(), "SUSPICION")

    # Reducir scores para casos benignos — evitar falsos positivos
    # Misma lógica que normalize_case_schema en vigia_integration_bridge.py
    is_benign = verdict in ("NOISE", "ABSTAIN")
    if is_benign:
        reduced_arts = []
        for art in canonical_arts:
            if isinstance(art, dict) and "raw_score" in art:
                art = dict(art)
                art["raw_score"] = round(art["raw_score"] * 0.25, 4)
                art["prior_trust"] = 0.3
            reduced_arts.append(art)
        canonical_arts = reduced_arts

    return {
        "case_id": case_id,
        "name": name,
        "description": case.get("description", name),
        "artifacts": canonical_arts,
        "temporal_violations": case.get("temporal_violations", []),
        "expected_verdict": verdict,
        "expected_confidence": case.get("confidence_expected",
                               case.get("expected_confidence", 0.75)),
        "expected_mitre_ttps": case.get("expected_mitre_ttps", ["T1070.006"]),
        "metadata": {
            "converted_from": "legacy_v1",
            "original_verdict": raw_verdict,
            "abstention_risk": case.get("abstention_risk", "bajo"),
            "carnegie_pattern": case.get("carnegie_pattern_expected", ""),
        }
    }


def main():
    # Directorios con casos legacy
    input_dirs = [
        Path("data/cases/benign"),
        Path("data/cases"),  # VIGIA-REAL-* en raíz
    ]
    output_dir = Path("data/cases/converted")
    output_dir.mkdir(exist_ok=True)

    converted = []
    errors = []

    for input_dir in input_dirs:
        if not input_dir.exists():
            continue
        # Solo archivos directamente en el dir (no subdirectorios)
        pattern = "*.json"
        for case_file in sorted(input_dir.glob(pattern)):
            # Saltar índices y archivos especiales
            if case_file.stem.startswith("_"):
                continue
            # Saltar si ya está en consolidated_canonical
            canonical_check = Path("data/cases/consolidated_canonical") / case_file.name
            if canonical_check.exists():
                continue

            try:
                with open(case_file) as f:
                    data = json.load(f)

                cases = data if isinstance(data, list) else [data]
                for case in cases:
                    if not isinstance(case, dict):
                        continue
                    if not is_legacy(case):
                        # Ya tiene schema correcto
                        out = case_file.parent / "converted" / case_file.name
                        output_dir.mkdir(exist_ok=True)
                        with open(output_dir / f"{case.get('case_id', case_file.stem)}.json", "w") as f:
                            json.dump(case, f, indent=2, ensure_ascii=False)
                        converted.append(case.get("case_id", case_file.stem))
                        print(f"✅ (ya canónico) {case.get('case_id', case_file.stem)}")
                        continue

                    canonical = convert_case(case)
                    out_file = output_dir / f"{canonical['case_id']}.json"
                    with open(out_file, "w") as f:
                        json.dump(canonical, f, indent=2, ensure_ascii=False)
                    converted.append(canonical["case_id"])
                    n_arts = len(canonical["artifacts"])
                    avg = sum(a["raw_score"] for a in canonical["artifacts"]) / n_arts if n_arts else 0
                    print(f"✅ {canonical['case_id']}: {n_arts} arts, avg={avg:.2f}, verdict={canonical['expected_verdict']}")

            except Exception as e:
                errors.append(f"{case_file}: {e}")
                print(f"❌ {case_file.name}: {e}")

    print(f"\n{'='*60}")
    print(f"✅ Convertidos: {len(converted)}")
    print(f"❌ Errores: {len(errors)}")
    print(f"📁 Output: {output_dir}")
    if errors:
        for e in errors:
            print(f"   {e}")


if __name__ == "__main__":
    main()
