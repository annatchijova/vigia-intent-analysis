"""
vigia/core/signal_adapter.py
─────────────────────────────────────────────────────────────────────────────
Adaptador de Señales — ForensicEngine → SignalOutput

PROBLEMA:
    El ForensicEngine (adversarial_nlp.py) retorna dicts heterogéneos
    con claves propias de cada herramienta (sda_nr, cli, acp, roi).
    El LikelihoodEngine solo consume SignalOutput.

SOLUCIÓN:
    Este módulo extrae las señales relevantes de los dicts legacy y las
    envuelve en SignalOutput, sin modificar adversarial_nlp.py.

    PRINCIPIO: No rompemos lo que funciona. El ForensicEngine existente
    sigue siendo el sistema operativo. Este adaptador es la capa de
    transición hacia el LikelihoodEngine.

BASELINE:
    Los z-scores se calculan contra el baseline AUTHENTIC del dataset
    bootstrap. Los valores por defecto son los del bootstrap v1.
    Actualizar con build_baseline_from_authentic() una vez calibrado.

SEPARACIÓN DE CAPAS (Daubert):
    EVIDENCE LAYER  → ForensicEngine + GCIEngine + DGPIEngine
                    → signal_adapter.py extrae SignalOutput
    INFERENCE LAYER → LikelihoodEngine consume SignalOutput
    REPORT LAYER    → LLM recibe ForensicRecord, genera narrativa ENFSI
─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from vigia.core.ebs_v1 import SignalOutput
from vigia.tools.signal_contract import SignalBuilder

import datetime
import hashlib
import json


# ---------------------------------------------------------------------------
# BaselineProfile — perfil de baseline versionado, inmutable y trazable
# ---------------------------------------------------------------------------

class BaselineProfile:
    """
    Perfil de baseline versionado e inmutable para trazabilidad Daubert.

    Nota de implementación:
        En CPython puro, object.__setattr__ puede bypassar __setattr__ en clases
        con __slots__. La única forma de inmutabilidad total es NamedTuple o
        evitar __slots__. Esta implementación usa __slots__ + __setattr__ override
        para bloquear el acceso ordinario y de alto nivel. El bypass via
        object.__setattr__ es un vector de CPython interno documentado —
        cualquier code review lo detectaría. Para producción, usar frozendict
        o una solución a nivel de empaquetado (mypy strict + linting).
    """
    __slots__ = ("version", "domain", "source", "created_at", "stats", "_hash_cache")

    def __init__(
        self,
        version: str,
        domain: str,
        source: str,
        created_at: str,
        stats: tuple,
    ) -> None:
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "stats", stats)
        object.__setattr__(self, "_hash_cache", None)
        # Sellamos la instancia: cualquier intento posterior de escritura
        # vía atributo normal o __dict__ lanza AttributeError.

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(
            f"BaselineProfile es inmutable (Daubert). "
            f"No se puede modificar '{name}' post-construcción."
        )

    def __delattr__(self, name: str) -> None:
        raise AttributeError(
            f"BaselineProfile es inmutable (Daubert). "
            f"No se puede eliminar '{name}'."
        )

    def __repr__(self) -> str:
        return (
            f"BaselineProfile(version={self.version!r}, "
            f"domain={self.domain!r}, hash={self.profile_hash})"
        )

    def get(self, tool_name: str) -> dict:
        """Retorna {\"mean\": float, \"mad\": float} para una herramienta."""
        for name, mean, mad in self.stats:
            if name == tool_name:
                return {"mean": mean, "mad": mad}
        return {"mean": 0.0, "mad": 1.0}

    @property
    def profile_hash(self) -> str:
        """SHA-256 del perfil. Cacheado — el objeto es inmutable una vez construido."""
        cached = object.__getattribute__(self, "_hash_cache")
        if cached is not None:
            return cached
        payload = json.dumps({
            "version": self.version,
            "domain": self.domain,
            "source": self.source,
            "stats": list(self.stats),
        }, sort_keys=True)
        h = hashlib.sha256(payload.encode()).hexdigest()[:16]
        object.__setattr__(self, "_hash_cache", h)
        return h

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "domain": self.domain,
            "source": self.source,
            "created_at": self.created_at,
            "profile_hash": self.profile_hash,
            "stats": {name: {"mean": m, "mad": d} for name, m, d in self.stats},
        }


