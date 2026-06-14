PROMPTS REAL CASES


**MODO AGENT**

mkdir -p ~/vigia-repo/results/real
cd ~/vigia-repo

for CASE in VIGIA-REAL-001 VIGIA-REAL-002 VIGIA-REAL-003 VIGIA-REAL-004 VIGIA-REAL-005 VIGIA-REAL-006 VIGIA-REAL-007 VIGIA-REAL-008 VIGIA-REAL-009 VIGIA-REAL-010 VIGIA-REAL-NROMANOFF VIGIA-REAL-TDUNGAN VIGIA-REAL-NFURY VIGIA-REAL-ROCBA VIGIA-REAL-SRL-ADMIN VIGIA-REAL-SRL-AV VIGIA-REAL-SRL-DC-MEMORY VIGIA-REAL-SRL-DMZ-FTP; do
  echo "=== $CASE ==="
  python3 vigia_agent.py \
    --evidence data/cases/converted/${CASE}.json \
    --case-id $CASE \
    --output results/real/${CASE}_bundle.json
  python3 verify_ebs_v1.py results/real/${CASE}_bundle.json --verbose
done


---

**Setup previo — una sola vez antes del primero:**

```bash
mkdir -p ~/vigia-repo/results/real
cd ~/vigia-repo
claude
```

---

**VIGIA-REAL-001 — NIST CFReDS Mr. Evil (Greg Schardt) | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-001.

Evidence: data/cases/converted/VIGIA-REAL-001.json
Case source: NIST CFReDS - Hacking Case (Greg Schardt / Mr. Evil)
Expected verdict: MALICE

Protocol:
1. Hash the evidence file with generate_forensic_hash before any analysis.
2. Run all three Peircean layers: Firstness (observation), Secondness (structural anomalies), Thirdness (deliberate pattern).
3. Apply the mandatory self-correction protocol: for every INTENT or MALICE finding, document the strongest benign alternative explanation and explain why it is insufficient.
4. Generate a sealed ForensicBundle to results/real/VIGIA-REAL-001_bundle.json
5. Generate the Amicus Curiae judicial narrative to results/real/VIGIA-REAL-001_amicus_curiae.md
6. Verify the sealed bundle with verify_ebs_v1.py and report the 4-hash output (H1 graph_hash, H2 bundle_hash, H3 HMAC chain, H4 EBS verify).

Follow CLAUDE.md invariants. LLM is outside the mathematical decision loop.
```

---

**VIGIA-REAL-002 — NIST CFReDS Data Leakage | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-002.

Evidence: data/cases/converted/VIGIA-REAL-002.json
Case source: NIST CFReDS - Data Leakage Case
Expected verdict: MALICE

Protocol:
1. Hash the evidence file with generate_forensic_hash before any analysis.
2. Run all three Peircean layers: Firstness, Secondness, Thirdness.
3. Apply mandatory self-correction: document strongest benign alternative for every INTENT/MALICE finding.
4. Generate sealed ForensicBundle to results/real/VIGIA-REAL-002_bundle.json
5. Generate Amicus Curiae narrative to results/real/VIGIA-REAL-002_amicus_curiae.md
6. Verify bundle with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-003 — Ali Hadi Web Server Compromise | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-003.

Evidence: data/cases/converted/VIGIA-REAL-003.json
Case source: Ali Hadi Challenge #1 - Web Server Case
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Run full Peircean analysis (Firstness / Secondness / Thirdness).
3. Mandatory self-correction for every INTENT/MALICE finding.
4. Sealed bundle → results/real/VIGIA-REAL-003_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-003_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-004 — Ali Hadi SysInternals Malware | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-004.

Evidence: data/cases/converted/VIGIA-REAL-004.json
Case source: Ali Hadi Challenge #7 - SysInternals Case
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Run full Peircean analysis — pay special attention to legitimate tools exhibiting anomalous behavior (living-off-the-land pattern).
3. Mandatory self-correction for every INTENT/MALICE finding.
4. Sealed bundle → results/real/VIGIA-REAL-004_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-004_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-005 — Ali Hadi Encrypt Them All | Esperado: SUSPICION**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-005.

Evidence: data/cases/converted/VIGIA-REAL-005.json
Case source: Ali Hadi Challenge #9 - Encrypt Them All Case
Expected verdict: SUSPICION (not MALICE — evidence supports elevated concern but does not meet MALICE threshold)

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Run full Peircean analysis. Note: SUSPICION is the epistemically correct verdict if evidence is insufficient to confirm malicious intent — do not force MALICE.
3. Mandatory self-correction: document why MALICE cannot be confirmed.
4. Sealed bundle → results/real/VIGIA-REAL-005_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-005_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-006 — Digital Corpora M57-Jean | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-006.

Evidence: data/cases/converted/VIGIA-REAL-006.json
Case source: Digital Corpora - M57-Jean Scenario
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Full Peircean analysis (Firstness / Secondness / Thirdness).
3. Mandatory self-correction for INTENT/MALICE findings.
4. Sealed bundle → results/real/VIGIA-REAL-006_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-006_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-007 — Digital Corpora Nitroba University | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-007.

Evidence: data/cases/converted/VIGIA-REAL-007.json
Case source: Digital Corpora - Nitroba University Harassment Scenario
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Full Peircean analysis.
3. Mandatory self-correction for INTENT/MALICE findings.
4. Sealed bundle → results/real/VIGIA-REAL-007_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-007_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-008 — Volatility Cridex Banking Trojan | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-008.

Evidence: data/cases/converted/VIGIA-REAL-008.json
Case source: Volatility Foundation - Cridex Memory Sample
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Full Peircean analysis — this is a memory forensics case. Apply detect_memory_habit_incongruence where applicable.
3. Mandatory self-correction for INTENT/MALICE findings.
4. Sealed bundle → results/real/VIGIA-REAL-008_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-008_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-009 — DFRWS 2008 Linux Exfiltration | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-009.

Evidence: data/cases/converted/VIGIA-REAL-009.json
Case source: DFRWS 2008 Forensic Challenge - Linux Memory
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Full Peircean analysis.
3. Mandatory self-correction for INTENT/MALICE findings.
4. Sealed bundle → results/real/VIGIA-REAL-009_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-009_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---

**VIGIA-REAL-010 — DFRWS 2011 Android Espionage | Esperado: MALICE**

```
Conduct a full VIGÍA forensic investigation on case VIGIA-REAL-010.

Evidence: data/cases/converted/VIGIA-REAL-010.json
Case source: DFRWS 2011 Forensic Challenge - Android
Expected verdict: MALICE

Protocol:
1. Hash evidence with generate_forensic_hash.
2. Full Peircean analysis — mobile/Android artifact set. Apply appropriate behavioral fingerprinting.
3. Mandatory self-correction for INTENT/MALICE findings.
4. Sealed bundle → results/real/VIGIA-REAL-010_bundle.json
5. Amicus Curiae → results/real/VIGIA-REAL-010_amicus_curiae.md
6. Verify with verify_ebs_v1.py — report 4-hash output.

Follow CLAUDE.md invariants.
```

---


