<!--
VIGIA Academic Documentation
Module: ebd2829f
Batch ID: vigia-doc-0016-ebd2829f
Generated: 2026-05-20T14:56:47.848267+00:00
-->

**ENGLISH**

`generate_release_bundle.py` produces cryptographically signed release bundles for the VIGIA forensic platform. It archives complete source code and a SHA-256 manifest, generating tamper-evident artifacts. SANS auditors rely on these deterministic outputs to verify software integrity and preserve chain-of-custody before deployment.

*Scientific Note: HMAC-SHA256 provides message authentication, not encryption; confidentiality of the bundle must be enforced separately by access controls.*

**ESPAÑOL**

`generate_release_bundle.py` genera paquetes de release firmados criptográficamente para la plataforma forense VIGIA. Archiva el código fuente completo y un manifiesto SHA-256, produciendo artefactos con evidencia de manipulación. Los auditores SANS emplean estos resultados deterministas para verificar la integridad del software y preservar la cadena de custodia antes del despliegue.

*Nota científica: HMAC-SHA256 proporciona autenticación, no cifrado; la confidencialidad del paquete requiere controles de acceso separados.*

**РУССКИЙ**

Модуль `generate_release_bundle.py` создаёт криптографически подписанные пакеты релиза для судебной платформы VIGIA. Он архивирует полный исходный код и манифест SHA-256, формируя контролируемые артефакты. Аудиторы SANS используют эти детерминированные результаты для проверки целостности ПО и поддержания цепочки хранения перед развёртыванием.

*Научное примечание: HMAC-SHA256 обеспечивает аутентификацию, но не шифрование; конфиденциальность пакета должна регулироваться отдельными средствами контроля доступа.*

**中文**

`generate_release_bundle.py` 为 VIGIA 取证平台生成经密码学签名的发布包。该组件归档完整源代码及 SHA-256 清单，生成防篡改工件。SANS 审计员利用这些确定性输出验证软件完整性，并在部署前保全监管链。

*科学注释：HMAC-SHA256 提供消息认证而非加密；包体的机密性须通过独立访问控制实现。*

---

**Glossary / Glosario / Глоссарий / 词汇表**

1. **HMAC-SHA256** — Symmetric authentication code (código de autenticación simétrico / симметричный код аутентификации / 对称认证码) derived via iterated hash operations.
2. **Release Bundle** — Distributable software archive (archivo de software distribuible / распространяемый архив ПО / 可分发软件归档) containing versioned artifacts.
3. **Deterministic Process** — Algorithm producing identical outputs (algoritmo que produce salidas idénticas / алгоритм с идентичными выходами / 产生相同输出的算法) from identical inputs.
4. **Tamper Evidence** — Irreversible indicator (indicador irreversible / необратимый индикатор / 不可逆指示器) of unauthorized data modification.
5. **Chain of Custody** — Documented continuity (continuidad documentada / документированная непрерывность / 记录在案的连续性) of evidence handling and transfer.
6. **SANS Auditor** — Certified examiner (examinador certificado / сертифицированный эксперт / 经认证的审查员) following SANS Institute digital forensics protocols.
7. **Source Code Manifest** — Cryptographic inventory (inventario criptográfico / криптографический инвентарь / 密码学清单) enumerating every file in a build.
8. **Integrity Verification** — Confirmatory test (prueba confirmatoria / подтверждающая пров
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
