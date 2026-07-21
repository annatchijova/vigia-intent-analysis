"""
vigia_artifact_graph.py
VIGÍA Forensic Suite — Grafo de Conocimiento Semántico de Artefactos (Capa 1)
Versión: v1.0-Valkyrie
Autora:  Anna Tchijova

Convierte un ForensicBundle en un grafo dirigido de relaciones semánticas
entre entidades forenses: procesos, conexiones de red, archivos, credenciales,
claves de configuración, entradas de log e hipótesis abductivas.

El grafo permite visualizar movimiento lateral no como línea de tiempo
sino como expansión de privilegios en un mapa topológico.

Exportaciones:
  - NetworkX DiGraph   → análisis in-process (PageRank, betweenness, etc.)
  - GEXF               → Gephi
  - GraphML            → yEd, Cytoscape
  - JSON               → D3.js / vis.js

Garantías:
  - _FallbackGraph es 100% funcional si networkx no está presente.
  - INTRINSIC_EDGES son tuplas de tres elementos bien tipadas (str, str, str).
  - _collect_artifacts no lanza excepciones silenciosas.
  - compute_metrics es determinista: usa sorted() en todos los iterables.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────
# DEPENDENCIA OPCIONAL
# ──────────────────────────────────────────────────────────────────────────

try:
    import networkx as nx
    _NX_AVAILABLE: bool = True
except ImportError:
    _NX_AVAILABLE = False

# ──────────────────────────────────────────────────────────────────────────
# PALETA SEMÁNTICA
# ──────────────────────────────────────────────────────────────────────────

NODE_COLORS: Dict[str, str] = {
    "PROCESS":      "#E74C3C",
    "NETWORK_CONN": "#3498DB",
    "REGISTRY_KEY": "#E67E22",
    "FILE":         "#95A5A6",
    "CREDENTIAL":   "#9B59B6",
    "LOG_ENTRY":    "#1ABC9C",
    "HYPOTHESIS":   "#F39C12",
    "ANOMALY":      "#C0392B",
    "HOST":         "#2ECC71",
    "PHASE":        "#BDC3C7",
    "TOOL":         "#5DADE2",
    "UNKNOWN":      "#ECF0F1",
}

# AG-DOS-01: límites para prevenir DoS por memoria
MAX_NODES: int = 5000
# MAX_EDGES configurable via VIGIA_MAX_EDGES (Kimi P1)
# Default: MAX_NODES * 10 = 50_000. Para casos reales complejos
# (Cridex, Volatility con muchos procesos) puede aumentarse:
#   export VIGIA_MAX_EDGES=200000
# AG-DOS-01b: MAX_EDGES configurable via VIGIA_MAX_EDGES — con validación de rango obligatoria.
# Un atacante que controla el entorno ANTES de importar este módulo podría poner
# VIGIA_MAX_EDGES=999999999 y anular la protección DoS. Validamos aquí en import-time.
# Rango permitido: [1_000, 1_000_000]. Fuera de rango → fallback a default seguro.
_MAX_EDGES_RAW: str = os.environ.get("VIGIA_MAX_EDGES", str(MAX_NODES * 10))
try:
    _MAX_EDGES_INT: int = int(_MAX_EDGES_RAW)
    if not (1_000 <= _MAX_EDGES_INT <= 1_000_000):
        import sys as _sys_dos
        _sys_dos.stderr.write(
            f"[VIGIA AG-DOS-01b] VIGIA_MAX_EDGES={_MAX_EDGES_RAW!r} fuera de rango [1000, 1000000]. "
            f"Usando default seguro: {MAX_NODES * 10}.\n"
        )
        _sys_dos.stderr.flush()
        _MAX_EDGES_INT = MAX_NODES * 10
except (ValueError, TypeError):
    import sys as _sys_dos
    _sys_dos.stderr.write(
        f"[VIGIA AG-DOS-01b] VIGIA_MAX_EDGES={_MAX_EDGES_RAW!r} no es entero válido. "
        f"Usando default seguro: {MAX_NODES * 10}.\n"
    )
    _sys_dos.stderr.flush()
    _MAX_EDGES_INT = MAX_NODES * 10
MAX_EDGES: int = _MAX_EDGES_INT
# AG-ENV-01 (Kimi P2): VIGIA_MAX_EDGES DEBE setearse en el entorno ANTES de importar
# este módulo. Python cachea los módulos en sys.modules — un reload() forzado
# recalcularía MAX_EDGES desde el entorno actual, pero el uso normal no hace reload().
# El valor queda fijo post-import como constante de módulo inmutable.
# Uso correcto:
#   export VIGIA_MAX_EDGES=200000
#   python3 -c "import vigia_artifact_graph; ..."
# Uso incorrecto (no tiene efecto):
#   import vigia_artifact_graph
#   os.environ["VIGIA_MAX_EDGES"] = "200000"  # demasiado tarde — ya fue leído

EDGE_WEIGHTS: Dict[str, float] = {
    "SPAWNED_BY":           1.0,
    "CONNECTED_TO":         0.8,
    "MODIFIED":             0.9,
    "PRECEDES":             0.5,
    "CAUSED_BY":            1.0,
    "SUPPORTS":             0.7,
    "CONTRADICTS":          0.6,
    "CORRELATES_WITH":      0.4,
    "LATERAL_MOVE":         1.0,
    "PRIVILEGE_ESCALATION": 1.0,
}

# Mapeo artefacto → tipo de nodo
ARTIFACT_TO_NODE_TYPE: Dict[str, str] = {
    "timestamp_uniformity":            "LOG_ENTRY",
    "log_gap_intervals":               "LOG_ENTRY",
    "process_memory_contradiction":    "PROCESS",
    "log_deletion":                    "LOG_ENTRY",
    "event_log_clearing":              "LOG_ENTRY",
    "artifact_overwrite":              "FILE",
    "file_timestamp_modification":     "FILE",
    "outbound_data_transfer":          "NETWORK_CONN",
    "data_volume":                     "NETWORK_CONN",
    "registry_modifications":          "REGISTRY_KEY",
    "persistence_mechanism":           "REGISTRY_KEY",
    "pass_the_hash_indicator":         "CREDENTIAL",
    "lateral_movement_detected":       "HOST",
    "phishing_email_delivered":        "LOG_ENTRY",
    "malicious_attachment_executed":   "PROCESS",
    "command_line_execution":          "PROCESS",
    "script_execution":                "PROCESS",
    "hardware_additions":              "FILE",
    "outbound_transfer":               "NETWORK_CONN",
    "port_scan":                       "NETWORK_CONN",
    "dns_enumeration":                 "NETWORK_CONN",
    "privilege_escalation":            "PROCESS",
    "credential_dumping":              "CREDENTIAL",
    "scheduled_task":                  "REGISTRY_KEY",
    "service_install":                 "REGISTRY_KEY",
}

# Relaciones semánticas intrínsecas entre artefactos
# Cada tupla: (artifact_a, artifact_b, edge_type)
# Invariante: todas las tuplas tienen exactamente 3 elementos str
INTRINSIC_EDGES: List[Tuple[str, str, str]] = [
    ("malicious_attachment_executed", "command_line_execution",     "SPAWNED_BY"),
    ("malicious_attachment_executed", "script_execution",           "SPAWNED_BY"),
    ("command_line_execution",        "script_execution",           "SPAWNED_BY"),
    ("script_execution",              "registry_modifications",     "MODIFIED"),
    ("script_execution",              "persistence_mechanism",      "MODIFIED"),
    ("script_execution",              "outbound_data_transfer",     "CONNECTED_TO"),
    ("command_line_execution",        "outbound_data_transfer",     "CONNECTED_TO"),
    ("pass_the_hash_indicator",       "lateral_movement_detected",  "LATERAL_MOVE"),
    ("credential_dumping",            "pass_the_hash_indicator",    "PRECEDES"),
    ("privilege_escalation",          "credential_dumping",         "PRECEDES"),
    ("log_deletion",                  "event_log_clearing",         "CORRELATES_WITH"),
    ("artifact_overwrite",            "file_timestamp_modification","CORRELATES_WITH"),
    ("log_gap_intervals",             "timestamp_uniformity",       "CORRELATES_WITH"),
    ("process_memory_contradiction",  "timestamp_uniformity",       "CAUSED_BY"),
    ("outbound_data_transfer",        "data_volume",                "CORRELATES_WITH"),
    ("registry_modifications",        "persistence_mechanism",      "CORRELATES_WITH"),
    ("service_install",               "scheduled_task",             "CORRELATES_WITH"),
    ("phishing_email_delivered",      "malicious_attachment_executed","PRECEDES"),
    ("command_line_execution",        "privilege_escalation",       "PRECEDES"),
]

# Secuencia kill-chain MITRE como aristas PRECEDES entre fases
MITRE_KILL_CHAIN: List[Tuple[str, str, str]] = [
    ("RECONNAISSANCE",        "INITIAL_ACCESS",        "PRECEDES"),
    ("INITIAL_ACCESS",        "EXECUTION",             "PRECEDES"),
    ("EXECUTION",             "PERSISTENCE",           "PRECEDES"),
    ("EXECUTION",             "DEFENSE_EVASION",       "PRECEDES"),
    ("PERSISTENCE",           "PRIVILEGE_ESCALATION",  "PRECEDES"),
    ("PRIVILEGE_ESCALATION",  "CREDENTIAL_ACCESS",     "PRECEDES"),
    ("CREDENTIAL_ACCESS",     "LATERAL_MOVEMENT",      "PRECEDES"),
    ("LATERAL_MOVEMENT",      "COLLECTION",            "PRECEDES"),
    ("COLLECTION",            "EXFILTRATION",          "PRECEDES"),
    ("DEFENSE_EVASION",       "CLEANUP",               "PRECEDES"),
]

# ──────────────────────────────────────────────────────────────────────────
# FALLBACK GRAPH — funcional sin networkx
# ──────────────────────────────────────────────────────────────────────────

class FallbackGraph:
    """
    Grafo dirigido mínimo implementado en stdlib puro.
    100% funcional cuando networkx no está disponible.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        # Adjacencia: src -> list of dst
        self._adj: Dict[str, List[str]] = {}
        # Grafo (metadatos)
        self.graph: Dict[str, Any] = {}

    def add_node(self, node_id: str, **attrs: Any) -> None:
        self._nodes[node_id] = dict(attrs)
        if node_id not in self._adj:
            self._adj[node_id] = []

    def add_edge(self, src: str, dst: str, **attrs: Any) -> None:
        # Agregar nodos si no existen
        if src not in self._nodes:
            self.add_node(src)
        if dst not in self._nodes:
            self.add_node(dst)
        edge = {"source": src, "target": dst, **attrs}
        # Evitar aristas duplicadas (mismo src, dst y relation)
        relation = attrs.get("relation", "")
        for existing in self._edges:
            if (existing["source"] == src and existing["target"] == dst
                    and existing.get("relation") == relation):
                return
        self._edges.append(edge)
        if dst not in self._adj.get(src, []):
            self._adj.setdefault(src, []).append(dst)

    def number_of_nodes(self) -> int:
        return len(self._nodes)

    def number_of_edges(self) -> int:
        return len(self._edges)

    def in_degree(self, node_id: str) -> int:
        """AG-FB-01: implementar in_degree para compute_metrics."""
        return sum(1 for e in self._edges if e.get("target") == node_id)

    def out_degree(self, node_id: str) -> int:
        """AG-FB-01: implementar out_degree para compute_metrics."""
        return sum(1 for e in self._edges if e.get("source") == node_id)

    def nodes(self) -> Dict[str, Dict[str, Any]]:
        return self._nodes

    def edges_list(self) -> List[Dict[str, Any]]:
        return list(self._edges)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": k, **v} for k, v in sorted(self._nodes.items())],
            "edges": self.edges_list(),
        }


