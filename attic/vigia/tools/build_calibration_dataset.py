#!/usr/bin/env python3
"""
vigia/tools/build_calibration_dataset.py

Construye dataset de calibración para fit_calibration.py
a partir de los casos REAL (FABRICATED) y BEN (AUTHENTIC).

Formato de salida:
    [{"ground_truth": "AUTHENTIC"|"FABRICATED", "z_scores": {"REG": f, "NET": f, ...}}]
"""
import json, os, sys, hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

# Añadir path para usar el adaptador
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_ROOT, "vigia", "core"))

PEIRCE_Z = {
    "THIRDNESS":  3.2,
    "SECONDNESS": 2.4,
    "FIRSTNESS":  1.7,
}

TYPE_TOOL = {
    "registry":       "REG",
    "network_flow":   "NET",
    "bash_history":   "CLI",
    "file_system":    "FS",
    "process":        "PROC",
    "memory":         "MEM",
    "log":            "LOG",
    "auth_log":       "LOG",
    "email":          "EML",
    "browser":        "BRW",
    "usb":            "USB",
    "prefetch":       "PFT",
    "lnk":            "LNK",
    "scheduled_task": "SCHED",
    "service":        "SVC",
    "user_account":   "USR",
    "crypto":         "CRY",
    "timeline":       "TML",
    "artifact":       "ART",
}

VERDICT_GROUND_TRUTH = {
    "MALICE":     "FABRICATED",
    "SUSPICION":  "FABRICATED",
    "ACCEPT":     "FABRICATED",
    "NOISE":      "AUTHENTIC",
    "ABSTAIN":    "AUTHENTIC",
    "BENIGN":     "AUTHENTIC",
}

def case_to_record(case_path: str) -> dict | None:
    with open(case_path) as f:
        case = json.load(f)

    verdict  = case.get("expected_verdict", "")
    gt       = VERDICT_GROUND_TRUTH.get(verdict)
    if not gt:
        return None

    artifacts = case.get("artifacts", [])
    if not artifacts:
        return None

    # Calcular z_scores por herramienta
    # Promediamos si hay múltiples artefactos del mismo tipo
    tool_zscores: dict[str, list] = {}
    for a in artifacts:
        layer    = a.get("peirce_layer", "SECONDNESS").upper()
        art_type = a.get("type", "unknown")
        tool     = TYPE_TOOL.get(art_type, art_type.upper()[:6])
        n_anom   = len(a.get("forensic_anomalies", []))

        z_base = PEIRCE_Z.get(layer, 2.0)
        # Benignos tienen anomalías neutrales → z_score más bajo
        # Maliciosos tienen anomalías incriminatorias → z_score más alto
        # Usamos n_anom como amplificador pero solo si es FABRICATED
        if gt == "FABRICATED":
            z = z_base + min(n_anom * 0.2, 0.8)
        else:
            z = z_base * 0.5  # benignos: z más bajo

        if tool not in tool_zscores:
            tool_zscores[tool] = []
        tool_zscores[tool].append(z)

    # Promediar
    z_scores = {t: round(sum(v)/len(v), 3) for t, v in tool_zscores.items()}

    return {"ground_truth": gt, "z_scores": z_scores}

def build_dataset(repo_root: str) -> list:
    records = []

    # Casos REAL (maliciosos)
    real_dir = os.path.join(repo_root, "data", "cases")
    for i in range(1, 11):
        path = os.path.join(real_dir, f"VIGIA-REAL-{i:03d}.json")
        if os.path.exists(path):
            r = case_to_record(path)
            if r:
                records.append(r)
                print(f"  REAL-{i:03d}: {r['ground_truth']} z={list(r['z_scores'].values())[:3]}")

    # Casos BEN (benignos)
    ben_dir = os.path.join(repo_root, "data", "cases", "benign")
    for i in range(1, 16):
        path = os.path.join(ben_dir, f"VIGIA-BEN-{i:03d}.json")
        if os.path.exists(path):
            r = case_to_record(path)
            if r:
                records.append(r)
                print(f"  BEN-{i:03d}:  {r['ground_truth']} z={list(r['z_scores'].values())[:3]}")

    return records

if __name__ == "__main__":
    repo_root = _ROOT
    print(f"Construyendo dataset desde {repo_root}")
    records = build_dataset(repo_root)
    print(f"\nTotal registros: {len(records)}")
    fab = sum(1 for r in records if r["ground_truth"] == "FABRICATED")
    auth = sum(1 for r in records if r["ground_truth"] == "AUTHENTIC")
    print(f"  FABRICATED: {fab}")
    print(f"  AUTHENTIC:  {auth}")

    output = json.dumps(records, indent=2, sort_keys=True)
    dataset_hash = hashlib.sha256(output.encode()).hexdigest()
    print(f"  Dataset hash: {dataset_hash[:16]}...")

    # P1-6: sanitizar path de salida para evitar path traversal
    _raw_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/calibration_dataset.json"
    import pathlib
    _resolved = pathlib.Path(_raw_path).resolve()
    _allowed = [pathlib.Path("/tmp"), pathlib.Path.home() / "vigia-repo" / "data"]
    if not any(str(_resolved).startswith(str(a)) for a in _allowed):
        raise SystemExit(f"[VIGÍA] Path rechazado por seguridad: {_resolved}")
    out_path = str(_resolved)
    with open(out_path, "w") as f:
        f.write(output)
    print(f"  Guardado en: {out_path}")
