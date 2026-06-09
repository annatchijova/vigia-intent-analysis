"""
Collapse Decision Layer (CDL) - V2 AGGRESSIVE

Regla principal: cualquier ruptura de sensor_independence → INCONCLUSIVE
"""

from enum import Enum
from typing import Set
from dataclasses import dataclass


class CollapseVerdict(Enum):
    MALICE = "MALICE"
    SUSPICION = "SUSPICION"
    INCONCLUSIVE = "INCONCLUSIVE"
    NOISE = "NOISE"


@dataclass
class CollapseContext:
    broken_assumptions: Set[str]
    coverage_ratio: float
    base_score: float
    has_structural_malice: bool
    independent_sources: int


class CollapseDecisionLayer:
    """Política agresiva: sensor_independence roto = INCONCLUSIVE"""
    
    def resolve(self, ctx: CollapseContext) -> CollapseVerdict:
        broken = ctx.broken_assumptions
        
        # REGLA CLAVE: sensor_independence roto → INCONCLUSIVE
        if "sensor_independence" in broken:
            return CollapseVerdict.INCONCLUSIVE
        
        # Otras reglas
        if "pipeline_integrity" in broken:
            return CollapseVerdict.INCONCLUSIVE
        
        if len(broken) >= 2:
            return CollapseVerdict.INCONCLUSIVE
        
        if ctx.coverage_ratio < 0.3:
            return CollapseVerdict.INCONCLUSIVE
        
        # Sin colapso
        if ctx.has_structural_malice:
            return CollapseVerdict.MALICE
        if ctx.base_score >= 0.5:
            return CollapseVerdict.MALICE
        if ctx.base_score >= 0.2:
            return CollapseVerdict.SUSPICION
        return CollapseVerdict.NOISE
    
    def explain(self, ctx: CollapseContext, verdict: CollapseVerdict) -> str:
        if verdict == CollapseVerdict.INCONCLUSIVE:
            if "sensor_independence" in ctx.broken_assumptions:
                return "INCONCLUSIVE: Sensor independence broken - cannot trust evidence correlation"
            if "pipeline_integrity" in ctx.broken_assumptions:
                return "INCONCLUSIVE: Pipeline integrity compromised"
            if len(ctx.broken_assumptions) >= 2:
                return f"INCONCLUSIVE: {len(ctx.broken_assumptions)} assumptions broken"
            if ctx.coverage_ratio < 0.3:
                return f"INCONCLUSIVE: Coverage too low ({ctx.coverage_ratio:.1%})"
        return "Standard verdict"
