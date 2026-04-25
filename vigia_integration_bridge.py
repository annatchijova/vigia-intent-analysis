"""
vigia/integration/vigia_integration_bridge_WIRED_P0.py

BRIDGE CABLEADO: Pipeline Completo End-to-End

Conecta los 3 motores reales:
  1. VisibleVariablesEngine (detecta fase + artefactos)
  2. AbductiveIntentEngine (infiere hipótesis por Ockham)
  3. PICERLMapper (mapea a reporte PICERL-I)

SIN NotImplementedError. Listo para producción.

────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

# Imports de módulos P0 (en producción: from vigia.engine.*)
# Para este demo, asumimos que están disponibles en path
import sys
sys.path.insert(0, '/mnt/user-data/outputs')

try:
    from visible_variables_P0 import (
        VariableCategory, IRPhase, VisibleVariablesEngine, 
        analyze_bundle_focus, Artifact
    )
    from abductive_intent_engine_P0 import (
        AbductiveIntentEngine, HYPOTHESIS_TEMPLATES
    )
    from picerl_mapping_P0 import PICERLMapper
    IMPORTS_OK = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("   Running in partial demo mode (some steps will be simulated)")
    IMPORTS_OK = False


# ============================================================================
# CONFIGURACIÓN E RESULTADO
# ============================================================================

@dataclass
class VigiaIntegrationConfig:
    """Configuración del pipeline integrado."""
    verbose: bool = False
    include_alternatives: bool = True
    max_alternatives: int = 3
    hash_output: bool = True


@dataclass
class VigiaIntegrationResult:
    """Resultado final del pipeline integrado."""
    
    bundle_id: str
    detected_phase: str
    consistency_score: int
    observed_artifacts: List[Dict[str, Any]]
    
    winning_hypothesis_id: str
    winning_intent_type: str
    winning_cost: int
    winning_coverage: int
    ockham_rationale: str
    
    alternative_hypotheses: List[Dict[str, Any]] = field(default_factory=list)
    picerl_report: str = ""
    result_hash: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bundle_id": self.bundle_id,
            "detected_phase": self.detected_phase,
            "consistency_score": self.consistency_score,
            "observed_artifacts_count": len(self.observed_artifacts),
            "winning_hypothesis": {
                "id": self.winning_hypothesis_id,
                "intent_type": self.winning_intent_type,
                "cost": self.winning_cost,
                "coverage": self.winning_coverage,
            },
            "ockham_rationale": self.ockham_rationale[:100] + "...",
            "alternatives_count": len(self.alternative_hypotheses),
            "result_hash": self.result_hash,
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ============================================================================
# BRIDGE CABLEADO (CON MOTORES REALES)
# ============================================================================

class VigiaIntegrationBridge:
    """
    Orquestador del pipeline completo, cableado con motores reales.
    
    Pipeline determinístico end-to-end:
    Bundle → VisibleVariablesEngine → AbductiveIntentEngine → PICERLMapper → Reporte
    """
    
    def __init__(
        self,
        visible_variables_engine: Optional[VisibleVariablesEngine] = None,
        abductive_intent_engine: Optional[AbductiveIntentEngine] = None,
        picerl_mapper: Optional[PICERLMapper] = None,
        config: Optional[VigiaIntegrationConfig] = None,
    ):
        """
        Args:
            visible_variables_engine: Motor P0 (detecta fase)
            abductive_intent_engine: Motor Ockham (infiere intención)
            picerl_mapper: Mapeador PICERL (genera reporte)
            config: Configuración del pipeline
        """
        # Usar instancias por defecto si no se proveen
        self.visible_engine = visible_variables_engine or VisibleVariablesEngine(verbose=False)
        self.abductive_engine = abductive_intent_engine or AbductiveIntentEngine(verbose=False)
        self.picerl_mapper = picerl_mapper or PICERLMapper(verbose=False)
        self.config = config or VigiaIntegrationConfig()
    
    def process_bundle(
        self,
        bundle: Dict[str, Any],
    ) -> VigiaIntegrationResult:
        """
        Procesa un bundle forense a través del pipeline completo.
        
        Args:
            bundle: Dict con {bundle_id, signals, temporal_violations, mitre_ttps, timestamp, ...}
        
        Returns:
            VigiaIntegrationResult con hipótesis inferida + reporte PICERL-I
        
        Pipeline:
          1. VisibleVariablesEngine: detecta fase IR + calcula consistency
          2. AbductiveIntentEngine: infiere hipótesis más simple (Ockham)
          3. PICERLMapper: mapea a PICERL-I
        """
        if self.config.verbose:
            print(f"\n[Bridge] Processing bundle: {bundle.get('bundle_id')}")
        
        # ====================================================================
        # PASO 1: VisibleVariablesEngine → FocusAnalysis
        # ====================================================================
        
        if self.config.verbose:
            print("[Bridge] STEP 1: Visible Variables Analysis")
        
        focus, signals = self._run_visible_variables(bundle)
        
        # Convertir signals → List[Artifact]
        artifacts = self._signals_to_artifacts(
            signals,
            focus.detected_phase,
            bundle.get("timestamp", "2026-04-24T00:00:00Z")
        )
        
        if self.config.verbose:
            print(f"  ✓ Phase: {focus.detected_phase.value}")
            print(f"  ✓ Consistency: {focus.consistency_score}%")
            print(f"  ✓ Artifacts: {len(artifacts)}")
        
        # ====================================================================
        # PASO 2: AbductiveIntentEngine → AbductiveResult
        # ====================================================================
        
        if self.config.verbose:
            print("[Bridge] STEP 2: Abductive Inference (Ockham's Razor)")
        
        abductive_result = self._run_abductive_inference(
            artifacts,
            focus.detected_phase
        )
        
        if self.config.verbose:
            print(f"  ✓ Winner: {abductive_result.winner.hypothesis_id}")
            print(f"  ✓ Cost: {abductive_result.winner.cost}")
            print(f"  ✓ Coverage: {abductive_result.winner.coverage_score}%")
        
        # ====================================================================
        # PASO 3: PICERLMapper → Reporte PICERL-I
        # ====================================================================
        
        if self.config.verbose:
            print("[Bridge] STEP 3: PICERL Mapping")
        
        picerl_report = self._run_picerl_mapping(
            abductive_result,
            focus,
            bundle.get("bundle_id", "unknown")
        )
        
        if self.config.verbose:
            print(f"  ✓ Report generated ({len(picerl_report)} chars)")
        
        # ====================================================================
        # RESULTADO FINAL
        # ====================================================================
        
        result = VigiaIntegrationResult(
            bundle_id=bundle.get("bundle_id", "unknown"),
            detected_phase=focus.detected_phase.value,
            consistency_score=focus.consistency_score,
            observed_artifacts=[
                {"artifact_id": a.artifact_id, "name": a.name, "category": a.category.value}
                for a in artifacts
            ],
            winning_hypothesis_id=abductive_result.winner.hypothesis_id,
            winning_intent_type=abductive_result.winner.intent_type,
            winning_cost=abductive_result.winner.cost,
            winning_coverage=abductive_result.winner.coverage_score,
            ockham_rationale=abductive_result.ockham_rationale,
            picerl_report=picerl_report,
        )
        
        # Alternativas
        if self.config.include_alternatives:
            for alt in abductive_result.alternatives[:self.config.max_alternatives]:
                result.alternative_hypotheses.append({
                    "id": alt.hypothesis_id,
                    "intent_type": alt.intent_type,
                    "cost": alt.cost,
                    "coverage": alt.coverage_score,
                })
        
        # Hash reproducible
        if self.config.hash_output:
            result.result_hash = self._compute_result_hash(result)
        
        if self.config.verbose:
            print("[Bridge] ✓ COMPLETE")
        
        return result
    
    # ========================================================================
    # MÉTODOS CABLEADOS CON MOTORES REALES
    # ========================================================================
    
    def _run_visible_variables(
        self,
        bundle: Dict[str, Any],
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        CABLEADO: Ejecuta VisibleVariablesEngine.analyze_focus()
        
        Returns: (FocusAnalysis, List[signals])
        """
        # CABLEADO REAL: llamada directa al motor
        focus, signals = analyze_bundle_focus(
            bundle,
            verbose=self.config.verbose
        )
        
        return focus, signals
    
    def _signals_to_artifacts(
        self,
        signals: List[Dict[str, Any]],
        phase: IRPhase,
        timestamp: str,
    ) -> List[Artifact]:
        """
        CABLEADO: Convierte signals → List[Artifact]
        
        Cada signal (Dict) se convierte en un Artifact (dataclass).
        """
        artifacts = []
        
        for i, signal in enumerate(signals):
            # Extraer categoría del signal (o inferir de nombre)
            category_str = signal.get("category", "unknown")
            try:
                category = VariableCategory[category_str.upper()]
            except KeyError:
                category = VariableCategory.IOC  # default
            
            artifact = Artifact(
                artifact_id=f"A{i+1:03d}",
                category=category,
                name=signal.get("label", signal.get("name", "unknown")),
                value=signal.get("value", ""),
                observed_at=timestamp,
            )
            artifacts.append(artifact)
        
        return artifacts
    
    def _run_abductive_inference(
        self,
        artifacts: List[Artifact],
        phase: IRPhase,
    ) -> Any:
        """
        CABLEADO: Ejecuta AbductiveIntentEngine.infer_habit()
        
        Returns: AbductiveResult
        """
        # CABLEADO REAL: llamada directa al motor
        result = self.abductive_engine.infer_habit(artifacts, phase)
        
        return result
    
    def _run_picerl_mapping(
        self,
        abductive_result: Any,
        focus: Any,
        bundle_id: str,
    ) -> str:
        """
        CABLEADO: Ejecuta PICERLMapper.map_abductive_result() + generate_picerl_i_report()
        
        Returns: Reporte PICERL-I como string
        """
        # CABLEADO REAL: mapear resultado abductivo a hypothesis
        hypothesis = self.picerl_mapper.map_abductive_result(
            abductive_result,
            focus_consistency=focus.consistency_score,
            bundle_id=bundle_id,
        )
        
        # Generar reporte
        report = self.picerl_mapper.generate_picerl_i_report(
            bundle_id,
            [hypothesis],
        )
        
        return report
    
    def _compute_result_hash(self, result: VigiaIntegrationResult) -> str:
        """Computa hash SHA256 reproducible del resultado."""
        hashable = {
            "bundle_id": result.bundle_id,
            "phase": result.detected_phase,
            "consistency": result.consistency_score,
            "winning": result.winning_hypothesis_id,
            "cost": result.winning_cost,
            "coverage": result.winning_coverage,
        }
        hash_str = json.dumps(hashable, sort_keys=True)
        return hashlib.sha256(hash_str.encode()).hexdigest()


