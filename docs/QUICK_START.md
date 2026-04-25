# VIGÍA Hito 1 — Quick Start Integration

## 1. COPIAR ARCHIVOS

```bash
# Copiar los 3 módulos a tu estructura
cp visible_variables.py    /path/to/vigia/engine/
cp picerl_mapping.py       /path/to/vigia/forensics/
cp trust_levels.py         /path/to/vigia/governance/
```

## 2. INTEGRACIÓN CON TU PIPELINE ACTUAL

### Flujo recomendado

```python
# tu_pipeline.py
from vigia.engine.visible_variables import VisibleVariablesEngine, analyze_bundle_focus
from vigia.forensics.picerl_mapping import PICERLMapper, generate_picerl_i_from_focus
from vigia.governance.trust_levels import TrustLevelVerifier, create_trusted_root, TrustLevel

# Paso 1: Detectar foco (variables visibles)
bundle = load_forensic_bundle()  # Tu código actual
focus, filtered_signals = analyze_bundle_focus(
    bundle=bundle,
    verbose=True
)

# Paso 2: Generar hipótesis de intención (PICERL-compatible)
mapper = PICERLMapper(verbose=True)
hypothesis = mapper.map_focus_analysis_to_intent(focus)

# Paso 3: Verificar confianza (niveles 1-4)
tr = create_trusted_root()
verifier = TrustLevelVerifier(trusted_root=tr, verbose=True)
verification = verifier.verify(
    data=bundle.to_dict(),
    trust_level=TrustLevel.LEVEL_2,  # O LEVEL_4 si quieres todo
)

# Paso 4: Pasar señales FILTRADAS a LikelihoodEngine
lr_record = likelihood_engine.infer(
    signals=[s for s in bundle.signals if s.label in focus.visible_variables],
    # Nota: now passing ONLY visible signals, not all
)

# Paso 5: Generar reporte
report = mapper.generate_picerl_i_report(
    bundle_id=bundle.bundle_id,
    hypotheses=[hypothesis],
    focus_analyses=[focus],
)

print(report)
```

## 3. OPCIÓN A: INTEGRACIÓN MÍNIMA (solo VisibleVariables)

Si solo querés filtro de ruido sin PICERL:

```python
from vigia.engine.visible_variables import analyze_bundle_focus

focus, filtered_signals = analyze_bundle_focus(bundle)
print(f"Phase detected: {focus.detected_phase.value}")
print(f"Variables visible: {len(focus.visible_variables)}")

# Usa filtered_signals en tu pipeline existente
my_likelihood_engine.infer(signals=filtered_signals)
```

## 4. OPCIÓN B: INTEGRACIÓN COMPLETA (todo)

```python
from vigia.engine.visible_variables import analyze_bundle_focus
from vigia.forensics.picerl_mapping import generate_picerl_i_from_focus
from vigia.governance.trust_levels import TrustLevelVerifier, TrustLevel

# Análisis completo
focus, filtered = analyze_bundle_focus(bundle, verbose=True)
hypotheses, picerl_report = generate_picerl_i_from_focus(bundle.bundle_id, [focus])
verification = TrustLevelVerifier().verify(bundle.to_dict(), TrustLevel.LEVEL_4)

# Salida estructurada
output = {
    "bundle_id": bundle.bundle_id,
    "focus_analysis": focus.to_dict(),
    "intent_hypothesis": hypotheses[0].to_dict(),
    "verification": verification.to_dict(),
    "picerl_i_report": picerl_report,
}

# JSON-serializable, listo para reportes
print(json.dumps(output, indent=2))
```

## 5. ADAPTACIÓN A TUS DATOS ACTUALES

### Si usas ForensicBundle con signos (artifacts)

```python
# Tu estructura actual
bundle = {
    "bundle_id": "case_002",
    "signals": [
        SignalOutput(tool_name="SDA", signal_id="...", value=0.8, z_score=1.2),
        SignalOutput(tool_name="CLI", signal_id="...", value=0.1, z_score=-2.5),
        ...
    ],
    "temporal_violations": [...],
    "mitre_ttps": ["T1497", "T1565.001"],
}

# Convertir a formato de visible_variables
analyzed = analyze_bundle_focus({
    "bundle_id": bundle["bundle_id"],
    "signals": [
        {
            "label": s.metadata.get("signal_type", s.tool_name.lower()) if s.metadata else s.tool_name.lower(),
            "type": "signal",
            "value": s.value,
            "z_score": s.z_score,
        }
        for s in bundle["signals"]
    ],
    "temporal_violations": bundle.get("temporal_violations", []),
    "mitre_ttps": bundle.get("mitre_ttps", []),
})
```

### Si usas casos JSON (case_002_log_fabrication.json)

```python
import json

case = json.load(open("case_002_log_fabrication__1_.json"))

# Extraer campos relevantes
bundle_dict = {
    "bundle_id": case["case_id"],
    "signals": [
        {
            "label": "temporal_uniformity" if "uniformity_flag" in art.get("metadata", {}) else art["evidence_type"],
            "type": "artifact",
        }
        for art in case["artifacts"]
    ],
    "temporal_violations": case.get("temporal_violations", []),
    "mitre_ttps": case.get("expected_mitre_ttps", []),
}

focus, filtered = analyze_bundle_focus(bundle_dict, verbose=True)
```

