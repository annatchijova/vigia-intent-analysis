"""Explicit availability limits for untrusted forensic JSON received over HTTP.

The limits apply to caller-supplied JSON bodies and OpenAI-compatible chat
messages, not to local evidence acquisition or the deterministic scoring core.
They keep the HTTP boundary from materialising unbounded temporary files or
dispatching arbitrarily large synthetic case graphs to a loopback service that
does not provide application authentication.
"""

from __future__ import annotations

import json
from typing import Any


# The checked-in corpus peaks at 217,373 bytes and 101 artifacts.  These
# boundaries leave substantial room for a legitimate remote case while making
# the service's availability contract explicit.
MAX_CASE_JSON_BYTES = 1_048_576
MAX_CASE_ARTIFACTS = 1_024


class CasePayloadError(ValueError):
    """Raised when a supplied HTTP case exceeds a declared intake bound."""


def validate_case_payload(case_data: Any) -> None:
    """Reject an oversized JSON case before writing or scoring it.

    This helper deliberately does not replace forensic schema validation.  It
    validates only transport-level size and artifact-cardinality limits; the
    existing normalized schema remains authoritative for case semantics.
    """
    if not isinstance(case_data, dict):
        raise CasePayloadError("case JSON must be an object")

    artifacts = case_data.get("artifacts")
    if isinstance(artifacts, list) and len(artifacts) > MAX_CASE_ARTIFACTS:
        raise CasePayloadError(
            f"case exceeds the {MAX_CASE_ARTIFACTS}-artifact API limit"
        )

    try:
        encoded = json.dumps(
            case_data,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError) as exc:
        raise CasePayloadError("case JSON could not be serialized safely") from exc

    if len(encoded) > MAX_CASE_JSON_BYTES:
        raise CasePayloadError(
            f"case exceeds the {MAX_CASE_JSON_BYTES}-byte API limit"
        )
