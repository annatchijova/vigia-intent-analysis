# VIGÍA — Главный индекс академической документации
<!-- Обновлено: 2026-06-26 | Корпус: 193 модуля | Языки: EN / ES / RU / ZH -->
<!-- Сгенерировано: Moonshot Kimi K2.6 Batch API | Аудит: ИИ-коллектив VIGÍA -->
<!-- Испанская версия: ACADEMIC_DOCS_MASTER_INDEX.md | Английская: ACADEMIC_DOCS_MASTER_INDEX_EN.md -->

> **Целевая аудитория:** Судебно-медицинские исследователи, технические судьи SANS, рецензенты по стандарту Даубер.  
> Каждый документ охватывает модуль на 4 языках с техническим глоссарием и научным примечанием,  
> раскрывающим семиотику Пирса, теорию сверхинтерпретации Эко и максимы Грайса как детерминированные,  
> фальсифицируемые вычислительные конструкции.  
> Все документы расположены в `docs/academic/` репозитория.

---

## Быстрая навигация

| Раздел | Модули | Описание |
|--------|--------|----------|
| [01 — Ядро системы](#01--ядро-системы-core) | 49 | Центральный конвейер, семиотика, сигналы, калибровка |
| [02 — Инструменты анализа](#02--инструменты-анализа-tools) | 39 | CAIE, состязательный NLP, MITRE, паттерны, EML |
| [03 — Форензика SIFT](#03--форензика-sift) | 16 | MFT, prefetch, shellbag, реестр, сеть, браузер, память |
| [04 — Специализированная форензика](#04--специализированная-форензика-forensics) | 10 | PDF, PKI, RFC3161, зрение, цепочка хранения |
| [05 — Механизм вывода](#05--механизм-вывода-inference) | 9 | Абдуктивное рассуждение, поведенческий отпечаток, детерминизм |
| [06 — Конвейер и оркестрация](#06--конвейер-и-оркестрация) | 6 | Бандл, отчёт, мост SIFT, реестр доказательств |
| [07 — Безопасность и песочница](#07--безопасность-и-песочница-security) | 5 | Песочница, форензическая безопасность, усиление |
| [08 — Управление и риски](#08--управление-и-риски-governance) | 4 | Уровни доверия, слой рисков, трассируемость |
| [09 — Корневой модуль VIGÍA](#09--корневой-модуль-vigía) | 10 | API, CLI, конфиг, namespace shim, ядро |
| [10 — Операционные скрипты](#10--операционные-скрипты-scripts) | 21 | Утилиты запуска, конвертация, анализ |
| [11 — Второстепенные специализированные модули](#11--второстепенные-специализированные-модули) | 12 | Абдукция, вердикт, паттерны, темпоральность, модели |

---

## 01 — Ядро системы (`core/`)

> Содержит 25% корпуса. Эти модули **не подлежат слиянию** — каждый является критическим  
> узлом в конвейере, соответствующем стандарту Даубера. Детерминированная целочисленная  
> оценка; без операций с плавающей точкой.

### 01.1 — Семиотическое обнаружение и определение намерений

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/forensic_technical_detector.py` | [forensic_technical_detector_academic.md](core/forensic_technical_detector_academic.md) | EN/ES/RU/ZH |
| `vigia/core/vigia_core_forensic_technical_detector.py` | [vigia_core_forensic_technical_detector_academic.md](core/vigia_core_forensic_technical_detector_academic.md) | EN/ES/RU/ZH |
| `vigia/core/semiotic_detector.py` | [94fbce3d_academic.md](unclassified/94fbce3d_academic.md) | EN/ES/RU/ZH |
| `vigia/core/semiotic_detector_v2.py` | [semiotic_detector_v2_academic.md](core/semiotic_detector_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/core/vigia_core_semiotic_detector.py` | [vigia_core_semiotic_detector_academic.md](core/vigia_core_semiotic_detector_academic.md) | EN/ES/RU/ZH |
| `vigia/core/narrative_auditor.py` | [narrative_auditor_academic.md](core/narrative_auditor_academic.md) | EN/ES/RU/ZH |
| `vigia/core/peirceplanner_bounded.py` | [673c2ea3_academic.md](unclassified/673c2ea3_academic.md) | EN/ES/RU/ZH |
| `vigia/core/abductive_intent_engine.py` | [abductive_intent_engine_academic.md](core/abductive_intent_engine_academic.md) | EN/ES/RU/ZH |
| `vigia/abductive_intent_engine.py` | [abductive_intent_engine_academic.md](root/abductive_intent_engine_academic.md) | EN/ES/RU/ZH |
| `vigia/core/carnegie_education_detector.py` | [carnegie_education_detector_academic.md](core/carnegie_education_detector_academic.md) | EN ⚠ |

### 01.2 — Сигналы, маппинг и качество

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/signal_mapper.py` | [signal_mapper_academic.md](core/signal_mapper_academic.md) | EN/ES/RU/ZH |
| `vigia/core/signal_quality_gate.py` | [signal_quality_gate_academic.md](core/signal_quality_gate_academic.md) | EN/ES/RU/ZH |
| `vigia/core/signal_contract.py` | [signal_contract_academic.md](core/signal_contract_academic.md) | EN/ES/RU/ZH |
| `vigia/core/advanced_signal_router.py` | [advanced_signal_router_academic.md](core/advanced_signal_router_academic.md) | EN/ES/RU/ZH |
| `vigia/core/normalization_layer.py` | [normalization_layer_academic.md](core/normalization_layer_academic.md) | EN/ES/RU/ZH |
| `vigia/signal_quality_gate.py` | [signal_quality_gate_academic.md](root/signal_quality_gate_academic.md) | EN/ES/RU/ZH |

### 01.3 — Калибровка и отношение правдоподобия

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/likelihood_engine.py` | [likelihood_engine_academic.md](core/likelihood_engine_academic.md) | EN/ES/RU/ZH |
| `vigia/core/likelihood_ratio.py` | [likelihood_ratio_academic.md](core/likelihood_ratio_academic.md) | EN/ES/RU/ZH |
| `vigia/core/lr_calibration.py` | [lr_calibration_academic.md](core/lr_calibration_academic.md) | EN/ES/RU/ZH |
| `vigia/core/fit_calibration.py` | [65ccdf43_academic.md](unclassified/65ccdf43_academic.md) | EN/ES/RU/ZH |
| `vigia/core/ebs_v1.py` | [ebs_v1_academic.md](core/ebs_v1_academic.md) | EN/ES/RU/ZH |
| `vigia/models/ebs.py` | [chain_academic.md](core/chain_academic.md) | EN/ES/RU/ZH |
| `engine/likelihood_engine.py` | [0c4cec60_academic.md](unclassified/0c4cec60_academic.md) | EN/ES/RU/ZH |

### 01.4 — Конвейер, целостность и цепочка хранения доказательств

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/pipeline.py` | [pipeline_academic.md](core/pipeline_academic.md) | EN/ES/RU/ZH |
| `vigia/core/canonicalize.py` | [canonicalize_academic.md](core/canonicalize_academic.md) | EN/ES/RU/ZH |
| `vigia/core/chain_of_custody.py` | [chain_of_custody_academic.md](core/chain_of_custody_academic.md) | EN/ES/RU ⚠ |
| `vigia/core/integrity_constraints.py` | [integrity_constraints_academic.md](core/integrity_constraints_academic.md) | EN/ES/RU/ZH |
| `vigia/core/audit_action.py` | [audit_action_academic.md](core/audit_action_academic.md) | EN/ES/RU/ZH |
| `vigia/core/execution_logger.py` | [execution_logger_academic.md](core/execution_logger_academic.md) | EN/ES/RU/ZH |
| `vigia/core/bundle_builder.py` | [5d49495e_academic.md](unclassified/5d49495e_academic.md) | EN ⚠ |

### 01.5 — Доказательства, доверие и принятие решений

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/evidence_aggregator.py` | [evidence_aggregator_academic.md](core/evidence_aggregator_academic.md) | EN/ES/RU/ZH |
| `vigia/core/trust_fusion.py` | [trust_fusion_academic.md](core/trust_fusion_academic.md) | EN/ES/RU/ZH |
| `vigia/core/trust_levels.py` | [trust_levels_academic.md](core/trust_levels_academic.md) | EN/ES/RU/ZH |
| `vigia/core/decision_layer.py` | [1ea10b1b_academic.md](unclassified/1ea10b1b_academic.md) | EN/ES/RU ⚠ |
| `vigia/core/dissent_report.py` | [dissent_report_academic.md](core/dissent_report_academic.md) | EN/ES/RU/ZH |
| `vigia/core/explainable_governance.py` | [explainable_governance_academic.md](core/explainable_governance_academic.md) | EN ⚠ |
| `vigia/core/compare_baseline.py` | [compare_baseline_academic.md](core/compare_baseline_academic.md) | EN/ES/RU/ZH |

### 01.6 — Рассуждение и причинность

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/causal_closure.py` | [causal_closure_academic.md](core/causal_closure_academic.md) | EN/ES/RU/ZH |
| `vigia/core/entanglement.py` | [entanglement_academic.md](core/entanglement_academic.md) | EN/ES/RU/ZH |
| `vigia/core/ockham_adversarial.py` | [adf95e94_academic.md](unclassified/adf95e94_academic.md) | EN/ES/RU/ZH |
| `vigia/core/graph_stability.py` | [graph_stability_academic.md](core/graph_stability_academic.md) | EN/ES/RU/ZH |
| `vigia/core/geopolitical_v2.py` | [geopolitical_v2_academic.md](core/geopolitical_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_adapter.py` | [forensic_adapter_academic.md](core/forensic_adapter_academic.md) | EN/ES/RU/ZH |

### 01.7 — Конфигурация, операционная безопасность и инфраструктура ядра

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/core/config_sentinel.py` | [config_sentinel_academic.md](core/config_sentinel_academic.md) | EN/ES/RU/ZH |
| `vigia/core/path_guard.py` | [path_guard_academic.md](core/path_guard_academic.md) | EN ⚠ |
| `vigia/core/risk_bounded_layer.py` | [777f8e26_academic.md](unclassified/777f8e26_academic.md) | EN/ES/RU/ZH |
| `vigia/core/shadow_mode.py` | [be1aca3f_academic.md](unclassified/be1aca3f_academic.md) | EN/ES/RU/ZH |
| `vigia/core/resource_optimizer.py` | [1566c038_academic.md](unclassified/1566c038_academic.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_db.py` | [forensic_db_academic.md](core/forensic_db_academic.md) | EN/ES/RU/ZH |
| `vigia/core/llm_backend.py` | [llm_backend_academic.md](core/llm_backend_academic.md) | EN/ES/RU/ZH |

---

## 02 — Инструменты анализа (`tools/`)

> Второй по величине раздел корпуса. Содержит кандидатов на тематическое слияние  
> (см. план интеграции). Модули CAIE **критические — не сливать**.

### 02.1 — Анализ перекрёстных артефактных несоответствий — CAIE (КРИТИЧНО — НЕ СЛИВАТЬ)

> CAIE является центральным детектором несоответствий. Его документация цитируется  
> напрямую в судебных отчётах. Слияние создаст неоднозначность в прослеживаемости доказательств.

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/caie.py` (v1) | [8c5d9283_academic.md](unclassified/8c5d9283_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/caie.py` (v2) | [ed0d4351_academic.md](unclassified/ed0d4351_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/cross_artifact_resonance.py` | [cross_artifact_resonance_academic.md](tools/cross_artifact_resonance_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_locality.py` | [entropy_locality_academic.md](tools/entropy_locality_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_kernel.py` | [44542c22_academic.md](unclassified/44542c22_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/document_integrity.py` | [document_integrity_academic.md](tools/document_integrity_academic.md) | EN/ES/RU/ZH |

### 02.2 — Состязательный NLP и тестирование мутаций

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/adversarial_nlp.py` | [ca997fe5_academic.md](unclassified/ca997fe5_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_robustness.py` | [8ffefb83_academic.md](unclassified/8ffefb83_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_mutation_suite.py` | [9624f888_academic.md](unclassified/9624f888_academic.md) | EN/ES/RU/ZH |
| `vigia/patterns/adversarial_silence.py` | [b5692c6d_academic.md](unclassified/b5692c6d_academic.md) | EN/ES/RU/ZH |

### 02.3 — MITRE ATT&CK и паттерны

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/mitre_mapping.py` | [mitre_mapping_academic.md](tools/mitre_mapping_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/mitre_clustering.py` | [8fcbd5bb_academic.md](unclassified/8fcbd5bb_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/pattern_detector.py` | [pattern_detector_academic.md](tools/pattern_detector_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/picerl_mapping.py` | [picerl_mapping_academic.md](tools/picerl_mapping_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/nlp_constants.py` | [nlp_constants_academic.md](tools/nlp_constants_academic.md) | EN/ES/RU/ZH |

### 02.4 — Форензика электронной почты и коммуникаций (EML)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/eml_gci.py` | [eml_gci_academic.md](tools/eml_gci_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/eml_symbolic.py` | [eml_symbolic_academic.md](tools/eml_symbolic_academic.md) | EN/ES/RU/ZH |

### 02.5 — Сигналы, адаптеры и темпоральность

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/signal_adapter.py` | [signal_adapter_academic.md](tools/signal_adapter_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/signal_contract.py` | [signal_contract_academic.md](tools/signal_contract_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/temporal_drift.py` | [temporal_drift_academic.md](tools/temporal_drift_academic.md) | EN/ES/RU/ZH |
| `vigia/temporal/coherence_validator.py` | [40950455_academic.md](unclassified/40950455_academic.md) | EN/ES/RU/ZH |

### 02.6 — Вывод и поведенческий отпечаток (`tools/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/abductive_intent_engine.py` | [fd5b51d8_academic.md](unclassified/fd5b51d8_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/behavioral_fingerprint.py` | [8517382b_academic.md](unclassified/8517382b_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/metabolic_profiler.py` | [metabolic_profiler_academic.md](tools/metabolic_profiler_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/visible_variables.py` | [visible_variables_academic.md](tools/visible_variables_academic.md) | EN/ES/RU/ZH |

### 02.7 — Геополитический контекст

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/geopolitical.py` | [geopolitical_academic.md](tools/geopolitical_academic.md) | EN/ES/RU/ZH |

### 02.8 — Калибровка и база знаний (`tools/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/build_calibration_dataset.py` | [build_calibration_dataset_academic.md](tools/build_calibration_dataset_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/generate_calibration.py` | [generate_calibration_academic.md](tools/generate_calibration_academic.md) | ZH only ⚠ |
| `vigia/tools/init_patterns_db.py` | [init_patterns_db_academic.md](tools/init_patterns_db_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/forensic_db.py` | [f780b9eb_academic.md](unclassified/f780b9eb_academic.md) | EN/ES/RU/ZH |

### 02.9 — Адаптеры дел и планирование

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/tools/vigia_case_adapter.py` | [vigia_case_adapter_academic.md](tools/vigia_case_adapter_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_entanglement.py` | [vigia_entanglement_academic.md](tools/vigia_entanglement_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner.py` | [vigia_planner_academic.md](tools/vigia_planner_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner_GIT.py` | [vigia_planner_GIT_academic.md](tools/vigia_planner_GIT_academic.md) | — |
| `vigia/tools/vigia_sift_bridge.py` | [3f495b70_academic.md](unclassified/3f495b70_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vision_audit.py` | [vision_audit_academic.md](tools/vision_audit_academic.md) | EN/ES/RU/ZH |

---

## 03 — Форензика SIFT (`sift/`)

> Модули прямой интеграции с SANS SIFT Workstation. Каждый модуль соответствует  
> независимой категории судебных доказательств, допустимых по FRE 901.  
> Хранятся раздельно по форензической специфике — один модуль документирует один тип артефакта.

| Модуль Python | Документ | Языки | Форензический артефакт |
|---------------|-----------|-------|------------------------|
| `vigia/sift/sift_orchestrator.py` | [e782beeb_academic.md](unclassified/e782beeb_academic.md) | EN/ES/RU/ZH | Главный оркестратор |
| `vigia/sift/unified_timeline_engine.py` | [5a035ab4_academic.md](unclassified/5a035ab4_academic.md) | EN/ES/RU/ZH | Единая временная шкала |
| `vigia/sift/mft_timeline_analyzer.py` | [mft_timeline_analyzer_academic.md](sift/mft_timeline_analyzer_academic.md) | EN/ES/RU/ZH | MFT / $MFT |
| `vigia/sift/registry_timeline_reconstructor.py` | [71679681_academic.md](unclassified/71679681_academic.md) | EN/ES/RU/ZH | Реестр Windows |
| `vigia/sift/prefetch_analyzer.py` | [prefetch_analyzer_academic.md](sift/prefetch_analyzer_academic.md) | EN/ES/RU/ZH | Prefetch / WinPrefetch |
| `vigia/sift/shellbag_analyzer.py` | [shellbag_analyzer_academic.md](sift/shellbag_analyzer_academic.md) | EN/ES/RU/ZH | ShellBags |
| `vigia/sift/amcache_shimcache.py` | [amcache_shimcache_academic.md](sift/amcache_shimcache_academic.md) | EN/ES/RU/ZH | AmCache / ShimCache |
| `vigia/sift/usb_device_tracker.py` | [usb_device_tracker_academic.md](sift/usb_device_tracker_academic.md) | EN/ES/RU/ZH | USB / SetupAPI |
| `vigia/sift/event_log_correlator.py` | [fda3319e_academic.md](unclassified/fda3319e_academic.md) | EN/ES/RU/ZH | Журналы событий Windows |
| `vigia/sift/disk_forensics.py` | [03834f85_academic.md](unclassified/03834f85_academic.md) | EN/ES/RU/ZH | Диск / Разделы |
| `vigia/sift/memory_forensics.py` | [memory_forensics_academic.md](sift/memory_forensics_academic.md) | EN/ES/RU/ZH | Volatility / ОЗУ |
| `vigia/sift/network_forensics.py` | [network_forensics_academic.md](sift/network_forensics_academic.md) | EN/ES/RU/ZH | PCAP / NetFlow |
| `vigia/sift/browser_forensics.py` | [350c8eab_academic.md](unclassified/350c8eab_academic.md) | EN/ES/RU/ZH | Артефакты браузера |
| `vigia/sift/ioc_manager.py` | [ioc_manager_academic.md](sift/ioc_manager_academic.md) | EN/ES/RU/ZH | IOC / Индикаторы |
| `vigia/sift/sans_phase.py` | [6f157b07_academic.md](unclassified/6f157b07_academic.md) | EN/ES/RU/ZH | Фазы SANS PICERL |
| `vigia/sift/_math_utils.py` | [_math_utils_academic.md](sift/_math_utils_academic.md) | EN/ES/RU/ZH | Детерминированные утилиты |

---

## 04 — Специализированная форензика (`forensics/`)

> Модули высокой технической специфики. **Не сливать** — каждый допустим  
> независимо как доказательство по стандарту Даубера. Модули RFC 3161 и PKI  
> реализуют международные стандарты и должны оставаться строго изолированными.

| Модуль Python | Документ | Языки | Стандарт |
|---------------|-----------|-------|----------|
| `vigia/forensics/temporal_forensics.py` | [temporal_forensics_academic.md](forensics/temporal_forensics_academic.md) | EN/ES/RU/ZH | Временны́е метки / MACB |
| `vigia/forensics/temporal_forensics_redteam.py` | [temporal_forensics_redteam_academic.md](forensics/temporal_forensics_redteam_academic.md) | EN/ES/RU/ZH | Временно́й red-team |
| `vigia/forensics/vision_audit.py` | [e0f29980_academic.md](unclassified/e0f29980_academic.md) | EN ⚠ | Визуальный аудит |
| `vigia/forensics/vision_audit_final.py` | [b2c8b2e5_academic.md](unclassified/b2c8b2e5_academic.md) | EN/ES/RU/ZH | Финальная визуальная форензика |
| `vigia/forensics/forensic_reporter.py` | [2640bfa6_academic.md](unclassified/2640bfa6_academic.md) | EN/ES/RU/ZH | Форензическая отчётность |
| `vigia/forensics/pdf_dual_parser.py` | [pdf_dual_parser_academic.md](forensics/pdf_dual_parser_academic.md) | EN/ES/RU/ZH | Двойной анализ PDF |
| `vigia/forensics/pki_tools.py` | [3c13ec36_academic.md](unclassified/3c13ec36_academic.md) | EN/ES/RU/ZH | PKI / Сертификаты |
| `vigia/forensics/rfc3161_chain.py` | [rfc3161_chain_academic.md](forensics/rfc3161_chain_academic.md) | EN/ES/RU/ZH | Временно́й штамп RFC 3161 |
| `vigia/forensics/vigia_chain_of_custody.py` | [vigia_chain_of_custody_academic.md](forensics/vigia_chain_of_custody_academic.md) | EN/ES/RU/ZH | Цепочка хранения доказательств |

---

## 05 — Механизм вывода (`inference/`)

> Реализует три пирсовских момента: Первичность (абдукция), Вторичность  
> (верификация), Третичность (синтез). Все вычисления детерминированы —  
> `decimal.Decimal` с точностью 28, без операций с плавающей точкой.

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/inference/abductive_reasoner.py` | [abductive_reasoner_academic.md](inference/abductive_reasoner_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/abductive_reasoner_v2.py` | [abductive_reasoner_v2_academic.md](inference/abductive_reasoner_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/behavioral_fingerprint.py` | [747d525d_academic.md](unclassified/747d525d_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/case_pattern_library.py` | [5506a8ca_academic.md](unclassified/5506a8ca_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/check_determinism.py` | [check_determinism_academic.md](inference/check_determinism_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/cross_artifact_resonance.py` | [cross_artifact_resonance_academic.md](inference/cross_artifact_resonance_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/metabolic_profiler.py` | [metabolic_profiler_academic.md](inference/metabolic_profiler_academic.md) | EN/ES/RU/ZH |
| `vigia/memory/case_pattern_library.py` | [be71e68a_academic.md](unclassified/be71e68a_academic.md) | EN/ES/RU/ZH |
| `vigia/collapse_decision.py` | [7b5f476a_academic.md](unclassified/7b5f476a_academic.md) | EN ⚠ |

---

## 06 — Конвейер и оркестрация (`pipeline/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/pipeline/pipeline.py` | [pipeline_academic.md](pipeline/pipeline_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/evidence_bundle.py` | [evidence_bundle_academic.md](pipeline/evidence_bundle_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_builder.py` | [10a8df9f_academic.md](unclassified/10a8df9f_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_exporter.py` | [report_exporter_academic.md](pipeline/report_exporter_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/security_evidence_registry.py` | [security_evidence_registry_academic.md](pipeline/security_evidence_registry_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/vigia_integration_bridge.py` | [db45f26c_academic.md](unclassified/db45f26c_academic.md) | EN/ES/RU/ZH |

---

## 07 — Безопасность и песочница (`security/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/security/sandbox.py` | [sandbox_academic.md](security/sandbox_academic.md) | EN/ES/RU/ZH |
| `vigia/sandbox.py` | [sandbox_academic.md](root/sandbox_academic.md) | EN/ES/RU/ZH |
| `vigia/security/security.py` | [security_academic.md](security/security_academic.md) | EN/ES/RU/ZH |
| `vigia/security/vigia_seguridad.py` | [vigia_seguridad_academic.md](security/vigia_seguridad_academic.md) | EN/ES/RU/ZH |
| `vigia/security.py` | [security_academic.md](root/security_academic.md) | EN/ES/RU/ZH |

---

## 08 — Управление и риски (`governance/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/governance/trust_levels_p0.py` | [trust_levels_p0_academic.md](governance/trust_levels_p0_academic.md) | EN/ES/RU/ZH |
| `vigia/governance/risk_bounded_layer_v2.py` | [risk_bounded_layer_v2_academic.md](governance/risk_bounded_layer_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/verdict/quadripartite.py` | [04d02947_academic.md](unclassified/04d02947_academic.md) | EN/ES/RU/ZH |
| `vigia/utils/path_guard.py` | [8d40e5b1_academic.md](unclassified/8d40e5b1_academic.md) | EN/ES/RU/ZH |

---

## 09 — Корневой модуль VIGÍA (`vigia/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/vigia_core.py` | [vigia_core_academic.md](root/vigia_core_academic.md) | EN/ES/RU/ZH |
| `vigia/vigia_api.py` | [vigia_api_academic.md](root/vigia_api_academic.md) | EN/ES/RU/ZH |
| `vigia/cli.py` | [cli_academic.md](root/cli_academic.md) | EN/ES/RU/ZH |
| `vigia/config.py` | [config_academic.md](root/config_academic.md) | EN/ES/RU/ZH |
| `vigia/vigia_namespace_shim.py` | [14ba142e_academic.md](unclassified/14ba142e_academic.md) | EN/ES/RU/ZH |
| `vigia/llm_backend_v2.py` | [llm_backend_v2_academic.md](root/llm_backend_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/vigia_sift_bridge.py` | [vigia_sift_bridge_academic.md](root/vigia_sift_bridge_academic.md) | EN/ES/RU/ZH |
| `vigia/vigia_sift_bridge_final.py` | [vigia_sift_bridge_final_academic.md](root/vigia_sift_bridge_final_academic.md) | EN/ES/RU/ZH |
| `vigia/vigia_command_center.py` | [vigia_command_center_academic.md](root/vigia_command_center_academic.md) | EN/ES/RU/ZH |
| `vigia/phonetic_loader.py` | [phonetic_loader_academic.md](root/phonetic_loader_academic.md) | EN/ES/RU/ZH |

---

## 10 — Операционные скрипты (`scripts/`)

### Выполнение и диагностика

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `scripts/run_vigia_full.py` | [2c0d7aea_academic.md](unclassified/2c0d7aea_academic.md) | EN/ES/RU/ZH |
| `scripts/run_case.py` | [run_case_academic.md](scripts/run_case_academic.md) | EN/ES/RU/ZH |
| `scripts/run_demo.py` | [run_demo_academic.md](scripts/run_demo_academic.md) | EN ⚠ |
| `scripts/pre_release_check.py` | [pre_release_check_academic.md](scripts/pre_release_check_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/compare_runs.py` | [8cf3f33e_academic.md](unclassified/8cf3f33e_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/evaluate_detector.py` | [c8cb7042_academic.md](unclassified/c8cb7042_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/consolidate_cases.py` | [0cf21887_academic.md](unclassified/0cf21887_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/top_breaking_phrases.py` | [cda1c372_academic.md](unclassified/cda1c372_academic.md) | EN/ES/RU/ZH |

### Конвертация и обслуживание

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `scripts/convert_break_cases.py` | [convert_break_cases_academic.md](scripts/convert_break_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/convert_legacy_cases.py` | [convert_legacy_cases_academic.md](scripts/convert_legacy_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/convert_md_cases.py` | [convert_md_cases_academic.md](scripts/convert_md_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/export_patterns.py` | [export_patterns_academic.md](scripts/export_patterns_academic.md) | EN/ES/RU/ZH |
| `scripts/fix_inits.py` | [fix_inits_academic.md](scripts/fix_inits_academic.md) | ZH only ⚠ |
| `scripts/fix_security_init.py` | [__init___academic.md](security/__init___academic.md) | EN/ES/RU/ZH |
| `scripts/vigia_mass_refactor.py` | [vigia_mass_refactor_academic.md](scripts/vigia_mass_refactor_academic.md) | EN/ES ⚠ |
| `scripts/vigia_patch_valkyrie.py` | [2989e9bd_academic.md](unclassified/2989e9bd_academic.md) | EN/ES ⚠ |
| `recalibrate_cases.py` | [13bb704b_academic.md](unclassified/13bb704b_academic.md) | EN/ES/RU/ZH |
| `apply_caie_patch.py` | [442419c2_academic.md](unclassified/442419c2_academic.md) | EN/ES/RU/ZH |
| `cases/demo_case.py` | [demo_case_academic.md](scripts/demo_case_academic.md) | EN/ES/RU/ZH |

---

## 11 — Второстепенные специализированные модули

### Расширенная абдукция (`abduction/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/abduction/hypothesis_lineage.py` | [hypothesis_lineage_academic.md](specialized/hypothesis_lineage_academic.md) | EN/ES/RU/ZH |
| `vigia/abduction/vigia_artifact_graph.py` | [3254c6ec_academic.md](unclassified/3254c6ec_academic.md) | EN/ES ⚠ |
| `vigia/abduction/vigia_counter_fact.py` | [8f6f7187_academic.md](unclassified/8f6f7187_academic.md) | EN ⚠ |

### Смягчение последствий и действия (`action/`)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `vigia/action/vigia_mitigation_planner.py` | [vigia_mitigation_planner_academic.md](specialized/vigia_mitigation_planner_academic.md) | EN/ES/RU/ZH |

### Состязательное тестирование

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `run_adversarial_tests.py` | [8ebd0d52_academic.md](unclassified/8ebd0d52_academic.md) | EN/ES/RU/ZH |

---

## Документы с неполным языковым охватом

Следующие документы требуют нового запуска Batch API для достижения полного покрытия EN/ES/RU/ZH.  
Выполните `python3 docs/academic/refresh_index_status.py` для обновления статуса языков во всех таблицах.

---

## 12 — Дополнительные модули (архитектурно не классифицированы)

| Модуль Python | Документ | Языки |
|---------------|-----------|-------|
| `pipeline_adapter.py` (канонический адаптер конвейера) | [131c3f89_academic.md](unclassified/131c3f89_academic.md) | EN/ES/RU/ZH |
| `vigia_sift_bridge_patch.py` (BRIDGE_PATCH_FINAL) | [19008897_academic.md](unclassified/19008897_academic.md) | EN/ES/RU/ZH |
| `document_integrity.py` (v2, PDF/DOCX) | [1c52745b_academic.md](unclassified/1c52745b_academic.md) | EN/ES/RU/ZH |
| `vigia_namespace_shim.py` (заглушка совместимости) | [2d6dff4d_academic.md](unclassified/2d6dff4d_academic.md) | EN/ES/RU/ZH |
| `ci_gate.py` | [2ddb875b_academic.md](unclassified/2ddb875b_academic.md) | EN/ES/RU/ZH |
| `vigia_batch_postprocess.py` | [43e2ca4a_academic.md](unclassified/43e2ca4a_academic.md) | EN/ES/RU/ZH |
| `run_calibration.py` | [495820ba_academic.md](unclassified/495820ba_academic.md) | EN/ES/RU/ZH |
| `pattern_repository_init.py` (FPRI) | [4cffb019_academic.md](unclassified/4cffb019_academic.md) | EN/ES/RU/ZH |
| `vigia_server.py` | [59fb9f58_academic.md](unclassified/59fb9f58_academic.md) | EN/ES/RU/ZH |
| `run_stress_tests.py` | [5f1c653e_academic.md](unclassified/5f1c653e_academic.md) | EN/ES/RU/ZH |
| `evidence_narrative_generator.py` | [68e0e743_academic.md](unclassified/68e0e743_academic.md) | EN/ES/RU/ZH |
| `vigia_scorer.py` (вариант B) | [69cb51de_academic.md](unclassified/69cb51de_academic.md) | EN/ES/RU/ZH |
| `vigia_batch_doc_generator.py` | [779b4236_academic.md](unclassified/779b4236_academic.md) | EN/ES/RU/ZH |
| `report_exporter_v2.py` | [8d0b9079_academic.md](unclassified/8d0b9079_academic.md) | EN/ES/RU/ZH |
| `verify_ebs_v1.py` (независимый верификатор EBS) | [9810a97e_academic.md](unclassified/9810a97e_academic.md) | EN/ES/RU/ZH |
| `recommendation_engine_v3.1.py` | [adc5d097_academic.md](unclassified/adc5d097_academic.md) | EN/ES/RU/ZH |
| `negation_handler.py` | [b8bde3c7_academic.md](unclassified/b8bde3c7_academic.md) | EN/ES/RU/ZH |
| `generate_execution_log.py` | [e6461489_academic.md](unclassified/e6461489_academic.md) | EN/ES/RU/ZH |
| `convert_synthetic_cases.py` | [e74f0754_academic.md](unclassified/e74f0754_academic.md) | EN/ES/RU/ZH |
| `generate_release_bundle.py` | [ebd2829f_academic.md](unclassified/ebd2829f_academic.md) | EN/ES/RU/ZH |
| `generate_report.py` | [ec80b958_academic.md](unclassified/ec80b958_academic.md) | EN/ES/RU/ZH |
| `vigia_api.py` (вариант — упрощённый интерфейс) | [ed735669_academic.md](unclassified/ed735669_academic.md) | EN/ES/RU/ZH |
| `vigia_scorer.py` (вариант C) | [ed8c1a84_academic.md](unclassified/ed8c1a84_academic.md) | EN/ES/RU/ZH |
| `sanitize_judicial.py` | [f8ae3e67_academic.md](unclassified/f8ae3e67_academic.md) | EN/ES/RU/ZH |

---

## Дублирующиеся модули — ожидают синхронизации с Git

> **Не сливать эти пары до разрешения кризиса синхронизации Git/локального репозитория.**  
> Слияние до согласования путей приведёт к повреждению форензической записи.

| Модуль | Конфликтующие хеши | Конфликт пути |
|--------|--------------------|---------------|
| `caie.py` | `8c5d9283`, `ed0d4351` | Одинаковый путь, разное содержимое |
| `abductive_intent_engine.py` | `f14e91cc`, `9cf0944e`, `fd5b51d8` | `vigia/core/`, `vigia/`, `vigia/tools/` |
| `vision_audit.py` | `e0f29980`, `b2c8b2e5`, `c12c7450` | `vigia/forensics/` ×2, `vigia/tools/` |
| `behavioral_fingerprint.py` | `747d525d`, `8517382b` | `vigia/inference/` vs `vigia/tools/` |
| `sandbox.py` | `2042863e`, `845ea393` | `vigia/security/` vs корень `vigia/` |
| `semiotic_detector.py` | `94fbce3d`, `b32a18e2`, `5dac09b1` | Три варианта пути |

---

## Статистика корпуса

| Метрика | Значение |
|---------|----------|
| Всего документов | 193 |
| Полное покрытие EN/ES/RU/ZH | ~160 документов (~83%) |
| Только EN | 8 документов |
| Только ZH | 2 документа |
| Частичное покрытие (EN/ES или EN/ES/RU) | 8 документов |
| Наибольший раздел | `core/` (49 документов) |
| Наиболее критичный для интеграции SIFT | `sift/` (16 документов) |
| Подтверждённые ошибки лицензии (Apache 2.0) | 2 документа — `fix_license_academic_docs.py` |
| Дублирующиеся модули в ожидании разрешения | 6 пар / 13 документов |

> ⚠ — документ имеет неполное языковое покрытие; рекомендуется перегенерация перед финальной подачей.

---

*Лицензия: Apache License, версия 2.0. Copyright © 2026 Anna Tchijova.*  
*Документация сгенерирована Moonshot Kimi K2.6 Batch API в составе ИИ-коллектива VIGÍA.*  
*(Claude, Gemini, DeepSeek, Qwen — аудиторы и рецензенты)*
