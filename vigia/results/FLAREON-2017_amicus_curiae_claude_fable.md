# AMICUS CURIAE — FLARE-On 4 (2017) malware set

**In the matter of case VIGIA-FLAREON-4 (FLARE-On 4 / 2017 CTF malware collection)**
**Submitted by:** VIGIA Autonomous Forensic Intent Engine (Claude Code / Claude Fable, Mode 2)
**Corpus entry:** `data/cases/VIGIA-FLAREON-4.json` (14 artifacts; schema validates)
**Evidence:** `evidence/flare-on/flareon4/` — 12 challenge samples; distribution zip SHA-256 `760f1130aa0166a25a50c334d5ecc1537a71e3761360fa17b83ab63a402748b7`
**Sealed bundle:** `FLAREON-2017_bundle_claude_fable.json`, decision hash `3e08cb52d46a9412cbdd...` (EBS verify PASS, Level 2)

---

## I. Purpose

This brief addresses a case where the raw signals point one way and the context
points another, and states plainly why the correct verdict is the more restrained
one. It is offered as a neutral aid, with the fact/inference boundary explicit.

## II. Facts established on the samples

1. Twelve reverse-engineering challenge samples across seven formats (PE, ELF, APK,
   PHP, HTML/JS, Arduino hex, pcap).
2. Deliberate obfuscation is present and authentic: a packed ELF (`pewpewboat`,
   entropy 7.60), an anomalously low-entropy PE (`covfefe`, 1.92, padding
   obfuscation), and JS char-code obfuscation (`login.html`).
3. `payload.dll` calls `IsDebuggerPresent` and resolves APIs dynamically
   (`GetProcAddress`/`LoadLibraryExW`) — explicit anti-analysis.
4. `shell.php` is a `base64_decode` webshell.
5. The `12` capture shows a staged download: `GET /secondstage` over HTTP with a
   spoofed Internet Explorer User-Agent, served by a Python `SimpleHTTP` server.
6. The samples are organised as a labelled `01..12` challenge tree, and the
   distribution zip hash matches the publicly released FireEye FLARE-On 4 (2017).

## III. The tension, stated honestly

The deterministic engine scores the set REJECT / posterior 0.9999 (LR ~23,904), and
the CAIE structural layer returns **MALICE** (composite 0.5277): the offensive
tradecraft genuinely crosses threshold. A verifier who stopped there would report
MALICE.

## IV. Why the emitted verdict is INTENT, not MALICE

Intent analysis must distinguish two things a single artifact can carry:

1. **Artifact-level intent** — was this code *deliberately* built to obfuscate and
   evade? **Yes, confirmed.** The packing, anti-debug calls, webshell and staged C2
   are not accidents; they are authored tradecraft.
2. **Operational malice** — is there deliberate intent to harm a *party*? **Not
   established, and affirmatively refuted by context.** These are publicly-announced
   educational challenges: no target, no victim host, no deployment, no exfiltrated
   data; the distribution hash matches the sanctioned FLARE-On release. The benign
   operational explanation is not just plausible — it is corroborated.

The `detect_eco_overinterpretation` control returned NORMAL_DISTRIBUTION: the
artifacts are authentic offensive samples, not fabricated or false-flag — consistent
with genuine-but-educational tradecraft. The CAIE MALICE signal is preserved as the
honest structural reading; the analyst tempers the emitted verdict to **INTENT**
because the operational-malice refutation succeeds. Downgrading here is the system
working correctly, not a weakness.

## V. What would change the verdict

Were these same artifacts recovered deployed on a live victim host — with a target,
a C2 endpoint under an attacker's control, and exfiltrated data — the operational
refutation would fail and the verdict would move to MALICE. The entire difference is
context, and here the context is a labelled, published CTF.

## VI. Chain of custody and reproducibility

Representative samples were hashed (e.g. `shell.php` SHA-256
`278bb0066af4204fb23e0e662d2a1ab214529231023814ed13350b70c38e9c2a`); the corpus case
validates (14 artifacts). The sealed decision reproduces bit-for-bit (`decision_hash`
identical across three runs) and passes `verify_ebs_v1.py` at **Level 2**. No
floating-point value governs the sealed decision and no language model influenced it.

## VII. Recommendation

Record the set as **INTENT** — deliberately-authored offensive/evasive code — with an
explicit finding that **real-world MALICE is not asserted** because the artifacts are
sanctioned educational CTF material with no victim or deployment. The case is a clean
illustration of VIGIA's core discipline: separating what an artifact *is* (malicious
by construction) from what an actor *did* (nothing operational, here).

*Respectfully submitted. The tradecraft is real; the victim is not — hence INTENT,
by deliberate restraint.*
