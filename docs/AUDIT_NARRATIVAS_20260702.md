# AUDIT_NARRATIVAS_20260702
## VIGÍA — Auditoría de Consistencia Narrativa vs. Bundles

```
Auditor        : Claude Code / VIGÍA (read-only, sin modificaciones)
Fecha          : 2026-07-02
Git tag        : pre-audit-narrativas-20260702
Alcance        : results/, vigia_output/, cases/, evidence/, reports/
Metodología    : Indexación de bundles → indexación de narrativas →
                 cruce por case_id → clasificación A/B/C/D
Acción tomada  : NINGUNA. Solo observación y documentación.
```

---

## ÍNDICE DE BUNDLES JSON (PASO 1)

### 1.1 Bundles en `results/srl2018/` — estructura pipeline_results

Todos los bundles en srl2018/ tienen formato EBS v1 (campo `pipeline_results.abduction.best_hypothesis`)
excepto VIGIA-REAL-\* que usan formato EBS modal (campo `overall_verdict`) o formato
EBS v2 (campo `decision_trace.decision`).

| case_id | best_hypothesis | is_conclusive | .sha256 |
|---------|-----------------|---------------|---------|
| ADMIN-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| AV-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| AV-003 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| DC-MEM-001 | **PIPELINE_ERROR** | False | ✓ |
| DC-MEM-003 | SUSPICION_DETECTED | False | ✓ |
| DC-MEM-004 | SUSPICION_DETECTED | False | ✓ |
| DC-MEM-005 | SUSPICION_DETECTED | False | ✓ |
| ELF-001 | **PIPELINE_ERROR** | False | ✓ |
| ELF-002 | SUSPICION_DETECTED | False | ✓ |
| ELF-003 | SUSPICION_DETECTED | False | ✓ |
| ELF-MEMORY-001 | SUSPICION_DETECTED | False | ✓ |
| FILE-001 | **PIPELINE_ERROR** | False | ✓ |
| FILE-002 | SUSPICION_DETECTED | False | ✓ |
| FILE-003 | SUSPICION_DETECTED | False | ✓ |
| FILE-MEMORY-001 | SUSPICION_DETECTED | False | ✓ |
| FILE-SNAPSHOT-001 | SUSPICION_DETECTED | False | ✓ |
| HUNT-001 | **PIPELINE_ERROR** | False | ✓ |
| HUNT-002 | SUSPICION_DETECTED | False | ✓ |
| HUNT-003 | SUSPICION_DETECTED | False | ✓ |
| HUNT-004 | SUSPICION_DETECTED | False | ✓ |
| HUNT-005 | SUSPICION_DETECTED | False | ✓ |
| M57-JO-2009-12-07 | **PIPELINE_ERROR** | False | ✓ |
| M57-PAT-2009-12-07 | **PIPELINE_ERROR** | False | ✓ |
| M57-PAT-2009-12-11 | **PIPELINE_ERROR** | False | ✓ |
| MAGNET-2020-CTF-WINDOWS | SUSPICION_DETECTED | False | ✓ |
| MAIL-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| MAIL-002 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| NARCOS-CCLEANER-MEMORY | SUSPICION_DETECTED | False | ✓ |
| NARCOS-JANE-Day2 | SUSPICION_DETECTED | False | ✓ |
| NARCOS-JANE-Day3 | SUSPICION_DETECTED | False | ✓ |
| NARCOS-JANE-Day4 | SUSPICION_DETECTED | False | ✓ |
| NARCOS-JOHN-ALT-DAY1 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| NARCOS-JOHN-ALT-DAY2 | MALICIOUS_INTENT_DETECTED | **False** | ✓ |
| NARCOS-JOHN-PRIMARY-Day1 | MALICIOUS_INTENT_DETECTED | **False** | ✓ |
| NARCOS-JOHN-PRIMARY-Day2 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| NARCOS-JOHN-PRIMARY-Day3 | MALICIOUS_INTENT_DETECTED | **False** | ✓ |
| NARCOS-JOHN-PRIMARY-Day4 | MALICIOUS_INTENT_DETECTED | **False** | ✓ |
| NARCOS-STEVE-Day1 | **FORMAT_NOT_SUPPORTED** | False | ✓ |
| NARCOS-STEVE-Day2 | **FORMAT_NOT_SUPPORTED** | False | ✓ |
| NARCOS-STEVE-Day4 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| RD01-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| RD02-001 | SUSPICION_DETECTED | False | ✓ |
| RD02-CDRIVE-001 | **PIPELINE_ERROR** | False | ✓ |
| RD02-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| RD03-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| RD04-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| RD05-001 | **PIPELINE_ERROR** | False | ✓ |
| RD05-002 | SUSPICION_DETECTED | False | ✓ |
| RD05-003 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| RD06-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| SP-001 | SUSPICION_DETECTED | False | ✓ |
| SP-MEMORY-001 | SUSPICION_DETECTED | False | ✓ |
| VANKO-FALLBACK-001 | **UNDETERMINED** | False | ✓ |
| VANKO-FALLBACK-002 | **UNDETERMINED** | False | ✓ |
| WKSTN01-001 | SUSPICION_DETECTED | False | ✓ |
| WKSTN01-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| WKSTN02-001 | SUSPICION_DETECTED | False | ✓ |
| WKSTN02-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| WKSTN03-001 | SUSPICION_DETECTED | False | ✓ |
| WKSTN03-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| WKSTN04-001 | MALICIOUS_INTENT_DETECTED | True | ✓ |
| WKSTN05-001 | SUSPICION_DETECTED | False | ✓ |
| WKSTN05-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |
| WKSTN06-001 | SUSPICION_DETECTED | False | ✓ |
| WKSTN06-MEMORY-001 | MALICIOUS_INTENT_DETECTED | False | ✓ |

