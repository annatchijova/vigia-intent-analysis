<!--
VIGIA Academic Documentation
Module: f8ae3e67
Batch ID: vigia-doc-0170-f8ae3e67
Generated: 2026-05-20T14:56:47.881448+00:00
-->

**ENGLISH**  
The VIGÍA sanitize_judicial module is a local forensic preprocessing tool for judicial PDF documents. It performs deterministic text extraction, removes personally identifiable information (PII), and replaces sensitive entities with consistent pseudonymous tokens. Processing occurs entirely within an air-gapped, cloud-free environment, preserving evidentiary integrity and confidentiality.

**ESPAÑOL**  
El módulo sanitize_judicial de VIGÍA es una herramienta forense local de preprocesamiento para documentos judiciales en PDF. Realiza extracción determinista de texto, elimina información de identificación personal (PII) y sustituye entidades sensibles por tokens pseudónimos consistentes. El procesamiento ocurre en un entorno aislado sin conexión a la nube, garantizando integridad probatoria y confidencialidad.

**РУССКИЙ**  
Модуль sanitize_judicial системы VIGÍA — это локальный инструмент судебно-экспертной предобработки PDF-документов. Выполняет детерминированное извлечение текста, удаляет персональные данные (PII) и заменяет конфиденциальные сущности стабильными псевдонимными токенами. Обработка происходит полностью в изолированной среде без облака, сохраняя доказательственную целостность и конфиденциальность.

**中文**  
VIGÍA sanitize_judicial 模块是司法 PDF 文件的本地取证预处理工具。执行确定性文本提取，清除个人可识别信息（PII），并以一致的伪名令牌替换敏感实体。全部处理在无云隔离环境中本地完成，确保证据完整性与保密性。

**Scientific Note**  
Deterministic token assignment ensures that repeated references to the same identity across multiple PDFs map to identical pseudonyms, enabling relational analysis without exposing raw PII. This process avoids probabilistic hashing and operates entirely within volatile memory, leaving no persistent cache of sensitive data.

**Glossary**  
1. **PII (Personally Identifiable Information)** — Data that can identify an individual, such as names or government identifiers.  
2. **Deterministic Extraction** — A reproducible process yielding identical output from identical input, ensuring scientific repeatability.  
3. **Pseudonymization** — Replacing private identifiers with artificial tokens to obscure identity while preserving data structure.  
4. **Consistent Token** — A fixed pseudonym assigned to a specific entity across a document set, enabling relational analysis without disclosure.  
5. **Air-Gapped Environment** — A system physically isolated from external networks to prevent unauthorized data exfiltration.  
6. **Evidentiary Integrity** — The unaltered state of digital evidence required for legal admissibility and chain-of-custody documentation.  
7. **Forensic Preprocessing** — Transformation of raw digital artifacts into sanitized formats prior to analytical examination.  
8. **Local Processing** — Computation executed entirely on-site without transmitting data to remote servers or cloud infrastructure.  
9. **Sanitization** — The systematic removal or obfuscation of sensitive data to comply with privacy and forensic protocols.  
10. **PDF Text Extraction** — Recovery of machine-readable character sequences from portable document format files for downstream analysis.
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
