<!--
VIGIA Academic Documentation
Module: 3aa7e98b
Batch ID: vigia-doc-0057-3aa7e98b
Generated: 2026-05-20T14:56:47.856732+00:00
-->

**ENGLISH**  
Module `vigia/core/geopolitical_v2.py` implements the deterministic Geopolitical Intent Engine v3.0-P0-003 for the VIGÍA forensic framework. It resolves geopolitical timestamps using exact IANA timezone rules, eliminating prior heuristic errors of up to 28 days in seasonal clock transitions. Patches C3, W7, W8, P2-B and P0-003 ensure temporal integrity by mapping geopolitical entities to canonical zone identifiers. Scientific note: All temporal calculations are rule-based and reproducible, preserving chain-of-custody validity in digital forensics.

**ESPAÑOL**  
El módulo `vigia/core/geopolitical_v2.py` implementa el Motor de Intención Geopolítica v3.0-P0-003 del marco forense VIGÍA. Resuelve marcas temporales geopolíticas mediante reglas exactas de zonas horarias IANA, eliminando errores heurísticos previos de hasta 28 días en transiciones de horario de verano. Los parches C3, W7, W8, P2-B y P0-003 garantizan integridad temporal al mapear entidades geopolíticas a identificadores canónicos. Nota científica: los cálculos temporales son deterministas y reproducibles, preservando la validez de la cadena de custodia.

**РУССКИЙ**  
Модуль `vigia/core/geopolitical_v2.py` реализует детерминированный Геополитический Интент-движок v3.0-P0-003 для судебной платформы VIGÍA. Он разрешает геополитические временные метки по точным правилам часовых поясов IANA, устраняя прежние эвристические погрешности до 28 суток при сезонных переходах. Патчи C3, W7, W8, P2-B и P0-003 обеспечивают временную целостность через сопоставление геополитических сущностей с каноническими идентификаторами. Научное примечание: все временные вычисления воспроизводимы и сохраняют юридическую силу цепочки хранения.

**中文**  
`vigia/core/geopolitical_v2.py` 模块为 VIGÍA 取证框架实现了确定性地缘政治意图引擎 v3.0-P0-003。该模块依据 IANA 时区规则的精确映射解析地缘政治时间戳，消除了先前在夏令时过渡期间最高达 28 天的启发式误差。补丁 C3、W7、W8、P2-B 及 P0-003 通过将地缘政治实体映射至标准时区标识符，确保时间完整性。科学注释：所有时间计算均基于规则且可复现，以保全数字取证中的监管链效力。

---

**Glossary / Glosario / Глоссарий / 术语表**

1. **Chain of custody / Cadena de custodia / Цепочка хранения / 监管链** — Forensic documentation tracking evidence from seizure to courtroom.  
2. **DST / Horario de verano / Летнее время / 夏令时** — Seasonal one-hour clock advance.  
3. **Deterministic system / Sistema determinista / Детерминированная система / 确定性系统** — Process yielding identical outputs from identical inputs.  
4. **Heuristic error / Error heurístico / Эвристическая погрешность / 启发式误差** — Inaccuracy from approximate rule-of-thumb methods.  
5. **IANA timezone database / Base de datos de zon
---
*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
