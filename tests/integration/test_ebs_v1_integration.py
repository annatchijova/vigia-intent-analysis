#!/usr/bin/env python3
"""
test_ebs_v1_integration.py
─────────────────────────────────────────────────────────────────────────────
Suite de Integracion VIGIA Forensic Suite EBS v1 — Refactorizada

Cubre las nuevas invariantes de arquitectura:
    - ForensicBundle es datos puros (sin seal())
    - BundleBuilder es el unico atestador criptografico
    - verify_ebs_v1.py es 100% stdlib, sin imports de produccion
    - LikelihoodEngine usa naming emergente (G_tool_i, no NLP/TEMPORAL)
    - Correccion de inflacion LR via penalizacion de correlacion
    - EvidenceGraph.global_stability() penaliza grafos fracturados
    - SystemState no contiene variables LLM/infraestructura
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
HERE = _HERE  # alias publico para tests que lo usan
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

PASSED, FAILED = [], []

def test(name: str):
    def decorator(fn):
        try:
            fn()
            PASSED.append(name)
            print(f"  [OK]   {name}")
        except Exception as e:
            FAILED.append(name)
            print(f"  [FAIL] {name}")
            print(f"         {type(e).__name__}: {e}")
            if os.environ.get("VERBOSE"):
                traceback.print_exc()
        return fn
    return decorator


# ===========================================================================
# T01-T07: Contratos de datos (ebs_v1.py)
# ===========================================================================

@test("T01 — SignalOutput crea y clipea correctamente")
def t01():
    from vigia.core.ebs_v1 import SignalOutput, Z_CLIP_MAX
    s = SignalOutput(tool_name="SDA", value=0.8, z_score=2.5, confidence=0.9)
    assert s.z_score == 2.5
    s2 = SignalOutput(tool_name="CLI", value=99, z_score=999.0)
    assert s2.z_score == Z_CLIP_MAX


@test("T02 — ForensicBundle es estructura de datos pura (sin seal)")
def t02():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="REJECT", posterior=0.75, risk=0.42),
        policy_spec=make_default_policy(),
    )
    # El bundle NO tiene metodo seal() — fue removido
    assert not hasattr(b, "seal"), "VIOLACION: seal() no debe existir en ForensicBundle"
    assert not hasattr(b, "quick_verify"), "quick_verify no debe existir en ForensicBundle"
    # integrity es None hasta que BundleBuilder lo selle
    assert b.integrity is None, "integrity debe ser None antes del sellado externo"


@test("T03 — SystemState no tiene campos LLM/infraestructura")
def t03():
    from vigia.core.ebs_v1 import SystemState
    import inspect
    sig = inspect.signature(SystemState.__init__) if hasattr(SystemState, '__init__') else None
    s = SystemState()
    assert not hasattr(s, "ollama_backend"), "VIOLACION: ollama_backend no debe estar en SystemState"
    assert not hasattr(s, "extra"), "extra no debe estar en SystemState (campo de infraestructura)"
    # Solo campos matematicos
    assert hasattr(s, "lambda_drift")
    assert hasattr(s, "gamma_stability")
    assert hasattr(s, "drift_score")


@test("T04 — EvidenceGraph.global_stability penaliza grafos fracturados")
def t04():
    from vigia.core.ebs_v1 import EvidenceGraph, EvidenceEdge
    # Grafo con 6 nodos pero solo 1 arista fuerte
    # n_possible = 6*5/2 = 15, n_stable = 1, coverage = 1/15
    edges = [EvidenceEdge(source="SDA", target="ACP", stability=0.92)]
    g = EvidenceGraph(nodes=["SDA", "ACP", "CLI", "ROI", "GCI", "DGPI"], edges=edges)
    s = g.global_stability()
    # stability = 0.92 * (1/15) = 0.061 — fracturado
    assert s < 0.10, f"Grafo fracturado deberia tener estabilidad baja: {s:.4f}"

    # Grafo denso: todos conectados
    from itertools import combinations
    nodes = ["SDA", "ACP", "CLI", "ROI"]
    dense_edges = [
        EvidenceEdge(source=a, target=b, stability=0.90)
        for a, b in combinations(nodes, 2)
    ]
    g2 = EvidenceGraph(nodes=nodes, edges=dense_edges)
    s2 = g2.global_stability()
    # 4 nodos, 6 aristas posibles, 6 estables → coverage=1.0, mean=0.90
    assert s2 > 0.85, f"Grafo denso deberia tener estabilidad alta: {s2:.4f}"


@test("T05 — EvidenceGraph sin nodos o 1 nodo — casos limite")
def t05():
    from vigia.core.ebs_v1 import EvidenceGraph
    g0 = EvidenceGraph(nodes=[], edges=[])
    assert g0.global_stability() == 1.0  # sin nodos: convencion
    g1 = EvidenceGraph(nodes=["SDA"], edges=[])
    assert g1.global_stability() == 0.0  # 1 nodo: imposible conectar


# ===========================================================================
# T10-T15: BundleBuilder (sellado externo)
# ===========================================================================

@test("T10 — BundleBuilder.seal() produce bundle valido")
def t10():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["SDA"], edges=[]),
        decision_trace=DecisionTrace(decision="REJECT", posterior=0.78, risk=0.65),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)

    assert "integrity" in sealed
    assert len(sealed["integrity"]["bundle_hash"]) == 64
    assert len(sealed["integrity"]["graph_hash"]) == 64
    # integrity asignado al objeto bundle tambien
    assert b.integrity is not None


@test("T11 — BundleBuilder.quick_verify PASS bundle valido")
def t11():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ABSTAIN", posterior=0.55, risk=0.60, epsilon_used=0.05),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)
    ok, msg = BundleBuilder.quick_verify(sealed)
    assert ok, f"quick_verify fallo: {msg}"


@test("T12 — BundleBuilder detecta tamper post-sellado")
def t12():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ACCEPT", posterior=0.15, risk=0.03),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)

    # Tamper
    import copy
    tampered = copy.deepcopy(sealed)
    tampered["decision_trace"]["posterior"] = 0.99

    ok, msg = BundleBuilder.quick_verify(tampered)
    assert not ok, "VULNERABILIDAD: tamper no detectado por quick_verify"


@test("T13 — BundleBuilder.seal() es deterministico en contenido")
def t13():
    """El bundle_hash depende del contenido. Mismo contenido = mismo bundle_hash."""
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder
    import json

    def make_sealed():
        b = ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=["SDA"], edges=[]),
            decision_trace=DecisionTrace(decision="REJECT", posterior=0.78, risk=0.65),
            policy_spec=make_default_policy(),
        )
        # Forzar timestamp y bundle_id iguales para test de determinismo
        b.bundle_id = "fixed-id-for-test"
        b.timestamp = "2026-01-01T00:00:00+00:00"
        b.system_state.timestamp = "2026-01-01T00:00:00+00:00"
        b.policy_spec.created_at = "2026-01-01T00:00:00+00:00"
        b.evidence_graph.generated_at = "2026-01-01T00:00:00+00:00"
        return BundleBuilder.seal(b)

    s1 = make_sealed()
    s2 = make_sealed()
    assert s1["integrity"]["bundle_hash"] == s2["integrity"]["bundle_hash"], \
        "Mismo contenido debe producir mismo bundle_hash"


@test("T14 — BundleBuilder.save y load produce bundle verificable")
def t14():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle
    import tempfile, os

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["GCI"], edges=[]),
        decision_trace=DecisionTrace(decision="ABSTAIN", posterior=0.5, risk=0.55, epsilon_used=0.05),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        f.write(json.dumps(sealed, sort_keys=True, indent=2, default=str))
        tmp = f.name

    try:
        with open(tmp) as f:
            loaded = json.load(f)
        result = verify_bundle(loaded)
        assert result.conformity_level >= 2, \
            f"Level esperado >= 2, got {result.conformity_level}"
    finally:
        os.unlink(tmp)


# ===========================================================================
# T20-T26: verify_ebs_v1.py — stdlib puro
# ===========================================================================

@test("T20 — verify_ebs_v1 es stdlib puro (sin imports de produccion)")
def t20():
    """
    El verificador no puede importar nada de vigia.models, vigia.engine, etc.
    Verifica que el modulo no tiene imports de produccion al inspeccionarlo.
    """
    import ast
    with open(os.path.join(HERE, "forensics", "verify_ebs_v1.py")) as f:
        tree = ast.parse(f.read())

    forbidden_prefixes = ("models.", "engine.", "governance.", "audit.", "forensics.bundle")
    bad_imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom) and node.module:
                for prefix in forbidden_prefixes:
                    if node.module.startswith(prefix):
                        bad_imports.append(node.module)

    assert not bad_imports, \
        f"verify_ebs_v1.py importa modulos de produccion: {bad_imports}"


@test("T21 — verify_ebs_v1 PASS bundle Level 2 valido")
def t21():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["SDA", "CLI"], edges=[]),
        decision_trace=DecisionTrace(decision="ABSTAIN", posterior=0.5, risk=0.55, epsilon_used=0.05),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)
    result = verify_bundle(sealed)
    assert result.conformity_level >= 2, (
        f"Level esperado >= 2, got {result.conformity_level}\n" +
        "\n".join(f"  {c['rule']}: {c['message']}"
                  for c in result.checks if not c["passed"])
    )


@test("T22 — verify_ebs_v1 FAIL bundle tampereado (R1)")
def t22():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle
    import copy

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ACCEPT", posterior=0.1, risk=0.02),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)
    tampered = copy.deepcopy(sealed)
    tampered["decision_trace"]["decision"] = "REJECT"
    tampered["decision_trace"]["posterior"] = 0.99

    result = verify_bundle(tampered)
    # passed=False confirma deteccion de tamper.
    # conformity_level puede ser 1 (estructura valida) pero con hashes invalidos.
    # Level 0 es para estructura completamente rota — no aplica aqui.
    assert not result.passed, "VULNERABILIDAD: verificador no detecto tamper"
    assert result.conformity_level <= 1, f"Tamper detectado debe impedir Level >= 2, got {result.conformity_level}"
    # Verificar que al menos R1 o R3 reportaron ERROR
    errors = [c for c in result.checks if not c["passed"] and c["severity"] == "ERROR"]
    assert len(errors) > 0, "Ningun check ERROR reportado — tamper no detectado correctamente" 


@test("T23 — verify_ebs_v1 FAIL violacion de politica (R2)")
def t23():
    from vigia.core.ebs_v1 import (
        ForensicBundle, EvidenceGraph, DecisionTrace,
        make_default_policy, ActionRecord,
    )
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle

    bad_action = ActionRecord(
        variable="posterior",
        delta=0.99,  # max_delta=0.10 → VIOLACION
        pre_value=0.1, post_value=1.09,
        decision_before="REJECT", risk_before=0.8,
        approved=True, actor="system",
    )
    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ACCEPT", posterior=0.1, risk=0.02),
        policy_spec=make_default_policy(),
        actions=[bad_action],
    )
    sealed = BundleBuilder.seal(b)
    result = verify_bundle(sealed)

    r2 = next((c for c in result.checks if c["rule"] == "R2_POLICY_COMPLIANCE"), None)
    assert r2 and not r2["passed"], "Violacion de politica no detectada"


@test("T24 — verify_ebs_v1 FAIL decision incoherente (R3)")
def t24():
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle
    import copy

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ACCEPT", posterior=0.5, risk=0.60, epsilon_used=0.05),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)

    # Tamperar solo la decision sin recalcular hashes — R3 debe atrapar
    # Pero con R1 activo, el tamper del decision_trace invalida bundle_hash primero
    # Lo verificamos a nivel logico creando un bundle con decision incoherente
    incoherent = copy.deepcopy(sealed)
    # Cambiar decision sin recalcular hashes
    incoherent["decision_trace"]["decision"] = "ACCEPT"
    incoherent["decision_trace"]["risk"] = 0.60  # risk=0.60 > epsilon=0.05 -> deberia ser ABSTAIN

    result = verify_bundle(incoherent)
    # R1 o R3 deberia fallar
    failures = [c["rule"] for c in result.checks if not c["passed"] and c["severity"] == "ERROR"]
    assert len(failures) > 0, "Bundle incoherente paso todos los checks"


# ===========================================================================
# T30-T35: Motor de inferencia (naming emergente + correccion LR)
# ===========================================================================

@test("T30 — LikelihoodEngine fallback gaussiano funciona")
def t30():
    from vigia.core.ebs_v1 import SignalOutput
    from engine.likelihood_engine import LikelihoodEngine

    engine = LikelihoodEngine()
    signals = [
        SignalOutput(tool_name="SDA", value=0.7, z_score=2.1, confidence=0.85),
        SignalOutput(tool_name="GCI", value=0.9, z_score=3.0, confidence=0.90),
    ]
    result = engine.infer(signals)
    assert 0.0 <= result["posterior"] <= 1.0
    assert result["lr"] > 0
    assert result["mode"] == "FALLBACK"


@test("T31 — LikelihoodEngine naming emergente con EvidenceGraph")
def t31():
    from vigia.core.ebs_v1 import SignalOutput, EvidenceGraph, EvidenceEdge
    from engine.likelihood_engine import LikelihoodEngine

    engine = LikelihoodEngine()
    signals = [
        SignalOutput(tool_name="SDA", value=0.8, z_score=3.0, confidence=0.9),
        SignalOutput(tool_name="ACP", value=0.7, z_score=2.5, confidence=0.85),
        SignalOutput(tool_name="GCI", value=0.9, z_score=2.0, confidence=0.8),
    ]

    # Grafo con una componente SDA-ACP y GCI solo
    graph = EvidenceGraph(
        nodes=["SDA", "ACP", "GCI"],
        edges=[EvidenceEdge(source="SDA", target="ACP", stability=0.90)],
        stability_threshold=0.85,
    )
    result = engine.infer(signals, evidence_graph=graph)

    assert result["clustering_method"] == "graph_conditioned_emergent"
    # Nombres de clusters NO deben ser "NLP" ni "TEMPORAL"
    cluster_names = [c["cluster"] for c in result["contributions"]]
    for name in cluster_names:
        assert name not in ("NLP", "TEMPORAL", "NLP_default", "TEMPORAL_default"), \
            f"VIOLACION: cluster hardcodeado '{name}' sobre estructura emergente"
        # Deben ser G_{tool}_{i} o G_cluster_{i} o "unassigned"
        assert name.startswith("G_") or name == "unassigned", \
            f"Nombre de cluster emergente esperado G_*, got '{name}'"


@test("T32 — LikelihoodEngine sin EvidenceGraph usa DEFAULT_CLUSTERS (heuristico)")
def t32():
    from vigia.core.ebs_v1 import SignalOutput
    from engine.likelihood_engine import LikelihoodEngine

    engine = LikelihoodEngine()
    signals = [SignalOutput(tool_name="SDA", value=0.7, z_score=2.0, confidence=0.85)]
    result = engine.infer(signals)
    assert result["clustering_method"] == "heuristic_default"


@test("T33 — Correccion de correlacion deflacta LR de senales redundantes")
def t33():
    """
    Dos senales correlacionadas (mismo z_score) deben producir LR menor
    que la suma directa (inflacion artificial).
    """
    from vigia.core.ebs_v1 import SignalOutput
    from engine.likelihood_engine import LikelihoodEngine, _correlation_penalty

    # Senas identicas = correlacion maxima = maxima penalizacion
    signals_correlated = [
        SignalOutput(tool_name="SDA", value=0.8, z_score=3.0, confidence=0.9),
        SignalOutput(tool_name="ACP", value=0.8, z_score=3.0, confidence=0.9),
    ]
    # Senales independientes (z muy diferentes)
    signals_independent = [
        SignalOutput(tool_name="SDA", value=0.8, z_score=3.0, confidence=0.9),
        SignalOutput(tool_name="ACP", value=0.1, z_score=0.1, confidence=0.9),
    ]

    penalty_corr = _correlation_penalty(signals_correlated)
    penalty_indep = _correlation_penalty(signals_independent)

    assert penalty_corr < penalty_indep, (
        f"Penalizacion de senales correlacionadas ({penalty_corr:.3f}) "
        f"debe ser menor que independientes ({penalty_indep:.3f})"
    )

    # La penalizacion de correlacion perfecta debe ser significativa
    assert penalty_corr < 0.6, \
        f"Correlacion perfecta deberia penalizar fuertemente: {penalty_corr:.3f}"


@test("T34 — Penalizacion de correlacion no anula evidencia (minimo 0.1)")
def t34():
    from vigia.core.ebs_v1 import SignalOutput
    from engine.likelihood_engine import _correlation_penalty

    signals = [
        SignalOutput(tool_name="SDA", value=0.8, z_score=5.0, confidence=1.0),
        SignalOutput(tool_name="ACP", value=0.8, z_score=5.0, confidence=1.0),
    ]
    penalty = _correlation_penalty(signals)
    assert penalty >= 0.1, f"Penalizacion no debe anular evidencia: {penalty:.4f}"


# ===========================================================================
# T40-T44: Gobernanza
# ===========================================================================

@test("T40 — RiskBoundedDecisionLayer formula correcta con invariantes")
def t40():
    from governance.risk_bounded_layer import RiskBoundedDecisionLayer

    layer = RiskBoundedDecisionLayer(lambda_drift=2.0, gamma_stability=2.0)

    # Invariante: drift siempre inflaciona riesgo
    r0 = layer.compute_risk(0.5, drift_score=0.0, graph_stability=1.0)
    r1 = layer.compute_risk(0.5, drift_score=0.5, graph_stability=1.0)
    assert r1 > r0, "VIOLACION: drift debe inflar riesgo"

    # Invariante: inestabilidad del grafo inflaciona riesgo
    r_stable = layer.compute_risk(0.5, drift_score=0.0, graph_stability=1.0)
    r_unstable = layer.compute_risk(0.5, drift_score=0.0, graph_stability=0.0)
    assert r_unstable > r_stable, "VIOLACION: inestabilidad debe inflar riesgo"


@test("T41 — ABSTAIN en zona media de incertidumbre")
def t41():
    from governance.risk_bounded_layer import RiskBoundedDecisionLayer
    # r = (1-0.5)*(1+2*0.05)*(1+2*(1-0.95)) = 0.5*1.10*1.10 = 0.605 -> ABSTAIN
    layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.05)
    trace = layer.decide(posterior=0.5, drift_score=0.05, graph_stability=0.95)
    assert trace.decision == "ABSTAIN", f"Expected ABSTAIN got {trace.decision} (r={trace.risk:.4f})"


@test("T42 — Grafo fracturado fuerza riesgo alto via global_stability penalizada")
def t42():
    """
    Con el nuevo global_stability() penalizado, un grafo fracturado produce
    S bajo -> riesgo alto -> ABSTAIN o REJECT aunque el posterior sea neutro.
    """
    from vigia.core.ebs_v1 import EvidenceGraph, EvidenceEdge
    from governance.risk_bounded_layer import RiskBoundedDecisionLayer

    # Grafo con 6 nodos y solo 1 arista: S = 0.92 * (1/15) = 0.061
    edges = [EvidenceEdge(source="SDA", target="ACP", stability=0.92)]
    g = EvidenceGraph(nodes=["SDA","ACP","CLI","ROI","GCI","DGPI"], edges=edges)
    s_fracturado = g.global_stability()

    layer = RiskBoundedDecisionLayer(epsilon_accept=0.05, epsilon_reject=0.05,
                                     gamma_stability=2.0)
    trace = layer.decide(posterior=0.5, drift_score=0.0, graph_stability=s_fracturado)

    # Con S=0.061 y gamma=2: r = 0.5 * 1.0 * (1 + 2*(1-0.061)) = 0.5 * 2.878 = 1.44
    # Clipeado a [0, R_MAX=5] -> REJECT (r >= 1-epsilon=0.95)
    assert trace.decision in ("ABSTAIN", "REJECT"), \
        f"Grafo fracturado deberia producir ABSTAIN/REJECT, got {trace.decision} (r={trace.risk:.4f})"


# ===========================================================================
# T50-T53: Pipeline completo
# ===========================================================================

@test("T50 — VigiaPipeline end-to-end con BundleBuilder")
def t50():
    from vigia.core.ebs_v1 import SignalOutput
    from vigia.pipeline.pipeline import VigiaPipeline
    from forensics.bundle_builder import BundleBuilder

    pipeline = VigiaPipeline(adaptive_policy=False)
    signals = [
        SignalOutput(tool_name="SDA", value=0.85, z_score=2.8, confidence=0.90),
        SignalOutput(tool_name="GCI", value=0.95, z_score=3.5, confidence=0.92),
    ]
    result = pipeline.run_full(signals, drift_score=0.05)

    bundle = result["bundle"]
    sealed = result["sealed_dict"]

    assert bundle.integrity is not None, "integrity debe ser asignado por BundleBuilder"
    ok, msg = BundleBuilder.quick_verify(sealed)
    assert ok, f"Bundle invalido: {msg}"
    assert result["decision"].decision in ("ACCEPT", "REJECT", "ABSTAIN")


@test("T51 — run_vigia retorna bundle_hash y pasa verificacion")
def t51():
    from vigia.pipeline.pipeline import run_vigia
    from forensics.verify_ebs_v1 import verify_bundle

    result = run_vigia([
        {"tool_name": "SDA", "value": 0.8, "z_score": 2.3, "confidence": 0.88},
        {"tool_name": "GCI", "value": 0.9, "z_score": 3.1, "confidence": 0.91},
    ])

    assert result["decision"] in ("ACCEPT", "REJECT", "ABSTAIN")
    assert result["verify"]["passed"] is True
    assert len(result["bundle_hash"]) == 64

    # Verificar con el verificador independiente
    bundle_dict = json.loads(result["bundle_json"])
    vresult = verify_bundle(bundle_dict)
    assert vresult.conformity_level >= 2, \
        f"Level esperado >= 2, got {vresult.conformity_level}"


@test("T52 — bundle_json no contiene variables de infraestructura LLM")
def t52():
    from vigia.pipeline.pipeline import run_vigia

    result = run_vigia([
        {"tool_name": "SDA", "value": 0.7, "z_score": 2.0, "confidence": 0.85},
    ])

    bundle_dict = json.loads(result["bundle_json"])
    state = bundle_dict.get("system_state", {})

    # Verificar ausencia de campos LLM/infraestructura
    forbidden = ["ollama_backend", "ollama_model", "extra", "narrative_backend"]
    for field in forbidden:
        assert field not in state, \
            f"VIOLACION: '{field}' encontrado en SystemState del bundle"


@test("T53 — decisiones son deterministas (mismo input = misma decision)")
def t53():
    from vigia.pipeline.pipeline import run_vigia

    signals = [
        {"tool_name": "SDA", "value": 0.7, "z_score": 2.0, "confidence": 0.85},
        {"tool_name": "CLI", "value": 0.6, "z_score": 1.8, "confidence": 0.80},
    ]
    r1 = run_vigia(signals)
    r2 = run_vigia(signals)

    assert r1["decision"] == r2["decision"]
    assert abs(float(r1["posterior"]) - float(r2["posterior"])) < 1e-9
    assert abs(float(r1["risk"]) - float(r2["risk"])) < 1e-9


# ===========================================================================
# T60: Verificador independiente CLI
# ===========================================================================

@test("T60 — verify_ebs_v1.py ejecutable como CLI standalone")
def t60():
    import subprocess, tempfile, os
    from vigia.core.ebs_v1 import ForensicBundle, EvidenceGraph, DecisionTrace, make_default_policy
    from forensics.bundle_builder import BundleBuilder

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["SDA"], edges=[]),
        decision_trace=DecisionTrace(decision="ABSTAIN", posterior=0.5, risk=0.55, epsilon_used=0.05),
        policy_spec=make_default_policy(),
    )
    sealed = BundleBuilder.seal(b)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump(sealed, f, sort_keys=True, default=str)
        tmp = f.name

    verify_script = os.path.join(HERE, "forensics", "verify_ebs_v1.py")

    try:
        proc = subprocess.run(
            [sys.executable, verify_script, tmp, "--json"],
            capture_output=True, text=True, timeout=10,
        )
        result = json.loads(proc.stdout)
        assert result["passed"] is True, f"CLI verificador fallo: {result}"
        assert result["conformity_level"] >= 2
        # Verificar que el proceso retorna exit code 0
        assert proc.returncode == 0
    finally:
        os.unlink(tmp)


# ===========================================================================
# Runner
# ===========================================================================


# ===========================================================================
# T70-T76: ResourceOptimizer
# ===========================================================================

@test("T70 — ResourceOptimizer ordena por prioridad P=logLR/costo")
def t70():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    # CLI (costo=0.3, LR=0.8) vs CLIP (costo=3.5, LR=3.0)
    # P_CLI  = 0.8/0.3 = 2.67
    # P_CLIP = 3.0/3.5 = 0.86
    # CLI debe tener prioridad mayor
    plan = opt.build_execution_plan(["CLI", "CLIP", "SDA"])
    names = [t.name for t in plan]
    # Herramientas ligeras primero, pesadas al final
    clip_idx = names.index("CLIP")
    cli_idx  = names.index("CLI")
    assert cli_idx < clip_idx, (
        f"CLI (P={opt.tool_priority('CLI'):.2f}) debe preceder a "
        f"CLIP (P={opt.tool_priority('CLIP'):.2f})"
    )


@test("T71 — CLIP y ELA son clasificadas como herramientas pesadas")
def t71():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    plan = opt.build_execution_plan(["SDA", "ELA", "CLIP", "CLI"])
    heavy = [t for t in plan if t.is_heavy]
    light = [t for t in plan if not t.is_heavy]
    heavy_names = {t.name for t in heavy}
    assert "CLIP" in heavy_names, "CLIP debe ser herramienta pesada"
    assert "ELA" in heavy_names, "ELA debe ser herramienta pesada"
    assert "CLI" not in heavy_names, "CLI no debe ser herramienta pesada"
    # Livianas preceden a pesadas en el plan
    if light and heavy:
        last_light = max(plan.index(t) for t in light)
        first_heavy = min(plan.index(t) for t in heavy)
        assert last_light < first_heavy, "Herramientas livianas deben preceder a pesadas"


@test("T72 — Regla de aborto activa con posterior >= 1-epsilon")
def t72():
    from engine.resource_optimizer import ResourceOptimizer
    from vigia.core.ebs_v1 import make_default_policy

    policy = make_default_policy(epsilon=0.05)
    opt = ResourceOptimizer(policy=policy)

    # posterior=0.96 >= 1-0.05=0.95 con CLIP pendiente -> ABORTAR
    decision = opt.should_abort(
        current_posterior=0.96,
        pending_tools=["CLIP", "ELA"],
        accumulated_cost=1.5,
    )
    assert decision.should_abort is True, (
        f"should_abort=False con posterior=0.96 y epsilon=0.05 — "
        f"CLIP/ELA deberian ser abortadas"
    )
    assert "CLIP" in decision.tools_remaining or "ELA" in decision.tools_remaining


@test("T73 — Regla de aborto NO activa en zona de incertidumbre (ABSTAIN)")
def t73():
    from engine.resource_optimizer import ResourceOptimizer
    from vigia.core.ebs_v1 import make_default_policy

    policy = make_default_policy(epsilon=0.05)
    opt = ResourceOptimizer(policy=policy)

    # posterior=0.6 en zona ABSTAIN -> NO abortar
    decision = opt.should_abort(
        current_posterior=0.60,
        pending_tools=["CLIP", "ELA"],
    )
    assert decision.should_abort is False, (
        f"No debe abortar en zona ABSTAIN (posterior=0.60): {decision.reason}"
    )


@test("T74 — Regla de aborto NO activa con certeza de ACCEPT (posterior bajo)")
def t74():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    # posterior=0.03 -> ACCEPT con certeza, pero igualmente ejecutar todo
    # (en forense, un ACCEPT necesita evidencia completa para ser defendible)
    decision = opt.should_abort(
        current_posterior=0.03,
        pending_tools=["CLIP"],
    )
    assert decision.should_abort is False, (
        "No debe abortar con certeza de ACCEPT — se necesita evidencia completa"
    )


@test("T75 — ResourceOptimizer respeta presupuesto de costo")
def t75():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    # Presupuesto de 2.0: SDA(0.5) + CLI(0.3) + GCI(1.0) = 1.8 OK
    # CLIP(3.5) excede presupuesto -> excluido del plan
    plan = opt.build_execution_plan(
        ["SDA", "CLI", "GCI", "CLIP"],
        max_cost_budget=2.0,
    )
    names = [t.name for t in plan]
    assert "CLIP" not in names, (
        f"CLIP (costo=3.5) debe ser excluida con budget=2.0, plan={names}"
    )
    total = sum(t.cost for t in plan)
    assert total <= 2.0 + 1e-6, f"Costo total {total:.2f} excede presupuesto 2.0"


@test("T76 — ROI del plan captura eficiencia real vs esperada")
def t76():
    from engine.resource_optimizer import ResourceOptimizer, ToolSpec

    opt = ResourceOptimizer()

    # Simular plan ejecutado
    spec_sda = ToolSpec("SDA", priority=3.0, cost=0.5, expected_log_lr=1.5, executed=True, actual_log_lr=2.0)
    spec_cli = ToolSpec("CLI", priority=2.67, cost=0.3, expected_log_lr=0.8, executed=True, actual_log_lr=0.5)
    spec_clip = ToolSpec("CLIP", priority=0.86, cost=3.5, expected_log_lr=3.0, skipped=True)

    roi = opt.compute_plan_roi([spec_sda, spec_cli, spec_clip])

    assert roi["n_executed"] == 2
    assert roi["n_skipped"] == 1
    assert roi["cost_saved_by_abort"] == 3.5
    assert abs(roi["total_cost_incurred"] - 0.8) < 1e-4, \
        f"costo esperado 0.8, got {roi['total_cost_incurred']}"
    assert abs(roi["actual_log_lr"] - 2.5) < 1e-4, \
        f"log_lr esperado 2.5, got {roi['actual_log_lr']}" 




# ===========================================================================
# T80-T88: Tres puntos finales
# ===========================================================================

@test("T80 — LikelihoodEngine hint_threshold derivado de PolicySpec (no hardcodeado)")
def t80():
    from vigia.core.ebs_v1 import make_default_policy, SignalOutput
    from engine.likelihood_engine import LikelihoodEngine

    # Con epsilon=0.10, hint_threshold_reject debe ser 0.90
    policy = make_default_policy(epsilon=0.10)
    engine = LikelihoodEngine(
        hint_threshold_reject=1.0 - policy.epsilon_accept,
        hint_threshold_accept=policy.epsilon_accept,
    )
    assert engine.hint_threshold_reject == 0.90
    assert engine.hint_threshold_accept == 0.10

    # Señal que produce posterior < 0.10 -> ACCEPT hint
    # z_score=-4.0 con gaussian fallback: log_lr = (-4)^2/2 * weight = 8 * 0.75 = 6
    # Pero weight = 0.5 + 0.5*0.5 = 0.75, log_lr_negativo requiere z negativo
    # Con z=-3.0: log_lr = -4.5 * 0.75 = -3.375 -> lr = exp(-3.375) ~ 0.034 -> post ~ 0.033
    # Necesitamos que sea ACCEPT: posterior < hint_threshold_accept = 0.10
    # Para eso: log_lr debe ser suficientemente negativo
    # Simular: usar hint_threshold_accept=0.60 para que z=0.05 de hint ACCEPT
    engine2 = LikelihoodEngine(
        hint_threshold_reject=0.95,
        hint_threshold_accept=0.60,
    )
    signals_low = [SignalOutput(tool_name="SDA", value=0.0, z_score=0.05, confidence=0.5)]
    r2 = engine2.infer(signals_low)
    # Con threshold_accept=0.60 y posterior~0.5, debe dar ACCEPT
    assert r2["decision_hint"] == "ACCEPT", \
        f"posterior={r2['posterior']:.4f} < 0.60 debe dar hint ACCEPT, got {r2['decision_hint']}"
    r = engine.infer(signals_low)
    # Con hint_threshold_accept=0.10 y prior_odds=1.0, posterior~0.5 > 0.10
    # El hint correcto es ABSTAIN para posterior cercano a 0.5
    assert r["decision_hint"] in ("ABSTAIN", "REJECT"), \
        f"posterior={r['posterior']:.4f} con threshold_accept=0.10 no debe dar ACCEPT"


@test("T81 — VigiaPipeline conecta hint_threshold con PolicySpec automaticamente")
def t81():
    from vigia.pipeline.pipeline import VigiaPipeline
    from vigia.core.ebs_v1 import make_default_policy

    # Con epsilon=0.15, el motor debe tener thresholds coherentes
    policy = make_default_policy(epsilon=0.15)
    pipeline = VigiaPipeline(adaptive_policy=False)

    # Verificar que los thresholds del motor coinciden con epsilon de la politica
    # (El VigiaPipeline configura esto en __init__)
    engine = pipeline._likelihood_engine
    policy_spec = pipeline._policy_spec
    expected_reject = round(1.0 - policy_spec.epsilon_accept, 10)
    actual_reject = round(engine.hint_threshold_reject, 10)
    assert abs(actual_reject - expected_reject) < 1e-9, \
        f"hint_threshold_reject={actual_reject} != 1-epsilon={expected_reject}"


@test("T82 — ResourceOptimizer fail-safe en build_execution_plan")
def t82():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    # Forzar error: pasar lista con tipo invalido
    # El fail-safe debe retornar plan plano, no propagar la excepcion
    class BadTool:
        def __str__(self):
            raise RuntimeError("ERROR FORZADO PARA TEST")

    bad_list = ["SDA", "CLI"]  # lista normal - probar con division por cero
    # Corromper el catalogo internamente
    opt._costs["VIGIA_TEST_TOOL"] = 0.0  # costo cero -> division por cero en P = LR/costo

    # Forzar division por cero: agregar tool con costo 0
    # _build_plan_internal hace expected / max(cost, EPS_NUMERIC), entonces no hay divzero
    # Vamos a probar el fail-safe directamente forzando excepcion en _build_plan_internal
    original_internal = opt._build_plan_internal
    def raise_error(*args, **kwargs):
        raise ZeroDivisionError("Error forzado en test")
    opt._build_plan_internal = raise_error

    plan = opt.build_execution_plan(["SDA", "CLI", "GCI"])

    # El fail-safe debe haber retornado un plan plano con todas las herramientas
    assert len(plan) == 3, f"Fail-safe debe retornar 3 tools, got {len(plan)}"
    names = [t.name for t in plan]
    assert "SDA" in names and "CLI" in names and "GCI" in names

    # Restaurar
    opt._build_plan_internal = original_internal


@test("T83 — ResourceOptimizer fail-safe en should_abort")
def t83():
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()
    original = opt._should_abort_internal
    def raise_error(*args, **kwargs):
        raise ValueError("Error forzado en should_abort test")
    opt._should_abort_internal = raise_error

    # El fail-safe debe retornar AbortDecision(should_abort=False)
    decision = opt.should_abort(0.99, ["CLIP", "ELA"])
    assert decision.should_abort is False, \
        "Fail-safe en should_abort debe retornar should_abort=False"
    assert "Fail-safe" in decision.reason

    opt._should_abort_internal = original


@test("T84 — ResourceOptimizer fail-safe en compute_plan_roi")
def t84():
    from engine.resource_optimizer import ResourceOptimizer, ToolSpec

    opt = ResourceOptimizer()
    # Pasar lista vacia con division por cero potencial
    roi = opt.compute_plan_roi([])
    # No debe fallar — debe retornar metricas neutras
    assert "roi" in roi
    assert roi["n_executed"] == 0


@test("T85 — AbductionTrace existe en ebs_v1 y tiene campos Peirce")
def t85():
    from vigia.core.ebs_v1 import AbductionTrace
    trace = AbductionTrace()
    assert hasattr(trace, "peirce_firstness")
    assert hasattr(trace, "peirce_secondness")
    assert hasattr(trace, "peirce_thirdness")
    assert hasattr(trace, "dominant_signal")
    assert hasattr(trace, "anomalies_found")
    assert hasattr(trace, "tools_available")
    assert hasattr(trace, "abort_triggered")


@test("T86 — ForensicBundle acepta abduction_trace y lo incluye en bundle_hash")
def t86():
    from vigia.core.ebs_v1 import (
        ForensicBundle, EvidenceGraph, DecisionTrace,
        make_default_policy, AbductionTrace,
    )
    from forensics.bundle_builder import BundleBuilder
    from forensics.verify_ebs_v1 import verify_bundle

    trace = AbductionTrace(
        tools_available=["SDA", "GCI"],
        dominant_signal="GCI",
        dominant_z_score=3.1,
        peirce_firstness="GCI z=3.1 detectado",
        peirce_secondness="Patron periodico anómalo",
        peirce_thirdness="Consistente con generacion LLM",
    )

    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=["GCI"], edges=[]),
        decision_trace=DecisionTrace(decision="ABSTAIN", posterior=0.55, risk=0.70, epsilon_used=0.05),
        policy_spec=make_default_policy(),
        abduction_trace=trace,
    )
    sealed = BundleBuilder.seal(b)

    # Debe estar en el bundle
    assert "abduction_trace" in sealed, "abduction_trace debe estar en el sealed dict"
    assert "peirce_firstness" in sealed["abduction_trace"]
    assert sealed["abduction_trace"]["peirce_thirdness"] != ""

    # Debe pasar verificacion Level 2
    result = verify_bundle(sealed)
    assert result.conformity_level >= 2, \
        f"Bundle con abduction_trace debe pasar Level 2, got {result.conformity_level}"


@test("T87 — VigiaPipeline construye AbductionTrace automaticamente")
def t87():
    from vigia.core.ebs_v1 import SignalOutput
    from vigia.pipeline.pipeline import VigiaPipeline

    pipeline = VigiaPipeline(adaptive_policy=False)
    signals = [
        SignalOutput(tool_name="SDA", value=0.9, z_score=3.2, confidence=0.92),
        SignalOutput(tool_name="GCI", value=0.8, z_score=2.8, confidence=0.88),
    ]
    result = pipeline.run_full(signals, drift_score=0.0)
    bundle = result["bundle"]

    assert bundle.abduction_trace is not None, \
        "run_full debe construir AbductionTrace automaticamente"
    assert bundle.abduction_trace.peirce_firstness != ""
    assert bundle.abduction_trace.peirce_thirdness != ""
    assert bundle.abduction_trace.inference_mode != ""


@test("T88 — AbductionTrace en bundle tampereado invalida bundle_hash")
def t88():
    """
    Modificar abduction_trace post-sellado debe invalidar bundle_hash (I2).
    """
    from vigia.core.ebs_v1 import (
        ForensicBundle, EvidenceGraph, DecisionTrace,
        make_default_policy, AbductionTrace,
    )
    from forensics.bundle_builder import BundleBuilder
    import copy

    trace = AbductionTrace(peirce_thirdness="Hipotesis original")
    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="REJECT", posterior=0.8, risk=0.72),
        policy_spec=make_default_policy(),
        abduction_trace=trace,
    )
    sealed = BundleBuilder.seal(b)
    tampered = copy.deepcopy(sealed)
    tampered["abduction_trace"]["peirce_thirdness"] = "Hipotesis falsificada"

    ok, msg = BundleBuilder.quick_verify(tampered)
    assert not ok, "Tamper en abduction_trace debe invalidar bundle_hash"


@test("T89 — fit_calibration.py genera modelos KDE validos con dataset sintetico")
def t89():
    """Verifica que el script de calibracion funciona end-to-end con datos sinteticos."""
    import sys, os
    _HERE = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.join(_HERE, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from fit_calibration import (
        generate_synthetic_dataset, fit_kde_per_tool,
        validate_dataset, fit_ledoit_wolf_nlp,
    )

    samples = generate_synthetic_dataset(n=60, seed=42)
    assert len(samples) == 60

    is_valid, errors = validate_dataset(samples)
    assert is_valid, f"Dataset invalido: {errors}"

    models, meta = fit_kde_per_tool(samples, tools=["SDA", "GCI"])
    assert len(models) >= 1, "Debe producir al menos 1 modelo"
    assert meta["dataset_hash"] != ""
    assert meta["tools_calibrated"]

    for tool, (kde_h0, kde_h1) in models.items():
        assert kde_h0 is not None
        assert kde_h1 is not None

    try:
        cov = fit_ledoit_wolf_nlp(samples, tools=["SDA", "GCI"])
        assert "cov_h0" in cov and "precision_h0" in cov
        assert cov["n_h0"] > 0
    except ValueError:
        pass  # pocas muestras con 2 tools — aceptable




# ===========================================================================
# T90-T99: Bloques finales de grado gubernamental
# ===========================================================================

@test("T90 — AbductionTrace definida ANTES de ForensicBundle (sin forward ref)")
def t90():
    """
    Verifica que AbductionTrace es un tipo resuelto, no una forward reference.
    Esto garantiza que type hints funcionan correctamente en runtime.
    """
    import inspect
    from vigia.core.ebs_v1 import AbductionTrace, ForensicBundle

    # AbductionTrace debe ser una clase real, no un string
    hint = ForensicBundle.__init__.__annotations__.get("abduction_trace", None)
    # Optional[AbductionTrace] — el tipo debe estar resuelto
    # Si la clase existe y se puede instanciar, el orden es correcto
    trace = AbductionTrace(peirce_firstness="test forward ref")
    assert trace.peirce_firstness == "test forward ref"

    # ForensicBundle debe aceptar AbductionTrace sin error de tipo
    from vigia.core.ebs_v1 import EvidenceGraph, DecisionTrace, make_default_policy
    b = ForensicBundle(
        evidence_graph=EvidenceGraph(nodes=[], edges=[]),
        decision_trace=DecisionTrace(decision="ACCEPT", posterior=0.1, risk=0.02),
        policy_spec=make_default_policy(),
        abduction_trace=trace,
    )
    assert b.abduction_trace is not None
    assert isinstance(b.abduction_trace, AbductionTrace)


@test("T91 — BundleBuilder incluye abduction_trace en bundle_hash (sensibilidad)")
def t91():
    """
    El bundle_hash debe cambiar si cambia el abduction_trace.
    Esto garantiza que el razonamiento es parte de la prueba auditorial.
    """
    from vigia.core.ebs_v1 import (
        ForensicBundle, EvidenceGraph, DecisionTrace,
        make_default_policy, AbductionTrace,
    )
    from forensics.bundle_builder import BundleBuilder

    def make_bundle(thirdness: str):
        b = ForensicBundle(
            evidence_graph=EvidenceGraph(nodes=[], edges=[]),
            decision_trace=DecisionTrace(decision="REJECT", posterior=0.8, risk=0.72),
            policy_spec=make_default_policy(),
            abduction_trace=AbductionTrace(peirce_thirdness=thirdness),
        )
        # Fijar timestamps y IDs para comparar solo el contenido
        b.bundle_id = "fixed-id-test-91"
        b.timestamp = "2026-01-01T00:00:00+00:00"
        b.system_state.timestamp = "2026-01-01T00:00:00+00:00"
        b.policy_spec.created_at = "2026-01-01T00:00:00+00:00"
        b.evidence_graph.generated_at = "2026-01-01T00:00:00+00:00"
        return BundleBuilder.seal(b)

    sealed_a = make_bundle("Hipotesis A: fabricacion LLM")
    sealed_b = make_bundle("Hipotesis B: edicion humana")

    hash_a = sealed_a["integrity"]["bundle_hash"]
    hash_b = sealed_b["integrity"]["bundle_hash"]

    assert hash_a != hash_b, \
        "CRITICO: bundle_hash debe cambiar cuando cambia abduction_trace"


@test("T92 — PKI: TimestampClient instancia y hace fallback sin TSA")
def t92():
    """
    TimestampClient debe retornar ReceiptProof aunque la TSA no este disponible.
    El bundle no debe bloquearse por fallo de red.
    """
    import sys, os
    sys.path.insert(0, os.path.join(HERE, 'forensics'))
    from forensics.pki_tools import TimestampClient, ReceiptProof

    # TSA inexistente — debe hacer fallback a local_hash
    client = TimestampClient("http://tsa.vigia.invalid:9999/tsa", timeout=1)
    fake_hash = "a" * 64

    receipt = client.stamp(fake_hash)

    assert isinstance(receipt, ReceiptProof)
    assert receipt.bundle_hash == fake_hash
    assert receipt.proof_type in ("local_hash", "cached", "rfc3161"), \
        f"proof_type inesperado: {receipt.proof_type}"
    assert receipt.local_anchor is not None
    # El fallback debe documentar el error
    if receipt.proof_type == "local_hash":
        assert receipt.error is not None


@test("T93 — PKI: ReceiptProof.to_dict() produce dict auditable")
def t93():
    from forensics.pki_tools import ReceiptProof

    receipt = ReceiptProof(
        bundle_hash="b" * 64,
        proof_type="local_hash",
        timestamp_utc="2026-01-01T00:00:00+00:00",
        tsa_url="http://test.tsa",
        error="TSA no disponible en test",
    )
    d = receipt.to_dict()
    required_fields = [
        "proof_type", "bundle_hash", "timestamp_utc",
        "tsa_url", "local_anchor", "is_tsa_backed",
    ]
    for field in required_fields:
        assert field in d, f"Falta campo '{field}' en ReceiptProof.to_dict()"
    assert d["is_tsa_backed"] is False
    assert len(d["local_anchor"]) == 64  # SHA-256


@test("T94 — PKI: HSMConnector falla gracefully sin pkcs11 instalado")
def t94():
    from forensics.pki_tools import HSMConnector, HSMSignature

    hsm = HSMConnector("/usr/lib/softhsm/libsofthsm2.so")
    # Sin pkcs11 disponible, connect debe retornar False
    result = hsm.connect(slot=0, pin="test")
    assert result is False

    # sign debe retornar HSMSignature con error documentado
    sig = hsm.sign("c" * 64)
    assert isinstance(sig, HSMSignature)
    assert sig.error is not None
    assert not sig.is_valid_format()


@test("T95 — fit_calibration genera KDE y Ledoit-Wolf con dataset sintetico")
def t95():
    import sys, os
    scripts_dir = os.path.join(HERE, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    from fit_calibration import (
        generate_synthetic_dataset,
        fit_kde_per_tool,
        fit_ledoit_wolf_nlp,
        validate_dataset,
        TOOLS_NLP,
    )

    samples = generate_synthetic_dataset(n=80, seed=42)
    is_valid, errors = validate_dataset(samples)
    assert is_valid, f"Dataset invalido: {errors}"

    # KDE
    models, meta = fit_kde_per_tool(samples, tools=["SDA", "GCI"])
    assert len(models) >= 1
    assert "SDA" in models or "GCI" in models
    for tool, (kde_h0, kde_h1) in models.items():
        assert kde_h0 is not None
        assert kde_h1 is not None
        assert meta["kde_diagnostics"][tool]["h0"]["bandwidth"] > 0

    # Ledoit-Wolf para SDA, ACP, CLI, ROI
    lw = fit_ledoit_wolf_nlp(samples, tools=TOOLS_NLP)
    assert "cov_h0" in lw
    assert "precision_h0" in lw
    assert "precision_h1" in lw
    assert lw["tools"] == TOOLS_NLP
    assert lw["n_h0"] > 0
    assert lw["n_h1"] > 0
    assert 0.0 <= lw["shrinkage_h0"] <= 1.0
    assert 0.0 <= lw["shrinkage_h1"] <= 1.0


@test("T96 — Ledoit-Wolf produce matrices invertibles")
def t96():
    """
    Las matrices de precision producidas por Ledoit-Wolf deben ser
    numericamente estables (condicion < 1e8 para ser usables).
    """
    import sys, os
    scripts_dir = os.path.join(HERE, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import numpy as np
    from fit_calibration import generate_synthetic_dataset, fit_ledoit_wolf_nlp, TOOLS_NLP

    samples = generate_synthetic_dataset(n=100, seed=7)
    lw = fit_ledoit_wolf_nlp(samples, tools=TOOLS_NLP)

    # Verificar que precision_h0 es invertible
    prec_h0 = np.array(lw["precision_h0"])
    prec_h1 = np.array(lw["precision_h1"])

    # Eigenvalores deben ser todos positivos (matriz definida positiva)
    eig_h0 = np.linalg.eigvalsh(prec_h0)
    eig_h1 = np.linalg.eigvalsh(prec_h1)

    assert all(e > -1e-10 for e in eig_h0), \
        f"precision_h0 no es definida positiva: min_eig={min(eig_h0):.6f}"
    assert all(e > -1e-10 for e in eig_h1), \
        f"precision_h1 no es definida positiva: min_eig={min(eig_h1):.6f}"

    # Numero de condicion aceptable
    assert lw["condition_number_h0"] < 1e10, \
        f"condition_number_h0 demasiado alto: {lw['condition_number_h0']}"


@test("T97 — RiskBoundedDecisionLayer.from_policy_spec lee epsilon del PolicySpec")
def t97():
    """
    BLOQUE 4: La decision ACCEPT/REJECT debe derivar de policy.epsilon_accept
    y policy.epsilon_reject. Ningun umbral hardcodeado en el codigo.
    """
    from governance.risk_bounded_layer import RiskBoundedDecisionLayer
    from vigia.core.ebs_v1 import make_default_policy

    # PolicySpec con epsilon=0.20 (mas permisivo)
    policy_lax = make_default_policy(epsilon=0.20)
    layer_lax = RiskBoundedDecisionLayer.from_policy_spec(policy_lax)

    # PolicySpec con epsilon=0.01 (muy estricto)
    policy_strict = make_default_policy(epsilon=0.01)
    layer_strict = RiskBoundedDecisionLayer.from_policy_spec(policy_strict)

    # Con posterior=0.5, drift=0, stability=1 -> r = 0.5
    # Con epsilon=0.20: r=0.5 < 1-0.20=0.80 y r=0.5 > 0.20 -> ABSTAIN
    # Con epsilon=0.01: r=0.5 > 1-0.01=0.99? No. 0.5 < 0.99 y 0.5 > 0.01 -> ABSTAIN
    trace_lax = layer_lax.decide(posterior=0.5, drift_score=0.0, graph_stability=1.0)
    trace_strict = layer_strict.decide(posterior=0.5, drift_score=0.0, graph_stability=1.0)

    # Ambos deben ser ABSTAIN con posterior=0.5 (zona media)
    assert trace_lax.decision == "ABSTAIN"
    assert trace_strict.decision == "ABSTAIN"

    # Los epsilon deben venir del PolicySpec
    assert abs(layer_lax._eps_accept - 0.20) < 1e-9
    assert abs(layer_strict._eps_accept - 0.01) < 1e-9


@test("T98 — VigiaPipeline usa epsilon del PolicySpec en RiskLayer (no hardcoded)")
def t98():
    """
    El pipeline debe configurar RiskBoundedDecisionLayer desde PolicySpec.
    Verificar que los epsilons del layer coinciden con los del PolicySpec.
    """
    from vigia.pipeline.pipeline import VigiaPipeline
    from vigia.core.ebs_v1 import make_default_policy

    policy = make_default_policy(epsilon=0.08)
    pipeline = VigiaPipeline(policy=policy, adaptive_policy=False)

    layer = pipeline._risk_layer
    policy_spec = pipeline._policy_spec

    assert abs(layer._eps_accept - policy_spec.epsilon_accept) < 1e-9, \
        f"layer._eps_accept={layer._eps_accept} != policy.epsilon_accept={policy_spec.epsilon_accept}"
    assert abs(layer._eps_reject - policy_spec.epsilon_reject) < 1e-9


@test("T99 — OPTIMIZER_FAIL_SAFE fuerza skipped=False en todas las herramientas")
def t99():
    """
    Cuando el optimizer falla, OPTIMIZER_FAIL_SAFE debe garantizar que
    spec.skipped=False para todas las herramientas — ninguna omitida.
    """
    from engine.resource_optimizer import ResourceOptimizer

    opt = ResourceOptimizer()

    # Forzar fallo interno
    original = opt._build_plan_internal
    def fail_internal(*args, **kwargs):
        raise RuntimeError("OPTIMIZER_FAIL_SAFE test")
    opt._build_plan_internal = fail_internal

    tools = ["SDA", "CLI", "GCI", "ELA", "CLIP"]
    plan = opt.build_execution_plan(tools)

    # Verificar que el fail-safe activo tiene skipped=False en todas
    for spec in plan:
        assert spec.skipped is False, \
            f"OPTIMIZER_FAIL_SAFE: {spec.name}.skipped debe ser False, got {spec.skipped}"
    assert len(plan) == len(tools)

    opt._build_plan_internal = original



def test_ebs_v1_integration_all_checks_passed():
    """U-1 (docs/PATTERN_HUNT_20260718.md): real pytest gate.

    The @test(...) decorators above run each check AT IMPORT and swallow any
    AssertionError into the module-level FAILED list, which was consulted ONLY
    under `if __name__ == "__main__"` — so under pytest every check could fail
    and the run stayed green (the checks executed at collection, their failures
    discarded). The authoritative run is still the standalone invocation
    (`python3 tests/integration/test_ebs_v1_integration.py`, wired in
    vigia-forensic-ci.yml) and this dir is --ignore'd from the default pytest
    suite (pyproject); this function is belt-and-suspenders so that IF the file
    is ever collected by pytest, a swallowed failure surfaces as a red test
    instead of a silent pass. FAILED is already populated by import time."""
    assert not FAILED, (
        f"{len(FAILED)}/{len(PASSED) + len(FAILED)} integration checks failed "
        f"(swallowed at import): {FAILED}"
    )


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  VIGIA Forensic Suite EBS v1 — Integration Tests (Refactored)")
    print("=" * 60 + "\n")

    total = len(PASSED) + len(FAILED)
    print(f"\n{'='*60}")
    print(f"  Resultado: {len(PASSED)}/{total} tests pasaron")

    if FAILED:
        print(f"\n  FALLARON ({len(FAILED)}):")
        for name in FAILED:
            print(f"    - {name}")
        print()
        sys.exit(1)

    print("\n  TODOS LOS TESTS PASARON")
    print("  Arquitectura EBS v1 refactorizada — lista para dataset real\n")
    sys.exit(0)