def _make_baseline(version: str, domain: str, source: str, stats: dict) -> BaselineProfile:
    """Factory conveniente para construir un BaselineProfile desde un dict."""
    stats_tuple = tuple(
        (tool, float(v["mean"]), float(v["mad"]))
        for tool, v in sorted(stats.items())
    )
    return BaselineProfile(
        version=version,
        domain=domain,
        source=source,
        created_at=datetime.datetime.utcnow().isoformat() + "Z",
        stats=stats_tuple,
    )


# ---------------------------------------------------------------------------
# Perfiles de baseline disponibles
# Bootstrap v2 — calibrado con generate_bootstrap_dataset(seed=42)
# ---------------------------------------------------------------------------

BASELINE_BOOTSTRAP_V2 = _make_baseline(
    version="bootstrap-v2",
    domain="legal_es",
    source="validate_dataset.py::generate_bootstrap_dataset(seed=42)",
    stats={
        "SDA": {"mean": 0.90, "mad": 0.35},
        "CLI": {"mean": 0.28, "mad": 0.12},
        "ACP": {"mean": 0.50, "mad": 0.25},
        "ROI": {"mean": 0.10, "mad": 0.08},
    },
)

# Alias: perfil por defecto activo
DEFAULT_BASELINE: BaselineProfile = BASELINE_BOOTSTRAP_V2


# ---------------------------------------------------------------------------
# Excepción de schema
# ---------------------------------------------------------------------------

class ForensicVerdictSchemaError(ValueError):
    """Lanzado cuando forensic_verdict_dict no cumple el schema esperado."""
    pass


# ---------------------------------------------------------------------------
# Validación de schema (Parche 5)
# ---------------------------------------------------------------------------

_REQUIRED_TOP_KEYS = ("analisis_capas",)
_REQUIRED_CAPAS_KEYS = ("sda_nr", "cli")  # mínimo obligatorio

def _validate_verdict_schema(d: dict) -> None:
    """
    Valida que el dict tenga las claves mínimas requeridas.
    Lanza ForensicVerdictSchemaError con detalle de qué falta.
    """
    for key in _REQUIRED_TOP_KEYS:
        if key not in d:
            raise ForensicVerdictSchemaError(
                f"forensic_verdict_dict falta clave obligatoria: '{key}'. "
                f"Claves presentes: {sorted(d.keys())}"
            )
    capas = d["analisis_capas"]
    if not isinstance(capas, dict):
        raise ForensicVerdictSchemaError(
            f"'analisis_capas' debe ser dict, recibido: {type(capas).__name__}"
        )
    missing = [k for k in _REQUIRED_CAPAS_KEYS if k not in capas]
    if missing:
        raise ForensicVerdictSchemaError(
            f"'analisis_capas' falta claves mínimas: {missing}. "
            f"Claves presentes: {sorted(capas.keys())}"
        )


