# VIGÍA — 学术文档主索引
<!-- 更新日期：2026-06-26 | 语料库：193 个模块 | 语言：EN / ES / RU / ZH -->
<!-- 由 Moonshot Kimi K2.6 批处理 API 生成 | 审核：VIGÍA AI 集体 -->
<!-- 西班牙语版本：ACADEMIC_DOCS_MASTER_INDEX.md | 英语版本：ACADEMIC_DOCS_MASTER_INDEX_EN.md -->

> **目标读者：** 法证研究人员、SANS 技术评委、Daubert 标准审核员。  
> 每份文档以 4 种语言涵盖对应模块，附技术术语表及科学注释，  
> 将皮尔斯符号学、艾柯过度解读理论和格赖斯准则阐释为确定性、可证伪的计算构型。  
> 所有文档位于仓库 `docs/academic/` 目录下。

---

## 快速导航

| 章节 | 模块数 | 描述 |
|------|--------|------|
| [01 — 系统核心](#01--系统核心-core) | 49 | 中央流水线、符号学、信号、校准 |
| [02 — 分析工具](#02--分析工具-tools) | 39 | CAIE、对抗性 NLP、MITRE、模式、EML |
| [03 — SIFT 法证分析](#03--sift-法证分析) | 16 | MFT、预取、ShellBag、注册表、网络、浏览器、内存 |
| [04 — 专项法证](#04--专项法证-forensics) | 10 | PDF、PKI、RFC3161、视觉、证据保管链 |
| [05 — 推理引擎](#05--推理引擎-inference) | 9 | 溯因推理、行为指纹、确定性 |
| [06 — 流水线与编排](#06--流水线与编排) | 6 | 证据包、报告、SIFT 桥接、证据注册 |
| [07 — 安全与沙箱](#07--安全与沙箱-security) | 5 | 沙箱、法证安全、加固 |
| [08 — 治理与风险](#08--治理与风险-governance) | 4 | 信任等级、风险层、可追溯性 |
| [09 — VIGÍA 根模块](#09--vigía-根模块) | 10 | API、CLI、配置、命名空间兼容垫片、核心 |
| [10 — 操作脚本](#10--操作脚本-scripts) | 21 | 执行工具、转换、分析 |
| [11 — 次级专项模块](#11--次级专项模块) | 12 | 溯因推理、裁决、模式、时序、模型 |

---

## 01 — 系统核心 (`core/`)

> 占语料库 25%。这些模块**不得合并** — 每个均是符合 Daubert 标准的流水线中的关键节点。  
> 采用确定性整数评分；不使用浮点运算。

### 01.1 — 符号学检测与意图识别

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
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

### 01.2 — 信号、映射与质量

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/signal_mapper.py` | [signal_mapper_academic.md](core/signal_mapper_academic.md) | EN/ES/RU/ZH |
| `vigia/core/signal_quality_gate.py` | [signal_quality_gate_academic.md](core/signal_quality_gate_academic.md) | EN/ES/RU/ZH |
| `vigia/core/signal_contract.py` | [signal_contract_academic.md](core/signal_contract_academic.md) | EN/ES/RU/ZH |
| `vigia/core/advanced_signal_router.py` | [advanced_signal_router_academic.md](core/advanced_signal_router_academic.md) | EN/ES/RU/ZH |
| `vigia/core/normalization_layer.py` | [normalization_layer_academic.md](core/normalization_layer_academic.md) | EN/ES/RU/ZH |
| `vigia/signal_quality_gate.py` | [signal_quality_gate_academic.md](root/signal_quality_gate_academic.md) | EN/ES/RU/ZH |

### 01.3 — 校准与似然比

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/likelihood_engine.py` | [likelihood_engine_academic.md](core/likelihood_engine_academic.md) | EN/ES/RU/ZH |
| `vigia/core/likelihood_ratio.py` | [likelihood_ratio_academic.md](core/likelihood_ratio_academic.md) | EN/ES/RU/ZH |
| `vigia/core/lr_calibration.py` | [lr_calibration_academic.md](core/lr_calibration_academic.md) | EN/ES/RU/ZH |
| `vigia/core/fit_calibration.py` | [65ccdf43_academic.md](unclassified/65ccdf43_academic.md) | EN/ES/RU/ZH |
| `vigia/core/ebs_v1.py` | [ebs_v1_academic.md](core/ebs_v1_academic.md) | EN/ES/RU/ZH |
| `vigia/models/ebs.py` | [chain_academic.md](core/chain_academic.md) | EN/ES/RU/ZH |
| `engine/likelihood_engine.py` | [0c4cec60_academic.md](unclassified/0c4cec60_academic.md) | EN/ES/RU/ZH |

### 01.4 — 流水线、完整性与证据保管链

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/pipeline.py` | [pipeline_academic.md](core/pipeline_academic.md) | EN/ES/RU/ZH |
| `vigia/core/canonicalize.py` | [canonicalize_academic.md](core/canonicalize_academic.md) | EN/ES/RU/ZH |
| `vigia/core/chain_of_custody.py` | [chain_of_custody_academic.md](core/chain_of_custody_academic.md) | EN/ES/RU ⚠ |
| `vigia/core/integrity_constraints.py` | [integrity_constraints_academic.md](core/integrity_constraints_academic.md) | EN/ES/RU/ZH |
| `vigia/core/audit_action.py` | [audit_action_academic.md](core/audit_action_academic.md) | EN/ES/RU/ZH |
| `vigia/core/execution_logger.py` | [execution_logger_academic.md](core/execution_logger_academic.md) | EN/ES/RU/ZH |
| `vigia/core/bundle_builder.py` | [5d49495e_academic.md](unclassified/5d49495e_academic.md) | EN ⚠ |

### 01.5 — 证据、信任与决策

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/evidence_aggregator.py` | [evidence_aggregator_academic.md](core/evidence_aggregator_academic.md) | EN/ES/RU/ZH |
| `vigia/core/trust_fusion.py` | [trust_fusion_academic.md](core/trust_fusion_academic.md) | EN/ES/RU/ZH |
| `vigia/core/trust_levels.py` | [trust_levels_academic.md](core/trust_levels_academic.md) | EN/ES/RU/ZH |
| `vigia/core/decision_layer.py` | [1ea10b1b_academic.md](unclassified/1ea10b1b_academic.md) | EN/ES/RU ⚠ |
| `vigia/core/dissent_report.py` | [dissent_report_academic.md](core/dissent_report_academic.md) | EN/ES/RU/ZH |
| `vigia/core/explainable_governance.py` | [explainable_governance_academic.md](core/explainable_governance_academic.md) | EN ⚠ |
| `vigia/core/compare_baseline.py` | [compare_baseline_academic.md](core/compare_baseline_academic.md) | EN/ES/RU/ZH |

### 01.6 — 推理与因果性

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/causal_closure.py` | [causal_closure_academic.md](core/causal_closure_academic.md) | EN/ES/RU/ZH |
| `vigia/core/entanglement.py` | [entanglement_academic.md](core/entanglement_academic.md) | EN/ES/RU/ZH |
| `vigia/core/ockham_adversarial.py` | [adf95e94_academic.md](unclassified/adf95e94_academic.md) | EN/ES/RU/ZH |
| `vigia/core/graph_stability.py` | [graph_stability_academic.md](core/graph_stability_academic.md) | EN/ES/RU/ZH |
| `vigia/core/geopolitical_v2.py` | [geopolitical_v2_academic.md](core/geopolitical_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_adapter.py` | [forensic_adapter_academic.md](core/forensic_adapter_academic.md) | EN/ES/RU/ZH |

### 01.7 — 配置、操作安全与核心基础设施

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/core/config_sentinel.py` | [config_sentinel_academic.md](core/config_sentinel_academic.md) | EN/ES/RU/ZH |
| `vigia/core/path_guard.py` | [path_guard_academic.md](core/path_guard_academic.md) | EN ⚠ |
| `vigia/core/risk_bounded_layer.py` | [777f8e26_academic.md](unclassified/777f8e26_academic.md) | EN/ES/RU/ZH |
| `vigia/core/shadow_mode.py` | [be1aca3f_academic.md](unclassified/be1aca3f_academic.md) | EN/ES/RU/ZH |
| `vigia/core/resource_optimizer.py` | [1566c038_academic.md](unclassified/1566c038_academic.md) | EN/ES/RU/ZH |
| `vigia/core/forensic_db.py` | [forensic_db_academic.md](core/forensic_db_academic.md) | EN/ES/RU/ZH |
| `vigia/core/llm_backend.py` | [llm_backend_academic.md](core/llm_backend_academic.md) | EN/ES/RU/ZH |

---

## 02 — 分析工具 (`tools/`)

> 语料库第二大部分。包含主题合并候选项（参见集成计划）。  
> CAIE 模块**至关重要——不得合并**。

### 02.1 — 跨制品不一致性分析 — CAIE（关键——不得合并）

> CAIE 是核心不一致性检测器，其文档在司法报告中被直接引用。  
> 合并将导致证据可追溯性产生歧义。

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/caie.py` (v1) | [8c5d9283_academic.md](unclassified/8c5d9283_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/caie.py` (v2) | [ed0d4351_academic.md](unclassified/ed0d4351_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/cross_artifact_resonance.py` | [cross_artifact_resonance_academic.md](tools/cross_artifact_resonance_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_locality.py` | [entropy_locality_academic.md](tools/entropy_locality_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/entropy_kernel.py` | [44542c22_academic.md](unclassified/44542c22_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/document_integrity.py` | [document_integrity_academic.md](tools/document_integrity_academic.md) | EN/ES/RU/ZH |

### 02.2 — 对抗性 NLP 与变异测试

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/adversarial_nlp.py` | [ca997fe5_academic.md](unclassified/ca997fe5_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_robustness.py` | [8ffefb83_academic.md](unclassified/8ffefb83_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/adversarial_mutation_suite.py` | [9624f888_academic.md](unclassified/9624f888_academic.md) | EN/ES/RU/ZH |
| `vigia/patterns/adversarial_silence.py` | [b5692c6d_academic.md](unclassified/b5692c6d_academic.md) | EN/ES/RU/ZH |

### 02.3 — MITRE ATT&CK 与模式

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/mitre_mapping.py` | [mitre_mapping_academic.md](tools/mitre_mapping_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/mitre_clustering.py` | [8fcbd5bb_academic.md](unclassified/8fcbd5bb_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/pattern_detector.py` | [pattern_detector_academic.md](tools/pattern_detector_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/picerl_mapping.py` | [picerl_mapping_academic.md](tools/picerl_mapping_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/nlp_constants.py` | [nlp_constants_academic.md](tools/nlp_constants_academic.md) | EN/ES/RU/ZH |

### 02.4 — 电子邮件与通信法证（EML）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/eml_gci.py` | [eml_gci_academic.md](tools/eml_gci_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/eml_symbolic.py` | [eml_symbolic_academic.md](tools/eml_symbolic_academic.md) | EN/ES/RU/ZH |

### 02.5 — 信号、适配器与时序性

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/signal_adapter.py` | [signal_adapter_academic.md](tools/signal_adapter_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/signal_contract.py` | [signal_contract_academic.md](tools/signal_contract_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/temporal_drift.py` | [temporal_drift_academic.md](tools/temporal_drift_academic.md) | EN/ES/RU/ZH |
| `vigia/temporal/coherence_validator.py` | [40950455_academic.md](unclassified/40950455_academic.md) | EN/ES/RU/ZH |

### 02.6 — 推理与行为指纹（`tools/`）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/abductive_intent_engine.py` | [fd5b51d8_academic.md](unclassified/fd5b51d8_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/behavioral_fingerprint.py` | [8517382b_academic.md](unclassified/8517382b_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/metabolic_profiler.py` | [metabolic_profiler_academic.md](tools/metabolic_profiler_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/visible_variables.py` | [visible_variables_academic.md](tools/visible_variables_academic.md) | EN/ES/RU/ZH |

### 02.7 — 地缘政治背景

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/geopolitical.py` | [geopolitical_academic.md](tools/geopolitical_academic.md) | EN/ES/RU/ZH |

### 02.8 — 校准与知识库（`tools/`）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/build_calibration_dataset.py` | [build_calibration_dataset_academic.md](tools/build_calibration_dataset_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/generate_calibration.py` | [generate_calibration_academic.md](tools/generate_calibration_academic.md) | 仅 ZH ⚠ |
| `vigia/tools/init_patterns_db.py` | [init_patterns_db_academic.md](tools/init_patterns_db_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/forensic_db.py` | [f780b9eb_academic.md](unclassified/f780b9eb_academic.md) | EN/ES/RU/ZH |

### 02.9 — 案例适配器与规划

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/tools/vigia_case_adapter.py` | [vigia_case_adapter_academic.md](tools/vigia_case_adapter_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_entanglement.py` | [vigia_entanglement_academic.md](tools/vigia_entanglement_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner.py` | [vigia_planner_academic.md](tools/vigia_planner_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vigia_planner_GIT.py` | [vigia_planner_GIT_academic.md](tools/vigia_planner_GIT_academic.md) | — |
| `vigia/tools/vigia_sift_bridge.py` | [3f495b70_academic.md](unclassified/3f495b70_academic.md) | EN/ES/RU/ZH |
| `vigia/tools/vision_audit.py` | [vision_audit_academic.md](tools/vision_audit_academic.md) | EN/ES/RU/ZH |

---

## 03 — SIFT 法证分析 (`sift/`)

> 与 SANS SIFT 工作站直接集成的模块。每个模块对应一类在 FRE 901 下可独立采纳的法证证据。  
> 按法证专项性保持独立——单个模块仅记录单类制品。

| Python 模块 | 文档 | 语言 | 法证制品 |
|-------------|------|------|----------|
| `vigia/sift/sift_orchestrator.py` | [e782beeb_academic.md](unclassified/e782beeb_academic.md) | EN/ES/RU/ZH | 主编排器 |
| `vigia/sift/unified_timeline_engine.py` | [5a035ab4_academic.md](unclassified/5a035ab4_academic.md) | EN/ES/RU/ZH | 统一时间线 |
| `vigia/sift/mft_timeline_analyzer.py` | [mft_timeline_analyzer_academic.md](sift/mft_timeline_analyzer_academic.md) | EN/ES/RU/ZH | MFT / $MFT |
| `vigia/sift/registry_timeline_reconstructor.py` | [71679681_academic.md](unclassified/71679681_academic.md) | EN/ES/RU/ZH | Windows 注册表 |
| `vigia/sift/prefetch_analyzer.py` | [prefetch_analyzer_academic.md](sift/prefetch_analyzer_academic.md) | EN/ES/RU/ZH | Prefetch / WinPrefetch |
| `vigia/sift/shellbag_analyzer.py` | [shellbag_analyzer_academic.md](sift/shellbag_analyzer_academic.md) | EN/ES/RU/ZH | ShellBags |
| `vigia/sift/amcache_shimcache.py` | [amcache_shimcache_academic.md](sift/amcache_shimcache_academic.md) | EN/ES/RU/ZH | AmCache / ShimCache |
| `vigia/sift/usb_device_tracker.py` | [usb_device_tracker_academic.md](sift/usb_device_tracker_academic.md) | EN/ES/RU/ZH | USB / SetupAPI |
| `vigia/sift/event_log_correlator.py` | [fda3319e_academic.md](unclassified/fda3319e_academic.md) | EN/ES/RU/ZH | Windows 事件日志 |
| `vigia/sift/disk_forensics.py` | [03834f85_academic.md](unclassified/03834f85_academic.md) | EN/ES/RU/ZH | 磁盘 / 分区 |
| `vigia/sift/memory_forensics.py` | [memory_forensics_academic.md](sift/memory_forensics_academic.md) | EN/ES/RU/ZH | Volatility / 内存 |
| `vigia/sift/network_forensics.py` | [network_forensics_academic.md](sift/network_forensics_academic.md) | EN/ES/RU/ZH | PCAP / NetFlow |
| `vigia/sift/browser_forensics.py` | [350c8eab_academic.md](unclassified/350c8eab_academic.md) | EN/ES/RU/ZH | 浏览器制品 |
| `vigia/sift/ioc_manager.py` | [ioc_manager_academic.md](sift/ioc_manager_academic.md) | EN/ES/RU/ZH | IOC / 指标 |
| `vigia/sift/sans_phase.py` | [6f157b07_academic.md](unclassified/6f157b07_academic.md) | EN/ES/RU/ZH | SANS PICERL 阶段 |
| `vigia/sift/_math_utils.py` | [_math_utils_academic.md](sift/_math_utils_academic.md) | EN/ES/RU/ZH | 确定性工具函数 |

---

## 04 — 专项法证 (`forensics/`)

> 高度技术专项模块。**不得合并** — 每个均可在 Daubert 标准下作为独立证据。  
> RFC 3161 与 PKI 模块实现国际标准，必须严格隔离。

| Python 模块 | 文档 | 语言 | 标准 |
|-------------|------|------|------|
| `vigia/forensics/temporal_forensics.py` | [temporal_forensics_academic.md](forensics/temporal_forensics_academic.md) | EN/ES/RU/ZH | 时间戳 / MACB |
| `vigia/forensics/temporal_forensics_redteam.py` | [temporal_forensics_redteam_academic.md](forensics/temporal_forensics_redteam_academic.md) | EN/ES/RU/ZH | 时序红队 |
| `vigia/forensics/vision_audit.py` | [e0f29980_academic.md](unclassified/e0f29980_academic.md) | 仅 EN ⚠ | 视觉审计 |
| `vigia/forensics/vision_audit_final.py` | [b2c8b2e5_academic.md](unclassified/b2c8b2e5_academic.md) | EN/ES/RU/ZH | 最终视觉法证 |
| `vigia/forensics/forensic_reporter.py` | [2640bfa6_academic.md](unclassified/2640bfa6_academic.md) | EN/ES/RU/ZH | 法证报告 |
| `vigia/forensics/pdf_dual_parser.py` | [pdf_dual_parser_academic.md](forensics/pdf_dual_parser_academic.md) | EN/ES/RU/ZH | PDF 双重分析 |
| `vigia/forensics/pki_tools.py` | [3c13ec36_academic.md](unclassified/3c13ec36_academic.md) | EN/ES/RU/ZH | PKI / 证书 |
| `vigia/forensics/rfc3161_chain.py` | [rfc3161_chain_academic.md](forensics/rfc3161_chain_academic.md) | EN/ES/RU/ZH | RFC 3161 时间戳 |
| `vigia/forensics/vigia_chain_of_custody.py` | [vigia_chain_of_custody_academic.md](forensics/vigia_chain_of_custody_academic.md) | EN/ES/RU/ZH | 证据保管链 |

---

## 05 — 推理引擎 (`inference/`)

> 实现皮尔斯三元时刻：第一性（溯因推理）、第二性（验证）、第三性（综合）。  
> 所有计算均为确定性——`decimal.Decimal` 精度 28，不使用浮点数。

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/inference/abductive_reasoner.py` | [abductive_reasoner_academic.md](inference/abductive_reasoner_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/abductive_reasoner_v2.py` | [abductive_reasoner_v2_academic.md](inference/abductive_reasoner_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/behavioral_fingerprint.py` | [747d525d_academic.md](unclassified/747d525d_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/case_pattern_library.py` | [5506a8ca_academic.md](unclassified/5506a8ca_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/check_determinism.py` | [check_determinism_academic.md](inference/check_determinism_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/cross_artifact_resonance.py` | [cross_artifact_resonance_academic.md](inference/cross_artifact_resonance_academic.md) | EN/ES/RU/ZH |
| `vigia/inference/metabolic_profiler.py` | [metabolic_profiler_academic.md](inference/metabolic_profiler_academic.md) | EN/ES/RU/ZH |
| `vigia/memory/case_pattern_library.py` | [be71e68a_academic.md](unclassified/be71e68a_academic.md) | EN/ES/RU/ZH |
| `vigia/collapse_decision.py` | [7b5f476a_academic.md](unclassified/7b5f476a_academic.md) | 仅 EN ⚠ |

---

## 06 — 流水线与编排 (`pipeline/`)

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/pipeline/pipeline.py` | [pipeline_academic.md](pipeline/pipeline_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/evidence_bundle.py` | [evidence_bundle_academic.md](pipeline/evidence_bundle_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_builder.py` | [10a8df9f_academic.md](unclassified/10a8df9f_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/report_exporter.py` | [report_exporter_academic.md](pipeline/report_exporter_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/security_evidence_registry.py` | [security_evidence_registry_academic.md](pipeline/security_evidence_registry_academic.md) | EN/ES/RU/ZH |
| `vigia/pipeline/vigia_integration_bridge.py` | [db45f26c_academic.md](unclassified/db45f26c_academic.md) | EN/ES/RU/ZH |

---

## 07 — 安全与沙箱 (`security/`)

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/security/sandbox.py` | [sandbox_academic.md](security/sandbox_academic.md) | EN/ES/RU/ZH |
| `vigia/sandbox.py` | [sandbox_academic.md](root/sandbox_academic.md) | EN/ES/RU/ZH |
| `vigia/security/security.py` | [security_academic.md](security/security_academic.md) | EN/ES/RU/ZH |
| `vigia/security/vigia_seguridad.py` | [vigia_seguridad_academic.md](security/vigia_seguridad_academic.md) | EN/ES/RU/ZH |
| `vigia/security.py` | [security_academic.md](root/security_academic.md) | EN/ES/RU/ZH |

---

## 08 — 治理与风险 (`governance/`)

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/governance/trust_levels_p0.py` | [trust_levels_p0_academic.md](governance/trust_levels_p0_academic.md) | EN/ES/RU/ZH |
| `vigia/governance/risk_bounded_layer_v2.py` | [risk_bounded_layer_v2_academic.md](governance/risk_bounded_layer_v2_academic.md) | EN/ES/RU/ZH |
| `vigia/verdict/quadripartite.py` | [04d02947_academic.md](unclassified/04d02947_academic.md) | EN/ES/RU/ZH |
| `vigia/utils/path_guard.py` | [8d40e5b1_academic.md](unclassified/8d40e5b1_academic.md) | EN/ES/RU/ZH |

---

## 09 — VIGÍA 根模块 (`vigia/`)

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
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

## 10 — 操作脚本 (`scripts/`)

### 执行与诊断

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `scripts/run_vigia_full.py` | [2c0d7aea_academic.md](unclassified/2c0d7aea_academic.md) | EN/ES/RU/ZH |
| `scripts/run_case.py` | [run_case_academic.md](scripts/run_case_academic.md) | EN/ES/RU/ZH |
| `scripts/run_demo.py` | [run_demo_academic.md](scripts/run_demo_academic.md) | 仅 EN ⚠ |
| `scripts/pre_release_check.py` | [pre_release_check_academic.md](scripts/pre_release_check_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/compare_runs.py` | [8cf3f33e_academic.md](unclassified/8cf3f33e_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/evaluate_detector.py` | [c8cb7042_academic.md](unclassified/c8cb7042_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/consolidate_cases.py` | [0cf21887_academic.md](unclassified/0cf21887_academic.md) | EN/ES/RU/ZH |
| `vigia/scripts/top_breaking_phrases.py` | [cda1c372_academic.md](unclassified/cda1c372_academic.md) | EN/ES/RU/ZH |

### 转换与维护

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `scripts/convert_break_cases.py` | [convert_break_cases_academic.md](scripts/convert_break_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/convert_legacy_cases.py` | [convert_legacy_cases_academic.md](scripts/convert_legacy_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/convert_md_cases.py` | [convert_md_cases_academic.md](scripts/convert_md_cases_academic.md) | EN/ES/RU/ZH |
| `scripts/export_patterns.py` | [export_patterns_academic.md](scripts/export_patterns_academic.md) | EN/ES/RU/ZH |
| `scripts/fix_inits.py` | [fix_inits_academic.md](scripts/fix_inits_academic.md) | 仅 ZH ⚠ |
| `scripts/fix_security_init.py` | [__init___academic.md](security/__init___academic.md) | EN/ES/RU/ZH |
| `scripts/vigia_mass_refactor.py` | [vigia_mass_refactor_academic.md](scripts/vigia_mass_refactor_academic.md) | EN/ES ⚠ |
| `scripts/vigia_patch_valkyrie.py` | [2989e9bd_academic.md](unclassified/2989e9bd_academic.md) | EN/ES ⚠ |
| `recalibrate_cases.py` | [13bb704b_academic.md](unclassified/13bb704b_academic.md) | EN/ES/RU/ZH |
| `apply_caie_patch.py` | [442419c2_academic.md](unclassified/442419c2_academic.md) | EN/ES/RU/ZH |
| `cases/demo_case.py` | [demo_case_academic.md](scripts/demo_case_academic.md) | EN/ES/RU/ZH |

---

## 11 — 次级专项模块

### 高级溯因推理（`abduction/`）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/abduction/hypothesis_lineage.py` | [hypothesis_lineage_academic.md](specialized/hypothesis_lineage_academic.md) | EN/ES/RU/ZH |
| `vigia/abduction/vigia_artifact_graph.py` | [3254c6ec_academic.md](unclassified/3254c6ec_academic.md) | EN/ES ⚠ |
| `vigia/abduction/vigia_counter_fact.py` | [8f6f7187_academic.md](unclassified/8f6f7187_academic.md) | 仅 EN ⚠ |

### 缓解与处置（`action/`）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `vigia/action/vigia_mitigation_planner.py` | [vigia_mitigation_planner_academic.md](specialized/vigia_mitigation_planner_academic.md) | EN/ES/RU/ZH |

### 对抗性测试

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `run_adversarial_tests.py` | [8ebd0d52_academic.md](unclassified/8ebd0d52_academic.md) | EN/ES/RU/ZH |

---

## 语言覆盖不完整的文档

以下文档需要重新运行 Batch API 以达到完整的 EN/ES/RU/ZH 覆盖。  
执行 `python3 docs/academic/refresh_index_status.py` 更新所有表格中的语言状态。

---

## 12 — 附加模块（架构上未分类）

| Python 模块 | 文档 | 语言 |
|-------------|------|------|
| `pipeline_adapter.py`（规范流水线适配器） | [131c3f89_academic.md](unclassified/131c3f89_academic.md) | EN/ES/RU/ZH |
| `vigia_sift_bridge_patch.py`（BRIDGE_PATCH_FINAL） | [19008897_academic.md](unclassified/19008897_academic.md) | EN/ES/RU/ZH |
| `document_integrity.py`（v2，PDF/DOCX） | [1c52745b_academic.md](unclassified/1c52745b_academic.md) | EN/ES/RU/ZH |
| `vigia_namespace_shim.py`（兼容性桩） | [2d6dff4d_academic.md](unclassified/2d6dff4d_academic.md) | EN/ES/RU/ZH |
| `ci_gate.py` | [2ddb875b_academic.md](unclassified/2ddb875b_academic.md) | EN/ES/RU/ZH |
| `vigia_batch_postprocess.py` | [43e2ca4a_academic.md](unclassified/43e2ca4a_academic.md) | EN/ES/RU/ZH |
| `run_calibration.py` | [495820ba_academic.md](unclassified/495820ba_academic.md) | EN/ES/RU/ZH |
| `pattern_repository_init.py`（FPRI） | [4cffb019_academic.md](unclassified/4cffb019_academic.md) | EN/ES/RU/ZH |
| `vigia_server.py` | [59fb9f58_academic.md](unclassified/59fb9f58_academic.md) | EN/ES/RU/ZH |
| `run_stress_tests.py` | [5f1c653e_academic.md](unclassified/5f1c653e_academic.md) | EN/ES/RU/ZH |
| `evidence_narrative_generator.py` | [68e0e743_academic.md](unclassified/68e0e743_academic.md) | EN/ES/RU/ZH |
| `vigia_scorer.py`（变体 B） | [69cb51de_academic.md](unclassified/69cb51de_academic.md) | EN/ES/RU/ZH |
| `vigia_batch_doc_generator.py` | [779b4236_academic.md](unclassified/779b4236_academic.md) | EN/ES/RU/ZH |
| `report_exporter_v2.py` | [8d0b9079_academic.md](unclassified/8d0b9079_academic.md) | EN/ES/RU/ZH |
| `verify_ebs_v1.py`（独立 EBS 验证器） | [9810a97e_academic.md](unclassified/9810a97e_academic.md) | EN/ES/RU/ZH |
| `recommendation_engine_v3.1.py` | [adc5d097_academic.md](unclassified/adc5d097_academic.md) | EN/ES/RU/ZH |
| `negation_handler.py` | [b8bde3c7_academic.md](unclassified/b8bde3c7_academic.md) | EN/ES/RU/ZH |
| `generate_execution_log.py` | [e6461489_academic.md](unclassified/e6461489_academic.md) | EN/ES/RU/ZH |
| `convert_synthetic_cases.py` | [e74f0754_academic.md](unclassified/e74f0754_academic.md) | EN/ES/RU/ZH |
| `generate_release_bundle.py` | [ebd2829f_academic.md](unclassified/ebd2829f_academic.md) | EN/ES/RU/ZH |
| `generate_report.py` | [ec80b958_academic.md](unclassified/ec80b958_academic.md) | EN/ES/RU/ZH |
| `vigia_api.py`（变体——简化接口） | [ed735669_academic.md](unclassified/ed735669_academic.md) | EN/ES/RU/ZH |
| `vigia_scorer.py`（变体 C） | [ed8c1a84_academic.md](unclassified/ed8c1a84_academic.md) | EN/ES/RU/ZH |
| `sanitize_judicial.py` | [f8ae3e67_academic.md](unclassified/f8ae3e67_academic.md) | EN/ES/RU/ZH |

---

## 重复模块——等待 Git 同步

> **在 Git/本地仓库同步问题解决之前，不得合并这些模块对。**  
> 在路径协调之前合并将损毁法证记录。

| 模块 | 冲突哈希 | 路径冲突 |
|------|----------|----------|
| `caie.py` | `8c5d9283`、`ed0d4351` | 相同路径，内容不同 |
| `abductive_intent_engine.py` | `f14e91cc`、`9cf0944e`、`fd5b51d8` | `vigia/core/`、`vigia/`、`vigia/tools/` |
| `vision_audit.py` | `e0f29980`、`b2c8b2e5`、`c12c7450` | `vigia/forensics/` ×2、`vigia/tools/` |
| `behavioral_fingerprint.py` | `747d525d`、`8517382b` | `vigia/inference/` vs `vigia/tools/` |
| `sandbox.py` | `2042863e`、`845ea393` | `vigia/security/` vs `vigia/` 根目录 |
| `semiotic_detector.py` | `94fbce3d`、`b32a18e2`、`5dac09b1` | 三种路径变体 |

---

## 语料库统计

| 指标 | 数值 |
|------|------|
| 文档总数 | 193 |
| 完整 EN/ES/RU/ZH 覆盖 | ~160 份文档（~83%） |
| 仅 EN | 8 份文档 |
| 仅 ZH | 2 份文档 |
| 部分覆盖（EN/ES 或 EN/ES/RU） | 8 份文档 |
| 最大章节 | `core/`（49 份文档） |
| 对 SIFT 集成最关键 | `sift/`（16 份文档） |
| 已确认许可证错误（Apache 2.0） | 2 份文档——`fix_license_academic_docs.py` |
| 待解决的重复模块 | 6 对 / 13 份文档 |

> ⚠ — 文档语言覆盖不完整；建议在最终提交前重新生成。

---

*许可证：Apache License 2.0。版权所有 © 2026 Anna Tchijova。*  
*文档由 Moonshot Kimi K2.6 批处理 API 作为 VIGÍA AI 集体的一部分生成。*  
*(Claude、Gemini、DeepSeek、Qwen — 审计员与审稿人)*
