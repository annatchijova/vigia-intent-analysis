

Te los hago ahora mismo. Van a ser **5 casos** que cubren todo el espectro:

---

## Caso 1: Temporal Imposible (EFFECT_BEFORE_CAUSE)

```json
{
  "case_id": "case_001_temporal",
  "name": "Impossible Timeline — Effect Before Cause",
  "description": "File write occurs before the process that created it was spawned. Classic timestomp + process hollowing.",
  "artifacts": [
    {
      "artifact_id": "proc_001",
      "evidence_type": "memory_process",
      "source_tool": "list_processes",
      "timestamp": "2026-04-10T10:00:05Z",
      "raw_score": 0.9,
      "prior_trust": 0.95,
      "provenance_chain": ["sha256:abc123def456", "sha256:789xyz012"],
      "description": "Process svchost.exe (PID 4412) spawned at 10:00:05",
      "metadata": {"pid": 4412, "parent_pid": 888, "image": "svchost.exe"}
    },
    {
      "artifact_id": "file_001",
      "evidence_type": "file_timestamp",
      "source_tool": "read_evidence",
      "timestamp": "2026-04-10T10:00:00Z",
      "raw_score": 0.85,
      "prior_trust": 0.7,
      "provenance_chain": ["sha256:aaa111bbb222"],
      "description": "C:\\Windows\\Temp\\payload.dll written at 10:00:00 — 5s BEFORE PID 4412 existed",
      "metadata": {"path": "C:\\Windows\\Temp\\payload.dll", "size_bytes": 143360, "writer_pid": 4412}
    },
    {
      "artifact_id": "log_001",
      "evidence_type": "log_entry",
      "source_tool": "read_evidence",
      "timestamp": "2026-04-10T10:00:02Z",
      "raw_score": 0.6,
      "prior_trust": 0.5,
      "provenance_chain": ["sha256:ccc333ddd444"],
      "description": "EventLog 4663: File creation by PID 4412 at 10:00:02",
      "metadata": {"event_id": 4663, "object_name": "payload.dll", "process_id": 4412}
    }
  ],
  "temporal_violations": [
    {
      "type": "EFFECT_BEFORE_CAUSE",
      "severity": 1.0,
      "cause": {"artifact_id": "proc_001", "timestamp": "2026-04-10T10:00:05Z", "description": "Process creation"},
      "effect": {"artifact_id": "file_001", "timestamp": "2026-04-10T10:00:00Z", "description": "File written by that process"},
      "delta_seconds": -5,
      "interpretation": "File written 5s before process existed. Physically impossible — timestamps manipulated (T1070.006)."
    }
  ],
  "expected_verdict": "MALICE",
  "expected_confidence": 0.95,
  "expected_mitre_ttps": ["T1070.006", "T1055", "T1036"],
  "peirce_chain": {
    "firstness": "File write timestamp precedes process spawn by 5 seconds",
    "secondness": "No clock skew explains negative delta — this is physical law violation",
    "thirdness": "Deliberate timestomp to plant pre-existing payload"
  },
  "demo_command": "python run_vigia_case.py cases/case_001_temporal.json",
  "demo_quote": "Here, a file is written before the process exists. This is physically impossible. The system flags fabrication."
}
```

---

## Caso 2: Log Fabrication (STATISTICAL_UNIFORMITY) — CON GCI

