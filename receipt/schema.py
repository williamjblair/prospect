"""The Prospect Receipt: the portable object that carries an AI's activity across the boundary
into signed, replayable scientific state.

A model can assert anything in a second. A receipt is the structured proposal that says exactly
what was claimed, which frozen artifacts it stands on, which facts a verifier confirms, how to
replay it, what status the evidence actually earns, and whether a human accepted it. It is not a
truth object. It is the bridge from activity to state:

    Activity  <  Receipt  <  Proposal  <  Review  <  Verification  <  Accepted event  <  State

The receipt makes that boundary portable. Any producer of scientific activity, an agent, a
notebook, a pipeline, or Prospect's own loop, can emit one, and the same frozen gate decides what
becomes state. No step is silently skipped, and no model sits in the trust path: the verifier is
frozen and the acceptance is a human key. This is the general pattern Prospect is a working
instance of, written from scratch for this dataset.
"""
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Literal, List

SCHEMA_VERSION = "prospect.receipt.v1"

# The typed status ladder. Never collapses to "verified"/"true". Weak evidence is never laundered
# through strong language: a hypothesis to test is `evidence_attached`, not `computationally_reproduced`.
Status = Literal[
    "claimed",                    # asserted, no evidence bound yet
    "evidence_attached",          # specific reproduced facts bound, but the claim itself is a proposal
    "computationally_reproduced", # re-derives from frozen released inputs (the EXACT lane)
    "independently_reanalyzed",   # a second, independent analysis agrees
    "contradicted",               # the data disagrees
    "refuted",                    # a stronger claim the data overturns
]

# How far the claim can be re-derived, and by whom.
Replayability = Literal[
    "exact",        # bit-for-bit re-derivable from frozen inputs (content-addressed)
    "reanalysis",   # re-run the analysis to reproduce
    "attested",     # rests on a human judgement or acceptance, not a re-derivation
    "none",
]

def content_id(frozen: dict) -> str:
    blob = "receipt\x1f" + json.dumps(frozen, sort_keys=True, separators=(",", ":"))
    return "rcpt_" + hashlib.sha256(blob.encode()).hexdigest()[:16]

@dataclass
class Artifact:
    name: str
    sha256: str                   # hash of the frozen input this receipt stands on
    locator: str = ""             # where to fetch it (path or public URI)

@dataclass
class EvidenceAtom:
    fact: str                     # the specific claim this atom supports
    value: str                    # the measured value, verbatim from the verifier
    source: str                   # which tool/table produced it

@dataclass
class Verifier:
    name: str                     # e.g. "MarsonPerturbseqChecker" / "frontier/verify.py"
    method: str                   # one line: how it decides
    replay: str                   # the command that re-derives the result

@dataclass
class Acceptance:
    signer: str
    delta_id: str
    pubkey: str
    signature: str
    attestation_type: str = "legacy_frontier_root_signature"
    covered_root: str = ""


@dataclass
class AcceptanceEvent:
    """A human-signed transition, separate from the proposal receipt."""

    receipt_id: str
    decision: Literal["accepted_into_state", "accepted_for_testing"]
    prior_root: str
    new_root: str
    signer: str
    pubkey: str
    signature: str


def _sorted_dicts(rows: Any, keys: tuple[str, ...]) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    normalized = [dict(row) for row in rows if isinstance(row, dict)]
    return sorted(normalized, key=lambda row: tuple(str(row.get(key, "")) for key in keys))


def canonical_receipt_body(receipt: dict[str, Any]) -> dict[str, Any]:
    """Return the complete proposal body covered by ``receipt_id``.

    Acceptance is deliberately excluded. A human acceptance event signs the
    receipt id and root transition separately, so accepting a proposal never
    changes the proposal's identity.
    """

    return {
        "schema_version": receipt.get("schema_version", SCHEMA_VERSION),
        "frontier": receipt.get("frontier", ""),
        "claim": receipt.get("claim", ""),
        "kind": receipt.get("kind", ""),
        "subject": sorted(str(item) for item in receipt.get("subject", [])),
        "producer": dict(receipt.get("producer") or {}),
        "artifacts": _sorted_dicts(receipt.get("artifacts"), ("name", "sha256", "locator")),
        "evidence": _sorted_dicts(receipt.get("evidence"), ("fact", "value", "source")),
        "verifier": dict(receipt.get("verifier") or {}),
        "status": receipt.get("status", ""),
        "replayability": receipt.get("replayability", ""),
        "conditions": sorted(str(item) for item in receipt.get("conditions", [])),
        "verification_requirements": list(receipt.get("verification_requirements", [])),
        "state_diff": dict(receipt.get("state_diff") or {}),
        "submitter_identity": dict(receipt.get("submitter_identity") or {}),
        "replay_metadata": dict(receipt.get("replay_metadata") or {}),
        "verdicts": _sorted_dicts(receipt.get("verdicts"), ("gene", "typed_status", "condition")),
    }


def receipt_id_for(receipt: dict[str, Any]) -> str:
    return content_id(canonical_receipt_body(receipt))

@dataclass
class Receipt:
    frontier: str                 # the frontier/dataset this proposes to change
    claim: str                    # the claim text
    kind: str                     # finding kind / "hypothesis" / "measurement"
    subject: List[str]            # the genes / entities
    producer: dict                # {kind, model, run} - the activity that generated it
    artifacts: List[Artifact]
    evidence: List[EvidenceAtom]
    verifier: Verifier
    status: Status
    replayability: Replayability
    schema_version: str = SCHEMA_VERSION
    conditions: List[str] = field(default_factory=list)
    verification_requirements: List[str] = field(default_factory=list)
    state_diff: dict = field(default_factory=dict)
    submitter_identity: dict = field(default_factory=dict)
    replay_metadata: dict = field(default_factory=dict)
    verdicts: List[dict] = field(default_factory=list)
    scope: List[str] = field(default_factory=list)   # conditions, caveats
    acceptance: Optional[Acceptance] = None
    receipt_id: str = ""

    def _materialize_defaults(self) -> None:
        if not self.conditions:
            self.conditions = list(self.scope)
        if not self.verification_requirements:
            self.verification_requirements = [
                self.verifier.method,
                self.verifier.replay,
                "human_signature_required",
            ]
        if not self.state_diff:
            self.state_diff = {
                "accepted": False,
                "model_can_apply": False,
                "effect": "proposal_only_no_state_mutation",
            }
        if not self.submitter_identity:
            self.submitter_identity = dict(self.producer)
        if not self.replay_metadata:
            self.replay_metadata = {
                "command": self.verifier.replay,
                "verifier": self.verifier.name,
                "replayability": self.replayability,
                "frontier": self.frontier,
            }

    def freeze(self):
        self._materialize_defaults()
        self.receipt_id = receipt_id_for(asdict(self))
        return self

    def to_dict(self):
        self._materialize_defaults()
        if not self.receipt_id:
            self.freeze()
        d = asdict(self)
        d["accepted"] = self.acceptance is not None
        if d["acceptance"] and not d["acceptance"].get("covered_root"):
            d["acceptance"]["covered_root"] = d["acceptance"].get("delta_id", "")
        return d