# ──────────────────────────────────────────────────────────────────────────
# TIPO UNIFICADO
# ──────────────────────────────────────────────────────────────────────────

# El grafo es un DiGraph de networkx o un FallbackGraph
AnyGraph = Any


# ──────────────────────────────────────────────────────────────────────────
# MOTOR PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────

class ArtifactGraphEngine:
    """
    Construye un grafo de conocimiento semántico desde un ForensicBundle.

    Orden de construcción:
      1. Nodo de hipótesis ganadora
      2. Nodos de artefactos observados
      3. Aristas SUPPORTS: artefacto → hipótesis
      4. Aristas intrínsecas entre artefactos conocidos
      5. Nodos de señales del evidence_graph
      6. Nodos de anomalías detectadas
      7. Nodos de alternativas descartadas
      8. Nodos de fases MITRE con kill-chain como backbone
    """

    def __init__(self) -> None:
        self._using_nx: bool = _NX_AVAILABLE
        # AG-SAN-02: contador de instancia — determinista por build
        self._unknown_counter: int = 0


    @staticmethod
    def _validate_bundle_schema(bundle: Dict[str, Any]) -> Optional[str]:
        """
        Verifica la estructura mínima de un ForensicBundle antes de construir el grafo.
        Retorna None si es válido, o mensaje de error si no.
        """
        if not isinstance(bundle, dict):
            return f"bundle debe ser dict, recibido: {type(bundle).__name__}"
        bid = bundle.get("bundle_id", "")
        if not isinstance(bid, str) or not bid.strip():
            return "bundle_id debe ser string no vacío"
        abduction = bundle.get("abduction_trace")
        if abduction is not None and not isinstance(abduction, dict):
            return "abduction_trace debe ser dict o None"
        evidence = bundle.get("evidence_graph")
        if evidence is not None and not isinstance(evidence, dict):
            return "evidence_graph debe ser dict o None"
        return None

    def build(self, bundle: Dict[str, Any]) -> AnyGraph:
        if self._using_nx:
            G: AnyGraph = nx.DiGraph()
            G.graph["vigia_bundle_id"] = bundle.get("bundle_id", "unknown")
            G.graph["vigia_version"] = "v1.0-Valkyrie"
            G.graph["generated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            G = FallbackGraph()
            G.graph["vigia_bundle_id"] = bundle.get("bundle_id", "unknown")

        # Validar schema del input
        schema_err = self._validate_bundle_schema(bundle)
        if schema_err:
            raise ValueError(f"[VIGIA schema] Bundle inválido: {schema_err}")

        # AG-DOS-01: límite de nodos
        # El check se aplica dinámicamente durante la construcción
        _node_count = [0]  # contador mutable por closure

        # AG-SAN-04: resetear contador al inicio de cada build
        self._unknown_counter = 0
        # AG-DOS-03: flag para capturar primer error de MAX_NODES en cualquier paso
        _build_truncated: str = ""

        abduction = bundle.get("abduction_trace", {}) or {}
        evidence_graph = bundle.get("evidence_graph", {}) or {}

        hyp: Dict[str, Any] = abduction.get("abductive_hypothesis", {}) or {}
        winner_id: str = str(hyp.get("hypothesis_id", ""))

        # ── 1. Hipótesis ganadora ────────────────────────────────────────
        if winner_id:
            mitre_list = hyp.get("mitre_techniques", [])
            mitre_str = ", ".join(
                str(t.get("technique_id", ""))
                for t in mitre_list
                if isinstance(t, dict)
            )
            self._add_node(G, winner_id,
                node_type="HYPOTHESIS",
                label=winner_id,
                intent_type=str(hyp.get("intent_type", "")),
                cost=int(hyp.get("cost", 0)),
                coverage=int(hyp.get("coverage_score", hyp.get("coverage", 0))),
                explanation=str(hyp.get("explanation", ""))[:200],
                mitre=mitre_str,
                color=NODE_COLORS["HYPOTHESIS"],
                size=30,
            )

        # AG-DOS-03: helper local que captura MAX_NODES y sigue construyendo
        # el grafo parcial en lugar de fallar completamente.
        def _safe_add_node(nid: str, **attrs: Any) -> None:
            nonlocal _build_truncated
            if _build_truncated:
                return  # ya se alcanzó el límite — no agregar más
            try:
                self._add_node(G, nid, **attrs)
            except ValueError as _e:
                _build_truncated = str(_e)

        def _safe_add_edge(src: str, dst: str, **attrs: Any) -> None:
            if _build_truncated:
                return
            try:
                self._add_edge(G, src, dst, **attrs)
            except Exception:
                pass  # aristas fallidas no son críticas

        # ── 2. Artefactos observados ─────────────────────────────────────
        artifacts = self._collect_artifacts(bundle)
        observed_names: set[str] = set()

        for art in artifacts:
            name = str(art.get("artifact_name", art.get("artifact_id", "")))
            if not name:
                continue
            observed_names.add(name)
            node_type = ARTIFACT_TO_NODE_TYPE.get(name, "UNKNOWN")
            _safe_add_node(f"ART_{name}",
                node_type=node_type,
                label=name,
                artifact_id=str(art.get("artifact_id", "")),
                observed=bool(art.get("observed", True)),
                adversarial_noise=bool(art.get("adversarial_noise", False)),
                value=str(art.get("value", ""))[:100],
                color=NODE_COLORS.get(node_type, NODE_COLORS["UNKNOWN"]),
                size=20,
            )

            # Arista SUPPORTS hacia hipótesis ganadora
            if winner_id and not art.get("adversarial_noise", False):
                _safe_add_edge(f"ART_{name}", winner_id,
                    relation="SUPPORTS",
                    weight=EDGE_WEIGHTS["SUPPORTS"],
                    label="supports",
                )

        # ── 3. Aristas intrínsecas ───────────────────────────────────────
        # AG-CHK-02: usar método de instancia en lugar de closure
        # para reutilizabilidad y eliminar acoplamiento con _nodes privado
        def _node_exists(g: Any, nid: str) -> bool:
            return self._graph_has_node(g, nid)

        for art_a, art_b, relation in INTRINSIC_EDGES:
            if art_a not in observed_names or art_b not in observed_names:
                continue
            nid_a = self._sanitize_node_id(f"ART_{art_a}")
            nid_b = self._sanitize_node_id(f"ART_{art_b}")
            # AG-EDGE-01: sólo agregar arista si ambos nodos ya existen
            if not _node_exists(G, nid_a) or not _node_exists(G, nid_b):
                continue
            _safe_add_edge(nid_a, nid_b,
                relation=relation,
                weight=EDGE_WEIGHTS.get(relation, 0.5),
                label=relation.lower().replace("_", " "),
            )

        # ── 4. Señales del evidence_graph ────────────────────────────────
        for node_data in evidence_graph.get("nodes", []):
            if not isinstance(node_data, dict):
                continue
            tool = str(node_data.get("tool_name", node_data.get("node_id", "")))
            if not tool:
                continue
            nid = f"TOOL_{tool}"
            z = float(node_data.get("z_score", 0.0))
            conf = float(node_data.get("confidence", 0.0))
            node_type = "ANOMALY" if z >= 2.0 else "TOOL"
            _safe_add_node(nid,
                node_type=node_type,
                label=tool,
                z_score=round(z, 4),
                confidence=round(conf, 4),
                color=NODE_COLORS.get(node_type, NODE_COLORS["TOOL"]),
                size=int(15 + min(15, z * 3)),
            )
            if winner_id and z >= 1.5:
                _safe_add_edge(nid, winner_id,
                    relation="SUPPORTS",
                    weight=round(conf * EDGE_WEIGHTS["SUPPORTS"], 3),
                    z_score=round(z, 4),
                    label=f"z={z:.2f}",
                )

        # ── 5. Anomalías detectadas ──────────────────────────────────────
        for i, anomaly in enumerate(abduction.get("anomalies_found", [])[:10]):
            if not isinstance(anomaly, dict):
                continue
            atype = str(anomaly.get("type", anomaly.get("pattern_name", f"ANOMALY_{i}")))
            nid = f"ANOM_{atype}_{i}"
            severity = float(anomaly.get("severity", anomaly.get("weight", 0.5)))
            _safe_add_node(nid,
                node_type="ANOMALY",
                label=atype,
                description=str(anomaly.get("description", ""))[:150],
                severity=round(severity, 3),
                mitre=str(anomaly.get("mitre_ttp", "")),
                color=NODE_COLORS["ANOMALY"],
                size=int(10 + severity * 20),
            )
            if winner_id:
                _safe_add_edge(nid, winner_id,
                    relation="CAUSED_BY",
                    weight=round(EDGE_WEIGHTS["CAUSED_BY"] * severity, 3),
                    label="caused by",
                )

        # ── 6. Alternativas descartadas ──────────────────────────────────
        for alt in (hyp.get("alternatives", []) or [])[:4]:
            if not isinstance(alt, dict):
                continue
            alt_id = str(alt.get("hypothesis_id", ""))
            if not alt_id:
                continue
            _safe_add_node(f"ALT_{alt_id}",
                node_type="HYPOTHESIS",
                label=f"{alt_id} (descartada)",
                intent_type=str(alt.get("intent_type", "")),
                cost=int(alt.get("cost", 0)),
                coverage=int(alt.get("coverage_score", alt.get("coverage", 0))),
                color="#7F8C8D",
                size=12,
            )
            if winner_id:
                _safe_add_edge(winner_id, f"ALT_{alt_id}",
                    relation="CONTRADICTS",
                    weight=EDGE_WEIGHTS["CONTRADICTS"],
                    label="descartada",
                )

        # ── 7. Kill chain MITRE ──────────────────────────────────────────
        detected_phase = str(
            hyp.get("phase", abduction.get("phase_target", ""))
        ).upper()
        if not _build_truncated:
            self._add_kill_chain(G, detected_phase, winner_id)

        if _build_truncated:
            import warnings as _w_dos3
            _w_dos3.warn(
                f"[VIGIA AG-DOS-03] Grafo truncado (MAX_NODES={MAX_NODES}): "
                f"{_build_truncated}. Grafo válido pero incompleto.",
                UserWarning, stacklevel=2,
            )
        return G

    # ── helpers de artefactos ─────────────────────────────────────────────

    def _collect_artifacts(self, bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrae artefactos de múltiples ubicaciones del bundle.
        No lanza excepciones — retorna lista vacía ante cualquier error.
        AG-DUP-01: no re-valida el schema (build() ya lo hizo).
        """
        artifacts: List[Dict[str, Any]] = []
        seen_names: set[str] = set()

        def _add(art: Dict[str, Any]) -> None:
            name = str(art.get("artifact_name", art.get("artifact_id", "")))
            if name and name not in seen_names:
                seen_names.add(name)
                artifacts.append(art)

        # Artefactos directos del bundle (formato adversarial/case)
        for a in bundle.get("artifacts", []):
            if isinstance(a, dict):
                _add(a)

        # Herramientas ejecutadas como artefactos de tipo TOOL
        # schema ya validado en build() — no revalidar (AG-DUP-02/03)

        abduction = bundle.get("abduction_trace", {}) or {}
        for tool in abduction.get("tools_executed", []):
            if isinstance(tool, str) and tool:
                _add({"artifact_name": tool, "artifact_id": f"TOOL_{tool}",
                      "observed": True, "value": "executed"})

        # Anomalías como artefactos
        for anomaly in abduction.get("anomalies_found", [])[:10]:
            if not isinstance(anomaly, dict):
                continue
            atype = str(anomaly.get("type", "")).lower().replace(" ", "_")
            if atype:
                _add({"artifact_name": atype, "artifact_id": atype,
                      "observed": True, "value": str(anomaly.get("description", ""))})

        # Required artifacts de la hipótesis ganadora
        hyp = abduction.get("abductive_hypothesis", {}) or {}
        assumed = set(hyp.get("assumed_artifacts", []) or [])
        for req in (hyp.get("required_artifacts", []) or []):
            if isinstance(req, str) and req not in assumed:
                _add({"artifact_name": req, "artifact_id": req,
                      "observed": True, "value": "required_observed"})

        return artifacts

    # ── kill chain ────────────────────────────────────────────────────────

    def _add_kill_chain(
        self, G: AnyGraph, detected_phase: str, winner_id: str
    ) -> None:
        all_phases: set[str] = {p for pair in MITRE_KILL_CHAIN for p in pair[:2]}

        for phase in sorted(all_phases):
            is_current = (phase == detected_phase)
            self._add_node(G, f"PHASE_{phase}",
                node_type="PHASE",
                label=phase.replace("_", " ").title(),
                current_phase=is_current,
                color="#E74C3C" if is_current else NODE_COLORS["PHASE"],
                size=18 if is_current else 10,
            )

        for phase_a, phase_b, relation in MITRE_KILL_CHAIN:
            self._add_edge(G, f"PHASE_{phase_a}", f"PHASE_{phase_b}",
                relation=relation,
                weight=EDGE_WEIGHTS["PRECEDES"],
                label="next",
            )

        if detected_phase and winner_id:
            self._add_edge(G, f"PHASE_{detected_phase}", winner_id,
                relation="CAUSED_BY",
                weight=0.8,
                label="detected here",
            )

    # ── primitivas de grafo ───────────────────────────────────────────────

    # Contador de nodos UNKNOWN para IDs únicos (AG-SAN-01)

    def _sanitize_node_id(self, raw_id: str) -> str:
        """
        Sanitiza un node_id para exportación segura.

        AG-SAN-02 (Kimi audit v2): contador de instancia en lugar de clase.
        Mismo input en builds distintos produce el mismo ID (determinista).
        El contador sólo avanza dentro de una build específica.

        AG-SAN-03: eliminado parámetro 'prefix' que nunca se usaba (código muerto).
        """
        if not raw_id or not isinstance(raw_id, str):
            self._unknown_counter += 1
            return f"UNKNOWN_{self._unknown_counter:04d}"
        sanitized = re.sub(r"[^a-zA-Z0-9_\-]", "_", raw_id.strip())
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")
        if not sanitized:
            self._unknown_counter += 1
            return f"UNKNOWN_{self._unknown_counter:04d}"
        return sanitized

    def _graph_has_node(self, G: Any, node_id: str) -> bool:
        """
        AG-CHK-02: verificar existencia de nodo usando la interfaz pública
        en lugar de acceder a _nodes directamente.
        FallbackGraph expone nodes() como método público.
        """
        if self._using_nx:
            return node_id in G.nodes
        # FallbackGraph: usar nodes() que es API pública
        return node_id in G.nodes()

    def _add_node(self, G: Any, node_id: str, **attrs: Any) -> None:
        """
        Agrega un nodo al grafo.

        AG-DOS-02 / AG-LIM-01 (Kimi audit v2):
        MAX_NODES ahora se APLICA aquí — no sólo se define.
        Si el grafo alcanza el límite, lanza ValueError para prevenir DoS.
        """
        # AG-DOS-02: verificar límite ANTES de agregar
        current_count = G.number_of_nodes()
        if current_count >= MAX_NODES:
            raise ValueError(
                f"[VIGIA AG-DOS-02] Límite de nodos alcanzado: {MAX_NODES}. "
                f"Bundle tiene demasiados artefactos para ser procesado de forma segura. "
                f"Revisar el bundle — puede ser un intento de DoS."
            )
        # Sanitizar node_id para exportación segura
        node_id = self._sanitize_node_id(node_id)
        # Tipos básicos para serialización
        safe_attrs = {k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                      for k, v in attrs.items()}
        if self._using_nx:
            G.add_node(node_id, **safe_attrs)
        else:
            G.add_node(node_id, **safe_attrs)

    def _add_edge(
        self, G: AnyGraph, src: str, dst: str, **attrs: Any
    ) -> None:
        """
        Agrega una arista al grafo.

        Kimi P1: verifica MAX_EDGES antes de agregar para prevenir DoS
        por grafos con millones de aristas (grafo completo k=5000 ~ 12.5M aristas).
        """
        # Verificar límite de aristas (Kimi P1)
        current_edges = G.number_of_edges()
        if current_edges >= MAX_EDGES:
            raise ValueError(
                f"[VIGIA AG-DOS-04] Límite de aristas alcanzado: {MAX_EDGES}. "
                "Bundle genera demasiadas relaciones — posible DoS."
            )
        # Sanitizar src/dst para consistencia con _add_node
        src = self._sanitize_node_id(src)
        dst = self._sanitize_node_id(dst)
        safe_attrs = {k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                      for k, v in attrs.items()}
        if self._using_nx:
            G.add_edge(src, dst, **safe_attrs)
        else:
            G.add_edge(src, dst, **safe_attrs)

    # ── exportadores ─────────────────────────────────────────────────────

    @staticmethod
    def _validate_output_path(output_path: str) -> str:
        """
        AG-OUT-01/02/03/B-175: valida output_path.
        - Sin traversal de path (..)
        - Directorio padre existe, no contiene symlinks y es escribible
        - Path dentro de directorios raíz permitidos (AG-OUT-04)
        - Nunca dentro de ``VIGIA_EVIDENCE_DIR`` (B-175)

        AG-OUT-04 (Kimi P1): el check anterior prevenía '..' pero no paths absolutos
        que apunten a rutas sensibles. Ejemplo: '/etc/passwd' no tiene '..' pero
        no debe ser un output válido para un grafo forense.
        El operador debe usar los directorios declarados en _ALLOWED_OUTPUT_ROOTS.
        """
        import os as _os_out
        import stat as _stat_out
        # Directorios raíz permitidos para exportación de grafos
        _ALLOWED_OUTPUT_ROOTS: tuple = (
            "/tmp", "/home", "/var", "/forensics", "/quarantine",
            "/mnt", "/opt", "/srv",
        )
        if not isinstance(output_path, str) or not output_path.strip():
            raise ValueError("output_path debe ser un string no vacío")
        if "\x00" in output_path:
            raise ValueError("output_path contiene un byte nulo")
        p = Path(output_path)
        # Barrera 1: sin traversal
        if any(part == ".." for part in p.parts):
            raise ValueError(f"Path traversal en output_path: {output_path!r}")
        raw_absolute = p if p.is_absolute() else Path.cwd() / p
        try:
            resolved = raw_absolute.resolve(strict=False)
        except (OSError, RuntimeError) as exc:
            raise ValueError(f"No se puede resolver output_path: {exc}") from exc

        # Barrera 2: pertenencia de filesystem por componentes, nunca por
        # prefijo textual (``/tmp-copy`` no hereda autoridad de ``/tmp``).
        allowed_roots = tuple(Path(root).resolve(strict=False) for root in _ALLOWED_OUTPUT_ROOTS)
        if not any(resolved == root or resolved.is_relative_to(root) for root in allowed_roots):
            raise ValueError(
                f"[VIGIA AG-OUT-04] Output path fuera de directorios permitidos: {output_path!r}. "
                f"Directorios válidos: {_ALLOWED_OUTPUT_ROOTS}"
            )

        # B-175: evidence is an immutable input even when it lives below a
        # generally valid host root such as /home or /tmp. Resolve first so a
        # redirect into evidence cannot hide behind a benign-looking raw path.
        evidence_dir = os.getenv("VIGIA_EVIDENCE_DIR", "").strip()
        if evidence_dir:
            try:
                evidence_root = Path(evidence_dir).resolve(strict=False)
            except (OSError, RuntimeError) as exc:
                raise ValueError(f"No se puede resolver VIGIA_EVIDENCE_DIR: {exc}") from exc
            if resolved == evidence_root or resolved.is_relative_to(evidence_root):
                raise ValueError(
                    "[VIGIA AG-OUT-05] Refusing to write graph output inside "
                    "VIGIA_EVIDENCE_DIR (forensic evidence is read-only)."
                )

        # Barrera 3: reject every existing raw path component that is a
        # symlink. Checking only the immediate parent missed
        # ``safe/link/nested/graph.gexf`` and could redirect output after the
        # logical path had passed containment checks.
        cursor = Path(raw_absolute.anchor)
        for component in raw_absolute.relative_to(raw_absolute.anchor).parts:
            cursor /= component
            try:
                mode = _os_out.lstat(cursor).st_mode
            except FileNotFoundError:
                break
            except OSError as exc:
                raise ValueError(f"No se puede inspeccionar output_path: {exc}") from exc
            if _stat_out.S_ISLNK(mode):
                raise ValueError(
                    f"[VIGIA AG-SYM-02] output_path contiene un symlink: {str(cursor)!r}. "
                    "Usar el directorio real directamente."
                )

        parent = raw_absolute.parent
        if not parent.exists():
            raise ValueError(
                f"Directorio padre no existe: {str(parent)!r}. "
                "Crear el directorio manualmente antes de exportar."
            )
        if not _os_out.access(str(parent), _os_out.W_OK):
            raise ValueError(
                f"Directorio padre no es escribible: {str(parent)!r}."
            )
        return str(raw_absolute)

    def export_gexf(self, G: AnyGraph, output_path: str) -> None:
        """Exporta a GEXF para Gephi."""
        if not self._using_nx:
            raise RuntimeError("networkx requerido para exportar GEXF")
        try:
            nx.write_gexf(G, self._validate_output_path(output_path))
        except Exception as e:
            raise OSError(f"[VIGIA AG-EXP-01] Error exportando GEXF a {output_path!r}: {e}") from e

    def export_graphml(self, G: AnyGraph, output_path: str) -> None:
        """Exporta a GraphML para yEd / Cytoscape."""
        if not self._using_nx:
            raise RuntimeError("networkx requerido para exportar GraphML")
        try:
            nx.write_graphml(G, self._validate_output_path(output_path))
        except Exception as e:
            raise OSError(f"[VIGIA AG-EXP-01] Error exportando GraphML a {output_path!r}: {e}") from e

    def export_json(self, G: AnyGraph) -> str:
        def _native(v: Any, _depth: int = 0) -> Any:
            """
            AG-SER-01/02: preservar tipos nativos JSON, incluyendo list y dict.
            Convierte a str sólo si el tipo realmente no es JSON-serializable.
            AG-SER-02 (Kimi v2): la versión anterior convertía listas a str().
            """
            # AG-SER-03 + Kimi P2: límite + captura explícita de RecursionError
            if _depth > 8:  return str(v)  # margen antes del límite de Python
            if isinstance(v, bool):  return v   # antes de int — bool es subclase
            if isinstance(v, int):   return v
            if isinstance(v, float): return round(v, 6)
            if isinstance(v, str):   return v
            if v is None:            return v
            if isinstance(v, list):
                try:
                    return [_native(item, _depth + 1) for item in v]
                except RecursionError:
                    return f"[RECURSION_LIMIT:list:{len(v)}items]"
            if isinstance(v, dict):
                try:
                    return {str(k): _native(val, _depth + 1) for k, val in v.items()}
                except RecursionError:
                    return f"[RECURSION_LIMIT:dict:{len(v)}keys]"
            return str(v)  # fallback para tipos realmente no serializables

        if self._using_nx:
            nodes = sorted(
                [{"id": n, **{k: _native(v) for k, v in G.nodes[n].items()}}
                 for n in G.nodes],
                key=lambda x: x["id"],
            )
            edges = sorted(
                [{"source": u, "target": v,
                  **{k: _native(val) for k, val in G.edges[u, v].items()}}
                 for u, v in G.edges],
                key=lambda x: (x["source"], x["target"]),
            )
        else:
            d = G.to_dict()
            nodes = sorted(d["nodes"], key=lambda x: x.get("id", ""))
            edges = sorted(d["edges"],
                           key=lambda x: (x.get("source", ""), x.get("target", "")))

        # AG-TS-01 (Kimi P2): usar timestamp del bundle/grafo para determinismo forense.
        # datetime.now() cambia en cada ejecución → JSON no reproducible bit-a-bit.
        # Prioridad: G.graph["generated_at"] → bundle metadata → timestamp del grafo
        # Si no hay ninguno disponible, usar cadena fija para indicar ausencia.
        if self._using_nx:
            _generated_at = (
                G.graph.get("generated_at")
                or G.graph.get("bundle_timestamp")
                or "TIMESTAMP_NOT_AVAILABLE"
            )
        else:
            _generated_at = (
                G.graph.get("generated_at")
                or G.graph.get("bundle_timestamp")
                or "TIMESTAMP_NOT_AVAILABLE"
            )
        return json.dumps({
            "nodes":    nodes,
            "edges":    edges,
            "metadata": {
                "n_nodes":       len(nodes),
                "n_edges":       len(edges),
                "backend":       "networkx" if self._using_nx else "fallback",
                "vigia_version": "v1.0-Valkyrie",
                "generated_at":  _generated_at,
            },
        }, indent=2, sort_keys=True, ensure_ascii=False)

    # ── métricas deterministas ────────────────────────────────────────────

    def compute_metrics(self, G: AnyGraph) -> Dict[str, Any]:
        """
        Calcula métricas topológicas. Usa sorted() en todos los iterables
        para garantizar determinismo en el output.

        AG-METRIC-01 — ADVERTENCIA DE DETERMINISMO:
        PageRank y Betweenness Centrality usan aritmética de punto flotante
        internamente (networkx). Los resultados pueden variar entre arquitecturas
        (x86 vs ARM, diferente precisión FPU) y versiones de numpy/networkx.

        ESTAS MÉTRICAS SON PARA VISUALIZACIÓN Y ANÁLISIS EXPLORATORIO ÚNICAMENTE.
        No deben usarse para justificar un veredicto forense ni como input de
        ningún pipeline determinista. El composite score de VIGÍA no depende
        de estas métricas — depende de AbductiveIntentEngine y PICERLMapper.

        Para auditoría reproducible: documentar la versión exacta de networkx
        y numpy en el reporte forense.
        """
        if not self._using_nx:
            return {
                "backend": "fallback",
                "n_nodes": G.number_of_nodes(),
                "n_edges": G.number_of_edges(),
                "note":    "networkx no disponible — métricas limitadas",
            }

        n = G.number_of_nodes()
        m = G.number_of_edges()
        metrics: Dict[str, Any] = {
            "backend": "networkx",
            "n_nodes": n,
            "n_edges": m,
        }

        if n == 0:
            return metrics

        # AG-METRIC-01: flag explícito en el output para que el consumidor sepa
        # que estas métricas no son reproducibles bit-a-bit entre arquitecturas.
        metrics["determinism_warning"] = (
            "METRICS_NON_DETERMINISTIC: PageRank y Betweenness usan float FPU. "
            "No usar para decisión forense. Solo visualización."
        )

        # PageRank — determinista con sorted
        try:
            pr = nx.pagerank(G, weight="weight", max_iter=100, tol=1e-6)
            top5 = sorted(pr.items(), key=lambda x: (-x[1], x[0]))[:5]
            metrics["top_pagerank"] = [
                {"node": nd, "score": round(sc, 6),
                 "type": str(G.nodes[nd].get("node_type", "?"))}
                for nd, sc in top5
            ]
        except Exception as exc:
            metrics["pagerank_error"] = str(exc)

        # Betweenness — determinista con sorted
        try:
            bc = nx.betweenness_centrality(G, weight="weight", normalized=True)
            top5_bc = sorted(bc.items(), key=lambda x: (-x[1], x[0]))[:5]
            metrics["top_betweenness"] = [
                {"node": nd, "score": round(sc, 6),
                 "type": str(G.nodes[nd].get("node_type", "?"))}
                for nd, sc in top5_bc
            ]
        except Exception as exc:
            metrics["betweenness_error"] = str(exc)

        # Componentes débilmente conectados — usar sorted para determinismo
        try:
            wcc = list(nx.weakly_connected_components(G))
            wcc_sorted = sorted([sorted(c) for c in wcc], key=lambda c: (-len(c), c[0]))
            metrics["weakly_connected_components"] = len(wcc_sorted)
            metrics["largest_component_size"] = len(wcc_sorted[0]) if wcc_sorted else 0
        except Exception as exc:
            metrics["wcc_error"] = str(exc)

        # Densidad
        metrics["density"] = round(nx.density(G), 6)

        # Nodos huérfanos (sin aristas)
        orphans = sorted(
            [n for n in G.nodes
             if G.in_degree(n) == 0 and G.out_degree(n) == 0]
        )
        metrics["orphan_node_count"] = len(orphans)
        if orphans:
            metrics["orphan_node_ids"] = orphans[:10]

        return metrics


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="VIGÍA Artifact Graph — Grafo semántico forense (Capa 1)"
    )
    parser.add_argument("--bundle",  required=True,
                        help="ForensicBundle sellado (.json)")
    parser.add_argument("--format",  choices=["gexf", "graphml", "json"],
                        default="json",
                        help="Formato de exportación (default: json)")
    parser.add_argument("--output",  default=None,
                        help="Archivo de salida")
    parser.add_argument("--metrics", action="store_true",
                        help="Calcular métricas topológicas")
    args = parser.parse_args()

    bundle_path = Path(args.bundle)
    if not bundle_path.exists():
        print(f"ERROR: {bundle_path} no encontrado", file=sys.stderr)
        return 1

    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    engine = ArtifactGraphEngine()
    G = engine.build(bundle)

    n = G.number_of_nodes()
    m = G.number_of_edges()
    backend = "networkx" if _NX_AVAILABLE else "fallback"
    print(f"[OK] Grafo construido ({backend}): {n} nodos, {m} aristas")

    if args.metrics:
        m_data = engine.compute_metrics(G)
        print(json.dumps(m_data, indent=2))

    suffix_map = {"json": ".graph.json", "gexf": ".gexf", "graphml": ".graphml"}
    out_path = Path(args.output) if args.output else bundle_path.with_suffix(
        suffix_map[args.format]
    )

    if args.format == "json":
        safe_output_path = Path(engine._validate_output_path(str(out_path)))
        safe_output_path.write_text(engine.export_json(G), encoding="utf-8")
        print(f"[OK] JSON → {safe_output_path}")
    elif args.format == "gexf":
        engine.export_gexf(G, str(out_path))
        print(f"[OK] GEXF → {out_path}")
    elif args.format == "graphml":
        engine.export_graphml(G, str(out_path))
        print(f"[OK] GraphML → {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