```json
{
  "case_id": "case_002_log_fabrication",
  "name": "Log Fabrication — Statistical Uniformity + GCI Detection",
  "description": "50 log entries with suspiciously uniform 2-second intervals. GCI detects CONSTANT_SLEEP pattern and infers eml(1, exp(e - 2.0)).",
  "artifacts": [
    {
      "artifact_id": "log_bulk_001",
      "evidence_type": "log_entry",
      "source_tool": "read_evidence",
      "timestamp": "2026-04-10T11:00:00Z",
      "raw_score": 0.8,
      "prior_trust": 0.65,
      "provenance_chain": ["sha256:fabricated_chain_001"],
      "description": "50 log entries: AuthFailure events, 2.000s intervals, entropy=3.145 each",
      "metadata": {
        "count": 50,
        "timestamps": [1765432800.0 + i*2.0 for i in range(50)],
        "interval_seconds_mean": 2.0,
        "interval_seconds_std": 0.001,
        "entropy_mean": 3.145,
        "entropy_std": 0.002,
        "source_ips": ["192.168.1.100"],
        "uniformity_flag": true
      }
    },
    {
      "artifact_id": "memory_001",
      "evidence_type": "memory_process",
      "source_tool": "list_processes",
      "timestamp": "2026-04-10T11:01:40Z",
      "raw_score": 0.1,
      "prior_trust": 0.95,
      "provenance_chain": ["sha256:mem_chain_authentic_001", "sha256:mem_chain_authentic_002"],
      "description": "Memory scan: NO brute force tool running. No network socket matching log source.",
      "metadata": {"active_network_sockets": [], "related_process": null}
    }
  ],
  "temporal_violations": [
    {
      "type": "STATISTICAL_UNIFORMITY",
      "severity": 0.85,
      "cause": {"artifact_id": "log_bulk_001", "description": "50 log events"},
      "effect": {"artifact_id": "log_bulk_001", "description": "Interval std=0.001s — inhuman precision"},
      "interpretation": "2.000s ± 0.001s intervals across 50 events. Human typing or real attacks have variance > 0.1s. This is scripted injection."
    }
  ],
  "gci_analysis": {
    "pattern": "DETERMINISTIC_CONSTANT",
    "is_algorithmic": true,
    "fit_score": 0.982,
    "cv": 0.004,
    "law": "Δt = 2.0000 ± 0.0001 (MAD)",
    "canonical_eml_form": "eml(1, exp(e - 2.0))",
    "representation_note": "Forma canónica en espacio EML de una ley constante. La inferencia se basa en MAD + CV."
  },
  "expected_verdict": "SUSPICION",
  "expected_score_range": [0.3, 0.55],
  "expected_mitre_ttps": ["T1497", "T1565.001", "T1070.006"],
  "peirce_chain": {
    "firstness": "50 AuthFailure log entries with near-perfect 2s intervals",
    "secondness": "Memory shows no process capable of generating these events. GCI detects CONSTANT_SLEEP pattern.",
    "thirdness": "Logs are fabricated — scripted injection with time.sleep(2.0). The attacker's habit is automation, not human behavior."
  },
  "demo_command": "python compare_baseline.py --case cases/case_002_log_fabrication.json",
  "demo_quote": "The baseline sees 50 strong log entries and concludes MALICE. VIGÍA detects temporal uniformity and memory contradiction, GCI infers the script pattern, reducing confidence and avoiding a false positive."
}
```

---

## Caso 3: False Flag (CULTURAL_VS_TECHNICAL)

```json
{
  "case_id": "case_003_false_flag",
  "name": "False Flag — Cultural Attribution Mismatch",
  "description": "High cultural markers pointing to Russian origin combined with near-zero technical evidence. Classic false flag pattern.",
  "artifacts": [
    {
      "artifact_id": "cultural_001",
      "evidence_type": "cultural_marker",
      "source_tool": "infer_intent",
      "timestamp": "2026-04-10T12:00:00Z",
      "raw_score": 0.85,
      "prior_trust": 0.3,
      "provenance_chain": ["sha256:cultural_chain_001"],
      "description": "Cyrillic filename: 'отчет_финансы.docx'. Keyboard layout: RU. Timezone: UTC+3.",
      "metadata": {"cyrillic_filenames": 3, "keyboard_layout_detected": "RU", "timezone_offset": "+03:00"}
    },
    {
      "artifact_id": "technical_001",
      "evidence_type": "memory_process",
      "source_tool": "list_processes",
      "timestamp": "2026-04-10T12:00:10Z",
      "raw_score": 0.05,
      "prior_trust": 0.95,
      "provenance_chain": ["sha256:mem_chain_001", "sha256:mem_chain_002"],
      "description": "Memory: No process injection. No kernel anomalies. Clean system state.",
      "metadata": {"injections_detected": 0, "kernel_anomalies": 0}
    },
    {
      "artifact_id": "technical_002",
      "evidence_type": "lsass_session",
      "source_tool": "list_processes",
      "timestamp": "2026-04-10T12:00:12Z",
      "raw_score": 0.08,
      "prior_trust": 0.95,
      "provenance_chain": ["sha256:lsass_chain_001"],
      "description": "LSASS: No credential dumping. Normal session count.",
      "metadata": {"sessions": 2, "anomalies": 0}
    }
  ],
  "caie_fractures": [
    {
      "fracture_type": "FALSE_FLAG_PATTERN",
      "severity": 0.82,
      "artifact_a": "Cultural markers (avg=0.85)",
      "artifact_b": "Technical evidence (avg=0.065)",
      "mitre_ttp": "T1585",
      "interpretation": "HIGH cultural attribution with NEAR-ZERO technical evidence. Consistent with planted identity markers. Real APT operators leave technical traces. This actor only left flags."
    }
  ],
  "expected_verdict": "MALICE",
  "expected_confidence": 0.75,
  "expected_mitre_ttps": ["T1585", "T1036.005"],
  "peirce_chain": {
    "firstness": "Cyrillic filenames, RU keyboard, UTC+3 timezone all present",
    "secondness": "Memory, LSASS, kernel — ALL clean despite claimed sophisticated attacker",
    "thirdness": "Cultural markers were planted. Real attacker is not Russian. The habit is disguise, not action."
  },
  "demo_command": "python run_vigia_case.py cases/case_003_false_flag.json",
  "demo_quote": "Naive sees low-confidence indicators and says NOISE. VIGÍA detects a FALSE_FLAG_PATTERN fracture: the cultural markers were deliberately planted. Planting evidence IS the malicious act."
}
```