def _compute_residuals(
    deltas: List[float],
    dgpi_result: Any,
) -> Optional[List[float]]:
    """
    Calcula residuals = deltas - model(deltas) según el patrón DGPI detectado.

    CONSTANT_SLEEP / JITTER_OBFUSCATED:
        model(t) = detected_constant
    LINEAR_DRIFT:
        model(t) = slope * t + intercept
    SINUSOIDAL_MIMICRY:
        model(t) = A*sin(2π*freq*t) + C
    Otros:
        retorna None
    """
    import math as _math
    params = getattr(dgpi_result, "parameters", {})
    ptype  = getattr(dgpi_result, "pattern_type", "")
    n = len(deltas)

    if ptype in ("CONSTANT_SLEEP", "JITTER_OBFUSCATED"):
        c = params.get("C")
        if c is None:
            return None
        return [abs(d - c) for d in deltas]

    if ptype == "LINEAR_DRIFT":
        slope = params.get("slope", 0.0)
        intercept = params.get("intercept", 0.0)
        return [abs(deltas[i] - (slope * i + intercept)) for i in range(n)]

    if ptype == "SINUSOIDAL_MIMICRY":
        freq = params.get("freq_hz", 0.0)
        amplitude = params.get("amplitude", 1.0)
        if freq <= 0:
            return None
        mean_d = sum(deltas) / n
        fitted = [amplitude * _math.sin(2 * _math.pi * freq * i) + mean_d for i in range(n)]
        return [abs(deltas[i] - fitted[i]) for i in range(n)]

    return None


# ---------------------------------------------------------------------------
# Extractores por herramienta
# Todos reciben baseline: BaselineProfile (por defecto DEFAULT_BASELINE)
# ---------------------------------------------------------------------------

def extract_sda_signal(
    sda_dict: Dict[str, Any],
    discriminator: str = "",
    emitter_type: str = "UNKNOWN",
    baseline: BaselineProfile = None,
) -> Optional[SignalOutput]:
    """
    Extrae señal SDA.

    sigma_max YA ES un z-score calculado por SDA_NominalizationAnalyzer
    contra su baseline institucional interno → is_pre_normalized=True.
    Evita la doble normalización identificada en auditoría (ChatGPT §1.1).
    """
    sigma_max = sda_dict.get("sigma_max")
    if sigma_max is None or not math.isfinite(sigma_max):
        return None

    bl = (baseline or DEFAULT_BASELINE).get("SDA")
    return SignalBuilder.from_raw(
        tool_name="SDA",
        value=sigma_max,
        baseline_mean=bl["mean"],
        baseline_mad=bl["mad"],
        confidence=_sda_confidence(sda_dict),
        discriminator=discriminator,
        is_pre_normalized=True,
        metadata={
            "emitter_type": emitter_type,
            "baseline_version": (baseline or DEFAULT_BASELINE).version,
            "baseline_domain": (baseline or DEFAULT_BASELINE).domain,
            "z_nv": sda_dict.get("z_nv", 0.0),
            "z_nom": sda_dict.get("z_nom", 0.0),
            "nv_ratio": sda_dict.get("nv_ratio", 0.0),
            "nominalization": sda_dict.get("nominalization", 0.0),
            "language": sda_dict.get("language", "?"),
            "generator_version": "SDA_NominalizationAnalyzer-v2",
            "transform_chain": ["nlp_morphosyntactic"],
        },
    )


def extract_cli_signal(
    cli_dict: Dict[str, Any],
    discriminator: str = "",
    emitter_type: str = "UNKNOWN",
    baseline: BaselineProfile = None,
) -> Optional[SignalOutput]:
    """
    Extrae señal CLI.

    cognitive_stress_index es una métrica cruda compuesta (no z-score puro)
    → is_pre_normalized=False, se normaliza contra el baseline AUTHENTIC.
    """
    stress = cli_dict.get("cognitive_stress_index")
    if stress is None or not math.isfinite(stress):
        return None

    bl = (baseline or DEFAULT_BASELINE).get("CLI")
    return SignalBuilder.from_raw(
        tool_name="CLI",
        value=stress,
        baseline_mean=bl["mean"],
        baseline_mad=bl["mad"],
        confidence=_cli_confidence(cli_dict),
        discriminator=discriminator,
        is_pre_normalized=False,
        metadata={
            "emitter_type": emitter_type,
            "baseline_version": (baseline or DEFAULT_BASELINE).version,
            "baseline_domain": (baseline or DEFAULT_BASELINE).domain,
            "z_exclusion": cli_dict.get("z_exclusion", 0.0),
            "z_certainty": cli_dict.get("z_certainty", 0.0),
            "exclusion_density": cli_dict.get("exclusion_density", 0.0),
            "certainty_density": cli_dict.get("certainty_density", 0.0),
            "generator_version": "CLI_Analyzer-v2",
            "transform_chain": ["nlp_epistemic_markers"],
        },
    )


