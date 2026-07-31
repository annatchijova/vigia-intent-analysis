# vigia/core/ontology.py — EPISTEMIC CONSTITUTION
#
# No Tribunal. No reasoning. Only describes the epistemic world.
# Deterministic. No floats. No probabilities. No ML.
#
# ---------------------------------------------------------------------------
# ATTRIBUTION
# ---------------------------------------------------------------------------
# Architecture and original implementation:
#     Kimi (Moonshot AI) — VIGIA AI Collective.
#     Kimi authored the layer separation this file exists to protect: a typed
#     Domain instead of free strings, OriginKind separated from
#     JustificationMode ("where a claim was born" is not "why we accept it"),
#     TemporalScope renamed to a coverage assessment ("temporal coverage" is
#     not "temporal truth"), a full canonical hash instead of a partial one,
#     and the removal of implicit wall-clock reads from auditable paths.
#
# Design review of the previous revision:
#     ChatGPT (OpenAI) — VIGIA AI Collective.
#     ChatGPT graded the prior revision 8.5/10 and identified the residual
#     forensic-engineering gaps addressed below: residual free-string typing
#     (ObservationPayload.value_type), the ambiguity of a missing dependency
#     in the registry graph, an invalidation cascade that was announced but
#     never implemented, and an imprecise definition of ARCHIVED.
#
# Integration, defect repair and determinism hardening:
#     Claude (Anthropic). See docs/EPISTEMIC_KERNEL.md for the full record of
#     what was changed on integration and why, including the two defects that
#     prevented the original files from importing or running at all.
#
# The complexity here is not accidental — it is the representation of the
# domain. Before removing a class or merging two enums, state which error the
# removal makes unrepresentable. If you cannot, the separation is load-bearing.
# ---------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Optional, Set, Tuple, Dict, List, FrozenSet
from enum import Enum, auto
from datetime import datetime
import hashlib


# =============================================================================
# PART I: TAXONOMY (Typed to the bone. No free strings for ontology.)
# =============================================================================

class Domain(Enum):
    """Typed domains. Never a free string."""
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    DOCUMENT = auto()
    NETWORK = auto()
    IDENTITY = auto()
    SYSTEM = auto()
    BEHAVIOR = auto()


class AuthorityLayer(Enum):
    """Distinct domains of authority. No order. No hierarchy."""
    CONSTITUTIVE = auto()
    TECHNICAL = auto()
    JURISDICTIONAL = auto()


class ClaimRole(Enum):
    """The function of a claim, not its logical power."""
    DEFINES = auto()
    CONSTRAINS = auto()
    DESCRIBES = auto()
    SUGGESTS = auto()


class OriginKind(Enum):
    """How the claim was born epistemologically."""
    FORMALIZATION = auto()
    EMPIRICAL_MEASUREMENT = auto()
    INSTITUTIONAL_DECISION = auto()
    ENGINEERING_CONVENTION = auto()
    HUMAN_HYPOTHESIS = auto()


class JustificationMode(Enum):
    """
    How the claim is justified. Separate from origin.

    Deliberately distinct from OriginKind. Collapsing the two conflates
    "this claim was born from a formalization" with "this claim is justified
    by a formal proof". Those are different dimensions, and a system that
    cannot tell them apart cannot audit its own reasoning.
    """
    FORMAL_PROOF = auto()
    DOCUMENTED_SPECIFICATION = auto()
    EMPIRICAL_REPLICATION = auto()
    INSTITUTIONAL_ACCEPTANCE = auto()
    EXPERT_CONSENSUS = auto()


class SourceType(Enum):
    """What artifact carries the claim."""
    RFC = auto()
    STANDARD = auto()
    LAW = auto()
    CODE = auto()
    DOCUMENTATION = auto()
    OBSERVATION = auto()
    PUBLICATION = auto()
    INTERNAL_HYPOTHESIS = auto()


class ObservationKind(Enum):
    """Typed observation kinds. Never a free string."""
    BINARY_STRUCTURE = auto()
    METADATA_STRUCTURE = auto()
    TIMESTAMP_ASSERTION = auto()
    CHAIN_OF_CUSTODY = auto()
    EXTERNAL_REFERENCE = auto()
    BEHAVIORAL_TRACE = auto()
    NETWORK_PATTERN = auto()


