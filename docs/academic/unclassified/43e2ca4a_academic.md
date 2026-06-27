<!--
VIGIA Academic Documentation
Module: 43e2ca4a
Batch ID: vigia-doc-0027-43e2ca4a
Generated: 2026-05-20T14:56:47.850423+00:00
-->

## ENGLISH

`vigia_batch_postprocess.py` is a deterministic post-processor for VIGIA Batch API outputs. It ingests structured raw logs (`batch_results.jsonl`) and generates standardized forensic reports in `docs_generados/`. The process is strictly reproducible: identical inputs yield bit-identical outputs, preserving chain-of-custody integrity. No probabilistic operations are employed.

## ESPAÑOL

`vigia_batch_postprocess.py` es un post-procesador determinista de salidas Batch API de VIGIA. Ingesta registros brutos estructurados (`batch_results.jsonl`) y genera informes forenses estandarizados en `docs_generados/`. El proceso es estrictamente reproducible: entradas idénticas producen salidas idénticas a nivel de bit, preservando la integridad de la cadena de custodia. No utiliza operaciones probabilísticas.

## РУССКИЙ

`vigia_batch_postprocess.py` — детерминированный постпроцессор выходных данных Batch API VIGIA. Принимает структурированные исходные журналы (`batch_results.jsonl`) и формирует стандартизированные экспертные отчёты в `docs_generados/`. Процесс строго воспроизводим: идентичные входные данные дают битово-идентичные результаты, сохраняя целостность цепочки сохранения. Вероятностные операции не применяются.

## 中文

`vigia_batch_postprocess.py` 是 VIGIA Batch API 输出的确定性后处理器。它摄取结构化原始日志（`batch_results.jsonl`），并在 `docs_generados/` 中生成标准化取证报告。该过程严格可复现：相同输入产生比特级一致输出，以保全保管链完整性。不使用概率运算。

## GLOSSARY / GLOSARIO / ГЛОССАРИЙ / 词汇表

1. **Batch API** — Interface for grouped forensic task submission. / Interfaz para envío agrupado de tareas forenses. / Интерфейс групповой отправки экспертных задач. / 用于分组取证任务提交的接口。

2. **Post-processing** — Automated transformation of raw outputs into final reports. / Transformación automatizada de salidas brutas en informes finales. / Автоматизированное преобразование исходных данных в итоговые отчёты. / 将原始输出自动转换为最终报告的过程。

3. **Deterministic system** — System where identical inputs always produce identical outputs. / Sistema donde entradas idénticas siempre producen salidas idénticas. / Система, в которой идентичные входы всегда дают идентичные выходы. / 相同输入始终产生相同输出的系统。

4. **JSONL** — Line-delimited JSON format for structured log streams. / Formato JSON delimitado por líneas para flujos de registro estructurados. / Построчный формат JSON для структурированных потоков журналов. / 用于结构化日志流的行分隔 JSON 格式。

5. **Bit-reproducible output** — Output that is identical on the binary level across runs. / Salida idéntica a nivel binario entre ejecuciones. / Выход, битово идентичный при повторных запусках. / 多次运行间在二进制级别完全一致的输出。

6. **Chain of custody** — Documented protocol ensuring evidence integrity. / Protocolo documentado que asegura la integridad de la evidencia. / Документированный протокол обеспечения целостности доказательств. / 确保证据完整性的记录在案协议。

7. **Forensic artifact** — Digital object collected as evidence during investigation. / Objeto digital recolectado como evidencia durante la investigación. / Цифровой объект, собранный как доказательство при расследовании. / 调查过程中作为证据收集的数字对象。

8. **Raw log** — Unprocessed machine-readable event record. / Registro de eventos no procesado legible por máquina. / Необработанная машиночитаемая запись событий. / 未经处理的机器可读事件记录。

9. **Rendered report** — Human-readable document generated from structured data. / Documento legible generado a partir de datos estructurados. / Читаемый документ, сформированный из структурированных данных. / 由结构化数据生成的人类可读文档。

10. **Standardized documentation** — Evidence files formatted under consistent schema rules. / Archivos de evidencia formateados bajo reglas de esquema consistentes. / Файлы доказательств, оформленные по единым правилам схемы. / 依据一致模式规则格式化的证据文件。

---

*Licensed under the Apache License, Version 2.0. Copyright 2026 Anna Tchijova.*
