"""
Contrato: el estado de cada entrada del registro debe ser legible por máquina.

MOTIVO (2026-08-01). Tres auditorías independientes del registro —dos de
modelos externos, una mía— produjeron números falsos leyendo estos mismos
ficheros:

  · una reportó B-115 y B-172 como abiertos: B-115 está SUBSUMIDO EN B-136 y
    B-172 MITIGADO;
  · otra reportó "82 de 200 bugs (41%) con efectos colaterales": el conteo
    real de lenguaje explícito de efecto colateral es 6 de 194 (3%). El
    parseo había confundido REFERENCIA CRUZADA con efecto colateral — el 71%
    de las entradas menciona otro B-NNN, y eso no significa nada;
  · la mía dio "56 abiertos" leyendo sólo el encabezado, y luego "5 entradas
    sin estado" exigiendo `**Estado**` en negritas. Ambas cifras eran falsas.

Medición correcta, con el parser de este módulo: **211 entradas — 199 CLOSED,
8 OPEN, 4 PARTIAL, 0 sin estado.**

  ABIERTAS  B-010 B-111 B-112 B-113 B-123 B-124 B-149 L-040
  PARCIALES B-129 B-145 B-151 B-162

Ninguno de los tres se equivocó por descuido. Se equivocaron porque el
registro expresa el estado de **cuatro formas distintas**, y cada parser
adivinó una:

  1. fila de tabla `| **Estado** | ... |`      (135 entradas)
  2. tag entre corchetes en el encabezado       ( 73 entradas)
  3. fila de tabla `| Estado | ... |` sin negritas (2 entradas)
  4. paréntesis en el encabezado                ( 1 entrada, normalizada a
                                                  corchetes por este cambio)

Este contrato NO normaliza las 211 entradas: reescribir un registro forense
histórico es riesgo sin beneficio, y las cuatro formas ya conviven. Lo que
hace es garantizar que **toda** entrada sea parseable por `parse_status()`,
que es una única implementación compartida en vez de una regex por auditoría.

Quien audite el registro debe importar `parse_status` de aquí en lugar de
escribir su propio regex. Ése es el punto del módulo.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY_FILES = ("BUGS_HISTORICO.md", "BUGS_PENDIENTES.md")

_ENTRY_RE = re.compile(r"(?m)^## ((?:B|L)-\d{3}[^\n]*)")
_ID_RE = re.compile(r"((?:B|L)-\d{3})")
_HEAD_TAG_RE = re.compile(r"\[([^\]]+)\]\s*$")
_ROW_RE = re.compile(r"\|\s*\*?\*?(?:Estado|Status)\*?\*?\s*\|([^|]*)\|")

# Vocabulario extraído de las 211 entradas reales, no inventado. Cada token se
# mapea a la única pregunta que un consumidor necesita responder: ¿esto sigue
# siendo un problema? Un token nuevo NO se clasifica en silencio — falla el
# test, para que quien lo introduzca decida su clase deliberadamente.
_CLOSED = {
    "RESUELTO", "RESOLVED", "FIXED", "CERRADO", "CLOSED", "APLICADO",
    "CORREGIDO", "MITIGADO", "MITIGATED", "DOCUMENTADO", "DOCUMENTED",
    "DESCARTADO", "DISCARDED", "SUBSUMIDO", "SUBSUMED", "SUPERSEDED",
    "NO APLICADO", "NOT ADOPTED", "NO ES UN BUG", "NOT A BUG",
    "CABLEADO", "MEDIDO", "VERIFICADO", "INVESTIGATED", "DELETED", "REMOVED",
    "HALLAZGO DE ARQUITECTURA DOCUMENTADO",
}
_OPEN = {
    "ABIERTO", "OPEN", "PENDIENTE", "PENDING", "POSPUESTO", "POSTPONED",
    "CANDIDATO", "CANDIDATE", "OBSERVADO", "OBSERVED", "TODO",
}
# Ni abierto ni cerrado: el trabajo avanzó pero queda resto declarado. Se
# distingue a propósito — colapsarlo a CERRADO es exactamente cómo un resto
# abierto desaparece de la vista.
_PARTIAL = {
    "PARCIALMENTE RESUELTO", "PARTIALLY RESOLVED", "REPARACIÓN PARCIAL",
    "REPARACION PARCIAL", "PARTIAL", "FASE 1 COMPLETADA",
}


def _tokens_present(raw: str) -> tuple[bool, bool, bool]:
    """(hay_cerrado, hay_abierto, hay_parcial) en el texto de estado completo.

    Se escanea el texto ENTERO, no su primer token, porque varias entradas
    llevan un estado DIVIDIDO: un mismo ID cubre dos sub-ítems con estados
    distintos.

      B-052: "P1 (narrativa honesta) FIXED ... P2 CERRADO ... NOT ADOPTED"
      B-151: "(a) RESUELTO (2026-07-19) ... (b) ABIERTO — decisión de arquitectura"

    Reducir eso a un token único es como se pierde un resto abierto: quien
    parsee el primero verá "FIXED"/"RESUELTO" y contará la entrada como
    cerrada. Ambas partes tienen que verse.
    """
    txt = " ".join(raw.strip().lstrip("*").split()).upper()

    # Un estado dividido se ANUNCIA con marcadores de sub-ítem: "(a)/(b)" o
    # "P1/P2". Ese es el discriminador — estructural, no léxico. Sin él, la
    # prosa que sigue al guión se cuela y produce falsos parciales:
    #
    #   B-090: 'RESUELTO — ... Marcado "⏳ abierto" en la auditoría fuente'
    #          "abierto" es una CITA histórica, no el estado actual.
    #   B-149: 'ABIERTO — ... Documentado como limitación'
    #          "documentado" describe cómo se manejó, no un cierre.
    #
    # Con marcadores -> se escanea todo (ambas partes cuentan).
    # Sin marcadores -> sólo la declaración inicial, antes del primer guión,
    # que es la convención del registro: "ESTADO — comentario".
    # `txt` ya está en mayúsculas: la clase debe cubrir ambos casos o "(a)"
    # nunca coincide (B-151 se clasificaba CLOSED perdiendo su parte (b)).
    dividido = re.search(r"\([A-Ca-c]\)", txt) or re.search(r"\bP[12]\b.*\bP[12]\b", txt)
    if not dividido:
        txt = re.split(r"—|\s-\s", txt, 1)[0]

    # Los marcadores de severidad y de sub-ítem no son estados.
    txt = re.sub(r"\bP[0-3]\b|\([A-Ca-c]\)", " ", txt)
    has = lambda bucket: any(re.search(rf"\b{re.escape(t)}\b", txt) for t in bucket)
    return has(_CLOSED), has(_OPEN), has(_PARTIAL)


def parse_status(heading: str, body: str) -> tuple[str, str]:
    """Devuelve `(clase, texto_de_estado)` para una entrada del registro.

    clase ∈ {"CLOSED", "OPEN", "PARTIAL", "UNKNOWN"}.

    Acepta las cuatro convenciones que conviven en el registro. La fila de
    tabla se prueba primero (es la que los autores actualizan), pero si no
    produce clasificación se cae al tag del encabezado: B-052 tiene una fila
    que empieza por un marcador de severidad y un tag que sí es explícito.
    """
    row = _ROW_RE.search(body)
    tag = _HEAD_TAG_RE.search(heading.strip())

    for raw in (row.group(1) if row else "", tag.group(1) if tag else ""):
        if not raw.strip():
            continue
        closed, open_, partial = _tokens_present(raw)
        text = " ".join(raw.split())[:80]
        if partial or (closed and open_):
            # Cerrado Y abierto a la vez = estado dividido. Nunca colapsar a
            # CLOSED: eso es exactamente cómo desaparece un resto abierto.
            return "PARTIAL", text
        if closed:
            return "CLOSED", text
        if open_:
            return "OPEN", text

    return "UNKNOWN", " ".join((row.group(1) if row else "").split())[:80]


def _entries() -> list[tuple[str, str, str, str]]:
    """(bug_id, fichero, encabezado, cuerpo) por cada entrada del registro."""
    out = []
    for fname in REGISTRY_FILES:
        text = (REPO / fname).read_text(encoding="utf-8")
        parts = _ENTRY_RE.split(text)
        for i in range(1, len(parts), 2):
            heading, body = parts[i], parts[i + 1]
            out.append((_ID_RE.match(heading).group(1), fname, heading, body))
    return out


# ---------------------------------------------------------------------------

def test_registry_is_not_empty():
    """Guarda de fondo: si el parser deja de encontrar entradas, todos los
    tests de abajo pasarían por vacuidad."""
    entries = _entries()
    assert len(entries) >= 200, (
        f"sólo {len(entries)} entradas parseadas; el registro tenía 211 el "
        f"2026-08-01. Si el formato de encabezado cambió, arreglar _ENTRY_RE "
        f"— no bajar este umbral."
    )


def test_every_entry_declares_a_machine_readable_status():
    """El contrato. Una entrada sin estado parseable es invisible para
    cualquier auditoría automática, y ésa es la causa raíz documentada en el
    docstring de este módulo."""
    offenders = []
    for bug_id, fname, heading, body in _entries():
        state, token = parse_status(heading, body)
        if state == "UNKNOWN":
            offenders.append(f"{fname}:{bug_id} token={token!r}")

    assert not offenders, (
        "entradas cuyo estado no es legible por máquina:\n  "
        + "\n  ".join(offenders)
        + "\n\nUsar una de las convenciones aceptadas: fila `| **Estado** | X |` "
        "o tag `[X]` al final del encabezado. Si X es un estado nuevo y "
        "deliberado, añadirlo a _CLOSED / _OPEN / _PARTIAL en este fichero "
        "— la clasificación es una decisión, no un detalle de formato."
    )


def test_open_and_closed_counts_are_stable():
    """Ancla numérica contra la deriva silenciosa.

    No fija un número exacto (el registro crece), pero sí que la inmensa
    mayoría esté cerrada y que los abiertos sigan siendo pocos y contables. Si
    esto falla, el registro cambió de forma sustantiva y toca releerlo — que
    es justo lo que las tres auditorías fallidas no hicieron.
    """
    counts = {"CLOSED": 0, "OPEN": 0, "PARTIAL": 0, "UNKNOWN": 0}
    for _, _, heading, body in _entries():
        counts[parse_status(heading, body)[0]] += 1

    assert counts["UNKNOWN"] == 0
    assert counts["CLOSED"] >= 150, counts
    assert counts["OPEN"] + counts["PARTIAL"] <= 40, (
        f"{counts['OPEN']} abiertas + {counts['PARTIAL']} parciales. Medido el "
        f"2026-08-01: 8 + 4 sobre 211 entradas. Un salto grande merece "
        f"revisión del registro, no un ajuste de este umbral."
    )


def test_status_parser_distinguishes_the_documented_cases():
    """Los casos concretos que las auditorías fallidas leyeron mal.

    Sin este test, `parse_status` podría degradarse a "todo CLOSED" y los
    tests de arriba seguirían pasando.
    """
    by_id = {bid: (h, b) for bid, _, h, b in _entries()}

    # B-115: cerrado vía SUBSUMIDO EN B-136, reportado como abierto por una
    # auditoría externa porque el tag no dice "RESUELTO".
    assert parse_status(*by_id["B-115"])[0] == "CLOSED"

    # B-172: MITIGADO, reportado como pendiente.
    assert parse_status(*by_id["B-172"])[0] == "CLOSED"

    # B-112/B-113: CANDIDATO en fila SIN negritas — la convención que mi
    # propio parser se saltó.
    for bid in ("B-112", "B-113"):
        assert parse_status(*by_id[bid])[0] == "OPEN", bid

    # B-224: estado sólo en el tag del encabezado, sin fila de tabla.
    assert parse_status(*by_id["B-224"])[0] == "CLOSED"

    # L-040: abierto de verdad.
    assert parse_status(*by_id["L-040"])[0] == "OPEN"

    # B-151: estado DIVIDIDO, "(a) RESUELTO ... (b) ABIERTO". Colapsarlo a
    # CLOSED es exactamente cómo desaparece un resto abierto: el sub-ítem (b)
    # es una decisión de arquitectura sin cablear.
    assert parse_status(*by_id["B-151"])[0] == "PARTIAL"

    # B-052: también dividido (P1/P2), pero AMBAS partes cerradas — P2 lo
    # está por doctrina sellada (NOT ADOPTED), que es un cierre, no un resto.
    assert parse_status(*by_id["B-052"])[0] == "CLOSED"

    # Los dos falsos parciales que costó distinguir: prosa que MENCIONA el
    # vocabulario del otro estado sin serlo.
    #   B-090 cita '"⏳ abierto" en la auditoría fuente' — cita histórica.
    #   B-149 dice "Documentado como limitación" — describe el manejo, no un cierre.
    assert parse_status(*by_id["B-090"])[0] == "CLOSED"
    assert parse_status(*by_id["B-149"])[0] == "OPEN"


def test_cross_reference_is_not_a_side_effect():
    """Fija la distinción que produjo el "41% con efectos colaterales".

    El 71% de las entradas menciona otro B-NNN. Eso es una referencia
    cruzada —contexto, linaje, supersesión— y no dice nada sobre si el fix
    fue limpio. Contarlo como efecto colateral infla la cifra ~14x.
    """
    entries = _entries()
    cross = [e for e in entries if re.search(r"B-\d{3}", e[3])]
    side = [
        e for e in entries
        if re.search(r"efecto colateral|side.?effect", e[3], re.I)
    ]
    assert len(cross) > len(side) * 5, (
        "la brecha entre referencia cruzada y efecto colateral explícito se "
        "cerró; revisar si el registro cambió de vocabulario antes de confiar "
        "en cualquier conteo de efectos colaterales."
    )