---

## Caso 4: Provenance Break (Chain of Custody Collapsed)

```json
{
  "case_id": "case_004_provenance_break",
  "name": "Provenance Break — Chain of Custody Collapsed",
  "description": "High-quality evidence with strong indicators — but the chain of custody has a missing ancestor. Trust collapses to near-zero. Traditional systems accept this. VIGÍA rejects it.",
  "artifacts": [
    {
      "artifact_id": "disk_001",
      "evidence_type": "file_hash",
      "source_tool": "generate_forensic_hash",
      "timestamp": "2026-04-10T13:00:00Z",
      "raw_score": 0.92,
      "prior_trust": 0.9,
      "provenance_chain": [],
      "description": "SHA-256 of suspicious binary: known malware hash match (VirusTotal: 47/70). BUT: no acquisition record. No chain from disk image to this file.",
      "metadata": {
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "vt_detections": 47,
        "acquisition_record": null,
        "examiner_signature": null,
        "parent_image_hash": null
      }
    },
    {
      "artifact_id": "disk_002",
      "evidence_type": "file_timestamp",
      "source_tool": "read_evidence",
      "timestamp": "2026-04-10T13:00:05Z",
      "raw_score": 0.88,
      "prior_trust": 0.85,
      "provenance_chain": ["sha256:partial_chain_ORPHANED"],
      "description": "File creation timestamp matches known C2 beacon interval. Strong indicator — but provenance chain has single orphaned hash, no root.",
      "metadata": {
        "created": "2026-04-09T03:14:00Z",
        "modified": "2026-04-09T03:14:00Z",
        "chain_root": null,
        "chain_orphaned": true
      }
    }
  ],
  "provenance_analysis": {
    "chain_status": "BROKEN",
    "missing_links": ["acquisition_record", "examiner_signature", "disk_image_hash"],
    "effective_trust": 0.05,
    "daubert_admissible": false,
    "reason": "No root of trust. Cannot verify evidence was not modified post-acquisition or planted post-incident."
  },
  "expected_verdict": "NOISE",
  "expected_confidence": 0.15,
  "expected_mitre_ttps": ["T1565.001"],
  "naive_verdict": "MALICE",
  "naive_score": 0.89,
  "peirce_chain": {
    "firstness": "47/70 VirusTotal detections — looks like strong evidence",
    "secondness": "No acquisition record. No examiner signature. Hash chain has no root.",
    "thirdness": "Evidence integrity cannot be verified. Under Daubert, this is inadmissible."
  },
  "demo_command": "python run_vigia_case.py cases/case_004_provenance_break.json",
  "demo_quote": "This case contains high-quality evidence with strong indicators. However, the chain of custody is broken. VIGÍA collapses trust and rejects the evidence. Traditional systems would accept this. VIGÍA does not."
}
```

---

## Caso 5: Multi-Source Consistent (Alta Confianza)