class PayloadEncoding(Enum):
    """
    How an observation payload value is encoded.

    Typed on integration (ChatGPT review): the original carried this as a free
    string `value_type` with the permitted values listed only in a comment.
    A payload whose encoding is a typo is a payload whose meaning is unknown,
    and an unknown encoding on an evidentiary value is not a cosmetic defect.
    """
    RAW = auto()
    HASH = auto()
    CANONICAL = auto()
    SIGNATURE = auto()


class TemporalCoverage(Enum):
    """
    Result of assessing an event time against a claim's validity window.

    Forensic time is not binary. A timestamp is an observation, not time
    itself. Coverage is separated from truth: WITHIN_SCOPE means the claim's
    temporal interval covers the event, NOT that the claim is true of it.
    """
    WITHIN_SCOPE = auto()
    UNKNOWN = auto()
    CLAIMED = auto()
    CONTRADICTED = auto()
    OUTSIDE_SCOPE = auto()


class ClaimStatus(Enum):
    """Mutable state of a claim in the registry. The claim atom is immutable."""
    ACTIVE = auto()
    QUESTIONED = auto()
    SUSPENDED = auto()
    SUPERSEDED = auto()
    ARCHIVED = auto()


class RevisionPolicy(Enum):
    """How may this claim change?"""
    IMMUTABLE = auto()
    VERSIONED = auto()
    DIAGNOSTIC = auto()
    RUNTIME_PRUNABLE = auto()


class DuplicateClaimError(Exception):
    """Raised when attempting to register a claim_id that already exists."""
    pass


# =============================================================================
# PART II: ATOMS (Immutable, hashable, auditable)
# =============================================================================

@dataclass(frozen=True)
class AuthoritySource:
    """Typed authority. Not a raw string."""
    name: str
    source_type: SourceType
    origin_kind: OriginKind
    justification_mode: JustificationMode
    jurisdiction: Optional[str] = None
    version_tag: Optional[str] = None
    url_or_ref: str = ""

    def __str__(self) -> str:
        parts = [self.name, self.source_type.name, self.origin_kind.name,
                 self.justification_mode.name]
        if self.version_tag:
            parts.append(self.version_tag)
        return ":".join(parts)

    def canonical_parts(self) -> Tuple[str, ...]:
        """
        Every field, for hashing. `__str__` is a human label and deliberately
        lossy (it omits jurisdiction and url_or_ref); hashing must not be.
        Two authorities differing only in jurisdiction are two authorities.
        """
        return (
            self.name,
            self.source_type.name,
            self.origin_kind.name,
            self.justification_mode.name,
            self.jurisdiction or "",
            self.version_tag or "",
            self.url_or_ref,
        )


@dataclass(frozen=True)
class TemporalWindow:
    """
    The validity interval of a claim. Forensic critical: claims are active
    only in time windows.

    Named TemporalWindow, not TemporalCoverage: the window is the interval,
    the coverage is the *result* of assessing an event against that interval.
    In the pre-integration revision both carried the same name in the same
    module, so the dataclass shadowed the enum and `assess()` raised
    AttributeError on every call. See docs/EPISTEMIC_KERNEL.md (defect D-1).
    """
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    version_range: Optional[Tuple[str, str]] = None

    def assess(self, event_time: Optional[datetime]) -> TemporalCoverage:
        """Never returns True/False. Always a TemporalCoverage status."""
        if event_time is None:
            return TemporalCoverage.UNKNOWN
        if self.valid_from and event_time < self.valid_from:
            return TemporalCoverage.OUTSIDE_SCOPE
        if self.valid_until and event_time > self.valid_until:
            return TemporalCoverage.OUTSIDE_SCOPE
        return TemporalCoverage.WITHIN_SCOPE