**Bundles VIGIA-REAL-\* en srl2018/ — formato EBS modal (`overall_verdict`):**

| case_id | overall_verdict | overall_confidence | composite_trust | daubert | .sha256 |
|---------|-----------------|--------------------|-----------------|---------|---------|
| VIGIA-REAL-NFURY | SUSPICION | MEDIUM | 0.1381 | True | ✓ |
| VIGIA-REAL-NROMANOFF | MALICE | HIGH | 1.0 | True | ✗ |
| VIGIA-REAL-ROCBA | MALICE | HIGH | 0.2043 | True | ✓ |
| VIGIA-REAL-SRL-ADMIN | MALICE | HIGH | 0.2075 | True | ✓ |
| VIGIA-REAL-SRL-AV | MALICE | HIGH | 0.2025 | True | ✓ |
| VIGIA-REAL-TDUNGAN | MALICE | HIGH | 1.0 | True | ✗ |
| VIGIA-REAL-VANKO | MALICE | HIGH | 1.0 | True | ✓ |

**Bundle VIGIA-REAL-SRL-DMZ-FTP en srl2018/ — formato EBS v2:**

| case_id | decision_trace.decision | caie_analysis.verdict | caie_composite | amicus_verdict | .sha256 |
|---------|-------------------------|-----------------------|----------------|----------------|---------|
| VIGIA-REAL-SRL-DMZ-FTP | **ABSTAIN** | MALICE | 0.3346 | MALICE (67%) | ✓ |

Nota: decisión `ABSTAIN` en `decision_trace` pero `MALICE` en `caie_analysis`. El amicus cita 67% de confianza para el veredicto global — alineado con el score 0.3346. No clasificado como error: el ABSTAIN indica que el motor Bayesiano no alcanzó umbral de aceptación/rechazo, pero el CAIE + trust_fusion emiten MALICE. La narrativa detalla explícitamente esta tensión.

### 1.2 Bundles en `results/` (raíz)

| archivo | best_hypothesis | is_conclusive | .sha256 |
|---------|-----------------|---------------|---------|
| insomnio_tactico_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| can038_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| real007_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| **NPS-2010-EMAILS_bundle_claude.json** | **PIPELINE_ERROR** | False | ✓ |
| srl_dmz_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| VIGIA-REAL-007_bundle.json | MALICIOUS_INTENT_DETECTED | False | ✓ |
| can018_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| **NPS-2014-USB-NONDETERMINISTIC_bundle.json** | **PIPELINE_ERROR** | False | ✓ |
| VIGIA-REAL-009_bundle.json | MALICIOUS_INTENT_DETECTED | False | ✓ |
| VIGIA-REAL-007_20260610.json | MALICIOUS_INTENT_DETECTED | True | ✗ |
| can031_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| VIGIA-REAL-006_bundle.json | MALICIOUS_INTENT_DETECTED | False | ✓ |
| VIGIA-REAL-001_bundle.json | MALICIOUS_INTENT_DETECTED | True | ✓ |
| NPS-2009-DOMEXUSERS_bundle_claude.json | NO_SEMIOTIC_ANOMALY_DETECTED | False | ✓ |

### 1.3 Bundles en `vigia_output/`

| archivo | decision/verdict | inference_mode | integrity.bundle_hash | .sha256 |
|---------|------------------|----------------|----------------------|---------|
| bundle_VIGIA-REAL-NROMANOFF.json | ACCEPT / caie=NOISE | **FALLBACK** | a943337c... | ✗ |
| bundle_VIGIA-REAL-TDUNGAN.json | ACCEPT / caie=NOISE | **FALLBACK** | (no verificado) | ✗ |
| ROCBA_agent_run.json | **PIPELINE_ERROR** | — | — | ✓ |
| ROCBA_sift_fallback.json | **PIPELINE_ERROR** | — | — | ✓ |
| ROCBA_disk_real.json | **UNDETERMINED** | — | — | ✓ |

### 1.4 Bundles en `results/agent_batch/`

| archivo | best_hypothesis | is_conclusive |
|---------|-----------------|---------------|
| NPS-2010-EMAILS_agent_bundle.json | NO_SEMIOTIC_ANOMALY_DETECTED | False |
| NPS-2009-DOMEXUSERS_agent_bundle.json | NO_SEMIOTIC_ANOMALY_DETECTED | False |
| VIGIA-HMG-99999-11-RAW_bundle.json | **PIPELINE_ERROR** | False |
| VIGIA-HMG-99999-11_agent_bundle.json | MALICIOUS_INTENT_DETECTED | True |
| VIGIA-HMG-99999-11-FINAL_bundle.json | MALICIOUS_INTENT_DETECTED | True |
| **VIGIA_BREAK_001-010_agent_bundle.json** | **PIPELINE_ERROR** | False |
| VIGIA_BREAK_001-010 individuales (001–010) | SUSPICION_DETECTED (pass=True) | varies |

---

## ÍNDICE DE NARRATIVAS (PASO 2)

