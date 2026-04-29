#!/usr/bin/env python3
# Copyright (c) 2026 Anna Tchijova
# Vigía - Autonomous Incident Response Engine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

"""
convert_md_cases.py

Convierte casos forenses de Markdown al formato JSON canónico de VIGÍA.
Específico para el formato de Anna: #### Caso NNN: "Nombre" – Subtítulo

Uso:
    python3 convert_md_cases.py

Genera: data/cases/consolidated/VIGIA-SYN-NNN.json
        data/cases/consolidated/_index.json
"""

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────

MD_SOURCES = [
    "nuevoscasos.md",
    "casos.md",
    "casos2.md",
    "casosfinal.md",
]

OUTPUT_DIR = "data/cases/consolidated"

# ── Parser ─────────────────────────────────────────────────────────────────

# Regex para el formato de Anna
CASE_RE = re.compile(
    r'#{2,4}\s*Caso\s+(\d+):\s*(.+?)\s*[\u2013\-]\s*(.+)',
    re.IGNORECASE,
)

VERDICT_RE = re.compile(
    r'Veredicto[:\s]*\**\s*(MALICE|INTENT|SUSPICION|NOISE|ABSTAIN)\**\s*\(?(\d+)?%?\)?',
    re.IGNORECASE,
)

INTERPRETATION_RE = re.compile(
    r'Interpretaci[oó]n de (?:VIGÍA|Vig[ií]a)[:\s]*["\"]([^"\"]+)["\"]',
    re.IGNORECASE,
)

SIGNALS_RE = re.compile(
    r'\*\*Signals?[:\*]*\*?\*?\s*(.*?)(?=\n\s*\*\s*\*\*[A-Z]|\Z)',
    re.DOTALL | re.IGNORECASE,
)

CARNEGIE_RE = re.compile(
    r'Carnegie(?:\s+Appeal)?[:\s]*["\"]?([^"\"]*)["\"]?',
    re.IGNORECASE,
)

GRICE_RE = re.compile(
    r'Grice[:\s]+(.*?)(?=\n\s*\*|\Z)',
    re.DOTALL | re.IGNORECASE,
)

PEIRCE_RE = re.compile(
    r'Peirce[:\s]+(.*?)(?=\n\s*\*|\Z)',
    re.DOTALL | re.IGNORECASE,
)


def _clean(text):
    if not text:
        return ""
    # Limpiar markdown residual
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'`[^`]+`', lambda m: m.group(0).strip('`'), text)
    return ' '.join(text.split()).strip()


def _content_hash(case):
    s = json.dumps(
        {k: v for k, v in sorted(case.items()) if not k.startswith('_')},
        sort_keys=True, ensure_ascii=True
    )
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def parse_md_file(path):
    """Parsea un archivo MD y retorna lista de casos."""
    text = open(path, encoding='utf-8').read()
    cases = []

    # Encontrar todos los encabezados de caso
    headers = list(CASE_RE.finditer(text))
    if not headers:
        print(f"  [WARN] No se encontraron casos en {path}")
        return cases

    for idx, match in enumerate(headers):
        case_num = match.group(1).strip()
        case_name = _clean(match.group(2))
        case_subtitle = _clean(match.group(3))

        # Extraer cuerpo entre este header y el siguiente
        start = match.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        body = text[start:end]

        case = parse_case_body(case_num, case_name, case_subtitle, body, path)
        if case:
            cases.append(case)

    return cases