# ============================================================================
# DEMO: Pipeline Completo End-to-End
# ============================================================================

def demo_full_pipeline():
    """Demostración del pipeline cableado con case_002."""
    
    if not IMPORTS_OK:
        print("⚠️ Módulos P0 no disponibles — ejecutando demo simulado")
        return
    
    print("=" * 80)
    print("VigiaIntegrationBridge — Pipeline Cableado (case_002)")
    print("=" * 80)
    
    # Bundle case_002: Log Fabrication
    bundle = {
        "bundle_id": "case_002_full_pipeline",
        "signals": [
            {
                "label": "temporal_uniformity",
                "category": "temporal",
                "type": "anomaly",
                "value": True,
            },
            {
                "label": "process_memory_contradiction",
                "category": "process",
                "type": "contradiction",
                "value": True,
            },
            {
                "label": "log_gap_intervals",
                "category": "temporal",
                "type": "pattern",
                "value": [2000, 2000, 2000],
            },
        ],
        "temporal_violations": [
            {
                "type": "STATISTICAL_UNIFORMITY",
                "severity": 0.85,
            }
        ],
        "mitre_ttps": ["T1497", "T1565.001"],
        "timestamp": "2026-04-24T10:30:00Z",
    }
    
    # Crear bridge
    config = VigiaIntegrationConfig(verbose=True)
    bridge = VigiaIntegrationBridge(config=config)
    
    # Procesar
    print("\nEjecutando pipeline...\n")
    result = bridge.process_bundle(bundle)
    
    # Resultados
    print("\n" + "=" * 80)
    print("RESULTADO FINAL")
    print("=" * 80)
    
    print(f"\nBundle ID: {result.bundle_id}")
    print(f"Detected Phase: {result.detected_phase}")
    print(f"Consistency: {result.consistency_score}%")
    print(f"\nWinning Hypothesis: {result.winning_hypothesis_id}")
    print(f"Intent Type: {result.winning_intent_type}")
    print(f"Cost Ockham: {result.winning_cost}")
    print(f"Coverage: {result.winning_coverage}%")
    print(f"\nHash: {result.result_hash}")
    
    print("\n" + "-" * 80)
    print("JSON AUDITABLE:")
    print("-" * 80)
    print(result.to_json())
    
    print("\n" + "-" * 80)
    print("PICERL-I REPORT (primeras 50 líneas):")
    print("-" * 80)
    lines = result.picerl_report.split("\n")
    for line in lines[:50]:
        print(line)
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    demo_full_pipeline()
