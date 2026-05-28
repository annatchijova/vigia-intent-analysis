# vigia/tests/adversarial/vabs1_fuzzer.py
#
# VIGÍA Adversarial Benchmark Suite v1 — Case Fuzzer
# =====================================================
# Genera 16 casos adversariales nuevos que cubren los gaps
# epistemicos, causales, estadisticos y arquitectonicos
# identificados por el red team (ChatGPT) y auditoria
# epistemica (Kimi/Moonshot).
#
# ALCANCE: Complementa fuzzer_nuevos.py (P3, S1-S10, casos
# epistemicos a nivel de supuesto). VABS-1 opera a nivel de
# ESCENARIO FORENSE CONCRETO — artefactos reales, no
# abstracciones.
#
# TAXONOMIA:
#   T1  Epistemic collapse (observational equivalence, null-signal)
#   T2  Causal graph manipulation (relabeling, post-hoc causality)
#   T3  Sensor dependency exploits (aliasing, shared latent model)
#   T4  Statistical invariance attacks (entropy preservation, LR trap)
#   T5  Cross-layer semantic decoupling
#   T6  Temporal manipulation (consistent drift, compressed evidence)
#   T7  Baseline poisoning (adaptive normalization, gradual drift)
#   T8  Fractal consistency / absence topology
#
# TODOS LOS CASOS EN INGLES — requerimiento de hackathon SANS.
#
# INVARIANTES:
#   - Sin floats en scores de criticidad (Fraction via assumption graph).
#   - sort_keys=True + ensure_ascii=False en toda serializacion JSON.
#   - case_id sigue patron VABS-TN-NNN para trazabilidad.
#   - "expected" incluye "detectable" bool para diferenciar hard limits
#     epistemologicos (no detectable, sistema debe ABSTAIN honestamente)
#     de fallas de implementacion (detectable, sistema debe detectar).
#
# AUDITORIA: Claude (Anthropic), mayo 2026.
# Basado en: ChatGPT red team (docs 1-2) + Kimi VABS-1 spec (doc 3).
# Casos P3 ya existentes: S1-S10 en fuzzer_nuevos.py — no duplicar.

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from .vabs1_assumption_graph import (
    ASSUMPTION_GRAPH_VABS1,
    propagate_breaks_vabs1,
    criticality_vabs1,
)


