"""
vigia/core/likelihood_engine.py
Adaptador de LikelihoodEngine para pipeline.py.
Acepta los parámetros extendidos (calibration_path, covariance_path, hint_thresholds)
y los traduce a la interfaz real de likelihood_ratio.LikelihoodEngine.
"""
import importlib as _il, sys as _sys, os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
if _root not in _sys.path: _sys.path.insert(0, _root)

_base_mod = _il.import_module("likelihood_ratio")
globals().update({k: getattr(_base_mod, k) for k in dir(_base_mod) if not k.startswith("__")})

# Re-exportar LikelihoodEngine con interfaz extendida
_BaseLikelihoodEngine = _base_mod.LikelihoodEngine

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
                _lr_cal = _il.import_module("lr_calibration")
                _calibrator = _lr_cal.LRCalibrator(calibration_path)
            except Exception:
                pass

        super().__init__(z_cap=z_cap, calibrator=_calibrator)
        self.hint_threshold_reject = hint_threshold_reject
        self.hint_threshold_accept = hint_threshold_accept
        self._calibration_path = calibration_path
        self._covariance_path = covariance_path
        self._mode = "calibrated" if _calibrator else "fallback"

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
            "contributions":      d.get("contributions", []),
            "components_used":    d.get("n_signals", len(signals)),
            "clustering_method":  "heuristic_default",
            "enfsi_label":        d.get("enfsi_label", "EQUIVOCAL"),
            "signal_count":       d.get("n_signals", len(signals)),
            "calibration_method": "fallback_gaussian",
            "_record":            d,
        }


def _correlation_penalty(signals):
    """Stub de compatibilidad para imports que lo usan directamente."""
    return 0.0
