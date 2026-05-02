# Consolidación de Casos VIGÍA - Dataset REAL

## Estado: COMPLETO ✓

Se consolidaron **10 casos forenses** basados en datasets públicos reales,
listos para ingestión por el pipeline de VIGÍA.

---

## Distribución de Veredictos

| Veredicto | Cantidad | Casos |
|-----------|----------|-------|
| **MALICE** | 9 | REAL-001 al 004, 006 al 010 |
| **SUSPICION** | 1 | REAL-005 (Encrypt Them All) |

**Rango de confianza**: 88% - 95%

---

## Fuentes Documentadas

| Fuente | Casos | Dataset |
|--------|-------|---------|
| NIST CFReDS | 2 | Hacking Case (Mr. Evil), Data Leakage Case |
| Ali Hadi Challenges | 3 | Web Server, SysInternals, Encrypt Them All |
| Digital Corpora | 2 | M57-Jean Spear-Phishing, Nitroba Harassment |
| Volatility Foundation | 1 | Cridex Banking Trojan |
| DFRWS | 2 | 2008 Linux Exfiltration, 2011 Android Espionage |

---

## Corrección Crítica Aplicada

**VIGIA-REAL-006 (M57-Jean)**:
- ❌ Antes: `NOISE` (incorrecto — la víctima no es el atacante)
- ✅ Después: `MALICE` (correcto — el spear-phishing fue exitoso)
- Devil's advocate actualizado para reflejar buena fe de la víctima
- Peirce reinterpretado: la intención es del atacante, no de Jean

---

## Estructura de Archivos Generados

```
vigia_cases_consolidated/
├── VIGIA-REAL-001.json   # NIST Hacking Case (Mr. Evil)
├── VIGIA-REAL-002.json   # NIST Data Leakage Case
├── VIGIA-REAL-003.json   # Ali Hadi Web Server Compromise
├── VIGIA-REAL-004.json   # Ali Hadi SysInternals Malware
├── VIGIA-REAL-005.json   # Ali Hadi Encrypt Them All [SUSPICION]
├── VIGIA-REAL-006.json   # Digital Corpora M57-Jean [CORREGIDO]
├── VIGIA-REAL-007.json   # Digital Corpora Nitroba Harassment
├── VIGIA-REAL-008.json   # Volatility Cridex Trojan
├── VIGIA-REAL-009.json   # DFRWS 2008 Linux Exfiltration
├── VIGIA-REAL-010.json   # DFRWS 2011 Android Espionage
└── _index.json           # Catálogo maestro
```

---

## Validación

- ✅ Todos los campos requeridos presentes
- ✅ Veredictos dentro de valores permitidos
- ✅ Capas Peirce válidas (FIRSTNESS/SECONDNESS/THIRDNESS)
- ✅ Tipos de artefactos válidos
- ✅ Confianza en rango 0-100 (todos entre 88-95)
- ✅ JSON sintácticamente válido
- ✅ `sort_keys=True` para determinismo bit-for-bit

---

## Próximo Paso

Estos 10 casos están listos para:
1. Ingestión por `vigia/pipeline/consolidate_cases.py`
2. Ejecución con `run_vigia.sh` para generar Agent Execution Logs
3. Inclusión en el Accuracy Report del hackathon

---

*Consolidado: 2026-04-28T05:52:03.542519+00:00*
*Schema: v1.0 | Standard: SANS_FIND_EVIL_2026*