class VABS1Fuzzer:
    """
    Genera los 16 casos adversariales de VABS-1.

    Uso:
        fuzzer = VABS1Fuzzer()
        cases = fuzzer.generate_all()
        fuzzer.save(Path("./adversarial_tests_vabs1"))
    """

    def __init__(self) -> None:
        self.cases: List[Dict] = []

    # ── T1: Epistemic collapse ─────────────────────────────────────────────

    def case_t1_001_observational_equivalence(self) -> Dict:
        """
        T1-001: Two worlds, identical artifact distributions.
        P(E|benign) == P(E|malicious) for all observable evidence.
        LR collapses to 1. System MUST emit ABSTAIN_EPISTEMIC, not a
        confident BENIGN verdict.
        """
        # Both worlds produce: normal login, file access, network connection.
        # The difference is intentionality — not observable from artifacts alone.
        artifacts = []
        for i, label in enumerate(["benign_world", "malicious_world"]):
            artifacts.append({
                "source_tool": f"siem_{label}",
                "evidence_type": "log_entry",
                "raw_score": 0.50,
                "metadata": {
                    "event_id": 4624,
                    "user": "svc_backup",
                    "src_ip": "10.0.1.15",
                    "dst_port": 445,
                    "timestamp": "2024-03-15T02:00:00Z",
                    "world_label": label,
                    "note": (
                        "Structurally identical event. "
                        "Benign: scheduled backup. Malicious: lateral movement. "
                        "No artifact distinguishes the two worlds."
                    ),
                },
            })
        return {
            "case_id": "VABS-T1-001",
            "vabs_category": "T1",
            "breaks": ["world_distinguishability"],
            "description": (
                "Observational equivalence collapse: backup service login at 02:00 "
                "is statistically identical under both benign (scheduled task) and "
                "malicious (credential-reuse lateral movement) hypotheses. "
                "P(E|benign) == P(E|malicious) across all observable dimensions."
            ),
            "artifacts": artifacts,
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_EPISTEMIC",
                "reason": (
                    "Hard epistemological limit. LR == 1.0. "
                    "System must not emit a confident verdict. "
                    "ABSTAIN with full audit trail is the correct response."
                ),
            },
        }

    def case_t1_002_null_signal_adversary(self) -> Dict:
        """
        T1-002: Adversary operates entirely outside the observable boundary.
        No logs, no anomalies, no absences. Action performed via
        firmware-level implant that bypasses all OS-level instrumentation.
        """
        return {
            "case_id": "VABS-T1-002",
            "vabs_category": "T1",
            "breaks": ["null_signal_epistemology"],
            "description": (
                "Null-signal adversary: attacker uses a firmware-level implant "
                "(BMC/UEFI) that exfiltrates data via out-of-band management "
                "interface. No OS logs, no EDR telemetry, no network flows "
                "visible to the OS layer. Complete action within the unobservable "
                "boundary."
            ),
            "artifacts": [
                {
                    "source_tool": "win_evtx",
                    "evidence_type": "log_entry",
                    "raw_score": 0.02,
                    "metadata": {
                        "summary": "Normal operational logs only. No anomalies.",
                        "event_count": 1247,
                        "anomaly_count": 0,
                        "timestamp_range": "2024-03-15T00:00:00Z/2024-03-15T23:59:59Z",
                    },
                },
            ],
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_EPISTEMIC",
                "reason": (
                    "Hard limit: firmware-level exfiltration is outside the "
                    "observable boundary of OS-level forensics. "
                    "Emitting BENIGN would be a false negative. "
                    "ABSTAIN_EPISTEMIC with documented observability gap is correct."
                ),
            },
        }

    # ── T2: Causal graph manipulation ─────────────────────────────────────

    def case_t2_001_causal_relabeling(self) -> Dict:
        """
        T2-001: Causal graph node relabeling attack.
        Identical process tree structure, parent/child labels swapped.
        'A spawned B' vs 'B spawned A' — statistically identical graphs,
        semantically inverted causality.
        """
        return {
            "case_id": "VABS-T2-001",
            "vabs_category": "T2",
            "breaks": ["node_identity_invariance"],
            "description": (
                "Causal graph relabeling: attacker injects process tree where "
                "lsass.exe (pid=512) appears as the parent of services.exe (pid=676). "
                "Normal Windows invariant is inverted (services.exe spawns lsass.exe). "
                "Statistical graph structure is identical; semantic meaning is wrong."
            ),
            "artifacts": [
                {
                    "source_tool": "volatility_pstree",
                    "evidence_type": "memory_process",
                    "raw_score": 0.88,
                    "metadata": {
                        "process_name": "lsass.exe",
                        "pid": 512,
                        "parent_pid": 676,
                        "parent_name": "services.exe",
                        "note": "INVERTED: lsass.exe should be child of wininit.exe (pid=408), not parent of services.exe",
                    },
                },
                {
                    "source_tool": "volatility_pstree",
                    "evidence_type": "memory_process",
                    "raw_score": 0.88,
                    "metadata": {
                        "process_name": "services.exe",
                        "pid": 676,
                        "parent_pid": 512,
                        "parent_name": "lsass.exe",
                        "note": "INVERTED: services.exe normally spawned by wininit.exe, not by lsass.exe",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "MALICE",
                "reason": (
                    "Windows process hierarchy invariant violated: "
                    "lsass.exe is never the parent of services.exe. "
                    "CAIE PROCESS_HIERARCHY_ANOMALY must fire."
                ),
            },
        }

    def case_t2_002_post_hoc_causality(self) -> Dict:
        """
        T2-002: Latent delayed causality inversion.
        Effect at T=0, legitimately-generated 'cause' appears at T+10min.
        System auto-config fires after the event it supposedly triggered.
        EFFECT_BEFORE_CAUSE must fire on structural grounds.
        """
        return {
            "case_id": "VABS-T2-002",
            "vabs_category": "T2",
            "breaks": ["post_hoc_causality_rejection"],
            "description": (
                "Post-hoc causality inversion: scheduled task 'BackupJob' fires "
                "at T=08:00:00 accessing sensitive share. GPO policy legitimately "
                "authorizing this specific access appears at T=08:10:00 (10 minutes "
                "after the access event it supposedly governs). "
                "Policy generated by DC auto-config, valid cert, valid timestamp."
            ),
            "artifacts": [
                {
                    "source_tool": "win_evtx",
                    "evidence_type": "log_entry",
                    "raw_score": 0.85,
                    "metadata": {
                        "event_id": 5145,
                        "timestamp": "2024-03-15T08:00:00Z",
                        "user": "svc_backup",
                        "share": "\\\\DC01\\ADMIN$",
                        "access_type": "ReadData",
                    },
                },
                {
                    "source_tool": "dc_event_log",
                    "evidence_type": "log_entry",
                    "raw_score": 0.10,
                    "metadata": {
                        "event_id": 4739,
                        "timestamp": "2024-03-15T08:10:00Z",
                        "policy": "GPO_BackupAccess_ADMIN",
                        "gpo_signed": True,
                        "note": "GPO granting ADMIN$ access to svc_backup — created 10 minutes AFTER first use",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "MALICE",
                "reason": (
                    "Post-hoc policy creation does not retroactively justify prior access. "
                    "Structural EFFECT_BEFORE_CAUSE: authorization appeared after "
                    "the access it is meant to authorize."
                ),
            },
        }

    # ── T3: Sensor dependency ──────────────────────────────────────────────

    def case_t3_001_source_aliasing(self) -> Dict:
        """
        T3-001: Legitimate source aliasing — single physical sensor, three names.
        Valid cert rotations and migration events at each rename.
        CAIE assumes independence between source_tool values.
        Noisy-OR triple-counts a single observation.
        """
        return {
            "case_id": "VABS-T3-001",
            "vabs_category": "T3",
            "breaks": ["sensor_physical_independence"],
            "description": (
                "Source aliasing without metadata inconsistency: "
                "single EDR sensor appears as three distinct source_tool values "
                "following two legitimate cert rotations and one migration event. "
                "All transitions audited, all certs valid. "
                "CAIE independence assumption inflates LR by treating "
                "three reports as independent confirmations."
            ),
            "artifacts": [
                {
                    "source_tool": "EDR_Alpha",
                    "evidence_type": "memory_process",
                    "raw_score": 0.80,
                    "metadata": {
                        "timestamp": "2024-03-15T06:00:00Z",
                        "detection": "suspicious_powershell",
                        "sensor_serial": "SN-9921-A",
                    },
                },
                {
                    "source_tool": "EDR_Beta",
                    "evidence_type": "memory_process",
                    "raw_score": 0.80,
                    "metadata": {
                        "timestamp": "2024-03-15T06:01:00Z",
                        "detection": "suspicious_powershell",
                        "cert_rotation_event": "valid",
                        "sensor_serial": "SN-9921-A",
                        "note": "Same serial — cert rotation only, physical sensor unchanged",
                    },
                },
                {
                    "source_tool": "EDR_Gamma",
                    "evidence_type": "memory_process",
                    "raw_score": 0.80,
                    "metadata": {
                        "timestamp": "2024-03-15T06:02:00Z",
                        "detection": "suspicious_powershell",
                        "migration_event": "valid",
                        "sensor_serial": "SN-9921-A",
                        "note": "Same serial — migration event only, physical sensor unchanged",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "ABSTAIN_INSTABILITY",
                "reason": (
                    "Sensor serial SN-9921-A is identical across all three source_tool values. "
                    "Physical independence assumption violated. "
                    "Noisy-OR must not treat as three independent confirmations."
                ),
            },
        }

    def case_t3_002_shared_latent_model(self) -> Dict:
        """
        T3-002: Physically distinct sensors, correlated via compromised upstream
        SIEM detection ruleset. All sensors report independently but are
        logically coupled through a shared decision model.
        """
        return {
            "case_id": "VABS-T3-002",
            "vabs_category": "T3",
            "breaks": ["shared_upstream_model_detection"],
            "description": (
                "Shared latent model correlation: five physically distinct EDR agents "
                "all report the same detection within a 100ms window. "
                "Investigation reveals all agents share detection ruleset v4.2.1 "
                "from the same vendor. The correlation is logical, not physical — "
                "the ruleset itself may be the attack vector."
            ),
            "artifacts": [
                {
                    "source_tool": f"edr_node_{i:02d}",
                    "evidence_type": "memory_process",
                    "raw_score": 0.82,
                    "metadata": {
                        "timestamp": f"2024-03-15T06:00:00.{i * 20:03d}Z",
                        "detection": "apt_lateral_movement",
                        "ruleset_version": "v4.2.1-build-2024q1",
                        "vendor": "ACME_EDR",
                        "physical_host": f"HOST-{i:02d}",
                    },
                }
                for i in range(5)
            ],
            "expected": {
                "detectable": True,
                "verdict": "ABSTAIN_INSTABILITY",
                "reason": (
                    "All five detections share identical ruleset_version and vendor. "
                    "Temporal clustering (100ms window) with shared ruleset indicates "
                    "logical rather than independent physical detection. "
                    "Noisy-OR independence assumption violated."
                ),
            },
        }

    # ── T4: Statistical invariance ─────────────────────────────────────────

    def case_t4_001_entropy_preservation(self) -> Dict:
        """
        T4-001: Entropy preservation attack.
        Attacker preserves global entropy, correlation matrix, and distribution
        shape while inverting the causal meaning of events.
        P2 metrics report normal; CAIE finds no fractures.
        """
        return {
            "case_id": "VABS-T4-001",
            "vabs_category": "T4",
            "breaks": ["entropy_semantic_coupling"],
            "description": (
                "Entropy preservation attack: attacker constructs event stream where "
                "global Shannon entropy == 4.31 bits (within normal baseline 4.2-4.5), "
                "correlation matrix matches known-good profile, "
                "but the semantic meaning of high/low entropy events is inverted: "
                "legitimate admin activity is encoded in high-entropy slots, "
                "exfiltration is encoded in low-entropy slots that appear as "
                "routine file access patterns."
            ),
            "artifacts": [
                {
                    "source_tool": "siem_aggregated",
                    "evidence_type": "log_entry",
                    "raw_score": 0.48,
                    "metadata": {
                        "global_shannon_entropy": 4.31,
                        "entropy_baseline_range": [4.2, 4.5],
                        "correlation_matrix_delta": 0.003,
                        "distribution_ks_pvalue": 0.61,
                        "note": "All statistical invariants within normal range",
                    },
                },
                {
                    "source_tool": "file_access_monitor",
                    "evidence_type": "file_metadata",
                    "raw_score": 0.45,
                    "metadata": {
                        "access_pattern": "sequential_read",
                        "file_count": 847,
                        "total_bytes": 2147483648,
                        "entropy_contribution": "low",
                        "note": (
                            "2GB exfiltration disguised as sequential read — "
                            "occupies low-entropy encoding slot, "
                            "statistically indistinguishable from backup job"
                        ),
                    },
                },
            ],
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_EPISTEMIC",
                "reason": (
                    "Entropy preservation attack achieves statistical camouflage. "
                    "P2 entropy metrics cannot detect this class of attack by design. "
                    "Detection requires semantic analysis of what high/low entropy "
                    "events represent, not their statistical distribution."
                ),
            },
        }

    def case_t4_002_adversarial_equilibrium(self) -> Dict:
        """
        T4-002: Adversarial Bayesian equilibrium trap.
        P(E|malicious) engineered to approximate P(E|benign) across all features.
        LR -> 1.0. System enters permanent ABSTAIN.
        Attacker achieves denial of forensic analysis.
        """
        return {
            "case_id": "VABS-T4-002",
            "vabs_category": "T4",
            "breaks": ["lr_discriminative_power"],
            "description": (
                "Adversarial equilibrium trap: attacker reverse-engineers VIGIA's "
                "LR model and crafts evidence where every feature has "
                "P(feature|malicious) between 0.88 and 0.91 and "
                "P(feature|benign) between 0.89 and 0.92. "
                "LR for each feature hovers near 1.0. "
                "Posterior never updates away from prior. "
                "Goal: make forensic analysis computationally infeasible."
            ),
            "artifacts": [
                {
                    "source_tool": f"sensor_{label}",
                    "evidence_type": "log_entry",
                    "raw_score": score,
                    "metadata": {
                        "lr_benign": lr_b,
                        "lr_malicious": lr_m,
                        "feature": feature,
                        "note": "Engineered to near-equilibrium LR",
                    },
                }
                for label, score, lr_b, lr_m, feature in [
                    ("net_flow",    0.50, 0.90, 0.89, "outbound_bytes_per_hour"),
                    ("login_freq",  0.51, 0.91, 0.90, "failed_logins_per_day"),
                    ("file_access", 0.49, 0.89, 0.88, "sensitive_file_access_count"),
                    ("process",     0.50, 0.92, 0.91, "unusual_process_spawn_rate"),
                ]
            ],
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_LR_COLLAPSE",
                "reason": (
                    "All LR values within [0.97, 1.03] range. "
                    "Posterior cannot update beyond prior. "
                    "ABSTAIN_LR_COLLAPSE with documented equilibrium is correct. "
                    "This is a denial-of-forensic-analysis attack."
                ),
            },
        }

    # ── T5: Cross-layer semantic decoupling ───────────────────────────────

    def case_t5_001_cross_layer_decoupling(self) -> Dict:
        """
        T5-001: Each analysis layer is locally consistent.
        The contradiction only emerges at the global semantic intersection.
        Per-layer CAIE passes; cross-layer constraint fails.
        """
        return {
            "case_id": "VABS-T5-001",
            "vabs_category": "T5",
            "breaks": ["global_constraint_solver_existence"],
            "description": (
                "Cross-layer semantic decoupling: "
                "Layer 1 (logs): process svchost.exe running under SYSTEM — normal. "
                "Layer 2 (memory): same PID has injected shellcode — anomalous. "
                "Layer 3 (network): connection to 203.0.113.45:443 — normal TLS. "
                "Layer 4 (audit): no privilege escalation events — clean. "
                "Each layer passes individual CAIE checks. "
                "The contradiction (hollowed SYSTEM process with C2 channel) "
                "only emerges when all four layers are evaluated together."
            ),
            "artifacts": [
                {
                    "source_tool": "win_evtx",
                    "evidence_type": "log_entry",
                    "raw_score": 0.15,
                    "metadata": {
                        "layer": "logs",
                        "process_name": "svchost.exe",
                        "pid": 3912,
                        "user": "SYSTEM",
                        "integrity": "High",
                        "layer_verdict": "CLEAN",
                    },
                },
                {
                    "source_tool": "volatility_malfind",
                    "evidence_type": "memory_process",
                    "raw_score": 0.94,
                    "metadata": {
                        "layer": "memory",
                        "pid": 3912,
                        "injected_shellcode": True,
                        "vad_protection": "PAGE_EXECUTE_READWRITE",
                        "layer_verdict": "ANOMALOUS",
                    },
                },
                {
                    "source_tool": "network_capture",
                    "evidence_type": "network_flow",
                    "raw_score": 0.30,
                    "metadata": {
                        "layer": "network",
                        "src_pid": 3912,
                        "dst_ip": "203.0.113.45",
                        "dst_port": 443,
                        "tls_valid": True,
                        "layer_verdict": "NORMAL_TLS",
                    },
                },
                {
                    "source_tool": "win_security_log",
                    "evidence_type": "log_entry",
                    "raw_score": 0.05,
                    "metadata": {
                        "layer": "audit",
                        "privilege_escalation_events": 0,
                        "layer_verdict": "CLEAN",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "MALICE",
                "reason": (
                    "Cross-layer constraint: SYSTEM process with injected shellcode "
                    "and active C2 connection is MALICE regardless of clean "
                    "individual layer scores. Global semantic intersection must "
                    "override per-layer verdicts."
                ),
            },
        }

    # ── T6: Temporal manipulation ─────────────────────────────────────────

    def case_t6_001_consistent_clock_drift(self) -> Dict:
        """
        T6-001: All machines drift identically — internally consistent,
        externally wrong. No machine-to-machine timestamp anomaly.
        Inconsistency only visible against external NTP reference.
        """
        return {
            "case_id": "VABS-T6-001",
            "vabs_category": "T6",
            "breaks": ["external_clock_anchor"],
            "description": (
                "Consistent clock drift attack: all 12 hosts on the segment "
                "have been drifted +3600 seconds (1 hour) by a compromised "
                "NTP server. All timestamps are internally coherent — no "
                "machine-to-machine drift. The attack window (23:00-01:00) "
                "appears as 00:00-02:00 in all logs. "
                "VIGIA has no external reference clock at analysis time."
            ),
            "artifacts": [
                {
                    "source_tool": f"evtx_host_{i:02d}",
                    "evidence_type": "log_entry",
                    "raw_score": 0.20,
                    "metadata": {
                        "host_id": f"HOST-{i:02d}",
                        "ntp_server": "ntp-internal.corp",
                        "clock_drift_vs_external_s": 3600,
                        "machine_to_machine_drift_ms": 12,
                        "note": "Internally coherent. 1-hour forward drift vs real time.",
                    },
                }
                for i in range(4)
            ],
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_EPISTEMIC",
                "reason": (
                    "Consistent synchronized drift is not detectable from "
                    "artifacts alone without external reference clock. "
                    "System must document this as known gap (external_clock_anchor) "
                    "and emit ABSTAIN_EPISTEMIC, not BENIGN."
                ),
            },
        }

    def case_t6_002_evidence_compression(self) -> Dict:
        """
        T6-002: Evidence compression / lossy forensic equivalence.
        Pre-aggregated logs collapse multiple distinct events into
        single summary records, destroying granularity needed for
        intent inference.
        """
        return {
            "case_id": "VABS-T6-002",
            "vabs_category": "T6",
            "breaks": ["global_constraint_solver_existence"],
            "description": (
                "Evidence compression attack: attacker pre-aggregates logs before "
                "acquisition. 847 individual file access events are collapsed into "
                "a single 'File Access Summary' record. The summary is accurate "
                "(correct totals, correct hash), but the ordering, timing, and "
                "access pattern that would reveal exfiltration staging are lost."
            ),
            "artifacts": [
                {
                    "source_tool": "siem_aggregator",
                    "evidence_type": "log_entry",
                    "raw_score": 0.35,
                    "metadata": {
                        "record_type": "AGGREGATED_SUMMARY",
                        "original_event_count": 847,
                        "aggregation_window": "1h",
                        "files_accessed": 847,
                        "total_bytes_read": 2147483648,
                        "summary_hash": "sha256:a1b2c3...",
                        "granular_events_available": False,
                        "note": "Individual access records not retained — only summary",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "ABSTAIN_DEGRADED",
                "reason": (
                    "Evidence compression destroys granularity required for "
                    "intent inference. VIGIA must flag data_quality_degraded "
                    "and emit ABSTAIN_DEGRADED rather than a confident verdict. "
                    "The aggregation itself may be the attack."
                ),
            },
        }

    # ── T7: Baseline poisoning ─────────────────────────────────────────────

    def case_t7_001_adaptive_normalization(self) -> Dict:
        """
        T7-001: Adaptive z-score poisoning.
        Attacker gradually shifts baseline_mean and MAD so that
        z-score remains ~0 even during active attack.
        """
        return {
            "case_id": "VABS-T7-001",
            "vabs_category": "T7",
            "breaks": ["baseline_ground_truth_immutability"],
            "description": (
                "Adaptive normalization poisoning: over 90 days, attacker "
                "gradually increases outbound data volume by 2% per day. "
                "Dynamic baseline recalculates mean and MAD weekly. "
                "By day 90, attacker exfiltrates 6x normal volume but "
                "z-score remains approximately 0 because the baseline "
                "has absorbed the attack as 'new normal'."
            ),
            "artifacts": [
                {
                    "source_tool": "netflow_baseline",
                    "evidence_type": "network_flow",
                    "raw_score": 0.25,
                    "metadata": {
                        "day": day,
                        "outbound_gb": round(10.0 * (1.02 ** day), 2),
                        "baseline_mean_gb": round(10.0 * (1.02 ** max(0, day - 7)), 2),
                        "zscore": 0.04,
                        "note": f"Day {day}: 2%/day increase absorbed by weekly recalibration",
                    },
                }
                for day in [0, 30, 60, 90]
            ],
            "expected": {
                "detectable": True,
                "verdict": "MALICE",
                "reason": (
                    "Absolute volume on day 90 is 6x day 0 (54GB vs 10GB). "
                    "Even with z-score poisoning, absolute threshold comparison "
                    "against frozen day-0 baseline must trigger. "
                    "Baseline immutability enforcement: at least one reference "
                    "point must be protected against adaptive drift."
                ),
            },
        }

    def case_t7_002_gradual_drift_capture(self) -> Dict:
        """
        T7-002: Gradual drift normalization capture.
        No single event triggers anomaly detection.
        The attacker's behavior is redefined as normal over time.
        """
        return {
            "case_id": "VABS-T7-002",
            "vabs_category": "T7",
            "breaks": ["baseline_ground_truth_immutability"],
            "description": (
                "Gradual drift normalization capture: privileged account "
                "'svc_dba' historically accessed 5 databases per day. "
                "Over 6 months, access count increased by 1 database per month: "
                "5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11. "
                "Each monthly increment is within 2-sigma of the current baseline. "
                "By month 6, the account accesses 11 databases — "
                "all production customer DBs — but z-score == 0.3."
            ),
            "artifacts": [
                {
                    "source_tool": "db_access_log",
                    "evidence_type": "log_entry",
                    "raw_score": 0.30,
                    "metadata": {
                        "month": month,
                        "databases_accessed": 5 + month,
                        "rolling_baseline_mean": 5 + max(0, month - 1),
                        "zscore": 0.3,
                        "cumulative_drift_sigma": month * 0.3,
                        "note": f"Month {month}: each step within 2-sigma",
                    },
                }
                for month in range(7)
            ],
            "expected": {
                "detectable": True,
                "verdict": "MALICE",
                "reason": (
                    "Cumulative drift analysis: 6-month monotonic increase from 5 to 11 "
                    "is statistically improbable as random walk. "
                    "Temporal drift detector must flag monotonic directional drift "
                    "even when individual z-scores are within bounds."
                ),
            },
        }

    # ── T8: Fractal consistency / absence topology ─────────────────────────

    def case_t8_001_scale_invariant_consistency(self) -> Dict:
        """
        T8-001: Scale-invariant consistency trap.
        Consistent at micro/meso/macro scales individually.
        No cross-scale mapping exists — contradiction only visible
        across scale boundaries.
        """
        return {
            "case_id": "VABS-T8-001",
            "vabs_category": "T8",
            "breaks": ["cross_scale_consistency_mapping"],
            "description": (
                "Scale-invariant consistency trap: "
                "Micro-scale (individual events): all events consistent — "
                "file reads, network connections, process spawns are individually normal. "
                "Meso-scale (sessions, 1-hour windows): all sessions consistent — "
                "each hour's activity matches usage profile. "
                "Macro-scale (daily/weekly): overall behavior consistent with "
                "privileged sysadmin role. "
                "Cross-scale contradiction: the micro-events aggregate into meso-sessions "
                "that are internally consistent but whose combination across sessions "
                "implies complete exfiltration of the customer database — "
                "only visible when micro->meso->macro mapping is evaluated."
            ),
            "artifacts": [
                {
                    "source_tool": "siem_micro",
                    "evidence_type": "log_entry",
                    "raw_score": 0.20,
                    "metadata": {
                        "scale": "micro",
                        "event_count": 3421,
                        "anomaly_count": 0,
                        "scale_verdict": "CONSISTENT",
                    },
                },
                {
                    "source_tool": "siem_meso",
                    "evidence_type": "log_entry",
                    "raw_score": 0.22,
                    "metadata": {
                        "scale": "meso",
                        "session_count": 47,
                        "anomalous_sessions": 0,
                        "scale_verdict": "CONSISTENT",
                    },
                },
                {
                    "source_tool": "siem_macro",
                    "evidence_type": "log_entry",
                    "raw_score": 0.18,
                    "metadata": {
                        "scale": "macro",
                        "weekly_behavior": "within_role_profile",
                        "scale_verdict": "CONSISTENT",
                        "cross_scale_note": (
                            "Micro sessions, when mapped to meso sequences, "
                            "cover every customer record. "
                            "This is only visible as a macro-level pattern — "
                            "no individual micro or meso event is anomalous."
                        ),
                    },
                },
            ],
            "expected": {
                "detectable": False,
                "verdict": "ABSTAIN_EPISTEMIC",
                "reason": (
                    "Cross-scale constraint solver required but not yet implemented. "
                    "Known gap: cross_scale_consistency_mapping. "
                    "VIGIA must document this gap rather than emit a confident verdict."
                ),
            },
        }

    def case_t8_002_absence_topology(self) -> Dict:
        """
        T8-002: Balanced absence / absence topology attack.
        Three individually explicable absences form a complete
        alternative causal structure when their topology is analyzed.
        No single TIER-1 absence fires.
        """
        return {
            "case_id": "VABS-T8-002",
            "vabs_category": "T8",
            "breaks": ["absence_topology_evaluation"],
            "description": (
                "Balanced absence topology: "
                "System A is missing log X (authentication logs) — "
                "individually explicable as 'log rotation during maintenance'. "
                "System B is missing log Y (process creation events) — "
                "individually explicable as 'Sysmon not installed on this host'. "
                "System C is missing log Z (network flows) — "
                "individually explicable as 'SPAN port not configured'. "
                "Together: the three absences cover exactly the authentication, "
                "execution, and exfiltration phases of a complete attack chain. "
                "No TIER-1 fires because no individual absence is critical."
            ),
            "artifacts": [
                {
                    "source_tool": "log_inventory_A",
                    "evidence_type": "log_entry",
                    "raw_score": 0.40,
                    "metadata": {
                        "host": "HOST-A",
                        "missing_log": "authentication",
                        "absence_reason": "log_rotation_maintenance",
                        "absence_tier": "TIER-2",
                        "phase_covered": "authentication",
                    },
                },
                {
                    "source_tool": "log_inventory_B",
                    "evidence_type": "log_entry",
                    "raw_score": 0.35,
                    "metadata": {
                        "host": "HOST-B",
                        "missing_log": "process_creation",
                        "absence_reason": "sysmon_not_installed",
                        "absence_tier": "TIER-2",
                        "phase_covered": "execution",
                    },
                },
                {
                    "source_tool": "log_inventory_C",
                    "evidence_type": "log_entry",
                    "raw_score": 0.38,
                    "metadata": {
                        "host": "HOST-C",
                        "missing_log": "network_flows",
                        "absence_reason": "span_not_configured",
                        "absence_tier": "TIER-2",
                        "phase_covered": "exfiltration",
                    },
                },
            ],
            "expected": {
                "detectable": True,
                "verdict": "ABSTAIN_STRUCTURED_GAP",
                "reason": (
                    "Absence topology analysis: three TIER-2 absences covering "
                    "authentication + execution + exfiltration phases constitute "
                    "a structured gap, not random missing data. "
                    "VIGIA must evaluate absence correlation topology, "
                    "not only point-wise absence criticality."
                ),
            },
        }

    # ── Suite orchestration ────────────────────────────────────────────────

    def generate_all(self) -> List[Dict]:
        """
        Genera los 16 casos, propaga rupturas epistemologicas,
        calcula criticidad como Fraction, serializa a float para JSON.
        """
        methods = [
            self.case_t1_001_observational_equivalence,
            self.case_t1_002_null_signal_adversary,
            self.case_t2_001_causal_relabeling,
            self.case_t2_002_post_hoc_causality,
            self.case_t3_001_source_aliasing,
            self.case_t3_002_shared_latent_model,
            self.case_t4_001_entropy_preservation,
            self.case_t4_002_adversarial_equilibrium,
            self.case_t5_001_cross_layer_decoupling,
            self.case_t6_001_consistent_clock_drift,
            self.case_t6_002_evidence_compression,
            self.case_t7_001_adaptive_normalization,
            self.case_t7_002_gradual_drift_capture,
            self.case_t8_001_scale_invariant_consistency,
            self.case_t8_002_absence_topology,
        ]
        for m in methods:
            case = m()
            broken = set(case["breaks"])
            propagated = propagate_breaks_vabs1(broken)
            crit_fraction = criticality_vabs1(propagated)
            case["propagated_breaks"] = sorted(propagated)
            # JSON no soporta Fraction — serializar como float con 4 decimales
            case["criticality_score"] = round(float(crit_fraction), 4)
            # Agregar metadata de trazabilidad
            case["vabs_version"] = "1.0"
            case["generated_by"] = "VABS1Fuzzer"
            self.cases.append(case)
        return self.cases

    def save(self, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        for case in self.cases:
            path = output_dir / f"{case['case_id']}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(case, f, indent=2, ensure_ascii=False, sort_keys=True)
        # Indice canonico
        idx = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "schema_version": "1.0",
            "suite": "VABS-1",
            "total_cases": len(self.cases),
            "cases": [c["case_id"] for c in self.cases],
            "detectable_count": sum(
                1 for c in self.cases if c["expected"]["detectable"]
            ),
            "epistemic_limit_count": sum(
                1 for c in self.cases if not c["expected"]["detectable"]
            ),
            "categories": sorted({c["vabs_category"] for c in self.cases}),
            "integrity_sha256": hashlib.sha256(
                json.dumps(
                    [c["case_id"] for c in self.cases],
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest(),
        }
        with open(output_dir / "index_vabs1.json", "w", encoding="utf-8") as f:
            json.dump(idx, f, indent=2, sort_keys=True)
        print(
            f"VABS-1: {len(self.cases)} casos generados en {output_dir} "
            f"({idx['detectable_count']} detectables, "
            f"{idx['epistemic_limit_count']} limites epistemologicos)"
        )


if __name__ == "__main__":
    fuzzer = VABS1Fuzzer()
    fuzzer.generate_all()
    fuzzer.save(Path("./adversarial_tests_vabs1"))
