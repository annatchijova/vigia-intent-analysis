"""
vigia/core/darvo_detector.py
DARVO Detector — asimetría de contacto actor_a vs actor_b

B-140 (L-029 / FW-009 Fase 1): anota el path motor
(vigia_scorer._vigia_score) vía detect_darvo_pattern() — detección
estructurada con trazabilidad Daubert, SIN efecto en veredicto. El efecto
sobre veredicto y el veredicto relacional false_flag siguen siendo
decisiones de doctrina (KNOWN_LIMITATIONS L-029).

F0 (2026-07-17, tanda firmada — dossier docs/PROPUESTA_L029_DARVO_20260717.md
+ auditoría docs/VEREDICTO_KIMI_L029_20260717.md):
  - Matching con word-boundaries: el substring desnudo acuñó el falso
    positivo ELI ('no contact' matcheaba dentro de "no contacts database" —
    un plural inglés) y hacía que 'log' disparara sobre cada "logs".
  - Las APIs de penalidad del pipeline (compute_darvo_penalty,
    adjust_consistency_score) fueron RETIRADAS (B-142): el canal era código
    muerto en runtime (SignalOutput no porta description/evidence_type) y
    dejarlo vivo era superficie latente que cualquier refactor del contrato
    de señales despertaría sin gate (L-004/B-070).
"""
from __future__ import annotations
import re
from fractions import Fraction
from typing import Any, Dict, List

SURVEILLANCE_KEYWORDS = ('honeypot', 'accesos', 'server', 'log', 'stalkeo', 'php error', 'trampolin')
ZERO_CONTACT_KEYWORDS = ('cero contacto', 'zero contact', 'no contact', 'bloqueado')
_SURVEILLANCE_TYPES = ('file_metadata', 'log_entry')


def _compile_keywords(keywords):
    """F0: patrones con frontera de palabra en ambos bordes.

    Lookarounds en vez de \\b para que las frases multi-palabra ('php
    error', 'cero contacto') anclen igual en los dos extremos. Con esto
    'no contact' ya NO matchea "no contactS database" (el plural que acuñó
    el FP ELI) y 'log' ya no matchea "logs"; 'server' como palabra suelta
    sigue matcheando ("4 S3 server list URLs") — la des-anotación de ELI
    viene del lado cero-contacto, y queda documentada así, honestamente.
    """
    return tuple(
        re.compile(r"(?<!\w)" + re.escape(k) + r"(?!\w)") for k in keywords
    )


_SURVEILLANCE_RES = _compile_keywords(SURVEILLANCE_KEYWORDS)
_ZERO_CONTACT_RES = _compile_keywords(ZERO_CONTACT_KEYWORDS)


def _field(artifact: Any, name: str, default: Any = None) -> Any:
    """Lee un campo de un artefacto dado como objeto O como dict (B-140).

    El path Modo 1 (EBS JSON) pasa artefactos como dicts planos; solo
    getattr dejaba al detector estructuralmente ciego frente a dicts.
    """
    if isinstance(artifact, dict):
        return artifact.get(name, default)
    return getattr(artifact, name, default)


def detect_darvo_pattern(artifacts: List[Any]) -> Dict[str, Any]:
    """Detección estructurada de la asimetría DARVO (FW-009 Fase 1).

    Devuelve conteos, la penalidad en Fraction y los ids de los artefactos
    que dispararon (trazabilidad Daubert). Aritmética Fraction pura,
    determinista; total frente a campos malformados (str() coercion,
    metadata no-dict tratada como vacía).
    """
    surveillance_count = 0
    zero_contact_count = 0
    matched: List[str] = []
    spans: List[Dict[str, str]] = []

    def _span(art_id: str, family: str, keyword: str, desc: str, m) -> Dict[str, str]:
        # F1: trazabilidad Daubert por keyword — familia, keyword y ventana
        # de contexto (decisión FIRMA: spans SÍ; la lista de keywords ya es
        # pública en el repo, la transparencia gana).
        return {
            "artifact_id": art_id,
            "family": family,
            "keyword": keyword,
            "context": desc[max(0, m.start() - 30):m.end() + 30],
        }

    for idx, a in enumerate(artifacts):
        desc = str(_field(a, 'description', '') or '').lower()
        meta = _field(a, 'metadata', None)
        if not isinstance(meta, dict):
            meta = {}
        etype = _field(a, 'evidence_type', None) or meta.get('evidence_type', '')
        art_id = str(_field(a, 'artifact_id', None) or f'#{idx}')

        hit = False
        if etype in _SURVEILLANCE_TYPES:
            surv_matches = [
                (kw, rx.search(desc))
                for kw, rx in zip(SURVEILLANCE_KEYWORDS, _SURVEILLANCE_RES)
            ]
            surv_matches = [(kw, m) for kw, m in surv_matches if m]
            if surv_matches:
                surveillance_count += 1
                hit = True
                for kw, m in surv_matches:
                    spans.append(_span(art_id, "surveillance", kw, desc, m))
        zc_matches = [
            (kw, rx.search(desc))
            for kw, rx in zip(ZERO_CONTACT_KEYWORDS, _ZERO_CONTACT_RES)
        ]
        zc_matches = [(kw, m) for kw, m in zc_matches if m]
        if zc_matches:
            zero_contact_count += 1
            hit = True
            for kw, m in zc_matches:
                spans.append(_span(art_id, "zero_contact", kw, desc, m))
        if hit:
            matched.append(art_id)

    if surveillance_count == 0:
        penalty = Fraction(0)
    elif zero_contact_count > 0:
        penalty = min(Fraction(8, 10), Fraction(surveillance_count * 3, 10))
    else:
        penalty = min(Fraction(8, 10), Fraction(surveillance_count, 10))

    return {
        # pattern_present exige la asimetría COMPLETA: infraestructura de
        # vigilancia Y reclamo de cero contacto. Keywords de vigilancia
        # solos ('log', 'server'...) disparan en decenas de casos del
        # corpus (incluidos benignos) — anotarlos como "DARVO" sería
        # narrativa engañosa. Censo F0 (2026-07-17, post word-boundary):
        # exactamente 4 casos anotados — KIWI-001/003/004/005, es decir UN
        # expediente (MPF7779408) + 2 copias declaradas. El quinto anotado
        # de B-140 (MAGNET-2021-IOS-ELI) era un falso positivo de substrings
        # ('server' en "S3 server list URLs", 'no contact' en "no contactS
        # database") corregido en esta tanda — B-142, dossier §1.1.
        # Limitación documentada: "cero intentos de contacto" (KIWI-003-A01)
        # NO matchea 'cero contacto'; ampliar la frase sería tuning sobre
        # N=1 — se documenta en vez de ajustarse.
        "pattern_present": surveillance_count > 0 and zero_contact_count > 0,
        # penalty conserva la fórmula histórica SOLO como trazabilidad de la
        # anotación; ya no tiene consumidores de decisión (B-142 retiró el
        # canal del pipeline).
        "penalty": penalty,
        "surveillance_count": surveillance_count,
        "zero_contact_count": zero_contact_count,
        "matched_artifacts": matched,
        "matched_spans": spans,
    }
