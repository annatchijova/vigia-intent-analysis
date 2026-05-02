# VIGÍA Evaluation Suite — Resumen para Claude

## ¿Qué es esto?

Paquete de evaluación determinista para VIGÍA. Separado en dos responsabilidades claras:

1. **evaluate_detector.py** → Métricas forenses reales (precision, recall, FPR) contra ground truth.
2. **compare_runs.py** → Comparación de versiones (deltas, regresiones, mejoras) sin confundir con métricas forenses.

## Archivos

| Archivo | Propósito |
|---------|-----------|
| `evaluate_detector.py` | Corre pipeline sobre 20 casos, calcula TP/FP/TN/FN reales |
| `compare_runs.py` | Compara dos runs, detecta regresiones con ground truth |
| `test_cases.json` | Dataset de 20 payloads adversariales con textos |
| `ground_truth.json` | Mapping artifact_id → ADVERSARIAL/BENIGN |
| `run_eval.sh` | Orquestador que corre todo y genera reportes |
| `prompt_para_claude.txt` | Prompt exacto para darle a Claude |

## Flujo de datos

```
test_cases.json + ground_truth.json
        ↓
evaluate_detector.py  →  baseline_metrics.json
        ↓
compare_runs.py       →  comparison.csv + diff en consola
```

## Vocabulario crítico

- **ADVERSARIAL**: Casos que el sistema DEBE detectar (alert ≥ MEDIUM)
- **BENIGN**: Casos que el sistema NO debe detectar (alert ≤ LOW)
- **IMPROVEMENT** (en compare_runs): v2.2.3 se comportó mejor que v2.2.2
- **REGRESSION** (en compare_runs): v2.2.3 empeoró respecto a v2.2.2

## Notas para la demo

- `compare_runs.py` NUNCA dice TP/FP. Eso es evaluate_detector.py.
- Driver detection es `heuristic_v1 (non-causal)`. No es atribución causal.
- Todo delta de MI se reduce por MCD (fracciones irreducibles).
- Hash canónico verifica determinismo bit-for-bit.