## 6. TESTING TU INTEGRACIÓN

```python
# test_hito_1_integration.py
import unittest
from visible_variables import analyze_bundle_focus
from picerl_mapping import generate_picerl_i_from_focus
from trust_levels import TrustLevelVerifier, TrustLevel

class TestHito1Integration(unittest.TestCase):
    
    def test_visible_variables_determinism(self):
        """Verificar que analyze_bundle_focus es determinístico"""
        bundle = {"bundle_id": "test", "signals": [], "temporal_violations": []}
        focus1, _ = analyze_bundle_focus(bundle)
        focus2, _ = analyze_bundle_focus(bundle)
        self.assertEqual(focus1.focus_hash, focus2.focus_hash)
    
    def test_picerl_mapping_falsability(self):
        """Verificar que toda hipótesis tiene campo what_would_falsify"""
        from visible_variables import FocusAnalysis, IRPhase, VariableCategory
        
        focus = FocusAnalysis(
            bundle_id="test",
            detected_phase=IRPhase.PERSISTENCE,
            phase_confidence=0.9,
            visible_categories={VariableCategory.PERSISTENCE},
            visible_variables={},
        )
        
        mapper = PICERLMapper()
        hyp = mapper.map_focus_analysis_to_intent(focus)
        self.assertIsNotNone(hyp.what_would_falsify)
        self.assertTrue(len(hyp.what_would_falsify) > 10)
    
    def test_trust_level_verification(self):
        """Verificar que TrustLevelVerifier retorna VerificationResult válido"""
        verifier = TrustLevelVerifier()
        result = verifier.verify({"test": "data"}, TrustLevel.LEVEL_2)
        self.assertEqual(result.status, "OK")
        self.assertIsNotNone(result.audit_log)

if __name__ == "__main__":
    unittest.main()
```

Ejecutar:
```bash
python3 -m pytest test_hito_1_integration.py -v
```

## 7. INTEGRACIÓN CON CI/CD (GitHub Actions)

```yaml
# .github/workflows/hito1_determinism.yml
name: Hito 1 Determinism Check

on: [push, pull_request]

jobs:
  determinism:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Check VisibleVariablesEngine determinism
        run: |
          python3 << 'EOF'
          from vigia.engine.visible_variables import VisibleVariablesEngine
          
          bundle = {
              "bundle_id": "ci_test",
              "signals": [{"label": "test", "type": "signal"}],
              "temporal_violations": [],
              "mitre_ttps": [],
          }
          
          hashes = set()
          for _ in range(5):
              focus = VisibleVariablesEngine().analyze_focus(**bundle)
              hashes.add(focus.focus_hash)
          
          assert len(hashes) == 1, f"No deterministic! Hashes: {hashes}"
          print("✓ Determinism OK")
          EOF
```

## 8. DOCUMENTACIÓN EN TU README.md

Agregar sección:

```markdown
### Módulos Hito 1 (VIGÍA Visible Variables + PICERL-I)

VIGÍA implementa **Lazy Abstraction** (Vizel/Technion) + **Terceridad Peirceana** para IR forense:

- **`vigia/engine/visible_variables.py`**: Detecta fase de IR + filtra variables relevantes
- **`vigia/forensics/picerl_mapping.py`**: Genera hipótesis de intención (PICERL-compatible)
- **`vigia/governance/trust_levels.py`**: Verificación en 4 niveles (等保2.0)

#### Uso rápido

```python
from vigia.engine.visible_variables import analyze_bundle_focus
from vigia.forensics.picerl_mapping import generate_picerl_i_from_focus

focus, signals = analyze_bundle_focus(forensic_bundle)
hypotheses, report = generate_picerl_i_from_focus(bundle_id, [focus])
print(report)
```

**Garantías Daubert**:
- ✅ Determinístico (SHA256 reproducible)
- ✅ Falsable (hipótesis con `what_would_falsify`)
- ✅ Metodología aceptada (PICERL, MITRE, CIS)
- ✅ Sin cajanegra (código abierto, solo stdlib)
```

## 9. TROUBLESHOOTING

### "ModuleNotFoundError: No module named 'visible_variables'"

**Solución**: Agregar al PATH:

```python
import sys
sys.path.insert(0, '/path/to/vigia')
from engine.visible_variables import analyze_bundle_focus
```

### "AttributeError: 'str' object has no attribute 'value'"

**Causa**: Enums mal inicializados
**Solución**: Verificar que IRPhase y VariableCategory están siendo importados correctamente

```python
from visible_variables import IRPhase, VariableCategory
# No: from visible_variables import * (puede causar conflictos)
```

### Hash reproducible divergente

**Causa**: Orden de diccionarios (Python 3.7+ debería estar OK)
**Solución**: Verificar que `json.dumps` usa `sort_keys=True` en todos lados

## 10. PRÓXIMOS PASOS

1. **Hoy**: Integrar visible_variables.py en tu pipeline
2. **Mañana**: Testear con case_002 y otros casos
3. **Semana 1**: Implementar Hito 2.1 (AbductiveIntentEngine)
4. **Semana 2**: Auditoría de seguridad previa a GitHub

---

**Quick reference**: 
- 3 módulos
- 450 líneas
- 0 dependencias externas requeridas
- 100% determinístico
- Listo para Daubert