def extract_acp_signal(
    acp_dict: Dict[str, Any],
    discriminator: str = "",
    emitter_type: str = "UNKNOWN",
    baseline: BaselineProfile = None,
) -> Optional[SignalOutput]:
    """
    Extrae señal ACP.

    max_zscore YA ES un z-score calculado por ACP contra baseline autoral
    → is_pre_normalized=True.
    """
    max_z = acp_dict.get("max_zscore")
    if max_z is None or not math.isfinite(max_z):
        return None

    bl = (baseline or DEFAULT_BASELINE).get("ACP")
    return SignalBuilder.from_raw(
        tool_name="ACP",
        value=abs(max_z),
        baseline_mean=bl["mean"],
        baseline_mad=bl["mad"],
        confidence=acp_dict.get("confidence_score", 0.7),
        discriminator=discriminator,
        is_pre_normalized=True,
        metadata={
            "emitter_type": emitter_type,
            "baseline_version": (baseline or DEFAULT_BASELINE).version,
            "baseline_domain": (baseline or DEFAULT_BASELINE).domain,
            "is_identity_spoofing": acp_dict.get("is_identity_spoofing", False),
            "generator_version": "ACP_Protocol-v2",
            "transform_chain": ["nlp_authorship_consistency"],
        },
    )


def extract_roi_signal(
    roi_dict: Dict[str, Any],
    discriminator: str = "",
    emitter_type: str = "UNKNOWN",
    baseline: BaselineProfile = None,
) -> Optional[SignalOutput]:
    """
    Extrae señal ROI.

    attack_confidence es un score crudo [0,1]
    → is_pre_normalized=False.
    """
    attack_conf = roi_dict.get("attack_confidence")
    if attack_conf is None or not math.isfinite(attack_conf):
        return None

    bl = (baseline or DEFAULT_BASELINE).get("ROI")
    return SignalBuilder.from_raw(
        tool_name="ROI",
        value=attack_conf,
        baseline_mean=bl["mean"],
        baseline_mad=bl["mad"],
        confidence=0.75,
        discriminator=discriminator,
        is_pre_normalized=False,
        metadata={
            "emitter_type": emitter_type,
            "baseline_version": (baseline or DEFAULT_BASELINE).version,
            "baseline_domain": (baseline or DEFAULT_BASELINE).domain,
            "is_obfuscation_attack": roi_dict.get("is_obfuscation_attack", False),
            "obfuscation_type": roi_dict.get("obfuscation_type", "UNKNOWN"),
            "generator_version": "ROI_Analyzer-v2",
            "transform_chain": ["nlp_register_obfuscation"],
        },
    )


def extract_all_signals(
    forensic_verdict_dict: Dict[str, Any],
    discriminator: str = "",
    baseline: BaselineProfile = None,
) -> List[SignalOutput]:
    """
    Extrae todas las señales disponibles de un ForensicVerdict serializado.
    El baseline activo queda registrado en metadata de cada señal (Daubert).
    """
    capas = forensic_verdict_dict.get("analisis_capas", {})
    emitter = forensic_verdict_dict.get("document", {}).get("emitter", {}).get("type", "UNKNOWN")
    bl = baseline or DEFAULT_BASELINE

    extractors = [
        (extract_sda_signal, capas.get("sda_nr", {})),
        (extract_cli_signal, capas.get("cli", {})),
        (extract_acp_signal, capas.get("acp", {})),
        (extract_roi_signal, capas.get("roi", {})),
    ]

    signals: List[SignalOutput] = []
    for fn, data in extractors:
        if data:
            sig = fn(data, discriminator=discriminator, emitter_type=emitter, baseline=bl)
            if sig is not None:
                signals.append(sig)

    return signals


