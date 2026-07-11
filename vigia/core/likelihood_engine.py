"""
vigia/core/likelihood_engine.py
Adaptador de LikelihoodEngine para pipeline.py.
Acepta los parámetros extendidos (calibration_path, covariance_path, hint_thresholds)
y los traduce a la interfaz real de likelihood_ratio.LikelihoodEngine.
"""
import importlib as _il, sys as _sys, os as _os
import logging as _logging
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _root not in _sys.path: _sys.path.insert(0, _root)

_logger = _logging.getLogger(__name__)

_base_mod = _il.import_module("vigia.core.likelihood_ratio")
globals().update({k: getattr(_base_mod, k) for k in dir(_base_mod) if not k.startswith("__")})

# Re-exportar LikelihoodEngine con interfaz extendida
_BaseLikelihoodEngine = _base_mod.LikelihoodEngine



def _build_contributions(signals, evidence_graph, base_contributions):
    """
    Construye lista de contributions con nombres de cluster emergentes.
    Si evidence_graph es None, retorna base_contributions sin modificar.
    Si evidence_graph provisto, asigna cada señal a su componente conectado
    usando nombres G_{tool}_{i} (determinístico: mismo grafo = mismo resultado).
    """
    if evidence_graph is None:
        return base_contributions

    # Construir componentes conectados del grafo (Union-Find simple)
    edges = getattr(evidence_graph, "edges", [])
    nodes = list(getattr(evidence_graph, "nodes", []))
    threshold = getattr(evidence_graph, "stability_threshold", 0.0)

    # Mapeo tool_name -> componente
    parent = {n: n for n in nodes}

    def find(x):
        while parent.get(x, x) != x:
            parent[x] = parent.get(parent[x], x)
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for edge in edges:
        src = getattr(edge, "source", None)
        tgt = getattr(edge, "target", None)
        stab = getattr(edge, "stability", 0.0)
        if src and tgt and stab >= threshold:
            union(src, tgt)

    # Asignar índice a cada componente (orden determinístico)
    comp_roots = {}
    comp_idx = {}
    idx = 0
    for node in sorted(nodes):
        root = find(node)
        if root not in comp_roots:
            comp_roots[root] = node
            comp_idx[root] = idx
            idx += 1

    result = []
    for sig in signals:
        tool = getattr(sig, "tool_name", "unknown")
        root = find(tool) if tool in parent else None
        if root and root in comp_idx:
            representative = comp_roots[root]
            cluster_name = f"G_{representative}_{comp_idx[root]}"
        else:
            cluster_name = "unassigned"
        result.append({
            "tool": tool,
            "cluster": cluster_name,
            "z_score": getattr(sig, "z_score", 0.0),
        })
    return result