@dataclass(frozen=True)
class ClaimContext:
    """
    A claim is never universal. It lives in a context.

    `prerequisites` remains an open set of strings by deliberate omission, not
    by oversight: the ChatGPT review proposed promoting it to an enum, but the
    admissible prerequisites of a forensic claim are domain facts that belong
    to the human maintainer's ontology, not to this engine. Enumerating them
    here would be inventing the taxonomy rather than representing it. Tracked
    as an open design question in docs/EPISTEMIC_KERNEL.md.
    """
    platform: Optional[str] = None
    version: Optional[str] = None
    operation: Optional[str] = None
    prerequisites: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class OntologyClaim:
    """
    Immutable atom of the epistemic constitution.
    A claim does NOT know who can contradict it. The Tribunal decides that.
    """
    claim_id: str
    statement: str
    domain: Domain
    layer: AuthorityLayer
    claim_role: ClaimRole
    origin_kind: OriginKind
    justification_mode: JustificationMode
    authority: AuthoritySource
    temporal_window: TemporalWindow
    context: ClaimContext
    revision_policy: RevisionPolicy
    dependencies: FrozenSet[str] = frozenset()
    provenance_chain: Tuple[str, ...] = field(default_factory=tuple)

    def assess_time(self, event_time: Optional[datetime]) -> TemporalCoverage:
        return self.temporal_window.assess(event_time)

    def __hash__(self) -> int:
        # Identity is the claim_id. Two atoms with the same id are the same
        # claim regardless of content; the registry refuses to register the
        # second one, and supersede() is the only versioned path.
        return hash(self.claim_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, OntologyClaim):
            return NotImplemented
        return self.claim_id == other.claim_id


@dataclass(frozen=True)
class ObservationPayload:
    """Typed payload for observations. Never a free string value."""
    key: str
    value: str
    encoding: PayloadEncoding = PayloadEncoding.RAW


@dataclass(frozen=True)
class Observation:
    """
    First-class citizen of the Tribunal.
    Observations come from the world, not from the Constitution.
    """
    obs_id: str
    statement: str
    domain: Domain
    kind: ObservationKind
    payload: Tuple[ObservationPayload, ...]
    temporal_window: TemporalWindow = field(default_factory=TemporalWindow)
    context: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)

    def context_dict(self) -> Dict[str, str]:
        return dict(self.context)

    def payload_dict(self) -> Dict[str, str]:
        return {p.key: p.value for p in self.payload}


# =============================================================================
# PART III: REGISTRY (The Constitution. Describes. Never judges.)
# =============================================================================

@dataclass(frozen=True)
class KernelSnapshot:
    """Cryptographic identity of the kernel state at a point in time."""
    claims_hash: str
    timestamp: datetime
    parent_snapshot: Optional[str] = None
    engine_version: str = ""
    ruleset_version: str = ""

    def __str__(self) -> str:
        return (f"KernelSnapshot(hash={self.claims_hash[:16]}..., "
                f"ts={self.timestamp.isoformat()})")


def _length_prefixed(parts: Tuple[str, ...]) -> bytes:
    """
    Injective encoding of a tuple of strings.

    A plain `"|".join(parts)` is not injective: a claim whose statement
    contains the separator produces the same byte string as a different claim
    with the field boundary elsewhere. For a hash that anchors a forensic
    snapshot, "unlikely in practice" is not the standard. Length-prefixing
    each field makes the boundaries unambiguous regardless of content.
    """
    out = bytearray()
    for p in parts:
        raw = p.encode("utf-8")
        out += str(len(raw)).encode("ascii")
        out += b":"
        out += raw
    return bytes(out)