| archivo | caso narrado | veredicto declarado | confianza | fuente bundle |
|---------|-------------|---------------------|-----------|---------------|
| evidence/VIGIA-NPS-2009-DOMEXUSERS-REPORT_claude.md | NPS-2009-DOMEXUSERS | NOISE | HIGH | results/NPS-2009-DOMEXUSERS_bundle_claude.json |
| evidence/VIGIA-NPS-2010-EMAILS-REPORT_claude.md | NPS-2010-EMAILS | NOISE | HIGH | results/NPS-2010-EMAILS_bundle_claude.json |
| evidence/VIGIA-NPS-2014-USB-NONDETERMINISTIC-REPORT_claude.md | NPS-2014-USB | NOISE | HIGH | results/NPS-2014-USB-NONDETERMINISTIC_bundle.json |
| evidence/VIGIA-NARCOS-SRL2018-REPORT_claude.md | NARCOS (John+Jane+Steve) | MALICE (John), NOISE/ABSTAIN (Steve) | HIGH | results/srl2018/NARCOS-\* |
| reports/hmg_99999_11_e01_claude.md | HMG-99999-11 (Bushell) | MALICE | HIGH | results/agent_batch/VIGIA-HMG-99999-11-FINAL_bundle.json |
| results/hmg_99999_11_claude.md | HMG-99999-11 (Bushell) | MALICE | HIGH | results/agent_batch/VIGIA-HMG-99999-11-FINAL_bundle.json |
| results/srl2018/VIGIA-REAL-NFURY_amicus_curiae.md | VIGIA-REAL-NFURY | SUSPICION | MEDIUM | results/srl2018/VIGIA-REAL-NFURY_bundle.json |
| results/srl2018/VIGIA-REAL-NROMANOFF_amicus_curiae.md | VIGIA-REAL-NROMANOFF (Romanoff) | MALICE | HIGH | results/srl2018/VIGIA-REAL-NROMANOFF_bundle.json |
| results/srl2018/VIGIA-REAL-ROCBA_amicus_curiae.md | VIGIA-REAL-ROCBA | MALICE | HIGH | results/srl2018/VIGIA-REAL-ROCBA_bundle.json |
| results/srl2018/VIGIA-REAL-SRL-ADMIN_amicus_curiae.md | VIGIA-REAL-SRL-ADMIN | MALICE | HIGH | results/srl2018/VIGIA-REAL-SRL-ADMIN_bundle.json |
| results/srl2018/VIGIA-REAL-SRL-AV_amicus_curiae.md | VIGIA-REAL-SRL-AV | MALICE | HIGH | results/srl2018/VIGIA-REAL-SRL-AV_bundle.json |
| results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_amicus_curiae.md | VIGIA-REAL-SRL-DMZ-FTP | MALICE (67%) | MEDIUM (overall) / HIGH (F-002, F-005) | results/srl2018/VIGIA-REAL-SRL-DMZ-FTP_bundle.json |
| results/srl2018/VIGIA-REAL-TDUNGAN_amicus_curiae.md | VIGIA-REAL-TDUNGAN (Dungan) | MALICE | HIGH | results/srl2018/VIGIA-REAL-TDUNGAN_bundle.json |
| results/srl2018/VIGIA-REAL-VANKO_amicus_curiae.md | VIGIA-REAL-VANKO (Vanko) | MALICE | HIGH | results/srl2018/VIGIA-REAL-VANKO_bundle.json |
| vigia_output/FORENSIC_REPORT_VIGIA-REAL-NROMANOFF_SEALED.md | VIGIA-REAL-NROMANOFF (Romanoff) | MALICE (99.99%) | HIGH | vigia_output/bundle_VIGIA-REAL-NROMANOFF.json ⚠ |

**Narrativas huérfanas (sin bundle forense correspondiente):**

| archivo | contenido |
|---------|-----------|
| results/flareon_11_claude.md … flareon_2014_claude.md (×10) | Writeups CTF Flare-On — análisis de reversing, no bundles VIGÍA |
| results/google_takeout_2020_claude.md | Análisis OSINT personal, no bundle |
| results/drive_download_2026_claude.md | Sin bundle |
| results/pagina_web_papa_claude.md | Sin bundle |
| results/relay_main_claude.md | Sin bundle |
| results/skill_evals_claude.md | Sin bundle |
| results/wedlm_claude.md | Sin bundle |

---

## CRUCE DE ÍNDICES — CLASIFICACIÓN A/B/C/D (PASO 3)

### A) CONSISTENTE — narrativa coincide con bundle

