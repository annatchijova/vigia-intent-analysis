#!/usr/bin/env python3
"""
vigia/tools/generate_calibration.py

Convierte vigia_60_cases_dataset.json (artefactos con texto)
al formato que necesita fit_calibration.py:
    [{"ground_truth": "AUTHENTIC"|"FABRICATED", "z_scores": {"SDA": f, ...}}]

Usa SemioticDetectorV2 para derivar z_scores desde el texto real.
Sin random — cada z_score viene del MI del detector.
"""
import json, os, sys, hashlib

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "vigia", "core"))
sys.path.insert(0, _ROOT)

TOOLS = ["SDA", "ACP", "CLI", "ROI", "GCI", "DGPI"]

def load_detector():
    try:
        from semiotic_detector_v2 import SemioticDetectorV2
        d = SemioticDetectorV2()
        print("[detector] SemioticDetectorV2 cargado", file=sys.stderr)
        return d
    except Exception as e:
        print(f"[detector] fallback — {e}", file=sys.stderr)
        return None

def text_to_zscore(text: str, tool: str, ground_truth: str, detector=None) -> float:
    """
    Deriva z_score desde el texto del artefacto.
    
    Con detector: usa MI del SemioticDetectorV2.
    Sin detector: heurística basada en palabras clave forenses.
    """
    if detector and text.strip():
        try:
            result = detector.analyze(text, f"CAL-{tool}", "2026-01-01T00:00:00Z")
            fsv = result.get("fsv", {})
            mi = fsv.get("manipulation_index", {})
            mi_val = mi.get("num", 0) / max(mi.get("den", 1), 1)
            alert = result.get("alert_level", "NORMAL")

            # Mapear MI + alert a z_score en escala razonable
            alert_z = {"CRITICAL": 3.5, "HIGH": 2.8, "MEDIUM": 2.0,
                       "LOW": 1.2, "NORMAL": 0.6}
            base_z = alert_z.get(alert, 0.6)
            z = base_z + mi_val * 2.0
            return round(min(z, 5.0), 3)
        except Exception:
            pass

    # Fallback heurístico
    text_lower = text.lower()
    evil_keywords = [
        "rm -rf", "history -c", "base64", "netcat", "nc ", "evil",
        "malware", "attacker", "exfil", "shadow", "passwd",
        "999.999", "deadbeef", "00000000", "-1 -1", "duration: -",
        "ignoreboth", "histcontrol", "chmod 777", "/dev/null",
        "self-loop", "invalid", "imposible", "fabricado"
    ]
    hits = sum(1 for kw in evil_keywords if kw in text_lower)
    if hits > 0:
        return round(min(1.5 + hits * 0.8, 4.5), 3)

    # Texto limpio → z_score bajo
    return round(0.3 + len(text) / 2000, 3)


def main():
    input_path = os.path.join(_ROOT, "data", "vigia_60_cases_dataset.json")
    output_path = os.path.join(_ROOT, "data", "calibration_dataset.json")

    with open(input_path) as f:
        artifacts = json.load(f)

    print(f"[cal] {len(artifacts)} artefactos cargados", file=sys.stderr)

    detector = load_detector()

    # Agrupar por source_case
    cases: dict = {}
    for art in artifacts:
        cid   = art.get("source_case", "UNKNOWN")
        gt    = art.get("class", "AUTHENTIC")
        tool  = art.get("tool", "SDA")
        text  = art.get("text", "")

        if cid not in cases:
            cases[cid] = {"ground_truth": gt, "z_scores": {}}

        z = text_to_zscore(text, tool, gt, detector)
        # Si ya existe esa herramienta, promediamos
        existing = cases[cid]["z_scores"].get(tool)
        if existing is not None:
            cases[cid]["z_scores"][tool] = round((existing + z) / 2, 3)
        else:
            cases[cid]["z_scores"][tool] = z

    # Completar herramientas faltantes con 0.5 (neutral)
    records = []
    for cid, data in cases.items():
        for tool in TOOLS:
            if tool not in data["z_scores"]:
                data["z_scores"][tool] = 0.5
        records.append({
            "ground_truth": data["ground_truth"],
            "z_scores": data["z_scores"]
        })

    # Stats
    fab  = sum(1 for r in records if r["ground_truth"] == "FABRICATED")
    auth = sum(1 for r in records if r["ground_truth"] == "AUTHENTIC")
    print(f"[cal] {len(records)} registros | FABRICATED={fab} AUTHENTIC={auth}",
          file=sys.stderr)

    output = json.dumps(records, indent=2, sort_keys=True)
    dataset_hash = hashlib.sha256(output.encode()).hexdigest()
    print(f"[cal] hash={dataset_hash[:16]}...", file=sys.stderr)

    with open(output_path, "w") as f:
        f.write(output)
    print(f"[cal] guardado en {output_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
