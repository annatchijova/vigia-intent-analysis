# Umbrales Dinámicos VIGÍA — Nota para mantenedores

## ⚠️ IMPORTANTE: No hardcodear constantes

Los siguientes parámetros son **dinámicos por diseño** para evitar que un atacante con acceso al código fuente (Open Source) pueda ajustar su comportamiento exactamente al límite:

### 1. Beaconing Detection (`network_forensics.py`)
- **Antes**: Umbral fijo de entropía `< 3.5 bits`
- **Ahora**: `beacon_score` compuesto ponderado:
  - CV bajo: +0.3
  - Periodicity ≥ 0.6: +0.3
  - Entropía relativa < 0.7: +0.2
  - Tendencia Mann-Kendall: +0.2
  - Umbral final: `≥ 0.7` (score compuesto)
- **Razón**: Un atacante que lea el código no puede ajustar jitter a un único número mágico.

### 2. Timestomp Masivo (`disk_forensics.py`)
- **Antes**: `len(group) >= 5` archivos con timestamp idéntico
- **Ahora**: `len(group) >= 3`
- **Razón**: Evadir lotes de 4 ya no funciona.

### 3. Causal Closure Score (`signal_mapper.py`)
- **Antes**: Entropía máxima fija = 4.7 bits
- **Ahora**: Entropía máxima real = número de causas únicas observadas
- **Factor de entropía acotado**: `max(1 - entropy, 0.5)` — nunca fuerza ABSTAIN arbitrariamente.

### 4. Conflict Penalty (`_math_utils.py`)
- **Antes**: Penalización al dominante (vulnerable a silenciamiento)
- **Ahora**: Penalización exclusiva a NO-dominantes
- **Invariante**: `z_final_dominante >= z_final_no_dominante` siempre que `z_inicial_dominante > z_inicial_no_dominante` y `Γ_dominante > Γ_no_dominante`.

## Regla de oro para futuros parches

> Si descubrís que un umbral es un número mágico escrito directamente en el código (ej. `>= 5`, `< 3.5`), convertirlo en una función dinámica o moverlo a configuración externa secreta (NO en el repo público).

---
*Documento interno del Colectivo VIGÍA — no incluir en release notes públicas*