def parse_case_body(num, name, subtitle, body, source_file):
    """Extrae los campos de un caso desde su cuerpo de texto."""

    # Veredicto — obligatorio
    verdict_match = VERDICT_RE.search(body)
    if not verdict_match:
        # Intentar encontrar veredicto en el texto sin formato
        for v in ["MALICE", "INTENT", "SUSPICION", "NOISE", "ABSTAIN"]:
            if v in body.upper():
                verdict = v
                confidence = 90
                break
        else:
            print(f"  [SKIP] Caso {num}: sin veredicto detectado")
            return None
    else:
        verdict = verdict_match.group(1).upper()
        confidence = int(verdict_match.group(2)) if verdict_match.group(2) else 90

    # Interpretación de VIGÍA
    interp_match = INTERPRETATION_RE.search(body)
    description = _clean(interp_match.group(1)) if interp_match else f"Caso sintético {num}: {name}"

    # Signals
    signals_match = SIGNALS_RE.search(body)
    signals_text = _clean(signals_match.group(1)) if signals_match else ""

    # Carnegie
    carnegie_match = CARNEGIE_RE.search(body)
    carnegie = _clean(carnegie_match.group(1)) if carnegie_match else None

    # Grice
    grice_match = GRICE_RE.search(body)
    grice = _clean(grice_match.group(1)[:200]) if grice_match else None

    # Peirce
    peirce_match = PEIRCE_RE.search(body)
    peirce_raw = _clean(peirce_match.group(1)[:300]) if peirce_match else ""

    # Construir artefactos desde signals
    artifacts = signals_to_artifacts(signals_text)

    # Construir cadena Peirce
    peirce = build_peirce(peirce_raw, signals_text, name, subtitle)

    # Devil's advocate basado en veredicto
    devil = devil_advocate_template(verdict, name)

    case_id = f"VIGIA-SYN-{int(num):03d}"

    return {
        "case_id": case_id,
        "case_name": f"{name} – {subtitle}",
        "source_origin": "synthetic_markdown",
        "source_dataset": "VIGÍA Internal Corpus 2026",
        "source_file": os.path.basename(source_file),
        "description": description,
        "expected_verdict": verdict,
        "confidence_expected": confidence,
        "expected_mitre_ttps": infer_mitre(signals_text, subtitle),
        "carnegie_pattern_expected": carnegie,
        "grice_violation": grice,
        "artifacts": artifacts,
        "peirce_expected": peirce,
        "devil_advocate": devil,
        "abstention_risk": "bajo" if confidence >= 90 else "medio",
        "_meta": {
            "parser_version": "2.0",
            "consolidated_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def signals_to_artifacts(signals_text):
    """Convierte texto de signals a lista de artefactos estructurados."""
    if not signals_text:
        return []

    # Detectar tipo de artefacto por keywords
    def detect_type(text):
        t = text.lower()
        if any(w in t for w in ["bash", "historial", "history", "shell", "comando"]):
            return "bash_history"
        if any(w in t for w in ["auth.log", "sshd", "sudo", "pam_unix", "login"]):
            return "syslog"
        if any(w in t for w in ["powershell", "ps1", "cmdlet", "invoke-"]):
            return "powershell_log"
        if any(w in t for w in ["ip", "dns", "red", "network", "conexión", "puerto"]):
            return "network_flow"
        if any(w in t for w in ["pdf", "exif", "metadata", "metadato", "imagen"]):
            return "file_metadata"
        if any(w in t for w in ["ticket", "jira", "slack", "mensaje", "correo", "email"]):
            return "slack_message"
        if any(w in t for w in ["timestamp", "hora", "fecha", "tiempo", "temporal"]):
            return "timestamp"
        if any(w in t for w in ["registro", "registry", "regedit", "hklm", "hkcu"]):
            return "registry"
        return "file_metadata"

    # Dividir signals en artefactos individuales
    # Buscar patrones como backticks, comillas, o frases descriptivas
    parts = re.split(r'(?<=\.)\s+(?=[A-ZÁÉÍÓÚ])', signals_text)
    if len(parts) == 1:
        parts = signals_text.split('. ')

    artifacts = []
    for i, part in enumerate(parts[:5], 1):
        part = part.strip()
        if len(part) < 20:
            continue
        art_type = detect_type(part)
        artifacts.append({
            "artifact_id": f"SYN-{i:03d}",
            "type": art_type,
            "content": part[:600],
            "forensic_anomalies": [
                "Inconsistencia semiótica detectada en análisis Peirce",
                "Verificar con herramientas complementarias",
            ],
            "peirce_layer": "FIRSTNESS" if i == 1 else "SECONDNESS" if i <= 3 else "THIRDNESS",
        })

    if not artifacts:
        artifacts.append({
            "artifact_id": "SYN-001",
            "type": "file_metadata",
            "content": signals_text[:600],
            "forensic_anomalies": ["Requiere análisis manual"],
            "peirce_layer": "FIRSTNESS",
        })

    return artifacts


def build_peirce(peirce_raw, signals, name, subtitle):
    """Construye la cadena Peirce desde el texto extraído."""
    peirce = {
        "firstness": "",
        "secondness": "",
        "thirdness": "",
    }

    if peirce_raw:
        # Intentar extraer capas explícitas
        for layer, keywords in [
            ("firstness", ["primeridad", "firstness", "primera", "observación"]),
            ("secondness", ["segundidad", "secondness", "segunda", "contradicción", "índice"]),
            ("thirdness", ["terceridad", "thirdness", "tercera", "símbolo", "intención"]),
        ]:
            for kw in keywords:
                if kw in peirce_raw.lower():
                    # Extraer el fragmento relevante
                    idx = peirce_raw.lower().index(kw)
                    peirce[layer] = peirce_raw[idx:idx+200].strip()
                    break

    # Fallbacks
    if not peirce["firstness"]:
        peirce["firstness"] = (
            f"Observación inicial: {signals[:150]}" if signals
            else f"Artefactos superficialmente normales en caso '{name}'"
        )
    if not peirce["secondness"]:
        peirce["secondness"] = f"Contradicción entre narrativa declarada y evidencia técnica en '{subtitle}'"
    if not peirce["thirdness"]:
        peirce["thirdness"] = f"Patrón de intención hostil: {subtitle}"

    return peirce


def infer_mitre(signals, subtitle):
    """Infiere TTPs de MITRE ATT&CK desde el contenido."""
    mitre = []
    combined = (signals + " " + subtitle).lower()

    mitre_map = {
        "T1078": ["credencial", "password", "contraseña", "login", "account"],
        "T1059": ["powershell", "bash", "script", "cmd", "shell"],
        "T1070": ["log", "historial", "borrar", "eliminar", "wipe", "shred"],
        "T1566": ["phishing", "email", "correo", "spear", "pdf malicioso"],
        "T1041": ["exfiltración", "exfil", "transferencia", "upload", "curl -T"],
        "T1036": ["svchost", "disfraz", "falso", "imitación", "mimicry"],
        "T1055": ["inyección", "injection", "hollow", "process"],
        "T1562": ["deshabilitar", "disable", "firewall", "antivirus", "evasion"],
        "T1110": ["brute force", "fuerza bruta", "spray", "intentos"],
        "T1003": ["dump", "mimikatz", "credencial", "hash", "lsass"],
    }

    for ttp, keywords in mitre_map.items():
        if any(kw in combined for kw in keywords):
            mitre.append(ttp)

    return mitre[:4]  # Máximo 4 TTPs


def devil_advocate_template(verdict, name):
    """Genera hipótesis alternativa benigna."""
    templates = {
        "MALICE": (
            "El comportamiento observado podría explicarse por un script "
            "automatizado mal configurado, un error de procedimiento de un "
            "administrador legítimo bajo presión, o una herramienta de "
            "auditoría no documentada con permisos excesivos."
        ),
        "INTENT": (
            "Las inconsistencias detectadas podrían deberse a un cambio de "
            "hábitos del usuario, configuración automática de una herramienta "
            "de terceros, o un malentendido de protocolos internos."
        ),
        "SUSPICION": (
            "Los artefactos presentes son ambiguos: podrían ser residuos de "
            "actividad de mantenimiento legítimo, pruebas de penetración "
            "autorizadas, o anomalías de software benigno."
        ),
        "NOISE": (
            "El patrón es consistente con actividad legítima de fondo: "
            "logs de sistema, actualizaciones automáticas, o herramientas "
            "de monitoreo con comportamiento verbose."
        ),
        "ABSTAIN": (
            "Evidencia insuficiente para formular una hipótesis benigna "
            "competente. Se requiere contexto adicional del entorno."
        ),
    }
    return templates.get(verdict, "Hipótesis benigna no determinada.")


# ── Motor de consolidación ──────────────────────────────────────────────────

def consolidate():
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes = set()
    all_cases = []
    stats = {"parsed": 0, "written": 0, "skipped": 0, "dedup": 0}

    print(f"Consolidando casos en {output_dir}/\n")

    for md_file in MD_SOURCES:
        if not os.path.exists(md_file):
            print(f"[SKIP] {md_file} no encontrado")
            continue
        print(f"[MD] Parseando {md_file}...")
        cases = parse_md_file(md_file)
        print(f"     {len(cases)} casos encontrados")
        stats["parsed"] += len(cases)

        for case in cases:
            h = _content_hash(case)
            if h in seen_hashes:
                stats["dedup"] += 1
                continue
            seen_hashes.add(h)

            # Escribir JSON individual
            out_path = output_dir / f"{case['case_id']}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(case, f, indent=2, ensure_ascii=False)
            all_cases.append(case["case_id"])
            stats["written"] += 1

    # Escribir índice
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": stats["written"],
        "schema_version": "2.0",
        "statistics": stats,
        "case_ids": sorted(all_cases),
        "verdicts_summary": {},
    }

    # Contar veredictos
    for case_id in all_cases:
        path = output_dir / f"{case_id}.json"
        v = json.load(open(path))["expected_verdict"]
        index["verdicts_summary"][v] = index["verdicts_summary"].get(v, 0) + 1

    with open(output_dir / "_index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"CONSOLIDACIÓN COMPLETADA")
    print(f"{'='*50}")
    print(f"  Parseados:    {stats['parsed']}")
    print(f"  Escritos:     {stats['written']}")
    print(f"  Deduplicados: {stats['dedup']}")
    print(f"  Veredictos:   {index['verdicts_summary']}")
    print(f"  Output:       {output_dir}/")
    print(f"{'='*50}")


if __name__ == "__main__":
    consolidate()
