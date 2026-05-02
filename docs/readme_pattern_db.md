# VIGÍA Pattern Database v1.0

## Qué es esto

Un **diccionario de detección determinista** que codifica las firmas de
manipulación semiótica encontradas en 110+ casos forenses (sintéticos + reales).

**NO es entrenamiento de IA. NO es machine learning.**
Es lógica abductiva con regex auditables: si el texto coincide con un patrón,
VIGÍA aplica un boost de confianza y documenta por qué.

---

## Estructura

| Archivo | Propósito |
|---------|-----------|
| `forensic_patterns_enriched.sqlite` | Base de datos SQLite con 37 patrones |
| `vigia_patterns_migration.sql` | Script SQL para migrar/actualizar la DB |
| `pattern_detector.py` | Módulo Python `SemioticPatternDetector` |

---

## Categorías de Patrones

### CARNEGIE (10 patrones) — Manipulación interpersonal
- `CARNEGIE_NOBLE_MOTIVE` — Apelación a motivos nobles para ocultar exfiltración
- `CARNEGIE_WEAPONIZED_INCOMPETENCE` — Fingir torpeza para evadir auditoría
- `CARNEGIE_PREEMPTIVE_CONFESSION` — Confesión rápida de falta menor
- `CARNEGIE_FLATTERY_MIRRORING` — Adulación/espejo lingüístico
- `CARNEGIE_HELPER_TRAP` — Ofrecer ayuda para insertarse en proceso
- `CARNEGIE_IMPORTANCE_APPEAL` — Usar jerarquía para paralizar receptor
- `CARNEGIE_PRIVACY_SHIELD` — Preocupación por privacidad como vehículo
- `CARNEGIE_NORMALIZATION_PRESSURE` — Presión social para anular dudas
- `CARNEGIE_ARTIFICIAL_URGENCY` — Urgencia falsa para evadir verificación
- `CARNEGIE_BORROWED_CREDIBILITY` — Citar autoridad inverosímil

### GRICE (10 patrones) — Violaciones cooperativas
- `GRICE_QUANTITY_FLOOD` — Saturar con información irrelevante
- `GRICE_QUANTITY_STARVATION` — Omitir información crítica
- `GRICE_QUALITY_UNVERIFIABLE` — Afirmación sin evidencia
- `GRICE_QUALITY_FALSE_NORMALITY` — Normalización sin sustento
- `GRICE_RELATION_IRRELEVANCE` — Información desconectada del problema
- `GRICE_MANNER_CHAOS` — Caos deliberado para ocultar
- `GRICE_MANNER_AMBIGUITY` — Opacidad intencional
- `GRICE_DEFENSIVE_EVASION` — Evasión combinada
- `GRICE_DESTRUCTION_REQUEST` — Solicitar destrucción de evidencia
- `GRICE_EVIDENCE_CLEANING` — Justificar destrucción como "limpieza"

### ECO (12 patrones) — Rastros semióticos
- `ECO_KEYBOARD_SLIP_CYRILLIC` — Desliz de teclado ruso
- `ECO_SLAVIC_SYNTAX` — Sintaxis eslava en inglés
- `ECO_ANACHRONISM_TOOL` — Herramienta incompatible con entorno
- `ECO_SYNTHETIC_JITTER` — Aleatoriedad demasiado perfecta
- `ECO_FALSE_AMATEUR_TRAIL` — Rastro falso de aficionado
- `ECO_HOMOGLYPH_WATERMARK` — Marca de agua con homóglifos
- `ECO_PLATFORM_CONTAMINATION` — Comando de SO equivocado
- `ECO_INHUMAN_PERFECTION` — Proceso sin entropía humana
- `ECO_SYNTHETIC_IDENTITY` — Identidad simulada (voz, estilo)
- `ECO_SEMIOTIC_COLLISION` — Meta-ataque contra el propio motor
- `ECO_TABOO_EXPLOITATION` — Uso de tabú social
- `ECO_PLAUSIBLE_DENIABILITY` — Explicación pueril para error

### PEIRCE (5 patrones) — Índices físicos
- `PEIRCE_TIMESTOMP_FRICTION` — Inconsistencia temporal
- `PEIRCE_ENTROPY_INVERSION` — Entropía anómala
- `PEIRCE_PROCESS_MASQUERADE` — Proceso en ubicación ilegítima
- `PEIRCE_MISSING_INDEX` — Ausencia de rastro esperado
- `PEIRCE_CIRCADIAN_BREAK` — Ruptura de ritmo circadiano

---

## Uso en el Pipeline

```python
from vigia.core.pattern_detector import detect_semiotic_frictions

# Analizar un artefacto
result = detect_semiotic_frictions(
    "Soy un desastre, rompí el proxy configurando el entorno de pruebas...",
    artifact_type="slack_message"
)

# Resultado
{
    "matches": [{
        "pattern_name": "CARNEGIE_WEAPONIZED_INCOMPETENCE",
        "weight": 0.90,
        "confidence_boost": 0.27,
        "peirce_layer": "THIRDNESS"
    }],
    "confidence_adjustment": 0.27,  # A sumar al cálculo de riesgo
    "dominant_category": "CARNEGIE"
}
```

---

## Determinismo garantizado

- ✅ Regex compiladas al inicio, no en runtime
- ✅ Orden fijo: peso descendente
- ✅ Sin random, sin floating point en scoring
- ✅ Sin dependencias externas (solo stdlib + sqlite3)
- ✅ `sort_keys=True` en todo output JSON

---

## Próximo paso

Integrar `pattern_detector.py` en `vigia/tools/adversarial_nlp.py` para que
el pipeline de inferencia aplique estos patrones automáticamente a cada
artefacto textual.

---

*Generado: 2026-04-28T06:23:26.338917+00:00*
*Schema: v1.0 | Casos fuente: 110+ | Patrones: 37*
*Standard: SANS_FIND_EVIL_2026*
