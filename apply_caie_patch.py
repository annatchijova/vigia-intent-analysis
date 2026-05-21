#!/usr/bin/env python3
# Copyright 2026 Anna Tchijova
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

CAIE_PATH = Path("vigia/tools/caie.py")

if not CAIE_PATH.exists():
    print("[ERROR] " + str(CAIE_PATH) + " not found. Are you in ~/vigia-repo?")
    exit(1)

caie_src = CAIE_PATH.read_text(encoding="utf-8")

# Patch 1: Add network_artifact and file_metadata
marker = '"usn_journal_gap":      EvidenceProfile(0.10, 0.38, "USN Journal gap vs LogFile — Ring-0 required to clear"),'
replacement = marker + "\n" + "    # P6: Network and file metadata (canonical cases)\n" + '    "network_artifact":     EvidenceProfile(0.50, 0.20, "Netflow, Zeek, IDS network artifacts — moderate spoofability"),\n' + '    "file_metadata":        EvidenceProfile(0.65, 0.18, "EXIF, PDF metadata, document properties — requires fabrication skill"),'

if "network_artifact" in caie_src:
    print("[SKIP] network_artifact already present")
else:
    caie_src = caie_src.replace(marker, replacement)
    print("[PATCH] Added network_artifact and file_metadata to EVIDENCE_PROFILES")

# Patch 2: Add pre-calculated fracture ingestion
pre_calc_lines = [
    "        # ===================================================================",
    "        # PRE-CALCULATED FRACTURE INGESTION (Canonical Cases)",
    "        # If artifacts carry pre-declared fractures in metadata, ingest them",
    "        # as fallback when auto-detection finds nothing.",
    "        # ===================================================================",
    "        for a in self._artifacts:",
    '            pre_fractures = a.metadata.get("caie_fractures_predeclared", [])',
    "            if not pre_fractures:",
    '                pre_fractures = a.metadata.get("caie_fractures", [])',
    "            for pf in pre_fractures:",
    '                if isinstance(pf, dict) and pf.get("type"):',
    "                    self._fractures.append(Fracture(",
    "                        artifact_a=a.description[:60],",
    '                        artifact_b="Pre-declared in canonical case",',
    '                        fracture_type=pf["type"],',
    '                        severity=float(pf.get("severity", 0.8)),',
    '                        interpretation=pf.get("description", "Pre-calculated fracture from case definition"),',
    '                        spoofability_delta=float(pf.get("spoofability_delta", 0.5)),',
    '                        ttp_id=pf.get("mitre_ttp"),',
    "                    ))",
    "",
]
pre_calc_block = "\n".join(pre_calc_lines) + "\n"

if "PRE-CALCULATED FRACTURE INGESTION" in caie_src:
    print("[SKIP] Pre-calculated fracture ingestion already present")
else:
    caie_src = caie_src.replace("        return self._fractures", pre_calc_block + "        return self._fractures")
    print("[PATCH] Added pre-calculated fracture ingestion")

CAIE_PATH.write_text(caie_src, encoding="utf-8")
print("[DONE] " + str(CAIE_PATH) + " patched successfully")