class LikelihoodEngine(_BaseLikelihoodEngine):
    """
    LikelihoodEngine con interfaz extendida para pipeline.py.
    Acepta calibration_path, covariance_path y hint_thresholds — los ignora
    o los usa si el calibrador está disponible.
    """
    def __init__(
        self,
        calibration_path: str = "",
        covariance_path: str = "",
        hint_threshold_reject: float = 0.95,
        hint_threshold_accept: float = 0.05,
        z_cap: float = 10.0,
        calibrator=None,
    ):
        # Intentar cargar calibrador desde path si está disponible
        _calibrator = calibrator
        if not _calibrator and calibration_path:
            try:
                _lr_cal = _il.import_module("vigia.core.lr_calibration")
                # B-102: resolve candidates the same way the pipeline does
                # (shared helper) so the same calibration_path cannot leave
                # this layer in FALLBACK while another layer calibrates.
                for _cand in _lr_cal.candidate_calibrator_paths(calibration_path):
                    try:
                        _calibrator = _lr_cal.LRCalibrator.load(_cand)
                        break
                    except FileNotFoundError:
                        continue
                    except Exception as _cand_exc:
                        _logger.warning(
                            "[LikelihoodEngine] calibrator at %s exists but "
                            "failed to load (%s: %s) — trying next candidate.",
                            _cand, type(_cand_exc).__name__, _cand_exc,
                        )
            except Exception as _exc:
                # B-098: this was a bare 'except: pass' — the cause of a
                # FALLBACK-mode degradation was unrecoverable from the logs.
                _logger.warning(
                    "[LikelihoodEngine] calibrator setup failed for %s "
                    "(%s: %s) — FALLBACK mode.",
                    calibration_path, type(_exc).__name__, _exc,
                )
            if not _calibrator:
                _logger.warning(
                    "[LikelihoodEngine] no usable calibrator for %s — "
                    "FALLBACK mode.",
                    calibration_path,
                )

        super().__init__(z_cap=z_cap, calibrator=_calibrator)
        self.hint_threshold_reject = hint_threshold_reject
        self.hint_threshold_accept = hint_threshold_accept
        self._calibration_path = calibration_path
        self._covariance_path = covariance_path
        self._mode = "CALIBRATED" if _calibrator else "FALLBACK"

    def infer(self, signals, evidence_graph=None, **kwargs):
        """
        Wrapper sobre LikelihoodEngine.infer() que retorna dict.
        pipeline.py espera dict con claves: posterior, lr, mode, log_lr, etc.
        """
        record = super().infer(signals=signals)
        d = record.to_dict() if hasattr(record, "to_dict") else {}

        posterior = d.get("posterior_probability", d.get("posterior", 0.5))
        log_lr    = d.get("combined_log_lr", 0.0)
        import math as _math
        lr = _math.exp(max(-20.0, min(20.0, log_lr)))

        return {
            # Campos obligatorios (accedidos con [])
            "posterior":          posterior,
            "lr":                 lr,
            "mode":               self._mode,
            # Campos opcionales (accedidos con .get())
            "log_lr":             log_lr,
            "redundancy_alerts":  {},
            "contributions":      _build_contributions(signals, evidence_graph, d.get("contributions", [])),
            "components_used":    d.get("n_signals", len(signals)),
            "clustering_method":  "heuristic_default",
            "enfsi_label":        d.get("enfsi_label", "EQUIVOCAL"),
            "signal_count":       d.get("n_signals", len(signals)),
            "calibration_method": "fallback_gaussian",
            "_record":            d,
            # decision_hint basado en hint_thresholds
            "decision_hint": (
                "ACCEPT" if posterior < self.hint_threshold_accept
                else "REJECT" if posterior >= self.hint_threshold_reject
                else "ABSTAIN"
            ),
            # clustering_method depende de si se pasó evidence_graph
            "clustering_method": (
                "graph_conditioned_emergent"
                if evidence_graph is not None
                else "heuristic_default"
            ),
        }


def _correlation_penalty(signals):
    """
    Calcula el factor de penalizacion por correlacion entre senales.
    Retorna float en [0.1, 1.0]: 1.0 = sin penalizacion, 0.1 = maxima.
    Señales con z_scores identicos = maxima correlacion = minimo factor.
    Determinista: opera solo sobre z_scores (enteros/floats puros).
    """
    if not signals or len(signals) < 2:
        return 1.0
    z_scores = [getattr(s, "z_score", 0.0) for s in signals]
    n = len(z_scores)
    mean_z = sum(z_scores) / n
    variance = sum((z - mean_z) ** 2 for z in z_scores) / n
    # Señales identicas (variance=0) -> max correlacion -> min factor (0.1)
    # Señales muy distintas (variance alta) -> min correlacion -> factor 1.0
    # Factor = max(0.1, 1.0 - exp(-variance / 2.0))
    import math as _math
    if variance < 1e-9:
        return 0.1
    factor = max(0.1, min(1.0, 1.0 - _math.exp(-variance / 2.0)))
    return round(factor, 4)
