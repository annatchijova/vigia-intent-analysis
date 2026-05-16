#!/usr/bin/env python3
"""
vigia_adversarial_gen.py
─────────────────────────────────────────────────────────────────────────────
VIGÍA Red Team — Generador de Escenarios Adversarios para Abducción

Genera archivos .jsonl de logs sintéticos diseñados para atacar el motor
de abducción (AbductiveIntentEngine) mediante cuatro vectores:

  V1 — ARTEFACTO_FALTANTE_CRÍTICO
       Mimética perfecta de una técnica MITRE pero omite el artefacto
       que la hace distinguible. Fuerza INCOMPLETE_COVERAGE o elección
       de hipótesis de menor cobertura.

  V2 — SEÑUELO_DE_COBERTURA
       Inyecta artefactos de una hipótesis de menor prioridad para
       que su coverage_score supere artificialmente al winner correcto.

  V3 — COLISIÓN_DE_COSTO
       Fabrica evidencia que iguale el costo Ockham entre la hipótesis
       real y un decoy, forzando desempate por len(required_artifacts).

  V4 — POLIMORFISMO_DE_FASE
       Inyecta artefactos que satisfacen parcialmente múltiples fases
       para confundir la detección de IRPhase e inducir análisis en
       la fase incorrecta (donde el winner legítimo no tiene templates).

Output:
  adversarial_<vector>_<n>.jsonl    logs sintéticos
  adversarial_oracle.json           tabla de verdad: input → respuesta esperada

Uso:
  python3 vigia_adversarial_gen.py --output ./red_team/ --count 10 --seed 42
  python3 vigia_adversarial_gen.py --vector V1 V2 --count 5

─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ══════════════════════════════════════════════════════════════════════════
# CONSTANTES Y TABLAS DE REFERENCIA
# ══════════════════════════════════════════════════════════════════════════

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def _ts(offset_seconds: int = 0) -> str:
    from datetime import timedelta
    t = datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)
    return t.isoformat().replace("+00:00", "Z")


# Hipótesis canónicas con sus artefactos requeridos
# (espejo de HYPOTHESIS_TEMPLATES en abductive_intent_engine.py)
HYPOTHESIS_CATALOG: Dict[str, Dict] = {
    "H_DE_001": {
        "intent_type": "log_fabrication",
        "phase": "DEFENSE_EVASION",
        "required": ["timestamp_uniformity", "process_memory_contradiction", "log_gap_intervals"],
        "assumed": [],
        "mitre": "T1565.001",
        "description": "Logs fabricados con intervalos uniformes no naturales",
    },
    "H_DE_002": {
        "intent_type": "log_deletion_after_exfil",
        "phase": "DEFENSE_EVASION",
        "required": ["log_deletion", "event_log_clearing"],
        "assumed": ["exfiltration_occurred", "attacker_wants_stealth"],
        "mitre": "T1070.001",
        "description": "Borrado de logs post-exfiltración",
    },
    "H_DE_003": {
        "intent_type": "anti_forensics_preparation",
        "phase": "DEFENSE_EVASION",
        "required": ["artifact_overwrite", "file_timestamp_modification"],
        "assumed": ["attacker_has_advanced_tools", "attacker_expects_investigation"],
        "mitre": "T1070.006",
        "description": "Anti-forense preparatorio antes de actuar",
    },
    "H_XF_001": {
        "intent_type": "bulk_data_exfiltration",
        "phase": "EXFILTRATION",
        "required": ["outbound_data_transfer", "data_volume"],
        "assumed": [],
        "mitre": "T1048",
        "description": "Exfiltración masiva de datos",
    },
    "H_PE_001": {
        "intent_type": "single_persistence",
        "phase": "PERSISTENCE",
        "required": ["registry_modifications", "persistence_mechanism"],
        "assumed": [],
        "mitre": "T1547.001",
        "description": "Persistencia vía registro",
    },
    "H_LM_001": {
        "intent_type": "pass_the_hash",
        "phase": "LATERAL_MOVEMENT",
        "required": ["pass_the_hash_indicator", "lateral_movement_detected"],
        "assumed": [],
        "mitre": "T1550.002",
        "description": "Pass-the-Hash lateral movement",
    },
    "H_IA_001": {
        "intent_type": "spearphishing_execution",
        "phase": "INITIAL_ACCESS",
        "required": ["phishing_email_delivered", "malicious_attachment_executed"],
        "assumed": [],
        "mitre": "T1566.001",
        "description": "Spearphishing con ejecución de adjunto",
    },
    "H_IA_003": {
        "intent_type": "supply_chain_compromise",
        "phase": "INITIAL_ACCESS",
        "required": ["hardware_additions"],
        "assumed": ["attacker_has_physical_access", "attacker_controls_supply_chain"],
        "mitre": "T1195.001",
        "description": "Compromiso de cadena de suministro vía hardware malicioso",
    },
    "H_EX_001": {
        "intent_type": "command_line_abuse",
        "phase": "EXECUTION",
        "required": ["command_line_execution", "script_execution"],
        "assumed": [],
        "mitre": "T1059",
        "description": "Abuso de línea de comandos",
    },
}

# Artefactos sintéticos por tipo — valores realistas para logs
ARTIFACT_GENERATORS: Dict[str, Any] = {
    "timestamp_uniformity": lambda rng: {
        "artifact_id": "ts_unif_001",
        "type": "log_metadata",
        "value": True,
        "intervals_ms": [2000 + rng.randint(-1, 1) for _ in range(50)],
        "std_ms": round(rng.uniform(0.001, 0.5), 3),
        "note": "Uniformidad estadísticamente imposible en proceso orgánico",
    },
    "process_memory_contradiction": lambda rng: {
        "artifact_id": "mem_contr_001",
        "type": "memory_scan",
        "value": True,
        "active_processes": [],
        "expected_process": None,
        "note": "No hay proceso que pueda generar este patrón de logs",
    },
    "log_gap_intervals": lambda rng: {
        "artifact_id": "log_gap_001",
        "type": "temporal",
        "value": [2000] * 50,
        "variance": 0.001,
        "note": "Varianza de 0.001ms — no es jitter natural",
    },
    "log_deletion": lambda rng: {
        "artifact_id": "log_del_001",
        "type": "event_log",
        "event_id": 1102,
        "value": True,
        "cleared_by": f"WORKSTATION\\user{rng.randint(1,9)}",
        "note": "Event ID 1102: Security log cleared",
    },
    "event_log_clearing": lambda rng: {
        "artifact_id": "evtclr_001",
        "type": "event_log",
        "event_id": 104,
        "value": True,
        "note": "System log cleared via wevtutil.exe",
    },
    "artifact_overwrite": lambda rng: {
        "artifact_id": "art_ow_001",
        "type": "file_system",
        "value": True,
        "tool_detected": rng.choice(["sdelete.exe", "cipher /w", "BCWipe"]),
        "files_affected": rng.randint(10, 500),
    },
    "file_timestamp_modification": lambda rng: {
        "artifact_id": "ts_mod_001",
        "type": "mft",
        "value": True,
        "si_fn_delta_seconds": rng.randint(86400, 3650 * 24 * 3600),
        "note": "SI/FN divergencia > 24h — timestomping probable",
    },
    "outbound_data_transfer": lambda rng: {
        "artifact_id": "outbound_001",
        "type": "network_flow",
        "value": True,
        "destination_ip": f"{rng.randint(1,254)}.{rng.randint(1,254)}.{rng.randint(1,254)}.1",
        "bytes_transferred": rng.randint(100_000_000, 10_000_000_000),
    },
    "data_volume": lambda rng: {
        "artifact_id": "data_vol_001",
        "type": "network_metric",
        "value": True,
        "gb_transferred": round(rng.uniform(0.5, 50.0), 2),
        "duration_seconds": rng.randint(60, 3600),
    },
    "registry_modifications": lambda rng: {
        "artifact_id": "reg_mod_001",
        "type": "registry",
        "value": True,
        "key": rng.choice([
            r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
            r"HKLM\SYSTEM\CurrentControlSet\Services",
        ]),
        "modification_type": "CREATE",
    },
    "persistence_mechanism": lambda rng: {
        "artifact_id": "pers_001",
        "type": "registry",
        "value": True,
        "mechanism": rng.choice(["RunKey", "ScheduledTask", "ServiceInstall"]),
    },
    "pass_the_hash_indicator": lambda rng: {
        "artifact_id": "pth_001",
        "type": "auth_log",
        "value": True,
        "logon_type": 3,
        "auth_package": "NTLM",
        "src_ip": f"192.168.{rng.randint(1,10)}.{rng.randint(10,50)}",
    },
    "lateral_movement_detected": lambda rng: {
        "artifact_id": "lat_mov_001",
        "type": "auth_log",
        "value": True,
        "target_hosts": [f"HOST{rng.randint(1,99):02d}" for _ in range(rng.randint(2, 8))],
        "credential_reuse": True,
    },
    "phishing_email_delivered": lambda rng: {
        "artifact_id": "phish_001",
        "type": "email_header",
        "value": True,
        "sender": f"ceo@{rng.choice(['micros0ft','paypa1','amaz0n'])}.com",
        "spf_result": "FAIL",
        "dkim_result": "FAIL",
    },
    "malicious_attachment_executed": lambda rng: {
        "artifact_id": "att_exec_001",
        "type": "process",
        "value": True,
        "parent_process": "OUTLOOK.EXE",
        "child_process": rng.choice(["wscript.exe", "cmd.exe", "powershell.exe"]),
        "spawned_network_connection": True,
    },
    "command_line_execution": lambda rng: {
        "artifact_id": "cmd_exec_001",
        "type": "bash_history",
        "value": True,
        "commands": [
            "whoami /priv", "net localgroup administrators",
            f"powershell -enc {_random_b64(rng)}",
        ],
    },
    "script_execution": lambda rng: {
        "artifact_id": "script_001",
        "type": "powershell_log",
        "value": True,
        "script_block_logging": True,
        "obfuscated": rng.choice([True, False]),
    },
}

def _random_b64(rng: random.Random) -> str:
    import base64
    payload = bytes([rng.randint(0, 255) for _ in range(32)])
    return base64.b64encode(payload).decode()[:24]


# ══════════════════════════════════════════════════════════════════════════
# GENERADORES DE VECTORES ADVERSARIOS
# ══════════════════════════════════════════════════════════════════════════

def _build_log_entry(
    case_id: str,
    phase: str,
    artifacts: List[Dict],
    verdict_expected: str,
    hypothesis_expected: str,
    incomplete_coverage: bool,
    attack_vector: str,
    adversarial_note: str,
    rng: random.Random,
) -> Dict:
    """Construye un caso VIGÍA en formato canónico."""
    return {
        "case_id": case_id,
        "generated_at": _utcnow(),
        "adversarial_vector": attack_vector,
        "adversarial_note": adversarial_note,
        "phase_target": phase,
        "artifacts": artifacts,
        "expected_verdict": verdict_expected,
        "expected_hypothesis": hypothesis_expected,
        "incomplete_coverage_expected": incomplete_coverage,
        "robustness_assertion": (
            "AbductiveIntentEngine DEBE elegir hypothesis_expected "
            "o reportar incomplete_coverage=True. "
            "Si elige una hipótesis alternativa de menor cobertura, "
            "el sistema ha sido engañado por el vector adversario."
        ),
        "hash": hashlib.sha256(
            json.dumps(
                {"case_id": case_id, "phase": phase, "vector": attack_vector},
                sort_keys=True,
            ).encode()
        ).hexdigest()[:16],
    }


def gen_v1_missing_critical_artifact(rng: random.Random, idx: int) -> Tuple[Dict, Dict]:
    """
    V1 — ARTEFACTO_FALTANTE_CRÍTICO

    Escenario: Logs que mimetizan T1565.001 (Log Fabrication / H_DE_001)
    PERO omiten 'process_memory_contradiction' — el artefacto que distingue
    fabricación de una falla legítima de reloj.

    Sin ese artefacto, cost(H_DE_001) sube a 1 (missing_required=1).
    H_DE_002 (log_deletion) tiene cost=2 por sus assumed_artifacts.
    El motor DEBE elegir H_DE_001 con coverage=67% o reportar INCOMPLETE.

    Prueba de robustez: Si VIGÍA elige H_DE_002 (coverage=0%), fue engañado.
    """
    artifacts = []
    # Inyectar solo 2 de los 3 requeridos de H_DE_001
    for art_name in ["timestamp_uniformity", "log_gap_intervals"]:
        # OMITIR process_memory_contradiction — artefacto crítico faltante
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            artifacts.append(a)

    # Ruido: inyectar artefactos de H_DE_002 para confundir
    for art_name in ["log_deletion", "event_log_clearing"]:
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            a["adversarial_noise"] = True  # marcado para transparencia
            a["note"] = "RUIDO ADVERSARIO: artefacto de fase distinta inyectado para confundir"
            artifacts.append(a)

    entry = _build_log_entry(
        case_id=f"ADV_V1_{idx:03d}",
        phase="DEFENSE_EVASION",
        artifacts=artifacts,
        verdict_expected="SUSPICION",
        hypothesis_expected="H_DE_001",
        incomplete_coverage=True,  # process_memory_contradiction falta
        attack_vector="V1_MISSING_CRITICAL_ARTIFACT",
        adversarial_note=(
            "Omite 'process_memory_contradiction' de H_DE_001 e inyecta "
            "artefactos de H_DE_002. Objetivo: forzar elección de hipótesis "
            "de menor cobertura. VIGÍA debe elegir H_DE_001 (cost=1, cov=67%) "
            "sobre H_DE_002 (cost=2, cov=100% de sus propios requeridos) porque "
            "Ockham prioriza menor costo absoluto."
        ),
        rng=rng,
    )

    oracle = {
        "case_id": entry["case_id"],
        "vector": "V1",
        "observed_artifacts": ["timestamp_uniformity", "log_gap_intervals"],
        "missing_critical": ["process_memory_contradiction"],
        "decoy_artifacts": ["log_deletion", "event_log_clearing"],
        "correct_winner": "H_DE_001",
        "correct_cost": 1,  # 1 missing_required
        "correct_coverage": 67,  # 2/3 * 100
        "decoy_H_DE_002_cost": 2,  # assumed_artifacts = 2
        "decoy_H_DE_002_coverage": 100,
        "why_h_de_001_wins": (
            "cost(H_DE_001)=1 < cost(H_DE_002)=2. "
            "Ockham: menor supuesto gana aunque cobertura sea menor. "
            "El artefacto missing es observationally accessible — "
            "la ausencia de proceso es evidencia, no ausencia de evidencia."
        ),
        "incomplete_coverage": True,
        "robustness_pass": "winner==H_DE_001 AND coverage==67 AND incomplete_coverage==True",
    }
    return entry, oracle


def gen_v2_coverage_decoy(rng: random.Random, idx: int) -> Tuple[Dict, Dict]:
    """
    V2 — SEÑUELO_DE_COBERTURA

    Escenario: Exfiltración real (H_XF_001) pero el atacante también ejecutó
    comandos (H_EX_001) para saturar el análisis.

    VIGÍA analiza EXFILTRATION phase. H_XF_001 tiene ambos requeridos.
    El atacante inyecta artefactos de fase EXECUTION para que parezca
    que hay más evidencia de ejecución que de exfiltración.

    Prueba: El motor NO debe cruzar fases. Los artefactos de EXECUTION
    son invisibles en la fase EXFILTRATION (Lazy Abstraction).
    """
    artifacts = []

    # Artefactos legítimos de H_XF_001
    for art_name in ["outbound_data_transfer", "data_volume"]:
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            artifacts.append(a)

    # Decoy: artefactos de EXECUTION phase — no visibles en EXFILTRATION
    for art_name in ["command_line_execution", "script_execution"]:
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            a["adversarial_noise"] = True
            a["phase_origin"] = "EXECUTION"
            a["note"] = "DECOY: artefacto de fase EXECUTION en contexto EXFILTRATION"
            artifacts.append(a)

    entry = _build_log_entry(
        case_id=f"ADV_V2_{idx:03d}",
        phase="EXFILTRATION",
        artifacts=artifacts,
        verdict_expected="MALICE",
        hypothesis_expected="H_XF_001",
        incomplete_coverage=False,
        attack_vector="V2_COVERAGE_DECOY",
        adversarial_note=(
            "Inyecta 2 artefactos de EXECUTION en contexto EXFILTRATION. "
            "Si Lazy Abstraction funciona, son descartados. "
            "H_XF_001 cost=0, coverage=100%. Debe ganar limpio."
        ),
        rng=rng,
    )

    oracle = {
        "case_id": entry["case_id"],
        "vector": "V2",
        "phase_analyzed": "EXFILTRATION",
        "relevant_artifacts": ["outbound_data_transfer", "data_volume"],
        "decoy_artifacts_cross_phase": ["command_line_execution", "script_execution"],
        "correct_winner": "H_XF_001",
        "correct_cost": 0,
        "correct_coverage": 100,
        "lazy_abstraction_assertion": (
            "Artefactos de fase EXECUTION deben ser filtrados por "
            "VisibleVariablesEngine antes de llegar al AbductiveIntentEngine. "
            "Si llegan, el motor los ignorará porque no están en "
            "required_artifacts de ninguna hipótesis EXFILTRATION."
        ),
        "robustness_pass": "winner==H_XF_001 AND cost==0 AND coverage==100",
    }
    return entry, oracle


def gen_v3_cost_collision(rng: random.Random, idx: int) -> Tuple[Dict, Dict]:
    """
    V3 — COLISIÓN_DE_COSTO

    Escenario: Ataque diseñado para que dos hipótesis tengan el mismo costo.
    H_IA_001 (spearphishing, 2 required, 0 assumed) vs
    H_IA_003 (supply_chain, 1 required, 2 assumed).

    Si observamos solo 'phishing_email_delivered' (1/2 de IA_001):
      cost(H_IA_001) = 1 missing + 0 assumed = 1
      cost(H_IA_003) = 0 missing + 2 assumed = 2

    Si observamos 'hardware_additions' (1/1 de IA_003):
      cost(H_IA_001) = 2 + 0 = 2
      cost(H_IA_003) = 0 + 2 = 2  ← EMPATE

    En empate, Ockham usa desempate por coverage_score (-coverage_score):
      coverage(H_IA_001) = 0% (nada de sus requeridos)
      coverage(H_IA_003) = 100% (su único requerido observado)
    → H_IA_003 gana por cobertura.

    Tercer desempate: len(required_artifacts)
      len(H_IA_001.required) = 2 > len(H_IA_003.required) = 1
    → H_IA_003 gana también por simplicidad.

    Prueba: El sistema debe resolver el empate determinísticamente.
    """
    artifacts = []

    # Solo hardware_additions (requerido de H_IA_003)
    # NO inyectar phishing_email_delivered ni malicious_attachment_executed
    artifacts.append({
        "artifact_id": "hw_add_001",
        "artifact_name": "hardware_additions",
        "type": "usb",
        "observed": True,
        "value": True,
        "device_vendor": rng.choice(["unknown_vendor", "modified_keyboard", "rogue_hid"]),
        "registered_in_asset_mgmt": False,
        "note": "Hardware no registrado — posible implante físico",
    })

    # Ruido de bajo costo para empujar hacia H_IA_001
    artifacts.append({
        "artifact_id": "email_noise_001",
        "artifact_name": "email_received",
        "type": "email_header",
        "observed": True,
        "adversarial_noise": True,
        "value": "email legítimo de IT departamento",
        "spf_result": "PASS",
        "note": "RUIDO: email legítimo para simular contexto de phishing sin serlo",
    })

    entry = _build_log_entry(
        case_id=f"ADV_V3_{idx:03d}",
        phase="INITIAL_ACCESS",
        artifacts=artifacts,
        verdict_expected="SUSPICION",
        hypothesis_expected="H_IA_003",
        incomplete_coverage=True,
        attack_vector="V3_COST_COLLISION",
        adversarial_note=(
            "Empate artificial cost=2 entre H_IA_001 y H_IA_003. "
            "H_IA_003 debe ganar por cobertura(100%) vs cobertura(0%) "
            "y por menor len(required_artifacts). "
            "El email legítimo es ruido — no satisface phishing_email_delivered."
        ),
        rng=rng,
    )

    oracle = {
        "case_id": entry["case_id"],
        "vector": "V3",
        "tie_between": ["H_IA_001", "H_IA_003"],
        "tie_cost": 2,
        "H_IA_001": {"coverage": 0, "len_required": 2},
        "H_IA_003": {"coverage": 100, "len_required": 1},
        "tiebreak_key": "(cost, -coverage_score, len(required_artifacts))",
        "correct_winner": "H_IA_003",
        "sort_key_winner": (2, -100, 1),
        "sort_key_loser":  (2, 0, 2),
        "why": "(-100, 1) < (0, 2) → H_IA_003 gana en el segundo y tercer criterio",
        "robustness_pass": "winner==H_IA_003 AND deterministic_tiebreak==True",
    }
    return entry, oracle


def gen_v4_phase_polymorphism(rng: random.Random, idx: int) -> Tuple[Dict, Dict]:
    """
    V4 — POLIMORFISMO_DE_FASE

    Escenario: El atacante inyecta artefactos que satisfacen parcialmente
    múltiples fases simultáneamente para confundir la detección de IRPhase.

    Objetivo: Si VisibleVariablesEngine detecta la fase incorrecta
    (PERSISTENCE en lugar de LATERAL_MOVEMENT), el motor analizará
    los artefactos con el conjunto de hipótesis equivocado.

    Inyección: registry_modifications (PERSISTENCE) + pass_the_hash_indicator
    (LATERAL_MOVEMENT) + lateral_movement_detected (LATERAL_MOVEMENT).

    Si la fase detectada es PERSISTENCE:
      → Analiza con hipótesis de PERSISTENCE
      → H_PE_001 tiene registry_modifications como requerido → cost=0
      → El artefacto pass_the_hash_indicator es invisible en esa fase
      → VIGÍA pierde el vector de lateral movement

    Prueba: La fase correcta es LATERAL_MOVEMENT. El sistema debe detectarla
    correctamente por la presencia de ambos artefactos LM vs solo 1 de PE.
    """
    artifacts = []

    # Artefactos LM — los reales
    for art_name in ["pass_the_hash_indicator", "lateral_movement_detected"]:
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            artifacts.append(a)

    # Ruido de PERSISTENCE — para confundir detección de fase
    gen_reg = ARTIFACT_GENERATORS.get("registry_modifications")
    if gen_reg:
        a = gen_reg(rng)
        a["observed"] = True
        a["artifact_name"] = "registry_modifications"
        a["adversarial_noise"] = True
        a["note"] = "RUIDO POLIMÓRFICO: clave de registro creada como side-effect del PtH, no como persistencia"
        artifacts.append(a)

    entry = _build_log_entry(
        case_id=f"ADV_V4_{idx:03d}",
        phase="LATERAL_MOVEMENT",
        artifacts=artifacts,
        verdict_expected="MALICE",
        hypothesis_expected="H_LM_001",
        incomplete_coverage=False,
        attack_vector="V4_PHASE_POLYMORPHISM",
        adversarial_note=(
            "Mezcla artefactos de LATERAL_MOVEMENT (PtH) y PERSISTENCE (registry). "
            "Si VisibleVariablesEngine detecta PERSISTENCE, pierde el PtH. "
            "La fase correcta es LATERAL_MOVEMENT: ambos PtH artifacts presentes. "
            "H_LM_001 cost=0, coverage=100%. H_PE_001 en PERSISTENCE también cost=0 "
            "pero en la fase equivocada — el perito no verá el lateral movement."
        ),
        rng=rng,
    )

    oracle = {
        "case_id": entry["case_id"],
        "vector": "V4",
        "correct_phase": "LATERAL_MOVEMENT",
        "decoy_phase": "PERSISTENCE",
        "artifacts_lm": ["pass_the_hash_indicator", "lateral_movement_detected"],
        "artifacts_pe_noise": ["registry_modifications"],
        "correct_winner": "H_LM_001",
        "phase_detection_assertion": (
            "VisibleVariablesEngine debe detectar LATERAL_MOVEMENT "
            "porque los artefactos de LM son más específicos y "
            "su cobertura en esa fase es 100% vs 33% en PERSISTENCE. "
            "La presencia de registry_modifications como side-effect "
            "no debe reclasificar la fase."
        ),
        "if_wrong_phase_detected": {
            "wrong_phase": "PERSISTENCE",
            "wrong_winner": "H_PE_001",
            "consequence": "PtH invisible — movimiento lateral no reportado al SIEM",
        },
        "robustness_pass": "detected_phase==LATERAL_MOVEMENT AND winner==H_LM_001",
    }
    return entry, oracle


# ══════════════════════════════════════════════════════════════════════════
# GENERADORES COMPUESTOS — ESCENARIOS MULTI-VECTOR
# ══════════════════════════════════════════════════════════════════════════

def gen_compound_apt_scenario(rng: random.Random, idx: int) -> Tuple[List[Dict], List[Dict]]:
    """
    Escenario APT completo — 4 fases encadenadas con ruido adversario.
    Simula un actor que usa anti-forense mientras exfiltra.

    Cadena: INITIAL_ACCESS → DEFENSE_EVASION (ruido) → EXFILTRATION → CLEANUP
    El CLEANUP omite artefactos para forzar incomplete_coverage en esa fase.
    """
    entries, oracles = [], []

    # Fase 1: IA limpia
    e1, o1 = gen_v2_coverage_decoy(rng, idx * 10 + 1)
    e1["case_id"] = f"ADV_APT_{idx:03d}_IA"
    e1["chain_position"] = 1
    e1["chain_total"] = 4
    entries.append(e1); oracles.append(o1)

    # Fase 2: DE con V1 (missing critical)
    e2, o2 = gen_v1_missing_critical_artifact(rng, idx * 10 + 2)
    e2["case_id"] = f"ADV_APT_{idx:03d}_DE"
    e2["chain_position"] = 2
    entries.append(e2); oracles.append(o2)

    # Fase 3: XF limpia (confirma la exfiltración)
    artifacts_xf = []
    for art_name in ["outbound_data_transfer", "data_volume"]:
        gen = ARTIFACT_GENERATORS.get(art_name)
        if gen:
            a = gen(rng)
            a["observed"] = True
            a["artifact_name"] = art_name
            artifacts_xf.append(a)

    e3 = _build_log_entry(
        case_id=f"ADV_APT_{idx:03d}_XF",
        phase="EXFILTRATION",
        artifacts=artifacts_xf,
        verdict_expected="MALICE",
        hypothesis_expected="H_XF_001",
        incomplete_coverage=False,
        attack_vector="COMPOUND_APT_XF",
        adversarial_note="Fase 3 APT: exfiltración confirmada post anti-forense.",
        rng=rng,
    )
    e3["chain_position"] = 3
    o3 = {"case_id": e3["case_id"], "correct_winner": "H_XF_001", "cost": 0, "coverage": 100}
    entries.append(e3); oracles.append(o3)

    # Fase 4: CLEANUP — V3 cost collision forzado
    e4, o4 = gen_v3_cost_collision(rng, idx * 10 + 4)
    e4["case_id"] = f"ADV_APT_{idx:03d}_CL"
    e4["chain_position"] = 4
    entries.append(e4); oracles.append(o4)

    return entries, oracles


# ══════════════════════════════════════════════════════════════════════════
# RUNNER PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════

VECTOR_GENERATORS = {
    "V1": gen_v1_missing_critical_artifact,
    "V2": gen_v2_coverage_decoy,
    "V3": gen_v3_cost_collision,
    "V4": gen_v4_phase_polymorphism,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="VIGÍA Red Team — Generador de Escenarios Adversarios para Abducción",
    )
    parser.add_argument("--output", default="./red_team",
                        help="Directorio de salida (default: ./red_team)")
    parser.add_argument("--count", type=int, default=5,
                        help="Casos por vector (default: 5)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Semilla aleatoria para reproducibilidad (default: 42)")
    parser.add_argument("--vector", nargs="+", choices=list(VECTOR_GENERATORS) + ["APT"],
                        default=list(VECTOR_GENERATORS) + ["APT"],
                        help="Vectores a generar (default: todos)")
    parser.add_argument("--json", action="store_true",
                        help="Salida en .json además de .jsonl")
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    all_oracles: List[Dict] = []
    total_cases = 0

    print("═" * 68)
    print("VIGÍA RED TEAM — Generador de Escenarios Adversarios")
    print("═" * 68)
    print(f"  Directorio: {out_dir.resolve()}")
    print(f"  Seed:       {args.seed}")
    print(f"  Vectores:   {', '.join(args.vector)}")
    print(f"  Casos/vector: {args.count}")
    print()

    for vector in args.vector:
        if vector == "APT":
            entries_all, oracles_all = [], []
            for i in range(args.count):
                es, os_ = gen_compound_apt_scenario(rng, i)
                entries_all.extend(es)
                oracles_all.extend(os_)

            out_path = out_dir / f"adversarial_APT.jsonl"
            with open(out_path, "w", encoding="utf-8") as f:
                for e in entries_all:
                    f.write(json.dumps(e, ensure_ascii=True) + "\n")

            all_oracles.extend(oracles_all)
            total_cases += len(entries_all)
            print(f"  [APT] {len(entries_all)} entradas → {out_path.name}")
            continue

        gen_fn = VECTOR_GENERATORS[vector]
        entries: List[Dict] = []
        oracles: List[Dict] = []

        for i in range(args.count):
            entry, oracle = gen_fn(rng, i)
            entries.append(entry)
            oracles.append(oracle)

        out_path = out_dir / f"adversarial_{vector}.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=True) + "\n")

        all_oracles.extend(oracles)
        total_cases += len(entries)
        print(f"  [{vector}] {len(entries)} casos → {out_path.name}")

    # Oracle completo
    oracle_path = out_dir / "adversarial_oracle.json"
    oracle_doc = {
        "generated_at": _utcnow(),
        "seed": args.seed,
        "total_cases": total_cases,
        "description": (
            "Tabla de verdad para validación de robustez del AbductiveIntentEngine. "
            "Cada entrada especifica el winner esperado, costo, cobertura y "
            "la condición de robustez_pass que VIGÍA debe satisfacer."
        ),
        "vectors": {
            "V1": "Artefacto crítico faltante — fuerza incomplete_coverage",
            "V2": "Señuelo de cobertura cruzando fases — prueba Lazy Abstraction",
            "V3": "Colisión de costo — prueba desempate determinístico",
            "V4": "Polimorfismo de fase — prueba detección de IRPhase",
            "APT": "Escenario APT encadenado — prueba consistencia multi-fase",
        },
        "cases": all_oracles,
    }
    oracle_path.write_text(
        json.dumps(oracle_doc, indent=2, sort_keys=True, ensure_ascii=True),
        encoding="utf-8",
    )

    print()
    print(f"  Oracle → {oracle_path.name}")
    print(f"\n  Total: {total_cases} casos adversarios generados")
    print()
    print("  Para validar contra VIGÍA:")
    print(f"    python3 run_all_cases.py --input {out_dir}/ --oracle {oracle_path}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