| case_id | bundle_verdict | narrativa_verdict | notas |
|---------|----------------|-------------------|-------|
| NPS-2009-DOMEXUSERS | NO_SEMIOTIC_ANOMALY_DETECTED (NOISE) | NOISE HIGH | CONSISTENTE |
| VIGIA-REAL-NFURY | SUSPICION (EBS) | SUSPICION MEDIUM | CONSISTENTE |
| VIGIA-REAL-NROMANOFF (srl2018 ↔ amicus) | MALICE (EBS) | MALICE HIGH | CONSISTENTE entre sí (ver §4b para la inconsistencia con vigia_output/) |
| VIGIA-REAL-ROCBA (srl2018 ↔ amicus) | MALICE | MALICE HIGH | CONSISTENTE |
| VIGIA-REAL-SRL-ADMIN | MALICE | MALICE HIGH | CONSISTENTE |
| VIGIA-REAL-SRL-AV | MALICE | MALICE HIGH | CONSISTENTE |
| VIGIA-REAL-SRL-DMZ-FTP | MALICE 67% (CAIE) / ABSTAIN (Bayesian) | MALICE 67% | CONSISTENTE — la narrativa refleja fielmente la tensión interna del bundle |
| VIGIA-REAL-TDUNGAN (srl2018 ↔ amicus) | MALICE | MALICE HIGH | CONSISTENTE |
| VIGIA-REAL-VANKO (srl2018 ↔ amicus) | MALICE | MALICE HIGH | CONSISTENTE |
| HMG-99999-11 (FINAL bundle ↔ narrativas) | MALICIOUS_INTENT_DETECTED | MALICE HIGH | CONSISTENTE (narrativas basadas en FINAL, no en RAW) |

### B) SOBRE-CONFIANZA — is_conclusive=False o posterior bajo, pero narrativa declara HIGH sin matiz

| case_id | bundle_conclusive | narrativa_confidence | hallazgo |
|---------|-------------------|----------------------|---------|
| NARCOS-JOHN-ALT-DAY2 | False | HIGH (MALICE 95%) | **SOBRE-CONFIANZA** — bundle is_conclusive=False pero narrativa declara MALICE 95% sin mencionar falta de conclusividad |
| NARCOS-JOHN-PRIMARY-Day1 | False | HIGH (MALICE) | **SOBRE-CONFIANZA** |
| NARCOS-JOHN-PRIMARY-Day3 | False | HIGH (MALICE) | **SOBRE-CONFIANZA** |
| NARCOS-JOHN-PRIMARY-Day4 | False | HIGH (MALICE) | **SOBRE-CONFIANZA** |
| WKSTN01-MEMORY-001 | False | (sin narrativa directa) | no aplica |
| VIGIA-REAL-NROMANOFF (vigia_output/) | FALLBACK/NOISE | MALICE 99.99% | **VER §4b — caso especial** |
| VIGIA-REAL-TDUNGAN (vigia_output/) | FALLBACK/NOISE | MALICE HIGH (amicus basado en EBS, no en FALLBACK) | No es SOBRE-CONFIANZA directa: la narrativa cita el EBS bundle, no el FALLBACK |

Nota sobre NARCOS-JOHN: La narrativa `evidence/VIGIA-NARCOS-SRL2018-REPORT_claude.md` no se indexa por bundle individual — cubre múltiples días con veredictos por día. Los bundles con is_conclusive=False reciben veredictos de MALICE 90-95% en la narrativa sin referencia explícita a la falta de conclusividad del bundle. Esta es SOBRE-CONFIANZA sistémica en casos de corpus forense.

### C) FALLO_OCULTO — bundle PIPELINE_ERROR/FORMAT_NOT_SUPPORTED/UNDETERMINED pero narrativa declara veredicto confiado

| case_id | bundle_error | narrativa_veredicto | ¿mencionado en narrativa? | CLASIFICACIÓN |
|---------|--------------|-------------------|--------------------------|---------------|
| NPS-2010-EMAILS | PIPELINE_ERROR (defusedxml) | NOISE HIGH | Sí — en sección "Mode 1 Execution Results" tabla, campo Verdict = PIPELINE_ERROR | **FALLO_OCULTO PARCIAL** — el error está documentado en tablas internas pero la sección ejecutiva declara "Overall verdict: NOISE (confirmed, 95% confidence)" sin matizar que el pipeline determinístico falló |
| NPS-2014-USB | PIPELINE_ERROR (defusedxml) | NOISE HIGH | Sí — en Known Limitations (B-017) | **FALLO_OCULTO PARCIAL** — ídem: NOISE 100% en sección principal, PIPELINE_ERROR enterrado en limitaciones |
| VIGIA_BREAK_001-010 (combined) | PIPELINE_ERROR ('list' has no attribute 'get') | N/A — caso de test, no narrativa forense | No hay narrativa | No aplica |
| NARCOS-STEVE-Day1 | FORMAT_NOT_SUPPORTED | Narrativa NARCOS cubre Steve — "B-016, infrastructure limitation. LLM MALICE 85% OVERRIDDEN" | Sí — explícitamente marcado con ABSTAIN y nota | **NO ES FALLO_OCULTO** — la narrativa documenta el fallback correctamente |
| NARCOS-STEVE-Day2 | FORMAT_NOT_SUPPORTED | Misma narrativa NARCOS | No identificado como Day2 específico | Requiere verificación más profunda |
| VANKO-FALLBACK-001 | UNDETERMINED | Sin narrativa directa | No aplica | No aplica |
| VANKO-FALLBACK-002 | UNDETERMINED | Sin narrativa directa | No aplica | No aplica |
| ROCBA_agent_run | PIPELINE_ERROR | Sin narrativa para este bundle específico | No aplica | No aplica |
| ROCBA_sift_fallback | PIPELINE_ERROR | Sin narrativa para este bundle específico | No aplica | No aplica |

### D) HUÉRFANA — narrativa sin bundle correspondiente

