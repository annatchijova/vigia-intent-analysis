"""
Test R7-1 — el emparejamiento traza <-> bundle, expuesto en el CLI.

Surprise / expectativa violada: `vigia/core/reasoning_trace.py` documenta el
invariante en su propio docstring —

    "The wiring and any verifier MUST assert this equals the sealed bundle
     verdict. A divergence is a wiring bug [...] and must FAIL verification,
     never be silently reconciled."

— y lo implementa correctamente en `verify_reasoning_trace()`. Pero esa funcion
solo se llamaba desde un test: `vigia_agent.py` la nombraba en un comentario
("verify_reasoning_trace() binds the two") sin invocarla, y ningun CLI la
exponia.

La reasoning trace vive FUERA del digest del bundle — es un archivo hermano con
integridad propia — asi que su cadena puede estar perfectamente intacta y aun
asi explicar OTRO caso: nada dentro de la cadena dice a que bundle pertenece.

Medido sobre artefactos reales de `vigia/results/mode1_crosscheck/`: la traza de
JESS-M1 (veredicto SUSPICION) presentada junto al bundle de FLAREON-2017-M1
(veredicto MALICE) daba "CHAIN VERIFIED", exit 0, "Timeline: PLAUSIBLE". Un
perito que corriera los comandos documentados verificaba los dos artefactos como
intactos sin enterarse de que no van juntos.

Fix, en los dos extremos:
  - produccion: `vigia_agent.py` llama `verify_reasoning_trace()` antes de
    escribir la traza y no la escribe si diverge (fail-soft respecto del bundle
    ya sellado, pero reportado como WIRING BUG, no como ruido de escritura);
  - verificacion: `verify_tool_log.py` reconoce una reasoning trace, busca el
    bundle hermano `<stem>.json` (o acepta `--paired-bundle`) y compara case_id
    y veredicto. Sin bundle con que comparar lo DICE, en vez de dejar que
    "CHAIN VERIFIED" se lea como "esta traza explica ese bundle".
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
CROSS = REPO_ROOT / "vigia" / "results" / "mode1_crosscheck"
MALICE_BUNDLE = CROSS / "FLAREON-2017_mode1_bundle.json"
MALICE_TRACE = CROSS / "FLAREON-2017_mode1_bundle_reasoning_trace.json"
SUSPICION_TRACE = CROSS / "JESS_mode1_bundle_reasoning_trace.json"


def _require(*paths):
    for p in paths:
        if not p.exists():
            pytest.skip(f"artefacto de referencia ausente: {p.name}")


def _run(*args):
    return subprocess.run(
        [sys.executable, "verify_tool_log.py", *[str(a) for a in args]],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )


class TestR7CliPairing:
    def test_legitimate_pair_verifies_and_reports_the_pairing(self):
        _require(MALICE_TRACE, MALICE_BUNDLE)
        r = _run(MALICE_TRACE)
        assert r.returncode == 0, r.stdout
        assert "Pairing traza <-> bundle" in r.stdout
        assert "[OK  ] case_id" in r.stdout
        assert "[OK  ] veredicto" in r.stdout

    def test_swapped_trace_is_rejected(self):
        """El vector: traza SUSPICION presentada junto al bundle MALICE."""
        _require(SUSPICION_TRACE, MALICE_BUNDLE)
        r = _run(SUSPICION_TRACE, "--paired-bundle", MALICE_BUNDLE)
        assert r.returncode == 1, r.stdout
        assert "CHAIN BROKEN" in r.stdout
        assert "[FAIL] case_id" in r.stdout
        assert "[FAIL] veredicto" in r.stdout
        assert "SUSPICION" in r.stdout and "MALICE" in r.stdout

    def test_sibling_bundle_is_found_automatically(self, tmp_path):
        """Un perito corre `verify_tool_log.py trace.json` a secas: el
        emparejamiento tiene que ocurrir igual."""
        _require(SUSPICION_TRACE, MALICE_BUNDLE)
        # traza de JESS renombrada como si fuera la de FLAREON
        (tmp_path / "X_bundle.json").write_text(MALICE_BUNDLE.read_text())
        (tmp_path / "X_bundle_reasoning_trace.json").write_text(
            SUSPICION_TRACE.read_text())
        r = _run(tmp_path / "X_bundle_reasoning_trace.json")
        assert r.returncode == 1, r.stdout
        assert "[FAIL] veredicto" in r.stdout

    def test_orphan_trace_says_pairing_was_not_checked(self, tmp_path):
        """Honest degradation: sin hermano no se puede comparar — y eso se
        dice, en vez de dejar pasar 'CHAIN VERIFIED' como si probara mas."""
        _require(SUSPICION_TRACE)
        orphan = tmp_path / "huerfana.json"
        orphan.write_text(SUSPICION_TRACE.read_text())
        r = _run(orphan)
        assert r.returncode == 0, r.stdout
        assert "EN AISLAMIENTO" in r.stdout
        assert "--paired-bundle" in r.stdout

    def test_plain_bundle_is_unaffected(self):
        """Un bundle que no es una traza no dispara el chequeo."""
        _require(MALICE_TRACE)
        r = _run(MALICE_TRACE)
        assert "Pairing" in r.stdout
        plain = REPO_ROOT / "vigia" / "results" / "ROCBA-CDRIVE_bundle_claude_fable.json"
        if not plain.exists():
            pytest.skip("bundle sin traza ausente")
        r2 = _run(plain)
        assert r2.returncode == 0, r2.stdout
        assert "Pairing" not in r2.stdout

    def test_all_real_pairs_still_verify(self):
        """Regresion: los pares legitimos del repo no deben romperse."""
        traces = sorted(CROSS.glob("*_reasoning_trace.json"))
        if not traces:
            pytest.skip("sin pares de referencia")
        for trace in traces:
            r = _run(trace)
            assert r.returncode == 0, f"{trace.name}:\n{r.stdout}"


class TestR7ProductionSideEnforcement:
    def test_agent_calls_verify_reasoning_trace(self):
        """El comentario de vigia_agent.py afirmaba que esta funcion ata los dos
        artefactos; ahora efectivamente la llama."""
        src = (REPO_ROOT / "vigia_agent.py").read_text()
        assert "verify_reasoning_trace(bundle, _trace_dict)" in src
        assert "_TracePairingError" in src

    def test_diverging_trace_is_not_written(self, tmp_path, monkeypatch):
        """Una traza que no empareja no debe escribirse como si explicara el
        bundle. Se ejercita la funcion de verificacion directamente: el bundle
        MALICE contra la traza SUSPICION."""
        from vigia.core.reasoning_trace import verify_reasoning_trace
        _require(MALICE_BUNDLE, SUSPICION_TRACE)
        bundle = json.loads(MALICE_BUNDLE.read_text())
        trace = json.loads(SUSPICION_TRACE.read_text())
        result = verify_reasoning_trace(bundle, trace)
        assert not result.valid
        assert any("VERDICT DIVERGENCE" in e for e in result.errors)

    def test_matching_trace_passes(self):
        from vigia.core.reasoning_trace import verify_reasoning_trace
        _require(MALICE_BUNDLE, MALICE_TRACE)
        result = verify_reasoning_trace(json.loads(MALICE_BUNDLE.read_text()),
                                        json.loads(MALICE_TRACE.read_text()))
        assert result.valid, result.errors