```json
{
  "case_id": "case_005_multi_source",
  "name": "Multi-Source Consistent — High Trust Evidence",
  "description": "Independent sources (memory, network, disk) with consistent timeline, intact provenance chains, and low cross-correlation. High composite trust.",
  "artifacts": [
    {
      "artifact_id": "memory_multi_001",
      "evidence_type": "memory_process",
      "source_tool": "list_processes",
      "timestamp": "2026-04-10T14:00:00Z",
      "raw_score": 0.91,
      "prior_trust": 0.95,
      "provenance_chain": ["sha256:acquire_001", "sha256:examiner_sign_001", "sha256:hash_chain_root_001"],
      "description": "Memory: Process injection detected. PID 2244 injected into lsass.exe.",
      "metadata": {"injected_pid": 2244, "target": "lsass.exe", "technique": "process_hollowing"}
    },
    {
      "artifact_id": "network_multi_001",
      "evidence_type": "dns_record",
      "source_tool": "audit_network",
      "timestamp": "2026-04-10T14:00:15Z",
      "raw_score": 0.78,
      "prior_trust": 0.82,
      "provenance_chain": ["sha256:pcap_001", "sha256:netflow_hash_001"],
      "description": "DNS: beacon to c2-domain.evil every 300s ± 45s.",
      "metadata": {"domain": "c2-domain.evil", "interval_seconds": 300, "interval_jitter": 45, "query_count": 12}
    },
    {
      "artifact_id": "disk_multi_001",
      "evidence_type": "file_hash",
      "source_tool": "generate_forensic_hash",
      "timestamp": "2026-04-10T14:00:30Z",
      "raw_score": 0.88,
      "prior_trust": 0.92,
      "provenance_chain": ["sha256:image_hash_001", "sha256:examiner_sign_002", "sha256:sector_hash_001"],
      "description": "Disk: beacon DLL found in C:\\Windows\\System32\\windef.dll. Hash matches known Cobalt Strike beacon.",
      "metadata": {
        "path": "C:\\Windows\\System32\\windef.dll",
        "sha256": "aabbccdd1122334455667788990011223344556677889900aabbccddeeff0011",
        "vt_detections": 52
      }
    },
    {
      "artifact_id": "tpm_multi_001",
      "evidence_type": "TPM_attestation",
      "source_tool": "audit_network",
      "timestamp": "2026-04-10T14:01:00Z",
      "raw_score": 0.97,
      "prior_trust": 0.99,
      "provenance_chain": ["sha256:tpm_pcr_001", "sha256:tpm_quote_001"],
      "description": "TPM PCR values confirm boot integrity was NOT compromised. Attack is post-boot.",
      "metadata": {"pcr_0_valid": true, "pcr_7_valid": true, "spoofability": 0.05}
    }
  ],
  "expected_verdict": "MALICE",
  "expected_confidence": 0.94,
  "expected_mitre_ttps": ["T1055", "T1036.005", "T1498"],
  "peirce_chain": {
    "firstness": "Independent memory, network, disk, and TPM artifacts all flagging the same entity",
    "secondness": "Low cross-correlation — these sources cannot have been fabricated together",
    "thirdness": "Cobalt Strike beacon with process injection confirmed. Evidence is reliable."
  },
  "demo_command": "python run_vigia_case.py cases/case_005_multi_source.json",
  "demo_quote": "Independent sources, high trust, consistent timeline. Correlation is low, and trust remains high. VIGÍA confirms this as reliable evidence."
}
```

---

## Resumen de los 5 casos

| Caso | Tipo | Veredicto Esperado | Feature destacada |
|------|------|-------------------|-------------------|
| 001 | Temporal imposible | MALICE | EFFECT_BEFORE_CAUSE (hard gate) |
| 002 | Log fabrication | SUSPICION | GCI + STATISTICAL_UNIFORMITY |
| 003 | False flag | MALICE | FALSE_FLAG_PATTERN |
| 004 | Provenance break | NOISE | Cadena de custodia rota |
| 005 | Multi-source | MALICE | Alta confianza por fuentes independientes |

---

## Cómo usarlos

```bash
# Correr un caso individual
python scripts/run_vigia_case.py cases/case_001_temporal.json

# Correr todos
python scripts/run_all_cases.py

# Comparar con naive
python scripts/compare_baseline.py

# Generar reporte
python scripts/generate_report.py
```

---

**¿Necesitás algún caso adicional o ajustar algo?**