| narrativa | caso | status |
|-----------|------|--------|
| results/flareon_*.claude.md (10 archivos) | CTF Flare-On | Writeups de reversing — no son investigaciones VIGÍA, no requieren bundle |
| results/google_takeout_2020_claude.md | análisis OSINT | Sin bundle — carácter exploratorio |
| results/drive_download_2026_claude.md | sin identificar | Sin bundle |
| results/pagina_web_papa_claude.md | sin identificar | Sin bundle |
| results/relay_main_claude.md | sin identificar | Sin bundle |
| results/skill_evals_claude.md | evaluación skill | Sin bundle — carácter evaluativo, no forense |
| results/wedlm_claude.md | sin identificar | Sin bundle |

---

## LOS 15 PIPELINE_ERROR — ANÁLISIS DETALLADO (PASO 4a)

Para cada caso confirmado como PIPELINE_ERROR en sesiones previas:

| case_id | bundle PIPELINE_ERROR | narrativa .md existe | veredicto narrativa | PROBLEMA |
|---------|----------------------|---------------------|---------------------|---------|
| **NPS-2010-EMAILS** | `results/NPS-2010-EMAILS_bundle_claude.json` | ✓ `evidence/VIGIA-NPS-2010-EMAILS-REPORT_claude.md` | NOISE HIGH | FALLO_OCULTO PARCIAL — sección ejecutiva no matiza el error del pipeline determinístico |
| **NPS-2014-USB-NONDETERMINISTIC** | `results/NPS-2014-USB-NONDETERMINISTIC_bundle.json` | ✓ `evidence/VIGIA-NPS-2014-USB-NONDETERMINISTIC-REPORT_claude.md` | NOISE HIGH | FALLO_OCULTO PARCIAL — ídem |
| **HMG-99999-11-RAW** | `results/agent_batch/VIGIA-HMG-99999-11-RAW_bundle.json` | ✓ `reports/hmg_99999_11_e01_claude.md`, `results/hmg_99999_11_claude.md` | MALICE HIGH | **NO ES FALLO_OCULTO** — las narrativas están basadas en el bundle FINAL (`VIGIA-HMG-99999-11-FINAL_bundle.json`, best_hypothesis=MALICIOUS_INTENT_DETECTED, is_conclusive=True), no en el RAW. El RAW es un paso intermedio documentado en el proceso. |
| **VIGIA_BREAK_001-010** | `results/agent_batch/VIGIA_BREAK_001-010_agent_bundle.json` (error: 'list' object has no attribute 'get') | ✗ Sin narrativa forense | N/A | Los VIGIA_BREAK son casos de test de adversarial robustness, no investigaciones forenses reales. Los bundles individuales (001–010) sí pasan en el batch_summary. El bundle combinado tiene un error de parser. No existe narrativa que oculte este error. |
| **DC-MEM-001** | `results/srl2018/DC-MEM-001_bundle.json` | ✗ | N/A | Sin narrativa — PIPELINE_ERROR silencioso en el índice de bundles |
| **ELF-001** | `results/srl2018/ELF-001_bundle.json` | ✗ | N/A | Sin narrativa |
| **FILE-001** | `results/srl2018/FILE-001_bundle.json` | ✗ | N/A | Sin narrativa |
| **HUNT-001** | `results/srl2018/HUNT-001_bundle.json` | ✗ | N/A | Sin narrativa |
| **M57-JO-2009-12-07** | `results/srl2018/M57-JO-2009-12-07_bundle.json` | ✗ | N/A | Sin narrativa |
| **M57-PAT-2009-12-07** | `results/srl2018/M57-PAT-2009-12-07_bundle.json` | ✗ | N/A | Sin narrativa |
| **M57-PAT-2009-12-11** | `results/srl2018/M57-PAT-2009-12-11_bundle.json` | ✗ | N/A | Sin narrativa |
| **RD02-CDRIVE-001** | `results/srl2018/RD02-CDRIVE-001_bundle.json` | ✗ | N/A | Sin narrativa |
| **RD05-001** | `results/srl2018/RD05-001_bundle.json` | ✗ | N/A | Sin narrativa |
| **ROCBA_agent_run** | `vigia_output/ROCBA_agent_run.json` | ✗ (amicus VIGIA-REAL-ROCBA no cubre este bundle) | N/A | Sin narrativa que comprometa el fallo |
| **ROCBA_sift_fallback** | `vigia_output/ROCBA_sift_fallback.json` | ✗ | N/A | Sin narrativa |

**Resumen §4a:**
- 2 casos de FALLO_OCULTO PARCIAL (NPS-2010, NPS-2014): el error está documentado pero no en posición prominente de la sección ejecutiva.
- 1 caso NO problemático (HMG-99999-11-RAW): workflow legítimo RAW → FINAL → narrativa.
- 1 caso no aplica como forense (VIGIA_BREAK_001-010): test de robustness.
- 11 casos sin narrativa correspondiente: el PIPELINE_ERROR no está ocultado, simplemente no hay narrativa.

---

## VIGIA-REAL-NROMANOFF — COMPARACIÓN DE HASHES (PASO 4b)

### Archivo en cuestión: `vigia_output/bundle_VIGIA-REAL-NROMANOFF.json`

```
sha256sum vigia_output/bundle_VIGIA-REAL-NROMANOFF.json
= ec9288f0bb455214686204661358f4b15ccefdd38d96be3d8f08b3ac33692036
```

```
integrity.bundle_hash (campo dentro del JSON)
= a943337c3880f7f07c0d88f5f9d35db38de6bf3a6f74b43643bb7949af6bb941
```

