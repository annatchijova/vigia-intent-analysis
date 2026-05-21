# VIGIA — Índice Maestro de Documentación Académica
<!-- Auto-generado: 2026-05-20 | Corpus: 193 módulos | Idiomas: EN / ES / RU / ZH -->
<!-- Generado por Batch API de Moonshot (Kimi K2.6) | Auditoría: Colectivo IA VIGIA -->

> **Audiencia objetivo:** Investigadores forenses, jueces técnicos (SANS), revisores Daubert.  
> Cada documento cubre el módulo en 4 idiomas con glosario técnico y nota 【科学说明】 sobre semiótica de Peirce, Eco y Grice.  
> Todos los documentos se encuentran en `docs/academic/` del repositorio.

---

## Navegación rápida

| Sección | Módulos | Descripción |
|---------|---------|-------------|
| [01 — Núcleo del Sistema](#01--núcleo-del-sistema-core) | 49 | Pipeline central, semiótica, señales, calibración |
| [02 — Herramientas de Análisis](#02--herramientas-de-análisis-tools) | 39 | CAIE, NLP adversarial, MITRE, patrones, EML |
| [03 — Análisis Forense SIFT](#03--análisis-forense-sift) | 16 | MFT, prefetch, shellbag, registry, network, browser, memory |
| [04 — Forense Especializado](#04--forense-especializado-forensics) | 10 | PDF, PKI, RFC3161, visión, cadena de custodia |
| [05 — Motor de Inferencia](#05--motor-de-inferencia-inference) | 9 | Razonamiento abductivo, fingerprint conductual, determinismo |
| [06 — Pipeline y Orquestación](#06--pipeline-y-orquestación) | 6 | Bundle, report, bridge SIFT, registro de evidencia |
| [07 — Seguridad y Sandbox](#07--seguridad-y-sandbox) | 4 | Sandbox, seguridad forense, hardening |
| [08 — Gobernanza y Riesgo](#08--gobernanza-y-riesgo) | 4 | Trust levels, risk layer, trazabilidad |
| [09 — Módulo Raíz VIGIA](#09--módulo-raíz-vigia) | 8 | API, CLI, config, namespace shim, core |
| [10 — Scripts Operacionales](#10--scripts-operacionales) | 8 + casos | Utilidades de ejecución, conversión, análisis |
| [11 — Módulos Especializados Menores](#11--módulos-especializados-menores) | 12 | Abduction, verdict, patterns, temporal, models |

---

## 01 — Núcleo del Sistema (`core/`)

> Contiene el 25% del corpus. Son los módulos que **no pueden fusionarse** — cada uno es un nodo crítico en el pipeline Daubert.

### 01.1 — Detección Semiótica y de Intención

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/forensic_technical_detector.py` | [02a8adb4_doc.md](02a8adb4_doc.md) | EN/ES/RU/ZH |
| `vigia/core/vigia_core_forensic_technical_detector.py` | [9e2e4cde_doc.md](9e2e4cde_doc.md) | EN/ES/RU/ZH |
| `vigia/core/semiotic_detector.py` | [94fbce3d_doc.md](94fbce3d_doc.md) | EN/ES |
| `vigia/core/semiotic_detector_v2.py` | [b32a18e2_doc.md](b32a18e2_doc.md) | EN/ES/RU/ZH |
| `vigia/core/vigia_core_semiotic_detector.py` | [5dac09b1_doc.md](5dac09b1_doc.md) | EN/ES/RU/ZH |
| `vigia/core/narrative_auditor.py` | [4d89a448_doc.md](4d89a448_doc.md) | EN/ES/RU/ZH |
| `vigia/core/peirceplanner_bounded.py` | [673c2ea3_doc.md](673c2ea3_doc.md) | EN/ES/RU/ZH |
| `vigia/core/abductive_intent_engine.py` | [f14e91cc_doc.md](f14e91cc_doc.md) | EN/ES/RU/ZH |
| `vigia/abductive_intent_engine.py` | [9cf0944e_doc.md](9cf0944e_doc.md) | EN/ES/RU/ZH |
| `vigia/core/carnegie_education_detector.py` | [9ae17aea_doc.md](9ae17aea_doc.md) | EN |

### 01.2 — Señales, Mapeo y Calidad

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/signal_mapper.py` | [7ed37665_doc.md](7ed37665_doc.md) | EN/ES/RU/ZH |
| `vigia/core/signal_quality_gate.py` | [65cc09c3_doc.md](65cc09c3_doc.md) | EN/ES/RU/ZH |
| `vigia/core/signal_contract.py` | [d91bf435_doc.md](d91bf435_doc.md) | EN/ES/RU/ZH |
| `vigia/core/advanced_signal_router.py` | [09c233b0_doc.md](09c233b0_doc.md) | EN/ES/RU/ZH |
| `vigia/core/normalization_layer.py` | [6d01ab83_doc.md](6d01ab83_doc.md) | EN/ES/RU/ZH |
| `vigia/signal_quality_gate.py` | [6ae41267_doc.md](6ae41267_doc.md) | EN/ES/RU/ZH |

### 01.3 — Calibración y Razón de Verosimilitud

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/likelihood_engine.py` | [07e3d476_doc.md](07e3d476_doc.md) | EN/ES/RU/ZH |
| `vigia/core/likelihood_ratio.py` | [0b473fc1_doc.md](0b473fc1_doc.md) | EN/ES/RU/ZH |
| `vigia/core/lr_calibration.py` | [43e5d14c_doc.md](43e5d14c_doc.md) | EN/ES/RU/ZH |
| `vigia/core/fit_calibration.py` | [65ccdf43_doc.md](65ccdf43_doc.md) | EN/ES/RU/ZH |
| `vigia/core/ebs_v1.py` | [bb8bfa2d_doc.md](bb8bfa2d_doc.md) | EN/ES/RU/ZH |
| `vigia/models/ebs.py` | [13b5b838_doc.md](13b5b838_doc.md) | EN/ES/RU/ZH |
| `engine/likelihood_engine.py` | [0c4cec60_doc.md](0c4cec60_doc.md) | EN/ES/RU/ZH |

### 01.4 — Pipeline, Integridad y Cadena de Custodia

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/pipeline.py` | [2fcd8826_doc.md](2fcd8826_doc.md) | EN/ES/RU/ZH |
| `vigia/core/canonicalize.py` | [69393490_doc.md](69393490_doc.md) | EN/ES/RU/ZH |
| `vigia/core/chain_of_custody.py` | [cc27fff8_doc.md](cc27fff8_doc.md) | EN/ES/RU |
| `vigia/core/integrity_constraints.py` | [2dbec0bc_doc.md](2dbec0bc_doc.md) | EN/ES/RU/ZH |
| `vigia/core/audit_action.py` | [48ab3a10_doc.md](48ab3a10_doc.md) | EN/ES/RU/ZH |
| `vigia/core/execution_logger.py` | [0b4cea01_doc.md](0b4cea01_doc.md) | EN/ES/RU/ZH |
| `vigia/core/bundle_builder.py` | [5d49495e_doc.md](5d49495e_doc.md) | EN |

### 01.5 — Evidencia, Confianza y Decisión

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/evidence_aggregator.py` | [3c7b4268_doc.md](3c7b4268_doc.md) | EN/ES/RU/ZH |
| `vigia/core/trust_fusion.py` | [b12aabdd_doc.md](b12aabdd_doc.md) | EN/ES/RU/ZH |
| `vigia/core/trust_levels.py` | [6599e8ef_doc.md](6599e8ef_doc.md) | EN/ES/RU/ZH |
| `vigia/core/decision_layer.py` | [1ea10b1b_doc.md](1ea10b1b_doc.md) | EN/ES/RU |
| `vigia/core/dissent_report.py` | [5fbbcb8f_doc.md](5fbbcb8f_doc.md) | EN/ES/RU/ZH |
| `vigia/core/explainable_governance.py` | [aa4e03f6_doc.md](aa4e03f6_doc.md) | EN |
| `vigia/core/compare_baseline.py` | [ae52197a_doc.md](ae52197a_doc.md) | EN/ES/RU/ZH |

### 01.6 — Razonamiento y Causalidad

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/causal_closure.py` | [79fddb64_doc.md](79fddb64_doc.md) | EN/ES/RU/ZH |
| `vigia/core/entanglement.py` | [e4d00825_doc.md](e4d00825_doc.md) | EN/ES/RU/ZH |
| `vigia/core/ockham_adversarial.py` | [adf95e94_doc.md](adf95e94_doc.md) | EN/ES/RU/ZH |
| `vigia/core/graph_stability.py` | [52d810c5_doc.md](52d810c5_doc.md) | EN/ES/RU/ZH |
| `vigia/core/geopolitical_v2.py` | [3aa7e98b_doc.md](3aa7e98b_doc.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_adapter.py` | [ab0b295d_doc.md](ab0b295d_doc.md) | EN/ES/RU/ZH |

### 01.7 — Configuración, Seguridad Operacional e Infraestructura Core

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/core/config_sentinel.py` | [06e4330c_doc.md](06e4330c_doc.md) | EN/ES/RU/ZH |
| `vigia/core/path_guard.py` | [608005f0_doc.md](608005f0_doc.md) | EN |
| `vigia/core/risk_bounded_layer.py` | [777f8e26_doc.md](777f8e26_doc.md) | EN/ES/RU/ZH |
| `vigia/core/shadow_mode.py` | [be1aca3f_doc.md](be1aca3f_doc.md) | EN/ES/RU/ZH |
| `vigia/core/resource_optimizer.py` | [1566c038_doc.md](1566c038_doc.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_db.py` | [2f970571_doc.md](2f970571_doc.md) | EN/ES/RU/ZH |
| `vigia/core/llm_backend.py` | [987f4f2e_doc.md](987f4f2e_doc.md) | EN/ES/RU/ZH |

---

## 02 — Herramientas de Análisis (`tools/`)

> Segunda capa más grande del corpus. Candidatos a fusión temática (ver sección de recomendaciones).

### 02.1 — Análisis de Incongruencias y Artefactos (CRITICO — NO FUSIONAR)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/caie.py` (v1) | [8c5d9283_doc.md](8c5d9283_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/caie.py` (v2) | [ed0d4351_doc.md](ed0d4351_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/cross_artifact_resonance.py` | [2f6f63bf_doc.md](2f6f63bf_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_locality.py` | [1dbdaea0_doc.md](1dbdaea0_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_kernel.py` | [44542c22_doc.md](44542c22_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/document_integrity.py` | [c61c815b_doc.md](c61c815b_doc.md) | EN/ES/RU/ZH |

### 02.2 — NLP Adversarial y Mutaciones

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/adversarial_nlp.py` | [ca997fe5_doc.md](ca997fe5_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_robustness.py` | [8ffefb83_doc.md](8ffefb83_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_mutation_suite.py` | [9624f888_doc.md](9624f888_doc.md) | EN/ES/RU/ZH |
| `vigia/patterns/adversarial_silence.py` | [b5692c6d_doc.md](b5692c6d_doc.md) | EN/ES/RU/ZH |

### 02.3 — MITRE ATT&CK y Patrones

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/mitre_mapping.py` | [55f58261_doc.md](55f58261_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/mitre_clustering.py` | [8fcbd5bb_doc.md](8fcbd5bb_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/pattern_detector.py` | [7a688cdd_doc.md](7a688cdd_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/picerl_mapping.py` | [f8c579f2_doc.md](f8c579f2_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/nlp_constants.py` | [5ca62db1_doc.md](5ca62db1_doc.md) | EN/ES/RU/ZH |

### 02.4 — Análisis de Email y Comunicaciones (EML)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/eml_gci.py` | [e21ddd66_doc.md](e21ddd66_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/eml_symbolic.py` | [3c4283bf_doc.md](3c4283bf_doc.md) | EN/ES/RU/ZH |

### 02.5 — Señales, Adaptadores y Temporalidad

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/signal_adapter.py` | [6725056c_doc.md](6725056c_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/signal_contract.py` | [26dcd8ee_doc.md](26dcd8ee_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/temporal_drift.py` | [f02065bf_doc.md](f02065bf_doc.md) | EN/ES/RU/ZH |
| `vigia/temporal/coherence_validator.py` | [40950455_doc.md](40950455_doc.md) | EN/ES/RU/ZH |

### 02.6 — Inferencia y Fingerprint (tools/)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/abductive_intent_engine.py` | [fd5b51d8_doc.md](fd5b51d8_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/behavioral_fingerprint.py` | [8517382b_doc.md](8517382b_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/metabolic_profiler.py` | [ef35ef9d_doc.md](ef35ef9d_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/visible_variables.py` | [e3ae3cf0_doc.md](e3ae3cf0_doc.md) | EN/ES/RU/ZH |

### 02.7 — Geopolítica y Contexto Externo

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/geopolitical.py` | [1c834989_doc.md](1c834989_doc.md) | EN/ES/RU/ZH |

### 02.8 — Calibración y Base de Conocimiento (tools/)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/build_calibration_dataset.py` | [af02e6b5_doc.md](af02e6b5_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/generate_calibration.py` | [9dc17ed4_doc.md](9dc17ed4_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/init_patterns_db.py` | [1e81c666_doc.md](1e81c666_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/forensic_db.py` | [f780b9eb_doc.md](f780b9eb_doc.md) | EN/ES/RU/ZH |

### 02.9 — Adaptadores de Casos y Planeación

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/tools/vigia_case_adapter.py` | [a409595e_doc.md](a409595e_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_entanglement.py` | [870bfb4a_doc.md](870bfb4a_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner.py` | [2a5dbf34_doc.md](2a5dbf34_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner_GIT.py` | [801ee7c7_doc.md](801ee7c7_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_sift_bridge.py` | [3f495b70_doc.md](3f495b70_doc.md) | EN/ES/RU/ZH |
| `vigia/tools/vision_audit.py` | [c12c7450_doc.md](c12c7450_doc.md) | EN/ES/RU/ZH |

---

## 03 — Análisis Forense SIFT (`sift/`)

> Módulos de integración directa con SANS SIFT Workstation. **Candidatos a índice unificado de integración SIFT** pero mantenidos separados por especificidad forense.

| Módulo Python | Doc | Idiomas | Artefacto Forense |
|---------------|-----|---------|-------------------|
| `vigia/sift/sift_orchestrator.py` | [e782beeb_doc.md](e782beeb_doc.md) | EN/ES/RU/ZH | Orquestador maestro |
| `vigia/sift/unified_timeline_engine.py` | [5a035ab4_doc.md](5a035ab4_doc.md) | EN/ES/RU/ZH | Timeline unificado |
| `vigia/sift/mft_timeline_analyzer.py` | [72884365_doc.md](72884365_doc.md) | EN/ES/RU/ZH | MFT / $MFT |
| `vigia/sift/registry_timeline_reconstructor.py` | [71679681_doc.md](71679681_doc.md) | EN/ES/RU/ZH | Windows Registry |
| `vigia/sift/prefetch_analyzer.py` | [6c431d0b_doc.md](6c431d0b_doc.md) | EN/ES/RU/ZH | Prefetch / WinPrefetch |
| `vigia/sift/shellbag_analyzer.py` | [c477932e_doc.md](c477932e_doc.md) | EN/ES/RU/ZH | ShellBags |
| `vigia/sift/amcache_shimcache.py` | [d909325d_doc.md](d909325d_doc.md) | EN/ES/RU/ZH | AmCache / ShimCache |
| `vigia/sift/usb_device_tracker.py` | [74d4c0cc_doc.md](74d4c0cc_doc.md) | EN/ES/RU/ZH | USB / SetupAPI |
| `vigia/sift/event_log_correlator.py` | [fda3319e_doc.md](fda3319e_doc.md) | EN/ES/RU/ZH | Windows Event Logs |
| `vigia/sift/disk_forensics.py` | [03834f85_doc.md](03834f85_doc.md) | EN/ES/RU/ZH | Disk / Particiones |
| `vigia/sift/memory_forensics.py` | [f44d4660_doc.md](f44d4660_doc.md) | EN/ES/RU/ZH | Volatility / RAM |
| `vigia/sift/network_forensics.py` | [b9ce7db8_doc.md](b9ce7db8_doc.md) | EN/ES/RU/ZH | PCAP / NetFlow |
| `vigia/sift/browser_forensics.py` | [350c8eab_doc.md](350c8eab_doc.md) | EN/ES/RU/ZH | Browser artifacts |
| `vigia/sift/ioc_manager.py` | [c0b86e2d_doc.md](c0b86e2d_doc.md) | EN/ES/RU/ZH | IOC / Indicadores |
| `vigia/sift/sans_phase.py` | [6f157b07_doc.md](6f157b07_doc.md) | EN/ES/RU/ZH | Fases SANS PICERL |
| `vigia/sift/_math_utils.py` | [91f2a764_doc.md](91f2a764_doc.md) | EN/ES/RU/ZH | Utils deterministas |

---

## 04 — Forense Especializado (`forensics/`)

> Módulos de alta especificidad técnica. **No fusionar** — cada uno es admisible como evidencia independiente bajo Daubert.

| Módulo Python | Doc | Idiomas | Estándar |
|---------------|-----|---------|----------|
| `vigia/forensics/temporal_forensics.py` | [19bc56e9_doc.md](19bc56e9_doc.md) | EN/ES/RU/ZH | Timestamps / MACB |
| `vigia/forensics/temporal_forensics_redteam.py` | [b00e30d6_doc.md](b00e30d6_doc.md) | EN/ES/RU/ZH | Red-team temporal |
| `vigia/forensics/vision_audit.py` | [e0f29980_doc.md](e0f29980_doc.md) | EN | Auditoría visual |
| `vigia/forensics/vision_audit_final.py` | [b2c8b2e5_doc.md](b2c8b2e5_doc.md) | EN/ES/RU/ZH | Visión forense final |
| `vigia/forensics/forensic_reporter.py` | [2640bfa6_doc.md](2640bfa6_doc.md) | EN/ES/RU/ZH | Reporting forense |
| `vigia/forensics/pdf_dual_parser.py` | [815ea136_doc.md](815ea136_doc.md) | EN/ES/RU/ZH | Análisis PDF dual |
| `vigia/forensics/pki_tools.py` | [3c13ec36_doc.md](3c13ec36_doc.md) | EN/ES/RU/ZH | PKI / Certificados |
| `vigia/forensics/rfc3161_chain.py` | [c639dd43_doc.md](c639dd43_doc.md) | EN/ES/RU/ZH | RFC 3161 timestamp |
| `vigia/forensics/vigia_chain_of_custody.py` | [4ac813e4_doc.md](4ac813e4_doc.md) | EN/ES/RU/ZH | Chain of Custody |
| `vigia/forensics/pki_tools.py` | [3c13ec36_doc.md](3c13ec36_doc.md) | EN/ES/RU/ZH | X.509 / PKCS#11 |

---

## 05 — Motor de Inferencia (`inference/`)

> Implementa los tres momentos Peircéanos: Firstness (abducción), Secondness (verificación), Thirdness (síntesis).

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/inference/abductive_reasoner.py` | [996f511d_doc.md](996f511d_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/abductive_reasoner_v2.py` | [8fa48c2f_doc.md](8fa48c2f_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/behavioral_fingerprint.py` | [747d525d_doc.md](747d525d_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/case_pattern_library.py` | [5506a8ca_doc.md](5506a8ca_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/check_determinism.py` | [7b4e076e_doc.md](7b4e076e_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/cross_artifact_resonance.py` | [ff2678bd_doc.md](ff2678bd_doc.md) | EN/ES/RU/ZH |
| `vigia/inference/metabolic_profiler.py` | [8bc0d526_doc.md](8bc0d526_doc.md) | EN/ES/RU/ZH |
| `vigia/memory/case_pattern_library.py` | [be71e68a_doc.md](be71e68a_doc.md) | EN/ES/RU/ZH |
| `vigia/collapse_decision.py` | [7b5f476a_doc.md](7b5f476a_doc.md) | EN |

---

## 06 — Pipeline y Orquestación (`pipeline/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/pipeline/pipeline.py` | [efe5a51e_doc.md](efe5a51e_doc.md) | EN/ES/RU/ZH |
| `vigia/pipeline/evidence_bundle.py` | [3e34d629_doc.md](3e34d629_doc.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_builder.py` | [10a8df9f_doc.md](10a8df9f_doc.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_exporter.py` | [232e96c6_doc.md](232e96c6_doc.md) | EN/ES/RU/ZH |
| `vigia/pipeline/security_evidence_registry.py` | [6ba25d19_doc.md](6ba25d19_doc.md) | EN/ES/RU/ZH |
| `vigia/pipeline/vigia_integration_bridge.py` | [db45f26c_doc.md](db45f26c_doc.md) | EN/ES/RU/ZH |

---

## 07 — Seguridad y Sandbox (`security/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/security/sandbox.py` | [2042863e_doc.md](2042863e_doc.md) | EN/ES/RU/ZH |
| `vigia/sandbox.py` | [845ea393_doc.md](845ea393_doc.md) | EN/ES/RU/ZH |
| `vigia/security/security.py` | [741696a1_doc.md](741696a1_doc.md) | EN/ES/RU/ZH |
| `vigia/security/vigia_seguridad.py` | [61a43ef6_doc.md](61a43ef6_doc.md) | EN/ES/RU/ZH |
| `vigia/security.py` | [8797b679_doc.md](8797b679_doc.md) | EN/ES/RU/ZH |

---

## 08 — Gobernanza y Riesgo (`governance/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/governance/trust_levels_p0.py` | [854c5cef_doc.md](854c5cef_doc.md) | EN/ES/RU/ZH |
| `vigia/governance/risk_bounded_layer_v2.py` | [224b5934_doc.md](224b5934_doc.md) | EN/ES/RU/ZH |
| `vigia/verdict/quadripartite.py` | [04d02947_doc.md](04d02947_doc.md) | EN/ES/RU/ZH |
| `vigia/utils/path_guard.py` | [8d40e5b1_doc.md](8d40e5b1_doc.md) | EN/ES/RU/ZH |

---

## 09 — Módulo Raíz VIGIA (`vigia/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/vigia_core.py` | [0642d009_doc.md](0642d009_doc.md) | EN/ES/RU/ZH |
| `vigia/vigia_api.py` | [75bb5e9f_doc.md](75bb5e9f_doc.md) | EN/ES/RU/ZH |
| `vigia/cli.py` | [7f454130_doc.md](7f454130_doc.md) | EN/ES/RU/ZH |
| `vigia/config.py` | [83a57d82_doc.md](83a57d82_doc.md) | EN/ES/RU/ZH |
| `vigia/vigia_namespace_shim.py` | [14ba142e_doc.md](14ba142e_doc.md) | EN/ES/RU/ZH |
| `vigia/llm_backend_v2.py` | [2bb62251_doc.md](2bb62251_doc.md) | EN/ES/RU/ZH |
| `vigia/vigia_sift_bridge.py` | [ff8f60eb_doc.md](ff8f60eb_doc.md) | EN/ES/RU/ZH |
| `vigia/vigia_sift_bridge_final.py` | [de7d9a40_doc.md](de7d9a40_doc.md) | EN/ES/RU/ZH |
| `vigia/vigia_command_center.py` | [7d593d40_doc.md](7d593d40_doc.md) | EN/ES/RU/ZH |
| `vigia/phonetic_loader.py` | [08182f1b_doc.md](08182f1b_doc.md) | EN/ES/RU/ZH |

---

## 10 — Scripts Operacionales (`scripts/`)

### Ejecución y Diagnóstico

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `scripts/run_vigia_full.py` | [2c0d7aea_doc.md](2c0d7aea_doc.md) | EN/ES/RU/ZH |
| `scripts/run_case.py` | [bc9b406c_doc.md](bc9b406c_doc.md) | EN/ES/RU/ZH |
| `scripts/run_demo.py` | [d4e678b5_doc.md](d4e678b5_doc.md) | EN |
| `scripts/pre_release_check.py` | [5be37470_doc.md](5be37470_doc.md) | EN/ES/RU/ZH |
| `vigia/scripts/compare_runs.py` | [8cf3f33e_doc.md](8cf3f33e_doc.md) | EN/ES/RU/ZH |
| `vigia/scripts/evaluate_detector.py` | [c8cb7042_doc.md](c8cb7042_doc.md) | EN/ES/RU/ZH |
| `vigia/scripts/consolidate_cases.py` | [0cf21887_doc.md](0cf21887_doc.md) | EN/ES/RU/ZH |
| `vigia/scripts/top_breaking_phrases.py` | [cda1c372_doc.md](cda1c372_doc.md) | EN/ES/RU/ZH |

### Conversión y Mantenimiento

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `scripts/convert_break_cases.py` | [28c684d0_doc.md](28c684d0_doc.md) | EN/ES/RU/ZH |
| `scripts/convert_legacy_cases.py` | [d1ec968d_doc.md](d1ec968d_doc.md) | EN/ES/RU/ZH |
| `scripts/convert_md_cases.py` | [a05271e7_doc.md](a05271e7_doc.md) | EN/ES/RU/ZH |
| `scripts/export_patterns.py` | [bd9cee0e_doc.md](bd9cee0e_doc.md) | EN/ES/RU/ZH |
| `scripts/fix_inits.py` | [9f525516_doc.md](9f525516_doc.md) | ZH |
| `scripts/fix_security_init.py` | [e1094ebf_doc.md](e1094ebf_doc.md) | EN/ES/RU/ZH |
| `scripts/vigia_mass_refactor.py` | [637ecdc6_doc.md](637ecdc6_doc.md) | EN/ES |
| `scripts/vigia_patch_valkyrie.py` | [2989e9bd_doc.md](2989e9bd_doc.md) | EN/ES |
| `recalibrate_cases.py` | [13bb704b_doc.md](13bb704b_doc.md) | EN/ES/RU/ZH |
| `apply_caie_patch.py` | [442419c2_doc.md](442419c2_doc.md) | EN/ES/RU/ZH |
| `cases/demo_case.py` | [1e1dcf92_doc.md](1e1dcf92_doc.md) | EN/ES/RU/ZH |

---

## 11 — Módulos Especializados Menores

### Abducción Avanzada (`abduction/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/abduction/hypothesis_lineage.py` | [e7859153_doc.md](e7859153_doc.md) | EN/ES/RU/ZH |
| `vigia/abduction/vigia_artifact_graph.py` | [3254c6ec_doc.md](3254c6ec_doc.md) | EN/ES |
| `vigia/abduction/vigia_counter_fact.py` | [8f6f7187_doc.md](8f6f7187_doc.md) | EN |

### Acción Mitigación (`action/`)

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `vigia/action/vigia_mitigation_planner.py` | [5fba2910_doc.md](5fba2910_doc.md) | EN/ES/RU/ZH |

### Adversarial Testing

| Módulo Python | Doc | Idiomas |
|---------------|-----|---------|
| `run_adversarial_tests.py` | [8ebd0d52_doc.md](8ebd0d52_doc.md) | EN/ES/RU/ZH |

---

## Documentos con cobertura de idioma incompleta

Los siguientes documentos fueron generados con cobertura parcial de idiomas. Candidatos a regeneración con Batch API si el tiempo lo permite:

| Hash | Idiomas presentes | Faltante |
|------|-------------------|----------|
| `9f525516` | ZH únicamente | EN/ES/RU |
| `69cb51de` | ZH únicamente | EN/ES/RU |
| `d4e678b5` | EN únicamente | ES/RU/ZH |
| `8f6f7187` | EN únicamente | ES/RU/ZH |
| `aa4e03f6` | EN únicamente | ES/RU/ZH |
| `9ae17aea` | EN únicamente | ES/RU/ZH |
| `7b5f476a` | EN únicamente | ES/RU/ZH |
| `608005f0` | EN únicamente | ES/RU/ZH |
| `e0f29980` | EN únicamente | ES/RU/ZH |
| `5d49495e` | EN únicamente | ES/RU/ZH |
| `3254c6ec` | EN/ES únicamente | RU/ZH |
| `2989e9bd` | EN/ES únicamente | RU/ZH |
| `637ecdc6` | EN/ES únicamente | RU/ZH |
| `94fbce3d` | EN/ES únicamente | RU/ZH |
| `cc27fff8` | EN/ES/RU | ZH |
| `1ea10b1b` | EN/ES/RU | ZH |
| `779b4236` | EN/ES/RU | ZH |

---

## Estadísticas del corpus

| Métrica | Valor |
|---------|-------|
| Total documentos | 193 |
| Cobertura EN/ES/RU/ZH completa | ~160 docs (~83%) |
| Documentos solo EN | 8 |
| Documentos solo ZH | 2 |
| Sección más grande | `core/` (49 docs) |
| Sección más crítica para SIFT | `sift/` (16 docs) |
| Módulos duplicados detectados | 7 pares (ver recomendaciones) |

---

*Licencia: GNU AGPL v3. Copyright © 2026 Anna Tchijova.*  
*Documentación generada por Batch API de Moonshot (Kimi K2.6) como parte del colectivo IA VIGIA.*