class OntologyRegistry:
    """
    The Constitution. Tracks mutable status per claim, but never deletes
    knowledge.

    Ordering contract: every accessor that returns more than one claim returns
    a tuple sorted by claim_id. Returning sets here would make iteration order
    depend on PYTHONHASHSEED, and any downstream serialization of that order
    would hash differently between runs — a determinism defect under the
    project's sealing invariants.
    """

    def __init__(self):
        self._claims: Dict[str, OntologyClaim] = {}
        self._status: Dict[str, ClaimStatus] = {}
        self._history: Dict[str, List[Tuple[datetime, ClaimStatus, str]]] = {}
        self._by_domain: Dict[Domain, Set[str]] = {}
        self._by_layer: Dict[AuthorityLayer, Set[str]] = {}
        self._dependents: Dict[str, Set[str]] = {}  # reverse dependency graph

    def register(self, claim: OntologyClaim) -> None:
        """Register a claim. Never overwrite. Modifications go through supersede()."""
        cid = claim.claim_id
        if cid in self._claims:
            raise DuplicateClaimError(
                f"Claim {cid} already registered. Use supersede() for versioned updates."
            )
        self._claims[cid] = claim
        self._status[cid] = ClaimStatus.ACTIVE
        self._history[cid] = []
        self._by_domain.setdefault(claim.domain, set()).add(cid)
        self._by_layer.setdefault(claim.layer, set()).add(cid)

        # Build reverse dependency graph. A dependency on a claim that is not
        # registered yet is permitted — registration order must not dictate
        # what the constitution can express — but the gap is not silent:
        # dangling_dependencies() reports it. See the method for the policy.
        for dep in claim.dependencies:
            self._dependents.setdefault(dep, set()).add(cid)

    def get(self, claim_id: str) -> Optional[OntologyClaim]:
        return self._claims.get(claim_id)

    def status(self, claim_id: str) -> Optional[ClaimStatus]:
        return self._status.get(claim_id)

    def history(self, claim_id: str) -> List[Tuple[datetime, ClaimStatus, str]]:
        return list(self._history.get(claim_id, []))

    def all_claim_ids(self) -> Tuple[str, ...]:
        return tuple(sorted(self._claims.keys()))

    def by_domain(self, domain: Domain) -> Tuple[OntologyClaim, ...]:
        return tuple(self._claims[c] for c in sorted(self._by_domain.get(domain, set())))

    def by_layer(self, layer: AuthorityLayer) -> Tuple[OntologyClaim, ...]:
        return tuple(self._claims[c] for c in sorted(self._by_layer.get(layer, set())))

    def dependents(self, claim_id: str) -> Tuple[OntologyClaim, ...]:
        """Claims that depend on this one. Used for cascade invalidation."""
        return tuple(self._claims[c]
                     for c in sorted(self._dependents.get(claim_id, set()))
                     if c in self._claims)

    def dangling_dependencies(self) -> Tuple[Tuple[str, str], ...]:
        """
        Every (claim_id, missing_dependency_id) pair the registry currently
        carries, sorted.

        Policy, answering the ChatGPT review's open question. A missing
        dependency does NOT block registration and does NOT invalidate the
        dependent claim. It is recorded as an external reference and made
        queryable. Rationale: this registry's governing rule is that it never
        deletes knowledge and never judges; refusing a registration would be
        a judgement, and silently accepting a phantom edge would be the
        dishonest option. Making the gap enumerable lets the caller decide,
        and lets an audit see what the kernel does not know.
        """
        missing = []
        for cid in sorted(self._claims):
            for dep in sorted(self._claims[cid].dependencies):
                if dep not in self._claims:
                    missing.append((cid, dep))
        return tuple(missing)

    def _set_status(self, claim_id: str, new_status: ClaimStatus, reason: str,
                    clock: datetime) -> None:
        if claim_id not in self._claims:
            raise KeyError(f"Unknown claim: {claim_id}")
        self._status[claim_id] = new_status
        self._history.setdefault(claim_id, []).append((clock, new_status, reason))

    def suspend_runtime_prunable(self, clock: datetime,
                                 reason: str = "runtime_prune") -> List[Tuple[OntologyClaim, ClaimStatus]]:
        """Suspend RUNTIME_PRUNABLE claims. Never delete. Never invalidate."""
        suspended = []
        for cid in sorted(self._claims):
            claim = self._claims[cid]
            if (claim.revision_policy == RevisionPolicy.RUNTIME_PRUNABLE and
                    self._status.get(cid) == ClaimStatus.ACTIVE):
                old = self._status[cid]
                self._set_status(cid, ClaimStatus.SUSPENDED, reason, clock)
                suspended.append((claim, old))
        return suspended

    def question_claim(self, claim_id: str, reason: str, clock: datetime) -> None:
        """A claim is questioned, not invalidated. Evidence may resolve it."""
        self._set_status(claim_id, ClaimStatus.QUESTIONED, reason, clock)

    def cascade_question(self, claim_id: str, reason: str,
                         clock: datetime) -> Tuple[str, ...]:
        """
        Question a claim and, transitively, every ACTIVE claim that depends on
        it. Returns the questioned ids in the order they were questioned.

        Implemented on integration: the reverse dependency graph was built by
        register() and documented as supporting "cascade invalidation", but no
        traversal existed (ChatGPT review). A cascade that is announced and
        absent is worse than one that is absent and admitted — a caller that
        questions a foundational claim would reasonably believe its dependents
        had been marked.

        Determinism: breadth-first, dependents visited in sorted claim_id
        order, so the emitted sequence and the resulting history are identical
        across runs and platforms.

        Only ACTIVE claims are questioned. SUPERSEDED, ARCHIVED and SUSPENDED
        claims are left as they are: their status already carries information
        that QUESTIONED would overwrite. Already-QUESTIONED claims are not
        re-questioned, which also terminates cycles.
        """
        if claim_id not in self._claims:
            raise KeyError(f"Unknown claim: {claim_id}")

        questioned: List[str] = []
        seen: Set[str] = set()
        queue: List[str] = [claim_id]

        while queue:
            cid = queue.pop(0)
            if cid in seen:
                continue
            seen.add(cid)
            if cid not in self._claims:
                # Phantom dependency edge; nothing to question.
                continue
            if self._status.get(cid) != ClaimStatus.ACTIVE:
                # Not questioned, but its dependents are still reachable
                # through it -- an inactive claim does not sever the graph.
                queue.extend(sorted(self._dependents.get(cid, set())))
                continue

            if cid == claim_id:
                cascade_reason = reason
            else:
                cascade_reason = f"{reason} (cascade from {claim_id})"
            self._set_status(cid, ClaimStatus.QUESTIONED, cascade_reason, clock)
            questioned.append(cid)
            queue.extend(sorted(self._dependents.get(cid, set())))

        return tuple(questioned)

    def supersede(self, claim_id: str, successor_id: str, reason: str,
                  clock: datetime) -> None:
        """A claim is superseded by a newer version. History preserved."""
        self._set_status(claim_id, ClaimStatus.SUPERSEDED,
                         f"{reason}: successor={successor_id}", clock)

    def archive(self, claim_id: str, reason: str, clock: datetime) -> None:
        """
        Archive a claim: preserved, retrievable, no longer active.

        ARCHIVED states custody, not falsity. The reason string carries why.
        The pre-integration docstring defined the status as "proven internally
        inconsistent", which overloaded a custody state with a verdict — in
        forensic systems "archived" means preserved but not active, and a
        reader who inferred "inconsistent" from the status alone would be
        reading a judgement the registry never made (ChatGPT review).

        Internal inconsistency is one legitimate reason to archive. It is not
        the definition of the status.
        """
        self._set_status(claim_id, ClaimStatus.ARCHIVED, reason, clock)

    def _canonical_bytes(self, claim: OntologyClaim) -> bytes:
        """Deterministic canonical serialization of a claim for hashing."""
        parts = (
            claim.claim_id,
            claim.statement,
            claim.domain.name,
            claim.layer.name,
            claim.claim_role.name,
            claim.origin_kind.name,
            claim.justification_mode.name,
        ) + claim.authority.canonical_parts() + (
            claim.temporal_window.valid_from.isoformat() if claim.temporal_window.valid_from else "",
            claim.temporal_window.valid_until.isoformat() if claim.temporal_window.valid_until else "",
            claim.temporal_window.version_range[0] if claim.temporal_window.version_range else "",
            claim.temporal_window.version_range[1] if claim.temporal_window.version_range else "",
            claim.context.platform or "",
            claim.context.version or "",
            claim.context.operation or "",
            ",".join(sorted(claim.context.prerequisites)),
            claim.revision_policy.name,
            ",".join(sorted(claim.dependencies)),
            ",".join(claim.provenance_chain),
        )
        return _length_prefixed(parts)

    def _compute_hash(self) -> str:
        """Deterministic hash of the complete current kernel state."""
        h = hashlib.sha256()
        for cid in sorted(self._claims.keys()):
            claim = self._claims[cid]
            status = self._status[cid]
            h.update(self._canonical_bytes(claim))
            h.update(status.name.encode())
        return h.hexdigest()

    def snapshot(self, clock: datetime, engine_version: str = "",
                 ruleset_version: str = "",
                 parent: Optional[str] = None) -> KernelSnapshot:
        """
        Deterministic audit snapshot of current kernel state.

        `clock` is injected, never read from the system: a snapshot that reads
        the wall clock cannot be reproduced by a third party verifying the
        bundle later.
        """
        return KernelSnapshot(
            claims_hash=self._compute_hash(),
            timestamp=clock,
            parent_snapshot=parent,
            engine_version=engine_version,
            ruleset_version=ruleset_version,
        )