```
FORENSIC_REPORT_VIGIA-REAL-NROMANOFF_SEALED.md cita:
INTEGRITY_HASH : bundle_hash=a943337c3880f7f07c0d88f5f9d35db38de6bf3a6f74b43643bb7949af6bb941
```

### ¿Los hashes coinciden?

`ec9288f0` ≠ `a943337c`. Sin embargo, esto **no indica tampering**. La explicación es canónica:

El campo `integrity.bundle_hash` es el hash SHA-256 del contenido JSON canonicalizado (via `canonicalize.py`), computado **sobre el contenido del bundle antes de que el campo hash se insertara en el JSON**. El `sha256sum` del archivo en disco incluye el campo `integrity.bundle_hash` en el texto, produciendo un hash diferente. Este comportamiento es inherente a cualquier sistema de auto-referencia de hash. El sealed report cita el hash interno canonicalizado, que coincide exactamente con el campo `integrity.bundle_hash` del archivo. **La integridad del archivo está intacta.**

### El problema real de NROMANOFF: inconsistencia de veredicto entre dos bundles

Este es el hallazgo crítico, independiente de los hashes:

| fuente | bundle | verdecto |
|--------|--------|---------|
| `vigia_output/bundle_VIGIA-REAL-NROMANOFF.json` | decision_trace.decision=ACCEPT, inference_mode=FALLBACK, caie_analysis.verdict=NOISE | **NOISE** |
| `results/srl2018/VIGIA-REAL-NROMANOFF_bundle.json` | overall_verdict=MALICE, overall_confidence=HIGH, composite_trust=1.0 | **MALICE** |
| `vigia_output/FORENSIC_REPORT_VIGIA-REAL-NROMANOFF_SEALED.md` | Cita hash del bundle FALLBACK (vigia_output/) | Declara **MALICE 99.99%** |

El reporte sellado ancla su INTEGRITY_HASH al bundle FALLBACK (cuyo veredicto interno es NOISE/ACCEPT en modo degradado), pero declara el veredicto del bundle EBS (srl2018/). Los dos bundles son el resultado de investigaciones distintas:
- El bundle en `vigia_output/` fue generado por Mode 1 (vigia_agent.py) en modo FALLBACK — 0 señales procesadas, sin herramientas SIFT disponibles.
- El bundle en `results/srl2018/` fue generado por Mode 2 (Claude Code + MCP) con investigación completa de 5 artefactos.

El sealed report debería citar el hash del bundle srl2018/ (que respalda el veredicto de MALICE), no el del bundle FALLBACK (que lo contradice). El hash a943337c es el integrity anchor incorrecto para el veredicto que se declara.

**Nota adicional**: El bundle EBS de NROMANOFF en srl2018/ no tiene archivo `.sha256` a su lado — anomalía respecto al resto de bundles srl2018/ que sí tienen `.sha256`.

---

## VIGIA-REAL-VANKO EN README.md ~L.894 (PASO 4c)

Extracto de README.md (línea ~897):

```
**VIGIA verdict:** MALICE | Confidence: HIGH | Trust fusion: 1.0 | Daubert: ADMISSIBLE (error 8.12%)
**Self-correction:** F-004 (802.11 monitor-mode WiFi captures) initially INTENT.
VIGIA applied Daubert single-source standard. **Downgraded: INTENT -> SUSPICION.**
```

Verificación del bundle de respaldo:

| elemento | resultado |
|----------|----------|
| Bundle `results/srl2018/VIGIA-REAL-VANKO_bundle.json` | ✓ EXISTE |
| overall_verdict | MALICE |
| overall_confidence | HIGH |
| composite_trust | 1.0 |
| daubert_admissible | True |
| .sha256 junto al bundle | ✓ EXISTE |
| Amicus curiae | `results/srl2018/VIGIA-REAL-VANKO_amicus_curiae.md` — MALICE, HIGH |

**Conclusión §4c**: El "Confidence: HIGH" en README.md ~L.897 tiene soporte real en bundle sellado con `.sha256`. La auto-corrección mencionada (INTENT→SUSPICION para F-004) es consistente con la documentación del amicus. **CASO BIEN FORMADO — sin anomalía.**

---

## TABLA CONSOLIDADA DE CLASIFICACIÓN (PASO 3)

