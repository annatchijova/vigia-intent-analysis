<!--
VIGIA Academic Documentation
Module: 2d6dff4d
Batch ID: vigia-doc-0174-2d6dff4d
Generated: 2026-05-20T14:56:47.882236+00:00
-->

**ENGLISH**

This compatibility stub resolves namespace continuity for the VIGIA digital forensics suite. Rather than implementing forensic logic directly, the module re-exports *ForensicDatabaseManager* and *LanguageDetector* from equivalent locations within the flattened repository architecture. It preserves legacy import paths expected by *temporal_forensics.py*, ensuring deterministic script behavior without code duplication. Scientists may treat this file as a symbolic bridge: it maintains experimental reproducibility while the codebase undergoes structural refactoring.

**ESPAÑOL**

Este módulo de compatibilidad resuelve la continuidad de espacios de nombres en la suite forense VIGIA. En lugar de implementar lógica forense directamente, reexporta *ForensicDatabaseManager* y *LanguageDetector* desde módulos equivalentes en la estructura aplanada del repositorio. Preserva rutas de importación heredadas requeridas por *temporal_forensics.py*, garantizando comportamiento determinista sin duplicación de código. Los científicos pueden interpretar este archivo como un puente simbólico que mantiene la reproducibilidad experimental durante la refactorización estructural.

**РУССКИЙ**

Данный модуль совместимости обеспечивает непрерывность пространства имён в цифровой судебно-экспертной системе VIGIA. Не реализуя форензическую логику напрямую, он реэкспортирует *ForensicDatabaseManager* и *LanguageDetector* из эквивалентных модулей плоской архитектуры репозитория. Сохраняя устаревшие пути импорта, необходимые для *temporal_forensics.py*, он гарантирует детерминированное поведение скриптов без дублирования кода. Учёные могут рассматривать файл как символический мост, поддерживающий воспроизводимость экспериментов при структурном рефакторинге.

**中文**

该兼容存根为VIGIA数字取证套件提供命名空间连续性。模块不直接实现取证逻辑，而从扁平化仓库的等效位置重新导出ForensicDatabaseManager与LanguageDetector。其保留temporal_forensics.py所需的旧版导入路径，确保脚本行为确定且避免代码冗余。科研人员可将此文件视为符号桥梁，在结构重构期间维持实验可复现性。

---

**GLOSSARY / GLOSARIO / ГЛОССАРИЙ / 术语表**

| Term | Definition |
|---|---|
| **Compatibility stub** | Minimal layer preserving access to relocated functions during system evolution. |
| **Namespace continuity** | Uninterrupted logical addressing of components despite physical file rearrangement. |
| **Re-export** | Exposing objects defined elsewhere through an intermediate module interface. |
| **Flattened repository** | Directory structure with reduced hierarchical nesting of packages. |
| **Import path** | Logical address a script uses to locate and load an external module. |
| **Deterministic behavior** | Exactly repeatable output given identical initial conditions and inputs. |
| **Legacy dependency** | Requirement inherited from earlier software versions or established protocols. |
| **Symbolic bridge** | Abstract intermediary linking obsolete references to current implementations. |
| **Structural refactoring** | Reorganizing codebase architecture without altering external functionality. |
| **Experimental reproducibility** | Capacity to replicate scientific results using original procedures and data. |

---

**Scientific Note / Nota Científica / Научное примечание / 科学注释**

*Deterministic forensic pipelines require invariant execution paths. Stub modules prevent chain-of-custody disruptions by ensuring hash validations and temporal analyses remain consistent across software revisions, independent of underlying directory restructuring.*
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