# ---------------------------------------------------------------------------
# Helpers de confianza interna
# ---------------------------------------------------------------------------

def _sda_confidence(d: Dict) -> float:
    """
    Confianza SDA: alta si hay suficientes palabras para el análisis morfosintáctico.
    """
    counts = d.get("counts", {})
    total = sum(counts.get(k, 0) for k in ("nouns", "verbs", "adjs"))
    if total >= 100:
        return 0.95
    if total >= 30:
        return 0.80
    if total >= 10:
        return 0.60
    return 0.40


def _cli_confidence(d: Dict) -> float:
    """
    Confianza CLI: alta si hay marcadores detectados.
    """
    excl = d.get("exclusion_density", 0.0)
    cert = d.get("certainty_density", 0.0)
    if excl + cert > 0.05:
        return 0.88
    if excl + cert > 0.01:
        return 0.72
    return 0.55


# ---------------------------------------------------------------------------
# Integración directa: ForensicVerdict → [SignalOutput] + ForensicRecord
# ---------------------------------------------------------------------------

def run_full_pipeline(
    forensic_verdict_dict: Dict[str, Any],
    likelihood_engine: Any,
    gci_result: Optional[Any] = None,
    dgpi_result: Optional[Any] = None,
    correlation_matrix: Optional[List[List[float]]] = None,
    baseline: BaselineProfile = None,
) -> Dict[str, Any]:
    """
    Pipeline completo: ForensicVerdict → SignalOutput[] → ForensicRecord.

    Parche 5: valida schema upfront — lanza ForensicVerdictSchemaError si faltan claves.
    Parche 2: acepta baseline explícito; registra su version/hash en el output.
    Parche 4: boost de confianza como factor multiplicativo (no sumativo).
    Parche 3: residual loop con logging estructurado en lugar de except:pass silencioso.
    """
    # ── Parche 5: Validación de schema ──────────────────────────────────────
    _validate_verdict_schema(forensic_verdict_dict)

    bl = baseline or DEFAULT_BASELINE
    doc_id = forensic_verdict_dict.get("document", {}).get("id", "unknown")
    signals = extract_all_signals(forensic_verdict_dict, discriminator=doc_id, baseline=bl)

    # ── GCI + DGPI ──────────────────────────────────────────────────────────
    gci_z_high = False
    dgpi_found = False

    if gci_result is not None and hasattr(gci_result, "signal"):
        gci_z_high = gci_result.signal.z_score > 2.0
        signals.append(gci_result.signal)

    if dgpi_result is not None and hasattr(dgpi_result, "signal"):
        dgpi_found = dgpi_result.is_algorithmic
        if gci_z_high and dgpi_found:
            # ── Parche 4: boost multiplicativo (no sumativo) ─────────────
            # Factor 1.15 cuando GCI y DGPI coinciden — conservador pero
            # trazable. La alternativa correcta es integrar como señal de
            # consistencia en LikelihoodEngine; pendiente para dataset real.
            import dataclasses as _dc
            boosted_confidence = min(1.0, dgpi_result.signal.confidence * 1.15)
            try:
                boosted = dgpi_result.signal.model_copy(
                    update={"confidence": boosted_confidence}
                )
            except AttributeError:
                boosted = _dc.replace(dgpi_result.signal, confidence=boosted_confidence)
            signals.append(boosted)
        else:
            signals.append(dgpi_result.signal)

    # ── Parche 3: Residual loop con logging estructurado ────────────────────
    residual_gci_signal = None
    _residual_error: Optional[str] = None
    if (
        dgpi_result is not None
        and dgpi_found
        and hasattr(dgpi_result, "parameters")
        and gci_result is not None
    ):
        try:
            raw_deltas = (
                gci_result.signal.metadata.get("raw_deltas")
                if gci_result.signal.metadata else None
            )
            if raw_deltas and len(raw_deltas) >= 5:
                residuals = _compute_residuals(raw_deltas, dgpi_result)
                if residuals and len(residuals) >= 5:
                    from vigia.tools.eml_gci import analyze_gci as _agci
                    res_gci = _agci(
                        deltas=residuals,
                        discriminator=f"residual-{doc_id}",
                        metadata={
                            "role": "residual_analysis",
                            "parent_pattern": dgpi_result.pattern_type,
                        },
                    )
                    residual_gci_signal = res_gci
                    if res_gci.signal.z_score > 2.0:
                        signals.append(res_gci.signal)
        except Exception as _exc:
            # Log estructurado — no silencioso (Parche 3)
            _residual_error = f"{type(_exc).__name__}: {_exc}"
            try:
                from vigia.security import audit_logger
                audit_logger.log_info(
                    event_type="RESIDUAL_LOOP_FAILED",
                    tool="signal_adapter.run_full_pipeline",
                    message=_residual_error,
                )
            except Exception:
                import sys
                print(f"[VIGIA_WARN] RESIDUAL_LOOP_FAILED doc={doc_id} err={_residual_error}",
                      file=sys.stderr)

    if not signals:
        raise ForensicVerdictSchemaError(
            f"No se pudieron extraer señales del ForensicVerdict (doc_id={doc_id}). "
            "Verificar que analisis_capas contiene sda_nr y cli con datos válidos."
        )

    lr_record = likelihood_engine.infer(signals, correlation_matrix=correlation_matrix)

    anomaly_flag = None
    if gci_z_high and not dgpi_found:
        anomaly_flag = (
            "STATISTICAL_ANOMALY_WITHOUT_GENERATIVE_MODEL — "
            "GCI detecta cadencia anómala pero DGPI no identifica función generadora. "
            "Posible: patrón nuevo, dataset insuficiente o adversario sofisticado."
        )

    result = {
        "document_id": doc_id,
        "baseline": {
            "version": bl.version,
            "domain": bl.domain,
            "profile_hash": bl.profile_hash,
        },
        "signals": [
            {
                "tool": s.tool_name,
                "signal_id": s.signal_id,
                "value": round(s.value, 4),
                "z_score": round(s.z_score, 4),
                "confidence": round(s.confidence, 4),
                "is_pre_normalized": (s.metadata or {}).get("is_pre_normalized", False),
            }
            for s in signals
        ],
        "lr_record": lr_record.to_dict(),
        "mcp_legacy": forensic_verdict_dict.get("mcp", {}).get("valor"),
        "mcp_verdict_legacy": forensic_verdict_dict.get("veredicto", {}).get("categoria"),
        "enfsi_label": lr_record.enfsi_label,
        "posterior_probability": round(lr_record.posterior_probability, 4),
        "anomaly_flag": anomaly_flag,
        "residual_analysis": (
            {
                "z_score": round(residual_gci_signal.signal.z_score, 4),
                "pattern_label": residual_gci_signal.pattern_label,
                "is_compound_generator": residual_gci_signal.signal.z_score > 2.0,
            }
            if residual_gci_signal is not None else None
        ),
        "residual_loop_error": _residual_error,
        "layer_separation": {
            "evidence_layer": [s.tool_name for s in signals],
            "inference_layer": "LikelihoodEngine-v0 (determinístico, sin LLM)",
            "report_layer": "LLM — narrativa Amicus Curiae (no vinculante, no entra al LR)",
        },
        "daubert_record_hash": lr_record.record_hash(),
    }
    # B8 (A-1): self-check del hash que acabamos de embeber — una asimetría
    # de serialización/cuantización rompe ACÁ (fail-loud), no años después
    # en el peritaje. El verificador es el mismo que usaría el perito.
    from vigia.core.likelihood_ratio import verify_daubert_record_hash
    _ok, _msg = verify_daubert_record_hash(result)
    if not _ok:
        raise RuntimeError(f"B8 self-check daubert_record_hash falló: {_msg}")
    return result