| case_id | narrativa | bundle | categoría | severidad |
|---------|-----------|--------|-----------|-----------|
| NPS-2009-DOMEXUSERS | NOISE HIGH | NOISE (is_conclusive=False) | **A — CONSISTENTE** | — |
| NPS-2010-EMAILS | NOISE HIGH | PIPELINE_ERROR | **C — FALLO_OCULTO PARCIAL** | MEDIA |
| NPS-2014-USB-NONDETERMINISTIC | NOISE HIGH | PIPELINE_ERROR | **C — FALLO_OCULTO PARCIAL** | MEDIA |
| HMG-99999-11 (Bushell) | MALICE HIGH | FINAL=MALICE / RAW=PIPELINE_ERROR | **A — CONSISTENTE** (narrativa usa FINAL) | — |
| VIGIA-REAL-NFURY | SUSPICION MEDIUM | SUSPICION | **A — CONSISTENTE** | — |
| VIGIA-REAL-NROMANOFF (amicus ↔ srl2018) | MALICE HIGH | MALICE | **A — CONSISTENTE** | — |
| VIGIA-REAL-NROMANOFF (SEALED.md ↔ vigia_output/) | MALICE 99.99% | NOISE (FALLBACK) — integrity anchor erróneo | **C — FALLO_OCULTO** | **ALTA** |
| VIGIA-REAL-TDUNGAN (amicus ↔ srl2018) | MALICE HIGH | MALICE | **A — CONSISTENTE** | — |
| VIGIA-REAL-TDUNGAN (vigia_output/bundle) | (sin narrativa sellada para este bundle) | NOISE (FALLBACK) | No aplica — no hay narrativa que oculte | — |
| VIGIA-REAL-ROCBA | MALICE HIGH | MALICE (EBS srl2018) | **A — CONSISTENTE** | — |
| VIGIA-REAL-SRL-ADMIN | MALICE HIGH | MALICE | **A — CONSISTENTE** | — |
| VIGIA-REAL-SRL-AV | MALICE HIGH | MALICE | **A — CONSISTENTE** | — |
| VIGIA-REAL-SRL-DMZ-FTP | MALICE 67% | MALICE (CAIE) / ABSTAIN (Bayesian) | **A — CONSISTENTE** (tensión interna reflejada en narrativa) | — |
| VIGIA-REAL-VANKO | MALICE HIGH | MALICE | **A — CONSISTENTE** | — |
| NARCOS-JOHN-ALT-DAY2 | MALICE 95% | MALICIOUS_INTENT_DETECTED (is_conclusive=**False**) | **B — SOBRE-CONFIANZA** | BAJA |
| NARCOS-JOHN-PRIMARY-Day1 | MALICE | MALICIOUS_INTENT_DETECTED (is_conclusive=**False**) | **B — SOBRE-CONFIANZA** | BAJA |
| NARCOS-JOHN-PRIMARY-Day3 | MALICE | MALICIOUS_INTENT_DETECTED (is_conclusive=**False**) | **B — SOBRE-CONFIANZA** | BAJA |
| NARCOS-JOHN-PRIMARY-Day4 | MALICE | MALICIOUS_INTENT_DETECTED (is_conclusive=**False**) | **B — SOBRE-CONFIANZA** | BAJA |
| NARCOS-STEVE-Day1 | ABSTAIN (marcado en narrativa) | FORMAT_NOT_SUPPORTED | **A — CONSISTENTE** (error documentado) | — |
| VANKO-FALLBACK-001 | Sin narrativa | UNDETERMINED | D — HUERFANA (no hay narrativa) | — |
| VANKO-FALLBACK-002 | Sin narrativa | UNDETERMINED | D — HUERFANA (no hay narrativa) | — |
| DC-MEM-001 | Sin narrativa | PIPELINE_ERROR | No aplica — sin narrativa | — |
| ELF-001 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| FILE-001 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| HUNT-001 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| M57-JO-2009-12-07 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| M57-PAT-2009-12-07 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| M57-PAT-2009-12-11 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| RD02-CDRIVE-001 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| RD05-001 | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| ROCBA_agent_run | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| ROCBA_sift_fallback | Sin narrativa | PIPELINE_ERROR | No aplica | — |
| flareon_*.claude.md (×10) | CTF writeups | Sin bundle forense | **D — HUERFANA** (intencional — no forenses) | — |
| google_takeout_2020_claude.md | OSINT | Sin bundle | **D — HUERFANA** | — |

---

## PRIORIDAD DE CORRECCIÓN — CATEGORÍA C (PASO 5)

Los casos de la categoría C ordenados por gravedad, con las acusaciones de MALICE contra personas nombradas primero:

### PRIORIDAD 1 — CRÍTICA: MALICE contra persona nombrada, integrity anchor incorrecto

**VIGIA-REAL-NROMANOFF — FORENSIC_REPORT_VIGIA-REAL-NROMANOFF_SEALED.md**

- **Persona nombrada**: Natasha Romanoff (personaje de corpus FOR508, dataset público SANS)
- **Problema**: El reporte sellado declara MALICE 99.99% y cita el hash del bundle FALLBACK (`a943337c...`), pero ese bundle tiene `decision_trace.decision = ACCEPT` y `caie_analysis.verdict = NOISE`. El veredicto de MALICE proviene del bundle EBS en `results/srl2018/VIGIA-REAL-NROMANOFF_bundle.json`, que NO es el que está referenciado como integrity anchor.
- **Riesgo Daubert**: El integrity anchor no respalda el veredicto declarado. Si se presenta el reporte sellado con su hash en un contexto legal, verificar el bundle citado produce un resultado contradictorio (NOISE) respecto al veredicto del reporte (MALICE).
- **Acción necesaria**: Reemplazar `INTEGRITY_HASH` en el reporte sellado por el hash del bundle EBS correcto (`results/srl2018/VIGIA-REAL-NROMANOFF_bundle.json`), o documentar explícitamente en el reporte que el análisis se basa en el bundle EBS y no en el bundle FALLBACK.
- **Nota**: El amicus curiae (`results/srl2018/VIGIA-REAL-NROMANOFF_amicus_curiae.md`) es correcto e interno al bundle EBS.

### PRIORIDAD 2 — ALTA: PIPELINE_ERROR con narrativa confiada sin matiz ejecutivo

**NPS-2010-EMAILS — evidence/VIGIA-NPS-2010-EMAILS-REPORT_claude.md**

