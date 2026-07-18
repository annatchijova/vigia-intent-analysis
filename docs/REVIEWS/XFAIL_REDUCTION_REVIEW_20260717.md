# Registro de discusión — XFail Reduction Protocol (2026-07-17)

Anexo al plan `docs/XFAIL_REDUCTION_STRATEGY_20260717.md`. **El plan es la
autoridad operativa; esto es el registro de cómo se refinó.** Incorporado
parcialmente al plan (los puntos aceptados ya están en él); lo que sigue
preserva la discusión y las razones de aceptar o empujar de vuelta.

## Origen

Auditoría externa (Kimi) sobre el plan original, seguida de un contrapunto con
datos vivos del repo. Tres correcciones aceptadas, un empujón de vuelta, varios
pedidos de formalización incorporados.

## Correcciones aceptadas (con evidencia del repo)

1. **H-01 es peor de lo que la auditoría sospechó.** `clock_source` tiene cero
   consumidores de producción (grep vacío en `vigia/`, `vigia_scorer.py`,
   `vigia_agent.py`, `sift_orchestrator.py`) y el hard gate del scorer no lee
   `delta_seconds` (L1120-1122: solo `type` + `severity>=0.9`). El pedido de
   la auditoría — test de caracterización deltas × clock_source, sin juzgar —
   se ejecutó: `tests/characterization/test_temporal_gate_curve.py`. Primer
   resultado, tal como se anticipó: curva binaria y topología de relojes
   inexistente. La decisión de ventana tiene dos dimensiones, no una (tamaño
   del delta + mismo reloj vs relojes distintos).

2. **El diff del batch ya existe parcialmente.** `vigia/scripts/compare_runs.py`
   es un comparador determinista IMPROVEMENT/REGRESSION/VERDICT_SHIFT. El
   "consideralo" original era perezoso: cablear `--diff` es tarea chica.

3. **Los 14 FAILs como `skip` — empujón de vuelta aceptado por la auditoría.**
   Un `skip` nunca ejecuta, así que no detecta degradación — es un memorial,
   no un detector. La forma correcta del objetivo ("saber que no se degradan")
   es un test de caracterización que pinee el veredicto ACTUAL (FN-001 → NOISE
   hoy, label en disputa en el docstring): si el motor cambia, el suite rompe
   y obliga a mirar. Misma filosofía que `strict=True` en canonical.

## Empujón de vuelta (mantenido)

Contra la propuesta de los 14 FAILs como `skip`: rechazada por la razón de
arriba. Si se convierten en algo dentro de pytest, deben ser pins de
caracterización, no skips. Por ahora se mantienen **fuera** de pytest (en el
batch) con adjudicación documentada (plan §4.3) — son ground-truth en disputa
o modos distintos del motor, no contratos de código. Convertirlos en pins es
opción futura, no deuda abierta.

## Formalizaciones incorporadas al plan

- **Protección cableada explícita** (plan §0): `strict=True` hace imposible el
  camino mecánico 33→0 sin adjudicación caso por caso. La defensa está en el
  código, no solo en prosa.
- **Protocolo de 6 pasos reutilizable** (plan §0): el plan define un protocolo,
  no una campaña; vale para cualquier tanda futura de xfails.
- **Tabla de adjudicación de los 14 FAILs** (plan §4.3): 6 doctrina/etiqueta,
  3 calibración (floor), 3 detector, 2 sin adjudicar (KIWI). Con referencia
  documental por caso. Denominadores separados: batch 201 ≠ corpus 193.
- **Rename** a "XFail Reduction Protocol": el título viejo sugería bajar un
  número; el objetivo real es que el suite no mienta.
- **Tanda 6 (D-G)**: estimación duplicada (código + validación de divergencias
  con el harness corpus-wide que el dossier ya corrió una vez).

## Riesgo metodológico identificado (y neutralizado)

La auditoría identificó bien que el riesgo mayor no es técnico sino
metodológico: la presión por cerrar xfails empujando a decisiones apresuradas
en fronteras doctrinales (H-01, D-2, D-G). El mecanismo ya instalado empuja en
contra: `strict=True` hace que reparar datos *rompa* el suite hasta revisión
caso por caso. La protección no es solo advertencia escrita — está cableada.