- **Persona nombrada**: Ninguna. Corpus educativo.
- **Problema**: La sección ejecutiva declara "Overall verdict: NOISE (confirmed, 95% confidence)" sin indicar que `results/NPS-2010-EMAILS_bundle_claude.json` contiene `PIPELINE_ERROR`. El error de defusedxml está documentado en tablas de la sección "Mode 1 Execution Results" y en Known Limitations, pero no en el Executive Summary.
- **Riesgo**: Un lector que lea solo el Executive Summary concluirá que el pipeline determinístico confirmó NOISE, lo cual es falso. El verdadero NOISE fue determinado por el MCP/Ollama, no por el pipeline de Mode 1.
- **Acción necesaria**: Agregar en el Executive Summary: "El pipeline determinístico (Mode 1) retornó PIPELINE_ERROR (defusedxml ausente). El veredicto NOISE es exclusivamente producto del análisis por Mode 2 (MCP)."

**NPS-2014-USB-NONDETERMINISTIC — evidence/VIGIA-NPS-2014-USB-NONDETERMINISTIC-REPORT_claude.md**

- **Persona nombrada**: Ninguna. Test de calibración.
- **Problema**: Análogo al de NPS-2010-EMAILS. La narrativa afirma "all tools converge" en la sección ejecutiva, pero el bundle de Mode 1 contiene PIPELINE_ERROR.
- **Riesgo**: Igual que arriba.
- **Acción necesaria**: Idéntica corrección en el Executive Summary.

### PRIORIDAD 3 — BAJA: is_conclusive=False no reflejado en narrativa (SOBRE-CONFIANZA)

**NARCOS-JOHN-\* (varios días) — evidence/VIGIA-NARCOS-SRL2018-REPORT_claude.md**

- **Personas nombradas**: "John" (personaje de corpus, no real identificado).
- **Problema**: Cuatro bundles (JOHN-ALT-DAY2, JOHN-PRIMARY-Day1/Day3/Day4) tienen `is_conclusive=False`, pero la narrativa NARCOS declara MALICE 90-95% sin mencionar la falta de conclusividad.
- **Riesgo**: Menor — los bundles sí muestran MALICIOUS_INTENT_DETECTED. El campo `is_conclusive=False` refleja un margen estadístico, no un cambio de veredicto. Sin embargo, una narrativa rigurosa debería matizarlo.
- **Acción recomendada** (no urgente): Agregar en los findings correspondientes que "is_conclusive=False indica posterior por debajo del umbral de certeza matemática, aunque el veredicto MALICE se mantiene."

---

## HALLAZGOS ADICIONALES

### VIGIA-REAL-TDUNGAN — bundle FALLBACK huérfano

El archivo `vigia_output/bundle_VIGIA-REAL-TDUNGAN.json` tiene el mismo problema estructural que NROMANOFF: `inference_mode=FALLBACK`, `caie_analysis.verdict=NOISE`. Sin embargo, a diferencia de NROMANOFF, **no existe un reporte sellado en vigia_output/ que cite este bundle**. El amicus curiae de TDUNGAN en srl2018/ está correctamente anclado al bundle EBS. Este bundle FALLBACK es un artefacto residual sin narrativa que lo contradiga — no es un FALLO_OCULTO activo, pero debe documentarse como evidencia potencialmente confusa.

### Bundles sin .sha256 en srl2018/

Dos bundles EBS modal en srl2018/ no tienen archivo `.sha256`:
- `VIGIA-REAL-NROMANOFF_bundle.json` (sin .sha256)
- `VIGIA-REAL-TDUNGAN_bundle.json` (sin .sha256)

Todos los demás bundles en srl2018/ tienen `.sha256`. Esta anomalía debe corregirse generando los archivos `.sha256` correspondientes.

---

## LIMITACIONES DE ESTA AUDITORÍA

1. El cruzamiento por case_id fue realizado por coincidencia de nombre de archivo y campo `case_id` en el JSON. No se verificó la coherencia de los campos `tool_execution_log` o `audit_trail` dentro de cada bundle.
2. Los archivos en `results/llm_mode/`, `results/kiwi/`, `results/r7_test/`, `results/real/` y `cases/tuck-2019-macos/` no fueron indexados en este pase — podrían contener bundles adicionales.
3. Los writeups CTF (`flareon_*.claude.md`) fueron clasificados como HUÉRFANOS intencionales, pero no se leyó su contenido completo para descartar que citen bundles VIGÍA.
4. No se verificó la integridad de los `tool_execution_log` chain (v2) dentro de cada bundle.

---

## RESUMEN EJECUTIVO

| categoría | cantidad | descripción |
|-----------|---------|-------------|
| A — CONSISTENTE | 16 | narrativa ↔ bundle coinciden |
| B — SOBRE-CONFIANZA | 4 | is_conclusive=False sin matiz en narrativa |
| C — FALLO_OCULTO | 3 | narrative confiada sobre bundle con error |
| D — HUÉRFANA | 8 | narrativas sin bundle correspondiente (mayoría intencionales) |
| Sin narrativa | 11 | PIPELINE_ERROR en bundles sin narrativa activa |

**Corrección urgente (antes de cualquier presentación externa):** El sealed report `vigia_output/FORENSIC_REPORT_VIGIA-REAL-NROMANOFF_SEALED.md` cita un integrity anchor que contradice su propio veredicto. Es la única anomalía que afecta directamente la admisibilidad Daubert de un reporte de MALICE contra una persona nombrada.
